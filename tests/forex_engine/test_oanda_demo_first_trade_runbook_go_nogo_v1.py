from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_first_trade_runbook_go_nogo_v1 import (  # noqa: E402
    RUNBOOK_BLOCKED_BROKER_CALL_READINESS,
    RUNBOOK_BLOCKED_BUCKET_READINESS,
    RUNBOOK_BLOCKED_MISSING_OWNER_COMMAND,
    RUNBOOK_BLOCKED_OWNER_COMMAND_NOT_READY,
    RUNBOOK_BLOCKED_OWNER_CONFIRMATION,
    RUNBOOK_BLOCKED_RUNTIME_CONTEXT,
    RUNBOOK_GO_READY_FOR_OWNER_MANUAL_DEMO_ATTEMPT,
    evaluate_oanda_demo_first_trade_runbook_go_nogo_v1,
)
from scripts.forex_delivery.run_oanda_demo_first_trade_runbook_go_nogo_v1 import (  # noqa: E402
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
        "live_order_allowed": False,
        "autonomous_order_allowed": False,
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    payload.update(overrides)
    return payload


def bucket_result(**overrides):
    payload = {
        "status": "BUCKET_UPDATE_READY",
        "recommendation": {
            "next_trade_requires_owner_approval": True,
            "live_allocation_allowed": False,
            "autonomous_compounding_allowed": False,
        },
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    payload.update(overrides)
    return payload


def runtime_context(**overrides):
    payload = {
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
        "existing_open_orders": 0,
        "existing_pending_orders": 0,
        "kill_switch_ready": True,
        "daily_stop_ready": True,
        "max_loss_gate_ready": True,
        "stop_loss_ready": True,
        "take_profit_ready": True,
        "pre_trade_evidence_ready": True,
        "post_trade_evidence_plan_ready": True,
        "owner_present_for_manual_run": True,
    }
    payload.update(overrides)
    return payload


def owner_confirmation(**overrides):
    payload = {
        "owner_confirmed_go_nogo_reviewed": True,
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
    }
    payload.update(overrides)
    return payload


def evaluate(**overrides):
    payload = {
        "owner_command_result": owner_command(),
        "broker_call_readiness_result": broker_call(),
        "result_bucket_readiness_result": bucket_result(),
        "runtime_readiness_context": runtime_context(),
        "owner_go_nogo_confirmation": owner_confirmation(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_first_trade_runbook_go_nogo_v1(**payload)


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


def test_default_blocks_missing_owner_command():
    result = evaluate_oanda_demo_first_trade_runbook_go_nogo_v1()
    assert result["status"] == RUNBOOK_BLOCKED_MISSING_OWNER_COMMAND
    assert result["go_nogo"] == "NOGO"
    assert "missing_owner_command_result" in result["blockers"]


def test_owner_command_not_ready_blocks():
    result = evaluate(owner_command_result=owner_command(status="OWNER_NOT_READY"))
    assert result["status"] == RUNBOOK_BLOCKED_OWNER_COMMAND_NOT_READY
    assert result["go_nogo"] == "NOGO"


def test_missing_broker_call_readiness_blocks():
    result = evaluate(broker_call_readiness_result=None)
    assert result["status"] == RUNBOOK_BLOCKED_BROKER_CALL_READINESS
    assert "missing_broker_call_readiness_result" in result["blockers"]


def test_broker_call_with_live_allowed_blocks():
    result = evaluate(broker_call_readiness_result=broker_call(live_order_allowed=True))
    assert result["status"] == RUNBOOK_BLOCKED_BROKER_CALL_READINESS
    assert "broker_call_live_order_allowed_must_not_be_true" in result["blockers"]


def test_missing_bucket_readiness_blocks():
    result = evaluate(result_bucket_readiness_result=None)
    assert result["status"] == RUNBOOK_BLOCKED_BUCKET_READINESS
    assert "missing_result_bucket_readiness_result" in result["blockers"]


def test_bucket_live_allocation_allowed_blocks():
    result = evaluate(
        result_bucket_readiness_result=bucket_result(
            recommendation={
                "next_trade_requires_owner_approval": True,
                "live_allocation_allowed": True,
                "autonomous_compounding_allowed": False,
            }
        )
    )
    assert result["status"] == RUNBOOK_BLOCKED_BUCKET_READINESS
    assert "result_bucket_live_allocation_must_be_false" in result["blockers"]


def test_missing_runtime_context_blocks():
    result = evaluate(runtime_readiness_context=None)
    assert result["status"] == RUNBOOK_BLOCKED_RUNTIME_CONTEXT
    assert "missing_runtime_readiness_context" in result["blockers"]


def test_live_endpoint_present_blocks():
    result = evaluate(runtime_readiness_context=runtime_context(live_endpoint_absent=False))
    assert result["status"] == RUNBOOK_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_live_endpoint_absent_required" in result["blockers"]


def test_runtime_token_not_external_blocks():
    result = evaluate(
        runtime_readiness_context=runtime_context(runtime_token_external=False)
    )
    assert result["status"] == RUNBOOK_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_runtime_token_external_required" in result["blockers"]


def test_runtime_account_id_not_external_blocks():
    result = evaluate(
        runtime_readiness_context=runtime_context(runtime_account_id_external=False)
    )
    assert result["status"] == RUNBOOK_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_runtime_account_id_external_required" in result["blockers"]


def test_credential_persistence_blocks():
    result = evaluate(
        runtime_readiness_context=runtime_context(
            credential_persistence_detected=True
        )
    )
    assert result["status"] == RUNBOOK_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_credential_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_account_id_persistence_blocks():
    result = evaluate(
        runtime_readiness_context=runtime_context(account_id_persistence_detected=True)
    )
    assert result["status"] == RUNBOOK_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_account_id_persistence_detected_must_be_false" in result[
        "blockers"
    ]


def test_existing_open_orders_blocks():
    result = evaluate(runtime_readiness_context=runtime_context(existing_open_orders=1))
    assert result["status"] == RUNBOOK_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_existing_open_orders_must_be_zero" in result["blockers"]


def test_existing_pending_orders_blocks():
    result = evaluate(
        runtime_readiness_context=runtime_context(existing_pending_orders=1)
    )
    assert result["status"] == RUNBOOK_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_existing_pending_orders_must_be_zero" in result["blockers"]


def test_order_already_attempted_blocks():
    result = evaluate(
        runtime_readiness_context=runtime_context(order_already_attempted=True)
    )
    assert result["status"] == RUNBOOK_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_order_already_attempted_must_be_false" in result[
        "blockers"
    ]


def test_missing_owner_confirmation_blocks():
    result = evaluate(owner_go_nogo_confirmation=None)
    assert result["status"] == RUNBOOK_BLOCKED_OWNER_CONFIRMATION
    assert "missing_owner_go_nogo_confirmation" in result["blockers"]


def test_missing_stop_loss_confirmation_blocks():
    result = evaluate(
        owner_go_nogo_confirmation=owner_confirmation(
            owner_confirmed_stop_loss=False
        )
    )
    assert result["status"] == RUNBOOK_BLOCKED_OWNER_CONFIRMATION
    assert "owner_confirmed_stop_loss_required" in result["blockers"]


def test_missing_take_profit_confirmation_blocks():
    result = evaluate(
        owner_go_nogo_confirmation=owner_confirmation(
            owner_confirmed_take_profit=False
        )
    )
    assert result["status"] == RUNBOOK_BLOCKED_OWNER_CONFIRMATION
    assert "owner_confirmed_take_profit_required" in result["blockers"]


def test_missing_kill_switch_confirmation_blocks():
    result = evaluate(
        owner_go_nogo_confirmation=owner_confirmation(
            owner_confirmed_kill_switch_ready=False
        )
    )
    assert result["status"] == RUNBOOK_BLOCKED_OWNER_CONFIRMATION
    assert "owner_confirmed_kill_switch_ready_required" in result["blockers"]


def test_valid_full_packet_returns_go():
    result = evaluate()
    assert result["status"] == RUNBOOK_GO_READY_FOR_OWNER_MANUAL_DEMO_ATTEMPT
    assert result["go_nogo"] == "GO"
    assert result["next_safe_action"] == "owner_may_run_first_demo_order_command_once"


def test_any_blocker_returns_nogo():
    result = evaluate(runtime_readiness_context=runtime_context(stop_loss_ready=False))
    assert result["go_nogo"] == "NOGO"
    assert result["next_safe_action"] == "repair_blocker_before_owner_manual_demo_attempt"


def test_pre_run_checklist_includes_core_order_controls():
    result = evaluate()
    checklist = " ".join(result["pre_run_checklist"]["items"])
    assert "stop_loss" in checklist
    assert "take_profit" in checklist
    assert "one_order_only" in checklist
    assert "no_second_order" in checklist


def test_post_run_checklist_includes_required_evidence_fields():
    result = evaluate()
    checklist = " ".join(result["post_run_evidence_checklist"]["items"])
    assert "order_reference" in checklist
    assert "fill_or_rejection" in checklist
    assert "stop_loss_take_profit_attachment" in checklist
    assert "pl" in checklist
    assert "balance_nav" in checklist
    assert "timestamp" in checklist


def test_kill_switch_plan_is_present():
    result = evaluate()
    assert result["kill_switch_plan"]["ready"] is True
    assert result["kill_switch_plan"]["kill_switch_ready"] is True


def test_risk_controls_are_present():
    result = evaluate()
    assert result["risk_controls"]["ready"] is True
    assert result["risk_controls"]["one_order_only"] is True
    assert result["risk_controls"]["live_order_allowed"] is False


def test_all_execution_authority_fields_remain_false():
    assert_execution_authority_false(evaluate())


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)


def test_script_dry_run_prints_json_and_performs_no_broker_action():
    code, payload = run_script_json([])
    assert code == 0
    assert payload["script_status"] == "FIRST_TRADE_GO_NOGO_DRY_RUN_PACKAGE"
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["account_id_read_performed"] is False


def test_script_print_runbook_emits_checklist_text_and_json():
    code, output = run_script(["--print-runbook"])
    assert code == 0
    assert "PRE-RUN CHECKLIST:" in output
    assert "POST-RUN EVIDENCE CHECKLIST:" in output
    payload = json.loads(output.split("JSON:\n", 1)[1])
    assert payload["decision"]["pre_run_checklist"]["items"]


def test_script_print_go_nogo_template_emits_sanitized_template():
    code, payload = run_script_json(["--print-go-nogo-template"])
    assert code == 0
    assert payload["script_status"] == "FIRST_TRADE_GO_NOGO_TEMPLATE_ONLY"
    rendered = json.dumps(payload, sort_keys=True)
    assert "SECRET" not in rendered
    assert payload["broker_network_call_performed"] is False
    assert payload["template"]["runtime_readiness_context"]["broker"] == "OANDA_DEMO"
