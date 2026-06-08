from __future__ import annotations

import pytest

from automation.operator_relief.adb_escalation import MODE_DRY_RUN, plan_adb_escalation
from automation.operator_relief.vacation_watchdog import (
    CLASSIFICATION_NON_SOS,
    CLASSIFICATION_SOS,
    build_vacation_heartbeat,
)


def _adb_intent_from_heartbeat(heartbeat: dict[str, object]) -> dict[str, object]:
    trigger = "blocked" if heartbeat["sos_required"] else "routine"
    report = plan_adb_escalation(
        trigger,
        mode=MODE_DRY_RUN,
        command_runner=_fail_if_adb_runner_is_called,
    )
    return {
        "wake_worthy": bool(heartbeat["sos_required"]),
        "notification_sent": False,
        "notification_provider_called": False,
        "adb_executed": False,
        "adb_report": report.to_dict(),
    }


def _fail_if_adb_runner_is_called(command: list[str]):
    raise AssertionError(f"ADB runner must not be called in no-send proof: {command!r}")


def _heartbeat(**states: dict[str, object]) -> dict[str, object]:
    return build_vacation_heartbeat(
        repo_state={"repo_path": r"C:\Dev\Ai.Os"},
        git_state={
            "branch": "feature/full-operator-relief-closed-loop-v1",
            "git_clean": True,
            "upstream_state": "MATCHES_ORIGIN",
            **states.get("git_state", {}),
        },
        validator_state={"status": "PASS", **states.get("validator_state", {})},
        approval_state={"pending_count": 0, "sos_pending_count": 0, **states.get("approval_state", {})},
        notification_state={
            "notification_rail": "ADB_SOS",
            "adb_sos_available": True,
            **states.get("notification_state", {}),
        },
        safety_state={
            "trading_live_blocked": True,
            "secret_risk_status": "CLEAR",
            **states.get("safety_state", {}),
        },
        queue_state=states.get("queue_state", {}),
        evidence_state=states.get("evidence_state", {}),
        timestamp_utc="2026-06-07T00:00:00+00:00",
    )


@pytest.mark.parametrize(
    ("name", "states"),
    [
        ("secret/key/token leak", {"safety_state": {"secret_leak": True}}),
        ("live broker/trading execution risk", {"safety_state": {"live_trading_risk": True}}),
        ("protected gate bypass", {"safety_state": {"protected_gate_bypass": True}}),
        ("main branch risk", {"git_state": {"main_branch_risk": True}}),
        (
            "validation failure invalidates merge readiness",
            {"validator_state": {"status": "FAIL", "invalidates_merge_readiness": True}},
        ),
        (
            "SOS pending while ADB SOS unavailable",
            {
                "approval_state": {"sos_pending_count": 1},
                "notification_state": {"adb_sos_available": False},
            },
        ),
    ],
)
def test_true_sos_conditions_are_adb_wake_worthy_without_sending(name: str, states: dict[str, object]) -> None:
    heartbeat = _heartbeat(**states)
    intent = _adb_intent_from_heartbeat(heartbeat)
    adb_report = intent["adb_report"]

    assert heartbeat["classification"] == CLASSIFICATION_SOS, name
    assert heartbeat["sos_required"] is True
    assert intent["wake_worthy"] is True
    assert intent["notification_sent"] is False
    assert intent["notification_provider_called"] is False
    assert intent["adb_executed"] is False
    assert adb_report["status"] == "ADB_ALERT_PLANNED"
    assert adb_report["mode"] == MODE_DRY_RUN
    assert adb_report["alert_required"] is True
    assert adb_report["command_result"] is None
    assert adb_report["executable"] is False


@pytest.mark.parametrize(
    ("name", "states"),
    [
        ("docs polish", {"safety_state": {"docs_polish": True}}),
        ("naming/style", {"safety_state": {"naming_style": True}}),
        ("optional refactor", {"safety_state": {"optional_refactor": True}}),
        ("future Telegram/Tasker work", {"safety_state": {"future_telegram_tasker": True}}),
        ("merge timing preference", {"safety_state": {"merge_timing_preference": True}}),
        ("stale but non-blocking report", {"evidence_state": {"stale_non_blocking_report": True}}),
    ],
)
def test_non_sos_conditions_stay_silent_without_adb_wake(name: str, states: dict[str, object]) -> None:
    heartbeat = _heartbeat(**states)
    intent = _adb_intent_from_heartbeat(heartbeat)
    adb_report = intent["adb_report"]

    assert heartbeat["classification"] == CLASSIFICATION_NON_SOS, name
    assert heartbeat["sos_required"] is False
    assert heartbeat["do_not_wake_reason"]
    assert intent["wake_worthy"] is False
    assert intent["notification_sent"] is False
    assert intent["notification_provider_called"] is False
    assert intent["adb_executed"] is False
    assert adb_report["status"] == "ADB_ALERT_NOT_REQUIRED"
    assert adb_report["alert_required"] is False
    assert adb_report["command_result"] is None
    assert adb_report["executable"] is False


def test_adb_sos_only_proof_uses_no_send_dry_run_invariants() -> None:
    heartbeat = _heartbeat(safety_state={"secret_leak": True})
    intent = _adb_intent_from_heartbeat(heartbeat)
    adb_report = intent["adb_report"]

    assert heartbeat["classification"] == CLASSIFICATION_SOS
    assert adb_report["reasons"] == ["ADB alert command planned only; no command executed."]
    assert intent == {
        "wake_worthy": True,
        "notification_sent": False,
        "notification_provider_called": False,
        "adb_executed": False,
        "adb_report": adb_report,
    }
