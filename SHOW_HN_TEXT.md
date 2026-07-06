# Show HN Post — Final Copy (Eidot)

This is the exact text to submit to Hacker News today or tomorrow morning.

## URL TO SUBMIT

```
https://github.com/razel369/ai-integrity
```

## TITLE (in the form field, exactly as written)

```
Show HN: Eidot – Open-source tamper-evident audit trail for AI agents
```

## TEXT (the optional "text" field)

```
Author here. We just renamed and shipped the next version of this:
"Eidot" (עדות = "testimony" in Hebrew). The substance is the same,
but the name fits the Israeli market we're targeting first.

We built this because every AI agent governance tool we tried was either:

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
   every batch. Auditors verify with `openssl ed25519 -verify` — no SaaS, no
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
  text-only.
- Streaming response handling — partial outputs from streamed LLMs.
- Multi-agent orchestration — when agent A delegates to agent B, fork the
  chain or share it?

MIT-licensed. Repo: https://github.com/razel369/ai-integrity

Happy to discuss the chain scheme, the policy DSL grammar, or how
Israeli banking regulation shaped the design (we started from Bank of
Israel Directive 369).
```

---

## POSTING INSTRUCTIONS

1. Go to https://news.ycombinator.com/submit
2. Paste `https://github.com/razel369/ai-integrity` in the URL field
3. Paste title exactly as written
4. Paste text exactly as written
5. Submit
6. Be online for the first 4 hours to reply to comments.
7. Best time: Tuesday, Wednesday, or Thursday, 8-10 AM US Eastern.

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
> with a structured "if-then-action" inside it.

**Q: "What's the deployment story? Single-host or SaaS?"**
> Both. The SDK works against either your local instance or our hosted
> version at eidot.ai. Bundles are generated server-side. Self-host
> with Docker (one command).

**Q: "Does it integrate with LangChain / LlamaIndex / OpenAI Assistants?"**
> We have wrappers for LangChain tools (Python). OpenAI Assistants and
> LlamaIndex need minimal adapters — happy to write them on request.

**Q: "Is this free?"**
> MIT-licensed source. The hosted version (eidot.ai) is free up to
> ~1M events/month. Above that, we charge for storage (the actual cost).
> Self-host is unlimited.
