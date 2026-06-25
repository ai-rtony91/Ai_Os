from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from contextlib import redirect_stdout
from io import StringIO
import inspect
from pathlib import Path
from typing import Any

from automation.forex_engine.oanda_demo_owner_read_required_sanitized_fields_capture_v1 import (
    OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_READY,
    capture_required_sanitized_fields_from_owner_read,
)
from automation.forex_engine.oanda_demo_sanitized_owner_run_read_only_telemetry_adapter_v1 import (
    ALLOWED_SANITIZED_FIELDS,
    INTERNAL_LEDGER_ONLY,
)


PACKET_NAME = (
    "AIOS FOREX OANDA DEMO OWNER RUN SANITIZED BROKER READ OUTPUT GENERATOR V1"
)
PACKET_ID = (
    "AIOS-FOREX-OANDA-DEMO-PACKET-12C-OWNER-RUN-SANITIZED-BROKER-READ-OUTPUT-GENERATOR-V1"
)
REPORT_PATH = (
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_GENERATOR_V1_REPORT.md"
)
DEFAULT_JSON_PATH = (
    "Reports/forex_delivery/"
    "oanda_demo_owner_run_sanitized_broker_read_output_v1.json"
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

SAFE_INTERNAL_BROKER_EVIDENCE_STATUS = "OWNER_RUN_READ_ONLY_EVIDENCE_CLASSIFIED"
SAFE_NESTED_SOURCE_KEYS = (
    "monitor_payload",
    "monitor_result",
    "pl_payload",
    "pl_result",
    "owner_read_result",
)

FIELD_ALIASES = {
    "trade_id": ("trade_id", "tradeID", "tradeId", "expected_trade_id", "id"),
    "instrument": ("instrument", "pair"),
    "side": ("side", "direction"),
    "units": ("units", "currentUnits", "current_units", "signed_units"),
    "entry_price": ("entry_price", "entry", "price", "open_price", "openTradePrice"),
    "realized_pl": (
        "realized_pl",
        "realizedPL",
        "realized_profit_loss",
        "pl",
        "profitLoss",
    ),
    "unrealized_pl": (
        "unrealized_pl",
        "unrealizedPL",
        "unrealized_profit_loss",
        "trueUnrealizedPL",
    ),
    "open_trade_count": ("open_trade_count", "openTradeCount"),
    "open_position_count": ("open_position_count", "openPositionCount"),
    "monitor_bucket": (
        "monitor_bucket",
        "current_bucket_result",
        "status_bucket",
        "pl_result_bucket",
    ),
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
        "broker_read_timestamp_utc",
        "read_timestamp_utc",
        "owner_read_timestamp_utc",
        "capture_timestamp_utc",
        "pl_capture_timestamp_utc",
        "timestamp",
        "time",
        "lastTransactionTime",
        "last_transaction_time",
    ),
    "evidence_source": ("evidence_source", "source"),
}

OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_NOT_REQUESTED = (
    "OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_NOT_REQUESTED"
)
OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_READY = (
    "OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_READY"
)
OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_WRITTEN = (
    "OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_WRITTEN"
)
OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_MISSING_FIELDS = (
    "OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_MISSING_FIELDS"
)
OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_SECRET_RISK = (
    "OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_SECRET_RISK"
)
OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_RAW_PAYLOAD_RISK = (
    "OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_RAW_PAYLOAD_RISK"
)
OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_UNSAFE_AUDIT_FLAG = (
    "OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_UNSAFE_AUDIT_FLAG"
)
OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_NO_SAFE_OWNER_READ_HELPER = (
    "OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_NO_SAFE_OWNER_READ_HELPER"
)
OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_READY_FOR_OWNER_RUN = (
    "OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_READY_FOR_OWNER_RUN"
)
OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_HELPER_IMPORT_FAILED = (
    "OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_HELPER_IMPORT_FAILED"
)
OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_HELPER_NOT_PROVEN_SAFE = (
    "OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_HELPER_NOT_PROVEN_SAFE"
)
OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_HELPER_RETURNED_UNSAFE_SHAPE = (
    "OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_HELPER_RETURNED_UNSAFE_SHAPE"
)

SAFE_OWNER_READ_HELPER_NOT_BOUND = "SAFE_OWNER_READ_HELPER_NOT_BOUND"
SAFE_OWNER_READ_HELPER_BOUND = "SAFE_OWNER_READ_HELPER_BOUND"
SAFE_OWNER_READ_HELPER_IMPORT_FAILED = "SAFE_OWNER_READ_HELPER_IMPORT_FAILED"
SAFE_OWNER_READ_HELPER_NOT_PROVEN_SAFE = "SAFE_OWNER_READ_HELPER_NOT_PROVEN_SAFE"
SAFE_OWNER_READ_HELPER_RETURNED_UNSAFE_SHAPE = (
    "SAFE_OWNER_READ_HELPER_RETURNED_UNSAFE_SHAPE"
)
SAFE_OWNER_READ_HELPER_NAME = (
    "scripts.run_oanda_demo_open_trade_monitor_v1.main + "
    "automation.forex_engine.oanda_demo_trade_320_read_only_pl_refresh_v1."
    "refresh_trade_320_pl_result"
)

DEFAULT_NEXT_ACTION = (
    "OWNER_MAY_RUN_WITH_OWNER_RUN_READ_BROKER_NOW_AFTER_SAFE_HELPER_BOUND"
)
OWNER_RUN_READY_NEXT_ACTION = "OWNER_RUN_READ_ONLY_SANITIZED_BROKER_OUTPUT_COMMAND"
READY_NEXT_ACTION = "RUN_PACKET_12B_CAPTURE_WRAPPER_WITH_SANITIZED_OUTPUT"
MISSING_NEXT_ACTION = "OWNER_READ_HELPER_MUST_CAPTURE_REQUIRED_FIELDS_WITHOUT_RAW_PAYLOAD"
SECRET_NEXT_ACTION = "STOP_REMOVE_SECRET_MARKERS_AND_RETRY"
RAW_NEXT_ACTION = "STOP_REMOVE_RAW_PAYLOAD_MARKERS_AND_RETRY"
UNSAFE_AUDIT_NEXT_ACTION = "STOP_FIX_UNSAFE_AUDIT_FLAGS_AND_RETRY"
NO_HELPER_NEXT_ACTION = "OWNER_READ_HELPER_INTEGRATION_NOT_PROVEN_SAFE"
HELPER_IMPORT_NEXT_ACTION = "RESTORE_SAFE_OWNER_READ_HELPER_IMPORT"
HELPER_NOT_PROVEN_NEXT_ACTION = "STOP_REVIEW_OWNER_READ_HELPER_SAFETY_PROOF"
HELPER_UNSAFE_SHAPE_NEXT_ACTION = (
    "STOP_FIX_OWNER_READ_HELPER_SANITIZED_RETURN_SHAPE"
)

OWNER_SIDE_PACKET_12C_COMMAND = (
    "python scripts/forex_delivery/"
    "run_oanda_demo_owner_run_sanitized_broker_read_output_generator_v1.py "
    "--owner-run-read-broker-now --write-json --json-path "
    "Reports/forex_delivery/oanda_demo_owner_run_sanitized_broker_read_output_v1.json "
    "--write-report --report-path "
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_GENERATOR_V1_REPORT.md "
    "--json"
)
OWNER_SIDE_PACKET_12B_COMMAND = (
    "python scripts/forex_delivery/"
    "run_oanda_demo_owner_read_required_sanitized_fields_capture_v1.py "
    "--sanitized-input-file "
    "Reports/forex_delivery/oanda_demo_owner_run_sanitized_broker_read_output_v1.json "
    "--write-json --json-path "
    "Reports/forex_delivery/oanda_demo_packet09_sanitized_owner_run_telemetry_evidence_v1.json "
    "--write-report --report-path "
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_V1_REPORT.md "
    "--json"
)
OWNER_SIDE_PACKET_11_COMMAND = (
    "python scripts/forex_delivery/"
    "run_oanda_demo_sanitized_evidence_normalizer_acceptance_run_v1.py "
    "--evidence-file "
    "Reports/forex_delivery/oanda_demo_packet09_sanitized_owner_run_telemetry_evidence_v1.json "
    "--write-report --report-path "
    "Reports/forex_delivery/"
    "AIOS_FOREX_OANDA_DEMO_SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_RUN_V1_REPORT.md "
    "--json"
)


def generate_owner_run_sanitized_broker_read_output(
    owner_run_read_broker_now: bool = False,
    write_json: bool = False,
    json_path: str | None = None,
    owner_read_result: dict | None = None,
    owner_read_helper: Callable[[], dict[str, Any]] | None = None,
    owner_read_helper_name: str | None = None,
    owner_read_helper_proven_safe: bool | None = None,
) -> dict[str, Any]:
    output_path = json_path or DEFAULT_JSON_PATH
    helper_binding = _safe_owner_read_helper_binding(
        owner_read_helper=owner_read_helper,
        owner_read_helper_name=owner_read_helper_name,
        owner_read_helper_proven_safe=owner_read_helper_proven_safe,
    )
    if owner_read_result is None:
        if owner_run_read_broker_now:
            if helper_binding.get("safe_owner_read_helper_bound") is not True:
                return _result(
                    output_status=_unbound_helper_output_status(helper_binding),
                    json_written=False,
                    json_path=output_path,
                    sanitized_output_ready=False,
                    required_fields_present=False,
                    missing_required_fields=[],
                    rejected_forbidden_fields=[],
                    unsafe_audit_flags=[],
                    candidate={},
                    owner_run_read_broker_now=owner_run_read_broker_now,
                    helper_binding=helper_binding,
                    next_action=_unbound_helper_next_action(helper_binding),
                )
            try:
                owner_read_result = helper_binding["runner"]()
            except Exception as exc:  # pragma: no cover - defensive owner-run guard
                helper_binding = _unbound_safe_owner_read_helper(
                    SAFE_OWNER_READ_HELPER_RETURNED_UNSAFE_SHAPE,
                    str(helper_binding.get("safe_owner_read_helper_name") or "UNKNOWN"),
                    f"helper_execution_failed_{type(exc).__name__}",
                )
                return _result(
                    output_status=(
                        OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_HELPER_RETURNED_UNSAFE_SHAPE
                    ),
                    json_written=False,
                    json_path=output_path,
                    sanitized_output_ready=False,
                    required_fields_present=False,
                    missing_required_fields=[],
                    rejected_forbidden_fields=[],
                    unsafe_audit_flags=[],
                    candidate={},
                    owner_run_read_broker_now=owner_run_read_broker_now,
                    helper_binding=helper_binding,
                    next_action=HELPER_UNSAFE_SHAPE_NEXT_ACTION,
                )
        else:
            if helper_binding.get("safe_owner_read_helper_bound") is True:
                return _result(
                    output_status=(
                        OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_READY_FOR_OWNER_RUN
                    ),
                    json_written=False,
                    json_path=output_path,
                    sanitized_output_ready=False,
                    required_fields_present=False,
                    missing_required_fields=[],
                    rejected_forbidden_fields=[],
                    unsafe_audit_flags=[],
                    candidate={},
                    owner_run_read_broker_now=owner_run_read_broker_now,
                    helper_binding=helper_binding,
                    next_action=OWNER_RUN_READY_NEXT_ACTION,
                )
            return _result(
                output_status=OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_NOT_REQUESTED,
                json_written=False,
                json_path=output_path,
                sanitized_output_ready=False,
                required_fields_present=False,
                missing_required_fields=[],
                rejected_forbidden_fields=[],
                unsafe_audit_flags=[],
                candidate={},
                owner_run_read_broker_now=owner_run_read_broker_now,
                helper_binding=helper_binding,
                next_action=DEFAULT_NEXT_ACTION,
            )

    if not isinstance(owner_read_result, Mapping):
        return _result(
            output_status=(
                OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_HELPER_RETURNED_UNSAFE_SHAPE
                if owner_run_read_broker_now
                else OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_MISSING_FIELDS
            ),
            json_written=False,
            json_path=output_path,
            sanitized_output_ready=False,
            required_fields_present=False,
            missing_required_fields=list(REQUIRED_SANITIZED_OUTPUT_FIELDS),
            rejected_forbidden_fields=[],
            unsafe_audit_flags=[],
            candidate={},
            owner_run_read_broker_now=owner_run_read_broker_now,
            helper_binding=helper_binding,
            next_action=(
                HELPER_UNSAFE_SHAPE_NEXT_ACTION
                if owner_run_read_broker_now
                else MISSING_NEXT_ACTION
            ),
        )

    safety = _input_safety(owner_read_result)
    candidate = _normalized_output(owner_read_result)
    missing = _missing_required_fields(candidate)
    required_present = not missing
    sanitized_ready = False
    json_written = False

    if safety["secret_risk"]:
        status = OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_SECRET_RISK
        next_action = SECRET_NEXT_ACTION
    elif safety["raw_payload_risk"]:
        status = OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_RAW_PAYLOAD_RISK
        next_action = RAW_NEXT_ACTION
    elif safety["unsafe_audit_flags"]:
        status = (
            OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_UNSAFE_AUDIT_FLAG
        )
        next_action = UNSAFE_AUDIT_NEXT_ACTION
    elif not required_present:
        status = OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_MISSING_FIELDS
        next_action = MISSING_NEXT_ACTION
    else:
        payload = _export_payload(candidate)
        capture_check = capture_required_sanitized_fields_from_owner_read(payload)
        sanitized_ready = (
            capture_check.get("capture_status")
            == OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_READY
            and capture_check.get("sanitized_evidence_ready") is True
        )
        if sanitized_ready and write_json:
            _write_json_artifact(payload, output_path)
            json_written = True
            status = OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_WRITTEN
            next_action = READY_NEXT_ACTION
        elif sanitized_ready:
            status = OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_READY
            next_action = READY_NEXT_ACTION
        else:
            status = OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_MISSING_FIELDS
            missing = _capture_missing_fields(capture_check)
            required_present = False
            next_action = MISSING_NEXT_ACTION

    return _result(
        output_status=status,
        json_written=json_written,
        json_path=output_path,
        sanitized_output_ready=sanitized_ready,
        required_fields_present=required_present,
        missing_required_fields=missing,
        rejected_forbidden_fields=safety["rejected_forbidden_fields"],
        unsafe_audit_flags=safety["unsafe_audit_flags"],
        candidate=candidate,
        owner_run_read_broker_now=owner_run_read_broker_now,
        helper_binding=helper_binding,
        next_action=next_action,
    )


def run_owner_run_sanitized_broker_read_output_generator(
    owner_run_read_broker_now: bool = False,
    write_json: bool = False,
    json_path: str | None = None,
    owner_read_result: dict | None = None,
    owner_read_helper: Callable[[], dict[str, Any]] | None = None,
    owner_read_helper_name: str | None = None,
    owner_read_helper_proven_safe: bool | None = None,
) -> dict[str, Any]:
    return generate_owner_run_sanitized_broker_read_output(
        owner_run_read_broker_now=owner_run_read_broker_now,
        write_json=write_json,
        json_path=json_path,
        owner_read_result=owner_read_result,
        owner_read_helper=owner_read_helper,
        owner_read_helper_name=owner_read_helper_name,
        owner_read_helper_proven_safe=owner_read_helper_proven_safe,
    )


def render_owner_run_sanitized_broker_read_output_generator_report(
    result: Mapping[str, Any],
    *,
    branch: str = "UNKNOWN",
) -> str:
    missing = _sequence_text(result.get("missing_required_fields"))
    rejected = _sequence_text(result.get("rejected_forbidden_fields"))
    unsafe = _sequence_text(result.get("unsafe_audit_flags"))
    return "\n".join(
        [
            "# AIOS FOREX OANDA DEMO OWNER RUN SANITIZED BROKER READ OUTPUT GENERATOR V1 REPORT",
            "",
            f"- packet_name: {PACKET_NAME}",
            f"- packet_id: {PACKET_ID}",
            "- pr_1089_anchor: owner-run sanitized broker read output generator",
            "- packet_12d_update: safe owner-read helper binding",
            f"- repo_branch: {branch}",
            f"- output_status: {_display(result.get('output_status'))}",
            (
                "- safe_owner_read_helper_status: "
                f"{_display(result.get('safe_owner_read_helper_status'))}"
            ),
            (
                "- safe_owner_read_helper_name: "
                f"{_display(result.get('safe_owner_read_helper_name'))}"
            ),
            (
                "- safe_owner_read_helper_bound: "
                f"{_yes_no(result.get('safe_owner_read_helper_bound'))}"
            ),
            f"- json_written: {_yes_no(result.get('json_written'))}",
            f"- json_path: {_display(result.get('json_path'))}",
            (
                "- sanitized_output_ready: "
                f"{_yes_no(result.get('sanitized_output_ready'))}"
            ),
            (
                "- required_fields_present: "
                f"{_yes_no(result.get('required_fields_present'))}"
            ),
            (
                "- owner_run_read_broker_now: "
                f"{_yes_no(result.get('owner_run_read_broker_now'))}"
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
            "## Owner-Side Commands",
            "",
            "### Packet 12D",
            "",
            f"- {OWNER_SIDE_PACKET_12C_COMMAND}",
            "",
            "### Packet 12B",
            "",
            f"- {OWNER_SIDE_PACKET_12B_COMMAND}",
            "",
            "### Packet 11",
            "",
            f"- {OWNER_SIDE_PACKET_11_COMMAND}",
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


def write_owner_run_sanitized_broker_read_output_generator_report(
    result: Mapping[str, Any],
    report_path: str | Path = REPORT_PATH,
    *,
    branch: str = "UNKNOWN",
) -> Path:
    path = Path(report_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_owner_run_sanitized_broker_read_output_generator_report(
            result,
            branch=branch,
        ),
        encoding="utf-8",
    )
    return path


def _safe_owner_read_helper_binding(
    *,
    owner_read_helper: Callable[[], dict[str, Any]] | None,
    owner_read_helper_name: str | None,
    owner_read_helper_proven_safe: bool | None,
) -> dict[str, Any]:
    if owner_read_helper is not None:
        helper_name = owner_read_helper_name or "injected_owner_read_helper"
        if owner_read_helper_proven_safe is not True:
            return _unbound_safe_owner_read_helper(
                SAFE_OWNER_READ_HELPER_NOT_PROVEN_SAFE,
                helper_name,
                "injected_helper_not_marked_proven_safe",
            )
        if not callable(owner_read_helper):
            return _unbound_safe_owner_read_helper(
                SAFE_OWNER_READ_HELPER_NOT_PROVEN_SAFE,
                helper_name,
                "injected_helper_not_callable",
            )
        return _bound_safe_owner_read_helper(helper_name, owner_read_helper)
    return _resolve_safe_owner_read_helper()


def _resolve_safe_owner_read_helper() -> dict[str, Any]:
    helper_name = SAFE_OWNER_READ_HELPER_NAME
    try:
        from automation.forex_engine.oanda_demo_read_only_filled_trade_pl_capture_v1 import (  # noqa: E501
            LIVE_API_HOST,
            PRACTICE_API_BASE_URL,
            default_oanda_demo_read_only_filled_trade_pl_capture_context_v1,
            validate_oanda_demo_read_only_filled_trade_pl_capture_endpoint_url_v1,
        )
        from automation.forex_engine.oanda_demo_trade_320_read_only_pl_refresh_v1 import (
            refresh_trade_320_pl_result,
        )
        from scripts.forex_delivery.run_oanda_demo_read_only_filled_trade_pl_capture_v1 import (
            REQUIRED_EXECUTE_CONFIRMATIONS,
        )
        from scripts.run_oanda_demo_open_trade_monitor_v1 import (
            main as monitor_main,
        )
    except Exception as exc:  # pragma: no cover - defensive import boundary
        return _unbound_safe_owner_read_helper(
            SAFE_OWNER_READ_HELPER_IMPORT_FAILED,
            helper_name,
            f"safe_helper_import_failed_{type(exc).__name__}",
        )

    blockers = _safe_helper_proof_blockers(
        monitor_main=monitor_main,
        required_confirmations=REQUIRED_EXECUTE_CONFIRMATIONS,
        capture_context=default_oanda_demo_read_only_filled_trade_pl_capture_context_v1(),
        practice_api_base_url=PRACTICE_API_BASE_URL,
        live_api_host=LIVE_API_HOST,
        endpoint_validator=validate_oanda_demo_read_only_filled_trade_pl_capture_endpoint_url_v1,
    )
    if blockers:
        return _unbound_safe_owner_read_helper(
            SAFE_OWNER_READ_HELPER_NOT_PROVEN_SAFE,
            helper_name,
            ",".join(blockers),
        )

    def runner() -> dict[str, Any]:
        return _run_bound_open_trade_monitor_pl_refresh_helper(
            monitor_main=monitor_main,
            refresh_trade_320_pl_result=refresh_trade_320_pl_result,
        )

    return _bound_safe_owner_read_helper(helper_name, runner)


def _safe_helper_proof_blockers(
    *,
    monitor_main: Callable[..., int],
    required_confirmations: Mapping[str, str],
    capture_context: Mapping[str, Any],
    practice_api_base_url: str,
    live_api_host: str,
    endpoint_validator: Callable[..., list[str]],
) -> list[str]:
    blockers: list[str] = []
    signature = inspect.signature(monitor_main)
    if "argv" not in signature.parameters:
        blockers.append("monitor_main_must_accept_argv")

    required_flags = {
        "--i-confirm-demo-only",
        "--i-confirm-read-only-pl-capture",
        "--i-confirm-windows-vault-only",
        "--i-confirm-no-env-file",
        "--i-confirm-no-repo-persistence",
        "--i-confirm-no-live-endpoint",
        "--i-confirm-no-order",
        "--i-confirm-no-close-trade",
        "--i-confirm-no-mutation",
        "--i-confirm-no-second-order",
        "--i-confirm-no-profit-claim",
    }
    observed_flags = set(required_confirmations.values())
    missing_flags = sorted(required_flags - observed_flags)
    if missing_flags:
        blockers.extend(f"missing_confirmation_{_safe_label(flag)}" for flag in missing_flags)

    expected_true = (
        "demo_only",
        "windows_vault_only",
        "read_only_pl_capture_only",
        "no_env_file",
        "no_repo_persistence",
        "no_live_credentials",
        "no_order_placement",
        "no_order_close",
        "no_order_mutation",
        "no_trade_mutation",
        "no_position_mutation",
        "no_second_order_attempt",
    )
    for field in expected_true:
        if capture_context.get(field) is not True:
            blockers.append(f"context_{field}_required")
    if capture_context.get("broker") != "OANDA_DEMO":
        blockers.append("context_broker_must_be_oanda_demo")
    if capture_context.get("environment") != "DEMO":
        blockers.append("context_environment_must_be_demo")
    if capture_context.get("live_mode") is True:
        blockers.append("context_live_mode_must_be_false")
    if capture_context.get("live_credentials_allowed") is True:
        blockers.append("context_live_credentials_allowed_must_be_false")
    if capture_context.get("profit_claimed") is True:
        blockers.append("context_profit_claim_must_be_false")
    if live_api_host in str(capture_context.get("demo_api_base_url", "")):
        blockers.append("context_demo_api_base_url_must_not_be_live")

    practice_url = f"{practice_api_base_url}/v3/accounts"
    if endpoint_validator(practice_url, method="GET"):
        blockers.append("practice_accounts_endpoint_must_validate")
    live_url = f"https://{live_api_host}/v3/accounts"
    if not endpoint_validator(live_url, method="GET"):
        blockers.append("live_accounts_endpoint_must_be_blocked")
    return _unique(blockers)


def _run_bound_open_trade_monitor_pl_refresh_helper(
    *,
    monitor_main: Callable[..., int],
    refresh_trade_320_pl_result: Callable[[dict | None], dict[str, Any]],
) -> dict[str, Any]:
    stream = StringIO()
    with redirect_stdout(stream):
        monitor_main(
            [
                "--owner-run-read-broker-now",
                "--expected-trade-id",
                "320",
                "--json",
            ],
        )
    monitor_payload = _json_mapping(stream.getvalue())
    monitor_result = monitor_payload.get("result")
    if not isinstance(monitor_result, Mapping):
        return {
            "helper_capture_status": SAFE_OWNER_READ_HELPER_RETURNED_UNSAFE_SHAPE,
            "broker_network_call_performed": (
                monitor_payload.get("broker_network_call_performed") is True
            ),
            "broker_read_performed": False,
            "blockers": ["owner_read_monitor_result_missing"],
        }

    pl_result = refresh_trade_320_pl_result(dict(monitor_result))
    return _merged_monitor_pl_output(monitor_payload, monitor_result, pl_result)


def _merged_monitor_pl_output(
    monitor_payload: Mapping[str, Any],
    monitor_result: Mapping[str, Any],
    pl_result: Mapping[str, Any],
) -> dict[str, Any]:
    broker_network_call_performed = (
        monitor_payload.get("broker_network_call_performed") is True
    )
    return {
        "trade_id": _field_alias_value(
            pl_result,
            monitor_result,
            field="trade_id",
        ),
        "instrument": _field_alias_value(
            pl_result,
            monitor_result,
            field="instrument",
        ),
        "side": _field_alias_value(pl_result, monitor_result, field="side"),
        "units": _field_alias_value(pl_result, monitor_result, field="units"),
        "entry_price": _field_alias_value(
            pl_result,
            monitor_result,
            field="entry_price",
        ),
        "realized_pl": _field_alias_value(
            pl_result,
            monitor_result,
            field="realized_pl",
        ),
        "unrealized_pl": _field_alias_value(
            pl_result,
            monitor_result,
            field="unrealized_pl",
        ),
        "open_trade_count": _field_alias_value(
            pl_result,
            monitor_result,
            field="open_trade_count",
        ),
        "open_position_count": _field_alias_value(
            pl_result,
            monitor_result,
            field="open_position_count",
        ),
        "monitor_bucket": _field_alias_value(
            monitor_result,
            pl_result,
            field="monitor_bucket",
        ),
        "result_bucket": _field_alias_value(
            pl_result,
            monitor_result,
            field="result_bucket",
        ),
        "repeat_proof_lane_status": pl_result.get("repeat_proof_lane_status"),
        "repeat_proof_eligible": pl_result.get("repeat_proof_eligible") is True,
        "profit_evidence": pl_result.get("profit_evidence") is True,
        "broker_read_mode": pl_result.get("broker_read_mode"),
        "broker_evidence_status": _field_alias_value(
            pl_result,
            monitor_result,
            monitor_payload,
            field="broker_evidence_status",
        ),
        "evidence_timestamp_utc": _field_alias_value(
            monitor_result,
            pl_result,
            monitor_payload,
            field="evidence_timestamp_utc",
        ),
        "evidence_source": (
            monitor_result.get("evidence_source")
            or pl_result.get("source")
            or "owner_run_open_trade_monitor_pl_refresh_helper"
        ),
        "broker_network_call_performed": broker_network_call_performed,
        "broker_read_performed": broker_network_call_performed,
        "live_endpoint_used": monitor_payload.get("live_endpoint_used") is True,
        "order_placement_performed": (
            monitor_payload.get("order_placement_performed") is True
        ),
        "order_mutation_performed": (
            monitor_payload.get("order_mutation_performed") is True
        ),
        "order_close_performed": monitor_payload.get("order_close_performed") is True,
        "position_mutation_performed": (
            monitor_payload.get("position_mutation_performed") is True
        ),
        "trade_mutation_performed": (
            monitor_payload.get("trade_mutation_performed") is True
        ),
        "raw_broker_payload_persisted": False,
        "secrets_written": monitor_payload.get("secrets_written") is True,
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
    }


def _bound_safe_owner_read_helper(
    helper_name: str,
    runner: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    return {
        "safe_owner_read_helper_status": SAFE_OWNER_READ_HELPER_BOUND,
        "safe_owner_read_helper_name": helper_name,
        "safe_owner_read_helper_bound": True,
        "safe_owner_read_helper_blockers": [],
        "runner": runner,
    }


def _unbound_safe_owner_read_helper(
    status: str,
    helper_name: str,
    blocker: str,
) -> dict[str, Any]:
    return {
        "safe_owner_read_helper_status": status,
        "safe_owner_read_helper_name": helper_name,
        "safe_owner_read_helper_bound": False,
        "safe_owner_read_helper_blockers": [blocker],
    }


def _unbound_helper_output_status(helper_binding: Mapping[str, Any]) -> str:
    status = helper_binding.get("safe_owner_read_helper_status")
    if status == SAFE_OWNER_READ_HELPER_IMPORT_FAILED:
        return OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_HELPER_IMPORT_FAILED
    if status == SAFE_OWNER_READ_HELPER_NOT_PROVEN_SAFE:
        return OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_HELPER_NOT_PROVEN_SAFE
    if status == SAFE_OWNER_READ_HELPER_RETURNED_UNSAFE_SHAPE:
        return (
            OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_HELPER_RETURNED_UNSAFE_SHAPE
        )
    return OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_NO_SAFE_OWNER_READ_HELPER


def _unbound_helper_next_action(helper_binding: Mapping[str, Any]) -> str:
    status = helper_binding.get("safe_owner_read_helper_status")
    if status == SAFE_OWNER_READ_HELPER_IMPORT_FAILED:
        return HELPER_IMPORT_NEXT_ACTION
    if status == SAFE_OWNER_READ_HELPER_NOT_PROVEN_SAFE:
        return HELPER_NOT_PROVEN_NEXT_ACTION
    if status == SAFE_OWNER_READ_HELPER_RETURNED_UNSAFE_SHAPE:
        return HELPER_UNSAFE_SHAPE_NEXT_ACTION
    return NO_HELPER_NEXT_ACTION


def _json_mapping(raw: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "helper_capture_status": SAFE_OWNER_READ_HELPER_RETURNED_UNSAFE_SHAPE,
            "blockers": ["owner_read_helper_json_parse_failed"],
        }
    if isinstance(parsed, dict):
        return parsed
    return {
        "helper_capture_status": SAFE_OWNER_READ_HELPER_RETURNED_UNSAFE_SHAPE,
        "blockers": ["owner_read_helper_json_root_not_object"],
    }


def _field_value(
    source: Mapping[str, Any],
    field: str,
    default: Any = None,
) -> Any:
    if field in source and source.get(field) is not None:
        return source.get(field)
    return default


def _field_alias_value(
    *sources: Mapping[str, Any],
    field: str,
    default: Any = None,
) -> Any:
    value = _first_safe_value(
        *sources,
        keys=FIELD_ALIASES.get(field, (field,)),
    )
    return value if value is not None else default


def _normalized_output(owner_read_result: Mapping[str, Any]) -> dict[str, Any]:
    sources = _safe_source_mappings(owner_read_result)
    normalized: dict[str, Any] = {}

    for field in REQUIRED_SANITIZED_OUTPUT_FIELDS:
        value = _first_safe_value(
            *sources,
            keys=FIELD_ALIASES.get(field, (field,)),
        )
        normalized_value = _normalize_required_field(field, value)
        if normalized_value is not None:
            normalized[field] = normalized_value

    for field in SAFE_AUDIT_EXPORT_FIELDS:
        value = _first_safe_value(*sources, keys=(field,))
        if isinstance(value, bool):
            normalized[field] = value

    return _complete_deterministic_safe_fields(normalized)


def _safe_source_mappings(owner_read_result: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    sources: list[Mapping[str, Any]] = []

    def add_source(candidate: Any) -> None:
        if not isinstance(candidate, Mapping):
            return
        if any(candidate is existing for existing in sources):
            return
        sources.append(candidate)

    primary = _primary_payload(owner_read_result)
    add_source(primary)
    add_source(owner_read_result)

    for container in tuple(sources):
        for key in SAFE_NESTED_SOURCE_KEYS:
            add_source(container.get(key))

    return tuple(sources)


def _complete_deterministic_safe_fields(candidate: Mapping[str, Any]) -> dict[str, Any]:
    completed = dict(candidate)
    if _missing_value(completed.get("side")):
        side = _side_from_signed_units(completed.get("units"))
        if side is not None:
            completed["side"] = side

    if (
        _missing_value(completed.get("broker_evidence_status"))
        and completed.get("broker_read_performed") is True
        and _all_required_fields_present_except(completed, "broker_evidence_status")
    ):
        completed["broker_evidence_status"] = SAFE_INTERNAL_BROKER_EVIDENCE_STATUS

    return completed


def _side_from_signed_units(value: Any) -> str | None:
    units = _coerce_int(value)
    if units is None or units == 0:
        return None
    return "long" if units > 0 else "short"


def _all_required_fields_present_except(
    candidate: Mapping[str, Any],
    excluded_field: str,
) -> bool:
    return all(
        field == excluded_field
        or (field in candidate and not _missing_value(candidate.get(field)))
        for field in REQUIRED_SANITIZED_OUTPUT_FIELDS
    )


def _primary_payload(owner_read_result: Mapping[str, Any]) -> Mapping[str, Any]:
    result = owner_read_result.get("result")
    if isinstance(result, Mapping):
        return result
    decision = owner_read_result.get("decision")
    if isinstance(decision, Mapping):
        result = decision.get("result")
        if isinstance(result, Mapping):
            return result
        return decision
    return owner_read_result


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


def _input_safety(owner_read_result: Mapping[str, Any]) -> dict[str, Any]:
    secret_fields = _secret_field_paths(owner_read_result)
    raw_fields = _forbidden_key_paths(
        owner_read_result,
        FORBIDDEN_RAW_PAYLOAD_MARKERS,
    )
    fake_fields = _fake_or_mock_field_paths(owner_read_result)
    unsafe = _unsafe_audit_flags(owner_read_result)
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


def _capture_missing_fields(capture_check: Mapping[str, Any]) -> list[str]:
    values = _sequence_text(capture_check.get("missing_required_fields"))
    return values or ["packet12b_capture_rejected"]


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
    output_status: str,
    json_written: bool,
    json_path: str,
    sanitized_output_ready: bool,
    required_fields_present: bool,
    missing_required_fields: Sequence[str],
    rejected_forbidden_fields: Sequence[str],
    unsafe_audit_flags: Sequence[str],
    candidate: Mapping[str, Any],
    owner_run_read_broker_now: bool,
    helper_binding: Mapping[str, Any] | None,
    next_action: str,
) -> dict[str, Any]:
    binding = helper_binding or {}
    return {
        "packet_name": PACKET_NAME,
        "packet_id": PACKET_ID,
        "output_status": output_status,
        "safe_owner_read_helper_status": binding.get(
            "safe_owner_read_helper_status",
            SAFE_OWNER_READ_HELPER_NOT_BOUND,
        ),
        "safe_owner_read_helper_name": binding.get(
            "safe_owner_read_helper_name",
            "NONE",
        ),
        "safe_owner_read_helper_bound": (
            binding.get("safe_owner_read_helper_bound") is True
        ),
        "json_written": json_written,
        "json_path": json_path,
        "sanitized_output_ready": sanitized_output_ready,
        "required_fields_present": required_fields_present,
        "missing_required_fields": list(missing_required_fields),
        "rejected_forbidden_fields": list(rejected_forbidden_fields),
        "unsafe_audit_flags": list(unsafe_audit_flags),
        "owner_run_read_broker_now": owner_run_read_broker_now,
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
