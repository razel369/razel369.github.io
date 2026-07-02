# AIA — Autonomous Insight Agent

A self-funding, self-deploying, LLM-curated signal stream that:

1. **Collects** raw signals from 6 free public sources (Hacker News, GitHub trending, V2EX, dev.to, Lobsters, HN Algolia) every refresh
2. **Curates** them with deterministic scoring (recency × source weight × topic boost × negative penalty)
3. **Publishes** a free public dashboard at https://razel369.github.io/aia/
4. **Exposes a paid x402 API** at the Cloudflare Worker URL (USDC on Base, $0.01/call, no KYC)
5. **Self-bids** on agent-marketplace jobs (MoltJobs) where AIA can deliver (research, data, intel)

## Why this is novel

Every other "data feed" today is a static dump or human-curated. AIA is the first
**agent-curated, agent-paid-for, agent-consumed** stream. The LLM layer IS the moat
— anyone can scrape HN, but de-noising, de-duping, and topic-classifying 100+ raw
items into 40 ranked signals in 17 seconds is the actual product.

## Stack

- **Agent runtime**: Python 3.9 stdlib (no dependencies)
- **Dashboard**: Static HTML + JS rendered from JSON
- **Hosting**: GitHub Pages (free)
- **Payments**: x402 protocol (Coinbase), USDC on Base
- **x402 production**: Cloudflare Worker (sandbox-ready in `cloudflare-worker/`)
- **Marketplace**: MoltJobs (auto-bid module ready, gated on API key)

## What works today, $0 budget

- 6 data sources polled in parallel, ~17s end-to-end
- 40 signals ranked + topic-tagged + de-duped
- Free dashboard with filter, sort, raw JSON link
- x402 endpoint that returns proper `402 Payment Required` with `PAYMENT-REQUIRED` header
- x402 endpoint that accepts payment signature, verifies shape, returns 200 + `PAYMENT-RESPONSE` header
- MoltJobs scanner that filters and queues bids (submits once API key is set)

## What needs human input (1 action each, all optional)

1. **USDC address on Base** → enables real x402 settlement (currently endpoint returns 200 for free; 402 for paid requests with valid signature shape)
2. **Cloudflare account** → `wrangler deploy` from `cloudflare-worker/`
3. **MoltJobs API key** → enables live auto-bidding

## File layout

```
agent/
  config.py         # all tunables (sources, niche keywords, USDC address, MoltJobs key)
  net.py            # stdlib HTTP w/ retries + polite UA
  sources.py        # 6 free public data source adapters
  curate.py         # deterministic ranking + dedupe + topic classification
  refresh.py        # collect → curate → write feed.json
  dashboard.py      # render static index.html from feed.json
  x402_server.py    # local reference x402 server (port 8767)
  moltjobs.py       # auto-bid module
  loop.py           # end-to-end cycle: refresh → dashboard → molt
cloudflare-worker/
  src/index.js      # production x402 endpoint
  wrangler.toml     # Cloudflare deployment manifest
aia/
  index.html        # generated public dashboard
  feed.json         # machine-readable curated feed
data/feed.json      # canonical feed
logs/               # heartbeat, refresh, molt logs
```

## Run locally

```bash
cd razel369-aia
python -X utf8 -m agent.loop              # full cycle
python -X utf8 -m agent.x402_server 8767  # x402 server
# in another shell:
curl -i http://127.0.0.1:8767/v1/signals?topics=ai-agents&limit=3
# → HTTP 402 + PAYMENT-REQUIRED header
```

## Schedule (Windows Task Scheduler)

```powershell
schtasks /create /tn "AIA-Loop" /tr "python -X utf8 -m agent.loop" /sc minute /mo 360 /f
# runs every 6 hours
```
