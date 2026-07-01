from copy import deepcopy
from pathlib import Path

import pytest

from automation.forex_engine.forex_runtime_maintenance_workload_execution_plan_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_CALENDAR,
    BLOCKED_BY_CLOSE_PROTECTION,
    BLOCKED_BY_POLICY,
    BLOCKED_BY_PROFIT_CLAIM,
    BLOCKED_BY_RISK_STATE,
    BLOCKED_BY_SENSITIVE_DATA,
    HARD_FALSE_FIELDS,
    MAINTENANCE_BACKUP_SNAPSHOT_REVIEW_READY,
    MAINTENANCE_EVIDENCE_REVIEW_READY,
    MAINTENANCE_NEXT_SESSION_PREP_READY,
    MAINTENANCE_OWNER_REVIEW_REQUIRED,
    MAINTENANCE_PNL_REVIEW_READY,
    MAINTENANCE_PR_LANDING_PREP_READY,
    MAINTENANCE_RECEIPT_REVIEW_READY,
    MAINTENANCE_REPLAY_VALIDATION_READY,
    MAINTENANCE_REPORT_CLEANUP_READY,
    MAINTENANCE_WORKLOAD_PLAN_READY,
    MODE,
    SCHEMA,
    evaluate_forex_runtime_maintenance_workload_execution_plan_v1,
)


REQUIRED_JOBS = {
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
}

REQUIRED_BLOCKED_RUNTIME_JOBS = {
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
}


def _payload() -> dict:
    return {
        "runtime_calendar_result": {
            "status": "RUNTIME_MARKET_CLOSED_MAINTENANCE",
            "ready": True,
            "runtime_job_router_enabled": True,
            "current_runtime_posture": "CLOSED_MAINTENANCE",
            "primary_job_lane": "maintain_evidence",
            "maintenance_window_recommended": True,
            "execution_authorized_by_calendar": False,
            "trade_window_open": False,
            "next_best_packet": "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1",
            "blocked_job_queue": [],
        },
        "market_close_result": {
            "status": "CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY",
            "ready": True,
            "close_protection_enabled": True,
            "new_risk_allowed_by_this_module": False,
            "new_trade_seeking_allowed_by_this_module": False,
            "post_close_maintenance_ready": True,
            "receipt_capture_ready": True,
            "owner_attention_required": False,
            "next_best_packet": "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1",
            "safety": {
                "metadata_only": True,
                "no_broker_call": True,
                "no_money_movement": True,
            },
        },
        "maintenance_policy": {
            "evidence_compaction_allowed": True,
            "receipt_review_allowed": True,
            "pnl_review_allowed": True,
            "replay_validation_allowed": True,
            "report_cleanup_allowed": True,
            "backup_snapshot_review_allowed": True,
            "next_session_prep_allowed": True,
            "pr_landing_prep_allowed": True,
            "owner_review_required": True,
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
        },
        "workload_state": {
            "unreviewed_receipts_count": 0,
            "pending_pnl_reviews_count": 0,
            "replay_backlog_count": 0,
            "pending_reports_count": 0,
            "evidence_snapshots_pending_count": 0,
            "backup_snapshot_review_pending": False,
            "next_session_prep_requested": False,
            "pr_landing_prep_requested": False,
            "owner_review_items_pending": 0,
            "proof_pipeline_paused": False,
            "proof_pipeline_can_continue": True,
        },
        "risk_state": {
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "drawdown_within_limit": True,
            "maintenance_risk_review_required": True,
        },
        "evidence_state": {
            "receipts_sanitized": True,
            "pnl_reconciled": True,
            "proof_continuity_ready": True,
            "repeatability_review_ready": True,
            "fake_pnl_blocked": True,
            "evidence_compaction_safe": True,
            "report_cleanup_safe": True,
            "replay_validation_safe": True,
        },
        "claims": {
            "guaranteed_profit_claimed": False,
            "fixed_return_promised": False,
            "daily_profit_guaranteed": False,
            "weekly_profit_guaranteed": False,
            "monthly_profit_guaranteed": False,
            "yearly_profit_guaranteed": False,
        },
    }


def _run(payload: dict | None = None) -> dict:
    return evaluate_forex_runtime_maintenance_workload_execution_plan_v1(
        payload or _payload()
    )


def _replace(**updates: dict) -> dict:
    payload = deepcopy(_payload())
    for section, values in updates.items():
        if section == "top":
            payload.update(values)
        elif section.endswith(".safety"):
            parent = section.split(".", 1)[0]
            payload[parent]["safety"].update(values)
        elif values is None:
            payload.pop(section, None)
        else:
            payload[section].update(values)
    return payload


def _job_ids(result: dict) -> set[str]:
    return {job["job_id"] for job in result["maintenance_job_queue"]}


def _blocked_action_ids(result: dict) -> set[str]:
    return {job["action_id"] for job in result["blocked_runtime_jobs"]}


def _owner_review_ids(result: dict) -> set[str]:
    return {review["review_id"] for review in result["owner_review_queue"]}


def test_clean_maintenance_plan_ready() -> None:
    result = _run()
    assert result["status"] == MAINTENANCE_WORKLOAD_PLAN_READY
    assert result["ready"] is True
    assert result["maintenance_plan_enabled"] is True
    assert result["next_best_packet"] == "AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1"


def test_output_schema_and_mode_present() -> None:
    result = _run()
    assert result["schema"] == SCHEMA
    assert result["mode"] == MODE


def test_maintenance_job_queue_includes_all_required_jobs() -> None:
    result = _run()
    assert _job_ids(result) == REQUIRED_JOBS
    assert all(job["priority"] in {"P0", "P1", "P2", "P3"} for job in result["maintenance_job_queue"])
    assert all(job["requires_runtime_permission"] is False for job in result["maintenance_job_queue"])


def test_blocked_runtime_jobs_include_all_runtime_and_git_actions() -> None:
    result = _run()
    assert _blocked_action_ids(result) == REQUIRED_BLOCKED_RUNTIME_JOBS


def test_owner_review_queue_includes_runtime_execution_packet_required() -> None:
    result = _run()
    assert "runtime_execution_packet_required_for_any_order" in _owner_review_ids(result)


def test_active_market_active_supervision_without_maintenance_blocks_by_calendar() -> None:
    result = _run(
        _replace(
            runtime_calendar_result={
                "status": "RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION",
                "current_runtime_posture": "ACTIVE_SUPERVISION",
                "maintenance_window_recommended": False,
                "trade_window_open": True,
            }
        )
    )
    assert result["status"] == BLOCKED_BY_CALENDAR


@pytest.mark.parametrize(
    "posture",
    [
        "CLOSED_MAINTENANCE",
        "HOLIDAY_DEGRADED_MAINTENANCE",
        "LOW_LIQUIDITY_MAINTENANCE",
        "WEEKEND_HEAVY_MAINTENANCE",
        "CLOSE_PROTECTION",
        "REOPEN_PREPARATION",
    ],
)
def test_maintenance_compatible_postures_are_allowed(posture: str) -> None:
    result = _run(_replace(runtime_calendar_result={"current_runtime_posture": posture}))
    assert result["status"] == MAINTENANCE_WORKLOAD_PLAN_READY


def test_calendar_execution_authorized_true_blocks() -> None:
    result = _run(
        _replace(runtime_calendar_result={"execution_authorized_by_calendar": True})
    )
    assert result["status"] == BLOCKED_BY_CALENDAR


@pytest.mark.parametrize(
    "field",
    [
        "broker_api_called_by_this_module",
        "live_trade_executed_by_this_module",
        "demo_trade_executed_by_this_module",
        "money_moved",
    ],
)
def test_market_close_result_unsafe_broker_trade_money_flags_block(field: str) -> None:
    result = _run(_replace(**{"market_close_result.safety": {field: True}}))
    assert result["status"] == BLOCKED_BY_CLOSE_PROTECTION


@pytest.mark.parametrize(
    "field",
    [
        "no_scheduler_created",
        "no_daemon_created",
        "no_broker_call",
        "no_trade_execution",
        "no_live_market_data_call",
        "no_strategy_mutation",
        "no_money_movement",
        "no_banking",
        "no_withdrawal",
    ],
)
def test_policy_true_fields_false_block_by_policy(field: str) -> None:
    result = _run(_replace(maintenance_policy={field: False}))
    assert result["status"] == BLOCKED_BY_POLICY


def test_raw_values_echoed_true_blocks_by_policy() -> None:
    result = _run(_replace(maintenance_policy={"raw_values_echoed": True}))
    assert result["status"] == BLOCKED_BY_POLICY


def test_kill_switch_active_routes_risk_review() -> None:
    result = _run(_replace(risk_state={"kill_switch_active": True}))
    assert result["status"] == BLOCKED_BY_RISK_STATE
    assert result["current_maintenance_lane"] == "risk_review"


def test_daily_loss_stop_active_routes_risk_review() -> None:
    result = _run(_replace(risk_state={"daily_loss_stop_active": True}))
    assert result["status"] == BLOCKED_BY_RISK_STATE


def test_drawdown_breach_routes_risk_review() -> None:
    result = _run(_replace(risk_state={"drawdown_within_limit": False}))
    assert result["status"] == BLOCKED_BY_RISK_STATE


def test_unreviewed_receipts_route_receipt_review() -> None:
    result = _run(_replace(workload_state={"unreviewed_receipts_count": 2}))
    assert result["status"] == MAINTENANCE_RECEIPT_REVIEW_READY


def test_pending_pnl_reviews_route_pnl_review() -> None:
    result = _run(_replace(workload_state={"pending_pnl_reviews_count": 1}))
    assert result["status"] == MAINTENANCE_PNL_REVIEW_READY


def test_evidence_snapshots_pending_route_evidence_review() -> None:
    result = _run(_replace(workload_state={"evidence_snapshots_pending_count": 1}))
    assert result["status"] == MAINTENANCE_EVIDENCE_REVIEW_READY


def test_replay_backlog_routes_replay_validation() -> None:
    result = _run(_replace(workload_state={"replay_backlog_count": 1}))
    assert result["status"] == MAINTENANCE_REPLAY_VALIDATION_READY


def test_pending_reports_route_report_cleanup() -> None:
    result = _run(_replace(workload_state={"pending_reports_count": 1}))
    assert result["status"] == MAINTENANCE_REPORT_CLEANUP_READY


def test_backup_snapshot_pending_routes_backup_review() -> None:
    result = _run(_replace(workload_state={"backup_snapshot_review_pending": True}))
    assert result["status"] == MAINTENANCE_BACKUP_SNAPSHOT_REVIEW_READY


def test_next_session_prep_requested_routes_next_session_prep() -> None:
    result = _run(_replace(workload_state={"next_session_prep_requested": True}))
    assert result["status"] == MAINTENANCE_NEXT_SESSION_PREP_READY


def test_pr_landing_prep_requested_routes_only_when_higher_priority_work_clean() -> None:
    result = _run(_replace(workload_state={"pr_landing_prep_requested": True}))
    assert result["status"] == MAINTENANCE_PR_LANDING_PREP_READY

    higher_priority_result = _run(
        _replace(
            workload_state={
                "pr_landing_prep_requested": True,
                "unreviewed_receipts_count": 1,
            }
        )
    )
    assert higher_priority_result["status"] == MAINTENANCE_RECEIPT_REVIEW_READY


def test_owner_review_items_pending_routes_owner_review() -> None:
    result = _run(_replace(workload_state={"owner_review_items_pending": 1}))
    assert result["status"] == MAINTENANCE_OWNER_REVIEW_REQUIRED


def test_proof_pipeline_paused_summary_is_present() -> None:
    result = _run(_replace(workload_state={"proof_pipeline_paused": True}))
    assert result["proof_pipeline_summary"]["proof_pipeline_paused"] is True
    assert result["proof_pipeline_summary"]["owner_review_required_if_paused"] is True


def test_sensitive_data_blocks_and_does_not_echo_raw_value() -> None:
    raw_value = "SHOULD_NOT_ECHO_RAW_SECRET_VALUE"
    result = _run(_replace(top={"api_key": raw_value}))
    assert result["status"] == BLOCKED_BY_SENSITIVE_DATA
    assert raw_value not in str(result)
    assert "payload.api_key" in result["blockers"]


def test_active_banking_withdrawal_blocks() -> None:
    result = _run(_replace(top={"banking_focus": {"withdrawal": True}}))
    assert result["status"] == BLOCKED_BY_BANKING_FOCUS


def test_explicit_false_banking_fields_do_not_block() -> None:
    result = _run(
        _replace(
            top={
                "banking_work_built": False,
                "withdrawal_work_built": False,
                "bank_routing_built": False,
                "money_moved": False,
            }
        )
    )
    assert result["status"] != BLOCKED_BY_BANKING_FOCUS


@pytest.mark.parametrize("field", ["close_approaching", "reopen_approaching", "maintenance_window"])
def test_approach_and_maintenance_window_fields_do_not_false_positive_banking(field: str) -> None:
    result = _run(_replace(top={field: True}))
    assert result["status"] != BLOCKED_BY_BANKING_FOCUS
    assert not any(field in blocker for blocker in result["blockers"])


def test_profit_guarantee_blocks() -> None:
    result = _run(_replace(claims={"daily_profit_guaranteed": True}))
    assert result["status"] == BLOCKED_BY_PROFIT_CLAIM


def test_all_hard_false_fields_remain_false() -> None:
    result = _run()
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False


def test_no_scheduler_or_daemon_created() -> None:
    result = _run()
    assert result["scheduler_created"] is False
    assert result["daemon_created"] is False
    assert result["safety"]["no_scheduler_created"] is True
    assert result["safety"]["no_daemon_created"] is True


def test_no_git_stage_commit_push_or_pr_fields_true() -> None:
    result = _run()
    assert result["git_stage_performed_by_this_module"] is False
    assert result["git_commit_performed_by_this_module"] is False
    assert result["git_push_performed_by_this_module"] is False
    assert result["pr_created_by_this_module"] is False


def test_no_delete_or_repo_cleanup_fields_true() -> None:
    result = _run()
    assert result["files_deleted_by_this_module"] is False
    assert result["repo_cleanup_performed_by_this_module"] is False
    assert result["report_cleanup_summary"]["file_deletion_allowed"] is False


def test_production_source_has_no_forbidden_runtime_markers() -> None:
    source = Path(
        "automation/forex_engine/forex_runtime_maintenance_workload_execution_plan_v1.py"
    ).read_text(encoding="utf-8").lower()
    forbidden = [
        "requests",
        "socket",
        "urllib",
        "subprocess",
        "os.environ",
        "broker_sdk",
        "schedule.every",
        "start-process",
    ]
    assert {marker for marker in forbidden if marker in source} == set()
