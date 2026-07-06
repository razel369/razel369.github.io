# Show HN Post — Final Copy

This is the exact text to submit to Hacker News today or tomorrow morning.

## URL TO SUBMIT

```
https://github.com/razel369/ai-integrity
```

## TITLE (in the form field, exactly as written)

```
Show HN: AI Integrity – Open-source tamper-evident audit trail for AI agents
```

(80 chars max; Hacker News-style — lowercase, concrete, no marketing)

## TEXT (the optional "text" field — Hacker News posts that include
context tend to get more engagement)

```
Author here. We built this because every AI agent governance tool we tried
was either:

(a) A SaaS observability platform (Langfuse, Helicone) — great for
    engineers, useless for regulators. Standard APPEND logs can be edited
    by anyone with DB access. Auditors know this and reject them.

(b) A "compliance dashboard" (Vanta, Drata, Secureframe) — lists what
    you should do. Does not capture what you did. The interview where the
    auditor asks "show me what your AI did on March 5th at 14:23" is
    where they break.

(c) An enterprise GRC platform (OneTrust, RSA Archer) — assumes you have
    a 200-person bank. We don't.

So we shipped this:

  • 3-line Python decorator that wraps any LLM tool call
  • SHA-256 hash-chained audit log (tampering any record breaks the chain)
  • Ed25519-signed evidence bundle (single ZIP, verifiable with openssl)
  • Markdown policy DSL (compliance officers can read and review it)
  • Pre-made regulatory packs (Bank of Israel Directive 369, Privacy
    Protection Amendment 13, EU AI Act Article 12, internal KYC)

The interesting design choices that took the most thought:

1. The chain has to be cryptographic, not just append-only. Hash + signature
   every batch. Auditors verify with openssl ed25519 -verify — no SaaS, no
   trust required.

2. Policies are markdown, not JSON. We debated this for 6 weeks. We landed
   on markdown because:
   - Compliance teams speak English, not JSON
   - Auditors need to be able to read them in a review meeting
   - Git diff-ability is the actual working feature

3. The export format is a ZIP, not an API. The auditor is not going to log
   into your SaaS to verify a signature. Give them a file they can
   verify offline forever.

What's not great yet (we'd love feedback):

- Multi-modal events (vision, voice, audio) — our current event schema is
  text-only. Designing the right abstraction for "what was the input?"
  when input is a video is non-trivial.
- Streaming response handling — partial outputs from streamed LLMs.
- Multi-agent orchestration — when agent A delegates to agent B, do we
  put both events in one chain or fork?

MIT-licensed. Repo: https://github.com/razel369/ai-integrity

Happy to discuss the chain scheme, the policy DSL grammar, or how we
decided the export format.
```

---

## POSTING INSTRUCTIONS

1. Go to https://news.ycombinator.com/submit
2. Paste `https://github.com/razel369/ai-integrity` in the URL field
3. Paste title exactly as written
4. Paste text exactly as written
5. Submit
6. Be online for the first 4 hours to reply to comments. HN rewards
   engagement in the early window — the difference between top-of-front-page
   and page 10 is often just the author being present for questions.
7. Best time: Tuesday, Wednesday, or Thursday, 8-10 AM US Eastern (when
   European + US East Coast audiences overlap).

## WHAT TO DO AFTER IT POSTS

Within 30 minutes of any comment, respond. Common questions and prepared answers:

**Q: "How is this different from Langfuse?"**
> We do observability (like Langfuse) PLUS we capture cryptographic proof
> of non-tampering. Langfuse's logs can be edited by anyone with DB access
> — and any auditor will tell you that's a deal-breaker. We hash-chain
> every event and sign the bundle. If a record changes after the fact,
> the chain breaks — auditors verify with `openssl ed25519 -verify`, no
> trust required.

**Q: "Why markdown for policies? That's a weird choice."**
> We tried both. JSON is what engineers love. But the moment a regulator
> needs to review a policy, JSON fails — they don't know the syntax, the
> tooling, the schema. Markdown reads like an English policy document
> with a structured "if-then-action" inside it. Compliance teams can edit
> it directly in their normal tool. Reviewers can review in code review.
> The grammar is small and well-defined.

**Q: "What's the deployment story? Single-host or SaaS?"**
> Both. The SDK works against either your local instance or our hosted
> version. Bundles are generated server-side. Self-host with Docker
> (one command). For most teams starting out, the hosted version is the
> fastest path — one API key, 5 minutes.

**Q: "Does it integrate with LangChain / LlamaIndex / OpenAI Assistants?"**
> We have wrappers for LangChain tools (Python). OpenAI Assistants and
> LlamaIndex need minimal adapters — happy to write them on request.
> The model is "wrap any function with a decorator", so any function can
> be audited.

**Q: "Is this free?"**
> MIT-licensed source. The hosted version is free up to ~1M events/month.
> Above that, we charge for storage (which is the actual cost). Self-host
> is unlimited.

## IF IT GETS NO TRACTION

Possible reasons and fixes:
- Title too vague → edit and resubmit (HN allows resubmit after 24h)
- Posted wrong time → wait until Tuesday morning
- Posted without text → resubmit with text
- Audience mismatch → try /r/MachineLearning instead

Most posts that don't make front page get 20-100 visits in 24 hours from
HN alone. Even an "unsuccessful" Show HN is worth the 5 minutes.
