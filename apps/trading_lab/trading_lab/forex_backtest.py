from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


PAPER_BACKTEST_SAFETY = {
    "paper_only": True,
    "execution_allowed": False,
    "broker_execution": False,
    "credential_use": False,
    "live_trading": False,
    "real_orders": False,
    "real_webhooks": False,
}

BLOCKED_SCOPE_FIELDS = {
    "broker",
    "broker_order",
    "credentials",
    "api_key",
    "token",
    "live_execution",
    "real_order",
    "webhook_url",
    "real_webhook",
}


def _load_forex_paper_bot():
    try:
        from . import forex_paper_bot  # type: ignore

        return forex_paper_bot
    except ImportError:
        module_path = Path(__file__).with_name("forex_paper_bot.py")
        spec = importlib.util.spec_from_file_location("forex_paper_bot", module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module


def _blocked_scope_reason(candle: dict[str, Any]) -> str | None:
    for field in sorted(BLOCKED_SCOPE_FIELDS):
        if candle.get(field):
            return f"{field}_blocked"
    return None


def _paper_stop_loss(close: float, direction: str, candle: dict[str, Any]) -> float | None:
    if candle.get("stop_loss") is not None:
        return float(candle["stop_loss"])
    if direction == "buy":
        return round(close * 0.99, 6)
    if direction == "sell":
        return round(close * 1.01, 6)
    return None


def run_backtest(
    candles: list[dict[str, Any]],
    *,
    starting_balance: float = 10000.0,
    default_pair: str = "EURUSD",
    default_direction: str = "buy",
    max_risk_percent: float = 1.0,
) -> dict[str, Any]:
    bot = _load_forex_paper_bot()
    ending_balance = float(starting_balance)
    decisions: list[dict[str, Any]] = []
    trades_allowed = 0
    trades_blocked = 0

    for index, candle in enumerate(candles):
        blocked_scope = _blocked_scope_reason(candle)
        pair = str(candle.get("pair", default_pair)).upper()
        direction = str(candle.get("direction", default_direction)).lower()
        close = float(candle.get("close", candle.get("entry_price", 0)))
        stop_loss = _paper_stop_loss(close, direction, candle)

        if blocked_scope:
            trades_blocked += 1
            decisions.append(
                {
                    "index": index,
                    "allowed": False,
                    "blocked_reason": blocked_scope,
                    **PAPER_BACKTEST_SAFETY,
                }
            )
            continue

        decision = bot.paper_decision(
            pair=pair,
            direction=direction,
            entry_price=close,
            stop_loss=stop_loss,
            account_equity=ending_balance,
            max_risk_percent=max_risk_percent,
        )
        decision_record = {"index": index, **decision}
        if decision.get("allowed"):
            trades_allowed += 1
            risk_amount = decision["mock_position_size"]["risk_amount"]
            paper_result_r = float(candle.get("paper_result_r", 0.0))
            ending_balance += risk_amount * paper_result_r
        else:
            trades_blocked += 1
        decisions.append(decision_record)

    return {
        "trades_considered": len(candles),
        "trades_allowed": trades_allowed,
        "trades_blocked": trades_blocked,
        "ending_balance": round(ending_balance, 2),
        "decisions": decisions,
        **PAPER_BACKTEST_SAFETY,
    }
