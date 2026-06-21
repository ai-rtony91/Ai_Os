from __future__ import annotations

from pathlib import Path

from automation.forex_engine import demo_validation_supervisor as supervisor


def _candidate(state: str, approved: bool = True, candidate_id: str = "cand-001", campaign_status: str = "CAMPAIGN_DEMO_CANDIDATE") -> dict:
    return {
        "candidate_id": candidate_id,
        "candidate_state": state,
        "candidate_approved": approved,
        "campaign_status": campaign_status,
    }


def _result(
    sessions: int = 3,
    trade_count: int = 20,
    win_count: int = 12,
    loss_count: int = 8,
    realized_pl: float = 3.5,
    expectancy: float = 0.08,
    profit_factor: float = 1.25,
    drawdown: float = 2.0,
    evidence_score: float = 0.8,
    risk_failed: bool = False,
) -> dict:
    return {
        "trade_count": trade_count,
        "session_count": sessions,
        "win_count": win_count,
        "loss_count": loss_count,
        "realized_pl": realized_pl,
        "expectancy": expectancy,
        "profit_factor": profit_factor,
        "max_drawdown": drawdown,
        "evidence_score": evidence_score,
        "risk_failed": risk_failed,
    }


def test_live_readiness_candidate_path() -> None:
    result = supervisor.evaluate_demo_validation_supervisor(
        _candidate(supervisor.DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION, approved=True),
        [_result()],
    )
    assert result["demo_validation_status"] == supervisor.DEMO_VALIDATION_LIVE_READINESS_CANDIDATE
    assert result["live_readiness_candidate"] is True
    assert result["demo_validation_completed"] is True
    assert result["demo_candidate_id"] == "cand-001"


def test_continue_path() -> None:
    result = supervisor.evaluate_demo_validation_supervisor(
        _candidate(supervisor.DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION, approved=True),
        [_result(expectancy=0.001, profit_factor=1.5, drawdown=2.0, evidence_score=0.8)],
    )
    assert result["demo_validation_status"] == supervisor.DEMO_VALIDATION_CONTINUE
    assert result["live_readiness_candidate"] is False


def test_more_evidence_path() -> None:
    result = supervisor.evaluate_demo_validation_supervisor(
        _candidate(supervisor.DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION, approved=True),
        [],
    )
    assert result["demo_validation_status"] == supervisor.DEMO_VALIDATION_MORE_EVIDENCE_REQUIRED
    assert result["demo_validation_next_safe_action"] == "collect_first_validation_batch"


def test_blocked_candidate_missing_path() -> None:
    result = supervisor.evaluate_demo_validation_supervisor(None, [_result()])
    assert result["demo_validation_status"] == supervisor.DEMO_VALIDATION_BLOCKED
    assert result["demo_validation_next_safe_action"] == "provide_demo_candidate_record"


def test_blocked_paused_candidate_path() -> None:
    result = supervisor.evaluate_demo_validation_supervisor(
        _candidate(supervisor.DEMO_CANDIDATE_PAUSED, approved=True),
        [_result()],
    )
    assert result["demo_validation_status"] == supervisor.DEMO_VALIDATION_BLOCKED
    assert "candidate_state_blocked:DEMO_CANDIDATE_PAUSED" in result["demo_validation_blockers"]


def test_blocked_revoked_candidate_path() -> None:
    result = supervisor.evaluate_demo_validation_supervisor(
        _candidate(supervisor.DEMO_CANDIDATE_REVOKED, approved=True),
        [_result()],
    )
    assert result["demo_validation_status"] == supervisor.DEMO_VALIDATION_BLOCKED
    assert "candidate_state_blocked:DEMO_CANDIDATE_REVOKED" in result["demo_validation_blockers"]


def test_candidate_not_approved_path() -> None:
    result = supervisor.evaluate_demo_validation_supervisor(
        _candidate(supervisor.DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION, approved=False),
        [_result()],
    )
    assert result["demo_validation_status"] == supervisor.DEMO_VALIDATION_BLOCKED
    assert "candidate_not_approved_for_demo_validation" in result["demo_validation_blockers"]


def test_negative_expectancy_rejection_path() -> None:
    result = supervisor.evaluate_demo_validation_supervisor(
        _candidate(supervisor.DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION),
        [_result(expectancy=-0.2)],
    )
    assert result["demo_validation_status"] == supervisor.DEMO_VALIDATION_REJECTED
    assert "negative_expectancy" in result["demo_validation_blockers"]


def test_low_profit_factor_rejection_path() -> None:
    result = supervisor.evaluate_demo_validation_supervisor(
        _candidate(supervisor.DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION),
        [_result(profit_factor=0.7)],
    )
    assert result["demo_validation_status"] == supervisor.DEMO_VALIDATION_REJECTED
    assert "profit_factor_below_threshold" in result["demo_validation_blockers"]


def test_excessive_drawdown_rejection_path() -> None:
    result = supervisor.evaluate_demo_validation_supervisor(
        _candidate(supervisor.DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION),
        [_result(drawdown=20.0)],
    )
    assert result["demo_validation_status"] == supervisor.DEMO_VALIDATION_REJECTED
    assert "drawdown_above_threshold" in result["demo_validation_blockers"]


def test_risk_failure_rejection_path() -> None:
    result = supervisor.evaluate_demo_validation_supervisor(
        _candidate(supervisor.DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION),
        [_result(risk_failed=True)],
    )
    assert result["demo_validation_status"] == supervisor.DEMO_VALIDATION_REJECTED
    assert "risk_failures_present" in result["demo_validation_blockers"]


def test_low_evidence_score_rejection_path() -> None:
    result = supervisor.evaluate_demo_validation_supervisor(
        _candidate(supervisor.DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION),
        [_result(evidence_score=0.1)],
    )
    assert result["demo_validation_status"] == supervisor.DEMO_VALIDATION_REJECTED
    assert "evidence_score_below_threshold" in result["demo_validation_blockers"]


def test_deterministic_output_path() -> None:
    base = {
        "demo_candidate_record": _candidate(supervisor.DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION),
        "demo_validation_results": [_result()],
    }
    first = supervisor.evaluate_demo_validation_supervisor(**base)
    second = supervisor.evaluate_demo_validation_supervisor(**base)
    assert first == second


def test_safety_validation_path() -> None:
    result = supervisor.evaluate_demo_validation_supervisor(
        _candidate(supervisor.DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION),
        [_result()],
    )
    assert result["safety"] == {
        "paper_only": False,
        "demo_validation_only": True,
        "broker_connection_active": False,
        "network_access": False,
        "credentials_accessed": False,
        "order_execution_enabled": False,
        "demo_order_submission_enabled": False,
        "demo_execution_active": False,
        "live_trading_authorized": False,
        "capital_allocated": False,
        "capital_allocation_modified": False,
        "operator_review_required": True,
    }


def test_source_scan_no_banned_tokens() -> None:
    source = Path("automation/forex_engine/demo_validation_supervisor.py").read_text(encoding="utf-8").lower()
    banned = ("requests", "urllib", "socket", "subprocess", "os.environ", ".env", "http://", "https://")
    for token in banned:
        assert token not in source
