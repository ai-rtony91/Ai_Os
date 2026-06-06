"""Configuration for the AI_OS Forex Engine v1 paper-only scaffold."""

from dataclasses import dataclass
from typing import Tuple

from automation.forex_engine.models import EngineMode


@dataclass(frozen=True)
class ForexEngineConfig:
    mode: str = EngineMode.PAPER_ONLY
    starting_balance_usd: float = 500.0
    paper_risk_per_trade_pct: float = 0.5
    first_live_risk_target_pct: float = 0.25
    max_daily_drawdown_pct: float = 2.0
    max_open_trades_paper: int = 2
    pause_after_consecutive_losses: int = 3
    minimum_confidence_to_trade: int = 70
    base_currency: str = "USD"
    symbols: Tuple[str, ...] = ("EURUSD", "GBPUSD", "USDJPY", "XAUUSD")
    timeframes: Tuple[str, ...] = ("1m", "5m", "15m", "1h")
    journal_dir: str = "automation/forex_engine/runtime/journal"
    demo_output_dir: str = "automation/forex_engine/runtime/demo"
    fixture_data_dir: str = "automation/forex_engine/fixtures"


def validate_config(config: ForexEngineConfig) -> None:
    if config.mode != EngineMode.PAPER_ONLY:
        raise ValueError("Forex Engine Sprint 1 mode must be PAPER_ONLY.")
    if config.starting_balance_usd <= 0:
        raise ValueError("starting_balance_usd must be positive.")
    if not 0 < config.paper_risk_per_trade_pct <= 5:
        raise ValueError("paper_risk_per_trade_pct must be > 0 and <= 5.")
    if not 0 < config.first_live_risk_target_pct <= 2:
        raise ValueError("first_live_risk_target_pct must be > 0 and <= 2.")
    if not 0 < config.max_daily_drawdown_pct <= 20:
        raise ValueError("max_daily_drawdown_pct must be > 0 and <= 20.")
    if not config.symbols:
        raise ValueError("symbols must not be empty.")
    if not config.timeframes:
        raise ValueError("timeframes must not be empty.")
    if config.max_open_trades_paper < 1:
        raise ValueError("max_open_trades_paper must be at least 1.")
    if config.pause_after_consecutive_losses < 1:
        raise ValueError("pause_after_consecutive_losses must be at least 1.")
    if not 0 <= config.minimum_confidence_to_trade <= 100:
        raise ValueError("minimum_confidence_to_trade must be between 0 and 100.")
