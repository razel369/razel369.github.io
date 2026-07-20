"""Unit tests for strategy + risk (no network)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from risk import RiskState, can_open_trade, check_drawdown, size_position
from strategy import Side, generate_signal


def _ohlcv(n: int = 80, start: float = 100.0) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    closes = [start]
    for _ in range(n - 1):
        closes.append(closes[-1] * (1 + float(rng.normal(0, 0.002))))
    closes = np.array(closes)
    high = closes * 1.001
    low = closes * 0.999
    open_ = closes.copy()
    vol = np.full(n, 1000.0)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": closes, "volume": vol}
    )


def test_no_signal_in_range():
    df = _ohlcv()
    # Flatten last bars so no breakout
    df.loc[df.index[-25]:, "high"] = 100.5
    df.loc[df.index[-25]:, "low"] = 99.5
    df.loc[df.index[-25]:, "close"] = 100.0
    assert generate_signal(df, lookback=20) is None


def test_long_breakout_signal():
    df = _ohlcv()
    # Force prior window capped, then breakout close
    i = len(df) - 1
    df.loc[df.index[i - 20 : i], "high"] = 100.0
    df.loc[df.index[i - 20 : i], "low"] = 99.0
    df.loc[df.index[i - 20 : i], "close"] = 99.5
    df.loc[df.index[i], "high"] = 105.0
    df.loc[df.index[i], "low"] = 100.0
    df.loc[df.index[i], "close"] = 104.0
    # Need enough history for ATR
    sig = generate_signal(df, lookback=20, atr_period=14, atr_stop_mult=1.5, take_profit_r=2.0)
    assert sig is not None
    assert sig.side == Side.LONG
    assert sig.stop < sig.entry < sig.take_profit


def test_size_respects_risk():
    from strategy import Signal

    sig = Signal(
        side=Side.LONG,
        entry=100.0,
        stop=98.0,
        take_profit=104.0,
        atr=1.0,
        reason="test",
    )
    plan = size_position(sig, equity=100.0, risk_pct=8.0, leverage=3)
    assert plan is not None
    # risk ≈ qty * 2
    assert abs(plan.risk_usdt - 8.0) < 0.01 or plan.notional <= 100 * 3 * 0.95 + 1e-6


def test_kill_switch():
    state = RiskState(starting_equity=100.0)
    assert check_drawdown(state, 69.0, 30.0) is True
    assert state.halted


def test_daily_limit():
    state = RiskState(starting_equity=100.0, daily_trades=3)
    ok, _ = can_open_trade(state, max_daily_trades=3)
    assert ok is False
