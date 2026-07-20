"""
# Binance Auto-Trader ($100 high-risk breakout)

בוט מסחר אוטומטי ל־**Binance USDT-M Futures** עם אסטרטגיית פריצה + ניהול סיכון ATR.

> **אזהרה:** אין שיטה מוכחת לרווח. עם 100$ וסיכון גבוה סביר שתפסיד את כל הסכום.
> כברירת מחדל הבוט רץ ב־`DRY_RUN=true` ולא שולח פקודות אמיתיות.

## השיטה (הגיון, לא קסם)

1. מסגרת זמן: `15m` (ברירת מחדל)
2. **כניסה LONG** אם הנר האחרון שנסגר נסגר מעל השיא של 20 הנרות הקודמים
3. **כניסה SHORT** אם נסגר מתחת לשפל של 20 הנרות הקודמים
4. **סטופ** = מרחק `ATR(14) × 1.5` מהכניסה
5. **טייק פרופיט** = `2R` (פי שניים ממרחק הסטופ)
6. **גודל פוזיציה** = כך שסיכון ≈ `8%` מההון עד הסטופ
7. **מינוף** = `3x` (לא x50)
8. מקסימום **3 עסקאות ליום**
9. **Kill switch** אם ההון יורד ב־`30%` מההתחלה

## התקנה

```bash
cd binance-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## מפתחות API ב־Binance

1. Binance → API Management → Create API
2. הפעל **Futures** בלבד
3. **אל תפעיל** Withdrawals
4. הגבל IP אם אפשר
5. לתרגול: [Futures Testnet](https://testnet.binancefuture.com/) + `USE_TESTNET=true`

שים ב־`.env`:

```env
BINANCE_API_KEY=...
BINANCE_API_SECRET=...
DRY_RUN=true
USE_TESTNET=true
```

## הרצה

```bash
# סימולציה / לוג אותות בלבד
python bot.py

# דמו מקומי בלי רשת (אם Binance חסום באזור שלך)
FORCE_OFFLINE=true RUN_ONCE=true python bot.py

# אחרי בדיקה בטסטנט — בזהירות:
# DRY_RUN=false USE_TESTNET=false  (רק אם אתה מבין שאתה עלול לאבד הכל)
```

## חשוב על הרשת

שרתי Binance Futures חסומים בחלק מהמדינות (שגיאת 451).  
הבוט חייב לרוץ **מהמחשב שלך / VPS באזור מותר**, עם מפתחות API שלך.  
בסביבות חסומות הוא נופל אוטומטית ל־offline demo כש־`DRY_RUN=true`.

## בדיקות

```bash
pytest -q
```

## מבנה

| קובץ | תפקיד |
|------|--------|
| `strategy.py` | אותות פריצה + ATR |
| `risk.py` | גודל פוזיציה, לימיט יומי, kill switch |
| `exchange_client.py` | חיבור ccxt ל־Binance Futures |
| `bot.py` | לולאה ראשית |
| `config.py` | הגדרות מ־`.env` |

## מה לא כלול בכוונה

- הבטחות רווח / "אלפי אחוזים"
- מינוף קיצוני
- מסחר במטבעות מימ בלי נזילות
- משיכת כספים דרך API
"""
