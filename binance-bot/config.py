"""Configuration for the Binance auto-trader."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    binance_api_key: str = ""
    binance_api_secret: str = ""

    dry_run: bool = True
    use_testnet: bool = True
    force_offline: bool = False
    demo_equity: float = 100.0
    run_once: bool = False

    symbol: str = "BTC/USDT:USDT"
    timeframe: str = "15m"
    leverage: int = Field(default=3, ge=1, le=10)

    # Risk: % of equity risked per trade (stop distance defines size)
    risk_per_trade_pct: float = Field(default=8.0, ge=1.0, le=15.0)
    max_daily_trades: int = Field(default=3, ge=1, le=10)
    max_drawdown_pct: float = Field(default=30.0, ge=5.0, le=80.0)
    take_profit_r: float = Field(default=2.0, ge=1.0, le=5.0)

    atr_period: int = Field(default=14, ge=5, le=50)
    atr_stop_mult: float = Field(default=1.5, ge=0.5, le=4.0)
    breakout_lookback: int = Field(default=20, ge=5, le=100)

    min_quote_balance: float = 5.0
    poll_seconds: int = Field(default=30, ge=10, le=300)

    starting_equity: float | None = None  # set at runtime from exchange


settings = Settings()
