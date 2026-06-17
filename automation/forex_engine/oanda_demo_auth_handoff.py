from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from automation.forex_engine import oanda_demo_runtime_handoff
from automation.forex_engine import schema_contracts as schemas


BROKER_ID = "OANDA"
BROKER_REFERENCE = "OANDA_DEMO_AUTH_HANDOFF_REFERENCE_ONLY"
AUTH_HANDOFF_READY = "OANDA_DEMO_AUTH_HANDOFF_READY"
AUTH_HANDOFF_BLOCKED = "OANDA_DEMO_AUTH_HANDOFF_BLOCKED"
SUPPORTED_DEMO_ACCOUNT_MODES = {"PRACTICE_DEMO", "PAPER_DEMO"}
SUPPORTED_ENVIRONMENTS = {"OANDA_PRACTICE_DEMO", "PRACTICE_REFERENCE_ONLY"}
AUTH_REFERENCE_FORMAT = "SANITIZED_REFERENCE_ONLY"
AUTH_MATERIAL_LOCATION = "EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY"
APPROVED_HANDOFF_SCOPE = "oanda_demo_auth_handoff_readiness_only"
APPROVED_HANDOFF_MODE = "READINESS_ONLY"
FAILURE_STATES = (
    "MISSING_CREDENTIALS",
    "MALFORMED_CREDENTIALS",
    "UNSUPPORTED_ACCOUNT_TYPE",
    "LIVE_ACCOUNT_ATTEMPT",
    "UNAUTHORIZED_EXECUTION_ATTEMPT",
)

FORBIDDEN_AUTH_FIELD_NAMES = {
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
    "live_account_id",
    "broker_order_id",
    "transaction_id",
    "live_payload",
    "raw_live_payload",
}

UNAUTHORIZED_TRUE_FIELDS = {
    "broker_sdk_allowed",
    "network_allowed",
    "network_api_allowed",
    "env_secret_read_allowed",
    "credentials_allowed",
    "credentials_used",
    "credential_material_present",
    "repo_stored_auth_material_present",
    "repo_auth_material_present",
    "auth_material_persisted",
    "broker_request_allowed",
    "broker_request_requested",
    "broker_request_sent",
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
    "network_probe_requested",
}

REQUIRED_HANDOFF_FIELDS = (
    "broker_id",
    "account_mode",
    "environment",
    "external_auth_reference_present",
    "external_auth_reference_format",
    "auth_material_location",
    "external_auth_boundary_confirmed",
    "repo_storage_confirmed_absent",
    "account_identifier_present",
    "audit_logging_acknowledged",
    "handoff_scope",
    "handoff_mode",
    "human_owner_demo_auth_handoff_approved",
)


@dataclass(frozen=True)
class OandaDemoAuthHandoff:
    broker_id: str = BROKER_ID
    account_mode: str = "PRACTICE_DEMO"
    environment: str = "OANDA_PRACTICE_DEMO"
    external_auth_reference_present: bool = True
    external_auth_reference_format: str = AUTH_REFERENCE_FORMAT
    auth_material_location: str = AUTH_MATERIAL_LOCATION
    external_auth_boundary_confirmed: bool = True
    repo_storage_confirmed_absent: bool = True
    account_identifier_present: bool = False
    audit_logging_acknowledged: bool = True
    handoff_scope: str = APPROVED_HANDOFF_SCOPE
    handoff_mode: str = APPROVED_HANDOFF_MODE
    human_owner_demo_auth_handoff_approved: bool = True
    broker_request_requested: bool = False
    execution_requested: bool = False
    network_probe_requested: bool = False


def build_external_auth_handoff_contract() -> dict[str, Any]:
    contract = {
        "schema": "AIOS_OANDA_DEMO_EXTERNAL_AUTH_HANDOFF_CONTRACT.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "mode": "OANDA_DEMO_AUTH_HANDOFF_READINESS",
        "purpose": "Accept sanitized external demo-auth readiness metadata only.",
        "required_handoff_fields": list(REQUIRED_HANDOFF_FIELDS),
        "accepted_auth_reference_format": AUTH_REFERENCE_FORMAT,
        "accepted_auth_material_location": AUTH_MATERIAL_LOCATION,
        "supported_account_modes": sorted(SUPPORTED_DEMO_ACCOUNT_MODES),
        "supported_environments": sorted(SUPPORTED_ENVIRONMENTS),
        "external_auth_required_for_future_handoff": True,
        "repo_stored_auth_material_allowed": False,
        "account_identifier_allowed": False,
        "audit_evidence_required": True,
        "fail_closed_default": True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_auth_side_effects(contract)
    return contract


def build_credential_boundary_contract() -> dict[str, Any]:
    contract = {
        "schema": "AIOS_OANDA_DEMO_CREDENTIAL_BOUNDARY_CONTRACT.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "boundary": "EXTERNAL_AUTH_MATERIAL_NEVER_STORED_IN_REPO",
        "repo_stored_auth_material_allowed": False,
        "repo_stored_auth_material_present": False,
        "credential_material_must_remain_external": True,
        "credential_values_may_be_logged": False,
        "account_identifiers_may_be_logged": False,
        "env_reads_allowed": False,
        "file_reads_for_auth_allowed": False,
        "file_writes_for_auth_allowed": False,
        "forbidden_auth_field_names": sorted(FORBIDDEN_AUTH_FIELD_NAMES),
        "malformed_auth_material_fails_closed": True,
        "missing_auth_material_fails_closed": True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_auth_side_effects(contract)
    return contract


def build_demo_account_validation_contract() -> dict[str, Any]:
    contract = {
        "schema": "AIOS_OANDA_DEMO_ACCOUNT_VALIDATION_CONTRACT.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "supported_account_modes": sorted(SUPPORTED_DEMO_ACCOUNT_MODES),
        "supported_environments": sorted(SUPPORTED_ENVIRONMENTS),
        "live_account_modes_blocked": True,
        "unsupported_account_modes_fail_closed": True,
        "account_identifier_allowed": False,
        "live_account_access_allowed": False,
        "real_money_routing_allowed": False,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_auth_side_effects(contract)
    return contract


def build_auth_evidence_requirements() -> dict[str, Any]:
    requirements = {
        "schema": "AIOS_OANDA_DEMO_AUTH_EVIDENCE_REQUIREMENTS.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "required_evidence": [
            "external_auth_handoff_contract",
            "credential_boundary_contract",
            "demo_account_validation_contract",
            "auth_readiness_validation_result",
            "auth_failure_state",
            "sanitized_auth_audit_event",
        ],
        "evidence_storage": "IN_MEMORY_SANITIZED_EVIDENCE_ONLY",
        "sanitized": True,
        "contains_private_data": False,
        "contains_real_credentials": False,
        "contains_account_identifier": False,
        "repo_stored_auth_material_present": False,
        "audit_log_required": True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_auth_side_effects(requirements)
    return requirements


def build_auth_audit_logging_requirements() -> dict[str, Any]:
    requirements = {
        "schema": "AIOS_OANDA_DEMO_AUTH_AUDIT_LOGGING_REQUIREMENTS.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "audit_event_required": True,
        "audit_event_storage": "IN_MEMORY_SANITIZED_EVIDENCE_ONLY",
        "allowed_audit_fields": [
            "schema",
            "event",
            "broker_id",
            "status",
            "classification",
            "failure_states",
            "blockers",
            "forbidden_fields_detected",
            "sanitized",
        ],
        "forbidden_audit_material": [
            "auth material values",
            "account identifiers",
            "broker request payloads",
            "live response payloads",
        ],
        "credential_values_recorded": False,
        "account_identifiers_recorded": False,
        "broker_payloads_recorded": False,
        "sanitized": True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_auth_side_effects(requirements)
    return requirements


def build_oanda_demo_auth_contract_set() -> dict[str, Any]:
    contract_set = {
        "schema": "AIOS_OANDA_DEMO_AUTH_CONTRACT_SET.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "external_auth_handoff_contract": build_external_auth_handoff_contract(),
        "credential_boundary_contract": build_credential_boundary_contract(),
        "demo_account_validation_contract": build_demo_account_validation_contract(),
        "runtime_handoff_contract_set": (
            oanda_demo_runtime_handoff.build_oanda_demo_runtime_handoff_contract_set()
        ),
        "evidence_requirements": build_auth_evidence_requirements(),
        "audit_logging_requirements": build_auth_audit_logging_requirements(),
        "contracts_ready_for_future_external_handoff": True,
        "runtime_handoff_required_before_connection_probe": True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_auth_side_effects(contract_set)
    return contract_set


def build_example_sanitized_demo_auth_handoff() -> dict[str, Any]:
    return asdict(OandaDemoAuthHandoff())


def validate_demo_account_boundary(
    handoff: OandaDemoAuthHandoff | dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = _handoff_payload(handoff)
    account_mode = str(payload.get("account_mode") or "").upper()
    environment = str(payload.get("environment") or "").upper()
    blockers: list[str] = []

    if not account_mode:
        blockers.append("missing_account_mode")
    elif account_mode not in SUPPORTED_DEMO_ACCOUNT_MODES:
        blockers.append("unsupported_account_type")
    if not environment:
        blockers.append("missing_environment")
    elif environment not in SUPPORTED_ENVIRONMENTS:
        blockers.append("unsupported_environment")
    if "LIVE" in account_mode or "LIVE" in environment or payload.get("live_account_attempted") is True:
        blockers.append("live_account_attempt_blocked")
    if payload.get("account_identifier_present") is True:
        blockers.append("account_identifier_not_allowed")

    result = {
        "schema": "AIOS_OANDA_DEMO_ACCOUNT_VALIDATION_RESULT.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "account_mode": account_mode,
        "environment": environment,
        "account_validation_passed": not blockers,
        "blockers": _unique(blockers),
        "account_identifier_present": payload.get("account_identifier_present") is True,
        "account_identifier_allowed": False,
        "live_account_attempted": payload.get("live_account_attempted") is True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_auth_side_effects(result)
    return result


def evaluate_oanda_demo_auth_handoff_readiness(
    handoff: OandaDemoAuthHandoff | dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = _handoff_payload(handoff)
    account_validation = validate_demo_account_boundary(payload)
    forbidden_fields = _forbidden_auth_field_paths(payload)
    unauthorized_fields = _unauthorized_true_field_paths(payload)
    blockers = _auth_readiness_blockers(payload, account_validation, forbidden_fields, unauthorized_fields)
    failure_states = _failure_states_from_blockers(blockers)
    status = AUTH_HANDOFF_BLOCKED if blockers else AUTH_HANDOFF_READY
    classification = "FAIL_CLOSED" if blockers else AUTH_HANDOFF_READY
    audit_event = _build_audit_event(
        status=status,
        classification=classification,
        blockers=blockers,
        forbidden_fields=forbidden_fields,
        unauthorized_fields=unauthorized_fields,
        failure_states=failure_states,
    )
    result = {
        "schema": "AIOS_OANDA_DEMO_AUTH_HANDOFF_READINESS_RESULT.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": status,
        "classification": classification,
        "auth_handoff_ready": not blockers,
        "authentication_readiness_passed": not blockers,
        "credential_boundary_passed": not forbidden_fields
        and not unauthorized_fields
        and payload.get("repo_storage_confirmed_absent") is True,
        "account_validation_passed": account_validation["account_validation_passed"],
        "external_auth_reference_present": payload.get("external_auth_reference_present") is True,
        "external_auth_reference_format": str(payload.get("external_auth_reference_format") or ""),
        "auth_material_location": str(payload.get("auth_material_location") or ""),
        "forbidden_fields_detected": forbidden_fields,
        "unauthorized_execution_fields_detected": unauthorized_fields,
        "failure_states": failure_states,
        "failure_states_evaluated": list(FAILURE_STATES),
        "blockers": blockers,
        "account_validation": account_validation,
        "audit_event": audit_event,
        "evidence_requirements": build_auth_evidence_requirements(),
        "audit_logging_requirements": build_auth_audit_logging_requirements(),
        "runtime_handoff_required_before_connection_probe": True,
        "runtime_handoff_contract_set": (
            oanda_demo_runtime_handoff.build_oanda_demo_runtime_handoff_contract_set()
        ),
        "repo_stored_auth_material_present": False,
        "credential_material_present": False,
        "auth_material_persisted": False,
        "contains_private_data": False,
        "contains_real_credentials": False,
        "contains_account_identifier": False,
        "fail_closed": bool(blockers),
        "next_safe_action": _next_safe_action(blockers),
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_auth_side_effects(result)
    return result


def summarize_oanda_demo_auth_handoff_readiness(
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(result or evaluate_oanda_demo_auth_handoff_readiness())
    summary = {
        "schema": "AIOS_OANDA_DEMO_AUTH_HANDOFF_READINESS_SUMMARY.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": str(payload.get("status") or AUTH_HANDOFF_BLOCKED),
        "classification": str(payload.get("classification") or "FAIL_CLOSED"),
        "auth_handoff_ready": payload.get("auth_handoff_ready") is True,
        "authentication_readiness_passed": payload.get("authentication_readiness_passed") is True,
        "credential_boundary_passed": payload.get("credential_boundary_passed") is True,
        "account_validation_passed": payload.get("account_validation_passed") is True,
        "failure_states": list(payload.get("failure_states") or []),
        "blockers": list(payload.get("blockers") or []),
        "sanitized_audit_event_recorded": isinstance(payload.get("audit_event"), dict),
        "contains_real_credentials": False,
        "contains_account_identifier": False,
        "repo_stored_auth_material_present": False,
        "next_safe_action": str(payload.get("next_safe_action") or _next_safe_action(payload.get("blockers") or [])),
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_auth_side_effects(summary)
    return summary


def classify_oanda_demo_auth_handoff_readiness(result: dict[str, Any] | None = None) -> str:
    payload = dict(result or evaluate_oanda_demo_auth_handoff_readiness())
    if list(payload.get("blockers") or []):
        return "FAIL_CLOSED"
    if payload.get("auth_handoff_ready") is True:
        return AUTH_HANDOFF_READY
    return "FAIL_CLOSED"


def assert_no_oanda_demo_auth_side_effects(payload: dict[str, Any]) -> bool:
    if _has_unsafe_capability(payload):
        raise ValueError("OANDA demo auth handoff readiness must not enable broker or live side effects")
    schemas.assert_no_live_permissions(payload)
    return True


def _auth_readiness_blockers(
    payload: dict[str, Any],
    account_validation: dict[str, Any],
    forbidden_fields: list[str],
    unauthorized_fields: list[str],
) -> list[str]:
    blockers: list[str] = []
    for field_name in REQUIRED_HANDOFF_FIELDS:
        if not _field_present(payload, field_name):
            blockers.append(f"missing_required_field:{field_name}")

    broker_id = str(payload.get("broker_id") or "").upper()
    if broker_id and broker_id != BROKER_ID:
        blockers.append("unsupported_broker_target")
    if payload.get("external_auth_reference_present") is not True:
        blockers.append("missing_external_auth_reference")
    if str(payload.get("external_auth_reference_format") or "") != AUTH_REFERENCE_FORMAT:
        blockers.append("malformed_external_auth_reference")
    if str(payload.get("auth_material_location") or "") != AUTH_MATERIAL_LOCATION:
        blockers.append("malformed_auth_material_location")
    if payload.get("external_auth_boundary_confirmed") is not True:
        blockers.append("external_auth_boundary_confirmation_required")
    if payload.get("repo_storage_confirmed_absent") is not True:
        blockers.append("repo_auth_material_must_be_absent")
    if payload.get("audit_logging_acknowledged") is not True:
        blockers.append("audit_logging_acknowledgement_required")
    if payload.get("handoff_scope") != APPROVED_HANDOFF_SCOPE:
        blockers.append(f"handoff_scope_must_equal:{APPROVED_HANDOFF_SCOPE}")
    if payload.get("handoff_mode") != APPROVED_HANDOFF_MODE:
        blockers.append(f"handoff_mode_must_equal:{APPROVED_HANDOFF_MODE}")
    if payload.get("human_owner_demo_auth_handoff_approved") is not True:
        blockers.append("human_owner_demo_auth_handoff_approval_required")
    if forbidden_fields:
        blockers.append("malformed_credential_material")
        blockers.extend([f"forbidden_field:{field}" for field in forbidden_fields])
    if unauthorized_fields:
        blockers.append("unauthorized_execution_attempt")
        blockers.extend([f"unauthorized_execution_field:{field}" for field in unauthorized_fields])
    blockers.extend(account_validation.get("blockers") or [])
    return _unique(blockers)


def _failure_states_from_blockers(blockers: list[str]) -> list[str]:
    states: list[str] = []
    if any("missing_external_auth_reference" in blocker for blocker in blockers):
        states.append("MISSING_CREDENTIALS")
    if any(
        marker in blocker
        for blocker in blockers
        for marker in (
            "malformed_external_auth_reference",
            "malformed_auth_material_location",
            "malformed_credential_material",
            "forbidden_field:",
            "repo_auth_material_must_be_absent",
        )
    ):
        states.append("MALFORMED_CREDENTIALS")
    if any("unsupported_account" in blocker or "unsupported_environment" in blocker for blocker in blockers):
        states.append("UNSUPPORTED_ACCOUNT_TYPE")
    if any("live_account_attempt_blocked" in blocker for blocker in blockers):
        states.append("LIVE_ACCOUNT_ATTEMPT")
    if any("unauthorized_execution" in blocker for blocker in blockers):
        states.append("UNAUTHORIZED_EXECUTION_ATTEMPT")
    return _unique(states)


def _build_audit_event(
    *,
    status: str,
    classification: str,
    blockers: list[str],
    forbidden_fields: list[str],
    unauthorized_fields: list[str],
    failure_states: list[str],
) -> dict[str, Any]:
    event = {
        "schema": "AIOS_OANDA_DEMO_AUTH_AUDIT_EVENT.v1",
        "event": "oanda_demo_auth_handoff_readiness_evaluated",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": status,
        "classification": classification,
        "failure_states": list(failure_states),
        "blockers": list(blockers),
        "forbidden_fields_detected": list(forbidden_fields),
        "unauthorized_execution_fields_detected": list(unauthorized_fields),
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
    assert_no_oanda_demo_auth_side_effects(event)
    return event


def _next_safe_action(blockers: list[str]) -> str:
    if blockers:
        return (
            "Keep OANDA demo auth handoff fail-closed until external sanitized readiness "
            "metadata is provided without credentials, account identifiers, broker requests, "
            "network calls, or execution permissions."
        )
    return (
        "OANDA demo auth handoff metadata is sanitized and ready for review only; "
        "broker connection, account access, order routing, and live execution remain blocked."
    )


def _blocked_capabilities() -> dict[str, Any]:
    return {
        "broker_sdk_allowed": False,
        "network_allowed": False,
        "network_api_allowed": False,
        "env_secret_read_allowed": False,
        "credentials_allowed": False,
        "credentials_used": False,
        "broker_request_allowed": False,
        "broker_request_sent": False,
        "broker_paper_orders_allowed": False,
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


def _handoff_payload(handoff: OandaDemoAuthHandoff | dict[str, Any] | None) -> dict[str, Any]:
    if handoff is None:
        return {}
    if isinstance(handoff, OandaDemoAuthHandoff):
        return asdict(handoff)
    return dict(handoff)


def _forbidden_auth_field_paths(value: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            normalized = _normalize_key(key_text)
            if normalized in FORBIDDEN_AUTH_FIELD_NAMES:
                paths.append(path)
            paths.extend(_forbidden_auth_field_paths(nested, path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            paths.extend(_forbidden_auth_field_paths(nested, f"{prefix}[{index}]"))
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


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
