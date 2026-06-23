from __future__ import annotations

import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_micro_trade_owner_approval_evidence_capture_v1 import (  # noqa: E402
    EVIDENCE_CAPTURE_AWAITING_POST_TRADE_RESULT,
    EVIDENCE_CAPTURE_BLOCKED_BRIDGE_NOT_READY,
    EVIDENCE_CAPTURE_BLOCKED_MISSING_BRIDGE_RESULT,
    EVIDENCE_CAPTURE_BLOCKED_OWNER_DECISION,
    EVIDENCE_CAPTURE_COMPLETE_BREAKEVEN,
    EVIDENCE_CAPTURE_COMPLETE_LOSS,
    EVIDENCE_CAPTURE_COMPLETE_PROFIT,
    EVIDENCE_CAPTURE_READY_FOR_RUNTIME_ONLY_DEMO_REVIEW,
    EVIDENCE_CAPTURE_REJECTED,
    evaluate_oanda_demo_micro_trade_owner_approval_evidence_capture_v1,
)


def bridge_ready_result():
    return {
        "status": "MICRO_TRADE_READY_FOR_OWNER_REVIEW",
        "trade_plan_summary": {
            "candidate_id": "demo-buy-001",
            "instrument": "EUR_USD",
            "direction": "BUY",
            "planned_entry": 1.1,
            "stop_loss": 1.095,
            "take_profit": 1.11,
            "position_size_units": 100,
            "risk_amount": 10.0,
            "reward_risk_ratio": 2.0,
        },
        "broker_readiness_summary": {"broker": "OANDA_DEMO", "demo_environment": True},
        "risk_summary": {"kill_switch_ready": True, "daily_stop_ready": True, "max_loss_gate_ready": True},
        "money_state_summary": {"balance_present": True, "nav_present": True},
        "evidence_requirements": {"evidence_capture_ready": True},
        "execution_authority": {
            "execution_allowed": False,
            "demo_order_allowed": False,
            "live_order_allowed": False,
            "broker_write_allowed": False,
            "autonomous_order_allowed": False,
            "scheduler_allowed": False,
            "daemon_allowed": False,
            "webhook_allowed": False,
        },
    }


def owner_decision():
    return {
        "owner_review_required": True,
        "owner_approved_runtime_only_demo_review": True,
        "owner_approved_live_trading": False,
        "owner_approved_autonomous_execution": False,
        "owner_acknowledged_loss_risk": True,
        "owner_acknowledged_no_profit_guarantee": True,
        "owner_acknowledged_stop_loss_required": True,
        "owner_acknowledged_take_profit_required": True,
    }


def pre_trade_evidence():
    return {
        "candidate_id": "demo-buy-001",
        "instrument": "EUR_USD",
        "direction": "BUY",
        "planned_entry": 1.1,
        "stop_loss": 1.095,
        "take_profit": 1.11,
        "position_size_units": 100,
        "risk_amount": 10.0,
        "reward_risk_ratio": 2.0,
        "spread_snapshot": 0.0001,
        "balance_snapshot": 1000.0,
        "nav_snapshot": 1000.0,
        "margin_available_snapshot": 900.0,
        "kill_switch_state": "READY",
        "daily_stop_state": "READY",
        "max_loss_gate_state": "READY",
        "timestamp_utc": "2026-06-23T23:40:00Z",
        "evidence_source": "sanitized_runtime_input",
    }


def post_trade_evidence(realized_pl=1.25):
    return {
        "realized_pl": realized_pl,
        "exit_price": 1.111,
        "close_reason": "take_profit",
        "trade_duration_minutes": 17,
        "post_balance": 1001.25,
        "post_nav": 1001.25,
        "timestamp_utc": "2026-06-23T23:57:00Z",
        "evidence_source": "sanitized_runtime_input",
    }


def evaluate(**overrides):
    payload = {
        "bridge_result": bridge_ready_result(),
        "owner_decision": owner_decision(),
        "pre_trade_evidence": pre_trade_evidence(),
        "post_trade_evidence": None,
    }
    payload.update(overrides)
    return evaluate_oanda_demo_micro_trade_owner_approval_evidence_capture_v1(**payload)


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


def test_default_blocks_missing_bridge_result():
    result = evaluate_oanda_demo_micro_trade_owner_approval_evidence_capture_v1()
    assert result["status"] == EVIDENCE_CAPTURE_BLOCKED_MISSING_BRIDGE_RESULT
    assert "missing_bridge_result" in result["blockers"]
    assert_no_execution_authority(result)


def test_bridge_not_ready_blocks():
    bridge = bridge_ready_result()
    bridge["status"] = "MICRO_TRADE_BLOCKED_OWNER_APPROVAL"
    result = evaluate(bridge_result=bridge)
    assert result["status"] == EVIDENCE_CAPTURE_BLOCKED_BRIDGE_NOT_READY


def test_bridge_ready_but_owner_decision_missing_blocks():
    result = evaluate(owner_decision=None)
    assert result["status"] == EVIDENCE_CAPTURE_BLOCKED_OWNER_DECISION
    assert "missing_owner_decision" in result["blockers"]


def test_owner_approval_missing_blocks():
    owner = owner_decision()
    owner["owner_approved_runtime_only_demo_review"] = False
    result = evaluate(owner_decision=owner)
    assert result["status"] == EVIDENCE_CAPTURE_BLOCKED_OWNER_DECISION


def test_owner_approving_live_trading_blocks():
    owner = owner_decision()
    owner["owner_approved_live_trading"] = True
    result = evaluate(owner_decision=owner)
    assert result["status"] == EVIDENCE_CAPTURE_BLOCKED_OWNER_DECISION
    assert "owner_approved_live_trading_must_remain_false" in result["blockers"]


def test_owner_approving_autonomous_execution_blocks():
    owner = owner_decision()
    owner["owner_approved_autonomous_execution"] = True
    result = evaluate(owner_decision=owner)
    assert result["status"] == EVIDENCE_CAPTURE_BLOCKED_OWNER_DECISION
    assert "owner_approved_autonomous_execution_must_remain_false" in result["blockers"]


def test_missing_loss_risk_acknowledgement_blocks():
    owner = owner_decision()
    owner["owner_acknowledged_loss_risk"] = False
    result = evaluate(owner_decision=owner)
    assert result["status"] == EVIDENCE_CAPTURE_BLOCKED_OWNER_DECISION


def test_missing_pre_trade_evidence_blocks():
    result = evaluate(pre_trade_evidence=None)
    assert result["status"] == EVIDENCE_CAPTURE_BLOCKED_OWNER_DECISION
    assert "missing_pre_trade_evidence" in result["blockers"]


def test_complete_bridge_owner_and_pre_trade_evidence_ready_for_runtime_only_demo_review():
    result = evaluate()
    assert result["status"] == EVIDENCE_CAPTURE_READY_FOR_RUNTIME_ONLY_DEMO_REVIEW


def test_all_execution_authority_remains_false_when_ready():
    result = evaluate()
    assert_no_execution_authority(result)


def test_post_trade_profit_classifies_complete_profit():
    result = evaluate(post_trade_evidence=post_trade_evidence(2.25))
    assert result["status"] == EVIDENCE_CAPTURE_COMPLETE_PROFIT


def test_post_trade_loss_classifies_complete_loss():
    result = evaluate(post_trade_evidence=post_trade_evidence(-1.5))
    assert result["status"] == EVIDENCE_CAPTURE_COMPLETE_LOSS


def test_post_trade_breakeven_classifies_complete_breakeven():
    result = evaluate(post_trade_evidence=post_trade_evidence(0))
    assert result["status"] == EVIDENCE_CAPTURE_COMPLETE_BREAKEVEN


def test_missing_post_trade_required_field_warns_deterministically():
    post_trade = post_trade_evidence()
    post_trade.pop("exit_price")
    result = evaluate(post_trade_evidence=post_trade)
    assert result["status"] == EVIDENCE_CAPTURE_AWAITING_POST_TRADE_RESULT
    assert "missing_post_trade_exit_price" in result["blockers"]


def test_unsafe_execution_authority_is_rejected():
    bridge = bridge_ready_result()
    bridge["execution_allowed"] = True
    result = evaluate(bridge_result=bridge)
    assert result["status"] == EVIDENCE_CAPTURE_REJECTED
    assert "unsafe_execution_allowed_true" in result["blockers"]


def test_output_is_json_serializable():
    json.dumps(evaluate(post_trade_evidence=post_trade_evidence()), sort_keys=True)
