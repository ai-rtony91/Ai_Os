from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from automation.forex_engine import schema_contracts as schemas


BROKER_ID = "OANDA"
BROKER_REFERENCE = "OANDA_DEMO_CONNECTION_GATE_REFERENCE_ONLY"
GATE_READY = "OANDA_DEMO_CONNECTION_GATE_READY"
GATE_BLOCKED = "OANDA_DEMO_CONNECTION_GATE_BLOCKED"
APPROVAL_SCOPE = "oanda_demo_connection_gate_spec_only"
GATE_MODE = "CONNECTION_READINESS_ONLY"
AUTH_REFERENCE_FORMAT = "SANITIZED_REFERENCE_ONLY"
AUTH_MATERIAL_LOCATION = "EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY"
SUPPORTED_ACCOUNT_MODES = {"PRACTICE_DEMO", "PAPER_DEMO"}
SUPPORTED_ENVIRONMENTS = {"OANDA_PRACTICE_DEMO", "PRACTICE_REFERENCE_ONLY"}
SUPPORTED_ENDPOINT_CLASSIFICATIONS = {"OANDA_PRACTICE_DEMO", "PRACTICE_REFERENCE_ONLY"}
MIN_TIMEOUT_SECONDS = 1
MAX_TIMEOUT_SECONDS = 30

REQUIRED_GATE_FIELDS = (
    "broker_id",
    "account_mode",
    "environment",
    "endpoint_classification",
    "approval_scope",
    "gate_mode",
    "external_auth_reference_present",
    "external_auth_reference_format",
    "auth_material_location",
    "runtime_auth_boundary_confirmed",
    "runtime_auth_proof_present",
    "repo_storage_confirmed_absent",
    "account_identifier_present",
    "human_owner_connection_gate_approved",
    "network_broker_call_gate_approved",
    "one_shot_only",
    "timeout_seconds",
    "stop_on_success_or_failure",
    "no_order_route_confirmed",
    "no_account_id_logging_confirmed",
    "audit_logging_acknowledged",
)

FORBIDDEN_GATE_FIELD_NAMES = {
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "token",
    "password",
    "secret",
    "private_key",
    "credential",
    "credentials",
    "broker_credentials",
    "account_id",
    "account_number",
    "account_identifier",
    "live_account_id",
    "broker_order_id",
    "transaction_id",
    "live_payload",
    "raw_live_payload",
    "authorization",
}

FORBIDDEN_VALUE_MARKERS = (
    "bearer ",
    "basic ",
    "api_key=",
    "access_token",
    "refresh_token",
    "password=",
    "secret=",
    "private_key",
    "-----begin",
    "sk-",
    "not_a_real_value",
)

UNAUTHORIZED_TRUE_FIELDS = {
    "broker_sdk_allowed",
    "network_allowed",
    "network_api_allowed",
    "env_secret_read_allowed",
    "credentials_allowed",
    "credentials_used",
    "credential_material_present",
    "repo_stored_auth_material_present",
    "auth_material_persisted",
    "broker_connection_allowed",
    "broker_request_allowed",
    "broker_request_requested",
    "broker_request_sent",
    "connection_attempt_allowed",
    "connection_attempt_allowed_now",
    "connection_attempt_requested",
    "connection_attempt_performed",
    "account_access_allowed",
    "account_mutation_allowed",
    "order_route_allowed",
    "order_route_requested",
    "broker_paper_orders_allowed",
    "paper_order_execution",
    "live_orders_allowed",
    "live_execution_allowed",
    "live_account_access_allowed",
    "real_money_routing_allowed",
    "would_place_order",
    "order_placed",
    "execution_allowed",
    "execution_requested",
    "live_endpoint_allowed",
    "live_endpoint_requested",
}


@dataclass(frozen=True)
class OandaDemoConnectionGateApproval:
    broker_id: str = BROKER_ID
    account_mode: str = "PRACTICE_DEMO"
    environment: str = "OANDA_PRACTICE_DEMO"
    endpoint_classification: str = "OANDA_PRACTICE_DEMO"
    approval_scope: str = APPROVAL_SCOPE
    gate_mode: str = GATE_MODE
    external_auth_reference_present: bool = True
    external_auth_reference_format: str = AUTH_REFERENCE_FORMAT
    auth_material_location: str = AUTH_MATERIAL_LOCATION
    runtime_auth_boundary_confirmed: bool = True
    runtime_auth_proof_present: bool = True
    repo_storage_confirmed_absent: bool = True
    account_identifier_present: bool = False
    human_owner_connection_gate_approved: bool = True
    network_broker_call_gate_approved: bool = True
    one_shot_only: bool = True
    timeout_seconds: int = 10
    stop_on_success_or_failure: bool = True
    no_order_route_confirmed: bool = True
    no_account_id_logging_confirmed: bool = True
    audit_logging_acknowledged: bool = True


def build_oanda_demo_connection_gate_contract() -> dict[str, Any]:
    contract = {
        "schema": "AIOS_OANDA_DEMO_CONNECTION_GATE_CONTRACT.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "mode": GATE_MODE,
        "purpose": "Validate readiness for a future one-shot OANDA practice/demo connection packet.",
        "required_gate_fields": list(REQUIRED_GATE_FIELDS),
        "approval_scope_required": APPROVAL_SCOPE,
        "gate_mode_required": GATE_MODE,
        "supported_account_modes": sorted(SUPPORTED_ACCOUNT_MODES),
        "supported_environments": sorted(SUPPORTED_ENVIRONMENTS),
        "supported_endpoint_classifications": sorted(SUPPORTED_ENDPOINT_CLASSIFICATIONS),
        "one_shot_only_required": True,
        "timeout_min_seconds": MIN_TIMEOUT_SECONDS,
        "timeout_max_seconds": MAX_TIMEOUT_SECONDS,
        "runtime_auth_boundary_required": True,
        "sanitized_connection_evidence_required": True,
        "no_order_route_required": True,
        "no_account_id_logging_required": True,
        "fail_closed_default": True,
        "connection_readiness_only": True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_connection_gate_side_effects(contract)
    return contract


def build_runtime_auth_boundary_requirements() -> dict[str, Any]:
    requirements = {
        "schema": "AIOS_OANDA_DEMO_CONNECTION_RUNTIME_AUTH_BOUNDARY.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "auth_material_location_required": AUTH_MATERIAL_LOCATION,
        "auth_reference_format_required": AUTH_REFERENCE_FORMAT,
        "runtime_auth_proof_required": True,
        "repo_stored_auth_material_allowed": False,
        "repo_stored_auth_material_present": False,
        "auth_values_may_be_logged": False,
        "account_identifiers_may_be_logged": False,
        "env_reads_allowed": False,
        "file_reads_for_auth_allowed": False,
        "file_writes_for_auth_allowed": False,
        "forbidden_gate_field_names": sorted(FORBIDDEN_GATE_FIELD_NAMES),
        "credential_like_values_blocked": True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_connection_gate_side_effects(requirements)
    return requirements


def build_sanitized_connection_evidence_schema() -> dict[str, Any]:
    evidence_schema = {
        "schema": "AIOS_OANDA_DEMO_CONNECTION_SANITIZED_EVIDENCE_SCHEMA.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "evidence_storage": "IN_MEMORY_SANITIZED_EVIDENCE_ONLY",
        "allowed_evidence_fields": [
            "schema",
            "event",
            "broker_id",
            "status",
            "classification",
            "connection_readiness_gate_ready",
            "connection_readiness_only",
            "future_connection_packet_ready_for_human_review",
            "blockers",
            "forbidden_fields_detected",
            "credential_like_value_paths_detected",
            "unauthorized_execution_fields_detected",
            "timeout_seconds",
            "one_shot_only",
            "sanitized",
        ],
        "forbidden_evidence_material": [
            "auth material values",
            "account identifiers",
            "broker response payloads",
            "raw request payloads",
            "order payloads",
            "live account data",
        ],
        "sanitized": True,
        "contains_private_data": False,
        "contains_real_credentials": False,
        "contains_account_identifier": False,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_connection_gate_side_effects(evidence_schema)
    return evidence_schema


def build_no_order_no_account_logging_rules() -> dict[str, Any]:
    rules = {
        "schema": "AIOS_OANDA_DEMO_CONNECTION_NO_ORDER_NO_ACCOUNT_LOGGING_RULES.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "order_route_must_remain_disabled": True,
        "account_identifier_logging_must_remain_disabled": True,
        "broker_order_identifier_logging_must_remain_disabled": True,
        "raw_payload_logging_must_remain_disabled": True,
        "account_access_must_not_be_requested_by_gate": True,
        "account_mutation_must_not_be_requested_by_gate": True,
        "order_mutation_must_not_be_requested_by_gate": True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_connection_gate_side_effects(rules)
    return rules


def build_network_broker_call_approval_gate_requirements() -> dict[str, Any]:
    requirements = {
        "schema": "AIOS_OANDA_DEMO_CONNECTION_NETWORK_BROKER_CALL_GATE.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "human_owner_gate_approval_required": True,
        "network_broker_call_gate_approval_required": True,
        "connection_attempt_packet_required_later": True,
        "approval_scope_required": APPROVAL_SCOPE,
        "gate_mode_required": GATE_MODE,
        "approved_gate_permits_connection_readiness_only": True,
        "approved_gate_does_not_permit_connection_attempt": True,
        "approved_gate_does_not_permit_account_access": True,
        "approved_gate_does_not_permit_order_routing": True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_connection_gate_side_effects(requirements)
    return requirements


def build_timeout_and_stop_controls() -> dict[str, Any]:
    controls = {
        "schema": "AIOS_OANDA_DEMO_CONNECTION_TIMEOUT_STOP_CONTROLS.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "one_shot_only_required": True,
        "retry_loop_allowed": False,
        "timeout_required": True,
        "timeout_min_seconds": MIN_TIMEOUT_SECONDS,
        "timeout_max_seconds": MAX_TIMEOUT_SECONDS,
        "stop_on_success_or_failure_required": True,
        "automatic_hard_stop_after_result_required": True,
        "manual_packet_stop_point_required": True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_connection_gate_side_effects(controls)
    return controls


def build_oanda_demo_connection_gate_contract_set() -> dict[str, Any]:
    contract_set = {
        "schema": "AIOS_OANDA_DEMO_CONNECTION_GATE_CONTRACT_SET.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "connection_gate_contract": build_oanda_demo_connection_gate_contract(),
        "runtime_auth_boundary_requirements": build_runtime_auth_boundary_requirements(),
        "sanitized_connection_evidence_schema": build_sanitized_connection_evidence_schema(),
        "no_order_no_account_logging_rules": build_no_order_no_account_logging_rules(),
        "network_broker_call_approval_gate_requirements": (
            build_network_broker_call_approval_gate_requirements()
        ),
        "timeout_and_stop_controls": build_timeout_and_stop_controls(),
        "contracts_ready_for_future_connection_packet_review": True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_connection_gate_side_effects(contract_set)
    return contract_set


def build_example_oanda_demo_connection_gate_approval() -> dict[str, Any]:
    return asdict(OandaDemoConnectionGateApproval())


def evaluate_oanda_demo_connection_gate(
    approval: OandaDemoConnectionGateApproval | dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = _approval_payload(approval)
    forbidden_fields = _forbidden_field_paths(payload)
    credential_like_values = _credential_like_value_paths(payload)
    unauthorized_fields = _unauthorized_true_field_paths(payload)
    blockers = _gate_blockers(
        payload,
        forbidden_fields=forbidden_fields,
        credential_like_values=credential_like_values,
        unauthorized_fields=unauthorized_fields,
    )
    status = GATE_BLOCKED if blockers else GATE_READY
    classification = "FAIL_CLOSED" if blockers else GATE_READY
    result = {
        "schema": "AIOS_OANDA_DEMO_CONNECTION_GATE_RESULT.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": status,
        "classification": classification,
        "connection_readiness_gate_ready": not blockers,
        "connection_readiness_only": True,
        "future_connection_packet_ready_for_human_review": not blockers,
        "connection_attempt_allowed_now": False,
        "connection_attempt_performed": False,
        "approval_scope_required": APPROVAL_SCOPE,
        "gate_mode_required": GATE_MODE,
        "approval_scope": str(payload.get("approval_scope") or ""),
        "gate_mode": str(payload.get("gate_mode") or ""),
        "account_mode": str(payload.get("account_mode") or "").upper(),
        "environment": str(payload.get("environment") or "").upper(),
        "endpoint_classification": str(payload.get("endpoint_classification") or "").upper(),
        "runtime_auth_boundary_confirmed": payload.get("runtime_auth_boundary_confirmed") is True,
        "runtime_auth_proof_present": payload.get("runtime_auth_proof_present") is True,
        "repo_storage_confirmed_absent": payload.get("repo_storage_confirmed_absent") is True,
        "account_identifier_present": payload.get("account_identifier_present") is True,
        "network_broker_call_gate_approved": payload.get("network_broker_call_gate_approved") is True,
        "one_shot_only": payload.get("one_shot_only") is True,
        "timeout_seconds": _int_or_none(payload.get("timeout_seconds")),
        "stop_on_success_or_failure": payload.get("stop_on_success_or_failure") is True,
        "no_order_route_confirmed": payload.get("no_order_route_confirmed") is True,
        "no_account_id_logging_confirmed": payload.get("no_account_id_logging_confirmed") is True,
        "audit_logging_acknowledged": payload.get("audit_logging_acknowledged") is True,
        "forbidden_fields_detected": forbidden_fields,
        "credential_like_value_paths_detected": credential_like_values,
        "unauthorized_execution_fields_detected": unauthorized_fields,
        "blockers": blockers,
        "contract_set": build_oanda_demo_connection_gate_contract_set(),
        "evidence_schema": build_sanitized_connection_evidence_schema(),
        "audit_event": _build_connection_audit_event(
            status=status,
            classification=classification,
            blockers=blockers,
            forbidden_fields=forbidden_fields,
            credential_like_values=credential_like_values,
            unauthorized_fields=unauthorized_fields,
            timeout_seconds=_int_or_none(payload.get("timeout_seconds")),
            one_shot_only=payload.get("one_shot_only") is True,
        ),
        "fail_closed": bool(blockers),
        "next_safe_action": _next_safe_action(blockers),
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_connection_gate_side_effects(result)
    return result


def summarize_oanda_demo_connection_gate(result: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(result or evaluate_oanda_demo_connection_gate())
    summary = {
        "schema": "AIOS_OANDA_DEMO_CONNECTION_GATE_SUMMARY.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": str(payload.get("status") or GATE_BLOCKED),
        "classification": classify_oanda_demo_connection_gate(payload),
        "connection_readiness_gate_ready": payload.get("connection_readiness_gate_ready") is True,
        "connection_readiness_only": True,
        "future_connection_packet_ready_for_human_review": (
            payload.get("future_connection_packet_ready_for_human_review") is True
        ),
        "connection_attempt_allowed_now": False,
        "connection_attempt_performed": False,
        "runtime_auth_proof_present": payload.get("runtime_auth_proof_present") is True,
        "network_broker_call_gate_approved": payload.get("network_broker_call_gate_approved") is True,
        "one_shot_only": payload.get("one_shot_only") is True,
        "timeout_seconds": payload.get("timeout_seconds"),
        "blockers": list(payload.get("blockers") or []),
        "sanitized_audit_event_recorded": isinstance(payload.get("audit_event"), dict),
        "contains_real_credentials": False,
        "contains_account_identifier": False,
        "repo_stored_auth_material_present": False,
        "next_safe_action": str(payload.get("next_safe_action") or _next_safe_action(payload.get("blockers") or [])),
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_connection_gate_side_effects(summary)
    return summary


def classify_oanda_demo_connection_gate(result: dict[str, Any] | None = None) -> str:
    payload = dict(result or evaluate_oanda_demo_connection_gate())
    if list(payload.get("blockers") or []):
        return "FAIL_CLOSED"
    if payload.get("connection_readiness_gate_ready") is True:
        return GATE_READY
    return "FAIL_CLOSED"


def assert_no_oanda_demo_connection_gate_side_effects(payload: dict[str, Any]) -> bool:
    if _has_unsafe_capability(payload):
        raise ValueError("OANDA demo connection gate must not enable broker, network, order, or live side effects")
    schemas.assert_no_live_permissions(payload)
    return True


def _gate_blockers(
    payload: dict[str, Any],
    *,
    forbidden_fields: list[str],
    credential_like_values: list[str],
    unauthorized_fields: list[str],
) -> list[str]:
    blockers: list[str] = []
    for field_name in REQUIRED_GATE_FIELDS:
        if not _field_present(payload, field_name):
            blockers.append(f"missing_required_field:{field_name}")

    broker_id = str(payload.get("broker_id") or "").upper()
    account_mode = str(payload.get("account_mode") or "").upper()
    environment = str(payload.get("environment") or "").upper()
    endpoint = str(payload.get("endpoint_classification") or "").upper()
    timeout_seconds = _int_or_none(payload.get("timeout_seconds"))

    if broker_id and broker_id != BROKER_ID:
        blockers.append("unsupported_broker_target")
    if account_mode and account_mode not in SUPPORTED_ACCOUNT_MODES:
        blockers.append("unsupported_account_type")
    if environment and environment not in SUPPORTED_ENVIRONMENTS:
        blockers.append("unsupported_environment")
    if endpoint and endpoint not in SUPPORTED_ENDPOINT_CLASSIFICATIONS:
        blockers.append("unsupported_endpoint_classification")
    if "LIVE" in account_mode or "LIVE" in environment:
        blockers.append("live_account_attempt_blocked")
    if "LIVE" in endpoint or payload.get("live_endpoint_requested") is True:
        blockers.append("live_endpoint_blocked")
    if payload.get("external_auth_reference_present") is not True:
        blockers.append("missing_external_auth_reference")
    if str(payload.get("external_auth_reference_format") or "") != AUTH_REFERENCE_FORMAT:
        blockers.append("malformed_external_auth_reference")
    if str(payload.get("auth_material_location") or "") != AUTH_MATERIAL_LOCATION:
        blockers.append("malformed_auth_material_location")
    if payload.get("runtime_auth_boundary_confirmed") is not True:
        blockers.append("runtime_auth_boundary_confirmation_required")
    if payload.get("runtime_auth_proof_present") is not True:
        blockers.append("runtime_auth_proof_required")
    if payload.get("repo_storage_confirmed_absent") is not True:
        blockers.append("repo_auth_material_must_be_absent")
    if payload.get("account_identifier_present") is True:
        blockers.append("account_identifier_not_allowed")
    if payload.get("human_owner_connection_gate_approved") is not True:
        blockers.append("human_owner_connection_gate_approval_required")
    if payload.get("network_broker_call_gate_approved") is not True:
        blockers.append("network_broker_call_gate_approval_required")
    if payload.get("one_shot_only") is not True:
        blockers.append("one_shot_only_required")
    if timeout_seconds is None:
        blockers.append("timeout_seconds_required")
    elif not MIN_TIMEOUT_SECONDS <= timeout_seconds <= MAX_TIMEOUT_SECONDS:
        blockers.append("timeout_seconds_out_of_bounds")
    if payload.get("stop_on_success_or_failure") is not True:
        blockers.append("stop_on_success_or_failure_required")
    if payload.get("no_order_route_confirmed") is not True:
        blockers.append("no_order_route_confirmation_required")
    if payload.get("no_account_id_logging_confirmed") is not True:
        blockers.append("no_account_id_logging_confirmation_required")
    if payload.get("audit_logging_acknowledged") is not True:
        blockers.append("audit_logging_acknowledgement_required")
    if payload.get("approval_scope") != APPROVAL_SCOPE:
        blockers.append(f"approval_scope_must_equal:{APPROVAL_SCOPE}")
    if payload.get("gate_mode") != GATE_MODE:
        blockers.append(f"gate_mode_must_equal:{GATE_MODE}")
    if payload.get("order_route_requested") is True or payload.get("would_place_order") is True:
        blockers.append("order_route_attempt_blocked")

    if forbidden_fields:
        blockers.append("forbidden_sensitive_field_detected")
        blockers.extend([f"forbidden_field:{field}" for field in forbidden_fields])
    if credential_like_values:
        blockers.append("credential_like_value_detected")
        blockers.extend([f"credential_like_value:{field}" for field in credential_like_values])
    if unauthorized_fields:
        blockers.append("unauthorized_execution_attempt")
        blockers.extend([f"unauthorized_execution_field:{field}" for field in unauthorized_fields])
    return _unique(blockers)


def _build_connection_audit_event(
    *,
    status: str,
    classification: str,
    blockers: list[str],
    forbidden_fields: list[str],
    credential_like_values: list[str],
    unauthorized_fields: list[str],
    timeout_seconds: int | None,
    one_shot_only: bool,
) -> dict[str, Any]:
    event = {
        "schema": "AIOS_OANDA_DEMO_CONNECTION_GATE_AUDIT_EVENT.v1",
        "event": "oanda_demo_connection_gate_evaluated",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": status,
        "classification": classification,
        "connection_readiness_gate_ready": not blockers,
        "connection_readiness_only": True,
        "future_connection_packet_ready_for_human_review": not blockers,
        "blockers": list(blockers),
        "forbidden_fields_detected": list(forbidden_fields),
        "credential_like_value_paths_detected": list(credential_like_values),
        "unauthorized_execution_fields_detected": list(unauthorized_fields),
        "timeout_seconds": timeout_seconds,
        "one_shot_only": one_shot_only,
        "sanitized": True,
        "contains_private_data": False,
        "contains_real_credentials": False,
        "contains_account_identifier": False,
        "credential_values_recorded": False,
        "account_identifiers_recorded": False,
        "broker_payloads_recorded": False,
        "repo_stored_auth_material_present": False,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_connection_gate_side_effects(event)
    return event


def _next_safe_action(blockers: list[str]) -> str:
    if blockers:
        return (
            "Keep the OANDA demo connection path fail-closed until the gate metadata is "
            "complete, sanitized, runtime-only, one-shot, and explicitly approved."
        )
    return (
        "Connection gate is ready for future protected packet review only; no broker "
        "connection, account access, order routing, or live execution is authorized."
    )


def _blocked_capabilities() -> dict[str, Any]:
    return {
        "broker_connection_allowed": False,
        "connection_attempt_allowed": False,
        "connection_attempt_allowed_now": False,
        "connection_attempt_performed": False,
        "broker_sdk_allowed": False,
        "network_allowed": False,
        "network_api_allowed": False,
        "env_secret_read_allowed": False,
        "credentials_allowed": False,
        "credentials_used": False,
        "credential_material_present": False,
        "repo_stored_auth_material_present": False,
        "auth_material_persisted": False,
        "broker_request_allowed": False,
        "broker_request_sent": False,
        "account_access_allowed": False,
        "account_mutation_allowed": False,
        "order_route_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_endpoint_allowed": False,
        "live_orders_allowed": False,
        "live_execution_allowed": False,
        "live_account_access_allowed": False,
        "real_money_routing_allowed": False,
        "would_place_order": False,
        "order_placed": False,
        "execution_allowed": False,
        "network_used": False,
        "live_ready": False,
        "live_trade_ready": False,
        "real_order_ready": False,
    }


def _has_unsafe_capability(value: Any) -> bool:
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized_key = _normalize_key(str(key))
            if normalized_key in UNAUTHORIZED_TRUE_FIELDS and nested is True:
                return True
            if _has_unsafe_capability(nested):
                return True
    elif isinstance(value, list):
        return any(_has_unsafe_capability(item) for item in value)
    return False


def _approval_payload(approval: OandaDemoConnectionGateApproval | dict[str, Any] | None) -> dict[str, Any]:
    if approval is None:
        return {}
    if isinstance(approval, OandaDemoConnectionGateApproval):
        return asdict(approval)
    return dict(approval)


def _forbidden_field_paths(value: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            normalized = _normalize_key(key_text)
            if normalized in FORBIDDEN_GATE_FIELD_NAMES:
                paths.append(path)
            paths.extend(_forbidden_field_paths(nested, path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            paths.extend(_forbidden_field_paths(nested, f"{prefix}[{index}]"))
    return _unique(paths)


def _credential_like_value_paths(value: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            paths.extend(_credential_like_value_paths(nested, path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            paths.extend(_credential_like_value_paths(nested, f"{prefix}[{index}]"))
    elif isinstance(value, str):
        lowered = value.strip().lower()
        if any(marker in lowered for marker in FORBIDDEN_VALUE_MARKERS):
            paths.append(prefix)
    return _unique(paths)


def _unauthorized_true_field_paths(value: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            normalized = _normalize_key(key_text)
            if normalized in UNAUTHORIZED_TRUE_FIELDS and nested is True:
                paths.append(path)
            paths.extend(_unauthorized_true_field_paths(nested, path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            paths.extend(_unauthorized_true_field_paths(nested, f"{prefix}[{index}]"))
    return _unique(paths)


def _field_present(fields: dict[str, Any], field_name: str) -> bool:
    return field_name in fields and fields[field_name] not in (None, "", [], {})


def _int_or_none(value: Any) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
