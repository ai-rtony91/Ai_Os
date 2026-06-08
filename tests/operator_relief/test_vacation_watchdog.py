from automation.operator_relief.vacation_watchdog import (
    CLASSIFICATION_NON_SOS,
    CLASSIFICATION_OK,
    CLASSIFICATION_SOS,
    MINIMUM_HEARTBEAT_FIELDS,
    build_vacation_heartbeat,
)


def test_clean_state_returns_no_sos_and_do_not_wake_reason():
    heartbeat = build_vacation_heartbeat(
        git_state={"branch": "feature/full-operator-relief-closed-loop-v1", "git_clean": True},
        notification_state={"adb_sos_available": True},
        safety_state={"trading_live_blocked": True, "secret_risk_status": "CLEAR"},
        timestamp_utc="2026-06-08T00:00:00+00:00",
    )

    assert heartbeat["classification"] == CLASSIFICATION_OK
    assert heartbeat["sos_required"] is False
    assert heartbeat["do_not_wake_reason"]


def test_secret_leak_input_returns_sos_required():
    heartbeat = build_vacation_heartbeat(safety_state={"secret_leak": True})

    assert heartbeat["classification"] == CLASSIFICATION_SOS
    assert heartbeat["sos_required"] is True
    assert "secret/key/token leak" in heartbeat["sos_findings"]


def test_live_trading_risk_input_returns_sos_required():
    heartbeat = build_vacation_heartbeat(safety_state={"live_trading_risk": True})

    assert heartbeat["classification"] == CLASSIFICATION_SOS
    assert heartbeat["sos_required"] is True
    assert "live broker/trading execution risk" in heartbeat["sos_findings"]


def test_protected_gate_bypass_input_returns_sos_required():
    heartbeat = build_vacation_heartbeat(approval_state={"protected_gate_bypass": True})

    assert heartbeat["classification"] == CLASSIFICATION_SOS
    assert heartbeat["sos_required"] is True
    assert "protected gate bypass" in heartbeat["sos_findings"]


def test_stale_non_blocking_queue_item_returns_non_sos_attention():
    heartbeat = build_vacation_heartbeat(queue_state={"stale_non_blocking": True})

    assert heartbeat["classification"] == CLASSIFICATION_NON_SOS
    assert heartbeat["sos_required"] is False
    assert "stale non-blocking queue item" in heartbeat["non_sos_findings"]


def test_missing_adb_sos_availability_with_sos_pending_returns_sos_required():
    heartbeat = build_vacation_heartbeat(
        approval_state={"sos_pending_count": 1},
        notification_state={"adb_sos_available": False},
    )

    assert heartbeat["classification"] == CLASSIFICATION_SOS
    assert heartbeat["sos_required"] is True
    assert "notification failure defeats SOS-only vacation mode" in heartbeat["sos_findings"]


def test_validator_failure_that_invalidates_merge_readiness_returns_sos_required():
    heartbeat = build_vacation_heartbeat(
        validator_state={"status": "FAILED", "invalidates_merge_readiness": True}
    )

    assert heartbeat["classification"] == CLASSIFICATION_SOS
    assert heartbeat["sos_required"] is True
    assert "validator failure invalidates merge readiness" in heartbeat["sos_findings"]


def test_optional_docs_polish_returns_non_sos_attention():
    heartbeat = build_vacation_heartbeat(safety_state={"docs_polish": True})

    assert heartbeat["classification"] == CLASSIFICATION_NON_SOS
    assert heartbeat["sos_required"] is False
    assert "docs polish" in heartbeat["non_sos_findings"]


def test_output_includes_all_minimum_heartbeat_fields():
    heartbeat = build_vacation_heartbeat()

    assert set(MINIMUM_HEARTBEAT_FIELDS).issubset(heartbeat)


def test_pure_classifier_requires_no_file_writes_or_notification_calls():
    heartbeat = build_vacation_heartbeat(
        repo_state={"repo_path": "C:/Dev/Ai.Os"},
        notification_state={"notification_rail": "ADB_SOS", "adb_sos_available": True},
    )

    assert heartbeat["repo_path"] == "C:/Dev/Ai.Os"
    assert heartbeat["notification_rail"] == "ADB_SOS"
    assert "executable" not in heartbeat
