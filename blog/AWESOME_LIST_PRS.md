# Awesome-List PR Kit

Below are ready-to-paste PR descriptions for adding AI Integrity to popular
awesome-* GitHub lists. Backlinks from these lists are high-DR and rank
well in Google. Most have a low PR acceptance bar.

---

## LIST 1: `eugenkiss/awesome-ai-agents`

URL: https://github.com/eugenkiss/awesome-ai-agents
Section: "Compliance & Safety"

PR title:
> Add AI Integrity — Open-source tamper-evident audit trail for AI agents

PR body:
```
### What is this?

[AI Integrity](https://github.com/razel369/ai-integrity) — MIT-licensed Python SDK
that records every AI agent decision in a hash-chained audit log, evaluates
each call against markdown-based policies, and exports a signed evidence
bundle for regulators.

### Why should it be in this list?

It is the only open-source project (to our knowledge) that targets Israeli
banking compliance (Bank of Israel Directive 369), EU AI Act Article 12, and
Privacy Protection Amendment 13 with ready-made policy packs, while also
working as a general agent observability tool with cryptographic proof.

The export bundle is a single signed ZIP that includes the chain
verification report — no SaaS dependency, no waiting on a sales call.

### Category

Compliance & Safety

### Link

https://github.com/razel369/ai-integrity
```

---

## LIST 2: `wbinglee/awesome-compliance`

URL: https://github.com/wbinglee/awesome-compliance
Section: "AI compliance"

PR title:
> Add AI Integrity — Open-source compliance evidence for AI agents

PR body:
```
Adds AI Integrity, an MIT-licensed SDK that produces tamper-evident audit
trails for AI agents with ready-made packs for:

- Israeli Banking (Bank of Israel Directive 369, 15 policies)
- Israeli Digital Health (Health Information Mobility Law 2024, 14 policies)
- Privacy Protection Amendment 13 + PPA AI Guidance
- EU AI Act Article 12 (mandatory from August 2026)

Each pack is a markdown file. Policies are authored in plain English + JSON
path expressions. Evidence exports are signed Ed25519 ZIPs that any auditor
can verify with `openssl`.

https://github.com/razel369/ai-integrity
```

---

## LIST 3: `jnv/awesome-law`

URL: https://github.com/jnv/awesome-law
Section (proposed): "Tech-law tooling / AI compliance"

PR title:
> Add AI Integrity — Free open-source tool for AI compliance evidence

PR body:
```
AI Integrity is a free, open-source (MIT) tool for producing the evidence
required by AI-specific regulations. It generates audit trails that satisfy:

- EU AI Act Article 12 (mandatory in EU from August 2026)
- Bank of Israel Directive 369 (model risk management)
- Israeli Privacy Protection Amendment 13 + PPA AI Guidance (2025)

The export is a self-contained signed bundle. Auditors and legal teams can
verify the cryptographic chain with `openssl` without installing anything.

https://github.com/razel369/ai-integrity

Suggested section: "Tech-law tooling / AI compliance"
```

---

## LIST 4: `kilimchoi/engineering-management`

URL: https://github.com/kilimchoi/engineering-management (or similar)
Section: "Compliance & security tools"

PR title:
> Add AI Integrity — Audit-trail SDK for AI agents (MIT)

PR body (short):
```
- AI Integrity: open-source Python SDK. Records every AI agent decision
  in a tamper-evident hash-chained log. Exports signed evidence bundles
  for regulators. Has packs for Israeli bank regulation, EU AI Act,
  Privacy Protection Amendment 13.

https://github.com/razel369/ai-integrity
```

---

## LIST 5: `protocol/Awesome-AI-Regulation`

(Search GitHub for similar lists — these get created regularly.)

PR title:
> Add Israeli compliance evidence tooling

PR body:
```
Adds a tooling entry for AI Integrity, an open-source (MIT) Python SDK for
producing tamper-evident audit trails of AI agent decisions, with ready-made
policies for:

- Bank of Israel Directive 369 (June 2026 update)
- Israeli Privacy Protection Amendment 13 + PPA AI Guidance (2025)
- EU AI Act Article 12

Export is a signed ZIP. Auditors can verify with `openssl`. No SaaS, no
sales call, no waiting for a demo.

https://github.com/razel369/ai-integrity
```

---

## POSTING WORKFLOW

For each list:

1. Open the URL above.
2. Fork the repo.
3. Find the appropriate README section.
4. Add one bullet following the format already in use.
5. Open PR with the body above (modify slightly per list style).
6. Reply to maintainer comments politely.

Expected outcomes:
- 3 of 5 PRs accepted within 2 weeks
- ~10-30 visitors per month from these lists (small but high-DR backlinks)
- SEO compound effect: every accepted list = +1 strong referring domain

---

## AUTHOR BIO SNIPPET

When DevRel or maintainers reply asking about the project, drop this:

```
Built by the team at https://github.com/razel369 — we ship open-source
compliance tooling for AI systems. Happy to answer technical questions on
the integration, the policy DSL, or the cryptographic chain verification.
```

(Keeps it short. Asks no for anything.)
