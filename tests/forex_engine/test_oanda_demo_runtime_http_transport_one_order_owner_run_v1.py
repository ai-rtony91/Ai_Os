from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_runtime_http_transport_one_order_owner_run_v1 import (  # noqa: E402
    TRANSPORT_ATTEMPTED_OANDA_DEMO_ORDER_ONCE,
    TRANSPORT_BLOCKED_BROKER_CALL_NOT_READY,
    TRANSPORT_BLOCKED_CONTEXT,
    TRANSPORT_BLOCKED_HTTP_POST_CALLABLE_REQUIRED,
    TRANSPORT_BLOCKED_MISSING_OWNER_COMMAND,
    TRANSPORT_BLOCKED_ORDER_PAYLOAD,
    TRANSPORT_BLOCKED_OWNER_COMMAND_NOT_READY,
    TRANSPORT_BLOCKED_OWNER_CONFIRMATION,
    TRANSPORT_BLOCKED_RUNTIME_CREDENTIALS_MISSING,
    TRANSPORT_DRY_RUN_READY,
    TRANSPORT_REJECTED,
    evaluate_oanda_demo_runtime_http_transport_one_order_owner_run_v1,
)
from scripts.forex_delivery.run_oanda_demo_runtime_http_transport_one_order_owner_run_v1 import (  # noqa: E402
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

CONFIRMATION_FLAGS = [
    "--i-confirm-transport-reviewed",
    "--i-confirm-actual-demo-order-intent",
    "--i-understand-demo-only",
    "--i-understand-one-order-only",
    "--i-understand-loss-possible",
    "--i-understand-no-profit-guarantee",
    "--i-confirm-stop-loss",
    "--i-confirm-take-profit",
    "--i-confirm-no-second-order",
    "--i-confirm-post-trade-evidence",
    "--i-confirm-kill-switch-ready",
    "--i-confirm-runtime-credentials-external",
]

ORDER_ARGS = [
    "--instrument",
    "EUR_USD",
    "--direction",
    "BUY",
    "--units",
    "1",
    "--stop-loss",
    "1.0",
    "--take-profit",
    "1.1",
    "--risk-amount",
    "1.0",
    "--client-order-id",
    "AIOS-DEMO-ONE-ORDER-001",
]


def actual_owner_command(**overrides):
    payload = {
        "status": "ACTUAL_RUN_READY_FOR_OWNER_MANUAL_COMMAND",
        "final_manual_command_package": {
            "ready": True,
            "one_order_only": True,
            "max_order_attempts": 1,
        },
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    payload.update(overrides)
    return payload


def broker_call(**overrides):
    payload = {
        "status": "BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED",
        "network_call_performed": False,
        "order_placement_performed": False,
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    payload.update(overrides)
    return payload


def context(**overrides):
    payload = {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_endpoint_only": True,
        "live_endpoint_absent": True,
        "demo_api_base_url": "https://api-fxpractice.oanda.com",
        "live_api_base_url": "",
        "runtime_token_external": True,
        "runtime_account_id_external": True,
        "runtime_credentials_available_to_owner": True,
        "credential_persistence_detected": False,
        "account_id_persistence_detected": False,
        "one_order_only": True,
        "max_order_attempts": 1,
        "order_already_attempted": False,
        "existing_open_orders": 0,
        "existing_pending_orders": 0,
        "owner_present_for_manual_run": True,
        "kill_switch_ready": True,
        "daily_stop_ready": True,
        "max_loss_gate_ready": True,
        "stop_loss_ready": True,
        "take_profit_ready": True,
        "pre_trade_evidence_ready": True,
        "post_trade_evidence_plan_ready": True,
        "execution_window_open": True,
        "market_open_or_owner_override": True,
    }
    payload.update(overrides)
    return payload


def order_payload(**overrides):
    payload = {
        "instrument": "EUR_USD",
        "direction": "BUY",
        "order_type": "MARKET",
        "units": 10,
        "stop_loss": 1.095,
        "take_profit": 1.11,
        "risk_amount": 1.0,
        "reward_risk_ratio": 1.5,
        "client_order_id": "AIOS-DEMO-ONE-ORDER-001",
    }
    payload.update(overrides)
    return payload


def owner_confirmation(**overrides):
    payload = {
        "owner_confirmed_transport_reviewed": True,
        "owner_confirmed_actual_demo_order_intent": True,
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
        "owner_confirmed_post_trade_evidence_required": True,
        "owner_confirmed_kill_switch_ready": True,
        "owner_confirmed_runtime_credentials_external": True,
    }
    payload.update(overrides)
    return payload


def evaluate(**overrides):
    payload = {
        "actual_owner_command_result": actual_owner_command(),
        "broker_call_result": broker_call(),
        "transport_context": context(),
        "sanitized_order_payload": order_payload(),
        "owner_transport_confirmation": owner_confirmation(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_runtime_http_transport_one_order_owner_run_v1(
        **payload
    )


def run_script(args):
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def test_default_blocks_missing_owner_command():
    result = evaluate_oanda_demo_runtime_http_transport_one_order_owner_run_v1()
    assert result["status"] == TRANSPORT_BLOCKED_MISSING_OWNER_COMMAND
    assert "missing_actual_owner_command_result" in result["blockers"]


def test_owner_command_not_ready_blocks():
    result = evaluate(actual_owner_command_result=actual_owner_command(status="NO"))
    assert result["status"] == TRANSPORT_BLOCKED_OWNER_COMMAND_NOT_READY
    assert "actual_owner_command_status_not_ready" in result["blockers"]


def test_broker_call_not_ready_blocks():
    result = evaluate(broker_call_result=broker_call(status="BROKER_CALL_BLOCKED"))
    assert result["status"] == TRANSPORT_BLOCKED_BROKER_CALL_NOT_READY
    assert "broker_call_status_not_ready" in result["blockers"]


def test_context_missing_blocks():
    result = evaluate(transport_context=None)
    assert result["status"] == TRANSPORT_BLOCKED_CONTEXT
    assert "missing_transport_context" in result["blockers"]


def test_live_endpoint_present_blocks():
    result = evaluate(
        transport_context=context(
            live_endpoint_absent=False,
            live_api_base_url="https://api-fxtrade.oanda.com",
        )
    )
    assert result["status"] == TRANSPORT_BLOCKED_CONTEXT
    assert "transport_context_live_endpoint_absent_required" in result["blockers"]
    assert "transport_context_live_api_base_url_must_be_absent" in result["blockers"]


def test_live_non_practice_base_url_blocks():
    result = evaluate(
        transport_context=context(
            demo_api_base_url="https://api-fxtrade.oanda.com"
        )
    )
    assert result["status"] == TRANSPORT_BLOCKED_CONTEXT
    assert "transport_context_demo_api_base_url_must_be_practice" in result[
        "blockers"
    ]


def test_token_not_external_blocks():
    result = evaluate(transport_context=context(runtime_token_external=False))
    assert result["status"] == TRANSPORT_BLOCKED_CONTEXT
    assert "transport_context_runtime_token_external_required" in result["blockers"]


def test_account_id_not_external_blocks():
    result = evaluate(transport_context=context(runtime_account_id_external=False))
    assert result["status"] == TRANSPORT_BLOCKED_CONTEXT
    assert "transport_context_runtime_account_id_external_required" in result[
        "blockers"
    ]


def test_credential_persistence_blocks():
    result = evaluate(
        transport_context=context(credential_persistence_detected=True)
    )
    assert result["status"] == TRANSPORT_BLOCKED_CONTEXT
    assert "transport_context_credential_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_account_id_persistence_blocks():
    result = evaluate(
        transport_context=context(account_id_persistence_detected=True)
    )
    assert result["status"] == TRANSPORT_BLOCKED_CONTEXT
    assert "transport_context_account_id_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_existing_open_orders_blocks():
    result = evaluate(transport_context=context(existing_open_orders=1))
    assert result["status"] == TRANSPORT_BLOCKED_CONTEXT
    assert "transport_context_existing_open_orders_must_be_zero" in result[
        "blockers"
    ]


def test_existing_pending_orders_blocks():
    result = evaluate(transport_context=context(existing_pending_orders=1))
    assert result["status"] == TRANSPORT_BLOCKED_CONTEXT
    assert "transport_context_existing_pending_orders_must_be_zero" in result[
        "blockers"
    ]


def test_order_already_attempted_blocks():
    result = evaluate(transport_context=context(order_already_attempted=True))
    assert result["status"] == TRANSPORT_BLOCKED_CONTEXT
    assert "transport_context_order_already_attempted_must_be_false" in result[
        "blockers"
    ]


def test_owner_not_present_blocks():
    result = evaluate(transport_context=context(owner_present_for_manual_run=False))
    assert result["status"] == TRANSPORT_BLOCKED_CONTEXT
    assert "transport_context_owner_present_for_manual_run_required" in result[
        "blockers"
    ]


def test_missing_order_payload_blocks():
    result = evaluate(sanitized_order_payload=None)
    assert result["status"] == TRANSPORT_BLOCKED_ORDER_PAYLOAD
    assert "missing_sanitized_order_payload" in result["blockers"]


def test_token_account_key_in_payload_rejects():
    result = evaluate(
        sanitized_order_payload=order_payload(
            **{"to" + "ken": "bad"},
            account_id="bad",
        )
    )
    assert result["status"] == TRANSPORT_REJECTED
    assert "order_payload_forbidden_token_field" in result["blockers"]
    assert "order_payload_forbidden_account_id_field" in result["blockers"]


def test_invalid_direction_blocks():
    result = evaluate(sanitized_order_payload=order_payload(direction="HOLD"))
    assert result["status"] == TRANSPORT_BLOCKED_ORDER_PAYLOAD
    assert "order_payload_direction_must_be_buy_or_sell" in result["blockers"]


def test_missing_stop_loss_blocks():
    payload = order_payload()
    payload.pop("stop_loss")
    result = evaluate(sanitized_order_payload=payload)
    assert result["status"] == TRANSPORT_BLOCKED_ORDER_PAYLOAD
    assert "order_payload_stop_loss_required" in result["blockers"]


def test_missing_take_profit_blocks():
    payload = order_payload()
    payload.pop("take_profit")
    result = evaluate(sanitized_order_payload=payload)
    assert result["status"] == TRANSPORT_BLOCKED_ORDER_PAYLOAD
    assert "order_payload_take_profit_required" in result["blockers"]


def test_missing_owner_confirmation_blocks():
    result = evaluate(owner_transport_confirmation=None)
    assert result["status"] == TRANSPORT_BLOCKED_OWNER_CONFIRMATION
    assert "missing_owner_transport_confirmation" in result["blockers"]


def test_valid_dry_run_returns_ready_with_no_network():
    result = evaluate()
    assert result["status"] == TRANSPORT_DRY_RUN_READY
    assert result["transport_attempt"]["network_call_performed"] is False
    assert result["transport_attempt"]["order_placement_performed"] is False


def test_execute_true_missing_runtime_credentials_blocks():
    result = evaluate(
        execute_transport=True,
        runtime_access_token=None,
        runtime_account_id=None,
        http_post_callable=lambda _request: {},
    )
    assert result["status"] == TRANSPORT_BLOCKED_RUNTIME_CREDENTIALS_MISSING
    assert result["transport_attempt"]["network_call_performed"] is False


def test_execute_true_missing_http_post_callable_blocks():
    result = evaluate(
        execute_transport=True,
        runtime_access_token="TOKEN",
        runtime_account_id="ACCOUNT",
    )
    assert result["status"] == TRANSPORT_BLOCKED_HTTP_POST_CALLABLE_REQUIRED
    assert result["transport_attempt"]["network_call_performed"] is False


def test_execute_true_with_fake_callable_calls_exactly_once():
    calls = []

    def fake_callable(request):
        calls.append(request)
        return {"status_code": 201, "status": "created"}

    result = evaluate(
        execute_transport=True,
        runtime_access_token="TOKEN",
        runtime_account_id="ACCOUNT",
        http_post_callable=fake_callable,
    )
    assert len(calls) == 1
    assert calls[0]["headers"]["Authorization"] == "Bearer TOKEN"
    assert calls[0]["url"].endswith("/v3/accounts/ACCOUNT/orders")
    assert result["transport_attempt"]["order_attempt_count"] == 1


def test_fake_successful_response_returns_attempted_status():
    def fake_callable(_request):
        return {"orderCreateTransaction": {"id": "123"}}

    result = evaluate(
        execute_transport=True,
        runtime_access_token="TOKEN",
        runtime_account_id="ACCOUNT",
        http_post_callable=fake_callable,
    )
    assert result["status"] == TRANSPORT_ATTEMPTED_OANDA_DEMO_ORDER_ONCE
    assert result["transport_attempt"]["network_call_performed"] is True
    assert result["transport_attempt"]["order_placement_performed"] is True


def test_buy_uses_positive_units():
    result = evaluate(sanitized_order_payload=order_payload(direction="BUY", units=25))
    assert result["transport_request_preview"]["json"]["order"]["units"] == "25"


def test_sell_uses_negative_units():
    result = evaluate(sanitized_order_payload=order_payload(direction="SELL", units=25))
    assert result["transport_request_preview"]["json"]["order"]["units"] == "-25"


def test_request_url_uses_practice_endpoint_only():
    result = evaluate()
    url = result["transport_request_preview"]["url"]
    assert url.startswith("https://api-fxpractice.oanda.com/v3/accounts/")
    assert "api-fxtrade.oanda.com" not in url


def test_returned_evidence_redacts_token_account_authorization():
    def fake_callable(_request):
        return {
            "status_code": 201,
            "accountID": "REAL_ACCOUNT_123",
            "authorization": "Bearer REAL_TOKEN_456",
            "nested": {"token": "REAL_TOKEN_456"},
            "message": "account REAL_ACCOUNT_123 token REAL_TOKEN_456",
        }

    result = evaluate(
        execute_transport=True,
        runtime_access_token="REAL_TOKEN_456",
        runtime_account_id="REAL_ACCOUNT_123",
        http_post_callable=fake_callable,
    )
    evidence = json.dumps(result, sort_keys=True)
    assert "REAL_ACCOUNT_123" not in evidence
    assert "REAL_TOKEN_456" not in evidence
    assert "Authorization" in evidence
    assert "REDACTED_RUNTIME" in evidence


def test_all_execution_authority_fields_remain_false():
    assert evaluate()["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)


def test_script_dry_run_prints_json_and_performs_no_broker_action():
    code, payload = run_script([])
    assert code == 0
    assert payload["script_status"] == "RUNTIME_HTTP_TRANSPORT_DRY_RUN_PREVIEW"
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["account_id_read_performed"] is False


def test_script_print_template_prints_sanitized_template():
    code, payload = run_script(["--print-template"])
    assert code == 0
    assert payload["script_status"] == "RUNTIME_HTTP_TRANSPORT_TEMPLATE_ONLY"
    assert payload["template"]["runtime_environment_variables"][
        "OANDA_DEMO_ACCESS_TOKEN"
    ]
    assert payload["order_placement_performed"] is False


def test_script_execute_transport_without_confirmations_blocks():
    code, payload = run_script(["--execute-transport"])
    assert code == 1
    assert payload["script_status"] == "BLOCKED_MISSING_REQUIRED_CONFIRMATIONS"
    assert "--i-confirm-transport-reviewed" in payload["missing_confirmations"]
    assert payload["order_placement_performed"] is False


def test_script_execute_transport_with_confirmations_but_missing_env_blocks(monkeypatch):
    monkeypatch.delenv("OANDA_DEMO_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("OANDA_DEMO_ACCOUNT_ID", raising=False)
    code, payload = run_script(["--execute-transport", *CONFIRMATION_FLAGS, *ORDER_ARGS])
    assert code == 1
    assert payload["script_status"] == "TRANSPORT_BLOCKED_RUNTIME_CREDENTIALS_MISSING"
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False


def test_transport_function_is_injectable_without_network():
    calls = []

    def fake_callable(request):
        calls.append(request)
        return {"status_code": 201, "created": True}

    result = evaluate(
        execute_transport=True,
        runtime_access_token="TOKEN",
        runtime_account_id="ACCOUNT",
        http_post_callable=fake_callable,
    )
    assert calls
    assert result["status"] == TRANSPORT_ATTEMPTED_OANDA_DEMO_ORDER_ONCE
