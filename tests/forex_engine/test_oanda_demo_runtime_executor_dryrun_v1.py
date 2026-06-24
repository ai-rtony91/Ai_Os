from __future__ import annotations

import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_runtime_executor_dryrun_v1 import (  # noqa: E402
    DRYRUN_BLOCKED_CONTROLS,
    DRYRUN_BLOCKED_FINAL_CLICK_NOT_READY,
    DRYRUN_BLOCKED_MISSING_FINAL_CLICK,
    DRYRUN_BLOCKED_RUNTIME_CONTEXT,
    DRYRUN_READY_FOR_OWNER_REVIEW,
    evaluate_oanda_demo_runtime_executor_dryrun_v1,
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


def final_click_ready(**overrides):
    result = {
        "status": "FINAL_CLICK_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTION_REVIEW",
        "prepared_order_review": {
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
            "hold_allowed_overnight": True,
            "final_owner_click_recorded": True,
            "runtime_only_credentials_required": True,
            "status": "READY_FOR_EXTERNAL_RUNTIME_EXECUTOR_REVIEW_ONLY",
        },
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    result.update(overrides)
    return result


def runtime_context(**overrides):
    context = {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "live_environment": False,
        "demo_environment": True,
        "runtime_only_credentials_required": True,
        "runtime_only_credentials_present": False,
        "credential_persistence_detected": False,
        "account_id_persistence_detected": False,
        "broker_network_call_performed": False,
        "order_placement_performed": False,
    }
    context.update(overrides)
    return context


def dryrun_controls(**overrides):
    controls = {
        "dryrun_mode": True,
        "allow_broker_network": False,
        "allow_order_placement": False,
        "allow_credential_read": False,
        "allow_account_id_read": False,
        "require_pre_trade_evidence": True,
        "require_post_trade_evidence": True,
        "require_owner_review_before_real_executor": True,
    }
    controls.update(overrides)
    return controls


def evaluate(**overrides):
    payload = {
        "final_owner_click_result": final_click_ready(),
        "runtime_executor_context": runtime_context(),
        "dryrun_controls": dryrun_controls(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_runtime_executor_dryrun_v1(**payload)


def assert_execution_authority_false(result):
    assert result["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_default_blocks_missing_final_click():
    result = evaluate_oanda_demo_runtime_executor_dryrun_v1()
    assert result["status"] == DRYRUN_BLOCKED_MISSING_FINAL_CLICK
    assert "missing_final_owner_click_result" in result["blockers"]
    assert_execution_authority_false(result)


def test_final_click_not_ready_blocks():
    result = evaluate(final_owner_click_result=final_click_ready(status="FINAL_CLICK_BLOCKED_ORDER_TICKET"))
    assert result["status"] == DRYRUN_BLOCKED_FINAL_CLICK_NOT_READY
    assert "final_owner_click_status_not_ready" in result["blockers"]


def test_missing_runtime_context_blocks():
    result = evaluate(runtime_executor_context=None)
    assert result["status"] == DRYRUN_BLOCKED_RUNTIME_CONTEXT
    assert "missing_runtime_executor_context" in result["blockers"]


def test_runtime_context_with_live_environment_blocks():
    result = evaluate(runtime_executor_context=runtime_context(live_environment=True))
    assert result["status"] == DRYRUN_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_live_environment_must_be_false" in result["blockers"]


def test_runtime_context_with_credentials_present_blocks_for_dryrun():
    result = evaluate(runtime_executor_context=runtime_context(runtime_only_credentials_present=True))
    assert result["status"] == DRYRUN_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_runtime_only_credentials_present_must_be_false" in result["blockers"]


def test_runtime_context_with_broker_network_already_performed_blocks():
    result = evaluate(runtime_executor_context=runtime_context(broker_network_call_performed=True))
    assert result["status"] == DRYRUN_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_broker_network_call_performed_must_be_false" in result["blockers"]


def test_missing_dryrun_controls_blocks():
    result = evaluate(dryrun_controls=None)
    assert result["status"] == DRYRUN_BLOCKED_CONTROLS
    assert "missing_dryrun_controls" in result["blockers"]


def test_dryrun_controls_allowing_broker_network_blocks():
    result = evaluate(dryrun_controls=dryrun_controls(allow_broker_network=True))
    assert result["status"] == DRYRUN_BLOCKED_CONTROLS
    assert "dryrun_controls_allow_broker_network_must_be_false" in result["blockers"]


def test_dryrun_controls_allowing_order_placement_blocks():
    result = evaluate(dryrun_controls=dryrun_controls(allow_order_placement=True))
    assert result["status"] == DRYRUN_BLOCKED_CONTROLS
    assert "dryrun_controls_allow_order_placement_must_be_false" in result["blockers"]


def test_valid_dryrun_returns_ready_for_owner_review():
    result = evaluate()
    assert result["status"] == DRYRUN_READY_FOR_OWNER_REVIEW


def test_dryrun_order_payload_status_is_not_executable():
    result = evaluate()
    assert result["dryrun_order_payload"]["status"] == "DRYRUN_ONLY_NOT_EXECUTABLE"
    assert result["dryrun_order_payload"]["broker_network_call_performed"] is False
    assert result["dryrun_order_payload"]["order_placement_performed"] is False


def test_simulated_execution_steps_stop_before_broker_call():
    result = evaluate()
    assert result["simulated_execution_steps"][-1] == "stop before broker call"


def test_all_execution_authority_remains_false():
    result = evaluate()
    assert_execution_authority_false(result)


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)
