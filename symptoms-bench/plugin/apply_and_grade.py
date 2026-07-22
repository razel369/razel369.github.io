#!/usr/bin/env python3
"""Apply a model reply file to a task workspace and grade it."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "harness"))
sys.path.insert(0, str(ROOT / "plugin"))
from run_eval import apply_files, default_source_file, extract_file_map, grade  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--reply", type=Path, required=True, help="Raw model output file")
    args = parser.parse_args()
    task = args.task.resolve()
    raw = args.reply.read_text(encoding="utf-8")
    files = extract_file_map(raw, default_py=default_source_file(task))
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "workspace"
        apply_files(task / "workspace", files, dest)
        ok = grade(task, dest)
    print("PASS" if ok else "FAIL", task.name)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
