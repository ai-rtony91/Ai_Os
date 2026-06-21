from __future__ import annotations

from typing import Any, Mapping


STATUS_READY = "BROKER_POLICY_READY"
STATUS_MORE_INFO = "BROKER_POLICY_MORE_INFORMATION_REQUIRED"
STATUS_BLOCKED = "BROKER_POLICY_BLOCKED"
STATUS_REJECTED = "BROKER_POLICY_REJECTED"

REQUIRED_FIELDS = [
    "broker_name",
    "account_type",
    "jurisdiction",
    "instrument_type",
    "symbol",
    "long_allowed",
    "short_allowed",
    "hedging_allowed",
    "fifo_required",
    "margin_trading_allowed",
    "max_leverage",
    "min_trade_size",
    "max_trade_size",
    "supported_order_types",
    "trading_sessions",
    "paper_only_policy_review",
]


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "broker_connection_active": False,
        "broker_access": False,
        "credentials_access": False,
        "network_access": False,
        "order_execution_enabled": False,
        "live_trading_authorized": False,
        "demo_execution_active": False,
        "capital_allocation_modified": False,
        "operator_review_required": True,
    }


def evaluate_broker_policy_readiness(
    policy: Mapping[str, Any] | None,
    intended_strategy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    policy = dict(policy or {})
    intended_strategy = dict(intended_strategy or {})

    blocked_reasons: list[str] = []
    approved_capabilities: list[str] = []
    blocked_capabilities: list[str] = []

    missing = [field for field in REQUIRED_FIELDS if field not in policy]
    if missing:
        blocked_reasons.extend(f"missing_policy_metadata:{field}" for field in missing)
        return {
            "policy_readiness_completed": True,
            "broker_policy_ready": False,
            "account_policy_status": STATUS_MORE_INFO,
            "approved_capabilities": [],
            "blocked_capabilities": blocked_capabilities,
            "blocked_reasons": blocked_reasons,
            "next_safe_action": "collect_complete_broker_policy_metadata",
            "operator_review_required": True,
            "safety": _safety(),
        }

    if not bool(policy.get("paper_only_policy_review")):
        blocked_reasons.append("paper_only_policy_review_required")
        blocked_capabilities.append("policy_review")
        status = STATUS_BLOCKED
    else:
        status = STATUS_READY

    symbol = intended_strategy.get("symbol", policy.get("symbol"))
    direction = intended_strategy.get("direction", "both")
    order_type = intended_strategy.get("order_type", "market")
    session = intended_strategy.get("session", "regular")
    trade_size = float(intended_strategy.get("trade_size", policy.get("min_trade_size", 0)))
    required_leverage = float(intended_strategy.get("required_leverage", 1))

    if symbol != policy.get("symbol"):
        blocked_reasons.append("instrument_symbol_not_supported")
        blocked_capabilities.append("instrument compatibility")
    else:
        approved_capabilities.append("instrument compatibility")

    if direction in {"buy", "both"}:
        if policy.get("long_allowed") is True:
            approved_capabilities.append("long trading")
        else:
            blocked_reasons.append("long_trading_not_allowed")
            blocked_capabilities.append("long trading")

    if direction in {"sell", "both"}:
        if policy.get("short_allowed") is True:
            approved_capabilities.append("short trading")
            approved_capabilities.append("bidirectional strategy support")
        else:
            blocked_reasons.append("short_trading_not_allowed")
            blocked_capabilities.append("short trading")
            blocked_capabilities.append("bidirectional strategy support")

    if policy.get("fifo_required") is True and policy.get("hedging_allowed") is True:
        blocked_reasons.append("hedging_fifo_conflict_requires_review")
        blocked_capabilities.append("hedging compatibility")
        blocked_capabilities.append("FIFO compatibility")
    else:
        approved_capabilities.append("hedging compatibility")
        approved_capabilities.append("FIFO compatibility")

    if not policy.get("margin_trading_allowed") and required_leverage > 1:
        blocked_reasons.append("margin_or_leverage_not_allowed")
        blocked_capabilities.append("margin/leverage compatibility")
    elif required_leverage > float(policy.get("max_leverage")):
        blocked_reasons.append("required_leverage_exceeds_broker_max")
        blocked_capabilities.append("margin/leverage compatibility")
    else:
        approved_capabilities.append("margin/leverage compatibility")

    if trade_size < float(policy.get("min_trade_size")) or trade_size > float(policy.get("max_trade_size")):
        blocked_reasons.append("trade_size_outside_broker_limits")
        blocked_capabilities.append("trade size compatibility")
    else:
        approved_capabilities.append("trade size compatibility")

    if order_type not in set(policy.get("supported_order_types", [])):
        blocked_reasons.append("unsupported_order_type")
        blocked_capabilities.append("order type compatibility")
    else:
        approved_capabilities.append("order type compatibility")

    if session not in set(policy.get("trading_sessions", [])):
        blocked_reasons.append("unsupported_trading_session")
        blocked_capabilities.append("session compatibility")
    else:
        approved_capabilities.append("session compatibility")

    if blocked_reasons and status == STATUS_READY:
        status = STATUS_BLOCKED

    return {
        "policy_readiness_completed": True,
        "broker_policy_ready": status == STATUS_READY,
        "account_policy_status": status,
        "approved_capabilities": sorted(set(approved_capabilities)),
        "blocked_capabilities": sorted(set(blocked_capabilities)),
        "blocked_reasons": blocked_reasons,
        "next_safe_action": "operator_review_broker_policy_before_credentials_or_execution"
        if status == STATUS_READY
        else "resolve_broker_policy_blockers_before_any_future_broker_stage",
        "operator_review_required": True,
        "safety": _safety(),
    }
