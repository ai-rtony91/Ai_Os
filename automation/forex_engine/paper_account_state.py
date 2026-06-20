"""Canonical deterministic paper account state for forex paper trading."""
from __future__ import annotations

from typing import Any

DEFAULT_TIMESTAMP = "2026-01-01T00:00:00Z"
DEFAULT_MAX_RISK_PERCENT = 3.0


def calculate_available_risk(
    equity: float,
    open_risk: float,
    max_risk_percent: float = DEFAULT_MAX_RISK_PERCENT,
) -> float:
    """Return remaining risk budget in dollars."""
    cap = round(float(equity) * float(max_risk_percent) / 100.0, 8)
    return round(max(0.0, cap - float(open_risk)), 8)


def calculate_drawdown(starting_balance: float, equity: float) -> float:
    """Return absolute drawdown from starting balance."""
    return round(max(0.0, float(starting_balance) - float(equity)), 8)


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_order_placed": False,
    }


def _validate_state(state: dict[str, Any], max_risk_percent: float) -> list[str]:
    reasons: list[str] = []
    if float(state["starting_balance"]) < 0 or float(state["current_balance"]) < 0:
        reasons.append("negative_balance")
    if float(state["open_risk"]) < 0 or float(state["available_risk"]) < 0:
        reasons.append("negative_risk")
    expected_equity = round(float(state["current_balance"]) + float(state["unrealized_pl"]), 8)
    if round(float(state["equity"]), 8) != expected_equity:
        reasons.append("equity_mismatch")
    risk_cap = round(float(state["equity"]) * float(max_risk_percent) / 100.0, 8)
    if float(state["open_risk"]) > risk_cap:
        reasons.append("available_risk_above_cap")
    return reasons


def create_paper_account_state(
    starting_balance: float = 10000.0,
    current_balance: float | None = None,
    equity: float | None = None,
    realized_pl: float = 0.0,
    unrealized_pl: float = 0.0,
    open_risk: float = 0.0,
    daily_loss: float = 0.0,
    trade_count: int = 0,
    session_count: int = 0,
    max_risk_percent: float = DEFAULT_MAX_RISK_PERCENT,
    last_update: str = DEFAULT_TIMESTAMP,
) -> dict[str, Any]:
    """Create a serializable paper account state with validation evidence."""
    balance = float(starting_balance if current_balance is None else current_balance)
    account_equity = float(balance + float(unrealized_pl) if equity is None else equity)
    state = {
        "starting_balance": round(float(starting_balance), 8),
        "current_balance": round(balance, 8),
        "equity": round(account_equity, 8),
        "realized_pl": round(float(realized_pl), 8),
        "unrealized_pl": round(float(unrealized_pl), 8),
        "open_risk": round(float(open_risk), 8),
        "available_risk": calculate_available_risk(account_equity, open_risk, max_risk_percent),
        "daily_loss": round(float(daily_loss), 8),
        "drawdown": calculate_drawdown(float(starting_balance), account_equity),
        "trade_count": int(trade_count),
        "session_count": int(session_count),
        "last_update": last_update,
        "paper_only": True,
        "safety": _safety(),
    }
    reasons = _validate_state(state, max_risk_percent)
    state["valid"] = not reasons
    state["rejection_reasons"] = reasons
    return state


def apply_closed_trade_to_account(
    account_state: dict[str, Any],
    closed_trade: dict[str, Any],
    max_risk_percent: float = DEFAULT_MAX_RISK_PERCENT,
    timestamp: str = DEFAULT_TIMESTAMP,
) -> dict[str, Any]:
    """Apply one closed paper trade to account balance and risk state."""
    realized = round(float(closed_trade.get("realized_pl", 0.0)), 8)
    risk_released = round(float(closed_trade.get("risk_dollars", 0.0)), 8)
    current_balance = round(float(account_state.get("current_balance", 0.0)) + realized, 8)
    total_realized = round(float(account_state.get("realized_pl", 0.0)) + realized, 8)
    open_risk = round(max(0.0, float(account_state.get("open_risk", 0.0)) - risk_released), 8)
    daily_loss = float(account_state.get("daily_loss", 0.0))
    if realized < 0:
        daily_loss = round(daily_loss + abs(realized), 8)
    return create_paper_account_state(
        starting_balance=float(account_state.get("starting_balance", current_balance)),
        current_balance=current_balance,
        equity=round(current_balance + float(account_state.get("unrealized_pl", 0.0)), 8),
        realized_pl=total_realized,
        unrealized_pl=float(account_state.get("unrealized_pl", 0.0)),
        open_risk=open_risk,
        daily_loss=daily_loss,
        trade_count=int(account_state.get("trade_count", 0)) + 1,
        session_count=int(account_state.get("session_count", 0)),
        max_risk_percent=max_risk_percent,
        last_update=timestamp,
    )
