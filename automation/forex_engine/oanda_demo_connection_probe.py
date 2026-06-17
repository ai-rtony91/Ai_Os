from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from automation.forex_engine import oanda_demo_connection_gate
from automation.forex_engine import oanda_demo_runtime_handoff
from automation.forex_engine import schema_contracts as schemas


BROKER_ID = "OANDA"
BROKER_REFERENCE = "OANDA_DEMO_CONNECTION_PROBE_REFERENCE_ONLY"
PROBE_READY = "OANDA_DEMO_CONNECTION_PROBE_READY"
PROBE_BLOCKED = "OANDA_DEMO_CONNECTION_PROBE_BLOCKED"
PROBE_SCOPE = "oanda_demo_connection_probe_only"
PROBE_MODE = "PROBE_VALIDATE_ONLY"
AUTH_REFERENCE_FORMAT = oanda_demo_connection_gate.AUTH_REFERENCE_FORMAT
AUTH_MATERIAL_LOCATION = oanda_demo_connection_gate.AUTH_MATERIAL_LOCATION
SUPPORTED_ACCOUNT_MODES = oanda_demo_connection_gate.SUPPORTED_ACCOUNT_MODES
SUPPORTED_ENVIRONMENTS = oanda_demo_connection_gate.SUPPORTED_ENVIRONMENTS
SUPPORTED_ENDPOINT_CLASSIFICATIONS = oanda_demo_connection_gate.SUPPORTED_ENDPOINT_CLASSIFICATIONS
MIN_TIMEOUT_SECONDS = oanda_demo_connection_gate.MIN_TIMEOUT_SECONDS
MAX_TIMEOUT_SECONDS = oanda_demo_connection_gate.MAX_TIMEOUT_SECONDS

REQUIRED_PROBE_FIELDS = (
    "broker_id",
    "account_mode",
    "environment",
    "endpoint_classification",
    "probe_scope",
    "probe_mode",
    "demo_probe_approval_flag",
    "network_broker_call_gate_approved",
    "runtime_auth_reference_present",
    "runtime_auth_reference_format",
    "auth_material_location",
    "runtime_auth_boundary_confirmed",
    "repo_storage_confirmed_absent",
    "account_identifier_present",
    "one_shot_only",
    "timeout_seconds",
    "stop_on_success_or_failure",
    "no_order_route_confirmed",
    "no_account_id_logging_confirmed",
    "audit_logging_acknowledged",
)

FORBIDDEN_PROBE_FIELD_NAMES = {
    *oanda_demo_connection_gate.FORBIDDEN_GATE_FIELD_NAMES,
    "auth_value",
    "auth_material_value",
    "runtime_auth_value",
    "runtime_auth_reference",
    "raw_request",
    "raw_response",
    "order_payload",
}

FORBIDDEN_VALUE_MARKERS = oanda_demo_connection_gate.FORBIDDEN_VALUE_MARKERS

UNAUTHORIZED_TRUE_FIELDS = {
    *oanda_demo_connection_gate.UNAUTHORIZED_TRUE_FIELDS,
    "account_access_requested",
    "account_mutation_requested",
    "market_data_requested",
    "order_route_attempted",
    "probe_retry_requested",
    "retry_loop_requested",
}

CLI_FORBIDDEN_ARG_MARKERS = (
    "account-id",
    "account_id",
    "account-number",
    "account_number",
    "api-key",
    "apikey",
    "authorization",
    "bearer",
    "password",
    "private-key",
    "refresh-token",
    "secret",
    "token",
)

CLI_ALLOWED_SAFETY_FLAGS = {
    "--no-account-id-logging-confirmed",
    "--no-order-route-confirmed",
}


@dataclass(frozen=True)
class OandaDemoConnectionProbeRequest:
    broker_id: str = BROKER_ID
    account_mode: str = "PRACTICE_DEMO"
    environment: str = "OANDA_PRACTICE_DEMO"
    endpoint_classification: str = "OANDA_PRACTICE_DEMO"
    probe_scope: str = PROBE_SCOPE
    probe_mode: str = PROBE_MODE
    demo_probe_approval_flag: bool = True
    network_broker_call_gate_approved: bool = True
    runtime_auth_reference_present: bool = True
    runtime_auth_reference_format: str = AUTH_REFERENCE_FORMAT
    auth_material_location: str = AUTH_MATERIAL_LOCATION
    runtime_auth_boundary_confirmed: bool = True
    repo_storage_confirmed_absent: bool = True
    account_identifier_present: bool = False
    one_shot_only: bool = True
    timeout_seconds: int = 10
    stop_on_success_or_failure: bool = True
    no_order_route_confirmed: bool = True
    no_account_id_logging_confirmed: bool = True
    audit_logging_acknowledged: bool = True


def build_oanda_demo_connection_probe_contract() -> dict[str, Any]:
    contract = {
        "schema": "AIOS_OANDA_DEMO_CONNECTION_PROBE_CONTRACT.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "mode": PROBE_MODE,
        "probe_scope_required": PROBE_SCOPE,
        "required_probe_fields": list(REQUIRED_PROBE_FIELDS),
        "supported_account_modes": sorted(SUPPORTED_ACCOUNT_MODES),
        "supported_environments": sorted(SUPPORTED_ENVIRONMENTS),
        "supported_endpoint_classifications": sorted(SUPPORTED_ENDPOINT_CLASSIFICATIONS),
        "runtime_auth_reference_interface": build_runtime_auth_reference_interface(),
        "runtime_handoff_contract_set": (
            oanda_demo_runtime_handoff.build_oanda_demo_runtime_handoff_contract_set()
        ),
        "runtime_handoff_intake_required": True,
        "connection_result_evidence_schema": build_probe_result_evidence_schema(),
        "one_shot_only_required": True,
        "timeout_min_seconds": MIN_TIMEOUT_SECONDS,
        "timeout_max_seconds": MAX_TIMEOUT_SECONDS,
        "probe_command_validate_only": True,
        "future_runtime_connector_required": True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_connection_probe_side_effects(contract)
    return contract


def build_runtime_auth_reference_interface() -> dict[str, Any]:
    interface = {
        "schema": "AIOS_OANDA_DEMO_PROBE_RUNTIME_AUTH_REFERENCE_INTERFACE.v1",
        "accepted_fields": [
            "runtime_auth_reference_present",
            "runtime_auth_reference_format",
            "auth_material_location",
            "runtime_auth_boundary_confirmed",
        ],
        "accepted_reference_format": AUTH_REFERENCE_FORMAT,
        "accepted_auth_material_location": AUTH_MATERIAL_LOCATION,
        "auth_value_accepted": False,
        "auth_value_logged": False,
        "auth_value_persisted": False,
        "account_identifier_accepted": False,
        "account_identifier_logged": False,
        "repo_storage_allowed": False,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_connection_probe_side_effects(interface)
    return interface


def build_probe_result_evidence_schema() -> dict[str, Any]:
    schema = {
        "schema": "AIOS_OANDA_DEMO_CONNECTION_PROBE_RESULT_EVIDENCE_SCHEMA.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "evidence_storage": "IN_MEMORY_SANITIZED_EVIDENCE_ONLY",
        "allowed_outcomes": [
            "PROBE_VALIDATED_NO_CONNECTION",
            "CONNECTED_SANITIZED",
            "AUTH_REJECTED_SANITIZED",
            "TIMEOUT_SANITIZED",
            "NETWORK_ERROR_SANITIZED",
            "BLOCKED_FAIL_CLOSED",
        ],
        "allowed_evidence_fields": [
            "schema",
            "event",
            "broker_id",
            "status",
            "classification",
            "outcome",
            "probe_ready",
            "blockers",
            "timeout_seconds",
            "one_shot_only",
            "stop_after_result",
            "sanitized",
        ],
        "forbidden_evidence_material": [
            "auth values",
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
    assert_no_oanda_demo_connection_probe_side_effects(schema)
    return schema


def build_example_oanda_demo_connection_probe_request() -> dict[str, Any]:
    return asdict(OandaDemoConnectionProbeRequest())


def evaluate_oanda_demo_connection_probe(
    request: OandaDemoConnectionProbeRequest | dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = _request_payload(request)
    forbidden_fields = _forbidden_field_paths(payload)
    credential_like_values = _credential_like_value_paths(payload)
    unauthorized_fields = _unauthorized_true_field_paths(payload)
    runtime_handoff = oanda_demo_runtime_handoff.evaluate_oanda_demo_runtime_handoff(
        _runtime_handoff_payload_from_probe(payload)
    )
    blockers = _probe_blockers(
        payload,
        forbidden_fields=forbidden_fields,
        credential_like_values=credential_like_values,
        unauthorized_fields=unauthorized_fields,
        runtime_handoff=runtime_handoff,
    )
    status = PROBE_BLOCKED if blockers else PROBE_READY
    classification = "FAIL_CLOSED" if blockers else PROBE_READY
    result = {
        "schema": "AIOS_OANDA_DEMO_CONNECTION_PROBE_RESULT.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": status,
        "classification": classification,
        "probe_ready": not blockers,
        "probe_validate_only": True,
        "future_runtime_connector_required": not blockers,
        "connection_attempt_allowed_now": False,
        "connection_attempt_performed": False,
        "connection_result_recorded": False,
        "probe_final_state": "STOPPED_AFTER_VALIDATION",
        "outcome": "BLOCKED_FAIL_CLOSED" if blockers else "PROBE_VALIDATED_NO_CONNECTION",
        "account_mode": str(payload.get("account_mode") or "").upper(),
        "environment": str(payload.get("environment") or "").upper(),
        "endpoint_classification": str(payload.get("endpoint_classification") or "").upper(),
        "runtime_auth_reference_present": payload.get("runtime_auth_reference_present") is True,
        "runtime_auth_reference_format": str(payload.get("runtime_auth_reference_format") or ""),
        "auth_material_location": str(payload.get("auth_material_location") or ""),
        "runtime_handoff": runtime_handoff,
        "runtime_handoff_ready": runtime_handoff["runtime_handoff_ready"],
        "runtime_handoff_intake_ready": runtime_handoff["runtime_handoff_intake_ready"],
        "timeout_seconds": _int_or_none(payload.get("timeout_seconds")),
        "one_shot_only": payload.get("one_shot_only") is True,
        "stop_after_result": payload.get("stop_on_success_or_failure") is True,
        "forbidden_fields_detected": forbidden_fields,
        "credential_like_value_paths_detected": credential_like_values,
        "unauthorized_execution_fields_detected": unauthorized_fields,
        "blockers": blockers,
        "contract": build_oanda_demo_connection_probe_contract(),
        "evidence_schema": build_probe_result_evidence_schema(),
        "audit_event": _build_probe_audit_event(
            status=status,
            classification=classification,
            outcome="BLOCKED_FAIL_CLOSED" if blockers else "PROBE_VALIDATED_NO_CONNECTION",
            blockers=blockers,
            forbidden_fields=forbidden_fields,
            credential_like_values=credential_like_values,
            unauthorized_fields=unauthorized_fields,
            timeout_seconds=_int_or_none(payload.get("timeout_seconds")),
            one_shot_only=payload.get("one_shot_only") is True,
            stop_after_result=payload.get("stop_on_success_or_failure") is True,
        ),
        "next_safe_action": _next_safe_action(blockers),
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_connection_probe_side_effects(result)
    return result


def summarize_oanda_demo_connection_probe(result: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(result or evaluate_oanda_demo_connection_probe())
    summary = {
        "schema": "AIOS_OANDA_DEMO_CONNECTION_PROBE_SUMMARY.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": str(payload.get("status") or PROBE_BLOCKED),
        "classification": classify_oanda_demo_connection_probe(payload),
        "probe_ready": payload.get("probe_ready") is True,
        "probe_validate_only": True,
        "connection_attempt_allowed_now": False,
        "connection_attempt_performed": False,
        "connection_result_recorded": payload.get("connection_result_recorded") is True,
        "outcome": str(payload.get("outcome") or "BLOCKED_FAIL_CLOSED"),
        "timeout_seconds": payload.get("timeout_seconds"),
        "one_shot_only": payload.get("one_shot_only") is True,
        "stop_after_result": payload.get("stop_after_result") is True,
        "blockers": list(payload.get("blockers") or []),
        "sanitized_audit_event_recorded": isinstance(payload.get("audit_event"), dict),
        "contains_real_credentials": False,
        "contains_account_identifier": False,
        "repo_stored_auth_material_present": False,
        "next_safe_action": str(payload.get("next_safe_action") or _next_safe_action(payload.get("blockers") or [])),
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_connection_probe_side_effects(summary)
    return summary


def classify_oanda_demo_connection_probe(result: dict[str, Any] | None = None) -> str:
    payload = dict(result or evaluate_oanda_demo_connection_probe())
    if list(payload.get("blockers") or []):
        return "FAIL_CLOSED"
    if payload.get("probe_ready") is True:
        return PROBE_READY
    return "FAIL_CLOSED"


def scan_probe_cli_args(argv: list[str]) -> list[str]:
    blockers: list[str] = []
    for raw_arg in argv:
        arg = str(raw_arg).strip()
        lowered = arg.lower()
        if lowered in CLI_ALLOWED_SAFETY_FLAGS:
            continue
        if any(marker in lowered for marker in CLI_FORBIDDEN_ARG_MARKERS):
            blockers.append("cli_sensitive_argument_rejected")
        if any(marker in lowered for marker in FORBIDDEN_VALUE_MARKERS):
            blockers.append("cli_credential_like_value_rejected")
        if "live" in lowered:
            blockers.append("cli_live_endpoint_or_account_rejected")
        if "order" in lowered and lowered not in {"--no-order-route-confirmed"}:
            blockers.append("cli_order_route_argument_rejected")
    return _unique(blockers)


def build_blocked_cli_result(blockers: list[str]) -> dict[str, Any]:
    result = {
        "schema": "AIOS_OANDA_DEMO_CONNECTION_PROBE_CLI_REJECTION.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": PROBE_BLOCKED,
        "classification": "FAIL_CLOSED",
        "probe_ready": False,
        "probe_validate_only": True,
        "connection_attempt_allowed_now": False,
        "connection_attempt_performed": False,
        "outcome": "BLOCKED_FAIL_CLOSED",
        "blockers": _unique(blockers),
        "sanitized": True,
        "contains_private_data": False,
        "contains_real_credentials": False,
        "contains_account_identifier": False,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_connection_probe_side_effects(result)
    return result


def assert_no_oanda_demo_connection_probe_side_effects(payload: dict[str, Any]) -> bool:
    if _has_unsafe_capability(payload):
        raise ValueError("OANDA demo connection probe must not enable unsafe side effects")
    schemas.assert_no_live_permissions(payload)
    return True


def _probe_blockers(
    payload: dict[str, Any],
    *,
    forbidden_fields: list[str],
    credential_like_values: list[str],
    unauthorized_fields: list[str],
    runtime_handoff: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    for field_name in REQUIRED_PROBE_FIELDS:
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
    if payload.get("probe_scope") != PROBE_SCOPE:
        blockers.append(f"probe_scope_must_equal:{PROBE_SCOPE}")
    if payload.get("probe_mode") != PROBE_MODE:
        blockers.append(f"probe_mode_must_equal:{PROBE_MODE}")
    if payload.get("demo_probe_approval_flag") is not True:
        blockers.append("demo_probe_approval_flag_required")
    if payload.get("network_broker_call_gate_approved") is not True:
        blockers.append("network_broker_call_gate_approval_required")
    if payload.get("runtime_auth_reference_present") is not True:
        blockers.append("runtime_auth_reference_required")
    if str(payload.get("runtime_auth_reference_format") or "") != AUTH_REFERENCE_FORMAT:
        blockers.append("malformed_runtime_auth_reference_format")
    if str(payload.get("auth_material_location") or "") != AUTH_MATERIAL_LOCATION:
        blockers.append("malformed_auth_material_location")
    if payload.get("runtime_auth_boundary_confirmed") is not True:
        blockers.append("runtime_auth_boundary_confirmation_required")
    if payload.get("repo_storage_confirmed_absent") is not True:
        blockers.append("repo_auth_material_must_be_absent")
    if payload.get("account_identifier_present") is True:
        blockers.append("account_identifier_not_allowed")
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
    if payload.get("order_route_requested") is True or payload.get("order_route_attempted") is True:
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
    if runtime_handoff.get("runtime_handoff_ready") is not True:
        blockers.append("runtime_handoff_required")
        blockers.extend(
            [
                f"runtime_handoff_blocker:{blocker}"
                for blocker in list(runtime_handoff.get("blockers") or [])
            ]
        )
    return _unique(blockers)


def _runtime_handoff_payload_from_probe(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "broker_id": payload.get("broker_id"),
        "account_mode": payload.get("account_mode"),
        "environment": payload.get("environment"),
        "endpoint_classification": payload.get("endpoint_classification"),
        "handoff_scope": oanda_demo_runtime_handoff.HANDOFF_SCOPE,
        "handoff_mode": oanda_demo_runtime_handoff.HANDOFF_MODE,
        "metadata_intake_authorized": payload.get("metadata_intake_authorized", True),
        "runtime_reference_present": payload.get("runtime_auth_reference_present"),
        "runtime_reference_format": payload.get("runtime_auth_reference_format"),
        "auth_material_location": payload.get("auth_material_location"),
        "runtime_boundary_confirmed": payload.get("runtime_auth_boundary_confirmed"),
        "repo_storage_confirmed_absent": payload.get("repo_storage_confirmed_absent"),
        "account_identifier_present": payload.get("account_identifier_present"),
        "credential_value_present": payload.get("credential_value_present", False),
        "no_account_id_storage_confirmed": payload.get("no_account_id_logging_confirmed"),
        "no_auth_value_storage_confirmed": payload.get("no_auth_value_storage_confirmed", True),
        "audit_logging_acknowledged": payload.get("audit_logging_acknowledged"),
    }


def _build_probe_audit_event(
    *,
    status: str,
    classification: str,
    outcome: str,
    blockers: list[str],
    forbidden_fields: list[str],
    credential_like_values: list[str],
    unauthorized_fields: list[str],
    timeout_seconds: int | None,
    one_shot_only: bool,
    stop_after_result: bool,
) -> dict[str, Any]:
    event = {
        "schema": "AIOS_OANDA_DEMO_CONNECTION_PROBE_AUDIT_EVENT.v1",
        "event": "oanda_demo_connection_probe_validated",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": status,
        "classification": classification,
        "outcome": outcome,
        "probe_ready": not blockers,
        "probe_validate_only": True,
        "connection_attempt_allowed_now": False,
        "connection_attempt_performed": False,
        "blockers": list(blockers),
        "forbidden_fields_detected": list(forbidden_fields),
        "credential_like_value_paths_detected": list(credential_like_values),
        "unauthorized_execution_fields_detected": list(unauthorized_fields),
        "timeout_seconds": timeout_seconds,
        "one_shot_only": one_shot_only,
        "stop_after_result": stop_after_result,
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
    assert_no_oanda_demo_connection_probe_side_effects(event)
    return event


def _next_safe_action(blockers: list[str]) -> str:
    if blockers:
        return (
            "Keep the OANDA demo probe fail-closed until sanitized probe metadata is "
            "complete and explicitly approved without auth values, account IDs, or order routing."
        )
    return (
        "Probe path is validated for a future protected runtime connector packet only; "
        "no connection attempt is authorized by this packet."
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


def _request_payload(request: OandaDemoConnectionProbeRequest | dict[str, Any] | None) -> dict[str, Any]:
    if request is None:
        return {}
    if isinstance(request, OandaDemoConnectionProbeRequest):
        return asdict(request)
    return dict(request)


def _forbidden_field_paths(value: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            normalized = _normalize_key(key_text)
            if normalized in FORBIDDEN_PROBE_FIELD_NAMES:
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
