from __future__ import annotations

import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_runtime_executor_one_order_only_v1 import (  # noqa: E402
    ONE_ORDER_BLOCKED_FINAL_GATE_NOT_READY,
    ONE_ORDER_BLOCKED_MISSING_FINAL_GATE,
    ONE_ORDER_BLOCKED_OWNER_CONFIRMATION,
    ONE_ORDER_BLOCKED_RUNTIME_CONTEXT,
    ONE_ORDER_CONTRACT_READY_STATUS,
    ONE_ORDER_READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET,
    evaluate_oanda_demo_runtime_executor_one_order_only_v1,
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


def final_gated_ready(**overrides):
    result = {
        "status": "FINAL_GATED_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTOR_PACKET",
        "prepared_runtime_package": {
            "package_status": "READY_FOR_SEPARATE_RUNTIME_EXECUTOR_PACKET",
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


def runtime_context(**overrides):
    context = {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_environment": True,
        "live_environment": False,
        "runtime_only_credentials_present": True,
        "credential_persistence_detected": False,
        "account_id_persistence_detected": False,
        "one_order_only": True,
        "existing_open_orders": 0,
        "existing_pending_orders": 0,
        "order_already_attempted": False,
        "broker_network_call_performed": False,
        "order_placement_performed": False,
        "kill_switch_ready": True,
        "daily_stop_ready": True,
        "max_loss_gate_ready": True,
        "hard_stop_loss_ready": True,
        "hard_take_profit_ready": True,
        "pre_trade_evidence_ready": True,
        "post_trade_evidence_plan_ready": True,
    }
    context.update(overrides)
    return context


def owner_confirmation(**overrides):
    confirmation = {
        "owner_confirmed_demo_only": True,
        "owner_confirmed_one_order_only": True,
        "owner_confirmed_no_live_money": True,
        "owner_confirmed_stop_loss": True,
        "owner_confirmed_take_profit": True,
        "owner_confirmed_loss_possible": True,
        "owner_confirmed_no_profit_guarantee": True,
        "owner_confirmed_runtime_credentials_outside_repo": True,
        "owner_confirmed_no_autonomous_execution": True,
        "owner_confirmed_separate_broker_execution_packet_required": True,
    }
    confirmation.update(overrides)
    return confirmation


def evaluate(**overrides):
    payload = {
        "final_gated_result": final_gated_ready(),
        "runtime_one_order_context": runtime_context(),
        "owner_runtime_confirmation": owner_confirmation(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_runtime_executor_one_order_only_v1(**payload)


def assert_execution_authority_false(result):
    assert result["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_default_blocks_missing_final_gate():
    result = evaluate_oanda_demo_runtime_executor_one_order_only_v1()
    assert result["status"] == ONE_ORDER_BLOCKED_MISSING_FINAL_GATE
    assert "missing_final_gated_result" in result["blockers"]
    assert_execution_authority_false(result)


def test_final_gate_not_ready_blocks():
    result = evaluate(
        final_gated_result=final_gated_ready(status="FINAL_GATED_BLOCKED_RUNTIME_CONTEXT")
    )
    assert result["status"] == ONE_ORDER_BLOCKED_FINAL_GATE_NOT_READY
    assert "final_gated_status_not_ready" in result["blockers"]


def test_missing_runtime_context_blocks():
    result = evaluate(runtime_one_order_context=None)
    assert result["status"] == ONE_ORDER_BLOCKED_RUNTIME_CONTEXT
    assert "missing_runtime_one_order_context" in result["blockers"]


def test_runtime_context_live_environment_blocks():
    result = evaluate(runtime_one_order_context=runtime_context(live_environment=True))
    assert result["status"] == ONE_ORDER_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_live_environment_must_be_false" in result["blockers"]


def test_runtime_context_missing_runtime_credentials_blocks():
    result = evaluate(
        runtime_one_order_context=runtime_context(runtime_only_credentials_present=False)
    )
    assert result["status"] == ONE_ORDER_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_runtime_only_credentials_present_required" in result["blockers"]


def test_runtime_context_credential_persistence_blocks():
    result = evaluate(
        runtime_one_order_context=runtime_context(credential_persistence_detected=True)
    )
    assert result["status"] == ONE_ORDER_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_credential_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_runtime_context_account_id_persistence_blocks():
    result = evaluate(
        runtime_one_order_context=runtime_context(account_id_persistence_detected=True)
    )
    assert result["status"] == ONE_ORDER_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_account_id_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_existing_open_orders_block():
    result = evaluate(runtime_one_order_context=runtime_context(existing_open_orders=1))
    assert result["status"] == ONE_ORDER_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_existing_open_orders_must_be_zero" in result["blockers"]


def test_existing_pending_orders_block():
    result = evaluate(runtime_one_order_context=runtime_context(existing_pending_orders=1))
    assert result["status"] == ONE_ORDER_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_existing_pending_orders_must_be_zero" in result["blockers"]


def test_order_already_attempted_blocks():
    result = evaluate(runtime_one_order_context=runtime_context(order_already_attempted=True))
    assert result["status"] == ONE_ORDER_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_order_already_attempted_must_be_false" in result["blockers"]


def test_missing_owner_confirmation_blocks():
    result = evaluate(owner_runtime_confirmation=None)
    assert result["status"] == ONE_ORDER_BLOCKED_OWNER_CONFIRMATION
    assert "missing_owner_runtime_confirmation" in result["blockers"]


def test_owner_failing_demo_only_confirmation_blocks():
    result = evaluate(
        owner_runtime_confirmation=owner_confirmation(owner_confirmed_demo_only=False)
    )
    assert result["status"] == ONE_ORDER_BLOCKED_OWNER_CONFIRMATION
    assert "owner_confirmed_demo_only_required" in result["blockers"]


def test_owner_failing_one_order_only_confirmation_blocks():
    result = evaluate(
        owner_runtime_confirmation=owner_confirmation(owner_confirmed_one_order_only=False)
    )
    assert result["status"] == ONE_ORDER_BLOCKED_OWNER_CONFIRMATION
    assert "owner_confirmed_one_order_only_required" in result["blockers"]


def test_owner_failing_no_live_money_confirmation_blocks():
    result = evaluate(
        owner_runtime_confirmation=owner_confirmation(owner_confirmed_no_live_money=False)
    )
    assert result["status"] == ONE_ORDER_BLOCKED_OWNER_CONFIRMATION
    assert "owner_confirmed_no_live_money_required" in result["blockers"]


def test_valid_one_order_contract_returns_ready():
    result = evaluate()
    assert result["status"] == ONE_ORDER_READY_FOR_SEPARATE_BROKER_EXECUTION_PACKET


def test_one_order_contract_max_order_attempts_is_one():
    result = evaluate()
    assert result["one_order_contract"]["contract_status"] == ONE_ORDER_CONTRACT_READY_STATUS
    assert result["one_order_contract"]["max_order_attempts"] == 1


def test_execution_rehearsal_stops_before_broker_call():
    result = evaluate()
    assert result["execution_rehearsal"]["steps"][-1] == "stop before broker call"


def test_all_execution_authority_remains_false():
    result = evaluate()
    assert_execution_authority_false(result)


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)
