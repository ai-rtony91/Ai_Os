from __future__ import annotations

from collections.abc import Mapping, Sequence
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
from typing import Any

from automation.forex_engine.oanda_demo_sanitized_owner_run_read_only_telemetry_adapter_v1 import (
    ALLOWED_SANITIZED_FIELDS,
    BROKER_EVIDENCE_BLOCKED,
    FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE,
    INTERNAL_LEDGER_ONLY,
    OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE,
    REJECTED_RAW_PAYLOAD_FIELD_NAMES,
    REJECTED_SECRET_FIELD_NAMES,
    SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED,
    SANITIZED_OWNER_RUN_TELEMETRY_BROKER_BLOCKED,
    SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE,
    SANITIZED_OWNER_RUN_TELEMETRY_MISSING,
    SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_RAW_PAYLOAD,
    SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_SECRET_RISK,
    adapt_sanitized_owner_run_oanda_telemetry,
)


PACKET_NAME = (
    "AIOS FOREX OANDA DEMO OWNER RUN SANITIZED TELEMETRY CAPTURE ATTEMPT V1"
)
REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_ATTEMPT_V1_REPORT.md"
)

CAMPAIGN_PACKET = 8
TRADE_ID = 320
TRADE_ID_TEXT = "320"
INSTRUMENT = "EUR_USD"
SIDE = "long"
UNITS = 1
ENTRY_PRICE = "1.13596"

OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_NOT_REQUESTED = (
    "OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_NOT_REQUESTED"
)
OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_ACCEPTED = (
    "OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_ACCEPTED"
)
OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_BROKER_BLOCKED = (
    "OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_BROKER_BLOCKED"
)
OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_SECRET_RISK = (
    "OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_SECRET_RISK"
)
OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_RAW_PAYLOAD = (
    "OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_RAW_PAYLOAD"
)
OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_INVALID_SHAPE = (
    "OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_INVALID_SHAPE"
)
OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_HELPER_MISSING = (
    "OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_HELPER_MISSING"
)

NOT_REQUESTED = "NOT_REQUESTED"
OWNER_RUN_READ_ONLY_BROKER_REQUESTED = "OWNER_RUN_READ_ONLY_BROKER_REQUESTED"

DEFAULT_NEXT_ACTION = "RUN_WITH_OWNER_READ_BROKER_FLAG_TO_ATTEMPT_SANITIZED_CAPTURE"
ACCEPTED_NEXT_ACTION = "FEED_SANITIZED_TELEMETRY_TO_TRADE_320_PL_REFRESH"
BROKER_BLOCKED_NEXT_ACTION = "REPAIR_OWNER_READ_ONLY_HELPER_OR_RUNTIME_AUTH_BOUNDARY"
SECRET_NEXT_ACTION = "STOP_REMOVE_SECRET_FIELDS_AND_RETRY_SANITIZED_OUTPUT"
RAW_PAYLOAD_NEXT_ACTION = "STOP_REMOVE_RAW_PAYLOAD_AND_RETRY_SANITIZED_OUTPUT"
INVALID_NEXT_ACTION = "FIX_SANITIZED_OWNER_RUN_TELEMETRY_SHAPE"
HELPER_MISSING_NEXT_ACTION = "RESTORE_OR_REGISTER_OWNER_RUN_READ_ONLY_HELPER"

ALLOWED_SANITIZED_FIELD_SET = set(ALLOWED_SANITIZED_FIELDS)

REQUIRED_SANITIZED_FIELDS = (
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
    "result_bucket": ("result_bucket", "pl_result_bucket", "pl_capture_classification"),
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

SECRET_KEY_TERMS = tuple(REJECTED_SECRET_FIELD_NAMES)
RAW_PAYLOAD_KEY_TERMS = tuple(REJECTED_RAW_PAYLOAD_FIELD_NAMES)


def run_owner_sanitized_telemetry_capture_attempt(
    evidence: dict | None = None,
    *,
    owner_run_read_broker_now: bool = False,
) -> dict[str, Any]:
    if evidence is None and owner_run_read_broker_now is not True:
        adapter_result = adapt_sanitized_owner_run_oanda_telemetry()
        return _capture_result(
            capture_status=OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_NOT_REQUESTED,
            adapter_result=adapter_result,
            broker_read_performed=False,
            broker_network_call_performed=False,
            raw_broker_payload_persisted=False,
            blockers=["owner_run_read_broker_now_flag_required"],
            next_action=DEFAULT_NEXT_ACTION,
        )

    raw_or_helper_result = evidence
    helper_missing = False
    helper_blockers: list[str] = []
    helper_network_call = False
    if raw_or_helper_result is None:
        raw_or_helper_result = _owner_run_read_only_helper_result()
        helper_status = str(raw_or_helper_result.get("helper_capture_status", ""))
        helper_missing = helper_status == OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_HELPER_MISSING
        helper_blockers = _sequence_text(raw_or_helper_result.get("blockers"))
        helper_network_call = raw_or_helper_result.get("broker_network_call_performed") is True

    if helper_missing:
        adapter_result = adapt_sanitized_owner_run_oanda_telemetry()
        return _capture_result(
            capture_status=OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_HELPER_MISSING,
            adapter_result=adapter_result,
            broker_read_performed=False,
            broker_network_call_performed=helper_network_call,
            raw_broker_payload_persisted=False,
            blockers=helper_blockers or ["owner_run_read_only_helper_missing"],
            next_action=HELPER_MISSING_NEXT_ACTION,
        )

    sanitized = sanitize_owner_run_telemetry_capture(raw_or_helper_result)
    adapter_input = sanitized.get("adapter_input")
    adapter_evidence = adapter_input if isinstance(adapter_input, dict) else {}
    if _secret_field_paths(raw_or_helper_result):
        adapter_evidence = raw_or_helper_result
    elif _raw_payload_field_paths(raw_or_helper_result):
        adapter_evidence = raw_or_helper_result

    adapter_result = adapt_sanitized_owner_run_oanda_telemetry(adapter_evidence)
    capture_status = _capture_status_from_adapter(adapter_result)
    return _capture_result(
        capture_status=capture_status,
        adapter_result=adapter_result,
        broker_read_performed=owner_run_read_broker_now is True,
        broker_network_call_performed=(
            helper_network_call
            or _broker_network_call_performed(raw_or_helper_result, owner_run_read_broker_now)
        ),
        raw_broker_payload_persisted=False,
        blockers=_unique(
            _sequence_text(adapter_result.get("blockers"))
            + _sequence_text(sanitized.get("blockers"))
        ),
        next_action=_next_action(capture_status, adapter_result),
    )


def sanitize_owner_run_telemetry_capture(raw_or_helper_result: dict) -> dict[str, Any]:
    if not isinstance(raw_or_helper_result, Mapping):
        return {
            "sanitization_status": OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_INVALID_SHAPE,
            "adapter_input": {},
            "blockers": ["helper_result_must_be_mapping"],
        }

    secret_fields = _secret_field_paths(raw_or_helper_result)
    if secret_fields:
        return {
            "sanitization_status": OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_SECRET_RISK,
            "adapter_input": {},
            "rejected_secret_fields": secret_fields,
            "blockers": [f"forbidden_secret_field_{field}" for field in secret_fields],
        }

    raw_payload_fields = _raw_payload_field_paths(raw_or_helper_result)
    if raw_payload_fields:
        return {
            "sanitization_status": OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_RAW_PAYLOAD,
            "adapter_input": {},
            "rejected_raw_payload_fields": raw_payload_fields,
            "blockers": [
                f"forbidden_raw_payload_field_{field}"
                for field in raw_payload_fields
            ],
        }

    source = _primary_payload(raw_or_helper_result)
    adapter_input: dict[str, Any] = {}
    for field in ALLOWED_SANITIZED_FIELDS:
        value = _first_safe_value(source, raw_or_helper_result, keys=FIELD_ALIASES[field])
        if value is not None and _safe_value_for_field(field, value):
            adapter_input[field] = value

    if "broker_read_mode" not in adapter_input:
        adapter_input["broker_read_mode"] = OWNER_RUN_READ_ONLY_BROKER_REQUESTED
    if "broker_evidence_status" not in adapter_input:
        adapter_input["broker_evidence_status"] = _derived_broker_evidence_status(
            source,
            raw_or_helper_result,
        )
    if "evidence_source" not in adapter_input:
        adapter_input["evidence_source"] = "owner_run_sanitized_telemetry_capture"

    blockers = _sanitized_shape_blockers(adapter_input)
    status = (
        OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_INVALID_SHAPE
        if blockers
        else OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_ACCEPTED
    )
    return {
        "sanitization_status": status,
        "adapter_input": adapter_input,
        "blockers": blockers,
    }


def render_owner_run_sanitized_telemetry_capture_attempt_report(
    result: Mapping[str, Any],
    *,
    branch: str = "UNKNOWN",
) -> str:
    blockers = result.get("blockers")
    blocker_text = ", ".join(str(item) for item in blockers) if blockers else "none"
    return "\n".join(
        [
            "# AIOS FOREX OANDA DEMO OWNER RUN SANITIZED TELEMETRY CAPTURE ATTEMPT V1 REPORT",
            "",
            f"- packet_name: {PACKET_NAME}",
            f"- repo_branch: {branch}",
            "- pr_1080_anchor: sanitized owner-run read-only telemetry adapter",
            f"- capture_status: {result.get('capture_status')}",
            f"- adapter_status: {result.get('adapter_status')}",
            (
                "- sanitized_broker_telemetry_ready: "
                f"{_yes_no(result.get('sanitized_broker_telemetry_ready'))}"
            ),
            (
                "- broker_read_performed: "
                f"{_yes_no(result.get('broker_read_performed'))}"
            ),
            (
                "- broker_network_call_performed: "
                f"{_yes_no(result.get('broker_network_call_performed'))}"
            ),
            f"- broker_evidence_status: {result.get('broker_evidence_status')}",
            f"- next_action: {result.get('next_action')}",
            f"- blockers: {blocker_text}",
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
            (
                "- raw broker payload persisted: "
                f"{_true_false(result.get('raw_broker_payload_persisted'))}"
            ),
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


def write_owner_run_sanitized_telemetry_capture_attempt_report(
    result: Mapping[str, Any],
    report_path: str | Path = REPORT_PATH,
    *,
    branch: str = "UNKNOWN",
) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_owner_run_sanitized_telemetry_capture_attempt_report(
            result,
            branch=branch,
        ),
        encoding="utf-8",
    )
    return path


def _owner_run_read_only_helper_result() -> dict[str, Any]:
    try:
        from scripts.forex_delivery.run_oanda_demo_trade_320_read_only_pl_refresh_v1 import (  # noqa: E501
            main as read_only_pl_refresh_main,
        )
    except Exception as exc:  # pragma: no cover - defensive runtime boundary
        return _helper_missing_result(
            f"read_only_pl_refresh_helper_import_failed_{type(exc).__name__}"
        )

    stream = StringIO()
    try:
        with redirect_stdout(stream):
            read_only_pl_refresh_main(["--owner-run-read-broker-now", "--json"])
    except Exception as exc:  # pragma: no cover - defensive runtime boundary
        return _helper_missing_result(
            f"read_only_pl_refresh_helper_execution_failed_{type(exc).__name__}"
        )
    payload = _json_mapping(stream.getvalue())
    payload["broker_network_call_performed"] = (
        payload.get("broker_network_call_performed") is True
    )
    return payload


def _helper_missing_result(blocker: str) -> dict[str, Any]:
    return {
        "helper_capture_status": OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_HELPER_MISSING,
        "broker_network_call_performed": False,
        "blockers": [_safe_label(blocker)],
    }


def _capture_result(
    *,
    capture_status: str,
    adapter_result: Mapping[str, Any],
    broker_read_performed: bool,
    broker_network_call_performed: bool,
    raw_broker_payload_persisted: bool,
    blockers: Sequence[str],
    next_action: str,
) -> dict[str, Any]:
    return {
        "packet_name": PACKET_NAME,
        "campaign_packet": CAMPAIGN_PACKET,
        "capture_status": capture_status,
        "adapter_status": adapter_result.get("adapter_status"),
        "sanitized_broker_telemetry_ready": adapter_result.get(
            "sanitized_broker_telemetry_ready"
        )
        is True,
        "broker_read_performed": broker_read_performed,
        "broker_network_call_performed": broker_network_call_performed,
        "broker_read_mode": adapter_result.get("broker_read_mode", NOT_REQUESTED),
        "broker_evidence_status": adapter_result.get("broker_evidence_status"),
        "dashboard_real_broker_telemetry_goal": True,
        "dashboard_fake_numbers_allowed": False,
        "dashboard_mock_numbers_allowed": False,
        "broker_data_source_required": OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE,
        "bank_data_source_required": FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE,
        "trade_id": adapter_result.get("trade_id", TRADE_ID),
        "instrument": adapter_result.get("instrument", INSTRUMENT),
        "side": adapter_result.get("side", SIDE),
        "units": adapter_result.get("units", UNITS),
        "entry_price": adapter_result.get("entry_price", ENTRY_PRICE),
        "realized_pl": adapter_result.get("realized_pl"),
        "unrealized_pl": adapter_result.get("unrealized_pl"),
        "open_trade_count": adapter_result.get("open_trade_count"),
        "open_position_count": adapter_result.get("open_position_count"),
        "monitor_bucket": adapter_result.get("monitor_bucket"),
        "result_bucket": adapter_result.get("result_bucket"),
        "repeat_proof_lane_status": adapter_result.get(
            "repeat_proof_lane_status"
        ),
        "repeat_proof_eligible": adapter_result.get("repeat_proof_eligible") is True,
        "profit_evidence": adapter_result.get("profit_evidence") is True,
        "withdrawal_allowed_now": False,
        "transfer_allowed_now": False,
        "money_movement_allowed_now": False,
        "profit_reserve_bucket_mode": INTERNAL_LEDGER_ONLY,
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
        "raw_broker_payload_persisted": raw_broker_payload_persisted,
        "blockers": _unique([str(blocker) for blocker in blockers]),
        "next_action": next_action,
    }


def _capture_status_from_adapter(adapter_result: Mapping[str, Any]) -> str:
    adapter_status = adapter_result.get("adapter_status")
    return {
        SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED: (
            OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_ACCEPTED
        ),
        SANITIZED_OWNER_RUN_TELEMETRY_BROKER_BLOCKED: (
            OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_BROKER_BLOCKED
        ),
        SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_SECRET_RISK: (
            OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_SECRET_RISK
        ),
        SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_RAW_PAYLOAD: (
            OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_RAW_PAYLOAD
        ),
        SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE: (
            OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_INVALID_SHAPE
        ),
        SANITIZED_OWNER_RUN_TELEMETRY_MISSING: (
            OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_HELPER_MISSING
        ),
    }.get(str(adapter_status), OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_INVALID_SHAPE)


def _next_action(capture_status: str, adapter_result: Mapping[str, Any]) -> str:
    if capture_status == OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_ACCEPTED:
        return ACCEPTED_NEXT_ACTION
    if capture_status == OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_BROKER_BLOCKED:
        return BROKER_BLOCKED_NEXT_ACTION
    if capture_status == OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_SECRET_RISK:
        return SECRET_NEXT_ACTION
    if capture_status == OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_RAW_PAYLOAD:
        return RAW_PAYLOAD_NEXT_ACTION
    if capture_status == OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_HELPER_MISSING:
        return HELPER_MISSING_NEXT_ACTION
    return str(adapter_result.get("next_action") or INVALID_NEXT_ACTION)


def _primary_payload(evidence: Mapping[str, Any]) -> Mapping[str, Any]:
    result = evidence.get("result")
    if isinstance(result, Mapping):
        return result
    decision = evidence.get("decision")
    if isinstance(decision, Mapping):
        result = decision.get("result")
        if isinstance(result, Mapping):
            return result
        return decision
    return evidence


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
    for mapping in mappings:
        for nested_key in ("result", "decision"):
            nested = mapping.get(nested_key)
            if isinstance(nested, Mapping):
                nested_value = _first_safe_value(nested, keys=keys)
                if nested_value is not None:
                    return nested_value
    return None


def _sanitized_shape_blockers(adapter_input: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field in REQUIRED_SANITIZED_FIELDS:
        if field not in adapter_input or adapter_input.get(field) is None:
            blockers.append(f"{field}_required")
    trade_id = adapter_input.get("trade_id")
    if trade_id is not None and str(trade_id).strip() != TRADE_ID_TEXT:
        blockers.append("trade_id_must_be_320")
    instrument = adapter_input.get("instrument")
    if instrument is not None and str(instrument).strip() != INSTRUMENT:
        blockers.append("instrument_must_be_EUR_USD")
    return _unique(blockers)


def _derived_broker_evidence_status(
    *mappings: Mapping[str, Any],
) -> str:
    status_values = []
    for mapping in mappings:
        if not isinstance(mapping, Mapping):
            continue
        for key in ("broker_evidence_status", "status", "script_status", "result_bucket"):
            if mapping.get(key) is not None:
                status_values.append(str(mapping.get(key)))
    if any(_is_broker_blocked_status(status) for status in status_values):
        return BROKER_EVIDENCE_BLOCKED
    return "OWNER_RUN_READ_ONLY_EVIDENCE_CLASSIFIED"


def _broker_network_call_performed(value: Any, owner_run_read_broker_now: bool) -> bool:
    if owner_run_read_broker_now is not True:
        return False
    if isinstance(value, Mapping):
        if value.get("broker_network_call_performed") is True:
            return True
        result = value.get("result")
        if isinstance(result, Mapping) and result.get("broker_network_call_performed") is True:
            return True
    return False


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


def _safe_value_for_field(field: str, value: Any) -> bool:
    if field in BOOL_FIELDS:
        return isinstance(value, bool)
    if isinstance(value, bool):
        return False
    return isinstance(value, (str, int, float))


def _safe_scalar_or_bool(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool)) and value is not None


def _is_broker_blocked_status(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    return (
        text in BROKER_BLOCKED_STATUSES
        or text.startswith("BLOCKED_")
        or text.startswith("BROKER_EVIDENCE_BLOCKED")
    )


def _json_mapping(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return _helper_missing_result("read_only_pl_refresh_helper_json_parse_failed")
    return parsed if isinstance(parsed, dict) else _helper_missing_result(
        "read_only_pl_refresh_helper_json_root_not_object"
    )


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


def _safe_path(path: Sequence[str]) -> str:
    text = "_".join(_safe_label(part) for part in path if str(part).strip())
    return text or "root"


def _safe_label(value: Any) -> str:
    text = str(value).strip().lower()
    cleaned = "".join(char if char.isalnum() else "_" for char in text)
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    return cleaned.strip("_")[:100] or "unknown"


def _display(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    text = str(value).strip()
    return text if text else "UNKNOWN"


def _yes_no(value: Any) -> str:
    return "yes" if value is True else "no"


def _true_false(value: Any) -> str:
    return "true" if value is True else "false"
