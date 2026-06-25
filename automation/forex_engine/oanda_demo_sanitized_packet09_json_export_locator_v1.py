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
    INTERNAL_LEDGER_ONLY,
)


PACKET_NAME = (
    "AIOS FOREX OANDA DEMO SANITIZED PACKET 09 JSON EXPORT LOCATOR V1"
)
PACKET_ID = (
    "AIOS-FOREX-OANDA-DEMO-PACKET-12A-SANITIZED-PACKET09-JSON-EXPORT-LOCATOR-V1"
)
REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_SANITIZED_PACKET09_JSON_EXPORT_LOCATOR_V1_REPORT.md"
)
DEFAULT_JSON_PATH = (
    "Reports/forex_delivery/"
    "oanda_demo_packet09_sanitized_owner_run_telemetry_evidence_v1.json"
)

SAFE_SOURCE_PATHS = (
    "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_ATTEMPT_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_SANITIZED_OWNER_RUN_READ_ONLY_TELEMETRY_ADAPTER_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_SANITIZED_TELEMETRY_SHAPE_NORMALIZER_V1_REPORT.md",
    "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_RUN_V1_REPORT.md",
)

TARGET_EVIDENCE_FIELDS = (
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
    "repeat_proof_lane_status",
    "repeat_proof_eligible",
    "profit_evidence",
    "broker_read_mode",
    "broker_evidence_status",
    "evidence_timestamp_utc",
    "evidence_source",
)
SAFE_AUDIT_FIELDS = (
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
EXPORT_FIELD_SET = set(TARGET_EVIDENCE_FIELDS) | set(SAFE_AUDIT_FIELDS)

SAFE_TRUE_AUDIT_FIELDS = {
    "no_new_order_placed",
    "no_live_trade_placed",
    "no_broker_state_modified",
    "no_secrets_written",
}
SAFE_FALSE_AUDIT_FIELDS = {
    "live_endpoint_used",
    "order_placement_performed",
    "order_mutation_performed",
    "order_close_performed",
    "position_mutation_performed",
    "trade_mutation_performed",
    "raw_broker_payload_persisted",
    "secrets_written",
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

SANITIZED_PACKET09_JSON_EXPORT_LOCATOR_NOT_REQUESTED = (
    "SANITIZED_PACKET09_JSON_EXPORT_LOCATOR_NOT_REQUESTED"
)
SANITIZED_PACKET09_JSON_EXPORT_READY = "SANITIZED_PACKET09_JSON_EXPORT_READY"
SANITIZED_PACKET09_JSON_EXPORT_WRITTEN = "SANITIZED_PACKET09_JSON_EXPORT_WRITTEN"
SANITIZED_PACKET09_JSON_EXPORT_BLOCKED_MISSING_FIELDS = (
    "SANITIZED_PACKET09_JSON_EXPORT_BLOCKED_MISSING_FIELDS"
)
SANITIZED_PACKET09_JSON_EXPORT_REJECTED_SECRET_RISK = (
    "SANITIZED_PACKET09_JSON_EXPORT_REJECTED_SECRET_RISK"
)
SANITIZED_PACKET09_JSON_EXPORT_REJECTED_RAW_PAYLOAD_RISK = (
    "SANITIZED_PACKET09_JSON_EXPORT_REJECTED_RAW_PAYLOAD_RISK"
)
SANITIZED_PACKET09_JSON_EXPORT_REJECTED_UNSAFE_AUDIT_FLAG = (
    "SANITIZED_PACKET09_JSON_EXPORT_REJECTED_UNSAFE_AUDIT_FLAG"
)

NEXT_ACTION_SUPPLY_SAFE_FIELDS = (
    "CAPTURE_REQUIRED_FIELDS_FROM_OWNER_READ_HELPER_WITHOUT_RAW_PAYLOAD"
)
NEXT_ACTION_RUN_PACKET11 = "RUN_PACKET_11_ACCEPTANCE_WITH_EXPORTED_JSON"
NEXT_ACTION_STOP_SECRET = "STOP_REMOVE_SECRET_MARKERS_AND_RETRY"
NEXT_ACTION_STOP_RAW = "STOP_REMOVE_RAW_PAYLOAD_MARKERS_AND_RETRY"
NEXT_ACTION_STOP_AUDIT = "STOP_FIX_UNSAFE_AUDIT_FLAGS_AND_RETRY"


def run_sanitized_packet09_json_export_locator(
    write_json: bool = False,
    json_path: str | None = None,
) -> dict[str, Any]:
    output_path = json_path or DEFAULT_JSON_PATH
    raw_candidate, source_paths = _load_candidate(output_path)
    safety = _candidate_safety(raw_candidate)
    candidate = _sanitize_candidate(raw_candidate)
    missing = _missing_required_fields(candidate)
    required_present = not missing
    sanitized_ready = (
        required_present
        and not safety["rejected_forbidden_fields"]
        and not safety["unsafe_audit_flags"]
    )
    json_written = False

    if safety["secret_risk"]:
        status = SANITIZED_PACKET09_JSON_EXPORT_REJECTED_SECRET_RISK
        next_action = NEXT_ACTION_STOP_SECRET
    elif safety["raw_payload_risk"]:
        status = SANITIZED_PACKET09_JSON_EXPORT_REJECTED_RAW_PAYLOAD_RISK
        next_action = NEXT_ACTION_STOP_RAW
    elif safety["unsafe_audit_flags"]:
        status = SANITIZED_PACKET09_JSON_EXPORT_REJECTED_UNSAFE_AUDIT_FLAG
        next_action = NEXT_ACTION_STOP_AUDIT
    elif not required_present:
        status = SANITIZED_PACKET09_JSON_EXPORT_BLOCKED_MISSING_FIELDS
        next_action = NEXT_ACTION_SUPPLY_SAFE_FIELDS
    elif write_json:
        json_written = _write_json_artifact(_export_payload(candidate), output_path)
        if json_written:
            status = SANITIZED_PACKET09_JSON_EXPORT_WRITTEN
            next_action = NEXT_ACTION_RUN_PACKET11
        else:
            status = SANITIZED_PACKET09_JSON_EXPORT_BLOCKED_MISSING_FIELDS
            next_action = NEXT_ACTION_SUPPLY_SAFE_FIELDS
    else:
        status = SANITIZED_PACKET09_JSON_EXPORT_READY
        next_action = NEXT_ACTION_RUN_PACKET11

    return _result(
        export_status=status,
        json_written=json_written,
        json_path=output_path,
        sanitized_evidence_ready=sanitized_ready,
        required_fields_present=required_present,
        missing_required_fields=missing,
        rejected_forbidden_fields=safety["rejected_forbidden_fields"],
        unsafe_audit_flags=safety["unsafe_audit_flags"],
        source_paths=source_paths,
        candidate=candidate,
        next_action=next_action,
    )


def render_sanitized_packet09_json_export_locator_report(
    result: Mapping[str, Any],
    *,
    branch: str = "UNKNOWN",
) -> str:
    missing = _sequence_text(result.get("missing_required_fields"))
    rejected = _sequence_text(result.get("rejected_forbidden_fields"))
    unsafe = _sequence_text(result.get("unsafe_audit_flags"))
    return "\n".join(
        [
            "# AIOS FOREX OANDA DEMO SANITIZED PACKET 09 JSON EXPORT LOCATOR V1 REPORT",
            "",
            f"- packet_name: {PACKET_NAME}",
            f"- packet_id: {PACKET_ID}",
            f"- repo_branch: {branch}",
            f"- export_status: {_display(result.get('export_status'))}",
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
            "- withdrawals, transfers, and money movement remain blocked",
            "",
            "## Machine Result",
            "",
            f"- broker_read_performed: {_yes_no(result.get('broker_read_performed'))}",
            (
                "- broker_network_call_performed: "
                f"{_yes_no(result.get('broker_network_call_performed'))}"
            ),
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


def write_sanitized_packet09_json_export_locator_report(
    result: Mapping[str, Any],
    report_path: str | Path = REPORT_PATH,
    *,
    branch: str = "UNKNOWN",
) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_sanitized_packet09_json_export_locator_report(
            result,
            branch=branch,
        ),
        encoding="utf-8",
    )
    return path


def _load_candidate(json_path: str) -> tuple[dict[str, Any], list[str]]:
    candidate: dict[str, Any] = {}
    source_paths: list[str] = []
    existing_json = Path(json_path)
    if existing_json.exists():
        parsed = _load_json_mapping(existing_json)
        candidate.update(parsed)
        source_paths.append(str(existing_json))
        return candidate, source_paths

    default_json = Path(DEFAULT_JSON_PATH)
    if str(default_json) != str(existing_json) and default_json.exists():
        parsed = _load_json_mapping(default_json)
        candidate.update(parsed)
        source_paths.append(str(default_json))
        return candidate, source_paths

    for source in SAFE_SOURCE_PATHS:
        path = Path(source)
        if not path.exists():
            continue
        source_paths.append(str(path))
        _merge_candidate_fields(
            candidate,
            _parse_report_fields(path.read_text(encoding="utf-8")),
        )
    return candidate, source_paths


def _load_json_mapping(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _parse_report_fields(text: str) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    in_rejected_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_rejected_section = stripped.lower() in {
                "## rejected secret fields",
                "## rejected raw payload fields",
            }
            continue
        if in_rejected_section or not stripped.startswith("- ") or ":" not in stripped:
            continue
        key, value = stripped[2:].split(":", 1)
        key = key.strip()
        if key in EXPORT_FIELD_SET:
            parsed = _parse_scalar(value.strip())
            if not _missing_value(parsed):
                fields[key] = parsed
    return fields


def _merge_candidate_fields(
    candidate: dict[str, Any],
    fields: Mapping[str, Any],
) -> None:
    for key, value in fields.items():
        if key not in candidate or _missing_value(candidate.get(key)):
            candidate[key] = value


def _sanitize_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for field in TARGET_EVIDENCE_FIELDS + SAFE_AUDIT_FIELDS:
        if field not in candidate:
            continue
        value = _normalize_field(field, candidate.get(field))
        if value is not None:
            sanitized[field] = value
    return sanitized


def _normalize_field(field: str, value: Any) -> Any:
    if _missing_value(value):
        return None
    if field in {"repeat_proof_eligible", "profit_evidence"} | set(SAFE_AUDIT_FIELDS):
        return value if isinstance(value, bool) else None
    if field in {
        "trade_id",
        "units",
        "open_trade_count",
        "open_position_count",
    }:
        return _coerce_int(value)
    if isinstance(value, bool):
        return None
    if isinstance(value, (str, int, float)):
        return str(value).strip()
    return None


def _candidate_safety(candidate: Mapping[str, Any]) -> dict[str, Any]:
    secret_fields = _forbidden_field_paths(candidate, FORBIDDEN_SECRET_MARKERS)
    raw_fields = _forbidden_field_paths(candidate, FORBIDDEN_RAW_PAYLOAD_MARKERS)
    fake_fields = _forbidden_field_paths(candidate, FAKE_MOCK_MARKERS)
    unsafe = _unsafe_audit_flags(candidate)
    return {
        "secret_risk": bool(secret_fields or fake_fields),
        "raw_payload_risk": bool(raw_fields),
        "rejected_forbidden_fields": _unique(secret_fields + raw_fields + fake_fields),
        "unsafe_audit_flags": unsafe,
    }


def _forbidden_field_paths(
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
            found.extend(_forbidden_field_paths(child, markers, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_forbidden_field_paths(child, markers, path + (str(index),)))
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
            unsafe.extend(_unsafe_audit_flags(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            unsafe.extend(_unsafe_audit_flags(child, path + (str(index),)))
    return _unique(unsafe)


def _missing_required_fields(candidate: Mapping[str, Any]) -> list[str]:
    return [
        field
        for field in TARGET_EVIDENCE_FIELDS
        if field not in candidate or _missing_value(candidate.get(field))
    ]


def _write_json_artifact(candidate: Mapping[str, Any], json_path: str) -> bool:
    acceptance = run_sanitized_evidence_normalizer_acceptance(dict(candidate))
    if (
        acceptance.get("acceptance_status")
        != SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED
    ):
        return False
    path = Path(json_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(dict(candidate), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return True


def _export_payload(candidate: Mapping[str, Any]) -> dict[str, Any]:
    return {
        field: candidate[field]
        for field in TARGET_EVIDENCE_FIELDS + SAFE_AUDIT_FIELDS
        if field in candidate
    }


def _result(
    *,
    export_status: str,
    json_written: bool,
    json_path: str,
    sanitized_evidence_ready: bool,
    required_fields_present: bool,
    missing_required_fields: Sequence[str],
    rejected_forbidden_fields: Sequence[str],
    unsafe_audit_flags: Sequence[str],
    source_paths: Sequence[str],
    candidate: Mapping[str, Any],
    next_action: str,
) -> dict[str, Any]:
    return {
        "packet_name": PACKET_NAME,
        "packet_id": PACKET_ID,
        "export_status": export_status,
        "json_written": json_written,
        "json_path": json_path,
        "sanitized_evidence_ready": sanitized_evidence_ready,
        "required_fields_present": required_fields_present,
        "missing_required_fields": list(missing_required_fields),
        "rejected_forbidden_fields": list(rejected_forbidden_fields),
        "unsafe_audit_flags": list(unsafe_audit_flags),
        "source_paths": list(source_paths),
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


def _parse_scalar(value: str) -> Any:
    text = value.strip()
    lowered = text.lower()
    if lowered in {"yes", "true"}:
        return True
    if lowered in {"no", "false"}:
        return False
    if lowered in {
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
        "",
    }:
        return None
    return text


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
