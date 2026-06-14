from __future__ import annotations

from typing import Any


ALLOWED_DECISIONS = {
    "continue_build",
    "improve_strategy",
    "improve_data",
    "improve_risk_controls",
    "stop_for_human_review",
}

PAPER_DECISION_POLICY_SAFETY = {
    "paper_only": True,
    "execution_allowed": False,
    "broker_execution": False,
    "credential_use": False,
    "live_trading": False,
    "real_orders": False,
    "real_webhooks": False,
    "network_access": False,
    "file_writes": False,
}

BLOCKED_SCOPE_FIELDS = {
    "api_key",
    "broker",
    "broker_order",
    "credentials",
    "live_execution",
    "network",
    "network_access",
    "real_order",
    "webhook",
    "webhook_url",
}


def blocked_decision(reason: str) -> dict[str, Any]:
    return {
        "allowed": False,
        "decision": "stop_for_human_review",
        "reason_code": reason,
        "decision_reasons": [reason],
        "next_safe_action": "Stop and review the paper report before continuing.",
        **PAPER_DECISION_POLICY_SAFETY,
    }


def _blocked_scope_reason(*payloads: dict[str, Any]) -> str | None:
    for payload in payloads:
        for field in sorted(BLOCKED_SCOPE_FIELDS):
            if payload.get(field):
                return f"{field}_blocked"
    return None


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _allowed_decision(
    decision: str,
    reason_code: str,
    *,
    trade_count: int,
    win_rate: float,
    total_pnl: float,
    risk_flags: list[Any],
) -> dict[str, Any]:
    if decision not in ALLOWED_DECISIONS:
        return blocked_decision("unsupported_decision")
    return {
        "allowed": True,
        "decision": decision,
        "reason_code": reason_code,
        "decision_reasons": [reason_code],
        "inputs": {
            "trade_count": trade_count,
            "win_rate": round(win_rate, 2),
            "total_pnl": round(total_pnl, 2),
            "risk_flags": risk_flags,
        },
        "next_safe_action": "Use this as a paper-only build recommendation. Do not route it to execution.",
        **PAPER_DECISION_POLICY_SAFETY,
    }


def decide_next_action(
    forex_report: dict[str, Any],
    *,
    live_execution: bool = False,
    broker_order: bool = False,
    credentials: Any = None,
    api_key: Any = None,
    real_order: bool = False,
    webhook_url: str | None = None,
    network: bool = False,
    network_access: bool = False,
) -> dict[str, Any]:
    if not isinstance(forex_report, dict) or not forex_report:
        return blocked_decision("invalid_report")

    unsafe_payload = {
        "live_execution": live_execution,
        "broker_order": broker_order,
        "credentials": credentials,
        "api_key": api_key,
        "real_order": real_order,
        "webhook_url": webhook_url,
        "network": network,
        "network_access": network_access,
    }
    blocked_reason = _blocked_scope_reason(unsafe_payload, forex_report)
    if blocked_reason:
        return blocked_decision(blocked_reason)

    if forex_report.get("allowed") is False:
        return blocked_decision("report_not_allowed")
    if forex_report.get("paper_only") is not True:
        return blocked_decision("report_not_paper_only")

    raw_flags = forex_report.get("risk_flags", [])
    risk_flags = raw_flags if isinstance(raw_flags, list) else [raw_flags]
    risk_flags = [flag for flag in risk_flags if flag]
    trade_count = int(_number(forex_report.get("trade_count", 0)))
    win_rate = _number(forex_report.get("win_rate", 0.0))
    total_pnl = _number(forex_report.get("total_pnl", 0.0))

    if risk_flags:
        return _allowed_decision(
            "stop_for_human_review",
            "risk_flags_present",
            trade_count=trade_count,
            win_rate=win_rate,
            total_pnl=total_pnl,
            risk_flags=risk_flags,
        )
    if trade_count <= 0:
        return _allowed_decision(
            "improve_data",
            "no_trades",
            trade_count=trade_count,
            win_rate=win_rate,
            total_pnl=total_pnl,
            risk_flags=risk_flags,
        )
    if win_rate < 50.0:
        return _allowed_decision(
            "improve_strategy",
            "low_win_rate",
            trade_count=trade_count,
            win_rate=win_rate,
            total_pnl=total_pnl,
            risk_flags=risk_flags,
        )
    if total_pnl < 0:
        return _allowed_decision(
            "improve_risk_controls",
            "negative_total_pnl",
            trade_count=trade_count,
            win_rate=win_rate,
            total_pnl=total_pnl,
            risk_flags=risk_flags,
        )
    return _allowed_decision(
        "continue_build",
        "acceptable_report",
        trade_count=trade_count,
        win_rate=win_rate,
        total_pnl=total_pnl,
        risk_flags=risk_flags,
    )
