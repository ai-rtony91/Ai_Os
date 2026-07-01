"""Metadata-only Forex market-close protection and receipt-capture evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_MARKET_CLOSE_PROTECTION_AND_RECEIPT_CAPTURE_V1"
MODE = "READ_ONLY_METADATA_ONLY_FOREX_MARKET_CLOSE_PROTECTION_AND_RECEIPT_CAPTURE"

CLOSE_PROTECTION_READY = "CLOSE_PROTECTION_READY"
CLOSE_PROTECTION_NO_NEW_RISK_READY = "CLOSE_PROTECTION_NO_NEW_RISK_READY"
CLOSE_PROTECTION_WAITING_RECEIPTS = "CLOSE_PROTECTION_WAITING_RECEIPTS"
CLOSE_PROTECTION_WAITING_POST_TRADE_REVIEW = (
    "CLOSE_PROTECTION_WAITING_POST_TRADE_REVIEW"
)
CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY = (
    "CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY"
)
CLOSE_PROTECTION_OWNER_ATTENTION_REQUIRED = (
    "CLOSE_PROTECTION_OWNER_ATTENTION_REQUIRED"
)
CLOSE_PROTECTION_RECEIPT_CAPTURE_READY = (
    "CLOSE_PROTECTION_RECEIPT_CAPTURE_READY"
)
CLOSE_PROTECTION_ACTIVE_SUPERVISION_DEFERRED = (
    "CLOSE_PROTECTION_ACTIVE_SUPERVISION_DEFERRED"
)
BLOCKED_BY_CALENDAR = "BLOCKED_BY_CALENDAR"
BLOCKED_BY_ACTIVE_SUPERVISION_STATE = "BLOCKED_BY_ACTIVE_SUPERVISION_STATE"
BLOCKED_BY_RECEIPT_STATE = "BLOCKED_BY_RECEIPT_STATE"
BLOCKED_BY_RISK_STATE = "BLOCKED_BY_RISK_STATE"
BLOCKED_BY_POLICY = "BLOCKED_BY_POLICY"
BLOCKED_BY_PROFIT_CLAIM = "BLOCKED_BY_PROFIT_CLAIM"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_MARKET_CLOSE_PROTECTION_AND_RECEIPT_CAPTURE_V1"

REQUIRED_TOP_LEVEL_SECTIONS = (
    "runtime_calendar_result",
    "active_supervision_result",
    "receipt_state",
    "close_policy",
    "risk_state",
    "owner_attention_policy",
    "claims",
)

RUNTIME_CALENDAR_REQUIRED_FIELDS = (
    "status",
    "ready",
    "runtime_job_router_enabled",
    "current_runtime_posture",
    "primary_job_lane",
    "close_protection_recommended",
    "trade_window_open",
    "close_window_active",
    "execution_authorized_by_calendar",
    "next_best_packet",
    "blocked_job_queue",
    "kill_switch_semantics",
)

ACTIVE_SUPERVISION_REQUIRED_FIELDS = (
    "status",
    "ready",
    "active_supervision_enabled",
    "trade_window_open",
    "may_execute_demo_by_this_module",
    "may_execute_live_by_this_module",
    "may_call_broker_by_this_module",
    "may_move_money",
    "next_best_packet",
    "blocked_action_queue",
    "owner_review_queue",
    "safety",
)

RECEIPT_REQUIRED_FIELDS = (
    "receipt_required_after_execution",
    "outstanding_receipts",
    "receipts_sanitized",
    "post_trade_review_complete",
    "receipt_capture_ready",
    "receipt_capture_metadata_only",
    "next_trade_blocked_until_receipts_reviewed",
    "receipt_values_sanitized",
    "no_raw_broker_receipts",
)

CLOSE_POLICY_REQUIRED_FIELDS = (
    "no_new_risk_during_close_protection",
    "no_new_trade_seeking_during_close_protection",
    "close_boundary_owner_summary_required",
    "owner_attention_if_unreviewed_receipts",
    "post_close_maintenance_prep_allowed",
    "receipt_capture_allowed",
    "broker_call_allowed",
    "trade_execution_allowed",
    "live_market_data_call_allowed",
    "strategy_mutation_allowed",
    "scheduler_creation_allowed",
    "daemon_creation_allowed",
    "raw_values_echoed",
)

RISK_REQUIRED_FIELDS = (
    "kill_switch_active",
    "daily_loss_stop_active",
    "drawdown_within_limit",
    "close_boundary_risk_review_required",
    "max_risk_per_trade_pct",
    "max_total_burst_risk_pct",
)

OWNER_ATTENTION_REQUIRED_FIELDS = (
    "owner_attention_if_unreviewed_receipts",
    "owner_attention_if_post_trade_review_incomplete",
    "owner_attention_if_risk_blocked",
    "close_boundary_owner_summary_required",
    "raw_values_echoed",
    "alert_channel_metadata_only",
    "no_alert_runtime_created",
)

CLAIM_FIELDS = (
    "guaranteed_profit_claimed",
    "fixed_return_promised",
    "daily_profit_guaranteed",
    "weekly_profit_guaranteed",
    "monthly_profit_guaranteed",
    "yearly_profit_guaranteed",
)

HARD_FALSE_FIELDS = (
    "live_trade_executed_by_this_module",
    "demo_trade_executed_by_this_module",
    "live_trade_closed_by_this_module",
    "demo_trade_closed_by_this_module",
    "broker_api_called_by_this_module",
    "credential_read",
    "credential_stored",
    "api_key_stored",
    "master_password_used",
    "vault_password_used",
    "money_moved",
    "bank_access_used",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "dashboard_runtime_created",
    "banking_work_built",
    "withdrawal_work_built",
    "transfer_work_built",
    "bank_routing_built",
    "withdrawal_execution_built",
    "ach_built",
    "wire_built",
    "card_built",
    "deposit_built",
    "strategy_mutated_by_this_module",
    "live_market_data_called_by_this_module",
    "demo_execution_payload_created",
    "live_execution_payload_created",
    "order_instruction_created",
    "broker_instruction_created",
    "close_order_instruction_created",
    "withdrawal_allowed_by_this_module",
    "bank_routing_allowed_by_this_module",
    "live_profit_guaranteed",
    "daily_profit_guaranteed",
    "weekly_profit_guaranteed",
    "monthly_profit_guaranteed",
    "yearly_profit_guaranteed",
    "fixed_return_promised_by_aios",
)

CLOSE_PROTECTION_JOB_SPECS = (
    ("no_new_risk_review", "P0"),
    ("no_new_trade_seeking_review", "P0"),
    ("active_supervision_defer_review", "P0"),
    ("open_intent_receipt_check", "P0"),
    ("receipt_capture_watch", "P1"),
    ("receipt_sanitization_check", "P1"),
    ("post_trade_review_check", "P1"),
    ("close_boundary_protection", "P0"),
    ("owner_attention_if_unreviewed_receipts", "P0"),
    ("post_close_maintenance_prep", "P2"),
)

BLOCKED_ACTION_IDS = (
    "open_new_trade_by_this_module",
    "execute_demo_by_this_module",
    "execute_live_by_this_module",
    "close_trade_by_this_module",
    "call_broker_by_this_module",
    "read_credentials_by_this_module",
    "move_money_by_this_module",
    "withdraw_by_this_module",
    "bank_route_by_this_module",
    "create_scheduler_by_this_module",
    "create_daemon_by_this_module",
    "mutate_strategy_by_this_module",
    "promise_profit_by_this_module",
)

OWNER_REVIEW_IDS = (
    "close_boundary_owner_summary_review",
    "runtime_execution_packet_required_for_any_order",
    "receipt_review_required_if_pending",
    "post_trade_review_required_if_incomplete",
    "risk_review_if_breached",
    "kill_switch_review_if_active",
    "post_close_maintenance_review",
)

SENSITIVE_KEY_PARTS = (
    "api_key",
    "token",
    "password",
    "secret",
    "bearer",
    "account_id",
    "accountnumber",
    "account_number",
    "routing_number",
    "card_number",
    "cvv",
    "master_password",
    "vault_password",
    "private_key",
)

SENSITIVE_VALUE_MARKERS = (
    "sk-",
    "bearer ",
    "api key",
    "token value",
    "access token",
    "private key",
    "password",
    "secret",
    "-----begin",
)

BANKING_KEY_TOKENS = frozenset(
    {
        "bank",
        "banking",
        "withdraw",
        "withdrawal",
        "routing",
        "route",
        "transfer",
        "ach",
        "wire",
        "card",
        "deposit",
        "money",
        "fund",
        "funding",
    }
)

BANKING_ALLOWED_TRUE_FIELDS = frozenset(
    {
        "withdrawal_deferred",
        "bank_routing_deferred",
        "receipt_required_after_execution",
        "next_trade_blocked_until_receipts_reviewed",
        "close_boundary_risk_review_required",
        "close_boundary_owner_summary_required",
        "owner_attention_if_unreviewed_receipts",
        "owner_attention_if_post_trade_review_incomplete",
        "owner_attention_if_risk_blocked",
    }
)


def evaluate_forex_market_close_protection_and_receipt_capture_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Evaluate close-boundary protection metadata without side effects."""

    source = _mapping(payload)
    if not source:
        return _build_result(INCOMPLETE_INPUTS, blockers=("payload_missing",))

    sensitive_blockers = _sensitive_data_blockers(source)
    if sensitive_blockers:
        return _build_result(BLOCKED_BY_SENSITIVE_DATA, blockers=sensitive_blockers)

    banking_blockers = _banking_focus_blockers(source)
    if banking_blockers:
        return _build_result(BLOCKED_BY_BANKING_FOCUS, blockers=banking_blockers)

    missing_top_level = tuple(
        f"{section}_missing"
        for section in REQUIRED_TOP_LEVEL_SECTIONS
        if section not in source
    )
    if missing_top_level:
        return _build_result(INCOMPLETE_INPUTS, source=source, blockers=missing_top_level)

    claims = _mapping(source.get("claims"))
    claim_blockers = _claim_blockers(claims)
    if claim_blockers:
        status = (
            INCOMPLETE_INPUTS
            if any(blocker.endswith("_missing") for blocker in claim_blockers)
            else BLOCKED_BY_PROFIT_CLAIM
        )
        return _build_result(status, source=source, blockers=claim_blockers)

    calendar = _mapping(source.get("runtime_calendar_result"))
    calendar_missing = _missing_fields(
        calendar,
        RUNTIME_CALENDAR_REQUIRED_FIELDS,
        "runtime_calendar_result",
    )
    if calendar_missing:
        return _build_result(INCOMPLETE_INPUTS, source=source, blockers=calendar_missing)
    calendar_policy_blockers = _calendar_policy_blockers(calendar)
    if calendar_policy_blockers:
        return _build_result(
            BLOCKED_BY_POLICY,
            source=source,
            blockers=calendar_policy_blockers,
        )
    calendar_blockers = _calendar_blockers(calendar)
    if calendar_blockers:
        return _build_result(
            BLOCKED_BY_CALENDAR,
            source=source,
            blockers=calendar_blockers,
        )

    active_supervision = _mapping(source.get("active_supervision_result"))
    active_missing = _missing_fields(
        active_supervision,
        ACTIVE_SUPERVISION_REQUIRED_FIELDS,
        "active_supervision_result",
    )
    if active_missing:
        return _build_result(INCOMPLETE_INPUTS, source=source, blockers=active_missing)
    active_blockers = _active_supervision_blockers(active_supervision)
    if active_blockers:
        return _build_result(
            BLOCKED_BY_ACTIVE_SUPERVISION_STATE,
            source=source,
            blockers=active_blockers,
        )

    close_policy = _mapping(source.get("close_policy"))
    policy_missing = _missing_fields(
        close_policy,
        CLOSE_POLICY_REQUIRED_FIELDS,
        "close_policy",
    )
    if policy_missing:
        return _build_result(INCOMPLETE_INPUTS, source=source, blockers=policy_missing)
    policy_blockers = _close_policy_blockers(close_policy)
    if policy_blockers:
        return _build_result(BLOCKED_BY_POLICY, source=source, blockers=policy_blockers)

    owner_policy = _mapping(source.get("owner_attention_policy"))
    owner_policy_missing = _missing_fields(
        owner_policy,
        OWNER_ATTENTION_REQUIRED_FIELDS,
        "owner_attention_policy",
    )
    if owner_policy_missing:
        return _build_result(
            INCOMPLETE_INPUTS,
            source=source,
            blockers=owner_policy_missing,
        )
    owner_policy_blockers = _owner_attention_policy_blockers(owner_policy)
    if owner_policy_blockers:
        return _build_result(
            BLOCKED_BY_POLICY,
            source=source,
            blockers=owner_policy_blockers,
        )

    risk = _mapping(source.get("risk_state"))
    risk_missing = _missing_fields(risk, RISK_REQUIRED_FIELDS, "risk_state")
    if risk_missing:
        return _build_result(INCOMPLETE_INPUTS, source=source, blockers=risk_missing)
    risk_blockers = _risk_blockers(risk)
    if risk_blockers:
        return _build_result(
            BLOCKED_BY_RISK_STATE,
            source=source,
            blockers=risk_blockers,
        )

    receipt = _mapping(source.get("receipt_state"))
    receipt_missing = _missing_fields(receipt, RECEIPT_REQUIRED_FIELDS, "receipt_state")
    if receipt_missing:
        return _build_result(INCOMPLETE_INPUTS, source=source, blockers=receipt_missing)
    receipt_policy_blockers = _receipt_policy_blockers(receipt)
    if receipt_policy_blockers:
        return _build_result(
            BLOCKED_BY_RECEIPT_STATE,
            source=source,
            blockers=receipt_policy_blockers,
        )
    if _bool(receipt.get("outstanding_receipts")):
        return _build_result(
            CLOSE_PROTECTION_WAITING_RECEIPTS,
            source=source,
            blockers=("outstanding_receipts_true",),
        )
    receipt_sanitization_blockers = _receipt_sanitization_blockers(receipt)
    if receipt_sanitization_blockers:
        return _build_result(
            BLOCKED_BY_RECEIPT_STATE,
            source=source,
            blockers=receipt_sanitization_blockers,
        )
    if not _bool(receipt.get("post_trade_review_complete")):
        return _build_result(
            CLOSE_PROTECTION_WAITING_POST_TRADE_REVIEW,
            source=source,
            blockers=("post_trade_review_complete_false",),
        )
    if _bool(receipt.get("receipt_capture_ready")):
        return _build_result(
            CLOSE_PROTECTION_RECEIPT_CAPTURE_READY,
            source=source,
            blockers=(),
        )

    return _build_result(
        CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY,
        source=source,
        blockers=(),
    )


def _build_result(
    status: str,
    *,
    source: Mapping[str, Any] | None = None,
    blockers: Sequence[str] = (),
) -> dict[str, Any]:
    data = _mapping(source)
    calendar = _mapping(data.get("runtime_calendar_result"))
    active_supervision = _mapping(data.get("active_supervision_result"))
    receipt = _mapping(data.get("receipt_state"))
    risk = _mapping(data.get("risk_state"))
    owner_policy = _mapping(data.get("owner_attention_policy"))

    blocker_list = list(_unique(blockers))
    ready = status in {
        CLOSE_PROTECTION_READY,
        CLOSE_PROTECTION_NO_NEW_RISK_READY,
        CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY,
        CLOSE_PROTECTION_RECEIPT_CAPTURE_READY,
        CLOSE_PROTECTION_ACTIVE_SUPERVISION_DEFERRED,
    }
    close_protection_enabled = _close_protection_enabled(calendar, status)
    close_window_active = _bool(calendar.get("close_window_active"))
    owner_attention_required = _owner_attention_required(
        status,
        receipt,
        risk,
        owner_policy,
        blocker_list,
    )
    active_supervision_deferred = close_protection_enabled and status not in {
        BLOCKED_BY_CALENDAR,
        INCOMPLETE_INPUTS,
    }
    receipt_capture_ready = (
        status == CLOSE_PROTECTION_RECEIPT_CAPTURE_READY
        and _bool(receipt.get("receipt_capture_ready"))
    )
    post_close_maintenance_ready = status in {
        CLOSE_PROTECTION_READY,
        CLOSE_PROTECTION_NO_NEW_RISK_READY,
        CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY,
    }
    next_best_packet = _next_packet(status)
    result = {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": ready,
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        "close_protection_enabled": close_protection_enabled,
        "close_window_active": close_window_active,
        "new_risk_allowed_by_this_module": False,
        "new_trade_seeking_allowed_by_this_module": False,
        "receipt_capture_required": _bool(
            receipt.get("receipt_required_after_execution")
        ),
        "receipt_capture_ready": receipt_capture_ready,
        "post_trade_review_required": True,
        "post_close_maintenance_ready": post_close_maintenance_ready,
        "owner_attention_required": owner_attention_required,
        "active_supervision_deferred": active_supervision_deferred,
        "close_protection_job_queue": _close_protection_job_queue(status),
        "blocked_action_queue": _blocked_action_queue(),
        "owner_review_queue": _owner_review_queue(status, owner_attention_required),
        "receipt_summary": _receipt_summary(receipt, status),
        "risk_summary": _risk_summary(risk, status),
        "active_supervision_summary": _active_supervision_summary(
            active_supervision,
            status,
            active_supervision_deferred,
        ),
        "post_close_maintenance_plan": _post_close_maintenance_plan(status),
        "owner_attention_summary": _owner_attention_summary(
            status,
            owner_attention_required,
            receipt,
            risk,
            blocker_list,
        ),
        "blockers": blocker_list,
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(status),
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "status": status,
            "ready": ready,
            "read_only": True,
            "metadata_only": True,
            "close_protection_enabled": close_protection_enabled,
            "close_window_active": close_window_active,
            "new_risk_allowed_by_this_module": False,
            "new_trade_seeking_allowed_by_this_module": False,
            "receipt_capture_ready": receipt_capture_ready,
            "post_close_maintenance_ready": post_close_maintenance_ready,
            "owner_attention_required": owner_attention_required,
            "active_supervision_deferred": active_supervision_deferred,
            "close_protection_job_count": len(CLOSE_PROTECTION_JOB_SPECS),
            "blocked_action_count": len(BLOCKED_ACTION_IDS),
            "blockers": blocker_list,
            "next_best_packet": next_best_packet,
            "no_order_instruction_created": True,
            "no_close_order_instruction_created": True,
        },
        "safety": _safety_summary(),
    }
    result.update({field: False for field in HARD_FALSE_FIELDS})
    return result


def _calendar_policy_blockers(calendar: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if _bool(calendar.get("execution_authorized_by_calendar")):
        blockers.append("calendar_execution_authorized_true")
    return tuple(_unique(blockers))


def _calendar_blockers(calendar: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if str(calendar.get("current_runtime_posture")) != "CLOSE_PROTECTION":
        blockers.append("calendar_posture_not_close_protection")
    if str(calendar.get("primary_job_lane")) != "protect_close":
        blockers.append("calendar_primary_job_lane_not_protect_close")
    if not _bool(calendar.get("ready")):
        blockers.append("calendar_ready_false")
    if not _bool(calendar.get("runtime_job_router_enabled")):
        blockers.append("calendar_runtime_job_router_enabled_false")
    if not isinstance(calendar.get("trade_window_open"), bool):
        blockers.append("calendar_trade_window_open_not_boolean")
    if not _bool(calendar.get("close_protection_recommended")):
        blockers.append("calendar_close_protection_recommended_false")
    if not _bool(calendar.get("close_window_active")):
        blockers.append("calendar_close_window_active_false")
    if not _present(calendar.get("next_best_packet")):
        blockers.append("calendar_next_best_packet_missing")
    if "blocked_job_queue" not in calendar:
        blockers.append("calendar_blocked_job_queue_missing")
    if "kill_switch_semantics" not in calendar:
        blockers.append("calendar_kill_switch_semantics_missing")
    return tuple(_unique(blockers))


def _active_supervision_blockers(
    active_supervision: Mapping[str, Any],
) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in (
        "ready",
        "active_supervision_enabled",
        "trade_window_open",
    ):
        if not isinstance(active_supervision.get(field), bool):
            blockers.append(f"active_supervision_result_{field}_not_boolean")
    for field in (
        "may_execute_demo_by_this_module",
        "may_execute_live_by_this_module",
        "may_call_broker_by_this_module",
        "may_move_money",
    ):
        if _bool(active_supervision.get(field)):
            blockers.append(f"active_supervision_result_{field}_true")
    if not _present(active_supervision.get("next_best_packet")):
        blockers.append("active_supervision_result_next_best_packet_missing")
    for field in ("blocked_action_queue", "owner_review_queue"):
        if not isinstance(active_supervision.get(field), Sequence) or isinstance(
            active_supervision.get(field),
            (str, bytes, bytearray),
        ):
            blockers.append(f"active_supervision_result_{field}_not_sequence")
    if not isinstance(active_supervision.get("safety"), Mapping):
        blockers.append("active_supervision_result_safety_missing")
    return tuple(_unique(blockers))


def _close_policy_blockers(close_policy: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in (
        "no_new_risk_during_close_protection",
        "no_new_trade_seeking_during_close_protection",
        "close_boundary_owner_summary_required",
        "owner_attention_if_unreviewed_receipts",
        "post_close_maintenance_prep_allowed",
        "receipt_capture_allowed",
    ):
        if not _bool(close_policy.get(field)):
            blockers.append(f"close_policy_{field}_false")
    for field in (
        "broker_call_allowed",
        "trade_execution_allowed",
        "live_market_data_call_allowed",
        "strategy_mutation_allowed",
        "scheduler_creation_allowed",
        "daemon_creation_allowed",
        "raw_values_echoed",
    ):
        if _bool(close_policy.get(field)):
            blockers.append(f"close_policy_{field}_true")
    return tuple(_unique(blockers))


def _owner_attention_policy_blockers(
    owner_policy: Mapping[str, Any],
) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in (
        "owner_attention_if_unreviewed_receipts",
        "owner_attention_if_post_trade_review_incomplete",
        "owner_attention_if_risk_blocked",
        "close_boundary_owner_summary_required",
        "alert_channel_metadata_only",
        "no_alert_runtime_created",
    ):
        if not _bool(owner_policy.get(field)):
            blockers.append(f"owner_attention_policy_{field}_false")
    if _bool(owner_policy.get("raw_values_echoed")):
        blockers.append("owner_attention_policy_raw_values_echoed_true")
    return tuple(_unique(blockers))


def _risk_blockers(risk: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if _bool(risk.get("kill_switch_active")):
        blockers.append("kill_switch_active_true")
    if _bool(risk.get("daily_loss_stop_active")):
        blockers.append("daily_loss_stop_active_true")
    if not _bool(risk.get("drawdown_within_limit")):
        blockers.append("drawdown_within_limit_false")
    if not _bool(risk.get("close_boundary_risk_review_required")):
        blockers.append("close_boundary_risk_review_required_false")
    for field in ("max_risk_per_trade_pct", "max_total_burst_risk_pct"):
        if not _is_number(risk.get(field)):
            blockers.append(f"{field}_not_number")
    if _number(risk.get("max_risk_per_trade_pct")) > 0.01:
        blockers.append("max_risk_per_trade_pct_above_0_01")
    if _number(risk.get("max_total_burst_risk_pct")) > 0.03:
        blockers.append("max_total_burst_risk_pct_above_0_03")
    return tuple(_unique(blockers))


def _receipt_policy_blockers(receipt: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in (
        "receipt_required_after_execution",
        "receipt_capture_metadata_only",
        "next_trade_blocked_until_receipts_reviewed",
    ):
        if not _bool(receipt.get(field)):
            blockers.append(f"receipt_state_{field}_false")
    return tuple(_unique(blockers))


def _receipt_sanitization_blockers(receipt: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in (
        "receipts_sanitized",
        "receipt_values_sanitized",
        "no_raw_broker_receipts",
    ):
        if not _bool(receipt.get(field)):
            blockers.append(f"receipt_state_{field}_false")
    return tuple(_unique(blockers))


def _claim_blockers(claims: Mapping[str, Any]) -> tuple[str, ...]:
    missing = _missing_fields(claims, CLAIM_FIELDS, "claims")
    if missing:
        return missing
    return tuple(f"{field}_true" for field in CLAIM_FIELDS if _bool(claims.get(field)))


def _close_protection_enabled(calendar: Mapping[str, Any], status: str) -> bool:
    if status in {BLOCKED_BY_CALENDAR, INCOMPLETE_INPUTS}:
        return False
    return (
        str(calendar.get("current_runtime_posture")) == "CLOSE_PROTECTION"
        and str(calendar.get("primary_job_lane")) == "protect_close"
        and _bool(calendar.get("close_protection_recommended"))
        and _bool(calendar.get("close_window_active"))
    )


def _owner_attention_required(
    status: str,
    receipt: Mapping[str, Any],
    risk: Mapping[str, Any],
    owner_policy: Mapping[str, Any],
    blockers: Sequence[str],
) -> bool:
    if status in {
        BLOCKED_BY_SENSITIVE_DATA,
        BLOCKED_BY_BANKING_FOCUS,
        BLOCKED_BY_PROFIT_CLAIM,
        BLOCKED_BY_POLICY,
    }:
        return True
    if status == BLOCKED_BY_RISK_STATE and _bool(
        owner_policy.get("owner_attention_if_risk_blocked")
    ):
        return True
    if _bool(receipt.get("outstanding_receipts")) and _bool(
        owner_policy.get("owner_attention_if_unreviewed_receipts")
    ):
        return True
    if not _bool(receipt.get("post_trade_review_complete")) and _bool(
        owner_policy.get("owner_attention_if_post_trade_review_incomplete")
    ):
        return True
    if _bool(risk.get("kill_switch_active")) or _bool(risk.get("daily_loss_stop_active")):
        return True
    return bool(blockers) and status.startswith("BLOCKED")


def _close_protection_job_queue(status: str) -> list[dict[str, Any]]:
    allowed_now = status in {
        CLOSE_PROTECTION_READY,
        CLOSE_PROTECTION_NO_NEW_RISK_READY,
        CLOSE_PROTECTION_WAITING_RECEIPTS,
        CLOSE_PROTECTION_WAITING_POST_TRADE_REVIEW,
        CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY,
        CLOSE_PROTECTION_RECEIPT_CAPTURE_READY,
        CLOSE_PROTECTION_ACTIVE_SUPERVISION_DEFERRED,
    }
    return [
        {
            "job_id": job_id,
            "priority": priority,
            "allowed_now": allowed_now,
            "requires_owner_packet": job_id
            in {
                "owner_attention_if_unreviewed_receipts",
                "post_close_maintenance_prep",
            },
            "requires_runtime_permission": False,
            "reason": _job_reason(job_id, status),
            "prohibited_actions": list(BLOCKED_ACTION_IDS),
        }
        for job_id, priority in CLOSE_PROTECTION_JOB_SPECS
    ]


def _job_reason(job_id: str, status: str) -> str:
    if status in {
        CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY,
        CLOSE_PROTECTION_RECEIPT_CAPTURE_READY,
        CLOSE_PROTECTION_WAITING_RECEIPTS,
        CLOSE_PROTECTION_WAITING_POST_TRADE_REVIEW,
    }:
        return f"{job_id} protects the close boundary without opening, closing, or routing orders."
    return f"{job_id} is held until status {status} is repaired or routed."


def _blocked_action_queue() -> list[dict[str, Any]]:
    return [
        {
            "action_id": action_id,
            "allowed_now": False,
            "reason": "This close-protection packet is metadata-only and blocks runtime, broker, credential, money, scheduler, daemon, strategy, and profit-promise actions.",
        }
        for action_id in BLOCKED_ACTION_IDS
    ]


def _owner_review_queue(
    status: str,
    owner_attention_required: bool,
) -> list[dict[str, Any]]:
    return [
        {
            "review_id": review_id,
            "required_now": _review_required_now(
                review_id,
                status,
                owner_attention_required,
            ),
            "reason": _review_reason(review_id, status),
        }
        for review_id in OWNER_REVIEW_IDS
    ]


def _review_required_now(
    review_id: str,
    status: str,
    owner_attention_required: bool,
) -> bool:
    if review_id == "runtime_execution_packet_required_for_any_order":
        return True
    if review_id == "close_boundary_owner_summary_review":
        return owner_attention_required or status in {
            CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY,
            CLOSE_PROTECTION_RECEIPT_CAPTURE_READY,
        }
    if review_id == "receipt_review_required_if_pending":
        return status in {
            CLOSE_PROTECTION_WAITING_RECEIPTS,
            BLOCKED_BY_RECEIPT_STATE,
        }
    if review_id == "post_trade_review_required_if_incomplete":
        return status == CLOSE_PROTECTION_WAITING_POST_TRADE_REVIEW
    if review_id == "risk_review_if_breached":
        return status == BLOCKED_BY_RISK_STATE
    if review_id == "kill_switch_review_if_active":
        return status == BLOCKED_BY_RISK_STATE
    if review_id == "post_close_maintenance_review":
        return status == CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY
    return False


def _review_reason(review_id: str, status: str) -> str:
    if review_id == "runtime_execution_packet_required_for_any_order":
        return "Any order still needs a separate owner-approved runtime execution packet."
    return f"{review_id} is tracked for close-protection status {status}."


def _receipt_summary(receipt: Mapping[str, Any], status: str) -> dict[str, Any]:
    return {
        "status": status,
        "receipt_required_after_execution": _bool(
            receipt.get("receipt_required_after_execution")
        ),
        "outstanding_receipts": _bool(receipt.get("outstanding_receipts")),
        "receipts_sanitized": _bool(receipt.get("receipts_sanitized")),
        "post_trade_review_complete": _bool(
            receipt.get("post_trade_review_complete")
        ),
        "receipt_capture_ready": _bool(receipt.get("receipt_capture_ready")),
        "receipt_capture_metadata_only": _bool(
            receipt.get("receipt_capture_metadata_only")
        ),
        "next_trade_blocked_until_receipts_reviewed": _bool(
            receipt.get("next_trade_blocked_until_receipts_reviewed")
        ),
        "receipt_values_sanitized": _bool(receipt.get("receipt_values_sanitized")),
        "no_raw_broker_receipts": _bool(receipt.get("no_raw_broker_receipts")),
        "raw_receipt_values_echoed": False,
    }


def _risk_summary(risk: Mapping[str, Any], status: str) -> dict[str, Any]:
    return {
        "status": status,
        "kill_switch_active": _bool(risk.get("kill_switch_active")),
        "daily_loss_stop_active": _bool(risk.get("daily_loss_stop_active")),
        "drawdown_within_limit": _bool(risk.get("drawdown_within_limit")),
        "close_boundary_risk_review_required": _bool(
            risk.get("close_boundary_risk_review_required")
        ),
        "max_risk_per_trade_pct": _round(
            _number(risk.get("max_risk_per_trade_pct"))
        ),
        "max_total_burst_risk_pct": _round(
            _number(risk.get("max_total_burst_risk_pct"))
        ),
        "risk_thresholds_within_close_boundary": not bool(_risk_blockers(risk)),
    }


def _active_supervision_summary(
    active_supervision: Mapping[str, Any],
    status: str,
    active_supervision_deferred: bool,
) -> dict[str, Any]:
    return {
        "status": str(active_supervision.get("status", "")),
        "close_protection_status": status,
        "ready": _bool(active_supervision.get("ready")),
        "active_supervision_enabled": _bool(
            active_supervision.get("active_supervision_enabled")
        ),
        "trade_window_open": _bool(active_supervision.get("trade_window_open")),
        "active_supervision_deferred": active_supervision_deferred,
        "may_execute_demo_by_this_module": False,
        "may_execute_live_by_this_module": False,
        "may_call_broker_by_this_module": False,
        "may_move_money": False,
        "next_best_packet_present": _present(
            active_supervision.get("next_best_packet")
        ),
    }


def _post_close_maintenance_plan(status: str) -> dict[str, Any]:
    return {
        "post_close_maintenance_prep_allowed": status
        in {
            CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY,
            CLOSE_PROTECTION_RECEIPT_CAPTURE_READY,
            CLOSE_PROTECTION_WAITING_RECEIPTS,
            CLOSE_PROTECTION_WAITING_POST_TRADE_REVIEW,
        },
        "route_to_maintenance_when_clean": status
        == CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY,
        "route_to_receipt_review_when_pending": status
        in {
            CLOSE_PROTECTION_WAITING_RECEIPTS,
            CLOSE_PROTECTION_WAITING_POST_TRADE_REVIEW,
            CLOSE_PROTECTION_RECEIPT_CAPTURE_READY,
            BLOCKED_BY_RECEIPT_STATE,
        },
        "new_risk_stays_blocked": True,
        "new_trade_seeking_stays_blocked": True,
    }


def _owner_attention_summary(
    status: str,
    owner_attention_required: bool,
    receipt: Mapping[str, Any],
    risk: Mapping[str, Any],
    blockers: Sequence[str],
) -> dict[str, Any]:
    return {
        "status": status,
        "owner_attention_required": owner_attention_required,
        "outstanding_receipts": _bool(receipt.get("outstanding_receipts")),
        "post_trade_review_complete": _bool(
            receipt.get("post_trade_review_complete")
        ),
        "risk_blocked": status == BLOCKED_BY_RISK_STATE,
        "kill_switch_active": _bool(risk.get("kill_switch_active")),
        "daily_loss_stop_active": _bool(risk.get("daily_loss_stop_active")),
        "blocker_count": len(_unique(blockers)),
        "raw_values_echoed": False,
        "alert_channel_metadata_only": True,
        "no_alert_runtime_created": True,
    }


def _safety_summary() -> dict[str, bool]:
    return {
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        "no_trade_execution": True,
        "no_trade_close": True,
        "no_broker_call": True,
        "no_credential_read": True,
        "no_money_movement": True,
        "no_withdrawal": True,
        "no_bank_routing": True,
        "no_scheduler": True,
        "no_daemon": True,
        "no_webhook": True,
        "no_dashboard_runtime": True,
        "no_strategy_mutation": True,
        "no_profit_guarantee": True,
        **{field: False for field in HARD_FALSE_FIELDS},
    }


def _next_packet(status: str) -> str:
    routes = {
        CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY: (
            "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1"
        ),
        CLOSE_PROTECTION_READY: (
            "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1"
        ),
        CLOSE_PROTECTION_NO_NEW_RISK_READY: (
            "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1"
        ),
        CLOSE_PROTECTION_RECEIPT_CAPTURE_READY: (
            "AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1"
        ),
        CLOSE_PROTECTION_WAITING_RECEIPTS: (
            "AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1"
        ),
        CLOSE_PROTECTION_WAITING_POST_TRADE_REVIEW: (
            "AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1"
        ),
        CLOSE_PROTECTION_OWNER_ATTENTION_REQUIRED: (
            "AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1"
        ),
        CLOSE_PROTECTION_ACTIVE_SUPERVISION_DEFERRED: (
            "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1"
        ),
        BLOCKED_BY_CALENDAR: (
            "AIOS_FOREX_RUNTIME_CALENDAR_STATUS_AND_MAINTENANCE_MODE_V1"
        ),
        BLOCKED_BY_ACTIVE_SUPERVISION_STATE: (
            "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1"
        ),
        BLOCKED_BY_RECEIPT_STATE: (
            "AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1"
        ),
        BLOCKED_BY_RISK_STATE: "AIOS_FOREX_RISK_SCALE_DOWN_REVIEW_V1",
    }
    return routes.get(status, NEXT_BEST_PACKET)


def _safe_manual_next_action(status: str) -> str:
    if status == CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY:
        return "Route to post-close maintenance; keep new risk and new trade seeking blocked."
    if status == CLOSE_PROTECTION_RECEIPT_CAPTURE_READY:
        return "Route sanitized receipt metadata to receipt review before any next trade lane."
    if status == CLOSE_PROTECTION_WAITING_RECEIPTS:
        return "Wait for sanitized receipts and keep next trade seeking blocked."
    if status == CLOSE_PROTECTION_WAITING_POST_TRADE_REVIEW:
        return "Complete post-trade review before post-close maintenance readiness."
    if status == BLOCKED_BY_CALENDAR:
        return "Repair calendar close-protection metadata before close-boundary routing."
    if status == BLOCKED_BY_ACTIVE_SUPERVISION_STATE:
        return "Repair active-supervision safety metadata before close-boundary routing."
    if status == BLOCKED_BY_RECEIPT_STATE:
        return "Repair receipt sanitization metadata before close-boundary routing."
    if status == BLOCKED_BY_RISK_STATE:
        return "Complete close-boundary risk review before further Forex routing."
    if status == BLOCKED_BY_POLICY:
        return "Repair close-protection policy metadata before continuing."
    if status == BLOCKED_BY_PROFIT_CLAIM:
        return "Remove profit guarantee or fixed-return claims."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys or secret-like values and rerun the evaluator."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove active banking, withdrawal, transfer, or money-movement focus fields."
    return "Provide complete market-close protection metadata and rerun the evaluator."


def _missing_fields(
    value: Mapping[str, Any],
    fields: Sequence[str],
    prefix: str,
) -> tuple[str, ...]:
    if not value:
        return (f"{prefix}_missing",)
    return tuple(f"{prefix}_{field}_missing" for field in fields if field not in value)


def _sensitive_data_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = _normalize_key(raw_key)
            child_path = f"{path}.{raw_key}"
            if _sensitive_key_active(key, child):
                blockers.append(f"{child_path}:sensitive_key")
                continue
            blockers.extend(_sensitive_data_blockers(child, child_path))
        return tuple(_unique(blockers))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_sensitive_data_blockers(child, f"{path}[{index}]"))
        return tuple(_unique(blockers))
    if isinstance(value, str) and not _safe_sensitive_value(value):
        if _looks_secret_string(value):
            blockers.append(f"{path}:secret_like_value")
    return tuple(_unique(blockers))


def _sensitive_key_active(key: str, child: Any) -> bool:
    if key.startswith("no_"):
        return False
    return any(part in key for part in SENSITIVE_KEY_PARTS) and not _safe_sensitive_value(
        child
    )


def _safe_sensitive_value(value: Any) -> bool:
    if value is False or value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"", "false", "0", "none", "off", "disabled"}
    return False


def _looks_secret_string(value: str) -> bool:
    lowered = value.lower()
    if any(marker in lowered for marker in SENSITIVE_VALUE_MARKERS):
        return True
    return len(value) >= 16 and _has_long_digit_run(value, minimum=12)


def _banking_focus_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key = _normalize_key(raw_key)
            child_path = f"{path}.{raw_key}"
            if child_path == "payload.active_supervision_result.may_move_money":
                blockers.extend(_banking_focus_blockers(child, child_path))
                continue
            if _banking_key_active(key) and _active_focus(child):
                blockers.append(f"{child_path}:banking_focus")
                continue
            blockers.extend(_banking_focus_blockers(child, child_path))
        return tuple(_unique(blockers))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_banking_focus_blockers(child, f"{path}[{index}]"))
    return tuple(_unique(blockers))


def _banking_key_active(key: str) -> bool:
    if key.startswith("no_") or key in BANKING_ALLOWED_TRUE_FIELDS:
        return False
    tokens = set(key.split("_"))
    return any(token in BANKING_KEY_TOKENS for token in tokens)


def _active_focus(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() not in {"", "false", "0", "none", "off", "disabled"}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    if isinstance(value, Mapping):
        return bool(value)
    return True


def _normalize_key(key: Any) -> str:
    return str(key).lower().replace("-", "_").replace(" ", "_")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _number(value: Any) -> float:
    return float(value) if _is_number(value) else 0.0


def _round(value: float) -> float:
    return round(value, 6)


def _present(value: Any) -> bool:
    return value is not None and value != ""


def _has_long_digit_run(value: str, minimum: int) -> bool:
    run = 0
    for char in value:
        if char.isdigit():
            run += 1
            if run >= minimum:
                return True
        else:
            run = 0
    return False


def _unique(values: Sequence[Any]) -> list[str]:
    result: list[str] = []
    for value in values:
        text = str(value)
        if text not in result:
            result.append(text)
    return result
