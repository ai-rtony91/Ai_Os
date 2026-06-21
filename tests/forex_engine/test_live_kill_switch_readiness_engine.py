from automation.forex_engine.live_kill_switch_readiness_engine import (
    STATUS_BLOCKED,
    STATUS_MORE_INFO,
    STATUS_READY,
    evaluate_live_kill_switch_readiness,
)


def _metadata():
    return {
        "kill_switch_declared": True,
        "manual_operator_stop_declared": True,
        "max_daily_loss_stop_declared": True,
        "max_drawdown_stop_declared": True,
        "emergency_disable_declared": True,
        "credential_revoke_path_declared": True,
        "audit_logging_declared": True,
        "notification_path_declared": True,
        "operator_override_declared": True,
        "paper_only_review": True,
    }


def test_kill_switch_ready():
    result = evaluate_live_kill_switch_readiness(_metadata())
    assert result["kill_switch_ready"] is True
    assert result["kill_switch_status"] == STATUS_READY
    assert result["safety"]["kill_switch_executed"] is False


def test_missing_metadata_blocked():
    result = evaluate_live_kill_switch_readiness({"kill_switch_declared": True})
    assert result["kill_switch_ready"] is False
    assert result["kill_switch_status"] == STATUS_MORE_INFO
    assert any(reason.startswith("missing_kill_switch_metadata:") for reason in result["blocked_reasons"])


def test_missing_kill_switch_blocked():
    metadata = _metadata()
    metadata["kill_switch_declared"] = False
    result = evaluate_live_kill_switch_readiness(metadata)
    assert result["kill_switch_status"] == STATUS_BLOCKED
    assert "kill_switch_control_failed:kill_switch_declared" in result["blocked_reasons"]


def test_missing_daily_loss_stop_blocked():
    metadata = _metadata()
    metadata["max_daily_loss_stop_declared"] = False
    result = evaluate_live_kill_switch_readiness(metadata)
    assert "kill_switch_control_failed:max_daily_loss_stop_declared" in result["blocked_reasons"]


def test_missing_drawdown_stop_blocked():
    metadata = _metadata()
    metadata["max_drawdown_stop_declared"] = False
    result = evaluate_live_kill_switch_readiness(metadata)
    assert "kill_switch_control_failed:max_drawdown_stop_declared" in result["blocked_reasons"]


def test_missing_emergency_disable_blocked():
    metadata = _metadata()
    metadata["emergency_disable_declared"] = False
    result = evaluate_live_kill_switch_readiness(metadata)
    assert "kill_switch_control_failed:emergency_disable_declared" in result["blocked_reasons"]


def test_missing_credential_revoke_path_blocked():
    metadata = _metadata()
    metadata["credential_revoke_path_declared"] = False
    result = evaluate_live_kill_switch_readiness(metadata)
    assert "kill_switch_control_failed:credential_revoke_path_declared" in result["blocked_reasons"]


def test_missing_audit_logging_blocked():
    metadata = _metadata()
    metadata["audit_logging_declared"] = False
    result = evaluate_live_kill_switch_readiness(metadata)
    assert "kill_switch_control_failed:audit_logging_declared" in result["blocked_reasons"]


def test_missing_notification_path_blocked():
    metadata = _metadata()
    metadata["notification_path_declared"] = False
    result = evaluate_live_kill_switch_readiness(metadata)
    assert "kill_switch_control_failed:notification_path_declared" in result["blocked_reasons"]


def test_deterministic_output():
    first = evaluate_live_kill_switch_readiness(_metadata())
    second = evaluate_live_kill_switch_readiness(_metadata())
    assert first == second


def test_safety_source_scan():
    source = open("automation/forex_engine/live_kill_switch_readiness_engine.py", encoding="utf-8").read()
    forbidden = ["requests", "urllib", "socket", "subprocess", "os.environ", ".env", "http://", "https://"]
    for token in forbidden:
        assert token not in source


def test_forbidden_execution_state_absent():
    result = evaluate_live_kill_switch_readiness(_metadata())
    safety = result["safety"]
    assert safety["kill_switch_executed"] is False
    assert safety["broker_connection_active"] is False
    assert safety["credentials_accessed"] is False
    assert safety["network_access"] is False
    assert safety["order_execution_enabled"] is False
    assert safety["live_trading_authorized"] is False
    assert safety["capital_allocation_modified"] is False
