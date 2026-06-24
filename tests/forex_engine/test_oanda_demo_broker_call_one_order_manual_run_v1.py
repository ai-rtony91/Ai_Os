from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_broker_call_one_order_manual_run_v1 import (  # noqa: E402
    BROKER_CALL_ATTEMPTED_DEMO_ORDER_ONCE,
    BROKER_CALL_BLOCKED_CONTEXT,
    BROKER_CALL_BLOCKED_FINAL_OWNER_RUN_NOT_READY,
    BROKER_CALL_BLOCKED_MISSING_FINAL_OWNER_RUN,
    BROKER_CALL_BLOCKED_ORDER_PAYLOAD,
    BROKER_CALL_BLOCKED_OWNER_APPROVAL,
    BROKER_CALL_DRY_RUN_READY,
    BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED,
    evaluate_oanda_demo_broker_call_one_order_manual_run_v1,
)
from scripts.forex_delivery.run_oanda_demo_broker_call_one_order_manual_run_v1 import (  # noqa: E402
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


def final_owner_run(**overrides):
    result = {
        "status": "OWNER_RUN_READY_FOR_EXPLICIT_MANUAL_COMMAND",
        "manual_runtime_run_contract": {
            "ready": True,
            "one_order_only": True,
            "max_order_attempts": 1,
            "actual_execution_requires_owner_to_run_command": True,
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
        "demo_api_base_url": "https://api-fxpractice.oanda.com",
        "live_api_base_url": "",
        "runtime_access_token_present": True,
        "runtime_account_id_present": True,
        "token_runtime_only": True,
        "account_id_runtime_only": True,
        "credential_persistence_detected": False,
        "account_id_persistence_detected": False,
        "one_order_only": True,
        "max_order_attempts": 1,
        "order_already_attempted": False,
        "existing_open_orders": 0,
        "existing_pending_orders": 0,
        "kill_switch_ready": True,
        "daily_stop_ready": True,
        "max_loss_gate_ready": True,
        "pre_trade_evidence_ready": True,
        "post_trade_evidence_plan_ready": True,
        "broker_network_call_performed": False,
        "order_placement_performed": False,
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
        "owner_approved_actual_oanda_demo_broker_call": True,
        "owner_confirmed_demo_only": True,
        "owner_confirmed_no_live_money": True,
        "owner_confirmed_one_order_only": True,
        "owner_confirmed_max_one_attempt": True,
        "owner_confirmed_stop_loss": True,
        "owner_confirmed_take_profit": True,
        "owner_confirmed_loss_possible": True,
        "owner_confirmed_no_profit_guarantee": True,
        "owner_confirmed_no_second_order": True,
        "owner_confirmed_manual_run_only": True,
        "owner_confirmed_no_autonomous_execution": True,
        "owner_confirmed_post_trade_evidence_required": True,
    }
    approval.update(overrides)
    return approval


def evaluate(**overrides):
    payload = {
        "final_owner_run_result": final_owner_run(),
        "broker_call_context": broker_context(),
        "sanitized_order_payload": order_payload(),
        "owner_broker_call_approval": owner_approval(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_broker_call_one_order_manual_run_v1(**payload)


def run_script(args):
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def assert_execution_authority_false(result):
    assert result["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_default_blocks_missing_final_owner_run():
    result = evaluate_oanda_demo_broker_call_one_order_manual_run_v1()
    assert result["status"] == BROKER_CALL_BLOCKED_MISSING_FINAL_OWNER_RUN
    assert "missing_final_owner_run_result" in result["blockers"]
    assert result["execution_attempt"]["network_call_performed"] is False
    assert result["execution_attempt"]["order_placement_performed"] is False
    assert_execution_authority_false(result)


def test_final_owner_run_not_ready_blocks():
    result = evaluate(final_owner_run_result=final_owner_run(status="OWNER_RUN_BLOCKED"))
    assert result["status"] == BROKER_CALL_BLOCKED_FINAL_OWNER_RUN_NOT_READY
    assert "final_owner_run_status_not_ready" in result["blockers"]


def test_missing_context_blocks():
    result = evaluate(broker_call_context=None)
    assert result["status"] == BROKER_CALL_BLOCKED_CONTEXT
    assert "missing_broker_call_context" in result["blockers"]


def test_live_environment_blocks():
    result = evaluate(broker_call_context=broker_context(live_environment=True))
    assert result["status"] == BROKER_CALL_BLOCKED_CONTEXT
    assert "broker_call_context_live_environment_must_be_false" in result["blockers"]


def test_live_api_base_url_blocks():
    result = evaluate(
        broker_call_context=broker_context(
            live_api_base_url="https://api-fxtrade.oanda.com"
        )
    )
    assert result["status"] == BROKER_CALL_BLOCKED_CONTEXT
    assert "broker_call_context_live_api_base_url_must_be_absent" in result[
        "blockers"
    ]


def test_missing_runtime_token_blocks():
    result = evaluate(
        broker_call_context=broker_context(runtime_access_token_present=False)
    )
    assert result["status"] == BROKER_CALL_BLOCKED_CONTEXT
    assert "broker_call_context_runtime_access_token_present_required" in result[
        "blockers"
    ]


def test_missing_runtime_account_id_blocks():
    result = evaluate(
        broker_call_context=broker_context(runtime_account_id_present=False)
    )
    assert result["status"] == BROKER_CALL_BLOCKED_CONTEXT
    assert "broker_call_context_runtime_account_id_present_required" in result[
        "blockers"
    ]


def test_credential_persistence_blocks():
    result = evaluate(
        broker_call_context=broker_context(credential_persistence_detected=True)
    )
    assert result["status"] == BROKER_CALL_BLOCKED_CONTEXT
    assert "broker_call_context_credential_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_account_id_persistence_blocks():
    result = evaluate(
        broker_call_context=broker_context(account_id_persistence_detected=True)
    )
    assert result["status"] == BROKER_CALL_BLOCKED_CONTEXT
    assert "broker_call_context_account_id_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_existing_open_orders_blocks():
    result = evaluate(broker_call_context=broker_context(existing_open_orders=1))
    assert result["status"] == BROKER_CALL_BLOCKED_CONTEXT
    assert "broker_call_context_existing_open_orders_must_be_zero" in result[
        "blockers"
    ]


def test_existing_pending_orders_blocks():
    result = evaluate(broker_call_context=broker_context(existing_pending_orders=1))
    assert result["status"] == BROKER_CALL_BLOCKED_CONTEXT
    assert "broker_call_context_existing_pending_orders_must_be_zero" in result[
        "blockers"
    ]


def test_order_already_attempted_blocks():
    result = evaluate(broker_call_context=broker_context(order_already_attempted=True))
    assert result["status"] == BROKER_CALL_BLOCKED_CONTEXT
    assert "broker_call_context_order_already_attempted_must_be_false" in result[
        "blockers"
    ]


def test_missing_order_payload_blocks():
    result = evaluate(sanitized_order_payload=None)
    assert result["status"] == BROKER_CALL_BLOCKED_ORDER_PAYLOAD
    assert "missing_sanitized_order_payload" in result["blockers"]


def test_order_payload_missing_stop_loss_blocks():
    payload = order_payload()
    payload.pop("stop_loss")
    result = evaluate(sanitized_order_payload=payload)
    assert result["status"] == BROKER_CALL_BLOCKED_ORDER_PAYLOAD
    assert "order_payload_stop_loss_required" in result["blockers"]


def test_order_payload_missing_take_profit_blocks():
    payload = order_payload()
    payload.pop("take_profit")
    result = evaluate(sanitized_order_payload=payload)
    assert result["status"] == BROKER_CALL_BLOCKED_ORDER_PAYLOAD
    assert "order_payload_take_profit_required" in result["blockers"]


def test_order_payload_containing_token_blocks():
    result = evaluate(sanitized_order_payload=order_payload(token="demo_token"))
    assert result["status"] == BROKER_CALL_BLOCKED_ORDER_PAYLOAD
    assert "order_payload_forbidden_token_field" in result["blockers"]


def test_order_payload_containing_account_id_blocks():
    result = evaluate(sanitized_order_payload=order_payload(account_id="abc-123"))
    assert result["status"] == BROKER_CALL_BLOCKED_ORDER_PAYLOAD
    assert "order_payload_forbidden_account_id_field" in result["blockers"]


def test_invalid_direction_blocks():
    result = evaluate(sanitized_order_payload=order_payload(direction="HOLD"))
    assert result["status"] == BROKER_CALL_BLOCKED_ORDER_PAYLOAD
    assert "order_payload_direction_must_be_buy_or_sell" in result["blockers"]


def test_invalid_units_blocks():
    result = evaluate(sanitized_order_payload=order_payload(units=0))
    assert result["status"] == BROKER_CALL_BLOCKED_ORDER_PAYLOAD
    assert "order_payload_units_must_be_positive" in result["blockers"]


def test_missing_owner_approval_blocks():
    result = evaluate(owner_broker_call_approval=None)
    assert result["status"] == BROKER_CALL_BLOCKED_OWNER_APPROVAL
    assert "missing_owner_broker_call_approval" in result["blockers"]


def test_owner_failing_actual_broker_call_approval_blocks():
    result = evaluate(
        owner_broker_call_approval=owner_approval(
            owner_approved_actual_oanda_demo_broker_call=False
        )
    )
    assert result["status"] == BROKER_CALL_BLOCKED_OWNER_APPROVAL
    assert "owner_approved_actual_oanda_demo_broker_call_required" in result[
        "blockers"
    ]


def test_valid_dry_run_returns_ready_with_no_network_and_no_order():
    result = evaluate()
    assert result["status"] == BROKER_CALL_DRY_RUN_READY
    assert result["execution_attempt"]["network_call_performed"] is False
    assert result["execution_attempt"]["order_placement_performed"] is False
    assert result["transport_request_preview"]["method"] == "POST"


def test_execute_true_without_transport_returns_transport_required():
    result = evaluate(execute_demo_order=True)
    assert result["status"] == BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED
    assert result["execution_attempt"]["network_call_performed"] is False
    assert result["execution_attempt"]["order_placement_performed"] is False


def test_execute_true_with_fake_transport_calls_transport_exactly_once():
    calls = []

    def fake_transport(request):
        calls.append(request)
        return {"status_code": 201, "status": "created"}

    result = evaluate(execute_demo_order=True, http_transport=fake_transport)
    assert len(calls) == 1
    assert result["status"] == BROKER_CALL_ATTEMPTED_DEMO_ORDER_ONCE
    assert result["execution_attempt"]["order_attempt_count"] == 1


def test_fake_successful_transport_returns_attempted_demo_order_once():
    def fake_transport(_request):
        return {"status_code": 201, "created": True}

    result = evaluate(execute_demo_order=True, http_transport=fake_transport)
    assert result["status"] == BROKER_CALL_ATTEMPTED_DEMO_ORDER_ONCE
    assert result["execution_attempt"]["network_call_performed"] is True
    assert result["execution_attempt"]["order_placement_performed"] is True


def test_transport_request_uses_demo_practice_base_url_only():
    result = evaluate()
    request = result["transport_request_preview"]
    assert request["url"].startswith(
        "https://api-fxpractice.oanda.com/v3/accounts/"
    )
    assert "api-fxtrade.oanda.com" not in request["url"]


def test_returned_evidence_does_not_include_token_or_account_id_values():
    def fake_transport(_request):
        return {
            "status_code": 201,
            "account_id": "REAL_ACCOUNT_123",
            "authorization": "Bearer REAL_TOKEN_456",
            "nested": {"token": "REAL_TOKEN_456"},
        }

    result = evaluate(execute_demo_order=True, http_transport=fake_transport)
    evidence = json.dumps(result, sort_keys=True)
    assert "REAL_ACCOUNT_123" not in evidence
    assert "REAL_TOKEN_456" not in evidence
    assert "RUNTIME_ONLY_ACCOUNT_ID" in evidence
    assert "RUNTIME_ONLY_BEARER_TOKEN" in evidence


def test_sell_order_uses_negative_units():
    result = evaluate(sanitized_order_payload=order_payload(direction="SELL", units=25))
    assert result["oanda_order_payload"]["order"]["units"] == "-25"


def test_buy_order_uses_positive_units():
    result = evaluate(sanitized_order_payload=order_payload(direction="BUY", units=25))
    assert result["oanda_order_payload"]["order"]["units"] == "25"


def test_all_execution_authority_fields_remain_false():
    assert_execution_authority_false(evaluate())


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)


def test_script_dry_run_prints_json_and_performs_no_broker_action():
    code, payload = run_script([])
    assert code == 0
    assert payload["script_status"] == "DRY_RUN_DECISION_ONLY"
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["account_id_read_performed"] is False


def test_script_print_template_prints_json_template():
    code, payload = run_script(["--print-template"])
    assert code == 0
    assert payload["script_status"] == "BROKER_CALL_TEMPLATE_ONLY"
    assert "template" in payload
    assert payload["template"]["runtime_credentials"]["OANDA_DEMO_ACCESS_TOKEN"]
    assert payload["order_placement_performed"] is False


def test_script_execute_flag_without_confirmations_blocks():
    code, payload = run_script(["--execute-demo-order"])
    assert code == 1
    assert payload["script_status"] == "BLOCKED_MISSING_REQUIRED_CONFIRMATIONS"
    assert "--i-approve-actual-oanda-demo-broker-call" in payload[
        "missing_confirmations"
    ]
    assert payload["order_placement_performed"] is False


def test_script_execute_flag_with_all_confirmations_still_does_not_call_broker():
    args = [
        "--execute-demo-order",
        "--i-approve-actual-oanda-demo-broker-call",
        "--i-understand-demo-only",
        "--i-understand-one-order-only",
        "--i-understand-loss-possible",
        "--i-understand-no-profit-guarantee",
        "--i-confirm-stop-loss",
        "--i-confirm-take-profit",
        "--i-confirm-no-second-order",
        "--i-confirm-post-trade-evidence",
    ]
    code, payload = run_script(args)
    assert code == 1
    assert payload["script_status"] == "BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED"
    assert payload["decision"]["status"] == BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False
