from __future__ import annotations

import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_runtime_executor_final_gated_v1 import (  # noqa: E402
    FINAL_GATED_BLOCKED_CONTROLS,
    FINAL_GATED_BLOCKED_DRYRUN_NOT_READY,
    FINAL_GATED_BLOCKED_FINAL_CLICK,
    FINAL_GATED_BLOCKED_MISSING_DRYRUN,
    FINAL_GATED_BLOCKED_RUNTIME_CONTEXT,
    FINAL_GATED_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTOR_PACKET,
    RUNTIME_PACKAGE_STATUS,
    evaluate_oanda_demo_runtime_executor_final_gated_v1,
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


def dryrun_ready(**overrides):
    result = {
        "status": "DRYRUN_READY_FOR_OWNER_REVIEW",
        "dryrun_order_payload": {
            "status": "DRYRUN_ONLY_NOT_EXECUTABLE",
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
            "hold_allowed_overnight": False,
        },
        "simulated_execution_steps": [
            "receive final owner-click review object",
            "verify demo broker target",
            "verify live trading blocked",
            "verify credentials are runtime-only and not read in dry-run",
            "verify SL/TP required",
            "verify pre-trade evidence required",
            "simulate order payload shape",
            "stop before broker call",
        ],
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    result.update(overrides)
    return result


def final_owner_click_ready(**overrides):
    result = {
        "status": "FINAL_CLICK_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTION_REVIEW",
        "prepared_order_review": {
            "status": "READY_FOR_EXTERNAL_RUNTIME_EXECUTOR_REVIEW_ONLY",
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
            "hold_allowed_overnight": False,
        },
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    result.update(overrides)
    return result


def runtime_context(**overrides):
    context = {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_environment": True,
        "live_environment": False,
        "runtime_only_credentials_present": True,
        "credential_persistence_detected": False,
        "account_id_persistence_detected": False,
        "kill_switch_ready": True,
        "daily_stop_ready": True,
        "max_loss_gate_ready": True,
        "broker_network_call_performed": False,
        "order_placement_performed": False,
    }
    context.update(overrides)
    return context


def final_gate_controls(**overrides):
    controls = {
        "final_runtime_packet_required": True,
        "owner_runtime_confirmation_required": True,
        "allow_live_trading": False,
        "allow_autonomous_execution": False,
        "allow_scheduler": False,
        "allow_daemon": False,
        "allow_webhook": False,
        "allow_order_placement_in_this_module": False,
        "require_runtime_executor_packet_next": True,
        "require_pre_trade_evidence": True,
        "require_post_trade_evidence": True,
    }
    controls.update(overrides)
    return controls


def evaluate(**overrides):
    payload = {
        "dryrun_result": dryrun_ready(),
        "final_owner_click_result": final_owner_click_ready(),
        "runtime_context": runtime_context(),
        "final_gate_controls": final_gate_controls(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_runtime_executor_final_gated_v1(**payload)


def assert_execution_authority_false(result):
    assert result["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_default_blocks_missing_dryrun():
    result = evaluate_oanda_demo_runtime_executor_final_gated_v1()
    assert result["status"] == FINAL_GATED_BLOCKED_MISSING_DRYRUN
    assert "missing_dryrun_result" in result["blockers"]
    assert_execution_authority_false(result)


def test_dryrun_not_ready_blocks():
    result = evaluate(dryrun_result=dryrun_ready(status="DRYRUN_BLOCKED_RUNTIME_CONTEXT"))
    assert result["status"] == FINAL_GATED_BLOCKED_DRYRUN_NOT_READY
    assert "dryrun_status_not_ready_for_owner_review" in result["blockers"]


def test_missing_final_owner_click_blocks():
    result = evaluate(final_owner_click_result=None)
    assert result["status"] == FINAL_GATED_BLOCKED_FINAL_CLICK
    assert "missing_final_owner_click_result" in result["blockers"]


def test_final_owner_click_not_ready_blocks():
    result = evaluate(
        final_owner_click_result=final_owner_click_ready(
            status="FINAL_CLICK_BLOCKED_RUNTIME_SAFETY"
        )
    )
    assert result["status"] == FINAL_GATED_BLOCKED_FINAL_CLICK
    assert "final_owner_click_status_not_ready" in result["blockers"]


def test_missing_runtime_context_blocks():
    result = evaluate(runtime_context=None)
    assert result["status"] == FINAL_GATED_BLOCKED_RUNTIME_CONTEXT
    assert "missing_runtime_context" in result["blockers"]


def test_runtime_context_live_environment_blocks():
    result = evaluate(runtime_context=runtime_context(live_environment=True))
    assert result["status"] == FINAL_GATED_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_live_environment_must_be_false" in result["blockers"]


def test_runtime_context_missing_runtime_credentials_blocks():
    result = evaluate(runtime_context=runtime_context(runtime_only_credentials_present=False))
    assert result["status"] == FINAL_GATED_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_runtime_only_credentials_present_required" in result["blockers"]


def test_runtime_context_credential_persistence_blocks():
    result = evaluate(runtime_context=runtime_context(credential_persistence_detected=True))
    assert result["status"] == FINAL_GATED_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_credential_persistence_detected_must_be_false" in result["blockers"]


def test_runtime_context_account_id_persistence_blocks():
    result = evaluate(runtime_context=runtime_context(account_id_persistence_detected=True))
    assert result["status"] == FINAL_GATED_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_account_id_persistence_detected_must_be_false" in result["blockers"]


def test_missing_kill_switch_blocks():
    result = evaluate(runtime_context=runtime_context(kill_switch_ready=False))
    assert result["status"] == FINAL_GATED_BLOCKED_RUNTIME_CONTEXT
    assert "runtime_context_kill_switch_ready_required" in result["blockers"]


def test_missing_controls_blocks():
    result = evaluate(final_gate_controls=None)
    assert result["status"] == FINAL_GATED_BLOCKED_CONTROLS
    assert "missing_final_gate_controls" in result["blockers"]


def test_controls_allowing_live_trading_blocks():
    result = evaluate(final_gate_controls=final_gate_controls(allow_live_trading=True))
    assert result["status"] == FINAL_GATED_BLOCKED_CONTROLS
    assert "final_gate_controls_allow_live_trading_must_be_false" in result["blockers"]


def test_controls_allowing_autonomous_execution_blocks():
    result = evaluate(final_gate_controls=final_gate_controls(allow_autonomous_execution=True))
    assert result["status"] == FINAL_GATED_BLOCKED_CONTROLS
    assert "final_gate_controls_allow_autonomous_execution_must_be_false" in result["blockers"]


def test_controls_allowing_order_placement_in_this_module_blocks():
    result = evaluate(final_gate_controls=final_gate_controls(allow_order_placement_in_this_module=True))
    assert result["status"] == FINAL_GATED_BLOCKED_CONTROLS
    assert "final_gate_controls_allow_order_placement_in_this_module_must_be_false" in result[
        "blockers"
    ]


def test_valid_final_gated_package_returns_ready():
    result = evaluate()
    assert result["status"] == FINAL_GATED_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTOR_PACKET


def test_prepared_runtime_package_status_is_ready_for_separate_executor():
    result = evaluate()
    assert result["prepared_runtime_package"]["package_status"] == RUNTIME_PACKAGE_STATUS


def test_required_runtime_actions_include_separate_one_order_executor_packet():
    result = evaluate()
    assert "run separate one-order-only runtime executor packet" in result[
        "required_runtime_actions"
    ]


def test_required_owner_actions_include_demo_only_and_one_order_confirmations():
    result = evaluate()
    assert "confirm demo-only environment" in result["required_owner_actions"]
    assert "confirm one order only" in result["required_owner_actions"]


def test_all_execution_authority_remains_false():
    result = evaluate()
    assert_execution_authority_false(result)


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)
