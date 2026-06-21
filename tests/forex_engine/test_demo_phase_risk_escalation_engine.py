"""Tests for demo phase risk escalation engine."""
from __future__ import annotations

import inspect

from automation.forex_engine.demo_phase_performance_monitor import (
    DECISION_DEGRADING,
    DECISION_IMPROVING,
    DECISION_INSUFFICIENT,
    DECISION_RISK_VIOLATION,
    DECISION_STABLE,
)
from automation.forex_engine.demo_phase_risk_escalation_engine import (
    ESCALATION_NO_ESCALATION,
    ESCALATION_RISK,
    ESCALATION_SUSPENSION,
    ESCALATION_WARNING,
    run_demo_phase_risk_escalation_engine,
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


def _monitor_result(state: str, risk_status: str = "RISK_OK", reasons: list[str] | None = None):
    return {
        "monitor_completed": state in {DECISION_IMPROVING, DECISION_STABLE, DECISION_DEGRADING},
        "performance_state": state,
        "risk_status": risk_status,
        "blocked_reasons": reasons or [],
        "expectancy_trend": "STABLE",
        "drawdown_trend": "STABLE",
        "consistency_trend": "STABLE",
        "next_safe_action": "monitor_continuously",
        "safety": _safe_payload(),
        "mode": "DEMO_PHASE_PERFORMANCE_MONITOR",
    }


def _event(index: int, realized_pl: float = 1.0, **overrides: object):
    payload = {
        "timestamp": f"2026-06-21T10:00:{index:02d}Z",
        "strategy_name": "DAY_TRADING_BREAKOUT_V1",
        "strategy_version": "v1",
        "symbol": "EURUSD",
        "direction": "BUY",
        "realized_pl": realized_pl,
        "risk_amount": 10.0,
        "max_drawdown": 1.6,
        "spread_cost": 0.15,
        "slippage": 0.4,
        "latency_ms": 100.0,
        "outcome": "WIN",
    }
    payload.update(overrides)
    return payload


def test_no_escalation_improving():
    result = run_demo_phase_risk_escalation_engine(
        monitor_result=_monitor_result(DECISION_IMPROVING),
        safe_context=_safe_payload(),
    )
    assert result["escalation_completed"] is True
    assert result["escalation_level"] == ESCALATION_NO_ESCALATION
    assert result["operator_review_required"] is False


def test_no_escalation_stable():
    result = run_demo_phase_risk_escalation_engine(
        monitor_result=_monitor_result(DECISION_STABLE),
        safe_context=_safe_payload(),
    )
    assert result["escalation_completed"] is True
    assert result["escalation_level"] == ESCALATION_NO_ESCALATION


def test_warning_degrading():
    result = run_demo_phase_risk_escalation_engine(
        monitor_result=_monitor_result(DECISION_DEGRADING),
        safe_context=_safe_payload(),
    )
    assert result["escalation_level"] == ESCALATION_WARNING
    assert result["performance_state"] == DECISION_DEGRADING
    assert result["operator_review_required"] is False


def test_risk_escalation():
    result = run_demo_phase_risk_escalation_engine(
        monitor_result=_monitor_result(DECISION_RISK_VIOLATION, risk_status="RISK_VIOLATION", reasons=["risk_threshold:0:excessive_drawdown:3.0"]),
        safe_context=_safe_payload(),
    )
    assert result["escalation_level"] == ESCALATION_RISK
    assert result["operator_review_required"] is True
    assert result["recommended_action"] != "continue_demo_phase"


def test_suspension_recommendation():
    result = run_demo_phase_risk_escalation_engine(
        monitor_result=_monitor_result(DECISION_RISK_VIOLATION, risk_status="RISK_VIOLATION", reasons=["risk_threshold:0:excessive_drawdown:3.0"]),
        repeated_risk_violation_count=2,
        safe_context=_safe_payload(),
    )
    assert result["escalation_level"] == ESCALATION_SUSPENSION
    assert result["recommended_action"] == "suspend_demo_phase_until_operator_review"


def test_unsafe_evidence_escalation():
    result = run_demo_phase_risk_escalation_engine(
        monitor_result=_monitor_result(
            DECISION_INSUFFICIENT,
            reasons=["unsafe_evidence:0:excessive_slippage"],
        ),
        safe_context=_safe_payload(),
    )
    assert result["escalation_level"] == ESCALATION_RISK
    assert result["operator_review_required"] is True


def test_missing_evidence_escalation():
    result = run_demo_phase_risk_escalation_engine(
        evidence_events=[],
        safe_context=_safe_payload(),
    )
    assert result["escalation_completed"] is False
    assert result["escalation_level"] in {ESCALATION_WARNING, ESCALATION_RISK}
    assert "insufficient_evidence" in result["blocked_reasons"]


def test_deterministic_output():
    payload = {"monitor_result": _monitor_result(DECISION_STABLE), "safe_context": _safe_payload()}
    first = run_demo_phase_risk_escalation_engine(**payload)
    second = run_demo_phase_risk_escalation_engine(**payload)
    assert first == second


def test_safety_source_scan():
    source = inspect.getsource(__import__("automation.forex_engine.demo_phase_risk_escalation_engine", fromlist=["*"]))
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
