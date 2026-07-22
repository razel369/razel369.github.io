# SymptomsBench

**Symptoms-Only Bug Hunt** — an LLM agent benchmark where the model gets a buggy repo and failing logs, but **no issue description**.

## Protocol

1. Agent receives:
   - Source files under `workspace/`
   - `logs.txt` (failing test / traceback output)
2. Agent must **not** receive:
   - The human-readable bug description
   - Hidden verification tests used for grading
3. Success = hidden tests pass after the agent's edits.

## Quick start

```bash
# Generate / refresh failing logs for all tasks
python3 harness/prepare_logs.py

# Score a candidate workspace (manual)
python3 harness/grade.py --task tasks/001_off_by_one

# Sanity: buggy code fails, oracle fixes pass
python3 harness/sanity_check.py

# Recommended: free local HuggingFace models (CPU)
python3 harness/run_eval_hf.py \
  --models HuggingFaceTB/SmolLM2-360M-Instruct Qwen/Qwen2.5-0.5B-Instruct Qwen/Qwen2.5-1.5B-Instruct

# Stronger models via free/cheap APIs (needs a key — see STRONGER_MODELS.md)
export GROQ_API_KEY='...'   # or GEMINI_API_KEY / OPENROUTER_API_KEY
python3 harness/run_eval_api.py --provider groq --models llama-3.3-70b-versatile

# Optional: Ollama (may segfault on some CPUs)
python3 harness/run_eval.py --models qwen2.5:3b llama3.2:3b gemma2:2b
```

See [STRONGER_MODELS.md](STRONGER_MODELS.md) for Groq / Gemini / OpenRouter setup.

## Chat-interface benchmark (paste into any model UI)

Ready-to-copy prompts live in [`interface/`](interface/):

```bash
python3 interface/build_pack.py          # regenerate prompts
# then open interface/README.md
# copy interface/SYSTEM.txt + interface/tasks/001_off_by_one_USER.txt into the chat
python3 interface/grade_reply.py --task 001_off_by_one --reply replies/001_off_by_one.txt
```

## Symptoms Debugger plugin

The product bet: a **log-only repair loop** that makes local models competitive with Fable 5 on this niche.

```bash
# Prove plugin lift (k=1 vs k=5) on the same local model
python3 plugin/run_plugin_eval.py --backend hf \
  --model Qwen/Qwen2.5-1.5B-Instruct --attempts 5 --compare-oneshot

# Export prompts for a manual Fable 5 head-to-head
python3 plugin/export_prompts.py
```

Details: [plugin/README.md](plugin/README.md) · [plugin/PROTOCOL_VS_FABLE.md](plugin/PROTOCOL_VS_FABLE.md)


## Metrics

| Metric | Meaning |
|--------|---------|
| `resolve@1` | Fraction of tasks fixed on first attempt |
| `steps` | Number of model calls used |
| `cost_tokens` | Prompt + completion tokens |
| `regression` | Hidden tests that newly fail (should stay 0) |

## Task layout

```
tasks/<id>_<slug>/
  meta.json          # difficulty, tags, description (HIDDEN from agent)
  bug_manifest.json  # planted bug info (HIDDEN)
  workspace/         # what the agent sees (buggy code)
  logs.txt           # failing symptoms (agent sees)
  hidden_tests/      # grading only
```
