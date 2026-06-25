from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from automation.forex_engine.oanda_demo_owner_run_sanitized_telemetry_capture_attempt_v1 import (
    OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_ACCEPTED,
    OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_BROKER_BLOCKED,
    OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_HELPER_MISSING,
    OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_INVALID_SHAPE,
    OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_NOT_REQUESTED,
    OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_RAW_PAYLOAD,
    OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_SECRET_RISK,
    run_owner_sanitized_telemetry_capture_attempt,
)
from automation.forex_engine.oanda_demo_sanitized_owner_run_read_only_telemetry_adapter_v1 import (
    BROKER_EVIDENCE_BLOCKED,
    FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE,
    INTERNAL_LEDGER_ONLY,
    NOT_REQUESTED,
    OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE,
    SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED,
    SANITIZED_OWNER_RUN_TELEMETRY_BROKER_BLOCKED,
    SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE,
    SANITIZED_OWNER_RUN_TELEMETRY_MISSING,
    SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_RAW_PAYLOAD,
    SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_SECRET_RISK,
)


PACKET_NAME = (
    "AIOS FOREX OANDA DEMO OWNER RUN SANITIZED TELEMETRY EXERCISE V1"
)
REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_V1_REPORT.md"
)

CAMPAIGN_PACKET = 9
TRADE_ID = 320
INSTRUMENT = "EUR_USD"
SIDE = "long"
UNITS = 1
ENTRY_PRICE = "1.13596"

OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_NOT_REQUESTED = (
    "OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_NOT_REQUESTED"
)
OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_ACCEPTED = (
    "OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_ACCEPTED"
)
OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_BROKER_BLOCKED = (
    "OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_BROKER_BLOCKED"
)
OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_HELPER_MISSING = (
    "OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_HELPER_MISSING"
)
OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_REJECTED_SECRET_RISK = (
    "OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_REJECTED_SECRET_RISK"
)
OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_REJECTED_RAW_PAYLOAD = (
    "OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_REJECTED_RAW_PAYLOAD"
)
OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_INVALID_SHAPE = (
    "OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_INVALID_SHAPE"
)

DEFAULT_NEXT_ACTION = "RUN_OWNER_SANITIZED_TELEMETRY_EXERCISE_WITH_OWNER_READ_FLAG"
ACCEPTED_NEXT_ACTION = (
    "FEED_SANITIZED_TELEMETRY_TO_TRADE_320_PL_REFRESH_AND_REPEAT_PROOF_GATE"
)
BROKER_BLOCKED_NEXT_ACTION = "REPAIR_OWNER_READ_ONLY_HELPER_OR_RUNTIME_AUTH_BOUNDARY"
HELPER_MISSING_NEXT_ACTION = "RESTORE_OR_REGISTER_OWNER_RUN_READ_ONLY_HELPER"
SECRET_NEXT_ACTION = "STOP_REMOVE_SECRET_FIELDS_AND_RETRY_SANITIZED_OUTPUT"
RAW_PAYLOAD_NEXT_ACTION = "STOP_REMOVE_RAW_PAYLOAD_AND_RETRY_SANITIZED_OUTPUT"
INVALID_NEXT_ACTION = "FIX_SANITIZED_OWNER_RUN_TELEMETRY_SHAPE"

SAFE_TRUE_STATUS_FIELDS = {
    "no_secrets_written",
    "no_broker_state_modified",
    "no_new_order_placed",
    "no_live_trade_placed",
}
SAFE_FALSE_STATUS_FIELDS = {
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
    "broker_state_modified",
}
SECRET_RISK_STATUS_FIELDS = {
    "no_secrets_written",
    "secrets_written",
    "credential_read_performed",
    "account_id_read_performed",
}
RAW_PAYLOAD_STATUS_FIELDS = {
    "raw_broker_payload_persisted",
}
SAFE_STATUS_FIELD_NAMES = SAFE_TRUE_STATUS_FIELDS | SAFE_FALSE_STATUS_FIELDS
SAFE_STATUS_FALSE_POSITIVE_BLOCKERS = {
    "forbidden_secret_field_result_no_secrets_written",
    "forbidden_secret_field_no_secrets_written",
    "forbidden_secret_field_result_secrets_written",
    "forbidden_secret_field_secrets_written",
    "forbidden_secret_field_result_account_id_read_performed",
    "forbidden_secret_field_account_id_read_performed",
    "forbidden_secret_field_result_credential_read_performed",
    "forbidden_secret_field_credential_read_performed",
    "forbidden_raw_payload_field_result_raw_broker_payload_persisted",
    "forbidden_raw_payload_field_raw_broker_payload_persisted",
}
REQUIRED_ACCEPTED_TELEMETRY_FIELDS = {
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
}


def run_owner_run_sanitized_telemetry_exercise(
    *,
    owner_run_read_broker_now: bool = False,
    evidence: dict | None = None,
) -> dict[str, Any]:
    if owner_run_read_broker_now is not True:
        capture_result = run_owner_sanitized_telemetry_capture_attempt()
        return _exercise_result(
            capture_result,
            exercise_status=OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_NOT_REQUESTED,
            owner_run_read_broker_now=False,
            broker_read_performed=False,
            broker_network_call_performed=False,
            sanitized_evidence_persisted=False,
            blockers=["owner_run_read_broker_now_flag_required"],
            next_action=DEFAULT_NEXT_ACTION,
        )

    status_violation = _status_flag_violation(evidence)
    if status_violation is not None:
        capture_result = _status_violation_capture_result(
            evidence,
            status_violation,
        )
        exercise_status = _exercise_status_from_capture(capture_result)
        return _exercise_result(
            capture_result,
            exercise_status=exercise_status,
            owner_run_read_broker_now=True,
            broker_read_performed=False,
            broker_network_call_performed=False,
            sanitized_evidence_persisted=False,
            blockers=_sequence_text(capture_result.get("blockers")),
            next_action=_next_action(exercise_status, capture_result),
        )

    capture_result = run_owner_sanitized_telemetry_capture_attempt(
        _capture_evidence_without_safe_status_fields(evidence),
        owner_run_read_broker_now=True,
    )
    capture_result = _repair_safe_status_false_positive_capture(capture_result)
    exercise_status = _exercise_status_from_capture(capture_result)
    return _exercise_result(
        capture_result,
        exercise_status=exercise_status,
        owner_run_read_broker_now=True,
        broker_read_performed=capture_result.get("broker_read_performed") is True,
        broker_network_call_performed=(
            capture_result.get("broker_network_call_performed") is True
        ),
        sanitized_evidence_persisted=(
            exercise_status == OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_ACCEPTED
        ),
        blockers=_sequence_text(capture_result.get("blockers")),
        next_action=_next_action(exercise_status, capture_result),
    )


def classify_sanitized_telemetry_exercise(
    capture_result: dict | None,
) -> dict[str, Any]:
    if capture_result is None:
        capture_result = run_owner_sanitized_telemetry_capture_attempt()
    if not isinstance(capture_result, Mapping):
        capture_result = {
            "capture_status": OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_INVALID_SHAPE,
            "adapter_status": SANITIZED_OWNER_RUN_TELEMETRY_MISSING,
            "sanitized_broker_telemetry_ready": False,
            "blockers": ["capture_result_must_be_mapping"],
        }

    status_violation = _status_flag_violation(capture_result)
    if status_violation is not None:
        capture_result = _status_violation_capture_result(
            capture_result,
            status_violation,
        )
    else:
        capture_result = _repair_safe_status_false_positive_capture(capture_result)

    exercise_status = _exercise_status_from_capture(capture_result)
    return _exercise_result(
        capture_result,
        exercise_status=exercise_status,
        owner_run_read_broker_now=capture_result.get("owner_run_read_broker_now") is True,
        broker_read_performed=capture_result.get("broker_read_performed") is True,
        broker_network_call_performed=(
            capture_result.get("broker_network_call_performed") is True
        ),
        sanitized_evidence_persisted=(
            exercise_status == OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_ACCEPTED
        ),
        blockers=_sequence_text(capture_result.get("blockers")),
        next_action=_next_action(exercise_status, capture_result),
    )


def render_owner_run_sanitized_telemetry_exercise_report(
    result: Mapping[str, Any],
    *,
    branch: str = "UNKNOWN",
) -> str:
    blockers = _sequence_text(result.get("blockers"))
    blocker_text = ", ".join(blockers) if blockers else "none"
    return "\n".join(
        [
            "# AIOS FOREX OANDA DEMO OWNER RUN SANITIZED TELEMETRY EXERCISE V1 REPORT",
            "",
            f"- packet_name: {PACKET_NAME}",
            "- pr_1081_anchor: owner-run sanitized telemetry capture attempt",
            f"- repo_branch: {branch}",
            f"- exercise_status: {_display(result.get('exercise_status'))}",
            f"- capture_status: {_display(result.get('capture_status'))}",
            f"- adapter_status: {_display(result.get('adapter_status'))}",
            (
                "- sanitized_broker_telemetry_ready: "
                f"{_yes_no(result.get('sanitized_broker_telemetry_ready'))}"
            ),
            f"- broker_read_performed: {_yes_no(result.get('broker_read_performed'))}",
            (
                "- broker_network_call_performed: "
                f"{_yes_no(result.get('broker_network_call_performed'))}"
            ),
            (
                "- sanitized_evidence_persisted: "
                f"{_yes_no(result.get('sanitized_evidence_persisted'))}"
            ),
            f"- broker_evidence_status: {_display(result.get('broker_evidence_status'))}",
            f"- next_action: {_display(result.get('next_action'))}",
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
                "- sanitized_evidence_persisted: "
                f"{_true_false(result.get('sanitized_evidence_persisted'))}"
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


def write_owner_run_sanitized_telemetry_exercise_report(
    result: Mapping[str, Any],
    report_path: str | Path = REPORT_PATH,
    *,
    branch: str = "UNKNOWN",
) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_owner_run_sanitized_telemetry_exercise_report(
            result,
            branch=branch,
        ),
        encoding="utf-8",
    )
    return path


def _exercise_result(
    capture_result: Mapping[str, Any],
    *,
    exercise_status: str,
    owner_run_read_broker_now: bool,
    broker_read_performed: bool,
    broker_network_call_performed: bool,
    sanitized_evidence_persisted: bool,
    blockers: Sequence[str],
    next_action: str,
) -> dict[str, Any]:
    source = capture_result if isinstance(capture_result, Mapping) else {}
    return {
        "packet_name": PACKET_NAME,
        "campaign_packet": CAMPAIGN_PACKET,
        "exercise_status": exercise_status,
        "capture_status": _field_value(
            source,
            "capture_status",
            OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_NOT_REQUESTED,
        ),
        "adapter_status": _field_value(
            source,
            "adapter_status",
            SANITIZED_OWNER_RUN_TELEMETRY_MISSING,
        ),
        "sanitized_broker_telemetry_ready": (
            source.get("sanitized_broker_telemetry_ready") is True
        ),
        "owner_run_read_broker_now": owner_run_read_broker_now,
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
        "repeat_proof_eligible": source.get("repeat_proof_eligible") is True,
        "profit_evidence": source.get("profit_evidence") is True,
        "withdrawal_allowed_now": False,
        "transfer_allowed_now": False,
        "money_movement_allowed_now": False,
        "profit_reserve_bucket_mode": INTERNAL_LEDGER_ONLY,
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
        "raw_broker_payload_persisted": False,
        "sanitized_evidence_persisted": sanitized_evidence_persisted,
        "blockers": _unique(blockers),
        "next_action": next_action,
    }


def _exercise_status_from_capture(capture_result: Mapping[str, Any]) -> str:
    capture_status = str(capture_result.get("capture_status", "")).strip()
    adapter_status = str(capture_result.get("adapter_status", "")).strip()
    ready = capture_result.get("sanitized_broker_telemetry_ready") is True
    if (
        capture_status == OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_ACCEPTED
        and adapter_status == SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED
        and ready
    ):
        return OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_ACCEPTED
    return {
        OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_NOT_REQUESTED: (
            OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_NOT_REQUESTED
        ),
        OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_BROKER_BLOCKED: (
            OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_BROKER_BLOCKED
        ),
        OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_HELPER_MISSING: (
            OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_HELPER_MISSING
        ),
        OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_SECRET_RISK: (
            OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_REJECTED_SECRET_RISK
        ),
        OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_RAW_PAYLOAD: (
            OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_REJECTED_RAW_PAYLOAD
        ),
        OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_INVALID_SHAPE: (
            OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_INVALID_SHAPE
        ),
    }.get(capture_status, OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_INVALID_SHAPE)


def _next_action(exercise_status: str, capture_result: Mapping[str, Any]) -> str:
    if exercise_status == OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_ACCEPTED:
        return ACCEPTED_NEXT_ACTION
    if exercise_status == OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_NOT_REQUESTED:
        return DEFAULT_NEXT_ACTION
    if exercise_status == OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_BROKER_BLOCKED:
        return BROKER_BLOCKED_NEXT_ACTION
    if exercise_status == OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_HELPER_MISSING:
        return HELPER_MISSING_NEXT_ACTION
    if exercise_status == OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_REJECTED_SECRET_RISK:
        return SECRET_NEXT_ACTION
    if exercise_status == OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_REJECTED_RAW_PAYLOAD:
        return RAW_PAYLOAD_NEXT_ACTION
    return str(capture_result.get("next_action") or INVALID_NEXT_ACTION)


def _capture_evidence_without_safe_status_fields(
    evidence: dict | None,
) -> dict | None:
    if evidence is None:
        return None
    if not isinstance(evidence, Mapping):
        return evidence
    return _drop_safe_status_fields(evidence)


def _drop_safe_status_fields(value: Any) -> Any:
    if isinstance(value, Mapping):
        cleaned: dict[str, Any] = {}
        for key, child in value.items():
            key_text = str(key)
            if key_text in SAFE_STATUS_FIELD_NAMES and _safe_status_value(
                key_text,
                child,
            ):
                continue
            cleaned[key] = _drop_safe_status_fields(child)
        return cleaned
    if isinstance(value, list):
        return [_drop_safe_status_fields(item) for item in value]
    return value


def _status_flag_violation(value: Any) -> dict[str, str] | None:
    violations = _status_flag_violations(value)
    return violations[0] if violations else None


def _status_flag_violations(
    value: Any,
    path: tuple[str, ...] = (),
) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = path + (key_text,)
            if key_text in SAFE_STATUS_FIELD_NAMES:
                if not _safe_status_value(key_text, child):
                    violations.append(
                        {
                            "field": key_text,
                            "path": _safe_path(child_path),
                            "kind": _status_rejection_kind(key_text),
                        }
                    )
                continue
            violations.extend(_status_flag_violations(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            violations.extend(
                _status_flag_violations(child, path + (str(index),))
            )
    return violations


def _safe_status_value(field: str, value: Any) -> bool:
    if field in SAFE_TRUE_STATUS_FIELDS:
        return value is True
    if field in SAFE_FALSE_STATUS_FIELDS:
        return value is False
    return False


def _status_rejection_kind(field: str) -> str:
    if field in RAW_PAYLOAD_STATUS_FIELDS:
        return "raw_payload"
    if field in SECRET_RISK_STATUS_FIELDS:
        return "secret_risk"
    return "invalid_shape"


def _status_violation_capture_result(
    source: Any,
    violation: Mapping[str, str],
) -> dict[str, Any]:
    if isinstance(source, Mapping):
        capture_result = dict(source)
    else:
        capture_result = {}

    kind = violation.get("kind")
    if kind == "raw_payload":
        capture_status = OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_RAW_PAYLOAD
        adapter_status = SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_RAW_PAYLOAD
        next_action = RAW_PAYLOAD_NEXT_ACTION
        blocker_prefix = "unsafe_raw_payload_status_field"
    elif kind == "secret_risk":
        capture_status = OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_SECRET_RISK
        adapter_status = SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_SECRET_RISK
        next_action = SECRET_NEXT_ACTION
        blocker_prefix = "unsafe_secret_status_field"
    else:
        capture_status = OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_INVALID_SHAPE
        adapter_status = SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE
        next_action = INVALID_NEXT_ACTION
        blocker_prefix = "unsafe_status_field"

    capture_result.update(
        {
            "capture_status": capture_status,
            "adapter_status": adapter_status,
            "sanitized_broker_telemetry_ready": False,
            "raw_broker_payload_persisted": False,
            "next_action": next_action,
        }
    )
    capture_result["blockers"] = _unique(
        _sequence_text(capture_result.get("blockers"))
        + [f"{blocker_prefix}_{violation.get('path') or 'unknown'}"]
    )
    return capture_result


def _repair_safe_status_false_positive_capture(
    capture_result: Any,
) -> Any:
    if not isinstance(capture_result, Mapping):
        return capture_result
    capture_status = str(capture_result.get("capture_status", "")).strip()
    if capture_status not in {
        OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_SECRET_RISK,
        OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_RAW_PAYLOAD,
    }:
        return capture_result

    blockers = _sequence_text(capture_result.get("blockers"))
    false_positive_blockers = [
        blocker for blocker in blockers if blocker in SAFE_STATUS_FALSE_POSITIVE_BLOCKERS
    ]
    if not false_positive_blockers:
        return capture_result
    remaining_blockers = [
        blocker for blocker in blockers if blocker not in SAFE_STATUS_FALSE_POSITIVE_BLOCKERS
    ]
    if remaining_blockers:
        return capture_result

    repaired = dict(capture_result)
    repaired["blockers"] = []
    if _has_required_accepted_telemetry(repaired):
        repaired.update(
            {
                "capture_status": OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_ACCEPTED,
                "adapter_status": SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED,
                "sanitized_broker_telemetry_ready": True,
                "next_action": ACCEPTED_NEXT_ACTION,
            }
        )
    elif _broker_evidence_blocked(repaired):
        repaired.update(
            {
                "capture_status": OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_BROKER_BLOCKED,
                "adapter_status": SANITIZED_OWNER_RUN_TELEMETRY_BROKER_BLOCKED,
                "sanitized_broker_telemetry_ready": False,
                "next_action": BROKER_BLOCKED_NEXT_ACTION,
            }
        )
    else:
        repaired.update(
            {
                "capture_status": OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_INVALID_SHAPE,
                "adapter_status": SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE,
                "sanitized_broker_telemetry_ready": False,
                "next_action": INVALID_NEXT_ACTION,
            }
        )
    return repaired


def _has_required_accepted_telemetry(capture_result: Mapping[str, Any]) -> bool:
    return all(
        field in capture_result and capture_result.get(field) is not None
        for field in REQUIRED_ACCEPTED_TELEMETRY_FIELDS
    )


def _broker_evidence_blocked(capture_result: Mapping[str, Any]) -> bool:
    status = str(capture_result.get("broker_evidence_status", "")).strip()
    return status == BROKER_EVIDENCE_BLOCKED or status.startswith("BLOCKED_")


def _field_value(
    source: Mapping[str, Any],
    field: str,
    default: Any = None,
) -> Any:
    if field in source and source.get(field) is not None:
        return source.get(field)
    return default


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
