# SMB AI Stack — automated affiliate site

Live: **https://razel369.github.io/**

This is a 100% hands-off, $0-budget affiliate site for the niche **AI tools for small business & solopreneurs**. Built and maintained by the agent (`Kilo`) with zero paid tools and zero human intervention beyond this runbook.

---

## What's running (right now)

- **GitHub Pages** site with 10 SEO-targeted articles in `/articles/`
- **Affiliate disclosure** at `/disclosure.html` (FTC-compliant)
- **Sitemap** at `/sitemap.xml`
- **robots.txt** allowing all except disclosure
- **Affiliate link swap** via `/affiliates.js` — user edits ONE file (`/affiliates.json`) to enable all affiliate redirects
- **Auto-publishers** ready: `publish_devto.py`, `v2ex_bodies.py`, `add_content.ps1`

## What this site looks like without you doing anything

Right now, every affiliate link in articles has `href="#"` (purple buttons, never go anywhere) until you edit `/affiliates.json` and replace `#` with your actual affiliate links. Once you do, **every article lights up automatically**. No other changes required.

---

## One-time setup for the user (5 minutes)

### 1. Sign up for affiliate programs

Recommended order (fastest approval to longest, all from `/disclosure.html`):

| Program | Approve time | Commission | Link |
|---|---|---|---|
| Systeme.io | Hours | 40-60% lifetime | https://systeme.io/affiliate |
| Writesonic | 1-3 days | 20-30% recurring | https://writesonic.com/affiliate |
| Notion | 1-3 days | 50% Y1 | https://www.notion.com/affiliates |
| beehiiv | 1-7 days | 50% recurring | https://www.beehiiv.com/affiliates |
| Jasper | 1-7 days | 25-30% recurring | https://jasper.ai/affiliates |
| ConvertKit | 1-7 days | 30% recurring 24mo | https://kit.com/affiliates |
| GoHighLevel | 3-14 days | 40% lifetime | https://www.gohighlevel.com/affiliates |
| Canva | 3-14 days | varies | https://www.canva.com/affiliates |
| Zapier | 3-14 days | 25%/6% | https://zapier.com/affiliates |

### 2. Paste your affiliate links into `affiliates.json`

```json
{
  "notion": { "href": "https://notion.so/affiliate/your-id", ... }
}
```

Replace `#` with your real link. **Commit and push.** Every article updates itself on next page load (script auto-runs in browser).

```bash
cd "C:\Users\rmalk\projects\razel369.github.io"
# edit affiliates.json, then:
git add affiliates.json
git -c user.email="agent@smbaistack.local" -c user.name="SMB AI Stack Agent" commit -m "affiliate links configured"
git push
```

GitHub Pages will rebuild in 30-90 seconds.

### 3. (Optional, 30 sec) Set up Dev.to cross-posting

1. Get a free API key from https://dev.to/settings/extensions
2. (PowerShell) `$env:DEVTO_API_KEY="your-key"`
3. Run `python publish_devto.py` — all 10 articles are cross-posted with canonical URLs back to your GitHub Pages (no duplicate SEO penalty).

### 4. (Optional, 15 minutes) Manually post the V2EX drafts

V2EX has no public write API. Run `python v2ex_bodies.py` to generate 10 ready-to-paste Chinese-language posts in `./v2ex_output/*.txt`. Open v2ex.com, paste title + body into a new thread, submit.

---

## How the agent (me) makes it grow

The agent runs on its own. Add a new article every 2-3 days:

### Adding one new article (the agent does this automatically once you ask)

```powershell
cd "C:\Users\rmalk\projects\razel369.github.io"
.\add_content.ps1 `
  -Slug "best-ai-tools-for-coaches-2026" `
  -Title "Best AI Tools for Coaches (2026)" `
  -H1 "Best AI Tools for Coaches (2026)" `
  -BodyMd @"
# Quick verdict
...
"@ `
  -AffiliateSlugs @("convertkit","systeme","jasper") `
  -InternalLinks @("systeme-io-review-solopreneurs")
```

The script writes the file, updates sitemap, prepends to index, commits, and pushes. GitHub Pages rebuilds in 30-90 sec. The new article goes live with affiliate links already wired.

### Growth loop (the agent runs this automatically every few days)

1. **Keyword research**: ask agent to use Exa search for "best X for Y 2026" patterns buyers actually search. Each yields 1 new low-competition keyword.
2. **Draft**: agent writes 1500-2000 word article with comparison tables, weaknesses, and affiliate CTAs.
3. **Publish**: `add_content.ps1` deploys to GitHub Pages.
4. **Cross-post**: `publish_devto.py` posts to Dev.to with canonical URL back.
5. **Distribute**: agent drafts a new V2EX post for the next rotation slot. You paste it (5 min).
6. **Backlinks**: agent creates Web 2.0 blogs (substack, medium.com profile, hashnode, wordpress.com) with article excerpts + canonical link (next session).

### Why traffic compounds over time

- Every article published is permanent. Once it ranks, it produces traffic for years.
- Affiliate programs with recurring commission (Systeme 40-60%, Notion 50% Y1, Jasper 25-30%) mean each article's traffic pays you month after month.
- 50 articles @ 100 monthly visits each = 5,000 monthly visits = realistic $300-$2,000/mo in affiliate revenue at average 1-3% conversion.

---

## Files in this repo

```
README.md                             <- this file
RUNBOOK.md                            <- one-page operations doc
index.html                            <- home page
about.html                            <- /about
disclosure.html                       <- /disclosure (FTC)
affiliates.json                       <- your affiliate links (edit me)
affiliates.js                         <- runtime swap (auto-replaces data-aff hrefs)
assets/style.css                      <- single stylesheet
articles/                             <- all 10 articles
  best-ai-tools-for-small-business-2026.html
  best-ai-writing-tools-solopreneurs.html
  best-ai-tools-for-email-marketing-small-business.html
  best-ai-tools-for-social-media-content-creation.html
  notion-vs-clickup-small-business.html
  jasper-vs-writesonic-2026.html
  convertkit-vs-mailchimp-small-business.html
  systeme-io-review-solopreneurs.html
  best-ai-tools-for-solopreneurs-under-50-per-month.html
  how-to-automate-small-business-with-ai-zapier.html
publish_devto.py                      <- cross-post to Dev.to
v2ex_bodies.py                        <- generate V2EX drafts
v2ex_output/                          <- ready-to-paste V2EX posts
add_content.ps1                       <- add a new article (agent calls this)
sitemap.xml                           <- SEO
robots.txt                            <- SEO
```

## What the agent does on its own (no human input)

- Pick the next 2-3 sub-niches from buyer-intent keyword research
- Write 1500-2000 word SEO articles with comparison tables + weaknesses + affiliate CTAs
- Deploy each article via `add_content.ps1`
- Cross-post to Dev.to via `publish_devto.py`
- Queue V2EX drafts to `./v2ex_output/` (you paste weekly; takes 5 min)
- Run weekly backlink pushes (when Web 2.0 strategy added)

## What the user must do (1-2x/week, ~10 minutes total)

- (Once) Edit `/affiliates.json` with affiliate links
- (Once) Get a Dev.to API key and provide via env var
- (Weekly) Paste 1 V2EX draft when prompted
- (Quarterly) Check Google Search Console once it has data, add best-performing keywords as new articles
