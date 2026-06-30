from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from automation.forex_engine.forex_supervised_demo_evidence_review_v1 import (
    DEMO_ORDER_EVIDENCE_MISSING,
    DEMO_ORDER_NOT_CREATED,
    NEXT_STAGE_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL,
    NEXT_STAGE_REVIEW_DEMO_EVIDENCE,
    PROTECTED_BOUNDARY_VIOLATION,
    REDACTION_REVIEW_REQUIRED,
    SUPERVISED_DEMO_EVIDENCE_CLEAN,
    SupervisedDemoEvidenceReviewInput,
    build_default_input,
    evaluate_supervised_demo_evidence_review_v1,
)
from scripts.forex_delivery.run_forex_supervised_demo_evidence_review_v1 import (
    run_forex_supervised_demo_evidence_review_v1,
)


def _input(**changes) -> SupervisedDemoEvidenceReviewInput:
    return replace(build_default_input(), **changes)


def test_default_input_is_clean():
    result = evaluate_supervised_demo_evidence_review_v1(_input())
    assert result.evidence_status == SUPERVISED_DEMO_EVIDENCE_CLEAN
    assert result.current_stage == "demo_evidence_review"
    assert result.next_stage == NEXT_STAGE_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL


def test_current_state_returns_clean():
    result = evaluate_supervised_demo_evidence_review_v1(_input())
    assert result.supervised_demo_order_attempted is True
    assert result.supervised_demo_order_success is True
    assert result.order_status == "created"
    assert result.order_status_code == 201
    assert result.demo_order_execution is True
    assert result.live_order_execution is False
    assert result.money_movement is False
    assert result.broker_api_called is True
    assert result.state_report_present is True
    assert result.redaction_verified is True
    assert result.max_one_order_verified is True


def test_missing_order_blocks():
    result = evaluate_supervised_demo_evidence_review_v1(
        _input(
            supervised_demo_order_attempted=False,
            state_report_present=False,
        ),
    )
    assert result.evidence_status == DEMO_ORDER_EVIDENCE_MISSING
    assert result.next_stage == NEXT_STAGE_REVIEW_DEMO_EVIDENCE
    assert "supervised_demo_order_attempted is False" in result.blockers
    assert "state_report_present is False" in result.blockers


def test_not_created_order_blocks():
    result = evaluate_supervised_demo_evidence_review_v1(
        _input(
            supervised_demo_order_success=False,
            order_status="not_created",
            order_status_code=400,
        ),
    )
    assert result.evidence_status == DEMO_ORDER_NOT_CREATED
    assert "supervised_demo_order_success is False" in result.blockers
    assert "order_status is not created" in result.blockers
    assert "order_status_code is 400" in result.blockers


def test_redaction_failure_blocks():
    result = evaluate_supervised_demo_evidence_review_v1(
        _input(token_redacted=False),
    )
    assert result.evidence_status == REDACTION_REVIEW_REQUIRED
    assert "token_redacted is False" in result.blockers


def test_protected_boundary_blocks():
    for field in (
        "live_order_execution",
        "money_movement",
        "scheduler_started",
        "daemon_started",
        "webhook_started",
    ):
        result = evaluate_supervised_demo_evidence_review_v1(
            _input(**{field: True}),
        )
        assert result.evidence_status == PROTECTED_BOUNDARY_VIOLATION
        assert result.next_stage == "stop_and_owner_review"
        assert result.live_order_execution is bool(field == "live_order_execution")
        assert result.money_movement is bool(field == "money_movement")
        assert result.scheduler_started is bool(field == "scheduler_started")
        assert result.daemon_started is bool(field == "daemon_started")
        assert result.webhook_started is bool(field == "webhook_started")


def test_runner_writes_state_and_report(tmp_path: Path):
    state_path = tmp_path / "AIOS_FOREX_SUPERVISED_DEMO_EVIDENCE_REVIEW_V1_STATE.json"
    report_path = tmp_path / "AIOS_FOREX_SUPERVISED_DEMO_EVIDENCE_REVIEW_V1_REPORT.md"
    payload = run_forex_supervised_demo_evidence_review_v1(
        state_output=state_path,
        report_output=report_path,
        write_report=True,
    )
    assert state_path.exists()
    assert report_path.exists()
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["result"]["evidence_status"] == SUPERVISED_DEMO_EVIDENCE_CLEAN
    assert state["review_summary"]["ready_for_micro_live_exception"] is True
    assert payload["result"]["next_stage"] == NEXT_STAGE_OWNER_MICRO_LIVE_EXCEPTION_APPROVAL
    assert (
        "SUPERVISED_DEMO_EVIDENCE_CLEAN"
        in report_path.read_text(encoding="utf-8")
    )


def test_config_template_is_valid_and_no_secrets():
    data = json.loads(
        Path(
            "configs/forex/AIOS_FOREX_SUPERVISED_DEMO_EVIDENCE_REVIEW_V1.example.json",
        ).read_text(encoding="utf-8"),
    )
    required = [
        "default_mode",
        "next_stage_after_success",
        "current_stage",
        "state_report_path",
        "report_path",
        "supervised_demo_order_execution_by_this_packet",
        "live_order_execution_by_this_packet",
        "money_movement_by_this_packet",
        "scheduler_started_by_this_packet",
        "daemon_started_by_this_packet",
        "webhook_started_by_this_packet",
        "requires_max_one_order_verification",
        "requires_redaction_verification",
    ]
    for field_name in required:
        assert field_name in data
    assert data["default_mode"] == "dry_run"
    assert data["next_stage_after_success"] == "owner_micro_live_exception_approval"
    assert data["current_stage"] == "demo_evidence_review"
    raw = json.dumps(data).lower()
    assert "token" not in raw
    assert "secret" not in raw


def test_docs_mention_owner_micro_live_exception_approval():
    text = Path(
        "docs/trading_lab/forex/FOREX_SUPERVISED_DEMO_EVIDENCE_REVIEW_V1.md",
    ).read_text(encoding="utf-8")
    required = [
        "supervised demo evidence review",
        "owner_micro_live_exception_approval",
        "does not call broker apis",
        "does not read bitwarden",
        "does not read credentials",
        "does not read `.env`",
        "does not start schedulers",
        "does not start daemons",
        "does not start webhooks",
        "reviewed evidence must be redacted",
        "no live order execution and no money movement",
    ]
    for phrase in required:
        assert phrase in text.lower()
