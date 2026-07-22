#!/usr/bin/env python3
"""Sanity checks: buggy workspaces fail; oracle fixes pass."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "tasks"
GRADE = ROOT / "harness" / "grade.py"

# Minimal oracle patches: relative file -> fixed source
ORACLES: dict[str, dict[str, str]] = {
    "001_off_by_one": {
        "sum_window.py": '''def sum_all(nums: list[int]) -> int:
    """Return the sum of every element in nums."""
    total = 0
    for i in range(len(nums)):
        total += nums[i]
    return total
'''
    },
    "002_wrong_operator": {
        "pricing.py": '''def apply_discount(price: float, discount: float) -> float:
    """Apply fractional discount in [0, 1], e.g. 0.2 = 20% off."""
    return price * (1 - discount)
'''
    },
    "003_wrong_variable": {
        "clamp.py": '''def clamp(x: float, lo: float, hi: float) -> float:
    """Clamp x into [lo, hi]."""
    if x < lo:
        result = lo
    elif x > hi:
        result = hi
    else:
        result = x
    return result
'''
    },
}


def grade(task: Path, workspace: Path) -> bool:
    proc = subprocess.run(
        [sys.executable, str(GRADE), "--task", str(task), "--workspace", str(workspace), "--json"],
        capture_output=True,
        text=True,
    )
    data = json.loads(proc.stdout or "{}")
    return bool(data.get("passed"))


def main() -> None:
    failures = 0
    for task in sorted(TASKS.iterdir()):
        if not task.is_dir():
            continue
        buggy_pass = grade(task, task / "workspace")
        if buggy_pass:
            print(f"BUGGY_SHOULD_FAIL: {task.name}")
            failures += 1
        else:
            print(f"buggy_fails_ok: {task.name}")

        if task.name in ORACLES:
            with tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / "workspace"
                shutil.copytree(task / "workspace", dest)
                for rel, content in ORACLES[task.name].items():
                    (dest / rel).write_text(content, encoding="utf-8")
                if not grade(task, dest):
                    print(f"ORACLE_SHOULD_PASS: {task.name}")
                    failures += 1
                else:
                    print(f"oracle_passes_ok: {task.name}")

    if failures:
        print(f"FAILED checks: {failures}")
        sys.exit(1)
    print("All sanity checks passed")


if __name__ == "__main__":
    main()
