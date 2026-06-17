from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Protocol

from automation.forex_engine import oanda_demo_connection_gate
from automation.forex_engine import oanda_demo_connection_probe
from automation.forex_engine import oanda_demo_runtime_handoff
from automation.forex_engine import oanda_demo_runtime_handoff_intake
from automation.forex_engine import schema_contracts as schemas


BROKER_ID = "OANDA"
BROKER_REFERENCE = "OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_REFERENCE_ONLY"
ATTEMPT_READY = "OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_READY"
ATTEMPT_BLOCKED = "OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_BLOCKED"
ATTEMPT_CONNECTED = "OANDA_DEMO_PROTECTED_CONNECTION_CONNECTED_SANITIZED"
ATTEMPT_FAILED = "OANDA_DEMO_PROTECTED_CONNECTION_FAILED_SANITIZED"
ATTEMPT_SCOPE = "oanda_demo_protected_connection_attempt_only"
ATTEMPT_MODE = "ONE_SHOT_PRACTICE_DEMO_CONNECT_ONLY"
AUTH_REFERENCE_FORMAT = oanda_demo_connection_gate.AUTH_REFERENCE_FORMAT
AUTH_MATERIAL_LOCATION = oanda_demo_connection_gate.AUTH_MATERIAL_LOCATION
SUPPORTED_ACCOUNT_MODES = {"PRACTICE_DEMO"}
SUPPORTED_ENVIRONMENTS = {"OANDA_PRACTICE_DEMO"}
SUPPORTED_ENDPOINT_CLASSIFICATIONS = {"OANDA_PRACTICE_DEMO"}
MIN_TIMEOUT_SECONDS = oanda_demo_connection_gate.MIN_TIMEOUT_SECONDS
MAX_TIMEOUT_SECONDS = oanda_demo_connection_gate.MAX_TIMEOUT_SECONDS

REQUIRED_APPROVAL_FIELDS = (
    "human_owner_protected_demo_connection_approved",
    "approval_scope",
    "connection_attempt_mode",
    "broker_id",
    "account_mode",
    "environment",
    "endpoint_classification",
    "network_broker_call_gate_approved",
    "runtime_handoff_intake_ready",
    "runtime_handoff_ready",
    "connection_gate_ready",
    "one_shot_only",
    "timeout_seconds",
    "stop_on_success_or_failure",
    "no_order_route_confirmed",
    "no_account_id_logging_confirmed",
    "audit_logging_acknowledged",
)

REQUIRED_RUNTIME_BOUNDARY_FIELDS = (
    "runtime_auth_reference_present",
    "runtime_auth_reference_format",
    "auth_material_location",
    "runtime_auth_boundary_confirmed",
    "repo_storage_confirmed_absent",
    "account_identifier_present",
    "credential_value_present",
    "no_account_id_storage_confirmed",
    "no_auth_value_storage_confirmed",
)

FORBIDDEN_ATTEMPT_FIELD_NAMES = {
    *oanda_demo_connection_probe.FORBIDDEN_PROBE_FIELD_NAMES,
    "account",
    "account_id",
    "account_ids",
    "account_identifier",
    "account_number",
    "accounts",
    "api_key",
    "apikey",
    "auth_header",
    "auth_material",
    "auth_material_value",
    "auth_value",
    "authorization",
    "bearer_token",
    "broker_credentials",
    "broker_payload",
    "credential",
    "credentials",
    "headers",
    "http_headers",
    "password",
    "private_key",
    "raw_broker_payload",
    "raw_payload",
    "raw_request",
    "raw_response",
    "refresh_token",
    "request_body",
    "response_body",
    "runtime_auth_reference",
    "runtime_auth_value",
    "secret",
    "token",
}

FORBIDDEN_VALUE_MARKERS = (
    *oanda_demo_connection_probe.FORBIDDEN_VALUE_MARKERS,
    "authorization:",
    "bearer",
    "client_secret",
    "oauth",
    "oanda-",
    "password",
    "private_key",
    "refresh_token",
)

LIVE_REFERENCE_MARKERS = (
    "LIVE",
    "REAL_MONEY",
    "PRODUCTION",
    "FXTRADE",
)

UNAUTHORIZED_TRUE_FIELDS = {
    "account_access_allowed",
    "account_access_requested",
    "account_mutation_allowed",
    "account_state_allowed",
    "account_state_requested",
    "broker_paper_orders_allowed",
    "credentials_allowed",
    "credentials_used",
    "credential_material_present",
    "credential_value_present",
    "env_secret_read_allowed",
    "live_account_access_allowed",
    "live_endpoint_allowed",
    "live_endpoint_requested",
    "live_execution_allowed",
    "live_orders_allowed",
    "market_data_allowed",
    "market_data_requested",
    "market_data_beyond_connection_auth_requested",
    "order_placed",
    "order_route_allowed",
    "order_route_attempted",
    "order_route_requested",
    "paper_order_execution",
    "probe_retry_requested",
    "real_money_routing_allowed",
    "retry_loop_allowed",
    "retry_loop_requested",
    "would_place_order",
}

UNSAFE_CONNECTOR_TRUE_FIELDS = {
    "account_accessed",
    "account_data_returned",
    "account_state_requested",
    "credentials_logged",
    "credential_value_returned",
    "live_endpoint_used",
    "market_data_returned",
    "market_data_requested",
    "order_placed",
    "order_route_attempted",
    "raw_payload_returned",
    "response_body_returned",
    "retry_loop_used",
}

CLI_FORBIDDEN_ARG_MARKERS = (
    "account-id",
    "account_id",
    "account-number",
    "account_number",
    "account-state",
    "account_state",
    "api-key",
    "apikey",
    "authorization",
    "bearer",
    "credential",
    "live",
    "market-data",
    "market_data",
    "order",
    "password",
    "private-key",
    "refresh-token",
    "secret",
    "token",
)

CLI_ALLOWED_SAFETY_FLAGS = {
    "--no-account-id-logging-confirmed",
    "--no-account-id-storage-confirmed",
    "--no-auth-value-storage-confirmed",
    "--no-order-route-confirmed",
    "--stop-on-success-or-failure",
}


class OandaDemoRuntimeConnector(Protocol):
    def attempt_connection(
        self,
        request: dict[str, Any],
        *,
        timeout_seconds: int,
    ) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class OandaDemoProtectedConnectionAttemptRequest:
    broker_id: str = BROKER_ID
    account_mode: str = "PRACTICE_DEMO"
    environment: str = "OANDA_PRACTICE_DEMO"
    endpoint_classification: str = "OANDA_PRACTICE_DEMO"
    approval_scope: str = ATTEMPT_SCOPE
    connection_attempt_mode: str = ATTEMPT_MODE
    human_owner_protected_demo_connection_approved: bool = True
    network_broker_call_gate_approved: bool = True
    runtime_handoff_intake_ready: bool = True
    runtime_handoff_ready: bool = True
    connection_gate_ready: bool = True
    runtime_auth_reference_present: bool = True
    runtime_auth_reference_format: str = AUTH_REFERENCE_FORMAT
    auth_material_location: str = AUTH_MATERIAL_LOCATION
    runtime_auth_boundary_confirmed: bool = True
    repo_storage_confirmed_absent: bool = True
    account_identifier_present: bool = False
    credential_value_present: bool = False
    no_account_id_storage_confirmed: bool = True
    no_auth_value_storage_confirmed: bool = True
    one_shot_only: bool = True
    timeout_seconds: int = 10
    stop_on_success_or_failure: bool = True
    no_order_route_confirmed: bool = True
    no_account_id_logging_confirmed: bool = True
    audit_logging_acknowledged: bool = True


def build_oanda_demo_protected_connection_attempt_contract() -> dict[str, Any]:
    contract = {
        "schema": "AIOS_OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_CONTRACT.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "mode": ATTEMPT_MODE,
        "approval_scope_required": ATTEMPT_SCOPE,
        "supported_account_modes": sorted(SUPPORTED_ACCOUNT_MODES),
        "supported_environments": sorted(SUPPORTED_ENVIRONMENTS),
        "supported_endpoint_classifications": sorted(SUPPORTED_ENDPOINT_CLASSIFICATIONS),
        "required_approval_fields": list(REQUIRED_APPROVAL_FIELDS),
        "required_runtime_boundary_fields": list(REQUIRED_RUNTIME_BOUNDARY_FIELDS),
        "practice_demo_only": True,
        "one_shot_only_required": True,
        "retry_loop_allowed": False,
        "timeout_min_seconds": MIN_TIMEOUT_SECONDS,
        "timeout_max_seconds": MAX_TIMEOUT_SECONDS,
        "runtime_connector_boundary": build_runtime_connector_boundary_contract(),
        "evidence_schema": build_sanitized_connection_attempt_evidence_schema(),
        "connection_auth_proof_only": True,
        "account_state_request_allowed": False,
        "market_data_request_allowed": False,
        "order_route_allowed": False,
        "raw_broker_payload_persistence_allowed": False,
        "account_identifier_persistence_allowed": False,
        "credential_persistence_allowed": False,
        "fail_closed_default": True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_protected_connection_attempt_side_effects(contract)
    return contract


def build_runtime_connector_boundary_contract() -> dict[str, Any]:
    contract = {
        "schema": "AIOS_OANDA_DEMO_RUNTIME_CONNECTOR_BOUNDARY.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "connector_location": "EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY",
        "repo_owned_connector": False,
        "repo_auth_value_reads_allowed": False,
        "repo_auth_value_writes_allowed": False,
        "runtime_auth_reference_format_required": AUTH_REFERENCE_FORMAT,
        "auth_material_location_required": AUTH_MATERIAL_LOCATION,
        "connector_receives_credentials_from_repo": False,
        "connector_may_return_raw_payload": False,
        "connector_must_return_sanitized_status_only": True,
        "connector_call_limit": 1,
        "stop_after_first_result_required": True,
        "forbidden_attempt_field_names": sorted(FORBIDDEN_ATTEMPT_FIELD_NAMES),
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_protected_connection_attempt_side_effects(contract)
    return contract


def build_sanitized_connection_attempt_evidence_schema() -> dict[str, Any]:
    schema = {
        "schema": "AIOS_OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_EVIDENCE_SCHEMA.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "evidence_storage": "IN_MEMORY_SANITIZED_EVIDENCE_ONLY",
        "allowed_outcomes": [
            "CONNECTED_SANITIZED",
            "AUTH_REJECTED_SANITIZED",
            "CONNECTION_FAILURE_SANITIZED",
            "NETWORK_ERROR_SANITIZED",
            "TIMEOUT_SANITIZED",
            "RUNTIME_CONNECTOR_MISSING_SANITIZED",
            "UNSANITIZED_CONNECTOR_RESULT_REJECTED",
            "BLOCKED_FAIL_CLOSED",
        ],
        "allowed_evidence_fields": [
            "schema",
            "event",
            "broker_id",
            "status",
            "classification",
            "outcome",
            "connection_attempt_preflight_passed",
            "connection_attempt_performed",
            "endpoint_classification",
            "timeout_seconds",
            "attempt_count",
            "one_shot_only",
            "retry_loop_used",
            "stop_after_result",
            "blockers",
            "status_family",
            "sanitized",
        ],
        "forbidden_evidence_material": [
            "auth values",
            "runtime auth reference values",
            "account identifiers",
            "broker payloads",
            "request or response bodies",
            "account state",
            "market data",
            "order payloads",
            "live endpoint URLs",
        ],
        "sanitized": True,
        "contains_private_data": False,
        "contains_real_credentials": False,
        "contains_account_identifier": False,
        "raw_broker_payload_persisted": False,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_protected_connection_attempt_side_effects(schema)
    return schema


def build_oanda_demo_protected_connection_attempt_contract_set() -> dict[str, Any]:
    contract_set = {
        "schema": "AIOS_OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_CONTRACT_SET.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "protected_connection_attempt_contract": build_oanda_demo_protected_connection_attempt_contract(),
        "runtime_connector_boundary_contract": build_runtime_connector_boundary_contract(),
        "runtime_handoff_intake_contract_set": (
            oanda_demo_runtime_handoff_intake.build_oanda_demo_runtime_handoff_intake_contract_set()
        ),
        "runtime_handoff_contract_set": (
            oanda_demo_runtime_handoff.build_oanda_demo_runtime_handoff_contract_set()
        ),
        "connection_gate_contract_set": (
            oanda_demo_connection_gate.build_oanda_demo_connection_gate_contract_set()
        ),
        "connection_probe_contract": oanda_demo_connection_probe.build_oanda_demo_connection_probe_contract(),
        "sanitized_evidence_schema": build_sanitized_connection_attempt_evidence_schema(),
        "contracts_ready_for_protected_demo_connection_attempt": True,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_protected_connection_attempt_side_effects(contract_set)
    return contract_set


def build_example_oanda_demo_protected_connection_attempt_request() -> dict[str, Any]:
    return asdict(OandaDemoProtectedConnectionAttemptRequest())


def evaluate_oanda_demo_protected_connection_attempt_preflight(
    request: OandaDemoProtectedConnectionAttemptRequest | dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = _request_payload(request)
    forbidden_fields = _forbidden_field_paths(payload)
    credential_like_values = _credential_like_value_paths(payload)
    live_references = _live_reference_paths(payload)
    unauthorized_fields = _unauthorized_true_field_paths(payload)
    runtime_handoff_intake = oanda_demo_runtime_handoff_intake.evaluate_oanda_demo_runtime_handoff_intake(
        _runtime_handoff_intake_payload_from_attempt(payload)
    )
    runtime_handoff = oanda_demo_runtime_handoff.evaluate_oanda_demo_runtime_handoff(
        _runtime_handoff_payload_from_attempt(payload)
    )
    connection_gate = oanda_demo_connection_gate.evaluate_oanda_demo_connection_gate(
        _connection_gate_payload_from_attempt(payload)
    )
    connection_probe = oanda_demo_connection_probe.evaluate_oanda_demo_connection_probe(
        _connection_probe_payload_from_attempt(payload)
    )
    blockers = _preflight_blockers(
        payload,
        forbidden_fields=forbidden_fields,
        credential_like_values=credential_like_values,
        live_references=live_references,
        unauthorized_fields=unauthorized_fields,
        runtime_handoff_intake=runtime_handoff_intake,
        runtime_handoff=runtime_handoff,
        connection_gate=connection_gate,
        connection_probe=connection_probe,
    )
    status = ATTEMPT_BLOCKED if blockers else ATTEMPT_READY
    classification = "FAIL_CLOSED" if blockers else ATTEMPT_READY
    result = {
        "schema": "AIOS_OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_PREFLIGHT_RESULT.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": status,
        "classification": classification,
        "connection_attempt_preflight_passed": not blockers,
        "connection_attempt_performed": False,
        "approval_scope": str(payload.get("approval_scope") or ""),
        "connection_attempt_mode": str(payload.get("connection_attempt_mode") or ""),
        "account_mode": str(payload.get("account_mode") or "").upper(),
        "environment": str(payload.get("environment") or "").upper(),
        "endpoint_classification": str(payload.get("endpoint_classification") or "").upper(),
        "runtime_auth_reference_present": payload.get("runtime_auth_reference_present") is True,
        "runtime_auth_reference_format": str(payload.get("runtime_auth_reference_format") or ""),
        "auth_material_location": str(payload.get("auth_material_location") or ""),
        "runtime_auth_boundary_confirmed": payload.get("runtime_auth_boundary_confirmed") is True,
        "runtime_handoff_intake_ready": runtime_handoff_intake["runtime_handoff_intake_ready"],
        "runtime_handoff_ready": runtime_handoff["runtime_handoff_ready"],
        "connection_gate_ready": connection_gate["connection_readiness_gate_ready"],
        "connection_probe_ready": connection_probe["probe_ready"],
        "one_shot_only": payload.get("one_shot_only") is True,
        "timeout_seconds": _int_or_none(payload.get("timeout_seconds")),
        "stop_after_result": payload.get("stop_on_success_or_failure") is True,
        "forbidden_fields_detected": forbidden_fields,
        "credential_like_value_paths_detected": credential_like_values,
        "live_reference_paths_detected": live_references,
        "unauthorized_execution_fields_detected": unauthorized_fields,
        "blockers": blockers,
        "runtime_handoff_intake_summary": _layer_summary(runtime_handoff_intake),
        "runtime_handoff_summary": _layer_summary(runtime_handoff),
        "connection_gate_summary": _layer_summary(connection_gate),
        "connection_probe_summary": _layer_summary(connection_probe),
        "contract": build_oanda_demo_protected_connection_attempt_contract(),
        "audit_event": _build_preflight_audit_event(
            status=status,
            classification=classification,
            blockers=blockers,
            forbidden_fields=forbidden_fields,
            credential_like_values=credential_like_values,
            live_references=live_references,
            unauthorized_fields=unauthorized_fields,
            timeout_seconds=_int_or_none(payload.get("timeout_seconds")),
        ),
        "next_safe_action": _next_safe_action(blockers),
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_protected_connection_attempt_side_effects(result)
    return result


def run_oanda_demo_protected_connection_attempt(
    request: OandaDemoProtectedConnectionAttemptRequest | dict[str, Any] | None = None,
    *,
    runtime_connector: OandaDemoRuntimeConnector | None = None,
) -> dict[str, Any]:
    payload = _request_payload(request)
    preflight = evaluate_oanda_demo_protected_connection_attempt_preflight(payload)
    timeout_seconds = _int_or_none(payload.get("timeout_seconds"))

    if preflight["connection_attempt_preflight_passed"] is not True:
        return _build_attempt_result(
            payload=payload,
            preflight=preflight,
            status=ATTEMPT_BLOCKED,
            classification="FAIL_CLOSED",
            outcome="BLOCKED_FAIL_CLOSED",
            blockers=list(preflight.get("blockers") or []),
            connection_attempt_performed=False,
            attempt_count=0,
            status_family="not_sent",
        )

    if runtime_connector is None:
        return _build_attempt_result(
            payload=payload,
            preflight=preflight,
            status=ATTEMPT_BLOCKED,
            classification="FAIL_CLOSED",
            outcome="RUNTIME_CONNECTOR_MISSING_SANITIZED",
            blockers=["external_runtime_connector_required"],
            connection_attempt_performed=False,
            attempt_count=0,
            status_family="not_sent",
        )

    connector_request = _runtime_connector_request(payload)
    try:
        connector_result = runtime_connector.attempt_connection(
            connector_request,
            timeout_seconds=int(timeout_seconds or 0),
        )
    except TimeoutError:
        return _build_attempt_result(
            payload=payload,
            preflight=preflight,
            status=ATTEMPT_FAILED,
            classification="TIMEOUT_SANITIZED",
            outcome="TIMEOUT_SANITIZED",
            blockers=["connection_attempt_timeout"],
            connection_attempt_performed=True,
            attempt_count=1,
            status_family="timeout",
        )
    except Exception:
        return _build_attempt_result(
            payload=payload,
            preflight=preflight,
            status=ATTEMPT_FAILED,
            classification="NETWORK_ERROR_SANITIZED",
            outcome="NETWORK_ERROR_SANITIZED",
            blockers=["runtime_connector_error_sanitized"],
            connection_attempt_performed=True,
            attempt_count=1,
            status_family="error",
        )

    sanitized = _classify_connector_result(connector_result)
    return _build_attempt_result(
        payload=payload,
        preflight=preflight,
        status=sanitized["status"],
        classification=sanitized["classification"],
        outcome=sanitized["outcome"],
        blockers=sanitized["blockers"],
        connection_attempt_performed=True,
        attempt_count=1,
        status_family=sanitized["status_family"],
    )


def summarize_oanda_demo_protected_connection_attempt(result: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = dict(result or run_oanda_demo_protected_connection_attempt())
    summary = {
        "schema": "AIOS_OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_SUMMARY.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": str(payload.get("status") or ATTEMPT_BLOCKED),
        "classification": str(payload.get("classification") or "FAIL_CLOSED"),
        "outcome": str(payload.get("outcome") or "BLOCKED_FAIL_CLOSED"),
        "connection_attempt_preflight_passed": payload.get("connection_attempt_preflight_passed") is True,
        "connection_attempt_performed": payload.get("connection_attempt_performed") is True,
        "endpoint_classification": str(payload.get("endpoint_classification") or ""),
        "live_endpoint_used": False,
        "attempt_count": int(payload.get("attempt_count") or 0),
        "retry_loop_used": False,
        "stop_after_result": payload.get("stop_after_result") is True,
        "blockers": list(payload.get("blockers") or []),
        "sanitized_audit_event_recorded": isinstance(payload.get("audit_event"), dict),
        "contains_real_credentials": False,
        "contains_account_identifier": False,
        "raw_broker_payload_persisted": False,
        "repo_stored_auth_material_present": False,
        "next_safe_action": str(payload.get("next_safe_action") or _next_safe_action(payload.get("blockers") or [])),
        **_blocked_capabilities(
            broker_request_sent=payload.get("broker_request_sent") is True,
            network_used=payload.get("network_used") is True,
            connection_attempt_performed=payload.get("connection_attempt_performed") is True,
        ),
    }
    assert_no_oanda_demo_protected_connection_attempt_side_effects(summary)
    return summary


def scan_attempt_cli_args(argv: list[str]) -> list[str]:
    blockers: list[str] = []
    for raw_arg in argv:
        arg = str(raw_arg).strip()
        lowered = arg.lower()
        if lowered in CLI_ALLOWED_SAFETY_FLAGS:
            continue
        if any(marker in lowered for marker in CLI_FORBIDDEN_ARG_MARKERS):
            blockers.append("cli_sensitive_or_forbidden_argument_rejected")
        if any(marker in lowered for marker in FORBIDDEN_VALUE_MARKERS):
            blockers.append("cli_credential_like_value_rejected")
    return _unique(blockers)


def build_blocked_cli_result(blockers: list[str]) -> dict[str, Any]:
    result = {
        "schema": "AIOS_OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_CLI_REJECTION.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": ATTEMPT_BLOCKED,
        "classification": "FAIL_CLOSED",
        "outcome": "BLOCKED_FAIL_CLOSED",
        "connection_attempt_preflight_passed": False,
        "connection_attempt_performed": False,
        "attempt_count": 0,
        "blockers": _unique(blockers),
        "sanitized": True,
        "contains_private_data": False,
        "contains_real_credentials": False,
        "contains_account_identifier": False,
        "raw_broker_payload_persisted": False,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_protected_connection_attempt_side_effects(result)
    return result


def assert_no_oanda_demo_protected_connection_attempt_side_effects(payload: dict[str, Any]) -> bool:
    if _has_unsafe_capability(payload):
        raise ValueError("OANDA protected demo connection attempt must not enable unsafe side effects")
    schemas.assert_no_live_permissions(payload)
    return True


def _preflight_blockers(
    payload: dict[str, Any],
    *,
    forbidden_fields: list[str],
    credential_like_values: list[str],
    live_references: list[str],
    unauthorized_fields: list[str],
    runtime_handoff_intake: dict[str, Any],
    runtime_handoff: dict[str, Any],
    connection_gate: dict[str, Any],
    connection_probe: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    for field_name in (*REQUIRED_APPROVAL_FIELDS, *REQUIRED_RUNTIME_BOUNDARY_FIELDS):
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
        blockers.append("unsupported_account_mode")
    if environment and environment not in SUPPORTED_ENVIRONMENTS:
        blockers.append("unsupported_environment")
    if endpoint and endpoint not in SUPPORTED_ENDPOINT_CLASSIFICATIONS:
        blockers.append("unsupported_endpoint_classification")
    if "LIVE" in account_mode or "LIVE" in environment:
        blockers.append("live_account_attempt_blocked")
    if "LIVE" in endpoint or payload.get("live_endpoint_requested") is True:
        blockers.append("live_endpoint_blocked")
    if live_references:
        blockers.append("live_reference_detected")
        blockers.extend([f"live_reference:{field}" for field in live_references])
    if payload.get("approval_scope") != ATTEMPT_SCOPE:
        blockers.append(f"approval_scope_must_equal:{ATTEMPT_SCOPE}")
    if payload.get("connection_attempt_mode") != ATTEMPT_MODE:
        blockers.append(f"connection_attempt_mode_must_equal:{ATTEMPT_MODE}")
    if payload.get("human_owner_protected_demo_connection_approved") is not True:
        blockers.append("human_owner_protected_demo_connection_approval_required")
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
    if payload.get("credential_value_present") is True:
        blockers.append("credential_value_not_allowed")
    if payload.get("no_account_id_storage_confirmed") is not True:
        blockers.append("no_account_id_storage_confirmation_required")
    if payload.get("no_auth_value_storage_confirmed") is not True:
        blockers.append("no_auth_value_storage_confirmation_required")
    if payload.get("runtime_handoff_intake_ready") is not True:
        blockers.append("runtime_handoff_intake_ready_confirmation_required")
    if payload.get("runtime_handoff_ready") is not True:
        blockers.append("runtime_handoff_ready_confirmation_required")
    if payload.get("connection_gate_ready") is not True:
        blockers.append("connection_gate_ready_confirmation_required")
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
    if payload.get("account_state_requested") is True or payload.get("account_access_requested") is True:
        blockers.append("account_state_request_blocked")
    if (
        payload.get("market_data_requested") is True
        or payload.get("market_data_beyond_connection_auth_requested") is True
    ):
        blockers.append("market_data_request_blocked")
    if payload.get("retry_loop_requested") is True or payload.get("probe_retry_requested") is True:
        blockers.append("retry_loop_blocked")
    max_attempts = _int_or_none(payload.get("max_attempts"))
    if max_attempts is not None and max_attempts != 1:
        blockers.append("max_attempts_must_equal_one")

    if forbidden_fields:
        blockers.append("forbidden_sensitive_field_detected")
        blockers.extend([f"forbidden_field:{field}" for field in forbidden_fields])
    if credential_like_values:
        blockers.append("credential_like_value_detected")
        blockers.extend([f"credential_like_value:{field}" for field in credential_like_values])
    if unauthorized_fields:
        blockers.append("unauthorized_connection_attempt")
        blockers.extend([f"unauthorized_execution_field:{field}" for field in unauthorized_fields])
    if runtime_handoff_intake.get("runtime_handoff_intake_ready") is not True:
        blockers.append("runtime_handoff_intake_required")
        blockers.extend(
            [
                f"runtime_handoff_intake_blocker:{blocker}"
                for blocker in list(runtime_handoff_intake.get("blockers") or [])
            ]
        )
    if runtime_handoff.get("runtime_handoff_ready") is not True:
        blockers.append("runtime_handoff_required")
        blockers.extend(
            [
                f"runtime_handoff_blocker:{blocker}"
                for blocker in list(runtime_handoff.get("blockers") or [])
            ]
        )
    if connection_gate.get("connection_readiness_gate_ready") is not True:
        blockers.append("connection_gate_required")
        blockers.extend(
            [
                f"connection_gate_blocker:{blocker}"
                for blocker in list(connection_gate.get("blockers") or [])
            ]
        )
    if connection_probe.get("probe_ready") is not True:
        blockers.append("connection_probe_required")
        blockers.extend(
            [
                f"connection_probe_blocker:{blocker}"
                for blocker in list(connection_probe.get("blockers") or [])
            ]
        )
    return _unique(blockers)


def _build_attempt_result(
    *,
    payload: dict[str, Any],
    preflight: dict[str, Any],
    status: str,
    classification: str,
    outcome: str,
    blockers: list[str],
    connection_attempt_performed: bool,
    attempt_count: int,
    status_family: str,
) -> dict[str, Any]:
    broker_request_sent = connection_attempt_performed
    network_used = connection_attempt_performed
    result = {
        "schema": "AIOS_OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_RESULT.v1",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": status,
        "classification": classification,
        "outcome": outcome,
        "connection_attempt_preflight_passed": preflight["connection_attempt_preflight_passed"],
        "connection_attempt_performed": connection_attempt_performed,
        "connection_auth_proof_sanitized": outcome == "CONNECTED_SANITIZED",
        "endpoint_classification": str(payload.get("endpoint_classification") or "").upper(),
        "practice_demo_endpoint_used": connection_attempt_performed,
        "live_endpoint_used": False,
        "timeout_seconds": _int_or_none(payload.get("timeout_seconds")),
        "attempt_count": int(attempt_count),
        "one_shot_only": payload.get("one_shot_only") is True,
        "retry_loop_used": False,
        "stop_after_result": True,
        "final_state": "STOPPED_AFTER_RESULT" if connection_attempt_performed else "STOPPED_BEFORE_CONNECTION",
        "status_family": status_family,
        "blockers": _unique(blockers),
        "preflight_status": preflight["status"],
        "preflight_blockers": list(preflight.get("blockers") or []),
        "sanitized": True,
        "contains_private_data": False,
        "contains_real_credentials": False,
        "contains_account_identifier": False,
        "credential_values_recorded": False,
        "account_identifiers_recorded": False,
        "broker_payloads_recorded": False,
        "raw_broker_payload_persisted": False,
        "repo_stored_auth_material_present": False,
        "account_state_requested": False,
        "market_data_requested": False,
        "order_route_requested": False,
        "audit_event": _build_attempt_audit_event(
            status=status,
            classification=classification,
            outcome=outcome,
            blockers=_unique(blockers),
            connection_attempt_performed=connection_attempt_performed,
            attempt_count=attempt_count,
            timeout_seconds=_int_or_none(payload.get("timeout_seconds")),
            status_family=status_family,
        ),
        "next_safe_action": _next_safe_action(_unique(blockers)),
        **_blocked_capabilities(
            broker_request_sent=broker_request_sent,
            network_used=network_used,
            connection_attempt_performed=connection_attempt_performed,
        ),
    }
    assert_no_oanda_demo_protected_connection_attempt_side_effects(result)
    return result


def _classify_connector_result(connector_result: dict[str, Any]) -> dict[str, Any]:
    payload = dict(connector_result or {})
    forbidden_fields = _forbidden_field_paths(payload)
    credential_like_values = _credential_like_value_paths(payload)
    live_references = _live_reference_paths(payload)
    unsafe_true_fields = _unsafe_connector_true_field_paths(payload)
    blockers = []
    if forbidden_fields:
        blockers.append("connector_result_forbidden_sensitive_field_detected")
        blockers.extend([f"connector_result_forbidden_field:{field}" for field in forbidden_fields])
    if credential_like_values:
        blockers.append("connector_result_credential_like_value_detected")
        blockers.extend([f"connector_result_credential_like_value:{field}" for field in credential_like_values])
    if live_references:
        blockers.append("connector_result_live_reference_detected")
        blockers.extend([f"connector_result_live_reference:{field}" for field in live_references])
    if unsafe_true_fields:
        blockers.append("connector_result_unsafe_side_effect_detected")
        blockers.extend([f"connector_result_unsafe_true_field:{field}" for field in unsafe_true_fields])
    if blockers:
        return {
            "status": ATTEMPT_BLOCKED,
            "classification": "FAIL_CLOSED",
            "outcome": "UNSANITIZED_CONNECTOR_RESULT_REJECTED",
            "blockers": _unique(blockers),
            "status_family": "sanitized_rejection",
        }

    status_family = _status_family(payload.get("status_code") or payload.get("http_status"))
    if payload.get("connected") is True and payload.get("auth_proof") is True:
        return {
            "status": ATTEMPT_CONNECTED,
            "classification": "CONNECTED_SANITIZED",
            "outcome": "CONNECTED_SANITIZED",
            "blockers": [],
            "status_family": status_family,
        }
    if payload.get("auth_rejected") is True or status_family in {"401", "403"}:
        return {
            "status": ATTEMPT_FAILED,
            "classification": "AUTH_REJECTED_SANITIZED",
            "outcome": "AUTH_REJECTED_SANITIZED",
            "blockers": ["auth_rejected_sanitized"],
            "status_family": status_family,
        }
    return {
        "status": ATTEMPT_FAILED,
        "classification": "CONNECTION_FAILURE_SANITIZED",
        "outcome": "CONNECTION_FAILURE_SANITIZED",
        "blockers": ["connection_not_proven_sanitized"],
        "status_family": status_family,
    }


def _runtime_connector_request(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "AIOS_OANDA_DEMO_RUNTIME_CONNECTOR_REQUEST.v1",
        "broker_id": BROKER_ID,
        "account_mode": "PRACTICE_DEMO",
        "environment": "OANDA_PRACTICE_DEMO",
        "endpoint_classification": "OANDA_PRACTICE_DEMO",
        "connection_auth_proof_only": True,
        "runtime_auth_reference_present": payload.get("runtime_auth_reference_present") is True,
        "runtime_auth_reference_format": AUTH_REFERENCE_FORMAT,
        "auth_material_location": AUTH_MATERIAL_LOCATION,
        "timeout_seconds": _int_or_none(payload.get("timeout_seconds")),
        "one_shot_only": True,
        "stop_on_success_or_failure": True,
        "account_identifier_present": False,
        "credential_value_present": False,
        "account_state_request_allowed": False,
        "market_data_request_allowed": False,
        "order_route_allowed": False,
        "raw_payload_logging_allowed": False,
        "sanitized": True,
        **_blocked_capabilities(),
    }


def _runtime_handoff_intake_payload_from_attempt(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "broker_id": payload.get("broker_id"),
        "account_mode": payload.get("account_mode"),
        "environment": payload.get("environment"),
        "endpoint_classification": payload.get("endpoint_classification"),
        "intake_scope": oanda_demo_runtime_handoff_intake.INTAKE_SCOPE,
        "intake_mode": oanda_demo_runtime_handoff_intake.INTAKE_MODE,
        "metadata_intake_authorized": True,
        "runtime_reference_present": payload.get("runtime_auth_reference_present"),
        "runtime_reference_format": payload.get("runtime_auth_reference_format"),
        "auth_material_location": payload.get("auth_material_location"),
        "runtime_boundary_confirmed": payload.get("runtime_auth_boundary_confirmed"),
        "external_operator_controlled_runtime_confirmed": payload.get("runtime_auth_boundary_confirmed"),
        "repo_storage_confirmed_absent": payload.get("repo_storage_confirmed_absent"),
        "account_identifier_present": payload.get("account_identifier_present"),
        "credential_value_present": payload.get("credential_value_present", False),
        "no_account_id_storage_confirmed": payload.get("no_account_id_storage_confirmed"),
        "no_auth_value_storage_confirmed": payload.get("no_auth_value_storage_confirmed"),
        "audit_logging_acknowledged": payload.get("audit_logging_acknowledged"),
    }


def _runtime_handoff_payload_from_attempt(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "broker_id": payload.get("broker_id"),
        "account_mode": payload.get("account_mode"),
        "environment": payload.get("environment"),
        "endpoint_classification": payload.get("endpoint_classification"),
        "handoff_scope": oanda_demo_runtime_handoff.HANDOFF_SCOPE,
        "handoff_mode": oanda_demo_runtime_handoff.HANDOFF_MODE,
        "metadata_intake_authorized": True,
        "runtime_reference_present": payload.get("runtime_auth_reference_present"),
        "runtime_reference_format": payload.get("runtime_auth_reference_format"),
        "auth_material_location": payload.get("auth_material_location"),
        "runtime_boundary_confirmed": payload.get("runtime_auth_boundary_confirmed"),
        "repo_storage_confirmed_absent": payload.get("repo_storage_confirmed_absent"),
        "account_identifier_present": payload.get("account_identifier_present"),
        "credential_value_present": payload.get("credential_value_present", False),
        "no_account_id_storage_confirmed": payload.get("no_account_id_storage_confirmed"),
        "no_auth_value_storage_confirmed": payload.get("no_auth_value_storage_confirmed"),
        "audit_logging_acknowledged": payload.get("audit_logging_acknowledged"),
    }


def _connection_gate_payload_from_attempt(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "broker_id": payload.get("broker_id"),
        "account_mode": payload.get("account_mode"),
        "environment": payload.get("environment"),
        "endpoint_classification": payload.get("endpoint_classification"),
        "approval_scope": oanda_demo_connection_gate.APPROVAL_SCOPE,
        "gate_mode": oanda_demo_connection_gate.GATE_MODE,
        "external_auth_reference_present": payload.get("runtime_auth_reference_present"),
        "external_auth_reference_format": payload.get("runtime_auth_reference_format"),
        "auth_material_location": payload.get("auth_material_location"),
        "runtime_auth_boundary_confirmed": payload.get("runtime_auth_boundary_confirmed"),
        "runtime_auth_proof_present": payload.get("runtime_auth_reference_present"),
        "repo_storage_confirmed_absent": payload.get("repo_storage_confirmed_absent"),
        "account_identifier_present": payload.get("account_identifier_present"),
        "human_owner_connection_gate_approved": payload.get("human_owner_protected_demo_connection_approved"),
        "network_broker_call_gate_approved": payload.get("network_broker_call_gate_approved"),
        "one_shot_only": payload.get("one_shot_only"),
        "timeout_seconds": payload.get("timeout_seconds"),
        "stop_on_success_or_failure": payload.get("stop_on_success_or_failure"),
        "no_order_route_confirmed": payload.get("no_order_route_confirmed"),
        "no_account_id_logging_confirmed": payload.get("no_account_id_logging_confirmed"),
        "audit_logging_acknowledged": payload.get("audit_logging_acknowledged"),
    }


def _connection_probe_payload_from_attempt(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "broker_id": payload.get("broker_id"),
        "account_mode": payload.get("account_mode"),
        "environment": payload.get("environment"),
        "endpoint_classification": payload.get("endpoint_classification"),
        "probe_scope": oanda_demo_connection_probe.PROBE_SCOPE,
        "probe_mode": oanda_demo_connection_probe.PROBE_MODE,
        "demo_probe_approval_flag": payload.get("human_owner_protected_demo_connection_approved"),
        "network_broker_call_gate_approved": payload.get("network_broker_call_gate_approved"),
        "runtime_auth_reference_present": payload.get("runtime_auth_reference_present"),
        "runtime_auth_reference_format": payload.get("runtime_auth_reference_format"),
        "auth_material_location": payload.get("auth_material_location"),
        "runtime_auth_boundary_confirmed": payload.get("runtime_auth_boundary_confirmed"),
        "repo_storage_confirmed_absent": payload.get("repo_storage_confirmed_absent"),
        "account_identifier_present": payload.get("account_identifier_present"),
        "one_shot_only": payload.get("one_shot_only"),
        "timeout_seconds": payload.get("timeout_seconds"),
        "stop_on_success_or_failure": payload.get("stop_on_success_or_failure"),
        "no_order_route_confirmed": payload.get("no_order_route_confirmed"),
        "no_account_id_logging_confirmed": payload.get("no_account_id_logging_confirmed"),
        "audit_logging_acknowledged": payload.get("audit_logging_acknowledged"),
    }


def _build_preflight_audit_event(
    *,
    status: str,
    classification: str,
    blockers: list[str],
    forbidden_fields: list[str],
    credential_like_values: list[str],
    live_references: list[str],
    unauthorized_fields: list[str],
    timeout_seconds: int | None,
) -> dict[str, Any]:
    event = {
        "schema": "AIOS_OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_PREFLIGHT_AUDIT_EVENT.v1",
        "event": "oanda_demo_protected_connection_attempt_preflight_validated",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": status,
        "classification": classification,
        "connection_attempt_preflight_passed": not blockers,
        "connection_attempt_performed": False,
        "blockers": list(blockers),
        "forbidden_fields_detected": list(forbidden_fields),
        "credential_like_value_paths_detected": list(credential_like_values),
        "live_reference_paths_detected": list(live_references),
        "unauthorized_execution_fields_detected": list(unauthorized_fields),
        "timeout_seconds": timeout_seconds,
        "one_shot_only": True,
        "sanitized": True,
        "contains_private_data": False,
        "contains_real_credentials": False,
        "contains_account_identifier": False,
        "credential_values_recorded": False,
        "account_identifiers_recorded": False,
        "broker_payloads_recorded": False,
        "raw_broker_payload_persisted": False,
        **_blocked_capabilities(),
    }
    assert_no_oanda_demo_protected_connection_attempt_side_effects(event)
    return event


def _build_attempt_audit_event(
    *,
    status: str,
    classification: str,
    outcome: str,
    blockers: list[str],
    connection_attempt_performed: bool,
    attempt_count: int,
    timeout_seconds: int | None,
    status_family: str,
) -> dict[str, Any]:
    event = {
        "schema": "AIOS_OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_AUDIT_EVENT.v1",
        "event": "oanda_demo_protected_connection_attempt_completed",
        "broker_id": BROKER_ID,
        "broker_reference": BROKER_REFERENCE,
        "status": status,
        "classification": classification,
        "outcome": outcome,
        "connection_attempt_performed": connection_attempt_performed,
        "attempt_count": int(attempt_count),
        "retry_loop_used": False,
        "timeout_seconds": timeout_seconds,
        "status_family": status_family,
        "blockers": list(blockers),
        "sanitized": True,
        "contains_private_data": False,
        "contains_real_credentials": False,
        "contains_account_identifier": False,
        "credential_values_recorded": False,
        "account_identifiers_recorded": False,
        "broker_payloads_recorded": False,
        "raw_broker_payload_persisted": False,
        **_blocked_capabilities(
            broker_request_sent=connection_attempt_performed,
            network_used=connection_attempt_performed,
            connection_attempt_performed=connection_attempt_performed,
        ),
    }
    assert_no_oanda_demo_protected_connection_attempt_side_effects(event)
    return event


def _layer_summary(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": str(payload.get("schema") or ""),
        "status": str(payload.get("status") or ""),
        "classification": str(payload.get("classification") or ""),
        "blockers": list(payload.get("blockers") or []),
        "sanitized": True,
        "contains_real_credentials": False,
        "contains_account_identifier": False,
    }


def _next_safe_action(blockers: list[str]) -> str:
    if blockers:
        return (
            "Keep the OANDA protected demo connection attempt fail-closed until "
            "approval, runtime boundary, one-shot, timeout, no-account, no-order, "
            "and sanitized connector requirements all pass."
        )
    return (
        "Protected OANDA practice/demo connection attempt evidence is sanitized; "
        "stop here and do not proceed to account state, market data, orders, or live trading."
    )


def _blocked_capabilities(
    *,
    broker_request_sent: bool = False,
    network_used: bool = False,
    connection_attempt_performed: bool = False,
) -> dict[str, Any]:
    return {
        "broker_connection_allowed": False,
        "connection_attempt_allowed": False,
        "connection_attempt_allowed_now": False,
        "connection_attempt_performed": bool(connection_attempt_performed),
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
        "broker_request_sent": bool(broker_request_sent),
        "account_access_allowed": False,
        "account_mutation_allowed": False,
        "account_state_allowed": False,
        "market_data_allowed": False,
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
        "network_used": bool(network_used),
        "live_ready": False,
        "live_trade_ready": False,
        "real_order_ready": False,
    }


def _request_payload(request: OandaDemoProtectedConnectionAttemptRequest | dict[str, Any] | None) -> dict[str, Any]:
    if request is None:
        return {}
    if isinstance(request, OandaDemoProtectedConnectionAttemptRequest):
        return asdict(request)
    return dict(request)


def _forbidden_field_paths(value: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            normalized = _normalize_key(key_text)
            if normalized in FORBIDDEN_ATTEMPT_FIELD_NAMES:
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


def _live_reference_paths(value: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            paths.extend(_live_reference_paths(nested, path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            paths.extend(_live_reference_paths(nested, f"{prefix}[{index}]"))
    elif isinstance(value, str):
        normalized = value.strip().upper().replace("-", "_").replace(" ", "_")
        if any(marker in normalized for marker in LIVE_REFERENCE_MARKERS):
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


def _unsafe_connector_true_field_paths(value: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            normalized = _normalize_key(key_text)
            if normalized in UNSAFE_CONNECTOR_TRUE_FIELDS and nested is True:
                paths.append(path)
            paths.extend(_unsafe_connector_true_field_paths(nested, path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            paths.extend(_unsafe_connector_true_field_paths(nested, f"{prefix}[{index}]"))
    return _unique(paths)


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


def _status_family(value: Any) -> str:
    try:
        status = int(value)
    except (TypeError, ValueError):
        return "unknown"
    if status in {401, 403}:
        return str(status)
    if status < 100 or status > 599:
        return "unknown"
    return f"{status // 100}xx"


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
