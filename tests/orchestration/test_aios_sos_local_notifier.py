from __future__ import annotations

from automation.orchestration.aios_sos_local_notifier import (
    SCHEMA,
    build_sos_local_notifier_plan,
)


def _plan(**overrides: object) -> dict[str, object]:
    payload = {
        "sos_policy": {},
        "stop_report": {},
        "core_status": {},
        "notifier_options": {},
    }
    payload.update(overrides)
    return build_sos_local_notifier_plan(**payload)


def test_no_sos_returns_no_alert() -> None:
    result = _plan()

    assert result["schema"] == SCHEMA
    assert result["notifier_status"] == "no_alert"
    assert result["alert_level"] == "none"
    assert result["should_alert"] is False


def test_sos_required_true_returns_alert_ready() -> None:
    result = _plan(sos_policy={"sos_required": True})

    assert result["notifier_status"] == "alert_ready"
    assert result["should_alert"] is True
    assert result["alert_level"] == "warning"


def test_wake_anthony_true_returns_alert_ready() -> None:
    result = _plan(sos_policy={"wake_anthony": True})

    assert result["notifier_status"] == "alert_ready"
    assert result["should_alert"] is True
    assert "wake" in str(result["alert_reason"]).lower()


def test_severity_critical_maps_to_critical_alert() -> None:
    result = _plan(sos_policy={"severity": "critical"})

    assert result["notifier_status"] == "alert_ready"
    assert result["alert_level"] == "critical"


def test_protected_action_attempt_creates_alert_ready() -> None:
    result = _plan(stop_report={"protected_action_attempt": True})

    assert result["notifier_status"] == "alert_ready"
    assert result["detected_risks"]["protected_action_attempt"] is True


def test_broker_live_trading_risk_creates_critical_alert() -> None:
    result = _plan(core_status={"broker_live_trading_risk": True})

    assert result["notifier_status"] == "alert_ready"
    assert result["alert_level"] == "critical"
    assert result["detected_risks"]["broker_live_trading"] is True


def test_credentials_risk_creates_critical_alert() -> None:
    result = _plan(sos_policy={"credentials_risk": True})

    assert result["notifier_status"] == "alert_ready"
    assert result["alert_level"] == "critical"
    assert result["detected_risks"]["credentials"] is True


def test_external_notification_request_is_blocked() -> None:
    result = _plan(
        sos_policy={"sos_required": True},
        notifier_options={"channels": ["telegram", "email"], "request_external_notifications": True},
    )

    assert result["external_notifications_requested"] is True
    assert result["external_notifications_blocked"] is True
    assert "external_notifications_blocked_in_v1" in result["rejection_reasons"]
    assert result["notifier_status"] == "alert_ready"


def test_no_real_toast_command_is_executed() -> None:
    result = _plan(
        sos_policy={"sos_required": True},
        notifier_options={"show_toast": True},
    )

    assert result["windows_toast_preview"]["enabled"] is False
    assert result["windows_toast_preview"]["command"] is None
    assert result["safety"]["real_toast_executed"] is False
    assert result["commands_executed"] == []


def test_no_powershell_command_is_executed() -> None:
    result = _plan(
        sos_policy={"sos_required": True},
        notifier_options={"run_powershell": True, "powershell_notification": True},
    )

    assert result["safety"]["powershell_notification_executed"] is False
    assert result["commands_executed"] == []
    assert "powershell_notification_blocked_in_v1" in result["rejection_reasons"]


def test_no_files_are_written() -> None:
    result = _plan(
        sos_policy={"sos_required": True},
        notifier_options={"write_reports": True},
    )

    assert result["files_written"] == []
    assert result["safety"]["files_written"] is False
    assert result["safety"]["reports_written"] is False


def test_no_network_access_is_requested() -> None:
    result = _plan(
        sos_policy={"sos_required": True},
        notifier_options={"channels": ["webhook"], "network_access": True, "send_webhook": True},
    )

    assert result["external_notifications_requested"] is True
    assert result["external_notifications_blocked"] is True
    assert result["safety"]["network_access_requested"] is False
    assert result["safety"]["network_access_used"] is False


def test_terminal_banner_preview_is_present_for_alert_ready() -> None:
    result = _plan(sos_policy={"sos_required": True})

    assert result["notifier_status"] == "alert_ready"
    assert result["terminal_banner_preview"]
    assert "AIOS SOS LOCAL ALERT PREVIEW" in result["terminal_banner_preview"][1]


def test_beep_plan_preview_is_present_for_alert_ready() -> None:
    result = _plan(sos_policy={"sos_required": True})

    assert result["notifier_status"] == "alert_ready"
    assert result["beep_plan_preview"]["would_beep"] is True
    assert result["beep_plan_preview"]["enabled"] is False


def test_safety_flags_prove_local_preview_only() -> None:
    result = _plan(sos_policy={"sos_required": True})
    safety = result["safety"]

    assert safety["mode"] == "LOCAL_PREVIEW_ONLY"
    assert safety["local_only"] is True
    assert safety["preview_only"] is True
    assert safety["sound_played"] is False
    assert safety["network_access_used"] is False
    assert safety["external_services_woken"] is False
    assert safety["broker"] is False
    assert safety["credentials"] is False
    assert safety["live_trading"] is False
    assert safety["real_orders"] is False
    assert safety["real_webhooks"] is False
    assert safety["scheduler_activation"] is False
    assert safety["daemon_activation"] is False
    assert safety["worker_dispatch"] is False
    assert safety["queue_mutation"] is False
    assert safety["approval_mutation"] is False


def test_existing_sos_policy_output_is_supported() -> None:
    result = _plan(
        sos_policy={
            "schema": "AIOS_SOS_ESCALATION_POLICY.v1",
            "escalation_status": "SOS_ESCALATION",
            "anthony_required": True,
            "matched_sos_categories": ["MONEY_TRADING_BROKER"],
        }
    )

    assert result["notifier_status"] == "alert_ready"
    assert result["alert_level"] == "critical"
    assert result["detected_risks"]["broker_live_trading"] is True


def test_validator_failure_after_repair_budget_triggers_warning() -> None:
    result = _plan(core_status={"validator_failed": True, "repair_budget_exhausted": True})

    assert result["notifier_status"] == "alert_ready"
    assert result["alert_level"] == "warning"
    assert result["detected_risks"]["validator_failure_after_repair_budget"] is True


def test_stuck_loop_or_repeated_failure_triggers_warning() -> None:
    result = _plan(stop_report={"stuck_loop": True, "repeated_failure": True})

    assert result["notifier_status"] == "alert_ready"
    assert result["alert_level"] == "warning"
    assert result["detected_risks"]["stuck_loop_or_repeated_failure"] is True

