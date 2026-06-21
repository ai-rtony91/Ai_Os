"""Tests for governed demo advancement gate."""
from __future__ import annotations

import inspect

from automation.forex_engine.governed_demo_advancement_gate import (
    DECISION_DEMO_ADVANCEMENT_APPROVED,
    DECISION_DEMO_ADVANCEMENT_BLOCKED,
    DECISION_MORE_EVIDENCE_REQUIRED,
    run_governed_demo_advancement_gate,
)
from automation.forex_engine.demo_validation_result_aggregator import (
    RECOMMENDATION_DEMO_VALIDATION_PASSED,
    RECOMMENDATION_DEMO_VALIDATION_FAILED,
)


def _safe_payload():
    return {
        "paper_only": True,
        "broker_access": False,
        "credentials_access": False,
        "network_access": False,
        "live_trading_active": False,
        "demo_execution_active": False,
        "capital_allocation_modified": False,
    }


def _aggregator_payload(
    *,
    passed: bool = True,
    recommendation: str = DECISION_DEMO_ADVANCEMENT_APPROVED,
    score: float = 85.0,
    stable: bool = True,
    safe: dict[str, object] | None = None,
    blocked: list[str] | None = None,
    operator_review_required: bool = True,
) -> dict[str, object]:
    return {
        "aggregation_completed": True,
        "demo_validation_passed": passed,
        "stable_winner": {"strategy_name": "DAY_TRADING_BREAKOUT_V1", "safety": safe or _safe_payload()} if stable else {},
        "portfolio_promotion_status": "PORTFOLIO_DEMO_REVIEW_CANDIDATE",
        "demo_validation_score": score,
        "promotion_recommendation": recommendation,
        "blocked_reasons": blocked or [],
        "next_safe_action": "collect_more_evidence",
        "operator_review_required": operator_review_required,
        "safety": safe or _safe_payload(),
    }


def test_demo_advancement_approved():
    result = run_governed_demo_advancement_gate(
        aggregator_result=_aggregator_payload(
            passed=True,
            recommendation=RECOMMENDATION_DEMO_VALIDATION_PASSED,
            operator_review_required=True,
            stable=True,
        )
    )
    assert result["gate_completed"] is True
    assert result["demo_advancement_approved"] is True
    assert result["demo_validation_passed"] is True
    assert result["stable_winner"]["strategy_name"] == "DAY_TRADING_BREAKOUT_V1"
    assert result["promotion_recommendation"] == DECISION_DEMO_ADVANCEMENT_APPROVED
    assert result["operator_review_required"] is True
    assert result["next_safe_action"] == "request_governed_demo_approval"


def test_missing_stable_winner_blocked():
    result = run_governed_demo_advancement_gate(
        aggregator_result=_aggregator_payload(
            passed=True,
            recommendation=RECOMMENDATION_DEMO_VALIDATION_PASSED,
            stable=False,
        )
    )
    assert result["demo_advancement_approved"] is False
    assert "missing_stable_winner" in result["blocked_reasons"]
    assert result["promotion_recommendation"] == DECISION_MORE_EVIDENCE_REQUIRED


def test_failed_validation_blocked():
    result = run_governed_demo_advancement_gate(
        aggregator_result=_aggregator_payload(
            passed=False,
            recommendation=RECOMMENDATION_DEMO_VALIDATION_PASSED,
        )
    )
    assert result["demo_advancement_approved"] is False
    assert "demo_validation_not_passed" in result["blocked_reasons"]
    assert result["promotion_recommendation"] == DECISION_DEMO_ADVANCEMENT_BLOCKED


def test_failed_promotion_recommendation_blocked():
    result = run_governed_demo_advancement_gate(
        aggregator_result=_aggregator_payload(
            passed=True,
            recommendation=RECOMMENDATION_DEMO_VALIDATION_FAILED,
        )
    )
    assert result["demo_advancement_approved"] is False
    assert any(
        reason.startswith("promotion_recommendation_not_passed")
        for reason in result["blocked_reasons"]
    )
    assert result["promotion_recommendation"] == DECISION_DEMO_ADVANCEMENT_BLOCKED


def test_unsafe_evidence_blocked():
    unsafe = _safe_payload()
    unsafe["broker_access"] = True
    result = run_governed_demo_advancement_gate(
        aggregator_result=_aggregator_payload(
            passed=True,
            recommendation=RECOMMENDATION_DEMO_VALIDATION_PASSED,
            safe=unsafe,
        )
    )
    assert result["demo_advancement_approved"] is False
    assert "safety_violation_detected" in result["blocked_reasons"]
    assert result["promotion_recommendation"] == DECISION_DEMO_ADVANCEMENT_BLOCKED


def test_operator_review_required():
    result = run_governed_demo_advancement_gate(
        aggregator_result=_aggregator_payload(
            passed=True,
            recommendation=RECOMMENDATION_DEMO_VALIDATION_PASSED,
            operator_review_required=False,
        )
    )
    assert result["demo_advancement_approved"] is False
    assert result["operator_review_required"] is False
    assert "operator_review_required_false" in result["blocked_reasons"]


def test_deterministic_output():
    payload = _aggregator_payload(
        passed=True,
        recommendation=RECOMMENDATION_DEMO_VALIDATION_PASSED,
        stable=True,
    )
    first = run_governed_demo_advancement_gate(aggregator_result=payload)
    second = run_governed_demo_advancement_gate(aggregator_result=payload)
    assert first == second


def test_safety_source_scan():
    source = inspect.getsource(__import__("automation.forex_engine.governed_demo_advancement_gate", fromlist=["*"]))
    forbidden = (
        "import requests",
        "from requests",
        "import urllib",
        "from urllib",
        "import subprocess",
        "from subprocess",
        "import socket",
        "from socket",
        "open(",
        "write_text",
        "write_bytes",
        "os.environ",
        "getenv(",
        "broker_sdk",
        "oanda",
    )
    for token in forbidden:
        assert token not in source
