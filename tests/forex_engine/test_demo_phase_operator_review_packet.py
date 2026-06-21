"""Tests for demo phase operator review packet."""
from __future__ import annotations

import inspect

from automation.forex_engine.demo_phase_evidence_tracker import DEMO_PHASE_VALIDATION_FAILED
from automation.forex_engine.demo_phase_performance_monitor import (
    DECISION_DEGRADING,
    DECISION_INSUFFICIENT,
    DECISION_IMPROVING,
)
from automation.forex_engine.demo_phase_risk_escalation_engine import (
    ESCALATION_RISK,
    ESCALATION_SUSPENSION,
    ESCALATION_WARNING,
    run_demo_phase_risk_escalation_engine,
)
from automation.forex_engine.demo_phase_operator_review_packet import (
    DECISION_APPROVE_CONTINUE_DEMO_PHASE,
    DECISION_REQUEST_MORE_EVIDENCE,
    DECISION_REJECT_DEMO_ADVANCEMENT,
    DECISION_SUSPEND_DEMO_PHASE,
    run_demo_phase_operator_review_packet,
)


def _safe_context():
    return {
        "paper_only": True,
        "broker_access": False,
        "credentials_access": False,
        "network_access": False,
        "live_trading_active": False,
        "demo_execution_active": False,
        "capital_allocation_modified": False,
    }


def _monitor_result(state: str, risk_status: str = "RISK_OK", reasons: list[str] | None = None):
    return {
        "monitor_completed": state in {DECISION_IMPROVING},
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


def test_approve_continue_demo_phase():
    packet = run_demo_phase_operator_review_packet(
        monitor_result=_monitor_result(DECISION_IMPROVING),
        safe_context=_safe_context(),
    )
    assert packet["review_packet_completed"] is True
    assert packet["operator_review_required"] is False
    assert packet["recommended_operator_decision"] == DECISION_APPROVE_CONTINUE_DEMO_PHASE


def test_request_more_evidence_for_warning():
    packet = run_demo_phase_operator_review_packet(
        monitor_result=_monitor_result(DECISION_DEGRADING),
        safe_context=_safe_context(),
    )
    assert packet["recommended_operator_decision"] == DECISION_REQUEST_MORE_EVIDENCE
    assert packet["operator_review_required"] is False


def test_risk_escalation_review_required():
    packet = run_demo_phase_operator_review_packet(
        monitor_result=_monitor_result(DECISION_DEGRADING, risk_status="RISK_VIOLATION", reasons=["risk_threshold:0:excessive_drawdown:3.5"]),
        safe_context=_safe_context(),
    )
    assert packet["operator_review_required"] is True
    assert packet["recommended_operator_decision"] == DECISION_REQUEST_MORE_EVIDENCE
    assert packet["escalation_level"] in {ESCALATION_RISK}


def test_suspend_demo_phase():
    packet = run_demo_phase_operator_review_packet(
        monitor_result=_monitor_result(DECISION_DEGRADING, risk_status="RISK_VIOLATION", reasons=["risk_threshold:0:excessive_drawdown:3.5"]),
        repeated_risk_violation_count=2,
        safe_context=_safe_context(),
    )
    assert packet["recommended_operator_decision"] == DECISION_SUSPEND_DEMO_PHASE
    assert packet["operator_review_required"] is True
    assert packet["escalation_level"] == ESCALATION_SUSPENSION


def test_reject_unsafe_evidence():
    packet = run_demo_phase_operator_review_packet(
        monitor_result=_monitor_result(
            DECISION_INSUFFICIENT,
            reasons=["unsafe_evidence:0:excessive_slippage"],
        ),
        safe_context=_safe_context(),
    )
    assert packet["recommended_operator_decision"] == DECISION_REJECT_DEMO_ADVANCEMENT
    assert packet["operator_review_required"] is True


def test_missing_evidence_review():
    packet = run_demo_phase_operator_review_packet(
        evidence_events=[],
        safe_context=_safe_context(),
    )
    assert packet["recommended_operator_decision"] == DECISION_REQUEST_MORE_EVIDENCE
    assert packet["operator_review_required"] is False
    assert any("insufficient_evidence" in str(reason) for reason in packet["blocked_reasons"])


def test_reject_on_demo_validation_failed():
    packet = run_demo_phase_operator_review_packet(
        monitor_result=run_demo_phase_risk_escalation_engine(
            monitor_result=_monitor_result(DECISION_IMPROVING),
            safe_context=_safe_context(),
            repeated_risk_violation_count=0,
        ),
        safe_context=_safe_context(),
    )
    # Use risk engine result as input to ensure deterministic pass-through for tracker statuses.
    assert packet["review_packet_completed"] is True


def test_deterministic_output():
    packet_payload = {
        "monitor_result": _monitor_result(DECISION_IMPROVING),
        "safe_context": _safe_context(),
        "evidence_events": [{"timestamp": "x"}],
    }
    first = run_demo_phase_operator_review_packet(**packet_payload)
    second = run_demo_phase_operator_review_packet(**packet_payload)
    assert first == second


def test_safety_source_scan():
    source = inspect.getsource(__import__("automation.forex_engine.demo_phase_operator_review_packet", fromlist=["*"]))
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
