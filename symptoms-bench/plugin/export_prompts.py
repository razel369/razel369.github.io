#!/usr/bin/env python3
"""Export per-task prompts for manual Fable 5 / frontier head-to-head."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "harness"))
from run_eval import SYSTEM, build_prompt, list_tasks  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "fable_prompts")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "SYSTEM.txt").write_text(SYSTEM, encoding="utf-8")
    for task in list_tasks():
        prompt = build_prompt(task)
        (args.out / f"{task.name}.txt").write_text(prompt, encoding="utf-8")
        print("wrote", task.name)
    print(f"Prompts in {args.out}")
    print("Paste SYSTEM.txt + each task file into Fable 5; save replies next to them.")


if __name__ == "__main__":
    main()
