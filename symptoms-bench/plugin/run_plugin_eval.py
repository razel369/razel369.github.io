#!/usr/bin/env python3
"""Evaluate Symptoms Debugger plugin (multi-attempt) on SymptomsBench."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugin"))
sys.path.insert(0, str(ROOT / "harness"))

from agent import SymptomsDebugger  # noqa: E402
from run_eval import list_tasks  # noqa: E402

RESULTS = ROOT / "results"


def make_hf_generator(model_id: str):
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

    def generate_fn(system: str, user: str) -> str:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tok(text, return_tensors="pt")
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=320,
                do_sample=False,
                pad_token_id=tok.eos_token_id,
            )
        gen = out[0][inputs["input_ids"].shape[-1] :]
        return tok.decode(gen, skip_special_tokens=True)

    return generate_fn


def make_api_generator(provider: str, model: str):
    import os

    from run_eval_api import PROVIDERS, chat_completions

    cfg = PROVIDERS[provider]
    api_key = os.environ.get(cfg["env"]) or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(f"Missing {cfg['env']}")
    base_url = cfg["base_url"]
    extra = {}
    if provider == "openrouter":
        extra = {
            "HTTP-Referer": "https://github.com/razel369/razel369.github.io",
            "X-Title": "SymptomsDebugger",
        }

    def generate_fn(system: str, user: str) -> str:
        # chat_completions uses SYSTEM from run_eval; call raw endpoint with our system
        import json
        import urllib.request

        url = base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": model,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                **extra,
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"] or ""

    return generate_fn


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["hf", "api"], default="hf")
    parser.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
    parser.add_argument("--provider", default="groq")
    parser.add_argument("--attempts", type=int, default=5)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--compare-oneshot", action="store_true",
                        help="Also run k=1 with same model for plugin lift")
    args = parser.parse_args()

    if args.backend == "hf":
        generate_fn = make_hf_generator(args.model)
        label = f"plugin-hf:{args.model}"
    else:
        generate_fn = make_api_generator(args.provider, args.model)
        label = f"plugin-{args.provider}:{args.model}"

    tasks = list_tasks()
    if args.limit:
        tasks = tasks[: args.limit]

    def run_arm(max_attempts: int, arm_name: str) -> dict:
        dbg = SymptomsDebugger(generate_fn, max_attempts=max_attempts)
        rows = []
        print(f"\n=== {arm_name} (k={max_attempts}) ===")
        for task in tasks:
            print(f"  -> {task.name} ...", flush=True)
            t0 = time.time()
            logs = (task / "logs.txt").read_text(encoding="utf-8")
            result = dbg.repair(
                task / "workspace",
                logs,
                grade_tests=task / "hidden_tests",
                smoke_tests=None,  # use workspace copy's tests/ inside the loop
            )
            row = {
                "task": task.name,
                "arm": arm_name,
                "passed": result.passed,
                "attempts_used": result.attempts_used,
                "seconds": round(time.time() - t0, 2),
                "errors": [h.error for h in result.history if h.error],
            }
            rows.append(row)
            mark = "PASS" if result.passed else "FAIL"
            print(f"     {mark} in {result.attempts_used} attempt(s), {row['seconds']}s")
        resolved = sum(1 for r in rows if r["passed"])
        solved_attempts = [r["attempts_used"] for r in rows if r["passed"]]
        return {
            "name": arm_name,
            "attempts_budget": max_attempts,
            "resolve_at_k": resolved / len(rows) if rows else 0.0,
            "resolved": resolved,
            "total": len(rows),
            "mean_attempts_when_solved": round(
                sum(solved_attempts) / len(solved_attempts), 2
            )
            if solved_attempts
            else None,
            "rows": rows,
        }

    arms = []
    if args.compare_oneshot and args.attempts > 1:
        arms.append(run_arm(1, f"{label}@k1"))
    arms.append(run_arm(args.attempts, f"{label}@k{args.attempts}"))

    out = {
        "benchmark": "SymptomsBench",
        "plugin": "SymptomsDebugger",
        "model": args.model,
        "backend": args.backend,
        "arms": {a["name"]: {k: v for k, v in a.items() if k != "rows"} for a in arms},
        "runs": [r for a in arms for r in a["rows"]],
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = RESULTS / f"plugin-run-{stamp}.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = [
        "# Symptoms Debugger Plugin Results",
        "",
        f"Generated: {stamp}",
        f"Model: `{args.model}`",
        "",
        "| Arm | Resolve@k | Resolved | Mean attempts (solved) |",
        "|-----|-----------|----------|------------------------|",
    ]
    for a in arms:
        lines.append(
            f"| `{a['name']}` | {a['resolve_at_k']:.1%} | {a['resolved']}/{a['total']} | {a['mean_attempts_when_solved']} |"
        )
    board = RESULTS / "PLUGIN_LEADERBOARD.md"
    board.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n" + "\n".join(lines))
    print(f"\nWrote {path}")


if __name__ == "__main__":
    main()
