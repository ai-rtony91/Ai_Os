from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.forex_proof_pipeline_pause_and_continue_v1 import (
    evaluate_forex_proof_pipeline_pause_and_continue_v1 as evaluate_pipeline,
)


def _no_receipt_payload() -> dict:
    return {
        "proof_source": {
            "source_type": "OWNER_APPROVED_DEMO_READINESS",
            "upstream_packet_id": "RUNNER-NO-RECEIPT",
            "receipt_present": False,
            "demo_order_executed": True,
            "live_trade_executed": False,
            "money_moved": False,
            "receipt_sanitized": False,
            "raw_broker_payload_present": False,
            "account_id_redacted": True,
            "order_id_redacted": True,
            "credential_values_redacted": True,
            "profit_claimed": False,
        },
    }


def _ready_payload() -> dict:
    return {
        "proof_source": {
            "source_type": "OANDA_DEMO_RECEIPT",
            "upstream_packet_id": "RUNNER-READY-001",
            "receipt_present": True,
            "demo_order_executed": True,
            "live_trade_executed": False,
            "money_moved": False,
            "receipt_sanitized": True,
            "raw_broker_payload_present": False,
            "account_id_redacted": True,
            "order_id_redacted": True,
            "credential_values_redacted": True,
            "profit_claimed": False,
        },
        "receipt": {
            "receipt_present": True,
            "broker_name": "OANDA",
            "mode": "OANDA_DEMO",
            "demo_order_executed": True,
            "live_trade_executed": False,
            "money_moved": False,
            "order_count": 1,
            "instrument": "EUR_USD",
            "side": "buy",
            "units": 1000,
            "order_id_redacted": True,
            "account_id_redacted": True,
            "credential_values_redacted": True,
            "stop_loss_present": True,
            "take_profit_present": True,
            "execution_timestamp_present": True,
            "receipt_sanitized": True,
        },
        "post_trade_review": {
            "post_trade_review_required": True,
            "post_trade_review_completed": True,
            "daily_pnl_recorded": True,
            "realized_pnl_present": True,
            "realized_pnl_is_demo": True,
            "spread_slippage_recorded": True,
            "risk_review_recorded": True,
            "owner_review_required": True,
            "no_second_trade_without_review": True,
        },
        "evidence": {
            "sample_count": 20,
            "min_sample_count": 20,
            "expectancy_positive": True,
            "profit_factor": 1.8,
            "min_profit_factor": 1.3,
            "max_drawdown_pct": 0.02,
            "max_allowed_drawdown_pct": 0.03,
            "walk_forward_gate_cleared": True,
            "out_of_sample_passed": True,
            "daily_review_count": 1,
            "weekly_review_count": 1,
            "monthly_review_count": 1,
            "yearly_review_ready": True,
            "guaranteed_profit_claimed": False,
            "fixed_return_promised": False,
        },
        "risk": {
            "max_risk_per_trade_pct": 0.005,
            "max_daily_loss_pct": 0.02,
            "kill_switch_ready": True,
            "daily_loss_stop_ready": True,
        },
        "owner": {
            "live_micro_owner_review_required": True,
            "live_execution_authorized": False,
            "live_trade_executed": False,
        },
    }


def _emit(label: str, payload: dict) -> None:
    result = evaluate_pipeline(payload)
    print(json.dumps({label: result}, indent=2, sort_keys=True))


def main() -> int:
    _emit("SCENARIO_NO_RECEIPT", _no_receipt_payload())
    _emit("SCENARIO_READY", _ready_payload())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
