from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


PACKET_NAME = (
    "AIOS FOREX OANDA DEMO RUNTIME AUTH BOUNDARY READ ONLY HELPER REPAIR V1"
)
REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_RUNTIME_AUTH_BOUNDARY_READ_ONLY_HELPER_REPAIR_V1_REPORT.md"
)

CAMPAIGN_PACKET = 6
TRADE_ID = 320
TRADE_ID_TEXT = "320"
INSTRUMENT = "EUR_USD"

RUNTIME_AUTH_BOUNDARY_READY_FOR_OWNER_RUN_READ_ONLY_HELPER = (
    "RUNTIME_AUTH_BOUNDARY_READY_FOR_OWNER_RUN_READ_ONLY_HELPER"
)
READ_ONLY_HELPER_CONTRACT_READY = "READ_ONLY_HELPER_CONTRACT_READY"
READ_ONLY_HELPER_RESULT_ACCEPTED_SANITIZED = (
    "READ_ONLY_HELPER_RESULT_ACCEPTED_SANITIZED"
)
READ_ONLY_HELPER_RESULT_REJECTED_UNSANITIZED = (
    "READ_ONLY_HELPER_RESULT_REJECTED_UNSANITIZED"
)
READ_ONLY_HELPER_MISSING = "READ_ONLY_HELPER_MISSING"
BROKER_EVIDENCE_BLOCKED = "BROKER_EVIDENCE_BLOCKED"
SECRET_RISK_DETECTED = "SECRET_RISK_DETECTED"
INVALID_RUNTIME_AUTH_BOUNDARY_EVIDENCE = (
    "INVALID_RUNTIME_AUTH_BOUNDARY_EVIDENCE"
)

OWNER_RUN_READ_ONLY_BROKER_REQUESTED = "OWNER_RUN_READ_ONLY_BROKER_REQUESTED"
OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE = (
    "OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE"
)
FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE = (
    "FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE"
)
INTERNAL_LEDGER_ONLY = "INTERNAL_LEDGER_ONLY"

DEFAULT_NEXT_ACTION = "OWNER_RUN_SAFE_HELPER_CAN_BE_WIRED_AFTER_CONTRACT_REVIEW"
ACCEPTED_NEXT_ACTION = "USE_SANITIZED_HELPER_RESULT_FOR_DASHBOARD_TELEMETRY"
UNSANITIZED_NEXT_ACTION = "RETURN_ONLY_ALLOWED_SANITIZED_HELPER_FIELDS"
SECRET_NEXT_ACTION = "STOP_REMOVE_SECRET_FIELDS_AND_RETRY_SANITIZED_HELPER_RESULT"
MISSING_NEXT_ACTION = "WIRE_OWNER_RUN_READ_ONLY_HELPER_TO_THIS_CONTRACT"
BROKER_BLOCKED_NEXT_ACTION = "REPAIR_READ_ONLY_HELPER_OR_RUNTIME_AUTH_BOUNDARY"
INVALID_NEXT_ACTION = "FIX_RUNTIME_AUTH_BOUNDARY_EVIDENCE_SCHEMA"

ACCEPTED_SANITIZED_FIELDS = (
    "trade_id",
    "instrument",
    "side",
    "units",
    "entry_price",
    "realized_pl",
    "unrealized_pl",
    "open_trade_count",
    "open_position_count",
    "monitor_bucket",
    "result_bucket",
    "broker_read_mode",
    "broker_evidence_status",
    "evidence_timestamp_utc",
    "evidence_source",
)

REJECTED_SECRET_FIELD_NAMES = (
    "access_token",
    "account_id",
    "account_identifier",
    "account_number",
    "api_key",
    "apikey",
    "auth_header",
    "authorization",
    "bearer_token",
    "credential",
    "credentials",
    "password",
    "private_key",
    "refresh_token",
    "secret",
    "token",
    "vault_value",
    "headers",
    "http_headers",
    "live_account_id",
    "transaction_id",
)

REJECTED_RAW_PAYLOAD_FIELD_NAMES = (
    "raw_broker_payload",
    "raw_payload",
    "raw_request",
    "raw_response",
    "request_body",
    "response_body",
    "live_payload",
)

SECRET_KEY_TERMS = (
    "access_token",
    "account_id",
    "account_identifier",
    "account_number",
    "api_key",
    "apikey",
    "auth_header",
    "authorization",
    "bearer_token",
    "credential",
    "password",
    "private_key",
    "refresh_token",
    "secret",
    "token",
    "vault_value",
    "http_headers",
    "live_account_id",
    "transaction_id",
)

RAW_PAYLOAD_KEY_TERMS = (
    "raw_broker_payload",
    "raw_payload",
    "raw_request",
    "raw_response",
    "request_body",
    "response_body",
    "live_payload",
)

SAFE_AUDIT_FIELD_NAMES = {
    "broker_network_call_performed",
    "broker_read_allowed_by_default",
    "broker_read_must_be_get_only",
    "broker_read_requires_owner_flag",
    "no_broker_state_modified",
    "no_live_trade_placed",
    "no_new_order_placed",
    "no_secret_write_required",
    "no_secrets_written",
    "order_close_performed",
    "order_mutation_performed",
    "order_placement_performed",
    "position_mutation_performed",
    "sanitized_evidence_only",
    "secrets_written",
    "trade_mutation_performed",
}

MUTATION_TRUE_FIELDS = (
    "order_placement_performed",
    "order_close_performed",
    "order_mutation_performed",
    "trade_mutation_performed",
    "position_mutation_performed",
    "broker_write_performed",
    "broker_state_modified",
    "live_endpoint_used",
    "live_trade_placed",
    "new_order_placed",
    "secrets_written",
)

SAFETY_FALSE_FIELDS = (
    "no_new_order_placed",
    "no_live_trade_placed",
    "no_broker_state_modified",
    "no_secrets_written",
)

MONEY_MOVEMENT_TRUE_FIELDS = (
    "withdrawal_allowed_now",
    "transfer_allowed_now",
    "money_movement_allowed_now",
    "withdrawal_performed",
    "transfer_performed",
    "money_movement_performed",
)

BROKER_BLOCKED_STATUSES = {
    BROKER_EVIDENCE_BLOCKED,
    "BLOCKED_BY_MISSING_VAULT_ADAPTER",
    "BLOCKED_BY_MISSING_TOKEN",
    "BLOCKED_BY_MISSING_ACCOUNT_ID",
    "BLOCKED_BY_UNSAFE_CONTEXT",
    "BLOCKED_BY_UNSAFE_ENDPOINT",
    "BLOCKED_BY_MISSING_HTTP_GET_ADAPTER",
    "BLOCKED_BY_READ_ONLY_PL_CAPTURE_FAILURE",
    "BLOCKED_MISSING_REQUIRED_CONFIRMATIONS",
}


def evaluate_runtime_auth_boundary_read_only_helper_repair(
    evidence: dict | None = None,
) -> dict[str, Any]:
    if evidence is None:
        return _result(
            runtime_auth_boundary_status=READ_ONLY_HELPER_CONTRACT_READY,
            read_only_helper_contract_ready=True,
            sanitized_broker_telemetry_ready=False,
            broker_evidence_status=BROKER_EVIDENCE_BLOCKED,
            accepted_sanitized_fields=[],
            rejected_secret_fields=[],
            rejected_raw_payload_fields=[],
            blockers=[],
            next_action=DEFAULT_NEXT_ACTION,
        )
    return validate_sanitized_read_only_helper_result(evidence)


def validate_sanitized_read_only_helper_result(helper_result: dict) -> dict[str, Any]:
    if not isinstance(helper_result, Mapping):
        return _result(
            runtime_auth_boundary_status=INVALID_RUNTIME_AUTH_BOUNDARY_EVIDENCE,
            read_only_helper_contract_ready=True,
            sanitized_broker_telemetry_ready=False,
            broker_evidence_status=INVALID_RUNTIME_AUTH_BOUNDARY_EVIDENCE,
            accepted_sanitized_fields=[],
            rejected_secret_fields=[],
            rejected_raw_payload_fields=[],
            blockers=["helper_result_must_be_mapping"],
            next_action=INVALID_NEXT_ACTION,
        )

    secret_fields = _secret_field_paths(helper_result)
    raw_payload_fields = _raw_payload_field_paths(helper_result)
    if secret_fields:
        return _result(
            runtime_auth_boundary_status=SECRET_RISK_DETECTED,
            read_only_helper_contract_ready=True,
            sanitized_broker_telemetry_ready=False,
            broker_evidence_status=SECRET_RISK_DETECTED,
            accepted_sanitized_fields=_accepted_fields(helper_result),
            rejected_secret_fields=secret_fields,
            rejected_raw_payload_fields=raw_payload_fields,
            blockers=[f"forbidden_secret_field_{field}" for field in secret_fields],
            next_action=SECRET_NEXT_ACTION,
        )

    if raw_payload_fields:
        return _result(
            runtime_auth_boundary_status=READ_ONLY_HELPER_RESULT_REJECTED_UNSANITIZED,
            read_only_helper_contract_ready=True,
            sanitized_broker_telemetry_ready=False,
            broker_evidence_status=READ_ONLY_HELPER_RESULT_REJECTED_UNSANITIZED,
            accepted_sanitized_fields=_accepted_fields(helper_result),
            rejected_secret_fields=[],
            rejected_raw_payload_fields=raw_payload_fields,
            blockers=[
                f"forbidden_raw_payload_field_{field}"
                for field in raw_payload_fields
            ],
            next_action=UNSANITIZED_NEXT_ACTION,
        )

    missing_blockers = _missing_helper_blockers(helper_result)
    if missing_blockers:
        return _result(
            runtime_auth_boundary_status=READ_ONLY_HELPER_MISSING,
            read_only_helper_contract_ready=True,
            sanitized_broker_telemetry_ready=False,
            broker_evidence_status=READ_ONLY_HELPER_MISSING,
            accepted_sanitized_fields=_accepted_fields(helper_result),
            rejected_secret_fields=[],
            rejected_raw_payload_fields=[],
            blockers=missing_blockers,
            next_action=MISSING_NEXT_ACTION,
        )

    invalid_blockers = _invalid_contract_blockers(helper_result)
    if invalid_blockers:
        return _result(
            runtime_auth_boundary_status=INVALID_RUNTIME_AUTH_BOUNDARY_EVIDENCE,
            read_only_helper_contract_ready=True,
            sanitized_broker_telemetry_ready=False,
            broker_evidence_status=INVALID_RUNTIME_AUTH_BOUNDARY_EVIDENCE,
            accepted_sanitized_fields=_accepted_fields(helper_result),
            rejected_secret_fields=[],
            rejected_raw_payload_fields=[],
            blockers=invalid_blockers,
            next_action=INVALID_NEXT_ACTION,
        )

    broker_blockers = _broker_blocked_blockers(helper_result)
    if broker_blockers:
        return _result(
            runtime_auth_boundary_status=BROKER_EVIDENCE_BLOCKED,
            read_only_helper_contract_ready=True,
            sanitized_broker_telemetry_ready=False,
            broker_evidence_status=BROKER_EVIDENCE_BLOCKED,
            accepted_sanitized_fields=_accepted_fields(helper_result),
            rejected_secret_fields=[],
            rejected_raw_payload_fields=[],
            blockers=broker_blockers,
            next_action=BROKER_BLOCKED_NEXT_ACTION,
        )

    accepted = _accepted_fields(helper_result)
    if not accepted:
        return _result(
            runtime_auth_boundary_status=INVALID_RUNTIME_AUTH_BOUNDARY_EVIDENCE,
            read_only_helper_contract_ready=True,
            sanitized_broker_telemetry_ready=False,
            broker_evidence_status=INVALID_RUNTIME_AUTH_BOUNDARY_EVIDENCE,
            accepted_sanitized_fields=[],
            rejected_secret_fields=[],
            rejected_raw_payload_fields=[],
            blockers=["at_least_one_accepted_sanitized_field_required"],
            next_action=INVALID_NEXT_ACTION,
        )

    return _result(
        runtime_auth_boundary_status=READ_ONLY_HELPER_RESULT_ACCEPTED_SANITIZED,
        read_only_helper_contract_ready=True,
        sanitized_broker_telemetry_ready=True,
        broker_evidence_status=READ_ONLY_HELPER_RESULT_ACCEPTED_SANITIZED,
        accepted_sanitized_fields=accepted,
        rejected_secret_fields=[],
        rejected_raw_payload_fields=[],
        blockers=[],
        next_action=ACCEPTED_NEXT_ACTION,
    )


def render_runtime_auth_boundary_read_only_helper_repair_report(
    result: Mapping[str, Any],
    *,
    branch: str = "UNKNOWN",
) -> str:
    blockers = result.get("blockers")
    blocker_text = ", ".join(str(item) for item in blockers) if blockers else "none"
    return "\n".join(
        [
            "# AIOS FOREX OANDA DEMO RUNTIME AUTH BOUNDARY READ ONLY HELPER REPAIR V1 REPORT",
            "",
            f"- packet_name: {PACKET_NAME}",
            f"- repo_branch: {branch}",
            "- pr_1078_anchor: read-only broker telemetry repair diagnostics",
            "- current_blocker: BROKER_EVIDENCE_BLOCKED",
            "",
            "## Runtime Auth Boundary Status",
            "",
            (
                "- runtime_auth_boundary_status: "
                f"{result.get('runtime_auth_boundary_status')}"
            ),
            (
                "- read_only_helper_contract_ready: "
                f"{_true_false(result.get('read_only_helper_contract_ready'))}"
            ),
            f"- broker_evidence_status: {result.get('broker_evidence_status')}",
            (
                "- sanitized_broker_telemetry_ready: "
                f"{_true_false(result.get('sanitized_broker_telemetry_ready'))}"
            ),
            f"- next_action: {result.get('next_action')}",
            f"- blockers: {blocker_text}",
            "",
            "## Read-Only Helper Contract",
            "",
            (
                "- owner_run_required: "
                f"{_true_false(result.get('owner_run_required'))}"
            ),
            (
                "- broker_read_allowed_by_default: "
                f"{_true_false(result.get('broker_read_allowed_by_default'))}"
            ),
            (
                "- broker_read_requires_owner_flag: "
                f"{_true_false(result.get('broker_read_requires_owner_flag'))}"
            ),
            (
                "- broker_read_must_be_get_only: "
                f"{_true_false(result.get('broker_read_must_be_get_only'))}"
            ),
            (
                "- raw_broker_payload_persistence_allowed: "
                f"{_true_false(result.get('raw_broker_payload_persistence_allowed'))}"
            ),
            (
                "- account_identifier_logging_allowed: "
                f"{_true_false(result.get('account_identifier_logging_allowed'))}"
            ),
            (
                "- auth_header_logging_allowed: "
                f"{_true_false(result.get('auth_header_logging_allowed'))}"
            ),
            (
                "- token_logging_allowed: "
                f"{_true_false(result.get('token_logging_allowed'))}"
            ),
            "",
            "## Accepted Sanitized Fields",
            "",
            *[f"- {field}" for field in ACCEPTED_SANITIZED_FIELDS],
            "",
            "## Rejected Secret Or Raw Payload Fields",
            "",
            *[f"- {field}" for field in REJECTED_SECRET_FIELD_NAMES],
            *[f"- {field}" for field in REJECTED_RAW_PAYLOAD_FIELD_NAMES],
            "",
            "## Real Broker Telemetry Doctrine",
            "",
            "- real broker telemetry is the dashboard goal when owner-authorized",
            "- fake/mock dashboard account values are forbidden",
            (
                "- dashboard_real_broker_telemetry_goal: "
                f"{_true_false(result.get('dashboard_real_broker_telemetry_goal'))}"
            ),
            (
                "- dashboard_fake_numbers_allowed: "
                f"{_true_false(result.get('dashboard_fake_numbers_allowed'))}"
            ),
            (
                "- dashboard_mock_numbers_allowed: "
                f"{_true_false(result.get('dashboard_mock_numbers_allowed'))}"
            ),
            f"- broker_data_source_required: {result.get('broker_data_source_required')}",
            f"- bank_data_source_required: {result.get('bank_data_source_required')}",
            "",
            "## Bank And Money Movement Boundary",
            "",
            "- bank telemetry remains a future separate read-only lane",
            "- withdrawals, transfers, and money movement remain blocked",
            (
                "- withdrawal_allowed_now: "
                f"{_true_false(result.get('withdrawal_allowed_now'))}"
            ),
            (
                "- transfer_allowed_now: "
                f"{_true_false(result.get('transfer_allowed_now'))}"
            ),
            (
                "- money_movement_allowed_now: "
                f"{_true_false(result.get('money_movement_allowed_now'))}"
            ),
            f"- profit_reserve_bucket_mode: {result.get('profit_reserve_bucket_mode')}",
            "",
            "## Safety Statements",
            "",
            "- no new order placed",
            "- no live trade placed",
            "- no broker state modified",
            "- no secrets written",
            "",
            "## Machine Result",
            "",
            f"- campaign_packet: {result.get('campaign_packet')}",
            f"- trade_id: {result.get('trade_id')}",
            (
                "- no_new_order_placed: "
                f"{_true_false(result.get('no_new_order_placed'))}"
            ),
            (
                "- no_live_trade_placed: "
                f"{_true_false(result.get('no_live_trade_placed'))}"
            ),
            (
                "- no_broker_state_modified: "
                f"{_true_false(result.get('no_broker_state_modified'))}"
            ),
            (
                "- no_secrets_written: "
                f"{_true_false(result.get('no_secrets_written'))}"
            ),
            "",
        ]
    )


def write_runtime_auth_boundary_read_only_helper_repair_report(
    result: Mapping[str, Any],
    report_path: str | Path = REPORT_PATH,
    *,
    branch: str = "UNKNOWN",
) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_runtime_auth_boundary_read_only_helper_repair_report(
            result,
            branch=branch,
        ),
        encoding="utf-8",
    )
    return path


def _result(
    *,
    runtime_auth_boundary_status: str,
    read_only_helper_contract_ready: bool,
    sanitized_broker_telemetry_ready: bool,
    broker_evidence_status: str,
    accepted_sanitized_fields: Sequence[str],
    rejected_secret_fields: Sequence[str],
    rejected_raw_payload_fields: Sequence[str],
    blockers: Sequence[str],
    next_action: str,
) -> dict[str, Any]:
    return {
        "packet_name": PACKET_NAME,
        "campaign_packet": CAMPAIGN_PACKET,
        "trade_id": TRADE_ID,
        "runtime_auth_boundary_status": runtime_auth_boundary_status,
        "read_only_helper_contract_ready": read_only_helper_contract_ready,
        "owner_run_required": True,
        "broker_read_allowed_by_default": False,
        "broker_read_requires_owner_flag": True,
        "broker_read_must_be_get_only": True,
        "raw_broker_payload_persistence_allowed": False,
        "account_identifier_logging_allowed": False,
        "auth_header_logging_allowed": False,
        "token_logging_allowed": False,
        "sanitized_broker_telemetry_ready": sanitized_broker_telemetry_ready,
        "accepted_sanitized_fields": _unique(accepted_sanitized_fields),
        "rejected_secret_fields": _unique(rejected_secret_fields),
        "rejected_raw_payload_fields": _unique(rejected_raw_payload_fields),
        "broker_evidence_status": broker_evidence_status,
        "dashboard_real_broker_telemetry_goal": True,
        "dashboard_fake_numbers_allowed": False,
        "dashboard_mock_numbers_allowed": False,
        "broker_data_source_required": OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE,
        "bank_data_source_required": FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE,
        "withdrawal_allowed_now": False,
        "transfer_allowed_now": False,
        "money_movement_allowed_now": False,
        "profit_reserve_bucket_mode": INTERNAL_LEDGER_ONLY,
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
        "blockers": _unique(blockers),
        "next_action": next_action,
    }


def _accepted_fields(helper_result: Mapping[str, Any]) -> list[str]:
    accepted: list[str] = []
    for field in ACCEPTED_SANITIZED_FIELDS:
        if field in helper_result and _safe_scalar(helper_result.get(field)):
            accepted.append(field)
    return accepted


def _secret_field_paths(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    rejected: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = path + (key_text,)
            if _secret_key(key_text):
                rejected.append(_safe_path(child_path))
                continue
            rejected.extend(_secret_field_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rejected.extend(_secret_field_paths(child, path + (str(index),)))
    elif isinstance(value, str):
        lowered = value.lower()
        if "bearer " in lowered or "authorization:" in lowered or "sk-" in lowered:
            rejected.append(_safe_path(path))
    return _unique(rejected)


def _raw_payload_field_paths(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    rejected: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = path + (key_text,)
            if _raw_payload_key(key_text):
                rejected.append(_safe_path(child_path))
                continue
            rejected.extend(_raw_payload_field_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rejected.extend(_raw_payload_field_paths(child, path + (str(index),)))
    return _unique(rejected)


def _missing_helper_blockers(helper_result: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if helper_result.get("read_only_helper_missing") is True:
        blockers.append("read_only_helper_missing_true")
    if helper_result.get("safe_read_only_helper_available") is False:
        blockers.append("safe_read_only_helper_available_false")
    for field in ("helper_status", "runtime_auth_boundary_status", "status"):
        value = helper_result.get(field)
        if value is None:
            continue
        lowered = str(value).strip().lower()
        if "helper_missing" in lowered or "read_only_helper_missing" in lowered:
            blockers.append(f"read_only_helper_missing_{_safe_label(value)}")
    return _unique(blockers)


def _invalid_contract_blockers(helper_result: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    trade_id = helper_result.get("trade_id")
    if trade_id is not None and str(trade_id).strip() != TRADE_ID_TEXT:
        blockers.append("trade_id_must_be_320")
    instrument = helper_result.get("instrument")
    if instrument is not None and str(instrument).strip() != INSTRUMENT:
        blockers.append("instrument_must_be_EUR_USD")
    method = helper_result.get("broker_read_method") or helper_result.get("method")
    if method is not None and str(method).strip().upper() != "GET":
        blockers.append("broker_read_method_must_be_get")
    broker_read_mode = str(helper_result.get("broker_read_mode", ""))
    if "LIVE" in broker_read_mode.upper():
        blockers.append("broker_read_mode_must_not_be_live")
    for field in MUTATION_TRUE_FIELDS:
        if helper_result.get(field) is True:
            blockers.append(f"unsafe_{field}_true")
    for field in SAFETY_FALSE_FIELDS:
        if helper_result.get(field) is False:
            blockers.append(f"{field}_must_not_be_false")
    for field in MONEY_MOVEMENT_TRUE_FIELDS:
        if helper_result.get(field) is True:
            blockers.append(f"{field}_must_not_be_true")
    if helper_result.get("dashboard_fake_numbers_allowed") is True:
        blockers.append("dashboard_fake_numbers_must_not_be_allowed")
    if helper_result.get("dashboard_mock_numbers_allowed") is True:
        blockers.append("dashboard_mock_numbers_must_not_be_allowed")
    if helper_result.get("sanitized_evidence_only") is False:
        blockers.append("sanitized_evidence_only_must_not_be_false")
    if helper_result.get("profit_reserve_bucket_mode") not in {None, INTERNAL_LEDGER_ONLY}:
        blockers.append("profit_reserve_bucket_mode_must_be_internal_ledger_only")
    return _unique(blockers)


def _broker_blocked_blockers(helper_result: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if helper_result.get("broker_evidence_blocked") is True:
        blockers.append("broker_evidence_blocked_true")
    for field in (
        "broker_evidence_status",
        "gate_status",
        "helper_status",
        "script_status",
        "status",
        "status_bucket",
        "result_bucket",
        "pl_capture_classification",
    ):
        value = helper_result.get(field)
        if _is_broker_blocked_status(value):
            blockers.append(f"broker_evidence_blocked_{_safe_label(value)}")
    for blocker in _sequence(helper_result.get("blockers")):
        lowered = str(blocker).lower()
        if "blocked" in lowered or "broker" in lowered or "vault" in lowered:
            blockers.append(f"broker_blocker_{_safe_label(blocker)}")
    return _unique(blockers)


def _is_broker_blocked_status(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    return (
        text in BROKER_BLOCKED_STATUSES
        or text.startswith("BLOCKED_")
        or text.startswith("BROKER_EVIDENCE_BLOCKED")
    )


def _secret_key(key: str) -> bool:
    key_text = key.lower()
    if key_text in SAFE_AUDIT_FIELD_NAMES or key_text in {
        "credential_name",
        "credential_names",
    }:
        return False
    return key_text in REJECTED_SECRET_FIELD_NAMES or any(
        term in key_text for term in SECRET_KEY_TERMS
    )


def _raw_payload_key(key: str) -> bool:
    key_text = key.lower()
    return key_text in REJECTED_RAW_PAYLOAD_FIELD_NAMES or any(
        term in key_text for term in RAW_PAYLOAD_KEY_TERMS
    )


def _safe_scalar(value: Any) -> bool:
    return isinstance(value, (str, int, float)) and not isinstance(value, bool)


def _sequence(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return list(value)
    if value:
        return [value]
    return []


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            unique.append(text)
    return unique


def _safe_path(path: Sequence[str]) -> str:
    text = "_".join(_safe_label(part) for part in path if str(part).strip())
    return text or "root"


def _safe_label(value: Any) -> str:
    text = str(value).strip().lower()
    cleaned = "".join(char if char.isalnum() else "_" for char in text)
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_")[:80] or "unknown"


def _true_false(value: Any) -> str:
    return "true" if value is True else "false"
