"""Build inert AIOS self-build execution packet objects."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from automation.orchestration.self_development.aios_self_build_candidate_selector import (
    BLOCKED_SURFACES,
    DEFAULT_VALIDATORS,
    select_self_build_candidate,
)


SCHEMA = "AIOS_SELF_BUILD_EXECUTION_PACKET.v1"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _int_value(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


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


def build_self_build_execution_packet(
    candidate: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Convert a selected candidate into a structured, inert packet object."""

    payload = payload or {}
    candidate = candidate or select_self_build_candidate(payload)
    candidate_id = _safe_str(candidate.get("candidate_id")) or "AIOS-SELF-BUILD-CANDIDATE"
    packet_id = _safe_str(payload.get("packet_id")) or f"{candidate_id}-EXECUTION-PACKET"
    max_repair_attempts = max(0, min(_int_value(payload.get("max_repair_attempts"), 2), 5))
    timebox_minutes = max(5, min(_int_value(payload.get("timebox_minutes"), 60), 240))
    validators = _dedupe(_as_list(candidate.get("required_validators")) or DEFAULT_VALIDATORS)
    allowed_files = _dedupe(_as_list(candidate.get("allowed_files")))

    return {
        "schema": SCHEMA,
        "packet_id": packet_id,
        "identity_marker": "AIOS-AUTONOMOUS-SELF-BUILD-EXECUTOR-BURN-IN-V1",
        "supervisor_identity": "ChatGPT Supervisor / Human-guided execution authority",
        "worker_identity": "Codex CLI local implementation worker",
        "zone": "AUTONOMOUS_SELF_BUILD_EXECUTION",
        "approval_authority": "Human Owner / Anthony",
        "mode": "APPLY_LOCAL_SELF_BUILD",
        "worktree": _safe_str(payload.get("worktree")) or r"C:\Dev\Ai.Os",
        "branch": _safe_str(payload.get("branch")) or "feature/autonomous-self-build-executor-burn-in-v1",
        "objective": _safe_str(candidate.get("objective")),
        "allowed_files": allowed_files,
        "blocked_files": [
            ".env",
            "secrets/**",
            "broker/**",
            "oanda/**",
            "automation/orchestration/queues/**",
            "automation/orchestration/locks/**",
            "automation/orchestration/approvals/**",
            "automation/orchestration/campaign_registry/**",
            "dashboard/**",
            "app/**",
            "website/**",
        ],
        "forbidden_surfaces": list(BLOCKED_SURFACES),
        "validator_chain": validators,
        "repair_policy": {
            "bounded": True,
            "max_repair_attempts": max_repair_attempts,
            "arbitrary_code_edits_allowed": False,
            "deterministic_stub_only": True,
        },
        "timebox_minutes": timebox_minutes,
        "max_repair_attempts": max_repair_attempts,
        "stop_conditions": [
            "SOS_ACTIVE",
            "PROTECTED_BOUNDARY_HIT",
            "MAX_REPAIR_ATTEMPTS_EXHAUSTED",
            "TIMEBOX_EXCEEDED",
            "VALIDATION_CRITICAL_FAIL",
            "PUSH_PR_MERGE_REQUESTED",
        ],
        "commit_policy": "LOCAL_COMMIT_ONLY_WITH_APPROVAL",
        "push_pr_merge_policy": "BLOCKED_IN_THIS_PACKET",
        "human_wake_policy": {
            "wake_for": [
                "SOS hard stop",
                "protected action attempt",
                "secrets/.env boundary",
                "broker/OANDA/live trading/webhook/order boundary",
                "repo corruption",
                "validator critical fail",
                "timebox breach",
            ],
            "do_not_wake_for": [
                "routine validator WARN",
                "normal deterministic self-build completion",
                "expected repair exhaustion without protected boundary",
            ],
        },
        "safety": {
            "data_only": True,
            "writes_files": False,
            "creates_ready_stage": False,
            "mutates_registry": False,
            "mutates_queue": False,
            "mutates_locks": False,
            "mutates_approval": False,
            "touches_secrets_or_env": False,
            "broker_or_live_trading": False,
            "pushes": False,
            "creates_pr": False,
            "merges": False,
        },
        "generated_utc": _safe_str(payload.get("generated_utc")) or _now(),
    }
