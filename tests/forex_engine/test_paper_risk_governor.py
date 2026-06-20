"""Tests for paper risk governor."""
from __future__ import annotations

from automation.forex_engine.paper_account_state import create_paper_account_state
from automation.forex_engine.paper_risk_governor import evaluate_paper_trade_risk


def _safe_candidate() -> dict[str, float | str]:
    return {
        "symbol": "EURUSD",
        "entry": 1.1,
        "stop": 1.095,
        "target": 1.11,
        "risk_percent": 1.0,
        "spread": 0.0002,
    }


def test_risk_governor_approves_safe_trade():
    result = evaluate_paper_trade_risk(_safe_candidate(), create_paper_account_state())
    assert result["risk_passed"] is True
    assert result["paper_only"] is True


def test_risk_governor_rejects_core_controls():
    candidate = _safe_candidate()
    candidate["stop"] = candidate["entry"]
    candidate["spread"] = 0.01
    candidate["risk_percent"] = 5.0
    open_trades = [
        {"symbol": "GBPUSD", "status": "active"},
        {"symbol": "USDJPY", "status": "active"},
        {"symbol": "AUDUSD", "status": "active"},
    ]
    result = evaluate_paper_trade_risk(candidate, create_paper_account_state(), open_trades)
    assert result["risk_passed"] is False
    assert result["rejection_reasons"][:4] == [
        "stop_required",
        "risk_percent_too_high",
        "max_open_trades_hit",
        "spread_too_high",
    ]
