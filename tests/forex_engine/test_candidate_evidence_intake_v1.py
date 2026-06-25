from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
import io
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.candidate_evidence_intake_v1 import (  # noqa: E402
    CANDIDATE_EVIDENCE_BLOCKED_EXCESSIVE_DRAWDOWN,
    CANDIDATE_EVIDENCE_BLOCKED_INSUFFICIENT_SAMPLE,
    CANDIDATE_EVIDENCE_BLOCKED_INVALID_METRICS,
    CANDIDATE_EVIDENCE_BLOCKED_LOW_PROFIT_FACTOR,
    CANDIDATE_EVIDENCE_BLOCKED_MISSING_IDENTITY,
    CANDIDATE_EVIDENCE_BLOCKED_MISSING_METRICS,
    CANDIDATE_EVIDENCE_BLOCKED_NEGATIVE_EXPECTANCY,
    CANDIDATE_EVIDENCE_BLOCKED_RISK_CONTROLS,
    CANDIDATE_EVIDENCE_BLOCKED_WALK_FORWARD,
    CANDIDATE_EVIDENCE_REVIEW_READY,
    RawCandidateEvidence,
    build_sample_incomplete_candidate,
    build_sample_review_ready_candidate,
    evaluate_candidate_evidence_intake,
    result_to_operator_text,
)
from scripts.forex_delivery.run_candidate_evidence_intake_v1 import main  # noqa: E402


def review_ready_candidate() -> RawCandidateEvidence:
    return build_sample_review_ready_candidate()


def test_incomplete_sample_returns_missing_identity() -> None:
    result = evaluate_candidate_evidence_intake(build_sample_incomplete_candidate())

    assert result.classification == CANDIDATE_EVIDENCE_BLOCKED_MISSING_IDENTITY


def test_incomplete_sample_blocks_candidate_review() -> None:
    result = evaluate_candidate_evidence_intake(build_sample_incomplete_candidate())

    assert result.candidate_review_allowed is False


def test_incomplete_sample_blocks_next_demo_trade() -> None:
    result = evaluate_candidate_evidence_intake(build_sample_incomplete_candidate())

    assert result.next_demo_trade_allowed is False


def test_incomplete_sample_blocks_real_money() -> None:
    result = evaluate_candidate_evidence_intake(build_sample_incomplete_candidate())

    assert result.real_money_allowed is False


def test_incomplete_sample_blocks_compounding() -> None:
    result = evaluate_candidate_evidence_intake(build_sample_incomplete_candidate())

    assert result.compounding_allowed is False


def test_incomplete_sample_keeps_broker_action_allowed_false() -> None:
    result = evaluate_candidate_evidence_intake(build_sample_incomplete_candidate())

    assert result.broker_action_allowed is False


def test_incomplete_sample_keeps_live_trading_allowed_false() -> None:
    result = evaluate_candidate_evidence_intake(build_sample_incomplete_candidate())

    assert result.live_trading_allowed is False


def test_missing_metrics_block_review() -> None:
    candidate = replace(review_ready_candidate(), expectancy=None)

    result = evaluate_candidate_evidence_intake(candidate)

    assert result.classification == CANDIDATE_EVIDENCE_BLOCKED_MISSING_METRICS
    assert result.candidate_review_allowed is False


def test_invalid_wins_losses_block_review() -> None:
    candidate = replace(review_ready_candidate(), total_trades=20, wins=15, losses=10)

    result = evaluate_candidate_evidence_intake(candidate)

    assert result.classification == CANDIDATE_EVIDENCE_BLOCKED_INVALID_METRICS
    assert result.candidate_review_allowed is False


def test_insufficient_sample_blocks_review() -> None:
    candidate = replace(
        review_ready_candidate(),
        total_trades=10,
        wins=6,
        losses=4,
        sample_depth_sufficient=False,
    )

    result = evaluate_candidate_evidence_intake(candidate)

    assert result.classification == CANDIDATE_EVIDENCE_BLOCKED_INSUFFICIENT_SAMPLE
    assert result.candidate_review_allowed is False


def test_negative_expectancy_blocks_review() -> None:
    candidate = replace(review_ready_candidate(), expectancy=Decimal("-0.01"))

    result = evaluate_candidate_evidence_intake(candidate)

    assert result.classification == CANDIDATE_EVIDENCE_BLOCKED_NEGATIVE_EXPECTANCY
    assert result.candidate_review_allowed is False


def test_low_profit_factor_blocks_review() -> None:
    candidate = replace(review_ready_candidate(), profit_factor=Decimal("1.10"))

    result = evaluate_candidate_evidence_intake(candidate)

    assert result.classification == CANDIDATE_EVIDENCE_BLOCKED_LOW_PROFIT_FACTOR
    assert result.candidate_review_allowed is False


def test_excessive_drawdown_blocks_review() -> None:
    candidate = replace(review_ready_candidate(), max_drawdown=Decimal("0.0600"))

    result = evaluate_candidate_evidence_intake(candidate)

    assert result.classification == CANDIDATE_EVIDENCE_BLOCKED_EXCESSIVE_DRAWDOWN
    assert result.candidate_review_allowed is False


def test_uncleared_walk_forward_blocks_review() -> None:
    candidate = replace(review_ready_candidate(), walk_forward_gate_cleared=False)

    result = evaluate_candidate_evidence_intake(candidate)

    assert result.classification == CANDIDATE_EVIDENCE_BLOCKED_WALK_FORWARD
    assert result.candidate_review_allowed is False


def test_missing_risk_controls_block_review() -> None:
    candidate = replace(review_ready_candidate(), risk_controls_present=False)

    result = evaluate_candidate_evidence_intake(candidate)

    assert result.classification == CANDIDATE_EVIDENCE_BLOCKED_RISK_CONTROLS
    assert result.candidate_review_allowed is False


def test_review_ready_sample_returns_review_ready() -> None:
    result = evaluate_candidate_evidence_intake(build_sample_review_ready_candidate())

    assert result.classification == CANDIDATE_EVIDENCE_REVIEW_READY


def test_review_ready_sample_allows_candidate_review() -> None:
    result = evaluate_candidate_evidence_intake(build_sample_review_ready_candidate())

    assert result.candidate_review_allowed is True


def test_review_ready_sample_still_keeps_next_demo_trade_false() -> None:
    result = evaluate_candidate_evidence_intake(build_sample_review_ready_candidate())

    assert result.next_demo_trade_allowed is False


def test_review_ready_sample_still_keeps_real_money_false() -> None:
    result = evaluate_candidate_evidence_intake(build_sample_review_ready_candidate())

    assert result.real_money_allowed is False


def test_review_ready_sample_still_keeps_compounding_false() -> None:
    result = evaluate_candidate_evidence_intake(build_sample_review_ready_candidate())

    assert result.compounding_allowed is False


def test_operator_text_for_incomplete_sample_contains_required_terms() -> None:
    result = evaluate_candidate_evidence_intake(build_sample_incomplete_candidate())
    text = result_to_operator_text(result)

    assert "not review-ready" in text
    assert "no next demo trade" in text


def test_json_output_contains_required_sections() -> None:
    stdout = io.StringIO()
    exit_code = main(["--sample-review-ready", "--json"], stdout=stdout)
    parsed = json.loads(stdout.getvalue())

    assert exit_code == 0
    assert parsed["classification"] == CANDIDATE_EVIDENCE_REVIEW_READY
    assert "normalized_candidate" in parsed
    assert "blockers" in parsed
    assert "permissions" in parsed
    assert "next_safe_action" in parsed
