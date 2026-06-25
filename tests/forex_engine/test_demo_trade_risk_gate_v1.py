from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from automation.forex_engine.demo_trade_risk_gate_v1 import (
    DEMO_RISK_BLOCKED_DAILY_LOSS,
    DEMO_RISK_BLOCKED_DUPLICATE_ORDER,
    DEMO_RISK_BLOCKED_KILL_SWITCH,
    DEMO_RISK_BLOCKED_MARKET_HOURS,
    DEMO_RISK_BLOCKED_MAX_RISK,
    DEMO_RISK_BLOCKED_MISSING_STOP_LOSS,
    DEMO_RISK_BLOCKED_MISSING_TAKE_PROFIT,
    DEMO_RISK_BLOCKED_OPEN_TRADES,
    DEMO_RISK_BLOCKED_PENDING_ORDERS,
    DEMO_RISK_BLOCKED_SPREAD,
    DEMO_RISK_BLOCKED_STRATEGY_NOT_READY,
    DEMO_RISK_REVIEW_READY,
    build_sample_valid_risk_input,
    evaluate_demo_trade_risk,
)


def test_valid_risk_passes_for_review() -> None:
    result = evaluate_demo_trade_risk(build_sample_valid_risk_input())
    assert result.classification == DEMO_RISK_REVIEW_READY
    assert result.risk_review_allowed is True


@pytest.mark.parametrize(
    ("updates", "expected"),
    [
        ({"proposed_risk_per_trade": Decimal("100.01")}, DEMO_RISK_BLOCKED_MAX_RISK),
        ({"current_daily_loss": Decimal("250.00")}, DEMO_RISK_BLOCKED_DAILY_LOSS),
        ({"current_open_trades": 1}, DEMO_RISK_BLOCKED_OPEN_TRADES),
        ({"current_pending_orders": 1}, DEMO_RISK_BLOCKED_PENDING_ORDERS),
        ({"current_spread": Decimal("1.6")}, DEMO_RISK_BLOCKED_SPREAD),
        ({"stop_loss_present": False}, DEMO_RISK_BLOCKED_MISSING_STOP_LOSS),
        ({"take_profit_present": False}, DEMO_RISK_BLOCKED_MISSING_TAKE_PROFIT),
        ({"duplicate_order_guard_clear": False}, DEMO_RISK_BLOCKED_DUPLICATE_ORDER),
        ({"kill_switch_clear": False}, DEMO_RISK_BLOCKED_KILL_SWITCH),
        ({"market_hours_clear": False}, DEMO_RISK_BLOCKED_MARKET_HOURS),
        ({"strategy_review_ready": False}, DEMO_RISK_BLOCKED_STRATEGY_NOT_READY),
    ],
)
def test_risk_gate_blocks_required_conditions(updates: dict[str, object], expected: str) -> None:
    result = evaluate_demo_trade_risk(replace(build_sample_valid_risk_input(), **updates))
    assert result.classification == expected
