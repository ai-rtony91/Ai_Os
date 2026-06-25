from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


PACKET_NAME = (
    "AIOS FOREX OANDA DEMO TRADE 320 OWNER RUN READ ONLY BROKER "
    "REFRESH GATE V1"
)
REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_TRADE_320_OWNER_RUN_READ_ONLY_REFRESH_GATE_V1_REPORT.md"
)

CAMPAIGN_PACKET = 4
TRADE_ID = 320
TRADE_ID_TEXT = "320"
INSTRUMENT = "EUR_USD"

OWNER_RUN_READ_ONLY_REFRESH_READY = "OWNER_RUN_READ_ONLY_REFRESH_READY"
OWNER_RUN_FLAG_REQUIRED = "OWNER_RUN_FLAG_REQUIRED"
BROKER_EVIDENCE_BLOCKED = "BROKER_EVIDENCE_BLOCKED"
SECRET_RISK_DETECTED = "SECRET_RISK_DETECTED"
INVALID_GATE_EVIDENCE = "INVALID_GATE_EVIDENCE"

NOT_REQUESTED = "NOT_REQUESTED"
OWNER_RUN_READ_ONLY_BROKER_REQUESTED = "OWNER_RUN_READ_ONLY_BROKER_REQUESTED"
BLOCKED_SECRET_RISK = "BLOCKED_SECRET_RISK"
INVALID_GATE_EVIDENCE_MODE = "INVALID_GATE_EVIDENCE"

DEFAULT_NEXT_ACTION = (
    "RUN_OWNER_READ_ONLY_REFRESH_WITH_EXPLICIT_FLAG_OR_KEEP_OFFLINE_MONITORING"
)
NOT_REQUESTED_CLARIFICATION = (
    "NOT_REQUESTED means no broker read was requested during the default "
    "dry-run. Owner-authorized read-only broker telemetry remains the "
    "dashboard goal."
)
READY_NEXT_ACTION = "RUN_OWNER_READ_ONLY_REFRESH_NOW_GET_ONLY_SANITIZED_EVIDENCE"
BROKER_BLOCKED_NEXT_ACTION = "KEEP_OFFLINE_MONITORING_AND_REPAIR_READ_ONLY_HELPER"
SECRET_RISK_NEXT_ACTION = "STOP_REMOVE_SECRET_FIELDS_AND_RETRY_SANITIZED_EVIDENCE"
INVALID_NEXT_ACTION = "FIX_GATE_EVIDENCE_SCHEMA_OR_KEEP_OFFLINE_MONITORING"

OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE = (
    "OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE"
)
FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE = (
    "FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE"
)
INTERNAL_LEDGER_ONLY = "INTERNAL_LEDGER_ONLY"

OWNER_RUN_FLAG_FIELDS = (
    "owner_run_read_broker_now",
    "owner_run_flag_present",
    "owner_run_read_only_refresh_requested",
)

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

SECRET_KEY_EXACT = {
    "access_token",
    "account_id",
    "accountid",
    "account_number",
    "api_key",
    "auth_header",
    "authorization",
    "authorization_header",
    "bank_account",
    "bank_account_id",
    "bank_account_number",
    "broker_account",
    "broker_account_id",
    "broker_payload",
    "credential",
    "credential_value",
    "headers",
    "iban",
    "oanda_account_id",
    "password",
    "raw_broker_payload",
    "raw_payload",
    "raw_response",
    "request_headers",
    "routing_number",
    "response_body",
    "runtime_access_token",
    "runtime_account_id",
    "secret",
    "secret_value",
    "swift",
    "token",
}

SECRET_KEY_TERMS = (
    "access_token",
    "account_id",
    "accountid",
    "account_number",
    "api_key",
    "auth_header",
    "authorization",
    "bank_account",
    "broker_account",
    "credential_value",
    "oanda_account_id",
    "password",
    "raw_broker_payload",
    "routing_number",
    "runtime_access_token",
    "runtime_account_id",
    "secret_value",
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


def evaluate_trade_320_owner_run_read_only_refresh_gate(
    evidence: dict | None = None,
) -> dict[str, Any]:
    if evidence is None:
        return _gate_result(
            gate_status=OWNER_RUN_FLAG_REQUIRED,
            broker_read_allowed_now=False,
            owner_run_flag_required=True,
            broker_read_mode=NOT_REQUESTED,
            next_action=DEFAULT_NEXT_ACTION,
            blockers=["owner_run_read_broker_now_flag_required"],
        )

    if not isinstance(evidence, Mapping):
        return _gate_result(
            gate_status=INVALID_GATE_EVIDENCE,
            broker_read_allowed_now=False,
            owner_run_flag_required=True,
            broker_read_mode=INVALID_GATE_EVIDENCE_MODE,
            sanitized_evidence_only=False,
            next_action=INVALID_NEXT_ACTION,
            blockers=["evidence_must_be_mapping"],
        )

    owner_flag_present = _owner_run_flag_present(evidence)
    broker_read_mode = _broker_read_mode(evidence, owner_flag_present)
    secret_blockers = _secret_blockers(evidence)
    if secret_blockers:
        return _gate_result(
            gate_status=SECRET_RISK_DETECTED,
            broker_read_allowed_now=False,
            owner_run_flag_required=not owner_flag_present,
            broker_read_mode=BLOCKED_SECRET_RISK,
            sanitized_evidence_only=False,
            forbidden_secret_fields_absent=False,
            next_action=SECRET_RISK_NEXT_ACTION,
            blockers=secret_blockers,
        )

    invalid_blockers = _invalid_gate_blockers(evidence)
    if invalid_blockers:
        return _gate_result(
            gate_status=INVALID_GATE_EVIDENCE,
            broker_read_allowed_now=False,
            owner_run_flag_required=not owner_flag_present,
            broker_read_mode=INVALID_GATE_EVIDENCE_MODE,
            sanitized_evidence_only=_sanitized_evidence_only(evidence),
            next_action=INVALID_NEXT_ACTION,
            blockers=invalid_blockers,
        )

    if not owner_flag_present:
        return _gate_result(
            gate_status=OWNER_RUN_FLAG_REQUIRED,
            broker_read_allowed_now=False,
            owner_run_flag_required=True,
            broker_read_mode=NOT_REQUESTED,
            sanitized_evidence_only=_sanitized_evidence_only(evidence),
            next_action=DEFAULT_NEXT_ACTION,
            blockers=["owner_run_read_broker_now_flag_required"],
        )

    broker_blockers = _broker_evidence_blockers(evidence)
    if broker_blockers:
        return _gate_result(
            gate_status=BROKER_EVIDENCE_BLOCKED,
            broker_read_allowed_now=False,
            owner_run_flag_required=False,
            broker_read_mode=broker_read_mode,
            sanitized_evidence_only=_sanitized_evidence_only(evidence),
            next_action=BROKER_BLOCKED_NEXT_ACTION,
            blockers=broker_blockers,
        )

    return _gate_result(
        gate_status=OWNER_RUN_READ_ONLY_REFRESH_READY,
        broker_read_allowed_now=True,
        owner_run_flag_required=False,
        broker_read_mode=broker_read_mode,
        sanitized_evidence_only=True,
        next_action=READY_NEXT_ACTION,
        blockers=[],
    )


def render_trade_320_owner_run_read_only_refresh_gate_report(
    result: Mapping[str, Any],
    *,
    branch: str = "UNKNOWN",
) -> str:
    blockers = result.get("blockers")
    blocker_text = ", ".join(str(item) for item in blockers) if blockers else "none"
    return "\n".join(
        [
            "# AIOS FOREX OANDA DEMO TRADE 320 OWNER RUN READ ONLY REFRESH GATE V1 REPORT",
            "",
            f"- packet_name: {PACKET_NAME}",
            f"- repo_branch: {branch}",
            "- pr_1075_anchor: Add OANDA demo trade 320 read-only PL refresh",
            "- trade_320_anchor: EUR_USD long 1 entry 1.13596 TP 321 SL 322",
            f"- gate_status: {result.get('gate_status')}",
            f"- broker_read_allowed_now: {_yes_no(result.get('broker_read_allowed_now'))}",
            f"- owner_run_flag_required: {_yes_no(result.get('owner_run_flag_required'))}",
            f"- broker_read_mode: {result.get('broker_read_mode')}",
            f"- next_action: {result.get('next_action')}",
            f"- blockers: {blocker_text}",
            "",
            "## Dashboard Real Data Doctrine",
            "",
            "- real broker telemetry required when authorized",
            "- no fake balances",
            "- no fake P/L",
            "- no fake positions",
            "- no fake bank numbers",
            "- bank telemetry is future separate read-only lane",
            (
                "- withdrawals/transfers require future owner-approved "
                "money-movement gate"
            ),
            "- profit reserve bucket is internal ledger only until a money-movement gate exists",
            (
                f"- broker_data_source_required: "
                f"{result.get('broker_data_source_required')}"
            ),
            (
                f"- bank_data_source_required: "
                f"{result.get('bank_data_source_required')}"
            ),
            (
                f"- profit_reserve_bucket_mode: "
                f"{result.get('profit_reserve_bucket_mode')}"
            ),
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
            f"- sanitized_evidence_only: {_true_false(result.get('sanitized_evidence_only'))}",
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
                "- profit_reserve_bucket_money_movement_requires_future_owner_gate: "
                f"{_true_false(result.get('profit_reserve_bucket_money_movement_requires_future_owner_gate'))}"
            ),
            (
                "- forbidden_secret_fields_absent: "
                f"{_true_false(result.get('forbidden_secret_fields_absent'))}"
            ),
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


def write_trade_320_owner_run_read_only_refresh_gate_report(
    result: Mapping[str, Any],
    report_path: str | Path = REPORT_PATH,
    *,
    branch: str = "UNKNOWN",
) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_trade_320_owner_run_read_only_refresh_gate_report(
            result,
            branch=branch,
        ),
        encoding="utf-8",
    )
    return path


def _gate_result(
    *,
    gate_status: str,
    broker_read_allowed_now: bool,
    owner_run_flag_required: bool,
    broker_read_mode: str,
    next_action: str,
    blockers: Sequence[str],
    sanitized_evidence_only: bool = True,
    forbidden_secret_fields_absent: bool = True,
) -> dict[str, Any]:
    return {
        "packet_name": PACKET_NAME,
        "campaign_packet": CAMPAIGN_PACKET,
        "trade_id": TRADE_ID,
        "gate_status": gate_status,
        "broker_read_allowed_now": broker_read_allowed_now,
        "owner_run_flag_required": owner_run_flag_required,
        "broker_read_mode": broker_read_mode,
        "sanitized_evidence_only": sanitized_evidence_only,
        "forbidden_secret_fields_absent": forbidden_secret_fields_absent,
        "dashboard_real_broker_telemetry_goal": True,
        "dashboard_fake_numbers_allowed": False,
        "dashboard_mock_numbers_allowed": False,
        "broker_data_source_required": OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE,
        "bank_data_source_required": FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE,
        "withdrawal_allowed_now": False,
        "transfer_allowed_now": False,
        "money_movement_allowed_now": False,
        "profit_reserve_bucket_mode": INTERNAL_LEDGER_ONLY,
        "profit_reserve_bucket_money_movement_requires_future_owner_gate": True,
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
        "next_action": next_action,
        "notes": [NOT_REQUESTED_CLARIFICATION],
        "blockers": _unique(blockers),
    }


def _owner_run_flag_present(evidence: Mapping[str, Any]) -> bool:
    return any(evidence.get(field) is True for field in OWNER_RUN_FLAG_FIELDS)


def _broker_read_mode(
    evidence: Mapping[str, Any],
    owner_flag_present: bool,
) -> str:
    explicit = evidence.get("broker_read_mode")
    if explicit:
        return str(explicit)
    if owner_flag_present:
        return OWNER_RUN_READ_ONLY_BROKER_REQUESTED
    return NOT_REQUESTED


def _sanitized_evidence_only(evidence: Mapping[str, Any]) -> bool:
    if evidence.get("sanitized_evidence_only") is False:
        return False
    return not _secret_blockers(evidence)


def _invalid_gate_blockers(evidence: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    trade_id = _first_present(evidence, ("trade_id", "expected_trade_id"))
    if trade_id is not None and str(trade_id).strip() != TRADE_ID_TEXT:
        blockers.append("trade_id_must_be_320")

    instrument = evidence.get("instrument")
    if instrument is not None and str(instrument).strip() != INSTRUMENT:
        blockers.append("instrument_must_be_EUR_USD")

    method = _first_present(evidence, ("broker_read_method", "method"))
    if method is not None and str(method).strip().upper() != "GET":
        blockers.append("broker_read_method_must_be_get")

    for field in MUTATION_TRUE_FIELDS:
        if evidence.get(field) is True:
            blockers.append(f"unsafe_{field}_true")

    for field in SAFETY_FALSE_FIELDS:
        if evidence.get(field) is False:
            blockers.append(f"{field}_must_not_be_false")

    return _unique(blockers)


def _broker_evidence_blockers(evidence: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if evidence.get("safe_read_only_helper_available") is not True:
        blockers.append("safe_read_only_helper_available_required")
    if evidence.get("sanitized_evidence_only") is not True:
        blockers.append("sanitized_evidence_only_required")

    status_values = (
        evidence.get("gate_status"),
        evidence.get("helper_status"),
        evidence.get("script_status"),
        evidence.get("status"),
        evidence.get("status_bucket"),
        evidence.get("broker_evidence_status"),
        evidence.get("pl_capture_classification"),
    )
    for status in status_values:
        if _is_broker_blocked_status(status):
            blockers.append(f"broker_evidence_blocked_{_safe_label(status)}")

    for blocker in _sequence(evidence.get("blockers")):
        blocker_text = str(blocker)
        lowered = blocker_text.lower()
        if "blocked" in lowered or "vault" in lowered or "broker" in lowered:
            blockers.append(f"broker_blocker_{_safe_label(blocker_text)}")

    return _unique(blockers)


def _is_broker_blocked_status(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    if text in BROKER_BLOCKED_STATUSES:
        return True
    return text.startswith("BLOCKED_") or text.startswith("BROKER_EVIDENCE_BLOCKED")


def _secret_blockers(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = path + (key_text,)
            if _sensitive_key(key_text):
                blockers.append(f"forbidden_secret_field_{_safe_path(child_path)}")
                continue
            blockers.extend(_secret_blockers(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            blockers.extend(_secret_blockers(child, path + (str(index),)))
    elif isinstance(value, str):
        lowered = value.lower()
        if "bearer " in lowered or "authorization:" in lowered:
            blockers.append(f"forbidden_secret_value_{_safe_path(path)}")
    return _unique(blockers)


def _sensitive_key(key: str) -> bool:
    key_text = key.lower()
    if key_text in SECRET_KEY_EXACT:
        return True
    return any(term in key_text for term in SECRET_KEY_TERMS)


def _first_present(source: Mapping[str, Any], keys: Sequence[str]) -> Any:
    for key in keys:
        if key in source and source.get(key) is not None:
            return source.get(key)
    return None


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
    return "_".join(_safe_label(part) for part in path if str(part).strip())


def _safe_label(value: Any) -> str:
    text = str(value).strip().lower()
    cleaned = "".join(char if char.isalnum() else "_" for char in text)
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_")[:80] or "unknown"


def _yes_no(value: Any) -> str:
    return "yes" if value is True else "no"


def _true_false(value: Any) -> str:
    return "true" if value is True else "false"
