"""Position sizing and kill-switch risk controls."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from strategy import Side, Signal


@dataclass
class RiskState:
    starting_equity: float
    daily_trades: int = 0
    trade_day: date = field(default_factory=date.today)
    halted: bool = False
    halt_reason: str = ""


@dataclass(frozen=True)
class PositionPlan:
    side: Side
    notional: float  # quote currency (USDT) exposure before leverage nuance
    qty: float  # base asset quantity
    entry: float
    stop: float
    take_profit: float
    risk_usdt: float
    leverage: int
    reason: str


def reset_day_if_needed(state: RiskState) -> None:
    today = date.today()
    if state.trade_day != today:
        state.trade_day = today
        state.daily_trades = 0


def check_drawdown(
    state: RiskState,
    equity: float,
    max_drawdown_pct: float,
) -> bool:
    """Return True if trading must halt."""
    if state.starting_equity <= 0:
        state.halted = True
        state.halt_reason = "invalid starting equity"
        return True
    dd = (state.starting_equity - equity) / state.starting_equity * 100.0
    if dd >= max_drawdown_pct:
        state.halted = True
        state.halt_reason = f"max drawdown {dd:.1f}% >= {max_drawdown_pct}%"
        return True
    return False


def size_position(
    signal: Signal,
    *,
    equity: float,
    risk_pct: float,
    leverage: int,
    min_notional: float = 5.0,
) -> PositionPlan | None:
    """Risk a fixed % of equity to the stop; notional = risk / stop_pct * leverage cap."""
    stop_dist = abs(signal.entry - signal.stop)
    if stop_dist <= 0 or signal.entry <= 0 or equity <= 0:
        return None

    risk_usdt = equity * (risk_pct / 100.0)
    # qty such that |entry-stop| * qty ≈ risk_usdt
    qty = risk_usdt / stop_dist
    notional = qty * signal.entry

    # Cap notional by available margin * leverage (approx: equity * leverage)
    max_notional = equity * leverage * 0.95
    if notional > max_notional:
        qty = max_notional / signal.entry
        notional = qty * signal.entry
        risk_usdt = qty * stop_dist

    if notional < min_notional:
        return None

    return PositionPlan(
        side=signal.side,
        notional=notional,
        qty=qty,
        entry=signal.entry,
        stop=signal.stop,
        take_profit=signal.take_profit,
        risk_usdt=risk_usdt,
        leverage=leverage,
        reason=signal.reason,
    )


def can_open_trade(state: RiskState, max_daily_trades: int) -> tuple[bool, str]:
    reset_day_if_needed(state)
    if state.halted:
        return False, state.halt_reason or "halted"
    if state.daily_trades >= max_daily_trades:
        return False, f"daily trade limit {max_daily_trades} reached"
    return True, "ok"
