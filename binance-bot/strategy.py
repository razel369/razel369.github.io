"""Breakout + ATR risk strategy — high risk, rules-based (not gambling).

Logic
-----
LONG when the latest closed candle closes above the prior N-bar high,
and ATR-based stop is wide enough to size a valid position.

SHORT when close breaks below the prior N-bar low (same rules).

Exit: stop at entry ± ATR*mult, take-profit at R-multiple of stop distance.

This does NOT guarantee profit. With $100 and high risk, expect frequent
wipe scenarios; the edge (if any) is discipline + defined R, not magic.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd


class Side(str, Enum):
    LONG = "long"
    SHORT = "short"


@dataclass(frozen=True)
class Signal:
    side: Side
    entry: float
    stop: float
    take_profit: float
    atr: float
    reason: str


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["high"]
    low = df["low"]
    close = df["close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(period).mean()


def generate_signal(
    df: pd.DataFrame,
    *,
    lookback: int = 20,
    atr_period: int = 14,
    atr_stop_mult: float = 1.5,
    take_profit_r: float = 2.0,
) -> Signal | None:
    """Return a signal on the last *closed* bar, or None."""
    need = lookback + atr_period + 3
    if len(df) < need:
        return None

    work = df.copy()
    work["atr"] = atr(work, atr_period)

    # Use last closed candle (assume caller already dropped incomplete bar if needed)
    i = len(work) - 1
    row = work.iloc[i]
    if np.isnan(row["atr"]) or row["atr"] <= 0:
        return None

    window = work.iloc[i - lookback : i]  # prior bars only (no look-ahead)
    prior_high = float(window["high"].max())
    prior_low = float(window["low"].min())
    close = float(row["close"])
    atr_val = float(row["atr"])
    stop_dist = atr_val * atr_stop_mult

    if close > prior_high:
        entry = close
        stop = entry - stop_dist
        tp = entry + stop_dist * take_profit_r
        return Signal(
            side=Side.LONG,
            entry=entry,
            stop=stop,
            take_profit=tp,
            atr=atr_val,
            reason=f"breakout_above_{lookback} high={prior_high:.4f}",
        )

    if close < prior_low:
        entry = close
        stop = entry + stop_dist
        tp = entry - stop_dist * take_profit_r
        return Signal(
            side=Side.SHORT,
            entry=entry,
            stop=stop,
            take_profit=tp,
            atr=atr_val,
            reason=f"breakout_below_{lookback} low={prior_low:.4f}",
        )

    return None
