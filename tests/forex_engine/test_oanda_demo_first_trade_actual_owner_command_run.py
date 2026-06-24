from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_first_trade_actual_owner_command_run import (  # noqa: E402
    ACTUAL_RUN_BLOCKED_BROKER_CALL,
    ACTUAL_RUN_BLOCKED_CONTEXT,
    ACTUAL_RUN_BLOCKED_EXECUTION_WINDOW_NOT_READY,
    ACTUAL_RUN_BLOCKED_MISSING_EXECUTION_WINDOW,
    ACTUAL_RUN_BLOCKED_OWNER_COMMAND,
    ACTUAL_RUN_BLOCKED_OWNER_CONFIRMATION,
    ACTUAL_RUN_READY_FOR_OWNER_MANUAL_COMMAND,
    REQUIRED_CONFIRMATION_FLAGS,
    evaluate_oanda_demo_first_trade_actual_owner_command_run,
)
from scripts.forex_delivery.run_oanda_demo_first_trade_actual_owner_command_run import (  # noqa: E402
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


def execution_window(**overrides):
    payload = {
        "status": "WINDOW_READY_FOR_OWNER_MANUAL_DEMO_EXECUTION",
        "execution_window_package": {
            "ready": True,
            "one_order_only": True,
            "max_order_attempts": 1,
            "actual_order_requires_owner_manual_command": True,
        },
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    payload.update(overrides)
    return payload


def owner_command(**overrides):
    payload = {
        "status": "OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND",
        "final_owner_command": {
            "command_type": "powershell",
            "script_path": "scripts/forex_delivery/run_owner_command.py",
            "command_text": "OWNER_RUNTIME_COMMAND_AVAILABLE_OUTSIDE_CODEX",
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


def owner_confirmation(**overrides):
    payload = {
        "owner_confirmed_actual_command_reviewed": True,
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
        "owner_confirmed_ready_to_press_manual_demo_button": True,
    }
    payload.update(overrides)
    return payload


def evaluate(**overrides):
    payload = {
        "execution_window_result": execution_window(),
        "owner_command_result": owner_command(),
        "broker_call_result": broker_call(),
        "actual_run_context": context(),
        "owner_actual_run_confirmation": owner_confirmation(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_first_trade_actual_owner_command_run(**payload)


def run_script(args):
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, stream.getvalue()


def run_script_json(args):
    code, output = run_script(args)
    return code, json.loads(output)


def assert_execution_authority_false(result):
    assert result["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_default_blocks_missing_execution_window():
    result = evaluate_oanda_demo_first_trade_actual_owner_command_run()
    assert result["status"] == ACTUAL_RUN_BLOCKED_MISSING_EXECUTION_WINDOW
    assert "missing_execution_window_result" in result["blockers"]


def test_execution_window_not_ready_blocks():
    result = evaluate(
        execution_window_result=execution_window(
            status="WINDOW_BLOCKED_CONTEXT",
            execution_window_package={
                "ready": False,
                "one_order_only": True,
                "max_order_attempts": 1,
                "actual_order_requires_owner_manual_command": True,
            },
        )
    )
    assert result["status"] == ACTUAL_RUN_BLOCKED_EXECUTION_WINDOW_NOT_READY
    assert "execution_window_status_not_ready" in result["blockers"]


def test_missing_owner_command_blocks():
    result = evaluate(owner_command_result=None)
    assert result["status"] == ACTUAL_RUN_BLOCKED_OWNER_COMMAND
    assert "missing_owner_command_result" in result["blockers"]


def test_owner_command_containing_token_account_key_rejects():
    result = evaluate(
        owner_command_result=owner_command(
            final_owner_command={
                "command_type": "powershell",
                "token": "<not_allowed>",
                "account_id": "<not_allowed>",
            }
        )
    )
    assert result["status"] == ACTUAL_RUN_BLOCKED_OWNER_COMMAND
    assert "owner_command_forbidden_token_field" in result["blockers"]
    assert "owner_command_forbidden_account_id_field" in result["blockers"]


def test_missing_broker_call_blocks():
    result = evaluate(broker_call_result=None)
    assert result["status"] == ACTUAL_RUN_BLOCKED_BROKER_CALL
    assert "missing_broker_call_result" in result["blockers"]


def test_broker_call_already_placed_order_blocks():
    result = evaluate(broker_call_result=broker_call(order_placement_performed=True))
    assert result["status"] == ACTUAL_RUN_BLOCKED_BROKER_CALL
    assert "broker_call_order_placement_performed_must_be_false" in result["blockers"]


def test_missing_actual_run_context_blocks():
    result = evaluate(actual_run_context=None)
    assert result["status"] == ACTUAL_RUN_BLOCKED_CONTEXT
    assert "missing_actual_run_context" in result["blockers"]


def test_live_endpoint_present_blocks():
    result = evaluate(actual_run_context=context(live_endpoint_absent=False))
    assert result["status"] == ACTUAL_RUN_BLOCKED_CONTEXT
    assert "actual_run_context_live_endpoint_absent_required" in result["blockers"]


def test_runtime_token_not_external_blocks():
    result = evaluate(actual_run_context=context(runtime_token_external=False))
    assert result["status"] == ACTUAL_RUN_BLOCKED_CONTEXT
    assert "actual_run_context_runtime_token_external_required" in result["blockers"]


def test_runtime_account_id_not_external_blocks():
    result = evaluate(actual_run_context=context(runtime_account_id_external=False))
    assert result["status"] == ACTUAL_RUN_BLOCKED_CONTEXT
    assert "actual_run_context_runtime_account_id_external_required" in result[
        "blockers"
    ]


def test_runtime_credentials_unavailable_to_owner_blocks():
    result = evaluate(
        actual_run_context=context(runtime_credentials_available_to_owner=False)
    )
    assert result["status"] == ACTUAL_RUN_BLOCKED_CONTEXT
    assert "actual_run_context_runtime_credentials_available_to_owner_required" in result[
        "blockers"
    ]


def test_credential_persistence_blocks():
    result = evaluate(actual_run_context=context(credential_persistence_detected=True))
    assert result["status"] == ACTUAL_RUN_BLOCKED_CONTEXT
    assert "actual_run_context_credential_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_account_id_persistence_blocks():
    result = evaluate(actual_run_context=context(account_id_persistence_detected=True))
    assert result["status"] == ACTUAL_RUN_BLOCKED_CONTEXT
    assert "actual_run_context_account_id_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_order_already_attempted_blocks():
    result = evaluate(actual_run_context=context(order_already_attempted=True))
    assert result["status"] == ACTUAL_RUN_BLOCKED_CONTEXT
    assert "actual_run_context_order_already_attempted_must_be_false" in result[
        "blockers"
    ]


def test_existing_open_orders_blocks():
    result = evaluate(actual_run_context=context(existing_open_orders=1))
    assert result["status"] == ACTUAL_RUN_BLOCKED_CONTEXT
    assert "actual_run_context_existing_open_orders_must_be_zero" in result[
        "blockers"
    ]


def test_existing_pending_orders_blocks():
    result = evaluate(actual_run_context=context(existing_pending_orders=1))
    assert result["status"] == ACTUAL_RUN_BLOCKED_CONTEXT
    assert "actual_run_context_existing_pending_orders_must_be_zero" in result[
        "blockers"
    ]


def test_owner_not_present_blocks():
    result = evaluate(actual_run_context=context(owner_present_for_manual_run=False))
    assert result["status"] == ACTUAL_RUN_BLOCKED_CONTEXT
    assert "actual_run_context_owner_present_for_manual_run_required" in result[
        "blockers"
    ]


def test_kill_switch_missing_blocks():
    result = evaluate(actual_run_context=context(kill_switch_ready=False))
    assert result["status"] == ACTUAL_RUN_BLOCKED_CONTEXT
    assert "actual_run_context_kill_switch_ready_required" in result["blockers"]


def test_execution_window_closed_blocks():
    result = evaluate(actual_run_context=context(execution_window_open=False))
    assert result["status"] == ACTUAL_RUN_BLOCKED_CONTEXT
    assert "actual_run_context_execution_window_open_required" in result["blockers"]


def test_missing_owner_confirmation_blocks():
    result = evaluate(owner_actual_run_confirmation=None)
    assert result["status"] == ACTUAL_RUN_BLOCKED_OWNER_CONFIRMATION
    assert "missing_owner_actual_run_confirmation" in result["blockers"]


def test_missing_ready_to_press_confirmation_blocks():
    result = evaluate(
        owner_actual_run_confirmation=owner_confirmation(
            owner_confirmed_ready_to_press_manual_demo_button=False
        )
    )
    assert result["status"] == ACTUAL_RUN_BLOCKED_OWNER_CONFIRMATION
    assert "owner_confirmed_ready_to_press_manual_demo_button_required" in result[
        "blockers"
    ]


def test_valid_full_packet_returns_actual_run_ready():
    result = evaluate()
    assert result["status"] == ACTUAL_RUN_READY_FOR_OWNER_MANUAL_COMMAND
    assert result["next_safe_action"] == (
        "owner_can_run_exact_manual_demo_order_command_once"
    )


def test_final_command_package_ready_true():
    assert evaluate()["final_manual_command_package"]["ready"] is True


def test_final_command_package_max_order_attempts_is_one():
    assert evaluate()["final_manual_command_package"]["max_order_attempts"] == 1


def test_final_command_package_owner_must_run_manually_true():
    assert evaluate()["final_manual_command_package"]["owner_must_run_manually"] is True


def test_final_manual_command_contains_execute_demo_order():
    command = evaluate()["final_manual_command_package"]["command_text"]
    assert "--execute-demo-order" in command


def test_final_manual_command_contains_required_confirmation_flags():
    command = evaluate()["final_manual_command_package"]["command_text"]
    for flag in REQUIRED_CONFIRMATION_FLAGS:
        assert flag in command


def test_final_manual_command_contains_runtime_placeholder_token_account_only():
    command = evaluate()["final_manual_command_package"]["command_text"]
    assert "<OANDA_DEMO_ACCESS_TOKEN_RUNTIME_ONLY>" in command
    assert "<OANDA_DEMO_ACCOUNT_ID_RUNTIME_ONLY>" in command
    assert "SECRET" not in command
    assert "LIVE" not in command


def test_all_execution_authority_fields_remain_false():
    assert_execution_authority_false(evaluate())


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)


def test_script_dry_run_prints_json_and_performs_no_broker_action():
    code, payload = run_script_json([])
    assert code == 0
    assert payload["script_status"] == "ACTUAL_OWNER_COMMAND_DRY_RUN_PACKAGE"
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["account_id_read_performed"] is False


def test_script_print_command_emits_placeholder_only_command():
    code, output = run_script(["--print-command"])
    assert code == 0
    assert "scripts/forex_delivery/run_oanda_demo_broker_call_one_order_manual_run_v1.py" in output
    assert "<OANDA_DEMO_ACCESS_TOKEN_RUNTIME_ONLY>" in output
    assert "<OANDA_DEMO_ACCOUNT_ID_RUNTIME_ONLY>" in output
    assert "--execute-demo-order" in output
    assert "SECRET" not in output


def test_script_print_final_warning_emits_risk_warning_and_evidence_checklist():
    code, output = run_script(["--print-final-warning"])
    assert code == 0
    assert "FINAL ONE-ORDER RISK WARNING" in output
    assert "EVIDENCE CHECKLIST:" in output
    assert "capture_sanitized_order_reference" in output
