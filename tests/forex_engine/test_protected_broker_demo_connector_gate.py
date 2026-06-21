from __future__ import annotations

from copy import deepcopy

from automation.forex_engine.protected_broker_demo_connector_gate import (
    BROKER_DEMO_RUNTIME_REVIEW_READY,
    BROKER_DEMO_RUNTIME_REVIEW_REJECTED,
    CONNECTOR_CONTRACT_REJECTED,
    CONNECTOR_CONTRACT_REVIEW_READY,
    LIVE_REVIEW_CERTIFICATE_REVIEW_READY,
    LIVE_REVIEW_CERTIFICATE_REJECTED,
    ONE_SHOT_EXCEPTION_REVIEW_READY,
    ONE_SHOT_EXCEPTION_REJECTED,
    PROTECTED_CONNECTOR_GATE_BLOCKED,
    PROTECTED_CONNECTOR_GATE_EXPIRED,
    PROTECTED_CONNECTOR_GATE_INCOMPLETE,
    PROTECTED_CONNECTOR_GATE_REJECTED,
    PROTECTED_CONNECTOR_GATE_REVIEW_READY,
    PROTECTED_CONNECTOR_GATE_REVOKED,
    RUNTIME_CONNECTOR_REVIEW_READY,
    RUNTIME_CONNECTOR_REJECTED,
    REVIEW_CHAIN_REVIEW_READY,
    REVIEW_CHAIN_REJECTED,
    evaluate_protected_broker_demo_connector_gate,
)


def _base_state() -> dict:
    return {
        "broker_demo_runtime_review": {"broker_demo_runtime_review_status": BROKER_DEMO_RUNTIME_REVIEW_READY},
        "runtime_connector": {"runtime_connector_status": RUNTIME_CONNECTOR_REVIEW_READY},
        "connector_contract": {"connector_contract_status": CONNECTOR_CONTRACT_REVIEW_READY},
        "review_chain_status": REVIEW_CHAIN_REVIEW_READY,
        "certificate_status": LIVE_REVIEW_CERTIFICATE_REVIEW_READY,
        "one_shot_status": ONE_SHOT_EXCEPTION_REVIEW_READY,
        "protected_connector_approval": True,
        "approval_window_active": True,
        "approval_trace": {"present": True},
        "replay_proof": {"present": True},
        "reconciliation_proof": {"present": True},
        "kill_switch_proof": {"present": True},
        "rollback_proof": {"present": True},
        "freshness_proof": {"fresh": True},
        "final_disarm_proof": {"present": True},
        "one_shot_controls": {
            "operator_review_required": True,
            "manual_arming_required": True,
            "no_retry_loop": True,
            "no_autonomous_reentry": True,
        },
        "post_trade_journal_path": "/tmp/journal",
        "operator_review_required": True,
        "manual_arming_required": True,
        "timeout_required": True,
        "revocation_path": "/tmp/revoke",
        "replay_prevention": "/tmp/replay",
        "rollback_path": "/tmp/rollback",
        "connector_scope": "forex_demo",
    }


def _run(state_overrides: dict | None = None, *, exact_state: bool = False) -> dict:
    if exact_state:
        assert state_overrides is not None
        return evaluate_protected_broker_demo_connector_gate(state_overrides)
    state = _base_state()
    if state_overrides:
        merged = deepcopy(state)
        for key, value in state_overrides.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                nested = deepcopy(merged[key])
                nested.update(value)
                merged[key] = nested
            else:
                merged[key] = value
        return evaluate_protected_broker_demo_connector_gate(merged)
    return evaluate_protected_broker_demo_connector_gate(state)


def test_empty_state_blocks() -> None:
    result = evaluate_protected_broker_demo_connector_gate({})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_broker_demo_runtime_review" in result["protected_connector_gate_blockers"]


def test_complete_proof_state_returns_review_ready() -> None:
    result = _run()
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_REVIEW_READY
    assert result["protected_connector_gate_review_ready"] is True
    assert result["protected_connector_gate_blockers"] == []


def test_missing_broker_demo_runtime_review_blocks() -> None:
    result = _run({"broker_demo_runtime_review": None}, exact_state=True)
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_broker_demo_runtime_review" in result["protected_connector_gate_blockers"]


def test_broker_demo_runtime_review_incomplete_blocks() -> None:
    result = _run({"broker_demo_runtime_review_status": "BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE"}, exact_state=True)
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "broker_demo_runtime_review_not_ready" in result["protected_connector_gate_blockers"]


def test_broker_demo_runtime_review_rejected_returns_rejected() -> None:
    result = _run({"broker_demo_runtime_review_status": BROKER_DEMO_RUNTIME_REVIEW_REJECTED}, exact_state=True)
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_REJECTED
    assert "rejected_broker_demo_runtime_review" in result["protected_connector_gate_blockers"]


def test_missing_runtime_connector_blocks() -> None:
    result = _run({"runtime_connector": None}, exact_state=True)
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_runtime_connector" in result["protected_connector_gate_blockers"]


def test_runtime_connector_incomplete_blocks() -> None:
    result = _run({"runtime_connector": {"runtime_connector_status": "RUNTIME_CONNECTOR_INCOMPLETE"}})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "runtime_connector_not_ready" in result["protected_connector_gate_blockers"]


def test_runtime_connector_rejected_returns_rejected() -> None:
    result = _run({"runtime_connector": {"runtime_connector_status": RUNTIME_CONNECTOR_REJECTED}})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_REJECTED
    assert "rejected_runtime_connector" in result["protected_connector_gate_blockers"]


def test_missing_connector_contract_blocks() -> None:
    result = _run({"connector_contract": None}, exact_state=True)
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_connector_contract" in result["protected_connector_gate_blockers"]


def test_connector_contract_incomplete_blocks() -> None:
    result = _run({"connector_contract": {"connector_contract_status": "CONNECTOR_CONTRACT_INCOMPLETE"}})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "connector_contract_not_ready" in result["protected_connector_gate_blockers"]


def test_connector_contract_rejected_returns_rejected() -> None:
    result = _run({"connector_contract": {"connector_contract_status": CONNECTOR_CONTRACT_REJECTED}})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_REJECTED
    assert "rejected_connector_contract" in result["protected_connector_gate_blockers"]


def test_missing_review_chain_blocks() -> None:
    result = _run({"review_chain_status": None}, exact_state=True)
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_review_chain" in result["protected_connector_gate_blockers"]


def test_review_chain_incomplete_blocks() -> None:
    result = _run({"review_chain_status": "REVIEW_CHAIN_INCOMPLETE"})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "review_chain_not_ready" in result["protected_connector_gate_blockers"]


def test_review_chain_rejected_returns_rejected() -> None:
    result = _run({"review_chain_status": REVIEW_CHAIN_REJECTED})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_REJECTED
    assert "rejected_review_chain" in result["protected_connector_gate_blockers"]


def test_missing_certificate_blocks() -> None:
    result = _run({"certificate_status": None}, exact_state=True)
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_certificate" in result["protected_connector_gate_blockers"]


def test_certificate_incomplete_blocks() -> None:
    result = _run({"certificate_status": "LIVE_REVIEW_CERTIFICATE_INCOMPLETE"})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "certificate_not_ready" in result["protected_connector_gate_blockers"]


def test_certificate_rejected_returns_rejected() -> None:
    result = _run({"certificate_status": LIVE_REVIEW_CERTIFICATE_REJECTED})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_REJECTED
    assert "rejected_certificate" in result["protected_connector_gate_blockers"]


def test_missing_one_shot_package_blocks() -> None:
    result = _run({"one_shot_status": None}, exact_state=True)
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_one_shot_package" in result["protected_connector_gate_blockers"]


def test_one_shot_package_incomplete_blocks() -> None:
    result = _run({"one_shot_status": "ONE_SHOT_EXCEPTION_INCOMPLETE"}, exact_state=True)
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "one_shot_package_not_ready" in result["protected_connector_gate_blockers"]


def test_one_shot_package_rejected_returns_rejected() -> None:
    result = _run({"one_shot_status": ONE_SHOT_EXCEPTION_REJECTED}, exact_state=True)
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_REJECTED
    assert "rejected_one_shot_package" in result["protected_connector_gate_blockers"]


def test_missing_protected_connector_approval_blocks() -> None:
    result = _run({"protected_connector_approval": None})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_protected_connector_approval" in result["protected_connector_gate_blockers"]


def test_inactive_approval_window_expires() -> None:
    result = _run({"approval_window_active": False})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_EXPIRED
    assert "approval_window_inactive" in result["protected_connector_gate_blockers"]


def test_missing_approval_trace_blocks() -> None:
    result = _run({"approval_trace": None})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_approval_trace" in result["protected_connector_gate_blockers"]


def test_missing_replay_proof_blocks() -> None:
    result = _run({"replay_proof": None})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_replay_proof" in result["protected_connector_gate_blockers"]


def test_missing_reconciliation_proof_blocks() -> None:
    result = _run({"reconciliation_proof": None})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_reconciliation_proof" in result["protected_connector_gate_blockers"]


def test_missing_kill_switch_proof_blocks() -> None:
    result = _run({"kill_switch_proof": None})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_kill_switch_proof" in result["protected_connector_gate_blockers"]


def test_missing_rollback_proof_blocks() -> None:
    result = _run({"rollback_proof": None})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_rollback_proof" in result["protected_connector_gate_blockers"]


def test_missing_freshness_proof_blocks() -> None:
    result = _run({"freshness_proof": None})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_freshness_proof" in result["protected_connector_gate_blockers"]


def test_missing_final_disarm_proof_blocks() -> None:
    result = _run({"final_disarm_proof": None})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_final_disarm_proof" in result["protected_connector_gate_blockers"]


def test_missing_one_shot_controls_blocks() -> None:
    result = _run({"one_shot_controls": None})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_one_shot_controls" in result["protected_connector_gate_blockers"]


def test_missing_post_trade_journal_path_blocks() -> None:
    result = _run({"post_trade_journal_path": ""})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_post_trade_journal_path" in result["protected_connector_gate_blockers"]


def test_missing_operator_review_blocks() -> None:
    result = _run({"operator_review_required": False})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_operator_review_requirement" in result["protected_connector_gate_blockers"]


def test_missing_manual_arming_blocks() -> None:
    result = _run({"manual_arming_required": False}, exact_state=False)
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_manual_arming_requirement" in result["protected_connector_gate_blockers"]


def test_missing_timeout_requirement_blocks() -> None:
    result = _run({"timeout_required": False})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_timeout_requirement" in result["protected_connector_gate_blockers"]


def test_missing_revocation_path_blocks() -> None:
    result = _run({"revocation_path": ""})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_revocation_path" in result["protected_connector_gate_blockers"]


def test_missing_replay_prevention_blocks() -> None:
    result = _run({"replay_prevention": ""})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_replay_prevention" in result["protected_connector_gate_blockers"]


def test_missing_rollback_path_blocks() -> None:
    result = _run({"rollback_path": ""})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_rollback_path" in result["protected_connector_gate_blockers"]


def test_missing_connector_scope_blocks() -> None:
    result = _run({"connector_scope": ""})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_INCOMPLETE
    assert "missing_connector_scope" in result["protected_connector_gate_blockers"]


def test_retry_loop_detected_blocks() -> None:
    result = _run({"one_shot_controls": {"operator_review_required": True, "manual_arming_required": True, "no_retry_loop": False, "no_autonomous_reentry": True}})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_BLOCKED
    assert "retry_loop_detected" in result["protected_connector_gate_blockers"]


def test_autonomous_reentry_detected_blocks() -> None:
    result = _run({"one_shot_controls": {"operator_review_required": True, "manual_arming_required": True, "no_retry_loop": True, "no_autonomous_reentry": False}})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_BLOCKED
    assert "autonomous_reentry_detected" in result["protected_connector_gate_blockers"]


def test_broker_connection_detected_blocks() -> None:
    result = _run({"broker_connection_active": True})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_BLOCKED
    assert "broker_connection_detected" in result["protected_connector_gate_blockers"]


def test_network_access_detected_blocks() -> None:
    result = _run({"network_access": True})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_BLOCKED
    assert "network_access_detected" in result["protected_connector_gate_blockers"]


def test_credential_access_detected_blocks() -> None:
    result = _run({"credential_access_detected": True})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_BLOCKED
    assert "credential_access_detected" in result["protected_connector_gate_blockers"]


def test_account_identifier_detected_blocks() -> None:
    result = _run({"account_identifier_access_detected": True})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_BLOCKED
    assert "account_identifier_access_detected" in result["protected_connector_gate_blockers"]


def test_order_execution_detected_blocks() -> None:
    result = _run({"order_execution_enabled": True})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_BLOCKED
    assert "order_execution_detected" in result["protected_connector_gate_blockers"]


def test_live_trading_authorization_detected_blocks() -> None:
    result = _run({"live_trading_authorized": True})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_BLOCKED
    assert "live_trading_authorization_detected" in result["protected_connector_gate_blockers"]


def test_execution_authority_detected_blocks() -> None:
    result = _run({"execution_authority_granted": True})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_BLOCKED
    assert "execution_authority_detected" in result["protected_connector_gate_blockers"]


def test_capital_allocation_detected_blocks() -> None:
    result = _run({"capital_allocated": True})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_BLOCKED
    assert "capital_allocation_detected" in result["protected_connector_gate_blockers"]


def test_protected_connector_revoked_returns_revoked() -> None:
    result = _run({"protected_connector_revoked": True})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_REVOKED
    assert "protected_connector_revoked" in result["protected_connector_gate_blockers"]


def test_protected_connector_expired_returns_expired() -> None:
    result = _run({"protected_connector_expired": True})
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_EXPIRED
    assert "protected_connector_expired" in result["protected_connector_gate_blockers"]


def test_alias_aware_upstream_statuses_work() -> None:
    state = {
        "broker_demo_review_status": BROKER_DEMO_RUNTIME_REVIEW_READY,
        "broker_demo_runtime_connector_status": RUNTIME_CONNECTOR_REVIEW_READY,
        "live_review_connector_contract_status": CONNECTOR_CONTRACT_REVIEW_READY,
        "chain_status": REVIEW_CHAIN_REVIEW_READY,
        "live_review_certificate_status": LIVE_REVIEW_CERTIFICATE_REVIEW_READY,
        "exception_package_status": ONE_SHOT_EXCEPTION_REVIEW_READY,
        "protected_connector_approval": True,
        "approval_active": True,
        "approval": {"present": True},
        "replayability_proof": {"present": True},
        "reconciliation": {"present": True},
        "kill_switch": {"present": True},
        "rollback": {"present": True},
        "evidence_freshness": {"fresh": True},
        "final_disarm": {"present": True},
        "one_shot_controls": {
            "operator_review_required": True,
            "manual_arming_required": True,
            "no_retry_loop": True,
            "no_autonomous_reentry": True,
        },
        "post_trade_journal_path": "/tmp/journal",
        "operator_review_required": True,
        "manual_arming_required": True,
        "timeout_required": True,
        "revoke_path": "/tmp/revoke",
        "anti_replay": "/tmp/replay",
        "rollback_route": "/tmp/rollback",
        "scope": "forex_demo",
    }
    result = _run(state, exact_state=True)
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_REVIEW_READY


def test_alias_aware_proof_inputs_work() -> None:
    state = _base_state()
    state["replay"] = state.pop("replay_proof")
    state["reconciliation"] = state.pop("reconciliation_proof")
    state["kill_switch"] = state.pop("kill_switch_proof")
    state["rollback"] = state.pop("rollback_proof")
    state["evidence_freshness"] = state.pop("freshness_proof")
    state["final_disarm"] = state.pop("final_disarm_proof")
    state["journal_path"] = state.pop("post_trade_journal_path")
    result = _run(state, exact_state=True)
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_REVIEW_READY


def test_alias_aware_approval_inputs_work() -> None:
    state = _base_state()
    state["connector_approval"] = state.pop("protected_connector_approval")
    state["approval_active"] = state.pop("approval_window_active")
    state["approval"] = state.pop("approval_trace")
    result = _run(state, exact_state=True)
    assert result["protected_connector_gate_status"] == PROTECTED_CONNECTOR_GATE_REVIEW_READY


def test_gate_contract_hard_false_permissions_enforced() -> None:
    result = _run()
    contract = result["protected_connector_gate_contract"]
    assert contract["broker_connection_allowed"] is False
    assert contract["network_access_allowed"] is False
    assert contract["credential_access_allowed"] is False
    assert contract["account_identifier_access_allowed"] is False
    assert contract["order_execution_allowed"] is False
    assert contract["live_trading_authorized"] is False
    assert contract["execution_authority_granted"] is False


def test_safety_never_authorizes_broker_connection() -> None:
    assert _run()["safety"]["broker_connection_active"] is False


def test_safety_never_authorizes_network_access() -> None:
    assert _run()["safety"]["network_access"] is False


def test_safety_never_authorizes_order_execution() -> None:
    assert _run()["safety"]["order_execution_enabled"] is False


def test_safety_never_authorizes_live_trading() -> None:
    assert _run()["safety"]["live_trading_authorized"] is False


def test_safety_never_grants_execution_authority() -> None:
    assert _run()["safety"]["execution_authority_granted"] is False


def test_next_safe_action_deterministic() -> None:
    assert _run()["protected_connector_gate_next_safe_action"] == _run()["protected_connector_gate_next_safe_action"]


def test_required_next_packets_deterministic() -> None:
    assert _run()["protected_connector_gate_required_next_packets"] == _run()["protected_connector_gate_required_next_packets"]


def test_blockers_deterministic_and_deduplicated() -> None:
    state = _run({"network_access": True}, exact_state=True)
    assert "network_access_detected" in state["protected_connector_gate_blockers"]
    assert len(state["protected_connector_gate_blockers"]) == len(set(state["protected_connector_gate_blockers"]))


def test_protected_connector_gate_only_true() -> None:
    assert _run()["safety"]["protected_connector_gate_only"] is True


def test_broker_demo_connector_not_active_true() -> None:
    assert _run()["safety"]["broker_demo_connector_not_active"] is True
