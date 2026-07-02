#!/usr/bin/env pwsh
# add_content.ps1 - run by me (the AI agent) on a schedule to add new articles.
# This is the long-term growth loop:
#   1. Research new low-competition buyer-intent keywords
#   2. Draft new article (1500-2000 words), affiliate links wired via data-aff
#   3. Render to HTML, add to articles/, regenerate sitemap.xml
#   4. Push to GitHub -> GitHub Pages picks up automatically (instant rebuild)
#   5. Run publish_devto.py to cross-post to Dev.to
#   6. Append new post body to next V2EX submission (rotate, don't spam)

param(
    [string]$Slug = "",
    [string]$Title = "",
    [string]$H1 = "",
    [string]$BodyMd = "",
    [string[]]$AffiliateSlugs = @(),
    [string[]]$InternalLinks = @()
)

# Usage examples (call me with these):
#   -Slug "best-ai-tools-for-coaches-2026" -Title "Best AI Tools for Coaches (2026)" -H1 "Best AI Tools for Coaches (2026)" -BodyMd "<the markdown body>" -AffiliateSlugs @("convertkit","systeme","jasper") -InternalLinks @("systeme-io-review-solopreneurs","best-ai-tools-for-small-business-2026")

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSCommandPath -Parent)

if (-not $Slug -or -not $Title -or -not $BodyMd) {
    Write-Host "Usage: add_content -Slug <slug> -Title <title> -H1 <h1> -BodyMd <md> -AffiliateSlugs <@()> -InternalLinks <@()>"
    exit 1
}

# Convert BodyMd (markdown) to HTML. We use a tiny inline converter to avoid any
# dependency installs. For richer formatting, swap in `npx marked` etc.
function ConvertTo-ArticleHtml {
    param([string]$Md, [string]$Title, [string]$H1, [string]$Slug)
    $html = ""
    $inCode = $false
    $buffer = ""
    foreach ($line in ($Md -split "`n")) {
        if ($line -match '^```') {
            if (-not $inCode) { $html += "`n<pre><code>" ; $inCode = $true } else { $html += "</code></pre>`n"; $inCode = $false }
            continue
        }
        if ($inCode) { $html += ($line.Replace("<","&lt;").Replace(">","&gt;") + "`n"); continue }
        if     ($line -match '^# (.*)$') { $html += "<h2>$($Matches[1])</h2>`n" }
        elseif ($line -match '^## (.*)$') { $html += "<h3>$($Matches[1])</h3>`n" }
        elseif ($line -match '^\s*- (.*)$') { $html += "<li>$($Matches[1])</li>`n" }
        elseif ($line -match '^\s*\d+\. (.*)$') { $html += "<li>$($Matches[1])</li>`n" }
        elseif ($line -match '^\| (.*) \|$') { $html += "$($line)`n" }
        elseif ($line.Trim() -eq "") { $html += "`n" }
        else { $html += "<p>$line</p>`n" }
    }
    $html = $html -replace '<p>(<h\d|<li>|</li>|</?ul>|<pre>)','$1' -replace '(</h\d>|</li>|</ul>|</pre>)</p>','$1'
    $html = $html -replace '\[([^\]]+)\]\(([^\)]+)\)','<a href="$2">$1</a>'

    return @"
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="$H1">
<meta name="robots" content="index, follow">
<meta property="og:title" content="$H1">
<meta property="og:description" content="$H1">
<meta property="og:type" content="article">
<title>$H1 — SMB AI Stack</title>
<link rel="canonical" href="https://razel369.github.io/articles/$Slug.html">
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
<header class="site-header"><div class="container"><a class="site-brand" href="/">SMB AI Stack</a><nav class="site-nav"><a href="/">Home</a><a href="/about.html">About</a><a href="/disclosure.html">Disclosure</a></nav></div></header>
<main class="container">
<div class="disclosure-banner"><strong>Disclosure:</strong> This article contains affiliate links. <a href="/disclosure.html">Read full disclosure →</a></div>

<h1>$H1</h1>
<p class="article-meta">Last updated: $(Get-Date -Format "MMMM d, yyyy")</p>

$html

<p>For the full SMB stack: <a href="best-ai-tools-for-small-business-2026.html">Best AI Tools for Small Business 2026</a>.</p>

</main>
<footer class="footer"><div class="container">SMB AI Stack · <a href="/disclosure.html">Affiliate disclosure</a> · <a href="/about.html">About</a></div></footer>
<script src="../affiliates.js"></script>
</body>
</html>
"@
}

$html = ConvertTo-ArticleHtml -Md $BodyMd -Title $Title -H1 $H1 -Slug $Slug
$out = "articles/$Slug.html"
$html | Out-File -Encoding utf8 -FilePath $out
Write-Host "[ok] wrote $out"

# Update sitemap.xml
$sitemap = (Get-Content "sitemap.xml" -Raw) -replace "</urlset>","  <url><loc>https://razel369.github.io/articles/$Slug.html</loc><priority>0.9</priority></url>`n</urlset>"
Set-Content -Path "sitemap.xml" -Value $sitemap -Encoding utf8
Write-Host "[ok] updated sitemap.xml"

# Update index.html (prepend a new <li> if missing)
$indexText = Get-Content "index.html" -Raw
$markup = "<li><a href=`"articles/$Slug.html`">$H1</a><div class=`"article-meta`">Last updated · 8 min read</div><div class=`"article-excerpt`">Independent review covering what works, what breaks, and who the article is for.</div></li>"
if ($indexText -notmatch [regex]::Escape("$Slug.html")) {
    $indexText = $indexText -replace "(<ul class=`"article-list`">)","`$1`n  $markup"
    Set-Content -Path "index.html" -Value $indexText -Encoding utf8
    Write-Host "[ok] updated index.html"
}

# Commit + push to GitHub
git add . | Out-Null
git -c user.email="agent@smbaistack.local" -c user.name="SMB AI Stack Agent" commit -m "Add article: $Slug" | Out-Null
git push origin main | Out-Null
Write-Host "[ok] pushed to GitHub -> Pages will rebuild automatically"
