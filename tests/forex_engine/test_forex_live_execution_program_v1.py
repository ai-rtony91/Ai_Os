from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from automation.forex_engine.forex_live_execution_program_v1 import (
    AUTONOMOUS_22H_6D_RUNTIME_REQUIRED,
    BROKER_RUNTIME_READ_ONLY_AUTH_REQUIRED,
    CURRENT_SESSION_WINDOW_DAYS_PER_WEEK,
    CURRENT_SESSION_WINDOW_HOURS,
    EXECUTION_CONTROL_STACK_NOT_READY,
    EXECUTION_CONTROL_STACK_REQUIRED,
    EXECUTION_CONTROLS_INCOMPLETE,
    KILL_SWITCH_BLOCKED,
    LIVE_22H_6D_EXECUTION_PROGRAM_READY,
    LIVE_ORDER_EXECUTION_RUNTIME_REQUIRED,
    LIVE_ORDER_LANE_REQUIRED,
    LIVE_TRADING_APPROVAL_REQUIRED,
    LIVE_TRADING_APPROVAL_REQUIRED as LIVE_TRADING_APPROVAL_REQUIRED_STATUS,
    MICRO_LIVE_EVIDENCE_REVIEW_REQUIRED,
    MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED,
    MICRO_LIVE_ORDER_EXECUTION_READY,
    MICRO_LIVE_ORDER_RUNTIME_REQUIRED,
    OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED,
    PROTECTED_BOUNDARY_VIOLATION,
    SUPERVISED_DEMO_EVIDENCE_REVIEW_REQUIRED,
    SUPERVISED_DEMO_ORDER_EXECUTION_READY,
    SUPERVISED_DEMO_ORDER_RUNTIME_REQUIRED,
    STAGE_AUTONOMOUS_READY,
    STAGE_AUTONOMOUS_RUNTIME,
    STAGE_BROKER_RUNTIME,
    STAGE_EXECUTION_CONTROL_STACK,
    build_default_live_execution_program_input,
    evaluate_live_execution_program,
)
from scripts.forex_delivery.run_forex_live_execution_program_v1 import (
    run_forex_live_execution_program_v1,
    STATE_JSON_PATH,
    REPORT_PATH,
)


def _input(**changes):
    return replace(build_default_live_execution_program_input(), **changes)


def _to_ready_input():
    return _input(
        execution_control_stack_ready=True,
        owner_supervised_demo_approval=True,
        supervised_demo_order_runtime_enabled=True,
        supervised_demo_order_executed=True,
        supervised_demo_evidence_clean=True,
        owner_micro_live_exception_approval=True,
        micro_live_order_runtime_enabled=True,
        micro_live_order_executed=True,
        micro_live_evidence_clean=True,
        owner_live_trading_approval=True,
        live_order_lane_enabled=True,
        live_order_execution_enabled=True,
        autonomous_22h_6d_enabled=True,
    )


def test_default_input_returns_owner_supervised_demo_approval_required():
    result = evaluate_live_execution_program(_input())
    assert result.program_status == OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED
    assert result.current_stage == STAGE_EXECUTION_CONTROL_STACK
    assert result.next_stage == "owner_supervised_demo_approval"


def test_missing_broker_auth_proof_blocks():
    result = evaluate_live_execution_program(_input(broker_runtime_read_only_auth_proven=False))
    assert result.program_status == BROKER_RUNTIME_READ_ONLY_AUTH_REQUIRED
    assert result.current_stage == STAGE_BROKER_RUNTIME
    assert result.next_stage == "broker_runtime_read_only_auth_probe"


def test_missing_execution_control_stack_blocks():
    result = evaluate_live_execution_program(_input(execution_control_stack_landed=False))
    assert result.program_status == EXECUTION_CONTROL_STACK_REQUIRED
    assert result.current_stage == STAGE_EXECUTION_CONTROL_STACK
    assert result.next_stage == "execution_control_stack"


def test_execution_control_stack_not_ready_blocks():
    result = evaluate_live_execution_program(
        _input(
            owner_supervised_demo_approval=True,
            execution_control_stack_ready=False,
        ),
    )
    assert result.program_status == EXECUTION_CONTROL_STACK_NOT_READY
    assert result.current_stage == STAGE_EXECUTION_CONTROL_STACK
    assert result.next_stage == "owner_supervised_demo_approval"


def test_protected_boundary_flags_block():
    result = evaluate_live_execution_program(
        _input(
            execution_control_stack_ready=True,
            owner_supervised_demo_approval=True,
            broker_api_called=True,
        ),
    )
    assert result.program_status == PROTECTED_BOUNDARY_VIOLATION
    assert result.next_stage == "stop_and_owner_review"
    assert result.demo_order_execution is False
    assert result.micro_live_order_execution is False
    assert result.live_order_execution is False
    assert result.money_movement is False
    assert result.autonomous_22h_6d_authorized is False


def test_kill_switch_triggered_blocks():
    result = evaluate_live_execution_program(
        _input(
            owner_supervised_demo_approval=True,
            execution_control_stack_ready=True,
            kill_switch_triggered=True,
        ),
    )
    assert result.program_status == KILL_SWITCH_BLOCKED
    assert result.next_stage == "owner_review_required"


def test_execution_controls_incomplete_blocks():
    result = evaluate_live_execution_program(
        _input(
            owner_supervised_demo_approval=True,
            execution_control_stack_ready=True,
            kill_switch_enabled=False,
        ),
    )
    assert result.program_status == EXECUTION_CONTROLS_INCOMPLETE
    assert result.next_stage == "repair_execution_control_stack"


def test_owner_demo_approval_false_blocks():
    result = evaluate_live_execution_program(
        _input(
            execution_control_stack_ready=True,
            owner_supervised_demo_approval=False,
        ),
    )
    assert result.program_status == OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED
    assert result.next_stage == "owner_supervised_demo_approval"


def test_supervised_demo_order_runtime_missing_blocks():
    result = evaluate_live_execution_program(
        _input(
            execution_control_stack_ready=True,
            owner_supervised_demo_approval=True,
            supervised_demo_order_runtime_enabled=False,
        ),
    )
    assert result.program_status == SUPERVISED_DEMO_ORDER_RUNTIME_REQUIRED
    assert result.next_stage == "supervised_demo_order_execution"


def test_supervised_demo_order_execution_ready():
    result = evaluate_live_execution_program(
        _input(
            execution_control_stack_ready=True,
            owner_supervised_demo_approval=True,
            supervised_demo_order_runtime_enabled=True,
            supervised_demo_order_executed=False,
        ),
    )
    assert result.program_status == SUPERVISED_DEMO_ORDER_EXECUTION_READY
    assert result.next_stage == "owner_run_supervised_demo_order"


def test_supervised_demo_evidence_review_required():
    result = evaluate_live_execution_program(
        _input(
            execution_control_stack_ready=True,
            owner_supervised_demo_approval=True,
            supervised_demo_order_runtime_enabled=True,
            supervised_demo_order_executed=True,
            supervised_demo_evidence_clean=False,
        ),
    )
    assert result.program_status == SUPERVISED_DEMO_EVIDENCE_REVIEW_REQUIRED
    assert result.next_stage == "demo_evidence_review"


def test_micro_live_approval_missing_blocks():
    result = evaluate_live_execution_program(
        _input(
            execution_control_stack_ready=True,
            owner_supervised_demo_approval=True,
            supervised_demo_order_runtime_enabled=True,
            supervised_demo_order_executed=True,
            supervised_demo_evidence_clean=True,
            owner_micro_live_exception_approval=False,
        ),
    )
    assert result.program_status == MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED
    assert result.next_stage == "owner_micro_live_exception_approval"


def test_micro_live_order_runtime_missing_blocks():
    result = evaluate_live_execution_program(
        _input(
            execution_control_stack_ready=True,
            owner_supervised_demo_approval=True,
            supervised_demo_order_runtime_enabled=True,
            supervised_demo_order_executed=True,
            supervised_demo_evidence_clean=True,
            owner_micro_live_exception_approval=True,
            micro_live_order_runtime_enabled=False,
        ),
    )
    assert result.program_status == MICRO_LIVE_ORDER_RUNTIME_REQUIRED
    assert result.next_stage == "controlled_micro_live_exception"


def test_micro_live_execution_ready():
    result = evaluate_live_execution_program(
        _input(
            execution_control_stack_ready=True,
            owner_supervised_demo_approval=True,
            supervised_demo_order_runtime_enabled=True,
            supervised_demo_order_executed=True,
            supervised_demo_evidence_clean=True,
            owner_micro_live_exception_approval=True,
            micro_live_order_runtime_enabled=True,
            micro_live_order_executed=False,
        ),
    )
    assert result.program_status == MICRO_LIVE_ORDER_EXECUTION_READY
    assert result.next_stage == "owner_run_micro_live_exception"


def test_micro_live_evidence_review_required():
    result = evaluate_live_execution_program(
        _input(
            execution_control_stack_ready=True,
            owner_supervised_demo_approval=True,
            supervised_demo_order_runtime_enabled=True,
            supervised_demo_order_executed=True,
            supervised_demo_evidence_clean=True,
            owner_micro_live_exception_approval=True,
            micro_live_order_runtime_enabled=True,
            micro_live_order_executed=True,
            micro_live_evidence_clean=False,
        ),
    )
    assert result.program_status == MICRO_LIVE_EVIDENCE_REVIEW_REQUIRED
    assert result.next_stage == "micro_live_evidence_review"


def test_live_trading_approval_missing_blocks():
    result = evaluate_live_execution_program(
        _input(
            execution_control_stack_ready=True,
            owner_supervised_demo_approval=True,
            supervised_demo_order_runtime_enabled=True,
            supervised_demo_order_executed=True,
            supervised_demo_evidence_clean=True,
            owner_micro_live_exception_approval=True,
            micro_live_order_runtime_enabled=True,
            micro_live_order_executed=True,
            micro_live_evidence_clean=True,
            owner_live_trading_approval=False,
        ),
    )
    assert result.program_status == LIVE_TRADING_APPROVAL_REQUIRED_STATUS
    assert result.next_stage == "owner_live_trading_approval"


def test_live_order_lane_missing_blocks():
    result = evaluate_live_execution_program(
        _input(
            execution_control_stack_ready=True,
            owner_supervised_demo_approval=True,
            supervised_demo_order_runtime_enabled=True,
            supervised_demo_order_executed=True,
            supervised_demo_evidence_clean=True,
            owner_micro_live_exception_approval=True,
            micro_live_order_runtime_enabled=True,
            micro_live_order_executed=True,
            micro_live_evidence_clean=True,
            owner_live_trading_approval=True,
            live_order_lane_enabled=False,
        ),
    )
    assert result.program_status == LIVE_ORDER_LANE_REQUIRED
    assert result.next_stage == "live_order_lane"


def test_live_order_execution_runtime_missing_blocks():
    result = evaluate_live_execution_program(
        _input(
            execution_control_stack_ready=True,
            owner_supervised_demo_approval=True,
            supervised_demo_order_runtime_enabled=True,
            supervised_demo_order_executed=True,
            supervised_demo_evidence_clean=True,
            owner_micro_live_exception_approval=True,
            micro_live_order_runtime_enabled=True,
            micro_live_order_executed=True,
            micro_live_evidence_clean=True,
            owner_live_trading_approval=True,
            live_order_lane_enabled=True,
            live_order_execution_enabled=False,
        ),
    )
    assert result.program_status == LIVE_ORDER_EXECUTION_RUNTIME_REQUIRED
    assert result.next_stage == "owner_run_live_order_execution"


def test_autonomous_22h_6d_runtime_missing_blocks():
    result = evaluate_live_execution_program(
        _input(
            execution_control_stack_ready=True,
            owner_supervised_demo_approval=True,
            supervised_demo_order_runtime_enabled=True,
            supervised_demo_order_executed=True,
            supervised_demo_evidence_clean=True,
            owner_micro_live_exception_approval=True,
            micro_live_order_runtime_enabled=True,
            micro_live_order_executed=True,
            micro_live_evidence_clean=True,
            owner_live_trading_approval=True,
            live_order_lane_enabled=True,
            live_order_execution_enabled=True,
            autonomous_22h_6d_enabled=False,
        ),
    )
    assert result.program_status == AUTONOMOUS_22H_6D_RUNTIME_REQUIRED
    assert result.next_stage == "autonomous_22h_6d_runtime"


def test_ready_with_staged_inputs():
    result = evaluate_live_execution_program(_to_ready_input())
    assert result.program_status == LIVE_22H_6D_EXECUTION_PROGRAM_READY
    assert result.current_stage == STAGE_AUTONOMOUS_READY
    assert result.next_stage == "owner_run_22h_6d_live_execution"
    assert result.demo_order_execution is False
    assert result.micro_live_order_execution is False
    assert result.live_order_execution is False
    assert result.money_movement is False
    assert result.autonomous_22h_6d_authorized is False
    assert result.broker_api_called is False
    assert result.bitwarden_cli_called is False
    assert result.credentials_read is False
    assert result.env_file_read is False
    assert result.scheduler_started is False
    assert result.daemon_started is False
    assert result.webhook_started is False


def test_runner_writes_state_and_report(tmp_path: Path):
    state_path = tmp_path / "AIOS_FOREX_LIVE_EXECUTION_PROGRAM_V1_STATE.json"
    report_path = tmp_path / "AIOS_FOREX_LIVE_EXECUTION_PROGRAM_V1_REPORT.md"
    payload = run_forex_live_execution_program_v1(
        state_output=state_path,
        report_output=report_path,
        write_report=True,
    )
    assert state_path.exists()
    assert report_path.exists()
    assert payload["result"]["program_status"] == OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["program_summary"]["program_status"] == OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED
    assert state["result"]["demo_order_execution"] is False
    assert state["result"]["micro_live_order_execution"] is False
    assert state["result"]["live_order_execution"] is False
    assert state["result"]["money_movement"] is False
    assert "demo_order_execution" in report_path.read_text(encoding="utf-8").lower()


def test_config_template_is_no_secret_and_has_required_fields():
    data = json.loads(
        Path("configs/forex/AIOS_FOREX_LIVE_EXECUTION_PROGRAM_V1.example.json").read_text(
            encoding="utf-8",
        ),
    )
    assert data["default_mode"] == "dry_run"
    assert data["target"] == "live 22hr/day 6day/week autonomous execution"
    assert data["broker_runtime_read_only_auth_proven"] is True
    assert data["execution_control_stack_landed"] is True
    assert data["owner_supervised_demo_approval_required"] is True
    assert data["micro_live_exception_approval_required"] is True
    assert data["live_trading_approval_required"] is True
    assert data["autonomous_22h_6d_owner_approval_required"] is True
    assert data["broker_api_called_by_this_packet"] is False
    assert data["bitwarden_cli_called_by_this_packet"] is False
    assert data["credentials_read_by_this_packet"] is False
    assert data["env_file_read_by_this_packet"] is False
    assert data["demo_order_execution_by_this_packet"] is False
    assert data["micro_live_order_execution_by_this_packet"] is False
    assert data["live_order_execution_by_this_packet"] is False
    assert data["money_movement_by_this_packet"] is False
    assert data["scheduler_started_by_this_packet"] is False
    assert data["daemon_started_by_this_packet"] is False
    assert data["webhook_started_by_this_packet"] is False
    assert data["next_stage"] == "owner_supervised_demo_approval"
    assert data["session_window_hours"] == CURRENT_SESSION_WINDOW_HOURS
    assert data["session_window_days_per_week"] == CURRENT_SESSION_WINDOW_DAYS_PER_WEEK
    dump = json.dumps(data).lower()
    assert "secret" not in dump
    assert "token" not in dump


def test_docs_mention_live_path_and_gate_contract():
    text = Path("docs/trading_lab/forex/FOREX_LIVE_EXECUTION_PROGRAM_V1.md").read_text(
        encoding="utf-8",
    ).lower()
    required_phrases = [
        "integrated live execution program lane",
        "live 22hr/day, 6day/week",
        "does not execute demo or live orders during validation",
        "does not call broker apis during validation",
        "does not read bitwarden",
        "does not read credentials",
        "does not read `.env`",
        "requires supervised demo approval before demo order execution",
        "requires clean demo evidence before micro-live exception",
        "requires micro-live approval and clean micro-live evidence before live lane",
        "requires owner live trading approval before any live order",
        "requires separate owner approval before 22h/6d autonomous runtime",
        "current next stage is owner_supervised_demo_approval",
    ]
    for phrase in required_phrases:
        assert phrase in text
