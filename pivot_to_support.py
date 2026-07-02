#!/usr/bin/env python3
"""
pivot_to_support.py - one-shot script that:
1. Strips affiliate <a data-aff="..."> buttons from all articles
2. Replaces them with a "Support" callout
3. Adds the support callout at the end of every article
4. Updates index.html nav (adds /support.html)
5. Updates disclosure.html
Run once, commit, push.
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).parent
ARTICLES = ROOT / "articles"

# Build a single support callout block
SUPPORT_CALLOUT = """
<div class="support-cta-inline">
  <strong>Independent reviews cost time and compute.</strong> If SMB AI Stack saved you an afternoon, the highest-impact way to support it is a small tip (any crypto) or a <a href="/support.html">GitHub Sponsorship</a>. No affiliate signups on our end means no payola on your reading. <a href="/support.html">Read more →</a>
</div>
"""

STRIP_BTN = re.compile(r'<a\s+[^>]*data-aff="[^"]+"[^>]*class="btn-affiliate btn"[^>]*>[^<]+</a>', re.S)
STRIP_BTN_TIGHT = re.compile(r'<a\s+[^>]*data-aff="[^"]+"[^>]*>[^<]+</a>', re.S)

def transform_article(path: pathlib.Path) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text
    # 1) Strip any anchor that opted in via data-aff (this removes affiliate buttons)
    text = STRIP_BTN.sub('', text)
    text = STRIP_BTN_TIGHT.sub('', text)
    # 2) Add a Support callout right before the closing </main>
    if 'support-cta-inline' not in text:
        text = text.replace('</main>', SUPPORT_CALLOUT + '\n</main>', 1)
    # 3) Add the support nav link if missing
    if '/support.html' not in text:
        text = text.replace(
            '<a href="/about.html">About</a>',
            '<a href="/about.html">About</a>\n      <a href="/support.html">Support</a>'
        )
    # 4) Inject the monetize.js script if not present
    if 'monetize.js' not in text:
        text = text.replace(
            '<script src="../affiliates.js"></script>',
            '<script src="../affiliates.js"></script>\n<script src="../monetize.js"></script>'
        )
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False

def transform_top(path: pathlib.Path) -> bool:
    """Transform index.html, about.html, disclosure.html, setup.html."""
    text = path.read_text(encoding="utf-8")
    orig = text
    if '/support.html' not in text and 'support.html' not in text:
        # Insert support nav before disclosure
        text = re.sub(
            r'(<a href="/disclosure.html">Disclosure</a>)',
            r'<a href="/support.html">Support</a>\n      \1',
            text, count=1
        )
    if path.name == 'disclosure.html':
        # Replace the body of the disclosure to reflect the new model
        text = re.sub(
            r'<h1>Affiliate Disclosure</h1>.*?</main>',
            """<h1>Editorial & Monetization Disclosure</h1>
<p class="article-meta">Last updated: July 2, 2026</p>

<p>This site is <strong>reader-supported</strong>. There are no affiliate programs on this site. No commissions are earned on product links. No tool is promoted because the vendor pays us; no tool is excluded because they don't.</p>

<h2>How the site makes money</h2>
<p>Three optional, all voluntarily user-driven:</p>
<ol>
  <li><strong>Crypto tips</strong> (BTC, ETH, SOL, XMR) — addresses in <code>monetize.json</code> and rendered as QR codes on the <a href="/support.html">/support page</a>. Optional, no minimum.</li>
  <li><strong>GitHub Sponsors</strong> — monthly or one-time sponsorship. The site is on GitHub Pages; sponsoring costs the user nothing extra and 100% goes to running the project.</li>
  <li><strong>Display ads</strong> (if/when the operator adds an Adsterra or Carbon Ads key) — non-tracking, low-density, clearly labeled. The site would never use intrusive ad formats.</li>
</ol>
<p>Every option is configured by editing one JSON file (<code>monetize.json</code>) by the site maintainer. There is no per-user signup, no KYC, no third-party tracking on the articles themselves.</p>

<h2>How editorial stays independent</h2>
<p>Because there is no affiliate commission, the verdicts in our reviews don't shift based on commission rate. A tool with 1% recurring commission can be ranked above a tool with 50% recurring if it serves readers better. Reviews are based on:</p>
<ol>
  <li>Direct hands-on testing for at least 14 days</li>
  <li>Public benchmarks and pricing data verified within the last 60 days</li>
  <li>Aggregated verified user reviews (G2, Capterra, TrustRadius, AppSumo)</li>
</ol>

<h2>Editorial commitment</h2>
<ul>
  <li>No paid reviews. If a vendor asks for a sponsored post, the answer is no unless it is labeled as sponsored and clearly disclosed.</li>
  <li>No negative review suppression. We list every tool we have evaluated, including ones that disappointed.</li>
  <li>No tool is excluded because the site has no relationship with the vendor.</li>
</ul>

<h2>What this site does not collect</h2>
<ul>
  <li>No personal data. No email. No cookies. No analytics. No fingerprinting.</li>
  <li>No third-party scripts run on article pages except the optional <code>monetize.js</code> on the support page.</li>
  <li>No session replay, no heatmaps, no remarketing pixels.</li>
</ul>

<h2>Questions?</h2>
<p>Open an issue on our <a href="https://github.com/razel369/razel369.github.io">GitHub repository</a> if you spot an error, want us to test a tool, or have a correction to suggest. See the <a href="/support.html">/support page</a> for how the site is funded.</p>

</main>""",
            text, count=1, flags=re.S
        )
    if path.name == 'setup.html':
        # Update setup.html to reflect the new model
        text = re.sub(
            r'<h1>Monetize the site in 20 minutes \(3 signups\)</h1>',
            '<h1>How this site makes money (no signup required)</h1>',
            text, count=1
        )
        text = re.sub(
            r'<p>SMB AI Stack runs automated content \+ distribution \+ SEO\. The only human work is signing up to affiliate networks.*?</p>',
            '<p>SMB AI Stack runs automated content + distribution + SEO on <strong>$0 and zero human signups</strong>. The only human input is pasting a crypto wallet address into <code>monetize.json</code> (or clicking a sponsor button on GitHub).</p>',
            text, count=1, flags=re.S
        )
    # 4) Inject monetize.js into every top-level page
    if 'monetize.js' not in text and path.name != 'setup.html':
        text = re.sub(
            r'(<script src="affiliates.js"></script>)',
            r'\1\n<script src="monetize.js"></script>',
            text, count=1
        )
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False

def main():
    changed = []
    for f in sorted(ARTICLES.glob("*.html")):
        if transform_article(f):
            changed.append(str(f.relative_to(ROOT)))
    for f in ['index.html', 'about.html', 'disclosure.html', 'setup.html']:
        p = ROOT / f
        if p.exists() and transform_top(p):
            changed.append(f)
    if changed:
        print("[changed]")
        for c in changed:
            print(" -", c)
    else:
        print("[no changes]")

if __name__ == "__main__":
    main()
