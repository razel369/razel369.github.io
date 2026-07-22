# SymptomsBench — Interface Pack

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
