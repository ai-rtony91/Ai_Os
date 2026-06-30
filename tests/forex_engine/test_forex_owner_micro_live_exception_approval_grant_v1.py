from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from automation.forex_engine.forex_owner_micro_live_exception_approval_grant_v1 import (
    CURRENT_STAGE,
    MICRO_LIVE_CONTROL_CONFIRMATION_REQUIRED,
    NEXT_STAGE_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER,
    OWNER_LIVE_RISK_CONFIRMATION_REQUIRED,
    OWNER_MICRO_LIVE_APPROVAL_CONFIRMATION_REQUIRED,
    OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED,
    PRIOR_GATE_REQUIRED,
    PROTECTED_BOUNDARY_VIOLATION,
    SUPERVISED_DEMO_EVIDENCE_REQUIRED,
    OwnerMicroLiveExceptionApprovalGrantInput,
    build_default_input,
    evaluate_owner_micro_live_exception_approval_grant_v1,
)
from scripts.forex_delivery import run_forex_owner_micro_live_exception_approval_grant_v1 as runtime_script


PROTECTED_OUTPUTS = (
    "live_order_execution",
    "money_movement",
    "broker_api_called",
    "bitwarden_cli_called",
    "credentials_read",
    "env_file_read",
    "scheduler_started",
    "daemon_started",
    "webhook_started",
)


def _input(**changes: object) -> OwnerMicroLiveExceptionApprovalGrantInput:
    return replace(build_default_input(), **changes)


def test_default_status_granted() -> None:
    result = evaluate_owner_micro_live_exception_approval_grant_v1(_input())
    assert result.owner_approval_status == OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED
    assert result.current_stage == CURRENT_STAGE
    assert result.next_stage == NEXT_STAGE_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER


def test_missing_prior_gate_blocks() -> None:
    result = evaluate_owner_micro_live_exception_approval_grant_v1(
        _input(prior_approval_gate_landed=False),
    )
    assert result.owner_approval_status == PRIOR_GATE_REQUIRED
    assert result.next_stage == "owner_micro_live_exception_approval"


def test_missing_supervised_demo_evidence_blocks() -> None:
    result = evaluate_owner_micro_live_exception_approval_grant_v1(
        _input(prior_approval_gate_landed=True, supervised_demo_evidence_clean=False),
    )
    assert result.owner_approval_status == SUPERVISED_DEMO_EVIDENCE_REQUIRED
    assert result.next_stage == "owner_micro_live_exception_approval"
    assert "supervised_demo_evidence_clean is False" in result.blockers


def test_missing_owner_approval_blocks() -> None:
    result = evaluate_owner_micro_live_exception_approval_grant_v1(
        _input(
            owner_micro_live_exception_approval=False,
        ),
    )
    assert result.owner_approval_status == OWNER_MICRO_LIVE_APPROVAL_CONFIRMATION_REQUIRED
    assert result.next_stage == CURRENT_STAGE
    assert "owner_micro_live_exception_approval is False" in result.blockers


def test_missing_owner_live_risk_acknowledgment_blocks() -> None:
    result = evaluate_owner_micro_live_exception_approval_grant_v1(
        _input(owner_understands_live_money_risk=False),
    )
    assert result.owner_approval_status == OWNER_LIVE_RISK_CONFIRMATION_REQUIRED
    assert result.next_stage == CURRENT_STAGE
    assert "owner_understands_live_money_risk is False" in result.blockers


def test_missing_control_confirmations_block() -> None:
    result = evaluate_owner_micro_live_exception_approval_grant_v1(
        _input(owner_confirms_no_autonomous_runtime=False),
    )
    assert result.owner_approval_status == MICRO_LIVE_CONTROL_CONFIRMATION_REQUIRED
    assert result.next_stage == CURRENT_STAGE
    assert "owner_confirms_no_autonomous_runtime is False" in result.blockers


def test_protected_boundary_flags_block() -> None:
    result = evaluate_owner_micro_live_exception_approval_grant_v1(
        _input(live_order_execution=True),
    )
    assert result.owner_approval_status == PROTECTED_BOUNDARY_VIOLATION
    assert result.next_stage == "stop_and_owner_review"


def test_grant_keeps_restrictions_static() -> None:
    result = evaluate_owner_micro_live_exception_approval_grant_v1(_input())
    assert result.owner_approval_status == OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED
    for field in PROTECTED_OUTPUTS:
        assert getattr(result, field) is False


def test_runner_writes_state_and_report(tmp_path: Path) -> None:
    state_path = tmp_path / "AIOS_FOREX_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANT_V1_STATE.json"
    report_path = tmp_path / "AIOS_FOREX_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANT_V1_REPORT.md"
    runtime_script.run_forex_owner_micro_live_exception_approval_grant_v1(
        state_output=state_path,
        report_output=report_path,
        write_report=True,
    )

    assert state_path.exists()
    assert report_path.exists()

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["result"]["owner_approval_status"] == OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED
    assert state["result"]["next_stage"] == NEXT_STAGE_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER
    assert state["approval_summary"]["approval_status"] == OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED
    assert state["approval_summary"]["next_stage_after_success"] == NEXT_STAGE_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER
    assert "OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED" in report_path.read_text(encoding="utf-8")


def test_config_template_valid_and_no_secrets() -> None:
    data = json.loads(
        Path(
            "configs/forex/AIOS_FOREX_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANT_V1.example.json",
        ).read_text(encoding="utf-8"),
    )
    assert data["default_mode"] == "dry_run"
    assert data["current_stage"] == "owner_micro_live_exception_approval_grant"
    assert data["approval_status"] == "OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED"
    assert data["next_stage_after_success"] == "controlled_micro_live_exception_runner"
    assert data["micro_live_max_orders"] == 1
    assert data["micro_live_size_policy"] == "minimum_owner_approved_size_only"
    assert data["owner_live_money_risk_ack"] is True
    assert data["owner_max_one_live_order_ack"] is True
    assert data["owner_no_autonomous_runtime_ack"] is True
    assert data["kill_switch_required"] is True
    assert data["daily_loss_cap_required"] is True
    assert data["trade_risk_cap_required"] is True
    assert data["audit_log_required"] is True
    assert data["live_order_execution_by_this_packet"] is False
    assert data["money_movement_by_this_packet"] is False
    assert data["broker_api_called_by_this_packet"] is False
    assert data["bitwarden_cli_called_by_this_packet"] is False
    assert data["credentials_read_by_this_packet"] is False
    assert data["env_file_read_by_this_packet"] is False
    assert data["scheduler_started_by_this_packet"] is False
    assert data["daemon_started_by_this_packet"] is False
    assert data["webhook_started_by_this_packet"] is False
    dump = json.dumps(data).lower()
    assert "secret" not in dump
    assert "token" not in dump


def test_docs_mention_real_money_risk_and_no_live_orders() -> None:
    text = Path(
        "docs/trading_lab/forex/FOREX_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANT_V1.md",
    ).read_text(encoding="utf-8").lower()
    required = (
        "micro-live means real-money live trading risk",
        "approval is limited to a future max-one-live-micro-order runner",
        "does not place live orders",
        "does not move money",
        "does not call broker apis",
        "does not call bitwarden",
        "does not read credentials",
        "does not read `.env`",
        "does not start 22h/6d runtime",
        "advance to controlled_micro_live_exception_runner",
    )
    for phrase in required:
        assert phrase in text
