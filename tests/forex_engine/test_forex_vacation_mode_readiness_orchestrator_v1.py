from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from automation.forex_engine import forex_vacation_mode_readiness_orchestrator_v1 as vm


RUNNER = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "forex_delivery"
    / "run_forex_vacation_mode_readiness_orchestrator_v1.py"
)


def _result(builder=vm.build_sample_ready_input):
    return vm.evaluate_forex_vacation_mode_readiness(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (vm.build_sample_ready_input, vm.VACATION_MODE_READY),
        (vm.build_sample_partial_input, vm.VACATION_MODE_REQUIRE_MORE_EVIDENCE),
        (vm.build_sample_unsafe_input, vm.VACATION_MODE_BLOCKED_UNSAFE),
        (
            vm.build_sample_schema_invalid_input,
            vm.VACATION_MODE_BLOCKED_SCHEMA_INVALID,
        ),
    ),
)
def test_sample_classifications(builder, classification: str):
    assert _result(builder).classification == classification


@pytest.mark.parametrize("flag_name", vm.PROTECTED_FLAG_NAMES)
def test_protected_flags_are_false(flag_name: str):
    result = _result()
    assert result.protected_flags[flag_name] is False
    assert getattr(result, flag_name) is False


def test_no_broker_action_is_authorized():
    result = _result()
    assert result.broker_action_authorized is False
    assert result.broker_action_allowed is False
    assert "broker_call" in result.blocked_actions


def test_no_live_trading_is_authorized():
    result = _result()
    assert result.live_trading_authorized is False
    assert result.live_trading_allowed is False
    assert result.live_execution_allowed is False
    assert "live_trading" in result.blocked_actions


def test_no_compounding_is_authorized():
    result = _result()
    assert result.compounding_authorized is False
    assert result.compounding_allowed is False
    assert "compounding" in result.blocked_actions


def test_no_autonomous_execution_is_authorized():
    result = _result()
    assert result.autonomous_execution_authorized is False
    assert result.autonomous_execution_allowed is False
    assert "autonomous_execution" in result.blocked_actions


def test_sos_readiness_is_evaluated_but_no_alert_is_sent():
    result = _result()
    assert "sos_alert_ready" in result.ready_surfaces
    assert result.sos_alert_evaluated is True
    assert result.sos_alert_sent is False


def test_readiness_percent_is_calculated_correctly():
    ready = _result(vm.build_sample_ready_input)
    partial = _result(vm.build_sample_partial_input)
    assert ready.readiness_percent == 100.0
    expected_partial = round(
        (partial.ready_surface_count / partial.total_surface_count) * 100,
        2,
    )
    assert partial.readiness_percent == expected_partial
    assert partial.ready_surface_count == 25
    assert partial.total_surface_count == 36


def test_next_safe_action_is_explicit():
    result = _result()
    assert "Review the build-only Vacation Mode readiness result" in result.next_safe_action
    assert "do not approve live execution" in result.next_safe_action


def test_unsafe_sample_reports_unsafe_fragments_but_output_flags_stay_false():
    result = _result(vm.build_sample_unsafe_input)
    assert result.classification == vm.VACATION_MODE_BLOCKED_UNSAFE
    assert result.unsafe_fragments_detected
    assert result.protected_flags["broker_action_allowed"] is False
    assert result.protected_flags["live_trading_allowed"] is False
    assert result.protected_flags["compounding_allowed"] is False
    assert result.protected_flags["autonomous_execution_allowed"] is False


def test_schema_invalid_sample_reports_missing_or_invalid_fields():
    result = _result(vm.build_sample_schema_invalid_input)
    assert result.classification == vm.VACATION_MODE_BLOCKED_SCHEMA_INVALID
    assert any("protected_flags" in item for item in result.unsafe_fragments_detected)
    assert any("readiness_surfaces" in item for item in result.unsafe_fragments_detected)


def test_json_serializable():
    payload = json.dumps(vm.to_jsonable_dict(_result()))
    assert "VACATION_MODE_READY" in payload


def test_markdown_output():
    text = vm.to_markdown(_result())
    assert text.startswith("# AIOS Forex Vacation Mode Readiness Orchestrator V1")
    assert "No OANDA call was made by this packet." in text


def test_cli_json_works():
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--sample-ready", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["classification"] == vm.VACATION_MODE_READY
    assert payload["ready_surface_count"] == 36


def test_cli_markdown_works():
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--sample-ready", "--markdown"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.startswith(
        "# AIOS Forex Vacation Mode Readiness Orchestrator V1"
    )
    assert "Classification: `VACATION_MODE_READY`" in completed.stdout


@pytest.mark.parametrize(
    "forbidden_true",
    (
        '"live_trading_allowed": true',
        '"live_execution_allowed": true',
        '"broker_action_allowed": true',
        '"credential_access_allowed": true',
        '"account_id_persistence_allowed": true',
        '"autonomous_execution_allowed": true',
        '"compounding_allowed": true',
        '"bank_movement_allowed": true',
        '"scheduler_allowed": true',
        '"daemon_allowed": true',
        '"webhook_allowed": true',
        '"unattended_vacation_mode_allowed": true',
        '"vacation_profit_trial_allowed": true',
        '"next_trade_authorized": true',
        '"repeat_trade_authorized": true',
        '"selected_packet_execution_authorized": true',
        '"codex_live_execution_authorized": true',
        '"owner_live_execution_approval_present": true',
    ),
)
def test_json_has_no_protected_true_flags(forbidden_true: str):
    payload = json.dumps(vm.to_jsonable_dict(_result())).lower()
    assert forbidden_true not in payload
