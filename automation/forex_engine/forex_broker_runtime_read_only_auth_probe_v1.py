"""Broker runtime read-only auth probe contract and helpers for Forex OANDA runtime."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


PACKET_ID = "AIOS-FOREX-BROKER-RUNTIME-READ-ONLY-AUTH-PROBE-V1"
CURRENT_STAGE = "broker_runtime_read_only_auth_probe"

DEFAULT_BROKER_RUNTIME_ITEM_REF = "AIOS / OANDA / Practice Demo / Broker Runtime"
DEFAULT_BROKER_API_TOKEN_FIELD_REF = "broker_api_token"
DEFAULT_BROKER_ACCOUNT_ID_FIELD_REF = "broker_account_id"
DEFAULT_ENDPOINT_FIELD_REF = "endpoint"
DEFAULT_ENVIRONMENT_FIELD_REF = "environment"
DEFAULT_ALLOWED_MODE_FIELD_REF = "allowed_mode"
DEFAULT_ENDPOINT = "https://api-fxpractice.oanda.com"
DEFAULT_ENVIRONMENT = "practice_demo"
DEFAULT_ALLOWED_MODE = "read_only_until_owner_demo_approval"

REDACTION_TOKEN_MARKER = "REDACTED_TOKEN"
REDACTION_ACCOUNT_MARKER = "REDACTED_ACCOUNT_ID"

BROKER_RUNTIME_READ_ONLY_AUTH_PROBE_READY = "OWNER_RUNTIME_READ_ONLY_PROBE_READY"
CREDENTIAL_REFERENCE_HANDOFF_REQUIRED = "CREDENTIAL_REFERENCE_HANDOFF_REQUIRED"
REFERENCE_CONTRACT_MISMATCH = "REFERENCE_CONTRACT_MISMATCH"
SECRET_LOGGING_REJECTED = "SECRET_LOGGING_REJECTED"
ENV_FILE_READ_REJECTED = "ENV_FILE_READ_REJECTED"
LIVE_ENDPOINT_REJECTED = "LIVE_ENDPOINT_REJECTED"
ORDER_PATH_REJECTED = "ORDER_PATH_REJECTED"
OWNER_READ_ONLY_APPROVAL_REQUIRED = "OWNER_READ_ONLY_APPROVAL_REQUIRED"
BW_SESSION_REQUIRED = "BW_SESSION_REQUIRED"
BITWARDEN_CLI_REQUIRED = "BITWARDEN_CLI_REQUIRED"
BITWARDEN_ITEM_READ_REQUIRED = "BITWARDEN_ITEM_READ_REQUIRED"
OANDA_PRACTICE_READ_ONLY_ACCOUNT_PROBE_REQUIRED = (
    "OANDA_PRACTICE_READ_ONLY_ACCOUNT_PROBE_REQUIRED"
)
BROKER_RUNTIME_READ_ONLY_AUTH_PROVEN = "BROKER_RUNTIME_READ_ONLY_AUTH_PROVEN"

CURRENT_SESSION_WINDOW_HOURS = 22
CURRENT_SESSION_WINDOW_DAYS_PER_WEEK = 6


@dataclass(frozen=True)
class BrokerRuntimeReadOnlyAuthProbeInput:
    credential_reference_handoff_landed: bool
    broker_runtime_item_ref: str
    broker_api_token_field_ref: str
    broker_account_id_field_ref: str
    endpoint_field_ref: str
    environment_field_ref: str
    allowed_mode_field_ref: str
    expected_endpoint: str
    expected_environment: str
    expected_allowed_mode: str
    owner_approved_read_only_probe: bool
    bw_session_present: bool
    runtime_probe_requested: bool
    bitwarden_cli_available: bool
    bitwarden_item_read_success: bool
    broker_account_summary_read_success: bool
    secret_values_logged: bool
    env_file_read: bool
    live_endpoint_used: bool
    order_endpoint_used: bool
    broker_api_called: bool
    bitwarden_cli_called: bool
    bitwarden_vault_read: bool
    credentials_read: bool
    order_execution: bool
    demo_authorized: bool
    live_authorized: bool
    session_window_hours: int
    session_window_days_per_week: int


@dataclass(frozen=True)
class BrokerRuntimeReadOnlyAuthProbeResult:
    probe_status: str
    current_stage: str
    next_stage: str
    blockers: list[str]
    broker_runtime_item_ref: str
    redaction_status: str
    bitwarden_cli_called: bool
    bitwarden_vault_read: bool
    credentials_read: bool
    env_file_read: bool
    broker_api_called: bool
    order_execution: bool
    demo_authorized: bool
    live_authorized: bool
    safe_next_action: str


def build_default_input(
    *,
    runtime_probe_requested: bool = False,
    owner_approved_read_only_probe: bool = False,
) -> BrokerRuntimeReadOnlyAuthProbeInput:
    return BrokerRuntimeReadOnlyAuthProbeInput(
        credential_reference_handoff_landed=True,
        broker_runtime_item_ref=DEFAULT_BROKER_RUNTIME_ITEM_REF,
        broker_api_token_field_ref=DEFAULT_BROKER_API_TOKEN_FIELD_REF,
        broker_account_id_field_ref=DEFAULT_BROKER_ACCOUNT_ID_FIELD_REF,
        endpoint_field_ref=DEFAULT_ENDPOINT_FIELD_REF,
        environment_field_ref=DEFAULT_ENVIRONMENT_FIELD_REF,
        allowed_mode_field_ref=DEFAULT_ALLOWED_MODE_FIELD_REF,
        expected_endpoint=DEFAULT_ENDPOINT,
        expected_environment=DEFAULT_ENVIRONMENT,
        expected_allowed_mode=DEFAULT_ALLOWED_MODE,
        owner_approved_read_only_probe=owner_approved_read_only_probe,
        bw_session_present=False,
        runtime_probe_requested=runtime_probe_requested,
        bitwarden_cli_available=False,
        bitwarden_item_read_success=False,
        broker_account_summary_read_success=False,
        secret_values_logged=False,
        env_file_read=False,
        live_endpoint_used=False,
        order_endpoint_used=False,
        broker_api_called=False,
        bitwarden_cli_called=False,
        bitwarden_vault_read=False,
        credentials_read=False,
        order_execution=False,
        demo_authorized=False,
        live_authorized=False,
        session_window_hours=CURRENT_SESSION_WINDOW_HOURS,
        session_window_days_per_week=CURRENT_SESSION_WINDOW_DAYS_PER_WEEK,
    )


def evaluate_broker_runtime_read_only_auth_probe(
    input_data: BrokerRuntimeReadOnlyAuthProbeInput,
) -> BrokerRuntimeReadOnlyAuthProbeResult:
    current_stage = CURRENT_STAGE
    blockers: list[str] = []
    next_stage = "owner_run_read_only_auth_probe"
    redaction_status = "redaction_not_verified"

    if not input_data.credential_reference_handoff_landed:
        probe_status = CREDENTIAL_REFERENCE_HANDOFF_REQUIRED
        next_stage = "bitwarden_cloud_credential_reference_handoff"
        blockers.append("credential_reference_handoff_landed is False")

    elif not _reference_contract_matches(input_data):
        probe_status = REFERENCE_CONTRACT_MISMATCH
        next_stage = "fix_bitwarden_reference_contract"
        blockers.append("bitwarden reference contract fields must match expected values")

    elif input_data.secret_values_logged:
        probe_status = SECRET_LOGGING_REJECTED
        next_stage = "remove_secret_logging"
        blockers.append("secret_values_logged is True")

    elif input_data.env_file_read:
        probe_status = ENV_FILE_READ_REJECTED
        next_stage = "remove_env_file_read"
        blockers.append("env_file_read is True")

    elif input_data.live_endpoint_used:
        probe_status = LIVE_ENDPOINT_REJECTED
        next_stage = "use_oanda_practice_endpoint_only"
        blockers.append("live_endpoint_used is True")

    elif input_data.order_endpoint_used or input_data.order_execution:
        probe_status = ORDER_PATH_REJECTED
        next_stage = "remove_order_path"
        blockers.append("order endpoint or order execution path used")

    elif not input_data.runtime_probe_requested:
        probe_status = BROKER_RUNTIME_READ_ONLY_AUTH_PROBE_READY
        next_stage = "owner_run_read_only_auth_probe"

    elif not input_data.owner_approved_read_only_probe:
        probe_status = OWNER_READ_ONLY_APPROVAL_REQUIRED
        next_stage = "owner_approve_read_only_probe"
        blockers.append("owner_approved_read_only_probe is False")

    elif not input_data.bw_session_present:
        probe_status = BW_SESSION_REQUIRED
        next_stage = "owner_unlock_bitwarden_cli"
        blockers.append("bw_session_present is False")

    elif not input_data.bitwarden_cli_available:
        probe_status = BITWARDEN_CLI_REQUIRED
        next_stage = "install_or_authenticate_bitwarden_cli"
        blockers.append("bitwarden_cli_available is False")

    elif not input_data.bitwarden_item_read_success:
        probe_status = BITWARDEN_ITEM_READ_REQUIRED
        next_stage = "read_owner_approved_bitwarden_item"
        blockers.append("bitwarden_item_read_success is False")

    elif not input_data.broker_account_summary_read_success:
        probe_status = OANDA_PRACTICE_READ_ONLY_ACCOUNT_PROBE_REQUIRED
        next_stage = "oanda_practice_account_summary_read"
        blockers.append("broker_account_summary_read_success is False")

    else:
        probe_status = BROKER_RUNTIME_READ_ONLY_AUTH_PROVEN
        next_stage = "execution_control_stack"
        blockers = []
        redaction_status = "redaction_required_boundaries_honored"

    if not blockers:
        redaction_status = "redaction_required_boundaries_honored"

    return BrokerRuntimeReadOnlyAuthProbeResult(
        probe_status=probe_status,
        current_stage=current_stage,
        next_stage=next_stage,
        blockers=blockers,
        broker_runtime_item_ref=input_data.broker_runtime_item_ref,
        redaction_status=redaction_status,
        bitwarden_cli_called=bool(input_data.bitwarden_cli_called),
        bitwarden_vault_read=bool(input_data.bitwarden_vault_read),
        credentials_read=bool(input_data.credentials_read),
        env_file_read=bool(input_data.env_file_read),
        broker_api_called=bool(input_data.broker_api_called),
        order_execution=False,
        demo_authorized=False,
        live_authorized=False,
        safe_next_action=_safe_next_action(probe_status),
    )


def redact_sensitive_values(
    payload: dict[str, Any],
    *,
    token: str,
    account_id: str,
) -> dict[str, Any]:
    redacted_token = token or ""
    redacted_account = account_id or ""

    def _redact(value: Any) -> Any:
        if isinstance(value, str):
            redacted = value
            if redacted_token:
                redacted = redacted.replace(redacted_token, REDACTION_TOKEN_MARKER)
            if redacted_account:
                redacted = redacted.replace(redacted_account, REDACTION_ACCOUNT_MARKER)
            return redacted
        if isinstance(value, list):
            return [_redact(item) for item in value]
        if isinstance(value, dict):
            return {key: _redact(child) for key, child in value.items()}
        return value

    return _redact(payload)


def input_as_dict(input_data: BrokerRuntimeReadOnlyAuthProbeInput) -> dict[str, Any]:
    return asdict(input_data)


def result_as_dict(result: BrokerRuntimeReadOnlyAuthProbeResult) -> dict[str, Any]:
    return asdict(result)


def _safe_next_action(status: str) -> str:
    actions = {
        CREDENTIAL_REFERENCE_HANDOFF_REQUIRED: "Create and land the bitwarden credential reference handoff packet.",
        REFERENCE_CONTRACT_MISMATCH: "Repair broker runtime reference contract to match exact policy.",
        SECRET_LOGGING_REJECTED: "Remove secret logging from all probe outputs.",
        ENV_FILE_READ_REJECTED: "Remove `.env` reads from this packet.",
        LIVE_ENDPOINT_REJECTED: "Use only https://api-fxpractice.oanda.com.",
        ORDER_PATH_REJECTED: "Remove all order path and order execution branches.",
        BROKER_RUNTIME_READ_ONLY_AUTH_PROBE_READY: "Run with --owner-approved-read-only-probe when owner is ready.",
        OWNER_READ_ONLY_APPROVAL_REQUIRED: "Collect owner runtime approval and rerun with explicit approval flag.",
        BW_SESSION_REQUIRED: "Set BW_SESSION in process environment.",
        BITWARDEN_CLI_REQUIRED: "Install/authorize Bitwarden CLI for this user.",
        BITWARDEN_ITEM_READ_REQUIRED: "Load and parse the approved Bitwarden item reference.",
        OANDA_PRACTICE_READ_ONLY_ACCOUNT_PROBE_REQUIRED: "Call OANDA practice account summary read endpoint.",
        BROKER_RUNTIME_READ_ONLY_AUTH_PROVEN: (
            "Move to execution control stack and keep this packet read-only."
        ),
    }
    return actions.get(status, "Review runtime auth contract for missing approvals.")


def _reference_contract_matches(input_data: BrokerRuntimeReadOnlyAuthProbeInput) -> bool:
    return (
        input_data.broker_runtime_item_ref == DEFAULT_BROKER_RUNTIME_ITEM_REF
        and input_data.broker_api_token_field_ref == DEFAULT_BROKER_API_TOKEN_FIELD_REF
        and input_data.broker_account_id_field_ref == DEFAULT_BROKER_ACCOUNT_ID_FIELD_REF
        and input_data.endpoint_field_ref == DEFAULT_ENDPOINT_FIELD_REF
        and input_data.environment_field_ref == DEFAULT_ENVIRONMENT_FIELD_REF
        and input_data.allowed_mode_field_ref == DEFAULT_ALLOWED_MODE_FIELD_REF
        and input_data.expected_endpoint == DEFAULT_ENDPOINT
        and input_data.expected_environment == DEFAULT_ENVIRONMENT
        and input_data.expected_allowed_mode == DEFAULT_ALLOWED_MODE
    )


__all__ = [
    "BrokerRuntimeReadOnlyAuthProbeInput",
    "BrokerRuntimeReadOnlyAuthProbeResult",
    "evaluate_broker_runtime_read_only_auth_probe",
    "build_default_input",
    "input_as_dict",
    "result_as_dict",
    "redact_sensitive_values",
    "CURRENT_STAGE",
    "BROKER_RUNTIME_READ_ONLY_AUTH_PROBE_READY",
    "CREDENTIAL_REFERENCE_HANDOFF_REQUIRED",
    "REFERENCE_CONTRACT_MISMATCH",
    "SECRET_LOGGING_REJECTED",
    "ENV_FILE_READ_REJECTED",
    "LIVE_ENDPOINT_REJECTED",
    "ORDER_PATH_REJECTED",
    "OWNER_READ_ONLY_APPROVAL_REQUIRED",
    "BW_SESSION_REQUIRED",
    "BITWARDEN_CLI_REQUIRED",
    "BITWARDEN_ITEM_READ_REQUIRED",
    "OANDA_PRACTICE_READ_ONLY_ACCOUNT_PROBE_REQUIRED",
    "BROKER_RUNTIME_READ_ONLY_AUTH_PROVEN",
    "DEFAULT_BROKER_RUNTIME_ITEM_REF",
    "DEFAULT_BROKER_API_TOKEN_FIELD_REF",
    "DEFAULT_BROKER_ACCOUNT_ID_FIELD_REF",
    "DEFAULT_ENDPOINT_FIELD_REF",
    "DEFAULT_ENVIRONMENT_FIELD_REF",
    "DEFAULT_ALLOWED_MODE_FIELD_REF",
    "DEFAULT_ENDPOINT",
    "DEFAULT_ENVIRONMENT",
    "DEFAULT_ALLOWED_MODE",
    "REDACTION_TOKEN_MARKER",
    "REDACTION_ACCOUNT_MARKER",
]
