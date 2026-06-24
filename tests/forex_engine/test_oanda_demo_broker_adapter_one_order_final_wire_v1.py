from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_broker_adapter_one_order_final_wire_v1 import (  # noqa: E402
    FINAL_WIRE_BLOCKED_ADAPTER_CONTEXT,
    FINAL_WIRE_BLOCKED_MISSING_RUNTIME_EXCEPTION,
    FINAL_WIRE_BLOCKED_ORDER_PAYLOAD,
    FINAL_WIRE_BLOCKED_OWNER_APPROVAL,
    FINAL_WIRE_BLOCKED_RUNTIME_EXCEPTION_NOT_READY,
    FINAL_WIRE_READY_FOR_MANUAL_ONE_ORDER_DEMO_RUNTIME_ATTEMPT,
    evaluate_oanda_demo_broker_adapter_one_order_final_wire_v1,
)
from scripts.forex_delivery.run_oanda_demo_broker_adapter_one_order_final_wire_v1 import (  # noqa: E402
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


def runtime_exception(**overrides):
    result = {
        "status": "EXCEPTION_READY_FOR_MANUAL_RUNTIME_DEMO_ORDER_ATTEMPT",
        "allowed_manual_runtime_invocation": True,
        "one_order_runtime_contract": {
            "one_order_only": True,
            "max_order_attempts": 1,
        },
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    result.update(overrides)
    return result


def adapter_context(**overrides):
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
        "broker_network_call_performed": False,
        "order_placement_performed": False,
        "manual_runtime_invocation_required": True,
    }
    context.update(overrides)
    return context


def order_payload(**overrides):
    payload = {
        "instrument": "EUR_USD",
        "direction": "BUY",
        "order_type": "MARKET",
        "units": 100,
        "stop_loss": 1.095,
        "take_profit": 1.11,
        "risk_amount": 5.0,
        "reward_risk_ratio": 2.0,
        "client_order_id": "AIOS-DEMO-ONE-ORDER-001",
    }
    payload.update(overrides)
    return payload


def owner_approval(**overrides):
    approval = {
        "owner_approved_final_manual_demo_order_attempt": True,
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
        "owner_confirmed_no_second_order": True,
    }
    approval.update(overrides)
    return approval


def evaluate(**overrides):
    payload = {
        "runtime_exception_result": runtime_exception(),
        "adapter_runtime_context": adapter_context(),
        "sanitized_order_payload": order_payload(),
        "owner_final_wire_approval": owner_approval(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_broker_adapter_one_order_final_wire_v1(**payload)


def run_script(args):
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def assert_execution_authority_false(result):
    assert result["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_default_blocks_missing_runtime_exception():
    result = evaluate_oanda_demo_broker_adapter_one_order_final_wire_v1()
    assert result["status"] == FINAL_WIRE_BLOCKED_MISSING_RUNTIME_EXCEPTION
    assert "missing_runtime_exception_result" in result["blockers"]
    assert_execution_authority_false(result)


def test_runtime_exception_not_ready_blocks():
    result = evaluate(
        runtime_exception_result=runtime_exception(
            status="EXCEPTION_BLOCKED_OWNER_APPROVAL"
        )
    )
    assert result["status"] == FINAL_WIRE_BLOCKED_RUNTIME_EXCEPTION_NOT_READY
    assert "runtime_exception_status_not_ready" in result["blockers"]


def test_missing_adapter_context_blocks():
    result = evaluate(adapter_runtime_context=None)
    assert result["status"] == FINAL_WIRE_BLOCKED_ADAPTER_CONTEXT
    assert "missing_adapter_runtime_context" in result["blockers"]


def test_adapter_context_live_environment_blocks():
    result = evaluate(adapter_runtime_context=adapter_context(live_environment=True))
    assert result["status"] == FINAL_WIRE_BLOCKED_ADAPTER_CONTEXT
    assert "adapter_context_live_environment_must_be_false" in result["blockers"]


def test_adapter_context_missing_runtime_credentials_blocks():
    result = evaluate(
        adapter_runtime_context=adapter_context(runtime_only_credentials_present=False)
    )
    assert result["status"] == FINAL_WIRE_BLOCKED_ADAPTER_CONTEXT
    assert "adapter_context_runtime_only_credentials_present_required" in result[
        "blockers"
    ]


def test_credential_persistence_blocks():
    result = evaluate(
        adapter_runtime_context=adapter_context(credential_persistence_detected=True)
    )
    assert result["status"] == FINAL_WIRE_BLOCKED_ADAPTER_CONTEXT
    assert "adapter_context_credential_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_account_id_persistence_blocks():
    result = evaluate(
        adapter_runtime_context=adapter_context(account_id_persistence_detected=True)
    )
    assert result["status"] == FINAL_WIRE_BLOCKED_ADAPTER_CONTEXT
    assert "adapter_context_account_id_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_existing_open_orders_block():
    result = evaluate(adapter_runtime_context=adapter_context(existing_open_orders=1))
    assert result["status"] == FINAL_WIRE_BLOCKED_ADAPTER_CONTEXT
    assert "adapter_context_existing_open_orders_must_be_zero" in result["blockers"]


def test_existing_pending_orders_block():
    result = evaluate(adapter_runtime_context=adapter_context(existing_pending_orders=1))
    assert result["status"] == FINAL_WIRE_BLOCKED_ADAPTER_CONTEXT
    assert "adapter_context_existing_pending_orders_must_be_zero" in result["blockers"]


def test_order_already_attempted_blocks():
    result = evaluate(adapter_runtime_context=adapter_context(order_already_attempted=True))
    assert result["status"] == FINAL_WIRE_BLOCKED_ADAPTER_CONTEXT
    assert "adapter_context_order_already_attempted_must_be_false" in result["blockers"]


def test_missing_order_payload_blocks():
    result = evaluate(sanitized_order_payload=None)
    assert result["status"] == FINAL_WIRE_BLOCKED_ORDER_PAYLOAD
    assert "missing_sanitized_order_payload" in result["blockers"]


def test_order_payload_missing_stop_loss_blocks():
    payload = order_payload()
    payload.pop("stop_loss")
    result = evaluate(sanitized_order_payload=payload)
    assert result["status"] == FINAL_WIRE_BLOCKED_ORDER_PAYLOAD
    assert "order_payload_stop_loss_required" in result["blockers"]


def test_order_payload_missing_take_profit_blocks():
    payload = order_payload()
    payload.pop("take_profit")
    result = evaluate(sanitized_order_payload=payload)
    assert result["status"] == FINAL_WIRE_BLOCKED_ORDER_PAYLOAD
    assert "order_payload_take_profit_required" in result["blockers"]


def test_order_payload_containing_account_id_blocks():
    result = evaluate(sanitized_order_payload=order_payload(account_id="abc123"))
    assert result["status"] == FINAL_WIRE_BLOCKED_ORDER_PAYLOAD
    assert "order_payload_forbidden_account_id_field" in result["blockers"]


def test_order_payload_containing_token_blocks():
    result = evaluate(sanitized_order_payload=order_payload(token="secret-token"))
    assert result["status"] == FINAL_WIRE_BLOCKED_ORDER_PAYLOAD
    assert "order_payload_forbidden_token_field" in result["blockers"]


def test_invalid_direction_blocks():
    result = evaluate(sanitized_order_payload=order_payload(direction="HOLD"))
    assert result["status"] == FINAL_WIRE_BLOCKED_ORDER_PAYLOAD
    assert "order_payload_direction_must_be_buy_or_sell" in result["blockers"]


def test_invalid_units_blocks():
    result = evaluate(sanitized_order_payload=order_payload(units=0))
    assert result["status"] == FINAL_WIRE_BLOCKED_ORDER_PAYLOAD
    assert "order_payload_units_must_be_positive" in result["blockers"]


def test_missing_owner_approval_blocks():
    result = evaluate(owner_final_wire_approval=None)
    assert result["status"] == FINAL_WIRE_BLOCKED_OWNER_APPROVAL
    assert "missing_owner_final_wire_approval" in result["blockers"]


def test_owner_failing_no_second_order_confirmation_blocks():
    result = evaluate(
        owner_final_wire_approval=owner_approval(owner_confirmed_no_second_order=False)
    )
    assert result["status"] == FINAL_WIRE_BLOCKED_OWNER_APPROVAL
    assert "owner_confirmed_no_second_order_required" in result["blockers"]


def test_valid_final_wire_returns_ready_for_manual_runtime_attempt():
    result = evaluate()
    assert result["status"] == FINAL_WIRE_READY_FOR_MANUAL_ONE_ORDER_DEMO_RUNTIME_ATTEMPT
    assert result["final_wire_request"]["status"] == "READY_FOR_MANUAL_RUNTIME_INVOCATION"
    assert result["dry_run_rehearsal"]["ready"] is True


def test_final_wire_request_contains_one_order_cap():
    request = evaluate()["final_wire_request"]
    assert request["one_order_only"] is True
    assert request["max_order_attempts"] == 1
    assert request["stop_after_order_attempt"] is True
    assert request["no_second_order"] is True


def test_all_execution_authority_fields_remain_false():
    assert_execution_authority_false(evaluate())


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)


def test_script_dry_run_prints_json_and_does_not_place_order():
    code, payload = run_script([])
    assert code == 0
    assert payload["script_status"] == "DRY_RUN_DECISION_ONLY"
    assert payload["order_placement_performed"] is False
    assert payload["broker_network_call_performed"] is False


def test_script_print_template_prints_json_template():
    code, payload = run_script(["--print-template"])
    assert code == 0
    assert payload["script_status"] == "TEMPLATE_ONLY"
    assert "template" in payload
    assert payload["order_placement_performed"] is False


def test_script_execute_flag_without_required_confirmations_blocks():
    code, payload = run_script(["--execute-demo-order"])
    assert code == 1
    assert payload["script_status"] == "BLOCKED_MISSING_REQUIRED_CONFIRMATIONS"
    assert "--i-confirm-no-second-order" in payload["missing_confirmations"]
    assert payload["order_placement_performed"] is False


def test_script_execute_flag_with_confirmations_returns_final_owner_runtime_block():
    args = [
        "--execute-demo-order",
        "--i-understand-demo-only",
        "--i-understand-one-order-only",
        "--i-understand-loss-possible",
        "--i-understand-no-profit-guarantee",
        "--i-confirm-stop-loss",
        "--i-confirm-take-profit",
        "--i-confirm-no-second-order",
    ]
    code, payload = run_script(args)
    assert code == 1
    assert payload["script_status"] == "BLOCKED_PENDING_FINAL_OWNER_RUNTIME_RUN"
    assert payload["order_placement_performed"] is False
    assert payload["broker_network_call_performed"] is False
