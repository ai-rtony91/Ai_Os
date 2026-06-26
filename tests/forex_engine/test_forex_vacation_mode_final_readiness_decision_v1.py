from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from automation.forex_engine import forex_vacation_mode_final_readiness_decision_v1 as gate


RUNNER = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "forex_delivery"
    / "run_forex_vacation_mode_final_readiness_decision_v1.py"
)


def _result(builder=gate.build_sample_ready_input):
    return gate.evaluate_forex_vacation_mode_final_readiness_decision(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (gate.build_sample_ready_input, gate.VACATION_MODE_READY),
        (gate.build_sample_partial_input, gate.VACATION_MODE_REQUIRE_MORE_EVIDENCE),
        (gate.build_sample_unsafe_input, gate.VACATION_MODE_BLOCKED_UNSAFE),
        (gate.build_sample_schema_invalid_input, gate.VACATION_MODE_BLOCKED_SCHEMA_INVALID),
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


def test_no_oanda_call_is_authorized():
    result = _result()
    assert result.oanda_api_call_authorized is False
    assert result.oanda_api_call_allowed is False
    assert "oanda_api_call" in result.blocked_actions


def test_no_credential_or_env_access_is_authorized():
    result = _result()
    assert result.credential_access_authorized is False
    assert result.credential_access_allowed is False
    assert result.env_read_authorized is False
    assert result.env_read_allowed is False
    assert "credential_access" in result.blocked_actions
    assert "env_read" in result.blocked_actions


def test_no_account_id_access_or_persistence_is_authorized():
    result = _result()
    assert result.account_id_access_authorized is False
    assert result.account_id_access_allowed is False
    assert result.account_id_persistence_authorized is False
    assert result.account_id_persistence_allowed is False


def test_no_raw_transaction_or_order_id_access_is_authorized():
    result = _result()
    assert result.raw_transaction_id_access_authorized is False
    assert result.raw_transaction_id_access_allowed is False
    assert result.raw_order_id_access_authorized is False
    assert result.raw_order_id_access_allowed is False
    assert "raw_transaction_id_access" in result.blocked_actions
    assert "raw_order_id_access" in result.blocked_actions


def test_no_order_placement_is_authorized():
    result = _result()
    assert result.order_placement_authorized is False
    assert result.order_placement_allowed is False
    assert "order_placement" in result.blocked_actions


def test_no_live_trading_or_execution_is_authorized():
    result = _result()
    assert result.live_trading_authorized is False
    assert result.live_trading_allowed is False
    assert result.live_execution_authorized is False
    assert result.live_execution_allowed is False
    assert "live_execution" in result.blocked_actions


def test_no_compounding_execution_is_authorized():
    result = _result()
    assert result.compounding_execution_authorized is False
    assert result.compounding_allowed is False
    assert "compounding_execution" in result.blocked_actions


def test_no_autonomous_execution_is_authorized():
    result = _result()
    assert result.autonomous_execution_authorized is False
    assert result.autonomous_execution_allowed is False
    assert "autonomous_execution" in result.blocked_actions


def test_no_bank_movement_withdrawal_or_deposit_is_authorized():
    result = _result()
    assert result.bank_movement_authorized is False
    assert result.bank_movement_allowed is False
    assert result.withdrawal_authorized is False
    assert result.withdrawal_allowed is False
    assert result.deposit_authorized is False
    assert result.deposit_allowed is False


def test_no_scheduler_daemon_webhook_is_authorized():
    result = _result()
    assert result.scheduler_allowed is False
    assert result.daemon_allowed is False
    assert result.webhook_allowed is False
    assert {"scheduler", "daemon", "webhook"}.issubset(set(result.blocked_actions))


def test_no_sos_alert_or_notification_channel_send_is_authorized():
    result = _result()
    assert result.sos_alert_sent is False
    assert result.notification_sent is False
    assert result.sms_sent is False
    assert result.push_sent is False
    assert result.email_sent is False
    assert result.telegram_sent is False
    assert result.tasker_sent is False
    assert result.adb_sent is False
    assert result.sos_alert_send_allowed is False
    assert result.notification_send_allowed is False
    assert result.sms_send_allowed is False
    assert result.push_send_allowed is False
    assert result.email_send_allowed is False
    assert result.telegram_send_allowed is False
    assert result.tasker_send_allowed is False
    assert result.adb_send_allowed is False


def test_no_vacation_mode_execution_is_authorized():
    result = _result()
    assert result.vacation_mode_execution_authorized is False
    assert result.unattended_vacation_mode_allowed is False
    assert result.vacation_profit_trial_allowed is False
    assert result.final_decision_authorizes_vacation_mode is False
    assert "vacation_mode_execution" in result.blocked_actions


def test_no_blocked_claims_are_made():
    result = _result()
    assert result.production_readiness_claimed is False
    assert result.profitable_22_6_claimed is False
    assert result.unattended_account_management_claimed is False
    assert "production_readiness" in result.blocked_claims
    assert "profitable_22_6_operation_confirmed" in result.blocked_claims
    assert "unattended_account_management_confirmed" in result.blocked_claims


def test_no_owner_final_approval_is_captured():
    result = _result()
    assert result.owner_final_approval_captured is False
    assert result.owner_final_vacation_approval_present is False
    assert "owner_final_vacation_approval_captured" in result.blocked_claims


def test_final_readiness_percent_is_calculated_correctly():
    ready = _result(gate.build_sample_ready_input)
    partial = _result(gate.build_sample_partial_input)
    assert ready.final_readiness_percent == 100.0
    expected_partial = round(
        (partial.ready_surface_count / partial.total_surface_count) * 100,
        2,
    )
    assert partial.final_readiness_percent == expected_partial
    assert partial.ready_surface_count < partial.total_surface_count
    assert partial.total_surface_count == 40


def test_source_summaries_are_included():
    result = _result()
    assert set(gate.SOURCE_KEYS) == set(result.source_summary)
    assert result.source_classifications["sos_owner_alert_bridge"] == (
        "SOS_OWNER_ALERT_BRIDGE_READY"
    )
    assert result.source_percentages["supervised_compounding_policy"] == 100.0
    assert result.source_ready_surface_counts["statistical_profit_proof"] == 32
    assert result.source_total_surface_counts["evidence_depth_quality"] == 32


def test_missing_surfaces_are_reported():
    result = _result(gate.build_sample_partial_input)
    assert result.missing_surfaces
    assert "vacation_readiness_orchestrator_ready" in result.missing_surfaces
    assert "all_source_classifications_ready" in result.missing_surfaces
    assert "exact_next_phase_declared" in result.missing_surfaces


def test_blocked_actions_are_reported():
    result = _result()
    assert set(gate.BLOCKED_ACTIONS).issubset(set(result.blocked_actions))


def test_blocked_claims_are_reported():
    result = _result()
    assert set(gate.BLOCKED_CLAIMS).issubset(set(result.blocked_claims))


def test_exact_next_phase_is_declared():
    assert _result().exact_next_phase == "SUPERVISED_DEMO_OPERATIONAL_VALIDATION_PHASE"


def test_next_safe_action_is_explicit():
    result = _result()
    assert "Review the final build-only Vacation Mode readiness decision" in (
        result.next_safe_action
    )
    assert "do not approve broker access" in result.next_safe_action


def test_mapping_input_works():
    source = gate.build_sample_ready_input()
    result = gate.evaluate_forex_vacation_mode_final_readiness_decision(
        {
            "source_vacation_readiness_result": source.source_vacation_readiness_result,
            "source_evidence_depth_quality_result": (
                source.source_evidence_depth_quality_result
            ),
            "source_statistical_profit_result": source.source_statistical_profit_result,
            "source_supervised_compounding_result": (
                source.source_supervised_compounding_result
            ),
            "source_sos_owner_alert_result": source.source_sos_owner_alert_result,
            "final_decision_surfaces": {
                name: True for name in gate.FINAL_DECISION_SURFACES
            },
            "owner_final_label": "pending_owner_review",
            "owner_notes_sanitized": "mapping input",
        }
    )
    assert result.classification == gate.VACATION_MODE_READY


def test_dataclass_like_input_works():
    source = gate.build_sample_ready_input()

    class AttributeInput:
        source_vacation_readiness_result = source.source_vacation_readiness_result
        source_evidence_depth_quality_result = source.source_evidence_depth_quality_result
        source_statistical_profit_result = source.source_statistical_profit_result
        source_supervised_compounding_result = source.source_supervised_compounding_result
        source_sos_owner_alert_result = source.source_sos_owner_alert_result
        final_decision_surfaces = {
            name: True for name in gate.FINAL_DECISION_SURFACES
        }
        owner_final_label = "pending_owner_review"
        owner_notes_sanitized = "attribute style input"

    result = gate.evaluate_forex_vacation_mode_final_readiness_decision(AttributeInput())
    assert result.classification == gate.VACATION_MODE_READY


def test_unsafe_sample_reports_unsafe_fragments_but_output_flags_stay_false():
    result = _result(gate.build_sample_unsafe_input)
    assert result.classification == gate.VACATION_MODE_BLOCKED_UNSAFE
    assert result.unsafe_fragments_detected
    assert result.protected_flags["broker_action_allowed"] is False
    assert result.protected_flags["oanda_api_call_allowed"] is False
    assert result.protected_flags["notification_send_allowed"] is False
    assert result.protected_flags["final_decision_authorizes_vacation_mode"] is False


def test_schema_invalid_sample_reports_schema_errors():
    result = _result(gate.build_sample_schema_invalid_input)
    assert result.classification == gate.VACATION_MODE_BLOCKED_SCHEMA_INVALID
    assert any("source_vacation_readiness_result" in item for item in result.unsafe_fragments_detected)
    assert any("final_decision_surfaces" in item for item in result.unsafe_fragments_detected)


def test_json_serializable():
    payload = json.dumps(gate.to_jsonable_dict(_result()))
    assert "VACATION_MODE_READY" in payload


def test_markdown_output():
    text = gate.to_markdown(_result())
    assert text.startswith("# AIOS Forex Vacation Mode Final Readiness Decision V1")
    assert "No Vacation Mode execution was authorized." in text


def test_cli_json_works():
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--sample-ready", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["classification"] == gate.VACATION_MODE_READY
    assert payload["ready_surface_count"] == 40


def test_cli_markdown_works():
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--sample-ready", "--markdown"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.startswith(
        "# AIOS Forex Vacation Mode Final Readiness Decision V1"
    )
    assert "Classification: `VACATION_MODE_READY`" in completed.stdout


@pytest.mark.parametrize(
    "forbidden_true",
    tuple(f'"{name}": true' for name in gate.PROTECTED_FLAG_NAMES),
)
def test_json_has_no_protected_true_flags(forbidden_true: str):
    payload = json.dumps(gate.to_jsonable_dict(_result())).lower()
    assert forbidden_true not in payload
