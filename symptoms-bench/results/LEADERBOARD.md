# SymptomsBench Results

## Free local HF CPU (full 12-task run)

Generated: 20260720-190729

| Model | Resolve@1 | Resolved | Avg seconds | Tokens |
|-------|-----------|----------|-------------|--------|
| `HuggingFaceTB/SmolLM2-360M-Instruct` | 0.0% | 0/12 | 3.66 | 6753 |
| `Qwen/Qwen2.5-0.5B-Instruct` | 33.3% | 4/12 | 3.70 | 5674 |
| `Qwen/Qwen2.5-1.5B-Instruct` | 41.7% | 5/12 | 8.76 | 5585 |

## How to add stronger models

No API keys are configured in this environment. Add one free key and run:

```bash
export GROQ_API_KEY='...'   # https://console.groq.com/keys
python3 harness/run_eval_api.py --provider groq --models llama-3.3-70b-versatile
```

See [STRONGER_MODELS.md](../STRONGER_MODELS.md) for Gemini / OpenRouter / DeepSeek / custom endpoints.
