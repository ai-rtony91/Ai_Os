"""Minimal Human Owner wake policy for AIOS autonomous research runs."""

from __future__ import annotations

from typing import Any


SCHEMA = "AIOS_MINIMAL_SOS_WAKE_POLICY_RESULT.v1"
MODE = "DRY_RUN_READ_ONLY"

WAKE_EVENTS = {
    "SOS_HARD_STOP": "SOS",
    "SOS_ACTIVE": "SOS",
    "PROTECTED_ACTION_ATTEMPT": "PROTECTED_BOUNDARY",
    "SECRETS_ENV_BOUNDARY": "PROTECTED_BOUNDARY",
    "SECRET_BOUNDARY": "PROTECTED_BOUNDARY",
    "BROKER_LIVE_TRADING_BOUNDARY": "PROTECTED_BOUNDARY",
    "OANDA_BOUNDARY": "PROTECTED_BOUNDARY",
    "WEBHOOK_ORDER_BOUNDARY": "PROTECTED_BOUNDARY",
    "REPO_CORRUPTION": "REPO_INTEGRITY",
    "VALIDATOR_CRITICAL_FAIL": "VALIDATOR_CRITICAL",
    "WORKER_RUNAWAY_TIMEBOX_BREACH": "TIMEBOX",
    "TIMEBOX_BREACH": "TIMEBOX",
    "UNEXPECTED_FILE_MUTATION": "FILE_BOUNDARY",
    "SECURITY_RISK": "SECURITY",
}

NO_WAKE_EVENTS = {
    "ROUTINE_VALIDATOR_WARN",
    "NORMAL_RESEARCH_COMPLETION",
    "EXPECTED_SIMULATION_FAILURE",
    "LOW_VALUE_RECOMMENDATION",
    "DASHBOARD_PRODUCTION_READINESS_CANDIDATE",
    "NO_READY_STAGE_IDLE",
    "NON_CRITICAL_TEST_FAILURE",
}


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _normalized(value: Any) -> str:
    return _safe_str(value).upper().replace("-", "_").replace(" ", "_") or "UNKNOWN"


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item and item not in seen:
            result.append(item)
            seen.add(item)
    return result


def _safety() -> dict[str, Any]:
    return {
        "writes_files": False,
        "starts_runtime": False,
        "launches_workers": False,
        "enables_scheduler": False,
        "starts_daemon": False,
        "mutates_queue": False,
        "mutates_locks": False,
        "mutates_approval": False,
        "mutates_registry": False,
        "writes_reports": False,
        "writes_telemetry": False,
        "writes_relay": False,
        "touches_secrets_or_env": False,
        "broker_or_live_trading": False,
        "protected_actions_blocked": True,
        "human_owner_required_before_protected_action": True,
    }


def build_minimal_sos_wake_policy_result(payload: dict[str, Any]) -> dict[str, Any]:
    events = [_normalized(item) for item in _as_list(payload.get("events") or payload.get("event_type"))]
    if not events:
        events = ["NORMAL_RESEARCH_COMPLETION"]

    wake_reasons: list[str] = []
    wake_classes: list[str] = []
    for event in events:
        if event in WAKE_EVENTS:
            wake_reasons.append(event)
            wake_classes.append(WAKE_EVENTS[event])

    wake_required = bool(wake_reasons)
    wake_class = "NO_WAKE"
    if wake_required:
        wake_class = "SOS" if "SOS" in wake_classes else wake_classes[0]

    next_safe_action = "Continue bounded local simulation/research without waking Human Owner."
    if wake_required:
        next_safe_action = "Stop the autonomous research run and wake the Human Owner for boundary review."

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "wake_required": wake_required,
        "wake_class": wake_class,
        "wake_reasons": _dedupe(wake_reasons),
        "do_not_wake_for": sorted(NO_WAKE_EVENTS),
        "next_safe_action": next_safe_action,
        "safety": _safety(),
    }
