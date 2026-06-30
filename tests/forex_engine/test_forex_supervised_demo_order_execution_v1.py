from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from automation.forex_engine.forex_supervised_demo_order_execution_v1 import (
    DEFAULT_RUNTIME_ALLOWED_MODES,
    OWNER_RUNTIME_ORDER_FLAG_REQUIRED,
    OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED,
    PREREQUISITES_REQUIRED,
    PROTECTED_BOUNDARY_VIOLATION,
    RUNTIME_CREDENTIAL_ACCESS_REQUIRED,
    PRACTICE_DEMO_BOUNDARY_REQUIRED,
    KILL_SWITCH_BLOCKED,
    EXECUTION_CONTROL_BLOCKED,
    SUPERVISED_DEMO_ORDER_READY,
    SupervisedDemoOrderInput,
    build_default_input,
    evaluate_supervised_demo_order_execution,
)
from scripts.forex_delivery.run_forex_supervised_demo_order_execution_v1 import (
    run_forex_supervised_demo_order_execution_v1,
)


def _input(**changes) -> SupervisedDemoOrderInput:
    return replace(build_default_input(), **changes)


def _runtime_ready_input() -> SupervisedDemoOrderInput:
    parsed_item_fields = {
        "broker_api_token": "token",
        "broker_account_id": "account",
        "endpoint": "https://api-fxpractice.oanda.com",
        "environment": "practice_demo",
        "allowed_mode": DEFAULT_RUNTIME_ALLOWED_MODES[0],
    }
    return _input(
        owner_supervised_demo_approval=True,
        owner_runtime_order_flag=True,
        bw_session_present=True,
        bitwarden_cli_available=True,
        bitwarden_item_read_success=True,
        credential_values_available_to_runtime=bool(parsed_item_fields),
        endpoint_is_oanda_practice=True,
        environment_is_practice_demo=True,
        allowed_mode_is_demo_only=True,
        broker_api_called=False,
        bitwarden_cli_called=False,
        credentials_read=False,
        env_file_read=False,
        demo_order_execution=False,
        live_order_execution=False,
        money_movement=False,
        scheduler_started=False,
        daemon_started=False,
        webhook_started=False,
        kill_switch_enabled=True,
        kill_switch_triggered=False,
        max_daily_loss_defined=True,
        daily_loss_within_limit=True,
        max_trade_risk_defined=True,
        proposed_trade_risk_within_limit=True,
        duplicate_order_guard_enabled=True,
        duplicate_order_detected=False,
        audit_log_enabled=True,
        audit_log_write_success=True,
        stop_loss_defined=True,
        take_profit_defined=True,
        units=1,
        side="buy",
        order_type="market",
        time_in_force="FOK",
        instrument="EUR_USD",
    )


def test_default_input_returns_owner_supervised_demo_approval_required():
    result = evaluate_supervised_demo_order_execution(_input())
    assert result.demo_order_status == OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED
    assert result.current_stage == "supervised_demo_order_execution"
    assert result.next_stage == "owner_supervised_demo_approval"


def test_missing_prerequisites_block():
    result = evaluate_supervised_demo_order_execution(
        _input(
            broker_runtime_read_only_auth_proven=False,
            execution_control_stack_landed=False,
        ),
    )
    assert result.demo_order_status == PREREQUISITES_REQUIRED
    assert result.next_stage == "complete_prior_execution_lanes"


def test_missing_owner_runtime_flag_blocks():
    result = evaluate_supervised_demo_order_execution(
        _input(owner_supervised_demo_approval=True, owner_runtime_order_flag=False),
    )
    assert result.demo_order_status == OWNER_RUNTIME_ORDER_FLAG_REQUIRED
    assert result.next_stage == "owner_run_supervised_demo_order"


def test_protected_boundary_flags_block():
    for field_name in [
        "broker_api_called",
        "bitwarden_cli_called",
        "credentials_read",
        "env_file_read",
        "demo_order_execution",
        "live_order_execution",
        "money_movement",
        "scheduler_started",
        "daemon_started",
        "webhook_started",
    ]:
        result = evaluate_supervised_demo_order_execution(
            _input(
                owner_supervised_demo_approval=True,
                owner_runtime_order_flag=True,
                **{field_name: True},
            ),
        )
        assert result.demo_order_status == PROTECTED_BOUNDARY_VIOLATION
        assert result.next_stage == "stop_and_owner_review"
        assert result.live_order_execution is False
        assert result.money_movement is False
        assert result.scheduler_started is False


def test_missing_runtime_access_blocked():
    for field_name in [
        "bw_session_present",
        "bitwarden_cli_available",
        "bitwarden_item_read_success",
        "credential_values_available_to_runtime",
    ]:
        kwargs = {
            "owner_supervised_demo_approval": True,
            "owner_runtime_order_flag": True,
        }
        for required in [
            "bw_session_present",
            "bitwarden_cli_available",
            "bitwarden_item_read_success",
            "credential_values_available_to_runtime",
        ]:
            kwargs[required] = required == field_name
        kwargs[field_name] = False
        result = evaluate_supervised_demo_order_execution(_input(**kwargs))
        assert result.demo_order_status == RUNTIME_CREDENTIAL_ACCESS_REQUIRED
        assert result.next_stage == "owner_unlock_bitwarden_cli"


def test_non_practice_boundary_blocks():
    for field_name in [
        "endpoint_is_oanda_practice",
        "environment_is_practice_demo",
        "allowed_mode_is_demo_only",
    ]:
        result = evaluate_supervised_demo_order_execution(
            _input(
                owner_supervised_demo_approval=True,
                owner_runtime_order_flag=True,
                bw_session_present=True,
                bitwarden_cli_available=True,
                bitwarden_item_read_success=True,
                credential_values_available_to_runtime=True,
                **{field_name: False},
            ),
        )
        assert result.demo_order_status == PRACTICE_DEMO_BOUNDARY_REQUIRED
        assert result.next_stage == "repair_demo_boundary"


def test_kill_switch_blocks_when_disabled_or_triggered():
    result = evaluate_supervised_demo_order_execution(
        _input(
            owner_supervised_demo_approval=True,
            owner_runtime_order_flag=True,
            bw_session_present=True,
            bitwarden_cli_available=True,
            bitwarden_item_read_success=True,
            credential_values_available_to_runtime=True,
            kill_switch_enabled=False,
        ),
    )
    assert result.demo_order_status == KILL_SWITCH_BLOCKED
    assert result.next_stage == "owner_review_required"

    result = evaluate_supervised_demo_order_execution(
        _input(
            owner_supervised_demo_approval=True,
            owner_runtime_order_flag=True,
            bw_session_present=True,
            bitwarden_cli_available=True,
            bitwarden_item_read_success=True,
            credential_values_available_to_runtime=True,
            kill_switch_triggered=True,
        ),
    )
    assert result.demo_order_status == KILL_SWITCH_BLOCKED
    assert result.next_stage == "owner_review_required"


def test_execution_controls_blocked_for_risk_audit_duplicate_or_sl_tp():
    for field_name in [
        "max_daily_loss_defined",
        "daily_loss_within_limit",
        "max_trade_risk_defined",
        "proposed_trade_risk_within_limit",
        "duplicate_order_guard_enabled",
        "audit_log_enabled",
        "audit_log_write_success",
        "stop_loss_defined",
        "take_profit_defined",
    ]:
        kwargs = {
            "owner_supervised_demo_approval": True,
            "owner_runtime_order_flag": True,
            "bw_session_present": True,
            "bitwarden_cli_available": True,
            "bitwarden_item_read_success": True,
            "credential_values_available_to_runtime": True,
            field_name: False if field_name not in {"duplicate_order_detected"} else True,
        }
        if field_name == "duplicate_order_guard_enabled":
            kwargs["duplicate_order_detected"] = False
        if field_name == "daily_loss_within_limit":
            kwargs["duplicate_order_detected"] = False
        result = evaluate_supervised_demo_order_execution(_input(**kwargs))
        assert result.demo_order_status == EXECUTION_CONTROL_BLOCKED
        assert result.next_stage == "repair_execution_controls"

    result = evaluate_supervised_demo_order_execution(
        _input(
            owner_supervised_demo_approval=True,
            owner_runtime_order_flag=True,
            bw_session_present=True,
            bitwarden_cli_available=True,
            bitwarden_item_read_success=True,
            credential_values_available_to_runtime=True,
            duplicate_order_guard_enabled=True,
            duplicate_order_detected=True,
        ),
    )
    assert result.demo_order_status == EXECUTION_CONTROL_BLOCKED
    assert result.next_stage == "repair_execution_controls"


def test_runtime_ready_when_all_controls_true():
    result = evaluate_supervised_demo_order_execution(_runtime_ready_input())
    assert result.demo_order_status == SUPERVISED_DEMO_ORDER_READY
    assert result.next_stage == "owner_execute_one_supervised_demo_order"
    assert result.current_stage == "supervised_demo_order_execution"


def test_output_gates_and_actions_are_false_in_runtime_ready():
    result = evaluate_supervised_demo_order_execution(_runtime_ready_input())
    assert result.live_order_execution is False
    assert result.money_movement is False
    assert result.scheduler_started is False
    assert result.daemon_started is False
    assert result.webhook_started is False


def test_runner_dry_run_writes_state_and_report(tmp_path: Path):
    state_path = tmp_path / "AIOS_FOREX_SUPERVISED_DEMO_ORDER_EXECUTION_V1_STATE.json"
    report_path = tmp_path / "AIOS_FOREX_SUPERVISED_DEMO_ORDER_EXECUTION_V1_REPORT.md"
    payload = run_forex_supervised_demo_order_execution_v1(
        owner_approved_supervised_demo_order=False,
        state_output=state_path,
        report_output=report_path,
        write_report=True,
    )
    assert state_path.exists()
    assert report_path.exists()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["result"]["demo_order_status"] == OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED
    assert state["result"]["current_stage"] == "supervised_demo_order_execution"
    assert state["result"]["next_stage"] == "owner_supervised_demo_approval"
    assert state["result"]["live_order_execution"] is False
    assert state["result"]["money_movement"] is False
    assert "OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED" in report_path.read_text(encoding="utf-8")
    assert payload["result"]["demo_order_status"] == OWNER_SUPERVISED_DEMO_APPROVAL_REQUIRED


def test_config_template_has_expected_no_secret_fields():
    data = json.loads(
        Path(
            "configs/forex/AIOS_FOREX_SUPERVISED_DEMO_ORDER_EXECUTION_V1.example.json",
        ).read_text(encoding="utf-8"),
    )
    required = [
        "default_mode",
        "runtime_flag",
        "broker",
        "environment",
        "endpoint",
        "instrument",
        "units",
        "side",
        "order_type",
        "time_in_force",
        "stop_loss_required",
        "take_profit_required",
        "max_orders_per_run",
        "live_order_execution_by_this_packet",
        "scheduler_started_by_this_packet",
        "daemon_started_by_this_packet",
        "webhook_started_by_this_packet",
        "next_stage_after_success",
    ]
    for field_name in required:
        assert field_name in data
    assert data["default_mode"] == "dry_run"
    assert data["runtime_flag"] == "--owner-approved-supervised-demo-order"
    assert data["endpoint"] == "https://api-fxpractice.oanda.com"
    assert data["environment"] == "practice_demo"
    assert data["units"] == 1
    assert data["stop_loss_required"] is True
    assert data["take_profit_required"] is True
    assert data["max_orders_per_run"] == 1
    assert data["next_stage_after_success"] == "supervised_demo_evidence_review"
    assert data["live_order_execution_by_this_packet"] is False
    assert data["scheduler_started_by_this_packet"] is False
    assert data["daemon_started_by_this_packet"] is False
    assert data["webhook_started_by_this_packet"] is False
    raw = json.dumps(data).lower()
    assert "token" not in raw
    assert "secret" not in raw


def test_docs_mention_no_live_authorization_and_single_demo_order():
    text = Path(
        "docs/trading_lab/forex/FOREX_SUPERVISED_DEMO_ORDER_EXECUTION_V1.md",
    ).read_text(encoding="utf-8").lower()
    phrases = [
        "first owner-run supervised demo order execution path",
        "default validation does not place orders",
        "runtime mode requires explicit owner flag",
        "oanda practice only",
        "at most one",
        "does not authorize live trading",
        "does not start 22h/6d runtime",
        "success moves to supervised_demo_evidence_review",
        "final target remains live 22hr/day, 6day/week autonomous execution",
    ]
    for phrase in phrases:
        assert phrase in text
