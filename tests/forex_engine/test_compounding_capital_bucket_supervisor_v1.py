from __future__ import annotations

import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.compounding_capital_bucket_supervisor_v1 import (  # noqa: E402
    BUCKET_ACTIVE_ACCUMULATING,
    BUCKET_BLOCKED_EVIDENCE,
    BUCKET_BLOCKED_MISSING_STATE,
    BUCKET_BLOCKED_POLICY,
    BUCKET_BLOCKED_RISK,
    BUCKET_TARGET_REACHED_COLLECT_PROFIT,
    evaluate_compounding_capital_bucket_supervisor_v1,
)


def bucket_state(current_return_percent=80.0, current_balance=1800.0, starting_balance=1000.0):
    return {
        "starting_balance": starting_balance,
        "current_balance": current_balance,
        "realized_profit": current_balance - starting_balance,
        "unrealized_profit": 0.0,
        "active_deployed_capital": current_balance * 0.5,
        "reserve_capital": current_balance * 0.5,
        "cycle_start_balance": starting_balance,
        "cycle_current_equity": current_balance,
        "cycle_realized_profit": current_balance - starting_balance,
        "cycle_unrealized_profit": 0.0,
        "cycle_trade_count": 4,
        "current_return_percent": current_return_percent,
        "target_return_min_percent": 100.0,
        "target_return_max_percent": 120.0,
        "total_goal_amount": 100000.0,
        "current_goal_progress_percent": (current_balance / 100000.0) * 100.0,
    }


def cycle_policy(**overrides):
    policy = {
        "compounding_enabled": True,
        "collect_when_target_reached": True,
        "redistribute_after_collection": True,
        "max_pairs_per_cycle": 2,
        "min_pair_quality_score": 70.0,
        "equal_weight_allowed": True,
        "risk_weighted_allowed": True,
        "scale_invariant_logic_required": True,
        "allow_future_150_percent_target": False,
        "force_trades_to_hit_quota": False,
    }
    policy.update(overrides)
    return policy


def risk_state(**overrides):
    risk = {
        "risk_gate_passed": True,
        "kill_switch_ready": True,
        "daily_stop_ready": True,
        "max_loss_gate_ready": True,
        "max_total_bucket_risk_percent": 5.0,
        "max_pair_risk_percent": 1.0,
        "margin_safe": True,
        "no_averaging_down": True,
        "one_cycle_at_a_time": True,
    }
    risk.update(overrides)
    return risk


def evidence_state(**overrides):
    evidence = {
        "evidence_capture_ready": True,
        "trade_outcome_tracking_ready": True,
        "profit_collection_tracking_ready": True,
        "redistribution_tracking_ready": True,
        "sanitized_money_state_ready": True,
        "no_profit_guarantee_acknowledged": True,
    }
    evidence.update(overrides)
    return evidence


def pair_candidates():
    return [
        {
            "instrument": "EUR_USD",
            "direction_bias": "LONG",
            "quality_score": 91.0,
            "spread_ok": True,
            "margin_required": 50.0,
            "max_position_size_units": 1000,
            "expected_reward_risk": 2.0,
            "eligible_for_allocation": True,
            "blocked_reason": "",
        },
        {
            "instrument": "GBP_USD",
            "direction_bias": "LONG",
            "quality_score": 82.0,
            "spread_ok": True,
            "margin_required": 60.0,
            "max_position_size_units": 1000,
            "expected_reward_risk": 1.8,
            "eligible_for_allocation": True,
            "blocked_reason": "",
        },
        {
            "instrument": "USD_JPY",
            "direction_bias": "LONG",
            "quality_score": 78.0,
            "spread_ok": True,
            "margin_required": 55.0,
            "max_position_size_units": 1000,
            "expected_reward_risk": 1.7,
            "eligible_for_allocation": True,
            "blocked_reason": "",
        },
    ]


def evaluate(**overrides):
    payload = {
        "bucket_state": bucket_state(),
        "pair_candidates": pair_candidates(),
        "cycle_policy": cycle_policy(),
        "risk_state": risk_state(),
        "evidence_state": evidence_state(),
    }
    payload.update(overrides)
    return evaluate_compounding_capital_bucket_supervisor_v1(**payload)


def assert_execution_false(result):
    assert result["execution_authority"] == {
        "execution_allowed": False,
        "demo_order_allowed": False,
        "live_order_allowed": False,
        "broker_write_allowed": False,
        "autonomous_order_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
    }


def test_default_blocks_missing_state():
    result = evaluate_compounding_capital_bucket_supervisor_v1()
    assert result["status"] == BUCKET_BLOCKED_MISSING_STATE
    assert "missing_bucket_state" in result["blockers"]
    assert_execution_false(result)


def test_failed_risk_gate_blocks():
    result = evaluate(risk_state=risk_state(risk_gate_passed=False))
    assert result["status"] == BUCKET_BLOCKED_RISK


def test_missing_evidence_capture_blocks():
    result = evaluate(evidence_state=evidence_state(evidence_capture_ready=False))
    assert result["status"] == BUCKET_BLOCKED_EVIDENCE


def test_policy_forcing_trades_to_hit_quota_blocks():
    result = evaluate(cycle_policy=cycle_policy(force_trades_to_hit_quota=True))
    assert result["status"] == BUCKET_BLOCKED_POLICY
    assert "force_trades_to_hit_quota_must_be_false" in result["blockers"]


def test_below_target_with_valid_gates_accumulates():
    result = evaluate(bucket_state=bucket_state(current_return_percent=75.0, current_balance=1750.0))
    assert result["status"] == BUCKET_ACTIVE_ACCUMULATING


def test_target_reached_between_100_and_120_collects_profit():
    result = evaluate(bucket_state=bucket_state(current_return_percent=110.0, current_balance=2100.0))
    assert result["status"] == BUCKET_TARGET_REACHED_COLLECT_PROFIT


def test_over_120_warns_to_collect_before_redeploy():
    result = evaluate(bucket_state=bucket_state(current_return_percent=125.0, current_balance=2250.0))
    assert result["status"] == BUCKET_TARGET_REACHED_COLLECT_PROFIT
    assert "over_target_return_collect_before_redeploy" in result["warnings"]


def test_redistribution_plan_uses_only_eligible_pairs():
    pairs = pair_candidates()
    pairs[1]["eligible_for_allocation"] = False
    pairs[1]["blocked_reason"] = "setup_invalid"
    result = evaluate(pair_candidates=pairs)
    selected = result["redistribution_plan"]["candidate_pairs_for_next_cycle"]
    assert all(pair["eligible_for_allocation"] for pair in selected)


def test_redistribution_respects_max_pairs_per_cycle():
    result = evaluate(cycle_policy=cycle_policy(max_pairs_per_cycle=1))
    assert len(result["redistribution_plan"]["candidate_pairs_for_next_cycle"]) == 1


def test_poor_quality_pairs_are_excluded():
    pairs = pair_candidates()
    pairs[0]["quality_score"] = 20.0
    result = evaluate(pair_candidates=pairs)
    assert any(pair["excluded_reason"] == "quality_below_minimum" for pair in result["allocation_plan"]["excluded_pairs"])


def test_spread_blocked_pairs_are_excluded():
    pairs = pair_candidates()
    pairs[0]["spread_ok"] = False
    result = evaluate(pair_candidates=pairs)
    assert any(pair["excluded_reason"] == "spread_blocked" for pair in result["allocation_plan"]["excluded_pairs"])


def test_margin_unaffordable_pairs_are_excluded():
    pairs = pair_candidates()
    pairs[0]["margin_required"] = 999999.0
    result = evaluate(pair_candidates=pairs)
    assert any(pair["excluded_reason"] == "margin_unaffordable" for pair in result["allocation_plan"]["excluded_pairs"])


def test_five_dollar_and_200k_bucket_use_same_percentage_logic():
    small = evaluate(bucket_state=bucket_state(current_return_percent=80.0, current_balance=9.0, starting_balance=5.0))
    large = evaluate(
        bucket_state=bucket_state(current_return_percent=80.0, current_balance=360000.0, starting_balance=200000.0)
    )
    assert small["status"] == large["status"] == BUCKET_ACTIVE_ACCUMULATING
    assert (
        small["progress_gauges"]["return_cycle_gauge"]["progress_percent_to_min_target"]
        == large["progress_gauges"]["return_cycle_gauge"]["progress_percent_to_min_target"]
    )


def test_future_150_target_blocks_unless_explicitly_allowed():
    blocked = evaluate(cycle_policy=cycle_policy(future_target_return_percent=150.0))
    allowed = evaluate(cycle_policy=cycle_policy(future_target_return_percent=150.0, allow_future_150_percent_target=True))
    assert blocked["status"] == BUCKET_BLOCKED_POLICY
    assert allowed["cycle_summary"]["target_return_max_percent"] == 150.0


def test_progress_gauges_include_100_120_cycle_gauge():
    result = evaluate()
    assert result["progress_gauges"]["return_cycle_gauge"]["gauge_id"] == "forex_return_100_120_progress"


def test_progress_gauges_include_100k_goal_gauge():
    result = evaluate()
    assert result["progress_gauges"]["total_goal_gauge"]["gauge_id"] == "account_goal_100k_progress"
    assert result["progress_gauges"]["total_goal_gauge"]["total_goal_amount"] == 100000.0


def test_all_execution_authority_remains_false():
    assert_execution_false(evaluate())


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)
