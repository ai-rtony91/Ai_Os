from __future__ import annotations

from copy import deepcopy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_market_close_protection_and_receipt_capture_v1 import (
    evaluate_forex_market_close_protection_and_receipt_capture_v1,
)


def _payload() -> dict:
    return {
        "runtime_calendar_result": {
            "status": "RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION",
            "ready": True,
            "runtime_job_router_enabled": True,
            "current_runtime_posture": "CLOSE_PROTECTION",
            "primary_job_lane": "protect_close",
            "close_protection_recommended": True,
            "trade_window_open": True,
            "close_window_active": True,
            "execution_authorized_by_calendar": False,
            "next_best_packet": "AIOS_FOREX_MARKET_CLOSE_PROTECTION_AND_RECEIPT_CAPTURE_V1",
            "blocked_job_queue": [],
            "kill_switch_semantics": {"kill_switch_blocks_trade": True},
        },
        "active_supervision_result": {
            "status": "ACTIVE_SUPERVISION_READY",
            "ready": True,
            "active_supervision_enabled": True,
            "trade_window_open": True,
            "may_execute_demo_by_this_module": False,
            "may_execute_live_by_this_module": False,
            "may_call_broker_by_this_module": False,
            "may_move_money": False,
            "next_best_packet": "AIOS_FOREX_OWNER_APPROVED_DEMO_MULTI_PAIR_BURST_RUNTIME_EXECUTION_V1",
            "blocked_action_queue": [],
            "owner_review_queue": [
                {"review_id": "runtime_execution_packet_required_for_any_order"}
            ],
            "safety": {"metadata_only": True, "no_money_movement": True},
        },
        "receipt_state": {
            "receipt_required_after_execution": True,
            "outstanding_receipts": False,
            "receipts_sanitized": True,
            "post_trade_review_complete": True,
            "receipt_capture_ready": False,
            "receipt_capture_metadata_only": True,
            "next_trade_blocked_until_receipts_reviewed": True,
            "receipt_values_sanitized": True,
            "no_raw_broker_receipts": True,
        },
        "close_policy": {
            "no_new_risk_during_close_protection": True,
            "no_new_trade_seeking_during_close_protection": True,
            "close_boundary_owner_summary_required": True,
            "owner_attention_if_unreviewed_receipts": True,
            "post_close_maintenance_prep_allowed": True,
            "receipt_capture_allowed": True,
            "broker_call_allowed": False,
            "trade_execution_allowed": False,
            "live_market_data_call_allowed": False,
            "strategy_mutation_allowed": False,
            "scheduler_creation_allowed": False,
            "daemon_creation_allowed": False,
            "raw_values_echoed": False,
        },
        "risk_state": {
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "drawdown_within_limit": True,
            "close_boundary_risk_review_required": True,
            "max_risk_per_trade_pct": 0.01,
            "max_total_burst_risk_pct": 0.03,
        },
        "owner_attention_policy": {
            "owner_attention_if_unreviewed_receipts": True,
            "owner_attention_if_post_trade_review_incomplete": True,
            "owner_attention_if_risk_blocked": True,
            "close_boundary_owner_summary_required": True,
            "raw_values_echoed": False,
            "alert_channel_metadata_only": True,
            "no_alert_runtime_created": True,
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
    result = evaluate_forex_market_close_protection_and_receipt_capture_v1(payload)
    return {
        "sample_name": sample_name,
        "status": result["status"],
        "ready": result["ready"],
        "close_protection_enabled": result["close_protection_enabled"],
        "close_window_active": result["close_window_active"],
        "new_risk_allowed_by_this_module": result[
            "new_risk_allowed_by_this_module"
        ],
        "new_trade_seeking_allowed_by_this_module": result[
            "new_trade_seeking_allowed_by_this_module"
        ],
        "receipt_capture_required": result["receipt_capture_required"],
        "receipt_capture_ready": result["receipt_capture_ready"],
        "post_trade_review_required": result["post_trade_review_required"],
        "post_close_maintenance_ready": result["post_close_maintenance_ready"],
        "owner_attention_required": result["owner_attention_required"],
        "next_best_packet": result["next_best_packet"],
        "blockers": result["blockers"],
    }


def main() -> None:
    samples = [
        _run("clean close protection post-close maintenance ready"),
        _run("outstanding receipts waiting", receipt_state={"outstanding_receipts": True}),
        _run(
            "post-trade review incomplete",
            receipt_state={"post_trade_review_complete": False},
        ),
        _run("receipt capture ready", receipt_state={"receipt_capture_ready": True}),
        _run(
            "calendar wrong blocked",
            runtime_calendar_result={"current_runtime_posture": "ACTIVE_SUPERVISION"},
        ),
        _run(
            "active supervision unsafe blocked",
            active_supervision_result={"may_call_broker_by_this_module": True},
        ),
        _run("kill switch blocked", risk_state={"kill_switch_active": True}),
        _run(
            "policy no-new-risk violation",
            close_policy={"no_new_risk_during_close_protection": False},
        ),
        _run(
            "banking false-positive guard",
            top={
                "close_approaching": True,
                "reopen_approaching": True,
                "close_boundary": "protect_close",
            },
        ),
    ]
    print(json.dumps(samples, separators=(",", ":")))


if __name__ == "__main__":
    main()
