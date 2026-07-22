"""Shared helpers for interactive SymptomsBench grading sessions."""

from __future__ import annotations

import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERFACE = Path(__file__).resolve().parent
REPLIES = INTERFACE / "replies"
SESSION_PATH = INTERFACE / "session.json"

import sys

sys.path.insert(0, str(ROOT / "harness"))
sys.path.insert(0, str(ROOT / "plugin"))
sys.path.insert(0, str(INTERFACE))

from grade_reply import emit_retry_prompt, grade_one, resolve_task  # noqa: E402
from prompts import SYSTEM, combined_prompt  # noqa: E402
from run_eval import list_tasks  # noqa: E402


def task_ids() -> list[str]:
    return [p.name for p in list_tasks()]


def read_prompt(task_id: str, kind: str = "user") -> str:
    """kind: user | combined | system"""
    if kind == "system":
        return (INTERFACE / "SYSTEM.txt").read_text(encoding="utf-8")
    suffix = "USER" if kind == "user" else "COMBINED"
    path = INTERFACE / "tasks" / f"{task_id}_{suffix}.txt"
    if not path.exists():
        # regenerate pack on the fly
        from build_pack import main as build

        build()
    return path.read_text(encoding="utf-8")


def load_session() -> dict:
    if SESSION_PATH.exists():
        return json.loads(SESSION_PATH.read_text(encoding="utf-8"))
    return {
        "model_name": "",
        "max_attempts": 3,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "tasks": {
            tid: {"status": "pending", "attempts": [], "passed": False}
            for tid in task_ids()
        },
    }


def save_session(session: dict) -> None:
    SESSION_PATH.write_text(json.dumps(session, indent=2) + "\n", encoding="utf-8")


def summary(session: dict) -> dict:
    tasks = session["tasks"]
    total = len(tasks)
    passed = sum(1 for t in tasks.values() if t.get("passed"))
    attempted = sum(1 for t in tasks.values() if t.get("attempts"))
    return {
        "total": total,
        "passed": passed,
        "attempted": attempted,
        "pending": total - attempted,
        "resolve_rate": passed / total if total else 0.0,
    }


def submit_reply(
    session: dict,
    task_id: str,
    reply: str,
    *,
    model_name: str | None = None,
) -> dict:
    REPLIES.mkdir(parents=True, exist_ok=True)
    task = resolve_task(task_id)
    state = session["tasks"].setdefault(
        task_id, {"status": "pending", "attempts": [], "passed": False}
    )
    attempt_n = len(state["attempts"]) + 1
    reply_path = REPLIES / f"{task_id}_a{attempt_n}.txt"
    reply_path.write_text(reply, encoding="utf-8")

    result = grade_one(task, reply)
    max_attempts = int(session.get("max_attempts", 3))
    entry = {
        "attempt": attempt_n,
        "passed": result["passed"],
        "error": result.get("error"),
        "patched_files": result.get("patched_files") or [],
        "reply_path": str(reply_path.relative_to(INTERFACE)),
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    state["attempts"].append(entry)

    payload: dict = {
        "task": task_id,
        "passed": result["passed"],
        "attempt": attempt_n,
        "error": result.get("error"),
        "patched_files": result.get("patched_files") or [],
        "reply_path": entry["reply_path"],
        "retry_prompt": None,
        "done": False,
    }

    if result["passed"]:
        state["passed"] = True
        state["status"] = "passed"
        payload["done"] = True
    elif attempt_n >= max_attempts:
        state["passed"] = False
        state["status"] = "failed"
        payload["done"] = True
    else:
        state["status"] = "retry"
        payload["retry_prompt"] = emit_retry_prompt(
            task,
            result,
            attempt=attempt_n + 1,
            max_attempts=max_attempts,
        )

    if model_name:
        session["model_name"] = model_name
    save_session(session)
    write_scorecard(session)
    return payload


def write_scorecard(session: dict) -> Path:
    s = summary(session)
    lines = [
        "# SymptomsBench Session Scorecard",
        "",
        f"Model: `{session.get('model_name') or '(unnamed)'}`",
        f"Resolved: **{s['passed']}/{s['total']}** ({s['resolve_rate']:.0%})",
        f"Attempted: {s['attempted']} · Pending: {s['pending']}",
        "",
        "| Task | Status | Attempts |",
        "|------|--------|----------|",
    ]
    for tid, st in session["tasks"].items():
        status = st.get("status", "pending")
        n = len(st.get("attempts") or [])
        lines.append(f"| `{tid}` | {status} | {n} |")
    path = INTERFACE / "SCORECARD.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def next_pending(session: dict) -> str | None:
    skipped = set(session.get("_skipped") or [])
    for tid, st in session["tasks"].items():
        if st.get("status") in {"pending", "retry"} and tid not in skipped:
            return tid
    # Fallback: any pending/retry including skipped
    for tid, st in session["tasks"].items():
        if st.get("status") in {"pending", "retry"}:
            return tid
    return None


def clipboard_copy(text: str) -> bool:
    """Best-effort clipboard copy. Returns True if something worked."""
    import shutil
    import subprocess

    candidates = []
    if shutil.which("wl-copy"):
        candidates.append(["wl-copy"])
    if shutil.which("xclip"):
        candidates.append(["xclip", "-selection", "clipboard"])
    if shutil.which("xsel"):
        candidates.append(["xsel", "--clipboard", "--input"])
    if shutil.which("pbcopy"):
        candidates.append(["pbcopy"])
    if shutil.which("clip.exe"):
        candidates.append(["clip.exe"])

    for cmd in candidates:
        try:
            subprocess.run(cmd, input=text.encode("utf-8"), check=True)
            return True
        except Exception:  # noqa: BLE001
            continue
    return False
