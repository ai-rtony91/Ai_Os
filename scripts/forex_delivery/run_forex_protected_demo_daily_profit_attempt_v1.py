from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_protected_demo_daily_profit_attempt_v1 import (  # noqa: E402
    evaluate_forex_protected_demo_daily_profit_attempt_v1,
)


def _sample_payload() -> dict:
    return {
        "daily_profit_evidence_result": {
            "daily_profit_status": "READY_FOR_PROTECTED_DEMO_PROFIT_ATTEMPT",
            "daily_profit_ready": True,
            "broker_api_called": False,
            "credential_read": False,
            "live_trade_executed": False,
            "demo_trade_executed": False,
            "money_moved": False,
        },
        "order_candidate": {
            "instrument": "EUR_USD",
            "side": "buy",
            "order_type": "market",
            "units": 1000,
            "setup_id": "setup-001",
            "evidence_id": "evidence-001",
            "expected_r_multiple": "1.8",
            "minimum_reward_risk_ratio": "1.5",
            "spread_within_limit": True,
            "slippage_within_limit": True,
            "session_allowed": True,
            "news_blackout_clear": True,
            "duplicate_candidate": False,
        },
        "risk_plan": {
            "max_risk_per_trade_pct": "0.01",
            "max_daily_loss_pct": "0.03",
            "stop_loss_present": True,
            "take_profit_present": True,
            "one_order_only": True,
            "max_order_count_this_packet": 1,
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "next_order_blocked_until_review": True,
        },
        "execution_window": {
            "execution_window_defined": True,
            "pre_trade_check_ready": True,
            "owner_can_cancel": True,
            "owner_approval_required": True,
            "credential_session_bridge_ready": True,
            "protected_runtime_gate_ready": True,
            "oanda_demo_mode_declared": True,
        },
        "protected_demo_policy": {
            "demo_only": True,
            "real_broker_call_allowed": False,
            "live_trading_allowed": False,
            "money_movement_allowed": False,
            "credential_read": False,
            "credential_stored": False,
            "broker_api_called": False,
            "dry_run_or_metadata_only": True,
            "actual_demo_execution_authorized": False,
        },
        "post_attempt_review": {
            "post_trade_review_required": True,
            "daily_pnl_record_required": True,
            "sanitized_receipt_required": True,
            "no_second_trade_without_review": True,
            "owner_review_required": True,
        },
    }


def main() -> int:
    result = evaluate_forex_protected_demo_daily_profit_attempt_v1(_sample_payload())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
