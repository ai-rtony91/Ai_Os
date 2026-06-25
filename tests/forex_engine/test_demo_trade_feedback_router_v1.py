from __future__ import annotations

from dataclasses import replace

import pytest

from automation.forex_engine.demo_trade_feedback_router_v1 import (
    FEEDBACK_BLOCKED_MISSING_POST_TRADE_EVIDENCE,
    FEEDBACK_BLOCKED_UNRECONCILED,
    FEEDBACK_ROUTED_LOSS_REQUIRES_REVIEW,
    FEEDBACK_ROUTED_PROFIT_IMPROVES_EVIDENCE,
    build_sample_feedback_loss_input,
    build_sample_feedback_profit_input,
    feedback_to_jsonable_dict,
    route_demo_trade_feedback,
)


def test_profit_feedback_routes_to_proof_improvement() -> None:
    result = route_demo_trade_feedback(build_sample_feedback_profit_input())
    assert result.classification == FEEDBACK_ROUTED_PROFIT_IMPROVES_EVIDENCE
    assert result.routed is True


def test_loss_feedback_routes_to_review() -> None:
    result = route_demo_trade_feedback(build_sample_feedback_loss_input())
    assert result.classification == FEEDBACK_ROUTED_LOSS_REQUIRES_REVIEW


def test_missing_evidence_blocks_feedback() -> None:
    sample = replace(build_sample_feedback_profit_input(), post_trade_evidence_present=False)
    result = route_demo_trade_feedback(sample)
    assert result.classification == FEEDBACK_BLOCKED_MISSING_POST_TRADE_EVIDENCE


def test_unreconciled_evidence_blocks_feedback() -> None:
    sample = replace(build_sample_feedback_profit_input(), broker_reconciled=False)
    result = route_demo_trade_feedback(sample)
    assert result.classification == FEEDBACK_BLOCKED_UNRECONCILED


@pytest.mark.parametrize(
    "target",
    [
        "Profit Proof Ledger",
        "Strategy Proof Engine",
        "Expectancy Strength Router",
        "Demo Review Engine",
        "Strategy Promotion Router",
        "Real Evidence Depth Engine",
    ],
)
def test_feedback_targets_include_proof_systems(target: str) -> None:
    data = feedback_to_jsonable_dict(route_demo_trade_feedback())
    assert target in data["targets"]
