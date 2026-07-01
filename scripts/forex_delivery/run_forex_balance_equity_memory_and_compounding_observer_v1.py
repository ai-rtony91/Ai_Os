from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_balance_equity_memory_and_compounding_observer_v1 import (  # noqa: E402
    evaluate_forex_balance_equity_memory_and_compounding_observer_v1,
)


def _base_payload() -> dict:
    return {
        "balance_memory": {
            "starting_balance": 10000.0,
            "current_balance": 10300.0,
            "current_equity": 10325.0,
            "realized_net_pnl": 300.0,
            "unrealized_pnl": 25.0,
            "trade_open_balance": 10250.0,
            "trade_close_balance": 10300.0,
            "day_start_balance": 10100.0,
            "day_current_balance": 10300.0,
            "week_start_balance": 10050.0,
            "week_current_balance": 10300.0,
            "month_start_balance": 10000.0,
            "month_current_balance": 10300.0,
            "vacation_mode_start_balance": 9900.0,
            "vacation_mode_current_balance": 10300.0,
            "snapshot_scope": "RUNTIME",
            "snapshot_event_id": "BALANCE-EVENT-001",
            "account_id_absent": True,
            "credentials_absent": True,
            "broker_values_absent": True,
        },
        "receipt_proof": {
            "receipts_required": True,
            "receipts_sanitized": True,
            "realized_pnl_verified": True,
            "fake_pnl_blocked": True,
            "balance_snapshot_source": "SANITIZED_RUNTIME_SNAPSHOT",
            "proof_ready_for_learning": True,
        },
        "compounding_policy": {
            "compounding_enabled": False,
            "compound_mode": "HOLD",
            "target_return_pct": 0.10,
            "target_balance": 12000.0,
            "profit_lock_pct": 0.5,
            "reinvest_profit_pct": 0.5,
            "max_scale_step_pct": 0.10,
            "stop_compounding_at_target": True,
            "scale_down_on_drawdown": True,
            "owner_review_required": True,
            "withdrawal_allowed": False,
            "bank_routing_allowed": False,
        },
        "risk_state": {
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "drawdown_within_limit": True,
            "max_drawdown_pct": 0.08,
            "current_drawdown_pct": 0.02,
            "max_daily_loss_pct": 0.03,
            "current_daily_loss_pct": 0.01,
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


def _sample(name: str, **updates) -> dict:
    payload = _base_payload()
    payload["sample_name"] = name
    for section, values in updates.items():
        payload[section].update(values)
    return payload


def main() -> None:
    samples = [
        _sample("profit stacking observation"),
        _sample(
            "compounding eligible",
            compounding_policy={
                "compounding_enabled": True,
                "compound_mode": "COMPOUND_TO_PERCENT_TARGET",
            },
        ),
        _sample("target return reached", compounding_policy={"target_return_pct": 0.02}),
        _sample("target balance reached", compounding_policy={"target_balance": 10200.0}),
        _sample(
            "drawdown scale down",
            compounding_policy={"compounding_enabled": True},
            risk_state={"drawdown_within_limit": False, "current_drawdown_pct": 0.12},
        ),
        _sample("missing receipt proof blocked", receipt_proof={"receipts_sanitized": False}),
    ]
    results = []
    for sample in samples:
        result = evaluate_forex_balance_equity_memory_and_compounding_observer_v1(sample)
        results.append(
            {
                "sample_name": sample["sample_name"],
                "status": result["status"],
                "ready": result["ready"],
                "realized_profit_from_baseline": result["realized_profit_from_baseline"],
                "equity_drift": result["equity_drift"],
                "recommended_compounding_action": result["recommended_compounding_action"],
                "next_best_packet": result["next_best_packet"],
            }
        )
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
