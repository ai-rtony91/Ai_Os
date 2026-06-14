from __future__ import annotations

from automation.orchestration.self_development.aios_minimal_sos_wake_policy import (
    SCHEMA,
    build_minimal_sos_wake_policy_result,
)


def _wake(event: str) -> dict:
    return build_minimal_sos_wake_policy_result({"event_type": event})


def test_sos_wakes() -> None:
    result = _wake("SOS_HARD_STOP")

    assert result["schema"] == SCHEMA
    assert result["wake_required"] is True
    assert result["wake_class"] == "SOS"


def test_protected_action_attempt_wakes() -> None:
    result = _wake("PROTECTED_ACTION_ATTEMPT")

    assert result["wake_required"] is True
    assert "PROTECTED_ACTION_ATTEMPT" in result["wake_reasons"]


def test_secrets_boundary_wakes() -> None:
    assert _wake("SECRETS_ENV_BOUNDARY")["wake_required"] is True


def test_broker_live_trading_boundary_wakes() -> None:
    assert _wake("BROKER_LIVE_TRADING_BOUNDARY")["wake_required"] is True


def test_timebox_breach_wakes() -> None:
    result = _wake("WORKER_RUNAWAY_TIMEBOX_BREACH")

    assert result["wake_required"] is True
    assert result["wake_class"] == "TIMEBOX"


def test_routine_warn_does_not_wake() -> None:
    assert _wake("ROUTINE_VALIDATOR_WARN")["wake_required"] is False


def test_normal_simulation_completion_does_not_wake() -> None:
    assert _wake("NORMAL_RESEARCH_COMPLETION")["wake_required"] is False


def test_expected_simulation_failure_does_not_wake_unless_critical() -> None:
    result = _wake("EXPECTED_SIMULATION_FAILURE")

    assert result["wake_required"] is False
    assert "EXPECTED_SIMULATION_FAILURE" in result["do_not_wake_for"]
