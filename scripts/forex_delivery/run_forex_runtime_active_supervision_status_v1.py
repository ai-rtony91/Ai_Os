from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_runtime_active_supervision_status_v1 import (
    evaluate_forex_runtime_active_supervision_status_v1,
)


def _payload() -> dict:
    return {
        "runtime_calendar_result": {
            "status": "RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION",
            "ready": True,
            "runtime_job_router_enabled": True,
            "current_runtime_posture": "ACTIVE_SUPERVISION",
            "primary_job_lane": "supervise_runtime",
            "trade_window_open": True,
            "execution_authorized_by_calendar": False,
            "next_best_packet": "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1",
            "blocked_job_queue": [],
            "vacation_mode_toggle_semantics": {"owner_toggle_required": True},
            "kill_switch_semantics": {"kill_switch_blocks_trade": True},
        },
        "vacation_mode_result": {
            "campaign_status": "VACATION_MODE_OWNER_TOGGLE_ACTIVE_SUPERVISION_READY",
            "campaign_ready": True,
            "vacation_mode_requested": True,
            "vacation_mode_toggle_state": "ON",
            "vacation_mode_operation_state": "VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE",
            "new_trade_seeking_allowed_by_this_module": False,
            "maintenance_allowed_by_this_module": True,
            "owner_attention_required": False,
            "next_best_packet": "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1",
            "safety": {"metadata_only": True},
        },
        "permission_snapshot": {
            "may_scan_metadata": True,
            "may_prepare_candidates": True,
            "may_prepare_demo_runtime_intent_metadata": True,
            "may_prepare_live_owner_review_metadata": True,
            "may_prepare_maintenance_work": True,
            "may_prepare_receipt_review": True,
            "may_prepare_balance_learning_review": True,
            "may_execute_demo_by_this_module": False,
            "may_execute_live_by_this_module": False,
            "may_call_broker_by_this_module": False,
            "may_read_credentials_by_this_module": False,
            "may_move_money": False,
            "may_withdraw": False,
            "may_bank_route": False,
            "owner_runtime_packet_required_for_execution": True,
        },
        "risk_state": {
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "drawdown_within_limit": True,
            "current_drawdown_pct": 0.01,
            "max_drawdown_pct": 0.04,
            "current_daily_loss_pct": 0.002,
            "max_daily_loss_pct": 0.03,
            "max_risk_per_trade_pct": 0.01,
            "max_total_burst_risk_pct": 0.03,
            "risk_policy_owner_reviewed": True,
        },
        "receipt_state": {
            "receipt_required_after_execution": True,
            "outstanding_receipts": False,
            "receipts_sanitized": True,
            "post_trade_review_complete": True,
            "next_trade_blocked_until_receipts_reviewed": True,
        },
        "balance_state": {
            "balance_memory_ready": True,
            "compounding_observer_ready": True,
            "withdrawal_deferred": True,
            "bank_routing_deferred": True,
            "money_moved": False,
            "current_balance_present": True,
            "current_equity_present": True,
        },
        "compounding_state": {
            "compounding_scale_ready": True,
            "compounding_status": "GOVERNED_COMPOUNDING_SCALE_UP_ALLOWED",
            "scale_decision": "SCALE_UP",
            "scale_direction": "UP",
            "proposed_next_risk_budget_pct": 0.003,
            "owner_decision_required": True,
            "money_moved": False,
            "withdrawal_allowed_by_this_module": False,
            "bank_routing_allowed_by_this_module": False,
        },
        "profit_protection_state": {
            "profit_protection_ready": True,
            "profit_protection_status": "PROFIT_LOCK_READY",
            "realized_profit_only": True,
            "withdrawal_review_future_enabled": True,
            "withdrawal_execution_allowed": False,
            "bank_routing_allowed": False,
            "money_moved": False,
        },
        "proof_state": {
            "proof_required": True,
            "proof_ready": True,
            "proof_continuity_ready": True,
            "fake_proof_blocked": True,
            "repeatability_review_ready": True,
            "owner_review_required_for_live": True,
        },
        "candidate_policy": {
            "candidate_refresh_metadata_allowed": True,
            "strategy_mutation_allowed": False,
            "broker_call_allowed": False,
            "live_market_data_call_allowed": False,
            "require_stop_loss": True,
            "require_take_profit": True,
            "require_spread_policy": True,
            "require_slippage_policy": True,
            "require_news_blackout_policy": True,
            "owner_runtime_packet_required_for_execution": True,
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
    payload = _payload()
    for section, values in updates.items():
        payload[section].update(values)
    result = evaluate_forex_runtime_active_supervision_status_v1(payload)
    return {
        "sample_name": sample_name,
        "status": result["status"],
        "ready": result["ready"],
        "active_supervision_enabled": result["active_supervision_enabled"],
        "trade_window_open": result["trade_window_open"],
        "vacation_mode_active": result["vacation_mode_active"],
        "may_scan_metadata": result["may_scan_metadata"],
        "may_prepare_candidates": result["may_prepare_candidates"],
        "may_execute_demo_by_this_module": result["may_execute_demo_by_this_module"],
        "may_execute_live_by_this_module": result["may_execute_live_by_this_module"],
        "may_call_broker_by_this_module": result["may_call_broker_by_this_module"],
        "may_move_money": result["may_move_money"],
        "next_best_packet": result["next_best_packet"],
        "blockers": result["blockers"],
    }


def main() -> None:
    samples = [
        _run("active supervision ready"),
        _run("calendar closed blocked", runtime_calendar_result={"trade_window_open": False}),
        _run("Vacation Mode off fallback", vacation_mode_result={"vacation_mode_toggle_state": "OFF"}),
        _run("kill switch blocked", risk_state={"kill_switch_active": True}),
        _run("outstanding receipts waiting", receipt_state={"outstanding_receipts": True}),
        _run("missing proof waiting", proof_state={"proof_ready": False}),
        _run("balance review required", balance_state={"balance_memory_ready": False}),
        _run("compounding review required", compounding_state={"compounding_scale_ready": False}),
        _run(
            "profit protection review required",
            profit_protection_state={"profit_protection_ready": False},
        ),
    ]
    print(json.dumps(samples, separators=(",", ":")))


if __name__ == "__main__":
    main()
