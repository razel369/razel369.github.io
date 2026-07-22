#!/usr/bin/env python3
"""Grade a task workspace against hidden tests."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def grade_task(task_dir: Path, workspace: Path | None = None) -> dict:
    task_dir = task_dir.resolve()
    src = workspace.resolve() if workspace else (task_dir / "workspace").resolve()
    hidden = task_dir / "hidden_tests"
    if not hidden.exists():
        raise FileNotFoundError(f"missing hidden tests: {hidden}")

    with tempfile.TemporaryDirectory(prefix="symptoms-grade-") as tmp:
        tmp_path = Path(tmp)
        # Copy workspace code (exclude its smoke tests from grading path confusion)
        work = tmp_path / "workspace"
        shutil.copytree(src, work, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        tests = tmp_path / "hidden_tests"
        shutil.copytree(hidden, tests)

        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(tests), "-q", "--tb=line"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        passed = proc.returncode == 0
        return {
            "task": task_dir.name,
            "passed": passed,
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="Path to task dir")
    parser.add_argument("--workspace", default=None, help="Optional alternate workspace")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = grade_task(Path(args.task), Path(args.workspace) if args.workspace else None)
    if args.json:
        print(json.dumps(result))
    else:
        print("PASS" if result["passed"] else "FAIL", result["task"])
        if not result["passed"]:
            print(result["stdout"])
            print(result["stderr"])
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
