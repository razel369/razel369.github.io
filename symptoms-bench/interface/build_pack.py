#!/usr/bin/env python3
"""Build a paste-ready chat-interface benchmark pack."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "interface"
sys.path.insert(0, str(ROOT / "harness"))
sys.path.insert(0, str(ROOT / "plugin"))

from prompts import SYSTEM, build_task_user_prompt, combined_prompt  # noqa: E402
from run_eval import collect_workspace_files, list_tasks  # noqa: E402


README = """# SymptomsBench — Interface Pack

הריצו את הבנצ'מרק על **כל מודל בצ'אט** (Fable / Claude / ChatGPT / Gemini / Cursor).

## איך להריץ (חד-פעמי / k=1)

1. פתחו שיחה חדשה עם המודל.
2. העתיקו את כל התוכן מ־`SYSTEM.txt` והדביקו כ־**Custom instructions / System**  
   (אם אין System — השתמשו ב־`tasks/<id>_COMBINED.txt` במקום).
3. לכל משימה ב־`tasks/`:
   - העתיקו את `*_USER.txt`
   - שלחו למודל
   - שמרו את התשובה המלאה בקובץ, למשל: `replies/001_off_by_one.txt`
4. ציון אוטומטי:

```bash
cd symptoms-bench
python3 interface/grade_reply.py --task 001_off_by_one --reply replies/001_off_by_one.txt
# או על כל התיקייה:
python3 interface/grade_reply.py --replies-dir replies
```

## פרוטוקול Multi-turn (k=3) מול Fable

כדי להשוות הוגן לתוסף:
1. ניסיון 1 = כמו למעלה.
2. אם נכשל — הריצו:

```bash
python3 interface/grade_reply.py --task 001_off_by_one --reply replies/001_a1.txt --emit-retry
```

זה מדפיס פרומפט Follow-up עם הלוגים החדשים. שלחו אותו באותה שיחה (או כהודעה הבאה), שמרו כ־`001_a2.txt`, חזרו עד 3 ניסיונות.

## חוקים חשובים
- אל תדביקו ל־model את `meta.json` / `bug_manifest.json`
- המודל חייב להחזיר בלוקי `<<<FILE>>> ... <<<END>>>`
- ציון = האם ה־hidden tests עוברים אחרי ה־patch

## Scorecard
אחרי `grade_reply.py --replies-dir replies` נוצר `interface/SCORECARD.md`.
"""


def main() -> None:
    if OUT.exists():
        for p in OUT.rglob("*"):
            if p.is_file() and p.name not in {"grade_reply.py", "build_pack.py"}:
                # keep scripts; wipe generated
                if p.parent.name == "tasks" or p.name in {
                    "SYSTEM.txt",
                    "README.md",
                    "manifest.json",
                    "SCORECARD.md",
                }:
                    p.unlink()
    (OUT / "tasks").mkdir(parents=True, exist_ok=True)
    (OUT / "replies").mkdir(parents=True, exist_ok=True)
    (OUT / "SYSTEM.txt").write_text(SYSTEM.strip() + "\n", encoding="utf-8")
    (OUT / "README.md").write_text(README, encoding="utf-8")

    manifest = []
    for task in list_tasks():
        logs = (task / "logs.txt").read_text(encoding="utf-8")
        files = collect_workspace_files(task / "workspace")
        py_files = [p.name for p in sorted((task / "workspace").glob("*.py"))]
        hint = py_files[0] if len(py_files) == 1 else None
        user = build_task_user_prompt(
            task.name,
            logs,
            files,
            attempt=1,
            max_attempts=1,
            hint_source=hint,
        )
        combined = combined_prompt(SYSTEM, user)
        (OUT / "tasks" / f"{task.name}_USER.txt").write_text(user + "\n", encoding="utf-8")
        (OUT / "tasks" / f"{task.name}_COMBINED.txt").write_text(
            combined + "\n", encoding="utf-8"
        )
        # Friendly markdown view
        md = (
            f"# {task.name}\n\n"
            f"1. Set system from `../SYSTEM.txt` (or use COMBINED below).\n"
            f"2. Copy the USER prompt.\n"
            f"3. Save model reply to `../replies/{task.name}.txt`.\n"
            f"4. Grade: `python3 interface/grade_reply.py --task {task.name} --reply interface/replies/{task.name}.txt`\n\n"
            f"## USER prompt\n\n```\n{user}\n```\n"
        )
        (OUT / "tasks" / f"{task.name}.md").write_text(md, encoding="utf-8")
        manifest.append(
            {
                "id": task.name,
                "user_prompt": f"tasks/{task.name}_USER.txt",
                "combined_prompt": f"tasks/{task.name}_COMBINED.txt",
                "hint_source": hint,
            }
        )

    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (OUT / "replies" / ".gitkeep").write_text("", encoding="utf-8")
    print(f"Wrote {len(manifest)} tasks to {OUT}")


if __name__ == "__main__":
    main()
