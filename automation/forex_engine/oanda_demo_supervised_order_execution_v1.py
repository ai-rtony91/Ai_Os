"""Governed OANDA demo supervised order execution controller."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from math import isfinite
from typing import Any


SCHEMA = "AIOS_FOREX_OANDA_DEMO_SUPERVISED_ORDER_EXECUTION_V1"
MODE = "SUPERVISED_OANDA_DEMO_ORDER_EXECUTION_CONTROLLER"

DEMO_ORDER_EXECUTED_WITH_INJECTED_ADAPTER = "DEMO_ORDER_EXECUTED_WITH_INJECTED_ADAPTER"
READY_FOR_OWNER_SUPERVISED_DEMO_EXECUTION = "READY_FOR_OWNER_SUPERVISED_DEMO_EXECUTION"
BLOCKED_BY_MISSING_ADAPTER = "BLOCKED_BY_MISSING_ADAPTER"
BLOCKED_BY_RUNTIME_HANDOFF = "BLOCKED_BY_RUNTIME_HANDOFF"
BLOCKED_BY_OWNER_APPROVAL = "BLOCKED_BY_OWNER_APPROVAL"
BLOCKED_BY_OANDA_DEMO_BOUNDARY = "BLOCKED_BY_OANDA_DEMO_BOUNDARY"
BLOCKED_BY_ORDER_PREVIEW = "BLOCKED_BY_ORDER_PREVIEW"
BLOCKED_BY_RISK_GATES = "BLOCKED_BY_RISK_GATES"
BLOCKED_BY_ABORT_CONDITIONS = "BLOCKED_BY_ABORT_CONDITIONS"
BLOCKED_BY_TELEMETRY = "BLOCKED_BY_TELEMETRY"
BLOCKED_BY_POST_TRADE_REVIEW = "BLOCKED_BY_POST_TRADE_REVIEW"
BLOCKED_BY_ADAPTER_CONTRACT = "BLOCKED_BY_ADAPTER_CONTRACT"
BLOCKED_BY_DATA_QUALITY = "BLOCKED_BY_DATA_QUALITY"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

THIS_PACKET = SCHEMA
NEXT_PACKET_IF_READY = "AIOS_FOREX_OANDA_DEMO_BROKER_ADAPTER_RUNTIME_BINDING_V1"
NEXT_PACKET_AFTER_EXECUTION = "AIOS_FOREX_OANDA_DEMO_POST_EXECUTION_REVIEW_V1"

CORE_EVIDENCE_KEYS = (
    "runtime_handoff_package",
    "owner_approval",
    "oanda_demo_boundary",
    "order_preview",
    "risk_gates",
    "abort_conditions",
    "telemetry",
    "post_trade_review",
)

SENSITIVE_KEY_PARTS = (
    "routing_number",
    "account_number",
    "debit_card_number",
    "card_number",
    "cvv",
    "password",
    "api_key",
    "broker_token",
    "access_token",
    "token",
    "secret",
)

SAFE_BOUNDARY_KEYS = frozenset(
    {
        "bank_access_allowed",
        "broker_api_allowed",
        "credential_read_allowed",
        "credential_storage_allowed",
        "credential_use_allowed",
        "credentials_included",
        "daemon_created",
        "dashboard_runtime_created",
        "demo_execution_allowed",
        "direct_broker_api_allowed",
        "live_account_allowed",
        "live_execution_allowed",
        "live_trading_allowed",
        "money_movement_allowed",
        "order_placement_allowed",
        "real_money_allowed",
        "scheduler_created",
        "supervised_demo_execution_allowed",
        "webhook_created",
    }
)

READY_HANDOFF_STATUSES = frozenset({"OANDA_DEMO_RUNTIME_HANDOFF_READY", "READY", "PASS"})
ALLOWED_BROKER_MODES = frozenset({"DEMO", "OANDA_DEMO", "PRACTICE"})
ALLOWED_ACCOUNT_ENVIRONMENTS = frozenset({"PRACTICE", "DEMO", "OANDA_DEMO"})
ALLOWED_SIDES = frozenset({"BUY", "SELL", "LONG", "SHORT"})
ALLOWED_ORDER_TYPES = frozenset({"MARKET", "LIMIT", "PREP_ONLY"})

OWNER_ACTION_IDS = (
    "REVIEW_RUNTIME_HANDOFF",
    "REVIEW_OWNER_APPROVAL",
    "REVIEW_OANDA_DEMO_BOUNDARY",
    "REVIEW_ORDER_PREVIEW",
    "REVIEW_RISK_GATES",
    "REVIEW_ABORT_CONDITIONS",
    "REVIEW_TELEMETRY",
    "REVIEW_POST_TRADE_REVIEW",
    "REVIEW_ADAPTER_CONTRACT",
    "REVIEW_EXECUTION_RESULT",
    "REVIEW_NEXT_PACKET",
)


def execute_oanda_demo_supervised_order_v1(
    payload: dict | None = None,
    broker_adapter: object | None = None,
) -> dict:
    """Validate owner-approved demo-order evidence and call only an injected adapter."""

    source = payload if isinstance(payload, Mapping) else {}
    adapter_supplied = broker_adapter is not None
    sensitive_data_present = _contains_sensitive_key(source)
    missing_information = _missing_information(source)

    runtime_handoff_summary = _runtime_handoff_summary(source)
    owner_approval_summary = _owner_approval_summary(source)
    oanda_demo_boundary_summary = _oanda_demo_boundary_summary(source)
    order_preview_summary = _order_preview_summary(source)
    risk_gate_summary = _risk_gate_summary(source)
    abort_condition_summary = _abort_condition_summary(source)
    telemetry_summary = _telemetry_summary(source)
    post_trade_review_summary = _post_trade_review_summary(source)
    data_quality_summary = _data_quality_summary(source)
    sanitized_order_request = _sanitized_order_request(
        owner_approval_summary=owner_approval_summary,
        oanda_demo_boundary_summary=oanda_demo_boundary_summary,
        order_preview_summary=order_preview_summary,
        risk_gate_summary=risk_gate_summary,
    )
    adapter_summary = _adapter_summary(broker_adapter)

    execution_status = _resolve_execution_status(
        sensitive_data_present=sensitive_data_present,
        missing_information=missing_information,
        runtime_handoff_summary=runtime_handoff_summary,
        owner_approval_summary=owner_approval_summary,
        oanda_demo_boundary_summary=oanda_demo_boundary_summary,
        order_preview_summary=order_preview_summary,
        risk_gate_summary=risk_gate_summary,
        abort_condition_summary=abort_condition_summary,
        telemetry_summary=telemetry_summary,
        post_trade_review_summary=post_trade_review_summary,
        data_quality_summary=data_quality_summary,
        adapter_supplied=adapter_supplied,
        adapter_summary=adapter_summary,
    )

    execution_result: dict[str, Any] | None = None
    supervised_demo_execution_attempted = False
    if execution_status == DEMO_ORDER_EXECUTED_WITH_INJECTED_ADAPTER:
        adapter_method = adapter_summary["adapter_method"]
        order_request_for_adapter = _copy_for_adapter(sanitized_order_request)
        try:
            raw_result = adapter_method(order_request_for_adapter)
        except Exception as exc:  # pragma: no cover - defensive fail-closed branch.
            execution_status = BLOCKED_BY_ADAPTER_CONTRACT
            execution_result = {
                "adapter_exception_type": type(exc).__name__,
                "adapter_exception_captured": True,
            }
            adapter_summary["adapter_called"] = True
            adapter_summary["adapter_exception_captured"] = True
            adapter_summary["blockers"] = _unique(
                [*adapter_summary["blockers"], "adapter_exception_raised"]
            )
        else:
            execution_result = _sanitize_for_output(raw_result)
            adapter_summary["adapter_called"] = True
            adapter_summary["adapter_result_captured"] = isinstance(raw_result, Mapping)
        supervised_demo_execution_attempted = True

    execution_blockers = _execution_blockers(
        execution_status=execution_status,
        sensitive_data_present=sensitive_data_present,
        missing_information=missing_information,
        runtime_handoff_summary=runtime_handoff_summary,
        owner_approval_summary=owner_approval_summary,
        oanda_demo_boundary_summary=oanda_demo_boundary_summary,
        order_preview_summary=order_preview_summary,
        risk_gate_summary=risk_gate_summary,
        abort_condition_summary=abort_condition_summary,
        telemetry_summary=telemetry_summary,
        post_trade_review_summary=post_trade_review_summary,
        data_quality_summary=data_quality_summary,
        adapter_summary=adapter_summary,
    )
    supervised_demo_execution_allowed = execution_status in {
        READY_FOR_OWNER_SUPERVISED_DEMO_EXECUTION,
        DEMO_ORDER_EXECUTED_WITH_INJECTED_ADAPTER,
    }
    next_best_packet = _next_best_packet(execution_status)

    validation_summary = {
        "sensitive_data_present": sensitive_data_present,
        "missing_information": list(missing_information),
        "runtime_handoff_ready": runtime_handoff_summary["ready"],
        "owner_approval_ready": owner_approval_summary["ready"],
        "oanda_demo_boundary_ready": oanda_demo_boundary_summary["ready"],
        "order_preview_ready": order_preview_summary["ready"],
        "risk_gates_ready": risk_gate_summary["ready"],
        "abort_conditions_ready": abort_condition_summary["ready"],
        "telemetry_ready": telemetry_summary["ready"],
        "post_trade_review_ready": post_trade_review_summary["ready"],
        "data_quality_ready": data_quality_summary["ready"],
        "adapter_contract_ready": adapter_summary["contract_ready"],
        "execution_blockers": list(execution_blockers),
    }

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only_design": False,
        "direct_broker_api_allowed": False,
        "live_trading_allowed": False,
        "real_money_allowed": False,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "credential_storage_allowed": False,
        "credential_read_allowed": False,
        "scheduler_created": False,
        "daemon_created": False,
        "webhook_created": False,
        "dashboard_runtime_created": False,
        "owner_decision_required": True,
        "owner_final_approval_required": True,
        "supervised_demo_execution_attempted": supervised_demo_execution_attempted,
        "supervised_demo_execution_allowed": supervised_demo_execution_allowed,
        "live_execution_allowed": False,
        "execution_status": execution_status,
        "execution_result": execution_result,
        "sanitized_order_request": sanitized_order_request,
        "validation_summary": validation_summary,
        "runtime_handoff_summary": runtime_handoff_summary,
        "owner_approval_summary": owner_approval_summary,
        "oanda_demo_boundary_summary": oanda_demo_boundary_summary,
        "order_preview_summary": order_preview_summary,
        "risk_gate_summary": risk_gate_summary,
        "abort_condition_summary": abort_condition_summary,
        "telemetry_summary": telemetry_summary,
        "post_trade_review_summary": post_trade_review_summary,
        "adapter_summary": _public_adapter_summary(adapter_summary),
        "execution_blockers": list(execution_blockers),
        "missing_information": list(missing_information),
        "owner_action_queue": _owner_action_queue(next_best_packet, execution_blockers),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(execution_status),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "as_of_date": _text(source.get("as_of_date"), datetime.now(timezone.utc).isoformat()),
            "owner_name": _text(source.get("owner_name"), owner_approval_summary.get("owner_name") or "Anthony"),
            "input_fields_seen": sorted(str(key) for key in source.keys()),
            "input_redacted": sensitive_data_present,
            "adapter_supplied": adapter_supplied,
            "adapter_called": bool(adapter_summary["adapter_called"]),
            "execution_status": execution_status,
            "supervised_demo_execution_attempted": supervised_demo_execution_attempted,
            "supervised_demo_execution_allowed": supervised_demo_execution_allowed,
            "live_execution_allowed": False,
            "next_best_packet": next_best_packet,
        },
        "safety": _safety(),
    }


def _runtime_handoff_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contexts = _contexts(source, "runtime_handoff_package")
    handoff_status = _text_from_contexts(contexts, ("handoff_status", "runtime_handoff_status", "status"))
    runtime_handoff_ready = _bool_from_contexts(contexts, ("runtime_handoff_ready",))
    supervised_demo_execution_authorized = _bool_from_contexts(
        contexts,
        ("supervised_demo_execution_authorized",),
    )
    next_best_packet = _text_from_contexts(contexts, ("next_best_packet",))
    handoff_blockers = _blockers_from_contexts(contexts, ("handoff_blockers", "blockers"))
    blockers: list[str] = []
    if not handoff_status:
        blockers.append("handoff_status_missing")
    elif handoff_status.upper() not in READY_HANDOFF_STATUSES:
        blockers.append("handoff_status_not_ready")
    if runtime_handoff_ready is not True:
        blockers.append(
            "runtime_handoff_ready_missing" if runtime_handoff_ready is None else "runtime_handoff_ready_false"
        )
    if handoff_blockers:
        blockers.extend(handoff_blockers)
    return {
        "ready": not blockers,
        "handoff_status": handoff_status,
        "runtime_handoff_ready": runtime_handoff_ready,
        "supervised_demo_execution_authorized": (
            False if supervised_demo_execution_authorized is None else supervised_demo_execution_authorized
        ),
        "next_best_packet": next_best_packet,
        "handoff_blockers": handoff_blockers,
        "blockers": _unique(blockers),
    }


def _owner_approval_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contexts = _contexts(source, "owner_approval")
    owner_name = _text_from_contexts(contexts, ("owner_name",))
    execution_mode = _text_from_contexts(contexts, ("execution_mode",))
    expected_true = {
        "owner_final_approval_for_demo_execution": _bool_from_contexts(
            contexts,
            ("owner_final_approval_for_demo_execution",),
        ),
        "owner_accepts_order_preview": _bool_from_contexts(contexts, ("owner_accepts_order_preview",)),
        "owner_accepts_demo_only_boundary": _bool_from_contexts(
            contexts,
            ("owner_accepts_demo_only_boundary",),
        ),
        "owner_accepts_risk_limits": _bool_from_contexts(contexts, ("owner_accepts_risk_limits",)),
        "owner_accepts_one_order_only": _bool_from_contexts(contexts, ("owner_accepts_one_order_only",)),
        "owner_can_cancel": _bool_from_contexts(contexts, ("owner_can_cancel",)),
        "execution_allowed": _bool_from_contexts(contexts, ("execution_allowed",)),
    }
    expected_false = {
        "live_execution_allowed": _false_authority_value(contexts, "live_execution_allowed"),
    }
    blockers = _exact_bool_blockers(expected_true=expected_true, expected_false=expected_false)
    if owner_name and owner_name != "Anthony":
        blockers.append("owner_name_not_anthony")
    if execution_mode != "DEMO_PRACTICE":
        blockers.append("execution_mode_missing" if not execution_mode else "execution_mode_not_demo_practice")
    return {
        "ready": not blockers,
        "owner_name": owner_name,
        "execution_mode": execution_mode,
        **expected_true,
        **expected_false,
        "blockers": _unique(blockers),
    }


def _oanda_demo_boundary_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contexts = _contexts(source, "oanda_demo_boundary")
    broker_name = _text_from_contexts(contexts, ("broker_name",))
    broker_mode = _text_from_contexts(contexts, ("broker_mode",))
    account_environment = _text_from_contexts(contexts, ("account_environment",))
    expected_true = {
        "demo_account_only": _bool_from_contexts(contexts, ("demo_account_only",)),
        "order_placement_allowed": _bool_from_contexts(contexts, ("order_placement_allowed",)),
    }
    expected_false = {
        "live_account_allowed": _false_authority_value(contexts, "live_account_allowed"),
        "real_money_allowed": _false_authority_value(contexts, "real_money_allowed"),
        "money_movement_allowed": _false_authority_value(contexts, "money_movement_allowed"),
        "bank_access_allowed": _false_authority_value(contexts, "bank_access_allowed"),
        "broker_api_allowed": _false_authority_value(contexts, "broker_api_allowed"),
        "credential_use_allowed": _false_authority_value(contexts, "credential_use_allowed"),
        "live_execution_allowed": _false_authority_value(contexts, "live_execution_allowed"),
    }
    blockers = _exact_bool_blockers(expected_true=expected_true, expected_false=expected_false)
    if broker_name and broker_name.upper() != "OANDA":
        blockers.append("broker_name_not_oanda")
    if not broker_mode:
        blockers.append("broker_mode_missing")
    elif broker_mode.upper() not in ALLOWED_BROKER_MODES:
        blockers.append("broker_mode_not_demo")
    if not account_environment:
        blockers.append("account_environment_missing")
    elif account_environment.upper() not in ALLOWED_ACCOUNT_ENVIRONMENTS:
        blockers.append("account_environment_not_demo")
    return {
        "ready": not blockers,
        "broker_name": broker_name,
        "broker_mode": broker_mode,
        "account_environment": account_environment,
        "order_placement_requires_injected_adapter": True,
        **expected_true,
        **expected_false,
        "blockers": _unique(blockers),
    }


def _order_preview_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contexts = _contexts(source, "order_preview")
    strategy_id = _text_from_contexts(contexts, ("strategy_id",))
    candidate_id = _text_from_contexts(contexts, ("candidate_id",))
    instrument = _text_from_contexts(contexts, ("instrument",))
    side = _text_from_contexts(contexts, ("side",))
    order_type = _text_from_contexts(contexts, ("order_type",))
    units = _number_from_contexts(contexts, ("units",))
    max_position_units = _number_from_contexts(contexts, ("max_position_units",))
    stop_loss_present = _bool_from_contexts(contexts, ("stop_loss_present",))
    take_profit_present = _bool_from_contexts(contexts, ("take_profit_present",))
    max_spread_pips = _number_from_contexts(contexts, ("max_spread_pips",))
    max_slippage_pips = _number_from_contexts(contexts, ("max_slippage_pips",))
    order_preview_accepted_by_owner = _bool_from_contexts(contexts, ("order_preview_accepted_by_owner",))
    order_preview_blocks = _blockers_from_contexts(contexts, ("order_preview_blocks",))

    blockers: list[str] = []
    for key, value in {
        "strategy_id": strategy_id,
        "candidate_id": candidate_id,
        "instrument": instrument,
    }.items():
        if not value:
            blockers.append(f"{key}_missing")
    if not side:
        blockers.append("side_missing")
    elif side.upper() not in ALLOWED_SIDES:
        blockers.append("side_not_supported")
    if not order_type:
        blockers.append("order_type_missing")
    elif order_type.upper() not in ALLOWED_ORDER_TYPES:
        blockers.append("order_type_not_supported")
    if units is None:
        blockers.append("units_missing")
    elif units <= 0:
        blockers.append("units_not_positive")
    if units is not None and max_position_units is not None and units > max_position_units:
        blockers.append("units_above_max_position_units")
    if stop_loss_present is not True:
        blockers.append("stop_loss_present_missing" if stop_loss_present is None else "stop_loss_present_false")
    if take_profit_present is not True:
        blockers.append(
            "take_profit_present_missing" if take_profit_present is None else "take_profit_present_false"
        )
    if max_spread_pips is None:
        blockers.append("max_spread_pips_missing")
    if max_slippage_pips is None:
        blockers.append("max_slippage_pips_missing")
    if order_preview_accepted_by_owner is not True:
        blockers.append(
            "order_preview_accepted_by_owner_missing"
            if order_preview_accepted_by_owner is None
            else "order_preview_accepted_by_owner_false"
        )
    if order_preview_blocks:
        blockers.extend(order_preview_blocks)
    return {
        "ready": not blockers,
        "strategy_id": strategy_id,
        "candidate_id": candidate_id,
        "instrument": instrument,
        "side": side,
        "order_type": order_type,
        "units": _normalize_number(units),
        "max_position_units": _normalize_number(max_position_units),
        "stop_loss_present": stop_loss_present,
        "take_profit_present": take_profit_present,
        "max_spread_pips": _normalize_number(max_spread_pips),
        "max_slippage_pips": _normalize_number(max_slippage_pips),
        "order_preview_accepted_by_owner": order_preview_accepted_by_owner,
        "order_preview_blocks": order_preview_blocks,
        "blockers": _unique(blockers),
    }


def _risk_gate_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contexts = _contexts(source, "risk_gates")
    expected_true = {
        "max_loss_gate_present": _bool_from_contexts(contexts, ("max_loss_gate_present",)),
        "daily_loss_stop_present": _bool_from_contexts(contexts, ("daily_loss_stop_present",)),
        "kill_switch_present": _bool_from_contexts(contexts, ("kill_switch_present",)),
        "position_size_limit_present": _bool_from_contexts(contexts, ("position_size_limit_present",)),
        "one_order_only": _bool_from_contexts(contexts, ("one_order_only",)),
    }
    expected_false = {
        "kill_switch_active": _false_authority_value(contexts, "kill_switch_active"),
    }
    max_risk_per_trade_pct = _number_from_contexts(contexts, ("max_risk_per_trade_pct",))
    max_daily_loss_pct = _number_from_contexts(contexts, ("max_daily_loss_pct",))
    risk_gate_blocks = _blockers_from_contexts(contexts, ("risk_gate_blocks",))
    blockers = _exact_bool_blockers(expected_true=expected_true, expected_false=expected_false)
    if max_risk_per_trade_pct is None:
        blockers.append("max_risk_per_trade_pct_missing")
    elif max_risk_per_trade_pct > 0.01:
        blockers.append("max_risk_per_trade_pct_above_limit")
    if max_daily_loss_pct is None:
        blockers.append("max_daily_loss_pct_missing")
    elif max_daily_loss_pct > 0.03:
        blockers.append("max_daily_loss_pct_above_limit")
    if risk_gate_blocks:
        blockers.extend(risk_gate_blocks)
    return {
        "ready": not blockers,
        **expected_true,
        **expected_false,
        "max_risk_per_trade_pct": _normalize_number(max_risk_per_trade_pct),
        "max_daily_loss_pct": _normalize_number(max_daily_loss_pct),
        "risk_gate_blocks": risk_gate_blocks,
        "blockers": _unique(blockers),
    }


def _abort_condition_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contexts = _contexts(source, "abort_conditions")
    expected_true = {
        "abort_if_owner_approval_missing": _bool_from_contexts(contexts, ("abort_if_owner_approval_missing",)),
        "abort_if_credentials_missing": _bool_from_contexts(contexts, ("abort_if_credentials_missing",)),
        "abort_if_broker_mode_not_demo": _bool_from_contexts(contexts, ("abort_if_broker_mode_not_demo",)),
        "abort_if_spread_above_max": _bool_from_contexts(contexts, ("abort_if_spread_above_max",)),
        "abort_if_slippage_above_max": _bool_from_contexts(contexts, ("abort_if_slippage_above_max",)),
        "abort_if_stop_loss_missing": _bool_from_contexts(contexts, ("abort_if_stop_loss_missing",)),
        "abort_if_take_profit_missing": _bool_from_contexts(contexts, ("abort_if_take_profit_missing",)),
        "abort_if_daily_loss_hit": _bool_from_contexts(contexts, ("abort_if_daily_loss_hit",)),
        "abort_if_kill_switch_active": _bool_from_contexts(contexts, ("abort_if_kill_switch_active",)),
        "abort_if_duplicate_order_detected": _bool_from_contexts(
            contexts,
            ("abort_if_duplicate_order_detected",),
        ),
        "abort_if_wrong_account_detected": _bool_from_contexts(contexts, ("abort_if_wrong_account_detected",)),
        "abort_if_live_account_detected": _bool_from_contexts(contexts, ("abort_if_live_account_detected",)),
    }
    abort_condition_blocks = _blockers_from_contexts(contexts, ("abort_condition_blocks",))
    blockers = _expected_true_blockers(expected_true)
    if abort_condition_blocks:
        blockers.extend(abort_condition_blocks)
    return {
        "ready": not blockers,
        **expected_true,
        "abort_condition_blocks": abort_condition_blocks,
        "blockers": _unique(blockers),
    }


def _telemetry_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contexts = _contexts(source, "telemetry")
    expected_true = {
        "audit_log_required": _bool_from_contexts(contexts, ("audit_log_required",)),
        "sanitized_ticket_required": _bool_from_contexts(contexts, ("sanitized_ticket_required",)),
        "pre_trade_snapshot_required": _bool_from_contexts(contexts, ("pre_trade_snapshot_required",)),
        "order_preview_snapshot_required": _bool_from_contexts(contexts, ("order_preview_snapshot_required",)),
        "post_trade_snapshot_required": _bool_from_contexts(contexts, ("post_trade_snapshot_required",)),
        "exception_capture_required": _bool_from_contexts(contexts, ("exception_capture_required",)),
        "owner_review_report_required": _bool_from_contexts(contexts, ("owner_review_report_required",)),
        "execution_result_required": _bool_from_contexts(contexts, ("execution_result_required",)),
    }
    telemetry_blocks = _blockers_from_contexts(contexts, ("telemetry_blocks",))
    blockers = _expected_true_blockers(expected_true)
    if telemetry_blocks:
        blockers.extend(telemetry_blocks)
    return {
        "ready": not blockers,
        **expected_true,
        "telemetry_blocks": telemetry_blocks,
        "blockers": _unique(blockers),
    }


def _post_trade_review_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contexts = _contexts(source, "post_trade_review")
    expected_true = {
        "post_trade_review_required": _bool_from_contexts(contexts, ("post_trade_review_required",)),
        "pnl_review_required": _bool_from_contexts(contexts, ("pnl_review_required",)),
        "risk_review_required": _bool_from_contexts(contexts, ("risk_review_required",)),
        "execution_quality_review_required": _bool_from_contexts(
            contexts,
            ("execution_quality_review_required",),
        ),
        "next_trade_blocked_until_review": _bool_from_contexts(
            contexts,
            ("next_trade_blocked_until_review",),
        ),
    }
    post_trade_review_blocks = _blockers_from_contexts(contexts, ("post_trade_review_blocks",))
    blockers = _expected_true_blockers(expected_true)
    if post_trade_review_blocks:
        blockers.extend(post_trade_review_blocks)
    return {
        "ready": not blockers,
        **expected_true,
        "post_trade_review_blocks": post_trade_review_blocks,
        "blockers": _unique(blockers),
    }


def _data_quality_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    contexts = _contexts(source, "data_quality")
    data_quality_blocks = _blockers_from_contexts(contexts, ("data_quality_blocks",))
    missing_fields = _blockers_from_contexts(contexts, ("missing_fields",))
    malformed_fields = _blockers_from_contexts(contexts, ("malformed_fields",))
    blockers = _unique([*data_quality_blocks, *missing_fields, *malformed_fields])
    return {
        "ready": not blockers,
        "data_quality_blocks": data_quality_blocks,
        "missing_fields": missing_fields,
        "malformed_fields": malformed_fields,
        "blockers": blockers,
    }


def _sanitized_order_request(
    *,
    owner_approval_summary: Mapping[str, Any],
    oanda_demo_boundary_summary: Mapping[str, Any],
    order_preview_summary: Mapping[str, Any],
    risk_gate_summary: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "broker_name": oanda_demo_boundary_summary.get("broker_name"),
        "broker_mode": oanda_demo_boundary_summary.get("broker_mode"),
        "account_environment": oanda_demo_boundary_summary.get("account_environment"),
        "strategy_id": order_preview_summary.get("strategy_id"),
        "candidate_id": order_preview_summary.get("candidate_id"),
        "instrument": order_preview_summary.get("instrument"),
        "side": order_preview_summary.get("side"),
        "order_type": order_preview_summary.get("order_type"),
        "units": order_preview_summary.get("units"),
        "stop_loss_present": order_preview_summary.get("stop_loss_present"),
        "take_profit_present": order_preview_summary.get("take_profit_present"),
        "max_spread_pips": order_preview_summary.get("max_spread_pips"),
        "max_slippage_pips": order_preview_summary.get("max_slippage_pips"),
        "risk_limits": {
            "max_position_units": order_preview_summary.get("max_position_units"),
            "max_risk_per_trade_pct": risk_gate_summary.get("max_risk_per_trade_pct"),
            "max_daily_loss_pct": risk_gate_summary.get("max_daily_loss_pct"),
            "kill_switch_active": risk_gate_summary.get("kill_switch_active"),
            "one_order_only": risk_gate_summary.get("one_order_only"),
        },
        "owner_name": owner_approval_summary.get("owner_name") or "Anthony",
        "owner_final_approval_for_demo_execution": owner_approval_summary.get(
            "owner_final_approval_for_demo_execution"
        ),
        "demo_only": True,
        "live_execution_allowed": False,
        "credentials_included": False,
    }


def _adapter_summary(broker_adapter: object | None) -> dict[str, Any]:
    if broker_adapter is None:
        return {
            "adapter_supplied": False,
            "contract_ready": False,
            "method_name": None,
            "adapter_method": None,
            "adapter_called": False,
            "adapter_result_captured": False,
            "blockers": ["adapter_missing"],
        }
    submit_demo_order = getattr(broker_adapter, "submit_demo_order", None)
    if callable(submit_demo_order):
        return {
            "adapter_supplied": True,
            "contract_ready": True,
            "method_name": "submit_demo_order",
            "adapter_method": submit_demo_order,
            "adapter_called": False,
            "adapter_result_captured": False,
            "blockers": [],
        }
    submit_order = getattr(broker_adapter, "submit_order", None)
    if callable(submit_order):
        return {
            "adapter_supplied": True,
            "contract_ready": True,
            "method_name": "submit_order",
            "adapter_method": submit_order,
            "adapter_called": False,
            "adapter_result_captured": False,
            "blockers": [],
        }
    return {
        "adapter_supplied": True,
        "contract_ready": False,
        "method_name": None,
        "adapter_method": None,
        "adapter_called": False,
        "adapter_result_captured": False,
        "blockers": ["adapter_submit_method_missing"],
    }


def _public_adapter_summary(adapter_summary: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "adapter_supplied": adapter_summary["adapter_supplied"],
        "contract_ready": adapter_summary["contract_ready"],
        "method_name": adapter_summary["method_name"],
        "adapter_called": adapter_summary["adapter_called"],
        "adapter_result_captured": adapter_summary["adapter_result_captured"],
        "blockers": list(adapter_summary["blockers"]),
    }


def _resolve_execution_status(
    *,
    sensitive_data_present: bool,
    missing_information: Sequence[str],
    runtime_handoff_summary: Mapping[str, Any],
    owner_approval_summary: Mapping[str, Any],
    oanda_demo_boundary_summary: Mapping[str, Any],
    order_preview_summary: Mapping[str, Any],
    risk_gate_summary: Mapping[str, Any],
    abort_condition_summary: Mapping[str, Any],
    telemetry_summary: Mapping[str, Any],
    post_trade_review_summary: Mapping[str, Any],
    data_quality_summary: Mapping[str, Any],
    adapter_supplied: bool,
    adapter_summary: Mapping[str, Any],
) -> str:
    if sensitive_data_present or not data_quality_summary["ready"]:
        return BLOCKED_BY_DATA_QUALITY
    if missing_information:
        return INCOMPLETE_INPUTS
    if not runtime_handoff_summary["ready"]:
        return BLOCKED_BY_RUNTIME_HANDOFF
    if not owner_approval_summary["ready"]:
        return BLOCKED_BY_OWNER_APPROVAL
    if not oanda_demo_boundary_summary["ready"]:
        return BLOCKED_BY_OANDA_DEMO_BOUNDARY
    if not order_preview_summary["ready"]:
        return BLOCKED_BY_ORDER_PREVIEW
    if not risk_gate_summary["ready"]:
        return BLOCKED_BY_RISK_GATES
    if not abort_condition_summary["ready"]:
        return BLOCKED_BY_ABORT_CONDITIONS
    if not telemetry_summary["ready"]:
        return BLOCKED_BY_TELEMETRY
    if not post_trade_review_summary["ready"]:
        return BLOCKED_BY_POST_TRADE_REVIEW
    if not adapter_supplied:
        return READY_FOR_OWNER_SUPERVISED_DEMO_EXECUTION
    if not adapter_summary["contract_ready"]:
        return BLOCKED_BY_ADAPTER_CONTRACT
    return DEMO_ORDER_EXECUTED_WITH_INJECTED_ADAPTER


def _execution_blockers(
    *,
    execution_status: str,
    sensitive_data_present: bool,
    missing_information: Sequence[str],
    runtime_handoff_summary: Mapping[str, Any],
    owner_approval_summary: Mapping[str, Any],
    oanda_demo_boundary_summary: Mapping[str, Any],
    order_preview_summary: Mapping[str, Any],
    risk_gate_summary: Mapping[str, Any],
    abort_condition_summary: Mapping[str, Any],
    telemetry_summary: Mapping[str, Any],
    post_trade_review_summary: Mapping[str, Any],
    data_quality_summary: Mapping[str, Any],
    adapter_summary: Mapping[str, Any],
) -> list[str]:
    if execution_status == DEMO_ORDER_EXECUTED_WITH_INJECTED_ADAPTER:
        return []
    if sensitive_data_present:
        return ["sensitive_data_provided"]
    if execution_status == INCOMPLETE_INPUTS:
        return [f"missing_{item}" for item in missing_information]
    if execution_status == BLOCKED_BY_RUNTIME_HANDOFF:
        return list(runtime_handoff_summary["blockers"])
    if execution_status == BLOCKED_BY_OWNER_APPROVAL:
        return list(owner_approval_summary["blockers"])
    if execution_status == BLOCKED_BY_OANDA_DEMO_BOUNDARY:
        return list(oanda_demo_boundary_summary["blockers"])
    if execution_status == BLOCKED_BY_ORDER_PREVIEW:
        return list(order_preview_summary["blockers"])
    if execution_status == BLOCKED_BY_RISK_GATES:
        return list(risk_gate_summary["blockers"])
    if execution_status == BLOCKED_BY_ABORT_CONDITIONS:
        return list(abort_condition_summary["blockers"])
    if execution_status == BLOCKED_BY_TELEMETRY:
        return list(telemetry_summary["blockers"])
    if execution_status == BLOCKED_BY_POST_TRADE_REVIEW:
        return list(post_trade_review_summary["blockers"])
    if execution_status == BLOCKED_BY_ADAPTER_CONTRACT:
        return list(adapter_summary["blockers"])
    if execution_status == BLOCKED_BY_DATA_QUALITY:
        return list(data_quality_summary["blockers"])
    return []


def _owner_action_queue(next_best_packet: str, execution_blockers: Sequence[str]) -> list[dict[str, Any]]:
    return [
        {
            "action_id": action_id,
            "owner_decision_required": True,
            "live_execution_allowed": False,
            "next_best_packet": next_best_packet if action_id == "REVIEW_NEXT_PACKET" else None,
            "blocked_by": list(execution_blockers),
        }
        for action_id in OWNER_ACTION_IDS
    ]


def _next_best_packet(execution_status: str) -> str:
    if execution_status == DEMO_ORDER_EXECUTED_WITH_INJECTED_ADAPTER:
        return NEXT_PACKET_AFTER_EXECUTION
    if execution_status == READY_FOR_OWNER_SUPERVISED_DEMO_EXECUTION:
        return NEXT_PACKET_IF_READY
    return THIS_PACKET


def _safe_manual_next_action(execution_status: str) -> str:
    if execution_status == DEMO_ORDER_EXECUTED_WITH_INJECTED_ADAPTER:
        return "Review the sanitized adapter result and complete post-execution review before any later demo order."
    if execution_status == READY_FOR_OWNER_SUPERVISED_DEMO_EXECUTION:
        return "Review the sanitized order request and bind a separately approved demo adapter packet before any supervised demo attempt."
    if execution_status == INCOMPLETE_INPUTS:
        return "Supply sanitized runtime handoff, owner approval, demo boundary, order preview, risk, abort, telemetry, and review evidence."
    return "Resolve listed blockers, keep direct broker/API/credential/live paths closed, then rerun this controller."


def _safety() -> dict[str, Any]:
    return {
        "direct_broker_api_allowed": False,
        "live_trading_allowed": False,
        "real_money_allowed": False,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "credential_storage_allowed": False,
        "credential_read_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
        "dashboard_runtime_allowed": False,
        "owner_gate_required": True,
        "demo_only": True,
        "fixed_return_target_promised": False,
        "profit_claim_authorized": False,
    }


def _missing_information(source: Mapping[str, Any]) -> list[str]:
    return [key for key in CORE_EVIDENCE_KEYS if not isinstance(source.get(key), Mapping)]


def _contexts(source: Mapping[str, Any], section: str) -> list[Mapping[str, Any]]:
    contexts: list[Mapping[str, Any]] = []
    section_value = _mapping(source.get(section))
    if section_value:
        contexts.append(section_value)
    snapshot = _mapping(source.get("readiness_snapshot"))
    if snapshot:
        contexts.append(snapshot)
    contexts.append(source)
    return contexts


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key).lower()
            if key_text not in SAFE_BOUNDARY_KEYS and any(part in key_text for part in SENSITIVE_KEY_PARTS):
                return True
            if _contains_sensitive_key(nested):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def _first_present(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> Any:
    for context in contexts:
        for key in keys:
            if key in context:
                return context[key]
    return None


def _text_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> str | None:
    return _text(_first_present(contexts, keys), None)


def _bool_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> bool | None:
    return _bool(_first_present(contexts, keys))


def _number_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> float | None:
    return _number(_first_present(contexts, keys))


def _blockers_from_contexts(contexts: Sequence[Mapping[str, Any]], keys: Sequence[str]) -> list[str]:
    blockers: list[str] = []
    for context in contexts:
        for key in keys:
            value = context.get(key)
            if isinstance(value, str) and value.strip():
                blockers.append(value.strip())
            elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                blockers.extend(str(item) for item in value if str(item).strip())
    return _unique(blockers)


def _false_authority_value(contexts: Sequence[Mapping[str, Any]], key: str) -> bool | None:
    saw_false = False
    for context in contexts:
        if key not in context:
            continue
        value = _bool(context[key])
        if value is True:
            return True
        if value is False:
            saw_false = True
    return False if saw_false else None


def _exact_bool_blockers(
    *,
    expected_true: Mapping[str, bool | None],
    expected_false: Mapping[str, bool | None],
) -> list[str]:
    blockers = _expected_true_blockers(expected_true)
    for key, value in expected_false.items():
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is not False:
            blockers.append(f"{key}_true")
    return blockers


def _expected_true_blockers(expected_true: Mapping[str, bool | None]) -> list[str]:
    blockers: list[str] = []
    for key, value in expected_true.items():
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is not True:
            blockers.append(f"{key}_false")
    return blockers


def _bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1", "pass"}:
            return True
        if lowered in {"false", "no", "0", "fail"}:
            return False
    return None


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and isfinite(float(value)):
        return float(value)
    if isinstance(value, str):
        try:
            number = float(value.strip())
        except ValueError:
            return None
        return number if isfinite(number) else None
    return None


def _text(value: Any, default: str | None = "") -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _normalize_number(value: float | None) -> int | float | None:
    if value is None:
        return None
    return int(value) if float(value).is_integer() else value


def _copy_for_adapter(value: Mapping[str, Any]) -> dict[str, Any]:
    copied: dict[str, Any] = {}
    for key, item in value.items():
        copied[key] = _copy_for_adapter(item) if isinstance(item, Mapping) else item
    return copied


def _sanitize_for_output(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {"adapter_result_captured": False, "adapter_result_type": type(value).__name__}
    sanitized: dict[str, Any] = {}
    for key, item in value.items():
        key_text = str(key)
        if _contains_sensitive_key({key_text: item}):
            sanitized[key_text] = "[REDACTED]"
        elif isinstance(item, Mapping):
            sanitized[key_text] = _sanitize_for_output(item)
        elif isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
            sanitized[key_text] = [
                _sanitize_for_output(nested) if isinstance(nested, Mapping) else nested for nested in item
            ]
        else:
            sanitized[key_text] = item
    return sanitized


def _unique(values: Sequence[Any]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        item = str(value)
        if item and item not in seen:
            seen.add(item)
            unique.append(item)
    return unique
