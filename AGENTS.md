# AGENTS.md

## Cursor Cloud specific instructions

This repository is a **static website** (deployed to GitHub Pages, note the `.nojekyll` file) plus a few Python/PowerShell helper scripts. There is **no build system, no package manager, and no lint/test framework** — nothing to compile and nothing to install beyond the Python 3 that is already present on the VM.

### Running the site (development)

Serve the repo root with any static file server, e.g.:

```
python3 -m http.server 8000
```

Then open `http://localhost:8000/`. You must serve over HTTP (not open files via `file://`) because `affiliates.js` / `monetize.js` fetch `/affiliates.json` and `/monetize.json` at runtime, which requires a web-server origin. Editing `affiliates.json` is the primary "configuration" step — it swaps every `data-aff` placeholder link across the site.

### Python helper scripts

`publish_devto.py`, `v2ex_bodies.py`, and `pivot_to_support.py` use **only the Python standard library** — do not add a `requirements.txt` or `pip install` step.

- `publish_devto.py` posts articles to the Dev.to API and requires a `DEVTO_API_KEY` env var. Use `python3 publish_devto.py --dry-run` to exercise it without a key or network writes.
- `v2ex_bodies.py` generates ready-to-paste drafts into `v2ex_output/`.

### Not runnable here

The `*.ps1` scripts (`add_content.ps1`, `check-domains.ps1`, etc.) are Windows PowerShell and are not runnable on this Linux VM unless `pwsh` is installed. They are content-authoring/publishing helpers, not part of serving the site.

### Known pre-existing content issue

Some article headings contain double-encoded UTF-8 (mojibake, e.g. `â€"` instead of an en-dash) baked into the committed HTML. This is a content/data bug in the source files, not an environment problem — GitHub Pages renders it identically. Do not "fix" it as part of environment setup.
