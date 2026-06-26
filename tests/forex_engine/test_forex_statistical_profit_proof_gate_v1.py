from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from automation.forex_engine import forex_statistical_profit_proof_gate_v1 as gate


RUNNER = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "forex_delivery"
    / "run_forex_statistical_profit_proof_gate_v1.py"
)


def _result(builder=gate.build_sample_ready_input):
    return gate.evaluate_forex_statistical_profit_proof_gate(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (gate.build_sample_ready_input, gate.STATISTICAL_PROFIT_PROOF_READY),
        (
            gate.build_sample_partial_input,
            gate.STATISTICAL_PROFIT_REQUIRE_MORE_EVIDENCE,
        ),
        (gate.build_sample_unsafe_input, gate.STATISTICAL_PROFIT_BLOCKED_UNSAFE),
        (
            gate.build_sample_schema_invalid_input,
            gate.STATISTICAL_PROFIT_BLOCKED_SCHEMA_INVALID,
        ),
    ),
)
def test_sample_classifications(builder, classification: str):
    assert _result(builder).classification == classification


@pytest.mark.parametrize("flag_name", gate.PROTECTED_FLAG_NAMES)
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
    assert "live_execution" in result.blocked_actions


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


def test_no_vacation_mode_execution_is_authorized():
    result = _result()
    assert result.vacation_mode_execution_authorized is False
    assert result.unattended_vacation_mode_allowed is False
    assert result.vacation_profit_trial_allowed is False
    assert result.statistical_profit_gate_authorizes_vacation_mode is False
    assert "vacation_mode_execution" in result.blocked_actions


def test_statistical_percent_is_calculated_correctly():
    ready = _result(gate.build_sample_ready_input)
    partial = _result(gate.build_sample_partial_input)
    assert ready.statistical_percent == 100.0
    expected_partial = round(
        (partial.ready_surface_count / partial.total_surface_count) * 100,
        2,
    )
    assert partial.statistical_percent == expected_partial
    assert partial.ready_surface_count < partial.total_surface_count
    assert partial.total_surface_count == 32


def test_missing_surfaces_are_reported():
    result = _result(gate.build_sample_partial_input)
    assert result.missing_surfaces
    assert "minimum_trade_count_met" in result.missing_surfaces
    assert "profit_factor_threshold_met" in result.missing_surfaces
    assert "result_distribution_ready" in result.missing_surfaces


def test_blocked_actions_are_reported():
    result = _result()
    assert set(
        (
            "broker_call",
            "oanda_api_call",
            "credential_access",
            "env_read",
            "account_id_access",
            "account_id_persistence",
            "order_placement",
            "live_execution",
            "autonomous_execution",
            "compounding",
            "bank_movement",
            "scheduler",
            "daemon",
            "webhook",
            "uncontrolled_retry",
            "selected_packet_execution",
            "commit",
            "push",
            "pr",
            "merge",
            "vacation_mode_execution",
        )
    ).issubset(set(result.blocked_actions))


def test_blocked_claims_are_reported():
    result = _result()
    assert set(
        (
            "guaranteed_profit",
            "future_profit",
            "final_statistical_profitability",
            "production_readiness",
            "vacation_mode_readiness",
            "autonomous_trading_readiness",
            "compounding_readiness",
            "live_execution_readiness",
            "profitable_22_6_operation_confirmed",
        )
    ).issubset(set(result.blocked_claims))


def test_next_packet_preview_is_supervised_compounding_policy_gate():
    assert _result().next_packet_preview == gate.NEXT_PACKET_PREVIEW
    assert (
        _result().next_packet_preview
        == "AIOS-FOREX-SUPERVISED-COMPOUNDING-POLICY-GATE-V1"
    )


def test_next_safe_action_is_explicit():
    result = _result()
    assert "Review the statistical profit proof result" in result.next_safe_action
    assert "do not approve broker access" in result.next_safe_action


def test_unsafe_sample_reports_unsafe_fragments_but_output_flags_stay_false():
    result = _result(gate.build_sample_unsafe_input)
    assert result.classification == gate.STATISTICAL_PROFIT_BLOCKED_UNSAFE
    assert result.unsafe_fragments_detected
    assert result.protected_flags["broker_action_allowed"] is False
    assert result.protected_flags["live_execution_allowed"] is False
    assert result.protected_flags["compounding_allowed"] is False
    assert result.protected_flags["autonomous_execution_allowed"] is False
    assert result.statistical_profit_gate_authorizes_vacation_mode is False


def test_schema_invalid_sample_reports_schema_errors():
    result = _result(gate.build_sample_schema_invalid_input)
    assert result.classification == gate.STATISTICAL_PROFIT_BLOCKED_SCHEMA_INVALID
    assert any(
        "source_quality_gate_result" in item
        for item in result.unsafe_fragments_detected
    )
    assert any(
        "statistical_surface_overrides" in item
        for item in result.unsafe_fragments_detected
    )


def test_json_serializable():
    payload = json.dumps(gate.to_jsonable_dict(_result()))
    assert "STATISTICAL_PROFIT_PROOF_READY" in payload


def test_dataclass_like_input_is_accepted():
    class AttributeInput:
        source_quality_gate_result = gate.build_sample_ready_input().source_quality_gate_result
        statistical_surface_overrides = {}
        owner_statistical_label = "pending_owner_review"
        owner_notes_sanitized = "attribute style input"

    result = gate.evaluate_forex_statistical_profit_proof_gate(AttributeInput())
    assert result.classification == gate.STATISTICAL_PROFIT_PROOF_READY


def test_markdown_output():
    text = gate.to_markdown(_result())
    assert text.startswith("# AIOS Forex Statistical Profit Proof Gate V1")
    assert "No SOS alert was sent." in text


def test_cli_json_works():
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--sample-ready", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["classification"] == gate.STATISTICAL_PROFIT_PROOF_READY
    assert payload["ready_surface_count"] == 32


def test_cli_markdown_works():
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--sample-ready", "--markdown"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.startswith("# AIOS Forex Statistical Profit Proof Gate V1")
    assert "Classification: `STATISTICAL_PROFIT_PROOF_READY`" in completed.stdout


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
        '"statistical_profit_gate_authorizes_trading": true',
        '"statistical_profit_gate_authorizes_execution": true',
        '"statistical_profit_gate_authorizes_compounding": true',
        '"statistical_profit_gate_authorizes_vacation_mode": true',
    ),
)
def test_json_has_no_protected_true_flags(forbidden_true: str):
    payload = json.dumps(gate.to_jsonable_dict(_result())).lower()
    assert forbidden_true not in payload
