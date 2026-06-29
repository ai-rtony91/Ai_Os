from __future__ import annotations

import io
from pathlib import Path

from automation.forex_engine.forex_live_execution_readiness_lane_v1 import (
    DEFAULT_SESSION_WINDOW_DAYS_PER_WEEK,
    DEFAULT_SESSION_WINDOW_HOURS,
    ExecutionReadinessInput,
    build_default_execution_readiness_input,
    evaluate_live_execution_readiness,
    run_forex_live_execution_readiness_lane_v1,
    LANE_STATUS_CONTROLLED_DEMO_EXECUTION_READY,
    LANE_STATUS_CONTROLLED_MICRO_LIVE_EXCEPTION_READY,
    LANE_STATUS_CREDENTIAL_PERSISTENCE_REQUIRED,
    LANE_STATUS_EXECUTION_CONTROLS_REQUIRED,
    LANE_STATUS_PROOF_PREREQUISITES_INCOMPLETE,
    LANE_STATUS_BROKER_READ_ONLY_PREP_REQUIRED,
    LANE_STATUS_SUPERVISED_DEMO_APPROVAL_REQUIRED,
)
from scripts.forex_delivery.run_forex_live_execution_readiness_lane_v1 import main


def _base_ready_input() -> ExecutionReadinessInput:
    return ExecutionReadinessInput(
        forex_110_closed=True,
        persistent_profitability_ready=True,
        walkforward_oos_proven=True,
        broker_read_only_config_present=True,
        broker_credentials_available_to_runtime=True,
        owner_demo_approval=True,
        owner_micro_live_exception_approval=True,
        kill_switch_defined=True,
        max_daily_loss_defined=True,
        max_trade_risk_defined=True,
        duplicate_order_guard_defined=True,
        audit_log_defined=True,
        session_window_hours=DEFAULT_SESSION_WINDOW_HOURS,
        session_window_days_per_week=DEFAULT_SESSION_WINDOW_DAYS_PER_WEEK,
    )


def test_default_input_returns_broker_read_only_prep_required() -> None:
    result = evaluate_live_execution_readiness(build_default_execution_readiness_input())

    assert result.lane_status == LANE_STATUS_BROKER_READ_ONLY_PREP_REQUIRED
    assert result.current_stage == "execution_readiness"
    assert result.next_stage == "broker_read_only_state_probe"


def test_incomplete_proof_returns_proof_prerequisites_incomplete() -> None:
    result = evaluate_live_execution_readiness(
        ExecutionReadinessInput(
            forex_110_closed=False,
            persistent_profitability_ready=True,
            walkforward_oos_proven=True,
            broker_read_only_config_present=False,
            broker_credentials_available_to_runtime=False,
            owner_demo_approval=False,
            owner_micro_live_exception_approval=False,
            kill_switch_defined=False,
            max_daily_loss_defined=False,
            max_trade_risk_defined=False,
            duplicate_order_guard_defined=False,
            audit_log_defined=False,
            session_window_hours=DEFAULT_SESSION_WINDOW_HOURS,
            session_window_days_per_week=DEFAULT_SESSION_WINDOW_DAYS_PER_WEEK,
        )
    )
    assert result.lane_status == LANE_STATUS_PROOF_PREREQUISITES_INCOMPLETE


def test_broker_config_present_but_credentials_absent_returns_credential_persistence_required() -> None:
    result = evaluate_live_execution_readiness(
        ExecutionReadinessInput(
            forex_110_closed=True,
            persistent_profitability_ready=True,
            walkforward_oos_proven=True,
            broker_read_only_config_present=True,
            broker_credentials_available_to_runtime=False,
            owner_demo_approval=False,
            owner_micro_live_exception_approval=False,
            kill_switch_defined=False,
            max_daily_loss_defined=False,
            max_trade_risk_defined=False,
            duplicate_order_guard_defined=False,
            audit_log_defined=False,
            session_window_hours=DEFAULT_SESSION_WINDOW_HOURS,
            session_window_days_per_week=DEFAULT_SESSION_WINDOW_DAYS_PER_WEEK,
        )
    )
    assert result.lane_status == LANE_STATUS_CREDENTIAL_PERSISTENCE_REQUIRED


def test_credentials_present_but_controls_incomplete_returns_execution_controls_required() -> None:
    result = evaluate_live_execution_readiness(
        ExecutionReadinessInput(
            forex_110_closed=True,
            persistent_profitability_ready=True,
            walkforward_oos_proven=True,
            broker_read_only_config_present=True,
            broker_credentials_available_to_runtime=True,
            owner_demo_approval=False,
            owner_micro_live_exception_approval=False,
            kill_switch_defined=True,
            max_daily_loss_defined=True,
            max_trade_risk_defined=False,
            duplicate_order_guard_defined=True,
            audit_log_defined=True,
            session_window_hours=DEFAULT_SESSION_WINDOW_HOURS,
            session_window_days_per_week=DEFAULT_SESSION_WINDOW_DAYS_PER_WEEK,
        )
    )
    assert result.lane_status == LANE_STATUS_EXECUTION_CONTROLS_REQUIRED


def test_controls_complete_but_demo_approval_absent_returns_supervised_demo_approval_required() -> None:
    input_state = _base_ready_input()
    result = evaluate_live_execution_readiness(
        ExecutionReadinessInput(
            **{**input_state.__dict__, "owner_demo_approval": False}
        )
    )
    assert result.lane_status == LANE_STATUS_SUPERVISED_DEMO_APPROVAL_REQUIRED


def test_demo_approval_true_returns_controlled_demo_execution_ready() -> None:
    input_state = _base_ready_input()
    result = evaluate_live_execution_readiness(
        ExecutionReadinessInput(
            **{**input_state.__dict__, "owner_micro_live_exception_approval": False}
        )
    )
    assert result.lane_status == LANE_STATUS_CONTROLLED_DEMO_EXECUTION_READY


def test_micro_live_approval_true_returns_controlled_micro_live_exception_ready() -> None:
    result = evaluate_live_execution_readiness(_base_ready_input())
    assert result.lane_status == LANE_STATUS_CONTROLLED_MICRO_LIVE_EXCEPTION_READY


def test_forbidden_authorization_flags_always_false() -> None:
    input_state = build_default_execution_readiness_input()
    result = evaluate_live_execution_readiness(input_state)

    assert result.broker_api_used is False
    assert result.credentials_read is False
    assert result.env_read is False
    assert result.order_execution is False
    assert result.live_authorized is False
    assert result.autonomous_22h_6d_authorized is False


def test_runner_writes_state_and_report(tmp_path: Path) -> None:
    state_path = tmp_path / "Reports" / "forex_delivery" / "AIOS_FOREX_LIVE_EXECUTION_READINESS_LANE_V1_STATE.json"
    report_path = tmp_path / "Reports" / "forex_delivery" / "AIOS_FOREX_LIVE_EXECUTION_READINESS_LANE_V1_REPORT.md"
    output = io.StringIO()

    exit_code = main(
        [
            "--state-path",
            str(state_path),
            "--report-path",
            str(report_path),
        ],
        stdout=output,
    )

    assert exit_code == 0
    assert state_path.exists()
    assert report_path.exists()
    assert "lane_status" in output.getvalue()


def test_documentation_targets_supervised_demo_then_22h6d_path() -> None:
    doc = Path("docs/trading_lab/forex/FOREX_LIVE_EXECUTION_READINESS_LANE_V1.md").read_text(
        encoding="utf-8",
    )
    assert (
        "supervised demo -> controlled micro-live exception -> 22hr/day, 6day/week autonomous execution"
        in doc.lower()
    )
