"""Deterministic AIOS self-build candidate selection.

The selector returns a concrete, bounded self-build candidate. It does not
write files, create READY stages, mutate registry state, or touch protected
surfaces.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_SELF_BUILD_CANDIDATE_SELECTION.v1"

DEFAULT_CANDIDATE_ID = "AIOS-SELF-BUILD-RUNNER-HARDENING-CANDIDATE"
DEFAULT_CANDIDATE_TITLE = "Harden AIOS autonomous self-build runners"

SELF_BUILD_PRIORITY = [
    "runner_hardening",
    "validator_repair",
    "status_integration",
    "self_build_execution",
    "worker_launch_safety",
]

OPTIONAL_PRIORITY = [
    "forex_research",
    "dashboard_ui",
]

BLOCKED_SURFACES = [
    "secrets",
    ".env",
    "broker",
    "OANDA",
    "live trading",
    "webhook",
    "orders",
    "scheduler",
    "daemon",
    "queue mutation",
    "lock mutation",
    "approval mutation",
    "registry mutation",
    "push",
    "PR",
    "merge",
]

DEFAULT_ALLOWED_FILES = [
    "automation/orchestration/self_development/*.py",
    "automation/orchestration/self_development/*.ps1",
    "schemas/aios/orchestration/*.schema.json",
    "tests/orchestration/test_aios_self_build_*.py",
]

DEFAULT_VALIDATORS = [
    "git diff --check",
    "python -m pytest tests/orchestration/test_aios_self_build_candidate_selector.py -q -p no:cacheprovider",
    "python -m pytest tests/orchestration/test_aios_self_build_execution_packet.py -q -p no:cacheprovider",
    "python -m pytest tests/orchestration/test_aios_self_build_validator_repair_engine.py -q -p no:cacheprovider",
    "python -m pytest tests/orchestration/test_aios_self_build_execution_ledger.py -q -p no:cacheprovider",
    "python -m pytest tests/orchestration/test_aios_autonomous_self_build_executor.py -q -p no:cacheprovider",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = _safe_str(value).lower()
    if not text:
        return default
    return text in {"true", "1", "yes", "y", "on", "approved", "present"}


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, (list, tuple, set)):
        return [_safe_str(item) for item in value if _safe_str(item)]
    return [_safe_str(value)] if _safe_str(value) else []


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item and item not in seen:
            result.append(item)
            seen.add(item)
    return result


def _normalized_lane(value: Any) -> str:
    return _safe_str(value).lower().replace("-", "_").replace(" ", "_")


def _candidate_for_lane(lane: str) -> dict[str, str]:
    lane = _normalized_lane(lane)
    if lane == "validator_repair":
        return {
            "candidate_id": "AIOS-SELF-BUILD-VALIDATOR-REPAIR-CANDIDATE",
            "candidate_title": "Harden AIOS validator repair decisions",
            "candidate_lane": lane,
            "priority": "high",
            "objective": "Improve deterministic repair guidance for failing self-build validators without arbitrary edits.",
            "reason": "Validator repair improves autonomous self-build quality while staying bounded.",
        }
    if lane == "status_integration":
        return {
            "candidate_id": "AIOS-SELF-BUILD-STATUS-INTEGRATION-CANDIDATE",
            "candidate_title": "Surface AIOS self-build status",
            "candidate_lane": lane,
            "priority": "medium",
            "objective": "Expose self-build readiness and next safe action through existing read-only recommendation status.",
            "reason": "Status surfacing improves operator visibility without launching workers.",
        }
    if lane == "self_build_execution":
        return {
            "candidate_id": "AIOS-SELF-BUILD-EXECUTION-CANDIDATE",
            "candidate_title": "Harden AIOS self-build execution loop",
            "candidate_lane": lane,
            "priority": "high",
            "objective": "Improve the bounded self-build execution loop and ledger proof.",
            "reason": "Execution-loop hardening advances autonomous repo work under strict local limits.",
        }
    if lane == "worker_launch_safety":
        return {
            "candidate_id": "AIOS-SELF-BUILD-WORKER-LAUNCH-SAFETY-CANDIDATE",
            "candidate_title": "Harden AIOS worker launch safety gates",
            "candidate_lane": lane,
            "priority": "high",
            "objective": "Strengthen preflight and launch-guard evidence without launching real workers.",
            "reason": "Worker launch safety must remain ahead of autonomy expansion.",
        }
    if lane == "forex_research":
        return {
            "candidate_id": "AIOS-SELF-BUILD-FOREX-RESEARCH-CANDIDATE",
            "candidate_title": "Extend synthetic Forex research automation",
            "candidate_lane": lane,
            "priority": "medium",
            "objective": "Improve synthetic-only Forex research, backtest, replay, or soak automation.",
            "reason": "Forex research is eligible only after self-build lanes have no available work.",
        }
    if lane == "dashboard_ui":
        return {
            "candidate_id": "AIOS-SELF-BUILD-DASHBOARD-DEFERRED-CANDIDATE",
            "candidate_title": "Dashboard/UI work deferred",
            "candidate_lane": lane,
            "priority": "deferred",
            "objective": "Defer dashboard/UI work until explicitly requested by Human Owner.",
            "reason": "Dashboard/UI is blocked in this packet unless explicitly requested.",
        }
    return {
        "candidate_id": DEFAULT_CANDIDATE_ID,
        "candidate_title": DEFAULT_CANDIDATE_TITLE,
        "candidate_lane": "runner_hardening",
        "priority": "high",
        "objective": "Improve autonomous self-build runner reliability while preserving safety boundaries.",
        "reason": "Repo is idle or no higher-priority eligible lane was supplied.",
    }


def select_self_build_candidate(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the next concrete self-build candidate."""

    payload = payload or {}
    generated_utc = _safe_str(payload.get("generated_utc")) or _now()
    requested_lanes = [_normalized_lane(item) for item in _as_list(payload.get("eligible_lanes"))]
    requested_lane = _normalized_lane(payload.get("requested_lane"))
    allow_dashboard_ui = _bool(payload.get("allow_dashboard_ui"), default=False)

    lanes = requested_lanes or ([requested_lane] if requested_lane else [])
    if not lanes:
        selected_lane = "runner_hardening"
    else:
        selected_lane = ""
        for lane in SELF_BUILD_PRIORITY:
            if lane in lanes:
                selected_lane = lane
                break
        if not selected_lane and "forex_research" in lanes:
            selected_lane = "forex_research"
        elif not selected_lane and "dashboard_ui" in lanes:
            selected_lane = "dashboard_ui" if allow_dashboard_ui else "runner_hardening"
        elif not selected_lane:
            selected_lane = "runner_hardening"

    if selected_lane == "dashboard_ui" and not allow_dashboard_ui:
        selected_lane = "runner_hardening"

    candidate = _candidate_for_lane(selected_lane)
    if requested_lane == "dashboard_ui" and not allow_dashboard_ui:
        candidate["reason"] = "Dashboard/UI is deferred unless explicitly requested; selecting runner hardening instead."

    return {
        "schema": SCHEMA,
        "generated_utc": generated_utc,
        "candidate_id": candidate["candidate_id"],
        "candidate_title": candidate["candidate_title"],
        "candidate_lane": candidate["candidate_lane"],
        "priority": candidate["priority"],
        "objective": candidate["objective"],
        "allowed_files": _dedupe(_as_list(payload.get("allowed_files")) or DEFAULT_ALLOWED_FILES),
        "blocked_surfaces": list(BLOCKED_SURFACES),
        "required_validators": _dedupe(_as_list(payload.get("required_validators")) or DEFAULT_VALIDATORS),
        "approval_required": "Human Owner approval required for APPLY; separate approval required for local commit.",
        "reason": candidate["reason"],
        "next_safe_action": "Build a bounded execution packet, run validators, and stop before push/PR/merge.",
        "safety": {
            "writes_files": False,
            "mutates_registry": False,
            "creates_ready_stage": False,
            "mutates_queue": False,
            "mutates_locks": False,
            "mutates_approval": False,
            "touches_secrets_or_env": False,
            "broker_or_live_trading": False,
            "pushes": False,
            "creates_pr": False,
            "merges": False,
            "dashboard_ui_deferred": candidate["candidate_lane"] != "dashboard_ui",
        },
    }
