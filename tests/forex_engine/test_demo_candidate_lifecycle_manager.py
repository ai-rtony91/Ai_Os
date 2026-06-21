from __future__ import annotations

from pathlib import Path

from automation.forex_engine.demo_candidate_lifecycle_manager import (
    CAMPAIGN_BLOCKED,
    CAMPAIGN_DEMO_CANDIDATE,
    CAMPAIGN_MORE_EVIDENCE_REQUIRED,
    CAMPAIGN_REJECTED,
    DEMO_CANDIDATE_ACTIVE,
    DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION,
    DEMO_CANDIDATE_CREATED,
    DEMO_CANDIDATE_PAUSED,
    DEMO_CANDIDATE_REVOKED,
    evaluate_demo_candidate_lifecycle,
)


def _campaign(
    status: str = CAMPAIGN_DEMO_CANDIDATE,
    trade_count: int = 30,
    session_count: int = 5,
    expectancy: float = 0.12,
    profit_factor: float = 1.25,
    drawdown: float = 3.0,
    evidence_score: float = 0.9,
):
    return {
        "campaign_status": status,
        "campaign_metrics": {
            "trade_count": trade_count,
            "session_count": session_count,
            "expectancy": expectancy,
            "profit_factor": profit_factor,
            "drawdown": drawdown,
            "evidence_score": evidence_score,
        },
        "campaign_next_safe_action": "collect_more_evidence",
    }


def _record(state: str) -> dict:
    return {"candidate_state": state}


def test_candidate_creation_path() -> None:
    result = evaluate_demo_candidate_lifecycle(_campaign(), {"strategy_id": "strat-1", "strategy_name": "mean_rev"})
    assert result["candidate_state"] == DEMO_CANDIDATE_CREATED
    assert result["candidate_created"] is True
    assert result["candidate_approved"] is False
    assert result["candidate_next_safe_action"] == "activate_candidate"
    assert result["candidate_history"]


def test_active_transition_path() -> None:
    first = evaluate_demo_candidate_lifecycle(_campaign(), {"strategy_id": "s"}, {})
    second = evaluate_demo_candidate_lifecycle(
        _campaign(),
        {"requested_transition": "ACTIVATE", "strategy_id": "s"},
        _record(first["candidate_state"]),
    )
    assert first["candidate_state"] == DEMO_CANDIDATE_CREATED
    assert second["candidate_state"] == DEMO_CANDIDATE_ACTIVE
    assert second["candidate_next_safe_action"] == "approve_or_pause_candidate"


def test_approval_transition_path() -> None:
    result = evaluate_demo_candidate_lifecycle(
        _campaign(),
        {"requested_transition": "APPROVE", "strategy_id": "s"},
        _record(DEMO_CANDIDATE_ACTIVE),
    )
    assert result["candidate_state"] == DEMO_CANDIDATE_APPROVED_FOR_DEMO_VALIDATION
    assert result["candidate_approved"] is True
    assert result["lifecycle_completed"] is True


def test_pause_transition_path() -> None:
    result = evaluate_demo_candidate_lifecycle(
        _campaign(),
        {"requested_transition": "PAUSE", "strategy_id": "s"},
        _record(DEMO_CANDIDATE_ACTIVE),
    )
    assert result["candidate_state"] == DEMO_CANDIDATE_PAUSED
    assert result["candidate_blockers"] == []
    assert result["candidate_next_safe_action"] == "investigate_and_resume_or_revoke"


def test_revoke_transition_path() -> None:
    result = evaluate_demo_candidate_lifecycle(
        _campaign(),
        {"requested_transition": "REVOKE", "strategy_id": "s"},
        _record(DEMO_CANDIDATE_ACTIVE),
    )
    assert result["candidate_state"] == DEMO_CANDIDATE_REVOKED
    assert "candidate_revoked" not in result["candidate_blockers"]
    assert result["candidate_next_safe_action"] == "investigate_reactivation_request_manually"


def test_invalid_transition_path() -> None:
    result = evaluate_demo_candidate_lifecycle(
        _campaign(),
        {"requested_transition": "APPROVE", "strategy_id": "s"},
        _record(DEMO_CANDIDATE_CREATED),
    )
    assert result["candidate_state"] == DEMO_CANDIDATE_CREATED
    assert "invalid_transition" in result["candidate_blockers"]


def test_missing_campaign_path() -> None:
    result = evaluate_demo_candidate_lifecycle(None, {"strategy_id": "s"})
    assert result["lifecycle_completed"] is False
    assert result["candidate_blockers"] == ["missing_campaign_result"]


def test_deterministic_output_path() -> None:
    payload = {
        "campaign_supervisor_result": _campaign(),
        "candidate_metadata": {"strategy_id": "s", "requested_transition": "", "strategy_name": "a"},
    }
    first = evaluate_demo_candidate_lifecycle(
        payload["campaign_supervisor_result"],
        payload["candidate_metadata"],
    )
    second = evaluate_demo_candidate_lifecycle(
        payload["campaign_supervisor_result"],
        payload["candidate_metadata"],
    )
    assert first == second

def test_history_generation_path() -> None:
    result = evaluate_demo_candidate_lifecycle(
        _campaign(),
        {"requested_transition": "ACTIVATE", "strategy_id": "s"},
        _record(DEMO_CANDIDATE_CREATED),
    )
    assert len(result["candidate_history"]) == 1
    transition = result["candidate_history"][0]
    assert transition["previous_state"] == DEMO_CANDIDATE_CREATED
    assert transition["new_state"] == DEMO_CANDIDATE_ACTIVE
    assert transition["campaign_status"] == CAMPAIGN_DEMO_CANDIDATE


def test_safety_validation_path() -> None:
    result = evaluate_demo_candidate_lifecycle(
        _campaign(),
        {"strategy_id": "s"},
    )
    assert result["safety"] == {
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


def test_source_scan_no_banned_tokens() -> None:
    source = Path("automation/forex_engine/demo_candidate_lifecycle_manager.py").read_text(encoding="utf-8").lower()
    banned = ("requests", "urllib", "socket", "subprocess", "os.environ", ".env", "http://", "https://")
    for token in banned:
        assert token not in source
