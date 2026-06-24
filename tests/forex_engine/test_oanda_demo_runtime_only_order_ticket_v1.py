from __future__ import annotations

import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_runtime_only_order_ticket_v1 import (  # noqa: E402
    ORDER_TICKET_BLOCKED_COMPOUNDING_BUCKET,
    ORDER_TICKET_BLOCKED_MISSING_TRADE_PLAN,
    ORDER_TICKET_BLOCKED_OWNER_EVIDENCE,
    ORDER_TICKET_BLOCKED_PROFITABILITY_BRIDGE,
    ORDER_TICKET_BLOCKED_RISK,
    ORDER_TICKET_BLOCKED_RUNTIME_CONTEXT,
    ORDER_TICKET_READY_FOR_OWNER_RUNTIME_REVIEW,
    evaluate_oanda_demo_runtime_only_order_ticket_v1,
)


EXECUTION_AUTHORITY_FALSE = {
    "execution_allowed": False,
    "demo_order_allowed": False,
    "live_order_allowed": False,
    "broker_write_allowed": False,
    "autonomous_order_allowed": False,
    "scheduler_allowed": False,
    "daemon_allowed": False,
    "webhook_allowed": False,
}


def trade_plan(direction="BUY", **overrides):
    plan = {
        "candidate_id": "demo-ticket-001",
        "strategy_id": "profit-bridge-v1",
        "instrument": "EUR_USD",
        "direction": direction,
        "order_type": "MARKET",
        "time_in_force": "FOK",
        "planned_entry": 1.1,
        "stop_loss": 1.095,
        "take_profit": 1.11,
        "position_size_units": 100,
        "risk_amount": 5.0,
        "expected_reward_amount": 10.0,
        "reward_risk_ratio": 2.0,
        "max_spread_allowed": 0.0002,
        "hold_allowed_overnight": False,
        "overnight_risk_note": "not held overnight",
    }
    if direction == "SELL":
        plan.update({"planned_entry": 1.1, "stop_loss": 1.105, "take_profit": 1.09})
    plan.update(overrides)
    return plan


def profitability_bridge_ready(**overrides):
    result = {
        "status": "MICRO_TRADE_READY_FOR_OWNER_REVIEW",
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    result.update(overrides)
    return result


def owner_evidence_ready(**overrides):
    result = {
        "status": "EVIDENCE_CAPTURE_READY_FOR_RUNTIME_ONLY_DEMO_REVIEW",
        "owner_decision_summary": {
            "owner_approved_runtime_only_demo_review": True,
            "owner_approved_live_trading": False,
            "owner_approved_autonomous_execution": False,
        },
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    result.update(overrides)
    return result


def compounding_bucket_ready(**overrides):
    result = {
        "status": "BUCKET_ACTIVE_ACCUMULATING",
        "cycle_summary": {"force_trades_to_hit_quota": False},
        "allocation_plan": {
            "selected_pairs": [
                {
                    "instrument": "EUR_USD",
                    "eligible_for_allocation": True,
                    "quality_score": 92.0,
                }
            ]
        },
        "risk_summary": {
            "risk_gate_passed": True,
            "kill_switch_ready": True,
            "daily_stop_ready": True,
            "max_loss_gate_ready": True,
            "margin_safe": True,
        },
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    result.update(overrides)
    return result


def runtime_context(**overrides):
    context = {
        "broker": "OANDA_DEMO",
        "demo_environment": True,
        "live_environment": False,
        "runtime_only_credentials_required": True,
        "credential_persistence_allowed": False,
        "account_id_persistence_allowed": False,
        "broker_network_call_performed": False,
        "order_placement_performed": False,
        "owner_runtime_review_required": True,
        "daily_stop_ready": True,
        "max_loss_gate_ready": True,
        "kill_switch_ready": True,
        "max_overnight_risk_amount": 5.0,
    }
    context.update(overrides)
    return context


def evaluate(**overrides):
    payload = {
        "trade_plan": trade_plan(),
        "profitability_bridge_result": profitability_bridge_ready(),
        "owner_approval_evidence_result": owner_evidence_ready(),
        "compounding_bucket_result": compounding_bucket_ready(),
        "runtime_context": runtime_context(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_runtime_only_order_ticket_v1(**payload)


def assert_execution_authority_false(result):
    assert result["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_default_blocks_missing_trade_plan():
    result = evaluate_oanda_demo_runtime_only_order_ticket_v1()
    assert result["status"] == ORDER_TICKET_BLOCKED_MISSING_TRADE_PLAN
    assert "missing_trade_plan" in result["blockers"]
    assert_execution_authority_false(result)


def test_missing_profitability_bridge_blocks():
    result = evaluate(profitability_bridge_result=None)
    assert result["status"] == ORDER_TICKET_BLOCKED_PROFITABILITY_BRIDGE
    assert "missing_profitability_bridge_result" in result["blockers"]


def test_profitability_bridge_not_ready_blocks():
    result = evaluate(profitability_bridge_result=profitability_bridge_ready(status="MICRO_TRADE_BLOCKED_RISK"))
    assert result["status"] == ORDER_TICKET_BLOCKED_PROFITABILITY_BRIDGE
    assert "profitability_bridge_status_not_ready" in result["blockers"]


def test_missing_owner_evidence_blocks():
    result = evaluate(owner_approval_evidence_result=None)
    assert result["status"] == ORDER_TICKET_BLOCKED_OWNER_EVIDENCE
    assert "missing_owner_approval_evidence_result" in result["blockers"]


def test_owner_evidence_approving_live_trading_blocks():
    owner = owner_evidence_ready()
    owner["owner_decision_summary"]["owner_approved_live_trading"] = True
    result = evaluate(owner_approval_evidence_result=owner)
    assert result["status"] == ORDER_TICKET_BLOCKED_OWNER_EVIDENCE
    assert "owner_approved_live_trading_must_remain_false" in result["blockers"]


def test_missing_compounding_bucket_blocks():
    result = evaluate(compounding_bucket_result=None)
    assert result["status"] == ORDER_TICKET_BLOCKED_COMPOUNDING_BUCKET
    assert "missing_compounding_bucket_result" in result["blockers"]


def test_compounding_forced_quota_chasing_blocks():
    compounding = compounding_bucket_ready()
    compounding["cycle_summary"]["force_trades_to_hit_quota"] = True
    result = evaluate(compounding_bucket_result=compounding)
    assert result["status"] == ORDER_TICKET_BLOCKED_COMPOUNDING_BUCKET
    assert "compounding_force_trades_to_hit_quota_must_be_false" in result["blockers"]


def test_missing_runtime_context_blocks():
    result = evaluate(runtime_context=None)
    assert result["status"] == ORDER_TICKET_BLOCKED_RUNTIME_CONTEXT
    assert "missing_runtime_context" in result["blockers"]


def test_runtime_context_live_environment_blocks():
    result = evaluate(runtime_context=runtime_context(live_environment=True))
    assert result["status"] == ORDER_TICKET_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_live_environment_must_be_false" in result["blockers"]


def test_runtime_context_credential_persistence_blocks():
    result = evaluate(runtime_context=runtime_context(credential_persistence_allowed=True))
    assert result["status"] == ORDER_TICKET_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_credential_persistence_allowed_must_be_false" in result["blockers"]


def test_invalid_buy_stop_take_profit_geometry_blocks():
    result = evaluate(trade_plan=trade_plan(stop_loss=1.105, take_profit=1.11))
    assert result["status"] == ORDER_TICKET_BLOCKED_RISK
    assert "buy_geometry_requires_stop_loss_below_entry_below_take_profit" in result["blockers"]


def test_invalid_sell_stop_take_profit_geometry_blocks():
    result = evaluate(trade_plan=trade_plan("SELL", stop_loss=1.095, take_profit=1.09))
    assert result["status"] == ORDER_TICKET_BLOCKED_RISK
    assert "sell_geometry_requires_take_profit_below_entry_below_stop_loss" in result["blockers"]


def test_reward_risk_below_threshold_blocks():
    result = evaluate(trade_plan=trade_plan(reward_risk_ratio=1.2))
    assert result["status"] == ORDER_TICKET_BLOCKED_RISK
    assert "reward_risk_ratio_below_minimum" in result["blockers"]


def test_overnight_hold_without_controls_blocks():
    result = evaluate(
        trade_plan=trade_plan(hold_allowed_overnight=True, overnight_risk_note="session carry risk acknowledged"),
        runtime_context=runtime_context(kill_switch_ready=False),
    )
    assert result["status"] == ORDER_TICKET_BLOCKED_RISK
    assert "overnight_kill_switch_ready_required" in result["blockers"]


def test_valid_buy_ticket_returns_owner_runtime_review():
    result = evaluate()
    assert result["status"] == ORDER_TICKET_READY_FOR_OWNER_RUNTIME_REVIEW
    assert result["order_ticket"]["direction"] == "BUY"


def test_valid_sell_ticket_returns_owner_runtime_review():
    result = evaluate(trade_plan=trade_plan("SELL"))
    assert result["status"] == ORDER_TICKET_READY_FOR_OWNER_RUNTIME_REVIEW
    assert result["order_ticket"]["direction"] == "SELL"


def test_order_ticket_status_is_review_only_not_executable():
    result = evaluate()
    assert result["order_ticket"]["status"] == "REVIEW_ONLY_NOT_EXECUTABLE"
    assert result["order_ticket"]["live_trading_allowed"] is False
    assert result["order_ticket"]["autonomous_order_allowed"] is False


def test_all_execution_authority_remains_false():
    result = evaluate()
    assert_execution_authority_false(result)


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)
