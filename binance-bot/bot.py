"""Main loop: fetch candles → signal → size → place bracket (or dry-run)."""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

from config import Settings, settings
from exchange_client import ExchangeClient
from risk import RiskState, can_open_trade, check_drawdown, size_position
from strategy import generate_signal

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

console = Console()


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(console=console, rich_tracebacks=True),
            logging.FileHandler(LOG_DIR / "bot.log", encoding="utf-8"),
        ],
    )


logger = logging.getLogger("bot")


def validate_settings(s: Settings) -> None:
    if not s.dry_run and (not s.binance_api_key or not s.binance_api_secret):
        raise SystemExit("Live mode requires BINANCE_API_KEY and BINANCE_API_SECRET")
    if s.leverage > 5:
        logger.warning("Leverage %s is aggressive for a $100 account", s.leverage)


def run_once(client: ExchangeClient, s: Settings, state: RiskState) -> None:
    equity = client.fetch_equity_usdt()
    if state.starting_equity <= 0:
        state.starting_equity = equity

    logger.info(
        "equity=%.2f USDT | start=%.2f | trades_today=%s | dry_run=%s testnet=%s",
        equity,
        state.starting_equity,
        state.daily_trades,
        s.dry_run,
        s.use_testnet,
    )

    if equity < s.min_quote_balance:
        logger.warning("Balance %.2f below min %.2f — skipping", equity, s.min_quote_balance)
        return

    if check_drawdown(state, equity, s.max_drawdown_pct):
        logger.error("KILL SWITCH: %s", state.halt_reason)
        return

    ok, why = can_open_trade(state, s.max_daily_trades)
    if not ok:
        logger.info("No new trades: %s", why)
        return

    open_pos = client.fetch_open_positions(s.symbol)
    if open_pos:
        logger.info("Already in position (%s) — waiting", len(open_pos))
        return

    df = client.fetch_ohlcv_df(s.symbol, s.timeframe)
    signal = generate_signal(
        df,
        lookback=s.breakout_lookback,
        atr_period=s.atr_period,
        atr_stop_mult=s.atr_stop_mult,
        take_profit_r=s.take_profit_r,
    )
    if signal is None:
        logger.info("No breakout signal on last closed candle")
        return

    plan = size_position(
        signal,
        equity=equity,
        risk_pct=s.risk_per_trade_pct,
        leverage=s.leverage,
        min_notional=s.min_quote_balance,
    )
    if plan is None:
        logger.info("Signal found but size too small / invalid")
        return

    logger.info(
        "SIGNAL %s entry=%.4f stop=%.4f tp=%.4f risk≈%.2f USDT notional≈%.2f | %s",
        plan.side.value,
        plan.entry,
        plan.stop,
        plan.take_profit,
        plan.risk_usdt,
        plan.notional,
        plan.reason,
    )

    client.set_leverage(s.symbol, s.leverage)
    result = client.place_bracket(
        s.symbol,
        plan.side,
        plan.qty,
        plan.stop,
        plan.take_profit,
        dry_run=s.dry_run,
    )
    state.daily_trades += 1
    logger.info("Order result: %s", result)


def main() -> None:
    setup_logging()
    s = settings
    validate_settings(s)

    console.print(
        "[bold]Binance breakout bot[/bold] — "
        f"symbol={s.symbol} tf={s.timeframe} lev={s.leverage}x "
        f"risk={s.risk_per_trade_pct}% dry_run={s.dry_run} testnet={s.use_testnet}"
    )
    console.print(
        "[yellow]No strategy guarantees profit. You can lose the entire balance.[/yellow]"
    )

    # Public market data works without keys; private calls need keys
    if not s.binance_api_key and not s.dry_run:
        raise SystemExit("API keys required for live trading")

    client = ExchangeClient(s)

    start = client.fetch_equity_usdt()
    if client.public_only or client.offline:
        logger.warning(
            "Simulated/public mode — equity=%.2f USDT (signals/dry-run only)",
            start,
        )
    state = RiskState(starting_equity=start)

    import ccxt

    logger.info("Starting loop; Ctrl+C to stop (RUN_ONCE=%s)", s.run_once)
    while True:
        try:
            run_once(client, s, state)
            if state.halted:
                logger.error("Halted — exiting loop")
                break
            if s.run_once:
                logger.info("RUN_ONCE complete — exiting")
                break
        except (ccxt.NetworkError, ccxt.ExchangeError, ccxt.RequestTimeout) as exc:
            logger.exception("Exchange error: %s", exc)
            if s.run_once:
                raise
        except KeyboardInterrupt:
            logger.info("Stopped by user")
            sys.exit(0)
        if not s.run_once:
            time.sleep(s.poll_seconds)


if __name__ == "__main__":
    main()
