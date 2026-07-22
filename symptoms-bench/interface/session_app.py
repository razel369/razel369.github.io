#!/usr/bin/env python3
"""Local web UI to automate SymptomsBench chat-interface grading.

Usage:
  python3 interface/session_app.py
  # open http://127.0.0.1:8765
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from session_lib import (  # noqa: E402
    load_session,
    next_pending,
    read_prompt,
    save_session,
    submit_reply,
    summary,
    task_ids,
    write_scorecard,
)

HOST = "127.0.0.1"
PORT = 8765

HTML = r"""<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>SymptomsBench Session</title>
<style>
  :root {
    --bg: #0f1419;
    --panel: #1a222c;
    --line: #2c3845;
    --text: #e7eef7;
    --muted: #93a4b7;
    --accent: #3dd6c6;
    --good: #3ecf8e;
    --bad: #ff6b6b;
    --warn: #f0c14b;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; font-family: "Segoe UI", "Heebo", sans-serif;
    background: radial-gradient(1200px 600px at 10% -10%, #1b2a33, var(--bg));
    color: var(--text); min-height: 100vh;
  }
  .wrap { max-width: 1100px; margin: 0 auto; padding: 24px; }
  h1 { margin: 0 0 6px; font-size: 1.6rem; }
  .sub { color: var(--muted); margin-bottom: 18px; }
  .grid { display: grid; grid-template-columns: 280px 1fr; gap: 16px; }
  @media (max-width: 860px) { .grid { grid-template-columns: 1fr; } }
  .card {
    background: color-mix(in srgb, var(--panel) 92%, black);
    border: 1px solid var(--line); border-radius: 14px; padding: 14px;
  }
  .task {
    display: flex; justify-content: space-between; gap: 8px;
    padding: 8px 10px; border-radius: 10px; cursor: pointer;
    border: 1px solid transparent; margin-bottom: 6px;
  }
  .task:hover { background: #222c37; }
  .task.active { border-color: var(--accent); background: #203039; }
  .badge { font-size: 12px; padding: 2px 8px; border-radius: 999px; border: 1px solid var(--line); }
  .badge.passed { color: var(--good); border-color: #245c40; }
  .badge.failed { color: var(--bad); border-color: #6d3030; }
  .badge.retry { color: var(--warn); border-color: #6d5a20; }
  .badge.pending { color: var(--muted); }
  .row { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0; }
  button, .btn {
    background: #243140; color: var(--text); border: 1px solid var(--line);
    border-radius: 10px; padding: 10px 12px; cursor: pointer; font: inherit;
  }
  button.primary { background: linear-gradient(135deg, #1f8f84, #2bb8a8); border: 0; color: #041512; font-weight: 700; }
  button.ghost { background: transparent; }
  button:disabled { opacity: .5; cursor: not-allowed; }
  input, textarea {
    width: 100%; background: #101820; color: var(--text);
    border: 1px solid var(--line); border-radius: 10px; padding: 10px; font: inherit;
  }
  textarea { min-height: 220px; direction: ltr; text-align: left; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
  pre {
    direction: ltr; text-align: left; white-space: pre-wrap; word-break: break-word;
    background: #101820; border: 1px solid var(--line); border-radius: 10px;
    padding: 12px; max-height: 260px; overflow: auto; font-size: 12px;
  }
  .stats { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; }
  .stat { min-width: 110px; }
  .stat b { display: block; font-size: 1.3rem; }
  .ok { color: var(--good); } .no { color: var(--bad); }
  .hint { color: var(--muted); font-size: .92rem; }
  label { display:block; margin: 8px 0 4px; color: var(--muted); font-size: .9rem; }
</style>
</head>
<body>
<div class="wrap">
  <h1>SymptomsBench Session</h1>
  <div class="sub">העתק פרומפט → הדבק בצ׳אט של המודל → הדבק תשובה כאן → ציון אוטומטי</div>

  <div class="stats card" id="stats"></div>

  <div class="card" style="margin-bottom:16px">
    <div class="row">
      <label style="margin:0">שם מודל</label>
      <input id="model" placeholder="e.g. Fable 5 / Claude / GPT..." style="max-width:320px"/>
      <label style="margin:0">max attempts</label>
      <input id="maxAttempts" type="number" min="1" max="10" value="3" style="max-width:90px"/>
      <button onclick="saveMeta()">שמור הגדרות</button>
      <button class="ghost" onclick="copyText(systemText, 'SYSTEM')">העתק SYSTEM</button>
      <button class="ghost" onclick="jumpNext()">המשימה הבאה</button>
    </div>
    <div class="hint">טיפ: אם אין System role — לחץ "העתק COMBINED" בכל משימה.</div>
  </div>

  <div class="grid">
    <div class="card" id="list"></div>
    <div class="card">
      <h2 id="title" style="margin-top:0">בחר משימה</h2>
      <div class="row">
        <button onclick="copyPrompt('user')">העתק USER</button>
        <button onclick="copyPrompt('combined')">העתק COMBINED</button>
        <button class="ghost" onclick="showPrompt('user')">הצג USER</button>
      </div>
      <pre id="promptView">(הפרומפט יופיע כאן)</pre>

      <label>תשובת המודל</label>
      <textarea id="reply" placeholder="<<<FILE module.py>>>&#10;...&#10;<<<END>>>"></textarea>
      <div class="row">
        <button class="primary" id="gradeBtn" onclick="grade()">שמור + דרג</button>
        <button class="ghost" id="copyRetry" style="display:none" onclick="copyText(retryPrompt, 'RETRY')">העתק RETRY prompt</button>
      </div>
      <div id="result" class="hint" style="margin-top:10px"></div>
      <pre id="retryView" style="display:none"></pre>
    </div>
  </div>
</div>
<script>
let state = null;
let current = null;
let systemText = '';
let retryPrompt = '';

async function api(path, opts) {
  const res = await fetch(path, opts);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function badge(status) {
  return `<span class="badge ${status}">${status}</span>`;
}

function render() {
  const s = state.summary;
  document.getElementById('stats').innerHTML = `
    <div class="stat"><b>${s.passed}/${s.total}</b> resolved</div>
    <div class="stat"><b>${s.attempted}</b> attempted</div>
    <div class="stat"><b>${s.pending}</b> pending</div>
    <div class="stat"><b>${Math.round(s.resolve_rate*100)}%</b> rate</div>`;
  document.getElementById('model').value = state.session.model_name || '';
  document.getElementById('maxAttempts').value = state.session.max_attempts || 3;
  systemText = state.system;

  const list = document.getElementById('list');
  list.innerHTML = '<h3 style="margin-top:0">משימות</h3>' + state.tasks.map(t => `
    <div class="task ${t.id===current?'active':''}" onclick="selectTask('${t.id}')">
      <span>${t.id}</span>${badge(t.status)}
    </div>`).join('');

  if (!current) current = state.next || state.tasks[0]?.id;
  if (current) {
    document.getElementById('title').textContent = current;
  }
}

async function refresh() {
  state = await api('/api/state');
  render();
  if (current) await showPrompt('user');
}

async function selectTask(id) {
  current = id;
  retryPrompt = '';
  document.getElementById('copyRetry').style.display = 'none';
  document.getElementById('retryView').style.display = 'none';
  document.getElementById('result').textContent = '';
  document.getElementById('reply').value = '';
  render();
  await showPrompt('user');
}

async function showPrompt(kind) {
  if (!current) return;
  const data = await api(`/api/prompt?task=${encodeURIComponent(current)}&kind=${kind}`);
  document.getElementById('promptView').textContent = data.text;
}

async function copyPrompt(kind) {
  if (!current) return;
  const data = await api(`/api/prompt?task=${encodeURIComponent(current)}&kind=${kind}`);
  await copyText(data.text, kind.toUpperCase());
  document.getElementById('promptView').textContent = data.text;
}

async function copyText(text, label) {
  try {
    await navigator.clipboard.writeText(text);
    flash(`הועתק ${label} ✅`);
  } catch {
    // fallback visible select
    const pre = document.getElementById('promptView');
    pre.textContent = text;
    flash(`לא הצלחתי להעתיק אוטומטית — סמן ידנית את ${label}`);
  }
  // also ask server to try OS clipboard
  await api('/api/clipboard', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({text})});
}

function flash(msg) {
  document.getElementById('result').textContent = msg;
}

async function saveMeta() {
  await api('/api/meta', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({
      model_name: document.getElementById('model').value,
      max_attempts: Number(document.getElementById('maxAttempts').value || 3)
    })
  });
  await refresh();
  flash('הגדרות נשמרו');
}

async function grade() {
  if (!current) return;
  const reply = document.getElementById('reply').value.trim();
  if (!reply) return flash('הדבק תשובת מודל קודם');
  document.getElementById('gradeBtn').disabled = true;
  try {
    const data = await api('/api/grade', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({
        task: current,
        reply,
        model_name: document.getElementById('model').value
      })
    });
    await refresh();
    if (data.passed) {
      flash(`PASS ✅ ניסיון ${data.attempt}`);
      document.getElementById('copyRetry').style.display = 'none';
      document.getElementById('retryView').style.display = 'none';
    } else if (data.retry_prompt) {
      retryPrompt = data.retry_prompt;
      flash(`FAIL ❌ ניסיון ${data.attempt} — יש RETRY prompt`);
      document.getElementById('retryView').style.display = 'block';
      document.getElementById('retryView').textContent = retryPrompt;
      document.getElementById('copyRetry').style.display = 'inline-block';
    } else {
      flash(`FAIL ❌ ניסיון ${data.attempt} — נגמר תקציב הניסיונות`);
    }
  } catch (e) {
    flash(String(e));
  } finally {
    document.getElementById('gradeBtn').disabled = false;
  }
}

function jumpNext() {
  const n = state.next;
  if (n) selectTask(n);
  else flash('אין משימות ממתינות');
}

refresh();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _html(self, body: str) -> None:
        raw = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self) -> dict:
        n = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(n).decode("utf-8") or "{}")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            self._html(HTML)
            return
        if parsed.path == "/api/state":
            session = load_session()
            tasks = [
                {
                    "id": tid,
                    "status": session["tasks"][tid].get("status", "pending"),
                    "attempts": len(session["tasks"][tid].get("attempts") or []),
                    "passed": bool(session["tasks"][tid].get("passed")),
                }
                for tid in task_ids()
            ]
            self._json(
                200,
                {
                    "session": {
                        "model_name": session.get("model_name", ""),
                        "max_attempts": session.get("max_attempts", 3),
                    },
                    "tasks": tasks,
                    "summary": summary(session),
                    "next": next_pending(session),
                    "system": (ROOT / "SYSTEM.txt").read_text(encoding="utf-8"),
                },
            )
            return
        if parsed.path == "/api/prompt":
            qs = parse_qs(parsed.query)
            task = (qs.get("task") or [""])[0]
            kind = (qs.get("kind") or ["user"])[0]
            if kind == "system":
                text = (ROOT / "SYSTEM.txt").read_text(encoding="utf-8")
            else:
                text = read_prompt(task, kind)
            self._json(200, {"task": task, "kind": kind, "text": text})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/meta":
            data = self._read_json()
            session = load_session()
            if "model_name" in data:
                session["model_name"] = str(data["model_name"])
            if "max_attempts" in data:
                session["max_attempts"] = max(1, int(data["max_attempts"]))
            save_session(session)
            write_scorecard(session)
            self._json(200, {"ok": True})
            return
        if parsed.path == "/api/clipboard":
            from session_lib import clipboard_copy

            data = self._read_json()
            ok = clipboard_copy(str(data.get("text") or ""))
            self._json(200, {"ok": ok})
            return
        if parsed.path == "/api/grade":
            data = self._read_json()
            session = load_session()
            result = submit_reply(
                session,
                str(data.get("task") or ""),
                str(data.get("reply") or ""),
                model_name=str(data.get("model_name") or "") or None,
            )
            self._json(200, result)
            return
        self._json(404, {"error": "not found"})

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    # Ensure prompts exist
    if not (ROOT / "tasks").exists() or not any((ROOT / "tasks").glob("*_USER.txt")):
        from build_pack import main as build

        build()
    session = load_session()
    write_scorecard(session)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"SymptomsBench session UI -> http://{HOST}:{PORT}")
    print("Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
