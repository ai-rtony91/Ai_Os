from __future__ import annotations

import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_broker_execution_packet_one_order_v1 import (  # noqa: E402
    BROKER_PACKET_BLOCKED_BROKER_CONTEXT,
    BROKER_PACKET_BLOCKED_MISSING_ONE_ORDER_CONTRACT,
    BROKER_PACKET_BLOCKED_ONE_ORDER_CONTRACT_NOT_READY,
    BROKER_PACKET_BLOCKED_OWNER_APPROVAL,
    BROKER_PACKET_READY_FOR_SEPARATE_RUNTIME_ONLY_DEMO_ORDER_ATTEMPT,
    BROKER_PACKET_READY_STATUS,
    evaluate_oanda_demo_broker_execution_packet_one_order_v1,
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


def one_order_ready(**overrides):
    result = {
        "status": "ONE_ORDER_READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET",
        "one_order_contract": {
            "contract_status": "READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET",
            "broker": "OANDA_DEMO",
            "environment": "DEMO",
            "instrument": "EUR_USD",
            "direction": "BUY",
            "order_type": "MARKET",
            "time_in_force": "FOK",
            "planned_entry": 1.1,
            "stop_loss": 1.095,
            "take_profit": 1.11,
            "position_size_units": 100,
            "risk_amount": 5.0,
            "reward_risk_ratio": 2.0,
            "hold_allowed_overnight": False,
        },
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    result.update(overrides)
    return result


def broker_context(**overrides):
    context = {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_environment": True,
        "live_environment": False,
        "runtime_only_credentials_present": True,
        "credential_persistence_detected": False,
        "account_id_persistence_detected": False,
        "one_order_only": True,
        "max_order_attempts": 1,
        "existing_open_orders": 0,
        "existing_pending_orders": 0,
        "order_already_attempted": False,
        "kill_switch_ready": True,
        "daily_stop_ready": True,
        "max_loss_gate_ready": True,
        "hard_stop_loss_ready": True,
        "hard_take_profit_ready": True,
        "pre_trade_evidence_ready": True,
        "post_trade_evidence_plan_ready": True,
        "broker_network_call_performed": False,
        "order_placement_performed": False,
    }
    context.update(overrides)
    return context


def owner_approval(**overrides):
    approval = {
        "owner_approved_separate_runtime_demo_order_attempt": True,
        "owner_confirmed_demo_only": True,
        "owner_confirmed_no_live_money": True,
        "owner_confirmed_one_order_only": True,
        "owner_confirmed_max_one_attempt": True,
        "owner_confirmed_stop_loss": True,
        "owner_confirmed_take_profit": True,
        "owner_confirmed_loss_possible": True,
        "owner_confirmed_no_profit_guarantee": True,
        "owner_confirmed_runtime_credentials_outside_repo": True,
        "owner_confirmed_no_autonomous_execution": True,
    }
    approval.update(overrides)
    return approval


def evaluate(**overrides):
    payload = {
        "one_order_contract_result": one_order_ready(),
        "broker_execution_context": broker_context(),
        "owner_broker_execution_approval": owner_approval(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_broker_execution_packet_one_order_v1(**payload)


def assert_execution_authority_false(result):
    assert result["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_default_blocks_missing_one_order_contract():
    result = evaluate_oanda_demo_broker_execution_packet_one_order_v1()
    assert result["status"] == BROKER_PACKET_BLOCKED_MISSING_ONE_ORDER_CONTRACT
    assert "missing_one_order_contract_result" in result["blockers"]
    assert_execution_authority_false(result)


def test_one_order_contract_not_ready_blocks():
    result = evaluate(
        one_order_contract_result=one_order_ready(
            status="ONE_ORDER_BLOCKED_RUNTIME_CONTEXT"
        )
    )
    assert result["status"] == BROKER_PACKET_BLOCKED_ONE_ORDER_CONTRACT_NOT_READY
    assert "one_order_contract_status_not_ready" in result["blockers"]


def test_missing_broker_context_blocks():
    result = evaluate(broker_execution_context=None)
    assert result["status"] == BROKER_PACKET_BLOCKED_BROKER_CONTEXT
    assert "missing_broker_execution_context" in result["blockers"]


def test_broker_context_live_environment_blocks():
    result = evaluate(broker_execution_context=broker_context(live_environment=True))
    assert result["status"] == BROKER_PACKET_BLOCKED_BROKER_CONTEXT
    assert "broker_context_live_environment_must_be_false" in result["blockers"]


def test_broker_context_missing_runtime_credentials_blocks():
    result = evaluate(
        broker_execution_context=broker_context(runtime_only_credentials_present=False)
    )
    assert result["status"] == BROKER_PACKET_BLOCKED_BROKER_CONTEXT
    assert "broker_context_runtime_only_credentials_present_required" in result["blockers"]


def test_broker_context_credential_persistence_blocks():
    result = evaluate(
        broker_execution_context=broker_context(credential_persistence_detected=True)
    )
    assert result["status"] == BROKER_PACKET_BLOCKED_BROKER_CONTEXT
    assert "broker_context_credential_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_broker_context_account_id_persistence_blocks():
    result = evaluate(
        broker_execution_context=broker_context(account_id_persistence_detected=True)
    )
    assert result["status"] == BROKER_PACKET_BLOCKED_BROKER_CONTEXT
    assert "broker_context_account_id_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_existing_open_orders_block():
    result = evaluate(broker_execution_context=broker_context(existing_open_orders=1))
    assert result["status"] == BROKER_PACKET_BLOCKED_BROKER_CONTEXT
    assert "broker_context_existing_open_orders_must_be_zero" in result["blockers"]


def test_existing_pending_orders_block():
    result = evaluate(broker_execution_context=broker_context(existing_pending_orders=1))
    assert result["status"] == BROKER_PACKET_BLOCKED_BROKER_CONTEXT
    assert "broker_context_existing_pending_orders_must_be_zero" in result["blockers"]


def test_order_already_attempted_blocks():
    result = evaluate(broker_execution_context=broker_context(order_already_attempted=True))
    assert result["status"] == BROKER_PACKET_BLOCKED_BROKER_CONTEXT
    assert "broker_context_order_already_attempted_must_be_false" in result["blockers"]


def test_missing_owner_approval_blocks():
    result = evaluate(owner_broker_execution_approval=None)
    assert result["status"] == BROKER_PACKET_BLOCKED_OWNER_APPROVAL
    assert "missing_owner_broker_execution_approval" in result["blockers"]


def test_owner_failing_demo_only_confirmation_blocks():
    result = evaluate(
        owner_broker_execution_approval=owner_approval(owner_confirmed_demo_only=False)
    )
    assert result["status"] == BROKER_PACKET_BLOCKED_OWNER_APPROVAL
    assert "owner_confirmed_demo_only_required" in result["blockers"]


def test_owner_failing_one_order_only_confirmation_blocks():
    result = evaluate(
        owner_broker_execution_approval=owner_approval(owner_confirmed_one_order_only=False)
    )
    assert result["status"] == BROKER_PACKET_BLOCKED_OWNER_APPROVAL
    assert "owner_confirmed_one_order_only_required" in result["blockers"]


def test_owner_failing_no_live_money_confirmation_blocks():
    result = evaluate(
        owner_broker_execution_approval=owner_approval(owner_confirmed_no_live_money=False)
    )
    assert result["status"] == BROKER_PACKET_BLOCKED_OWNER_APPROVAL
    assert "owner_confirmed_no_live_money_required" in result["blockers"]


def test_valid_packet_returns_ready_for_separate_runtime_demo_attempt():
    result = evaluate()
    assert result["status"] == BROKER_PACKET_READY_FOR_SEPARATE_RUNTIME_ONLY_DEMO_ORDER_ATTEMPT


def test_broker_execution_packet_order_attempt_limit_is_one():
    result = evaluate()
    assert result["broker_execution_packet"]["packet_status"] == BROKER_PACKET_READY_STATUS
    assert result["broker_execution_packet"]["order_attempt_limit"] == 1


def test_pre_trade_evidence_requirements_include_stop_loss_and_take_profit():
    result = evaluate()
    assert "stop_loss" in result["pre_trade_evidence_requirements"]
    assert "take_profit" in result["pre_trade_evidence_requirements"]


def test_post_trade_evidence_requirements_include_realized_pl_when_closed():
    result = evaluate()
    assert "realized_pl_when_closed" in result["post_trade_evidence_requirements"]


def test_all_execution_authority_remains_false():
    result = evaluate()
    assert_execution_authority_false(result)


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)
