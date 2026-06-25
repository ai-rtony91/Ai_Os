from __future__ import annotations

from dataclasses import replace

import pytest

from automation.forex_engine.demo_order_plan_builder_v1 import (
    DEMO_ORDER_PLAN_BLOCKED_ACCOUNT,
    DEMO_ORDER_PLAN_BLOCKED_OPERATOR_APPROVAL,
    DEMO_ORDER_PLAN_BLOCKED_POSITION_SIZE,
    DEMO_ORDER_PLAN_BLOCKED_RISK,
    DEMO_ORDER_PLAN_BLOCKED_STRATEGY,
    DEMO_ORDER_PLAN_REVIEW_READY,
    build_demo_order_plan,
    build_sample_demo_order_plan_input,
)


def test_ready_order_plan_review_ready() -> None:
    result = build_demo_order_plan(build_sample_demo_order_plan_input())
    assert result.classification == DEMO_ORDER_PLAN_REVIEW_READY
    assert result.order_plan_review_allowed is True


@pytest.mark.parametrize(
    ("updates", "expected"),
    [
        ({"account_ready": False}, DEMO_ORDER_PLAN_BLOCKED_ACCOUNT),
        ({"risk_ready": False}, DEMO_ORDER_PLAN_BLOCKED_RISK),
        ({"position_size_ready": False}, DEMO_ORDER_PLAN_BLOCKED_POSITION_SIZE),
        ({"supertrend_status": "SUPER_TREND_NOT_READY"}, DEMO_ORDER_PLAN_BLOCKED_STRATEGY),
        ({"operator_review_required": False}, DEMO_ORDER_PLAN_BLOCKED_OPERATOR_APPROVAL),
    ],
)
def test_order_plan_blocks_required_conditions(updates: dict[str, object], expected: str) -> None:
    result = build_demo_order_plan(replace(build_sample_demo_order_plan_input(), **updates))
    assert result.classification == expected


@pytest.mark.parametrize(
    "permission",
    [
        "demo_execution_allowed",
        "broker_action_allowed",
        "real_money_allowed",
        "compounding_allowed",
        "bank_movement_allowed",
    ],
)
def test_order_plan_keeps_protected_permissions_false(permission: str) -> None:
    result = build_demo_order_plan(build_sample_demo_order_plan_input())
    assert getattr(result, permission) is False
