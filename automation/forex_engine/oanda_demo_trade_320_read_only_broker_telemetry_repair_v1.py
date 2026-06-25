from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


PACKET_NAME = (
    "AIOS FOREX OANDA DEMO READ ONLY BROKER TELEMETRY HELPER REPAIR V1"
)
REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_TRADE_320_READ_ONLY_BROKER_TELEMETRY_REPAIR_V1_REPORT.md"
)

CAMPAIGN_PACKET = 5
TRADE_ID = 320
TRADE_ID_TEXT = "320"
INSTRUMENT = "EUR_USD"

READ_ONLY_BROKER_TELEMETRY_READY = "READ_ONLY_BROKER_TELEMETRY_READY"
BROKER_EVIDENCE_BLOCKED = "BROKER_EVIDENCE_BLOCKED"
READ_ONLY_HELPER_MISSING = "READ_ONLY_HELPER_MISSING"
READ_ONLY_HELPER_REJECTED_UNSANITIZED_RESULT = (
    "READ_ONLY_HELPER_REJECTED_UNSANITIZED_RESULT"
)
SECRET_RISK_DETECTED = "SECRET_RISK_DETECTED"
INVALID_TELEMETRY_EVIDENCE = "INVALID_TELEMETRY_EVIDENCE"

OWNER_RUN_READ_ONLY_BROKER_REQUESTED = "OWNER_RUN_READ_ONLY_BROKER_REQUESTED"
OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE = (
    "OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE"
)
INTERNAL_LEDGER_ONLY = "INTERNAL_LEDGER_ONLY"

REPAIR_HELPER_NEXT_ACTION = "REPAIR_READ_ONLY_HELPER_OR_RUNTIME_AUTH_BOUNDARY"
RESTORE_HELPER_NEXT_ACTION = "RESTORE_OR_REGISTER_READ_ONLY_HELPER_BOUNDARY"
SANITIZE_NEXT_ACTION = "RETURN_SANITIZED_HELPER_RESULT_ONLY"
SECRET_NEXT_ACTION = "STOP_REMOVE_SECRET_FIELDS_AND_RETRY_SANITIZED_EVIDENCE"
READY_NEXT_ACTION = "SEND_SANITIZED_BROKER_TELEMETRY_TO_DASHBOARD"
INVALID_NEXT_ACTION = "FIX_TELEMETRY_EVIDENCE_SCHEMA"

OBSERVED_PACKET_04_OWNER_RUN_BLOCKED_EVIDENCE: dict[str, Any] = {
    "source": "observed_packet_04_owner_run_gate",
    "campaign_packet": 4,
    "trade_id": TRADE_ID,
    "instrument": INSTRUMENT,
    "broker_network_call_performed": True,
    "broker_read_mode": OWNER_RUN_READ_ONLY_BROKER_REQUESTED,
    "gate_status": BROKER_EVIDENCE_BLOCKED,
    "script_status": BROKER_EVIDENCE_BLOCKED,
    "sanitized_evidence_only": True,
    "no_new_order_placed": True,
    "no_live_trade_placed": True,
    "no_broker_state_modified": True,
    "no_secrets_written": True,
    "withdrawal_allowed_now": False,
    "transfer_allowed_now": False,
    "money_movement_allowed_now": False,
    "dashboard_real_broker_telemetry_goal": True,
    "dashboard_fake_numbers_allowed": False,
    "dashboard_mock_numbers_allowed": False,
    "blockers": [
        "broker_evidence_blocked_broker_evidence_blocked",
        "broker_blocker_broker_evidence_blocked_true",
        "broker_blocker_evidence_status_indicates_broker_blocked",
    ],
}

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

READY_STATUSES = {
    READ_ONLY_BROKER_TELEMETRY_READY,
    "OWNER_RUN_READ_ONLY_REFRESH_READY",
    "OWNER_RUN_READ_ONLY_EVIDENCE_CLASSIFIED",
    "READ_ONLY_FILLED_TRADE_PL_CAPTURE_ATTEMPTED",
    "FILLED_TRADE_PL_POSITIVE",
    "FILLED_TRADE_PL_NEGATIVE",
    "FILLED_TRADE_PL_ZERO",
    "FILLED_TRADE_PL_OPEN_UNREALIZED",
    "FILLED_TRADE_PL_NOT_FOUND",
    "OWNER_RUN_READ_ONLY_EVIDENCE_READY",
}

HELPER_MISSING_TERMS = (
    "read_only_helper_missing",
    "missing_read_only_helper",
    "helper_import_failed",
    "helper_not_callable",
    "helper_unavailable",
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

MONEY_MOVEMENT_TRUE_FIELDS = (
    "withdrawal_allowed_now",
    "transfer_allowed_now",
    "money_movement_allowed_now",
    "withdrawal_performed",
    "transfer_performed",
    "money_movement_performed",
)

UNSANITIZED_TRUE_FIELDS = (
    "raw_payload_present",
    "raw_broker_payload_present",
    "raw_response_present",
    "raw_helper_result_present",
    "credential_values_included",
    "account_identifiers_included",
    "auth_headers_included",
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
    "response_body",
    "routing_number",
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
    "raw_payload",
    "raw_response",
    "request_headers",
    "response_body",
    "routing_number",
    "runtime_access_token",
    "runtime_account_id",
    "secret_value",
)


def diagnose_trade_320_read_only_broker_telemetry(
    evidence: dict | None = None,
) -> dict[str, Any]:
    source = (
        dict(OBSERVED_PACKET_04_OWNER_RUN_BLOCKED_EVIDENCE)
        if evidence is None
        else evidence
    )
    return build_sanitized_trade_320_broker_telemetry_result(source)


def build_sanitized_trade_320_broker_telemetry_result(
    raw_or_helper_result: dict,
) -> dict[str, Any]:
    if not isinstance(raw_or_helper_result, Mapping):
        return _result(
            broker_evidence_status=INVALID_TELEMETRY_EVIDENCE,
            broker_read_mode="INVALID_TELEMETRY_EVIDENCE",
            sanitized_broker_telemetry_ready=False,
            blockers=["telemetry_evidence_must_be_mapping"],
            next_action=INVALID_NEXT_ACTION,
        )

    evidence = raw_or_helper_result
    secret_blockers = _secret_blockers(evidence)
    if secret_blockers:
        return _result(
            broker_evidence_status=SECRET_RISK_DETECTED,
            broker_read_mode="BLOCKED_SECRET_RISK",
            sanitized_broker_telemetry_ready=False,
            blockers=secret_blockers,
            next_action=SECRET_NEXT_ACTION,
            evidence=evidence,
        )

    helper_missing_blockers = _helper_missing_blockers(evidence)
    if helper_missing_blockers:
        return _result(
            broker_evidence_status=READ_ONLY_HELPER_MISSING,
            broker_read_mode=_broker_read_mode(evidence),
            sanitized_broker_telemetry_ready=False,
            blockers=helper_missing_blockers,
            next_action=RESTORE_HELPER_NEXT_ACTION,
            evidence=evidence,
        )

    unsanitized_blockers = _unsanitized_blockers(evidence)
    if unsanitized_blockers:
        return _result(
            broker_evidence_status=READ_ONLY_HELPER_REJECTED_UNSANITIZED_RESULT,
            broker_read_mode=_broker_read_mode(evidence),
            sanitized_broker_telemetry_ready=False,
            blockers=unsanitized_blockers,
            next_action=SANITIZE_NEXT_ACTION,
            evidence=evidence,
        )

    invalid_blockers = _invalid_blockers(evidence)
    if invalid_blockers:
        return _result(
            broker_evidence_status=INVALID_TELEMETRY_EVIDENCE,
            broker_read_mode=_broker_read_mode(evidence),
            sanitized_broker_telemetry_ready=False,
            blockers=invalid_blockers,
            next_action=INVALID_NEXT_ACTION,
            evidence=evidence,
        )

    broker_blockers = _broker_blocked_blockers(evidence)
    if broker_blockers:
        return _result(
            broker_evidence_status=BROKER_EVIDENCE_BLOCKED,
            broker_read_mode=_broker_read_mode(evidence),
            sanitized_broker_telemetry_ready=False,
            blockers=broker_blockers,
            next_action=REPAIR_HELPER_NEXT_ACTION,
            evidence=evidence,
        )

    if _ready_telemetry(evidence):
        return _result(
            broker_evidence_status=READ_ONLY_BROKER_TELEMETRY_READY,
            broker_read_mode=_broker_read_mode(evidence),
            sanitized_broker_telemetry_ready=True,
            blockers=[],
            next_action=READY_NEXT_ACTION,
            evidence=evidence,
        )

    return _result(
        broker_evidence_status=INVALID_TELEMETRY_EVIDENCE,
        broker_read_mode=_broker_read_mode(evidence),
        sanitized_broker_telemetry_ready=False,
        blockers=["recognized_sanitized_broker_telemetry_status_required"],
        next_action=INVALID_NEXT_ACTION,
        evidence=evidence,
    )


def render_trade_320_read_only_broker_telemetry_repair_report(
    result: Mapping[str, Any],
    *,
    branch: str = "UNKNOWN",
) -> str:
    blockers = result.get("blockers")
    blocker_text = ", ".join(str(item) for item in blockers) if blockers else "none"
    return "\n".join(
        [
            "# AIOS FOREX OANDA DEMO TRADE 320 READ ONLY BROKER TELEMETRY REPAIR V1 REPORT",
            "",
            f"- packet_name: {PACKET_NAME}",
            f"- repo_branch: {branch}",
            "- pr_1076_anchor: owner-run read-only refresh gate",
            "- pr_1077_anchor: preserved Packet 04 owner-run blocked evidence",
            (
                "- trade_320_anchor: EUR_USD long 1 entry 1.13596 "
                "TP 321 SL 322"
            ),
            "",
            "## Observed Packet 04 Owner-Run Result",
            "",
            "- broker_network_call_performed: true",
            "- broker_read_mode: OWNER_RUN_READ_ONLY_BROKER_REQUESTED",
            "- gate_status: BROKER_EVIDENCE_BLOCKED",
            "- script_status: BROKER_EVIDENCE_BLOCKED",
            "- no_new_order_placed: true",
            "- no_live_trade_placed: true",
            "- no_broker_state_modified: true",
            "- no_secrets_written: true",
            "- money_movement_allowed_now: false",
            "",
            "## Broker Telemetry Status",
            "",
            f"- broker_evidence_status: {result.get('broker_evidence_status')}",
            (
                "- broker_evidence_blocked: "
                f"{_true_false(result.get('broker_evidence_blocked'))}"
            ),
            (
                "- sanitized_broker_telemetry_ready: "
                f"{_true_false(result.get('sanitized_broker_telemetry_ready'))}"
            ),
            f"- broker_read_mode: {result.get('broker_read_mode')}",
            f"- monitor_bucket: {_display(result.get('monitor_bucket'))}",
            f"- result_bucket: {_display(result.get('result_bucket'))}",
            f"- realized_pl: {_display(result.get('realized_pl'))}",
            f"- unrealized_pl: {_display(result.get('unrealized_pl'))}",
            f"- open_trade_count: {_display(result.get('open_trade_count'))}",
            f"- open_position_count: {_display(result.get('open_position_count'))}",
            "",
            "## Blocker Diagnosis",
            "",
            f"- blockers: {blocker_text}",
            f"- next_action: {result.get('next_action')}",
            "",
            "## Real Broker Telemetry Doctrine",
            "",
            "- real broker telemetry is the dashboard goal when owner-authorized",
            "- broker reads must remain owner-run, read-only, GET-only, and sanitized",
            f"- broker_data_source_required: {result.get('broker_data_source_required')}",
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


def write_trade_320_read_only_broker_telemetry_repair_report(
    result: Mapping[str, Any],
    report_path: str | Path = REPORT_PATH,
    *,
    branch: str = "UNKNOWN",
) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_trade_320_read_only_broker_telemetry_repair_report(
            result,
            branch=branch,
        ),
        encoding="utf-8",
    )
    return path


def _result(
    *,
    broker_evidence_status: str,
    broker_read_mode: str,
    sanitized_broker_telemetry_ready: bool,
    blockers: Sequence[str],
    next_action: str,
    evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source = evidence or {}
    return {
        "packet_name": PACKET_NAME,
        "campaign_packet": CAMPAIGN_PACKET,
        "trade_id": TRADE_ID,
        "broker_read_mode": broker_read_mode,
        "broker_evidence_status": broker_evidence_status,
        "broker_evidence_blocked": broker_evidence_status
        != READ_ONLY_BROKER_TELEMETRY_READY,
        "sanitized_broker_telemetry_ready": sanitized_broker_telemetry_ready,
        "dashboard_real_broker_telemetry_goal": True,
        "dashboard_fake_numbers_allowed": False,
        "dashboard_mock_numbers_allowed": False,
        "broker_data_source_required": OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE,
        "monitor_bucket": _first_safe_value(
            source,
            ("monitor_bucket", "status_bucket", "current_bucket_result"),
        ),
        "result_bucket": _first_safe_value(
            source,
            ("result_bucket", "pl_result_bucket", "pl_capture_classification"),
        ),
        "realized_pl": _first_safe_value(source, ("realized_pl", "realizedPL", "pl")),
        "unrealized_pl": _first_safe_value(
            source,
            ("unrealized_pl", "unrealizedPL", "trueUnrealizedPL"),
        ),
        "open_trade_count": _first_safe_value(
            source,
            ("open_trade_count", "openTradeCount", "account_openTradeCount"),
        ),
        "open_position_count": _first_safe_value(
            source,
            ("open_position_count", "openPositionCount", "account_openPositionCount"),
        ),
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
        "withdrawal_allowed_now": False,
        "transfer_allowed_now": False,
        "money_movement_allowed_now": False,
        "profit_reserve_bucket_mode": INTERNAL_LEDGER_ONLY,
        "blockers": _unique([str(blocker) for blocker in blockers]),
        "next_action": next_action,
    }


def _broker_read_mode(evidence: Mapping[str, Any]) -> str:
    explicit = _first_present(
        evidence,
        ("broker_read_mode", "read_mode", "broker_mode"),
    )
    if explicit:
        return str(explicit)
    if evidence.get("owner_run_read_broker_now") is True:
        return OWNER_RUN_READ_ONLY_BROKER_REQUESTED
    return OWNER_RUN_READ_ONLY_BROKER_REQUESTED


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
        if "bearer " in lowered or "authorization:" in lowered or "sk-" in lowered:
            blockers.append(f"forbidden_secret_value_{_safe_path(path)}")
    return _unique(blockers)


def _sensitive_key(key: str) -> bool:
    key_text = key.lower()
    if key_text in {"credential_name", "credential_names"}:
        return False
    if key_text in SECRET_KEY_EXACT:
        return True
    return any(term in key_text for term in SECRET_KEY_TERMS)


def _helper_missing_blockers(evidence: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if evidence.get("read_only_helper_missing") is True:
        blockers.append("read_only_helper_missing_true")
    if evidence.get("safe_read_only_helper_available") is False:
        blockers.append("safe_read_only_helper_available_false")
    for status in _status_values(evidence):
        lowered = str(status).strip().lower()
        if any(term in lowered for term in HELPER_MISSING_TERMS):
            blockers.append(f"read_only_helper_missing_{_safe_label(status)}")
    for blocker in _sequence(evidence.get("blockers")):
        lowered = str(blocker).strip().lower()
        if any(term in lowered for term in HELPER_MISSING_TERMS):
            blockers.append(f"read_only_helper_missing_{_safe_label(blocker)}")
    return _unique(blockers)


def _unsanitized_blockers(evidence: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if evidence.get("sanitized_evidence_only") is False:
        blockers.append("sanitized_evidence_only_must_not_be_false")
    if evidence.get("sanitized_broker_telemetry_ready") is False and _ready_status_seen(
        evidence
    ):
        blockers.append("ready_status_requires_sanitized_broker_telemetry")
    for field in UNSANITIZED_TRUE_FIELDS:
        if evidence.get(field) is True:
            blockers.append(f"{field}_must_not_be_true")
    return _unique(blockers)


def _invalid_blockers(evidence: Mapping[str, Any]) -> list[str]:
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

    broker_read_mode = _broker_read_mode(evidence)
    if "LIVE" in broker_read_mode.upper():
        blockers.append("broker_read_mode_must_not_be_live")

    for field in MUTATION_TRUE_FIELDS:
        if evidence.get(field) is True:
            blockers.append(f"unsafe_{field}_true")

    for field in SAFETY_FALSE_FIELDS:
        if evidence.get(field) is False:
            blockers.append(f"{field}_must_not_be_false")

    for field in MONEY_MOVEMENT_TRUE_FIELDS:
        if evidence.get(field) is True:
            blockers.append(f"{field}_must_not_be_true")

    if evidence.get("dashboard_fake_numbers_allowed") is True:
        blockers.append("dashboard_fake_numbers_must_not_be_allowed")
    if evidence.get("dashboard_mock_numbers_allowed") is True:
        blockers.append("dashboard_mock_numbers_must_not_be_allowed")
    if evidence.get("profit_reserve_bucket_mode") not in {None, INTERNAL_LEDGER_ONLY}:
        blockers.append("profit_reserve_bucket_mode_must_be_internal_ledger_only")
    return _unique(blockers)


def _broker_blocked_blockers(evidence: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if evidence.get("broker_evidence_blocked") is True:
        blockers.append("broker_evidence_blocked_true")
    for status in _status_values(evidence):
        if _is_broker_blocked_status(status):
            blockers.append(f"broker_evidence_blocked_{_safe_label(status)}")
    for blocker in _sequence(evidence.get("blockers")):
        lowered = str(blocker).lower()
        if "blocked" in lowered or "broker" in lowered or "vault" in lowered:
            blockers.append(f"broker_blocker_{_safe_label(blocker)}")
    return _unique(blockers)


def _ready_telemetry(evidence: Mapping[str, Any]) -> bool:
    if not _ready_status_seen(evidence):
        return False
    if evidence.get("sanitized_evidence_only") is not True:
        return False
    if evidence.get("safe_read_only_helper_available") is not True:
        return False
    return _has_safe_telemetry(evidence)


def _ready_status_seen(evidence: Mapping[str, Any]) -> bool:
    return any(str(status).strip() in READY_STATUSES for status in _status_values(evidence))


def _has_safe_telemetry(evidence: Mapping[str, Any]) -> bool:
    fields = (
        "monitor_bucket",
        "status_bucket",
        "result_bucket",
        "pl_result_bucket",
        "realized_pl",
        "realizedPL",
        "unrealized_pl",
        "unrealizedPL",
        "open_trade_count",
        "openTradeCount",
        "open_position_count",
        "openPositionCount",
    )
    return any(_first_safe_value(evidence, (field,)) is not None for field in fields)


def _is_broker_blocked_status(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    return (
        text in BROKER_BLOCKED_STATUSES
        or text.startswith("BLOCKED_")
        or text.startswith("BROKER_EVIDENCE_BLOCKED")
    )


def _status_values(evidence: Mapping[str, Any]) -> list[Any]:
    values: list[Any] = []
    for key in (
        "broker_evidence_status",
        "gate_status",
        "helper_status",
        "script_status",
        "status",
        "status_bucket",
        "result_bucket",
        "pl_capture_classification",
    ):
        if key in evidence and evidence.get(key) is not None:
            values.append(evidence.get(key))
    result = evidence.get("result")
    if isinstance(result, Mapping):
        values.extend(_status_values(result))
    decision = evidence.get("decision")
    if isinstance(decision, Mapping):
        values.extend(_status_values(decision))
    return values


def _first_safe_value(source: Mapping[str, Any], keys: Sequence[str]) -> Any:
    direct = _first_present(source, keys)
    if _safe_scalar(direct):
        return direct
    for nested_key in ("result", "decision"):
        nested = source.get(nested_key)
        if isinstance(nested, Mapping):
            nested_value = _first_safe_value(nested, keys)
            if nested_value is not None:
                return nested_value
    return None


def _first_present(source: Mapping[str, Any], keys: Sequence[str]) -> Any:
    for key in keys:
        if key in source and source.get(key) is not None:
            return source.get(key)
    return None


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


def _display(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    text = str(value).strip()
    return text if text else "UNKNOWN"


def _true_false(value: Any) -> str:
    return "true" if value is True else "false"

