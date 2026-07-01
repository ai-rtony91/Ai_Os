from __future__ import annotations

from copy import deepcopy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_runtime_maintenance_workload_execution_plan_v1 import (
    evaluate_forex_runtime_maintenance_workload_execution_plan_v1,
)


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


def _run(sample_name: str, **updates: dict) -> dict:
    payload = deepcopy(_payload())
    for section, values in updates.items():
        if section == "top":
            payload.update(values)
        else:
            payload[section].update(values)
    result = evaluate_forex_runtime_maintenance_workload_execution_plan_v1(payload)
    return {
        "sample_name": sample_name,
        "status": result["status"],
        "ready": result["ready"],
        "maintenance_plan_enabled": result["maintenance_plan_enabled"],
        "current_maintenance_lane": result["current_maintenance_lane"],
        "maintenance_window_recommended": result["maintenance_window_recommended"],
        "trade_window_open": result["trade_window_open"],
        "post_close_maintenance_ready": result["post_close_maintenance_ready"],
        "next_best_packet": result["next_best_packet"],
        "blockers": result["blockers"],
    }


def main() -> None:
    samples = [
        _run("clean maintenance plan ready"),
        _run("unreviewed receipts", workload_state={"unreviewed_receipts_count": 2}),
        _run("pending PnL review", workload_state={"pending_pnl_reviews_count": 1}),
        _run(
            "evidence compaction",
            workload_state={"evidence_snapshots_pending_count": 1},
        ),
        _run("replay validation", workload_state={"replay_backlog_count": 1}),
        _run("report cleanup", workload_state={"pending_reports_count": 1}),
        _run(
            "backup snapshot review",
            workload_state={"backup_snapshot_review_pending": True},
        ),
        _run(
            "next session prep",
            workload_state={"next_session_prep_requested": True},
        ),
        _run("PR landing prep", workload_state={"pr_landing_prep_requested": True}),
        _run("risk blocked", risk_state={"kill_switch_active": True}),
        _run(
            "active market blocked",
            runtime_calendar_result={
                "status": "RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION",
                "current_runtime_posture": "ACTIVE_SUPERVISION",
                "maintenance_window_recommended": False,
                "trade_window_open": True,
            },
        ),
        _run(
            "banking false-positive guard",
            top={
                "close_approaching": True,
                "reopen_approaching": True,
                "maintenance_window": "closed_review",
            },
        ),
    ]
    print(json.dumps(samples, separators=(",", ":")))


if __name__ == "__main__":
    main()
