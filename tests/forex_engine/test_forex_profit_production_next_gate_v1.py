from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_profit_production_next_gate_v1 import (  # noqa: E402
    BLOCKED_EXCESSIVE_DRAWDOWN,
    BLOCKED_INSUFFICIENT_SAMPLE,
    BLOCKED_LOW_PROFIT_FACTOR,
    BLOCKED_MISSING_EVIDENCE,
    BLOCKED_NEGATIVE_EXPECTANCY,
    BLOCKED_RISK_CONTROL_FAILURE,
    READY_FOR_DEMO_ONLY_NEXT_STEP,
    READY_FOR_OWNER_REVIEW,
    build_report_markdown,
    evaluate_forex_profit_production_next_gate_v1,
)


def _base_evidence(**overrides: object) -> dict[str, object]:
    evidence: dict[str, object] = {
        "total_trades": 40,
        "expectancy": 0.25,
        "profit_factor": 1.35,
        "max_drawdown_pct": 5.5,
        "risk_controls_present": True,
        "risk_controls_passed": True,
        "owner_approval_required": True,
        "live_trading_requested": False,
    }
    evidence.update(overrides)
    return evidence


@pytest.mark.parametrize("evidence", [None, {}])
def test_missing_evidence_blocks(evidence: object) -> None:
    result = evaluate_forex_profit_production_next_gate_v1(evidence)
    assert result["status"] == BLOCKED_MISSING_EVIDENCE
    assert result["passed"] is False
    assert result["blockers"]
    assert result["demo_next_step_ready"] is False
    assert result["live_trading_allowed"] is False


def test_insufficient_sample_blocks() -> None:
    result = evaluate_forex_profit_production_next_gate_v1(
        _base_evidence(total_trades=29)
    )
    assert result["status"] == BLOCKED_INSUFFICIENT_SAMPLE
    assert result["passed"] is False
    assert result["blockers"]
    assert result["demo_next_step_ready"] is False


def test_negative_expectancy_blocks() -> None:
    result = evaluate_forex_profit_production_next_gate_v1(
        _base_evidence(expectancy=0)
    )
    assert result["status"] == BLOCKED_NEGATIVE_EXPECTANCY
    assert result["passed"] is False
    assert result["blockers"]


def test_low_profit_factor_blocks() -> None:
    result = evaluate_forex_profit_production_next_gate_v1(
        _base_evidence(profit_factor=1.09)
    )
    assert result["status"] == BLOCKED_LOW_PROFIT_FACTOR
    assert result["passed"] is False
    assert result["blockers"]


def test_drawdown_blocks() -> None:
    result = evaluate_forex_profit_production_next_gate_v1(
        _base_evidence(max_drawdown_pct=10.01)
    )
    assert result["status"] == BLOCKED_EXCESSIVE_DRAWDOWN
    assert result["passed"] is False
    assert result["blockers"]


def test_risk_controls_missing_block() -> None:
    result = evaluate_forex_profit_production_next_gate_v1(
        _base_evidence(risk_controls_present=False)
    )
    assert result["status"] == BLOCKED_RISK_CONTROL_FAILURE
    assert "risk_controls_present_false" in result["blockers"]
    assert result["passed"] is False


def test_risk_controls_failing_block() -> None:
    result = evaluate_forex_profit_production_next_gate_v1(
        _base_evidence(risk_controls_passed=False)
    )
    assert result["status"] == BLOCKED_RISK_CONTROL_FAILURE
    assert "risk_controls_passed_false" in result["blockers"]
    assert result["passed"] is False


def test_live_request_is_blocked() -> None:
    result = evaluate_forex_profit_production_next_gate_v1(
        _base_evidence(live_trading_requested=True)
    )
    assert result["status"] == BLOCKED_RISK_CONTROL_FAILURE
    assert "live_trading_requested_true" in result["blockers"]
    assert result["passed"] is False


def test_valid_evidence_reaches_owner_review() -> None:
    result = evaluate_forex_profit_production_next_gate_v1(
        _base_evidence(owner_approval_required=True)
    )
    assert result["status"] == READY_FOR_OWNER_REVIEW
    assert result["passed"] is True
    assert result["demo_next_step_ready"] is True
    assert result["live_trading_allowed"] is False
    assert result["blockers"] == []
    assert result["warnings"]
    assert result["next_safe_action"]


def test_valid_evidence_reaches_demo_only_next_step() -> None:
    result = evaluate_forex_profit_production_next_gate_v1(
        _base_evidence(owner_approval_required=False)
    )
    assert result["status"] == READY_FOR_DEMO_ONLY_NEXT_STEP
    assert result["passed"] is True
    assert result["demo_next_step_ready"] is True
    assert result["live_trading_allowed"] is False
    assert result["blockers"] == []
    assert result["warnings"]
    assert result["next_safe_action"]


def test_serialized_output_does_not_contain_live_or_profit_claims() -> None:
    result = evaluate_forex_profit_production_next_gate_v1(
        _base_evidence(owner_approval_required=False)
    )
    serialized = json.dumps(result, sort_keys=True).lower()
    report = build_report_markdown(result).lower()
    banned_phrases = [
        "live ready",
        "guaranteed profit",
        "approved for live",
        "safe to trade live",
        "profits guaranteed",
    ]
    for phrase in banned_phrases:
        assert phrase not in serialized
        assert phrase not in report
