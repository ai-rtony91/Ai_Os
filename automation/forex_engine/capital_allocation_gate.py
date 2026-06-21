from __future__ import annotations

from typing import Any, Mapping


STATUS_READY = "CAPITAL_ALLOCATION_READY"
STATUS_MORE_INFO = "CAPITAL_ALLOCATION_MORE_INFORMATION_REQUIRED"
STATUS_BLOCKED = "CAPITAL_ALLOCATION_BLOCKED"
STATUS_REJECTED = "CAPITAL_ALLOCATION_REJECTED"

REQUIRED_FIELDS = [
    "account_equity_declared",
    "max_account_risk_percent_declared",
    "max_trade_risk_percent_declared",
    "max_daily_loss_percent_declared",
    "max_drawdown_percent_declared",
    "single_micro_trade_only",
    "capital_allocation_requires_operator_approval",
    "paper_only_allocation_review",
]


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "capital_allocated": False,
        "capital_allocation_modified": False,
        "broker_connection_active": False,
        "credentials_accessed": False,
        "network_access": False,
        "order_execution_enabled": False,
        "live_trading_authorized": False,
        "demo_execution_active": False,
        "operator_review_required": True,
    }


def evaluate_capital_allocation_gate(metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    metadata = dict(metadata or {})
    approved_controls: list[str] = []
    blocked_controls: list[str] = []
    blocked_reasons: list[str] = []

    missing = [field for field in REQUIRED_FIELDS if field not in metadata]
    if missing:
        blocked_reasons.extend(f"missing_capital_allocation_metadata:{field}" for field in missing)
        return {
            "capital_allocation_completed": True,
            "capital_allocation_ready": False,
            "capital_allocation_status": STATUS_MORE_INFO,
            "approved_controls": [],
            "blocked_controls": [],
            "max_trade_risk_amount": 0.0,
            "max_daily_loss_amount": 0.0,
            "blocked_reasons": blocked_reasons,
            "next_safe_action": "collect_complete_capital_allocation_metadata",
            "operator_review_required": True,
            "safety": _safety(),
        }

    account_equity = float(metadata.get("account_equity_declared", 0))
    max_account_risk_percent = float(metadata.get("max_account_risk_percent_declared", 0))
    max_trade_risk_percent = float(metadata.get("max_trade_risk_percent_declared", 0))
    max_daily_loss_percent = float(metadata.get("max_daily_loss_percent_declared", 0))
    max_drawdown_percent = float(metadata.get("max_drawdown_percent_declared", 0))

    positive_checks = [
        ("account_equity_declared", account_equity > 0, "account equity declared"),
        ("max_account_risk_percent_declared", 0 < max_account_risk_percent <= 5, "max account risk percent declared"),
        ("max_trade_risk_percent_declared", 0 < max_trade_risk_percent <= 1, "max trade risk percent declared"),
        ("max_daily_loss_percent_declared", 0 < max_daily_loss_percent <= 3, "max daily loss percent declared"),
        ("max_drawdown_percent_declared", 0 < max_drawdown_percent <= 10, "max drawdown percent declared"),
        ("single_micro_trade_only", bool(metadata.get("single_micro_trade_only")) is True, "single micro-trade only"),
        (
            "capital_allocation_requires_operator_approval",
            bool(metadata.get("capital_allocation_requires_operator_approval")) is True,
            "operator approval required",
        ),
        ("paper_only_allocation_review", bool(metadata.get("paper_only_allocation_review")) is True, "paper-only allocation review enforced"),
    ]

    for field, passed, control in positive_checks:
        if passed:
            approved_controls.append(control)
        else:
            blocked_controls.append(control)
            blocked_reasons.append(f"capital_allocation_control_failed:{field}")

    if max_trade_risk_percent > max_account_risk_percent:
        blocked_reasons.append("trade_risk_exceeds_account_risk_limit")
        blocked_controls.append("trade risk within account risk")

    if max_daily_loss_percent < max_trade_risk_percent:
        blocked_reasons.append("daily_loss_limit_below_trade_risk")
        blocked_controls.append("daily loss supports trade risk")

    status = STATUS_READY if not blocked_reasons else STATUS_BLOCKED

    max_trade_risk_amount = round(account_equity * (max_trade_risk_percent / 100), 2) if account_equity > 0 else 0.0
    max_daily_loss_amount = round(account_equity * (max_daily_loss_percent / 100), 2) if account_equity > 0 else 0.0

    return {
        "capital_allocation_completed": True,
        "capital_allocation_ready": status == STATUS_READY,
        "capital_allocation_status": status,
        "approved_controls": sorted(set(approved_controls)),
        "blocked_controls": sorted(set(blocked_controls)),
        "max_trade_risk_amount": max_trade_risk_amount,
        "max_daily_loss_amount": max_daily_loss_amount,
        "blocked_reasons": blocked_reasons,
        "next_safe_action": "operator_review_capital_allocation_before_single_micro_trade_approval"
        if status == STATUS_READY
        else "resolve_capital_allocation_blockers_before_trade_approval",
        "operator_review_required": True,
        "safety": _safety(),
    }
