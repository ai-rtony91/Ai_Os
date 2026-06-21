"""Tests for demo phase performance monitor."""
from __future__ import annotations

import inspect

from automation.forex_engine.demo_phase_performance_monitor import (
    DECISION_DEGRADING,
    DECISION_IMPROVING,
    DECISION_INSUFFICIENT,
    DECISION_RISK_VIOLATION,
    DECISION_STABLE,
    run_demo_phase_performance_monitor,
)


def _event(index: int, **overrides: object) -> dict[str, object]:
    payload = {
        "timestamp": f"2026-06-21T10:00:{index:02d}Z",
        "strategy_name": "DAY_TRADING_BREAKOUT_V1",
        "strategy_version": "v1",
        "symbol": "EURUSD",
        "direction": "BUY",
        "realized_pl": 0.0,
        "risk_amount": 10.0,
        "max_drawdown": 1.2,
        "spread_cost": 0.15,
        "slippage": 0.4,
        "latency_ms": 100.0,
        "outcome": "WIN",
    }
    payload.update(overrides)
    return payload


def _safe_payload() -> dict[str, object]:
    return {
        "paper_only": True,
        "broker_access": False,
        "credentials_access": False,
        "network_access": False,
        "live_trading_active": False,
        "demo_execution_active": False,
        "capital_allocation_modified": False,
    }


def _monitor_result(**overrides: object):
    base = {
        "evidence_events": [
            _event(1, realized_pl=0.4, outcome="WIN", max_drawdown=1.6),
            _event(2, realized_pl=0.4, outcome="WIN", max_drawdown=1.6),
            _event(3, realized_pl=0.5, outcome="WIN", max_drawdown=1.6),
            _event(4, realized_pl=0.5, outcome="WIN", max_drawdown=1.6),
            _event(5, realized_pl=0.5, outcome="WIN", max_drawdown=1.6),
            _event(6, realized_pl=0.5, outcome="WIN", max_drawdown=1.6),
        ],
        "safe_context": _safe_payload(),
    }
    base.update(overrides)
    return run_demo_phase_performance_monitor(**base)


def test_improving_performance():
    result = run_demo_phase_performance_monitor(
        safe_context=_safe_payload(),
        evidence_events=[
            _event(1, realized_pl=-2.0, outcome="WIN", max_drawdown=1.9),
            _event(2, realized_pl=-1.5, outcome="WIN", max_drawdown=1.8),
            _event(3, realized_pl=-1.0, outcome="WIN", max_drawdown=1.7),
            _event(4, realized_pl=1.0, outcome="WIN", max_drawdown=1.6),
            _event(5, realized_pl=1.8, outcome="WIN", max_drawdown=1.5),
            _event(6, realized_pl=2.2, outcome="WIN", max_drawdown=1.4),
        ],
    )
    assert result["monitor_completed"] is True
    assert result["performance_state"] == DECISION_IMPROVING
    assert result["expectancy_trend"] == "IMPROVING"
    assert result["drawdown_trend"] in {"IMPROVING", "STABLE"}
    assert result["risk_status"] == "RISK_OK"


def test_stable_performance():
    result = _monitor_result()
    assert result["monitor_completed"] is True
    assert result["performance_state"] == DECISION_STABLE
    assert result["expectancy_trend"] == "STABLE"


def test_degrading_performance():
    result = run_demo_phase_performance_monitor(
        safe_context=_safe_payload(),
        evidence_events=[
            _event(1, realized_pl=1.8, outcome="WIN", max_drawdown=1.2),
            _event(2, realized_pl=1.4, outcome="WIN", max_drawdown=1.1),
            _event(3, realized_pl=1.2, outcome="WIN", max_drawdown=1.0),
            _event(4, realized_pl=-1.5, outcome="LOSS", max_drawdown=1.9),
            _event(5, realized_pl=-2.2, outcome="LOSS", max_drawdown=2.1),
            _event(6, realized_pl=-2.5, outcome="LOSS", max_drawdown=2.4),
        ],
    )
    assert result["monitor_completed"] is True
    assert result["performance_state"] == DECISION_DEGRADING
    assert result["expectancy_trend"] == DECISION_DEGRADING


def test_risk_violation():
    result = run_demo_phase_performance_monitor(
        safe_context=_safe_payload(),
        evidence_events=[
            _event(1, realized_pl=1.0, outcome="WIN", max_drawdown=3.5),
            _event(2, realized_pl=1.2, outcome="WIN", max_drawdown=3.2),
            _event(3, realized_pl=1.1, outcome="WIN", max_drawdown=3.8),
            _event(4, realized_pl=0.9, outcome="WIN", max_drawdown=3.6),
            _event(5, realized_pl=1.3, outcome="WIN", max_drawdown=3.9),
            _event(6, realized_pl=1.1, outcome="WIN", max_drawdown=3.7),
        ],
    )
    assert result["monitor_completed"] is False
    assert result["performance_state"] == DECISION_RISK_VIOLATION
    assert result["risk_status"] == "RISK_VIOLATION"


def test_insufficient_evidence():
    result = run_demo_phase_performance_monitor(
        safe_context=_safe_payload(),
        evidence_events=[_event(1, realized_pl=0.5), _event(2, realized_pl=1.0)],
    )
    assert result["monitor_completed"] is False
    assert result["performance_state"] == DECISION_INSUFFICIENT
    assert "insufficient_evidence" in result["blocked_reasons"]


def test_deterministic_output():
    payload = {
        "safe_context": _safe_payload(),
        "evidence_events": [
            _event(1, realized_pl=0.5),
            _event(2, realized_pl=0.8),
            _event(3, realized_pl=1.0),
            _event(4, realized_pl=1.2),
            _event(5, realized_pl=1.3),
            _event(6, realized_pl=1.4),
        ],
    }
    first = run_demo_phase_performance_monitor(**payload)
    second = run_demo_phase_performance_monitor(**payload)
    assert first == second


def test_safety_source_scan():
    source = inspect.getsource(__import__("automation.forex_engine.demo_phase_performance_monitor", fromlist=["*"]))
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
