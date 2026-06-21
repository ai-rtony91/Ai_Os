from __future__ import annotations

from copy import deepcopy

from automation.forex_engine.broker_demo_runtime_review import (
    BROKER_DEMO_RUNTIME_REVIEW_BLOCKED,
    BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE,
    BROKER_DEMO_RUNTIME_REVIEW_READY,
    BROKER_DEMO_RUNTIME_REVIEW_REJECTED,
    CONNECTOR_CONTRACT_REJECTED,
    CONNECTOR_CONTRACT_REVIEW_READY,
    LIVE_REVIEW_CERTIFICATE_REJECTED,
    LIVE_REVIEW_CERTIFICATE_REVIEW_READY,
    ONE_SHOT_EXCEPTION_REJECTED,
    ONE_SHOT_EXCEPTION_REVIEW_READY,
    RUNTIME_CONNECTOR_REJECTED,
    RUNTIME_CONNECTOR_REVIEW_READY,
    REVIEW_CHAIN_REJECTED,
    REVIEW_CHAIN_REVIEW_READY,
    evaluate_broker_demo_runtime_review,
)


def _base_state() -> dict:
    return {
        "runtime_connector": {
            "runtime_connector_status": RUNTIME_CONNECTOR_REVIEW_READY,
            "runtime_connector_completed": True,
        },
        "connector_contract": {
            "connector_contract_status": CONNECTOR_CONTRACT_REVIEW_READY,
            "connector_contract_completed": True,
        },
        "review_chain": {
            "review_chain_status": REVIEW_CHAIN_REVIEW_READY,
            "review_chain_completed": True,
        },
        "certificate": {
            "certificate_status": LIVE_REVIEW_CERTIFICATE_REVIEW_READY,
            "certificate_completed": True,
        },
        "one_shot_package": {
            "exception_package_status": ONE_SHOT_EXCEPTION_REVIEW_READY,
            "exception_package_completed": True,
        },
        "replay_proof": {"present": True},
        "reconciliation_proof": {"present": True},
        "kill_switch_proof": {"present": True},
        "rollback_proof": {"present": True},
        "freshness_proof": {"fresh": True},
        "final_disarm_proof": {"present": True},
        "post_trade_journal_path": "/tmp/journal",
        "one_shot_controls": {
            "operator_review_required": True,
            "manual_arming_required": True,
            "no_retry_loop": True,
            "no_autonomous_reentry": True,
        },
        "operator_review_required": True,
    }


def _run(state_overrides: dict | None = None, *, exact_state: bool = False) -> dict:
    state = _base_state()
    if state_overrides is not None:
        if exact_state:
            return evaluate_broker_demo_runtime_review(state_overrides)
        merged = deepcopy(state)
        for key, value in state_overrides.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                m = deepcopy(merged[key])
                m.update(value)
                merged[key] = m
            else:
                merged[key] = value
        return evaluate_broker_demo_runtime_review(merged)
    return evaluate_broker_demo_runtime_review(state)


def test_empty_state_blocks() -> None:
    result = evaluate_broker_demo_runtime_review({})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "missing_runtime_connector" in result["broker_demo_review_blockers"]


def test_complete_proof_state_returns_ready() -> None:
    result = _run()
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_READY
    assert result["broker_demo_runtime_review_ready"] is True
    assert result["broker_demo_review_blockers"] == []


def test_missing_runtime_connector_blocks() -> None:
    result = _run({"runtime_connector": None})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "missing_runtime_connector" in result["broker_demo_review_blockers"]


def test_runtime_connector_incomplete_blocks() -> None:
    state = _base_state()
    state["runtime_connector"]["runtime_connector_status"] = "RUNTIME_CONNECTOR_INCOMPLETE"
    result = _run(state)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "runtime_connector_not_ready" in result["broker_demo_review_blockers"]


def test_runtime_connector_rejected_returns_rejected() -> None:
    state = _base_state()
    state["runtime_connector"]["runtime_connector_status"] = RUNTIME_CONNECTOR_REJECTED
    result = _run(state)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_REJECTED
    assert "rejected_runtime_connector" in result["broker_demo_review_blockers"]


def test_missing_connector_contract_blocks() -> None:
    state = _base_state()
    state.pop("connector_contract")
    result = _run(state, exact_state=True)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "missing_connector_contract" in result["broker_demo_review_blockers"]


def test_connector_contract_incomplete_blocks() -> None:
    state = _base_state()
    state["connector_contract"]["connector_contract_status"] = "CONNECTOR_CONTRACT_INCOMPLETE"
    result = _run(state)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "connector_contract_not_ready" in result["broker_demo_review_blockers"]


def test_connector_contract_rejected_returns_rejected() -> None:
    state = _base_state()
    state["connector_contract"]["connector_contract_status"] = CONNECTOR_CONTRACT_REJECTED
    result = _run(state)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_REJECTED
    assert "rejected_connector_contract" in result["broker_demo_review_blockers"]


def test_missing_review_chain_blocks() -> None:
    state = _base_state()
    state.pop("review_chain")
    result = _run(state, exact_state=True)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "missing_review_chain" in result["broker_demo_review_blockers"]


def test_review_chain_incomplete_blocks() -> None:
    state = _base_state()
    state["review_chain"]["review_chain_status"] = "REVIEW_CHAIN_INCOMPLETE"
    result = _run(state)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "review_chain_not_ready" in result["broker_demo_review_blockers"]


def test_review_chain_rejected_returns_rejected() -> None:
    state = _base_state()
    state["review_chain"]["review_chain_status"] = REVIEW_CHAIN_REJECTED
    result = _run(state)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_REJECTED
    assert "rejected_review_chain" in result["broker_demo_review_blockers"]


def test_missing_certificate_blocks() -> None:
    state = _base_state()
    state.pop("certificate")
    result = _run(state, exact_state=True)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "missing_certificate" in result["broker_demo_review_blockers"]


def test_certificate_incomplete_blocks() -> None:
    state = _base_state()
    state["certificate"]["certificate_status"] = "LIVE_REVIEW_CERTIFICATE_INCOMPLETE"
    result = _run(state)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "certificate_not_ready" in result["broker_demo_review_blockers"]


def test_certificate_rejected_returns_rejected() -> None:
    state = _base_state()
    state["certificate"]["certificate_status"] = LIVE_REVIEW_CERTIFICATE_REJECTED
    result = _run(state)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_REJECTED
    assert "rejected_certificate" in result["broker_demo_review_blockers"]


def test_missing_one_shot_package_blocks() -> None:
    state = _base_state()
    state.pop("one_shot_package")
    result = _run(state, exact_state=True)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "missing_one_shot_package" in result["broker_demo_review_blockers"]


def test_one_shot_package_incomplete_blocks() -> None:
    state = _base_state()
    state["one_shot_package"]["exception_package_status"] = "ONE_SHOT_EXCEPTION_INCOMPLETE"
    result = _run(state)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "one_shot_package_not_ready" in result["broker_demo_review_blockers"]


def test_one_shot_package_rejected_returns_rejected() -> None:
    state = _base_state()
    state["one_shot_package"]["exception_package_status"] = ONE_SHOT_EXCEPTION_REJECTED
    result = _run(state)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_REJECTED
    assert "rejected_one_shot_package" in result["broker_demo_review_blockers"]


def test_missing_replay_proof_blocks() -> None:
    result = _run({"replay_proof": None})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "missing_replay_proof" in result["broker_demo_review_blockers"]


def test_missing_reconciliation_proof_blocks() -> None:
    result = _run({"reconciliation_proof": None})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "missing_reconciliation_proof" in result["broker_demo_review_blockers"]


def test_missing_kill_switch_proof_blocks() -> None:
    result = _run({"kill_switch_proof": None})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "missing_kill_switch_proof" in result["broker_demo_review_blockers"]


def test_missing_rollback_proof_blocks() -> None:
    result = _run({"rollback_proof": None})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "missing_rollback_proof" in result["broker_demo_review_blockers"]


def test_missing_freshness_proof_blocks() -> None:
    result = _run({"freshness_proof": None})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "missing_freshness_proof" in result["broker_demo_review_blockers"]


def test_missing_final_disarm_proof_blocks() -> None:
    result = _run({"final_disarm_proof": None})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "missing_final_disarm_proof" in result["broker_demo_review_blockers"]


def test_missing_one_shot_controls_blocks() -> None:
    result = _run({"one_shot_controls": None})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "missing_one_shot_controls" in result["broker_demo_review_blockers"]


def test_missing_post_trade_journal_path_blocks() -> None:
    result = _run({"post_trade_journal_path": ""})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "missing_post_trade_journal_path" in result["broker_demo_review_blockers"]


def test_missing_operator_review_blocks() -> None:
    result = _run({"operator_review_required": False})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "missing_operator_review_requirement" in result["broker_demo_review_blockers"]


def test_missing_manual_arming_blocks() -> None:
    result = _run({"one_shot_controls": {"operator_review_required": True, "manual_arming_required": False, "no_retry_loop": True, "no_autonomous_reentry": True}})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "missing_manual_arming_requirement" in result["broker_demo_review_blockers"]


def test_retry_loop_detected_blocks() -> None:
    result = _run({"one_shot_controls": {"operator_review_required": True, "manual_arming_required": True, "no_retry_loop": False, "no_autonomous_reentry": True}})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "retry_loop_detected" in result["broker_demo_review_blockers"]


def test_autonomous_reentry_detected_blocks() -> None:
    result = _run({"one_shot_controls": {"operator_review_required": True, "manual_arming_required": True, "no_retry_loop": True, "no_autonomous_reentry": False}})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    assert "autonomous_reentry_detected" in result["broker_demo_review_blockers"]


def test_broker_connection_detected_blocks() -> None:
    result = _run({"broker_connection_active": True})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_BLOCKED
    assert "broker_connection_detected" in result["broker_demo_review_blockers"]


def test_network_access_detected_blocks() -> None:
    result = _run({"network_access": True})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_BLOCKED
    assert "network_access_detected" in result["broker_demo_review_blockers"]


def test_credential_access_detected_blocks() -> None:
    result = _run({"credentials_accessed": True})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_BLOCKED
    assert "credential_access_detected" in result["broker_demo_review_blockers"]


def test_account_identifier_access_detected_blocks() -> None:
    result = _run({"account_identifiers_accessed": True})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_BLOCKED
    assert "account_identifier_access_detected" in result["broker_demo_review_blockers"]


def test_order_execution_detected_blocks() -> None:
    result = _run({"order_execution_enabled": True})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_BLOCKED
    assert "order_execution_detected" in result["broker_demo_review_blockers"]


def test_live_trading_authorization_detected_blocks() -> None:
    result = _run({"live_trading_authorized": True})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_BLOCKED
    assert "live_trading_authorization_detected" in result["broker_demo_review_blockers"]


def test_execution_authority_detected_blocks() -> None:
    result = _run({"execution_authority_granted": True})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_BLOCKED
    assert "execution_authority_detected" in result["broker_demo_review_blockers"]


def test_capital_allocation_detected_blocks() -> None:
    result = _run({"capital_allocated": True})
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_BLOCKED
    assert "capital_allocation_detected" in result["broker_demo_review_blockers"]


def test_alias_aware_runtime_connector_status_works() -> None:
    state = {
        "runtime_connector": {"status": RUNTIME_CONNECTOR_REVIEW_READY},
        "connector_contract": {"connector_contract_status": CONNECTOR_CONTRACT_REVIEW_READY},
        "review_chain": {"review_chain_status": REVIEW_CHAIN_REVIEW_READY},
        "certificate": {"certificate_status": LIVE_REVIEW_CERTIFICATE_REVIEW_READY},
        "one_shot_package": {"exception_package_status": ONE_SHOT_EXCEPTION_REVIEW_READY},
        "replay_proof": {"present": True},
        "reconciliation_proof": {"present": True},
        "kill_switch_proof": {"present": True},
        "rollback_proof": {"present": True},
        "freshness_proof": {"fresh": True},
        "final_disarm_proof": {"present": True},
        "post_trade_journal_path": "/tmp/journal",
        "one_shot_controls": {
            "operator_review_required": True,
            "manual_arming_required": True,
            "no_retry_loop": True,
            "no_autonomous_reentry": True,
        },
        "operator_review_required": True,
    }
    result = _run(state, exact_state=True)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_READY


def test_alias_aware_connector_contract_status_works() -> None:
    state = {
        "runtime_connector": {"runtime_connector_status": RUNTIME_CONNECTOR_REVIEW_READY},
        "connector_contract": {"status": CONNECTOR_CONTRACT_REVIEW_READY},
        "review_chain": {"review_chain_status": REVIEW_CHAIN_REVIEW_READY},
        "certificate": {"certificate_status": LIVE_REVIEW_CERTIFICATE_REVIEW_READY},
        "one_shot_package": {"exception_package_status": ONE_SHOT_EXCEPTION_REVIEW_READY},
        "replay_proof": {"present": True},
        "reconciliation_proof": {"present": True},
        "kill_switch_proof": {"present": True},
        "rollback_proof": {"present": True},
        "freshness_proof": {"fresh": True},
        "final_disarm_proof": {"present": True},
        "post_trade_journal_path": "/tmp/journal",
        "one_shot_controls": {
            "operator_review_required": True,
            "manual_arming_required": True,
            "no_retry_loop": True,
            "no_autonomous_reentry": True,
        },
        "operator_review_required": True,
    }
    result = _run(state, exact_state=True)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_READY


def test_alias_aware_proof_inputs_work() -> None:
    state = {
        "runtime_connector": {"runtime_connector_status": RUNTIME_CONNECTOR_REVIEW_READY},
        "connector_contract": {"connector_contract_status": CONNECTOR_CONTRACT_REVIEW_READY},
        "review_chain": {"review_chain_status": REVIEW_CHAIN_REVIEW_READY},
        "certificate": {"certificate_status": LIVE_REVIEW_CERTIFICATE_REVIEW_READY},
        "one_shot_package": {"exception_package_status": ONE_SHOT_EXCEPTION_REVIEW_READY},
        "replay": {"present": True},
        "reconciliation": {"present": True},
        "kill_switch": {"present": True},
        "rollback": {"present": True},
        "evidence_freshness": {"fresh": True},
        "final_disarm": {"present": True},
        "journal_path": "/tmp/journal",
        "controls": {
            "operator_review_required": True,
            "manual_arming_required": True,
            "no_retry_loop": True,
            "no_autonomous_reentry": True,
        },
        "operator_review_required": True,
    }
    result = _run(state, exact_state=True)
    assert result["broker_demo_review_status"] == BROKER_DEMO_RUNTIME_REVIEW_READY


def test_broker_demo_runtime_contract_hard_false_permissions_enforced() -> None:
    result = _run()
    contract = result["broker_demo_runtime_contract"]
    assert contract["broker_connection_allowed"] is False
    assert contract["network_access_allowed"] is False
    assert contract["credential_access_allowed"] is False
    assert contract["account_identifier_access_allowed"] is False
    assert contract["order_execution_allowed"] is False
    assert contract["live_trading_authorized"] is False
    assert contract["execution_authority_granted"] is False


def test_safety_never_authorizes_broker_connection() -> None:
    result = _run()
    assert result["safety"]["broker_connection_active"] is False


def test_safety_never_authorizes_network_access() -> None:
    result = _run()
    assert result["safety"]["network_access"] is False


def test_safety_never_authorizes_order_execution() -> None:
    result = _run()
    assert result["safety"]["order_execution_enabled"] is False


def test_safety_never_authorizes_live_trading() -> None:
    result = _run()
    assert result["safety"]["live_trading_authorized"] is False


def test_safety_never_grants_execution_authority() -> None:
    result = _run()
    assert result["safety"]["execution_authority_granted"] is False


def test_next_safe_action_deterministic() -> None:
    first = _run()
    second = _run()
    assert first["broker_demo_review_next_safe_action"] == second["broker_demo_review_next_safe_action"]


def test_required_next_packets_deterministic() -> None:
    first = _run()
    second = _run()
    assert first["broker_demo_review_required_next_packets"] == second["broker_demo_review_required_next_packets"]


def test_broker_demo_review_only_true() -> None:
    result = _run()
    assert result["safety"]["broker_demo_review_only"] is True


def test_deterministic_and_deduplicated_blockers() -> None:
    result = _run(
        {
            "broker_connection_active": True,
            "unsafe_broker_connection_detected": True,
            "execution_authority_granted": True,
        },
        exact_state=True,
    )
    assert len(result["broker_demo_review_blockers"]) == len(set(result["broker_demo_review_blockers"]))
