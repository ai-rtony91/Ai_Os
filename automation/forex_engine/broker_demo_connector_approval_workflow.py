"""Broker demo connector approval workflow gate."""

from __future__ import annotations

from typing import Any, Dict, List


APPROVAL_WORKFLOW_BLOCKED = "APPROVAL_WORKFLOW_BLOCKED"
APPROVAL_WORKFLOW_INCOMPLETE = "APPROVAL_WORKFLOW_INCOMPLETE"
APPROVAL_WORKFLOW_REVIEW_READY = "APPROVAL_WORKFLOW_REVIEW_READY"
APPROVAL_WORKFLOW_REJECTED = "APPROVAL_WORKFLOW_REJECTED"
APPROVAL_WORKFLOW_REVOKED = "APPROVAL_WORKFLOW_REVOKED"
APPROVAL_WORKFLOW_EXPIRED = "APPROVAL_WORKFLOW_EXPIRED"


REQUIRED_BLOCKERS_ORDER = [
    "missing_protected_connector_gate",
    "protected_connector_gate_not_ready",
    "missing_broker_demo_runtime_review",
    "broker_demo_runtime_review_not_ready",
    "missing_runtime_connector",
    "runtime_connector_not_ready",
    "missing_connector_contract",
    "connector_contract_not_ready",
    "missing_approval_request",
    "missing_approval_trace",
    "missing_approval_evidence_bundle",
    "approval_window_inactive",
    "missing_approval_timestamp",
    "missing_approval_freshness",
    "missing_approval_scope",
    "missing_approval_reviewer",
    "missing_approval_expiration",
    "missing_approval_revocation_path",
    "missing_approval_audit_record",
    "missing_replay_prevention",
    "missing_kill_switch_proof",
    "missing_rollback_proof",
    "missing_reconciliation_proof",
    "missing_final_disarm_proof",
    "missing_one_shot_controls",
    "approval_expired",
    "approval_revoked",
    "broker_connection_detected",
    "network_access_detected",
    "credential_access_detected",
    "account_identifier_access_detected",
    "order_execution_detected",
    "live_trading_authorization_detected",
    "execution_authority_detected",
    "capital_allocation_detected",
]


def evaluate_broker_demo_connector_approval_workflow(
    state: Dict[str, Any], optional_limits: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    s = _normalize_inputs(state)

    required_statuses = {
        "protected_connector_gate_status": "PROTECTED_CONNECTOR_GATE_REVIEW_READY",
        "broker_demo_runtime_review_status": "BROKER_DEMO_RUNTIME_REVIEW_READY",
        "runtime_connector_status": "RUNTIME_CONNECTOR_REVIEW_READY",
        "connector_contract_status": "CONNECTOR_CONTRACT_REVIEW_READY",
    }

    blockers = []
    for key, expected in required_statuses.items():
        value = s.get(key)
        if value is None:
            blockers.append(f"missing_{key.replace('_status', '')}")
        elif value != expected:
            blockers.append(f"{key.replace('_status', '')}_not_ready")

    blockers.extend(_required_inputs_blockers(s))
    blockers.extend(_required_controls_blockers(s))

    if s.get("approval_expired"):
        blockers.append("approval_expired")
    if s.get("approval_revoked"):
        blockers.append("approval_revoked")

    unsafe_flags = [
        "broker_connection_detected",
        "network_access_detected",
        "credential_access_detected",
        "account_identifier_access_detected",
        "order_execution_detected",
        "live_trading_authorization_detected",
        "execution_authority_detected",
        "capital_allocation_detected",
    ]
    for flag in unsafe_flags:
        if s.get(flag):
            blockers.append(flag)

    blockers = _dedupe_ordered(blockers)
    blockers = [b for b in REQUIRED_BLOCKERS_ORDER if b in blockers] + [
        b for b in blockers if b not in REQUIRED_BLOCKERS_ORDER
    ]

    has_request_key = "approval_request_present" in s
    request_present = s.get("approval_request_present")

    if s.get("approval_revoked"):
        status = APPROVAL_WORKFLOW_REVOKED
    elif s.get("approval_expired"):
        status = APPROVAL_WORKFLOW_EXPIRED
    elif any(b in blockers for b in unsafe_flags):
        status = APPROVAL_WORKFLOW_BLOCKED
    elif has_request_key and request_present is False and len(blockers) == 1 and blockers == ["missing_approval_request"]:
        status = APPROVAL_WORKFLOW_REJECTED
    elif blockers:
        status = APPROVAL_WORKFLOW_REJECTED if has_request_key and request_present is False else APPROVAL_WORKFLOW_INCOMPLETE
    else:
        status = APPROVAL_WORKFLOW_REVIEW_READY

    review_ready = status == APPROVAL_WORKFLOW_REVIEW_READY
    blocked = status == APPROVAL_WORKFLOW_BLOCKED
    completed = status in {APPROVAL_WORKFLOW_REVIEW_READY, APPROVAL_WORKFLOW_REJECTED}

    warnings = []
    if s.get("approval_window_active") is False:
        warnings.append("approval_window_inactive")

    summary = {
        "status": status,
        "blockers_count": len(blockers),
        "limit_profile": (optional_limits or {}).get("profile", "default"),
        "approval_scope": s.get("approval_scope"),
        "approval_reviewer": s.get("approval_reviewer"),
        "approval_window_active": s.get("approval_window_active"),
        "approval_freshness": s.get("approval_freshness"),
    }

    required_next_packets = _next_packets(blockers, status)

    return {
        "approval_workflow_completed": completed,
        "approval_workflow_status": status,
        "approval_workflow_review_ready": review_ready,
        "approval_workflow_blocked": blocked,
        "approval_workflow_review_required": status in {
            APPROVAL_WORKFLOW_INCOMPLETE,
            APPROVAL_WORKFLOW_REJECTED,
        },
        "approval_workflow_summary": summary,
        "approval_workflow_blockers": blockers,
        "approval_workflow_warnings": warnings,
        "approval_workflow_next_safe_action": required_next_packets[0]
        if required_next_packets
        else "route_to_broker_demo_connector_implementation",
        "approval_workflow_required_next_packets": required_next_packets,
        "approval_workflow_contract": {
            "contract_version": "BROKER_DEMO_CONNECTOR_APPROVAL_WORKFLOW_V1",
            "protected_connector_gate_required": True,
            "runtime_review_required": True,
            "runtime_connector_required": True,
            "connector_contract_required": True,
            "approval_trace_required": True,
            "approval_evidence_required": True,
            "approval_window_required": True,
            "approval_freshness_required": True,
            "approval_scope_required": True,
            "approval_reviewer_required": True,
            "approval_expiration_required": True,
            "approval_revocation_required": True,
            "approval_audit_required": True,
            "replay_prevention_required": True,
            "kill_switch_required": True,
            "rollback_required": True,
            "reconciliation_required": True,
            "final_disarm_required": True,
            "one_shot_controls_required": True,
            "broker_connection_allowed": False,
            "network_access_allowed": False,
            "credential_access_allowed": False,
            "account_identifier_access_allowed": False,
            "order_execution_allowed": False,
            "live_trading_authorized": False,
            "execution_authority_granted": False,
        },
        "safety": {
            "broker_connection_active": False,
            "network_access": False,
            "credentials_accessed": False,
            "account_identifiers_accessed": False,
            "order_execution_enabled": False,
            "live_trading_authorized": False,
            "execution_authority_granted": False,
            "capital_allocated": False,
            "approval_workflow_only": True,
        },
    }


def _required_inputs_blockers(state: Dict[str, Any]) -> List[str]:
    required = [
        ("approval_request_present", "present"),
        ("approval_trace", "any"),
        ("approval_evidence_bundle", "any"),
        ("approval_window_active", "boolean"),
        ("approval_timestamp", "any"),
        ("approval_freshness", "any"),
        ("approval_scope", "any"),
        ("approval_reviewer", "any"),
        ("approval_expiration", "any"),
        ("approval_revocation_path", "any"),
        ("approval_audit_record", "any"),
    ]
    blockers = []
    for field, mode in required:
        value = state.get(field)
        if mode == "present":
            if value is False:
                blockers.append("missing_approval_request")
        elif mode == "boolean":
            if value is not True:
                blockers.append("approval_window_inactive")
        elif value is None or (isinstance(value, str) and value.strip() == ""):
            blockers.append(f"missing_{field}")
    return blockers


def _required_controls_blockers(state: Dict[str, Any]) -> List[str]:
    required = [
        "replay_prevention",
        "kill_switch_proof",
        "rollback_proof",
        "reconciliation_proof",
        "final_disarm_proof",
        "one_shot_controls",
    ]
    blockers = []
    for field in required:
        if state.get(field) is None:
            blockers.append(f"missing_{field}")
    return blockers


def _next_packets(blockers: List[str], status: str) -> List[str]:
    if status == APPROVAL_WORKFLOW_REVOKED:
        return ["resolve_revocation", "await_new_approval_package"]
    if status == APPROVAL_WORKFLOW_EXPIRED:
        return ["refresh_approval_window", "refresh_approval_timestamp"]
    if status == APPROVAL_WORKFLOW_REJECTED:
        return ["collect_missing_approval_request_context"]
    if status == APPROVAL_WORKFLOW_BLOCKED:
        return ["clear_unsafe_runtime_flags"]
    if not blockers:
        return ["route_to_broker_demo_connector_implementation"]

    ordered = []
    if any("protected_connector_gate" in b for b in blockers):
        ordered.append("run_protected_broker_demo_connector_gate")
    if any("runtime_review" in b for b in blockers):
        ordered.append("run_broker_demo_runtime_review")
    if any("runtime_connector" in b for b in blockers):
        ordered.append("run_runtime_connector_gate")
    if any("connector_contract" in b for b in blockers):
        ordered.append("run_connector_contract_review")
    if any("approval" in b for b in blockers):
        ordered.append("prepare_approval_artifacts")
    if any(flag in blockers for flag in [
        "broker_connection_detected",
        "network_access_detected",
        "credential_access_detected",
        "account_identifier_access_detected",
        "order_execution_detected",
        "live_trading_authorization_detected",
        "execution_authority_detected",
        "capital_allocation_detected",
    ]):
        ordered.append("remove_unsafe_runtime_access")
    return _dedupe_ordered(ordered)


def _normalize_inputs(state: Dict[str, Any] | None) -> Dict[str, Any]:
    if state is None:
        return {}

    raw_aliases = {
        # required statuses
        "protected_connector_gate_status": "protected_connector_gate_status",
        "broker_demo_runtime_review_status": "broker_demo_runtime_review_status",
        "runtime_connector_status": "runtime_connector_status",
        "connector_contract_status": "connector_contract_status",

        # required inputs
        "approval_request_present": "approval_request_present",
        "approvalrequestpresent": "approval_request_present",
        "approverequestpresent": "approval_request_present",
        "approval_trace": "approval_trace",
        "approvaltrace": "approval_trace",
        "approval_trace_bundle": "approval_trace",
        "approval_evidence_bundle": "approval_evidence_bundle",
        "approvalevidencebundle": "approval_evidence_bundle",
        "approval_window_active": "approval_window_active",
        "approvalwindowactive": "approval_window_active",
        "approval_timestamp": "approval_timestamp",
        "approvaltimestamp": "approval_timestamp",
        "approval_freshness": "approval_freshness",
        "approvalfreshness": "approval_freshness",
        "approval_scope": "approval_scope",
        "approvalscope": "approval_scope",
        "approval_reviewer": "approval_reviewer",
        "approvalreviewer": "approval_reviewer",
        "approval_expiration": "approval_expiration",
        "approvalexpiration": "approval_expiration",
        "approval_revocation_path": "approval_revocation_path",
        "approvalrevocationpath": "approval_revocation_path",
        "approval_audit_record": "approval_audit_record",
        "approvalauditrecord": "approval_audit_record",
        "approvalrevocation": "approval_revoked",
        "approval_revoked": "approval_revoked",
        "approval_expired": "approval_expired",
        "approvalexpired": "approval_expired",

        # required controls
        "replay_prevention": "replay_prevention",
        "replayprevention": "replay_prevention",
        "kill_switch_proof": "kill_switch_proof",
        "killswitchproof": "kill_switch_proof",
        "rollback_proof": "rollback_proof",
        "rollbackproof": "rollback_proof",
        "reconciliation_proof": "reconciliation_proof",
        "reconciliationproof": "reconciliation_proof",
        "final_disarm_proof": "final_disarm_proof",
        "finaldisarmproof": "final_disarm_proof",
        "one_shot_controls": "one_shot_controls",
        "oneshotcontrols": "one_shot_controls",

        # unsafe/runtime flags
        "broker_connection_detected": "broker_connection_detected",
        "brokerconnectiondetected": "broker_connection_detected",
        "network_access_detected": "network_access_detected",
        "networkaccessdetected": "network_access_detected",
        "credential_access_detected": "credential_access_detected",
        "credentialaccessdetected": "credential_access_detected",
        "account_identifier_access_detected": "account_identifier_access_detected",
        "accountidentifieraccessdetected": "account_identifier_access_detected",
        "order_execution_detected": "order_execution_detected",
        "orderexecutiondetected": "order_execution_detected",
        "live_trading_authorization_detected": "live_trading_authorization_detected",
        "livetradingauthorizationdetected": "live_trading_authorization_detected",
        "execution_authority_detected": "execution_authority_detected",
        "executionauthoritydetected": "execution_authority_detected",
        "capital_allocation_detected": "capital_allocation_detected",
        "capitalallocationdetected": "capital_allocation_detected",
    }
    aliases = {_normalize_key(key): value for key, value in raw_aliases.items()}

    normalized: Dict[str, Any] = {}
    for key, value in dict(state).items():
        normalized_key = _normalize_key(str(key))
        canonical = aliases.get(normalized_key, normalized_key)
        normalized[canonical] = value
    return normalized


def _normalize_key(value: str) -> str:
    return "".join(c.lower() for c in value if c.isalnum())


def _dedupe_ordered(items: List[str]) -> List[str]:
    return list(dict.fromkeys(items))
