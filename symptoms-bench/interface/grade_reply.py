#!/usr/bin/env python3
"""Grade a chat-interface model reply against SymptomsBench hidden tests."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "harness"))
sys.path.insert(0, str(ROOT / "plugin"))

from prompts import SYSTEM, build_task_user_prompt  # noqa: E402
from run_eval import (  # noqa: E402
    apply_files,
    collect_workspace_files,
    default_source_file,
    extract_file_map,
    grade,
    list_tasks,
)


def resolve_task(name: str) -> Path:
    name = name.strip().removesuffix(".txt").removesuffix(".md")
    direct = ROOT / "tasks" / name
    if direct.exists():
        return direct
    matches = [p for p in list_tasks() if p.name.startswith(name) or name in p.name]
    if len(matches) == 1:
        return matches[0]
    raise SystemExit(f"Unknown task: {name}. Known: {[p.name for p in list_tasks()]}")


def grade_one(task: Path, reply_text: str) -> dict:
    files = extract_file_map(reply_text, default_py=default_source_file(task))
    # Drop test paths
    files = {
        k: v
        for k, v in files.items()
        if "tests" not in Path(k).parts and not Path(k).name.startswith("test_")
    }
    if not files:
        return {
            "task": task.name,
            "passed": False,
            "error": "no source file patch found in reply",
        }
    with tempfile.TemporaryDirectory(prefix="iface-grade-") as tmp:
        dest = Path(tmp) / "workspace"
        apply_files(task / "workspace", files, dest)
        ok = grade(task, dest)
        # Capture smoke logs for retry prompts
        import subprocess

        smoke = dest / "tests"
        logs = ""
        if not ok and smoke.exists():
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", str(smoke), "-q", "--tb=short"],
                cwd=dest,
                capture_output=True,
                text=True,
            )
            logs = (proc.stdout or "") + (proc.stderr or "")
        return {
            "task": task.name,
            "passed": ok,
            "patched_files": sorted(files),
            "retry_logs": logs,
            "error": None if ok else "hidden tests failed",
        }


def emit_retry_prompt(task: Path, result: dict, attempt: int = 2, max_attempts: int = 3) -> str:
    files = collect_workspace_files(task / "workspace")
    # Note: for true multi-turn we'd patch workspace with last reply; for interface
    # pack we keep original sources + new failing logs from grading sandbox when available.
    logs = result.get("retry_logs") or (task / "logs.txt").read_text(encoding="utf-8")
    hint = default_source_file(task)
    return build_task_user_prompt(
        task.name,
        logs,
        files,
        attempt=attempt,
        max_attempts=max_attempts,
        hint_source=hint,
        prior_note=(
            "Previous reply failed grading. Do not repeat the same broken patch.\n"
            f"Files seen in previous reply: {', '.join(result.get('patched_files') or [])}"
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", help="Task id, e.g. 001_off_by_one")
    parser.add_argument("--reply", type=Path, help="Path to model reply text")
    parser.add_argument("--replies-dir", type=Path, help="Grade all *.txt replies")
    parser.add_argument("--emit-retry", action="store_true")
    parser.add_argument("--attempt", type=int, default=2)
    args = parser.parse_args()

    results = []
    if args.replies_dir:
        for reply in sorted(args.replies_dir.glob("*.txt")):
            stem = reply.stem
            # Allow 001_off_by_one_a2.txt style names
            if "_a" in stem and stem.rsplit("_a", 1)[-1].isdigit():
                stem = stem.rsplit("_a", 1)[0]
            task = resolve_task(stem)
            text = reply.read_text(encoding="utf-8")
            results.append(grade_one(task, text))
    else:
        if not args.task or not args.reply:
            parser.error("Provide --task and --reply, or --replies-dir")
        task = resolve_task(args.task)
        text = args.reply.read_text(encoding="utf-8")
        result = grade_one(task, text)
        results.append(result)
        if args.emit_retry and not result["passed"]:
            print("===== RETRY PROMPT (copy into chat) =====")
            print(emit_retry_prompt(task, result, attempt=args.attempt))
            print("===== END RETRY PROMPT =====")

    resolved = sum(1 for r in results if r["passed"])
    for r in results:
        mark = "PASS" if r["passed"] else "FAIL"
        extra = f" ({r['error']})" if r.get("error") and not r["passed"] else ""
        print(f"{mark} {r['task']}{extra}")

    if len(results) > 1 or args.replies_dir:
        lines = [
            "# SymptomsBench Interface Scorecard",
            "",
            f"Resolved: **{resolved}/{len(results)}** ({(resolved/len(results) if results else 0):.0%})",
            "",
            "| Task | Result |",
            "|------|--------|",
        ]
        for r in results:
            lines.append(f"| `{r['task']}` | {'PASS' if r['passed'] else 'FAIL'} |")
        scorecard = ROOT / "interface" / "SCORECARD.md"
        scorecard.write_text("\n".join(lines) + "\n", encoding="utf-8")
        (ROOT / "interface" / "scorecard.json").write_text(
            json.dumps({"resolved": resolved, "total": len(results), "results": results}, indent=2),
            encoding="utf-8",
        )
        print(f"Scorecard -> {scorecard}")

    sys.exit(0 if all(r["passed"] for r in results) else 1)


if __name__ == "__main__":
    main()
