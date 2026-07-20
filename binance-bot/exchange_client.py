"""Binance Futures exchange adapter via ccxt."""

from __future__ import annotations

import logging
from typing import Any

import ccxt
import numpy as np
import pandas as pd

from config import Settings
from strategy import Side

logger = logging.getLogger(__name__)


class ExchangeClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.public_only = not (settings.binance_api_key and settings.binance_api_secret)
        self._sim_equity = float(settings.demo_equity)
        self.offline = False
        opts: dict[str, Any] = {
            "apiKey": settings.binance_api_key or None,
            "secret": settings.binance_api_secret or None,
            "enableRateLimit": True,
            "options": {
                "defaultType": "future",
                "adjustForTimeDifference": True,
            },
        }

        if settings.force_offline:
            self.offline = True
            self.exchange = None
            logger.warning("FORCE_OFFLINE=true — using synthetic candles (no Binance calls)")
            return

        try:
            if settings.use_testnet and not self.public_only:
                self.exchange = ccxt.binanceusdm(opts)
                self.exchange.set_sandbox_mode(True)
                self.exchange.load_markets()
            elif self.public_only:
                self.exchange = ccxt.binanceusdm(
                    {"enableRateLimit": True, "options": {"defaultType": "future"}}
                )
                self.exchange.load_markets()
            else:
                self.exchange = ccxt.binanceusdm(opts)
                self.exchange.load_markets()
        except ccxt.ExchangeNotAvailable as exc:
            logger.error(
                "Binance unavailable from this network/region (%s). "
                "Run the bot on your machine / VPN, or set FORCE_OFFLINE=true for local demo.",
                exc,
            )
            if settings.dry_run:
                self.offline = True
                self.exchange = None
                logger.warning("Falling back to OFFLINE demo mode")
            else:
                raise

    def fetch_ohlcv_df(self, symbol: str, timeframe: str, limit: int = 150) -> pd.DataFrame:
        if self.offline:
            return _synthetic_ohlcv(limit=limit)
        assert self.exchange is not None
        raw = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(raw, columns=["ts", "open", "high", "low", "close", "volume"])
        df["ts"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
        if len(df) >= 2:
            df = df.iloc[:-1].copy()
        return df

    def fetch_equity_usdt(self) -> float:
        if self.offline or self.public_only:
            return self._sim_equity
        assert self.exchange is not None
        bal = self.exchange.fetch_balance()
        total = bal.get("total") or {}
        usdt = total.get("USDT")
        if usdt is not None:
            return float(usdt)
        free = bal.get("free") or {}
        return float(free.get("USDT") or 0.0)

    def set_leverage(self, symbol: str, leverage: int) -> None:
        if self.offline or self.public_only or self.settings.dry_run:
            logger.info("skip set_leverage (offline/public/dry_run) → %sx %s", leverage, symbol)
            return
        assert self.exchange is not None
        try:
            self.exchange.set_leverage(leverage, symbol)
        except Exception as exc:  # noqa: BLE001
            logger.warning("set_leverage failed (may already be set): %s", exc)

    def fetch_open_positions(self, symbol: str) -> list[dict[str, Any]]:
        if self.offline or self.public_only:
            return []
        assert self.exchange is not None
        try:
            positions = self.exchange.fetch_positions([symbol])
        except Exception:  # noqa: BLE001
            positions = self.exchange.fetch_positions()
        open_pos = []
        for p in positions:
            if p.get("symbol") != symbol:
                continue
            contracts = abs(float(p.get("contracts") or 0))
            if contracts > 0:
                open_pos.append(p)
        return open_pos

    def place_bracket(
        self,
        symbol: str,
        side: Side,
        qty: float,
        stop: float,
        take_profit: float,
        dry_run: bool,
    ) -> dict[str, Any]:
        """Market entry + stop-market + take-profit (reduce-only)."""
        if self.offline or dry_run or self.exchange is None:
            plan = {
                "symbol": symbol,
                "side": side.value,
                "amount": round(qty, 6),
                "stop": round(stop, 2),
                "take_profit": round(take_profit, 2),
                "dry_run": True,
                "offline": self.offline,
            }
            logger.info("DRY_RUN/OFFLINE bracket: %s", plan)
            return plan

        market = self.exchange.market(symbol)
        amount = float(self.exchange.amount_to_precision(symbol, qty))
        stop_p = float(self.exchange.price_to_precision(symbol, stop))
        tp_p = float(self.exchange.price_to_precision(symbol, take_profit))

        entry_side = "buy" if side == Side.LONG else "sell"
        exit_side = "sell" if side == Side.LONG else "buy"

        entry = self.exchange.create_order(symbol, "market", entry_side, amount)
        params = {"reduceOnly": True, "workingType": "MARK_PRICE"}
        stop_order = self.exchange.create_order(
            symbol,
            "STOP_MARKET",
            exit_side,
            amount,
            None,
            {**params, "stopPrice": stop_p},
        )
        tp_order = self.exchange.create_order(
            symbol,
            "TAKE_PROFIT_MARKET",
            exit_side,
            amount,
            None,
            {**params, "stopPrice": tp_p},
        )
        return {
            "dry_run": False,
            "entry": entry,
            "stop_order": stop_order,
            "tp_order": tp_order,
            "market_id": market.get("id"),
            "symbol": symbol,
            "side": side.value,
            "amount": amount,
            "stop": stop_p,
            "take_profit": tp_p,
        }


def _synthetic_ohlcv(limit: int = 150, seed: int = 7) -> pd.DataFrame:
    """Deterministic fake candles ending in a long breakout (for offline demo)."""
    rng = np.random.default_rng(seed)
    n = max(limit, 80)
    closes = [100.0]
    for _ in range(n - 2):
        closes.append(closes[-1] * (1 + float(rng.normal(0, 0.0015))))
    prior_high = max(closes[-21:-1]) if n > 22 else max(closes)
    closes.append(prior_high * 1.02)
    closes_arr = np.array(closes[-limit:])
    high = closes_arr * 1.002
    low = closes_arr * 0.998
    open_ = np.roll(closes_arr, 1)
    open_[0] = closes_arr[0]
    vol = np.full(len(closes_arr), 1000.0)
    ts = pd.date_range(end=pd.Timestamp.now(tz="UTC"), periods=len(closes_arr), freq="15min")
    return pd.DataFrame(
        {"ts": ts, "open": open_, "high": high, "low": low, "close": closes_arr, "volume": vol}
    )
