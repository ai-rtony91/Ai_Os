from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_owner_run_actual_one_order_command_v1 import (  # noqa: E402
    OWNER_COMMAND_BLOCKED_BROKER_CALL_NOT_READY,
    OWNER_COMMAND_BLOCKED_CONTEXT,
    OWNER_COMMAND_BLOCKED_MISSING_BROKER_CALL_RESULT,
    OWNER_COMMAND_BLOCKED_OWNER_APPROVAL,
    OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND,
    evaluate_oanda_demo_owner_run_actual_one_order_command_v1,
)
from scripts.forex_delivery.run_oanda_demo_owner_run_actual_one_order_command_v1 import (  # noqa: E402
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


def broker_call_result(**overrides):
    result = {
        "status": "BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED",
        "network_call_performed": False,
        "order_placement_performed": False,
        "execution_attempt": {
            "network_call_performed": False,
            "order_placement_performed": False,
        },
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    result.update(overrides)
    return result


def owner_approval(**overrides):
    approval = {
        "owner_approved_actual_one_order_command": True,
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
        "owner_confirmed_runtime_credentials_external": True,
    }
    approval.update(overrides)
    return approval


def command_context(**overrides):
    context = {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_endpoint_only": True,
        "live_endpoint_absent": True,
        "runtime_token_external": True,
        "runtime_account_id_external": True,
        "credential_persistence_detected": False,
        "account_id_persistence_detected": False,
        "one_order_only": True,
        "max_order_attempts": 1,
        "order_already_attempted": False,
        "kill_switch_ready": True,
        "daily_stop_ready": True,
        "max_loss_gate_ready": True,
        "pre_trade_evidence_ready": True,
        "post_trade_evidence_plan_ready": True,
    }
    context.update(overrides)
    return context


def evaluate(**overrides):
    payload = {
        "broker_call_result": broker_call_result(),
        "owner_command_approval": owner_approval(),
        "command_context": command_context(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_owner_run_actual_one_order_command_v1(**payload)


def run_script(args):
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def command_text(result):
    return result["final_owner_command"]["command_text"]


def assert_execution_authority_false(result):
    assert result["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_default_blocks_missing_broker_call_result():
    result = evaluate_oanda_demo_owner_run_actual_one_order_command_v1()
    assert result["status"] == OWNER_COMMAND_BLOCKED_MISSING_BROKER_CALL_RESULT
    assert "missing_broker_call_result" in result["blockers"]
    assert result["final_owner_command"]["ready"] is False
    assert_execution_authority_false(result)


def test_broker_call_not_ready_blocks():
    result = evaluate(broker_call_result=broker_call_result(status="BROKER_BLOCKED"))
    assert result["status"] == OWNER_COMMAND_BLOCKED_BROKER_CALL_NOT_READY
    assert "broker_call_status_not_ready_for_owner_command" in result["blockers"]


def test_missing_owner_approval_blocks():
    result = evaluate(owner_command_approval=None)
    assert result["status"] == OWNER_COMMAND_BLOCKED_OWNER_APPROVAL
    assert "missing_owner_command_approval" in result["blockers"]


def test_missing_command_context_blocks():
    result = evaluate(command_context=None)
    assert result["status"] == OWNER_COMMAND_BLOCKED_CONTEXT
    assert "missing_command_context" in result["blockers"]


def test_live_endpoint_not_absent_blocks():
    result = evaluate(command_context=command_context(live_endpoint_absent=False))
    assert result["status"] == OWNER_COMMAND_BLOCKED_CONTEXT
    assert "command_context_live_endpoint_absent_required" in result["blockers"]


def test_runtime_token_not_external_blocks():
    result = evaluate(command_context=command_context(runtime_token_external=False))
    assert result["status"] == OWNER_COMMAND_BLOCKED_CONTEXT
    assert "command_context_runtime_token_external_required" in result["blockers"]


def test_runtime_account_id_not_external_blocks():
    result = evaluate(
        command_context=command_context(runtime_account_id_external=False)
    )
    assert result["status"] == OWNER_COMMAND_BLOCKED_CONTEXT
    assert "command_context_runtime_account_id_external_required" in result[
        "blockers"
    ]


def test_credential_persistence_blocks():
    result = evaluate(
        command_context=command_context(credential_persistence_detected=True)
    )
    assert result["status"] == OWNER_COMMAND_BLOCKED_CONTEXT
    assert "command_context_credential_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_account_id_persistence_blocks():
    result = evaluate(
        command_context=command_context(account_id_persistence_detected=True)
    )
    assert result["status"] == OWNER_COMMAND_BLOCKED_CONTEXT
    assert "command_context_account_id_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_order_already_attempted_blocks():
    result = evaluate(command_context=command_context(order_already_attempted=True))
    assert result["status"] == OWNER_COMMAND_BLOCKED_CONTEXT
    assert "command_context_order_already_attempted_must_be_false" in result[
        "blockers"
    ]


def test_missing_stop_loss_owner_confirmation_blocks():
    result = evaluate(
        owner_command_approval=owner_approval(owner_confirmed_stop_loss=False)
    )
    assert result["status"] == OWNER_COMMAND_BLOCKED_OWNER_APPROVAL
    assert "owner_confirmed_stop_loss_required" in result["blockers"]


def test_missing_take_profit_owner_confirmation_blocks():
    result = evaluate(
        owner_command_approval=owner_approval(owner_confirmed_take_profit=False)
    )
    assert result["status"] == OWNER_COMMAND_BLOCKED_OWNER_APPROVAL
    assert "owner_confirmed_take_profit_required" in result["blockers"]


def test_missing_post_trade_evidence_confirmation_blocks():
    result = evaluate(
        owner_command_approval=owner_approval(
            owner_confirmed_post_trade_evidence_required=False
        )
    )
    assert result["status"] == OWNER_COMMAND_BLOCKED_OWNER_APPROVAL
    assert "owner_confirmed_post_trade_evidence_required_required" in result[
        "blockers"
    ]


def test_valid_command_returns_ready():
    result = evaluate()
    assert result["status"] == OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND
    assert result["final_owner_command"]["ready"] is True


def test_final_command_contains_execute_demo_order():
    assert "--execute-demo-order" in command_text(evaluate())


def test_final_command_contains_actual_broker_call_confirmation():
    assert "--i-approve-actual-oanda-demo-broker-call" in command_text(evaluate())


def test_final_command_contains_no_second_order_confirmation():
    assert "--i-confirm-no-second-order" in command_text(evaluate())


def test_final_command_uses_access_token_placeholder_and_not_real_token():
    text = command_text(evaluate())
    assert "OANDA_DEMO_ACCESS_TOKEN" in text
    assert "REAL_TOKEN" not in text
    assert "sk-" not in text


def test_final_command_uses_account_id_placeholder_and_not_real_account_id():
    text = command_text(evaluate())
    assert "OANDA_DEMO_ACCOUNT_ID" in text
    assert "REAL_ACCOUNT" not in text


def test_final_command_contains_one_order_only_warning():
    assert "ONE ORDER ONLY" in command_text(evaluate())


def test_all_execution_authority_fields_remain_false():
    assert_execution_authority_false(evaluate())


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)


def test_script_dry_run_prints_json_and_performs_no_broker_action():
    code, payload = run_script([])
    assert code == 0
    assert payload["script_status"] == "OWNER_COMMAND_DRY_RUN_PACKAGE"
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["account_id_read_performed"] is False


def test_script_print_command_prints_command_template_only():
    code, payload = run_script(["--print-command"])
    assert code == 0
    assert payload["script_status"] == "OWNER_COMMAND_TEMPLATE_ONLY"
    assert "--execute-demo-order" in payload["final_owner_command"]["command_text"]
    assert "decision" not in payload
    assert payload["order_placement_performed"] is False


def test_script_print_checklist_prints_checklist_only():
    code, payload = run_script(["--print-checklist"])
    assert code == 0
    assert payload["script_status"] == "OWNER_COMMAND_CHECKLIST_ONLY"
    assert "manual_pre_run_checklist" in payload
    assert "manual_post_run_evidence_checklist" in payload
    assert "final_owner_command" not in payload
    assert payload["order_placement_performed"] is False
