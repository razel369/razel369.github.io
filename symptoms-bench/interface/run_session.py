#!/usr/bin/env python3
"""CLI wizard for running SymptomsBench against a chat-model UI.

Usage:
  python3 interface/run_session.py
  python3 interface/run_session.py --model "Fable 5" --attempts 3
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from session_lib import (  # noqa: E402
    clipboard_copy,
    load_session,
    next_pending,
    read_prompt,
    save_session,
    submit_reply,
    summary,
    write_scorecard,
)


def ask(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return "q"


def read_multiline(prompt: str) -> str:
    print(prompt)
    print("(סיים עם שורה יחידה: END  או Ctrl-D)")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines).strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="")
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--combined", action="store_true", help="Prefer COMBINED prompts")
    args = parser.parse_args()

    # ensure pack
    if not any((ROOT / "tasks").glob("*_USER.txt")):
        from build_pack import main as build

        build()

    session = load_session()
    if args.model:
        session["model_name"] = args.model
    session["max_attempts"] = max(1, args.attempts)
    save_session(session)

    print("=== SymptomsBench CLI Session ===")
    print("פקודות: [c]opy prompt · [p]aste+grade · [n]ext · [s]tatus · [q]uit")
    print()

    # Copy system once
    system = read_prompt("", "system")
    if clipboard_copy(system):
        print("✓ SYSTEM הועתק ללוח. הדבק כ־Custom instructions / System במודל.")
    else:
        print("לא הצלחתי להעתיק ללוח. SYSTEM נמצא ב: interface/SYSTEM.txt")
    print()

    while True:
        s = summary(session)
        print(
            f"מצב: {s['passed']}/{s['total']} resolved · "
            f"{s['attempted']} attempted · {s['pending']} pending"
        )
        tid = next_pending(session)
        if not tid:
            print("סיימת את כל המשימות 🎉")
            print(f"Scorecard: {write_scorecard(session)}")
            break

        st = session["tasks"][tid]
        attempt_n = len(st.get("attempts") or []) + 1
        print(f"\n>>> משימה: {tid}  (attempt {attempt_n}/{session['max_attempts']})  status={st.get('status')}")
        cmd = ask("[c]=copy  [p]=paste/grade  [n]=skip  [s]=status  [q]=quit  > ").strip().lower()
        if cmd in {"q", "quit"}:
            break
        if cmd in {"s", "status"}:
            write_scorecard(session)
            print(f"Scorecard -> {ROOT / 'SCORECARD.md'}")
            continue
        if cmd in {"n", "next", "skip"}:
            # Rotate: move this task to the end by rewriting key order via status marker
            print(f"דילוג על {tid} לעכשיו (נשארת pending).")
            # Implement soft-skip list in session
            skipped = session.setdefault("_skipped", [])
            if tid not in skipped:
                skipped.append(tid)
            # If everything remaining is skipped, clear skip list to revisit
            pending = [
                t
                for t, st in session["tasks"].items()
                if st.get("status") in {"pending", "retry"} and t not in skipped
            ]
            if not pending:
                session["_skipped"] = []
                print("חזרנו על כל הדילוגים — מתחילים סבב נוסף על הממתינות.")
            save_session(session)
            continue
        if cmd in {"c", "copy", ""}:
            kind = "combined" if args.combined or attempt_n == 1 and ask("combined? [y/N] ").lower() == "y" else "user"
            # For retries, prefer using last stored retry if exists — rebuild via empty grade path not available.
            # If status is retry, tell user to use paste flow that returns retry; for copy on retry
            # we copy a fresh user prompt (attempt 1 style). Better: if last attempt failed, rebuild retry.
            text = read_prompt(tid, kind)
            if st.get("status") == "retry" and st.get("attempts"):
                # Reconstruct retry from last failed attempt file by re-grading quickly
                from grade_reply import grade_one, resolve_task, emit_retry_prompt

                last = st["attempts"][-1]
                reply_path = ROOT / last["reply_path"]
                if reply_path.exists():
                    result = grade_one(resolve_task(tid), reply_path.read_text(encoding="utf-8"))
                    text = emit_retry_prompt(
                        resolve_task(tid),
                        result,
                        attempt=attempt_n,
                        max_attempts=session["max_attempts"],
                    )
                    print("(מצב retry — מועתק RETRY prompt)")
            if clipboard_copy(text):
                print(f"✓ הועתק ({'RETRY/USER' if st.get('status')=='retry' else kind}). הדבק בצ׳אט המודל.")
            else:
                out = ROOT / "replies" / f"_clipboard_{tid}.txt"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(text, encoding="utf-8")
                print(f"לא היה clipboard — נשמר ל־{out}")
            continue
        if cmd in {"p", "paste", "grade"}:
            reply = read_multiline("הדבק כאן את תשובת המודל:")
            if not reply:
                print("ריק — מבטל")
                continue
            result = submit_reply(
                session,
                tid,
                reply,
                model_name=session.get("model_name") or args.model or None,
            )
            session = load_session()
            if result["passed"]:
                print(f"PASS ✅  (attempt {result['attempt']})")
            elif result.get("retry_prompt"):
                print(f"FAIL ❌  (attempt {result['attempt']}) — יש retry")
                if clipboard_copy(result["retry_prompt"]):
                    print("✓ RETRY prompt הועתק ללוח. שלח אותו כהודעה הבאה במודל.")
                else:
                    out = ROOT / "replies" / f"{tid}_retry_prompt.txt"
                    out.write_text(result["retry_prompt"], encoding="utf-8")
                    print(f"RETRY prompt נשמר ל־{out}")
            else:
                print(f"FAIL ❌  (attempt {result['attempt']}) — נגמר תקציב הניסיונות")
            continue
        print("פקודה לא מוכרת")

    write_scorecard(load_session())
    print("יציאה. session.json + SCORECARD.md עודכנו.")


if __name__ == "__main__":
    main()
