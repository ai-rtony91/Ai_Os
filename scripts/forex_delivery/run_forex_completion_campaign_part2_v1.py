"""Run the local safe Forex Completion Campaign Part 2 sample."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_completion_campaign_part2_v1 import (  # noqa: E402
    evaluate_forex_completion_campaign_part2_v1,
)


def safe_sample_payload() -> dict:
    return {
        "protected_runtime_execution_result": {
            "protected_runtime_status": "PROTECTED_ONE_ORDER_GATE_CLEARED",
            "broker_api_called": False,
            "credential_read": False,
        },
        "credential_session_bridge_result": {
            "credential_session_bridge_status": "RUNTIME_CREDENTIAL_SESSION_BRIDGE_READY",
        },
        "post_execution_review_loop_result": {
            "post_execution_review_status": "POST_EXECUTION_REVIEW_LOOP_READY",
        },
        "supervised_operation_readiness_result": {
            "readiness_status": "TWENTY_TWO_HOUR_SIX_DAY_READINESS_PASSED",
            "total_score": 100,
        },
        "profit_proof_metadata": {
            "evidence_sample_count": 120,
            "min_evidence_sample_count": 30,
            "expectancy_positive": True,
            "profit_factor_meets_threshold": True,
            "drawdown_within_limit": True,
            "walk_forward_gate_cleared": True,
            "out_of_sample_passed": True,
            "spread_slippage_model_present": True,
            "evidence_quality_status": "PROVEN",
        },
        "return_target_validation_metadata": {
            "return_target_defined": True,
            "target_evidence_status": "PROVEN",
            "fixed_return_target_promised": False,
            "guaranteed_profit_claimed": False,
            "owner_target_review_required": True,
            "evidence_supports_target_review": True,
        },
        "broker_runtime_evidence_metadata": {
            "one_order_protected_gate_present": True,
            "broker_api_called": False,
            "credential_read": False,
        },
        "oanda_mode_declaration": {"mode": "OANDA_DEMO"},
        "safety_real_money_gate_metadata": {
            "kill_switch_ready": True,
            "daily_loss_stop_ready": True,
            "max_loss_gate_ready": True,
            "stop_loss_required": True,
            "take_profit_required": True,
            "one_order_only": True,
            "money_movement_allowed": False,
            "live_trading_allowed": False,
            "owner_live_exception_required": True,
        },
        "dashboard_truth_owner_control_metadata": {
            "dashboard_truth_contract_present": True,
            "owner_action_queue_present": True,
            "sos_ready": True,
            "audit_ready": True,
            "manual_owner_control_required": True,
            "no_dashboard_runtime_created": True,
        },
        "capital_planner_metadata": {"capital_planner_ready": True},
        "owner_value_entry_metadata": {"owner_control_ready": True},
        "sos_metadata": {"sos_ready": True},
        "live_execution_and_capital_operation_campaign_result": {
            "money_moved": False,
        },
    }


def main() -> int:
    result = evaluate_forex_completion_campaign_part2_v1(safe_sample_payload())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("schema") and result.get("campaign_status") else 1


if __name__ == "__main__":
    raise SystemExit(main())
