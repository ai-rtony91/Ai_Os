from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from automation.forex_engine.forex_owner_micro_live_exception_approval_v1 import (
    CURRENT_STAGE,
    MICRO_LIVE_CONTROL_CONFIRMATION_REQUIRED,
    NEXT_STAGE_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER,
    OWNER_LIVE_RISK_ACK_REQUIRED,
    OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED,
    OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED,
    PROTECTED_BOUNDARY_VIOLATION,
    SUPERVISED_DEMO_EVIDENCE_REQUIRED,
    OwnerMicroLiveExceptionApprovalInput,
    build_default_input,
    evaluate_owner_micro_live_exception_approval_v1,
)
from scripts.forex_delivery import run_forex_owner_micro_live_exception_approval_v1 as runtime_script


def _input(**changes) -> OwnerMicroLiveExceptionApprovalInput:
    return replace(build_default_input(), **changes)


def test_default_status_requires_owner_approval() -> None:
    result = evaluate_owner_micro_live_exception_approval_v1(_input())
    assert result.owner_approval_status == OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED
    assert result.current_stage == CURRENT_STAGE
    assert result.next_stage == CURRENT_STAGE


def test_missing_supervised_demo_evidence_blocks() -> None:
    result = evaluate_owner_micro_live_exception_approval_v1(
        _input(supervised_demo_evidence_clean=False, demo_order_status_code=400),
    )
    assert result.owner_approval_status == SUPERVISED_DEMO_EVIDENCE_REQUIRED
    assert result.next_stage == "demo_evidence_review"
    assert "supervised_demo_evidence_clean is False" in result.blockers
    assert "demo_order_status_code is 400" in result.blockers


def test_missing_owner_live_risk_acknowledgment_blocks() -> None:
    result = evaluate_owner_micro_live_exception_approval_v1(
        _input(
            owner_micro_live_exception_approval=True,
            owner_understands_live_money_risk=False,
        ),
    )
    assert result.owner_approval_status == OWNER_LIVE_RISK_ACK_REQUIRED
    assert result.next_stage == CURRENT_STAGE
    assert "owner_understands_live_money_risk is False" in result.blockers


def test_missing_control_confirmations_block() -> None:
    result = evaluate_owner_micro_live_exception_approval_v1(
        _input(
            owner_micro_live_exception_approval=True,
            owner_confirms_no_autonomous_runtime=False,
        ),
    )
    assert result.owner_approval_status == MICRO_LIVE_CONTROL_CONFIRMATION_REQUIRED
    assert result.next_stage == CURRENT_STAGE
    assert "owner_confirms_no_autonomous_runtime is False" in result.blockers


def test_protected_boundary_flags_block() -> None:
    result = evaluate_owner_micro_live_exception_approval_v1(
        _input(
            owner_micro_live_exception_approval=True,
            live_order_execution=True,
        ),
    )
    assert result.owner_approval_status == PROTECTED_BOUNDARY_VIOLATION
    assert result.next_stage == "stop_and_owner_review"


def test_all_confirmations_true_grants_approval() -> None:
    result = evaluate_owner_micro_live_exception_approval_v1(
        _input(
            owner_micro_live_exception_approval=True,
        ),
    )
    assert result.owner_approval_status == OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED
    assert result.next_stage == NEXT_STAGE_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER


def test_output_boundaries_remain_disabled() -> None:
    result = evaluate_owner_micro_live_exception_approval_v1(_input(owner_micro_live_exception_approval=True))
    assert result.owner_approval_status == OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED
    assert result.live_order_execution is False
    assert result.money_movement is False
    assert result.broker_api_called is False
    assert result.bitwarden_cli_called is False
    assert result.credentials_read is False
    assert result.env_file_read is False
    assert result.scheduler_started is False
    assert result.daemon_started is False
    assert result.webhook_started is False


def test_runner_writes_state_and_report(tmp_path: Path) -> None:
    state_path = tmp_path / "AIOS_FOREX_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_V1_STATE.json"
    report_path = tmp_path / "AIOS_FOREX_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_V1_REPORT.md"
    payload = runtime_script.run_forex_owner_micro_live_exception_approval_v1(
        state_output=state_path,
        report_output=report_path,
        write_report=True,
    )
    assert state_path.exists()
    assert report_path.exists()

    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert (
        state["approval_summary"]["next_stage_after_success"]
        == NEXT_STAGE_CONTROLLED_MICRO_LIVE_EXCEPTION_RUNNER
    )
    assert state["result"]["next_stage"] == CURRENT_STAGE
    assert "owner_micro_live_exception_approval" in state["input"]
    assert state["result"]["owner_approval_status"] == OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED
    assert "OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED" in report_path.read_text(
        encoding="utf-8",
    )


def test_config_template_valid_and_no_secrets() -> None:
    data = json.loads(
        Path(
            "configs/forex/AIOS_FOREX_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_V1.example.json",
        ).read_text(encoding="utf-8"),
    )
    assert data["default_mode"] == "dry_run"
    assert data["current_stage"] == "owner_micro_live_exception_approval"
    assert data["next_stage_after_success"] == "controlled_micro_live_exception_runner"
    assert data["micro_live_max_orders"] == 1
    assert data["micro_live_size_policy"] == "minimum_owner_approved_size_only"
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
        "docs/trading_lab/forex/FOREX_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_V1.md",
    ).read_text(encoding="utf-8").lower()
    required = [
        "micro-live means real-money live trading risk",
        "does not place live orders",
        "does not move money",
        "does not call broker apis",
        "does not call bitwarden",
        "does not read credentials",
        "does not read `.env`",
        "advance to controlled_micro_live_exception_runner",
    ]
    for phrase in required:
        assert phrase in text
