from __future__ import annotations

import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_final_owner_click_order_bridge_v1 import (  # noqa: E402
    FINAL_CLICK_BLOCKED_DIAGNOSTICS_NOT_READY,
    FINAL_CLICK_BLOCKED_MISSING_DIAGNOSTICS,
    FINAL_CLICK_BLOCKED_ORDER_TICKET,
    FINAL_CLICK_BLOCKED_OWNER_CLICK,
    FINAL_CLICK_BLOCKED_RUNTIME_SAFETY,
    FINAL_CLICK_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTION_REVIEW,
    evaluate_oanda_demo_final_owner_click_order_bridge_v1,
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


FIRST_EIGHT_DIAGNOSTICS = (
    "end_to_end_dry_run_ticket",
    "oanda_demo_read_only_connection_model",
    "fake_buy_sell_ticket_replay",
    "risk_failure_gate",
    "evidence_capture",
    "overnight_protection",
    "compounding_bucket",
    "final_owner_click_dry_run_rehearsal",
)


def plumbing_ready(**overrides):
    diagnostic_results = [
        {
            "check_id": check_id,
            "name": check_id,
            "status": "PASS",
            "required": True,
            "blockers": [],
            "evidence_summary": {},
            "next_action": "no_action_required",
        }
        for check_id in FIRST_EIGHT_DIAGNOSTICS
    ]
    diagnostic_results.append(
        {
            "check_id": "demo_micro_trade_readiness_review_only",
            "name": "demo readiness",
            "status": "PASS",
            "required": True,
            "blockers": [],
            "evidence_summary": {
                "review_only_ready": True,
                "order_placement_allowed": False,
            },
            "next_action": "no_action_required",
        }
    )
    diagnostic_results.append(
        {
            "check_id": "morning_proof_review_model",
            "name": "morning proof",
            "status": "NOT_RUN",
            "required": False,
            "blockers": ["morning_proof_pending_until_after_overnight_result"],
            "evidence_summary": {"pending_until_after_overnight_result": True},
            "next_action": "run_morning_proof_review_after_demo_attempt_result",
        }
    )
    result = {
        "status": "DIAGNOSTIC_READY_FOR_DEMO_ATTEMPT_REVIEW",
        "diagnostic_results": diagnostic_results,
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    result.update(overrides)
    return result


def order_ticket_result(overnight=False, **overrides):
    result = {
        "status": "ORDER_TICKET_READY_FOR_OWNER_RUNTIME_REVIEW",
        "order_ticket": {
            "broker": "OANDA_DEMO",
            "environment": "DEMO",
            "instrument": "EUR_USD",
            "direction": "BUY",
            "order_type": "MARKET",
            "time_in_force": "FOK",
            "planned_entry": 1.1,
            "stop_loss": 1.095,
            "take_profit": 1.11,
            "position_size_units": 100,
            "risk_amount": 5.0,
            "reward_risk_ratio": 2.0,
            "hold_allowed_overnight": overnight,
            "pre_trade_evidence_required": True,
            "post_trade_evidence_required": True,
            "owner_final_click_required": True,
            "runtime_only_credentials_required": True,
            "live_trading_allowed": False,
            "autonomous_order_allowed": False,
            "status": "REVIEW_ONLY_NOT_EXECUTABLE",
        },
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    result.update(overrides)
    return result


def owner_click(**overrides):
    click = {
        "owner_final_click_required": True,
        "owner_clicked_final_demo_review": True,
        "owner_understands_demo_only": True,
        "owner_understands_no_profit_guarantee": True,
        "owner_understands_loss_possible": True,
        "owner_understands_stop_loss_required": True,
        "owner_understands_take_profit_required": True,
        "owner_approves_overnight_hold_if_ticket_allows": False,
        "owner_approves_live_trading": False,
        "owner_approves_autonomous_execution": False,
    }
    click.update(overrides)
    return click


def runtime_safety(**overrides):
    safety = {
        "broker": "OANDA_DEMO",
        "demo_environment": True,
        "live_environment": False,
        "runtime_only_credentials_present": True,
        "credential_persistence_detected": False,
        "account_id_persistence_detected": False,
        "kill_switch_ready": True,
        "daily_stop_ready": True,
        "max_loss_gate_ready": True,
        "stop_loss_attached_required": True,
        "take_profit_attached_required": True,
        "broker_network_call_performed": False,
        "order_placement_performed": False,
    }
    safety.update(overrides)
    return safety


def evaluate(**overrides):
    payload = {
        "plumbing_diagnostic_result": plumbing_ready(),
        "runtime_order_ticket_result": order_ticket_result(),
        "owner_final_click": owner_click(),
        "runtime_safety_context": runtime_safety(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_final_owner_click_order_bridge_v1(**payload)


def assert_execution_authority_false(result):
    assert result["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_default_blocks_missing_diagnostics():
    result = evaluate_oanda_demo_final_owner_click_order_bridge_v1()
    assert result["status"] == FINAL_CLICK_BLOCKED_MISSING_DIAGNOSTICS
    assert "missing_plumbing_diagnostic_result" in result["blockers"]
    assert_execution_authority_false(result)


def test_diagnostics_not_ready_blocks():
    result = evaluate(plumbing_diagnostic_result=plumbing_ready(status="DIAGNOSTIC_BLOCKED_FAILURES"))
    assert result["status"] == FINAL_CLICK_BLOCKED_DIAGNOSTICS_NOT_READY


def test_missing_order_ticket_blocks():
    result = evaluate(runtime_order_ticket_result=None)
    assert result["status"] == FINAL_CLICK_BLOCKED_ORDER_TICKET
    assert "missing_runtime_order_ticket_result" in result["blockers"]


def test_order_ticket_not_ready_blocks():
    result = evaluate(
        runtime_order_ticket_result=order_ticket_result(status="ORDER_TICKET_BLOCKED_RISK")
    )
    assert result["status"] == FINAL_CLICK_BLOCKED_ORDER_TICKET


def test_missing_owner_final_click_blocks():
    result = evaluate(owner_final_click=None)
    assert result["status"] == FINAL_CLICK_BLOCKED_OWNER_CLICK
    assert "missing_owner_final_click" in result["blockers"]


def test_owner_approving_live_trading_blocks():
    result = evaluate(owner_final_click=owner_click(owner_approves_live_trading=True))
    assert result["status"] == FINAL_CLICK_BLOCKED_OWNER_CLICK
    assert "owner_approves_live_trading_must_be_false" in result["blockers"]


def test_owner_approving_autonomous_execution_blocks():
    result = evaluate(owner_final_click=owner_click(owner_approves_autonomous_execution=True))
    assert result["status"] == FINAL_CLICK_BLOCKED_OWNER_CLICK
    assert "owner_approves_autonomous_execution_must_be_false" in result["blockers"]


def test_missing_no_profit_guarantee_acknowledgement_blocks():
    result = evaluate(
        owner_final_click=owner_click(owner_understands_no_profit_guarantee=False)
    )
    assert result["status"] == FINAL_CLICK_BLOCKED_OWNER_CLICK
    assert "owner_understands_no_profit_guarantee_required" in result["blockers"]


def test_missing_runtime_safety_context_blocks():
    result = evaluate(runtime_safety_context=None)
    assert result["status"] == FINAL_CLICK_BLOCKED_RUNTIME_SAFETY
    assert "missing_runtime_safety_context" in result["blockers"]


def test_runtime_safety_live_environment_blocks():
    result = evaluate(runtime_safety_context=runtime_safety(live_environment=True))
    assert result["status"] == FINAL_CLICK_BLOCKED_RUNTIME_SAFETY
    assert "runtime_safety_live_environment_must_be_false" in result["blockers"]


def test_runtime_safety_credential_persistence_blocks():
    result = evaluate(
        runtime_safety_context=runtime_safety(credential_persistence_detected=True)
    )
    assert result["status"] == FINAL_CLICK_BLOCKED_RUNTIME_SAFETY
    assert "runtime_safety_credential_persistence_detected_must_be_false" in result["blockers"]


def test_missing_kill_switch_blocks():
    result = evaluate(runtime_safety_context=runtime_safety(kill_switch_ready=False))
    assert result["status"] == FINAL_CLICK_BLOCKED_RUNTIME_SAFETY
    assert "runtime_safety_kill_switch_ready_required" in result["blockers"]


def test_missing_stop_loss_required_blocks():
    result = evaluate(runtime_safety_context=runtime_safety(stop_loss_attached_required=False))
    assert result["status"] == FINAL_CLICK_BLOCKED_RUNTIME_SAFETY
    assert "runtime_safety_stop_loss_attached_required_required" in result["blockers"]


def test_missing_take_profit_required_blocks():
    result = evaluate(runtime_safety_context=runtime_safety(take_profit_attached_required=False))
    assert result["status"] == FINAL_CLICK_BLOCKED_RUNTIME_SAFETY
    assert "runtime_safety_take_profit_attached_required_required" in result["blockers"]


def test_valid_non_overnight_final_click_returns_ready():
    result = evaluate()
    assert result["status"] == FINAL_CLICK_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTION_REVIEW


def test_valid_overnight_final_click_requires_overnight_approval():
    blocked = evaluate(runtime_order_ticket_result=order_ticket_result(overnight=True))
    assert blocked["status"] == FINAL_CLICK_BLOCKED_OWNER_CLICK
    assert "owner_overnight_hold_approval_required_for_overnight_ticket" in blocked["blockers"]

    ready = evaluate(
        runtime_order_ticket_result=order_ticket_result(overnight=True),
        owner_final_click=owner_click(owner_approves_overnight_hold_if_ticket_allows=True),
    )
    assert ready["status"] == FINAL_CLICK_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTION_REVIEW


def test_prepared_order_review_status_is_external_runtime_review_only():
    result = evaluate()
    assert result["prepared_order_review"]["status"] == (
        "READY_FOR_EXTERNAL_RUNTIME_EXECUTOR_REVIEW_ONLY"
    )


def test_all_execution_authority_remains_false():
    result = evaluate()
    assert_execution_authority_false(result)


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)
