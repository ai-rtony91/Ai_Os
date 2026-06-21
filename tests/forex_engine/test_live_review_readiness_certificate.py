from __future__ import annotations

from automation.forex_engine.live_review_readiness_certificate import (
    LIVE_REVIEW_CERTIFICATE_BLOCKED,
    LIVE_REVIEW_CERTIFICATE_INCOMPLETE,
    LIVE_REVIEW_CERTIFICATE_REJECTED,
    LIVE_REVIEW_CERTIFICATE_REVIEW_READY,
    generate_live_review_readiness_certificate,
)


def _base_state() -> dict:
    return {
        "demo_validation_contract": {
            "demo_validation_contract_status": "DEMO_CONTRACT_COMPLETE",
            "demo_validation_contract_completed": True,
            "live_readiness_candidate": True,
            "blockers": [],
            "safety": {},
        },
        "one_shot_exception_package": {
            "exception_package_status": "ONE_SHOT_EXCEPTION_REVIEW_READY",
            "exception_package_completed": True,
            "live_micro_trade_review_ready": True,
            "blockers": [],
            "safety": {"no_retry_loop": True, "no_autonomous_reentry": True, "manual_arming_required": True, "final_disarm_required": True},
        },
        "live_readiness_candidate": True,
        "approval_trace": {"approval_window_active": True, "approval_window_status": "ACTIVE"},
        "risk_limits": {
            "maximum_loss": 120.0,
            "daily_loss_cap": 30.0,
            "stop_loss": 2.0,
            "order_type": "market",
            "units_or_notional_limit": 0.1,
        },
        "kill_switch_proof": {"present": True},
        "rollback_proof": {"present": True},
        "reconciliation_proof": {"present": True},
        "evidence_freshness": {"fresh": True},
        "replayability_proof": {"present": True},
        "final_disarm_proof": {"present": True},
        "post_trade_journal_path": "/tmp/journal.ndjson",
        "operator_review_required": True,
        "one_shot_controls": {
            "no_retry_loop": True,
            "no_autonomous_reentry": True,
            "manual_arming_required": True,
            "final_disarm_required": True,
        },
    }


def _run(state: dict | None = None, *, exact_state: bool = True) -> dict:
    base = _base_state()
    if state is None:
        return generate_live_review_readiness_certificate(base)
    if exact_state:
        return generate_live_review_readiness_certificate(state)
    merged = base.copy()
    merged.update(state)
    return generate_live_review_readiness_certificate(merged)


def test_empty_state_blocks() -> None:
    result = generate_live_review_readiness_certificate({})
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_BLOCKED
    assert "missing_demo_validation_contract" in result["blockers"]


def test_complete_state_returns_review_ready() -> None:
    result = _run()
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_REVIEW_READY
    assert result["human_live_review_ready"] is True
    assert result["live_micro_trade_review_ready"] is True
    assert result["certificate_completed"] is True


def test_missing_demo_contract_blocks() -> None:
    state = _base_state()
    state.pop("demo_validation_contract")
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_BLOCKED
    assert "missing_demo_validation_contract" in result["blockers"]


def test_incomplete_demo_contract_blocks() -> None:
    state = _base_state()
    state["demo_validation_contract"]["demo_validation_contract_status"] = "DEMO_CONTRACT_CONTINUE"
    state["demo_validation_contract"]["demo_validation_contract_completed"] = False
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_INCOMPLETE
    assert "demo_validation_contract_not_complete" in result["blockers"]


def test_rejected_demo_profitability_state_returns_rejected() -> None:
    state = _base_state()
    state["demo_validation_contract"]["demo_validation_contract_status"] = "DEMO_CONTRACT_REJECTED"
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_REJECTED
    assert "demo_or_profitability_rejected" in result["blockers"]


def test_missing_one_shot_package_blocks() -> None:
    state = _base_state()
    state.pop("one_shot_exception_package")
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_INCOMPLETE
    assert "missing_one_shot_exception_package" in result["blockers"]


def test_incomplete_one_shot_package_blocks() -> None:
    state = _base_state()
    state["one_shot_exception_package"]["exception_package_status"] = "ONE_SHOT_EXCEPTION_INCOMPLETE"
    state["one_shot_exception_package"]["exception_package_completed"] = False
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_INCOMPLETE
    assert "one_shot_exception_package_not_review_ready" in result["blockers"]


def test_missing_live_readiness_candidate_blocks() -> None:
    state = _base_state()
    state.pop("live_readiness_candidate")
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_INCOMPLETE
    assert "missing_live_readiness_candidate" in result["blockers"]


def test_missing_approval_trace_blocks() -> None:
    state = _base_state()
    state.pop("approval_trace")
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_INCOMPLETE
    assert "missing_approval_trace" in result["blockers"]


def test_missing_risk_limits_blocks() -> None:
    state = _base_state()
    state.pop("risk_limits")
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_INCOMPLETE
    assert "missing_risk_limits" in result["blockers"]


def test_missing_kill_switch_blocks() -> None:
    state = _base_state()
    state.pop("kill_switch_proof")
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_INCOMPLETE
    assert "missing_kill_switch_proof" in result["blockers"]


def test_missing_rollback_blocks() -> None:
    state = _base_state()
    state.pop("rollback_proof")
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_INCOMPLETE
    assert "missing_rollback_proof" in result["blockers"]


def test_missing_reconciliation_blocks() -> None:
    state = _base_state()
    state.pop("reconciliation_proof")
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_INCOMPLETE
    assert "missing_reconciliation_proof" in result["blockers"]


def test_missing_evidence_freshness_blocks() -> None:
    state = _base_state()
    state.pop("evidence_freshness")
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_INCOMPLETE
    assert "missing_evidence_freshness" in result["blockers"]


def test_stale_evidence_blocks() -> None:
    state = _base_state()
    state["evidence_freshness"] = {"fresh": False, "evidence_age_minutes": 120}
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_INCOMPLETE
    assert "missing_evidence_freshness" in result["blockers"]


def test_missing_replayability_proof_blocks() -> None:
    state = _base_state()
    state.pop("replayability_proof")
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_INCOMPLETE
    assert "missing_replayability_proof" in result["blockers"]


def test_missing_final_disarm_proof_blocks() -> None:
    state = _base_state()
    state.pop("final_disarm_proof")
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_INCOMPLETE
    assert "missing_final_disarm_proof" in result["blockers"]


def test_missing_post_trade_journal_path_blocks() -> None:
    state = _base_state()
    state.pop("post_trade_journal_path")
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_INCOMPLETE
    assert "missing_post_trade_journal_path" in result["blockers"]


def test_missing_operator_review_requirement_blocks() -> None:
    state = _base_state()
    state["operator_review_required"] = False
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_INCOMPLETE
    assert "missing_operator_review_requirement" in result["blockers"]


def test_live_trading_authorization_flag_blocks() -> None:
    result = _run({"unsafe_live_trading_detected": True})
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_BLOCKED
    assert "live_trading_authorization_detected" in result["blockers"]

    state = _base_state()
    state["live_trading_authorized"] = True
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_BLOCKED
    assert "live_trading_authorization_detected" in result["blockers"]


def test_order_execution_enabled_flag_blocks() -> None:
    result = _run({"unsafe_order_execution_detected": True})
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_BLOCKED
    assert "order_execution_enabled_detected" in result["blockers"]


def test_broker_connection_flag_blocks() -> None:
    result = _run({"unsafe_broker_connection_detected": True})
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_BLOCKED
    assert "broker_connection_detected" in result["blockers"]


def test_credential_access_flag_blocks() -> None:
    result = _run({"unsafe_credential_access_detected": True})
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_BLOCKED
    assert "credential_access_detected" in result["blockers"]


def test_account_identifier_access_flag_blocks() -> None:
    result = _run({"unsafe_account_identifier_access_detected": True})
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_BLOCKED
    assert "account_identifier_access_detected" in result["blockers"]


def test_network_access_flag_blocks() -> None:
    result = _run({"unsafe_network_access_detected": True})
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_BLOCKED
    assert "network_access_detected" in result["blockers"]


def test_capital_allocation_flag_blocks() -> None:
    result = _run({"unsafe_capital_allocation_detected": True})
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_BLOCKED
    assert "capital_allocation_detected" in result["blockers"]


def test_alias_demo_contract_inputs_work() -> None:
    state = _base_state()
    state["demo_contract"] = state.pop("demo_validation_contract")
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_REVIEW_READY


def test_alias_one_shot_inputs_work() -> None:
    state = _base_state()
    state["exception_package"] = state.pop("one_shot_exception_package")
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_REVIEW_READY


def test_alias_proof_inputs_work() -> None:
    state = _base_state()
    state["kill_switch"] = state.pop("kill_switch_proof")
    state["rollback"] = state.pop("rollback_proof")
    state["reconciliation"] = state.pop("reconciliation_proof")
    state["replay"] = state.pop("replayability_proof")
    state["final_disarm"] = state.pop("final_disarm_proof")
    state["evidence_fresh"] = state.pop("evidence_freshness")
    state["journal_path"] = state.pop("post_trade_journal_path")
    state["risk"] = state.pop("risk_limits")
    state["approval"] = state.pop("approval_trace")
    result = _run(state)
    assert result["certificate_status"] == LIVE_REVIEW_CERTIFICATE_REVIEW_READY


def test_next_safe_action_deterministic() -> None:
    incomplete = _run({"risk_limits": {"present": False}}, exact_state=False)
    assert incomplete["next_safe_action"] == "collect_and_refresh_missing_evidence"
    assert incomplete["required_next_packets"] == ["collect_missing_evidence", "refresh_risk_controls", "repair_live_readiness_inputs"]

    blocked = _run({"unsafe_network_access_detected": True}, exact_state=True)
    assert blocked["next_safe_action"] == "resolve_unsafe_or_authorization_blockers"


def test_required_next_packets_ranked_by_completion_leverage() -> None:
    ready = _run()
    assert ready["required_next_packets"] == ["prepare_live_review_bundle", "request_human_live_review", "final_readiness_acknowledgment"]
    blocked = _run({"unsafe_broker_connection_detected": True}, exact_state=True)
    assert blocked["required_next_packets"] == ["clear_unsafe_runtime_flags", "restore_safety_invariants", "resolve_control_gaps"]


def test_certificate_never_authorizes_live_trading() -> None:
    result = _run()
    assert result["live_trading_authorized"] is False
    assert result["safety"]["live_trading_authorized"] is False


def test_certificate_never_grants_execution_authority() -> None:
    result = _run()
    assert result["safety"]["execution_authority_granted"] is False


def test_certificate_review_certificate_only() -> None:
    result = _run()
    assert result["safety"]["review_certificate_only"] is True


def test_safety_propagates_one_shot_controls() -> None:
    result = _run()
    assert result["safety"]["one_shot_only"] is True
    assert result["safety"]["manual_arming_required"] is True
    assert result["safety"]["final_disarm_required"] is True
