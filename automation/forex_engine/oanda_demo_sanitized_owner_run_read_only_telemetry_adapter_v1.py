from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


PACKET_NAME = (
    "AIOS FOREX OANDA DEMO SANITIZED OWNER RUN READ ONLY TELEMETRY ADAPTER V1"
)
REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_SANITIZED_OWNER_RUN_READ_ONLY_TELEMETRY_ADAPTER_V1_REPORT.md"
)

CAMPAIGN_PACKET = 7
TRADE_ID = 320
TRADE_ID_TEXT = "320"
INSTRUMENT = "EUR_USD"
SIDE = "long"
UNITS = 1
ENTRY_PRICE = "1.13596"

SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED = (
    "SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED"
)
SANITIZED_OWNER_RUN_TELEMETRY_MISSING = "SANITIZED_OWNER_RUN_TELEMETRY_MISSING"
SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_SECRET_RISK = (
    "SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_SECRET_RISK"
)
SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_RAW_PAYLOAD = (
    "SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_RAW_PAYLOAD"
)
SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE = (
    "SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE"
)
SANITIZED_OWNER_RUN_TELEMETRY_BROKER_BLOCKED = (
    "SANITIZED_OWNER_RUN_TELEMETRY_BROKER_BLOCKED"
)

BROKER_EVIDENCE_BLOCKED = "BROKER_EVIDENCE_BLOCKED"
NOT_REQUESTED = "NOT_REQUESTED"
OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE = (
    "OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE"
)
FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE = (
    "FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE"
)
INTERNAL_LEDGER_ONLY = "INTERNAL_LEDGER_ONLY"

DEFAULT_NEXT_ACTION = (
    "RUN_OWNER_READ_ONLY_HELPER_AND_FEED_SANITIZED_OUTPUT_TO_ADAPTER"
)
ACCEPTED_NEXT_ACTION = "FEED_SANITIZED_TELEMETRY_TO_TRADE_320_PL_REFRESH"
SECRET_NEXT_ACTION = "STOP_REMOVE_SECRET_FIELDS_AND_RETRY_SANITIZED_OUTPUT"
RAW_PAYLOAD_NEXT_ACTION = "STOP_REMOVE_RAW_PAYLOAD_AND_RETRY_SANITIZED_OUTPUT"
INVALID_NEXT_ACTION = "FIX_SANITIZED_OWNER_RUN_TELEMETRY_SHAPE"
BROKER_BLOCKED_NEXT_ACTION = "REPAIR_OWNER_READ_ONLY_HELPER_OR_RUNTIME_AUTH_BOUNDARY"

ALLOWED_SANITIZED_FIELDS = (
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
ALLOWED_SANITIZED_FIELD_SET = set(ALLOWED_SANITIZED_FIELDS)

ACCEPTED_REQUIRED_FIELDS = (
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

RAW_PAYLOAD_KEY_TERMS = (
    "raw_broker_payload",
    "raw_payload",
    "raw_request",
    "raw_response",
    "request_body",
    "response_body",
    "live_payload",
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

BOOL_FIELDS = {
    "repeat_proof_eligible",
    "profit_evidence",
}


def adapt_sanitized_owner_run_oanda_telemetry(
    evidence: dict | None = None,
) -> dict[str, Any]:
    if evidence is None:
        return _result(
            adapter_status=SANITIZED_OWNER_RUN_TELEMETRY_MISSING,
            sanitized_broker_telemetry_ready=False,
            broker_evidence_status=BROKER_EVIDENCE_BLOCKED,
            broker_read_mode=NOT_REQUESTED,
            accepted_sanitized_fields=[],
            rejected_secret_fields=[],
            rejected_raw_payload_fields=[],
            invalid_shape_blockers=[],
            blockers=["sanitized_owner_run_telemetry_missing"],
            next_action=DEFAULT_NEXT_ACTION,
        )
    return validate_owner_run_telemetry_shape(evidence)


def validate_owner_run_telemetry_shape(evidence: dict) -> dict[str, Any]:
    if not isinstance(evidence, Mapping):
        return _result(
            adapter_status=SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE,
            sanitized_broker_telemetry_ready=False,
            broker_evidence_status=SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE,
            broker_read_mode=NOT_REQUESTED,
            accepted_sanitized_fields=[],
            rejected_secret_fields=[],
            rejected_raw_payload_fields=[],
            invalid_shape_blockers=["evidence_must_be_mapping"],
            blockers=["evidence_must_be_mapping"],
            next_action=INVALID_NEXT_ACTION,
        )

    secret_fields = _secret_field_paths(evidence)
    raw_payload_fields = _raw_payload_field_paths(evidence)
    if secret_fields:
        return _result(
            adapter_status=SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_SECRET_RISK,
            sanitized_broker_telemetry_ready=False,
            broker_evidence_status=(
                SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_SECRET_RISK
            ),
            broker_read_mode=_broker_read_mode(evidence),
            accepted_sanitized_fields=_accepted_fields(evidence),
            rejected_secret_fields=secret_fields,
            rejected_raw_payload_fields=raw_payload_fields,
            invalid_shape_blockers=[],
            blockers=[f"forbidden_secret_field_{field}" for field in secret_fields],
            next_action=SECRET_NEXT_ACTION,
            evidence=evidence,
        )

    if raw_payload_fields:
        return _result(
            adapter_status=SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_RAW_PAYLOAD,
            sanitized_broker_telemetry_ready=False,
            broker_evidence_status=(
                SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_RAW_PAYLOAD
            ),
            broker_read_mode=_broker_read_mode(evidence),
            accepted_sanitized_fields=_accepted_fields(evidence),
            rejected_secret_fields=[],
            rejected_raw_payload_fields=raw_payload_fields,
            invalid_shape_blockers=[],
            blockers=[
                f"forbidden_raw_payload_field_{field}"
                for field in raw_payload_fields
            ],
            next_action=RAW_PAYLOAD_NEXT_ACTION,
            evidence=evidence,
        )

    shape_blockers = _shape_blockers(evidence)
    if shape_blockers:
        return _result(
            adapter_status=SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE,
            sanitized_broker_telemetry_ready=False,
            broker_evidence_status=SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE,
            broker_read_mode=_broker_read_mode(evidence),
            accepted_sanitized_fields=_accepted_fields(evidence),
            rejected_secret_fields=[],
            rejected_raw_payload_fields=[],
            invalid_shape_blockers=shape_blockers,
            blockers=shape_blockers,
            next_action=INVALID_NEXT_ACTION,
            evidence=evidence,
        )

    broker_blockers = _broker_blocked_blockers(evidence)
    if broker_blockers:
        return _result(
            adapter_status=SANITIZED_OWNER_RUN_TELEMETRY_BROKER_BLOCKED,
            sanitized_broker_telemetry_ready=False,
            broker_evidence_status=BROKER_EVIDENCE_BLOCKED,
            broker_read_mode=_broker_read_mode(evidence),
            accepted_sanitized_fields=_accepted_fields(evidence),
            rejected_secret_fields=[],
            rejected_raw_payload_fields=[],
            invalid_shape_blockers=[],
            blockers=broker_blockers,
            next_action=BROKER_BLOCKED_NEXT_ACTION,
            evidence=evidence,
        )

    missing_required = _missing_required_fields(evidence)
    if missing_required:
        return _result(
            adapter_status=SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE,
            sanitized_broker_telemetry_ready=False,
            broker_evidence_status=SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE,
            broker_read_mode=_broker_read_mode(evidence),
            accepted_sanitized_fields=_accepted_fields(evidence),
            rejected_secret_fields=[],
            rejected_raw_payload_fields=[],
            invalid_shape_blockers=missing_required,
            blockers=missing_required,
            next_action=INVALID_NEXT_ACTION,
            evidence=evidence,
        )

    return _result(
        adapter_status=SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED,
        sanitized_broker_telemetry_ready=True,
        broker_evidence_status=str(evidence.get("broker_evidence_status")),
        broker_read_mode=_broker_read_mode(evidence),
        accepted_sanitized_fields=_accepted_fields(evidence),
        rejected_secret_fields=[],
        rejected_raw_payload_fields=[],
        invalid_shape_blockers=[],
        blockers=[],
        next_action=ACCEPTED_NEXT_ACTION,
        evidence=evidence,
    )


def render_sanitized_owner_run_read_only_telemetry_adapter_report(
    result: Mapping[str, Any],
    *,
    branch: str = "UNKNOWN",
) -> str:
    blockers = result.get("blockers")
    blocker_text = ", ".join(str(item) for item in blockers) if blockers else "none"
    return "\n".join(
        [
            "# AIOS FOREX OANDA DEMO SANITIZED OWNER RUN READ ONLY TELEMETRY ADAPTER V1 REPORT",
            "",
            f"- packet_name: {PACKET_NAME}",
            f"- repo_branch: {branch}",
            "- pr_1079_anchor: runtime auth boundary read-only helper repair",
            (
                "- current_blocker: broker telemetry not ready until sanitized "
                "owner-run helper output exists"
            ),
            f"- adapter_status: {result.get('adapter_status')}",
            (
                "- sanitized_broker_telemetry_ready: "
                f"{_yes_no(result.get('sanitized_broker_telemetry_ready'))}"
            ),
            f"- broker_evidence_status: {result.get('broker_evidence_status')}",
            f"- broker_read_mode: {result.get('broker_read_mode')}",
            f"- next_action: {result.get('next_action')}",
            f"- blockers: {blocker_text}",
            "",
            "## Accepted Sanitized Fields",
            "",
            *[f"- {field}" for field in ALLOWED_SANITIZED_FIELDS],
            "",
            "## Rejected Secret Fields",
            "",
            *[f"- {field}" for field in REJECTED_SECRET_FIELD_NAMES],
            "",
            "## Rejected Raw Payload Fields",
            "",
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
            f"- instrument: {_display(result.get('instrument'))}",
            f"- side: {_display(result.get('side'))}",
            f"- units: {_display(result.get('units'))}",
            f"- entry_price: {_display(result.get('entry_price'))}",
            f"- realized_pl: {_display(result.get('realized_pl'))}",
            f"- unrealized_pl: {_display(result.get('unrealized_pl'))}",
            f"- open_trade_count: {_display(result.get('open_trade_count'))}",
            f"- open_position_count: {_display(result.get('open_position_count'))}",
            f"- monitor_bucket: {_display(result.get('monitor_bucket'))}",
            f"- result_bucket: {_display(result.get('result_bucket'))}",
            (
                "- repeat_proof_lane_status: "
                f"{_display(result.get('repeat_proof_lane_status'))}"
            ),
            (
                "- repeat_proof_eligible: "
                f"{_true_false(result.get('repeat_proof_eligible'))}"
            ),
            f"- profit_evidence: {_true_false(result.get('profit_evidence'))}",
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


def write_sanitized_owner_run_read_only_telemetry_adapter_report(
    result: Mapping[str, Any],
    report_path: str | Path = REPORT_PATH,
    *,
    branch: str = "UNKNOWN",
) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_sanitized_owner_run_read_only_telemetry_adapter_report(
            result,
            branch=branch,
        ),
        encoding="utf-8",
    )
    return path


def _result(
    *,
    adapter_status: str,
    sanitized_broker_telemetry_ready: bool,
    broker_evidence_status: str,
    broker_read_mode: str,
    accepted_sanitized_fields: Sequence[str],
    rejected_secret_fields: Sequence[str],
    rejected_raw_payload_fields: Sequence[str],
    invalid_shape_blockers: Sequence[str],
    blockers: Sequence[str],
    next_action: str,
    evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source = evidence or {}
    return {
        "packet_name": PACKET_NAME,
        "campaign_packet": CAMPAIGN_PACKET,
        "trade_id": _field_value(source, "trade_id", TRADE_ID),
        "adapter_status": adapter_status,
        "sanitized_broker_telemetry_ready": sanitized_broker_telemetry_ready,
        "broker_evidence_status": broker_evidence_status,
        "broker_read_mode": broker_read_mode,
        "dashboard_real_broker_telemetry_goal": True,
        "dashboard_fake_numbers_allowed": False,
        "dashboard_mock_numbers_allowed": False,
        "broker_data_source_required": OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE,
        "bank_data_source_required": FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE,
        "instrument": _field_value(source, "instrument", INSTRUMENT),
        "side": _field_value(source, "side", SIDE),
        "units": _field_value(source, "units", UNITS),
        "entry_price": _field_value(source, "entry_price", ENTRY_PRICE),
        "realized_pl": _field_value(source, "realized_pl"),
        "unrealized_pl": _field_value(source, "unrealized_pl"),
        "open_trade_count": _field_value(source, "open_trade_count"),
        "open_position_count": _field_value(source, "open_position_count"),
        "monitor_bucket": _field_value(source, "monitor_bucket"),
        "result_bucket": _field_value(source, "result_bucket"),
        "repeat_proof_lane_status": _field_value(
            source,
            "repeat_proof_lane_status",
        ),
        "repeat_proof_eligible": _field_value(
            source,
            "repeat_proof_eligible",
            False,
        ),
        "profit_evidence": _field_value(source, "profit_evidence", False),
        "withdrawal_allowed_now": False,
        "transfer_allowed_now": False,
        "money_movement_allowed_now": False,
        "profit_reserve_bucket_mode": INTERNAL_LEDGER_ONLY,
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
        "broker_network_call_performed": False,
        "broker_read_performed": False,
        "accepted_sanitized_fields": _unique(accepted_sanitized_fields),
        "rejected_secret_fields": _unique(rejected_secret_fields),
        "rejected_raw_payload_fields": _unique(rejected_raw_payload_fields),
        "invalid_shape_blockers": _unique(invalid_shape_blockers),
        "blockers": _unique(blockers),
        "next_action": next_action,
    }


def _field_value(
    source: Mapping[str, Any],
    field: str,
    default: Any = None,
) -> Any:
    if field in source and source.get(field) is not None:
        return source.get(field)
    return default


def _accepted_fields(evidence: Mapping[str, Any]) -> list[str]:
    return [
        field
        for field in ALLOWED_SANITIZED_FIELDS
        if field in evidence and _safe_value_for_field(field, evidence.get(field))
    ]


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


def _shape_blockers(evidence: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for key, value in evidence.items():
        key_text = str(key)
        if key_text not in ALLOWED_SANITIZED_FIELD_SET:
            blockers.append(f"unexpected_field_{_safe_label(key_text)}")
            continue
        if not _safe_value_for_field(key_text, value):
            blockers.append(f"{_safe_label(key_text)}_must_be_safe_scalar")

    trade_id = evidence.get("trade_id")
    if trade_id is None:
        blockers.append("trade_id_required")
    elif str(trade_id).strip() != TRADE_ID_TEXT:
        blockers.append("trade_id_must_be_320")

    instrument = evidence.get("instrument")
    if instrument is not None and str(instrument).strip() != INSTRUMENT:
        blockers.append("instrument_must_be_EUR_USD")

    broker_read_mode = _broker_read_mode(evidence)
    if "LIVE" in broker_read_mode.upper():
        blockers.append("broker_read_mode_must_not_be_live")

    return _unique(blockers)


def _missing_required_fields(evidence: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field in ACCEPTED_REQUIRED_FIELDS:
        if field not in evidence or evidence.get(field) is None:
            blockers.append(f"{field}_required")
    return blockers


def _broker_blocked_blockers(evidence: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field in (
        "broker_evidence_status",
        "monitor_bucket",
        "result_bucket",
    ):
        value = evidence.get(field)
        if _is_broker_blocked_status(value):
            blockers.append(f"broker_evidence_blocked_{_safe_label(value)}")
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


def _broker_read_mode(evidence: Mapping[str, Any]) -> str:
    mode = evidence.get("broker_read_mode")
    if mode is None:
        return NOT_REQUESTED
    return str(mode).strip() or NOT_REQUESTED


def _safe_value_for_field(field: str, value: Any) -> bool:
    if field in BOOL_FIELDS:
        return isinstance(value, bool)
    if isinstance(value, bool):
        return False
    return isinstance(value, (str, int, float))


def _secret_key(key: str) -> bool:
    key_text = key.lower()
    return key_text in REJECTED_SECRET_FIELD_NAMES or any(
        term in key_text for term in SECRET_KEY_TERMS
    )


def _raw_payload_key(key: str) -> bool:
    key_text = key.lower()
    return key_text in REJECTED_RAW_PAYLOAD_FIELD_NAMES or any(
        term in key_text for term in RAW_PAYLOAD_KEY_TERMS
    )


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


def _display(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    text = str(value).strip()
    return text if text else "UNKNOWN"


def _yes_no(value: Any) -> str:
    return "yes" if value is True else "no"


def _true_false(value: Any) -> str:
    return "true" if value is True else "false"
