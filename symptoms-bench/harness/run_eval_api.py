#!/usr/bin/env python3
"""Run SymptomsBench against OpenAI-compatible HTTP APIs.

Supported providers (set env vars, then pick --provider):

  groq        GROQ_API_KEY          https://api.groq.com/openai/v1
  openrouter  OPENROUTER_API_KEY    https://openrouter.ai/api/v1
  openai      OPENAI_API_KEY        https://api.openai.com/v1
  deepseek    DEEPSEEK_API_KEY      https://api.deepseek.com
  together    TOGETHER_API_KEY      https://api.together.xyz/v1
  fireworks   FIREWORKS_API_KEY     https://api.fireworks.ai/inference/v1
  gemini      GEMINI_API_KEY        https://generativelanguage.googleapis.com/v1beta/openai/
  custom      OPENAI_API_KEY + --base-url

Free / cheap starters:
  groq:       llama-3.3-70b-versatile, openai/gpt-oss-120b, qwen/qwen3-32b
  openrouter: google/gemini-2.0-flash-001, qwen/qwen3-32b:free (when listed free)
  gemini:     gemini-2.0-flash, gemini-2.5-flash
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
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

PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "env": "GROQ_API_KEY",
        "defaults": [
            "llama-3.3-70b-versatile",
            "openai/gpt-oss-20b",
            "qwen/qwen3-32b",
        ],
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "env": "OPENROUTER_API_KEY",
        "defaults": [
            "google/gemini-2.0-flash-001",
            "qwen/qwen3-32b",
            "meta-llama/llama-3.3-70b-instruct",
        ],
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "env": "OPENAI_API_KEY",
        "defaults": ["gpt-4.1-mini", "gpt-4.1"],
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "env": "DEEPSEEK_API_KEY",
        "defaults": ["deepseek-chat", "deepseek-reasoner"],
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "env": "TOGETHER_API_KEY",
        "defaults": ["Qwen/Qwen2.5-72B-Instruct-Turbo"],
    },
    "fireworks": {
        "base_url": "https://api.fireworks.ai/inference/v1",
        "env": "FIREWORKS_API_KEY",
        "defaults": ["accounts/fireworks/models/llama-v3p3-70b-instruct"],
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "env": "GEMINI_API_KEY",
        "defaults": ["gemini-2.0-flash", "gemini-2.5-flash"],
    },
    "custom": {
        "base_url": "",
        "env": "OPENAI_API_KEY",
        "defaults": [],
    },
}


def chat_completions(
    *,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    timeout: int = 180,
    extra_headers: dict[str, str] | None = None,
) -> tuple[str, dict]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {detail[:500]}") from exc

    choices = body.get("choices") or []
    if not choices:
        raise RuntimeError(f"empty choices: {body!r}"[:500])
    content = choices[0].get("message", {}).get("content") or ""
    usage = body.get("usage") or {}
    return content, {
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
    }


def run_model_on_task(
    *,
    model: str,
    task_dir: Path,
    base_url: str,
    api_key: str,
    extra_headers: dict[str, str] | None,
) -> dict:
    prompt = build_prompt(task_dir)
    t0 = time.time()
    error = None
    passed = False
    usage = {"prompt_tokens": 0, "completion_tokens": 0}
    raw = ""
    try:
        raw, usage = chat_completions(
            base_url=base_url,
            api_key=api_key,
            model=model,
            prompt=prompt,
            extra_headers=extra_headers,
        )
        files = extract_file_map(raw, default_py=default_source_file(task_dir))
        with tempfile.TemporaryDirectory(prefix="symptoms-api-") as tmp:
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", default="groq", choices=sorted(PROVIDERS))
    parser.add_argument("--models", nargs="+", default=None)
    parser.add_argument("--base-url", default=None, help="Override API base URL")
    parser.add_argument("--api-key", default=None, help="Override API key")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--list-providers", action="store_true")
    args = parser.parse_args()

    if args.list_providers:
        for name, cfg in PROVIDERS.items():
            print(f"{name:12} env={cfg['env']:20} base={cfg['base_url']}")
            if cfg["defaults"]:
                print(f"             defaults: {', '.join(cfg['defaults'])}")
        return

    cfg = PROVIDERS[args.provider]
    api_key = args.api_key or os.environ.get(cfg["env"]) or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(
            f"Missing API key. Set {cfg['env']} (or pass --api-key).\n"
            f"Examples of free/cheap keys:\n"
            f"  Groq:       https://console.groq.com/keys\n"
            f"  OpenRouter: https://openrouter.ai/keys\n"
            f"  Gemini:     https://aistudio.google.com/apikey\n",
            file=sys.stderr,
        )
        sys.exit(2)

    base_url = args.base_url or cfg["base_url"] or os.environ.get("OPENAI_BASE_URL")
    if not base_url:
        print("custom provider requires --base-url or OPENAI_BASE_URL", file=sys.stderr)
        sys.exit(2)

    models = args.models or cfg["defaults"]
    if not models:
        print("Pass --models for custom provider", file=sys.stderr)
        sys.exit(2)

    extra_headers: dict[str, str] = {}
    if args.provider == "openrouter":
        extra_headers["HTTP-Referer"] = "https://github.com/razel369/razel369.github.io"
        extra_headers["X-Title"] = "SymptomsBench"

    RESULTS.mkdir(parents=True, exist_ok=True)
    tasks = list_tasks()
    if args.limit:
        tasks = tasks[: args.limit]

    all_rows: list[dict] = []
    summary: dict[str, dict] = {}

    for model in models:
        print(f"\n=== {args.provider}:{model} ===")
        rows = []
        for task_dir in tasks:
            print(f"  -> {task_dir.name} ...", flush=True)
            row = run_model_on_task(
                model=model,
                task_dir=task_dir,
                base_url=base_url,
                api_key=api_key,
                extra_headers=extra_headers,
            )
            row["provider"] = args.provider
            rows.append(row)
            all_rows.append(row)
            mark = "PASS" if row["passed"] else "FAIL"
            extra = f" ({row['error']})" if row["error"] else ""
            print(f"     {mark} {row['seconds']}s{extra}")

        resolved = sum(1 for r in rows if r["passed"])
        label = f"{args.provider}:{model}"
        summary[label] = {
            "resolve_at_1": resolved / len(rows) if rows else 0.0,
            "resolved": resolved,
            "total": len(rows),
            "avg_seconds": round(sum(r["seconds"] for r in rows) / max(len(rows), 1), 2),
            "tokens": sum(r["prompt_tokens"] + r["completion_tokens"] for r in rows),
        }

    out = {
        "benchmark": "SymptomsBench",
        "protocol": "logs-only",
        "backend": f"api:{args.provider}",
        "summary": summary,
        "runs": all_rows,
    }
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_path = RESULTS / f"run-api-{stamp}.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    (RESULTS / "latest.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    # Merge into leaderboard markdown
    lines = [
        "# SymptomsBench Results",
        "",
        f"Latest API run: {stamp} ({args.provider})",
        "",
        "| Model | Resolve@1 | Resolved | Avg seconds | Tokens |",
        "|-------|-----------|----------|-------------|--------|",
    ]
    for label, s in summary.items():
        lines.append(
            f"| `{label}` | {s['resolve_at_1']:.1%} | {s['resolved']}/{s['total']} | {s['avg_seconds']} | {s['tokens']} |"
        )
    board = RESULTS / "LEADERBOARD.md"
    prev = board.read_text(encoding="utf-8") if board.exists() else ""
    board.write_text(prev.rstrip() + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")
    print("\n" + "\n".join(lines))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
