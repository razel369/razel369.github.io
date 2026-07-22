#!/usr/bin/env python3
"""Generate failing logs.txt for each task by running workspace smoke tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "tasks"


def prepare_task(task_dir: Path) -> None:
    workspace = task_dir / "workspace"
    tests = workspace / "tests"
    if not tests.exists():
        print(f"skip {task_dir.name}: no smoke tests")
        return
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(tests), "-q", "--tb=short"],
        cwd=workspace,
        capture_output=True,
        text=True,
    )
    # Agent sees combined stdout/stderr of the failing run
    logs = (proc.stdout or "") + (proc.stderr or "")
    (task_dir / "logs.txt").write_text(logs, encoding="utf-8")
    status = "FAIL" if proc.returncode != 0 else "UNEXPECTED_PASS"
    print(f"{status}: {task_dir.name} (exit={proc.returncode})")


def main() -> None:
    for task_dir in sorted(TASKS.iterdir()):
        if task_dir.is_dir() and (task_dir / "workspace").exists():
            prepare_task(task_dir)


if __name__ == "__main__":
    main()
