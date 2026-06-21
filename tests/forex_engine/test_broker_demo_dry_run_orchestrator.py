from automation.forex_engine.broker_demo_dry_run_orchestrator import (
    DRY_RUN_ORCHESTRATION_BLOCKED,
    DRY_RUN_ORCHESTRATION_EXPIRED,
    DRY_RUN_ORCHESTRATION_INCOMPLETE,
    DRY_RUN_ORCHESTRATION_READY,
    DRY_RUN_ORCHESTRATION_REJECTED,
    DRY_RUN_ORCHESTRATION_REVOKED,
    orchestrate_broker_demo_dry_run,
)


def ready_state():
    return {
        "dry_run_status": "BROKER_DEMO_DRY_RUN_READY",
        "runtime_plan_status": "PROTECTED_RUNTIME_PLAN_REVIEW_READY",
        "approval_workflow_status": "APPROVAL_WORKFLOW_REVIEW_READY",
        "protected_connector_gate_status": "PROTECTED_CONNECTOR_GATE_REVIEW_READY",
        "broker_demo_runtime_review_status": "BROKER_DEMO_RUNTIME_REVIEW_READY",
        "runtime_connector_status": "RUNTIME_CONNECTOR_REVIEW_READY",
        "connector_contract_status": "CONNECTOR_CONTRACT_REVIEW_READY",
        "review_chain_status": "REVIEW_CHAIN_REVIEW_READY",
        "certificate_status": "LIVE_REVIEW_CERTIFICATE_REVIEW_READY",
        "one_shot_status": "ONE_SHOT_EXCEPTION_REVIEW_READY",
        "orchestration_request_present": True,
        "orchestration_trace": True,
        "orchestration_scope": True,
        "orchestration_owner": True,
        "orchestration_expiration": True,
        "orchestration_freshness": True,
        "orchestration_audit_record": True,
        "orchestration_handoff_boundary": True,
        "orchestration_connector_scope": True,
        "orchestration_replay_id": True,
        "orchestration_idempotency_key": True,
        "orchestration_result_sink": True,
        "sanitized_payload_only": True,
        "dry_run_trace": True,
        "dry_run_request_shape": True,
        "dry_run_response_shape": True,
        "runtime_plan_trace": True,
        "runtime_plan_evidence_bundle": True,
        "approval_trace": True,
        "approval_evidence_bundle": True,
        "approval_window_active": True,
        "replay_prevention": True,
        "replay_proof": True,
        "reconciliation_proof": True,
        "kill_switch_proof": True,
        "rollback_proof": True,
        "freshness_proof": True,
        "final_disarm_proof": True,
        "one_shot_controls": True,
        "post_trade_journal_path": True,
        "operator_review_required": True,
        "manual_arming_required": True,
        "timeout_required": True,
    }


def test_empty_state_incomplete():
    result = orchestrate_broker_demo_dry_run({})
    assert result["dry_run_orchestration_status"] == DRY_RUN_ORCHESTRATION_EXPIRED
    assert "missing_dry_run_connector" in result["dry_run_orchestration_blockers"]


def test_complete_state_ready():
    result = orchestrate_broker_demo_dry_run(ready_state())
    assert result["dry_run_orchestration_status"] == DRY_RUN_ORCHESTRATION_READY
    assert result["dry_run_orchestration_ready"] is True
    assert result["dry_run_handoff_package"]["ready_for_future_broker_demo_connector_review"] is True


def test_missing_runtime_plan_incomplete():
    state = ready_state()
    state.pop("runtime_plan_status")
    result = orchestrate_broker_demo_dry_run(state)
    assert result["dry_run_orchestration_status"] == DRY_RUN_ORCHESTRATION_INCOMPLETE
    assert "missing_runtime_plan" in result["dry_run_orchestration_blockers"]


def test_rejected_upstream_rejected():
    state = ready_state()
    state["dry_run_status"] = "BROKER_DEMO_DRY_RUN_REJECTED"
    result = orchestrate_broker_demo_dry_run(state)
    assert result["dry_run_orchestration_status"] == DRY_RUN_ORCHESTRATION_REJECTED


def test_revoked_status():
    state = ready_state()
    state["dry_run_orchestration_revoked"] = True
    result = orchestrate_broker_demo_dry_run(state)
    assert result["dry_run_orchestration_status"] == DRY_RUN_ORCHESTRATION_REVOKED


def test_expired_status():
    state = ready_state()
    state["dry_run_orchestration_expired"] = True
    result = orchestrate_broker_demo_dry_run(state)
    assert result["dry_run_orchestration_status"] == DRY_RUN_ORCHESTRATION_EXPIRED


def test_unsafe_broker_blocks():
    state = ready_state()
    state["broker_connection_active"] = True
    result = orchestrate_broker_demo_dry_run(state)
    assert result["dry_run_orchestration_status"] == DRY_RUN_ORCHESTRATION_BLOCKED
    assert "broker_connection_detected" in result["dry_run_orchestration_blockers"]


def test_unsafe_network_blocks():
    state = ready_state()
    state["network_access"] = True
    result = orchestrate_broker_demo_dry_run(state)
    assert result["dry_run_orchestration_status"] == DRY_RUN_ORCHESTRATION_BLOCKED


def test_contract_hard_false_permissions():
    result = orchestrate_broker_demo_dry_run(ready_state())
    contract = result["dry_run_orchestration_contract"]
    assert contract["broker_connection_allowed"] is False
    assert contract["network_access_allowed"] is False
    assert contract["order_execution_allowed"] is False
    assert contract["live_trading_authorized"] is False
    assert contract["execution_authority_granted"] is False


def test_safety_hard_false_permissions():
    result = orchestrate_broker_demo_dry_run(ready_state())
    safety = result["safety"]
    assert safety["broker_connection_active"] is False
    assert safety["network_access"] is False
    assert safety["order_execution_enabled"] is False
    assert safety["live_trading_authorized"] is False
    assert safety["execution_authority_granted"] is False
    assert safety["broker_demo_dry_run_orchestration_only"] is True


def test_alias_aware_inputs_work():
    state = ready_state()
    state["broker_demo_dry_run_status"] = state.pop("dry_run_status")
    state["protected_runtime_plan_status"] = state.pop("runtime_plan_status")
    state["approval_status"] = state.pop("approval_workflow_status")
    state["connector_gate_status"] = state.pop("protected_connector_gate_status")
    result = orchestrate_broker_demo_dry_run(state)
    assert result["dry_run_orchestration_status"] == DRY_RUN_ORCHESTRATION_READY


def test_next_action_deterministic():
    result = orchestrate_broker_demo_dry_run(ready_state())
    assert result["dry_run_orchestration_next_safe_action"] == "proceed_to_future_broker_demo_connector_review"


def test_required_packets_deterministic():
    result = orchestrate_broker_demo_dry_run(ready_state())
    assert result["dry_run_orchestration_required_next_packets"] == [
        "AIOS_FOREX_PROTECTED_BROKER_DEMO_CONNECTOR_REVIEW_V1",
        "AIOS_FOREX_BROKER_DEMO_CONNECTOR_IMPLEMENTATION_PLAN_V1",
        "AIOS_FOREX_BROKER_DEMO_CREDENTIAL_BOUNDARY_V1",
    ]


def test_blockers_deduplicated():
    state = ready_state()
    state["network_access"] = True
    state["network_access_detected"] = True
    result = orchestrate_broker_demo_dry_run(state)
    assert result["dry_run_orchestration_blockers"].count("network_access_detected") == 1