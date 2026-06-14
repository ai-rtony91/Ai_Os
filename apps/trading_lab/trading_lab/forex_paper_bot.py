from __future__ import annotations

from typing import Any


SUPPORTED_PAIRS = {"EURUSD", "GBPUSD", "USDJPY"}
SUPPORTED_DIRECTIONS = {"buy", "sell"}
MAX_RISK_PERCENT = 2.0

PAPER_SAFETY = {
    "paper_only": True,
    "execution_allowed": False,
    "broker_execution": False,
    "credential_use": False,
    "live_trading": False,
    "real_orders": False,
    "real_webhooks": False,
}


def blocked_decision(reason: str) -> dict[str, Any]:
    return {
        "allowed": False,
        "decision_type": "blocked",
        "blocked_reason": reason,
        **PAPER_SAFETY,
    }


def _unsafe_scope_reason(
    execution_mode: str,
    live_execution: bool,
    broker_order: bool,
    credentials: Any,
    real_order: bool,
    webhook_url: str | None,
) -> str | None:
    if execution_mode != "paper":
        return "execution_mode_must_be_paper"
    if live_execution:
        return "live_execution_blocked"
    if broker_order:
        return "broker_order_blocked"
    if credentials:
        return "credentials_blocked"
    if real_order:
        return "real_order_blocked"
    if webhook_url:
        return "real_webhook_blocked"
    return None


def validate_signal(
    pair: str,
    direction: str,
    entry_price: float,
    stop_loss: float | None,
    account_equity: float,
    max_risk_percent: float,
    *,
    execution_mode: str = "paper",
    live_execution: bool = False,
    broker_order: bool = False,
    credentials: Any = None,
    real_order: bool = False,
    webhook_url: str | None = None,
) -> dict[str, Any]:
    unsafe_reason = _unsafe_scope_reason(
        execution_mode=execution_mode,
        live_execution=live_execution,
        broker_order=broker_order,
        credentials=credentials,
        real_order=real_order,
        webhook_url=webhook_url,
    )
    if unsafe_reason:
        return blocked_decision(unsafe_reason)

    normalized_pair = str(pair).upper()
    normalized_direction = str(direction).lower()

    if normalized_pair not in SUPPORTED_PAIRS:
        return blocked_decision("unsupported_pair")
    if normalized_direction not in SUPPORTED_DIRECTIONS:
        return blocked_decision("unsupported_direction")
    if stop_loss is None:
        return blocked_decision("stop_loss_required")
    if account_equity <= 0:
        return blocked_decision("account_equity_must_be_positive")
    if entry_price <= 0 or stop_loss <= 0:
        return blocked_decision("prices_must_be_positive")
    if entry_price == stop_loss:
        return blocked_decision("stop_loss_must_differ_from_entry")
    if max_risk_percent <= 0 or max_risk_percent > MAX_RISK_PERCENT:
        return blocked_decision("max_risk_percent_exceeds_paper_limit")

    return {
        "allowed": True,
        "pair": normalized_pair,
        "direction": normalized_direction,
        "entry_price": float(entry_price),
        "stop_loss": float(stop_loss),
        "account_equity": float(account_equity),
        "max_risk_percent": float(max_risk_percent),
        **PAPER_SAFETY,
    }


def calculate_mock_position_size(
    account_equity: float,
    max_risk_percent: float,
    entry_price: float,
    stop_loss: float,
) -> dict[str, float]:
    risk_amount = float(account_equity) * (float(max_risk_percent) / 100.0)
    stop_distance = abs(float(entry_price) - float(stop_loss))
    if stop_distance == 0:
        return {"risk_amount": round(risk_amount, 2), "mock_units": 0.0}
    return {
        "risk_amount": round(risk_amount, 2),
        "mock_units": round(risk_amount / stop_distance, 2),
    }


def paper_decision(
    pair: str,
    direction: str,
    entry_price: float,
    stop_loss: float | None,
    account_equity: float,
    max_risk_percent: float,
    *,
    execution_mode: str = "paper",
    live_execution: bool = False,
    broker_order: bool = False,
    credentials: Any = None,
    real_order: bool = False,
    webhook_url: str | None = None,
) -> dict[str, Any]:
    validation = validate_signal(
        pair=pair,
        direction=direction,
        entry_price=entry_price,
        stop_loss=stop_loss,
        account_equity=account_equity,
        max_risk_percent=max_risk_percent,
        execution_mode=execution_mode,
        live_execution=live_execution,
        broker_order=broker_order,
        credentials=credentials,
        real_order=real_order,
        webhook_url=webhook_url,
    )
    if not validation["allowed"]:
        return validation

    position = calculate_mock_position_size(
        account_equity=validation["account_equity"],
        max_risk_percent=validation["max_risk_percent"],
        entry_price=validation["entry_price"],
        stop_loss=validation["stop_loss"],
    )
    return {
        "allowed": True,
        "decision_type": "paper_decision_only",
        "pair": validation["pair"],
        "direction": validation["direction"],
        "mock_position_size": position,
        "next_safe_action": "Review the paper decision locally. Do not route it to a broker.",
        **PAPER_SAFETY,
    }
