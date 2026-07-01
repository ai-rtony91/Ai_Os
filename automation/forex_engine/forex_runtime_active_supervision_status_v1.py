"""Metadata-only Forex runtime active supervision status evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1"
MODE = "READ_ONLY_METADATA_ONLY_RUNTIME_ACTIVE_SUPERVISION_STATUS"

ACTIVE_SUPERVISION_READY = "ACTIVE_SUPERVISION_READY"
ACTIVE_SUPERVISION_METADATA_SCAN_READY = "ACTIVE_SUPERVISION_METADATA_SCAN_READY"
ACTIVE_SUPERVISION_OWNER_REVIEW_REQUIRED = "ACTIVE_SUPERVISION_OWNER_REVIEW_REQUIRED"
ACTIVE_SUPERVISION_MAINTENANCE_FALLBACK = "ACTIVE_SUPERVISION_MAINTENANCE_FALLBACK"
ACTIVE_SUPERVISION_WAITING_FOR_PROOF = "ACTIVE_SUPERVISION_WAITING_FOR_PROOF"
ACTIVE_SUPERVISION_WAITING_FOR_RECEIPTS = "ACTIVE_SUPERVISION_WAITING_FOR_RECEIPTS"
ACTIVE_SUPERVISION_BALANCE_REVIEW_REQUIRED = (
    "ACTIVE_SUPERVISION_BALANCE_REVIEW_REQUIRED"
)
ACTIVE_SUPERVISION_COMPOUNDING_REVIEW_REQUIRED = (
    "ACTIVE_SUPERVISION_COMPOUNDING_REVIEW_REQUIRED"
)
ACTIVE_SUPERVISION_PROFIT_PROTECTION_REVIEW_REQUIRED = (
    "ACTIVE_SUPERVISION_PROFIT_PROTECTION_REVIEW_REQUIRED"
)
BLOCKED_BY_CALENDAR = "BLOCKED_BY_CALENDAR"
BLOCKED_BY_VACATION_MODE = "BLOCKED_BY_VACATION_MODE"
BLOCKED_BY_RISK_STATE = "BLOCKED_BY_RISK_STATE"
BLOCKED_BY_PERMISSION_SNAPSHOT = "BLOCKED_BY_PERMISSION_SNAPSHOT"
BLOCKED_BY_RECEIPT_STATE = "BLOCKED_BY_RECEIPT_STATE"
BLOCKED_BY_BALANCE_STATE = "BLOCKED_BY_BALANCE_STATE"
BLOCKED_BY_COMPOUNDING_STATE = "BLOCKED_BY_COMPOUNDING_STATE"
BLOCKED_BY_PROFIT_PROTECTION_STATE = "BLOCKED_BY_PROFIT_PROTECTION_STATE"
BLOCKED_BY_PROOF_STATE = "BLOCKED_BY_PROOF_STATE"
BLOCKED_BY_POLICY = "BLOCKED_BY_POLICY"
BLOCKED_BY_PROFIT_CLAIM = "BLOCKED_BY_PROFIT_CLAIM"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1"

REQUIRED_TOP_LEVEL_SECTIONS = (
    "runtime_calendar_result",
    "vacation_mode_result",
    "permission_snapshot",
    "risk_state",
    "receipt_state",
    "proof_state",
    "candidate_policy",
    "claims",
)

RUNTIME_CALENDAR_REQUIRED_FIELDS = (
    "status",
    "ready",
    "runtime_job_router_enabled",
    "current_runtime_posture",
    "primary_job_lane",
    "trade_window_open",
    "execution_authorized_by_calendar",
    "next_best_packet",
    "blocked_job_queue",
    "vacation_mode_toggle_semantics",
    "kill_switch_semantics",
)

VACATION_MODE_REQUIRED_FIELDS = (
    "campaign_status",
    "campaign_ready",
    "vacation_mode_requested",
    "vacation_mode_toggle_state",
    "vacation_mode_operation_state",
    "new_trade_seeking_allowed_by_this_module",
    "maintenance_allowed_by_this_module",
    "owner_attention_required",
    "next_best_packet",
    "safety",
)

PERMISSION_REQUIRED_FIELDS = (
    "may_scan_metadata",
    "may_prepare_candidates",
    "may_prepare_demo_runtime_intent_metadata",
    "may_prepare_live_owner_review_metadata",
    "may_prepare_maintenance_work",
    "may_prepare_receipt_review",
    "may_prepare_balance_learning_review",
    "may_execute_demo_by_this_module",
    "may_execute_live_by_this_module",
    "may_call_broker_by_this_module",
    "may_read_credentials_by_this_module",
    "may_move_money",
    "may_withdraw",
    "may_bank_route",
    "owner_runtime_packet_required_for_execution",
)

RISK_REQUIRED_FIELDS = (
    "kill_switch_active",
    "daily_loss_stop_active",
    "drawdown_within_limit",
    "current_drawdown_pct",
    "max_drawdown_pct",
    "current_daily_loss_pct",
    "max_daily_loss_pct",
    "max_risk_per_trade_pct",
    "max_total_burst_risk_pct",
    "risk_policy_owner_reviewed",
)

RECEIPT_REQUIRED_FIELDS = (
    "receipt_required_after_execution",
    "outstanding_receipts",
    "receipts_sanitized",
    "post_trade_review_complete",
    "next_trade_blocked_until_receipts_reviewed",
)

BALANCE_REQUIRED_FIELDS = (
    "balance_memory_ready",
    "compounding_observer_ready",
    "withdrawal_deferred",
    "bank_routing_deferred",
    "money_moved",
    "current_balance_present",
    "current_equity_present",
)

COMPOUNDING_REQUIRED_FIELDS = (
    "compounding_scale_ready",
    "compounding_status",
    "scale_decision",
    "scale_direction",
    "proposed_next_risk_budget_pct",
    "owner_decision_required",
    "money_moved",
    "withdrawal_allowed_by_this_module",
    "bank_routing_allowed_by_this_module",
)

PROFIT_PROTECTION_REQUIRED_FIELDS = (
    "profit_protection_ready",
    "profit_protection_status",
    "realized_profit_only",
    "withdrawal_review_future_enabled",
    "withdrawal_execution_allowed",
    "bank_routing_allowed",
    "money_moved",
)

PROOF_REQUIRED_FIELDS = (
    "proof_required",
    "proof_ready",
    "proof_continuity_ready",
    "fake_proof_blocked",
    "repeatability_review_ready",
    "owner_review_required_for_live",
)

CANDIDATE_POLICY_REQUIRED_FIELDS = (
    "candidate_refresh_metadata_allowed",
    "strategy_mutation_allowed",
    "broker_call_allowed",
    "live_market_data_call_allowed",
    "require_stop_loss",
    "require_take_profit",
    "require_spread_policy",
    "require_slippage_policy",
    "require_news_blackout_policy",
    "owner_runtime_packet_required_for_execution",
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
    "withdrawal_allowed_by_this_module",
    "bank_routing_allowed_by_this_module",
    "live_profit_guaranteed",
    "daily_profit_guaranteed",
    "weekly_profit_guaranteed",
    "monthly_profit_guaranteed",
    "yearly_profit_guaranteed",
    "fixed_return_promised_by_aios",
)

SUPERVISION_JOB_SPECS = (
    ("risk_status_check", "P0"),
    ("kill_switch_state_check", "P0"),
    ("daily_loss_stop_check", "P0"),
    ("drawdown_check", "P0"),
    ("spread_policy_watch", "P1"),
    ("slippage_policy_watch", "P1"),
    ("receipt_capture_watch", "P1"),
    ("post_trade_review_watch", "P1"),
    ("balance_equity_watch", "P2"),
    ("compounding_scale_watch", "P2"),
    ("profit_protection_watch", "P2"),
    ("candidate_metadata_refresh", "P2"),
    ("proof_continuity_check", "P1"),
    ("owner_alert_readiness", "P1"),
)

BLOCKED_ACTION_IDS = (
    "execute_demo_by_this_module",
    "execute_live_by_this_module",
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
    "active_supervision_owner_summary_review",
    "runtime_execution_packet_required_for_any_order",
    "proof_and_receipt_review_if_pending",
    "balance_and_compounding_review_if_pending",
    "profit_protection_review_if_pending",
    "kill_switch_review_if_active",
    "risk_review_if_breached",
)

VACATION_ACTIVE_STATES = frozenset(
    {
        "VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE",
        "VACATION_MODE_ON_EVALUATING_GATES",
    }
)

VACATION_MAINTENANCE_STATES = frozenset({"OFF", "PAUSE"})

PERMISSION_FALSE_FIELDS = frozenset(
    {
        "may_execute_demo_by_this_module",
        "may_execute_live_by_this_module",
        "may_call_broker_by_this_module",
        "may_read_credentials_by_this_module",
        "may_move_money",
        "may_withdraw",
        "may_bank_route",
    }
)

SENSITIVE_KEY_PARTS = (
    "api_key",
    "token",
    "password",
    "secret",
    "bearer",
    "account_id",
    "accountnumber",
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
        "withdrawal_review_future_enabled",
        "receipt_required_after_execution",
        "next_trade_blocked_until_receipts_reviewed",
        "realized_profit_only",
    }
)


def evaluate_forex_runtime_active_supervision_status_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify market-open active supervision posture from metadata only."""

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
    claim_blockers = _profit_claim_blockers(claims)
    if claim_blockers:
        return _build_result(
            BLOCKED_BY_PROFIT_CLAIM,
            source=source,
            blockers=claim_blockers,
        )

    calendar = _mapping(source.get("runtime_calendar_result"))
    calendar_missing = _missing_fields(calendar, RUNTIME_CALENDAR_REQUIRED_FIELDS, "runtime_calendar_result")
    if calendar_missing:
        return _build_result(INCOMPLETE_INPUTS, source=source, blockers=calendar_missing)
    calendar_blockers = _calendar_blockers(calendar)
    if calendar_blockers:
        status = BLOCKED_BY_POLICY if "calendar_execution_authorized_true" in calendar_blockers else BLOCKED_BY_CALENDAR
        return _build_result(status, source=source, blockers=calendar_blockers)

    vacation = _mapping(source.get("vacation_mode_result"))
    vacation_missing = _missing_fields(vacation, VACATION_MODE_REQUIRED_FIELDS, "vacation_mode_result")
    if vacation_missing:
        return _build_result(INCOMPLETE_INPUTS, source=source, blockers=vacation_missing)
    vacation_toggle = str(vacation.get("vacation_mode_toggle_state", ""))
    if vacation_toggle in VACATION_MAINTENANCE_STATES:
        return _build_result(
            ACTIVE_SUPERVISION_MAINTENANCE_FALLBACK,
            source=source,
            blockers=(f"vacation_mode_toggle_state_{vacation_toggle.lower()}",),
        )
    vacation_blockers = _vacation_blockers(vacation)
    if vacation_blockers:
        return _build_result(BLOCKED_BY_VACATION_MODE, source=source, blockers=vacation_blockers)
    if _bool(vacation.get("owner_attention_required")):
        return _build_result(
            ACTIVE_SUPERVISION_OWNER_REVIEW_REQUIRED,
            source=source,
            blockers=("vacation_mode_owner_attention_required",),
        )

    permission = _mapping(source.get("permission_snapshot"))
    permission_missing = _missing_fields(permission, PERMISSION_REQUIRED_FIELDS, "permission_snapshot")
    if permission_missing:
        return _build_result(INCOMPLETE_INPUTS, source=source, blockers=permission_missing)
    permission_blockers = _permission_blockers(permission)
    if permission_blockers:
        return _build_result(
            BLOCKED_BY_PERMISSION_SNAPSHOT,
            source=source,
            blockers=permission_blockers,
        )

    risk = _mapping(source.get("risk_state"))
    risk_missing = _missing_fields(risk, RISK_REQUIRED_FIELDS, "risk_state")
    if risk_missing:
        return _build_result(INCOMPLETE_INPUTS, source=source, blockers=risk_missing)
    risk_blockers = _risk_blockers(risk)
    if risk_blockers:
        status = BLOCKED_BY_POLICY if "risk_policy_owner_reviewed_false" in risk_blockers else BLOCKED_BY_RISK_STATE
        return _build_result(status, source=source, blockers=risk_blockers)

    receipt = _mapping(source.get("receipt_state"))
    receipt_missing = _missing_fields(receipt, RECEIPT_REQUIRED_FIELDS, "receipt_state")
    if receipt_missing:
        return _build_result(INCOMPLETE_INPUTS, source=source, blockers=receipt_missing)
    if _bool(receipt.get("outstanding_receipts")):
        return _build_result(
            ACTIVE_SUPERVISION_WAITING_FOR_RECEIPTS,
            source=source,
            blockers=("outstanding_receipts_true",),
        )
    receipt_blockers = _receipt_blockers(receipt)
    if receipt_blockers:
        return _build_result(BLOCKED_BY_RECEIPT_STATE, source=source, blockers=receipt_blockers)

    balance = _mapping(source.get("balance_state"))
    if not balance:
        return _build_result(
            ACTIVE_SUPERVISION_BALANCE_REVIEW_REQUIRED,
            source=source,
            blockers=("balance_state_missing",),
        )
    balance_missing = _missing_fields(balance, BALANCE_REQUIRED_FIELDS, "balance_state")
    if balance_missing:
        return _build_result(
            ACTIVE_SUPERVISION_BALANCE_REVIEW_REQUIRED,
            source=source,
            blockers=balance_missing,
        )
    balance_blockers = _balance_blockers(balance)
    if balance_blockers:
        status = (
            ACTIVE_SUPERVISION_BALANCE_REVIEW_REQUIRED
            if _balance_review_blockers(balance_blockers)
            else BLOCKED_BY_BALANCE_STATE
        )
        return _build_result(status, source=source, blockers=balance_blockers)

    compounding = _mapping(source.get("compounding_state"))
    if not compounding:
        return _build_result(
            ACTIVE_SUPERVISION_COMPOUNDING_REVIEW_REQUIRED,
            source=source,
            blockers=("compounding_state_missing",),
        )
    compounding_missing = _missing_fields(compounding, COMPOUNDING_REQUIRED_FIELDS, "compounding_state")
    if compounding_missing:
        return _build_result(
            ACTIVE_SUPERVISION_COMPOUNDING_REVIEW_REQUIRED,
            source=source,
            blockers=compounding_missing,
        )
    compounding_blockers = _compounding_blockers(compounding)
    if compounding_blockers:
        status = (
            ACTIVE_SUPERVISION_COMPOUNDING_REVIEW_REQUIRED
            if "compounding_scale_ready_false" in compounding_blockers
            else BLOCKED_BY_COMPOUNDING_STATE
        )
        return _build_result(status, source=source, blockers=compounding_blockers)

    profit = _mapping(source.get("profit_protection_state"))
    if not profit:
        return _build_result(
            ACTIVE_SUPERVISION_PROFIT_PROTECTION_REVIEW_REQUIRED,
            source=source,
            blockers=("profit_protection_state_missing",),
        )
    profit_missing = _missing_fields(profit, PROFIT_PROTECTION_REQUIRED_FIELDS, "profit_protection_state")
    if profit_missing:
        return _build_result(
            ACTIVE_SUPERVISION_PROFIT_PROTECTION_REVIEW_REQUIRED,
            source=source,
            blockers=profit_missing,
        )
    profit_blockers = _profit_protection_blockers(profit)
    if profit_blockers:
        status = (
            ACTIVE_SUPERVISION_PROFIT_PROTECTION_REVIEW_REQUIRED
            if "profit_protection_ready_false" in profit_blockers
            else BLOCKED_BY_PROFIT_PROTECTION_STATE
        )
        return _build_result(status, source=source, blockers=profit_blockers)

    proof = _mapping(source.get("proof_state"))
    proof_missing = _missing_fields(proof, PROOF_REQUIRED_FIELDS, "proof_state")
    if proof_missing:
        return _build_result(INCOMPLETE_INPUTS, source=source, blockers=proof_missing)
    proof_waiting = _proof_waiting_blockers(proof)
    if proof_waiting:
        return _build_result(
            ACTIVE_SUPERVISION_WAITING_FOR_PROOF,
            source=source,
            blockers=proof_waiting,
        )
    proof_blockers = _proof_blockers(proof)
    if proof_blockers:
        return _build_result(BLOCKED_BY_PROOF_STATE, source=source, blockers=proof_blockers)

    candidate = _mapping(source.get("candidate_policy"))
    candidate_missing = _missing_fields(candidate, CANDIDATE_POLICY_REQUIRED_FIELDS, "candidate_policy")
    if candidate_missing:
        return _build_result(INCOMPLETE_INPUTS, source=source, blockers=candidate_missing)
    candidate_blockers = _candidate_policy_blockers(candidate)
    if candidate_blockers:
        return _build_result(BLOCKED_BY_POLICY, source=source, blockers=candidate_blockers)

    if (
        _bool(permission.get("may_scan_metadata"))
        and _bool(permission.get("may_prepare_candidates"))
        and not _bool(permission.get("may_prepare_demo_runtime_intent_metadata"))
        and not _bool(permission.get("may_prepare_live_owner_review_metadata"))
    ):
        return _build_result(ACTIVE_SUPERVISION_METADATA_SCAN_READY, source=source)

    return _build_result(ACTIVE_SUPERVISION_READY, source=source)


def _build_result(
    status: str,
    *,
    source: Mapping[str, Any] | None = None,
    blockers: Sequence[str] = (),
) -> dict[str, Any]:
    data = _mapping(source)
    calendar = _mapping(data.get("runtime_calendar_result"))
    vacation = _mapping(data.get("vacation_mode_result"))
    permission = _mapping(data.get("permission_snapshot"))
    risk = _mapping(data.get("risk_state"))
    receipt = _mapping(data.get("receipt_state"))
    balance = _mapping(data.get("balance_state"))
    compounding = _mapping(data.get("compounding_state"))
    profit = _mapping(data.get("profit_protection_state"))
    proof = _mapping(data.get("proof_state"))
    candidate = _mapping(data.get("candidate_policy"))

    ready = status in {
        ACTIVE_SUPERVISION_READY,
        ACTIVE_SUPERVISION_METADATA_SCAN_READY,
    }
    active_supervision_enabled = ready
    blocker_list = list(_unique(blockers))
    next_best_packet = _next_packet(status)
    result = {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": ready,
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        "active_supervision_enabled": active_supervision_enabled,
        "trade_window_open": _bool(calendar.get("trade_window_open")),
        "vacation_mode_active": _vacation_mode_active(vacation),
        "may_scan_metadata": _bool(permission.get("may_scan_metadata")),
        "may_prepare_candidates": _bool(permission.get("may_prepare_candidates")),
        "may_prepare_demo_runtime_intent_metadata": _bool(
            permission.get("may_prepare_demo_runtime_intent_metadata")
        ),
        "may_prepare_live_owner_review_metadata": _bool(
            permission.get("may_prepare_live_owner_review_metadata")
        ),
        "may_prepare_maintenance_work": _bool(permission.get("may_prepare_maintenance_work")),
        "may_prepare_receipt_review": _bool(permission.get("may_prepare_receipt_review")),
        "may_prepare_balance_learning_review": _bool(
            permission.get("may_prepare_balance_learning_review")
        ),
        "may_execute_demo_by_this_module": False,
        "may_execute_live_by_this_module": False,
        "may_call_broker_by_this_module": False,
        "may_read_credentials_by_this_module": False,
        "may_move_money": False,
        "may_withdraw": False,
        "may_bank_route": False,
        "owner_runtime_packet_required_for_execution": _bool(
            permission.get("owner_runtime_packet_required_for_execution")
        )
        or True,
        "supervision_job_queue": _supervision_job_queue(status),
        "blocked_action_queue": _blocked_action_queue(),
        "deferred_job_queue": _deferred_job_queue(status),
        "owner_review_queue": _owner_review_queue(status),
        "risk_watch_summary": _risk_watch_summary(risk, status),
        "receipt_watch_summary": _receipt_watch_summary(receipt, status),
        "balance_watch_summary": _balance_watch_summary(balance, status),
        "compounding_watch_summary": _compounding_watch_summary(compounding, status),
        "profit_protection_watch_summary": _profit_protection_watch_summary(profit, status),
        "proof_watch_summary": _proof_watch_summary(proof, status),
        "candidate_refresh_summary": _candidate_refresh_summary(candidate, status),
        "owner_alert_summary": _owner_alert_summary(vacation, risk, proof, blocker_list),
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
            "owner_decision_required": True,
            "active_supervision_enabled": active_supervision_enabled,
            "trade_window_open": _bool(calendar.get("trade_window_open")),
            "vacation_mode_active": _vacation_mode_active(vacation),
            "blocked_action_count": len(BLOCKED_ACTION_IDS),
            "supervision_job_count": len(SUPERVISION_JOB_SPECS),
            "blockers": blocker_list,
            "next_best_packet": next_best_packet,
            "no_execution_payload_created": True,
        },
        "safety": _safety_summary(),
    }
    result.update({field: False for field in HARD_FALSE_FIELDS})
    return result


def _calendar_blockers(calendar: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if str(calendar.get("current_runtime_posture")) != "ACTIVE_SUPERVISION":
        blockers.append("calendar_posture_not_active_supervision")
    if str(calendar.get("primary_job_lane")) != "supervise_runtime":
        blockers.append("calendar_primary_job_lane_not_supervise_runtime")
    if not _bool(calendar.get("ready")):
        blockers.append("calendar_ready_false")
    if not _bool(calendar.get("runtime_job_router_enabled")):
        blockers.append("calendar_runtime_job_router_enabled_false")
    if not _bool(calendar.get("trade_window_open")):
        blockers.append("calendar_trade_window_open_false")
    if _bool(calendar.get("execution_authorized_by_calendar")):
        blockers.append("calendar_execution_authorized_true")
    if not _present(calendar.get("next_best_packet")):
        blockers.append("calendar_next_best_packet_missing")
    if "blocked_job_queue" not in calendar:
        blockers.append("calendar_blocked_job_queue_missing")
    if "vacation_mode_toggle_semantics" not in calendar:
        blockers.append("calendar_vacation_mode_toggle_semantics_missing")
    if "kill_switch_semantics" not in calendar:
        blockers.append("calendar_kill_switch_semantics_missing")
    return tuple(_unique(blockers))


def _vacation_blockers(vacation: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    toggle = str(vacation.get("vacation_mode_toggle_state", ""))
    operation = str(vacation.get("vacation_mode_operation_state", ""))
    for field in (
        "new_trade_seeking_allowed_by_this_module",
        "maintenance_allowed_by_this_module",
        "owner_attention_required",
    ):
        if not isinstance(vacation.get(field), bool):
            blockers.append(f"{field}_not_boolean")
    if not _bool(vacation.get("campaign_ready")):
        blockers.append("campaign_ready_false")
    if not _bool(vacation.get("vacation_mode_requested")):
        blockers.append("vacation_mode_requested_false")
    if toggle not in {"ON", "RESUME"}:
        blockers.append("vacation_mode_toggle_state_not_on_or_resume")
    if operation not in VACATION_ACTIVE_STATES:
        blockers.append("vacation_mode_operation_state_not_active_supervision")
    if not _present(vacation.get("next_best_packet")):
        blockers.append("vacation_mode_next_best_packet_missing")
    if not isinstance(vacation.get("safety"), Mapping):
        blockers.append("vacation_mode_safety_missing")
    return tuple(_unique(blockers))


def _permission_blockers(permission: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if not _bool(permission.get("may_scan_metadata")):
        blockers.append("may_scan_metadata_false")
    if not _bool(permission.get("may_prepare_candidates")):
        blockers.append("may_prepare_candidates_false")
    for field in (
        "may_prepare_demo_runtime_intent_metadata",
        "may_prepare_live_owner_review_metadata",
        "may_prepare_maintenance_work",
        "may_prepare_receipt_review",
        "may_prepare_balance_learning_review",
    ):
        if not isinstance(permission.get(field), bool):
            blockers.append(f"{field}_not_boolean")
    for field in PERMISSION_FALSE_FIELDS:
        if _bool(permission.get(field)):
            blockers.append(f"{field}_true")
    if not _bool(permission.get("owner_runtime_packet_required_for_execution")):
        blockers.append("owner_runtime_packet_required_for_execution_false")
    return tuple(_unique(blockers))


def _risk_blockers(risk: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if _bool(risk.get("kill_switch_active")):
        blockers.append("kill_switch_active_true")
    if _bool(risk.get("daily_loss_stop_active")):
        blockers.append("daily_loss_stop_active_true")
    if not _bool(risk.get("drawdown_within_limit")):
        blockers.append("drawdown_within_limit_false")
    current_drawdown = _number(risk.get("current_drawdown_pct"))
    max_drawdown = _number(risk.get("max_drawdown_pct"))
    current_daily_loss = _number(risk.get("current_daily_loss_pct"))
    max_daily_loss = _number(risk.get("max_daily_loss_pct"))
    max_risk_per_trade = _number(risk.get("max_risk_per_trade_pct"))
    max_total_burst = _number(risk.get("max_total_burst_risk_pct"))
    for field in (
        "current_drawdown_pct",
        "max_drawdown_pct",
        "current_daily_loss_pct",
        "max_daily_loss_pct",
        "max_risk_per_trade_pct",
        "max_total_burst_risk_pct",
    ):
        if not _is_number(risk.get(field)):
            blockers.append(f"{field}_not_number")
    if current_drawdown > max_drawdown:
        blockers.append("current_drawdown_exceeds_max_drawdown")
    if current_daily_loss > max_daily_loss:
        blockers.append("current_daily_loss_exceeds_max_daily_loss")
    if max_risk_per_trade > 0.01:
        blockers.append("max_risk_per_trade_pct_above_0_01")
    if max_total_burst > 0.03:
        blockers.append("max_total_burst_risk_pct_above_0_03")
    if not _bool(risk.get("risk_policy_owner_reviewed")):
        blockers.append("risk_policy_owner_reviewed_false")
    return tuple(_unique(blockers))


def _receipt_blockers(receipt: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if not _bool(receipt.get("receipt_required_after_execution")):
        blockers.append("receipt_required_after_execution_false")
    if not _bool(receipt.get("receipts_sanitized")):
        blockers.append("receipts_sanitized_false")
    if not _bool(receipt.get("post_trade_review_complete")):
        blockers.append("post_trade_review_complete_false")
    if not _bool(receipt.get("next_trade_blocked_until_receipts_reviewed")):
        blockers.append("next_trade_blocked_until_receipts_reviewed_false")
    return tuple(_unique(blockers))


def _balance_blockers(balance: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if not _bool(balance.get("balance_memory_ready")):
        blockers.append("balance_memory_ready_false")
    if not _bool(balance.get("compounding_observer_ready")):
        blockers.append("compounding_observer_ready_false")
    if not _bool(balance.get("withdrawal_deferred")):
        blockers.append("withdrawal_deferred_false")
    if not _bool(balance.get("bank_routing_deferred")):
        blockers.append("bank_routing_deferred_false")
    if _bool(balance.get("money_moved")):
        blockers.append("balance_money_moved_true")
    for field in ("current_balance_present", "current_equity_present"):
        if not isinstance(balance.get(field), bool):
            blockers.append(f"{field}_not_boolean")
    return tuple(_unique(blockers))


def _balance_review_blockers(blockers: Sequence[str]) -> bool:
    review_terms = {
        "balance_memory_ready_false",
        "compounding_observer_ready_false",
        "current_balance_present_not_boolean",
        "current_equity_present_not_boolean",
    }
    return any(blocker in review_terms for blocker in blockers)


def _compounding_blockers(compounding: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if not _bool(compounding.get("compounding_scale_ready")):
        blockers.append("compounding_scale_ready_false")
    if not _present(compounding.get("compounding_status")):
        blockers.append("compounding_status_missing")
    if not _present(compounding.get("scale_decision")):
        blockers.append("scale_decision_missing")
    if not _present(compounding.get("scale_direction")):
        blockers.append("scale_direction_missing")
    if not _is_number(compounding.get("proposed_next_risk_budget_pct")):
        blockers.append("proposed_next_risk_budget_pct_not_number")
    if not _bool(compounding.get("owner_decision_required")):
        blockers.append("compounding_owner_decision_required_false")
    if _bool(compounding.get("money_moved")):
        blockers.append("compounding_money_moved_true")
    if _bool(compounding.get("withdrawal_allowed_by_this_module")):
        blockers.append("compounding_withdrawal_allowed_true")
    if _bool(compounding.get("bank_routing_allowed_by_this_module")):
        blockers.append("compounding_bank_routing_allowed_true")
    return tuple(_unique(blockers))


def _profit_protection_blockers(profit: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if not _bool(profit.get("profit_protection_ready")):
        blockers.append("profit_protection_ready_false")
    if not _present(profit.get("profit_protection_status")):
        blockers.append("profit_protection_status_missing")
    if not _bool(profit.get("realized_profit_only")):
        blockers.append("realized_profit_only_false")
    if not isinstance(profit.get("withdrawal_review_future_enabled"), bool):
        blockers.append("withdrawal_review_future_enabled_not_boolean")
    if _bool(profit.get("withdrawal_execution_allowed")):
        blockers.append("profit_withdrawal_execution_allowed_true")
    if _bool(profit.get("bank_routing_allowed")):
        blockers.append("profit_bank_routing_allowed_true")
    if _bool(profit.get("money_moved")):
        blockers.append("profit_money_moved_true")
    return tuple(_unique(blockers))


def _proof_waiting_blockers(proof: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if _bool(proof.get("proof_required")) and not _bool(proof.get("proof_ready")):
        blockers.append("proof_required_but_not_ready")
    if not _bool(proof.get("proof_continuity_ready")):
        blockers.append("proof_continuity_ready_false")
    if not _bool(proof.get("repeatability_review_ready")):
        blockers.append("repeatability_review_ready_false")
    return tuple(_unique(blockers))


def _proof_blockers(proof: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if not _bool(proof.get("proof_required")):
        blockers.append("proof_required_false")
    if not _bool(proof.get("fake_proof_blocked")):
        blockers.append("fake_proof_blocked_false")
    if not _bool(proof.get("owner_review_required_for_live")):
        blockers.append("owner_review_required_for_live_false")
    return tuple(_unique(blockers))


def _candidate_policy_blockers(candidate: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    true_required = (
        "candidate_refresh_metadata_allowed",
        "require_stop_loss",
        "require_take_profit",
        "require_spread_policy",
        "require_slippage_policy",
        "require_news_blackout_policy",
        "owner_runtime_packet_required_for_execution",
    )
    for field in true_required:
        if not _bool(candidate.get(field)):
            blockers.append(f"{field}_false")
    false_required = (
        "strategy_mutation_allowed",
        "broker_call_allowed",
        "live_market_data_call_allowed",
    )
    for field in false_required:
        if _bool(candidate.get(field)):
            blockers.append(f"{field}_true")
    return tuple(_unique(blockers))


def _profit_claim_blockers(claims: Mapping[str, Any]) -> tuple[str, ...]:
    missing = _missing_fields(claims, CLAIM_FIELDS, "claims")
    if missing:
        return missing
    return tuple(f"{field}_true" for field in CLAIM_FIELDS if _bool(claims.get(field)))


def _supervision_job_queue(status: str) -> list[dict[str, Any]]:
    allowed_now = status in {
        ACTIVE_SUPERVISION_READY,
        ACTIVE_SUPERVISION_METADATA_SCAN_READY,
    }
    return [
        {
            "job_id": job_id,
            "priority": priority,
            "allowed_now": allowed_now,
            "requires_owner_packet": job_id
            in {
                "candidate_metadata_refresh",
                "owner_alert_readiness",
            },
            "requires_runtime_permission": True,
            "reason": _job_reason(job_id, status),
            "prohibited_actions": list(BLOCKED_ACTION_IDS),
        }
        for job_id, priority in SUPERVISION_JOB_SPECS
    ]


def _job_reason(job_id: str, status: str) -> str:
    if status in {ACTIVE_SUPERVISION_READY, ACTIVE_SUPERVISION_METADATA_SCAN_READY}:
        return f"{job_id} is ready for metadata-only active supervision."
    return f"{job_id} is held until status {status} is repaired or routed."


def _blocked_action_queue() -> list[dict[str, Any]]:
    return [
        {
            "action_id": action_id,
            "allowed_now": False,
            "reason": "This packet is metadata-only and cannot execute runtime, broker, credential, money, scheduler, daemon, strategy, or profit-claim actions.",
        }
        for action_id in BLOCKED_ACTION_IDS
    ]


def _deferred_job_queue(status: str) -> list[dict[str, str]]:
    if status == ACTIVE_SUPERVISION_MAINTENANCE_FALLBACK:
        return [
            {
                "job_id": "runtime_active_supervision",
                "deferred_until": "Vacation Mode returns to ON or RESUME during an open trade window.",
                "reason": "Vacation Mode is not in active supervision posture.",
            }
        ]
    if status == ACTIVE_SUPERVISION_WAITING_FOR_PROOF:
        return [
            {
                "job_id": "runtime_execution_owner_packet",
                "deferred_until": "Proof continuity is ready.",
                "reason": "Proof state is not continuous enough for active supervision readiness.",
            }
        ]
    if status == ACTIVE_SUPERVISION_WAITING_FOR_RECEIPTS:
        return [
            {
                "job_id": "candidate_refresh_after_receipts",
                "deferred_until": "Outstanding receipts and post-trade review are clean.",
                "reason": "Receipt watch must close before the next trade lane.",
            }
        ]
    if status.startswith("BLOCKED") or status == INCOMPLETE_INPUTS:
        return [
            {
                "job_id": "active_supervision_ready_state",
                "deferred_until": "Blocking metadata is repaired.",
                "reason": "Blocked status prevents active supervision readiness.",
            }
        ]
    return []


def _owner_review_queue(status: str) -> list[dict[str, Any]]:
    return [
        {
            "review_id": review_id,
            "required_now": _review_required_now(review_id, status),
            "reason": _review_reason(review_id, status),
        }
        for review_id in OWNER_REVIEW_IDS
    ]


def _review_required_now(review_id: str, status: str) -> bool:
    if review_id == "runtime_execution_packet_required_for_any_order":
        return True
    if review_id == "active_supervision_owner_summary_review":
        return status in {
            ACTIVE_SUPERVISION_READY,
            ACTIVE_SUPERVISION_METADATA_SCAN_READY,
            ACTIVE_SUPERVISION_OWNER_REVIEW_REQUIRED,
        }
    if review_id == "proof_and_receipt_review_if_pending":
        return status in {
            ACTIVE_SUPERVISION_WAITING_FOR_PROOF,
            ACTIVE_SUPERVISION_WAITING_FOR_RECEIPTS,
            BLOCKED_BY_RECEIPT_STATE,
            BLOCKED_BY_PROOF_STATE,
        }
    if review_id == "balance_and_compounding_review_if_pending":
        return status in {
            ACTIVE_SUPERVISION_BALANCE_REVIEW_REQUIRED,
            ACTIVE_SUPERVISION_COMPOUNDING_REVIEW_REQUIRED,
            BLOCKED_BY_BALANCE_STATE,
            BLOCKED_BY_COMPOUNDING_STATE,
        }
    if review_id == "profit_protection_review_if_pending":
        return status in {
            ACTIVE_SUPERVISION_PROFIT_PROTECTION_REVIEW_REQUIRED,
            BLOCKED_BY_PROFIT_PROTECTION_STATE,
        }
    if review_id == "kill_switch_review_if_active":
        return status == BLOCKED_BY_RISK_STATE
    if review_id == "risk_review_if_breached":
        return status in {BLOCKED_BY_RISK_STATE, BLOCKED_BY_POLICY}
    return False


def _review_reason(review_id: str, status: str) -> str:
    if review_id == "runtime_execution_packet_required_for_any_order":
        return "Any order still needs a later owner-approved runtime execution packet."
    return f"{review_id} is tracked for status {status}."


def _risk_watch_summary(risk: Mapping[str, Any], status: str) -> dict[str, Any]:
    return {
        "status": status,
        "kill_switch_active": _bool(risk.get("kill_switch_active")),
        "daily_loss_stop_active": _bool(risk.get("daily_loss_stop_active")),
        "drawdown_within_limit": _bool(risk.get("drawdown_within_limit")),
        "current_drawdown_pct": _round(_number(risk.get("current_drawdown_pct"))),
        "max_drawdown_pct": _round(_number(risk.get("max_drawdown_pct"))),
        "current_daily_loss_pct": _round(_number(risk.get("current_daily_loss_pct"))),
        "max_daily_loss_pct": _round(_number(risk.get("max_daily_loss_pct"))),
        "max_risk_per_trade_pct": _round(_number(risk.get("max_risk_per_trade_pct"))),
        "max_total_burst_risk_pct": _round(_number(risk.get("max_total_burst_risk_pct"))),
        "risk_policy_owner_reviewed": _bool(risk.get("risk_policy_owner_reviewed")),
    }


def _receipt_watch_summary(receipt: Mapping[str, Any], status: str) -> dict[str, Any]:
    return {
        "status": status,
        "receipt_required_after_execution": _bool(receipt.get("receipt_required_after_execution")),
        "outstanding_receipts": _bool(receipt.get("outstanding_receipts")),
        "receipts_sanitized": _bool(receipt.get("receipts_sanitized")),
        "post_trade_review_complete": _bool(receipt.get("post_trade_review_complete")),
        "next_trade_blocked_until_receipts_reviewed": _bool(
            receipt.get("next_trade_blocked_until_receipts_reviewed")
        ),
    }


def _balance_watch_summary(balance: Mapping[str, Any], status: str) -> dict[str, Any]:
    return {
        "status": status,
        "balance_memory_ready": _bool(balance.get("balance_memory_ready")),
        "compounding_observer_ready": _bool(balance.get("compounding_observer_ready")),
        "withdrawal_deferred": _bool(balance.get("withdrawal_deferred")),
        "bank_routing_deferred": _bool(balance.get("bank_routing_deferred")),
        "money_moved": False,
        "current_balance_present": _bool(balance.get("current_balance_present")),
        "current_equity_present": _bool(balance.get("current_equity_present")),
    }


def _compounding_watch_summary(compounding: Mapping[str, Any], status: str) -> dict[str, Any]:
    return {
        "status": status,
        "compounding_scale_ready": _bool(compounding.get("compounding_scale_ready")),
        "compounding_status": str(compounding.get("compounding_status", "")),
        "scale_decision": str(compounding.get("scale_decision", "")),
        "scale_direction": str(compounding.get("scale_direction", "")),
        "proposed_next_risk_budget_pct": _round(
            _number(compounding.get("proposed_next_risk_budget_pct"))
        ),
        "owner_decision_required": _bool(compounding.get("owner_decision_required")),
        "money_moved": False,
        "withdrawal_allowed_by_this_module": False,
        "bank_routing_allowed_by_this_module": False,
    }


def _profit_protection_watch_summary(profit: Mapping[str, Any], status: str) -> dict[str, Any]:
    return {
        "status": status,
        "profit_protection_ready": _bool(profit.get("profit_protection_ready")),
        "profit_protection_status": str(profit.get("profit_protection_status", "")),
        "realized_profit_only": _bool(profit.get("realized_profit_only")),
        "withdrawal_review_future_enabled": _bool(
            profit.get("withdrawal_review_future_enabled")
        ),
        "withdrawal_execution_allowed": False,
        "bank_routing_allowed": False,
        "money_moved": False,
    }


def _proof_watch_summary(proof: Mapping[str, Any], status: str) -> dict[str, Any]:
    return {
        "status": status,
        "proof_required": _bool(proof.get("proof_required")),
        "proof_ready": _bool(proof.get("proof_ready")),
        "proof_continuity_ready": _bool(proof.get("proof_continuity_ready")),
        "fake_proof_blocked": _bool(proof.get("fake_proof_blocked")),
        "repeatability_review_ready": _bool(proof.get("repeatability_review_ready")),
        "owner_review_required_for_live": _bool(proof.get("owner_review_required_for_live")),
    }


def _candidate_refresh_summary(candidate: Mapping[str, Any], status: str) -> dict[str, Any]:
    return {
        "status": status,
        "candidate_refresh_metadata_allowed": _bool(
            candidate.get("candidate_refresh_metadata_allowed")
        ),
        "strategy_mutation_allowed": False,
        "broker_call_allowed": False,
        "live_market_data_call_allowed": False,
        "require_stop_loss": _bool(candidate.get("require_stop_loss")),
        "require_take_profit": _bool(candidate.get("require_take_profit")),
        "require_spread_policy": _bool(candidate.get("require_spread_policy")),
        "require_slippage_policy": _bool(candidate.get("require_slippage_policy")),
        "require_news_blackout_policy": _bool(candidate.get("require_news_blackout_policy")),
        "owner_runtime_packet_required_for_execution": True,
    }


def _owner_alert_summary(
    vacation: Mapping[str, Any],
    risk: Mapping[str, Any],
    proof: Mapping[str, Any],
    blockers: Sequence[str],
) -> dict[str, Any]:
    return {
        "owner_alert_ready": True,
        "owner_attention_required": _bool(vacation.get("owner_attention_required"))
        or bool(blockers),
        "kill_switch_alert": _bool(risk.get("kill_switch_active")),
        "daily_loss_stop_alert": _bool(risk.get("daily_loss_stop_active")),
        "proof_alert": _bool(proof.get("proof_required")) and not _bool(proof.get("proof_ready")),
        "blocker_count": len(_unique(blockers)),
    }


def _safety_summary() -> dict[str, bool]:
    return {
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        "no_trade_execution": True,
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
        ACTIVE_SUPERVISION_READY: "AIOS_FOREX_OWNER_APPROVED_DEMO_MULTI_PAIR_BURST_RUNTIME_EXECUTION_V1",
        ACTIVE_SUPERVISION_METADATA_SCAN_READY: "AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1",
        ACTIVE_SUPERVISION_OWNER_REVIEW_REQUIRED: "AIOS_FOREX_LIVE_MICRO_MULTI_PAIR_BURST_OWNER_REVIEW_V1",
        ACTIVE_SUPERVISION_MAINTENANCE_FALLBACK: "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1",
        ACTIVE_SUPERVISION_WAITING_FOR_PROOF: "AIOS_FOREX_PROOF_PIPELINE_PAUSE_AND_CONTINUE_V1",
        ACTIVE_SUPERVISION_WAITING_FOR_RECEIPTS: "AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1",
        ACTIVE_SUPERVISION_BALANCE_REVIEW_REQUIRED: "AIOS_FOREX_BALANCE_EQUITY_MEMORY_AND_COMPOUNDING_OBSERVER_V1",
        ACTIVE_SUPERVISION_COMPOUNDING_REVIEW_REQUIRED: "AIOS_FOREX_GOVERNED_COMPOUNDING_CAPITAL_SCALING_V1",
        ACTIVE_SUPERVISION_PROFIT_PROTECTION_REVIEW_REQUIRED: "AIOS_FOREX_PROFIT_PROTECTION_AND_WITHDRAWAL_REVIEW_FUTURE_V1",
        BLOCKED_BY_RISK_STATE: "AIOS_FOREX_RISK_SCALE_DOWN_REVIEW_V1",
        BLOCKED_BY_CALENDAR: "AIOS_FOREX_RUNTIME_CALENDAR_STATUS_AND_MAINTENANCE_MODE_V1",
        BLOCKED_BY_VACATION_MODE: "AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1",
        BLOCKED_BY_RECEIPT_STATE: "AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1",
    }
    return routes.get(status, NEXT_BEST_PACKET)


def _safe_manual_next_action(status: str) -> str:
    if status == ACTIVE_SUPERVISION_READY:
        return "Review active supervision summary; any order still needs a separate owner-approved runtime packet."
    if status == ACTIVE_SUPERVISION_METADATA_SCAN_READY:
        return "Run metadata-only candidate refresh without creating execution payloads."
    if status == ACTIVE_SUPERVISION_OWNER_REVIEW_REQUIRED:
        return "Complete owner review before preparing any runtime execution packet."
    if status == ACTIVE_SUPERVISION_MAINTENANCE_FALLBACK:
        return "Use maintenance workload while Vacation Mode is OFF or PAUSE."
    if status == ACTIVE_SUPERVISION_WAITING_FOR_PROOF:
        return "Repair proof continuity before active supervision readiness."
    if status == ACTIVE_SUPERVISION_WAITING_FOR_RECEIPTS:
        return "Capture and sanitize receipts before the next trade lane."
    if status == ACTIVE_SUPERVISION_BALANCE_REVIEW_REQUIRED:
        return "Repair balance and equity memory readiness."
    if status == ACTIVE_SUPERVISION_COMPOUNDING_REVIEW_REQUIRED:
        return "Repair governed compounding scale metadata."
    if status == ACTIVE_SUPERVISION_PROFIT_PROTECTION_REVIEW_REQUIRED:
        return "Repair profit protection metadata before active supervision readiness."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys or secret-like values and rerun the metadata evaluator."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove active banking, withdrawal, transfer, or money-movement focus fields."
    if status == BLOCKED_BY_PROFIT_CLAIM:
        return "Remove profit guarantee and fixed-return claims."
    return "Repair the blocked metadata section and rerun active supervision status."


def _vacation_mode_active(vacation: Mapping[str, Any]) -> bool:
    return str(vacation.get("vacation_mode_toggle_state", "")) in {"ON", "RESUME"}


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
            key = str(raw_key).lower().replace("-", "_").replace(" ", "_")
            child_path = f"{path}.{raw_key}"
            if any(part in key for part in SENSITIVE_KEY_PARTS) and not _safe_sensitive_value(child):
                blockers.append(f"{child_path}:sensitive_key")
            blockers.extend(_sensitive_data_blockers(child, child_path))
        return tuple(_unique(blockers))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_sensitive_data_blockers(child, f"{path}[{index}]"))
        return tuple(_unique(blockers))
    if isinstance(value, str) and not _safe_sensitive_value(value) and _looks_secret_string(value):
        blockers.append(f"{path}:secret_like_value")
    return tuple(_unique(blockers))


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
            key = str(raw_key).lower().replace("-", "_").replace(" ", "_")
            child_path = f"{path}.{raw_key}"
            if key in PERMISSION_FALSE_FIELDS:
                blockers.extend(_banking_focus_blockers(child, child_path))
                continue
            if key in BANKING_ALLOWED_TRUE_FIELDS and child is True:
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
    if "money_movement" in key:
        return True
    tokens = set(key.split("_"))
    return any(token in BANKING_KEY_TOKENS for token in tokens)


def _active_focus(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        lowered = value.strip().lower()
        return lowered not in {"", "false", "0", "none", "off", "disabled"}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    if isinstance(value, Mapping):
        return bool(value)
    return True


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
