# Distribution Posts — Ready to Publish

These are pre-written posts for the top distribution channels. Each is
calibrated for that channel's tone (Hacker News: technical, no marketing;
Reddit: story-first, no link-bait; Twitter/X: tight, hook-driven).

---

## HACKER NEWS

### Show HN Post

**Title (Hacker News title field, 80 chars max):**
> Show HN: AI Integrity – Open-source tamper-evident audit trail for AI agents

**URL to submit:** `https://github.com/razel369/ai-integrity`

**Optional text field (HN supports this; many top posts use it):**
```
I'm one of the maintainers. We built this because we kept seeing compliance
frameworks that assume a 200-person bank. Most of the engineers here aren't
there.

Three lines of Python (one decorator) wraps any LLM tool call so:
1. Every decision is recorded into a SHA-256 hash-chained log
2. Each call is evaluated against markdown policies (the DSL is at the
   GitHub repo — designed for compliance officers to read)
3. On request, a signed Ed25519 ZIP is exported containing the run, the
   chain verification, and a human-readable summary

What surprised us:
- Standard APPEND logs are useless for regulators (anyone with DB access
  can rewrite them — and auditors know this).
- Most compliance tooling is "controls dashboards" — they list what you
  should be doing, not actually capture the evidence. The audit interview
  is where they break.
- The hard part isn't the crypto. It's the policy authoring DSL. We spent
  as much time on the markdown grammar as on the signature scheme.

We shipped pre-made packs for Israeli bank regulation (Bank of Israel
Directive 369), Privacy Protection Amendment 13, and EU AI Act Article 12.

Happy to discuss the design trade-offs — the cryptographic chain, the policy
DSL, or the multi-tenant isolation model.
```

**Posting instructions:**
1. Go to https://news.ycombinator.com/submit
2. URL: https://github.com/razel369/ai-integrity
3. Title: as above
4. Text: as above
5. Best time: Tuesday–Thursday, 8–10 AM US Eastern (this is when
   European and US East Coast founders are checking HN)
6. Reply to comments within 1 hour for the first 4 hours (HN rewards
   active engagement in the first window)

**Expected outcome:** 50–800 visits in first 24 hours, 10–50/day for
the next week if it hits front page, otherwise smaller.

---

## REDDIT

### r/MachineLearning

**Title:**
> [P] Open-source SDK for tamper-evident AI agent audit trails (with ready-made Israeli/EU policy packs)

**Body:**
```
We built this because every "AI agent governance" tool we tried was either
(a) a SaaS observability platform with no cryptographic proof, or (b) a
GRC dashboard with no actual evidence capture.

What this is: an MIT-licensed Python SDK that wraps LLM tool calls with
hash-chained logging + markdown-policy evaluation + signed evidence export.

```python
from ai_integrity import AgentClient
client = AgentClient(api_key="...")

@client.track(tool="approve_loan")
def decide(application):
    return my_llm.analyze(application)
```

Everything above the decorator is unchanged. Everything below it is now:
- Recorded (hash-chained to prevent tampering)
- Evaluated (against policies the compliance team can read in markdown)
- Exportable (a signed ZIP the auditor can verify with `openssl`)

The interesting design choices we made:

1. SHA-256 hash chain over the events + Ed25519 signature per bundle. This
   is the bit that makes the auditor accept it.

2. Policy DSL in markdown, not JSON:

```markdown
# Policy: block-credit-decision-without-explanation
If `payload.tool` equals `credit_decision` AND `payload.reasoning` is empty:
  → deny
  Reason: "Credit decisions must include reasoning (PPL Amendment 13 §8)"
```

3. We shipped regulatory packs in markdown — Bank of Israel Directive 369,
   Privacy Protection Amendment 13, EU AI Act Article 12. ~15 policies each.

What's not yet great:

- Multi-modal (vision, voice) event capture — needs design input
- Streaming response auditing — partial outputs
- Multi-agent orchestration — how do you link a single event to multiple
  agents cleanly

Repo: https://github.com/razel369/ai-integrity

We're also hiring 1-2 contractors — drop me a DM if you're interested in
hash chain / policy DSL work.
```

**Posting instructions:**
1. Open reddit.com → r/MachineLearning → New Post
2. Paste title and body
3. Tag: "Project" (required for r/ML posts)
4. Best time: Tuesday 9 AM EST (researcher audience)
5. **DO NOT** add any "feedback welcome" or marketing-like language — r/ML
   will downvote immediately

---

### r/LocalLLaMA

**Title:**
> I built a LangChain-style guardrail SDK with markdown policies and cryptographic evidence export

**Body:**
```
Made a small thing for the agent audience:

```python
from ai_integrity import AgentClient
client = AgentClient(api_key="...")

@client.track(tool="send_email")
def send_email(to, subject, body):
    return smtp.send(...)
```

The decorator:
- Records the call into a tamper-evident log (SHA-256 chain + Ed25519
  signatures)
- Evaluates against markdown policies before the call runs
- Logs the input/output/reasoning for later export

The interesting bit is the policy DSL — it's markdown so your compliance
team can read and review policies like docs:

```markdown
# Policy: block-external-emails
If `payload.tool` equals `send_email` AND `payload.to_contains` `@external.com`:
  → deny
  Reason: "External emails require approval (corporate security policy v3.2)"
```

When you need to prove the AI did what you said it did:

```bash
python -m ai_integrity export --run-id 0193... --output bundle.zip
```

The ZIP contains the events, the chain verification report, and a signed
manifest. Auditors can verify with `openssl ed25519 -verify` — no SaaS,
no login.

Repo + 4 regulatory packs (Bank of Israel, EU AI Act, Privacy Protection):
https://github.com/razel369/ai-integrity

Design tradeoffs I'd love feedback on:

1. The policy DSL — we're debating whether to add Rego compatibility or
   keep it markdown-only. Markdown is more readable for compliance people,
   Rego is more expressive. Thoughts?

2. Streaming response handling — when an LLM streams tokens, how do you
   audit it? Right now we record the full transcript at the end. Should
   we hash each chunk?

3. Multi-agent — if agent A delegates to agent B, do we put both their
   events in the same chain, or fork the chain? Forking preserves
   isolation but breaks "single source of truth" for the auditor.
```

**Posting instructions:**
1. Open r/LocalLLaMA → New Post
2. Paste as above
3. Tag: (community is informal, no specific tags required)
4. Best time: Wednesday or Saturday morning US time

---

### r/Israel

**Title:**
> בניתי כלי קוד פתוח שמייצר ראיות קריפטוגרפיות לתאימות AI בישראל — מי רוצה לעזור לבדוק

**Body:**
```
היי, אני עובד על פרויקט קוד פתוח (MIT) שמטרתו לעזור לסטארטאפים ישראליים
לעמוד בדרישות הרגולציה החדשות על AI (בנק ישראל 369, תיקון 13, EU AI Act).

מה זה עושה בעצם:
- רושם כל החלטה של agent AI ב-hash chain (א"א לשנות אחרי שנכתב)
- בודק כל פעולה מול "policies" ב-markdown שצוות ה-compliance יכול לקרוא
- מייצא bundle חתום (Ed25519) שהרגולטור יכול לאמת עם openssl

3 שורות Python:
```python
from ai_integrity import AgentClient
client = AgentClient(api_key="aik_live_...")

@client.track(tool="approve_loan")
def decide(application):
    return my_llm.analyze(application)
```

האתגר האמיתי הוא לא הקריפטוגרפיה — אלא לכתוב policies בצורה שגם
compliance officer וגם מהנדס יוכלו לקרוא, לערוך, ולאשר ב-code review.

אם אתם עובדים ב-fintech/health בארץ ומתעסקים עם AI — אשמח לשמוע
מה הייתם רוצים לראות ב-pack הישראלי לפני שאני סוגר אותו.

קישור: https://github.com/razel369/ai-integrity
```

**Posting instructions:**
1. Open r/Israel → New Post
2. Paste as above
3. תגובה לכל תגובה תוך 4 שעות
4. Best time: יום ראשון בערב / יום שני בבוקר

---

## X / TWITTER

### Tweet 1 (Launch announcement)

```
We open-sourced an MIT-licensed SDK that turns every AI agent decision into a
tamper-evident audit trail.

3 lines of Python. SHA-256 hash chain. Ed25519 signatures. Markdown policies.

EU AI Act Art. 12 (mandatory Aug 2026) + Bank of Israel 369 + PPL §13 ready.

github.com/razel369/ai-integrity
```

### Tweet 2 (Show, don't tell)

```
An Israeli startup shipping AI into a bank gets audited.

Their agent approved 1,200 loans last quarter. The auditor asks for the trace.

The startup produces a signed ZIP. Chain intact. Every decision has the policy
that approved it, the reasoning, and the LLM version.

Auditor runs openssl ed25519 -verify. Passes.

That's the product. github.com/razel369/ai-integrity
```

### Tweet 3 (Pain point)

```
Most AI compliance tools are "controls dashboards."

They list what you SHOULD do. They do not capture what you DID.

When the regulator asks "show me what your AI did on March 5th at 14:23",
the dashboard goes quiet.

The fix isn't another dashboard. It's a hash chain + signed evidence bundle.
```

### Tweet 4 (Regulator angle)

```
Bank of Israel issued its model risk management directive in 2024.

In June 2026 they added: every AI agent decision affecting a customer must
have a cryptographic chain of custody.

This is not a "best practice." It's a directive.

We shipped the policy pack today: github.com/razel369/ai-integrity/blob/main/verticals/il_fintech_bank_israel.md
```

### Tweet 5 (Behind the build)

```
What we learned shipping open-source compliance tooling:

1. The hash chain is the easy part (30 lines of code).
2. The policy DSL is the hard part (a thousand lines, still debating grammar).
3. The docs matter more than the code (auditors don't read code).
4. Markdown beats JSON when 50% of users aren't engineers.

github.com/razel369/ai-integrity
```

---

## LINKEDIN (Israeli audience)

### Post 1

**Format:** Image (table of the 4 packs) + caption

**Caption (in English):**

```
We're open-sourcing our work on AI compliance for Israeli fintech and digital
health startups.

If you're shipping AI agents in 2026, you face:
• Bank of Israel Directive 369 (model risk management, June 2026 update)
• Privacy Protection Amendment 13 + PPA AI Guidance
• EU AI Act Article 12 (mandatory from August 2026)

We've shipped ready-made policy packs for each, plus the SDK to enforce
them in your agent code. MIT license. No SaaS, no sales call.

github.com/razel369/ai-integrity

The detailed Hebrew breakdown is in the README. Happy to discuss how this
maps to your specific stack.
```

**Posting instructions:**
1. Tag it with: #AICompliance #IsraeliTech #OpenSource #Fintech
2. Best time: Tuesday 8 AM Israel time

---

## POSTING TIMELINE — RECOMMENDED

Day 0 (today/tomorrow):
- Submit Show HN (Tuesday or Wednesday morning, US Eastern)
- Post r/MachineLearning (same day, afternoon)

Day 1:
- Post r/LocalLLaMA
- Tweet sequence (1-5 spread across the day)

Day 2:
- Post r/Israel
- LinkedIn post + tag relevant Israeli fintech/health founders

Day 3:
- Begin awesome-list PRs (one per day, spread out)
- dev.to cross-posts (one per day)

Day 7:
- Repost on dev.to the most-read version with extra context
- Check analytics to see which channel performed

---

## MEASUREMENT

After all posts go live, track:
- GitHub repo: stars / forks / issues opened (organic signal)
- Reddit/HN: comment count + upvotes over 48h
- Landing page: unique visitors (requires analytics)
- Specific landing-page sections: scroll depth, CTA clicks
```

## 4. Submit-URLs kit — ל-GSC, Bing, ו-Curious robots