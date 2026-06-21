from copy import deepcopy

import pytest

from automation.forex_engine.broker_demo_connector_dry_run import (
    STATUS_BLOCKED,
    STATUS_EXPIRED,
    STATUS_INCOMPLETE,
    STATUS_READY,
    STATUS_REJECTED,
    STATUS_REVOKED,
    evaluate_broker_demo_connector_dry_run,
)


def _base_state():
    return {
        "runtime_plan_status": "PROTECTED_RUNTIME_PLAN_REVIEW_READY",
        "approval_workflow_status": "APPROVAL_WORKFLOW_REVIEW_READY",
        "protected_connector_gate_status": "PROTECTED_CONNECTOR_GATE_REVIEW_READY",
        "broker_demo_runtime_review_status": "BROKER_DEMO_RUNTIME_REVIEW_READY",
        "runtime_connector_status": "RUNTIME_CONNECTOR_REVIEW_READY",
        "connector_contract_status": "CONNECTOR_CONTRACT_REVIEW_READY",
        "review_chain_status": "REVIEW_CHAIN_REVIEW_READY",
        "certificate_status": "LIVE_REVIEW_CERTIFICATE_REVIEW_READY",
        "one_shot_status": "ONE_SHOT_EXCEPTION_REVIEW_READY",
        "dry_run_request_present": True,
        "dry_run_trace": True,
        "dry_run_scope": True,
        "dry_run_owner": True,
        "dry_run_expiration": True,
        "dry_run_freshness": True,
        "dry_run_audit_record": True,
        "dry_run_handoff_boundary": True,
        "dry_run_connector_scope": True,
        "dry_run_request_shape": True,
        "dry_run_response_shape": True,
        "sanitized_payload_only": True,
        "approval_trace": True,
        "approval_evidence_bundle": True,
        "approval_window_active": True,
        "runtime_plan_trace": True,
        "runtime_plan_evidence_bundle": True,
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
        "no_retry_loop": True,
        "no_autonomous_reentry": True,
    }


def _eval(state):
    return evaluate_broker_demo_connector_dry_run(state)


def test_empty_state_blocks():
    result = _eval({})
    assert result["dry_run_status"] in {STATUS_INCOMPLETE, STATUS_BLOCKED}
    assert not result["dry_run_completed"]
    assert result["dry_run_required_next_packets"]


def test_complete_proof_state_returns_ready():
    result = _eval(_base_state())
    assert result["dry_run_status"] == STATUS_READY
    assert result["dry_run_completed"]
    assert result["dry_run_ready"]
    assert not result["dry_run_review_required"]


@pytest.mark.parametrize(
    "mutator, blocker",
    [
        (lambda s: s.pop("runtime_plan_status", None), "missing_runtime_plan"),
        (lambda s: s.__setitem__("runtime_plan_status", "BROKEN"), "runtime_plan_not_ready"),
        (lambda s: s.__setitem__("runtime_plan_status", "BROKEN_REJECTED"), "rejected_runtime_plan"),
    ],
    ids=["missing runtime plan", "runtime plan incomplete", "runtime plan rejected"],
)
def test_runtime_plan_block_patterns(mutator, blocker):
    state = _base_state()
    mutator(state)
    result = _eval(state)
    if blocker == "rejected_runtime_plan":
        assert result["dry_run_status"] == STATUS_REJECTED
    else:
        assert result["dry_run_status"] == STATUS_INCOMPLETE
    assert blocker in result["dry_run_blockers"]


@pytest.mark.parametrize(
    "mutator, blocker, status",
    [
        (lambda s: s.pop("approval_workflow_status", None), "missing_approval_workflow", STATUS_INCOMPLETE),
        (lambda s: s.__setitem__("approval_workflow_status", "BROKEN"), "approval_workflow_not_ready", STATUS_INCOMPLETE),
        (lambda s: s.__setitem__("approval_workflow_status", "BROKEN_REJECTED"), "rejected_approval_workflow", STATUS_REJECTED),
        (lambda s: s.pop("protected_connector_gate_status", None), "missing_protected_connector_gate", STATUS_INCOMPLETE),
        (lambda s: s.__setitem__("protected_connector_gate_status", "BROKEN"), "protected_connector_gate_not_ready", STATUS_INCOMPLETE),
        (lambda s: s.__setitem__("protected_connector_gate_status", "BROKEN_REJECTED"), "rejected_protected_connector_gate", STATUS_REJECTED),
        (lambda s: s.pop("broker_demo_runtime_review_status", None), "missing_broker_demo_runtime_review", STATUS_INCOMPLETE),
        (lambda s: s.__setitem__("broker_demo_runtime_review_status", "BROKEN"), "broker_demo_runtime_review_not_ready", STATUS_INCOMPLETE),
        (lambda s: s.__setitem__("broker_demo_runtime_review_status", "BROKEN_REJECTED"), "rejected_broker_demo_runtime_review", STATUS_REJECTED),
        (lambda s: s.pop("runtime_connector_status", None), "missing_runtime_connector", STATUS_INCOMPLETE),
        (lambda s: s.__setitem__("runtime_connector_status", "BROKEN"), "runtime_connector_not_ready", STATUS_INCOMPLETE),
        (lambda s: s.__setitem__("runtime_connector_status", "BROKEN_REJECTED"), "rejected_runtime_connector", STATUS_REJECTED),
        (lambda s: s.pop("connector_contract_status", None), "missing_connector_contract", STATUS_INCOMPLETE),
        (lambda s: s.__setitem__("connector_contract_status", "BROKEN"), "connector_contract_not_ready", STATUS_INCOMPLETE),
        (lambda s: s.__setitem__("connector_contract_status", "BROKEN_REJECTED"), "rejected_connector_contract", STATUS_REJECTED),
        (lambda s: s.pop("review_chain_status", None), "missing_review_chain", STATUS_INCOMPLETE),
        (lambda s: s.__setitem__("review_chain_status", "BROKEN"), "review_chain_not_ready", STATUS_INCOMPLETE),
        (lambda s: s.__setitem__("review_chain_status", "BROKEN_REJECTED"), "rejected_review_chain", STATUS_REJECTED),
        (lambda s: s.pop("certificate_status", None), "missing_certificate", STATUS_INCOMPLETE),
        (lambda s: s.__setitem__("certificate_status", "BROKEN"), "certificate_not_ready", STATUS_INCOMPLETE),
        (lambda s: s.__setitem__("certificate_status", "BROKEN_REJECTED"), "rejected_certificate", STATUS_REJECTED),
        (lambda s: s.pop("one_shot_status", None), "missing_one_shot_package", STATUS_INCOMPLETE),
        (lambda s: s.__setitem__("one_shot_status", "BROKEN"), "one_shot_package_not_ready", STATUS_INCOMPLETE),
        (lambda s: s.__setitem__("one_shot_status", "BROKEN_REJECTED"), "rejected_one_shot_package", STATUS_REJECTED),
    ],
)
def test_runtime_review_and_chain_block_patterns(mutator, blocker, status):
    state = _base_state()
    mutator(state)
    result = _eval(state)
    if status == STATUS_REJECTED:
        assert result["dry_run_status"] == STATUS_REJECTED
    else:
        assert result["dry_run_status"] == STATUS_INCOMPLETE
    assert blocker in result["dry_run_blockers"]


@pytest.mark.parametrize(
    "field, blocker",
    [
        ("dry_run_request_present", "missing_dry_run_request"),
        ("dry_run_trace", "missing_dry_run_trace"),
        ("dry_run_scope", "missing_dry_run_scope"),
        ("dry_run_owner", "missing_dry_run_owner"),
        ("dry_run_expiration", "missing_dry_run_expiration"),
        ("dry_run_freshness", "missing_dry_run_freshness"),
        ("dry_run_audit_record", "missing_dry_run_audit_record"),
        ("dry_run_handoff_boundary", "missing_dry_run_handoff_boundary"),
        ("dry_run_connector_scope", "missing_dry_run_connector_scope"),
        ("dry_run_request_shape", "missing_dry_run_request_shape"),
        ("dry_run_response_shape", "missing_dry_run_response_shape"),
        ("sanitized_payload_only", "missing_sanitized_payload_only"),
    ],
)
def test_missing_dry_run_inputs(field, blocker):
    state = _base_state()
    state.pop(field)
    result = _eval(state)
    assert result["dry_run_status"] == STATUS_INCOMPLETE
    assert blocker in result["dry_run_blockers"]


@pytest.mark.parametrize(
    "field, blocker",
    [
        ("approval_trace", "missing_approval_trace"),
        ("approval_evidence_bundle", "missing_approval_evidence_bundle"),
        ("runtime_plan_trace", "missing_runtime_plan_trace"),
        ("runtime_plan_evidence_bundle", "missing_runtime_plan_evidence_bundle"),
        ("replay_prevention", "missing_replay_prevention"),
        ("replay_proof", "missing_replay_proof"),
        ("reconciliation_proof", "missing_reconciliation_proof"),
        ("kill_switch_proof", "missing_kill_switch_proof"),
        ("rollback_proof", "missing_rollback_proof"),
        ("freshness_proof", "missing_freshness_proof"),
        ("final_disarm_proof", "missing_final_disarm_proof"),
        ("one_shot_controls", "missing_one_shot_controls"),
        ("post_trade_journal_path", "missing_post_trade_journal_path"),
        ("operator_review_required", "missing_operator_review_requirement"),
        ("manual_arming_required", "missing_manual_arming_requirement"),
        ("timeout_required", "missing_timeout_requirement"),
    ],
)
def test_missing_dry_run_controls(field, blocker):
    state = _base_state()
    state.pop(field)
    result = _eval(state)
    assert result["dry_run_status"] == STATUS_INCOMPLETE
    assert blocker in result["dry_run_blockers"]


def test_inactive_approval_window_causes_expired():
    state = _base_state()
    state["approval_window_active"] = False
    result = _eval(state)
    assert result["dry_run_status"] == STATUS_EXPIRED


@pytest.mark.parametrize(
    "field, blocker",
    [
        ("no_retry_loop", "retry_loop_detected"),
        ("no_autonomous_reentry", "autonomous_reentry_detected"),
    ],
)
def test_negative_control_blockers(field, blocker):
    state = _base_state()
    state[field] = False
    result = _eval(state)
    assert result["dry_run_status"] == STATUS_INCOMPLETE
    assert blocker in result["dry_run_blockers"]


@pytest.mark.parametrize(
    "field",
    [
        "broker_connection_detected",
        "network_access_detected",
        "credential_access_detected",
        "account_identifier_access_detected",
        "order_execution_detected",
        "live_trading_authorization_detected",
        "execution_authority_detected",
        "capital_allocation_detected",
    ],
)
def test_runtime_unsafe_flags_block(field):
    state = _base_state()
    state[field] = True
    result = _eval(state)
    assert result["dry_run_status"] == STATUS_BLOCKED


def test_dry_run_revoked_returns_revoked():
    state = _base_state()
    state["dry_run_revoked"] = True
    result = _eval(state)
    assert result["dry_run_status"] == STATUS_REVOKED
    assert result["dry_run_review_required"]


def test_dry_run_expired_returns_expired():
    state = _base_state()
    state["dry_run_expired"] = True
    result = _eval(state)
    assert result["dry_run_status"] == STATUS_EXPIRED


def test_alias_aware_upstream_statuses_work():
    state = _base_state()
    state.pop("runtime_plan_status")
    state.pop("approval_workflow_status")
    state.pop("protected_connector_gate_status")
    state.pop("broker_demo_runtime_review_status")
    state.pop("runtime_connector_status")
    state.pop("connector_contract_status")
    state.pop("review_chain_status")
    state.pop("certificate_status")
    state.pop("one_shot_status")
    state["protected_runtime_plan_status"] = "PROTECTED_RUNTIME_PLAN_REVIEW_READY"
    state["approval_status"] = "APPROVAL_WORKFLOW_REVIEW_READY"
    state["connector_gate_status"] = "PROTECTED_CONNECTOR_GATE_REVIEW_READY"
    state["broker_demo_review_status"] = "BROKER_DEMO_RUNTIME_REVIEW_READY"
    state["broker_demo_runtime_connector_status"] = "RUNTIME_CONNECTOR_REVIEW_READY"
    state["live_review_connector_contract_status"] = "CONNECTOR_CONTRACT_REVIEW_READY"
    state["chain_status"] = "REVIEW_CHAIN_REVIEW_READY"
    state["live_review_certificate_status"] = "LIVE_REVIEW_CERTIFICATE_REVIEW_READY"
    state["exception_package_status"] = "ONE_SHOT_EXCEPTION_REVIEW_READY"
    result = _eval(state)
    assert result["dry_run_status"] == STATUS_READY


def test_alias_aware_dry_run_inputs_work():
    state = _base_state()
    state.update(
        {
            "dry_run_request_present": False,
            "request_present": True,
            "dry_run_trace": False,
            "request_trace": True,
            "dry_run_scope": False,
            "request_scope": True,
            "dry_run_owner": False,
            "request_owner": True,
            "dry_run_expiration": False,
            "request_expiration": True,
            "dry_run_freshness": False,
            "request_freshness": True,
            "dry_run_audit_record": False,
            "request_audit_record": True,
            "dry_run_handoff_boundary": False,
            "request_handoff_boundary": True,
            "dry_run_connector_scope": False,
            "request_connector_scope": True,
            "dry_run_request_shape": False,
            "request_shape": True,
            "dry_run_response_shape": False,
            "response_shape": True,
            "sanitized_only": True,
        },
    )
    result = _eval(state)
    assert result["dry_run_status"] == STATUS_READY
    assert result["dry_run_request_envelope"]["sanitized_payload_only"] is True


def test_alias_aware_control_inputs_work():
    state = _base_state()
    state["approval_trace"] = False
    state["approval"] = True
    state["runtime_plan_trace"] = False
    state["plan_trace"] = True
    state["runtime_plan_evidence_bundle"] = False
    state["plan_evidence_bundle"] = True
    state["replay_prevention"] = False
    state["anti_replay"] = True
    state["replay_proof"] = False
    state["replayability_proof"] = True
    state["freshness_proof"] = False
    state["evidence_freshness"] = True
    state["final_disarm_proof"] = False
    state["final_disarm"] = True
    result = _eval(state)
    assert result["dry_run_status"] == STATUS_READY


def test_request_envelope_hard_false_permissions_enforced():
    result = _eval(_base_state())
    envelope = result["dry_run_request_envelope"]
    assert envelope["envelope_version"] == "BROKER_DEMO_CONNECTOR_DRY_RUN_REQUEST_V1"
    assert envelope["request_type"] == "BROKER_DEMO_DRY_RUN"
    assert envelope["dry_run_only"] is True
    assert envelope["sanitized_payload_only"] is True
    assert envelope["broker_connection_requested"] is False
    assert envelope["network_requested"] is False
    assert envelope["credential_access_requested"] is False
    assert envelope["account_identifier_requested"] is False
    assert envelope["order_execution_requested"] is False
    assert envelope["live_trading_requested"] is False
    assert envelope["execution_authority_requested"] is False


def test_response_envelope_hard_false_permissions_enforced():
    result = _eval(_base_state())
    envelope = result["dry_run_response_envelope"]
    assert envelope["envelope_version"] == "BROKER_DEMO_CONNECTOR_DRY_RUN_RESPONSE_V1"
    assert envelope["response_type"] == "BROKER_DEMO_DRY_RUN_RESULT"
    assert envelope["dry_run_only"] is True
    assert envelope["sanitized_payload_only"] is True
    assert envelope["broker_connection_performed"] is False
    assert envelope["network_performed"] is False
    assert envelope["credential_access_performed"] is False
    assert envelope["account_identifier_access_performed"] is False
    assert envelope["order_execution_performed"] is False
    assert envelope["live_trading_performed"] is False
    assert envelope["execution_authority_granted"] is False


def test_contract_hard_false_permissions_enforced():
    result = _eval(_base_state())
    contract = result["dry_run_contract"]
    assert contract["contract_version"] == "BROKER_DEMO_CONNECTOR_DRY_RUN_V1"
    for field in contract:
        if field.endswith("_required"):
            assert contract[field] is True
    assert contract["broker_connection_allowed"] is False
    assert contract["network_access_allowed"] is False
    assert contract["credential_access_allowed"] is False
    assert contract["account_identifier_access_allowed"] is False
    assert contract["order_execution_allowed"] is False
    assert contract["live_trading_authorized"] is False
    assert contract["execution_authority_granted"] is False


def test_safety_never_authorizes_broker_connection():
    result = _eval(_base_state())
    assert result["safety"]["broker_connection_active"] is False


def test_safety_never_authorizes_network_access():
    result = _eval(_base_state())
    assert result["safety"]["network_access"] is False


def test_safety_never_authorizes_order_execution():
    result = _eval(_base_state())
    assert result["safety"]["order_execution_enabled"] is False


def test_safety_never_authorizes_live_trading():
    result = _eval(_base_state())
    assert result["safety"]["live_trading_authorized"] is False


def test_safety_never_grants_execution_authority():
    result = _eval(_base_state())
    assert result["safety"]["execution_authority_granted"] is False


def test_next_safe_action_is_deterministic():
    result_a = _eval(_base_state())
    result_b = _eval(_base_state())
    assert result_a["dry_run_next_safe_action"] == result_b["dry_run_next_safe_action"]


def test_required_next_packets_deterministic_and_deduped():
    result = _eval(_base_state())
    assert result["dry_run_required_next_packets"] == sorted(set(result["dry_run_required_next_packets"]))
    assert result["dry_run_required_next_packets"]


def test_blockers_are_deterministic_and_deduped():
    state = _base_state()
    state.pop("dry_run_scope")
    state.pop("request_scope", None)
    first = _eval(state)
    second = _eval(state)
    assert first["dry_run_blockers"] == second["dry_run_blockers"]
    assert first["dry_run_blockers"] == sorted(set(first["dry_run_blockers"]))


def test_broker_demo_dry_run_only_true():
    result = _eval(_base_state())
    assert result["dry_run_request_envelope"]["dry_run_only"] is True
    assert result["dry_run_response_envelope"]["dry_run_only"] is True


def test_sanitized_payload_only_true():
    result = _eval(_base_state())
    assert result["dry_run_request_envelope"]["sanitized_payload_only"] is True
    assert result["dry_run_response_envelope"]["sanitized_payload_only"] is True
    assert result["dry_run_contract"]["sanitized_payload_required"]
    assert result["safety"]["sanitized_payload_only"] is True


def test_broker_demo_connector_not_active_true():
    result = _eval(_base_state())
    assert result["safety"]["broker_demo_connector_not_active"] is True


@pytest.mark.parametrize(
    "field, alias",
    [
        ("dry_run_request_present", "request_present"),
        ("dry_run_trace", "request_trace"),
        ("dry_run_scope", "request_scope"),
        ("dry_run_owner", "request_owner"),
        ("dry_run_expiration", "request_expiration"),
        ("dry_run_freshness", "request_freshness"),
        ("dry_run_audit_record", "request_audit_record"),
        ("dry_run_handoff_boundary", "request_handoff_boundary"),
        ("dry_run_connector_scope", "request_connector_scope"),
        ("dry_run_request_shape", "request_shape"),
        ("dry_run_response_shape", "response_shape"),
        ("sanitized_payload_only", "sanitized_only"),
    ],
)
def test_alias_inputs_specific(field, alias):
    state = _base_state()
    state.pop(field, None)
    state[alias] = True
    result = _eval(state)
    assert result["dry_run_status"] == STATUS_READY


@pytest.mark.parametrize(
    "field, alias",
    [
        ("approval_trace", "approval"),
        ("approval_evidence_bundle", "approval_evidence"),
        ("runtime_plan_trace", "plan_trace"),
        ("runtime_plan_evidence_bundle", "plan_evidence_bundle"),
        ("replay_prevention", "anti_replay"),
        ("replay_proof", "replay"),
        ("reconciliation_proof", "reconciliation"),
        ("kill_switch_proof", "kill_switch"),
        ("rollback_proof", "rollback"),
        ("freshness_proof", "evidence_fresh"),
        ("final_disarm_proof", "final_disarm"),
        ("one_shot_controls", "controls"),
        ("post_trade_journal_path", "journal_path"),
    ],
)
def test_alias_control_specific(field, alias):
    state = _base_state()
    state.pop(field, None)
    state[alias] = True
    if isinstance(state.get(field), bool):
        state[field] = False
    result = _eval(state)
    assert result["dry_run_status"] == STATUS_READY
