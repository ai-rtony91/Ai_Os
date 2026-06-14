"""Bounded validator repair decision engine for AIOS self-build cycles."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_SELF_BUILD_VALIDATOR_REPAIR_RESULT.v1"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _normalized(value: Any) -> str:
    return _safe_str(value).upper().replace("-", "_").replace(" ", "_") or "UNKNOWN"


def _int_value(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = _safe_str(value).lower()
    if not text:
        return default
    return text in {"true", "1", "yes", "y", "on", "active", "present"}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def _validator_summary(validator_results: list[Any]) -> dict[str, Any]:
    normalized_results: list[dict[str, str]] = []
    pass_count = 0
    fail_count = 0
    warn_count = 0
    for index, result in enumerate(validator_results):
        if isinstance(result, dict):
            validator_id = _safe_str(result.get("validator_id") or result.get("name") or f"validator_{index + 1}")
            status = _normalized(result.get("status"))
        else:
            text = _normalized(result)
            validator_id = f"validator_{index + 1}"
            status = text
        if status in {"PASS", "WARN_REVIEWED"}:
            pass_count += 1
        elif status.startswith("WARN"):
            warn_count += 1
        else:
            fail_count += 1
        normalized_results.append({"validator_id": validator_id, "status": status})
    return {
        "results": normalized_results,
        "pass_count": pass_count,
        "warn_count": warn_count,
        "fail_count": fail_count,
        "all_pass": fail_count == 0 and warn_count == 0,
        "acceptable": fail_count == 0,
    }


def build_validator_repair_result(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a bounded repair decision; never edits code."""

    payload = payload or {}
    generated_utc = _safe_str(payload.get("generated_utc")) or _now()
    max_repair_attempts = max(0, _int_value(payload.get("max_repair_attempts"), 2))
    current_attempt = max(0, _int_value(payload.get("current_attempt"), 0))
    protected_boundary_hits = [_safe_str(item) for item in _as_list(payload.get("protected_boundary_hits")) if _safe_str(item)]
    sos_status = _normalized(payload.get("sos_status") or "CLEAR")
    validator_results = _as_list(payload.get("validator_results")) or [
        {"validator_id": "identity_spine", "status": "PASS"},
        {"validator_id": "orchestration_validator_chain", "status": "PASS"},
        {"validator_id": "approval_sos_hard_gate", "status": "PASS"},
    ]
    summary = _validator_summary(validator_results)

    status = "PASS"
    repair_needed = False
    wake_required = False
    next_repair_action = ""
    next_safe_action = "Validators passed; continue to bounded ledger proof or stop before protected actions."
    stop_conditions: list[str] = []

    if sos_status == "SOS_ACTIVE" or _bool(payload.get("sos_active"), default=False):
        status = "HARD_STOP"
        wake_required = True
        stop_conditions.append("SOS_ACTIVE")
        next_safe_action = "Wake Human Owner and stop self-build execution."
    elif protected_boundary_hits:
        status = "HARD_STOP"
        wake_required = True
        stop_conditions.append("PROTECTED_BOUNDARY_HIT")
        next_safe_action = "Wake Human Owner; remove protected boundary before continuing."
    elif summary["acceptable"]:
        status = "PASS"
    elif current_attempt < max_repair_attempts:
        status = "REPAIR_ATTEMPT_AVAILABLE"
        repair_needed = True
        next_repair_action = "Re-run deterministic validator-focused repair stub for failing validator evidence only."
        next_safe_action = "Run one bounded deterministic repair attempt, then re-run validators."
    else:
        status = "REPAIR_EXHAUSTED"
        repair_needed = False
        stop_conditions.append("MAX_REPAIR_ATTEMPTS_EXHAUSTED")
        next_safe_action = "Human review required; repair attempts are exhausted."

    return {
        "schema": SCHEMA,
        "generated_utc": generated_utc,
        "status": status,
        "repair_needed": repair_needed,
        "current_attempt": current_attempt,
        "max_repair_attempts": max_repair_attempts,
        "validator_summary": summary,
        "protected_boundary_hits": protected_boundary_hits,
        "sos_status": sos_status,
        "wake_required": wake_required,
        "next_repair_action": next_repair_action,
        "repair_actions": [next_repair_action] if next_repair_action else [],
        "stop_conditions": stop_conditions,
        "next_safe_action": next_safe_action,
        "safety": {
            "writes_files": False,
            "arbitrary_code_edits": False,
            "mutates_queue": False,
            "mutates_locks": False,
            "mutates_approval": False,
            "mutates_registry": False,
            "touches_secrets_or_env": False,
            "broker_or_live_trading": False,
            "protected_actions_blocked": True,
        },
    }
