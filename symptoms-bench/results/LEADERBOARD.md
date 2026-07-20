# SymptomsBench Results

Generated: 20260720-190729  
Backend: HuggingFace transformers (CPU, free local)

| Model | Resolve@1 | Resolved | Avg seconds | Tokens |
|-------|-----------|----------|-------------|--------|
| `HuggingFaceTB/SmolLM2-360M-Instruct` | 0.0% | 0/12 | 3.66 | 6753 |
| `Qwen/Qwen2.5-0.5B-Instruct` | 33.3% | 4/12 | 3.70 | 5674 |
| `Qwen/Qwen2.5-1.5B-Instruct` | 41.7% | 5/12 | 8.76 | 5585 |

## Notes

- Protocol: logs-only (no issue description).
- Ollama backend crashed with segfault on this CPU; HF transformers is the supported free path.
- Early runs failed mostly on brittle JSON output parsing; the harness now prefers `<<<FILE>>>` blocks and tolerates truncated fences.
- Ceiling is intentionally low for small models — room for stronger agents.
