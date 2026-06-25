from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from automation.forex_engine.oanda_demo_sanitized_owner_run_read_only_telemetry_adapter_v1 import (
    ACCEPTED_REQUIRED_FIELDS,
    ALLOWED_SANITIZED_FIELDS,
    BROKER_EVIDENCE_BLOCKED,
    FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE,
    INTERNAL_LEDGER_ONLY,
    NOT_REQUESTED,
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


PACKET_NAME = "AIOS FOREX OANDA DEMO SANITIZED TELEMETRY SHAPE NORMALIZER V1"
REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_SANITIZED_TELEMETRY_SHAPE_NORMALIZER_V1_REPORT.md"
)

CAMPAIGN_PACKET = 10
TRADE_ID = 320
TRADE_ID_TEXT = "320"
INSTRUMENT = "EUR_USD"
SIDE = "long"
UNITS = 1
ENTRY_PRICE = "1.13596"

OWNER_RUN_READ_ONLY_BROKER_REQUESTED = "OWNER_RUN_READ_ONLY_BROKER_REQUESTED"
OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_V1 = (
    "OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_V1"
)
NORMALIZED_OWNER_RUN_SANITIZED_TELEMETRY_READY = (
    "NORMALIZED_OWNER_RUN_SANITIZED_TELEMETRY_READY"
)

SANITIZED_TELEMETRY_SHAPE_NORMALIZER_NOT_REQUESTED = (
    "SANITIZED_TELEMETRY_SHAPE_NORMALIZER_NOT_REQUESTED"
)
SANITIZED_TELEMETRY_SHAPE_NORMALIZER_ACCEPTED = (
    "SANITIZED_TELEMETRY_SHAPE_NORMALIZER_ACCEPTED"
)
SANITIZED_TELEMETRY_SHAPE_NORMALIZER_INVALID_SHAPE = (
    "SANITIZED_TELEMETRY_SHAPE_NORMALIZER_INVALID_SHAPE"
)
SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_SECRET_RISK = (
    "SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_SECRET_RISK"
)
SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_RAW_PAYLOAD = (
    "SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_RAW_PAYLOAD"
)
SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_UNSAFE_AUDIT_FLAG = (
    "SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_UNSAFE_AUDIT_FLAG"
)
SANITIZED_TELEMETRY_SHAPE_NORMALIZER_BROKER_BLOCKED = (
    "SANITIZED_TELEMETRY_SHAPE_NORMALIZER_BROKER_BLOCKED"
)

DEFAULT_NEXT_ACTION = "FEED_PACKET_09_SANITIZED_OWNER_RUN_OUTPUT_TO_NORMALIZER"
ACCEPTED_NEXT_ACTION = (
    "FEED_SANITIZED_TELEMETRY_TO_TRADE_320_PL_REFRESH_AND_REPEAT_PROOF_GATE"
)
INVALID_NEXT_ACTION = "CAPTURE_REQUIRED_FIELDS_FROM_OWNER_READ_HELPER_WITHOUT_RAW_PAYLOAD"
SECRET_NEXT_ACTION = "STOP_REMOVE_SECRET_FIELDS_AND_RETRY_SANITIZED_OUTPUT"
RAW_PAYLOAD_NEXT_ACTION = "STOP_REMOVE_RAW_PAYLOAD_AND_RETRY_SANITIZED_OUTPUT"
UNSAFE_AUDIT_NEXT_ACTION = "STOP_FIX_UNSAFE_AUDIT_FLAGS_AND_RETRY_SANITIZED_OUTPUT"
BROKER_BLOCKED_NEXT_ACTION = "REPAIR_OWNER_READ_ONLY_HELPER_OR_RUNTIME_AUTH_BOUNDARY"

SAFE_TRUE_AUDIT_FIELDS = {
    "no_secrets_written",
    "no_broker_state_modified",
    "no_new_order_placed",
    "no_live_trade_placed",
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
SAFE_AUDIT_FIELDS = SAFE_TRUE_AUDIT_FIELDS | SAFE_FALSE_AUDIT_FIELDS

SAFE_TRUE_CONTROL_FIELDS = {
    "dashboard_real_broker_telemetry_goal",
}
SAFE_FALSE_CONTROL_FIELDS = {
    "dashboard_fake_numbers_allowed",
    "dashboard_mock_numbers_allowed",
    "withdrawal_allowed_now",
    "transfer_allowed_now",
    "money_movement_allowed_now",
}
SAFE_CONTROL_FIELDS = SAFE_TRUE_CONTROL_FIELDS | SAFE_FALSE_CONTROL_FIELDS

FORBIDDEN_SECRET_FIELD_NAMES = set(REJECTED_SECRET_FIELD_NAMES) | {
    "request_headers",
}
FORBIDDEN_RAW_PAYLOAD_FIELD_NAMES = set(REJECTED_RAW_PAYLOAD_FIELD_NAMES)

FAKE_MOCK_DASHBOARD_FIELD_NAMES = {
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

BOOL_FIELDS = {
    "repeat_proof_eligible",
    "profit_evidence",
}
INT_FIELDS = {
    "trade_id",
    "units",
    "open_trade_count",
    "open_position_count",
}
STRING_FIELDS = {
    "instrument",
    "side",
    "entry_price",
    "realized_pl",
    "unrealized_pl",
    "monitor_bucket",
    "result_bucket",
    "repeat_proof_lane_status",
    "broker_read_mode",
    "broker_evidence_status",
    "evidence_timestamp_utc",
    "evidence_source",
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


def normalize_sanitized_owner_run_telemetry_shape(
    evidence: dict | None = None,
) -> dict[str, Any]:
    if evidence is None:
        adapter_result = adapt_sanitized_owner_run_oanda_telemetry()
        return _normalizer_result(
            normalizer_status=SANITIZED_TELEMETRY_SHAPE_NORMALIZER_NOT_REQUESTED,
            adapter_result=adapter_result,
            normalized_adapter_input=None,
            normalized_adapter_input_ready=False,
            normalized_sanitized_evidence_persisted=False,
            broker_read_performed=False,
            broker_network_call_performed=False,
            rejected_secret_fields=[],
            rejected_raw_payload_fields=[],
            rejected_forbidden_fields=[],
            invalid_shape_blockers=[],
            missing_required_fields=[],
            blockers=["sanitized_owner_run_telemetry_not_requested"],
            next_action=DEFAULT_NEXT_ACTION,
        )

    if not isinstance(evidence, Mapping):
        return _rejected_result(
            normalizer_status=SANITIZED_TELEMETRY_SHAPE_NORMALIZER_INVALID_SHAPE,
            adapter_status=SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE,
            broker_evidence_status=SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE,
            broker_read_mode=NOT_REQUESTED,
            blockers=["evidence_must_be_mapping"],
            next_action=INVALID_NEXT_ACTION,
        )

    audit_violations = _unsafe_audit_flag_paths(evidence)
    if audit_violations:
        return _rejected_result(
            normalizer_status=(
                SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_UNSAFE_AUDIT_FLAG
            ),
            adapter_status=SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE,
            broker_evidence_status=(
                SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_UNSAFE_AUDIT_FLAG
            ),
            broker_read_mode=_safe_text_value(evidence.get("broker_read_mode"), NOT_REQUESTED),
            invalid_shape_blockers=[
                f"unsafe_audit_flag_{field}" for field in audit_violations
            ],
            blockers=[f"unsafe_audit_flag_{field}" for field in audit_violations],
            next_action=UNSAFE_AUDIT_NEXT_ACTION,
            source=evidence,
        )

    fake_mock_fields = _fake_mock_dashboard_field_paths(evidence)
    if fake_mock_fields:
        return _rejected_result(
            normalizer_status=SANITIZED_TELEMETRY_SHAPE_NORMALIZER_INVALID_SHAPE,
            adapter_status=SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE,
            broker_evidence_status=SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE,
            broker_read_mode=_safe_text_value(evidence.get("broker_read_mode"), NOT_REQUESTED),
            rejected_forbidden_fields=fake_mock_fields,
            invalid_shape_blockers=[
                f"fake_or_mock_dashboard_field_{field}" for field in fake_mock_fields
            ],
            blockers=[
                f"fake_or_mock_dashboard_field_{field}" for field in fake_mock_fields
            ],
            next_action=INVALID_NEXT_ACTION,
            source=evidence,
        )

    secret_fields = _secret_field_paths(evidence)
    if secret_fields:
        return _rejected_result(
            normalizer_status=(
                SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_SECRET_RISK
            ),
            adapter_status=SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_SECRET_RISK,
            broker_evidence_status=SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_SECRET_RISK,
            broker_read_mode=_safe_text_value(evidence.get("broker_read_mode"), NOT_REQUESTED),
            rejected_secret_fields=secret_fields,
            rejected_forbidden_fields=secret_fields,
            blockers=[f"forbidden_secret_field_{field}" for field in secret_fields],
            next_action=SECRET_NEXT_ACTION,
            source=evidence,
        )

    raw_payload_fields = _raw_payload_field_paths(evidence)
    if raw_payload_fields:
        return _rejected_result(
            normalizer_status=(
                SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_RAW_PAYLOAD
            ),
            adapter_status=SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_RAW_PAYLOAD,
            broker_evidence_status=SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_RAW_PAYLOAD,
            broker_read_mode=_safe_text_value(evidence.get("broker_read_mode"), NOT_REQUESTED),
            rejected_raw_payload_fields=raw_payload_fields,
            rejected_forbidden_fields=raw_payload_fields,
            blockers=[
                f"forbidden_raw_payload_field_{field}" for field in raw_payload_fields
            ],
            next_action=RAW_PAYLOAD_NEXT_ACTION,
            source=evidence,
        )

    normalized_adapter_input = _normalized_adapter_input(evidence)
    adapter_result = adapt_sanitized_owner_run_oanda_telemetry(
        normalized_adapter_input,
    )
    adapter_status = str(adapter_result.get("adapter_status") or "")
    missing_required_fields = _missing_required_fields(normalized_adapter_input)
    invalid_shape_blockers = _sequence_text(
        adapter_result.get("invalid_shape_blockers"),
    )
    blockers = _sequence_text(adapter_result.get("blockers"))

    if adapter_status == SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED:
        return _normalizer_result(
            normalizer_status=SANITIZED_TELEMETRY_SHAPE_NORMALIZER_ACCEPTED,
            adapter_result=adapter_result,
            normalized_adapter_input=normalized_adapter_input,
            normalized_adapter_input_ready=True,
            normalized_sanitized_evidence_persisted=True,
            broker_read_performed=_broker_read_performed(evidence),
            broker_network_call_performed=_broker_network_call_performed(evidence),
            rejected_secret_fields=[],
            rejected_raw_payload_fields=[],
            rejected_forbidden_fields=[],
            invalid_shape_blockers=[],
            missing_required_fields=[],
            blockers=[],
            next_action=ACCEPTED_NEXT_ACTION,
        )

    if adapter_status == SANITIZED_OWNER_RUN_TELEMETRY_BROKER_BLOCKED:
        return _normalizer_result(
            normalizer_status=SANITIZED_TELEMETRY_SHAPE_NORMALIZER_BROKER_BLOCKED,
            adapter_result=adapter_result,
            normalized_adapter_input=normalized_adapter_input,
            normalized_adapter_input_ready=False,
            normalized_sanitized_evidence_persisted=False,
            broker_read_performed=_broker_read_performed(evidence),
            broker_network_call_performed=_broker_network_call_performed(evidence),
            rejected_secret_fields=[],
            rejected_raw_payload_fields=[],
            rejected_forbidden_fields=[],
            invalid_shape_blockers=invalid_shape_blockers,
            missing_required_fields=missing_required_fields,
            blockers=blockers,
            next_action=BROKER_BLOCKED_NEXT_ACTION,
        )

    normalizer_status = SANITIZED_TELEMETRY_SHAPE_NORMALIZER_INVALID_SHAPE
    next_action = INVALID_NEXT_ACTION
    if adapter_status == SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_SECRET_RISK:
        normalizer_status = SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_SECRET_RISK
        next_action = SECRET_NEXT_ACTION
    elif adapter_status == SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_RAW_PAYLOAD:
        normalizer_status = SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_RAW_PAYLOAD
        next_action = RAW_PAYLOAD_NEXT_ACTION

    return _normalizer_result(
        normalizer_status=normalizer_status,
        adapter_result=adapter_result,
        normalized_adapter_input=normalized_adapter_input,
        normalized_adapter_input_ready=False,
        normalized_sanitized_evidence_persisted=False,
        broker_read_performed=_broker_read_performed(evidence),
        broker_network_call_performed=_broker_network_call_performed(evidence),
        rejected_secret_fields=_sequence_text(adapter_result.get("rejected_secret_fields")),
        rejected_raw_payload_fields=_sequence_text(
            adapter_result.get("rejected_raw_payload_fields"),
        ),
        rejected_forbidden_fields=_unique(
            _sequence_text(adapter_result.get("rejected_secret_fields"))
            + _sequence_text(adapter_result.get("rejected_raw_payload_fields"))
        ),
        invalid_shape_blockers=invalid_shape_blockers,
        missing_required_fields=missing_required_fields,
        blockers=blockers or missing_required_fields,
        next_action=next_action,
    )


def run_sanitized_telemetry_shape_normalizer(
    evidence: dict | None = None,
) -> dict[str, Any]:
    return normalize_sanitized_owner_run_telemetry_shape(evidence)


def render_sanitized_telemetry_shape_normalizer_report(
    result: Mapping[str, Any],
    *,
    branch: str = "UNKNOWN",
) -> str:
    blockers = _sequence_text(result.get("blockers"))
    blocker_text = ", ".join(blockers) if blockers else "none"
    accepted_fields = _sequence_text(result.get("accepted_sanitized_fields"))
    missing_fields = _sequence_text(result.get("missing_required_fields"))
    rejected_fields = _sequence_text(result.get("rejected_forbidden_fields"))
    return "\n".join(
        [
            "# AIOS FOREX OANDA DEMO SANITIZED TELEMETRY SHAPE NORMALIZER V1 REPORT",
            "",
            f"- packet_name: {PACKET_NAME}",
            "- pr_1082_anchor: owner-run sanitized telemetry exercise",
            f"- repo_branch: {branch}",
            f"- normalizer_status: {_display(result.get('normalizer_status'))}",
            f"- adapter_status: {_display(result.get('adapter_status'))}",
            (
                "- sanitized_broker_telemetry_ready: "
                f"{_yes_no(result.get('sanitized_broker_telemetry_ready'))}"
            ),
            (
                "- normalized_adapter_input_ready: "
                f"{_yes_no(result.get('normalized_adapter_input_ready'))}"
            ),
            f"- broker_read_performed: {_yes_no(result.get('broker_read_performed'))}",
            (
                "- broker_network_call_performed: "
                f"{_yes_no(result.get('broker_network_call_performed'))}"
            ),
            f"- broker_evidence_status: {_display(result.get('broker_evidence_status'))}",
            f"- next_action: {_display(result.get('next_action'))}",
            f"- blockers: {blocker_text}",
            "",
            "## Normalized Accepted Fields",
            "",
            *([f"- {field}" for field in accepted_fields] or ["- none"]),
            "",
            "## Missing Required Fields",
            "",
            *([f"- {field}" for field in missing_fields] or ["- none"]),
            "",
            "## Rejected Forbidden Fields",
            "",
            *([f"- {field}" for field in rejected_fields] or ["- none"]),
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
            (
                "- broker_data_source_required: "
                f"{_display(result.get('broker_data_source_required'))}"
            ),
            (
                "- bank_data_source_required: "
                f"{_display(result.get('bank_data_source_required'))}"
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
            (
                "- profit_reserve_bucket_mode: "
                f"{_display(result.get('profit_reserve_bucket_mode'))}"
            ),
            "",
            "## Safety Statements",
            "",
            "- no new order placed",
            "- no live trade placed",
            "- no broker state modified",
            "- no secrets written",
            "- raw broker payload persisted: false",
            "",
            "## Machine Result",
            "",
            f"- campaign_packet: {CAMPAIGN_PACKET}",
            f"- trade_id: {_display(result.get('trade_id'))}",
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
                "- normalized_sanitized_evidence_persisted: "
                f"{_true_false(result.get('normalized_sanitized_evidence_persisted'))}"
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
            "",
        ]
    )


def write_sanitized_telemetry_shape_normalizer_report(
    result: Mapping[str, Any],
    report_path: str | Path = REPORT_PATH,
    *,
    branch: str = "UNKNOWN",
) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_sanitized_telemetry_shape_normalizer_report(
            result,
            branch=branch,
        ),
        encoding="utf-8",
    )
    return path


def _normalized_adapter_input(evidence: Mapping[str, Any]) -> dict[str, Any]:
    primary = _primary_payload(evidence)
    normalized: dict[str, Any] = {}

    for field in ALLOWED_SANITIZED_FIELDS:
        value = _first_safe_value(primary, evidence, keys=FIELD_ALIASES[field])
        normalized_value = _normalize_field_value(field, value)
        if normalized_value is not None:
            normalized[field] = normalized_value

    if "broker_read_mode" not in normalized and _broker_read_performed(evidence):
        normalized["broker_read_mode"] = OWNER_RUN_READ_ONLY_BROKER_REQUESTED

    if "evidence_source" not in normalized and _is_packet_09_style(evidence):
        normalized["evidence_source"] = OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_V1

    broker_status = normalized.get("broker_evidence_status")
    if _can_mark_normalized_ready(normalized) and not _broker_status_blocked(
        broker_status,
    ):
        normalized["broker_evidence_status"] = (
            NORMALIZED_OWNER_RUN_SANITIZED_TELEMETRY_READY
        )

    return normalized


def _normalizer_result(
    *,
    normalizer_status: str,
    adapter_result: Mapping[str, Any],
    normalized_adapter_input: Mapping[str, Any] | None,
    normalized_adapter_input_ready: bool,
    normalized_sanitized_evidence_persisted: bool,
    broker_read_performed: bool,
    broker_network_call_performed: bool,
    rejected_secret_fields: Sequence[str],
    rejected_raw_payload_fields: Sequence[str],
    rejected_forbidden_fields: Sequence[str],
    invalid_shape_blockers: Sequence[str],
    missing_required_fields: Sequence[str],
    blockers: Sequence[str],
    next_action: str,
) -> dict[str, Any]:
    source = normalized_adapter_input or adapter_result
    adapter_status = str(
        adapter_result.get("adapter_status")
        or SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE
    )
    return {
        "packet_name": PACKET_NAME,
        "campaign_packet": CAMPAIGN_PACKET,
        "normalizer_status": normalizer_status,
        "adapter_status": adapter_status,
        "sanitized_broker_telemetry_ready": (
            adapter_result.get("sanitized_broker_telemetry_ready") is True
            and normalizer_status == SANITIZED_TELEMETRY_SHAPE_NORMALIZER_ACCEPTED
        ),
        "normalized_adapter_input_ready": normalized_adapter_input_ready,
        "broker_read_performed": broker_read_performed,
        "broker_network_call_performed": broker_network_call_performed,
        "broker_read_mode": _field_value(source, "broker_read_mode", NOT_REQUESTED),
        "broker_evidence_status": _field_value(
            source,
            "broker_evidence_status",
            BROKER_EVIDENCE_BLOCKED,
        ),
        "dashboard_real_broker_telemetry_goal": True,
        "dashboard_fake_numbers_allowed": False,
        "dashboard_mock_numbers_allowed": False,
        "broker_data_source_required": OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE,
        "bank_data_source_required": FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE,
        "trade_id": _field_value(source, "trade_id", TRADE_ID),
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
        "repeat_proof_eligible": _field_value(source, "repeat_proof_eligible"),
        "profit_evidence": _field_value(source, "profit_evidence"),
        "withdrawal_allowed_now": False,
        "transfer_allowed_now": False,
        "money_movement_allowed_now": False,
        "profit_reserve_bucket_mode": INTERNAL_LEDGER_ONLY,
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
        "raw_broker_payload_persisted": False,
        "normalized_sanitized_evidence_persisted": (
            normalized_sanitized_evidence_persisted
        ),
        "accepted_sanitized_fields": _sequence_text(
            adapter_result.get("accepted_sanitized_fields"),
        ),
        "missing_required_fields": _unique(missing_required_fields),
        "rejected_secret_fields": _unique(rejected_secret_fields),
        "rejected_raw_payload_fields": _unique(rejected_raw_payload_fields),
        "rejected_forbidden_fields": _unique(rejected_forbidden_fields),
        "invalid_shape_blockers": _unique(invalid_shape_blockers),
        "normalized_adapter_input": (
            dict(normalized_adapter_input) if normalized_adapter_input else {}
        ),
        "blockers": _unique(blockers),
        "next_action": next_action,
    }


def _rejected_result(
    *,
    normalizer_status: str,
    adapter_status: str,
    broker_evidence_status: str,
    broker_read_mode: str,
    blockers: Sequence[str],
    next_action: str,
    source: Mapping[str, Any] | None = None,
    rejected_secret_fields: Sequence[str] = (),
    rejected_raw_payload_fields: Sequence[str] = (),
    rejected_forbidden_fields: Sequence[str] = (),
    invalid_shape_blockers: Sequence[str] = (),
) -> dict[str, Any]:
    adapter_result = {
        "adapter_status": adapter_status,
        "sanitized_broker_telemetry_ready": False,
        "broker_read_mode": broker_read_mode,
        "broker_evidence_status": broker_evidence_status,
        "accepted_sanitized_fields": [],
    }
    return _normalizer_result(
        normalizer_status=normalizer_status,
        adapter_result=adapter_result,
        normalized_adapter_input=None,
        normalized_adapter_input_ready=False,
        normalized_sanitized_evidence_persisted=False,
        broker_read_performed=_broker_read_performed(source),
        broker_network_call_performed=_broker_network_call_performed(source),
        rejected_secret_fields=rejected_secret_fields,
        rejected_raw_payload_fields=rejected_raw_payload_fields,
        rejected_forbidden_fields=rejected_forbidden_fields,
        invalid_shape_blockers=invalid_shape_blockers,
        missing_required_fields=[],
        blockers=blockers,
        next_action=next_action,
    )


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
    return None


def _normalize_field_value(field: str, value: Any) -> Any:
    if _missingish(value):
        return None
    if field in BOOL_FIELDS:
        return value if isinstance(value, bool) else None
    if field in INT_FIELDS:
        return _coerce_int(value)
    if field in STRING_FIELDS:
        if isinstance(value, bool):
            return None
        if isinstance(value, (str, int, float)):
            return str(value).strip()
    return None


def _missing_required_fields(normalized: Mapping[str, Any]) -> list[str]:
    missing: list[str] = []
    for field in ACCEPTED_REQUIRED_FIELDS:
        if field not in normalized or normalized.get(field) is None:
            missing.append(f"{field}_required")
    return missing


def _can_mark_normalized_ready(normalized: Mapping[str, Any]) -> bool:
    required_without_status = [
        field for field in ACCEPTED_REQUIRED_FIELDS if field != "broker_evidence_status"
    ]
    return all(field in normalized and normalized.get(field) is not None for field in required_without_status)


def _unsafe_audit_flag_paths(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    violations: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = path + (key_text,)
            if key_text in SAFE_TRUE_AUDIT_FIELDS and child is not True:
                violations.append(_safe_path(child_path))
                continue
            if key_text in SAFE_FALSE_AUDIT_FIELDS and child is not False:
                violations.append(_safe_path(child_path))
                continue
            if key_text in SAFE_TRUE_CONTROL_FIELDS and child is not True:
                violations.append(_safe_path(child_path))
                continue
            if key_text in SAFE_FALSE_CONTROL_FIELDS and child is not False:
                violations.append(_safe_path(child_path))
                continue
            if key_text == "profit_reserve_bucket_mode" and child != INTERNAL_LEDGER_ONLY:
                violations.append(_safe_path(child_path))
                continue
            violations.extend(_unsafe_audit_flag_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            violations.extend(_unsafe_audit_flag_paths(child, path + (str(index),)))
    return _unique(violations)


def _secret_field_paths(value: Any, path: tuple[str, ...] = ()) -> list[str]:
    rejected: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = path + (key_text,)
            if key_text in SAFE_AUDIT_FIELDS or key_text in SAFE_CONTROL_FIELDS:
                continue
            if key_text == "profit_reserve_bucket_mode":
                continue
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
            if key_text in SAFE_AUDIT_FIELDS or key_text in SAFE_CONTROL_FIELDS:
                continue
            if _raw_payload_key(key_text):
                rejected.append(_safe_path(child_path))
                continue
            rejected.extend(_raw_payload_field_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rejected.extend(_raw_payload_field_paths(child, path + (str(index),)))
    return _unique(rejected)


def _fake_mock_dashboard_field_paths(
    value: Any,
    path: tuple[str, ...] = (),
) -> list[str]:
    rejected: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = path + (key_text,)
            if key_text in SAFE_CONTROL_FIELDS:
                continue
            if _fake_mock_dashboard_key(key_text):
                rejected.append(_safe_path(child_path))
                continue
            rejected.extend(_fake_mock_dashboard_field_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rejected.extend(
                _fake_mock_dashboard_field_paths(child, path + (str(index),)),
            )
    return _unique(rejected)


def _secret_key(key: str) -> bool:
    key_norm = _normalized_key(key)
    forbidden = {_normalized_key(name) for name in FORBIDDEN_SECRET_FIELD_NAMES}
    return key_norm in forbidden or any(term in key_norm for term in forbidden)


def _raw_payload_key(key: str) -> bool:
    key_norm = _normalized_key(key)
    forbidden = {_normalized_key(name) for name in FORBIDDEN_RAW_PAYLOAD_FIELD_NAMES}
    return key_norm in forbidden or any(term in key_norm for term in forbidden)


def _fake_mock_dashboard_key(key: str) -> bool:
    key_norm = _normalized_key(key)
    if key_norm in {_normalized_key(name) for name in FAKE_MOCK_DASHBOARD_FIELD_NAMES}:
        return True
    has_fake_or_mock = "fake" in key_norm or "mock" in key_norm
    has_dashboard_or_account = "dashboard" in key_norm or "account" in key_norm
    has_number_or_balance = "number" in key_norm or "balance" in key_norm
    return has_fake_or_mock and has_dashboard_or_account and has_number_or_balance


def _broker_read_performed(value: Any) -> bool:
    return _bool_field_from_evidence(value, "broker_read_performed")


def _broker_network_call_performed(value: Any) -> bool:
    return _bool_field_from_evidence(value, "broker_network_call_performed")


def _bool_field_from_evidence(value: Any, field: str) -> bool:
    if not isinstance(value, Mapping):
        return False
    if value.get(field) is True:
        return True
    result = value.get("result")
    if isinstance(result, Mapping) and result.get(field) is True:
        return True
    return False


def _is_packet_09_style(evidence: Mapping[str, Any]) -> bool:
    if evidence.get("campaign_packet") == 9:
        return True
    if "exercise_status" in evidence:
        return True
    if "capture_status" in evidence and "adapter_status" in evidence:
        return True
    if isinstance(evidence.get("result"), Mapping):
        return True
    return _broker_read_performed(evidence)


def _broker_status_blocked(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    return (
        text == BROKER_EVIDENCE_BLOCKED
        or text == SANITIZED_OWNER_RUN_TELEMETRY_BROKER_BLOCKED
        or text.startswith("BLOCKED_")
        or text.startswith("BROKER_EVIDENCE_BLOCKED")
    )


def _safe_scalar_or_bool(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool)) and value is not None


def _coerce_int(value: Any) -> int | Any | None:
    if isinstance(value, bool) or _missingish(value):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else value
    if isinstance(value, str):
        text = value.strip()
        try:
            return int(text)
        except ValueError:
            try:
                as_float = float(text)
            except ValueError:
                return text
            return int(as_float) if as_float.is_integer() else text
    return None


def _missingish(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        text = value.strip().lower()
        return text in {"", "unknown", "none", "null", "n/a"}
    return False


def _field_value(
    source: Mapping[str, Any],
    field: str,
    default: Any = None,
) -> Any:
    if field in source and source.get(field) is not None:
        return source.get(field)
    return default


def _safe_text_value(value: Any, default: str) -> str:
    if value is None or isinstance(value, bool):
        return default
    text = str(value).strip()
    return text if text else default


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


def _display(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    text = str(value).strip()
    return text if text else "UNKNOWN"


def _yes_no(value: Any) -> str:
    return "yes" if value is True else "no"


def _true_false(value: Any) -> str:
    return "true" if value is True else "false"
