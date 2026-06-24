from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_first_trade_owner_manual_execution_window_v1 import (  # noqa: E402
    WINDOW_BLOCKED_CONTEXT,
    WINDOW_BLOCKED_GO_NOGO_NOT_READY,
    WINDOW_BLOCKED_MISSING_GO_NOGO,
    WINDOW_BLOCKED_OWNER_COMMAND,
    WINDOW_BLOCKED_OWNER_CONFIRMATION,
    WINDOW_READY_FOR_OWNER_MANUAL_DEMO_EXECUTION,
    evaluate_oanda_demo_first_trade_owner_manual_execution_window_v1,
)
from scripts.forex_delivery.run_oanda_demo_first_trade_owner_manual_execution_window_v1 import (  # noqa: E402
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


def go_nogo(**overrides):
    payload = {
        "status": "RUNBOOK_GO_READY_FOR_OWNER_MANUAL_DEMO_ATTEMPT",
        "go_nogo": "GO",
        "next_safe_action": "owner_may_run_first_demo_order_command_once",
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
        "execution_window_minutes": 30,
        "market_open_or_owner_override": True,
    }
    payload.update(overrides)
    return payload


def owner_confirmation(**overrides):
    payload = {
        "owner_confirmed_execution_window_reviewed": True,
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
        "go_nogo_result": go_nogo(),
        "owner_command_result": owner_command(),
        "execution_window_context": context(),
        "owner_execution_window_confirmation": owner_confirmation(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_first_trade_owner_manual_execution_window_v1(**payload)


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


def test_default_blocks_missing_go_nogo():
    result = evaluate_oanda_demo_first_trade_owner_manual_execution_window_v1()
    assert result["status"] == WINDOW_BLOCKED_MISSING_GO_NOGO
    assert "missing_go_nogo_result" in result["blockers"]


def test_go_nogo_not_ready_blocks():
    result = evaluate(go_nogo_result=go_nogo(go_nogo="NOGO"))
    assert result["status"] == WINDOW_BLOCKED_GO_NOGO_NOT_READY
    assert "go_nogo_decision_must_be_go" in result["blockers"]


def test_missing_owner_command_blocks():
    result = evaluate(owner_command_result=None)
    assert result["status"] == WINDOW_BLOCKED_OWNER_COMMAND
    assert "missing_owner_command_result" in result["blockers"]


def test_owner_command_containing_token_account_key_rejects():
    result = evaluate(
        owner_command_result=owner_command(
            final_owner_command={
                "command_type": "powershell",
                "runtime_token": "<not_allowed>",
                "account_id": "<not_allowed>",
            }
        )
    )
    assert result["status"] == WINDOW_BLOCKED_OWNER_COMMAND
    assert "owner_command_forbidden_token_field" in result["blockers"]
    assert "owner_command_forbidden_account_id_field" in result["blockers"]


def test_missing_execution_context_blocks():
    result = evaluate(execution_window_context=None)
    assert result["status"] == WINDOW_BLOCKED_CONTEXT
    assert "missing_execution_window_context" in result["blockers"]


def test_live_endpoint_present_blocks():
    result = evaluate(execution_window_context=context(live_endpoint_absent=False))
    assert result["status"] == WINDOW_BLOCKED_CONTEXT
    assert "execution_window_context_live_endpoint_absent_required" in result[
        "blockers"
    ]


def test_runtime_token_not_external_blocks():
    result = evaluate(execution_window_context=context(runtime_token_external=False))
    assert result["status"] == WINDOW_BLOCKED_CONTEXT
    assert "execution_window_context_runtime_token_external_required" in result[
        "blockers"
    ]


def test_runtime_account_id_not_external_blocks():
    result = evaluate(
        execution_window_context=context(runtime_account_id_external=False)
    )
    assert result["status"] == WINDOW_BLOCKED_CONTEXT
    assert "execution_window_context_runtime_account_id_external_required" in result[
        "blockers"
    ]


def test_runtime_credentials_unavailable_to_owner_blocks():
    result = evaluate(
        execution_window_context=context(
            runtime_credentials_available_to_owner=False
        )
    )
    assert result["status"] == WINDOW_BLOCKED_CONTEXT
    assert (
        "execution_window_context_runtime_credentials_available_to_owner_required"
        in result["blockers"]
    )


def test_credential_persistence_blocks():
    result = evaluate(
        execution_window_context=context(credential_persistence_detected=True)
    )
    assert result["status"] == WINDOW_BLOCKED_CONTEXT
    assert "execution_window_context_credential_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_account_id_persistence_blocks():
    result = evaluate(
        execution_window_context=context(account_id_persistence_detected=True)
    )
    assert result["status"] == WINDOW_BLOCKED_CONTEXT
    assert "execution_window_context_account_id_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_order_already_attempted_blocks():
    result = evaluate(execution_window_context=context(order_already_attempted=True))
    assert result["status"] == WINDOW_BLOCKED_CONTEXT
    assert "execution_window_context_order_already_attempted_must_be_false" in result[
        "blockers"
    ]


def test_existing_open_orders_blocks():
    result = evaluate(execution_window_context=context(existing_open_orders=1))
    assert result["status"] == WINDOW_BLOCKED_CONTEXT
    assert "execution_window_context_existing_open_orders_must_be_zero" in result[
        "blockers"
    ]


def test_existing_pending_orders_blocks():
    result = evaluate(execution_window_context=context(existing_pending_orders=1))
    assert result["status"] == WINDOW_BLOCKED_CONTEXT
    assert "execution_window_context_existing_pending_orders_must_be_zero" in result[
        "blockers"
    ]


def test_owner_not_present_blocks():
    result = evaluate(
        execution_window_context=context(owner_present_for_manual_run=False)
    )
    assert result["status"] == WINDOW_BLOCKED_CONTEXT
    assert "execution_window_context_owner_present_for_manual_run_required" in result[
        "blockers"
    ]


def test_kill_switch_missing_blocks():
    result = evaluate(execution_window_context=context(kill_switch_ready=False))
    assert result["status"] == WINDOW_BLOCKED_CONTEXT
    assert "execution_window_context_kill_switch_ready_required" in result["blockers"]


def test_stop_loss_missing_blocks():
    result = evaluate(execution_window_context=context(stop_loss_ready=False))
    assert result["status"] == WINDOW_BLOCKED_CONTEXT
    assert "execution_window_context_stop_loss_ready_required" in result["blockers"]


def test_take_profit_missing_blocks():
    result = evaluate(execution_window_context=context(take_profit_ready=False))
    assert result["status"] == WINDOW_BLOCKED_CONTEXT
    assert "execution_window_context_take_profit_ready_required" in result["blockers"]


def test_market_closed_without_owner_override_blocks():
    result = evaluate(
        execution_window_context=context(market_open_or_owner_override=False)
    )
    assert result["status"] == WINDOW_BLOCKED_CONTEXT
    assert "execution_window_context_market_open_or_owner_override_required" in result[
        "blockers"
    ]


def test_missing_owner_confirmation_blocks():
    result = evaluate(owner_execution_window_confirmation=None)
    assert result["status"] == WINDOW_BLOCKED_OWNER_CONFIRMATION
    assert "missing_owner_execution_window_confirmation" in result["blockers"]


def test_missing_runtime_external_confirmation_blocks():
    result = evaluate(
        owner_execution_window_confirmation=owner_confirmation(
            owner_confirmed_runtime_credentials_external=False
        )
    )
    assert result["status"] == WINDOW_BLOCKED_OWNER_CONFIRMATION
    assert "owner_confirmed_runtime_credentials_external_required" in result[
        "blockers"
    ]


def test_valid_full_packet_returns_window_ready():
    result = evaluate()
    assert result["status"] == WINDOW_READY_FOR_OWNER_MANUAL_DEMO_EXECUTION
    assert result["next_safe_action"] == (
        "owner_may_execute_one_demo_order_inside_window"
    )


def test_execution_window_package_ready_true():
    assert evaluate()["execution_window_package"]["ready"] is True


def test_execution_window_max_order_attempts_is_one():
    assert evaluate()["execution_window_package"]["max_order_attempts"] == 1


def test_final_pre_execution_checklist_contains_core_controls():
    checklist = " ".join(evaluate()["final_pre_execution_checklist"]["items"])
    assert "stop_loss" in checklist
    assert "take_profit" in checklist
    assert "kill_switch" in checklist
    assert "one_order_only" in checklist


def test_final_post_execution_checklist_contains_required_evidence():
    checklist = " ".join(evaluate()["final_post_execution_evidence_path"]["items"])
    assert "order_reference" in checklist
    assert "fill_or_rejection" in checklist
    assert "sl_tp_attachment" in checklist
    assert "pl_" in checklist
    assert "balance_nav" in checklist
    assert "timestamp" in checklist


def test_all_execution_authority_fields_remain_false():
    assert_execution_authority_false(evaluate())


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)


def test_script_dry_run_prints_json_and_performs_no_broker_action():
    code, payload = run_script_json([])
    assert code == 0
    assert payload["script_status"] == "FIRST_TRADE_EXECUTION_WINDOW_DRY_RUN_PACKAGE"
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["account_id_read_performed"] is False


def test_script_print_window_emits_window_text_and_json():
    code, output = run_script(["--print-window"])
    assert code == 0
    assert "OWNER MANUAL EXECUTION WINDOW" in output
    payload = json.loads(output.split("JSON:\n", 1)[1])
    assert payload["decision"]["execution_window_package"]["ready"] is True


def test_script_print_final_checklist_emits_checklist_text():
    code, output = run_script(["--print-final-checklist"])
    assert code == 0
    assert "FINAL PRE-EXECUTION CHECKLIST:" in output
    assert "FINAL POST-EXECUTION EVIDENCE PATH:" in output
    assert "confirm_stop_loss_ready" in output


def test_script_print_owner_command_reminder_emits_placeholder_only_reminder():
    code, output = run_script(["--print-owner-command-reminder"])
    assert code == 0
    assert "<OANDA_DEMO_ACCESS_VALUE_RUNTIME_ONLY>" in output
    assert "<OANDA_DEMO_ACCOUNT_RUNTIME_ONLY>" in output
    assert "SECRET" not in output
    assert "Codex must not execute this command." in output
