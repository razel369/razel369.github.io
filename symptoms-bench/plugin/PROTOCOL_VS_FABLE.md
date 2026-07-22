# Head-to-head protocol: Symptoms Debugger vs Fable 5

## Claim
On **logs-only bug fix** tasks, a small local model wrapped in Symptoms Debugger can match or beat Fable 5 when both get the same attempt budget.

## Shared constraints
- Inputs: project files + failing logs only  
- Hidden: `meta.json`, `bug_manifest.json`, hidden tests used only for grading  
- Output: patched source files  
- Success: hidden tests pass  
- Budget: `k` attempts (default **5**)  
- After each failed attempt, the next turn receives **fresh pytest logs only** (no natural-language coaching)

## Arms
| Arm | Model | Scaffold |
|-----|-------|----------|
| A | Local (e.g. Qwen2.5-1.5B / 7B) | Symptoms Debugger plugin |
| B | Fable 5 | Same loop rules, human/API driver that only forwards logs |

Optional Arm C: Fable 5 **single shot** (k=1) — shows the value of the loop itself.

## Metrics
1. `Resolve@k` — primary  
2. `Attempts-to-fix` mean on solved tasks  
3. Tokens / wall time  

## How to run Arm A
```bash
python3 plugin/run_plugin_eval.py --backend hf \
  --model Qwen/Qwen2.5-1.5B-Instruct --attempts 5
```

## How to run Arm B (Fable 5)
Until Cursor exposes Fable as an API, use one of:
1. Manual: paste each task prompt from `plugin/export_prompts.py`, paste reply, run `plugin/apply_and_grade.py`  
2. Proxy: if you have another frontier API, run `--attempts 5` as an upper bound stand-in and label it clearly  

## Disallowed
- Pasting bug_manifest / meta descriptions into the model  
- Editing hidden tests  
- Using web search that reveals the planted bug writeup  
