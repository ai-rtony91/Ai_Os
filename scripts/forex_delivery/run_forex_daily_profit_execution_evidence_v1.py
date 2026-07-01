from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_daily_profit_execution_evidence_v1 import (  # noqa: E402
    evaluate_forex_daily_profit_execution_evidence_v1,
)


def _sample_payload() -> dict:
    return {
        "evidence_sample_count": 80,
        "min_evidence_sample_count": 50,
        "expectancy_positive": True,
        "profit_factor": "1.65",
        "min_profit_factor": "1.25",
        "max_drawdown_pct": "0.08",
        "max_allowed_drawdown_pct": "0.12",
        "walk_forward_gate_cleared": True,
        "out_of_sample_passed": True,
        "spread_slippage_model_present": True,
        "daily_profit_target_defined": True,
        "guaranteed_profit_claimed": False,
        "fixed_return_target_promised": False,
        "protected_runtime_gate_ready": True,
        "credential_session_bridge_ready": True,
        "post_trade_review_ready": True,
        "twenty_two_hour_six_day_ready": True,
        "broker_mode_declared": "OANDA_DEMO",
        "one_order_gate_ready": True,
        "owner_approval_required": True,
        "broker_api_called": False,
        "credential_read": False,
        "live_trade_executed": False,
        "demo_trade_executed": False,
        "max_risk_per_trade_pct": "0.01",
        "max_daily_loss_pct": "0.03",
        "stop_loss_required": True,
        "take_profit_required": True,
        "kill_switch_ready": True,
        "kill_switch_active": False,
        "daily_loss_stop_ready": True,
        "daily_loss_stop_active": False,
        "one_order_only": True,
        "next_order_blocked_until_review": True,
        "pre_trade_check_ready": True,
        "execution_window_defined": True,
        "post_trade_review_required": True,
        "daily_pnl_record_required": True,
        "no_second_trade_without_review": True,
        "owner_can_stop": True,
    }


def main() -> int:
    result = evaluate_forex_daily_profit_execution_evidence_v1(_sample_payload())
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
