"""Classify Forex runtime calendar status and maintenance posture."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_multi_pair_universe_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_SENSITIVE_DATA,
    _bool,
    _mapping,
    _present,
    _unique,
    banking_focus_blockers,
    sensitive_data_blockers,
)

SCHEMA = "AIOS_FOREX_RUNTIME_CALENDAR_STATUS_AND_MAINTENANCE_MODE_V1"
MODE = "READ_ONLY_METADATA_ONLY_RUNTIME_CALENDAR_STATUS_AND_MAINTENANCE_MODE"

RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION = "RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION"
RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION = "RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION"
RUNTIME_MARKET_CLOSED_MAINTENANCE = "RUNTIME_MARKET_CLOSED_MAINTENANCE"
RUNTIME_MARKET_REOPEN_APPROACHING_PREP = "RUNTIME_MARKET_REOPEN_APPROACHING_PREP"
RUNTIME_WEEKEND_HEAVY_MAINTENANCE = "RUNTIME_WEEKEND_HEAVY_MAINTENANCE"
RUNTIME_HOLIDAY_DEGRADED_MAINTENANCE = "RUNTIME_HOLIDAY_DEGRADED_MAINTENANCE"
RUNTIME_LOW_LIQUIDITY_DEGRADED_MAINTENANCE = (
    "RUNTIME_LOW_LIQUIDITY_DEGRADED_MAINTENANCE"
)
VACATION_MODE_YEAR_ROUND_RUNTIME_READY = "VACATION_MODE_YEAR_ROUND_RUNTIME_READY"
BLOCKED_BY_CALENDAR_METADATA = "BLOCKED_BY_CALENDAR_METADATA"
BLOCKED_BY_PROFIT_CLAIM = "BLOCKED_BY_PROFIT_CLAIM"
BLOCKED_BY_AUTONOMY_DRIFT = "BLOCKED_BY_AUTONOMY_DRIFT"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_RUNTIME_CALENDAR_STATUS_AND_MAINTENANCE_MODE_V1"

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
    "live_profit_guaranteed",
    "daily_profit_guaranteed",
    "weekly_profit_guaranteed",
    "monthly_profit_guaranteed",
    "yearly_profit_guaranteed",
    "fixed_return_promised_by_aios",
)

RUNTIME_CALENDAR_REQUIRED_FIELDS = (
    "timezone",
    "forex_week_window_defined",
    "market_open",
    "close_approaching",
    "reopen_approaching",
    "weekend_closed",
    "holiday_degraded",
    "low_liquidity_degraded",
    "broker_calendar_source",
    "runtime_uses_declared_calendar_only",
    "no_live_execution_authorized_by_calendar",
)

RUNTIME_POLICY_REQUIRED_FIELDS = (
    "ai_runtime_supervision_continuous_when_host_available",
    "market_calendar_controls_trade_windows",
    "maintenance_windows_control_non_trade_work",
    "night_optimization_allowed",
    "weekend_heavy_maintenance_allowed",
    "post_close_maintenance_allowed",
    "pre_open_preparation_allowed",
    "close_protection_required",
    "no_scheduler_created",
    "no_daemon_created",
    "no_runtime_trade_without_owner_gate",
    "no_unlimited_autonomous_trading",
)

CADENCE_REQUIRED_FIELDS = (
    "daily_weekly_monthly_are_review_cadence",
    "yearly_means_vacation_mode_maturity",
    "yearly_profit_guarantee",
    "daily_profit_guarantee",
    "weekly_profit_guarantee",
    "monthly_profit_guarantee",
    "fixed_return_promised",
)

CALENDAR_TRUE_FIELDS = (
    "forex_week_window_defined",
    "runtime_uses_declared_calendar_only",
    "no_live_execution_authorized_by_calendar",
)

POLICY_TRUE_FIELDS = (
    "ai_runtime_supervision_continuous_when_host_available",
    "market_calendar_controls_trade_windows",
    "maintenance_windows_control_non_trade_work",
    "night_optimization_allowed",
    "weekend_heavy_maintenance_allowed",
    "post_close_maintenance_allowed",
    "pre_open_preparation_allowed",
    "close_protection_required",
    "no_scheduler_created",
    "no_daemon_created",
    "no_runtime_trade_without_owner_gate",
    "no_unlimited_autonomous_trading",
)

CADENCE_TRUE_FIELDS = (
    "daily_weekly_monthly_are_review_cadence",
    "yearly_means_vacation_mode_maturity",
)

PROFIT_CLAIM_FIELDS = (
    "yearly_profit_guarantee",
    "daily_profit_guarantee",
    "weekly_profit_guarantee",
    "monthly_profit_guarantee",
    "fixed_return_promised",
)

MAINTENANCE_WORKLOAD_KEYS = (
    "evidence_compaction",
    "receipt_review",
    "pnl_review",
    "spread_slippage_review",
    "replay_validation",
    "walk_forward_review",
    "strategy_retirement_review",
    "risk_policy_review",
    "report_cleanup",
    "next_session_candidate_prep",
    "dashboard_state_projection",
    "backup_snapshot_review",
    "pr_landing_prep",
)

BLOCKED_WORKLOAD_KEYS = (
    "live_trade_execution_by_this_module",
    "demo_trade_execution_by_this_module",
    "broker_call_by_this_module",
    "credential_read_by_this_module",
    "scheduler_creation_by_this_module",
    "daemon_creation_by_this_module",
    "dashboard_runtime_creation_by_this_module",
    "money_movement_by_this_module",
    "banking_work_by_this_module",
    "withdrawal_work_by_this_module",
    "transfer_work_by_this_module",
    "unlimited_autonomous_trading",
)

ROUTER_FIELDS = (
    "runtime_job_router_enabled",
    "current_runtime_posture",
    "primary_job_lane",
    "secondary_job_lanes",
    "job_queue",
    "owner_review_queue",
    "deferred_job_queue",
    "blocked_job_queue",
    "next_window_preparation",
    "vacation_mode_toggle_semantics",
    "kill_switch_semantics",
    "runtime_product_fit_summary",
)


def evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify declared calendar state without creating runtime side effects."""

    source = _mapping(payload)
    sensitive_blockers = sensitive_data_blockers(source)
    if sensitive_blockers:
        return _build_result(
            source=source,
            status=BLOCKED_BY_SENSITIVE_DATA,
            ready=False,
            blockers=sensitive_blockers,
            next_best_packet=NEXT_BEST_PACKET,
            safe_manual_next_action="Remove sensitive keys or values before calendar review.",
        )

    banking_blockers = _runtime_banking_focus_blockers(source)
    if banking_blockers:
        return _build_result(
            source=source,
            status=BLOCKED_BY_BANKING_FOCUS,
            ready=False,
            blockers=banking_blockers,
            next_best_packet=NEXT_BEST_PACKET,
            safe_manual_next_action="Remove banking, withdrawal, transfer, or money-movement focus fields.",
        )

    if not source:
        return _build_result(
            source=source,
            status=INCOMPLETE_INPUTS,
            ready=False,
            blockers=("payload_missing",),
        )

    calendar = _mapping(source.get("runtime_calendar"))
    policy = _mapping(source.get("runtime_policy"))
    cadence = _mapping(source.get("cadence_interpretation"))
    missing = _missing_required_sections(calendar, policy, cadence)
    if missing:
        return _build_result(
            source=source,
            status=INCOMPLETE_INPUTS,
            ready=False,
            blockers=missing,
        )

    profit_claims = tuple(field for field in PROFIT_CLAIM_FIELDS if cadence.get(field) is True)
    if profit_claims:
        return _build_result(
            source=source,
            status=BLOCKED_BY_PROFIT_CLAIM,
            ready=False,
            blockers=tuple(f"{field}_true" for field in profit_claims),
        )

    if policy.get("no_unlimited_autonomous_trading") is False:
        return _build_result(
            source=source,
            status=BLOCKED_BY_AUTONOMY_DRIFT,
            ready=False,
            blockers=("no_unlimited_autonomous_trading_false",),
        )

    calendar_blockers = _calendar_metadata_blockers(calendar, policy, cadence)
    if calendar_blockers:
        return _build_result(
            source=source,
            status=BLOCKED_BY_CALENDAR_METADATA,
            ready=False,
            blockers=calendar_blockers,
        )

    status = _status_from_calendar(calendar, policy, cadence)
    ready = status not in {
        BLOCKED_BY_CALENDAR_METADATA,
        BLOCKED_BY_PROFIT_CLAIM,
        BLOCKED_BY_AUTONOMY_DRIFT,
        BLOCKED_BY_SENSITIVE_DATA,
        BLOCKED_BY_BANKING_FOCUS,
        INCOMPLETE_INPUTS,
    }
    return _build_result(
        source=source,
        status=status,
        ready=ready,
        blockers=(),
        next_best_packet=_next_packet(status),
        safe_manual_next_action=_safe_manual_next_action(status),
    )


def _status_from_calendar(
    calendar: Mapping[str, Any],
    policy: Mapping[str, Any],
    cadence: Mapping[str, Any],
) -> str:
    vacation_ready = _vacation_mode_year_round_ready(policy, cadence)
    vacation_review_requested = (
        _bool(calendar.get("vacation_mode_year_round_runtime_review_requested"))
        or _bool(policy.get("vacation_mode_year_round_runtime_review_requested"))
    )
    if vacation_ready and vacation_review_requested:
        return VACATION_MODE_YEAR_ROUND_RUNTIME_READY
    if _bool(calendar.get("weekend_closed")):
        return RUNTIME_WEEKEND_HEAVY_MAINTENANCE
    if _bool(calendar.get("holiday_degraded")):
        return RUNTIME_HOLIDAY_DEGRADED_MAINTENANCE
    if _bool(calendar.get("low_liquidity_degraded")):
        return RUNTIME_LOW_LIQUIDITY_DEGRADED_MAINTENANCE
    if _bool(calendar.get("market_open")) and _bool(calendar.get("close_approaching")):
        return RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION
    if _bool(calendar.get("market_open")):
        return RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION
    if _bool(calendar.get("reopen_approaching")):
        return RUNTIME_MARKET_REOPEN_APPROACHING_PREP
    return RUNTIME_MARKET_CLOSED_MAINTENANCE


def _build_result(
    *,
    source: Mapping[str, Any],
    status: str,
    ready: bool,
    blockers: Sequence[str],
    next_best_packet: str = NEXT_BEST_PACKET,
    safe_manual_next_action: str | None = None,
) -> dict[str, Any]:
    calendar = _mapping(source.get("runtime_calendar"))
    policy = _mapping(source.get("runtime_policy"))
    cadence = _mapping(source.get("cadence_interpretation"))
    blocker_list = list(_unique(blockers))
    trade_window_open = _trade_window_open(status, calendar)
    maintenance_recommended = _maintenance_window_recommended(status)
    next_session_prep = status == RUNTIME_MARKET_REOPEN_APPROACHING_PREP
    close_protection = status == RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION
    vacation_ready = _vacation_mode_year_round_ready(policy, cadence) and not blocker_list
    runtime_supervision_requested = _runtime_supervision_requested(source, policy)
    router_enabled = bool(ready) and not blocker_list
    posture = _current_runtime_posture(status)
    primary_lane = _primary_job_lane(status)
    job_queue = _job_queue(status, router_enabled)
    deferred_jobs = _deferred_job_queue(status)
    blocked_jobs = _blocked_job_queue()
    owner_reviews = _owner_review_queue(status, next_best_packet)
    next_window_preparation = _next_window_preparation(status)
    result = {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": bool(ready),
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        "runtime_supervision_requested": runtime_supervision_requested,
        "market_calendar_enabled": _bool(calendar.get("runtime_uses_declared_calendar_only")),
        "maintenance_mode_supported": _maintenance_supported(policy),
        "trade_window_open": trade_window_open,
        "maintenance_window_recommended": maintenance_recommended,
        "next_session_prep_recommended": next_session_prep,
        "close_protection_recommended": close_protection,
        "vacation_mode_year_round_ready": vacation_ready,
        "runtime_calendar_summary": _runtime_calendar_summary(calendar, status),
        "maintenance_workload": _maintenance_workload(status),
        "blocked_workload": _blocked_workload(),
        "cadence_interpretation_summary": _cadence_summary(cadence),
        "runtime_job_router_enabled": router_enabled,
        "current_runtime_posture": posture,
        "primary_job_lane": primary_lane,
        "secondary_job_lanes": _secondary_job_lanes(status),
        "job_queue": job_queue,
        "owner_review_queue": owner_reviews,
        "deferred_job_queue": deferred_jobs,
        "blocked_job_queue": blocked_jobs,
        "next_window_preparation": next_window_preparation,
        "vacation_mode_toggle_semantics": _vacation_mode_toggle_semantics(),
        "kill_switch_semantics": _kill_switch_semantics(),
        "runtime_product_fit_summary": _runtime_product_fit_summary(cadence),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": safe_manual_next_action or _safe_manual_next_action(status),
        "blockers": blocker_list,
        "audit_record": {
            "schema": SCHEMA,
            "mode": MODE,
            "status": status,
            "ready": bool(ready),
            "runtime_supervision_requested": runtime_supervision_requested,
            "market_calendar_enabled": _bool(calendar.get("runtime_uses_declared_calendar_only")),
            "maintenance_mode_supported": _maintenance_supported(policy),
            "trade_window_open": trade_window_open,
            "runtime_job_router_enabled": router_enabled,
            "current_runtime_posture": posture,
            "primary_job_lane": primary_lane,
            "blockers": blocker_list,
            "next_best_packet": next_best_packet,
            "read_only": True,
            "metadata_only": True,
        },
        "safety": _safety_summary(),
        "withdrawal_built": False,
        "bank_routing_built": False,
        **{field: False for field in HARD_FALSE_FIELDS},
    }
    return result


def _missing_required_sections(
    calendar: Mapping[str, Any],
    policy: Mapping[str, Any],
    cadence: Mapping[str, Any],
) -> tuple[str, ...]:
    missing: list[str] = []
    if not calendar:
        missing.append("runtime_calendar_missing")
    if not policy:
        missing.append("runtime_policy_missing")
    if not cadence:
        missing.append("cadence_interpretation_missing")
    missing.extend(f"missing_runtime_calendar_{field}" for field in RUNTIME_CALENDAR_REQUIRED_FIELDS if field not in calendar)
    missing.extend(f"missing_runtime_policy_{field}" for field in RUNTIME_POLICY_REQUIRED_FIELDS if field not in policy)
    missing.extend(f"missing_cadence_interpretation_{field}" for field in CADENCE_REQUIRED_FIELDS if field not in cadence)
    for field in ("market_open", "close_approaching", "reopen_approaching", "weekend_closed", "holiday_degraded", "low_liquidity_degraded"):
        if field in calendar and not isinstance(calendar.get(field), bool):
            missing.append(f"runtime_calendar_{field}_not_boolean")
    return tuple(_unique(missing))


def _runtime_banking_focus_blockers(source: Mapping[str, Any]) -> tuple[str, ...]:
    allowed_calendar_terms = (
        "payload.runtime_calendar.close_approaching:banking_focus",
        "payload.runtime_calendar.reopen_approaching:banking_focus",
    )
    allowed_false_root_terms = {
        "payload.withdrawal_built:banking_focus": source.get("withdrawal_built") is False,
        "payload.bank_routing_built:banking_focus": source.get("bank_routing_built") is False,
    }
    return tuple(
        blocker
        for blocker in banking_focus_blockers(source)
        if blocker not in allowed_calendar_terms and not allowed_false_root_terms.get(blocker, False)
    )


def _calendar_metadata_blockers(
    calendar: Mapping[str, Any],
    policy: Mapping[str, Any],
    cadence: Mapping[str, Any],
) -> tuple[str, ...]:
    blockers: list[str] = []
    if not _present(calendar.get("timezone")):
        blockers.append("runtime_calendar_timezone_missing")
    if not _present(calendar.get("broker_calendar_source")):
        blockers.append("runtime_calendar_broker_calendar_source_missing")
    blockers.extend(f"runtime_calendar_{field}_not_true" for field in CALENDAR_TRUE_FIELDS if calendar.get(field) is not True)
    blockers.extend(f"runtime_policy_{field}_not_true" for field in POLICY_TRUE_FIELDS if policy.get(field) is not True)
    blockers.extend(f"cadence_interpretation_{field}_not_true" for field in CADENCE_TRUE_FIELDS if cadence.get(field) is not True)
    blockers.extend(f"cadence_interpretation_{field}_not_false" for field in PROFIT_CLAIM_FIELDS if cadence.get(field) is not False)
    return tuple(_unique(blockers))


def _runtime_calendar_summary(calendar: Mapping[str, Any], status: str) -> dict[str, Any]:
    return {
        "timezone": str(calendar.get("timezone", "")),
        "broker_calendar_source_present": _present(calendar.get("broker_calendar_source")),
        "forex_week_window_defined": _bool(calendar.get("forex_week_window_defined")),
        "market_open": _bool(calendar.get("market_open")),
        "close_approaching": _bool(calendar.get("close_approaching")),
        "reopen_approaching": _bool(calendar.get("reopen_approaching")),
        "weekend_closed": _bool(calendar.get("weekend_closed")),
        "holiday_degraded": _bool(calendar.get("holiday_degraded")),
        "low_liquidity_degraded": _bool(calendar.get("low_liquidity_degraded")),
        "runtime_uses_declared_calendar_only": _bool(calendar.get("runtime_uses_declared_calendar_only")),
        "calendar_authorizes_live_execution": False,
        "status": status,
    }


def _cadence_summary(cadence: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "daily_weekly_monthly_are_review_cadence": _bool(cadence.get("daily_weekly_monthly_are_review_cadence")),
        "yearly_means_vacation_mode_maturity": _bool(cadence.get("yearly_means_vacation_mode_maturity")),
        "daily_profit_guarantee": False,
        "weekly_profit_guarantee": False,
        "monthly_profit_guarantee": False,
        "yearly_profit_guarantee": False,
        "fixed_return_promised": False,
        "profit_frequency_is_not_guaranteed": True,
    }


def _maintenance_workload(status: str) -> dict[str, str]:
    if status in {
        RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION,
        RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION,
    }:
        label = "AVAILABLE_FOR_REVIEW_WHEN_NOT_COMPETING_WITH_PROTECTION"
    elif status == RUNTIME_MARKET_REOPEN_APPROACHING_PREP:
        label = "RECOMMENDED_FOR_NEXT_SESSION_PREP"
    else:
        label = "RECOMMENDED_DURING_CLOSED_OR_DEGRADED_WINDOW"
    return {key: label for key in MAINTENANCE_WORKLOAD_KEYS}


def _blocked_workload() -> dict[str, str]:
    return {key: "BLOCKED_BY_THIS_METADATA_MODULE" for key in BLOCKED_WORKLOAD_KEYS}


def _current_runtime_posture(status: str) -> str:
    mapping = {
        RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION: "ACTIVE_SUPERVISION",
        RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION: "CLOSE_PROTECTION",
        RUNTIME_MARKET_CLOSED_MAINTENANCE: "CLOSED_MAINTENANCE",
        RUNTIME_MARKET_REOPEN_APPROACHING_PREP: "REOPEN_PREPARATION",
        RUNTIME_WEEKEND_HEAVY_MAINTENANCE: "WEEKEND_HEAVY_MAINTENANCE",
        RUNTIME_HOLIDAY_DEGRADED_MAINTENANCE: "HOLIDAY_DEGRADED_MAINTENANCE",
        RUNTIME_LOW_LIQUIDITY_DEGRADED_MAINTENANCE: "LOW_LIQUIDITY_MAINTENANCE",
        VACATION_MODE_YEAR_ROUND_RUNTIME_READY: "VACATION_MODE_YEAR_ROUND_REVIEW",
    }
    return mapping.get(status, "BLOCKED")


def _primary_job_lane(status: str) -> str:
    mapping = {
        RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION: "supervise_runtime",
        RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION: "protect_close",
        RUNTIME_MARKET_CLOSED_MAINTENANCE: "maintain_evidence",
        RUNTIME_MARKET_REOPEN_APPROACHING_PREP: "prepare_next_session",
        RUNTIME_WEEKEND_HEAVY_MAINTENANCE: "weekend_audit",
        RUNTIME_HOLIDAY_DEGRADED_MAINTENANCE: "degraded_market_safety",
        RUNTIME_LOW_LIQUIDITY_DEGRADED_MAINTENANCE: "degraded_market_safety",
        VACATION_MODE_YEAR_ROUND_RUNTIME_READY: "vacation_mode_maturity_review",
    }
    return mapping.get(status, "blocked")


def _secondary_job_lanes(status: str) -> list[str]:
    mapping = {
        RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION: [
            "proof_continuity",
            "owner_alert_readiness",
            "candidate_metadata_refresh",
        ],
        RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION: [
            "receipt_capture",
            "post_close_maintenance_prep",
        ],
        RUNTIME_MARKET_CLOSED_MAINTENANCE: [
            "proof_review",
            "report_cleanup",
            "next_session_prep",
            "pr_landing_prep",
        ],
        RUNTIME_MARKET_REOPEN_APPROACHING_PREP: [
            "spread_slippage_policy_refresh",
            "owner_attention_readiness",
        ],
        RUNTIME_WEEKEND_HEAVY_MAINTENANCE: [
            "weekly_review",
            "walk_forward_review",
            "risk_policy_review",
            "pr_landing_prep",
        ],
        RUNTIME_HOLIDAY_DEGRADED_MAINTENANCE: [
            "maintenance_review",
            "risk_policy_review",
            "owner_alert_readiness",
        ],
        RUNTIME_LOW_LIQUIDITY_DEGRADED_MAINTENANCE: [
            "maintenance_review",
            "spread_slippage_review",
            "owner_alert_readiness",
        ],
        VACATION_MODE_YEAR_ROUND_RUNTIME_READY: [
            "owner_toggle_review",
            "proof_receipt_readiness",
            "runtime_boundary_review",
        ],
    }
    return list(mapping.get(status, ()))


def _job_queue(status: str, router_enabled: bool) -> list[dict[str, Any]]:
    specs = {
        RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION: (
            ("risk_status_check", "supervise_runtime", "P0"),
            ("kill_switch_state_check", "supervise_runtime", "P0"),
            ("spread_slippage_watch", "supervise_runtime", "P0"),
            ("receipt_capture_watch", "supervise_runtime", "P0"),
            ("owner_alert_readiness", "supervise_runtime", "P0"),
            ("candidate_refresh_metadata", "proof_continuity", "P1"),
            ("proof_continuity_check", "proof_continuity", "P1"),
        ),
        RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION: (
            ("no_new_risk_review", "protect_close", "P0"),
            ("open_intent_receipt_check", "protect_close", "P0"),
            ("close_boundary_protection", "protect_close", "P0"),
            ("owner_attention_if_unreviewed_receipts", "protect_close", "P0"),
            ("post_close_maintenance_prep", "maintain_evidence", "P1"),
        ),
        RUNTIME_MARKET_CLOSED_MAINTENANCE: (
            ("receipt_review", "maintain_evidence", "P0"),
            ("pnl_review", "maintain_evidence", "P0"),
            ("evidence_compaction", "maintain_evidence", "P1"),
            ("report_cleanup", "maintain_evidence", "P1"),
            ("replay_validation", "maintain_evidence", "P1"),
            ("next_session_candidate_prep", "prepare_next_session", "P1"),
            ("backup_snapshot_review", "maintain_evidence", "P1"),
            ("pr_landing_prep", "maintain_evidence", "P1"),
        ),
        RUNTIME_MARKET_REOPEN_APPROACHING_PREP: (
            ("next_session_candidate_prep", "prepare_next_session", "P0"),
            ("spread_slippage_policy_refresh", "prepare_next_session", "P0"),
            ("market_open_readiness_review", "prepare_next_session", "P1"),
            ("owner_attention_readiness", "prepare_next_session", "P1"),
        ),
        RUNTIME_WEEKEND_HEAVY_MAINTENANCE: (
            ("weekly_expectancy_review", "weekend_audit", "P0"),
            ("drawdown_review", "weekend_audit", "P0"),
            ("trade_quality_review", "weekend_audit", "P1"),
            ("report_cleanup", "weekend_audit", "P1"),
            ("evidence_compaction", "weekend_audit", "P1"),
            ("strategy_retirement_review", "weekend_audit", "P2"),
            ("walk_forward_review", "weekend_audit", "P2"),
            ("risk_policy_review", "weekend_audit", "P2"),
            ("backup_snapshot_review", "weekend_audit", "P2"),
            ("pr_landing_prep", "weekend_audit", "P2"),
        ),
        RUNTIME_HOLIDAY_DEGRADED_MAINTENANCE: (
            ("degraded_market_safety_review", "degraded_market_safety", "P0"),
            ("risk_policy_review", "degraded_market_safety", "P1"),
            ("receipt_review", "maintain_evidence", "P1"),
            ("report_cleanup", "maintain_evidence", "P2"),
        ),
        RUNTIME_LOW_LIQUIDITY_DEGRADED_MAINTENANCE: (
            ("degraded_market_safety_review", "degraded_market_safety", "P0"),
            ("spread_slippage_review", "degraded_market_safety", "P0"),
            ("risk_policy_review", "degraded_market_safety", "P1"),
            ("candidate_quality_review", "maintain_evidence", "P2"),
        ),
        VACATION_MODE_YEAR_ROUND_RUNTIME_READY: (
            ("vacation_mode_owner_toggle_review", "vacation_mode_maturity_review", "P0"),
            ("year_round_runtime_maturity_review", "vacation_mode_maturity_review", "P0"),
            ("proof_and_receipt_readiness_review", "vacation_mode_maturity_review", "P1"),
            ("broker_runtime_boundary_review", "vacation_mode_maturity_review", "P1"),
            ("banking_withdrawal_deferred_review", "vacation_mode_maturity_review", "P2"),
        ),
    }
    return [
        _job(
            job_id=job_id,
            job_lane=lane,
            priority=priority,
            allowed_now=router_enabled,
            reason=_job_reason(status, job_id),
        )
        for job_id, lane, priority in specs.get(status, ())
    ]


def _job(
    *,
    job_id: str,
    job_lane: str,
    priority: str,
    allowed_now: bool,
    reason: str,
) -> dict[str, Any]:
    return {
        "job_id": job_id,
        "job_lane": job_lane,
        "priority": priority,
        "allowed_now": bool(allowed_now),
        "requires_owner_packet": job_id in {
            "vacation_mode_owner_toggle_review",
            "broker_runtime_boundary_review",
        },
        "requires_runtime_permission": False,
        "reason": reason,
        "prohibited_actions": [
            "live_trade_execution",
            "demo_trade_execution",
            "broker_call",
            "credential_read",
            "money_movement",
            "scheduler_creation",
            "daemon_creation",
        ],
    }


def _job_reason(status: str, job_id: str) -> str:
    if status == RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION:
        return "Market is open; supervise declared state while owner, proof, risk, and runtime gates still control trade eligibility."
    if status == RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION:
        return "Close is approaching; protect boundaries and receipts before taking any new risk."
    if status == RUNTIME_MARKET_CLOSED_MAINTENANCE:
        return "Market is closed; use time for non-broker evidence and preparation work."
    if status == RUNTIME_MARKET_REOPEN_APPROACHING_PREP:
        return "Reopen is approaching; prepare metadata for the next declared market window."
    if status == RUNTIME_WEEKEND_HEAVY_MAINTENANCE:
        return "Weekend closure supports deeper review and audit work."
    if status in {
        RUNTIME_HOLIDAY_DEGRADED_MAINTENANCE,
        RUNTIME_LOW_LIQUIDITY_DEGRADED_MAINTENANCE,
    }:
        return "Declared degraded conditions shift work to safety and maintenance review."
    if status == VACATION_MODE_YEAR_ROUND_RUNTIME_READY:
        return "Vacation Mode maturity review requires owner-visible operation state decisions."
    return f"{job_id} is blocked until valid runtime calendar metadata is restored."


def _owner_review_queue(status: str, next_best_packet: str) -> list[dict[str, Any]]:
    if status == VACATION_MODE_YEAR_ROUND_RUNTIME_READY:
        reviews = (
            ("vacation_mode_owner_toggle_review", "OWNER_TOGGLE_STATE"),
            ("year_round_runtime_maturity_review", "YEAR_ROUND_RUNTIME_MATURITY"),
            ("proof_and_receipt_readiness_review", "PROOF_AND_RECEIPT_READINESS"),
            ("broker_runtime_boundary_review", "BROKER_RUNTIME_BOUNDARY"),
            ("banking_withdrawal_deferred_review", "BANKING_WITHDRAWAL_DEFERRED"),
        )
        return [
            {
                "review_id": review_id,
                "review_type": review_type,
                "required": True,
                "reason": "Vacation Mode maturity must be owner-visible and operation-state governed.",
                "next_packet": next_best_packet,
            }
            for review_id, review_type in reviews
        ]
    if status == RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION:
        return [
            {
                "review_id": "owner_attention_if_unreviewed_receipts",
                "review_type": "CLOSE_PROTECTION_RECEIPT_REVIEW",
                "required": True,
                "reason": "Close protection should surface unreviewed receipts before the window closes.",
                "next_packet": next_best_packet,
            }
        ]
    if status.startswith("BLOCKED") or status == INCOMPLETE_INPUTS:
        return [
            {
                "review_id": "repair_runtime_calendar_metadata",
                "review_type": "BLOCKED_METADATA_REPAIR",
                "required": True,
                "reason": "Runtime calendar router is blocked or incomplete.",
                "next_packet": NEXT_BEST_PACKET,
            }
        ]
    return []


def _deferred_job_queue(status: str) -> list[dict[str, str]]:
    deferred_by_status = {
        RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION: (
            ("weekend_heavy_audit", "weekend_closed", "Heavy audit belongs in weekend maintenance."),
            ("long_report_cleanup", "market_closed", "Long cleanup should wait for a maintenance window."),
            ("strategy_retirement_review", "weekend_closed", "Retirement review belongs in heavy maintenance."),
        ),
        RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION: (
            ("new_candidate_expansion", "next_open_window", "Close protection blocks new risk expansion."),
            ("long_report_cleanup", "market_closed", "Cleanup should wait for post-close maintenance."),
        ),
        RUNTIME_MARKET_CLOSED_MAINTENANCE: (
            ("active_spread_slippage_watch", "market_open", "Live watch belongs to an open supervision window."),
        ),
        RUNTIME_MARKET_REOPEN_APPROACHING_PREP: (
            ("weekend_heavy_audit", "weekend_closed", "Heavy audit should wait for weekend closure."),
        ),
        RUNTIME_WEEKEND_HEAVY_MAINTENANCE: (
            ("active_spread_slippage_watch", "market_open", "Live watch belongs to an open supervision window."),
        ),
        RUNTIME_HOLIDAY_DEGRADED_MAINTENANCE: (
            ("active_trade_seeking", "clear_open_market_window", "Holiday degraded state is maintenance-first."),
        ),
        RUNTIME_LOW_LIQUIDITY_DEGRADED_MAINTENANCE: (
            ("active_trade_seeking", "clear_liquid_market_window", "Low liquidity state is maintenance-first."),
        ),
        VACATION_MODE_YEAR_ROUND_RUNTIME_READY: (
            ("runtime_execution", "separate_owner_approved_runtime_packet", "Calendar maturity review does not execute."),
        ),
    }
    return [
        {"job_id": job_id, "deferred_until": deferred_until, "reason": reason}
        for job_id, deferred_until, reason in deferred_by_status.get(status, ())
    ]


def _blocked_job_queue() -> list[dict[str, Any]]:
    return [
        {
            "job_id": job_id,
            "allowed_now": False,
            "reason": "This metadata-only calendar router blocks runtime, broker, credential, banking, and autonomous execution work.",
        }
        for job_id in BLOCKED_WORKLOAD_KEYS
    ]


def _next_window_preparation(status: str) -> dict[str, Any]:
    if status == RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION:
        window = "current_open_window"
        jobs = ["candidate_refresh_metadata", "proof_continuity_check"]
        allowed = True
    elif status == RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION:
        window = "post_close_maintenance"
        jobs = ["post_close_maintenance_prep", "receipt_review"]
        allowed = True
    elif status == RUNTIME_MARKET_REOPEN_APPROACHING_PREP:
        window = "next_open_window"
        jobs = ["next_session_candidate_prep", "market_open_readiness_review"]
        allowed = True
    elif status == RUNTIME_WEEKEND_HEAVY_MAINTENANCE:
        window = "next_week_open_window"
        jobs = ["weekly_expectancy_review", "risk_policy_review", "next_session_candidate_prep"]
        allowed = True
    elif status == VACATION_MODE_YEAR_ROUND_RUNTIME_READY:
        window = "owner_governed_vacation_mode_operation"
        jobs = ["vacation_mode_owner_toggle_review", "proof_and_receipt_readiness_review"]
        allowed = True
    elif status in {
        RUNTIME_HOLIDAY_DEGRADED_MAINTENANCE,
        RUNTIME_LOW_LIQUIDITY_DEGRADED_MAINTENANCE,
        RUNTIME_MARKET_CLOSED_MAINTENANCE,
    }:
        window = "next_clear_market_window"
        jobs = ["next_session_candidate_prep", "risk_policy_review"]
        allowed = True
    else:
        window = "blocked_until_metadata_repair"
        jobs = []
        allowed = False
    return {
        "next_expected_window_type": window,
        "preparation_allowed": allowed,
        "preparation_jobs": jobs,
        "execution_authorized_by_calendar": False,
    }


def _vacation_mode_toggle_semantics() -> dict[str, bool]:
    return {
        "vacation_mode_on_means_request_governed_operation": True,
        "vacation_mode_off_means_stop_new_trade_seeking": True,
        "toggle_does_not_bypass_owner_gate": True,
        "toggle_does_not_bypass_market_calendar": True,
        "toggle_does_not_bypass_kill_switch": True,
        "toggle_does_not_authorize_withdrawal": True,
    }


def _kill_switch_semantics() -> dict[str, bool]:
    return {
        "kill_switch_is_emergency_hard_stop": True,
        "kill_switch_is_not_vacation_mode_toggle": True,
        "kill_switch_blocks_new_trades": True,
        "kill_switch_requires_owner_attention": True,
    }


def _runtime_product_fit_summary(cadence: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "designed_for_24_7_supervision_as_available": True,
        "trade_windows_calendar_gated": True,
        "maintenance_windows_used_productively": True,
        "daily_weekly_monthly_are_review_cadence": _bool(
            cadence.get("daily_weekly_monthly_are_review_cadence")
        ),
        "yearly_is_vacation_mode_maturity": _bool(
            cadence.get("yearly_means_vacation_mode_maturity")
        ),
        "banking_withdrawal_deferred": True,
        "broker_execution_requires_separate_owner_packet": True,
    }


def _trade_window_open(status: str, calendar: Mapping[str, Any]) -> bool:
    return (
        status == RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION
        and _bool(calendar.get("market_open"))
        and not _bool(calendar.get("weekend_closed"))
        and not _bool(calendar.get("holiday_degraded"))
        and not _bool(calendar.get("low_liquidity_degraded"))
    )


def _maintenance_window_recommended(status: str) -> bool:
    return status in {
        RUNTIME_MARKET_CLOSED_MAINTENANCE,
        RUNTIME_MARKET_REOPEN_APPROACHING_PREP,
        RUNTIME_WEEKEND_HEAVY_MAINTENANCE,
        RUNTIME_HOLIDAY_DEGRADED_MAINTENANCE,
        RUNTIME_LOW_LIQUIDITY_DEGRADED_MAINTENANCE,
    }


def _maintenance_supported(policy: Mapping[str, Any]) -> bool:
    return (
        _bool(policy.get("maintenance_windows_control_non_trade_work"))
        and _bool(policy.get("night_optimization_allowed"))
        and _bool(policy.get("weekend_heavy_maintenance_allowed"))
        and _bool(policy.get("post_close_maintenance_allowed"))
        and _bool(policy.get("pre_open_preparation_allowed"))
    )


def _vacation_mode_year_round_ready(
    policy: Mapping[str, Any],
    cadence: Mapping[str, Any],
) -> bool:
    return (
        _bool(policy.get("ai_runtime_supervision_continuous_when_host_available"))
        and _bool(policy.get("market_calendar_controls_trade_windows"))
        and _bool(policy.get("maintenance_windows_control_non_trade_work"))
        and _bool(policy.get("no_runtime_trade_without_owner_gate"))
        and _bool(policy.get("no_unlimited_autonomous_trading"))
        and _bool(cadence.get("daily_weekly_monthly_are_review_cadence"))
        and _bool(cadence.get("yearly_means_vacation_mode_maturity"))
        and all(cadence.get(field) is False for field in PROFIT_CLAIM_FIELDS)
    )


def _runtime_supervision_requested(
    source: Mapping[str, Any],
    policy: Mapping[str, Any],
) -> bool:
    return _bool(source.get("runtime_supervision_requested")) or _bool(
        policy.get("ai_runtime_supervision_continuous_when_host_available")
    )


def _safety_summary() -> dict[str, Any]:
    return {
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        "calendar_authorizes_live_execution": False,
        "no_broker_access": True,
        "no_credential_access": True,
        "no_money_movement": True,
        "no_scheduler_or_daemon_created": True,
        "withdrawal_built": False,
        "bank_routing_built": False,
        **{field: False for field in HARD_FALSE_FIELDS},
    }


def _next_packet(status: str) -> str:
    mapping = {
        RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION: "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1",
        RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION: "AIOS_FOREX_MARKET_CLOSE_PROTECTION_AND_RECEIPT_CAPTURE_V1",
        RUNTIME_MARKET_CLOSED_MAINTENANCE: "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1",
        RUNTIME_MARKET_REOPEN_APPROACHING_PREP: "AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1",
        RUNTIME_WEEKEND_HEAVY_MAINTENANCE: "AIOS_FOREX_WEEKEND_HEAVY_MAINTENANCE_AND_AUDIT_V1",
        RUNTIME_HOLIDAY_DEGRADED_MAINTENANCE: "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1",
        RUNTIME_LOW_LIQUIDITY_DEGRADED_MAINTENANCE: "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1",
        VACATION_MODE_YEAR_ROUND_RUNTIME_READY: "AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1",
    }
    return mapping.get(status, NEXT_BEST_PACKET)


def _safe_manual_next_action(status: str) -> str:
    if status == RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION:
        return "Continue active supervision using declared calendar status; owner and risk gates still govern trades."
    if status == RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION:
        return "Prefer close protection, receipt capture, and no-new-risk review."
    if status == RUNTIME_MARKET_CLOSED_MAINTENANCE:
        return "Shift to maintenance, proof review, replay, cleanup, and next-session planning."
    if status == RUNTIME_MARKET_REOPEN_APPROACHING_PREP:
        return "Prepare next-session candidates without broker calls or execution."
    if status == RUNTIME_WEEKEND_HEAVY_MAINTENANCE:
        return "Run weekend heavy maintenance planning and audit work only."
    if status in {
        RUNTIME_HOLIDAY_DEGRADED_MAINTENANCE,
        RUNTIME_LOW_LIQUIDITY_DEGRADED_MAINTENANCE,
    }:
        return "Use degraded-window maintenance and avoid execution intent escalation."
    if status == VACATION_MODE_YEAR_ROUND_RUNTIME_READY:
        return "Route to owner review for Vacation Mode year-round maturity; this module still executes nothing."
    if status == BLOCKED_BY_PROFIT_CLAIM:
        return "Remove daily, weekly, monthly, yearly, or fixed-return profit claims."
    if status == BLOCKED_BY_AUTONOMY_DRIFT:
        return "Restore no-unlimited-autonomous-trading metadata."
    if status == BLOCKED_BY_CALENDAR_METADATA:
        return "Repair declared calendar and runtime policy metadata."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys or values before calendar review."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove banking, withdrawal, transfer, or money-movement focus fields."
    return "Provide complete runtime calendar, runtime policy, and cadence metadata."
