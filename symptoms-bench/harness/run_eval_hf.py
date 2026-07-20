#!/usr/bin/env python3
"""Run SymptomsBench with local HuggingFace transformers models (free)."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "tasks"
RESULTS = ROOT / "results"
GRADE = ROOT / "harness" / "grade.py"

# Reuse prompt builder from run_eval
sys.path.insert(0, str(ROOT / "harness"))
from run_eval import (  # noqa: E402
    SYSTEM,
    apply_files,
    build_prompt,
    default_source_file,
    extract_file_map,
    grade,
    list_tasks,
)

DEFAULT_MODELS = [
    "Qwen/Qwen2.5-0.5B-Instruct",
    "Qwen/Qwen2.5-1.5B-Instruct",
    "HuggingFaceTB/SmolLM2-360M-Instruct",
]


def load_model(model_id: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"Loading {model_id} ...", flush=True)
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        dtype=torch.float32,
        device_map="cpu",
    )
    model.eval()
    return tok, model


def generate(tok, model, prompt: str, max_new_tokens: int = 320) -> tuple[str, dict]:
    import torch

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": prompt},
    ]
    if hasattr(tok, "apply_chat_template"):
        text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        text = SYSTEM + "\n\n" + prompt
    inputs = tok(text, return_tensors="pt")
    prompt_tokens = int(inputs["input_ids"].shape[-1])
    # Soft-stop around end marker when present in vocab
    eos_ids = [tok.eos_token_id] if tok.eos_token_id is not None else []
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tok.eos_token_id,
            eos_token_id=eos_ids or None,
        )
    gen = out[0][prompt_tokens:]
    completion_tokens = int(gen.shape[-1])
    content = tok.decode(gen, skip_special_tokens=True)
    return content, {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }


def run_model_on_task(tok, model, model_id: str, task_dir: Path) -> dict:
    prompt = build_prompt(task_dir)
    t0 = time.time()
    error = None
    passed = False
    usage = {"prompt_tokens": 0, "completion_tokens": 0}
    raw = ""
    try:
        raw, usage = generate(tok, model, prompt)
        files = extract_file_map(raw, default_py=default_source_file(task_dir))
        with tempfile.TemporaryDirectory(prefix="symptoms-hf-") as tmp:
            dest = Path(tmp) / "workspace"
            apply_files(task_dir / "workspace", files, dest)
            passed = grade(task_dir, dest)
    except Exception as exc:  # noqa: BLE001
        error = f"{type(exc).__name__}: {exc}"
        passed = False
    return {
        "task": task_dir.name,
        "model": model_id,
        "passed": passed,
        "seconds": round(time.time() - t0, 2),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "error": error,
        "raw_preview": raw[:500],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    RESULTS.mkdir(parents=True, exist_ok=True)
    tasks = list_tasks()
    if args.limit:
        tasks = tasks[: args.limit]

    all_rows: list[dict] = []
    summary: dict[str, dict] = {}

    for model_id in args.models:
        tok, model = load_model(model_id)
        print(f"\n=== {model_id} ===")
        rows = []
        for task_dir in tasks:
            print(f"  -> {task_dir.name} ...", flush=True)
            row = run_model_on_task(tok, model, model_id, task_dir)
            rows.append(row)
            all_rows.append(row)
            mark = "PASS" if row["passed"] else "FAIL"
            extra = f" ({row['error']})" if row["error"] else ""
            print(f"     {mark} {row['seconds']}s{extra}")
        # Free memory between models
        del model
        del tok
        try:
            import torch

            torch.cuda.empty_cache()
        except Exception:  # noqa: BLE001
            pass

        resolved = sum(1 for r in rows if r["passed"])
        summary[model_id] = {
            "resolve_at_1": resolved / len(rows) if rows else 0.0,
            "resolved": resolved,
            "total": len(rows),
            "avg_seconds": round(sum(r["seconds"] for r in rows) / max(len(rows), 1), 2),
            "tokens": sum(r["prompt_tokens"] + r["completion_tokens"] for r in rows),
        }

    out = {
        "benchmark": "SymptomsBench",
        "protocol": "logs-only",
        "backend": "transformers-cpu",
        "summary": summary,
        "runs": all_rows,
    }
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_path = RESULTS / f"run-hf-{stamp}.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    (RESULTS / "latest.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = [
        "# SymptomsBench Results",
        "",
        f"Generated: {stamp}",
        "Backend: HuggingFace transformers (CPU, free local)",
        "",
        "| Model | Resolve@1 | Resolved | Avg seconds | Tokens |",
        "|-------|-----------|----------|-------------|--------|",
    ]
    for model_id, s in summary.items():
        lines.append(
            f"| `{model_id}` | {s['resolve_at_1']:.1%} | {s['resolved']}/{s['total']} | {s['avg_seconds']} | {s['tokens']} |"
        )
    (RESULTS / "LEADERBOARD.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n" + "\n".join(lines))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
