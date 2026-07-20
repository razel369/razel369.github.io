# Stronger models for SymptomsBench

There are **no API keys** in this environment right now. To score stronger models, pick one free/cheap provider, paste a key, and run `harness/run_eval_api.py`.

## Fastest free options

| Provider | Signup | Example models | Cost |
|----------|--------|----------------|------|
| **Groq** | https://console.groq.com/keys | `llama-3.3-70b-versatile`, `qwen/qwen3-32b` | Free daily quota |
| **Gemini** | https://aistudio.google.com/apikey | `gemini-2.0-flash`, `gemini-2.5-flash` | Free tier |
| **OpenRouter** | https://openrouter.ai/keys | `google/gemini-2.0-flash-001`, occasional `:free` models | Free credits / free tags |

## Run

```bash
# Groq 70B
export GROQ_API_KEY='...'
python3 harness/run_eval_api.py --provider groq --models llama-3.3-70b-versatile

# Gemini Flash
export GEMINI_API_KEY='...'
python3 harness/run_eval_api.py --provider gemini --models gemini-2.0-flash

# OpenRouter
export OPENROUTER_API_KEY='...'
python3 harness/run_eval_api.py --provider openrouter --models google/gemini-2.0-flash-001

# Any OpenAI-compatible endpoint
export OPENAI_API_KEY='...'
python3 harness/run_eval_api.py --provider custom \
  --base-url https://YOUR_HOST/v1 \
  --models your-model-name
```

List providers:

```bash
python3 harness/run_eval_api.py --list-providers
```

## Local (no key) but limited

CPU-only box (~15GB RAM) can run up to ~1.5B–3B well. For 7B+ you want a GPU host or an API.

```bash
python3 harness/run_eval_hf.py --models Qwen/Qwen2.5-3B-Instruct
```

## Recommended next scoreboard targets

1. `llama-3.3-70b-versatile` (Groq)
2. `gemini-2.0-flash` (Gemini free)
3. `deepseek-chat` / `deepseek-reasoner` (cheap)
4. `gpt-4.1-mini` (if you have OpenAI credit)
