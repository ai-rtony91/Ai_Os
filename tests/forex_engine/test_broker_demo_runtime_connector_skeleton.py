from __future__ import annotations

import pytest

from automation.forex_engine.broker_demo_runtime_connector_skeleton import (
    evaluate_broker_demo_runtime_connector,
)


def _base_state():
    return {
        "connector_contract_status": "CONNECTOR_CONTRACT_REVIEW_READY",
        "review_chain_status": "REVIEW_CHAIN_REVIEW_READY",
        "review_chain_completed": True,
        "certificate_status": "LIVE_REVIEW_CERTIFICATE_REVIEW_READY",
        "certificate_completed": True,
        "one_shot_status": "ONE_SHOT_EXCEPTION_REVIEW_READY",
        "live_micro_trade_review_ready": True,
        "replay_proof": {"present": True},
        "reconciliation_proof": {"present": True},
        "kill_switch_proof": {"present": True},
        "rollback_proof": {"present": True},
        "freshness_proof": {"present": True},
        "final_disarm_proof": {"present": True},
        "one_shot_controls": {
            "one_order_only": True,
            "manual_arming_required": True,
            "no_retry_loop": True,
            "no_autonomous_reentry": True,
            "final_disarm_required": True,
        },
    }


def _assert_review_ready(result):
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_REVIEW_READY"
    assert result["runtime_connector_ready"] is True
    assert result["runtime_connector_blocked"] is False
    assert result["runtime_connector_review_required"] is False
    assert result["runtime_connector_completed"] is True


def test_empty_state_blocks():
    result = evaluate_broker_demo_runtime_connector({})
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_BLOCKED"
    assert result["runtime_connector_ready"] is False
    assert result["runtime_connector_blocked"] is True
    assert "missing_connector_contract" in result["runtime_connector_blockers"]


def test_complete_proof_state_review_ready():
    result = evaluate_broker_demo_runtime_connector(_base_state())
    _assert_review_ready(result)


def test_missing_connector_contract_blocks():
    state = _base_state()
    state.pop("connector_contract_status")
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_INCOMPLETE"
    assert "missing_connector_contract" in result["runtime_connector_blockers"]


def test_missing_review_chain_blocks():
    state = _base_state()
    state.pop("review_chain_status")
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_INCOMPLETE"
    assert "missing_review_chain" in result["runtime_connector_blockers"]


def test_missing_certificate_blocks():
    state = _base_state()
    state.pop("certificate_status")
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_INCOMPLETE"
    assert "missing_certificate" in result["runtime_connector_blockers"]


def test_missing_replay_proof_blocks():
    state = _base_state()
    state["replay_proof"] = {}
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_INCOMPLETE"
    assert "missing_replay_proof" in result["runtime_connector_blockers"]


def test_missing_reconciliation_proof_blocks():
    state = _base_state()
    state["reconciliation_proof"] = {}
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_INCOMPLETE"
    assert "missing_reconciliation_proof" in result["runtime_connector_blockers"]


def test_missing_kill_switch_proof_blocks():
    state = _base_state()
    state["kill_switch_proof"] = {}
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_INCOMPLETE"
    assert "missing_kill_switch_proof" in result["runtime_connector_blockers"]


def test_missing_rollback_proof_blocks():
    state = _base_state()
    state["rollback_proof"] = {}
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_INCOMPLETE"
    assert "missing_rollback_proof" in result["runtime_connector_blockers"]


def test_missing_freshness_proof_blocks():
    state = _base_state()
    state["freshness_proof"] = {}
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_INCOMPLETE"
    assert "missing_freshness_proof" in result["runtime_connector_blockers"]


def test_missing_final_disarm_proof_blocks():
    state = _base_state()
    state["final_disarm_proof"] = {}
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_INCOMPLETE"
    assert "missing_final_disarm_proof" in result["runtime_connector_blockers"]


def test_missing_one_shot_controls_blocks():
    state = _base_state()
    state["one_shot_controls"] = {}
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_INCOMPLETE"
    assert "missing_one_shot_controls" in result["runtime_connector_blockers"]


def test_broker_connection_detected_blocks():
    state = _base_state()
    state["broker_connection_detected"] = True
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_BLOCKED"
    assert "broker_connection_detected" in result["runtime_connector_blockers"]


def test_network_access_detected_blocks():
    state = _base_state()
    state["unsafe_network_access_detected"] = True
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_BLOCKED"
    assert "network_access_detected" in result["runtime_connector_blockers"]


def test_credential_access_detected_blocks():
    state = _base_state()
    state["unsafe_credential_access_detected"] = True
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_BLOCKED"
    assert "credential_access_detected" in result["runtime_connector_blockers"]


def test_account_identifier_detected_blocks():
    state = _base_state()
    state["unsafe_account_identifier_access_detected"] = True
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_BLOCKED"
    assert "account_identifier_access_detected" in result["runtime_connector_blockers"]


def test_order_execution_detected_blocks():
    state = _base_state()
    state["unsafe_order_execution_detected"] = True
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_BLOCKED"
    assert "order_execution_detected" in result["runtime_connector_blockers"]


def test_live_trading_authorization_detected_blocks():
    state = _base_state()
    state["unsafe_live_trading_authorization_detected"] = True
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_BLOCKED"
    assert "live_trading_authorization_detected" in result["runtime_connector_blockers"]


def test_execution_authority_detected_blocks():
    state = _base_state()
    state["unsafe_execution_authority_detected"] = True
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_BLOCKED"
    assert "execution_authority_detected" in result["runtime_connector_blockers"]


def test_deterministic_blocker_list():
    state = _base_state()
    state.pop("connector_contract_status")
    state.pop("review_chain_status")
    state["one_shot_controls"] = {}
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_blockers"] == [
        "missing_connector_contract",
        "missing_review_chain",
        "missing_one_shot_controls",
    ]


def test_deterministic_next_safe_action():
    base = evaluate_broker_demo_runtime_connector(_base_state())["runtime_connector_next_safe_action"]
    ready_again = evaluate_broker_demo_runtime_connector(_base_state())["runtime_connector_next_safe_action"]
    assert base == ready_again


def test_runtime_contract_values_enforced():
    result = evaluate_broker_demo_runtime_connector(_base_state())
    contract = result["runtime_contract"]
    assert contract["contract_version"] == "BROKER_DEMO_RUNTIME_CONNECTOR_SKELETON_V1"
    assert contract["review_chain_required"] is True
    assert contract["connector_contract_required"] is True
    assert contract["certificate_required"] is True
    assert contract["replay_required"] is True
    assert contract["reconciliation_required"] is True
    assert contract["kill_switch_required"] is True
    assert contract["rollback_required"] is True
    assert contract["freshness_required"] is True
    assert contract["final_disarm_required"] is True
    assert contract["one_shot_controls_required"] is True
    assert contract["broker_connection_active"] is False
    assert contract["network_access"] is False
    assert contract["credentials_accessed"] is False
    assert contract["account_identifiers_accessed"] is False
    assert contract["order_execution_enabled"] is False
    assert contract["live_trading_authorized"] is False
    assert contract["execution_authority_granted"] is False


def test_review_only_safety_preserved():
    result = evaluate_broker_demo_runtime_connector(_base_state())
    safety = result["safety"]
    assert safety == {
        "broker_connection_active": False,
        "network_access": False,
        "credentials_accessed": False,
        "account_identifiers_accessed": False,
        "order_execution_enabled": False,
        "live_trading_authorized": False,
        "execution_authority_granted": False,
    }


def test_never_authorize_live_trading():
    result = evaluate_broker_demo_runtime_connector(_base_state())
    assert result["runtime_contract"]["live_trading_authorized"] is False
    assert result["safety"]["live_trading_authorized"] is False


def test_never_authorize_execution_authority():
    result = evaluate_broker_demo_runtime_connector(_base_state())
    assert result["runtime_contract"]["execution_authority_granted"] is False
    assert result["safety"]["execution_authority_granted"] is False


def test_missing_connector_contract_status_mandates_blocked_when_not_ready():
    state = _base_state()
    state["connector_contract_status"] = "CONNECTOR_CONTRACT_INCOMPLETE"
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_INCOMPLETE"
    assert "connector_contract_not_ready" in result["runtime_connector_blockers"]


def test_missing_review_chain_status_not_ready():
    state = _base_state()
    state["review_chain_status"] = "REVIEW_CHAIN_INCOMPLETE"
    state["review_chain_completed"] = True
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_INCOMPLETE"
    assert "review_chain_not_ready" in result["runtime_connector_blockers"]


def test_missing_certificate_status_not_ready():
    state = _base_state()
    state["certificate_status"] = "LIVE_REVIEW_CERTIFICATE_INCOMPLETE"
    state["certificate_completed"] = True
    result = evaluate_broker_demo_runtime_connector(state)
    assert result["runtime_connector_status"] == "RUNTIME_CONNECTOR_INCOMPLETE"
    assert "certificate_not_ready" in result["runtime_connector_blockers"]
