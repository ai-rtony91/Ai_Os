"""Run safe sample payloads for governed multi-pair burst Vacation Mode."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_vacation_mode_multi_pair_burst_rollup_v1 import (  # noqa: E402
    evaluate_forex_vacation_mode_multi_pair_burst_rollup_v1,
)


def _candidate(pair: str, score: int) -> dict:
    return {
        "pair": pair,
        "side": "BUY",
        "order_type": "MARKET",
        "units": 1000,
        "setup_id": f"SETUP-{pair}",
        "evidence_id": f"EVIDENCE-{pair}",
        "candidate_score": score,
        "expected_r_multiple": 1.8,
        "minimum_reward_risk_ratio": 1.2,
        "risk_pct": 0.005,
        "stop_loss_present": True,
        "take_profit_present": True,
        "session_allowed": True,
        "news_blackout_clear": True,
        "spread_within_limit": True,
        "slippage_within_limit": True,
    }


def _base_payload(mode: str) -> dict:
    return {
        "governed_burst_requested": True,
        "pair_universe": {
            "allowed_pairs": ["EUR_USD", "GBP_USD", "USD_JPY"],
            "excluded_pairs": [],
            "candidate_pairs": ["EUR_USD", "GBP_USD", "USD_JPY"],
            "max_pairs_to_scan": 3,
            "all_pairs_scan_requested": True,
            "only_trade_allowed_pairs": True,
            "unsupported_pairs_block": True,
            "pair_universe_source": "OWNER_DECLARED_SAMPLE",
            "owner_review_required": True,
        },
        "opportunity_batch": {
            "candidates": [
                _candidate("EUR_USD", 91),
                _candidate("GBP_USD", 88),
                _candidate("USD_JPY", 82),
            ],
            "min_candidate_score": 70,
            "max_candidates_per_burst": 2,
            "require_stop_loss": True,
            "require_take_profit": True,
            "require_session_allowed": True,
            "require_news_blackout_clear": True,
            "require_spread_within_limit": True,
            "require_slippage_within_limit": True,
            "duplicate_pair_block": True,
        },
        "risk_policy": {
            "max_risk_per_trade_pct": 0.01,
            "max_total_burst_risk_pct": 0.03,
            "max_daily_loss_pct": 0.03,
            "max_concurrent_open_trades": 4,
            "max_candidates_per_burst": 2,
            "max_same_currency_exposure_count": 3,
            "correlation_gate_required": True,
            "correlation_within_limit": True,
            "currency_exposure_within_limit": True,
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "one_burst_at_a_time": True,
            "next_burst_blocked_until_review": True,
        },
        "permission": {
            "mode": mode,
            "owner_review_required": True,
            "owner_live_approval_required_for_live": True,
            "runtime_credentials_required_for_execution": True,
            "proof_required_for_live": True,
            "previous_burst_review_complete": True,
            "receipt_required": True,
            "post_burst_review_required": True,
            "may_execute_by_this_module": False,
            "may_call_broker_by_this_module": False,
            "owner_live_approval_metadata_present": mode == "LIVE_MICRO_RUNTIME_INTENT",
        },
        "proof": {
            "demo_proof_ready": True,
            "live_micro_review_ready": True,
            "repeatability_score": 84,
        },
        "runtime_boundary": {
            "runtime_session_available": True,
            "credential_values_in_payload": False,
            "account_id_in_payload": False,
            "no_stored_credentials": True,
        },
    }


def _waiting_receipts_payload() -> dict:
    payload = _base_payload("LIVE_MICRO_RUNTIME_INTENT")
    payload["burst_receipts"] = {
        "receipts_present": False,
        "receipts": [],
        "all_receipts_sanitized": True,
        "no_account_ids": True,
        "no_credentials": True,
        "all_order_ids_redacted": True,
        "broker_name": "OANDA",
        "mode": "OANDA_LIVE",
        "live_trade_executed_by_this_module": False,
        "broker_api_called_by_this_module": False,
        "money_moved": False,
    }
    return payload


def main() -> None:
    samples = {
        "valid_demo_multi_pair_burst_intent": _base_payload("DEMO_BURST"),
        "valid_live_micro_multi_pair_owner_review": _base_payload("LIVE_MICRO_REVIEW"),
        "valid_protected_live_micro_burst_runtime_intent_metadata": _base_payload(
            "LIVE_MICRO_RUNTIME_INTENT"
        ),
        "waiting_for_burst_receipts": _waiting_receipts_payload(),
    }
    results = {
        name: evaluate_forex_vacation_mode_multi_pair_burst_rollup_v1(payload)
        for name, payload in samples.items()
    }
    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
