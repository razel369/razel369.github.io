# Symptoms Debugger Plugin

**One job:** make a local model beat frontier chat models at **log-only bug fixing**.

Not a general coding assistant. A tight loop:

```
logs + code → propose fix → run hidden/smoke tests → if fail, append new logs → retry
```

## Why this can beat Fable 5 (in this niche)

| | Fable 5 (chat) | Local + this plugin |
|--|----------------|---------------------|
| Signal | prose / guessed diagnosis | real pytest output every turn |
| Retries | expensive / manual | free, automatic, capped |
| Success metric | “sounds right” | tests green |
| Context | general knowledge | only symptoms + repo |

Claim we optimize for:

> **Local model + Symptoms Debugger ≥ Fable 5 on Resolve@k (logs-only).**

## Quick eval

```bash
cd symptoms-bench

# Plugin lift: same local model, k=1 vs k=5
python3 plugin/run_plugin_eval.py \
  --backend hf \
  --model Qwen/Qwen2.5-1.5B-Instruct \
  --attempts 5

# Head-to-head later (needs API key for a frontier stand-in, or paste Fable outputs)
python3 plugin/run_plugin_eval.py --backend api --provider groq \
  --model llama-3.3-70b-versatile --attempts 1
```

## Plugin API (minimal)

```python
from plugin.agent import SymptomsDebugger

dbg = SymptomsDebugger(generate_fn=my_llm_call, max_attempts=5)
result = dbg.repair(workspace_dir, initial_logs)
assert result.passed
```

## Fair Fable 5 protocol

1. Same 12 SymptomsBench tasks  
2. Same visible inputs: `workspace/` + `logs.txt` only  
3. Fable 5: up to **k** turns; each turn may receive new failing logs (no bug spoilers)  
4. Local+plugin: same **k**  
5. Winner = higher Resolve@k, then fewer attempts, then fewer tokens  

See [PROTOCOL_VS_FABLE.md](PROTOCOL_VS_FABLE.md).
