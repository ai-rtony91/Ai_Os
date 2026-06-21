from __future__ import annotations

import copy

from automation.forex_engine.live_review_connector_contract import (
    CONNECTOR_CONTRACT_BLOCKED,
    CONNECTOR_CONTRACT_INCOMPLETE,
    CONNECTOR_CONTRACT_REJECTED,
    CONNECTOR_CONTRACT_REVIEW_READY,
    evaluate_live_review_connector_contract,
)


def _base_state():
    return {
        "review_chain_orchestrator": {"review_chain_status": "REVIEW_CHAIN_REVIEW_READY"},
        "live_review_readiness_certificate": {"certificate_status": "LIVE_REVIEW_CERTIFICATE_REVIEW_READY"},
        "one_shot_exception_package": {
            "exception_package_status": "ONE_SHOT_EXCEPTION_REVIEW_READY",
        },
        "replay_proof": {"present": True},
        "reconciliation_proof": {"present": True},
        "kill_switch_proof": {"present": True},
        "rollback_proof": {"present": True},
        "freshness_proof": {"present": True},
        "final_disarm_proof": {"present": True},
        "post_trade_journal_path": "/tmp/journal",
        "operator_review_required": True,
        "one_shot_controls": {
            "one_order_only": True,
            "no_retry_loop": True,
            "no_autonomous_reentry": True,
            "manual_arming_required": True,
            "final_disarm_required": True,
        },
    }


def _evaluate(state):
    return evaluate_live_review_connector_contract(state)


def test_empty_state_blocks():
    result = _evaluate({})
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_BLOCKED
    assert "missing_review_chain_orchestrator" in result["connector_blockers"]
    assert "missing_live_review_certificate" in result["connector_blockers"]
    assert "missing_one_shot_exception_package" in result["connector_blockers"]


def test_complete_state_returns_review_ready():
    result = _evaluate(_base_state())
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_REVIEW_READY
    assert result["connector_ready"]


def test_missing_review_chain_blocks():
    state = _base_state()
    state.pop("review_chain_orchestrator")
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_BLOCKED
    assert "missing_review_chain_orchestrator" in result["connector_blockers"]


def test_review_chain_incomplete_blocks():
    state = _base_state()
    state["review_chain_orchestrator"]["review_chain_status"] = "REVIEW_CHAIN_INCOMPLETE"
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_INCOMPLETE
    assert "review_chain_not_review_ready" in result["connector_blockers"]


def test_review_chain_rejected_returns_rejected():
    state = _base_state()
    state["review_chain_orchestrator"]["review_chain_status"] = "REVIEW_CHAIN_REJECTED"
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_REJECTED
    assert "rejected_review_chain" in result["connector_blockers"]


def test_missing_certificate_blocks():
    state = _base_state()
    state.pop("live_review_readiness_certificate")
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_BLOCKED
    assert "missing_live_review_certificate" in result["connector_blockers"]


def test_certificate_incomplete_blocks():
    state = _base_state()
    state["live_review_readiness_certificate"]["certificate_status"] = "LIVE_REVIEW_CERTIFICATE_INCOMPLETE"
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_INCOMPLETE
    assert "certificate_not_review_ready" in result["connector_blockers"]


def test_certificate_rejected_returns_rejected():
    state = _base_state()
    state["live_review_readiness_certificate"]["certificate_status"] = "LIVE_REVIEW_CERTIFICATE_REJECTED"
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_REJECTED
    assert "certificate_rejected" in result["connector_blockers"]


def test_missing_one_shot_package_blocks():
    state = _base_state()
    state.pop("one_shot_exception_package")
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_BLOCKED
    assert "missing_one_shot_exception_package" in result["connector_blockers"]


def test_one_shot_incomplete_blocks():
    state = _base_state()
    state["one_shot_exception_package"]["exception_package_status"] = "ONE_SHOT_EXCEPTION_INCOMPLETE"
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_INCOMPLETE
    assert "one_shot_package_not_review_ready" in result["connector_blockers"]


def test_one_shot_rejected_returns_rejected():
    state = _base_state()
    state["one_shot_exception_package"]["exception_package_status"] = "ONE_SHOT_EXCEPTION_REJECTED"
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_REJECTED
    assert "one_shot_package_rejected" in result["connector_blockers"]


def test_missing_replay_proof_blocks():
    state = _base_state()
    state.pop("replay_proof")
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_INCOMPLETE
    assert "missing_replay_proof" in result["connector_blockers"]


def test_missing_reconciliation_proof_blocks():
    state = _base_state()
    state.pop("reconciliation_proof")
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_INCOMPLETE
    assert "missing_reconciliation_proof" in result["connector_blockers"]


def test_missing_kill_switch_proof_blocks():
    state = _base_state()
    state.pop("kill_switch_proof")
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_INCOMPLETE
    assert "missing_kill_switch_proof" in result["connector_blockers"]


def test_missing_rollback_proof_blocks():
    state = _base_state()
    state.pop("rollback_proof")
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_INCOMPLETE
    assert "missing_rollback_proof" in result["connector_blockers"]


def test_missing_freshness_proof_blocks():
    state = _base_state()
    state.pop("freshness_proof")
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_INCOMPLETE
    assert "missing_freshness_proof" in result["connector_blockers"]


def test_missing_one_shot_controls_blocks():
    state = _base_state()
    state.pop("one_shot_controls")
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_INCOMPLETE
    assert "missing_one_shot_controls" in result["connector_blockers"]


def test_missing_final_disarm_proof_blocks():
    state = _base_state()
    state.pop("final_disarm_proof")
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_INCOMPLETE
    assert "missing_final_disarm_proof" in result["connector_blockers"]


def test_missing_post_trade_journal_path_blocks():
    state = _base_state()
    state["post_trade_journal_path"] = ""
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_INCOMPLETE
    assert "missing_post_trade_journal_path" in result["connector_blockers"]


def test_missing_operator_review_blocks():
    state = _base_state()
    state["operator_review_required"] = False
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_INCOMPLETE
    assert "missing_operator_review_requirement" in result["connector_blockers"]


def test_missing_manual_arming_blocks():
    state = _base_state()
    state["one_shot_controls"]["manual_arming_required"] = False
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_INCOMPLETE
    assert "missing_manual_arming_requirement" in result["connector_blockers"]


def test_retry_loop_detected_blocks():
    state = _base_state()
    state["retry_loop_detected"] = True
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_BLOCKED
    assert "retry_loop_detected" in result["connector_blockers"]


def test_autonomous_reentry_detected_blocks():
    state = _base_state()
    state["autonomous_reentry_detected"] = True
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_BLOCKED
    assert "autonomous_reentry_detected" in result["connector_blockers"]


def test_broker_connection_flag_blocks():
    state = _base_state()
    state["broker_connection_detected"] = True
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_BLOCKED
    assert "broker_connection_detected" in result["connector_blockers"]


def test_network_access_flag_blocks():
    state = _base_state()
    state["network_access"] = True
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_BLOCKED
    assert "network_access_detected" in result["connector_blockers"]


def test_credential_access_flag_blocks():
    state = _base_state()
    state["credential_access_detected"] = True
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_BLOCKED
    assert "credential_access_detected" in result["connector_blockers"]


def test_account_identifier_access_flag_blocks():
    state = _base_state()
    state["account_identifier_access_detected"] = True
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_BLOCKED
    assert "account_identifier_access_detected" in result["connector_blockers"]


def test_order_execution_flag_blocks():
    state = _base_state()
    state["order_execution_enabled"] = True
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_BLOCKED
    assert "order_execution_detected" in result["connector_blockers"]


def test_live_trading_authorization_flag_blocks():
    state = _base_state()
    state["live_trading_authorized"] = True
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_BLOCKED
    assert "live_trading_authorization_detected" in result["connector_blockers"]


def test_execution_authority_flag_blocks():
    state = _base_state()
    state["execution_authority_detected"] = True
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_BLOCKED
    assert "execution_authority_detected" in result["connector_blockers"]


def test_capital_allocation_flag_blocks():
    state = _base_state()
    state["capital_allocation_detected"] = True
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_BLOCKED
    assert "capital_allocation_detected" in result["connector_blockers"]


def test_alias_aware_review_chain_inputs_work():
    state = _base_state()
    state["review_chain"] = {"chain_status": state["review_chain_orchestrator"]["review_chain_status"]}
    state.pop("review_chain_orchestrator")
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_REVIEW_READY


def test_alias_aware_certificate_inputs_work():
    state = _base_state()
    state["certificate"] = {
        "live_review_certificate_status": state["live_review_readiness_certificate"]["certificate_status"],
    }
    state.pop("live_review_readiness_certificate")
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_REVIEW_READY


def test_alias_aware_one_shot_inputs_work():
    state = _base_state()
    state["one_shot_package"] = {"one_shot_status": state["one_shot_exception_package"]["exception_package_status"]}
    state.pop("one_shot_exception_package")
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_REVIEW_READY


def test_alias_aware_proof_inputs_work():
    state = _base_state()
    state.pop("replay_proof")
    state["replayability_proof"] = {"present": True}
    state["replay"] = False
    result = _evaluate(state)
    assert result["connector_contract_status"] == CONNECTOR_CONTRACT_REVIEW_READY


def test_connector_runtime_contract_has_all_required_false_execution_permissions():
    contract = _evaluate(_base_state())["connector_runtime_contract"]
    assert contract["broker_connection_allowed"] is False
    assert contract["credential_access_allowed"] is False
    assert contract["account_identifier_access_allowed"] is False
    assert contract["network_access_allowed"] is False
    assert contract["order_execution_allowed"] is False
    assert contract["live_trading_authorized"] is False
    assert contract["execution_authority_granted"] is False


def test_safety_never_authorizes_broker_connection():
    assert _evaluate(_base_state())["safety"]["broker_connection_active"] is False


def test_safety_never_authorizes_network_access():
    assert _evaluate(_base_state())["safety"]["network_access"] is False


def test_safety_never_authorizes_order_execution():
    assert _evaluate(_base_state())["safety"]["order_execution_enabled"] is False


def test_safety_never_authorizes_live_trading():
    assert _evaluate(_base_state())["safety"]["live_trading_authorized"] is False


def test_safety_never_grants_execution_authority():
    assert _evaluate(_base_state())["safety"]["execution_authority_granted"] is False


def test_connector_next_safe_action_deterministic():
    state = _base_state()
    ready = _evaluate(state)
    assert ready["connector_next_safe_action"] == _evaluate(state)["connector_next_safe_action"]
    assert ready["connector_next_safe_action"] == "submit_review_chain_for_human_approval"


def test_connector_required_next_packets_deterministic():
    state = _base_state()
    packets = _evaluate(state)
    assert packets["connector_required_next_packets"] == _evaluate(state)["connector_required_next_packets"]
    assert packets["connector_required_next_packets"] == [
        "prepare_final_connector_signoff_packet",
        "request_human_review",
        "close_connector_contract_review",
    ]


def test_blockers_are_deterministic_and_deduplicated():
    state = _base_state()
    state.pop("review_chain_orchestrator")
    state["review_chain"] = {"chain_status": "REVIEW_CHAIN_INCOMPLETE"}
    first = _evaluate(state)
    second = _evaluate(state)
    assert first["connector_blockers"] == second["connector_blockers"]
    assert len(first["connector_blockers"]) == len(set(first["connector_blockers"]))


def test_connector_review_required_true():
    result = _evaluate(_base_state())
    assert result["connector_review_required"] is True
