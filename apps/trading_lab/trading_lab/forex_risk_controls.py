from __future__ import annotations

from typing import Any


SUPPORTED_PAIRS = {"EURUSD", "GBPUSD", "USDJPY"}
SUPPORTED_ACTIONS = {"buy", "sell", "hold"}

PAPER_RISK_SAFETY = {
    "paper_only": True,
    "execution_allowed": False,
    "broker_execution": False,
    "credential_use": False,
    "live_trading": False,
    "real_orders": False,
    "real_webhooks": False,
    "network_access": False,
}


def _number(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _blocked(
    reason: str,
    *,
    pair: str,
    action: str | None,
    position_size_units: float,
    max_position_size_units: float,
    risk_percent: float,
    max_risk_percent: float,
    daily_loss_limit_hit: bool = False,
    max_trades_limit_hit: bool = False,
) -> dict[str, Any]:
    return {
        "allowed": False,
        "blocked_reason": reason,
        "pair": pair,
        "action": action,
        "position_size_units": position_size_units,
        "max_position_size_units": max_position_size_units,
        "risk_percent": risk_percent,
        "max_risk_percent": max_risk_percent,
        "daily_loss_limit_hit": daily_loss_limit_hit,
        "max_trades_limit_hit": max_trades_limit_hit,
        "paper_only": True,
        "safety": PAPER_RISK_SAFETY.copy(),
        "next_safe_action": "Stop and review the blocked paper risk-control decision.",
    }


def _safety_block_reason(flags: dict[str, Any]) -> str | None:
    blocked_fields = [
        ("live_execution", "live_execution_blocked"),
        ("broker_order", "broker_order_blocked"),
        ("credentials", "credentials_blocked"),
        ("api_key", "api_key_blocked"),
        ("real_order", "real_order_blocked"),
        ("webhook_url", "real_webhook_blocked"),
        ("real_webhook", "real_webhook_blocked"),
        ("network", "network_blocked"),
        ("network_access", "network_blocked"),
    ]
    for field, reason in blocked_fields:
        if flags.get(field):
            return reason
    return None


def _daily_loss_limit_hit(account: dict[str, Any], limits: dict[str, Any]) -> bool:
    daily_loss_limit = _number(limits.get("daily_loss_limit"), 0.0)
    if daily_loss_limit <= 0:
        return False
    explicit_daily_loss = _number(account.get("daily_loss"), 0.0)
    daily_pnl = _number(account.get("daily_pnl"), 0.0)
    observed_loss = max(explicit_daily_loss, abs(min(daily_pnl, 0.0)))
    return observed_loss >= daily_loss_limit


def _max_trades_limit_hit(account: dict[str, Any], limits: dict[str, Any]) -> bool:
    max_trades = int(_number(limits.get("max_trades_per_day"), 0.0))
    if max_trades <= 0:
        return False
    trades_today = int(_number(account.get("trades_today"), 0.0))
    return trades_today >= max_trades


def evaluate_risk_controls(
    signal: dict[str, Any],
    account: dict[str, Any],
    limits: dict[str, Any],
    **safety_flags: Any,
) -> dict[str, Any]:
    if not isinstance(signal, dict):
        signal = {}
    if not isinstance(account, dict):
        account = {}
    if not isinstance(limits, dict):
        limits = {}

    pair = str(signal.get("pair", "")).upper()
    action_value = signal.get("action")
    action = str(action_value).lower() if action_value is not None else None
    max_position_size_units = _number(limits.get("max_position_size_units"), 0.0)
    max_risk_percent = _number(limits.get("max_risk_percent"), 0.0)
    position_size_units = _number(signal.get("position_size_units"), 0.0)
    risk_percent = _number(signal.get("risk_percent"), 0.0)

    if action == "hold":
        position_size_units = 0.0
        risk_percent = 0.0

    daily_limit_hit = _daily_loss_limit_hit(account, limits)
    trades_limit_hit = _max_trades_limit_hit(account, limits)

    safety_reason = _safety_block_reason(safety_flags)
    if safety_reason:
        return _blocked(
            safety_reason,
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if pair not in SUPPORTED_PAIRS:
        return _blocked(
            "invalid_pair",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if action is None:
        return _blocked(
            "missing_action",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if action not in SUPPORTED_ACTIONS:
        return _blocked(
            "unsupported_action",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if max_position_size_units > 0 and position_size_units > max_position_size_units:
        return _blocked(
            "position_size_above_max",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if max_risk_percent > 0 and risk_percent > max_risk_percent:
        return _blocked(
            "risk_percent_above_max",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=trades_limit_hit,
        )
    if daily_limit_hit:
        return _blocked(
            "daily_loss_limit_hit",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            daily_loss_limit_hit=True,
            max_trades_limit_hit=trades_limit_hit,
        )
    if trades_limit_hit:
        return _blocked(
            "max_trades_limit_hit",
            pair=pair,
            action=action,
            position_size_units=position_size_units,
            max_position_size_units=max_position_size_units,
            risk_percent=risk_percent,
            max_risk_percent=max_risk_percent,
            daily_loss_limit_hit=daily_limit_hit,
            max_trades_limit_hit=True,
        )

    return {
        "allowed": True,
        "blocked_reason": "none",
        "pair": pair,
        "action": action,
        "position_size_units": position_size_units,
        "max_position_size_units": max_position_size_units,
        "risk_percent": risk_percent,
        "max_risk_percent": max_risk_percent,
        "daily_loss_limit_hit": False,
        "max_trades_limit_hit": False,
        "paper_only": True,
        "safety": PAPER_RISK_SAFETY.copy(),
        "next_safe_action": "Use this paper-only risk decision for local review only.",
    }
