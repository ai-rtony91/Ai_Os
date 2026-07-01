"""Metadata-only Forex runtime maintenance workload planner."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


SCHEMA = "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1"
MODE = "READ_ONLY_METADATA_ONLY_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN"

MAINTENANCE_WORKLOAD_PLAN_READY = "MAINTENANCE_WORKLOAD_PLAN_READY"
MAINTENANCE_EVIDENCE_REVIEW_READY = "MAINTENANCE_EVIDENCE_REVIEW_READY"
MAINTENANCE_RECEIPT_REVIEW_READY = "MAINTENANCE_RECEIPT_REVIEW_READY"
MAINTENANCE_PNL_REVIEW_READY = "MAINTENANCE_PNL_REVIEW_READY"
MAINTENANCE_REPLAY_VALIDATION_READY = "MAINTENANCE_REPLAY_VALIDATION_READY"
MAINTENANCE_REPORT_CLEANUP_READY = "MAINTENANCE_REPORT_CLEANUP_READY"
MAINTENANCE_BACKUP_SNAPSHOT_REVIEW_READY = (
    "MAINTENANCE_BACKUP_SNAPSHOT_REVIEW_READY"
)
MAINTENANCE_NEXT_SESSION_PREP_READY = "MAINTENANCE_NEXT_SESSION_PREP_READY"
MAINTENANCE_PR_LANDING_PREP_READY = "MAINTENANCE_PR_LANDING_PREP_READY"
MAINTENANCE_OWNER_REVIEW_REQUIRED = "MAINTENANCE_OWNER_REVIEW_REQUIRED"
BLOCKED_BY_CALENDAR = "BLOCKED_BY_CALENDAR"
BLOCKED_BY_CLOSE_PROTECTION = "BLOCKED_BY_CLOSE_PROTECTION"
BLOCKED_BY_POLICY = "BLOCKED_BY_POLICY"
BLOCKED_BY_RISK_STATE = "BLOCKED_BY_RISK_STATE"
BLOCKED_BY_PROFIT_CLAIM = "BLOCKED_BY_PROFIT_CLAIM"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1"

MAINTENANCE_COMPATIBLE_POSTURES = frozenset(
    {
        "CLOSED_MAINTENANCE",
        "HOLIDAY_DEGRADED_MAINTENANCE",
        "LOW_LIQUIDITY_MAINTENANCE",
        "WEEKEND_HEAVY_MAINTENANCE",
        "CLOSE_PROTECTION",
        "REOPEN_PREPARATION",
    }
)

REQUIRED_SECTIONS = (
    "runtime_calendar_result",
    "market_close_result",
    "maintenance_policy",
    "workload_state",
    "risk_state",
    "evidence_state",
    "claims",
)

RUNTIME_CALENDAR_REQUIRED_FIELDS = (
    "status",
    "ready",
    "runtime_job_router_enabled",
    "current_runtime_posture",
    "primary_job_lane",
    "maintenance_window_recommended",
    "execution_authorized_by_calendar",
    "trade_window_open",
    "next_best_packet",
    "blocked_job_queue",
)

MARKET_CLOSE_REQUIRED_FIELDS = (
    "status",
    "ready",
    "close_protection_enabled",
    "new_risk_allowed_by_this_module",
    "new_trade_seeking_allowed_by_this_module",
    "post_close_maintenance_ready",
    "receipt_capture_ready",
    "owner_attention_required",
    "next_best_packet",
    "safety",
)

POLICY_TRUE_FIELDS = (
    "evidence_compaction_allowed",
    "receipt_review_allowed",
    "pnl_review_allowed",
    "replay_validation_allowed",
    "report_cleanup_allowed",
    "backup_snapshot_review_allowed",
    "next_session_prep_allowed",
    "pr_landing_prep_allowed",
    "owner_review_required",
    "no_scheduler_created",
    "no_daemon_created",
    "no_broker_call",
    "no_trade_execution",
    "no_live_market_data_call",
    "no_strategy_mutation",
    "no_money_movement",
    "no_banking",
    "no_withdrawal",
)

POLICY_FALSE_FIELDS = ("raw_values_echoed",)

WORKLOAD_COUNT_FIELDS = (
    "unreviewed_receipts_count",
    "pending_pnl_reviews_count",
    "replay_backlog_count",
    "pending_reports_count",
    "evidence_snapshots_pending_count",
    "owner_review_items_pending",
)

WORKLOAD_BOOL_FIELDS = (
    "backup_snapshot_review_pending",
    "next_session_prep_requested",
    "pr_landing_prep_requested",
    "proof_pipeline_paused",
    "proof_pipeline_can_continue",
)

RISK_REQUIRED_FIELDS = (
    "kill_switch_active",
    "daily_loss_stop_active",
    "drawdown_within_limit",
    "maintenance_risk_review_required",
)

EVIDENCE_REQUIRED_FIELDS = (
    "receipts_sanitized",
    "pnl_reconciled",
    "proof_continuity_ready",
    "repeatability_review_ready",
    "fake_pnl_blocked",
    "evidence_compaction_safe",
    "report_cleanup_safe",
    "replay_validation_safe",
)

EVIDENCE_TRUE_FIELDS = (
    "fake_pnl_blocked",
    "evidence_compaction_safe",
    "report_cleanup_safe",
    "replay_validation_safe",
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
    "files_deleted_by_this_module",
    "repo_cleanup_performed_by_this_module",
    "git_stage_performed_by_this_module",
    "git_commit_performed_by_this_module",
    "git_push_performed_by_this_module",
    "pr_created_by_this_module",
    "withdrawal_allowed_by_this_module",
    "bank_routing_allowed_by_this_module",
    "live_profit_guaranteed",
    "daily_profit_guaranteed",
    "weekly_profit_guaranteed",
    "monthly_profit_guaranteed",
    "yearly_profit_guaranteed",
    "fixed_return_promised_by_aios",
)

MAINTENANCE_JOB_SPECS = (
    ("risk_review", "P0"),
    ("receipt_review", "P1"),
    ("pnl_reconciliation_review", "P1"),
    ("evidence_compaction", "P2"),
    ("replay_validation", "P2"),
    ("report_cleanup", "P2"),
    ("backup_snapshot_review", "P3"),
    ("next_session_prep", "P3"),
    ("owner_review", "P3"),
    ("pr_landing_prep", "P3"),
)

BLOCKED_RUNTIME_ACTION_IDS = (
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
    "delete_files_by_this_module",
    "stage_commit_push_pr_by_this_module",
    "promise_profit_by_this_module",
)

OWNER_REVIEW_IDS = (
    "maintenance_owner_summary_review",
    "risk_review_if_blocked",
    "receipt_review_if_pending",
    "pnl_review_if_pending",
    "proof_pipeline_review_if_paused",
    "next_session_prep_review_if_requested",
    "pr_landing_review_if_requested",
    "runtime_execution_packet_required_for_any_order",
)

STATUS_TO_LANE = {
    BLOCKED_BY_RISK_STATE: "risk_review",
    MAINTENANCE_RECEIPT_REVIEW_READY: "receipt_review",
    MAINTENANCE_PNL_REVIEW_READY: "pnl_reconciliation_review",
    MAINTENANCE_EVIDENCE_REVIEW_READY: "evidence_compaction",
    MAINTENANCE_REPLAY_VALIDATION_READY: "replay_validation",
    MAINTENANCE_REPORT_CLEANUP_READY: "report_cleanup",
    MAINTENANCE_BACKUP_SNAPSHOT_REVIEW_READY: "backup_snapshot_review",
    MAINTENANCE_NEXT_SESSION_PREP_READY: "next_session_prep",
    MAINTENANCE_OWNER_REVIEW_REQUIRED: "owner_review",
    MAINTENANCE_PR_LANDING_PREP_READY: "pr_landing_prep",
    MAINTENANCE_WORKLOAD_PLAN_READY: "clean_maintenance_plan",
}

STATUS_ROUTES = {
    MAINTENANCE_WORKLOAD_PLAN_READY: "AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1",
    MAINTENANCE_EVIDENCE_REVIEW_READY: "AIOS_FOREX_PROOF_PIPELINE_PAUSE_AND_CONTINUE_V1",
    MAINTENANCE_RECEIPT_REVIEW_READY: "AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1",
    MAINTENANCE_PNL_REVIEW_READY: "AIOS_FOREX_POST_EXECUTION_REVIEW_LOOP_V1",
    MAINTENANCE_REPLAY_VALIDATION_READY: "AIOS_FOREX_PROFIT_REPEATABILITY_EVIDENCE_V1",
    MAINTENANCE_REPORT_CLEANUP_READY: "AIOS_FOREX_COMPLETION_CAMPAIGN_REVIEW_REPAIR_V1",
    MAINTENANCE_BACKUP_SNAPSHOT_REVIEW_READY: "AIOS_DAILY_AUTOMATION_SNAPSHOT_REVIEW_V1",
    MAINTENANCE_NEXT_SESSION_PREP_READY: "AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1",
    MAINTENANCE_PR_LANDING_PREP_READY: "AIOS_FOREX_COMPLETION_CAMPAIGN_PART3_OWNER_VALIDATION_AND_PR_LANDING_V1",
    MAINTENANCE_OWNER_REVIEW_REQUIRED: "AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1",
    BLOCKED_BY_RISK_STATE: "AIOS_FOREX_RISK_SCALE_DOWN_REVIEW_V1",
    BLOCKED_BY_CALENDAR: "AIOS_FOREX_RUNTIME_CALENDAR_STATUS_AND_MAINTENANCE_MODE_V1",
    BLOCKED_BY_CLOSE_PROTECTION: "AIOS_FOREX_MARKET_CLOSE_PROTECTION_AND_RECEIPT_CAPTURE_V1",
}

SENSITIVE_KEY_PARTS = (
    "api_key",
    "access_key",
    "refresh_token",
    "secret",
    "password",
    "credential",
    "account_id",
    "private_key",
    "master_password",
    "vault_password",
)

SENSITIVE_VALUE_MARKERS = (
    "secret",
    "api_key",
    "password",
    "credential",
    "bearer ",
    "token=",
    "sk-",
)

BANKING_TOKENS = frozenset(
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
        "iban",
        "swift",
    }
)

BANKING_ALLOWED_TRUE_FIELDS = frozenset(
    {
        "no_banking",
        "no_withdrawal",
        "no_money_movement",
        "banking_withdrawal_transfer_freeze",
    }
)


def evaluate_forex_runtime_maintenance_workload_execution_plan_v1(
    payload: dict | None = None,
) -> dict:
    source = _mapping(payload)

    sensitive_blockers = _sensitive_data_blockers(source)
    if sensitive_blockers:
        return _build_result(
            BLOCKED_BY_SENSITIVE_DATA,
            source=source,
            blockers=sensitive_blockers,
        )

    missing = _missing_required_sections(source)
    if missing:
        return _build_result(INCOMPLETE_INPUTS, source=source, blockers=missing)

    section_blockers = _section_shape_blockers(source)
    if section_blockers:
        return _build_result(INCOMPLETE_INPUTS, source=source, blockers=section_blockers)

    claim_blockers = _claim_blockers(_mapping(source.get("claims")))
    if claim_blockers:
        return _build_result(
            BLOCKED_BY_PROFIT_CLAIM,
            source=source,
            blockers=claim_blockers,
        )

    calendar_blockers = _calendar_blockers(_mapping(source.get("runtime_calendar_result")))
    if calendar_blockers:
        return _build_result(
            BLOCKED_BY_CALENDAR,
            source=source,
            blockers=calendar_blockers,
        )

    close_blockers = _market_close_blockers(_mapping(source.get("market_close_result")))
    if close_blockers:
        return _build_result(
            BLOCKED_BY_CLOSE_PROTECTION,
            source=source,
            blockers=close_blockers,
        )

    policy_blockers = _policy_blockers(
        _mapping(source.get("maintenance_policy")),
        _mapping(source.get("risk_state")),
        _mapping(source.get("evidence_state")),
    )
    if policy_blockers:
        return _build_result(BLOCKED_BY_POLICY, source=source, blockers=policy_blockers)

    banking_blockers = _banking_focus_blockers(source)
    if banking_blockers:
        return _build_result(
            BLOCKED_BY_BANKING_FOCUS,
            source=source,
            blockers=banking_blockers,
        )

    status = _maintenance_status(
        _mapping(source.get("workload_state")),
        _mapping(source.get("risk_state")),
    )
    return _build_result(status, source=source, blockers=())


def _maintenance_status(workload: Mapping[str, Any], risk: Mapping[str, Any]) -> str:
    if _bool(risk.get("kill_switch_active")):
        return BLOCKED_BY_RISK_STATE
    if _bool(risk.get("daily_loss_stop_active")):
        return BLOCKED_BY_RISK_STATE
    if not _bool(risk.get("drawdown_within_limit")):
        return BLOCKED_BY_RISK_STATE
    if _int(workload.get("unreviewed_receipts_count")) > 0:
        return MAINTENANCE_RECEIPT_REVIEW_READY
    if _int(workload.get("pending_pnl_reviews_count")) > 0:
        return MAINTENANCE_PNL_REVIEW_READY
    if _int(workload.get("evidence_snapshots_pending_count")) > 0:
        return MAINTENANCE_EVIDENCE_REVIEW_READY
    if _int(workload.get("replay_backlog_count")) > 0:
        return MAINTENANCE_REPLAY_VALIDATION_READY
    if _int(workload.get("pending_reports_count")) > 0:
        return MAINTENANCE_REPORT_CLEANUP_READY
    if _bool(workload.get("backup_snapshot_review_pending")):
        return MAINTENANCE_BACKUP_SNAPSHOT_REVIEW_READY
    if _bool(workload.get("next_session_prep_requested")):
        return MAINTENANCE_NEXT_SESSION_PREP_READY
    if _int(workload.get("owner_review_items_pending")) > 0:
        return MAINTENANCE_OWNER_REVIEW_REQUIRED
    if _bool(workload.get("pr_landing_prep_requested")):
        return MAINTENANCE_PR_LANDING_PREP_READY
    return MAINTENANCE_WORKLOAD_PLAN_READY


def _build_result(
    status: str,
    *,
    source: Mapping[str, Any],
    blockers: Sequence[str],
) -> dict[str, Any]:
    calendar = _mapping(source.get("runtime_calendar_result"))
    close = _mapping(source.get("market_close_result"))
    policy = _mapping(source.get("maintenance_policy"))
    workload = _mapping(source.get("workload_state"))
    risk = _mapping(source.get("risk_state"))
    evidence = _mapping(source.get("evidence_state"))

    blocked = status.startswith("BLOCKED") or status == INCOMPLETE_INPUTS
    current_lane = STATUS_TO_LANE.get(status, "blocked")
    next_best_packet = _next_packet(status)
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "ready": not blocked,
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": _owner_decision_required(status, workload, risk),
        "maintenance_plan_enabled": not blocked,
        "current_maintenance_lane": current_lane,
        "maintenance_window_recommended": _bool(
            calendar.get("maintenance_window_recommended")
        ),
        "trade_window_open": _bool(calendar.get("trade_window_open")),
        "post_close_maintenance_ready": _bool(
            close.get("post_close_maintenance_ready")
        ),
        "maintenance_job_queue": _maintenance_job_queue(
            status=status,
            current_lane=current_lane,
            policy=policy,
        ),
        "deferred_runtime_jobs": _deferred_runtime_jobs(status),
        "blocked_runtime_jobs": _blocked_runtime_jobs(),
        "owner_review_queue": _owner_review_queue(status, workload, risk),
        "priority_summary": _priority_summary(status, current_lane),
        "receipt_review_summary": _receipt_review_summary(workload, evidence),
        "pnl_review_summary": _pnl_review_summary(workload, evidence),
        "evidence_compaction_summary": _evidence_compaction_summary(workload, evidence),
        "replay_validation_summary": _replay_validation_summary(workload, evidence),
        "report_cleanup_summary": _report_cleanup_summary(workload, evidence),
        "backup_snapshot_summary": _backup_snapshot_summary(workload),
        "next_session_prep_summary": _next_session_prep_summary(workload),
        "pr_landing_prep_summary": _pr_landing_prep_summary(workload, status),
        "risk_review_summary": _risk_review_summary(risk, status),
        "proof_pipeline_summary": _proof_pipeline_summary(workload, evidence),
        "blockers": list(blockers),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(status),
        "audit_record": {
            "schema": SCHEMA,
            "status": status,
            "metadata_only": True,
            "read_only": True,
            "blocked_runtime_jobs_count": len(BLOCKED_RUNTIME_ACTION_IDS),
            "blocker_count": len(blockers),
            "next_best_packet": next_best_packet,
        },
        "safety": _safety(),
    }
    for field in HARD_FALSE_FIELDS:
        result[field] = False
    return result


def _missing_required_sections(source: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        f"{section}_missing"
        for section in REQUIRED_SECTIONS
        if not isinstance(source.get(section), Mapping)
    )


def _section_shape_blockers(source: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    blockers.extend(
        _missing_fields(
            "runtime_calendar_result",
            _mapping(source.get("runtime_calendar_result")),
            RUNTIME_CALENDAR_REQUIRED_FIELDS,
        )
    )
    blockers.extend(
        _missing_fields(
            "market_close_result",
            _mapping(source.get("market_close_result")),
            MARKET_CLOSE_REQUIRED_FIELDS,
        )
    )
    blockers.extend(_policy_shape_blockers(_mapping(source.get("maintenance_policy"))))
    blockers.extend(_workload_shape_blockers(_mapping(source.get("workload_state"))))
    blockers.extend(
        _missing_fields("risk_state", _mapping(source.get("risk_state")), RISK_REQUIRED_FIELDS)
    )
    blockers.extend(
        _missing_fields(
            "evidence_state",
            _mapping(source.get("evidence_state")),
            EVIDENCE_REQUIRED_FIELDS,
        )
    )
    blockers.extend(_missing_fields("claims", _mapping(source.get("claims")), CLAIM_FIELDS))
    return _unique(blockers)


def _policy_shape_blockers(policy: Mapping[str, Any]) -> list[str]:
    required_fields = tuple(POLICY_TRUE_FIELDS) + tuple(POLICY_FALSE_FIELDS)
    return list(_missing_fields("maintenance_policy", policy, required_fields))


def _workload_shape_blockers(workload: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field in WORKLOAD_COUNT_FIELDS:
        if field not in workload:
            blockers.append(f"workload_state.{field}_missing")
        elif not _is_non_negative_int(workload.get(field)):
            blockers.append(f"workload_state.{field}_invalid")
    for field in WORKLOAD_BOOL_FIELDS:
        if field not in workload:
            blockers.append(f"workload_state.{field}_missing")
        elif not isinstance(workload.get(field), bool):
            blockers.append(f"workload_state.{field}_not_boolean")
    return blockers


def _missing_fields(
    section: str,
    data: Mapping[str, Any],
    fields: Sequence[str],
) -> tuple[str, ...]:
    return tuple(f"{section}.{field}_missing" for field in fields if field not in data)


def _calendar_blockers(calendar: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    if calendar.get("ready") is not True:
        blockers.append("runtime_calendar_result.ready_not_true")
    if calendar.get("runtime_job_router_enabled") is not True:
        blockers.append("runtime_calendar_result.runtime_job_router_enabled_not_true")
    if calendar.get("execution_authorized_by_calendar") is True:
        blockers.append("runtime_calendar_result.execution_authorized_by_calendar_true")
    if not isinstance(calendar.get("maintenance_window_recommended"), bool):
        blockers.append("runtime_calendar_result.maintenance_window_recommended_not_boolean")
    if not isinstance(calendar.get("trade_window_open"), bool):
        blockers.append("runtime_calendar_result.trade_window_open_not_boolean")
    if not _present(calendar.get("primary_job_lane")):
        blockers.append("runtime_calendar_result.primary_job_lane_missing")
    if not _present(calendar.get("next_best_packet")):
        blockers.append("runtime_calendar_result.next_best_packet_missing")
    if not isinstance(calendar.get("blocked_job_queue"), list):
        blockers.append("runtime_calendar_result.blocked_job_queue_not_list")

    posture = str(calendar.get("current_runtime_posture", "")).strip()
    if posture not in MAINTENANCE_COMPATIBLE_POSTURES:
        blockers.append("runtime_calendar_result.maintenance_posture_not_allowed")
    if posture == "ACTIVE_SUPERVISION" and not _bool(
        calendar.get("maintenance_window_recommended")
    ):
        blockers.append("runtime_calendar_result.active_supervision_not_maintenance")
    return _unique(blockers)


def _market_close_blockers(close: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    bool_fields = (
        "ready",
        "close_protection_enabled",
        "new_risk_allowed_by_this_module",
        "new_trade_seeking_allowed_by_this_module",
        "post_close_maintenance_ready",
        "receipt_capture_ready",
        "owner_attention_required",
    )
    for field in bool_fields:
        if not isinstance(close.get(field), bool):
            blockers.append(f"market_close_result.{field}_not_boolean")
    if close.get("new_risk_allowed_by_this_module") is not False:
        blockers.append("market_close_result.new_risk_allowed_by_this_module_not_false")
    if close.get("new_trade_seeking_allowed_by_this_module") is not False:
        blockers.append(
            "market_close_result.new_trade_seeking_allowed_by_this_module_not_false"
        )
    if not _present(close.get("status")):
        blockers.append("market_close_result.status_missing")
    if not _present(close.get("next_best_packet")):
        blockers.append("market_close_result.next_best_packet_missing")
    safety = _mapping(close.get("safety"))
    unsafe_close_flags = (
        "broker_api_called_by_this_module",
        "broker_api_called",
        "trade_executed_by_this_module",
        "live_trade_executed_by_this_module",
        "demo_trade_executed_by_this_module",
        "close_trade_by_this_module",
        "money_moved",
        "bank_access_used",
        "withdrawal_work_built",
        "banking_work_built",
        "transfer_work_built",
    )
    for field in unsafe_close_flags:
        if safety.get(field) is True or close.get(field) is True:
            blockers.append(f"market_close_result.{field}_unsafe_true")
    return _unique(blockers)


def _policy_blockers(
    policy: Mapping[str, Any],
    risk: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> tuple[str, ...]:
    blockers: list[str] = []
    for field in POLICY_TRUE_FIELDS:
        if policy.get(field) is not True:
            blockers.append(f"maintenance_policy.{field}_not_true")
    for field in POLICY_FALSE_FIELDS:
        if policy.get(field) is not False:
            blockers.append(f"maintenance_policy.{field}_not_false")
    if risk.get("maintenance_risk_review_required") is not True:
        blockers.append("risk_state.maintenance_risk_review_required_not_true")
    for field in EVIDENCE_TRUE_FIELDS:
        if evidence.get(field) is not True:
            blockers.append(f"evidence_state.{field}_not_true")
    return _unique(blockers)


def _claim_blockers(claims: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(f"claims.{field}_true" for field in CLAIM_FIELDS if claims.get(field) is True)


def _maintenance_job_queue(
    *,
    status: str,
    current_lane: str,
    policy: Mapping[str, Any],
) -> list[dict[str, Any]]:
    allowed_by_policy = {
        "risk_review": True,
        "receipt_review": _bool(policy.get("receipt_review_allowed")),
        "pnl_reconciliation_review": _bool(policy.get("pnl_review_allowed")),
        "evidence_compaction": _bool(policy.get("evidence_compaction_allowed")),
        "replay_validation": _bool(policy.get("replay_validation_allowed")),
        "report_cleanup": _bool(policy.get("report_cleanup_allowed")),
        "backup_snapshot_review": _bool(policy.get("backup_snapshot_review_allowed")),
        "next_session_prep": _bool(policy.get("next_session_prep_allowed")),
        "owner_review": _bool(policy.get("owner_review_required")),
        "pr_landing_prep": _bool(policy.get("pr_landing_prep_allowed")),
    }
    blocked = status.startswith("BLOCKED") or status == INCOMPLETE_INPUTS
    return [
        {
            "job_id": job_id,
            "priority": priority,
            "allowed_now": (
                allowed_by_policy.get(job_id, False)
                and (job_id == current_lane or (blocked and job_id == "risk_review"))
            ),
            "requires_owner_packet": job_id
            in {
                "risk_review",
                "owner_review",
                "next_session_prep",
                "pr_landing_prep",
            },
            "requires_runtime_permission": False,
            "reason": _job_reason(job_id, status),
            "prohibited_actions": list(BLOCKED_RUNTIME_ACTION_IDS),
        }
        for job_id, priority in MAINTENANCE_JOB_SPECS
    ]


def _job_reason(job_id: str, status: str) -> str:
    if status.startswith("BLOCKED") or status == INCOMPLETE_INPUTS:
        return f"{job_id} is held until status {status} is repaired or routed."
    return f"{job_id} is metadata-only maintenance work and cannot create runtime execution."


def _blocked_runtime_jobs() -> list[dict[str, Any]]:
    return [
        {
            "action_id": action_id,
            "allowed_now": False,
            "reason": "This planner is metadata-only and blocks runtime, broker, credential, money, scheduler, daemon, strategy, delete, Git, PR, and profit-promise actions.",
        }
        for action_id in BLOCKED_RUNTIME_ACTION_IDS
    ]


def _deferred_runtime_jobs(status: str) -> list[dict[str, str]]:
    return [
        {
            "job_id": action_id,
            "deferred_until": "separate_owner_approved_runtime_packet",
            "reason": f"Runtime work is outside {SCHEMA} while status is {status}.",
        }
        for action_id in BLOCKED_RUNTIME_ACTION_IDS
    ]


def _owner_review_queue(
    status: str,
    workload: Mapping[str, Any],
    risk: Mapping[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "review_id": review_id,
            "required_now": _owner_review_required_now(review_id, status, workload, risk),
            "reason": _owner_review_reason(review_id, status),
        }
        for review_id in OWNER_REVIEW_IDS
    ]


def _owner_review_required_now(
    review_id: str,
    status: str,
    workload: Mapping[str, Any],
    risk: Mapping[str, Any],
) -> bool:
    if review_id == "runtime_execution_packet_required_for_any_order":
        return True
    if review_id == "maintenance_owner_summary_review":
        return status in {MAINTENANCE_WORKLOAD_PLAN_READY, MAINTENANCE_OWNER_REVIEW_REQUIRED}
    if review_id == "risk_review_if_blocked":
        return (
            status == BLOCKED_BY_RISK_STATE
            or _bool(risk.get("kill_switch_active"))
            or _bool(risk.get("daily_loss_stop_active"))
            or not _bool(risk.get("drawdown_within_limit"))
        )
    if review_id == "receipt_review_if_pending":
        return _int(workload.get("unreviewed_receipts_count")) > 0
    if review_id == "pnl_review_if_pending":
        return _int(workload.get("pending_pnl_reviews_count")) > 0
    if review_id == "proof_pipeline_review_if_paused":
        return _bool(workload.get("proof_pipeline_paused"))
    if review_id == "next_session_prep_review_if_requested":
        return _bool(workload.get("next_session_prep_requested"))
    if review_id == "pr_landing_review_if_requested":
        return _bool(workload.get("pr_landing_prep_requested"))
    return False


def _owner_review_reason(review_id: str, status: str) -> str:
    if review_id == "runtime_execution_packet_required_for_any_order":
        return "Any order still requires a separate owner-approved runtime packet."
    return f"{review_id} is tracked for maintenance status {status}."


def _priority_summary(status: str, current_lane: str) -> dict[str, Any]:
    return {
        "status": status,
        "current_maintenance_lane": current_lane,
        "priority_order": [
            "risk_review",
            "receipt_review",
            "pnl_reconciliation_review",
            "evidence_compaction",
            "replay_validation",
            "report_cleanup",
            "backup_snapshot_review",
            "next_session_prep",
            "owner_review",
            "pr_landing_prep",
            "clean_maintenance_plan",
        ],
    }


def _receipt_review_summary(
    workload: Mapping[str, Any], evidence: Mapping[str, Any]
) -> dict[str, Any]:
    count = _int(workload.get("unreviewed_receipts_count"))
    return {
        "unreviewed_receipts_count": count,
        "receipts_sanitized": _bool(evidence.get("receipts_sanitized")),
        "receipt_review_ready": count > 0,
        "raw_receipts_echoed": False,
    }


def _pnl_review_summary(
    workload: Mapping[str, Any], evidence: Mapping[str, Any]
) -> dict[str, Any]:
    count = _int(workload.get("pending_pnl_reviews_count"))
    return {
        "pending_pnl_reviews_count": count,
        "pnl_reconciled": _bool(evidence.get("pnl_reconciled")),
        "pnl_review_ready": count > 0,
        "fake_pnl_blocked": _bool(evidence.get("fake_pnl_blocked")),
    }


def _evidence_compaction_summary(
    workload: Mapping[str, Any], evidence: Mapping[str, Any]
) -> dict[str, Any]:
    count = _int(workload.get("evidence_snapshots_pending_count"))
    return {
        "evidence_snapshots_pending_count": count,
        "proof_continuity_ready": _bool(evidence.get("proof_continuity_ready")),
        "evidence_compaction_safe": _bool(evidence.get("evidence_compaction_safe")),
        "evidence_review_ready": count > 0,
    }


def _replay_validation_summary(
    workload: Mapping[str, Any], evidence: Mapping[str, Any]
) -> dict[str, Any]:
    count = _int(workload.get("replay_backlog_count"))
    return {
        "replay_backlog_count": count,
        "repeatability_review_ready": _bool(evidence.get("repeatability_review_ready")),
        "replay_validation_safe": _bool(evidence.get("replay_validation_safe")),
        "replay_validation_ready": count > 0,
    }


def _report_cleanup_summary(
    workload: Mapping[str, Any], evidence: Mapping[str, Any]
) -> dict[str, Any]:
    count = _int(workload.get("pending_reports_count"))
    return {
        "pending_reports_count": count,
        "report_cleanup_safe": _bool(evidence.get("report_cleanup_safe")),
        "report_cleanup_ready": count > 0,
        "file_deletion_allowed": False,
    }


def _backup_snapshot_summary(workload: Mapping[str, Any]) -> dict[str, Any]:
    pending = _bool(workload.get("backup_snapshot_review_pending"))
    return {
        "backup_snapshot_review_pending": pending,
        "backup_snapshot_review_ready": pending,
        "restore_or_delete_allowed": False,
    }


def _next_session_prep_summary(workload: Mapping[str, Any]) -> dict[str, Any]:
    requested = _bool(workload.get("next_session_prep_requested"))
    return {
        "next_session_prep_requested": requested,
        "next_session_prep_ready": requested,
        "runtime_permission_created": False,
    }


def _pr_landing_prep_summary(workload: Mapping[str, Any], status: str) -> dict[str, Any]:
    requested = _bool(workload.get("pr_landing_prep_requested"))
    return {
        "pr_landing_prep_requested": requested,
        "pr_landing_prep_metadata_only": True,
        "pr_landing_prep_ready": status == MAINTENANCE_PR_LANDING_PREP_READY,
        "git_or_pr_action_allowed": False,
    }


def _risk_review_summary(risk: Mapping[str, Any], status: str) -> dict[str, Any]:
    return {
        "kill_switch_active": _bool(risk.get("kill_switch_active")),
        "daily_loss_stop_active": _bool(risk.get("daily_loss_stop_active")),
        "drawdown_within_limit": _bool(risk.get("drawdown_within_limit")),
        "maintenance_risk_review_required": True,
        "risk_review_ready": status == BLOCKED_BY_RISK_STATE,
        "runtime_action_created": False,
    }


def _proof_pipeline_summary(
    workload: Mapping[str, Any], evidence: Mapping[str, Any]
) -> dict[str, Any]:
    paused = _bool(workload.get("proof_pipeline_paused"))
    can_continue = _bool(workload.get("proof_pipeline_can_continue"))
    return {
        "proof_pipeline_paused": paused,
        "proof_pipeline_can_continue": can_continue,
        "proof_continuity_ready": _bool(evidence.get("proof_continuity_ready")),
        "owner_review_required_if_paused": paused,
    }


def _owner_decision_required(
    status: str,
    workload: Mapping[str, Any],
    risk: Mapping[str, Any],
) -> bool:
    return (
        status
        in {
            BLOCKED_BY_RISK_STATE,
            MAINTENANCE_OWNER_REVIEW_REQUIRED,
            MAINTENANCE_PR_LANDING_PREP_READY,
        }
        or _bool(workload.get("proof_pipeline_paused"))
        or _bool(risk.get("kill_switch_active"))
        or _bool(risk.get("daily_loss_stop_active"))
        or not _bool(risk.get("drawdown_within_limit"))
    )


def _next_packet(status: str) -> str:
    return STATUS_ROUTES.get(status, SCHEMA)


def _safe_manual_next_action(status: str) -> str:
    if status == MAINTENANCE_WORKLOAD_PLAN_READY:
        return "Prepare the next Forex session packet without runtime execution."
    if status == MAINTENANCE_RECEIPT_REVIEW_READY:
        return "Review sanitized receipts before PnL, replay, report, or PR-prep work."
    if status == MAINTENANCE_PNL_REVIEW_READY:
        return "Reconcile PnL metadata from sanitized receipts before lower-priority work."
    if status == MAINTENANCE_EVIDENCE_REVIEW_READY:
        return "Compact safe evidence metadata while preserving raw-value boundaries."
    if status == MAINTENANCE_REPLAY_VALIDATION_READY:
        return "Run replay validation as metadata evidence only."
    if status == MAINTENANCE_REPORT_CLEANUP_READY:
        return "Clean report metadata without deleting files or mutating Git state."
    if status == MAINTENANCE_BACKUP_SNAPSHOT_REVIEW_READY:
        return "Review backup snapshot evidence without restore, delete, or promotion."
    if status == MAINTENANCE_NEXT_SESSION_PREP_READY:
        return "Prepare next-session metadata and stop before runtime permission."
    if status == MAINTENANCE_PR_LANDING_PREP_READY:
        return "Prepare PR landing metadata only; do not stage, commit, push, or open a PR."
    if status == MAINTENANCE_OWNER_REVIEW_REQUIRED:
        return "Queue owner review metadata and keep all runtime actions blocked."
    if status == BLOCKED_BY_RISK_STATE:
        return "Route to risk scale-down review; do not create runtime execution."
    if status == BLOCKED_BY_CALENDAR:
        return "Repair or rerun runtime calendar metadata before maintenance planning."
    if status == BLOCKED_BY_CLOSE_PROTECTION:
        return "Repair or rerun market-close protection metadata before maintenance planning."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive values and rerun with sanitized metadata only."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove active banking, withdrawal, transfer, card, deposit, or money focus."
    if status == BLOCKED_BY_PROFIT_CLAIM:
        return "Remove guaranteed-profit or fixed-return claims before continuing."
    return "Repair incomplete or unsafe metadata and rerun this planner."


def _safety() -> dict[str, Any]:
    safety = {
        "read_only": True,
        "metadata_only": True,
        "maintenance_planner_only": True,
        "no_scheduler_created": True,
        "no_daemon_created": True,
        "no_broker_call": True,
        "no_trade_execution": True,
        "no_live_market_data_call": True,
        "no_strategy_mutation": True,
        "no_money_movement": True,
        "no_banking": True,
        "no_withdrawal": True,
        "raw_values_echoed": False,
    }
    for field in HARD_FALSE_FIELDS:
        safety[field] = False
    return safety


def _sensitive_data_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if _sensitive_key_active(key_text, child):
                blockers.append(child_path)
            blockers.extend(_sensitive_data_blockers(child, child_path))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            blockers.extend(_sensitive_data_blockers(child, f"{path}[{index}]"))
    elif isinstance(value, str) and _looks_secret_string(value):
        blockers.append(path)
    return _unique(blockers)


def _sensitive_key_active(key: str, value: Any) -> bool:
    normalized = _normalize_key(key)
    if not any(part in normalized for part in SENSITIVE_KEY_PARTS):
        return False
    if value in {False, None, ""}:
        return False
    if isinstance(value, str) and value.strip().lower() in {
        "false",
        "none",
        "not_present",
        "redacted",
        "sanitized",
        "metadata_only",
    }:
        return False
    return True


def _looks_secret_string(value: str) -> bool:
    text = value.strip().lower()
    if not text:
        return False
    if any(marker in text for marker in SENSITIVE_VALUE_MARKERS):
        return True
    return _has_long_digit_run(text, 12)


def _banking_focus_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}"
            if _banking_key_active(key_text) and _active_focus(child):
                blockers.append(child_path)
            blockers.extend(_banking_focus_blockers(child, child_path))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            blockers.extend(_banking_focus_blockers(child, f"{path}[{index}]"))
    return _unique(blockers)


def _banking_key_active(key: str) -> bool:
    normalized = _normalize_key(key)
    if normalized in BANKING_ALLOWED_TRUE_FIELDS:
        return False
    tokens = set(_key_tokens(normalized))
    return bool(tokens & BANKING_TOKENS)


def _active_focus(value: Any) -> bool:
    if value is False or value is None:
        return False
    if value is True:
        return True
    if isinstance(value, (list, tuple, dict)):
        return bool(value)
    if isinstance(value, str):
        text = value.strip().lower()
        return text not in {
            "",
            "false",
            "no",
            "none",
            "0",
            "off",
            "disabled",
            "inactive",
            "blocked",
            "deferred",
            "freeze",
            "frozen",
            "not_applicable",
            "not_requested",
            "metadata_only",
            "n/a",
        }
    if isinstance(value, (int, float)):
        return value != 0
    return True


def _key_tokens(normalized_key: str) -> tuple[str, ...]:
    chunks: list[str] = []
    current = ""
    for character in normalized_key:
        if character.isalnum():
            current += character
        elif current:
            chunks.append(current)
            current = ""
    if current:
        chunks.append(current)
    return tuple(chunks)


def _normalize_key(key: Any) -> str:
    return str(key).strip().lower().replace("-", "_").replace(" ", "_")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return bool(value)


def _int(value: Any) -> int:
    return int(value) if isinstance(value, int) and not isinstance(value, bool) else 0


def _is_non_negative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _present(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _has_long_digit_run(value: str, minimum: int) -> bool:
    run = 0
    for character in value:
        if character.isdigit():
            run += 1
            if run >= minimum:
                return True
        else:
            run = 0
    return False


def _unique(values: Sequence[Any]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(value) for value in values))


__all__ = [
    "BLOCKED_BY_BANKING_FOCUS",
    "BLOCKED_BY_CALENDAR",
    "BLOCKED_BY_CLOSE_PROTECTION",
    "BLOCKED_BY_POLICY",
    "BLOCKED_BY_PROFIT_CLAIM",
    "BLOCKED_BY_RISK_STATE",
    "BLOCKED_BY_SENSITIVE_DATA",
    "HARD_FALSE_FIELDS",
    "INCOMPLETE_INPUTS",
    "MAINTENANCE_BACKUP_SNAPSHOT_REVIEW_READY",
    "MAINTENANCE_EVIDENCE_REVIEW_READY",
    "MAINTENANCE_NEXT_SESSION_PREP_READY",
    "MAINTENANCE_OWNER_REVIEW_REQUIRED",
    "MAINTENANCE_PNL_REVIEW_READY",
    "MAINTENANCE_PR_LANDING_PREP_READY",
    "MAINTENANCE_RECEIPT_REVIEW_READY",
    "MAINTENANCE_REPLAY_VALIDATION_READY",
    "MAINTENANCE_REPORT_CLEANUP_READY",
    "MAINTENANCE_WORKLOAD_PLAN_READY",
    "MODE",
    "SCHEMA",
    "evaluate_forex_runtime_maintenance_workload_execution_plan_v1",
]
