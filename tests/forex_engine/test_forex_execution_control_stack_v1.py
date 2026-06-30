from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from automation.forex_engine.forex_execution_control_stack_v1 import (
    AUDIT_LOG_REQUIRED,
    AUDIT_LOG_WRITE_REQUIRED,
    BROKER_RUNTIME_READ_ONLY_AUTH_REQUIRED,
    EXECUTION_CONTROL_STACK_READY,
    DUPLICATE_ORDER_BLOCKED,
    DUPLICATE_ORDER_GUARD_REQUIRED,
    ExecutionControlInput,
    KILL_SWITCH_BLOCKED,
    KILL_SWITCH_REQUIRED,
    MAX_DAILY_LOSS_BLOCKED,
    MAX_DAILY_LOSS_REQUIRED,
    MAX_TRADE_RISK_BLOCKED,
    MAX_TRADE_RISK_REQUIRED,
    PROTECTED_BOUNDARY_VIOLATION,
    STOP_LOSS_REQUIRED,
    SUPERVISED_DEMO_APPROVAL_REQUIRED,
    TAKE_PROFIT_REQUIRED,
    build_default_input,
    evaluate_execution_control_stack,
)
from scripts.forex_delivery.run_forex_execution_control_stack_v1 import run_execution_control_stack


def _input(**changes) -> ExecutionControlInput:
    return replace(build_default_input(), **changes)


def test_default_input_returns_supervised_demo_approval_required():
    result = evaluate_execution_control_stack(_input())
    assert result.control_status == SUPERVISED_DEMO_APPROVAL_REQUIRED
    assert result.current_stage == "execution_control_stack"
    assert result.next_stage == "owner_supervised_demo_approval"


def test_missing_broker_auth_proof_returns_required_status():
    result = evaluate_execution_control_stack(
        replace(_input(), broker_runtime_read_only_auth_proven=False),
    )
    assert result.control_status == BROKER_RUNTIME_READ_ONLY_AUTH_REQUIRED
    assert result.next_stage == "broker_runtime_read_only_auth_probe"


@pytest.mark.parametrize(
    "field_name",
    [
        "broker_api_called",
        "bitwarden_cli_called",
        "credentials_read",
        "env_file_read",
        "order_execution",
        "demo_authorized",
        "live_authorized",
    ],
)
def test_protected_action_flags_return_boundary_violation(field_name):
    changes = {field_name: True}
    result = evaluate_execution_control_stack(_input(**changes))
    assert result.control_status == PROTECTED_BOUNDARY_VIOLATION
    assert result.next_stage == "stop_and_owner_review"
    assert result.order_execution is False
    assert result.demo_authorized is False
    assert result.live_authorized is False


def test_kill_switch_required_when_disabled():
    result = evaluate_execution_control_stack(_input(kill_switch_enabled=False))
    assert result.control_status == KILL_SWITCH_REQUIRED
    assert result.next_stage == "define_kill_switch"


def test_kill_switch_blocked_when_triggered():
    result = evaluate_execution_control_stack(_input(kill_switch_triggered=True))
    assert result.control_status == KILL_SWITCH_BLOCKED
    assert result.next_stage == "owner_review_required"


def test_max_daily_loss_required_when_missing():
    result = evaluate_execution_control_stack(_input(max_daily_loss_defined=False))
    assert result.control_status == MAX_DAILY_LOSS_REQUIRED
    assert result.next_stage == "define_max_daily_loss"


def test_max_daily_loss_blocked_when_exceeded():
    result = evaluate_execution_control_stack(
        _input(current_daily_loss_amount=30.00, max_daily_loss_amount=20.00),
    )
    assert result.control_status == MAX_DAILY_LOSS_BLOCKED
    assert result.next_stage == "daily_loss_owner_review"


def test_max_trade_risk_required_when_missing():
    result = evaluate_execution_control_stack(_input(max_trade_risk_defined=False))
    assert result.control_status == MAX_TRADE_RISK_REQUIRED
    assert result.next_stage == "define_max_trade_risk"


def test_max_trade_risk_blocked_when_exceeded():
    result = evaluate_execution_control_stack(_input(proposed_trade_risk_amount=3.00))
    assert result.control_status == MAX_TRADE_RISK_BLOCKED
    assert result.next_stage == "reduce_trade_risk"


def test_duplicate_order_guard_required_when_missing():
    result = evaluate_execution_control_stack(_input(duplicate_order_guard_enabled=False))
    assert result.control_status == DUPLICATE_ORDER_GUARD_REQUIRED
    assert result.next_stage == "define_duplicate_order_guard"


def test_duplicate_order_blocked_when_detected():
    result = evaluate_execution_control_stack(_input(duplicate_order_detected=True))
    assert result.control_status == DUPLICATE_ORDER_BLOCKED
    assert result.next_stage == "duplicate_order_owner_review"


def test_audit_log_required_when_disabled():
    result = evaluate_execution_control_stack(_input(audit_log_enabled=False))
    assert result.control_status == AUDIT_LOG_REQUIRED
    assert result.next_stage == "define_order_intent_audit_log"


def test_audit_log_write_required_when_write_fails():
    result = evaluate_execution_control_stack(_input(audit_log_write_success=False))
    assert result.control_status == AUDIT_LOG_WRITE_REQUIRED
    assert result.next_stage == "repair_order_intent_audit_log"


def test_stop_loss_required_when_missing():
    result = evaluate_execution_control_stack(_input(stop_loss_defined=False))
    assert result.control_status == STOP_LOSS_REQUIRED
    assert result.next_stage == "define_stop_loss"


def test_take_profit_required_when_missing():
    result = evaluate_execution_control_stack(_input(take_profit_defined=False))
    assert result.control_status == TAKE_PROFIT_REQUIRED
    assert result.next_stage == "define_take_profit"


def test_owner_demo_approval_returns_ready():
    result = evaluate_execution_control_stack(_input(owner_demo_approval=True))
    assert result.control_status == EXECUTION_CONTROL_STACK_READY
    assert result.next_stage == "supervised_demo_order_execution"
    assert result.order_execution is False
    assert result.live_authorized is False
    assert result.demo_authorized is False


def test_runner_writes_state_and_report(tmp_path: Path):
    state_path = tmp_path / "AIOS_FOREX_EXECUTION_CONTROL_STACK_V1_STATE.json"
    report_path = tmp_path / "AIOS_FOREX_EXECUTION_CONTROL_STACK_V1_REPORT.md"
    payload = run_execution_control_stack(
        owner_demo_approval=False,
        state_output=state_path,
        report_output=report_path,
        write_report=True,
    )
    assert state_path.exists()
    assert report_path.exists()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    result = state["result"]
    assert result["control_status"] == SUPERVISED_DEMO_APPROVAL_REQUIRED
    assert result["next_stage"] == "owner_supervised_demo_approval"
    assert result["order_execution"] is False
    assert result["demo_authorized"] is False
    assert result["live_authorized"] is False
    assert "supervised demo approval" in state["result"]["safe_next_action"].lower()
    assert payload["result"]["control_status"] == SUPERVISED_DEMO_APPROVAL_REQUIRED


def test_template_has_required_no_secret_values_and_contract_fields():
    data = json.loads(
        Path(
            "configs/forex/AIOS_FOREX_EXECUTION_CONTROL_STACK_V1.example.json",
        ).read_text(encoding="utf-8"),
    )
    required_fields = [
        "broker_runtime_read_only_auth_proven",
        "default_mode",
        "kill_switch_enabled",
        "kill_switch_triggered",
        "max_daily_loss_amount",
        "max_trade_risk_amount",
        "duplicate_order_guard_enabled",
        "audit_log_enabled",
        "stop_loss_required",
        "take_profit_required",
        "demo_authorized_by_this_packet",
        "live_authorized_by_this_packet",
        "order_execution_by_this_packet",
        "broker_api_called_by_this_packet",
        "credentials_read_by_this_packet",
        "next_stage_after_success",
    ]
    for field_name in required_fields:
        assert field_name in data
    assert data["broker_runtime_read_only_auth_proven"] is True
    assert data["default_mode"] == "dry_run"
    assert data["max_daily_loss_amount"] == 25.0
    assert data["max_trade_risk_amount"] == 2.0
    raw_dump = json.dumps(data).lower()
    assert "token" not in raw_dump
    assert "secret" not in raw_dump


def test_docs_mention_required_order_controls_and_authorization_boundaries():
    text = Path(
        "docs/trading_lab/forex/FOREX_EXECUTION_CONTROL_STACK_V1.md",
    ).read_text(encoding="utf-8")
    phrases = [
        "execution control stack after broker runtime read-only auth proof",
        "does not call broker apis",
        "does not read bitwarden",
        "does not place orders",
        "does not authorize demo trading",
        "does not authorize live trading",
        "default state blocks at supervised demo approval",
        "supervised demo -> controlled micro-live exception -> live 22hr/day, 6day/week",
    ]
    lower_text = text.lower()
    for phrase in phrases:
        assert phrase in lower_text
