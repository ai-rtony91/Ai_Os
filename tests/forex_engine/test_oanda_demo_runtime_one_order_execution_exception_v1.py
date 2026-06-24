from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_runtime_one_order_execution_exception_v1 import (  # noqa: E402
    EXCEPTION_BLOCKED_BROKER_PACKET_NOT_READY,
    EXCEPTION_BLOCKED_MISSING_BROKER_PACKET,
    EXCEPTION_BLOCKED_OWNER_APPROVAL,
    EXCEPTION_BLOCKED_RUNTIME_CONTEXT,
    EXCEPTION_READY_FOR_MANUAL_RUNTIME_DEMO_ORDER_ATTEMPT,
    evaluate_oanda_demo_runtime_one_order_execution_exception_v1,
)
from scripts.forex_delivery.run_oanda_demo_runtime_one_order_execution_exception_v1 import (  # noqa: E402
    main as script_main,
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


def broker_packet_ready(**overrides):
    result = {
        "status": "BROKER_PACKET_READY_FOR_SEPARATE_RUNTIME_ONLY_DEMO_ORDER_ATTEMPT",
        "broker_execution_packet": {
            "packet_status": "READY_FOR_EXTERNAL_RUNTIME_ONLY_ORDER_ATTEMPT",
            "broker": "OANDA_DEMO",
            "environment": "DEMO",
            "order_attempt_limit": 1,
            "one_order_only": True,
            "live_trading_allowed": False,
            "autonomous_execution_allowed": False,
            "hard_stop_loss_required": True,
            "hard_take_profit_required": True,
            "pre_trade_evidence_required": True,
            "post_trade_evidence_required": True,
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
        "account_id_runtime_only": True,
        "token_runtime_only": True,
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
        "manual_runtime_invocation_required": True,
    }
    context.update(overrides)
    return context


def owner_approval(**overrides):
    approval = {
        "owner_approved_manual_runtime_demo_order_attempt": True,
        "owner_confirmed_demo_only": True,
        "owner_confirmed_no_live_money": True,
        "owner_confirmed_one_order_only": True,
        "owner_confirmed_max_one_attempt": True,
        "owner_confirmed_stop_loss": True,
        "owner_confirmed_take_profit": True,
        "owner_confirmed_loss_possible": True,
        "owner_confirmed_no_profit_guarantee": True,
        "owner_confirmed_runtime_credentials_outside_repo": True,
        "owner_confirmed_manual_invocation_required": True,
        "owner_confirmed_no_autonomous_execution": True,
    }
    approval.update(overrides)
    return approval


def evaluate(**overrides):
    payload = {
        "broker_execution_packet_result": broker_packet_ready(),
        "runtime_exception_context": runtime_context(),
        "owner_runtime_exception_approval": owner_approval(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_runtime_one_order_execution_exception_v1(**payload)


def run_script(args):
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def assert_execution_authority_false(result):
    assert result["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_default_blocks_missing_broker_packet():
    result = evaluate_oanda_demo_runtime_one_order_execution_exception_v1()
    assert result["status"] == EXCEPTION_BLOCKED_MISSING_BROKER_PACKET
    assert "missing_broker_execution_packet_result" in result["blockers"]
    assert result["allowed_manual_runtime_invocation"] is False
    assert_execution_authority_false(result)


def test_broker_packet_not_ready_blocks():
    result = evaluate(
        broker_execution_packet_result=broker_packet_ready(
            status="BROKER_PACKET_BLOCKED_OWNER_APPROVAL"
        )
    )
    assert result["status"] == EXCEPTION_BLOCKED_BROKER_PACKET_NOT_READY
    assert "broker_execution_packet_status_not_ready" in result["blockers"]


def test_missing_runtime_context_blocks():
    result = evaluate(runtime_exception_context=None)
    assert result["status"] == EXCEPTION_BLOCKED_RUNTIME_CONTEXT
    assert "missing_runtime_exception_context" in result["blockers"]


def test_runtime_context_live_environment_blocks():
    result = evaluate(runtime_exception_context=runtime_context(live_environment=True))
    assert result["status"] == EXCEPTION_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_live_environment_must_be_false" in result["blockers"]


def test_runtime_context_missing_runtime_credentials_blocks():
    result = evaluate(
        runtime_exception_context=runtime_context(runtime_only_credentials_present=False)
    )
    assert result["status"] == EXCEPTION_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_runtime_only_credentials_present_required" in result["blockers"]


def test_runtime_context_credential_persistence_blocks():
    result = evaluate(
        runtime_exception_context=runtime_context(credential_persistence_detected=True)
    )
    assert result["status"] == EXCEPTION_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_credential_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_runtime_context_account_id_persistence_blocks():
    result = evaluate(
        runtime_exception_context=runtime_context(account_id_persistence_detected=True)
    )
    assert result["status"] == EXCEPTION_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_account_id_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_existing_open_orders_block():
    result = evaluate(runtime_exception_context=runtime_context(existing_open_orders=1))
    assert result["status"] == EXCEPTION_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_existing_open_orders_must_be_zero" in result["blockers"]


def test_existing_pending_orders_block():
    result = evaluate(runtime_exception_context=runtime_context(existing_pending_orders=1))
    assert result["status"] == EXCEPTION_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_existing_pending_orders_must_be_zero" in result["blockers"]


def test_order_already_attempted_blocks():
    result = evaluate(runtime_exception_context=runtime_context(order_already_attempted=True))
    assert result["status"] == EXCEPTION_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_order_already_attempted_must_be_false" in result["blockers"]


def test_missing_owner_approval_blocks():
    result = evaluate(owner_runtime_exception_approval=None)
    assert result["status"] == EXCEPTION_BLOCKED_OWNER_APPROVAL
    assert "missing_owner_runtime_exception_approval" in result["blockers"]


def test_owner_failing_demo_only_confirmation_blocks():
    result = evaluate(
        owner_runtime_exception_approval=owner_approval(owner_confirmed_demo_only=False)
    )
    assert result["status"] == EXCEPTION_BLOCKED_OWNER_APPROVAL
    assert "owner_confirmed_demo_only_required" in result["blockers"]


def test_owner_failing_one_order_only_confirmation_blocks():
    result = evaluate(
        owner_runtime_exception_approval=owner_approval(owner_confirmed_one_order_only=False)
    )
    assert result["status"] == EXCEPTION_BLOCKED_OWNER_APPROVAL
    assert "owner_confirmed_one_order_only_required" in result["blockers"]


def test_owner_failing_loss_acknowledgement_blocks():
    result = evaluate(
        owner_runtime_exception_approval=owner_approval(owner_confirmed_loss_possible=False)
    )
    assert result["status"] == EXCEPTION_BLOCKED_OWNER_APPROVAL
    assert "owner_confirmed_loss_possible_required" in result["blockers"]


def test_valid_exception_returns_ready_for_manual_runtime_attempt():
    result = evaluate()
    assert result["status"] == EXCEPTION_READY_FOR_MANUAL_RUNTIME_DEMO_ORDER_ATTEMPT


def test_allowed_manual_runtime_invocation_true_only_when_all_gates_pass():
    assert evaluate()["allowed_manual_runtime_invocation"] is True
    blocked = evaluate(runtime_exception_context=runtime_context(live_environment=True))
    assert blocked["allowed_manual_runtime_invocation"] is False


def test_all_execution_authority_fields_remain_false():
    result = evaluate()
    assert_execution_authority_false(result)


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)


def test_script_dry_run_prints_json_and_does_not_place_order():
    code, payload = run_script([])
    assert code == 0
    assert payload["script_status"] == "DRY_RUN_DECISION_ONLY"
    assert payload["order_placement_performed"] is False
    assert payload["broker_network_call_performed"] is False


def test_script_execute_flag_without_required_confirmations_blocks():
    code, payload = run_script(["--execute-demo-order"])
    assert code == 1
    assert payload["script_status"] == "BLOCKED_MISSING_REQUIRED_CONFIRMATIONS"
    assert "--i-understand-demo-only" in payload["missing_confirmations"]
    assert payload["order_placement_performed"] is False


def test_script_execute_flag_with_confirmations_returns_pending_adapter_block():
    args = [
        "--execute-demo-order",
        "--i-understand-demo-only",
        "--i-understand-one-order-only",
        "--i-understand-loss-possible",
        "--i-understand-no-profit-guarantee",
        "--i-confirm-stop-loss",
        "--i-confirm-take-profit",
    ]
    code, payload = run_script(args)
    assert code == 1
    assert payload["script_status"] == "BLOCKED_PENDING_BROKER_ADAPTER_IMPLEMENTATION"
    assert payload["order_placement_performed"] is False
    assert payload["broker_network_call_performed"] is False
