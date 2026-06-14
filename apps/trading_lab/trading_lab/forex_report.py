from __future__ import annotations

from typing import Any


PAPER_REPORT_SAFETY = {
    "paper_only": True,
    "research_only": True,
    "network_access": False,
    "file_writes": False,
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
    "file_output",
    "live_execution",
    "network",
    "network_access",
    "output_path",
    "real_order",
    "webhook_url",
}


def blocked_report(reason: str) -> dict[str, Any]:
    return {
        "allowed": False,
        "report_type": "blocked",
        "blocked_reason": reason,
        "risk_flags": ["blocked_scope"],
        **PAPER_REPORT_SAFETY,
    }


def _blocked_scope_reason(*payloads: dict[str, Any]) -> str | None:
    for payload in payloads:
        for field in sorted(BLOCKED_SCOPE_FIELDS):
            if payload.get(field):
                return f"{field}_blocked"
    return None


def _safe_number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _risk_flags(trade_count: int, win_rate: float, total_pnl: float, backtest_summary: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    if trade_count == 0:
        flags.append("no_trades")
    if win_rate < 50.0 and trade_count > 0:
        flags.append("win_rate_below_50")
    if total_pnl < 0:
        flags.append("negative_total_pnl")
    if int(backtest_summary.get("trades_blocked", 0)) > 0:
        flags.append("blocked_backtest_trades_present")
    return flags


def build_report(
    backtest_summary: dict[str, Any],
    ledger_summary: dict[str, Any],
    strategy_metadata: dict[str, Any],
    *,
    live_execution: bool = False,
    broker_order: bool = False,
    credentials: Any = None,
    api_key: Any = None,
    real_order: bool = False,
    webhook_url: str | None = None,
    network: bool = False,
    network_access: bool = False,
    output_path: str | None = None,
    file_output: bool = False,
) -> dict[str, Any]:
    unsafe_payload = {
        "live_execution": live_execution,
        "broker_order": broker_order,
        "credentials": credentials,
        "api_key": api_key,
        "real_order": real_order,
        "webhook_url": webhook_url,
        "network": network,
        "network_access": network_access,
        "output_path": output_path,
        "file_output": file_output,
    }
    blocked_reason = _blocked_scope_reason(unsafe_payload, backtest_summary, ledger_summary, strategy_metadata)
    if blocked_reason:
        return blocked_report(blocked_reason)

    trade_count = int(ledger_summary.get("trade_count", backtest_summary.get("trades_allowed", 0)))
    winning_trades = int(ledger_summary.get("winning_trades", 0))
    win_rate = round((winning_trades / trade_count) * 100.0, 2) if trade_count else 0.0
    total_pnl = round(_safe_number(ledger_summary.get("total_pnl", 0.0)), 2)
    flags = _risk_flags(trade_count, win_rate, total_pnl, backtest_summary)

    return {
        "allowed": True,
        "report_type": "paper_scorecard",
        "trade_count": trade_count,
        "win_rate": win_rate,
        "total_pnl": total_pnl,
        "risk_flags": flags,
        "strategy": {
            "name": strategy_metadata.get("name", "forex_strategy_rules"),
            "version": strategy_metadata.get("version", "paper-v1"),
            "signal": strategy_metadata.get("signal", "hold"),
        },
        "backtest": {
            "trades_considered": int(backtest_summary.get("trades_considered", 0)),
            "trades_allowed": int(backtest_summary.get("trades_allowed", 0)),
            "trades_blocked": int(backtest_summary.get("trades_blocked", 0)),
            "ending_balance": _safe_number(backtest_summary.get("ending_balance", 0.0)),
        },
        **PAPER_REPORT_SAFETY,
    }
