from pathlib import Path

from automation.forex_engine.forex_multi_pair_universe_v1 import HARD_FALSE_FIELDS
from automation.forex_engine.forex_vacation_mode_multi_pair_burst_rollup_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_SENSITIVE_DATA,
    READY_FOR_DEMO_MULTI_PAIR_BURST_INTENT,
    READY_FOR_LIVE_MICRO_MULTI_PAIR_BURST_OWNER_REVIEW,
    READY_FOR_PROTECTED_LIVE_MICRO_MULTI_PAIR_BURST_RUNTIME_INTENT,
    WAITING_FOR_MULTI_PAIR_BURST_RECEIPTS,
    evaluate_forex_vacation_mode_multi_pair_burst_rollup_v1,
)


def _candidate(pair="EUR_USD", score=90):
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


def _payload(mode="DEMO_BURST", include_receipts=False, receipts_present=False):
    payload = {
        "governed_burst_requested": True,
        "pair_universe": {
            "allowed_pairs": ["EUR_USD", "GBP_USD", "USD_JPY"],
            "excluded_pairs": [],
            "candidate_pairs": ["EUR_USD", "GBP_USD", "USD_JPY"],
            "max_pairs_to_scan": 3,
            "all_pairs_scan_requested": True,
            "only_trade_allowed_pairs": True,
            "unsupported_pairs_block": True,
            "pair_universe_source": "OWNER_DECLARED",
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
    if include_receipts:
        payload["burst_receipts"] = {
            "receipts_present": receipts_present,
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


def test_demo_multi_pair_burst_routes_correctly():
    result = evaluate_forex_vacation_mode_multi_pair_burst_rollup_v1(
        _payload("DEMO_BURST")
    )
    assert result["campaign_status"] == READY_FOR_DEMO_MULTI_PAIR_BURST_INTENT
    assert result["next_best_packet"] == "AIOS_FOREX_OWNER_APPROVED_DEMO_MULTI_PAIR_BURST_RUNTIME_EXECUTION_V1"


def test_live_micro_owner_review_routes_correctly():
    result = evaluate_forex_vacation_mode_multi_pair_burst_rollup_v1(
        _payload("LIVE_MICRO_REVIEW")
    )
    assert result["campaign_status"] == READY_FOR_LIVE_MICRO_MULTI_PAIR_BURST_OWNER_REVIEW


def test_live_protected_burst_runtime_intent_routes_correctly():
    result = evaluate_forex_vacation_mode_multi_pair_burst_rollup_v1(
        _payload("LIVE_MICRO_RUNTIME_INTENT")
    )
    assert result["campaign_status"] == READY_FOR_PROTECTED_LIVE_MICRO_MULTI_PAIR_BURST_RUNTIME_INTENT


def test_waiting_receipts_routes_correctly():
    result = evaluate_forex_vacation_mode_multi_pair_burst_rollup_v1(
        _payload("LIVE_MICRO_RUNTIME_INTENT", include_receipts=True, receipts_present=False)
    )
    assert result["campaign_status"] == WAITING_FOR_MULTI_PAIR_BURST_RECEIPTS
    assert result["next_best_packet"] == "AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1"


def test_sensitive_data_blocks_and_does_not_echo_raw_value():
    result = evaluate_forex_vacation_mode_multi_pair_burst_rollup_v1(
        {"governed_burst_requested": True, "api_key": "sk-secret-example"}
    )
    assert result["campaign_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "sk-secret-example" not in str(result)


def test_banking_focus_blocks():
    result = evaluate_forex_vacation_mode_multi_pair_burst_rollup_v1(
        {"governed_burst_requested": True, "withdrawal_plan": True}
    )
    assert result["campaign_status"] == BLOCKED_BY_BANKING_FOCUS


def test_all_hard_false_fields_remain_false():
    result = evaluate_forex_vacation_mode_multi_pair_burst_rollup_v1(
        _payload("DEMO_BURST")
    )
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False


def test_production_source_has_no_forbidden_runtime_markers():
    files = [
        Path("automation/forex_engine/forex_multi_pair_universe_v1.py"),
        Path("automation/forex_engine/forex_multi_pair_opportunity_batch_v1.py"),
        Path("automation/forex_engine/forex_basket_risk_exposure_governor_v1.py"),
        Path("automation/forex_engine/forex_governed_burst_permission_engine_v1.py"),
        Path("automation/forex_engine/forex_burst_receipt_and_post_burst_review_v1.py"),
        Path("automation/forex_engine/forex_vacation_mode_multi_pair_burst_rollup_v1.py"),
    ]
    forbidden = [
        "requests",
        "socket",
        "urllib",
        "subprocess",
        "os.environ",
        "broker_sdk",
        "schedule.every",
        "start-process",
    ]
    hits = {
        str(path): [marker for marker in forbidden if marker in path.read_text(encoding="utf-8").lower()]
        for path in files
    }
    assert not any(hits.values()), hits
