from __future__ import annotations

from typing import Any


SUPPORTED_PAIRS = {"EURUSD", "GBPUSD", "USDJPY"}

PAPER_STRATEGY_SAFETY = {
    "paper_only": True,
    "execution_allowed": False,
    "broker_execution": False,
    "credential_use": False,
    "live_trading": False,
    "real_orders": False,
    "real_webhooks": False,
}

BLOCKED_SCOPE_FIELDS = {
    "api_key",
    "broker_order",
    "credentials",
    "live_execution",
    "real_order",
    "webhook_url",
}


def blocked_signal(reason: str) -> dict[str, Any]:
    return {
        "allowed": False,
        "signal": "hold",
        "signal_type": "blocked",
        "blocked_reason": reason,
        **PAPER_STRATEGY_SAFETY,
    }


def _blocked_scope_reason(payload: dict[str, Any]) -> str | None:
    for field in sorted(BLOCKED_SCOPE_FIELDS):
        if payload.get(field):
            return f"{field}_blocked"
    return None


def _indicator_value(input_data: dict[str, Any], name: str) -> float | None:
    if name in input_data:
        return float(input_data[name])
    indicators = input_data.get("indicators", {})
    if isinstance(indicators, dict) and name in indicators:
        return float(indicators[name])
    return None


def evaluate_strategy(
    pair: str,
    input_data: dict[str, Any],
    *,
    live_execution: bool = False,
    broker_order: bool = False,
    credentials: Any = None,
    api_key: Any = None,
    real_order: bool = False,
    webhook_url: str | None = None,
) -> dict[str, Any]:
    unsafe_payload = {
        "live_execution": live_execution,
        "broker_order": broker_order,
        "credentials": credentials,
        "api_key": api_key,
        "real_order": real_order,
        "webhook_url": webhook_url,
    }
    blocked_reason = _blocked_scope_reason(unsafe_payload)
    if blocked_reason:
        return blocked_signal(blocked_reason)

    normalized_pair = str(pair).upper()
    if normalized_pair not in SUPPORTED_PAIRS:
        return blocked_signal("unsupported_pair")

    fast_ma = _indicator_value(input_data, "fast_ma")
    slow_ma = _indicator_value(input_data, "slow_ma")
    momentum = _indicator_value(input_data, "momentum")

    if fast_ma is None or slow_ma is None or momentum is None:
        return {
            "allowed": True,
            "signal": "hold",
            "signal_type": "paper_strategy_signal",
            "reason": "insufficient_data",
            "pair": normalized_pair,
            **PAPER_STRATEGY_SAFETY,
        }

    if fast_ma > slow_ma and momentum > 0:
        signal = "buy"
        reason = "fast_ma_above_slow_ma_with_positive_momentum"
    elif fast_ma < slow_ma and momentum < 0:
        signal = "sell"
        reason = "fast_ma_below_slow_ma_with_negative_momentum"
    else:
        signal = "hold"
        reason = "filters_not_aligned"

    return {
        "allowed": True,
        "signal": signal,
        "signal_type": "paper_strategy_signal",
        "reason": reason,
        "pair": normalized_pair,
        "fast_ma": fast_ma,
        "slow_ma": slow_ma,
        "momentum": momentum,
        **PAPER_STRATEGY_SAFETY,
    }
