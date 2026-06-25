from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from automation.forex_engine.oanda_demo_sanitized_owner_run_read_only_telemetry_adapter_v1 import (
    FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE,
    INTERNAL_LEDGER_ONLY,
    OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE,
    SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED,
    SANITIZED_OWNER_RUN_TELEMETRY_MISSING,
)
from automation.forex_engine.oanda_demo_sanitized_telemetry_shape_normalizer_v1 import (
    SANITIZED_TELEMETRY_SHAPE_NORMALIZER_ACCEPTED,
    SANITIZED_TELEMETRY_SHAPE_NORMALIZER_NOT_REQUESTED,
    normalize_sanitized_owner_run_telemetry_shape,
)


PACKET_NAME = (
    "AIOS FOREX OANDA DEMO SANITIZED EVIDENCE NORMALIZER ACCEPTANCE RUN V1"
)
REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_RUN_V1_REPORT.md"
)

CAMPAIGN_PACKET = 11
TRADE_ID = 320
INSTRUMENT = "EUR_USD"
SIDE = "long"
UNITS = 1
ENTRY_PRICE = "1.13596"

SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_NOT_REQUESTED = (
    "SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_NOT_REQUESTED"
)
SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED = (
    "SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED"
)
SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_REJECTED = (
    "SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_REJECTED"
)

DEFAULT_NEXT_ACTION = (
    "SUPPLY_PACKET_09_SANITIZED_JSON_EVIDENCE_FILE_TO_ACCEPTANCE_RUNNER"
)
ACCEPTED_NEXT_ACTION = (
    "FEED_SANITIZED_TELEMETRY_TO_TRADE_320_PL_REFRESH_AND_REPEAT_PROOF_GATE"
)
REJECTED_NEXT_ACTION = (
    "FIX_SANITIZED_EVIDENCE_FILE_REQUIRED_FIELDS_WITHOUT_RAW_PAYLOAD"
)


def run_sanitized_evidence_normalizer_acceptance(
    evidence: dict | None = None,
    *,
    evidence_file_path: str | None = None,
) -> dict[str, Any]:
    normalizer_result = normalize_sanitized_owner_run_telemetry_shape(evidence)
    acceptance_status = _acceptance_status(normalizer_result)
    return _acceptance_result(
        normalizer_result,
        evidence_file_path=evidence_file_path,
        acceptance_status=acceptance_status,
        next_action=_next_action(acceptance_status, normalizer_result),
    )


def render_sanitized_evidence_normalizer_acceptance_report(
    result: Mapping[str, Any],
    *,
    branch: str = "UNKNOWN",
) -> str:
    missing_fields = _sequence_text(result.get("missing_required_fields"))
    rejected_fields = _sequence_text(result.get("rejected_forbidden_fields"))
    blockers = _sequence_text(result.get("blockers"))
    blocker_text = ", ".join(blockers) if blockers else "none"
    return "\n".join(
        [
            "# AIOS FOREX OANDA DEMO SANITIZED EVIDENCE NORMALIZER ACCEPTANCE RUN V1 REPORT",
            "",
            f"- packet_name: {PACKET_NAME}",
            "- issue_1085_anchor: Packet 11 sanitized evidence normalizer acceptance run",
            "- pr_1084_anchor: OANDA demo sanitized telemetry shape normalizer",
            f"- repo_branch: {branch}",
            f"- evidence_file_path_supplied: {_display(result.get('evidence_file_path'))}",
            f"- acceptance_status: {_display(result.get('acceptance_status'))}",
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
            f"- next_action: {_display(result.get('next_action'))}",
            f"- blockers: {blocker_text}",
            "",
            "## Acceptance Evidence",
            "",
            f"- sanitized_evidence_accepted: {_yes_no(result.get('sanitized_evidence_accepted'))}",
            (
                "- normalized_sanitized_evidence_persisted: "
                f"{_true_false(result.get('normalized_sanitized_evidence_persisted'))}"
            ),
            "- raw owner evidence payload persisted: false",
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
            "",
        ]
    )


def write_sanitized_evidence_normalizer_acceptance_report(
    result: Mapping[str, Any],
    report_path: str | Path = REPORT_PATH,
    *,
    branch: str = "UNKNOWN",
) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_sanitized_evidence_normalizer_acceptance_report(
            result,
            branch=branch,
        ),
        encoding="utf-8",
    )
    return path


def _acceptance_status(normalizer_result: Mapping[str, Any]) -> str:
    if normalizer_result.get("normalizer_status") == (
        SANITIZED_TELEMETRY_SHAPE_NORMALIZER_NOT_REQUESTED
    ):
        return SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_NOT_REQUESTED
    if (
        normalizer_result.get("normalizer_status")
        == SANITIZED_TELEMETRY_SHAPE_NORMALIZER_ACCEPTED
        and normalizer_result.get("adapter_status")
        == SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED
        and normalizer_result.get("sanitized_broker_telemetry_ready") is True
        and normalizer_result.get("normalized_adapter_input_ready") is True
    ):
        return SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED
    return SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_REJECTED


def _next_action(
    acceptance_status: str,
    normalizer_result: Mapping[str, Any],
) -> str:
    if acceptance_status == SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED:
        return ACCEPTED_NEXT_ACTION
    if acceptance_status == SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_NOT_REQUESTED:
        return DEFAULT_NEXT_ACTION
    return str(normalizer_result.get("next_action") or REJECTED_NEXT_ACTION)


def _acceptance_result(
    normalizer_result: Mapping[str, Any],
    *,
    evidence_file_path: str | None,
    acceptance_status: str,
    next_action: str,
) -> dict[str, Any]:
    return {
        "packet_name": PACKET_NAME,
        "campaign_packet": CAMPAIGN_PACKET,
        "evidence_file_path": evidence_file_path or "NOT_SUPPLIED",
        "acceptance_status": acceptance_status,
        "sanitized_evidence_accepted": (
            acceptance_status == SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED
        ),
        "normalizer_status": normalizer_result.get("normalizer_status"),
        "adapter_status": normalizer_result.get(
            "adapter_status",
            SANITIZED_OWNER_RUN_TELEMETRY_MISSING,
        ),
        "sanitized_broker_telemetry_ready": (
            normalizer_result.get("sanitized_broker_telemetry_ready") is True
        ),
        "normalized_adapter_input_ready": (
            normalizer_result.get("normalized_adapter_input_ready") is True
        ),
        "broker_read_performed": (
            normalizer_result.get("broker_read_performed") is True
        ),
        "broker_network_call_performed": (
            normalizer_result.get("broker_network_call_performed") is True
        ),
        "dashboard_real_broker_telemetry_goal": True,
        "dashboard_fake_numbers_allowed": False,
        "dashboard_mock_numbers_allowed": False,
        "broker_data_source_required": OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE,
        "bank_data_source_required": FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE,
        "trade_id": _field_value(normalizer_result, "trade_id", TRADE_ID),
        "instrument": _field_value(normalizer_result, "instrument", INSTRUMENT),
        "side": _field_value(normalizer_result, "side", SIDE),
        "units": _field_value(normalizer_result, "units", UNITS),
        "entry_price": _field_value(normalizer_result, "entry_price", ENTRY_PRICE),
        "realized_pl": _field_value(normalizer_result, "realized_pl"),
        "unrealized_pl": _field_value(normalizer_result, "unrealized_pl"),
        "open_trade_count": _field_value(normalizer_result, "open_trade_count"),
        "open_position_count": _field_value(
            normalizer_result,
            "open_position_count",
        ),
        "monitor_bucket": _field_value(normalizer_result, "monitor_bucket"),
        "result_bucket": _field_value(normalizer_result, "result_bucket"),
        "repeat_proof_lane_status": _field_value(
            normalizer_result,
            "repeat_proof_lane_status",
        ),
        "repeat_proof_eligible": _field_value(
            normalizer_result,
            "repeat_proof_eligible",
            False,
        ),
        "profit_evidence": _field_value(
            normalizer_result,
            "profit_evidence",
            False,
        ),
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
            normalizer_result.get("normalized_sanitized_evidence_persisted") is True
        ),
        "missing_required_fields": _sequence_text(
            normalizer_result.get("missing_required_fields"),
        ),
        "rejected_forbidden_fields": _sequence_text(
            normalizer_result.get("rejected_forbidden_fields"),
        ),
        "blockers": _sequence_text(normalizer_result.get("blockers")),
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


def _sequence_text(value: Any) -> list[str]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [str(item) for item in value]
    if value:
        return [str(value)]
    return []


def _display(value: Any) -> str:
    if value is None:
        return "UNKNOWN"
    text = str(value).strip()
    return text if text else "UNKNOWN"


def _yes_no(value: Any) -> str:
    return "yes" if value is True else "no"


def _true_false(value: Any) -> str:
    return "true" if value is True else "false"
