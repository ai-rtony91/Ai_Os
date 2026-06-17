from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from automation.forex_engine import oanda_demo_runtime_handoff_intake
from automation.forex_engine import schema_contracts as schemas


BROKER_ID = "OANDA"
BROKER_REFERENCE = "OANDA_DEMO_RUNTIME_HANDOFF_REFERENCE_ONLY"
RUNTIME_HANDOFF_READY = "OANDA_DEMO_RUNTIME_HANDOFF_READY"
RUNTIME_HANDOFF_BLOCKED = "OANDA_DEMO_RUNTIME_HANDOFF_BLOCKED"
HANDOFF_SCOPE = "oanda_demo_runtime_handoff_only"
HANDOFF_MODE = "RUNTIME_HANDOFF_VALIDATE_ONLY"
AUTH_REFERENCE_FORMAT = "SANITIZED_REFERENCE_ONLY"
AUTH_MATERIAL_LOCATION = "EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY"
SUPPORTED_ACCOUNT_MODES = {"PRACTICE_DEMO", "PAPER_DEMO"}
SUPPORTED_ENVIRONMENTS = {"OANDA_PRACTICE_DEMO", "PRACTICE_REFERENCE_ONLY"}
SUPPORTED_ENDPOINT_CLASSIFICATIONS = {"OANDA_PRACTICE_DEMO", "PRACTICE_REFERENCE_ONLY"}

REQUIRED_RUNTIME_HANDOFF_FIELDS = (
    "broker_id",
    "account_mode",
    "environment",
    "endpoint_classification",
    "handoff_scope",
    "handoff_mode",
    "runtime_reference_present",
    "runtime_reference_format",
    "auth_material_location",
    "runtime_boundary_confirmed",
    "repo_storage_confirmed_absent",
    "account_identifier_present",
    "credential_value_present",
    "no_account_id_storage_confirmed",
    "no_auth_value_storage_confirmed",
    "audit_logging_acknowledged",
)

FORBIDDEN_RUNTIME_FIELD_NAMES = {
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
    "auth_value",
    "auth_material_value",
    "runtime_auth_value",
    "runtime_auth_reference",
    "account_id",
    "account_number",
    "account_identifier",
    "live_account_id",
    "broker_order_id",
    "transaction_id",
    "live_payload",
    "raw_live_payload",
    "raw_request",
    "raw_response",
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
    "probe_attempt_requested",
    "probe_execution_requested",
    "account_access_allowed",
    "account_access_requested",
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
class OandaDemoRuntimeHandoff:
    broker_id: str = BROKER_ID
    account_mode: str = "PRACTICE_DEMO"
    environment: str = "OANDA_PRACTICE_DEMO"
    endpoint_classification: str = "OANDA_PRACTICE_DEMO"
    handoff_scope: str = HANDOFF_SCOPE
    handoff_mode: str = HANDOFF_MODE
    runtime_reference_present: bool = True
    runtime_reference_format: str = AUTH_REFERENCE_FORMAT
    auth_material_location: str = AUTH_MATERIAL_LOCATION
    runtime_boundary_confirmed: bool = True
    repo_storage_confirmed_absent: bool = True
    account_identifier_present: bool = False
    credential_value_present: bool = False
    no_account_id_storage_confirmed: bool = True
    no_auth_value_storage_confirmed: bool = True
    audit_logging_acknowledged: bool = True


def build_runtime_handoff_contract() -> dict[str, Any]:
    contract = {
        "schema": "AIOS_OANDA_DEMO_RUNTIME_HANDOFF_CONTRACT.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "mode": HANDOFF_MODE,
        "handoff_scope_required": HANDOFF_SCOPE,
        "required_handoff_fields": list(REQUIRED_RUNTIME_HANDOFF_FIELDS),
        "supported_account_modes": sorted(SUPPORTED_ACCOUNT_MODES),
        "supported_environments": sorted(SUPPORTED_ENVIRONMENTS),
        "supported_endpoint_classifications": sorted(SUPPORTED_ENDPOINT_CLASSIFICATIONS),
        "runtime_reference_format_required": AUTH_REFERENCE_FORMAT,
        "auth_material_location_required": AUTH_MATERIAL_LOCATION,
        "runtime_boundary_required": True,
        "repo_storage_allowed": False,
        "auth_values_allowed": False,
        "account_identifiers_allowed": False,
        "sanitized_evidence_required": True,
        "fail_closed_default": True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_runtime_handoff_side_effects(contract)
    return contract


def build_runtime_auth_reference_validation_contract() -> dict[str, Any]:
    contract = {
        "schema": "AIOS_OANDA_DEMO_RUNTIME_AUTH_REFERENCE_VALIDATION.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "runtime_reference_value_accepted": False,
        "runtime_reference_presence_flag_required": True,
        "runtime_reference_format_required": AUTH_REFERENCE_FORMAT,
        "auth_material_location_required": AUTH_MATERIAL_LOCATION,
        "malformed_runtime_reference_fails_closed": True,
        "missing_runtime_reference_fails_closed": True,
        "forbidden_runtime_field_names": sorted(FORBIDDEN_RUNTIME_FIELD_NAMES),
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_runtime_handoff_side_effects(contract)
    return contract


def build_runtime_boundary_enforcement_contract() -> dict[str, Any]:
    contract = {
        "schema": "AIOS_OANDA_DEMO_RUNTIME_BOUNDARY_ENFORCEMENT.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "boundary": "AUTH_MATERIAL_REMAINS_EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY",
        "repo_storage_allowed": False,
        "repo_storage_confirmed_absent_required": True,
        "env_reads_allowed": False,
        "file_reads_for_auth_allowed": False,
        "file_writes_for_auth_allowed": False,
        "auth_values_may_be_logged": False,
        "account_identifiers_may_be_logged": False,
        "broker_payloads_may_be_logged": False,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_runtime_handoff_side_effects(contract)
    return contract


def build_runtime_handoff_evidence_schema() -> dict[str, Any]:
    evidence_schema = {
        "schema": "AIOS_OANDA_DEMO_RUNTIME_HANDOFF_EVIDENCE_SCHEMA.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "evidence_storage": "IN_MEMORY_SANITIZED_EVIDENCE_ONLY",
        "allowed_evidence_fields": [
            "schema",
            "event",
            "broker_id",
            "status",
            "classification",
            "runtime_handoff_ready",
            "runtime_boundary_enforced",
            "blockers",
            "forbidden_fields_detected",
            "credential_like_value_paths_detected",
            "unauthorized_execution_fields_detected",
            "sanitized",
        ],
        "forbidden_evidence_material": [
            "auth values",
            "runtime reference values",
            "account identifiers",
            "broker payloads",
            "order payloads",
            "live account data",
            "raw request or response bodies",
        ],
        "sanitized": True,
        "contains_private_data": False,
        "contains_real_credentials": False,
        "contains_account_identifier": False,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_runtime_handoff_side_effects(evidence_schema)
    return evidence_schema


def build_oanda_demo_runtime_handoff_contract_set() -> dict[str, Any]:
    contract_set = {
        "schema": "AIOS_OANDA_DEMO_RUNTIME_HANDOFF_CONTRACT_SET.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "runtime_handoff_intake_contract_set": (
            oanda_demo_runtime_handoff_intake.build_oanda_demo_runtime_handoff_intake_contract_set()
        ),
        "runtime_handoff_intake_required_before_runtime_handoff": True,
        "runtime_handoff_contract": build_runtime_handoff_contract(),
        "runtime_auth_reference_validation_contract": build_runtime_auth_reference_validation_contract(),
        "runtime_boundary_enforcement_contract": build_runtime_boundary_enforcement_contract(),
        "sanitized_handoff_evidence_schema": build_runtime_handoff_evidence_schema(),
        "contracts_ready_for_future_runtime_handoff": True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_runtime_handoff_side_effects(contract_set)
    return contract_set


def build_example_oanda_demo_runtime_handoff() -> dict[str, Any]:
    return asdict(OandaDemoRuntimeHandoff())


def evaluate_oanda_demo_runtime_handoff(
    handoff: OandaDemoRuntimeHandoff | dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = _handoff_payload(handoff)
    forbidden_fields = _forbidden_field_paths(payload)
    credential_like_values = _credential_like_value_paths(payload)
    unauthorized_fields = _unauthorized_true_field_paths(payload)
    runtime_handoff_intake = oanda_demo_runtime_handoff_intake.evaluate_oanda_demo_runtime_handoff_intake(
        _runtime_handoff_intake_payload_from_handoff(payload)
    )
    blockers = _runtime_handoff_blockers(
        payload,
        forbidden_fields=forbidden_fields,
        credential_like_values=credential_like_values,
        unauthorized_fields=unauthorized_fields,
        runtime_handoff_intake=runtime_handoff_intake,
    )
    status = RUNTIME_HANDOFF_BLOCKED if blockers else RUNTIME_HANDOFF_READY
    classification = "FAIL_CLOSED" if blockers else RUNTIME_HANDOFF_READY
    result = {
        "schema": "AIOS_OANDA_DEMO_RUNTIME_HANDOFF_RESULT.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": status,
        "classification": classification,
        "runtime_handoff_ready": not blockers,
        "runtime_boundary_enforced": not blockers,
        "runtime_reference_present": payload.get("runtime_reference_present") is True,
        "runtime_reference_format": str(payload.get("runtime_reference_format") or ""),
        "auth_material_location": str(payload.get("auth_material_location") or ""),
        "runtime_handoff_intake": runtime_handoff_intake,
        "runtime_handoff_intake_ready": runtime_handoff_intake["runtime_handoff_intake_ready"],
        "account_identifier_present": payload.get("account_identifier_present") is True,
        "credential_value_present": payload.get("credential_value_present") is True,
        "forbidden_fields_detected": forbidden_fields,
        "credential_like_value_paths_detected": credential_like_values,
        "unauthorized_execution_fields_detected": unauthorized_fields,
        "blockers": blockers,
        "contract_set": build_oanda_demo_runtime_handoff_contract_set(),
        "evidence_schema": build_runtime_handoff_evidence_schema(),
        "audit_event": _build_runtime_handoff_audit_event(
            status=status,
            classification=classification,
            blockers=blockers,
            forbidden_fields=forbidden_fields,
            credential_like_values=credential_like_values,
            unauthorized_fields=unauthorized_fields,
        ),
        "next_safe_action": _next_safe_action(blockers),
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_runtime_handoff_side_effects(result)
    return result


def summarize_oanda_demo_runtime_handoff(result: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(result or evaluate_oanda_demo_runtime_handoff())
    summary = {
        "schema": "AIOS_OANDA_DEMO_RUNTIME_HANDOFF_SUMMARY.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": str(payload.get("status") or RUNTIME_HANDOFF_BLOCKED),
        "classification": classify_oanda_demo_runtime_handoff(payload),
        "runtime_handoff_ready": payload.get("runtime_handoff_ready") is True,
        "runtime_boundary_enforced": payload.get("runtime_boundary_enforced") is True,
        "runtime_handoff_intake_ready": payload.get("runtime_handoff_intake_ready") is True,
        "runtime_reference_present": payload.get("runtime_reference_present") is True,
        "blockers": list(payload.get("blockers") or []),
        "sanitized_audit_event_recorded": isinstance(payload.get("audit_event"), dict),
        "contains_real_credentials": False,
        "contains_account_identifier": False,
        "repo_stored_auth_material_present": False,
        "next_safe_action": str(payload.get("next_safe_action") or _next_safe_action(payload.get("blockers") or [])),
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_runtime_handoff_side_effects(summary)
    return summary


def classify_oanda_demo_runtime_handoff(result: dict[str, Any] | None = None) -> str:
    payload = dict(result or evaluate_oanda_demo_runtime_handoff())
    if list(payload.get("blockers") or []):
        return "FAIL_CLOSED"
    if payload.get("runtime_handoff_ready") is True:
        return RUNTIME_HANDOFF_READY
    return "FAIL_CLOSED"


def assert_no_oanda_demo_runtime_handoff_side_effects(payload: dict[str, Any]) -> bool:
    if _has_unsafe_capability(payload):
        raise ValueError("OANDA demo runtime handoff must not enable unsafe side effects")
    schemas.assert_no_live_permissions(payload)
    return True


def _runtime_handoff_blockers(
    payload: dict[str, Any],
    *,
    forbidden_fields: list[str],
    credential_like_values: list[str],
    unauthorized_fields: list[str],
    runtime_handoff_intake: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    for field_name in REQUIRED_RUNTIME_HANDOFF_FIELDS:
        if not _field_present(payload, field_name):
            blockers.append(f"missing_required_field:{field_name}")

    broker_id = str(payload.get("broker_id") or "").upper()
    account_mode = str(payload.get("account_mode") or "").upper()
    environment = str(payload.get("environment") or "").upper()
    endpoint = str(payload.get("endpoint_classification") or "").upper()

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
        blockers.append("live_endpoint_reference_blocked")
    if payload.get("handoff_scope") != HANDOFF_SCOPE:
        blockers.append(f"handoff_scope_must_equal:{HANDOFF_SCOPE}")
    if payload.get("handoff_mode") != HANDOFF_MODE:
        blockers.append(f"handoff_mode_must_equal:{HANDOFF_MODE}")
    if payload.get("runtime_reference_present") is not True:
        blockers.append("runtime_reference_required")
    if str(payload.get("runtime_reference_format") or "") != AUTH_REFERENCE_FORMAT:
        blockers.append("malformed_runtime_reference")
    if str(payload.get("auth_material_location") or "") != AUTH_MATERIAL_LOCATION:
        blockers.append("malformed_auth_material_location")
    if payload.get("runtime_boundary_confirmed") is not True:
        blockers.append("runtime_boundary_confirmation_required")
    if payload.get("repo_storage_confirmed_absent") is not True:
        blockers.append("repo_auth_material_must_be_absent")
    if payload.get("account_identifier_present") is True:
        blockers.append("account_identifier_not_allowed")
    if payload.get("credential_value_present") is True:
        blockers.append("credential_value_not_allowed")
    if payload.get("no_account_id_storage_confirmed") is not True:
        blockers.append("no_account_id_storage_confirmation_required")
    if payload.get("no_auth_value_storage_confirmed") is not True:
        blockers.append("no_auth_value_storage_confirmation_required")
    if payload.get("audit_logging_acknowledged") is not True:
        blockers.append("audit_logging_acknowledgement_required")

    if forbidden_fields:
        blockers.append("forbidden_sensitive_field_detected")
        blockers.extend([f"forbidden_field:{field}" for field in forbidden_fields])
    if credential_like_values:
        blockers.append("credential_like_value_detected")
        blockers.extend([f"credential_like_value:{field}" for field in credential_like_values])
    if unauthorized_fields:
        blockers.append("unauthorized_probe_attempt")
        blockers.extend([f"unauthorized_execution_field:{field}" for field in unauthorized_fields])
    if runtime_handoff_intake.get("runtime_handoff_intake_ready") is not True:
        blockers.append("runtime_handoff_intake_required")
        blockers.extend(
            [
                f"runtime_handoff_intake_blocker:{blocker}"
                for blocker in list(runtime_handoff_intake.get("blockers") or [])
            ]
        )
    return _unique(blockers)


def _runtime_handoff_intake_payload_from_handoff(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "broker_id": payload.get("broker_id"),
        "account_mode": payload.get("account_mode"),
        "environment": payload.get("environment"),
        "endpoint_classification": payload.get("endpoint_classification"),
        "intake_scope": oanda_demo_runtime_handoff_intake.INTAKE_SCOPE,
        "intake_mode": oanda_demo_runtime_handoff_intake.INTAKE_MODE,
        "metadata_intake_authorized": payload.get("metadata_intake_authorized", True),
        "runtime_reference_present": payload.get("runtime_reference_present"),
        "runtime_reference_format": payload.get("runtime_reference_format"),
        "auth_material_location": payload.get("auth_material_location"),
        "runtime_boundary_confirmed": payload.get("runtime_boundary_confirmed"),
        "external_operator_controlled_runtime_confirmed": payload.get(
            "external_operator_controlled_runtime_confirmed",
            payload.get("runtime_boundary_confirmed"),
        ),
        "repo_storage_confirmed_absent": payload.get("repo_storage_confirmed_absent"),
        "account_identifier_present": payload.get("account_identifier_present"),
        "credential_value_present": payload.get("credential_value_present"),
        "no_account_id_storage_confirmed": payload.get("no_account_id_storage_confirmed"),
        "no_auth_value_storage_confirmed": payload.get("no_auth_value_storage_confirmed"),
        "audit_logging_acknowledged": payload.get("audit_logging_acknowledged"),
    }


def _build_runtime_handoff_audit_event(
    *,
    status: str,
    classification: str,
    blockers: list[str],
    forbidden_fields: list[str],
    credential_like_values: list[str],
    unauthorized_fields: list[str],
) -> dict[str, Any]:
    event = {
        "schema": "AIOS_OANDA_DEMO_RUNTIME_HANDOFF_AUDIT_EVENT.v1",
        "event": "oanda_demo_runtime_handoff_validated",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": status,
        "classification": classification,
        "runtime_handoff_ready": not blockers,
        "runtime_boundary_enforced": not blockers,
        "blockers": list(blockers),
        "forbidden_fields_detected": list(forbidden_fields),
        "credential_like_value_paths_detected": list(credential_like_values),
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
    assert_no_oanda_demo_runtime_handoff_side_effects(event)
    return event


def _next_safe_action(blockers: list[str]) -> str:
    if blockers:
        return (
            "Keep runtime handoff fail-closed until sanitized runtime-reference metadata "
            "proves auth values and account identifiers remain outside repo and chat."
        )
    return (
        "Runtime handoff is valid for future protected probe review only; no broker "
        "connection, authentication, account access, or order routing is authorized."
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


def _handoff_payload(handoff: OandaDemoRuntimeHandoff | dict[str, Any] | None) -> dict[str, Any]:
    if handoff is None:
        return {}
    if isinstance(handoff, OandaDemoRuntimeHandoff):
        return asdict(handoff)
    return dict(handoff)


def _forbidden_field_paths(value: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            normalized = _normalize_key(key_text)
            if normalized in FORBIDDEN_RUNTIME_FIELD_NAMES:
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


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
