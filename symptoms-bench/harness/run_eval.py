#!/usr/bin/env python3
"""Run SymptomsBench against Ollama models (free/local)."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "tasks"
RESULTS = ROOT / "results"
GRADE = ROOT / "harness" / "grade.py"

SYSTEM = """You are a debugging agent.
You receive a small Python project and the failing test output (logs).
There is NO separate bug description — diagnose from symptoms only.
Return ONLY a JSON object mapping relative file paths to the FULL fixed file contents.
Example:
{"sum_window.py": "def sum_all(nums):\\n    return sum(nums)\\n"}
Do not wrap in markdown. Do not include tests/ files unless you must fix them.
"""


def list_tasks() -> list[Path]:
    return sorted(p for p in TASKS.iterdir() if p.is_dir() and (p / "workspace").exists())


def collect_workspace_files(workspace: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for path in sorted(workspace.rglob("*")):
        if not path.is_file():
            continue
        if any(part in {"__pycache__", ".pytest_cache", "tests"} for part in path.parts):
            continue
        rel = path.relative_to(workspace).as_posix()
        if path.suffix.lower() not in {".py", ".md", ".txt", ".toml", ".cfg", ".ini"}:
            continue
        files[rel] = path.read_text(encoding="utf-8")
    return files


def build_prompt(task_dir: Path) -> str:
    workspace = task_dir / "workspace"
    logs = (task_dir / "logs.txt").read_text(encoding="utf-8")
    files = collect_workspace_files(workspace)
    parts = [
        f"Task id: {task_dir.name}",
        "Failing logs:",
        "```",
        logs.strip(),
        "```",
        "",
        "Project files:",
    ]
    for rel, content in files.items():
        parts.append(f"\n----- FILE: {rel} -----\n{content}")
    parts.append(
        "\nRespond with JSON only: {\"relative/path.py\": \"full fixed source\"}"
    )
    return "\n".join(parts)


def ollama_chat(model: str, prompt: str, timeout: int = 180) -> tuple[str, dict]:
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "options": {"temperature": 0.1},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    content = body.get("message", {}).get("content", "")
    usage = {
        "prompt_tokens": body.get("prompt_eval_count", 0),
        "completion_tokens": body.get("eval_count", 0),
    }
    return content, usage


def extract_json_map(text: str) -> dict[str, str]:
    text = text.strip()
    # Strip markdown fences if present
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    # Find first JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("no JSON object in model output")
    obj = json.loads(text[start : end + 1])
    if not isinstance(obj, dict):
        raise ValueError("JSON root must be object")
    out: dict[str, str] = {}
    for k, v in obj.items():
        if isinstance(v, str):
            out[str(k)] = v
    if not out:
        raise ValueError("empty file map")
    return out


def apply_files(workspace_src: Path, files: dict[str, str], dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(
        workspace_src,
        dest,
        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"),
    )
    for rel, content in files.items():
        # Never allow escaping workspace
        rel_path = Path(rel)
        if rel_path.is_absolute() or ".." in rel_path.parts:
            continue
        target = dest / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def grade(task_dir: Path, workspace: Path) -> bool:
    proc = subprocess.run(
        [
            sys.executable,
            str(GRADE),
            "--task",
            str(task_dir),
            "--workspace",
            str(workspace),
            "--json",
        ],
        capture_output=True,
        text=True,
    )
    try:
        payload = json.loads(proc.stdout.strip() or "{}")
    except json.JSONDecodeError:
        return False
    return bool(payload.get("passed"))


def run_model_on_task(model: str, task_dir: Path) -> dict:
    prompt = build_prompt(task_dir)
    t0 = time.time()
    error = None
    passed = False
    usage = {"prompt_tokens": 0, "completion_tokens": 0}
    raw = ""
    try:
        raw, usage = ollama_chat(model, prompt)
        files = extract_json_map(raw)
        with tempfile.TemporaryDirectory(prefix="symptoms-run-") as tmp:
            dest = Path(tmp) / "workspace"
            apply_files(task_dir / "workspace", files, dest)
            passed = grade(task_dir, dest)
    except Exception as exc:  # noqa: BLE001
        error = f"{type(exc).__name__}: {exc}"
        passed = False
    return {
        "task": task_dir.name,
        "model": model,
        "passed": passed,
        "seconds": round(time.time() - t0, 2),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "error": error,
        "raw_preview": raw[:500],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--models",
        nargs="+",
        default=["qwen2.5:3b", "llama3.2:3b", "gemma2:2b"],
    )
    parser.add_argument("--limit", type=int, default=0, help="Limit tasks (0=all)")
    args = parser.parse_args()

    RESULTS.mkdir(parents=True, exist_ok=True)
    tasks = list_tasks()
    if args.limit:
        tasks = tasks[: args.limit]

    # Sanity: Ollama up
    try:
        urllib.request.urlopen("http://127.0.0.1:11434/", timeout=5).read()
    except urllib.error.URLError as exc:
        print("Ollama is not running on :11434", exc, file=sys.stderr)
        sys.exit(2)

    all_rows: list[dict] = []
    summary: dict[str, dict] = {}

    for model in args.models:
        print(f"\n=== {model} ===")
        rows = []
        for task_dir in tasks:
            print(f"  -> {task_dir.name} ...", flush=True)
            row = run_model_on_task(model, task_dir)
            rows.append(row)
            all_rows.append(row)
            mark = "PASS" if row["passed"] else "FAIL"
            extra = f" ({row['error']})" if row["error"] else ""
            print(f"     {mark} {row['seconds']}s{extra}")
        resolved = sum(1 for r in rows if r["passed"])
        summary[model] = {
            "resolve_at_1": resolved / len(rows) if rows else 0.0,
            "resolved": resolved,
            "total": len(rows),
            "avg_seconds": round(sum(r["seconds"] for r in rows) / max(len(rows), 1), 2),
            "tokens": sum(r["prompt_tokens"] + r["completion_tokens"] for r in rows),
        }

    out = {
        "benchmark": "SymptomsBench",
        "protocol": "logs-only",
        "summary": summary,
        "runs": all_rows,
    }
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_path = RESULTS / f"run-{stamp}.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    latest = RESULTS / "latest.json"
    latest.write_text(json.dumps(out, indent=2), encoding="utf-8")

    # Markdown leaderboard
    lines = [
        "# SymptomsBench Results",
        "",
        f"Generated: {stamp}",
        "",
        "| Model | Resolve@1 | Resolved | Avg seconds | Tokens |",
        "|-------|-----------|----------|-------------|--------|",
    ]
    for model, s in summary.items():
        lines.append(
            f"| `{model}` | {s['resolve_at_1']:.1%} | {s['resolved']}/{s['total']} | {s['avg_seconds']} | {s['tokens']} |"
        )
    board = RESULTS / "LEADERBOARD.md"
    board.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n" + "\n".join(lines))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
