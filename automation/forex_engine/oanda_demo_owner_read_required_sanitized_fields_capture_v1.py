from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from automation.forex_engine.oanda_demo_sanitized_evidence_normalizer_acceptance_run_v1 import (
    SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED,
    run_sanitized_evidence_normalizer_acceptance,
)
from automation.forex_engine.oanda_demo_sanitized_owner_run_read_only_telemetry_adapter_v1 import (
    ALLOWED_SANITIZED_FIELDS,
    INTERNAL_LEDGER_ONLY,
)


PACKET_NAME = (
    "AIOS FOREX OANDA DEMO OWNER READ REQUIRED SANITIZED FIELDS CAPTURE V1"
)
PACKET_ID = (
    "AIOS-FOREX-OANDA-DEMO-PACKET-12B-OWNER-READ-REQUIRED-SANITIZED-FIELDS-CAPTURE-V1"
)
REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_V1_REPORT.md"
)
DEFAULT_JSON_PATH = (
    "Reports/forex_delivery/"
    "oanda_demo_packet09_sanitized_owner_run_telemetry_evidence_v1.json"
)

REQUIRED_SANITIZED_OUTPUT_FIELDS = tuple(ALLOWED_SANITIZED_FIELDS)
SAFE_AUDIT_EXPORT_FIELDS = (
    "broker_network_call_performed",
    "broker_read_performed",
    "live_endpoint_used",
    "order_placement_performed",
    "order_mutation_performed",
    "order_close_performed",
    "position_mutation_performed",
    "trade_mutation_performed",
    "raw_broker_payload_persisted",
    "secrets_written",
    "no_new_order_placed",
    "no_live_trade_placed",
    "no_broker_state_modified",
    "no_secrets_written",
)
EXPORT_FIELD_SET = set(REQUIRED_SANITIZED_OUTPUT_FIELDS) | set(
    SAFE_AUDIT_EXPORT_FIELDS,
)

SAFE_TRUE_AUDIT_FIELDS = {
    "no_new_order_placed",
    "no_live_trade_placed",
    "no_broker_state_modified",
    "no_secrets_written",
}
SAFE_FALSE_AUDIT_FIELDS = {
    "secrets_written",
    "raw_broker_payload_persisted",
    "credential_read_performed",
    "account_id_read_performed",
    "live_endpoint_used",
    "order_placement_performed",
    "order_mutation_performed",
    "order_close_performed",
    "position_mutation_performed",
    "trade_mutation_performed",
}
SAFE_FALSE_CONTROL_FIELDS = {
    "dashboard_fake_numbers_allowed",
    "dashboard_mock_numbers_allowed",
    "withdrawal_allowed_now",
    "transfer_allowed_now",
    "money_movement_allowed_now",
}

FORBIDDEN_SECRET_MARKERS = {
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
}
FORBIDDEN_RAW_PAYLOAD_MARKERS = {
    "raw_broker_payload",
    "raw_payload",
    "raw_request",
    "raw_response",
    "request_body",
    "response_body",
    "live_payload",
}
FAKE_MOCK_MARKERS = {
    "fake_dashboard_account_value",
    "mock_dashboard_account_value",
    "fake_dashboard_account_balance",
    "mock_dashboard_account_balance",
    "fake_account_balance",
    "mock_account_balance",
    "dashboard_fake_account_balance",
    "dashboard_mock_account_balance",
    "fake_dashboard_numbers",
    "mock_dashboard_numbers",
}

INT_FIELDS = {
    "trade_id",
    "units",
    "open_trade_count",
    "open_position_count",
}
BOOL_FIELDS = {
    "repeat_proof_eligible",
    "profit_evidence",
}

FIELD_ALIASES = {
    "trade_id": ("trade_id", "tradeID", "tradeId", "expected_trade_id", "id"),
    "instrument": ("instrument", "pair"),
    "side": ("side", "direction"),
    "units": ("units", "currentUnits", "current_units"),
    "entry_price": ("entry_price", "entry", "price", "open_price"),
    "realized_pl": ("realized_pl", "realizedPL", "pl", "profitLoss"),
    "unrealized_pl": ("unrealized_pl", "unrealizedPL", "trueUnrealizedPL"),
    "open_trade_count": ("open_trade_count", "openTradeCount"),
    "open_position_count": ("open_position_count", "openPositionCount"),
    "monitor_bucket": ("monitor_bucket", "status_bucket", "current_bucket_result"),
    "result_bucket": (
        "result_bucket",
        "pl_result_bucket",
        "pl_capture_classification",
    ),
    "repeat_proof_lane_status": ("repeat_proof_lane_status",),
    "repeat_proof_eligible": ("repeat_proof_eligible",),
    "profit_evidence": ("profit_evidence", "is_profit_evidence"),
    "broker_read_mode": ("broker_read_mode", "read_mode", "broker_mode"),
    "broker_evidence_status": ("broker_evidence_status",),
    "evidence_timestamp_utc": (
        "evidence_timestamp_utc",
        "timestamp_utc",
        "time",
        "lastTransactionTime",
    ),
    "evidence_source": ("evidence_source", "source"),
}

OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_NOT_REQUESTED = (
    "OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_NOT_REQUESTED"
)
OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_READY = (
    "OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_READY"
)
OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_WRITTEN = (
    "OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_WRITTEN"
)
OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_BLOCKED_MISSING_FIELDS = (
    "OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_BLOCKED_MISSING_FIELDS"
)
OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_REJECTED_SECRET_RISK = (
    "OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_REJECTED_SECRET_RISK"
)
OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_REJECTED_RAW_PAYLOAD_RISK = (
    "OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_REJECTED_RAW_PAYLOAD_RISK"
)
OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_REJECTED_UNSAFE_AUDIT_FLAG = (
    "OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_REJECTED_UNSAFE_AUDIT_FLAG"
)

DEFAULT_NEXT_ACTION = "SUPPLY_OWNER_RUN_SANITIZED_TELEMETRY_INPUT_FILE"
READY_NEXT_ACTION = "RUN_PACKET_11_ACCEPTANCE_WRAPPER_WITH_CAPTURED_JSON"
MISSING_NEXT_ACTION = (
    "OWNER_RUN_READ_HELPER_MUST_CAPTURE_REQUIRED_FIELDS_WITHOUT_RAW_PAYLOAD"
)
SECRET_NEXT_ACTION = "STOP_REMOVE_SECRET_MARKERS_AND_RETRY"
RAW_NEXT_ACTION = "STOP_REMOVE_RAW_PAYLOAD_MARKERS_AND_RETRY"
UNSAFE_AUDIT_NEXT_ACTION = "STOP_FIX_UNSAFE_AUDIT_FLAGS_AND_RETRY"
OWNER_SIDE_COMMAND = (
    "python scripts/forex_delivery/"
    "run_oanda_demo_owner_read_required_sanitized_fields_capture_v1.py "
    "--sanitized-input-file <safe_sanitized_owner_read_output.json> "
    "--write-json --json-path "
    "Reports/forex_delivery/oanda_demo_packet09_sanitized_owner_run_telemetry_evidence_v1.json "
    "--write-report --report-path "
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_V1_REPORT.md "
    "--json"
)


def capture_required_sanitized_fields_from_owner_read(
    sanitized_input: dict | None = None,
    write_json: bool = False,
    json_path: str | None = None,
) -> dict[str, Any]:
    output_path = json_path or DEFAULT_JSON_PATH
    if sanitized_input is None:
        return _result(
            capture_status=OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_NOT_REQUESTED,
            json_written=False,
            json_path=output_path,
            sanitized_evidence_ready=False,
            required_fields_present=False,
            missing_required_fields=[],
            rejected_forbidden_fields=[],
            unsafe_audit_flags=[],
            candidate={},
            next_action=DEFAULT_NEXT_ACTION,
        )

    if not isinstance(sanitized_input, Mapping):
        return _result(
            capture_status=(
                OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_BLOCKED_MISSING_FIELDS
            ),
            json_written=False,
            json_path=output_path,
            sanitized_evidence_ready=False,
            required_fields_present=False,
            missing_required_fields=list(REQUIRED_SANITIZED_OUTPUT_FIELDS),
            rejected_forbidden_fields=[],
            unsafe_audit_flags=[],
            candidate={},
            next_action=MISSING_NEXT_ACTION,
        )

    safety = _input_safety(sanitized_input)
    candidate = _normalized_output(sanitized_input)
    missing = _missing_required_fields(candidate)
    required_present = not missing
    json_written = False
    sanitized_ready = False

    if safety["secret_risk"]:
        status = OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_REJECTED_SECRET_RISK
        next_action = SECRET_NEXT_ACTION
    elif safety["raw_payload_risk"]:
        status = OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_REJECTED_RAW_PAYLOAD_RISK
        next_action = RAW_NEXT_ACTION
    elif safety["unsafe_audit_flags"]:
        status = (
            OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_REJECTED_UNSAFE_AUDIT_FLAG
        )
        next_action = UNSAFE_AUDIT_NEXT_ACTION
    elif not required_present:
        status = OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_BLOCKED_MISSING_FIELDS
        next_action = MISSING_NEXT_ACTION
    else:
        payload = _export_payload(candidate)
        acceptance = run_sanitized_evidence_normalizer_acceptance(payload)
        sanitized_ready = (
            acceptance.get("acceptance_status")
            == SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED
        )
        if sanitized_ready and write_json:
            _write_json_artifact(payload, output_path)
            json_written = True
            status = OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_WRITTEN
            next_action = READY_NEXT_ACTION
        elif sanitized_ready:
            status = OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_READY
            next_action = READY_NEXT_ACTION
        else:
            status = OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_BLOCKED_MISSING_FIELDS
            missing = _acceptance_missing_fields(acceptance)
            required_present = False
            next_action = MISSING_NEXT_ACTION

    return _result(
        capture_status=status,
        json_written=json_written,
        json_path=output_path,
        sanitized_evidence_ready=sanitized_ready,
        required_fields_present=required_present,
        missing_required_fields=missing,
        rejected_forbidden_fields=safety["rejected_forbidden_fields"],
        unsafe_audit_flags=safety["unsafe_audit_flags"],
        candidate=candidate,
        next_action=next_action,
    )


def run_owner_read_required_sanitized_fields_capture(
    sanitized_input: dict | None = None,
    write_json: bool = False,
    json_path: str | None = None,
) -> dict[str, Any]:
    return capture_required_sanitized_fields_from_owner_read(
        sanitized_input,
        write_json=write_json,
        json_path=json_path,
    )


def render_owner_read_required_sanitized_fields_capture_report(
    result: Mapping[str, Any],
    *,
    branch: str = "UNKNOWN",
) -> str:
    missing = _sequence_text(result.get("missing_required_fields"))
    rejected = _sequence_text(result.get("rejected_forbidden_fields"))
    unsafe = _sequence_text(result.get("unsafe_audit_flags"))
    return "\n".join(
        [
            "# AIOS FOREX OANDA DEMO OWNER READ REQUIRED SANITIZED FIELDS CAPTURE V1 REPORT",
            "",
            f"- packet_name: {PACKET_NAME}",
            f"- packet_id: {PACKET_ID}",
            "- pr_1087_anchor: OANDA sanitized Packet 09 JSON export locator",
            f"- repo_branch: {branch}",
            f"- capture_status: {_display(result.get('capture_status'))}",
            f"- json_written: {_yes_no(result.get('json_written'))}",
            f"- json_path: {_display(result.get('json_path'))}",
            (
                "- sanitized_evidence_ready: "
                f"{_yes_no(result.get('sanitized_evidence_ready'))}"
            ),
            (
                "- required_fields_present: "
                f"{_yes_no(result.get('required_fields_present'))}"
            ),
            f"- broker_read_performed: {_yes_no(result.get('broker_read_performed'))}",
            (
                "- broker_network_call_performed: "
                f"{_yes_no(result.get('broker_network_call_performed'))}"
            ),
            f"- next_action: {_display(result.get('next_action'))}",
            "",
            "## Missing Required Fields",
            "",
            *([f"- {field}" for field in missing] or ["- none"]),
            "",
            "## Rejected Forbidden Fields",
            "",
            *([f"- {field}" for field in rejected] or ["- none"]),
            "",
            "## Unsafe Audit Flags",
            "",
            *([f"- {field}" for field in unsafe] or ["- none"]),
            "",
            "## Safety Statements",
            "",
            "- no new order placed",
            "- no live trade placed",
            "- no broker state modified",
            "- no secrets written",
            "- raw broker payload persisted: false",
            "- fake/mock numbers forbidden",
            "- money movement blocked",
            "- profit reserve internal ledger only",
            "",
            "## Owner-Side Command",
            "",
            f"- {OWNER_SIDE_COMMAND}",
            "",
            "## Machine Result",
            "",
            f"- no_new_order_placed: {_true_false(result.get('no_new_order_placed'))}",
            f"- no_live_trade_placed: {_true_false(result.get('no_live_trade_placed'))}",
            (
                "- no_broker_state_modified: "
                f"{_true_false(result.get('no_broker_state_modified'))}"
            ),
            f"- no_secrets_written: {_true_false(result.get('no_secrets_written'))}",
            (
                "- raw_broker_payload_persisted: "
                f"{_true_false(result.get('raw_broker_payload_persisted'))}"
            ),
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
            (
                "- profit_reserve_bucket_mode: "
                f"{_display(result.get('profit_reserve_bucket_mode'))}"
            ),
            "",
        ]
    )


def write_owner_read_required_sanitized_fields_capture_report(
    result: Mapping[str, Any],
    report_path: str | Path = REPORT_PATH,
    *,
    branch: str = "UNKNOWN",
) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_owner_read_required_sanitized_fields_capture_report(
            result,
            branch=branch,
        ),
        encoding="utf-8",
    )
    return path


def _normalized_output(sanitized_input: Mapping[str, Any]) -> dict[str, Any]:
    primary = _primary_payload(sanitized_input)
    normalized: dict[str, Any] = {}

    for field in REQUIRED_SANITIZED_OUTPUT_FIELDS:
        value = _first_safe_value(
            primary,
            sanitized_input,
            keys=FIELD_ALIASES.get(field, (field,)),
        )
        normalized_value = _normalize_required_field(field, value)
        if normalized_value is not None:
            normalized[field] = normalized_value

    for field in SAFE_AUDIT_EXPORT_FIELDS:
        value = _first_safe_value(primary, sanitized_input, keys=(field,))
        if isinstance(value, bool):
            normalized[field] = value

    return normalized


def _primary_payload(sanitized_input: Mapping[str, Any]) -> Mapping[str, Any]:
    result = sanitized_input.get("result")
    if isinstance(result, Mapping):
        return result
    decision = sanitized_input.get("decision")
    if isinstance(decision, Mapping):
        result = decision.get("result")
        if isinstance(result, Mapping):
            return result
        return decision
    return sanitized_input


def _first_safe_value(
    *mappings: Mapping[str, Any],
    keys: Sequence[str],
) -> Any:
    for mapping in mappings:
        if not isinstance(mapping, Mapping):
            continue
        for key in keys:
            if key in mapping and _safe_scalar_or_bool(mapping.get(key)):
                return mapping.get(key)
    return None


def _normalize_required_field(field: str, value: Any) -> Any:
    if _missing_value(value):
        return None
    if field in BOOL_FIELDS:
        return value if isinstance(value, bool) else None
    if field in INT_FIELDS:
        return _coerce_int(value)
    if isinstance(value, bool):
        return None
    if isinstance(value, (str, int, float)):
        return str(value).strip()
    return None


def _input_safety(sanitized_input: Mapping[str, Any]) -> dict[str, Any]:
    secret_fields = _secret_field_paths(sanitized_input)
    raw_fields = _forbidden_key_paths(sanitized_input, FORBIDDEN_RAW_PAYLOAD_MARKERS)
    fake_fields = _fake_or_mock_field_paths(sanitized_input)
    unsafe = _unsafe_audit_flags(sanitized_input)
    return {
        "secret_risk": bool(secret_fields or fake_fields),
        "raw_payload_risk": bool(raw_fields),
        "rejected_forbidden_fields": _unique(secret_fields + raw_fields + fake_fields),
        "unsafe_audit_flags": unsafe,
    }


def _secret_field_paths(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    found = _forbidden_key_paths(value, FORBIDDEN_SECRET_MARKERS, path)
    if isinstance(value, Mapping):
        for key, child in value.items():
            found.extend(_secret_field_paths(child, path + (str(key),)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_secret_field_paths(child, path + (str(index),)))
    elif isinstance(value, str):
        lowered = value.lower()
        if "bearer " in lowered or "authorization:" in lowered or "sk-" in lowered:
            found.append(_safe_path(path))
    return _unique(found)


def _forbidden_key_paths(
    value: Any,
    markers: set[str],
    path: tuple[str, ...] = (),
) -> list[str]:
    found: list[str] = []
    normalized_markers = {_normalized_key(marker) for marker in markers}
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = path + (key_text,)
            normalized_key = _normalized_key(key_text)
            if normalized_key in normalized_markers:
                found.append(_safe_path(child_path))
                continue
            found.extend(_forbidden_key_paths(child, markers, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_forbidden_key_paths(child, markers, path + (str(index),)))
    return _unique(found)


def _fake_or_mock_field_paths(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    found: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = path + (key_text,)
            if _fake_or_mock_key(key_text):
                found.append(_safe_path(child_path))
                continue
            found.extend(_fake_or_mock_field_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_fake_or_mock_field_paths(child, path + (str(index),)))
    return _unique(found)


def _unsafe_audit_flags(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    unsafe: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = path + (key_text,)
            if key_text in SAFE_TRUE_AUDIT_FIELDS:
                if child is not True:
                    unsafe.append(_safe_path(child_path))
                continue
            if key_text in SAFE_FALSE_AUDIT_FIELDS:
                if child is not False:
                    unsafe.append(_safe_path(child_path))
                continue
            if key_text in SAFE_FALSE_CONTROL_FIELDS:
                if child is not False:
                    unsafe.append(_safe_path(child_path))
                continue
            if key_text == "profit_reserve_bucket_mode" and child != INTERNAL_LEDGER_ONLY:
                unsafe.append(_safe_path(child_path))
                continue
            unsafe.extend(_unsafe_audit_flags(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            unsafe.extend(_unsafe_audit_flags(child, path + (str(index),)))
    return _unique(unsafe)


def _missing_required_fields(candidate: Mapping[str, Any]) -> list[str]:
    return [
        field
        for field in REQUIRED_SANITIZED_OUTPUT_FIELDS
        if field not in candidate or _missing_value(candidate.get(field))
    ]


def _acceptance_missing_fields(acceptance: Mapping[str, Any]) -> list[str]:
    values = (
        _sequence_text(acceptance.get("missing_required_fields"))
        or _sequence_text(acceptance.get("blockers"))
        or ["packet11_acceptance_rejected"]
    )
    cleaned: list[str] = []
    for value in values:
        text = str(value)
        if text.endswith("_required"):
            text = text[: -len("_required")]
        cleaned.append(text)
    return _unique(cleaned)


def _write_json_artifact(candidate: Mapping[str, Any], json_path: str) -> None:
    path = Path(json_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dict(candidate), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _export_payload(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        field: candidate[field]
        for field in REQUIRED_SANITIZED_OUTPUT_FIELDS + SAFE_AUDIT_EXPORT_FIELDS
        if field in candidate
    }


def _result(
    *,
    capture_status: str,
    json_written: bool,
    json_path: str,
    sanitized_evidence_ready: bool,
    required_fields_present: bool,
    missing_required_fields: Sequence[str],
    rejected_forbidden_fields: Sequence[str],
    unsafe_audit_flags: Sequence[str],
    candidate: Mapping[str, Any],
    next_action: str,
) -> dict[str, Any]:
    return {
        "packet_name": PACKET_NAME,
        "packet_id": PACKET_ID,
        "capture_status": capture_status,
        "json_written": json_written,
        "json_path": json_path,
        "sanitized_evidence_ready": sanitized_evidence_ready,
        "required_fields_present": required_fields_present,
        "missing_required_fields": list(missing_required_fields),
        "rejected_forbidden_fields": list(rejected_forbidden_fields),
        "unsafe_audit_flags": list(unsafe_audit_flags),
        "broker_read_performed": candidate.get("broker_read_performed") is True,
        "broker_network_call_performed": (
            candidate.get("broker_network_call_performed") is True
        ),
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
        "raw_broker_payload_persisted": False,
        "withdrawal_allowed_now": False,
        "transfer_allowed_now": False,
        "money_movement_allowed_now": False,
        "profit_reserve_bucket_mode": INTERNAL_LEDGER_ONLY,
        "next_action": next_action,
    }


def _missing_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {
            "",
            "unknown",
            "none",
            "null",
            "n/a",
            "not_requested",
            "broker_evidence_blocked",
            "sanitized_owner_run_telemetry_missing",
            "sanitized_owner_run_telemetry_invalid_shape",
            "sanitized_telemetry_shape_normalizer_not_requested",
            "sanitized_evidence_normalizer_acceptance_not_requested",
        }
    return False


def _coerce_int(value: Any) -> int | None:
    if isinstance(value, bool) or _missing_value(value):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else None
    try:
        return int(str(value).strip())
    except ValueError:
        return None


def _safe_scalar_or_bool(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool)) and value is not None


def _fake_or_mock_key(key: str) -> bool:
    normalized = _normalized_key(key)
    if normalized in {_normalized_key(marker) for marker in FAKE_MOCK_MARKERS}:
        return True
    has_fake_or_mock = "fake" in normalized or "mock" in normalized
    has_dashboard_or_account = "dashboard" in normalized or "account" in normalized
    has_number_or_balance = "number" in normalized or "balance" in normalized
    return has_fake_or_mock and has_dashboard_or_account and has_number_or_balance


def _normalized_key(value: str) -> str:
    return "".join(char for char in value.lower() if char.isalnum())


def _safe_path(path: Sequence[str]) -> str:
    text = "_".join(_safe_label(part) for part in path if str(part).strip())
    return text or "root"


def _safe_label(value: Any) -> str:
    text = str(value).strip().lower()
    cleaned = "".join(char if char.isalnum() else "_" for char in text)
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_")[:100] or "unknown"


def _sequence_text(value: Any) -> list[str]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [str(item) for item in value]
    if value:
        return [str(value)]
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


def _display(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    text = str(value).strip()
    return text if text else "UNKNOWN"


def _yes_no(value: Any) -> str:
    return "yes" if value is True else "no"


def _true_false(value: Any) -> str:
    return "true" if value is True else "false"
