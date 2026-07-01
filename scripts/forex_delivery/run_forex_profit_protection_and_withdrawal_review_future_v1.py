from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_profit_protection_and_withdrawal_review_future_v1 import (
    evaluate_forex_profit_protection_and_withdrawal_review_future_v1,
)


def _payload() -> dict:
    return {
        "compounding_result": {
            "status": "GOVERNED_COMPOUNDING_SCALE_UP_ALLOWED",
            "ready": True,
            "scale_decision": "SCALE_UP",
            "protected_profit_amount": 800.0,
            "reinvest_amount": 400.0,
            "profit_lock_amount": 800.0,
            "money_moved": False,
            "withdrawal_allowed_by_this_module": False,
            "bank_routing_allowed_by_this_module": False,
            "live_profit_guaranteed": False,
            "fixed_return_promised_by_aios": False,
        },
        "profit_protection_policy": {
            "realized_profit_only": True,
            "receipts_required": True,
            "receipts_sanitized": True,
            "owner_review_required": True,
            "protect_profit_at_target": True,
            "profit_lock_pct": 0.4,
            "reinvest_profit_pct": 0.2,
            "minimum_profit_to_protect": 500.0,
            "withdrawal_review_future_allowed": True,
            "withdrawal_execution_allowed": False,
            "bank_routing_allowed": False,
            "money_movement_allowed": False,
            "transfer_allowed": False,
            "ach_allowed": False,
            "wire_allowed": False,
            "card_allowed": False,
            "deposit_allowed": False,
        },
        "profit_state": {
            "realized_net_profit": 2000.0,
            "unrealized_profit": 0.0,
            "target_reached": False,
            "target_type": "RETURN_TARGET",
            "receipts_ready": True,
            "pnl_reconciled": True,
            "fake_pnl_blocked": True,
            "balance_snapshot_ready": True,
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


def _run(name: str, **updates: dict) -> dict:
    payload = _payload()
    for section, values in updates.items():
        payload[section].update(values)
    payload["sample_name"] = name
    output = evaluate_forex_profit_protection_and_withdrawal_review_future_v1(payload)
    return {
        "sample_name": name,
        "status": output["status"],
        "protected_profit_amount": output["protected_profit_amount"],
        "reinvest_amount": output["reinvest_amount"],
        "deferred_withdrawal_review_amount": output["deferred_withdrawal_review_amount"],
        "withdrawal_review_future_enabled": output["withdrawal_review_future_enabled"],
        "withdrawal_execution_allowed": output["withdrawal_execution_allowed"],
        "bank_routing_allowed": output["bank_routing_allowed"],
        "money_moved": output["money_moved"],
        "next_best_packet": output["next_best_packet"],
        "blockers": output["blockers"],
    }


def main() -> None:
    results = [
        _run("profit lock ready"),
        _run("future withdrawal review ready", profit_state={"target_reached": True}),
        _run(
            "reinvestment bucket ready",
            profit_protection_policy={"minimum_profit_to_protect": 5000.0},
            compounding_result={"reinvest_amount": 250.0},
        ),
        _run(
            "unrealized profit blocked",
            profit_state={"realized_net_profit": 0.0, "unrealized_profit": 250.0},
        ),
        _run("missing receipts blocked", profit_state={"receipts_ready": False}),
        _run("active withdrawal blocked", profit_protection_policy={"withdrawal_execution_allowed": True}),
        _run("compounding result blocked", compounding_result={"ready": False}),
    ]
    print(json.dumps(results, separators=(",", ":")))


if __name__ == "__main__":
    main()
