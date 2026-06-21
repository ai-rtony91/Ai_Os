"""Tests for live-candidate readiness spine."""
from __future__ import annotations

import inspect

from automation.forex_engine.demo_phase_evidence_tracker import (
    DEMO_PHASE_TRACKING,
    DEMO_PHASE_VALIDATION_PASSED,
)
from automation.forex_engine.demo_phase_operator_review_packet import (
    DECISION_APPROVE_CONTINUE_DEMO_PHASE,
    DECISION_REQUEST_MORE_EVIDENCE,
    DECISION_REJECT_DEMO_ADVANCEMENT,
    run_demo_phase_operator_review_packet,
)
from automation.forex_engine.demo_phase_performance_monitor import (
    DECISION_DEGRADING,
    DECISION_IMPROVING,
    DECISION_RISK_VIOLATION,
    DECISION_STABLE,
)
from automation.forex_engine.live_candidate_readiness_spine import (
    DECISION_APPROVE_CONTINUE_DEMO_PHASE,
    LIVE_CANDIDATE_BLOCKED,
    LIVE_CANDIDATE_MORE_DEMO_EVIDENCE_REQUIRED,
    LIVE_CANDIDATE_REVIEW_READY,
    LIVE_CANDIDATE_REJECTED,
    run_live_candidate_readiness_spine,
)


def _safe_context():
    return {
        "paper_only": True,
        "broker_access": False,
        "credentials_access": False,
        "network_access": False,
        "live_trading_authorized": False,
        "demo_execution_active": False,
        "order_execution_enabled": False,
        "capital_allocation_modified": False,
        "operator_approval_required": True,
    }


def _monitor(state: str, risk_status: str = "RISK_OK", reasons: list[str] | None = None):
    return {
        "monitor_completed": True,
        "performance_state": state,
        "risk_status": risk_status,
        "blocked_reasons": reasons or [],
        "expectancy_trend": "STABLE",
        "drawdown_trend": "STABLE",
        "consistency_trend": "STABLE",
        "next_safe_action": "monitor_continuously",
        "safety": _safe_context(),
        "mode": "DEMO_PHASE_PERFORMANCE_MONITOR",
    }


def _stable_winner():
    return {"strategy_name": "DAY_TRADING_BREAKOUT_V1", "strategy_version": "v1", "symbol": "EURUSD"}


def _agg_result(validator_passed: bool = True, stable: bool = True):
    return {
        "demo_validation_passed": validator_passed,
        "stable_winner": _stable_winner() if stable else {},
        "demo_review_ready": True,
        "scorecard_passed": validator_passed,
        "portfolio_promotion_status": "PORTFOLIO_DEMO_REVIEW_CANDIDATE",
        "next_safe_action": "ready",
        "promotion_recommendation": "DEMO_VALIDATION_PASSED",
        "safety": _safe_context(),
    }


def test_live_candidate_review_ready():
    result = run_live_candidate_readiness_spine(
        demo_validation_result=_agg_result(),
        tracker_result={"demo_phase_status": DEMO_PHASE_VALIDATION_PASSED},
        monitor_result=_monitor(DECISION_IMPROVING),
        safe_context=_safe_context(),
    )
    assert result["readiness_completed"] is True
    assert result["live_candidate_status"] == LIVE_CANDIDATE_REVIEW_READY
    assert result["live_candidate_review_ready"] is True
    assert result["demo_validation_passed"] is True
    assert result["operator_decision"] == DECISION_APPROVE_CONTINUE_DEMO_PHASE
    assert result["operator_approval_required"] is True


def test_more_demo_evidence_required():
    result = run_live_candidate_readiness_spine(
        demo_validation_result=_agg_result(),
        tracker_result={"demo_phase_status": DEMO_PHASE_TRACKING},
        monitor_result=_monitor(DECISION_STABLE),
        safe_context=_safe_context(),
    )
    assert result["live_candidate_status"] == LIVE_CANDIDATE_MORE_DEMO_EVIDENCE_REQUIRED
    assert result["operator_decision"] == DECISION_APPROVE_CONTINUE_DEMO_PHASE
    assert result["readiness_reasons"] == ["demo_phase_tracking", "performance_state_acceptable", "risk_status_acceptable", "operator_review_approved", "operator_approval_required"]


def test_blocked_missing_stable_winner():
    result = run_live_candidate_readiness_spine(
        demo_validation_result=_agg_result(stable=False),
        tracker_result={"demo_phase_status": DEMO_PHASE_VALIDATION_PASSED},
        monitor_result=_monitor(DECISION_STABLE),
        safe_context=_safe_context(),
    )
    assert result["live_candidate_status"] == LIVE_CANDIDATE_REJECTED
    assert "missing_stable_winner" in result["blocked_reasons"]
    assert result["readiness_completed"] is True


def test_blocked_failed_demo_validation():
    result = run_live_candidate_readiness_spine(
        demo_validation_result=_agg_result(validator_passed=False),
        tracker_result={"demo_phase_status": DEMO_PHASE_VALIDATION_PASSED},
        monitor_result=_monitor(DECISION_STABLE),
        safe_context=_safe_context(),
    )
    assert result["live_candidate_status"] == LIVE_CANDIDATE_REJECTED
    assert "demo_validation_not_passed" in result["blocked_reasons"]


def test_blocked_degrading_performance():
    result = run_live_candidate_readiness_spine(
        demo_validation_result=_agg_result(),
        tracker_result={"demo_phase_status": DEMO_PHASE_VALIDATION_PASSED},
        monitor_result=_monitor(DECISION_DEGRADING),
        safe_context=_safe_context(),
    )
    assert result["live_candidate_status"] == LIVE_CANDIDATE_BLOCKED
    assert "performance_degrading" in result["blocked_reasons"]


def test_blocked_risk_violation():
    result = run_live_candidate_readiness_spine(
        demo_validation_result=_agg_result(),
        tracker_result={"demo_phase_status": DEMO_PHASE_VALIDATION_PASSED},
        monitor_result=_monitor(DECISION_RISK_VIOLATION, risk_status="RISK_VIOLATION"),
        safe_context=_safe_context(),
    )
    assert result["live_candidate_status"] == LIVE_CANDIDATE_BLOCKED
    assert "risk_violation_present" in result["blocked_reasons"]


def test_blocked_operator_review_not_approved():
    result = run_live_candidate_readiness_spine(
        demo_validation_result=_agg_result(),
        tracker_result={"demo_phase_status": DEMO_PHASE_VALIDATION_PASSED},
        monitor_result=_monitor(DECISION_IMPROVING),
        safe_context=_safe_context(),
        operator_packet=run_demo_phase_operator_review_packet(
            monitor_result=_monitor(DECISION_IMPROVING),
            safe_context=_safe_context(),
        ) | {"recommended_operator_decision": DECISION_REQUEST_MORE_EVIDENCE},
    )
    assert result["live_candidate_status"] == LIVE_CANDIDATE_BLOCKED
    assert "operator_review_not_approved" in result["blocked_reasons"]


def test_blocked_unsafe_evidence():
    result = run_live_candidate_readiness_spine(
        demo_validation_result=_agg_result(),
        tracker_result={"demo_phase_status": DEMO_PHASE_VALIDATION_PASSED, "blocked_reasons": ["unsafe_evidence:0:high_latency"]},
        monitor_result=_monitor(DECISION_STABLE),
        safe_context=_safe_context(),
    )
    assert result["live_candidate_status"] == LIVE_CANDIDATE_BLOCKED
    assert "unsafe_evidence" in result["blocked_reasons"]


def test_deterministic_output():
    payload = {
        "demo_validation_result": _agg_result(),
        "tracker_result": {"demo_phase_status": DEMO_PHASE_VALIDATION_PASSED},
        "monitor_result": _monitor(DECISION_STABLE),
        "safe_context": _safe_context(),
    }
    first = run_live_candidate_readiness_spine(**payload)
    second = run_live_candidate_readiness_spine(**payload)
    assert first == second


def test_safety_source_scan():
    source = inspect.getsource(__import__("automation.forex_engine.live_candidate_readiness_spine", fromlist=["*"]))
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
        "run_live_trading",
    )
    for token in forbidden:
        assert token not in source
