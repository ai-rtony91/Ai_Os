"""Tests for canonical paper account state."""
from __future__ import annotations

from automation.forex_engine.paper_account_state import apply_closed_trade_to_account, create_paper_account_state


def test_account_state_creation_and_closed_trade_balance_update():
    account = create_paper_account_state(starting_balance=10000.0)
    updated = apply_closed_trade_to_account(account, {"realized_pl": 125.0, "risk_dollars": 100.0})
    assert account["valid"] is True
    assert updated["current_balance"] == 10125.0
    assert updated["realized_pl"] == 125.0
    assert updated["trade_count"] == 1


def test_impossible_account_state_rejected():
    account = create_paper_account_state(starting_balance=10000.0, current_balance=-1.0, open_risk=-1.0)
    assert account["valid"] is False
    assert "negative_balance" in account["rejection_reasons"]
    assert "negative_risk" in account["rejection_reasons"]
