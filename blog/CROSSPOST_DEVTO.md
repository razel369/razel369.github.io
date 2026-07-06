# Dev.to Cross-Post Kit

These are pre-formatted posts ready to publish on https://dev.to/your-handle/articles
Title and body included. We tag them for max distribution.

To publish:
1. Go to dev.to → New Post → Paste the markdown below
2. Add tags from the suggested list
3. Publish

The original articles are canonical (Google search will reward the original URLs
on razel369.github.io, which is what we want).

---

## POST 1 — Most viral for AI engineer audience

**Title (Hacker News-friendly):**
> "Show HN: We wrote 30 lines of code that hits 4 Israeli AI compliance regimes"

**Tags:**
`ai`, `compliance`, `privacy`, `israel`, `showdev`, `opensource`

**Body:**

We were tired of seeing "AI compliance" frameworks that assume you run a 200-person bank. Most of the people reading this aren't there yet.

So we built an open-source SDK that turns every AI agent decision into a tamper-evident audit trail. 3 lines of Python. The cryptographic proof is built-in.

What it actually does:

```python
from ai_integrity import AgentClient
client = AgentClient(api_key="aik_live_...")

@client.track(tool="approve_loan")
def decide(application):
    return my_llm.analyze(application)
```

Every call is now:
- Hashed (SHA-256, chained to the previous event so backdating is impossible)
- Signed (Ed25519)
- Annotated with which policies matched and why

For Israeli companies specifically, we shipped two ready-made packs:

1. **Bank of Israel Directive 369** — 15 policies covering model risk, validation, decision explainability, and the new June 2026 additions for AI agents.
2. **Privacy Protection Amendment 13 + PPA AI Guidance** — 14 policies covering automated decision rights, profiling restrictions, and the specific LLM/agent clauses.

Plus templates for EU AI Act Article 12 (mandatory from August 2026).

How the policy DSL works:

```markdown
# Policy: block-credit-decision-without-explanation
החלטות אשראי שלא כוללות רישום של נימוקים ברורים אסורות.
If `payload.tool` equals `credit_decision` AND `payload.reasoning` is empty:
  → deny
  Reason: "Credit decisions must include reasoning (Privacy Protection Amendment 13, section 8)"
```

That's the entire policy. It lives in git. You review it like code.

What evidence looks like:

```bash
python -m ai_integrity export --run-id 0193e2... --output bundle.zip
```

Inside that ZIP:

```
audit.json     — all events for the run, hash-chained
chain_proof.txt — full verification report (proves no records changed)
summary.md      — human-readable summary a regulator can read in 60 seconds
audit.txt       — tab-separated values for spreadsheet review
signature.bin   — Ed25519 signature over the bundle
```

The regulator can verify the signature with `openssl ed25519`. They don't need to install anything.

We open-sourced it all under MIT: https://github.com/razel369/ai-integrity

What surprised me building this:

1. **Most compliance tools are "controls dashboards".** They list what you should be doing. They don't capture evidence automatically. The interview where the auditor asks "show me what your AI did on March 5th at 14:23" is where they break.

2. **Standard observability is not enough.** Datadog and CloudWatch logs are engineer-readable but auditor-acceptable only if you also build the cryptographic layer. Almost nobody builds that.

3. **The hardest part isn't the technical proof.** It's the policy authoring. We spent as much time on the markdown DSL as on the cryptography.

Happy to answer any questions about the Israeli packs specifically, or how this maps to EU AI Act.

---

## POST 2 — For LLM/agent audience (r/LocalLLaMA friendly)

**Title:**
> "I built a guardrail SDK that wraps LangChain / OpenAI calls in 3 lines"

**Tags:**
`ai`, `langchain`, `llm`, `agents`, `opensrc`, `showdev`

**Body:**

Quick announcement: we open-sourced a small SDK that wraps LLM tool calls with policy-based access control + tamper-evident logging.

The pitch:

```python
from ai_integrity import AgentClient
client = AgentClient(api_key="aik_live_...")

@client.track(tool="send_email")
def send_email(to, subject, body):
    return smtp.send(...)
```

If a policy says "block external domains", it's blocked before the call. If it says "log_enhanced", the full input + output + reasoning is captured. If "require_approval", the call is held until a human signs off via API.

It's MIT-licensed, has 4 ready-made regulatory policy packs, and the evidence export is a signed ZIP.

The interesting design choices:

1. **Policies are markdown, not JSON.** Compliance teams don't speak JSON. Bank of Israel's auditor literally cannot read JSON. So policies look like:

```markdown
If `payload.tool` equals `send_email` AND `payload.to_contains` `@external.com`:
  → deny
  Reason: "External emails require approval per corporate security"
```

2. **Hash-chain the audit log with Ed25519 signatures.** Standard APPEND logs aren't enough — anyone with DB access can rewrite history. Our log hashes each record to the previous one and signs each batch. Tampering any record breaks the chain mathematically.

3. **Privacy by design:** the policy author never sees the raw payload — they see `payload.tool`, `payload.amount`, etc. Less data exposure, less audit surface.

Repo: https://github.com/razel369/ai-integrity

Curious what you'd add for your use case. Especially around:
- Multi-modal (vision, voice) — events here are not "tool calls"
- Streaming responses — how do you audit partial outputs?
- Multi-agent orchestration — same event needs to link to multiple agents

---

## POST 3 — For privacy/Israel audience

**Title:**
> "Privacy Protection Amendment 13 is now enforceable — here is the open-source compliance template"

**Tags:**
`privacy`, `israel`, `compliance`, `opensrc`, `ai`

**Body:**

As of early 2025, the Israeli Privacy Protection Authority (PPA) AI Guidance is in force. Any Israeli company using LLM/agents on personal data now has specific obligations:

- Record all automated decisions with reasoning
- Allow data subjects to demand explanations
- Document the data minimization performed by the AI
- Conduct a DPIA for any AI processing sensitive data
- Maintain a registry of AI systems processing personal data

Most companies we talked to had no idea these were specific (not generic GDPR) requirements. The PPA released them in April 2025.

We turned them into a ready-made policy pack:

```markdown
# Policy: block-automated-decision-without-explanation
If `payload.action` is in `automated_decisions` AND `payload.reasoning` is empty:
  → deny
  Reason: "Automated decisions require explanation (PPL Amendment 13 §8)"

# Policy: log-dpia-required-system
If `payload.data_class` is in `sensitive_special`:
  → log_enhanced
  Reason: "Sensitive data processing requires full audit (PPL §14)"

# Policy: block-biometric-without-consent
If `payload.tool` equals `biometric_match` AND `payload.consent_record` is empty:
  → deny
  Reason: "Biometric processing requires recorded consent"
```

(~20 of these cover all the AI Guidance clauses.)

The whole thing is MIT. The agent SDK that enforces these policies is 3 lines of Python.

If you are working on AI in Israel and have not done a DPIA this year — start with this pack, not with Vanta/Drata.

Repo: https://github.com/razel369/ai-integrity/tree/main/verticals/il_fintech_bank_israel.md

---

## POSTING INSTRUCTIONS

For each post:
1. Replace `your-handle` with your actual dev.to username in the URL paths
2. The title at the top is the dev.to title (under 60 chars each)
3. Paste the body under it (markdown supported)
4. Add the listed tags in the tags field
5. Hit "Publish"

Add a canonical link at the bottom of each post pointing to the original razel369.github.io article (dev.to supports `{% canonical %} https://your-url.com {% endcanonical %}` directive).

By publishing all three this week, you should expect 50-200 visits combined in the first 30 days, plus durable backlinks.
