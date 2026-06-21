from __future__ import annotations

from pathlib import Path

from automation.forex_engine import strategy_campaign_supervisor as supervisor

CAMPAIGN_EVIDENCE_READY = "CAMPAIGN_EVIDENCE_READY"
CAMPAIGN_MORE_EVIDENCE_REQUIRED = "CAMPAIGN_MORE_EVIDENCE_REQUIRED"
CAMPAIGN_EVIDENCE_REJECTED = "CAMPAIGN_EVIDENCE_REJECTED"


def _evidence_ready() -> dict:
    return {
        "campaign_evidence_status": CAMPAIGN_EVIDENCE_READY,
        "campaign_trade_count": 32,
        "campaign_session_count": 4,
        "campaign_expectancy": 0.12,
        "campaign_profit_factor": 1.3,
        "campaign_max_drawdown": 4.5,
        "campaign_evidence_score": 0.89,
    }


def _evidence_more() -> dict:
    return {
        "campaign_evidence_status": CAMPAIGN_MORE_EVIDENCE_REQUIRED,
        "campaign_trade_count": 12,
        "campaign_session_count": 1,
        "campaign_expectancy": 0.2,
        "campaign_profit_factor": 1.4,
        "campaign_max_drawdown": 2.0,
    }


def _evidence_rejected() -> dict:
    return {
        "campaign_evidence_status": CAMPAIGN_EVIDENCE_REJECTED,
        "campaign_trade_count": 25,
        "campaign_session_count": 3,
        "campaign_expectancy": -0.1,
        "campaign_profit_factor": 0.8,
        "campaign_max_drawdown": 3.0,
    }


def _promotion_pass() -> dict:
    return {"status": "PASS", "passed": True}


def _promotion_fail() -> dict:
    return {"status": "REJECTED", "passed": False, "blocked_reasons": ["promotion_not_ready"]}


def _capital_pass() -> dict:
    return {"status": "PASS", "passed": True}


def _capital_fail() -> dict:
    return {"status": "FAIL", "passed": False, "blocked_reasons": ["capital_risk_limit"]}


def test_positive_demo_candidate_path() -> None:
    result = supervisor.evaluate_campaign_supervisor(
        campaign_evidence_result=_evidence_ready(),
        promotion_workflow_result=_promotion_pass(),
        capital_allocation_result=_capital_pass(),
    )
    assert result["campaign_status"] == supervisor.CAMPAIGN_DEMO_CANDIDATE
    assert result["campaign_demo_candidate"] is True
    assert result["campaign_completed"] is True
    assert result["campaign_next_safe_action"] == "build_demo_candidate_packet"


def test_continue_path() -> None:
    result = supervisor.evaluate_campaign_supervisor(
        campaign_evidence_result=_evidence_more(),
        promotion_workflow_result=_promotion_pass(),
        capital_allocation_result=_capital_pass(),
    )
    assert result["campaign_status"] == supervisor.CAMPAIGN_MORE_EVIDENCE_REQUIRED
    assert result["campaign_demo_candidate"] is False
    assert "campaign_evidence_not_ready" in result["campaign_blockers"]


def test_more_evidence_path() -> None:
    result = supervisor.evaluate_campaign_supervisor(
        campaign_evidence_result={},
        promotion_workflow_result=_promotion_pass(),
        capital_allocation_result=_capital_pass(),
    )
    assert result["campaign_status"] == supervisor.CAMPAIGN_MORE_EVIDENCE_REQUIRED
    assert "missing_campaign_evidence" in result["campaign_blockers"]


def test_blocked_path() -> None:
    result = supervisor.evaluate_campaign_supervisor(
        campaign_evidence_result=_evidence_ready(),
        promotion_workflow_result=_promotion_pass(),
        capital_allocation_result=_capital_fail(),
    )
    assert result["campaign_status"] == supervisor.CAMPAIGN_BLOCKED
    assert any("capital_allocation_gate_blocked" in item for item in result["campaign_blockers"])


def test_rejected_path() -> None:
    result = supervisor.evaluate_campaign_supervisor(
        campaign_evidence_result=_evidence_rejected(),
        promotion_workflow_result=_promotion_pass(),
        capital_allocation_result=_capital_pass(),
    )
    assert result["campaign_status"] == supervisor.CAMPAIGN_REJECTED
    assert "campaign_evidence_rejected" in result["campaign_blockers"]


def test_negative_expectancy_path() -> None:
    evidence = _evidence_ready()
    evidence["campaign_expectancy"] = -0.05
    result = supervisor.evaluate_campaign_supervisor(
        campaign_evidence_result=evidence,
        promotion_workflow_result=_promotion_pass(),
        capital_allocation_result=_capital_pass(),
    )
    assert result["campaign_status"] == supervisor.CAMPAIGN_REJECTED
    assert "negative_expectancy" in result["campaign_blockers"]


def test_capital_gate_failure_path() -> None:
    result = supervisor.evaluate_campaign_supervisor(
        campaign_evidence_result=_evidence_ready(),
        promotion_workflow_result=_promotion_pass(),
        capital_allocation_result={"blocked": True},
    )
    assert result["campaign_status"] == supervisor.CAMPAIGN_BLOCKED
    assert "capital_allocation_gate_blocked" in result["campaign_blockers"]


def test_promotion_workflow_failure_path() -> None:
    result = supervisor.evaluate_campaign_supervisor(
        campaign_evidence_result=_evidence_ready(),
        promotion_workflow_result=_promotion_fail(),
        capital_allocation_result=_capital_pass(),
    )
    assert result["campaign_status"] == supervisor.CAMPAIGN_REJECTED
    assert "promotion_workflow_rejected" in result["campaign_blockers"]


def test_deterministic_output_path() -> None:
    base = {
        "campaign_evidence_result": _evidence_ready(),
        "promotion_workflow_result": _promotion_pass(),
        "capital_allocation_result": _capital_pass(),
    }
    first = supervisor.evaluate_campaign_supervisor(**base)
    second = supervisor.evaluate_campaign_supervisor(**base)
    assert first == second


def test_safety_validation_path() -> None:
    result = supervisor.evaluate_campaign_supervisor(
        campaign_evidence_result=_evidence_ready(),
        promotion_workflow_result=_promotion_pass(),
        capital_allocation_result=_capital_pass(),
    )
    safety = result["safety"]
    assert safety == {
        "paper_only": True,
        "broker_connection_active": False,
        "network_access": False,
        "credentials_accessed": False,
        "order_execution_enabled": False,
        "demo_execution_active": False,
        "live_trading_authorized": False,
        "capital_allocated": False,
        "capital_allocation_modified": False,
        "operator_review_required": True,
    }


def test_source_scan_prohibits_network_filesystem_credentials_symbols() -> None:
    source = Path("automation/forex_engine/strategy_campaign_supervisor.py").read_text(encoding="utf-8").lower()
    banned = (
        "requests",
        "urllib",
        "socket",
        "subprocess",
        "os.environ",
        ".env",
        "http://",
        "https://",
    )
    for token in banned:
        assert token not in source
