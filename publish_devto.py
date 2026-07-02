#!/usr/bin/env python3
"""
publish_devto.py - cross-post articles from the site to Dev.to via API.

Setup (one-time):
1. Go to https://dev.to/settings/extensions and copy your API key.
2. Set the env var:  $env:DEVTO_API_KEY="your-key-here"   (PowerShell)
   Or:               export DEVTO_API_KEY=your-key-here  (bash)
3. Edit FRONTMATTER below for each article (canonical_url etc are auto).

Usage:
  python publish_devto.py                  # publish all undrafted articles
  python publish_devto.py best-ai-tools   # publish specific slug(s)
  python publish_devto.py --dry-run        # show payloads, do not post

After running, the article appears on dev.to under your username, and the
canonical URL points back to razel369.github.io to avoid duplicate-content SEO issues.
"""
import os, sys, json, urllib.request, urllib.error, pathlib, re, time

API = "https://dev.to/api/articles"
ROOT = pathlib.Path(__file__).parent / "articles"

# Edit per article if needed. canonical_url is auto-built.
PIPELINE = [
    "best-ai-tools-for-small-business-2026",
    "best-ai-writing-tools-solopreneurs",
    "notion-vs-clickup-small-business",
    "jasper-vs-writesonic-2026",
    "convertkit-vs-mailchimp-small-business",
    "systeme-io-review-solopreneurs",
    "best-ai-tools-for-email-marketing-small-business",
    "best-ai-tools-for-social-media-content-creation",
    "best-ai-tools-for-solopreneurs-under-50-per-month",
    "how-to-automate-small-business-with-ai-zapier",
]

def html_to_markdown(html: str) -> str:
    """Minimal HTML -> Markdown so dev.to accepts plain text."""
    html = re.sub(r"<h1[^>]*>(.*?)</h1>", r"# \1\n", html, flags=re.S)
    html = re.sub(r"<h2[^>]*>(.*?)</h2>", r"## \1\n", html, flags=re.S)
    html = re.sub(r"<h3[^>]*>(.*?)</h3>", r"### \1\n", html, flags=re.S)
    html = re.sub(r"<strong>(.*?)</strong>", r"**\1**", html, flags=re.S)
    html = re.sub(r"<em>(.*?)</em>", r"*\1*", html, flags=re.S)
    html = re.sub(r"<pre><code[^>]*>(.*?)</code></pre>", r"```\n\1\n```\n", html, flags=re.S)
    html = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", html, flags=re.S)
    html = re.sub(r"<a\s+[^>]*data-aff=\"[^\"]*\"[^>]*href=\"#\"[^>]*>(.*?)</a>", r"\1", html, flags=re.S)
    html = re.sub(r"<a\s+[^>]*href=\"#\"[^>]*>(.*?)</a>", r"\1", html, flags=re.S)
    html = re.sub(r"<a\s+[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", r"[\2](\1)", html, flags=re.S)
    html = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1", html, flags=re.S)
    html = re.sub(r"<[uo]l[^>]*>", "", html)
    html = re.sub(r"</[uo]l>", "", html)
    html = re.sub(r"<table[^>]*>", "", html); html = re.sub(r"</table>", "", html)
    html = re.sub(r"<tr[^>]*>", "", html); html = re.sub(r"</tr>", "\n", html)
    html = re.sub(r"<t[hd][^>]*>", "| ", html); html = re.sub(r"</t[hd]>", " ", html)
    html = re.sub(r"<[^>]+>", "", html)
    html = re.sub(r"&nbsp;", " ", html); html = re.sub(r"&amp;", "&", html)
    html = re.sub(r"&middot;", "-", html); html = re.sub(r"&#39;", "'", html)
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()

def post(slug: str, key: str, dry: bool):
    path = ROOT / f"{slug}.html"
    if not path.exists():
        print(f"[skip] {slug}: not found at {path}")
        return
    html = path.read_text(encoding="utf-8")
    body_html = re.search(r'<main class="container">(.*?)</main>', html, re.S)
    if not body_html: body_html = re.search(r'<main>(.*?)</main>', html, re.S)
    if not body_html:
        print(f"[skip] {slug}: no <main> block")
        return
    body = html_to_markdown(body_html.group(1))
    title = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S).group(1).strip()
    canonical = f"https://razel369.github.io/articles/{slug}.html"
    payload = {
        "article": {
            "title": title,
            "body_markdown": body + f"\n\n*Originally published at [{canonical}]({canonical}).*",
            "canonical_url": canonical,
            "published": True,
            "tags": ["ai", "saas", "smallbusiness", "productivity"],
        }
    }
    if dry:
        print(f"--- DRY {slug} ---")
        print(json.dumps(payload, indent=2)[:500] + "\n...")
        return
    req = urllib.request.Request(API, data=json.dumps(payload).encode(),
        headers={"api-key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            print(f"[ok] {slug}: HTTP {r.status}")
    except urllib.error.HTTPError as e:
        print(f"[err] {slug}: HTTP {e.code} {e.read()[:300].decode(errors='ignore')}")

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    key = os.environ.get("DEVTO_API_KEY", "").strip()
    if not dry and not key:
        print("Set DEVTO_API_KEY environment variable. Use --dry-run to preview without a key.")
        sys.exit(1)
    targets = args or PIPELINE
    for slug in targets:
        post(slug, key, dry)
        time.sleep(1)

if __name__ == "__main__":
    main()
