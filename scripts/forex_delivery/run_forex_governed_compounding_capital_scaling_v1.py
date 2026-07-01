from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_governed_compounding_capital_scaling_v1 import (
    evaluate_forex_governed_compounding_capital_scaling_v1,
)

def _payload() -> dict:
    return {
        "balance_observer_result": {
            "status": "GO",
            "ready": True,
            "realized_profit_from_baseline": 2500.0,
            "equity_drift": 12.5,
            "target_return_reached": False,
            "target_balance_reached": False,
            "withdrawal_deferred": True,
            "bank_routing_deferred": True,
            "money_moved": False,
        },
        "compounding_scale_policy": {
            "compounding_enabled": True,
            "owner_review_required": True,
            "scale_up_allowed": True,
            "scale_down_on_drawdown": True,
            "stop_at_target": True,
            "current_risk_budget_pct": 0.0025,
            "max_scale_step_pct": 0.0010,
            "max_risk_per_trade_pct": 0.01,
            "max_total_burst_risk_pct": 0.03,
            "profit_lock_pct": 0.35,
            "reinvest_profit_pct": 0.25,
            "minimum_verified_profit_to_scale": 500.0,
            "consecutive_scale_ups_since_review": 1,
            "max_consecutive_scale_ups_before_review": 4,
            "withdrawal_allowed": False,
            "bank_routing_allowed": False,
            "money_movement_allowed": False,
        },
        "proof_state": {
            "receipts_sanitized": True,
            "realized_pnl_verified": True,
            "repeatability_score": 82,
            "proof_ready_for_scaling": True,
            "fake_pnl_blocked": True,
        },
        "risk_state": {
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "drawdown_within_limit": True,
            "current_drawdown_pct": 0.01,
            "max_drawdown_pct": 0.04,
            "current_daily_loss_pct": 0.005,
            "max_daily_loss_pct": 0.03,
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


def _sample(name: str, **updates: dict) -> dict:
    payload = _payload()
    payload["sample_name"] = name
    for section, section_updates in updates.items():
        payload[section].update(section_updates)
    return payload


def main() -> None:
    samples = [
        _sample("clean scale up"),
        _sample(
            "hold because compounding disabled",
            compounding_scale_policy={"compounding_enabled": False},
        ),
        _sample(
            "hold because low repeatability",
            proof_state={"repeatability_score": 50},
        ),
        _sample(
            "owner review because scale up not allowed",
            compounding_scale_policy={"scale_up_allowed": False},
        ),
        _sample(
            "protect profit because target return reached",
            balance_observer_result={"target_return_reached": True},
        ),
        _sample(
            "protect profit because target balance reached",
            balance_observer_result={"target_balance_reached": True},
        ),
        _sample(
            "scale down because drawdown breach",
            risk_state={"drawdown_within_limit": False},
        ),
        _sample("blocked missing proof", proof_state={"receipts_sanitized": False}),
    ]
    results = []
    for sample in samples:
        output = evaluate_forex_governed_compounding_capital_scaling_v1(sample)
        results.append(
            {
                "sample_name": sample["sample_name"],
                "status": output["status"],
                "scale_decision": output["scale_decision"],
                "scale_direction": output["scale_direction"],
                "current_risk_budget_pct": output["current_risk_budget_pct"],
                "proposed_next_risk_budget_pct": output["proposed_next_risk_budget_pct"],
                "profit_lock_amount": output["profit_lock_amount"],
                "reinvest_amount": output["reinvest_amount"],
                "protected_profit_amount": output["protected_profit_amount"],
                "next_best_packet": output["next_best_packet"],
                "blockers": output["blockers"],
            }
        )
    print(json.dumps(results, separators=(",", ":")))


if __name__ == "__main__":
    main()
