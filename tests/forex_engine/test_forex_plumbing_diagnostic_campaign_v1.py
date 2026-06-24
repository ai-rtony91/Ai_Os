from __future__ import annotations

import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.forex_plumbing_diagnostic_campaign_v1 import (  # noqa: E402
    DIAGNOSTIC_BLOCKED_FAILURES,
    DIAGNOSTIC_BLOCKED_MISSING_INPUTS,
    DIAGNOSTIC_READY_FOR_DEMO_ATTEMPT_REVIEW,
    DIAGNOSTIC_READY_FOR_OWNER_REVIEW,
    evaluate_forex_plumbing_diagnostic_campaign_v1,
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


def passing_checks(morning_proof_pending=True):
    checks = {
        "end_to_end_dry_run_ticket": {
            "passed": True,
            "ticket_created": True,
            "review_only": True,
            "evidence_summary": {"ticket_status": "REVIEW_ONLY_NOT_EXECUTABLE"},
        },
        "oanda_demo_read_only_connection_model": {
            "passed": True,
            "read_only_model_ready": True,
            "broker_network_call_performed": False,
            "credential_read_performed": False,
            "evidence_summary": {"environment": "OANDA_DEMO_READ_ONLY_MODEL"},
        },
        "fake_buy_sell_ticket_replay": {
            "passed": True,
            "buy_replay_passed": True,
            "sell_replay_passed": True,
            "evidence_summary": {"buy": "PASS", "sell": "PASS"},
        },
        "risk_failure_gate": {
            "passed": True,
            "risk_failure_blocked": True,
            "stop_loss_failure_blocked": True,
            "take_profit_failure_blocked": True,
            "evidence_summary": {"risk_failures_blocked": True},
        },
        "evidence_capture": {
            "passed": True,
            "pre_trade_capture_ready": True,
            "post_trade_capture_ready": True,
            "sanitized_evidence_only": True,
            "evidence_summary": {"sanitized_evidence_only": True},
        },
        "overnight_protection": {
            "passed": True,
            "kill_switch_ready": True,
            "daily_stop_ready": True,
            "max_loss_gate_ready": True,
            "overnight_risk_note_ready": True,
            "evidence_summary": {"overnight_protection_ready": True},
        },
        "compounding_bucket": {
            "passed": True,
            "bucket_supervisor_ready": True,
            "force_trades_to_hit_quota": False,
            "eligible_pair_allocation_ready": True,
            "evidence_summary": {"bucket_cycle_ready": True},
        },
        "final_owner_click_dry_run_rehearsal": {
            "passed": True,
            "owner_click_rehearsed": True,
            "final_confirmation_required": True,
            "order_placement_performed": False,
            "evidence_summary": {"owner_click_dry_run_only": True},
        },
        "demo_micro_trade_readiness_review_only": {
            "passed": True,
            "review_only_ready": True,
            "owner_review_required": True,
            "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
            "evidence_summary": {"review_only_ready": True},
        },
        "morning_proof_review_model": {
            "pending": morning_proof_pending,
            "proof_review_model_ready": not morning_proof_pending,
            "realized_pl_capture_ready": not morning_proof_pending,
            "evidence_summary": {"pending_until_after_overnight_result": morning_proof_pending},
        },
    }
    if not morning_proof_pending:
        checks["morning_proof_review_model"]["passed"] = True
    return checks


def evaluate(checks=None):
    selected_checks = passing_checks() if checks is None else checks
    return evaluate_forex_plumbing_diagnostic_campaign_v1({"checks": selected_checks})


def result_by_id(result, check_id):
    return {item["check_id"]: item for item in result["diagnostic_results"]}[check_id]


def assert_execution_authority_false(result):
    assert result["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_default_blocks_missing_inputs():
    result = evaluate_forex_plumbing_diagnostic_campaign_v1()
    assert result["status"] == DIAGNOSTIC_BLOCKED_MISSING_INPUTS
    assert "missing_diagnostic_inputs" in result["blockers"]
    assert_execution_authority_false(result)


def test_all_missing_diagnostics_blocks():
    result = evaluate(checks={})
    assert result["status"] == DIAGNOSTIC_BLOCKED_FAILURES
    assert "end_to_end_dry_run_ticket_not_run" in result["blockers"]


def test_one_required_failure_blocks():
    checks = passing_checks()
    checks["risk_failure_gate"]["passed"] = False
    result = evaluate(checks)
    assert result["status"] == DIAGNOSTIC_BLOCKED_FAILURES
    assert result_by_id(result, "risk_failure_gate")["status"] == "FAIL"


def test_one_required_blocked_check_blocks():
    checks = passing_checks()
    checks["overnight_protection"]["blocked"] = True
    result = evaluate(checks)
    assert result["status"] == DIAGNOSTIC_BLOCKED_FAILURES
    assert result_by_id(result, "overnight_protection")["status"] == "BLOCKED"


def test_checks_1_to_8_pass_and_9_ready_with_10_pending_returns_demo_attempt_review():
    result = evaluate(passing_checks(morning_proof_pending=True))
    assert result["status"] == DIAGNOSTIC_READY_FOR_DEMO_ATTEMPT_REVIEW
    assert result_by_id(result, "morning_proof_review_model")["status"] == "NOT_RUN"


def test_all_ten_pass_returns_owner_review_ready():
    result = evaluate(passing_checks(morning_proof_pending=False))
    assert result["status"] == DIAGNOSTIC_READY_FOR_OWNER_REVIEW
    assert result["pass_count"] == 10


def test_demo_micro_trade_readiness_remains_review_only():
    result = evaluate()
    check = result_by_id(result, "demo_micro_trade_readiness_review_only")
    assert check["status"] == "PASS"
    assert check["evidence_summary"]["review_only_ready"] is True
    assert check["evidence_summary"]["order_placement_allowed"] is False


def test_morning_proof_can_be_pending_before_overnight_result():
    result = evaluate()
    check = result_by_id(result, "morning_proof_review_model")
    assert check["status"] == "NOT_RUN"
    assert check["required"] is False
    assert "morning_proof_pending_until_after_overnight_result" in check["blockers"]


def test_all_execution_authority_remains_false():
    result = evaluate()
    assert_execution_authority_false(result)


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)
