"""Owner-approved OANDA demo one-order execution readiness evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation
from typing import Any


SCHEMA = "AIOS_FOREX_OWNER_APPROVED_DEMO_ONE_ORDER_PROFIT_ATTEMPT_EXECUTION_V1"
MODE = "READ_ONLY_METADATA_ONLY_OWNER_APPROVED_DEMO_ONE_ORDER_EXECUTION"
PREPARE_MODE = "READ_ONLY_METADATA_ONLY_OWNER_APPROVED_DEMO_ONE_ORDER_PREPARE"

PACKET_ID = "AIOS_FOREX_OWNER_APPROVED_DEMO_ONE_ORDER_PROFIT_ATTEMPT_EXECUTION_V1"
NEXT_PACKET_CURRENT = SCHEMA
NEXT_PACKET_RUNTIME_RECEIPT_AND_POST_TRADE_REVIEW = (
    "AIOS_FOREX_OANDA_DEMO_RUNTIME_RECEIPT_AND_POST_TRADE_REVIEW_V1"
)

REPO_APPROVED_RUNTIME_INTERFACE = (
    "oanda_demo_owner_approved_one_order_protected_runtime_execution_v1."
    "evaluate_oanda_demo_owner_approved_one_order_protected_runtime_execution_v1"
)

DEMO_ONE_ORDER_EXECUTION_READY_FOR_RUNTIME = (
    "DEMO_ONE_ORDER_EXECUTION_READY_FOR_RUNTIME"
)
DEMO_ONE_ORDER_EXECUTION_PREPARED_NOT_SENT = (
    "DEMO_ONE_ORDER_EXECUTION_PREPARED_NOT_SENT"
)
BLOCKED_BY_OWNER_APPROVAL = "BLOCKED_BY_OWNER_APPROVAL"
BLOCKED_BY_EXISTING_RUNTIME_EXECUTION_INTERFACE_MISSING = (
    "BLOCKED_BY_EXISTING_RUNTIME_EXECUTION_INTERFACE_MISSING"
)
BLOCKED_BY_RUNTIME_CREDENTIAL_SESSION_REQUIRED = (
    "BLOCKED_BY_RUNTIME_CREDENTIAL_SESSION_REQUIRED"
)
BLOCKED_BY_ORDER_CANDIDATE = "BLOCKED_BY_ORDER_CANDIDATE"
BLOCKED_BY_RISK_GATES = "BLOCKED_BY_RISK_GATES"
BLOCKED_BY_OANDA_DEMO_MODE = "BLOCKED_BY_OANDA_DEMO_MODE"
BLOCKED_BY_ONE_ORDER_LIMIT = "BLOCKED_BY_ONE_ORDER_LIMIT"
BLOCKED_BY_KILL_SWITCH = "BLOCKED_BY_KILL_SWITCH"
BLOCKED_BY_DAILY_LOSS_STOP = "BLOCKED_BY_DAILY_LOSS_STOP"
BLOCKED_BY_POST_TRADE_REVIEW = "BLOCKED_BY_POST_TRADE_REVIEW"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

READY_PROTECTED_DEMO_ATTEMPT_STATUSES = frozenset(
    {
        "PROTECTED_DEMO_DAILY_PROFIT_ATTEMPT_READY",
        "READY_FOR_OWNER_APPROVED_DEMO_ONE_ORDER_PACKET",
    }
)
ALLOWED_OANDA_DEMO_MODES = frozenset({"OANDA_DEMO", "PRACTICE", "DEMO"})

TOP_LEVEL_SECTIONS = (
    "owner_approval",
    "protected_demo_attempt_result",
    "runtime_boundary",
    "existing_runtime_interface",
    "order_candidate",
    "risk_plan",
    "oanda_demo_boundary",
    "post_trade_review",
)

HARD_FALSE_FIELDS = (
    "live_trade_executed",
    "money_moved",
    "bank_access_used",
    "credential_stored",
    "api_key_stored",
    "master_password_used",
    "vault_password_used",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "dashboard_runtime_created",
    "actual_live_execution_authorized",
    "banking_work_built",
    "withdrawal_work_built",
    "transfer_work_built",
    "broker_api_called",
    "credential_read",
    "demo_trade_executed",
    "actual_demo_execution_authorized",
)

SENSITIVE_KEY_PARTS = (
    "api_key",
    "token_value",
    "password",
    "master_password",
    "vault_password",
    "account_number",
    "routing_number",
    "card_number",
    "debit_card_number",
    "cvv",
    "account_id",
    "oanda_account_id",
    "bearer",
    "broker_token",
    "access_token",
    "private_key",
)

SAFE_SENSITIVE_METADATA_KEYS = frozenset(
    {
        "account_id_in_payload",
        "api_key_stored",
        "broker_api_called",
        "credential_read",
        "credential_stored",
        "credential_values_in_payload",
        "master_password_used",
        "no_raw_secret_logging",
        "no_stored_account_id",
        "no_stored_api_key",
        "vault_password_used",
    }
)

SENSITIVE_SIGNAL_FALSE_KEYS = frozenset(
    {"account_id_in_payload", "credential_values_in_payload"}
)

BANKING_KEY_PARTS = (
    "bank",
    "banking",
    "withdraw",
    "withdrawal",
    "transfer",
    "debit",
    "card",
    "rail",
    "ach",
    "wire",
    "sweep",
    "bucket_purge",
    "money_movement",
)

SAFE_BANKING_FALSE_KEYS = frozenset(
    {
        "bank_access_used",
        "banking_work_built",
        "money_moved",
        "money_movement_allowed",
        "transfer_work_built",
        "withdrawal_work_built",
    }
)
SAFE_BANKING_TRUE_KEYS = frozenset(
    {
        "approval_scope_no_banking_transfer",
        "approval_scope_no_money_movement",
    }
)


def evaluate_forex_owner_approved_demo_one_order_profit_attempt_execution_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Evaluate owner-approved demo one-order readiness without side effects."""

    source = payload if isinstance(payload, Mapping) else {}
    sensitive_data_blockers = _sensitive_data_blockers(source)
    banking_focus_blockers = _banking_focus_blockers(source)

    if sensitive_data_blockers:
        return _build_result(
            source=source,
            status=BLOCKED_BY_SENSITIVE_DATA,
            blockers=sensitive_data_blockers,
            sensitive_data_detected=True,
            banking_focus_detected=False,
            redacted=True,
        )
    if banking_focus_blockers:
        return _build_result(
            source=source,
            status=BLOCKED_BY_BANKING_FOCUS,
            blockers=banking_focus_blockers,
            sensitive_data_detected=False,
            banking_focus_detected=True,
            redacted=True,
        )
    if not source:
        return _build_result(
            source=source,
            status=INCOMPLETE_INPUTS,
            blockers=tuple(f"missing_{section}" for section in TOP_LEVEL_SECTIONS),
            sensitive_data_detected=False,
            banking_focus_detected=False,
            redacted=False,
        )

    summaries = _summaries(source)
    status, blockers = _execution_status(summaries)
    return _build_result(
        source=source,
        status=status,
        blockers=tuple(blockers),
        sensitive_data_detected=False,
        banking_focus_detected=False,
        redacted=False,
        summaries=summaries,
    )


def prepare_owner_approved_demo_one_order_execution_command_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Return a sanitized prepared-not-sent intent packet only."""

    evaluation = evaluate_forex_owner_approved_demo_one_order_profit_attempt_execution_v1(
        payload
    )
    if evaluation["demo_one_order_execution_status"] != (
        DEMO_ONE_ORDER_EXECUTION_READY_FOR_RUNTIME
    ):
        return {
            **evaluation,
            "prepared": False,
            "sent_to_runtime": False,
            "demo_one_order_execution_prepared": False,
        }

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "mode": PREPARE_MODE,
        "packet_id": PACKET_ID,
        "demo_one_order_execution_status": DEMO_ONE_ORDER_EXECUTION_PREPARED_NOT_SENT,
        "status": DEMO_ONE_ORDER_EXECUTION_PREPARED_NOT_SENT,
        "source_evaluation_status": DEMO_ONE_ORDER_EXECUTION_READY_FOR_RUNTIME,
        "prepared": True,
        "sent_to_runtime": False,
        "demo_one_order_execution_prepared": True,
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        "approval_token_required": True,
        "sanitized_execution_intent": dict(
            evaluation["sanitized_execution_intent"]
        ),
        "blockers": [],
        "next_best_packet": NEXT_PACKET_RUNTIME_RECEIPT_AND_POST_TRADE_REVIEW,
        "safe_manual_next_action": (
            "Route this sanitized intent to a separately approved runtime receipt "
            "and post-trade review packet; no broker call is made here."
        ),
        "safety": _safety(),
    }
    result.update({field: False for field in HARD_FALSE_FIELDS})
    return result


def _execution_status(
    summaries: Mapping[str, Mapping[str, Any]]
) -> tuple[str, list[str]]:
    owner = summaries["owner_approval_summary"]
    protected_demo = summaries["protected_demo_attempt_summary"]
    runtime = summaries["runtime_boundary_summary"]
    interface = summaries["existing_runtime_interface_summary"]
    oanda = summaries["oanda_demo_boundary_summary"]
    order = summaries["order_candidate_summary"]
    risk = summaries["risk_plan_summary"]
    review = summaries["post_trade_review_summary"]

    if not owner["ready"]:
        return BLOCKED_BY_OWNER_APPROVAL, list(owner["blockers"])
    if not protected_demo["ready"]:
        return INCOMPLETE_INPUTS, list(protected_demo["blockers"])
    if not runtime["ready"]:
        return BLOCKED_BY_RUNTIME_CREDENTIAL_SESSION_REQUIRED, list(
            runtime["blockers"]
        )
    if not interface["ready"]:
        return BLOCKED_BY_EXISTING_RUNTIME_EXECUTION_INTERFACE_MISSING, list(
            interface["blockers"]
        )
    if not oanda["ready"]:
        return BLOCKED_BY_OANDA_DEMO_MODE, list(oanda["blockers"])
    if order["duplicate_candidate"] is True:
        return BLOCKED_BY_ONE_ORDER_LIMIT, ["duplicate_candidate_true"]
    if not order["candidate_metadata_ready"]:
        return BLOCKED_BY_ORDER_CANDIDATE, list(order["candidate_blockers"])
    if not order["stop_take_metadata_ready"]:
        return BLOCKED_BY_RISK_GATES, list(order["stop_take_blockers"])
    if risk["kill_switch_active"] is True:
        return BLOCKED_BY_KILL_SWITCH, ["kill_switch_active_true"]
    if risk["daily_loss_stop_active"] is True:
        return BLOCKED_BY_DAILY_LOSS_STOP, ["daily_loss_stop_active_true"]
    if not risk["one_order_limit_ready"]:
        return BLOCKED_BY_ONE_ORDER_LIMIT, list(risk["one_order_limit_blockers"])
    if not risk["risk_limits_ready"]:
        return BLOCKED_BY_RISK_GATES, list(risk["risk_limit_blockers"])
    if not review["ready"]:
        return BLOCKED_BY_POST_TRADE_REVIEW, list(review["blockers"])
    return DEMO_ONE_ORDER_EXECUTION_READY_FOR_RUNTIME, []


def _summaries(source: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "owner_approval_summary": _owner_approval_summary(
            _mapping(source.get("owner_approval"))
        ),
        "protected_demo_attempt_summary": _protected_demo_attempt_summary(
            _mapping(source.get("protected_demo_attempt_result"))
        ),
        "runtime_boundary_summary": _runtime_boundary_summary(
            _mapping(source.get("runtime_boundary"))
        ),
        "existing_runtime_interface_summary": _existing_runtime_interface_summary(
            _mapping(source.get("existing_runtime_interface"))
        ),
        "order_candidate_summary": _order_candidate_summary(
            _mapping(source.get("order_candidate"))
        ),
        "risk_plan_summary": _risk_plan_summary(
            _mapping(source.get("risk_plan"))
        ),
        "oanda_demo_boundary_summary": _oanda_demo_boundary_summary(
            _mapping(source.get("oanda_demo_boundary"))
        ),
        "post_trade_review_summary": _post_trade_review_summary(
            _mapping(source.get("post_trade_review"))
        ),
    }


def _owner_approval_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    checks = {
        "approval_text_present": _bool(data.get("approval_text_present")),
        "approval_packet_id_matches": data.get("approval_packet_id") == PACKET_ID,
        "owner_name_anthony": data.get("owner_name") == "Anthony",
        "approval_scope_demo_only": _bool(
            data.get("approval_scope_demo_only")
        ),
        "approval_scope_one_order_only": _bool(
            data.get("approval_scope_one_order_only")
        ),
        "approval_scope_no_live_trade": _bool(
            data.get("approval_scope_no_live_trade")
        ),
        "approval_scope_no_money_movement": _bool(
            data.get("approval_scope_no_money_movement")
        ),
        "approval_scope_no_banking_transfer": _bool(
            data.get("approval_scope_no_banking_transfer")
        ),
    }
    blockers = _false_gate_blockers(checks)
    return {
        "present": bool(data),
        "ready": bool(data) and not blockers,
        "blockers": _unique(blockers if data else ["owner_approval_missing"]),
        **checks,
    }


def _protected_demo_attempt_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    status = _text(data.get("protected_demo_attempt_status"))
    hard_false_clear = all(
        data.get(field) is False
        for field in (
            "actual_demo_execution_authorized",
            "actual_live_execution_authorized",
            "broker_api_called",
            "credential_read",
            "money_moved",
        )
    )
    checks = {
        "protected_demo_attempt_status_allowed": (
            status in READY_PROTECTED_DEMO_ATTEMPT_STATUSES
        ),
        "protected_demo_attempt_ready": _bool(
            data.get("protected_demo_attempt_ready")
        ),
        "protected_demo_attempt_hard_false_inputs_clear": hard_false_clear,
    }
    blockers = _false_gate_blockers(checks)
    return {
        "present": bool(data),
        "ready": bool(data) and not blockers,
        "protected_demo_attempt_status": status,
        "blockers": _unique(
            blockers if data else ["protected_demo_attempt_result_missing"]
        ),
        **checks,
    }


def _runtime_boundary_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    checks = {
        "runtime_credential_session_available": _bool(
            data.get("runtime_credential_session_available")
        ),
        "credential_values_in_payload_false": data.get(
            "credential_values_in_payload"
        )
        is False,
        "account_id_in_payload_false": data.get("account_id_in_payload")
        is False,
        "credential_session_scope_one_order_demo_only": data.get(
            "credential_session_scope"
        )
        == "ONE_ORDER_DEMO_ONLY",
        "session_unexpired": _bool(data.get("session_unexpired")),
        "no_stored_api_key": _bool(data.get("no_stored_api_key")),
        "no_stored_account_id": _bool(data.get("no_stored_account_id")),
        "no_raw_secret_logging": _bool(data.get("no_raw_secret_logging")),
        "redaction_required": _bool(data.get("redaction_required")),
    }
    blockers = _false_gate_blockers(checks)
    return {
        "present": bool(data),
        "ready": bool(data) and not blockers,
        "blockers": _unique(blockers if data else ["runtime_boundary_missing"]),
        **checks,
    }


def _existing_runtime_interface_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    interface_name = _text(data.get("interface_name"))
    checks = {
        "repo_runtime_interface_identified": _bool(
            data.get("repo_runtime_interface_identified")
        ),
        "interface_name_present": bool(interface_name),
        "interface_is_demo_only": _bool(data.get("interface_is_demo_only")),
        "interface_supports_one_order": _bool(
            data.get("interface_supports_one_order")
        ),
        "interface_does_not_store_credentials": _bool(
            data.get("interface_does_not_store_credentials")
        ),
        "interface_does_not_allow_live_trade": _bool(
            data.get("interface_does_not_allow_live_trade")
        ),
    }
    blockers = _false_gate_blockers(checks)
    return {
        "present": bool(data),
        "ready": bool(data) and not blockers,
        "interface_name": interface_name,
        "repo_approved_runtime_interface": REPO_APPROVED_RUNTIME_INTERFACE,
        "blockers": _unique(
            blockers if data else ["existing_runtime_interface_missing"]
        ),
        **checks,
    }


def _order_candidate_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    candidate_fields = (
        "instrument",
        "side",
        "order_type",
        "units",
        "setup_id",
        "evidence_id",
    )
    missing_candidate = tuple(
        field for field in candidate_fields if not _present(data.get(field))
    )
    units = _decimal(data.get("units"))
    duplicate_candidate = data.get("duplicate_candidate") is True
    candidate_checks = {
        "required_candidate_fields_present": not missing_candidate,
        "units_positive": units is not None and units > 0,
        "duplicate_candidate_clear": duplicate_candidate is False,
    }
    stop_take_checks = {
        "stop_loss_present": _bool(data.get("stop_loss_present")),
        "take_profit_present": _bool(data.get("take_profit_present")),
        "stop_loss_value_or_distance_present": _bool(
            data.get("stop_loss_value_or_distance_present")
        ),
        "take_profit_value_or_distance_present": _bool(
            data.get("take_profit_value_or_distance_present")
        ),
    }
    candidate_blockers = _false_gate_blockers(candidate_checks)
    candidate_blockers.extend(f"missing_{field}" for field in missing_candidate)
    stop_take_blockers = _false_gate_blockers(stop_take_checks)
    return {
        "present": bool(data),
        "candidate_metadata_ready": bool(data) and not candidate_blockers,
        "stop_take_metadata_ready": bool(data) and not stop_take_blockers,
        "instrument": _text(data.get("instrument")),
        "side": _text(data.get("side")),
        "order_type": _text(data.get("order_type")),
        "units": _number_or_original(data.get("units")),
        "setup_id": _text(data.get("setup_id")),
        "evidence_id": _text(data.get("evidence_id")),
        "duplicate_candidate": duplicate_candidate,
        "candidate_blockers": _unique(
            candidate_blockers if data else ["order_candidate_missing"]
        ),
        "stop_take_blockers": _unique(
            stop_take_blockers if data else ["order_candidate_missing"]
        ),
        **candidate_checks,
        **stop_take_checks,
    }


def _risk_plan_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    max_risk = _decimal(data.get("max_risk_per_trade_pct"))
    max_daily_loss = _decimal(data.get("max_daily_loss_pct"))
    max_order_count = _decimal(data.get("max_order_count_this_packet"))
    risk_limit_checks = {
        "max_risk_per_trade_pct_gate": max_risk is not None
        and max_risk <= Decimal("0.01"),
        "max_daily_loss_pct_gate": max_daily_loss is not None
        and max_daily_loss <= Decimal("0.03"),
    }
    one_order_checks = {
        "one_order_only": _bool(data.get("one_order_only")),
        "max_order_count_this_packet_one": max_order_count == Decimal("1"),
        "next_order_blocked_until_review": _bool(
            data.get("next_order_blocked_until_review")
        ),
    }
    kill_switch_active = data.get("kill_switch_active") is True
    daily_loss_stop_active = data.get("daily_loss_stop_active") is True
    risk_limit_blockers = _false_gate_blockers(risk_limit_checks)
    one_order_blockers = _false_gate_blockers(one_order_checks)
    if data and "kill_switch_active" not in data:
        risk_limit_blockers.append("kill_switch_active_missing")
    if data and "daily_loss_stop_active" not in data:
        risk_limit_blockers.append("daily_loss_stop_active_missing")
    return {
        "present": bool(data),
        "risk_limits_ready": bool(data)
        and not risk_limit_blockers
        and not kill_switch_active
        and not daily_loss_stop_active,
        "one_order_limit_ready": bool(data) and not one_order_blockers,
        "max_risk_per_trade_pct": _number_or_none(max_risk),
        "max_daily_loss_pct": _number_or_none(max_daily_loss),
        "max_order_count_this_packet": _number_or_none(max_order_count),
        "kill_switch_active": kill_switch_active,
        "daily_loss_stop_active": daily_loss_stop_active,
        "risk_limit_blockers": _unique(
            risk_limit_blockers if data else ["risk_plan_missing"]
        ),
        "one_order_limit_blockers": _unique(
            one_order_blockers if data else ["risk_plan_missing"]
        ),
        **risk_limit_checks,
        **one_order_checks,
    }


def _oanda_demo_boundary_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    mode = _text(data.get("mode"))
    broker_name = _text(data.get("broker_name"))
    checks = {
        "broker_name_oanda": broker_name == "OANDA",
        "mode_demo": mode in ALLOWED_OANDA_DEMO_MODES,
        "live_trading_allowed_false": data.get("live_trading_allowed")
        is False,
        "real_money_allowed_false": data.get("real_money_allowed") is False,
        "money_movement_allowed_false": data.get("money_movement_allowed")
        is False,
        "account_id_in_payload_false": data.get("account_id_in_payload")
        is False,
    }
    blockers = _false_gate_blockers(checks)
    return {
        "present": bool(data),
        "ready": bool(data) and not blockers,
        "broker_name": broker_name,
        "mode": mode,
        "blockers": _unique(
            blockers if data else ["oanda_demo_boundary_missing"]
        ),
        **checks,
    }


def _post_trade_review_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    checks = {
        "post_trade_review_required": _bool(
            data.get("post_trade_review_required")
        ),
        "daily_pnl_record_required": _bool(
            data.get("daily_pnl_record_required")
        ),
        "sanitized_receipt_required": _bool(
            data.get("sanitized_receipt_required")
        ),
        "owner_review_required": _bool(data.get("owner_review_required")),
        "no_second_trade_without_review": _bool(
            data.get("no_second_trade_without_review")
        ),
    }
    blockers = _false_gate_blockers(checks)
    return {
        "present": bool(data),
        "ready": bool(data) and not blockers,
        "blockers": _unique(blockers if data else ["post_trade_review_missing"]),
        **checks,
    }


def _build_result(
    *,
    source: Mapping[str, Any],
    status: str,
    blockers: Sequence[str],
    sensitive_data_detected: bool,
    banking_focus_detected: bool,
    redacted: bool,
    summaries: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if summaries is None:
        summaries = _redacted_summaries() if redacted else _summaries(source)
    ready = status == DEMO_ONE_ORDER_EXECUTION_READY_FOR_RUNTIME
    sanitized_execution_intent = (
        _sanitized_execution_intent(source) if ready and not redacted else {}
    )
    next_best_packet = _next_best_packet(status)
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "mode": MODE,
        "packet_id": PACKET_ID,
        "demo_one_order_execution_status": status,
        "status": status,
        "demo_one_order_execution_ready": ready,
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        "approval_token_required": True,
        **summaries,
        "sanitized_execution_intent": sanitized_execution_intent,
        "blockers": list(blockers),
        "sensitive_data_detected": sensitive_data_detected,
        "sensitive_values_echoed": False,
        "banking_focus_detected": banking_focus_detected,
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(status),
        "owner_action_queue": _owner_action_queue(status, blockers, next_best_packet),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "packet_id": PACKET_ID,
            "demo_one_order_execution_status": status,
            "demo_one_order_execution_ready": ready,
            "input_redacted": redacted,
            "sensitive_data_detected": sensitive_data_detected,
            "sensitive_values_echoed": False,
            "banking_focus_detected": banking_focus_detected,
            "blocker_count": len(blockers),
            "next_best_packet": next_best_packet,
            "read_only": True,
            "metadata_only": True,
        },
        "safety": _safety(),
    }
    result.update({field: False for field in HARD_FALSE_FIELDS})
    return result


def _sanitized_execution_intent(source: Mapping[str, Any]) -> dict[str, Any]:
    order = _mapping(source.get("order_candidate"))
    risk = _mapping(source.get("risk_plan"))
    boundary = _mapping(source.get("oanda_demo_boundary"))
    return {
        "packet_id": PACKET_ID,
        "broker_name": "OANDA",
        "mode": _text(boundary.get("mode")),
        "instrument": _text(order.get("instrument")),
        "side": _text(order.get("side")),
        "order_type": _text(order.get("order_type")),
        "units": _number_or_original(order.get("units")),
        "stop_loss_present": _bool(order.get("stop_loss_present")),
        "take_profit_present": _bool(order.get("take_profit_present")),
        "stop_loss_value_or_distance_present": _bool(
            order.get("stop_loss_value_or_distance_present")
        ),
        "take_profit_value_or_distance_present": _bool(
            order.get("take_profit_value_or_distance_present")
        ),
        "setup_id": _text(order.get("setup_id")),
        "evidence_id": _text(order.get("evidence_id")),
        "one_order_only": _bool(risk.get("one_order_only")),
        "owner_approval_required": True,
        "owner_approved": True,
        "demo_only": True,
        "actual_live_execution_authorized": False,
        "money_movement_allowed": False,
        "post_trade_review_required": True,
    }


def _redacted_summaries() -> dict[str, dict[str, Any]]:
    summary = {
        "present": False,
        "ready": False,
        "redacted": True,
        "blockers": ["redacted_until_safe_metadata_provided"],
    }
    return {
        "owner_approval_summary": dict(summary),
        "protected_demo_attempt_summary": dict(summary),
        "runtime_boundary_summary": dict(summary),
        "existing_runtime_interface_summary": dict(summary),
        "order_candidate_summary": {
            "present": False,
            "candidate_metadata_ready": False,
            "stop_take_metadata_ready": False,
            "redacted": True,
            "candidate_blockers": ["redacted_until_safe_metadata_provided"],
            "stop_take_blockers": ["redacted_until_safe_metadata_provided"],
            "duplicate_candidate": False,
        },
        "risk_plan_summary": {
            "present": False,
            "risk_limits_ready": False,
            "one_order_limit_ready": False,
            "redacted": True,
            "risk_limit_blockers": ["redacted_until_safe_metadata_provided"],
            "one_order_limit_blockers": [
                "redacted_until_safe_metadata_provided"
            ],
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
        },
        "oanda_demo_boundary_summary": dict(summary),
        "post_trade_review_summary": dict(summary),
    }


def _owner_action_queue(
    status: str, blockers: Sequence[str], next_best_packet: str
) -> list[dict[str, Any]]:
    actions = (
        "REVIEW_OWNER_APPROVAL_SCOPE",
        "REVIEW_RUNTIME_CREDENTIAL_SESSION",
        "REVIEW_EXISTING_RUNTIME_INTERFACE",
        "REVIEW_SANITIZED_EXECUTION_INTENT",
        "REVIEW_POST_TRADE_REVIEW_REQUIREMENT",
        "REVIEW_NEXT_PACKET",
    )
    return [
        {
            "action_id": action,
            "owner_decision_required": True,
            "blocked_by": list(blockers),
            "current_status": status,
            "next_best_packet": next_best_packet
            if action == "REVIEW_NEXT_PACKET"
            else None,
            **{field: False for field in HARD_FALSE_FIELDS},
        }
        for action in actions
    ]


def _next_best_packet(status: str) -> str:
    if status in {
        DEMO_ONE_ORDER_EXECUTION_READY_FOR_RUNTIME,
        DEMO_ONE_ORDER_EXECUTION_PREPARED_NOT_SENT,
    }:
        return NEXT_PACKET_RUNTIME_RECEIPT_AND_POST_TRADE_REVIEW
    return NEXT_PACKET_CURRENT


def _safe_manual_next_action(status: str) -> str:
    if status == DEMO_ONE_ORDER_EXECUTION_READY_FOR_RUNTIME:
        return (
            "Owner may route the sanitized intent to a separately approved "
            "OANDA demo runtime receipt and post-trade review packet."
        )
    if status == DEMO_ONE_ORDER_EXECUTION_PREPARED_NOT_SENT:
        return (
            "Review the prepared sanitized intent; no runtime call has been made."
        )
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys or values and rerun with sanitized metadata."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove banking, withdrawal, transfer, card, rail, sweep, or money-movement fields."
    if status == BLOCKED_BY_OWNER_APPROVAL:
        return "Repair the exact Anthony approval metadata for this packet."
    if status == BLOCKED_BY_EXISTING_RUNTIME_EXECUTION_INTERFACE_MISSING:
        return "Identify an existing repo-approved OANDA demo one-order runtime interface."
    if status == BLOCKED_BY_RUNTIME_CREDENTIAL_SESSION_REQUIRED:
        return "Refresh runtime-only one-order demo credential-session metadata outside repo and chat."
    if status == BLOCKED_BY_ORDER_CANDIDATE:
        return "Provide a complete sanitized one-order candidate."
    if status == BLOCKED_BY_RISK_GATES:
        return "Repair stop loss, take profit, risk percentage, or daily-loss metadata."
    if status == BLOCKED_BY_OANDA_DEMO_MODE:
        return "Repair OANDA demo boundary metadata and keep live and money flags false."
    if status == BLOCKED_BY_ONE_ORDER_LIMIT:
        return "Restore one-order-only controls and remove duplicate-candidate indicators."
    if status == BLOCKED_BY_KILL_SWITCH:
        return "Deactivate the kill-switch block before any demo runtime review."
    if status == BLOCKED_BY_DAILY_LOSS_STOP:
        return "Clear daily-loss-stop metadata before any demo runtime review."
    if status == BLOCKED_BY_POST_TRADE_REVIEW:
        return "Require sanitized receipt, daily PnL record, owner review, and no second trade before review."
    return "Provide complete sanitized owner-approved demo one-order metadata."


def _safety() -> dict[str, Any]:
    safety: dict[str, Any] = {field: False for field in HARD_FALSE_FIELDS}
    safety.update(
        {
            "read_only": True,
            "metadata_only": True,
            "owner_approval_required": True,
            "demo_only": True,
            "live_trading_allowed": False,
            "real_money_allowed": False,
            "money_movement_allowed": False,
            "credential_or_account_value_echoed": False,
            "runtime_call_made": False,
            "order_sent_to_broker": False,
        }
    )
    return safety


def _sensitive_data_blockers(value: Any) -> tuple[str, ...]:
    blockers: list[str] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, Mapping):
            for raw_key, child in node.items():
                key_text = str(raw_key).lower().replace("-", "_")
                child_path = f"{path}.field"
                if _safe_sensitive_key(key_text, child):
                    if (
                        key_text in SENSITIVE_SIGNAL_FALSE_KEYS
                        and child is not False
                    ):
                        blockers.append(f"sensitive_signal_at_{child_path}")
                    continue
                if any(part in key_text for part in SENSITIVE_KEY_PARTS):
                    blockers.append(f"sensitive_key_at_{child_path}")
                    continue
                walk(child, child_path)
            return
        if isinstance(node, Sequence) and not isinstance(
            node, (str, bytes, bytearray)
        ):
            for child in node:
                walk(child, f"{path}.item")
            return
        if isinstance(node, str) and _secret_like_value(node):
            blockers.append(f"secret_like_value_at_{path}")
            return
        if isinstance(node, int) and not isinstance(node, bool):
            if _has_long_digit_run(str(node)):
                blockers.append(f"long_digit_run_at_{path}")

    walk(value, "payload")
    return tuple(_unique(blockers))


def _safe_sensitive_key(key_text: str, value: Any) -> bool:
    return key_text in SAFE_SENSITIVE_METADATA_KEYS and isinstance(value, bool)


def _secret_like_value(value: str) -> bool:
    lowered = value.lower()
    markers = (
        "sk-",
        "bearer",
        "api key",
        "token value",
        "broker token",
        "access token",
        "private key",
        "password",
        "secret",
        "-----begin",
    )
    return any(marker in lowered for marker in markers) or _has_long_digit_run(
        lowered
    )


def _banking_focus_blockers(value: Any) -> tuple[str, ...]:
    blockers: list[str] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, Mapping):
            for raw_key, child in node.items():
                key_text = str(raw_key).lower().replace("-", "_")
                child_path = f"{path}.field"
                if key_text in SAFE_BANKING_FALSE_KEYS and child is False:
                    continue
                if key_text in SAFE_BANKING_TRUE_KEYS and child is True:
                    continue
                if any(part in key_text for part in BANKING_KEY_PARTS):
                    blockers.append(f"banking_focus_key_at_{child_path}")
                    continue
                walk(child, child_path)
            return
        if isinstance(node, Sequence) and not isinstance(
            node, (str, bytes, bytearray)
        ):
            for child in node:
                walk(child, f"{path}.item")

    walk(value, "payload")
    return tuple(_unique(blockers))


def _false_gate_blockers(checks: Mapping[str, bool]) -> list[str]:
    return [key for key, value in checks.items() if value is False]


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _text(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip().upper()
    return None


def _decimal(value: Any) -> Decimal | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _number_or_none(value: Decimal | None) -> int | float | None:
    if value is None:
        return None
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def _number_or_original(value: Any) -> int | float | str | None:
    number = _decimal(value)
    if number is not None:
        return _number_or_none(number)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _has_long_digit_run(value: str) -> bool:
    run = 0
    for character in value:
        if character.isdigit():
            run += 1
            if run >= 9:
                return True
        else:
            run = 0
    return False


def _unique(values: Sequence[Any]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        item = str(value)
        if item and item not in seen:
            seen.add(item)
            output.append(item)
    return output
