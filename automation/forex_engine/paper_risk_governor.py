"""Paper-only risk governor for deterministic forex sessions."""
from __future__ import annotations

from typing import Any

DEFAULT_TIMESTAMP = 1760000000.0


def evaluate_paper_trade_risk(
    candidate: dict[str, Any],
    account_state: dict[str, Any] | None = None,
    open_trades: list[dict[str, Any]] | None = None,
    limits: dict[str, Any] | None = None,
    now_timestamp: float = DEFAULT_TIMESTAMP,
) -> dict[str, Any]:
    """Evaluate a candidate against paper-only risk controls."""
    account = dict(account_state or {})
    active = list(open_trades or [])
    caps = {
        "max_risk_percent": 2.0,
        "max_daily_loss": 300.0,
        "max_open_trades": 3,
        "max_spread": 0.001,
        "require_target": False,
        "max_data_age_seconds": 300.0,
        **dict(limits or {}),
    }
    rejection_reasons: list[str] = []

    symbol = candidate.get("symbol")
    entry = candidate.get("entry")
    stop = candidate.get("stop")
    target = candidate.get("target")
    risk_percent = float(candidate.get("risk_percent", 0.0) or 0.0)
    spread = float(candidate.get("spread", 0.0) or 0.0)

    if not stop or stop == entry:
        rejection_reasons.append("stop_required")
    if caps["require_target"] and not target:
        rejection_reasons.append("target_required")
    if risk_percent <= 0 or risk_percent > float(caps["max_risk_percent"]):
        rejection_reasons.append("risk_percent_too_high")
    if float(account.get("daily_loss", 0.0)) >= float(caps["max_daily_loss"]):
        rejection_reasons.append("max_daily_loss_hit")
    if len(active) >= int(caps["max_open_trades"]):
        rejection_reasons.append("max_open_trades_hit")
    if spread > float(caps["max_spread"]):
        rejection_reasons.append("spread_too_high")
    timestamp = candidate.get("timestamp")
    if timestamp is not None and float(now_timestamp) - float(timestamp) > float(caps["max_data_age_seconds"]):
        rejection_reasons.append("stale_data")
    if symbol and any(trade.get("symbol") == symbol and trade.get("status") in {"opened", "active"} for trade in active):
        rejection_reasons.append("duplicate_symbol")

    return {
        "risk_passed": not rejection_reasons,
        "rejection_reasons": rejection_reasons,
        "risk_used": round(risk_percent, 8) if not rejection_reasons else 0.0,
        "paper_only": True,
    }
