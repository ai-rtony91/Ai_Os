from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from automation.forex_engine.broker_read_only_snapshot_contract_v1 import (
    build_sample_market_closed_snapshot,
    build_sample_unknown_exposure_snapshot,
    build_sample_valid_broker_snapshot,
)
from automation.forex_engine.demo_account_readiness_gate_v1 import (
    DEMO_ACCOUNT_BLOCKED_BROKER_SNAPSHOT,
    DEMO_ACCOUNT_BLOCKED_MARKET,
    DEMO_ACCOUNT_BLOCKED_SPREAD,
    DEMO_ACCOUNT_BLOCKED_UNKNOWN_EXPOSURE,
    DEMO_ACCOUNT_READY_FOR_REVIEW,
    DemoAccountReadinessInput,
    build_sample_blocked_account_input,
    build_sample_ready_account_input,
    evaluate_demo_account_readiness,
)


def test_ready_account_allows_review() -> None:
    result = evaluate_demo_account_readiness(build_sample_ready_account_input())
    assert result.classification == DEMO_ACCOUNT_READY_FOR_REVIEW
    assert result.account_review_allowed is True


def test_blocked_snapshot_blocks_account() -> None:
    result = evaluate_demo_account_readiness(build_sample_blocked_account_input())
    assert result.classification == DEMO_ACCOUNT_BLOCKED_BROKER_SNAPSHOT


def test_market_closed_blocks_account() -> None:
    result = evaluate_demo_account_readiness(DemoAccountReadinessInput(build_sample_market_closed_snapshot()))
    assert result.classification == DEMO_ACCOUNT_BLOCKED_MARKET


def test_spread_above_max_blocks_account() -> None:
    snapshot = replace(build_sample_valid_broker_snapshot(), spread=Decimal("2.0"))
    result = evaluate_demo_account_readiness(DemoAccountReadinessInput(snapshot))
    assert result.classification == DEMO_ACCOUNT_BLOCKED_SPREAD


def test_unknown_exposure_blocks_account() -> None:
    result = evaluate_demo_account_readiness(DemoAccountReadinessInput(build_sample_unknown_exposure_snapshot()))
    assert result.classification == DEMO_ACCOUNT_BLOCKED_UNKNOWN_EXPOSURE


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
def test_account_readiness_keeps_protected_permissions_false(permission: str) -> None:
    result = evaluate_demo_account_readiness(build_sample_ready_account_input())
    assert getattr(result, permission) is False
