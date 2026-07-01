"""Metadata-only protected demo daily profit attempt readiness evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any


SCHEMA = "AIOS_FOREX_PROTECTED_DEMO_DAILY_PROFIT_ATTEMPT_V1"
MODE = "READ_ONLY_METADATA_ONLY_PROTECTED_DEMO_DAILY_PROFIT_ATTEMPT"

PROTECTED_DEMO_DAILY_PROFIT_ATTEMPT_READY = (
    "PROTECTED_DEMO_DAILY_PROFIT_ATTEMPT_READY"
)
READY_FOR_OWNER_APPROVED_DEMO_ONE_ORDER_PACKET = (
    "READY_FOR_OWNER_APPROVED_DEMO_ONE_ORDER_PACKET"
)
READY_FOR_LIVE_MICRO_EXCEPTION_REVIEW_AFTER_DEMO_EVIDENCE = (
    "READY_FOR_LIVE_MICRO_EXCEPTION_REVIEW_AFTER_DEMO_EVIDENCE"
)
CONTINUE_PROFIT_EVIDENCE_CAPTURE = "CONTINUE_PROFIT_EVIDENCE_CAPTURE"
BLOCKED_BY_DAILY_PROFIT_EVIDENCE_REQUIRED = (
    "BLOCKED_BY_DAILY_PROFIT_EVIDENCE_REQUIRED"
)
BLOCKED_BY_ORDER_CANDIDATE = "BLOCKED_BY_ORDER_CANDIDATE"
BLOCKED_BY_RISK_LIMITS = "BLOCKED_BY_RISK_LIMITS"
BLOCKED_BY_EXECUTION_WINDOW = "BLOCKED_BY_EXECUTION_WINDOW"
BLOCKED_BY_POST_TRADE_REVIEW = "BLOCKED_BY_POST_TRADE_REVIEW"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

DAILY_PROFIT_READY_STATUSES = frozenset(
    {
        "DAILY_PROFIT_EXECUTION_EVIDENCE_READY",
        "READY_FOR_PROTECTED_DEMO_PROFIT_ATTEMPT",
    }
)

NEXT_PACKET_CURRENT = SCHEMA
NEXT_PACKET_OWNER_APPROVED_DEMO = (
    "AIOS_FOREX_OWNER_APPROVED_DEMO_ONE_ORDER_PROFIT_ATTEMPT_EXECUTION_V1"
)
NEXT_PACKET_LIVE_MICRO_REVIEW = (
    "AIOS_FOREX_LIVE_MICRO_EXCEPTION_REVIEW_AFTER_DEMO_PROFIT_EVIDENCE_V1"
)

BANKING_FREEZE_STATEMENT = (
    "Banking, withdrawal, transfer, card, rail, ACH, wire, sweep, "
    "bucket purge, deposit, and money-movement work remains frozen."
)

HARD_FALSE_FIELDS = (
    "live_trade_executed",
    "demo_trade_executed",
    "money_moved",
    "bank_access_used",
    "broker_api_called",
    "credential_read",
    "credential_stored",
    "api_key_stored",
    "master_password_used",
    "vault_password_used",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "dashboard_runtime_created",
    "actual_demo_execution_authorized",
    "actual_live_execution_authorized",
    "banking_work_built",
    "withdrawal_work_built",
    "transfer_work_built",
)

TOP_LEVEL_SECTIONS = (
    "daily_profit_evidence_result",
    "order_candidate",
    "risk_plan",
    "execution_window",
    "protected_demo_policy",
    "post_attempt_review",
)

ORDER_REQUIRED_FIELDS = (
    "instrument",
    "side",
    "order_type",
    "units",
    "setup_id",
    "evidence_id",
    "expected_r_multiple",
    "minimum_reward_risk_ratio",
    "spread_within_limit",
    "slippage_within_limit",
    "session_allowed",
    "news_blackout_clear",
    "duplicate_candidate",
)

RISK_REQUIRED_FIELDS = (
    "max_risk_per_trade_pct",
    "max_daily_loss_pct",
    "stop_loss_present",
    "take_profit_present",
    "one_order_only",
    "max_order_count_this_packet",
    "kill_switch_active",
    "daily_loss_stop_active",
    "next_order_blocked_until_review",
)

EXECUTION_WINDOW_REQUIRED_FIELDS = (
    "execution_window_defined",
    "pre_trade_check_ready",
    "owner_can_cancel",
    "owner_approval_required",
    "credential_session_bridge_ready",
    "protected_runtime_gate_ready",
    "oanda_demo_mode_declared",
)

PROTECTED_POLICY_REQUIRED_FIELDS = (
    "demo_only",
    "real_broker_call_allowed",
    "live_trading_allowed",
    "money_movement_allowed",
    "credential_read",
    "credential_stored",
    "broker_api_called",
    "dry_run_or_metadata_only",
    "actual_demo_execution_authorized",
)

POST_REVIEW_REQUIRED_FIELDS = (
    "post_trade_review_required",
    "daily_pnl_record_required",
    "sanitized_receipt_required",
    "no_second_trade_without_review",
    "owner_review_required",
)

SANITIZED_PACKET_FIELDS = (
    "instrument",
    "side",
    "order_type",
    "units",
    "setup_id",
    "evidence_id",
    "expected_r_multiple",
    "minimum_reward_risk_ratio",
    "max_risk_per_trade_pct",
    "max_daily_loss_pct",
    "stop_loss_present",
    "take_profit_present",
    "one_order_only",
    "demo_only",
    "owner_approval_required",
    "post_trade_review_required",
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

SAFE_SENSITIVE_NAMED_METADATA_KEYS = frozenset(
    {
        "api_key_stored",
        "broker_api_called",
        "credential_read",
        "credential_stored",
        "master_password_used",
        "vault_password_used",
        "account_id_provided",
        "no_stored_account_id",
        "no_stored_api_key",
        "no_master_password",
        "no_vault_password",
        "no_raw_token",
    }
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

SAFE_BANKING_NAMED_METADATA_KEYS = frozenset(
    {
        "money_movement_allowed",
        "bank_access_used",
        "banking_work_built",
        "withdrawal_work_built",
        "transfer_work_built",
    }
)


def evaluate_forex_protected_demo_daily_profit_attempt_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Evaluate one-order protected demo readiness without side effects."""

    source = payload if isinstance(payload, Mapping) else {}
    sensitive_data_blockers = _sensitive_data_blockers(source)
    banking_focus_blockers = _banking_focus_blockers(source)

    if sensitive_data_blockers:
        return _build_result(
            source=source,
            protected_demo_attempt_status=BLOCKED_BY_SENSITIVE_DATA,
            blockers=sensitive_data_blockers,
            sensitive_data_detected=True,
            banking_focus_detected=False,
            redacted=True,
        )
    if banking_focus_blockers:
        return _build_result(
            source=source,
            protected_demo_attempt_status=BLOCKED_BY_BANKING_FOCUS,
            blockers=banking_focus_blockers,
            sensitive_data_detected=False,
            banking_focus_detected=True,
            redacted=True,
        )
    if not source:
        return _build_result(
            source=source,
            protected_demo_attempt_status=INCOMPLETE_INPUTS,
            blockers=tuple(f"missing_{section}" for section in TOP_LEVEL_SECTIONS),
            sensitive_data_detected=False,
            banking_focus_detected=False,
            redacted=False,
        )

    summaries = _summaries(source)
    protected_demo_attempt_status, blockers = _protected_demo_attempt_status(
        source=source,
        daily_profit_evidence_summary=summaries["daily_profit_evidence_summary"],
        order_candidate_summary=summaries["order_candidate_summary"],
        risk_plan_summary=summaries["risk_plan_summary"],
        execution_window_summary=summaries["execution_window_summary"],
        protected_demo_policy_summary=summaries["protected_demo_policy_summary"],
        post_attempt_review_summary=summaries["post_attempt_review_summary"],
    )
    return _build_result(
        source=source,
        protected_demo_attempt_status=protected_demo_attempt_status,
        blockers=tuple(blockers),
        sensitive_data_detected=False,
        banking_focus_detected=False,
        redacted=False,
        summaries=summaries,
    )


def _protected_demo_attempt_status(
    *,
    source: Mapping[str, Any],
    daily_profit_evidence_summary: dict[str, Any],
    order_candidate_summary: dict[str, Any],
    risk_plan_summary: dict[str, Any],
    execution_window_summary: dict[str, Any],
    protected_demo_policy_summary: dict[str, Any],
    post_attempt_review_summary: dict[str, Any],
) -> tuple[str, list[str]]:
    if daily_profit_evidence_summary["present"] is False:
        return BLOCKED_BY_DAILY_PROFIT_EVIDENCE_REQUIRED, [
            "missing_daily_profit_evidence_result"
        ]
    if daily_profit_evidence_summary["daily_profit_ready"] is False:
        return CONTINUE_PROFIT_EVIDENCE_CAPTURE, _unique(
            daily_profit_evidence_summary["daily_profit_evidence_blockers"]
        )
    if order_candidate_summary["order_candidate_ready"] is False:
        return BLOCKED_BY_ORDER_CANDIDATE, _unique(
            order_candidate_summary["order_candidate_blockers"]
        )
    if risk_plan_summary["risk_plan_ready"] is False:
        return BLOCKED_BY_RISK_LIMITS, _unique(
            risk_plan_summary["risk_plan_blockers"]
        )
    if execution_window_summary["execution_window_ready"] is False:
        return BLOCKED_BY_EXECUTION_WINDOW, _unique(
            execution_window_summary["execution_window_blockers"]
        )
    if protected_demo_policy_summary["protected_demo_policy_ready"] is False:
        return BLOCKED_BY_EXECUTION_WINDOW, _unique(
            protected_demo_policy_summary["protected_demo_policy_blockers"]
        )
    if post_attempt_review_summary["post_attempt_review_ready"] is False:
        return BLOCKED_BY_POST_TRADE_REVIEW, _unique(
            post_attempt_review_summary["post_attempt_review_blockers"]
        )
    if _bool(source.get("demo_evidence_complete")) or _bool(
        source.get("live_micro_exception_review_after_demo_evidence_requested")
    ):
        return READY_FOR_LIVE_MICRO_EXCEPTION_REVIEW_AFTER_DEMO_EVIDENCE, []
    if _bool(source.get("owner_approved_demo_one_order_packet_requested")) or _bool(
        source.get("owner_requested_demo_packet")
    ):
        return READY_FOR_OWNER_APPROVED_DEMO_ONE_ORDER_PACKET, []
    return PROTECTED_DEMO_DAILY_PROFIT_ATTEMPT_READY, []


def _summaries(source: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    daily_profit_evidence = source.get("daily_profit_evidence_result")
    order_candidate = source.get("order_candidate")
    risk_plan = source.get("risk_plan")
    execution_window = source.get("execution_window")
    protected_demo_policy = source.get("protected_demo_policy")
    post_attempt_review = source.get("post_attempt_review")
    return {
        "daily_profit_evidence_summary": _daily_profit_evidence_summary(
            daily_profit_evidence
        ),
        "order_candidate_summary": _order_candidate_summary(order_candidate),
        "risk_plan_summary": _risk_plan_summary(risk_plan),
        "execution_window_summary": _execution_window_summary(execution_window),
        "protected_demo_policy_summary": _protected_demo_policy_summary(
            protected_demo_policy
        ),
        "post_attempt_review_summary": _post_attempt_review_summary(
            post_attempt_review
        ),
    }


def _daily_profit_evidence_summary(value: Any) -> dict[str, Any]:
    source = value if isinstance(value, Mapping) else {}
    present = bool(source)
    status = source.get("daily_profit_status")
    hard_false_inputs_clear = all(
        source.get(field) is False
        for field in (
            "broker_api_called",
            "credential_read",
            "live_trade_executed",
            "demo_trade_executed",
            "money_moved",
        )
    )
    gates = {
        "present": present,
        "daily_profit_status_allowed": status in DAILY_PROFIT_READY_STATUSES,
        "daily_profit_ready": _bool(source.get("daily_profit_ready")),
        "daily_profit_hard_false_inputs_clear": hard_false_inputs_clear,
    }
    blockers = [key for key, ready in gates.items() if ready is False]
    return {
        **gates,
        "daily_profit_status": _safe_status_label(status),
        "broker_api_called": False,
        "credential_read": False,
        "live_trade_executed": False,
        "demo_trade_executed": False,
        "money_moved": False,
        "daily_profit_evidence_blockers": blockers,
    }


def _order_candidate_summary(value: Any) -> dict[str, Any]:
    source = value if isinstance(value, Mapping) else {}
    missing = _missing_fields(source, ORDER_REQUIRED_FIELDS)
    duplicate_candidate = source.get("duplicate_candidate") is True
    expected_r_multiple = _decimal(source.get("expected_r_multiple"))
    minimum_reward_risk_ratio = _decimal(source.get("minimum_reward_risk_ratio"))
    reward_risk_gate = (
        expected_r_multiple is not None
        and minimum_reward_risk_ratio is not None
        and expected_r_multiple >= minimum_reward_risk_ratio
    )
    gates = {
        "required_fields_present": not missing,
        "spread_within_limit": _bool(source.get("spread_within_limit")),
        "slippage_within_limit": _bool(source.get("slippage_within_limit")),
        "session_allowed": _bool(source.get("session_allowed")),
        "news_blackout_clear": _bool(source.get("news_blackout_clear")),
        "duplicate_candidate_clear": duplicate_candidate is False,
        "reward_risk_gate": reward_risk_gate,
    }
    blockers = [key for key, ready in gates.items() if ready is False]
    blockers.extend(f"missing_{field}" for field in missing)
    return {
        "instrument": _string_or_none(source.get("instrument")),
        "side": _string_or_none(source.get("side")),
        "order_type": _string_or_none(source.get("order_type")),
        "units": _number_or_original(source.get("units")),
        "setup_id": _string_or_none(source.get("setup_id")),
        "evidence_id": _string_or_none(source.get("evidence_id")),
        "expected_r_multiple": _number_or_none(expected_r_multiple),
        "minimum_reward_risk_ratio": _number_or_none(minimum_reward_risk_ratio),
        "duplicate_candidate": duplicate_candidate,
        **gates,
        "order_candidate_ready": all(gates.values()),
        "order_candidate_blockers": _unique(blockers),
    }


def _risk_plan_summary(value: Any) -> dict[str, Any]:
    source = value if isinstance(value, Mapping) else {}
    missing = _missing_fields(source, RISK_REQUIRED_FIELDS)
    max_risk_per_trade_pct = _decimal(source.get("max_risk_per_trade_pct"))
    max_daily_loss_pct = _decimal(source.get("max_daily_loss_pct"))
    max_order_count = _decimal(source.get("max_order_count_this_packet"))
    gates = {
        "required_fields_present": not missing,
        "risk_per_trade_gate": max_risk_per_trade_pct is not None
        and max_risk_per_trade_pct <= Decimal("0.01"),
        "daily_loss_gate": max_daily_loss_pct is not None
        and max_daily_loss_pct <= Decimal("0.03"),
        "stop_loss_present": _bool(source.get("stop_loss_present")),
        "take_profit_present": _bool(source.get("take_profit_present")),
        "one_order_only": _bool(source.get("one_order_only")),
        "max_order_count_gate": max_order_count == Decimal("1"),
        "kill_switch_inactive": source.get("kill_switch_active") is False,
        "daily_loss_stop_inactive": source.get("daily_loss_stop_active") is False,
        "next_order_blocked_until_review": _bool(
            source.get("next_order_blocked_until_review")
        ),
    }
    blockers = [key for key, ready in gates.items() if ready is False]
    blockers.extend(f"missing_{field}" for field in missing)
    return {
        "max_risk_per_trade_pct": _number_or_none(max_risk_per_trade_pct),
        "max_daily_loss_pct": _number_or_none(max_daily_loss_pct),
        "max_order_count_this_packet": _number_or_none(max_order_count),
        "kill_switch_active": source.get("kill_switch_active") is True,
        "daily_loss_stop_active": source.get("daily_loss_stop_active") is True,
        **gates,
        "risk_plan_ready": all(gates.values()),
        "risk_plan_blockers": _unique(blockers),
    }


def _execution_window_summary(value: Any) -> dict[str, Any]:
    source = value if isinstance(value, Mapping) else {}
    missing = _missing_fields(source, EXECUTION_WINDOW_REQUIRED_FIELDS)
    gates = {
        "required_fields_present": not missing,
        "execution_window_defined": _bool(source.get("execution_window_defined")),
        "pre_trade_check_ready": _bool(source.get("pre_trade_check_ready")),
        "owner_can_cancel": _bool(source.get("owner_can_cancel")),
        "owner_approval_required": _bool(source.get("owner_approval_required")),
        "credential_session_bridge_ready": _bool(
            source.get("credential_session_bridge_ready")
        ),
        "protected_runtime_gate_ready": _bool(
            source.get("protected_runtime_gate_ready")
        ),
        "oanda_demo_mode_declared": _bool(
            source.get("oanda_demo_mode_declared")
        ),
    }
    blockers = [key for key, ready in gates.items() if ready is False]
    blockers.extend(f"missing_{field}" for field in missing)
    return {
        **gates,
        "execution_window_ready": all(gates.values()),
        "execution_window_blockers": _unique(blockers),
    }


def _protected_demo_policy_summary(value: Any) -> dict[str, Any]:
    source = value if isinstance(value, Mapping) else {}
    missing = _missing_fields(source, PROTECTED_POLICY_REQUIRED_FIELDS)
    gates = {
        "required_fields_present": not missing,
        "demo_only": _bool(source.get("demo_only")),
        "real_broker_call_blocked": source.get("real_broker_call_allowed")
        is False,
        "live_trading_blocked": source.get("live_trading_allowed") is False,
        "money_movement_blocked": source.get("money_movement_allowed") is False,
        "credential_read_blocked": source.get("credential_read") is False,
        "credential_storage_blocked": source.get("credential_stored") is False,
        "broker_api_call_blocked": source.get("broker_api_called") is False,
        "dry_run_or_metadata_only": _bool(
            source.get("dry_run_or_metadata_only")
        ),
        "actual_demo_execution_blocked": source.get(
            "actual_demo_execution_authorized"
        )
        is False,
    }
    blockers = [key for key, ready in gates.items() if ready is False]
    blockers.extend(f"missing_{field}" for field in missing)
    return {
        **gates,
        "protected_demo_policy_ready": all(gates.values()),
        "protected_demo_policy_blockers": _unique(blockers),
    }


def _post_attempt_review_summary(value: Any) -> dict[str, Any]:
    source = value if isinstance(value, Mapping) else {}
    missing = _missing_fields(source, POST_REVIEW_REQUIRED_FIELDS)
    gates = {
        "required_fields_present": not missing,
        "post_trade_review_required": _bool(
            source.get("post_trade_review_required")
        ),
        "daily_pnl_record_required": _bool(
            source.get("daily_pnl_record_required")
        ),
        "sanitized_receipt_required": _bool(
            source.get("sanitized_receipt_required")
        ),
        "no_second_trade_without_review": _bool(
            source.get("no_second_trade_without_review")
        ),
        "owner_review_required": _bool(source.get("owner_review_required")),
    }
    blockers = [key for key, ready in gates.items() if ready is False]
    blockers.extend(f"missing_{field}" for field in missing)
    return {
        **gates,
        "post_attempt_review_ready": all(gates.values()),
        "post_attempt_review_blockers": _unique(blockers),
    }


def _build_result(
    *,
    source: Mapping[str, Any],
    protected_demo_attempt_status: str,
    blockers: Sequence[str],
    sensitive_data_detected: bool,
    banking_focus_detected: bool,
    redacted: bool,
    summaries: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if summaries is None:
        summaries = _redacted_summaries() if redacted else _summaries(source)
    protected_demo_attempt_ready = protected_demo_attempt_status in {
        PROTECTED_DEMO_DAILY_PROFIT_ATTEMPT_READY,
        READY_FOR_OWNER_APPROVED_DEMO_ONE_ORDER_PACKET,
        READY_FOR_LIVE_MICRO_EXCEPTION_REVIEW_AFTER_DEMO_EVIDENCE,
    }
    next_best_packet = _next_best_packet(protected_demo_attempt_status)
    sanitized_packet = (
        {}
        if redacted
        else _sanitized_demo_attempt_packet(
            source=source,
            protected_demo_attempt_ready=protected_demo_attempt_ready,
        )
    )
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "mode": MODE,
        "protected_demo_attempt_status": protected_demo_attempt_status,
        "protected_demo_attempt_ready": protected_demo_attempt_ready,
        "owner_decision_required": True,
        "read_only": True,
        "metadata_only": True,
        "daily_profit_evidence_summary": summaries[
            "daily_profit_evidence_summary"
        ],
        "order_candidate_summary": summaries["order_candidate_summary"],
        "risk_plan_summary": summaries["risk_plan_summary"],
        "execution_window_summary": summaries["execution_window_summary"],
        "protected_demo_policy_summary": summaries[
            "protected_demo_policy_summary"
        ],
        "post_attempt_review_summary": summaries["post_attempt_review_summary"],
        "banking_freeze_summary": _banking_freeze_summary(
            protected_demo_attempt_status=protected_demo_attempt_status,
            banking_focus_detected=banking_focus_detected,
        ),
        "sanitized_demo_attempt_packet": sanitized_packet,
        "owner_action_queue": _owner_action_queue(
            protected_demo_attempt_status=protected_demo_attempt_status,
            blockers=blockers,
            next_best_packet=next_best_packet,
        ),
        "blockers": list(blockers),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(
            protected_demo_attempt_status
        ),
        "audit_record": _audit_record(
            protected_demo_attempt_status=protected_demo_attempt_status,
            protected_demo_attempt_ready=protected_demo_attempt_ready,
            blocker_count=len(blockers),
            next_best_packet=next_best_packet,
            sensitive_data_detected=sensitive_data_detected,
            banking_focus_detected=banking_focus_detected,
        ),
        "safety": _safety(),
    }
    result.update({field: False for field in HARD_FALSE_FIELDS})
    return result


def _sanitized_demo_attempt_packet(
    *,
    source: Mapping[str, Any],
    protected_demo_attempt_ready: bool,
) -> dict[str, Any]:
    if not protected_demo_attempt_ready:
        return {field: None for field in SANITIZED_PACKET_FIELDS}
    order_candidate = source.get("order_candidate")
    risk_plan = source.get("risk_plan")
    execution_window = source.get("execution_window")
    protected_demo_policy = source.get("protected_demo_policy")
    post_attempt_review = source.get("post_attempt_review")
    order = order_candidate if isinstance(order_candidate, Mapping) else {}
    risk = risk_plan if isinstance(risk_plan, Mapping) else {}
    execution = execution_window if isinstance(execution_window, Mapping) else {}
    policy = (
        protected_demo_policy if isinstance(protected_demo_policy, Mapping) else {}
    )
    post = post_attempt_review if isinstance(post_attempt_review, Mapping) else {}
    return {
        "instrument": _string_or_none(order.get("instrument")),
        "side": _string_or_none(order.get("side")),
        "order_type": _string_or_none(order.get("order_type")),
        "units": _number_or_original(order.get("units")),
        "setup_id": _string_or_none(order.get("setup_id")),
        "evidence_id": _string_or_none(order.get("evidence_id")),
        "expected_r_multiple": _number_or_none(
            _decimal(order.get("expected_r_multiple"))
        ),
        "minimum_reward_risk_ratio": _number_or_none(
            _decimal(order.get("minimum_reward_risk_ratio"))
        ),
        "max_risk_per_trade_pct": _number_or_none(
            _decimal(risk.get("max_risk_per_trade_pct"))
        ),
        "max_daily_loss_pct": _number_or_none(
            _decimal(risk.get("max_daily_loss_pct"))
        ),
        "stop_loss_present": _bool(risk.get("stop_loss_present")),
        "take_profit_present": _bool(risk.get("take_profit_present")),
        "one_order_only": _bool(risk.get("one_order_only")),
        "demo_only": _bool(policy.get("demo_only")),
        "owner_approval_required": _bool(
            execution.get("owner_approval_required")
        ),
        "post_trade_review_required": _bool(
            post.get("post_trade_review_required")
        ),
        "actual_demo_execution_authorized": False,
    }


def _redacted_summaries() -> dict[str, dict[str, Any]]:
    return {
        "daily_profit_evidence_summary": {
            "redacted": True,
            "present": False,
            "daily_profit_ready": False,
            "daily_profit_evidence_blockers": [
                "redacted_until_safe_metadata_provided"
            ],
            "broker_api_called": False,
            "credential_read": False,
            "live_trade_executed": False,
            "demo_trade_executed": False,
            "money_moved": False,
        },
        "order_candidate_summary": {
            "redacted": True,
            "order_candidate_ready": False,
            "order_candidate_blockers": [
                "redacted_until_safe_metadata_provided"
            ],
        },
        "risk_plan_summary": {
            "redacted": True,
            "risk_plan_ready": False,
            "risk_plan_blockers": ["redacted_until_safe_metadata_provided"],
        },
        "execution_window_summary": {
            "redacted": True,
            "execution_window_ready": False,
            "execution_window_blockers": [
                "redacted_until_safe_metadata_provided"
            ],
        },
        "protected_demo_policy_summary": {
            "redacted": True,
            "protected_demo_policy_ready": False,
            "protected_demo_policy_blockers": [
                "redacted_until_safe_metadata_provided"
            ],
        },
        "post_attempt_review_summary": {
            "redacted": True,
            "post_attempt_review_ready": False,
            "post_attempt_review_blockers": [
                "redacted_until_safe_metadata_provided"
            ],
        },
    }


def _banking_freeze_summary(
    *, protected_demo_attempt_status: str, banking_focus_detected: bool
) -> dict[str, Any]:
    return {
        "status": protected_demo_attempt_status,
        "banking_focus_detected": banking_focus_detected,
        "banking_work_allowed": False,
        "withdrawal_work_allowed": False,
        "transfer_work_allowed": False,
        "money_movement_allowed": False,
        "banking_work_built": False,
        "withdrawal_work_built": False,
        "transfer_work_built": False,
        "next_best_packet_stays_current_when_blocked": (
            protected_demo_attempt_status
            in {
                BLOCKED_BY_BANKING_FOCUS,
                BLOCKED_BY_SENSITIVE_DATA,
                BLOCKED_BY_DAILY_PROFIT_EVIDENCE_REQUIRED,
                BLOCKED_BY_ORDER_CANDIDATE,
                BLOCKED_BY_RISK_LIMITS,
                BLOCKED_BY_EXECUTION_WINDOW,
                BLOCKED_BY_POST_TRADE_REVIEW,
                CONTINUE_PROFIT_EVIDENCE_CAPTURE,
                INCOMPLETE_INPUTS,
            }
        ),
        "statement": BANKING_FREEZE_STATEMENT,
    }


def _owner_action_queue(
    *,
    protected_demo_attempt_status: str,
    blockers: Sequence[str],
    next_best_packet: str,
) -> list[dict[str, Any]]:
    if protected_demo_attempt_status == BLOCKED_BY_BANKING_FOCUS:
        return [
            {
                "action": "KEEP_BANKING_WITHDRAWAL_TRANSFER_FROZEN",
                "required": True,
                "raw_values_echoed": False,
            },
            {
                "action": "RETURN_TO_PROTECTED_DEMO_ATTEMPT_READINESS",
                "required": True,
                "next_best_packet": next_best_packet,
            },
        ]
    if protected_demo_attempt_status == BLOCKED_BY_SENSITIVE_DATA:
        return [
            {
                "action": "REMOVE_SENSITIVE_DATA_FROM_METADATA",
                "required": True,
                "raw_values_echoed": False,
            }
        ]
    if protected_demo_attempt_status in {
        PROTECTED_DEMO_DAILY_PROFIT_ATTEMPT_READY,
        READY_FOR_OWNER_APPROVED_DEMO_ONE_ORDER_PACKET,
    }:
        return [
            {
                "action": "OWNER_REVIEW_SANITIZED_DEMO_ATTEMPT_PACKET",
                "required": True,
                "next_best_packet": next_best_packet,
            },
            {
                "action": "APPROVE_OR_REJECT_SEPARATE_DEMO_EXECUTION_PACKET",
                "required": True,
                "no_trade_authorized_by_this_result": True,
            },
        ]
    if (
        protected_demo_attempt_status
        == READY_FOR_LIVE_MICRO_EXCEPTION_REVIEW_AFTER_DEMO_EVIDENCE
    ):
        return [
            {
                "action": "OWNER_REVIEW_DEMO_EVIDENCE_BEFORE_LIVE_MICRO_PACKET",
                "required": True,
                "next_best_packet": next_best_packet,
                "no_live_trade_authorized_by_this_result": True,
            }
        ]
    return [
        {
            "action": "REPAIR_BLOCKERS",
            "required": True,
            "blocker_count": len(blockers),
            "next_best_packet": next_best_packet,
        }
    ]


def _audit_record(
    *,
    protected_demo_attempt_status: str,
    protected_demo_attempt_ready: bool,
    blocker_count: int,
    next_best_packet: str,
    sensitive_data_detected: bool,
    banking_focus_detected: bool,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "protected_demo_attempt_status": protected_demo_attempt_status,
        "protected_demo_attempt_ready": protected_demo_attempt_ready,
        "blocker_count": blocker_count,
        "sensitive_data_detected": sensitive_data_detected,
        "sensitive_values_echoed": False,
        "banking_focus_detected": banking_focus_detected,
        "read_only": True,
        "metadata_only": True,
        "next_best_packet": next_best_packet,
    }


def _safety() -> dict[str, Any]:
    safety: dict[str, Any] = {field: False for field in HARD_FALSE_FIELDS}
    safety.update(
        {
            "no_guaranteed_profit_claim": True,
            "no_profit_guarantee": True,
            "broker_execution_authorized": False,
            "demo_order_authorized": False,
            "live_micro_exception_authorized": False,
            "credential_or_account_value_echoed": False,
            "metadata_only": True,
            "read_only": True,
        }
    )
    return safety


def _next_best_packet(protected_demo_attempt_status: str) -> str:
    if protected_demo_attempt_status in {
        PROTECTED_DEMO_DAILY_PROFIT_ATTEMPT_READY,
        READY_FOR_OWNER_APPROVED_DEMO_ONE_ORDER_PACKET,
    }:
        return NEXT_PACKET_OWNER_APPROVED_DEMO
    if (
        protected_demo_attempt_status
        == READY_FOR_LIVE_MICRO_EXCEPTION_REVIEW_AFTER_DEMO_EVIDENCE
    ):
        return NEXT_PACKET_LIVE_MICRO_REVIEW
    return NEXT_PACKET_CURRENT


def _safe_manual_next_action(protected_demo_attempt_status: str) -> str:
    if protected_demo_attempt_status == BLOCKED_BY_BANKING_FOCUS:
        return BANKING_FREEZE_STATEMENT
    if protected_demo_attempt_status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive fields and rerun metadata-only evaluation."
    if protected_demo_attempt_status == INCOMPLETE_INPUTS:
        return "Provide complete sanitized protected-demo attempt metadata."
    if protected_demo_attempt_status == BLOCKED_BY_DAILY_PROFIT_EVIDENCE_REQUIRED:
        return "Complete daily profit evidence before protected demo review."
    if protected_demo_attempt_status == CONTINUE_PROFIT_EVIDENCE_CAPTURE:
        return "Continue daily profit evidence capture before demo readiness."
    if protected_demo_attempt_status == BLOCKED_BY_ORDER_CANDIDATE:
        return "Repair or replace the sanitized one-order candidate metadata."
    if protected_demo_attempt_status == BLOCKED_BY_RISK_LIMITS:
        return "Lower risk or repair stop, target, kill-switch, and one-order controls."
    if protected_demo_attempt_status == BLOCKED_BY_EXECUTION_WINDOW:
        return "Define the protected demo execution window and owner approval gate."
    if protected_demo_attempt_status == BLOCKED_BY_POST_TRADE_REVIEW:
        return "Prepare post-attempt review before any owner-approved demo packet."
    if (
        protected_demo_attempt_status
        == READY_FOR_LIVE_MICRO_EXCEPTION_REVIEW_AFTER_DEMO_EVIDENCE
    ):
        return "Owner may review a separate live-micro exception packet after demo evidence."
    return "Owner may review the separate owner-approved demo one-order packet next."


def _sensitive_data_blockers(value: Any) -> tuple[str, ...]:
    blockers: list[str] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, Mapping):
            for raw_key, child in node.items():
                key_text = str(raw_key).lower()
                if _sensitive_key_blocked(key_text, child):
                    blockers.append(f"sensitive_key_at_{path}")
                    continue
                walk(child, f"{path}.field")
            return
        if isinstance(node, Sequence) and not isinstance(node, (str, bytes, bytearray)):
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


def _sensitive_key_blocked(key_text: str, value: Any) -> bool:
    if key_text in SAFE_SENSITIVE_NAMED_METADATA_KEYS and isinstance(value, bool):
        return False
    return any(part in key_text for part in SENSITIVE_KEY_PARTS)


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
        value
    )


def _banking_focus_blockers(value: Any) -> tuple[str, ...]:
    blockers: list[str] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, Mapping):
            for raw_key, child in node.items():
                key_text = str(raw_key).lower()
                if key_text in SAFE_BANKING_NAMED_METADATA_KEYS and child is False:
                    continue
                if any(part in key_text for part in BANKING_KEY_PARTS):
                    blockers.append(f"banking_focus_key_at_{path}")
                    continue
                walk(child, f"{path}.field")
            return
        if isinstance(node, Sequence) and not isinstance(node, (str, bytes, bytearray)):
            for child in node:
                walk(child, f"{path}.item")

    walk(value, "payload")
    return tuple(_unique(blockers))


def _missing_fields(source: Mapping[str, Any], required_fields: Sequence[str]) -> tuple[str, ...]:
    if not source:
        return tuple(required_fields)
    return tuple(field for field in required_fields if field not in source)


def _safe_status_label(value: Any) -> str:
    if isinstance(value, str) and value in DAILY_PROFIT_READY_STATUSES:
        return value
    if isinstance(value, str) and value:
        return "NOT_READY_OR_UNSUPPORTED"
    return "MISSING"


def _string_or_none(value: Any) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def _number_or_original(value: Any) -> int | float | str | None:
    decimal_value = _decimal(value)
    if decimal_value is not None:
        return _number_or_none(decimal_value)
    if isinstance(value, str) and value:
        return value
    return None


def _number_or_none(value: Decimal | None) -> int | float | None:
    if value is None:
        return None
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def _decimal(value: Any) -> Decimal | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _bool(value: Any) -> bool:
    return value is True


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


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
