from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from automation.forex_engine import forex_sos_owner_alert_bridge_v1 as bridge


RUNNER = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "forex_delivery"
    / "run_forex_sos_owner_alert_bridge_v1.py"
)


def _result(builder=bridge.build_sample_ready_input):
    return bridge.evaluate_forex_sos_owner_alert_bridge(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (bridge.build_sample_ready_input, bridge.SOS_OWNER_ALERT_BRIDGE_READY),
        (
            bridge.build_sample_partial_input,
            bridge.SOS_OWNER_ALERT_REQUIRE_MORE_EVIDENCE,
        ),
        (bridge.build_sample_unsafe_input, bridge.SOS_OWNER_ALERT_BLOCKED_UNSAFE),
        (
            bridge.build_sample_schema_invalid_input,
            bridge.SOS_OWNER_ALERT_BLOCKED_SCHEMA_INVALID,
        ),
    ),
)
def test_sample_classifications(builder, classification: str):
    assert _result(builder).classification == classification


@pytest.mark.parametrize("flag_name", bridge.PROTECTED_FLAG_NAMES)
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


def test_no_bank_movement_is_authorized():
    result = _result()
    assert result.bank_movement_authorized is False
    assert result.bank_movement_allowed is False
    assert "bank_movement" in result.blocked_actions


def test_no_withdrawal_is_authorized():
    result = _result()
    assert result.withdrawal_authorized is False
    assert result.withdrawal_allowed is False
    assert "withdrawal" in result.blocked_actions


def test_no_deposit_is_authorized():
    result = _result()
    assert result.deposit_authorized is False
    assert result.deposit_allowed is False
    assert "deposit" in result.blocked_actions


def test_no_scheduler_daemon_webhook_is_authorized():
    result = _result()
    assert result.scheduler_allowed is False
    assert result.daemon_allowed is False
    assert result.webhook_allowed is False
    assert {"scheduler", "daemon", "webhook"}.issubset(set(result.blocked_actions))


def test_no_sos_alert_is_sent():
    result = _result()
    assert result.sos_alert_sent is False
    assert result.sos_alert_send_allowed is False
    assert result.sos_owner_alert_bridge_sends_alert is False
    assert "sos_alert_send" in result.blocked_actions


def test_no_notification_channel_send_is_authorized():
    result = _result()
    assert result.notification_sent is False
    assert result.sms_sent is False
    assert result.push_sent is False
    assert result.email_sent is False
    assert result.telegram_sent is False
    assert result.tasker_sent is False
    assert result.adb_sent is False
    assert result.notification_send_allowed is False
    assert result.sms_send_allowed is False
    assert result.push_send_allowed is False
    assert result.email_send_allowed is False
    assert result.telegram_send_allowed is False
    assert result.tasker_send_allowed is False
    assert result.adb_send_allowed is False
    assert {
        "notification_send",
        "sms_send",
        "push_send",
        "email_send",
        "telegram_send",
        "tasker_send",
        "adb_send",
    }.issubset(set(result.blocked_actions))


def test_no_vacation_mode_execution_is_authorized():
    result = _result()
    assert result.vacation_mode_execution_authorized is False
    assert result.unattended_vacation_mode_allowed is False
    assert result.vacation_profit_trial_allowed is False
    assert result.sos_owner_alert_bridge_authorizes_vacation_mode is False
    assert "vacation_mode_execution" in result.blocked_actions


def test_sos_alert_percent_is_calculated_correctly():
    ready = _result(bridge.build_sample_ready_input)
    partial = _result(bridge.build_sample_partial_input)
    assert ready.sos_alert_percent == 100.0
    expected_partial = round(
        (partial.ready_surface_count / partial.total_surface_count) * 100,
        2,
    )
    assert partial.sos_alert_percent == expected_partial
    assert partial.ready_surface_count < partial.total_surface_count
    assert partial.total_surface_count == 42


def test_missing_surfaces_are_reported():
    result = _result(bridge.build_sample_partial_input)
    assert result.missing_surfaces
    assert "source_supervised_compounding_policy_ready" in result.missing_surfaces
    assert "source_statistical_profit_proof_ready" in result.missing_surfaces
    assert "alert_rate_limit_required" in result.missing_surfaces


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
            "raw_transaction_id_access",
            "raw_order_id_access",
            "order_placement",
            "live_execution",
            "autonomous_execution",
            "compounding_execution",
            "bank_movement",
            "withdrawal",
            "deposit",
            "scheduler",
            "daemon",
            "webhook",
            "uncontrolled_retry",
            "sos_alert_send",
            "notification_send",
            "sms_send",
            "push_send",
            "email_send",
            "telegram_send",
            "tasker_send",
            "adb_send",
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
            "compounding_execution_readiness",
            "live_execution_readiness",
            "profitable_22_6_operation_confirmed",
            "unattended_account_management_confirmed",
            "actual_owner_notification_confirmed",
            "owner_approval_captured",
            "vacation_mode_final_ready",
        )
    ).issubset(set(result.blocked_claims))


def test_next_packet_preview_is_final_readiness_decision():
    assert _result().next_packet_preview == bridge.NEXT_PACKET_PREVIEW
    assert (
        _result().next_packet_preview
        == "AIOS-FOREX-VACATION-MODE-FINAL-READINESS-DECISION-V1"
    )


def test_next_safe_action_is_explicit():
    result = _result()
    assert "Review the SOS owner alert bridge result" in result.next_safe_action
    assert "do not approve broker access" in result.next_safe_action


def test_mapping_input_works():
    source = bridge.build_sample_ready_input().source_supervised_compounding_result
    result = bridge.evaluate_forex_sos_owner_alert_bridge(
        {
            "source_supervised_compounding_result": source,
            "sos_alert_surfaces": {name: True for name in bridge.SOS_ALERT_SURFACES},
            "owner_alert_label": "pending_owner_review",
            "owner_notes_sanitized": "mapping input",
        }
    )
    assert result.classification == bridge.SOS_OWNER_ALERT_BRIDGE_READY


def test_dataclass_like_input_works():
    class AttributeInput:
        source_supervised_compounding_result = (
            bridge.build_sample_ready_input().source_supervised_compounding_result
        )
        sos_alert_surfaces = {name: True for name in bridge.SOS_ALERT_SURFACES}
        owner_alert_label = "pending_owner_review"
        owner_notes_sanitized = "attribute style input"

    result = bridge.evaluate_forex_sos_owner_alert_bridge(AttributeInput())
    assert result.classification == bridge.SOS_OWNER_ALERT_BRIDGE_READY


def test_unsafe_sample_reports_unsafe_fragments_but_output_flags_stay_false():
    result = _result(bridge.build_sample_unsafe_input)
    assert result.classification == bridge.SOS_OWNER_ALERT_BLOCKED_UNSAFE
    assert result.unsafe_fragments_detected
    assert result.protected_flags["sos_alert_send_allowed"] is False
    assert result.protected_flags["notification_send_allowed"] is False
    assert result.protected_flags["sms_send_allowed"] is False
    assert result.protected_flags["email_send_allowed"] is False
    assert result.protected_flags["telegram_send_allowed"] is False
    assert result.protected_flags["tasker_send_allowed"] is False
    assert result.protected_flags["adb_send_allowed"] is False


def test_schema_invalid_sample_reports_schema_errors():
    result = _result(bridge.build_sample_schema_invalid_input)
    assert result.classification == bridge.SOS_OWNER_ALERT_BLOCKED_SCHEMA_INVALID
    assert any(
        "source_supervised_compounding_result" in item
        for item in result.unsafe_fragments_detected
    )
    assert any("sos_alert_surfaces" in item for item in result.unsafe_fragments_detected)


def test_json_serializable():
    payload = json.dumps(bridge.to_jsonable_dict(_result()))
    assert "SOS_OWNER_ALERT_BRIDGE_READY" in payload


def test_markdown_output():
    text = bridge.to_markdown(_result())
    assert text.startswith("# AIOS Forex SOS Owner Alert Bridge V1")
    assert "No SOS alert was sent." in text


def test_cli_json_works():
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--sample-ready", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["classification"] == bridge.SOS_OWNER_ALERT_BRIDGE_READY
    assert payload["ready_surface_count"] == 42


def test_cli_markdown_works():
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--sample-ready", "--markdown"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout.startswith("# AIOS Forex SOS Owner Alert Bridge V1")
    assert "Classification: `SOS_OWNER_ALERT_BRIDGE_READY`" in completed.stdout


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
        '"compounding_execution_authorized": true',
        '"bank_movement_allowed": true',
        '"withdrawal_allowed": true',
        '"deposit_allowed": true',
        '"scheduler_allowed": true',
        '"daemon_allowed": true',
        '"webhook_allowed": true',
        '"sos_alert_send_allowed": true',
        '"notification_send_allowed": true',
        '"sms_send_allowed": true',
        '"push_send_allowed": true',
        '"email_send_allowed": true',
        '"telegram_send_allowed": true',
        '"tasker_send_allowed": true',
        '"adb_send_allowed": true',
        '"unattended_vacation_mode_allowed": true',
        '"vacation_profit_trial_allowed": true',
        '"next_trade_authorized": true',
        '"repeat_trade_authorized": true',
        '"selected_packet_execution_authorized": true',
        '"codex_live_execution_authorized": true',
        '"owner_live_execution_approval_present": true',
        '"sos_owner_alert_bridge_authorizes_trading": true',
        '"sos_owner_alert_bridge_authorizes_execution": true',
        '"sos_owner_alert_bridge_authorizes_compounding": true',
        '"sos_owner_alert_bridge_authorizes_vacation_mode": true',
        '"sos_owner_alert_bridge_sends_alert": true',
    ),
)
def test_json_has_no_protected_true_flags(forbidden_true: str):
    payload = json.dumps(bridge.to_jsonable_dict(_result())).lower()
    assert forbidden_true not in payload
