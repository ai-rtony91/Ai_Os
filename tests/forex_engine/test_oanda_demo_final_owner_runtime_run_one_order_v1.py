from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_final_owner_runtime_run_one_order_v1 import (  # noqa: E402
    OWNER_RUN_BLOCKED_FINAL_WIRE_NOT_READY,
    OWNER_RUN_BLOCKED_MISSING_FINAL_WIRE,
    OWNER_RUN_BLOCKED_OWNER_APPROVAL,
    OWNER_RUN_BLOCKED_RUNTIME_CONTEXT,
    OWNER_RUN_READY_FOR_EXPLICIT_MANUAL_COMMAND,
    evaluate_oanda_demo_final_owner_runtime_run_one_order_v1,
)
from scripts.forex_delivery.run_oanda_demo_final_owner_runtime_run_one_order_v1 import (  # noqa: E402
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


def final_wire_result(**overrides):
    result = {
        "status": "FINAL_WIRE_READY_FOR_MANUAL_ONE_ORDER_DEMO_RUNTIME_ATTEMPT",
        "final_wire_request": {
            "status": "READY_FOR_MANUAL_RUNTIME_INVOCATION",
            "one_order_only": True,
            "max_order_attempts": 1,
            "live_trading_allowed": False,
            "autonomous_execution_allowed": False,
        },
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    result.update(overrides)
    return result


def owner_approval(**overrides):
    approval = {
        "owner_approved_final_manual_runtime_run": True,
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


def runtime_context(**overrides):
    context = {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "live_environment": False,
        "demo_environment": True,
        "runtime_credentials_external": True,
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


def evaluate(**overrides):
    payload = {
        "final_wire_result": final_wire_result(),
        "owner_runtime_run_approval": owner_approval(),
        "runtime_run_context": runtime_context(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_final_owner_runtime_run_one_order_v1(**payload)


def run_script(args):
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def assert_execution_authority_false(result):
    assert result["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_default_blocks_missing_final_wire():
    result = evaluate_oanda_demo_final_owner_runtime_run_one_order_v1()
    assert result["status"] == OWNER_RUN_BLOCKED_MISSING_FINAL_WIRE
    assert "missing_final_wire_result" in result["blockers"]
    assert_execution_authority_false(result)


def test_final_wire_not_ready_blocks():
    result = evaluate(final_wire_result=final_wire_result(status="FINAL_WIRE_BLOCKED"))
    assert result["status"] == OWNER_RUN_BLOCKED_FINAL_WIRE_NOT_READY
    assert "final_wire_status_not_ready" in result["blockers"]


def test_missing_owner_approval_blocks():
    result = evaluate(owner_runtime_run_approval=None)
    assert result["status"] == OWNER_RUN_BLOCKED_OWNER_APPROVAL
    assert "missing_owner_runtime_run_approval" in result["blockers"]


def test_missing_runtime_context_blocks():
    result = evaluate(runtime_run_context=None)
    assert result["status"] == OWNER_RUN_BLOCKED_RUNTIME_CONTEXT
    assert "missing_runtime_run_context" in result["blockers"]


def test_live_environment_blocks():
    result = evaluate(runtime_run_context=runtime_context(live_environment=True))
    assert result["status"] == OWNER_RUN_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_live_environment_must_be_false" in result["blockers"]


def test_credential_persistence_blocks():
    result = evaluate(
        runtime_run_context=runtime_context(credential_persistence_detected=True)
    )
    assert result["status"] == OWNER_RUN_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_credential_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_account_id_persistence_blocks():
    result = evaluate(
        runtime_run_context=runtime_context(account_id_persistence_detected=True)
    )
    assert result["status"] == OWNER_RUN_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_account_id_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_existing_open_orders_block():
    result = evaluate(runtime_run_context=runtime_context(existing_open_orders=1))
    assert result["status"] == OWNER_RUN_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_existing_open_orders_must_be_zero" in result["blockers"]


def test_existing_pending_orders_block():
    result = evaluate(runtime_run_context=runtime_context(existing_pending_orders=1))
    assert result["status"] == OWNER_RUN_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_existing_pending_orders_must_be_zero" in result["blockers"]


def test_order_already_attempted_blocks():
    result = evaluate(runtime_run_context=runtime_context(order_already_attempted=True))
    assert result["status"] == OWNER_RUN_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_order_already_attempted_must_be_false" in result["blockers"]


def test_missing_stop_loss_owner_confirmation_blocks():
    result = evaluate(
        owner_runtime_run_approval=owner_approval(owner_confirmed_stop_loss=False)
    )
    assert result["status"] == OWNER_RUN_BLOCKED_OWNER_APPROVAL
    assert "owner_confirmed_stop_loss_required" in result["blockers"]


def test_missing_take_profit_owner_confirmation_blocks():
    result = evaluate(
        owner_runtime_run_approval=owner_approval(owner_confirmed_take_profit=False)
    )
    assert result["status"] == OWNER_RUN_BLOCKED_OWNER_APPROVAL
    assert "owner_confirmed_take_profit_required" in result["blockers"]


def test_missing_no_second_order_owner_confirmation_blocks():
    result = evaluate(
        owner_runtime_run_approval=owner_approval(owner_confirmed_no_second_order=False)
    )
    assert result["status"] == OWNER_RUN_BLOCKED_OWNER_APPROVAL
    assert "owner_confirmed_no_second_order_required" in result["blockers"]


def test_valid_owner_run_returns_ready_for_explicit_manual_command():
    result = evaluate()
    assert result["status"] == OWNER_RUN_READY_FOR_EXPLICIT_MANUAL_COMMAND
    assert result["manual_runtime_run_contract"]["ready"] is True
    assert result["next_safe_action"] == "owner_may_run_manual_demo_order_command_once"


def test_manual_runtime_run_contract_is_one_order_only_true():
    assert evaluate()["manual_runtime_run_contract"]["one_order_only"] is True


def test_manual_runtime_run_contract_max_order_attempts_is_one():
    assert evaluate()["manual_runtime_run_contract"]["max_order_attempts"] == 1


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


def test_script_print_final_command_template_prints_json_template():
    code, payload = run_script(["--print-final-command-template"])
    assert code == 0
    assert payload["script_status"] == "FINAL_COMMAND_TEMPLATE_ONLY"
    assert "template" in payload
    assert payload["template"]["one_order_only"] is True
    assert payload["order_placement_performed"] is False


def test_script_execute_flag_without_confirmations_blocks():
    code, payload = run_script(["--execute-demo-order"])
    assert code == 1
    assert payload["script_status"] == "BLOCKED_MISSING_REQUIRED_CONFIRMATIONS"
    assert "--i-approve-final-manual-runtime-run" in payload["missing_confirmations"]
    assert "--i-confirm-post-trade-evidence" in payload["missing_confirmations"]
    assert payload["order_placement_performed"] is False


def test_script_execute_flag_with_all_confirmations_returns_not_implemented_status():
    args = [
        "--execute-demo-order",
        "--i-approve-final-manual-runtime-run",
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
    assert (
        payload["script_status"]
        == "FINAL_OWNER_RUNTIME_RUN_READY_BUT_BROKER_CALL_NOT_IMPLEMENTED_IN_THIS_PR"
    )
    assert (
        payload["decision"]["status"]
        == OWNER_RUN_READY_FOR_EXPLICIT_MANUAL_COMMAND
    )
    assert payload["order_placement_performed"] is False
    assert payload["broker_network_call_performed"] is False
