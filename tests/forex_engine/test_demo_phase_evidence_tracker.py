"""Tests for demo phase evidence tracker."""
from __future__ import annotations

import inspect

from automation.forex_engine.demo_phase_evidence_tracker import (
    DEMO_PHASE_MORE_EVIDENCE_REQUIRED,
    DEMO_PHASE_NOT_STARTED,
    DEMO_PHASE_TRACKING,
    DEMO_PHASE_VALIDATION_FAILED,
    DEMO_PHASE_VALIDATION_PASSED,
    DECISION_DEMO_ADVANCEMENT_APPROVED,
    run_demo_phase_evidence_tracker,
)


def _event(i: int, **overrides: object):
    payload = {
        "timestamp": f"2026-06-21T10:00:{i:02d}Z",
        "strategy_name": "DAY_TRADING_BREAKOUT_V1",
        "strategy_version": "v1",
        "symbol": "EURUSD",
        "direction": "BUY",
        "realized_pl": 7.5,
        "risk_amount": 10.0,
        "max_drawdown": 1.1,
        "spread_cost": 0.15,
        "slippage": 0.4,
        "latency_ms": 120.0,
        "outcome": "WIN",
    }
    payload.update(overrides)
    return payload


def _advancement(approved: bool = True):
    return {
        "demo_advancement_approved": approved,
        "promotion_recommendation": DECISION_DEMO_ADVANCEMENT_APPROVED if approved else "DEMO_ADVANCEMENT_BLOCKED",
        "safety": {
            "paper_only": True,
            "broker_access": False,
            "credentials_access": False,
            "network_access": False,
            "live_trading_active": False,
            "demo_execution_active": False,
            "capital_allocation_modified": False,
        },
    }


def test_demo_phase_tracking_starts_after_approved_advancement():
    result = run_demo_phase_evidence_tracker(
        advancement_result=_advancement(True),
        evidence_events=[_event(1), _event(2), _event(3)],
    )
    assert result["tracking_completed"] is True
    assert result["demo_phase_active"] is True
    assert result["demo_phase_status"] in {DEMO_PHASE_TRACKING, DEMO_PHASE_VALIDATION_PASSED, DEMO_PHASE_VALIDATION_FAILED}


def test_blocked_without_advancement_approval():
    result = run_demo_phase_evidence_tracker(
        advancement_result=_advancement(False),
        evidence_events=[_event(1), _event(2)],
    )
    assert result["tracking_completed"] is False
    assert result["demo_phase_active"] is False
    assert result["demo_phase_status"] == DEMO_PHASE_NOT_STARTED
    assert "governed_advancement_not_approved" in result["blocked_reasons"]


def test_valid_evidence_events_counted():
    result = run_demo_phase_evidence_tracker(
        advancement_result=_advancement(True),
        evidence_events=[_event(1), _event(2), _event(3, outcome="LOSS")],
    )
    assert result["evidence_events_count"] == 3
    assert result["validated_events_count"] == 3
    assert result["invalid_events_count"] == 0
    assert result["current_demo_score"] != 0.0


def test_malformed_evidence_rejected():
    result = run_demo_phase_evidence_tracker(
        advancement_result=_advancement(True),
        evidence_events=[{"timestamp": "x", "bad": True}],
    )
    assert result["validated_events_count"] == 0
    assert result["invalid_events_count"] == 1
    assert result["demo_phase_status"] == DEMO_PHASE_MORE_EVIDENCE_REQUIRED
    assert any("malformed_evidence_event" in reason for reason in result["blocked_reasons"])


def test_unsafe_evidence_blocked():
    result = run_demo_phase_evidence_tracker(
        advancement_result=_advancement(True),
        evidence_events=[_event(1, latency_ms=-50.0)],
    )
    assert result["demo_phase_status"] == DEMO_PHASE_MORE_EVIDENCE_REQUIRED
    assert result["demo_phase_active"] is False
    assert any("unsafe_evidence" in reason or "malformed_evidence_event" in reason for reason in result["blocked_reasons"])


def test_validation_passed_with_sufficient_positive_evidence():
    events = [_event(i, realized_pl=20.0, outcome="WIN") for i in range(3)]
    result = run_demo_phase_evidence_tracker(
        advancement_result=_advancement(True),
        evidence_events=events,
    )
    assert result["demo_phase_status"] == DEMO_PHASE_VALIDATION_PASSED
    assert result["current_demo_score"] > 1.0


def test_validation_failed_with_negative_evidence():
    events = [_event(i, realized_pl=-20.0, outcome="LOSS") for i in range(3)]
    result = run_demo_phase_evidence_tracker(
        advancement_result=_advancement(True),
        evidence_events=events,
    )
    assert result["demo_phase_status"] == DEMO_PHASE_VALIDATION_FAILED
    assert result["current_demo_score"] < 1.0


def test_deterministic_output():
    payload = dict(
        advancement_result=_advancement(True),
        evidence_events=[_event(1), _event(2), _event(3)],
    )
    first = run_demo_phase_evidence_tracker(**payload)
    second = run_demo_phase_evidence_tracker(**payload)
    assert first == second


def test_safety_source_scan():
    source = inspect.getsource(__import__("automation.forex_engine.demo_phase_evidence_tracker", fromlist=["*"]))
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
