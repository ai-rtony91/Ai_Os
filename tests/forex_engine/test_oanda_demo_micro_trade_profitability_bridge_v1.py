from __future__ import annotations

import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_micro_trade_profitability_bridge_v1 import (  # noqa: E402
    MICRO_TRADE_BLOCKED_BROKER_READINESS,
    MICRO_TRADE_BLOCKED_MISSING_PLAN,
    MICRO_TRADE_BLOCKED_MONEY_STATE,
    MICRO_TRADE_BLOCKED_OWNER_APPROVAL,
    MICRO_TRADE_BLOCKED_PROFITABILITY_STRUCTURE,
    MICRO_TRADE_BLOCKED_RISK,
    MICRO_TRADE_READY_FOR_OWNER_REVIEW,
    evaluate_oanda_demo_micro_trade_profitability_bridge_v1,
)


def valid_trade_plan(direction="BUY"):
    if direction == "SELL":
        planned_entry = 1.1000
        stop_loss = 1.1050
        take_profit = 1.0900
    else:
        planned_entry = 1.1000
        stop_loss = 1.0950
        take_profit = 1.1100

    return {
        "candidate_id": f"demo-{direction.lower()}-001",
        "strategy_id": "profit-bridge-v1",
        "instrument": "EUR_USD",
        "direction": direction,
        "entry_reason": "Validated setup with defined risk and reward.",
        "planned_entry": planned_entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "position_size_units": 100,
        "risk_amount": 10.0,
        "expected_reward_amount": 20.0,
        "reward_risk_ratio": 2.0,
        "max_spread_allowed": 0.0002,
        "order_type": "MARKET",
        "time_in_force": "FOK",
        "trade_window": "NY_OVERLAP",
        "hold_allowed_overnight": False,
        "overnight_risk_note": "No overnight hold planned.",
        "min_reward_risk_ratio": 1.5,
        "max_position_size_units": 1000,
    }


def valid_broker_readiness():
    return {
        "broker": "OANDA_DEMO",
        "broker_readiness_passed": True,
        "read_only_money_visibility_ready": True,
        "demo_environment": True,
        "live_environment": False,
        "account_id_present_runtime_only": True,
        "credential_present_runtime_only": True,
        "no_credential_persistence": True,
        "no_account_id_persistence": True,
    }


def valid_risk_state():
    return {
        "risk_gate_passed": True,
        "kill_switch_ready": True,
        "daily_stop_ready": True,
        "max_loss_gate_ready": True,
        "stop_loss_required": True,
        "take_profit_required": True,
        "no_averaging_down": True,
        "one_order_only": True,
        "max_daily_loss_remaining": 50.0,
        "max_allowed_trade_loss": 10.0,
        "max_position_size_units": 1000,
    }


def valid_money_state():
    return {
        "balance": "1000.00",
        "nav": "1000.00",
        "margin_available": "900.00",
        "margin_used_percent": 0.0,
        "max_margin_used_percent": 20.0,
        "open_trade_count": 0,
        "pending_order_count": 0,
        "max_open_trade_count_allowed": 0,
        "max_pending_order_count_allowed": 0,
    }


def valid_evidence_state():
    return {
        "evidence_capture_ready": True,
        "pre_trade_snapshot_required": True,
        "post_trade_snapshot_required": True,
        "pnl_capture_required": True,
        "broker_readiness_capture_required": True,
        "risk_capture_required": True,
        "screenshot_or_report_required": True,
        "trade_outcome_schema_ready": True,
    }


def valid_owner_approval():
    return {
        "owner_review_required": True,
        "owner_approved_for_demo_micro_trade_review": True,
        "owner_approved_for_order_placement": False,
    }


def evaluate(**overrides):
    payload = {
        "trade_plan": valid_trade_plan(),
        "broker_readiness": valid_broker_readiness(),
        "risk_state": valid_risk_state(),
        "money_state": valid_money_state(),
        "evidence_state": valid_evidence_state(),
        "owner_approval": valid_owner_approval(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_micro_trade_profitability_bridge_v1(**payload)


def assert_no_execution_authority(result):
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


def test_default_no_input_blocks_missing_plan():
    result = evaluate_oanda_demo_micro_trade_profitability_bridge_v1()
    assert result["status"] == MICRO_TRADE_BLOCKED_MISSING_PLAN
    assert "missing_trade_plan" in result["blockers"]
    assert_no_execution_authority(result)


def test_missing_broker_readiness_blocks():
    result = evaluate(broker_readiness=None)
    assert result["status"] == MICRO_TRADE_BLOCKED_BROKER_READINESS


def test_failed_risk_gate_blocks():
    risk = valid_risk_state()
    risk["risk_gate_passed"] = False
    result = evaluate(risk_state=risk)
    assert result["status"] == MICRO_TRADE_BLOCKED_RISK
    assert "risk_gate_passed_not_ready" in result["blockers"]


def test_missing_money_state_blocks():
    result = evaluate(money_state=None)
    assert result["status"] == MICRO_TRADE_BLOCKED_MONEY_STATE


def test_invalid_buy_stop_take_profit_geometry_blocks():
    plan = valid_trade_plan("BUY")
    plan["stop_loss"] = 1.101
    result = evaluate(trade_plan=plan)
    assert result["status"] == MICRO_TRADE_BLOCKED_PROFITABILITY_STRUCTURE
    assert "buy_stop_take_profit_geometry_invalid" in result["blockers"]


def test_invalid_sell_stop_take_profit_geometry_blocks():
    plan = valid_trade_plan("SELL")
    plan["take_profit"] = 1.101
    result = evaluate(trade_plan=plan)
    assert result["status"] == MICRO_TRADE_BLOCKED_PROFITABILITY_STRUCTURE
    assert "sell_stop_take_profit_geometry_invalid" in result["blockers"]


def test_reward_risk_below_threshold_blocks():
    plan = valid_trade_plan()
    plan["reward_risk_ratio"] = 1.2
    result = evaluate(trade_plan=plan)
    assert "reward_risk_below_threshold" in result["blockers"]


def test_oversized_position_blocks():
    plan = valid_trade_plan()
    plan["position_size_units"] = 1001
    result = evaluate(trade_plan=plan)
    assert "position_size_above_micro_cap" in result["blockers"]


def test_missing_stop_loss_blocks():
    plan = valid_trade_plan()
    plan.pop("stop_loss")
    result = evaluate(trade_plan=plan)
    assert "missing_stop_loss" in result["blockers"]


def test_missing_take_profit_blocks():
    plan = valid_trade_plan()
    plan.pop("take_profit")
    result = evaluate(trade_plan=plan)
    assert "missing_take_profit" in result["blockers"]


def test_overnight_hold_without_risk_controls_blocks():
    plan = valid_trade_plan()
    plan["hold_allowed_overnight"] = True
    plan["overnight_risk_note"] = "Hold only with hard stops and review."
    risk = valid_risk_state()
    risk["kill_switch_ready"] = False
    result = evaluate(trade_plan=plan, risk_state=risk)
    assert "overnight_kill_switch_not_ready" in result["blockers"]


def test_money_state_margin_too_high_blocks():
    money = valid_money_state()
    money["margin_used_percent"] = 21.0
    result = evaluate(money_state=money)
    assert result["status"] == MICRO_TRADE_BLOCKED_MONEY_STATE
    assert "margin_used_percent_above_limit" in result["blockers"]


def test_open_trade_count_above_allowed_blocks():
    money = valid_money_state()
    money["open_trade_count"] = 1
    result = evaluate(money_state=money)
    assert "open_trade_count_above_allowed" in result["blockers"]


def test_pending_order_count_above_allowed_blocks():
    money = valid_money_state()
    money["pending_order_count"] = 1
    result = evaluate(money_state=money)
    assert "pending_order_count_above_allowed" in result["blockers"]


def test_missing_evidence_capture_blocks():
    evidence = valid_evidence_state()
    evidence["evidence_capture_ready"] = False
    result = evaluate(evidence_state=evidence)
    assert result["status"] == MICRO_TRADE_BLOCKED_PROFITABILITY_STRUCTURE
    assert "evidence_capture_ready_not_ready" in result["blockers"]


def test_missing_owner_approval_blocks():
    approval = valid_owner_approval()
    approval["owner_approved_for_demo_micro_trade_review"] = False
    result = evaluate(owner_approval=approval)
    assert result["status"] == MICRO_TRADE_BLOCKED_OWNER_APPROVAL


def test_fully_valid_buy_demo_micro_trade_plan_ready_for_owner_review():
    result = evaluate(trade_plan=valid_trade_plan("BUY"))
    assert result["status"] == MICRO_TRADE_READY_FOR_OWNER_REVIEW


def test_fully_valid_sell_demo_micro_trade_plan_ready_for_owner_review():
    result = evaluate(trade_plan=valid_trade_plan("SELL"))
    assert result["status"] == MICRO_TRADE_READY_FOR_OWNER_REVIEW


def test_ready_state_still_keeps_all_execution_authority_false():
    result = evaluate()
    assert result["status"] == MICRO_TRADE_READY_FOR_OWNER_REVIEW
    assert_no_execution_authority(result)


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)
