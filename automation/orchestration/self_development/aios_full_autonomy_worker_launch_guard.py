"""Pure AIOS full-autonomy worker launch guard.

This module gates whether a command preview may proceed to a future, separate
approved worker-launch packet. It never launches workers, starts runtime,
enables schedulers, mutates queues, mutates locks, mutates approvals, mutates
registries, writes reports, writes telemetry, or writes relay state.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_FULL_AUTONOMY_WORKER_LAUNCH_GUARD_RESULT.v1"
MODE = "DRY_RUN_READ_ONLY"

GUARD_DECISIONS = (
    "LAUNCH_DENIED",
    "LAUNCH_REVIEW_REQUIRED",
    "LAUNCH_AWAITING_HUMAN_APPROVAL",
    "LAUNCH_APPROVED_FOR_FUTURE_PACKET_NOT_EXECUTED",
    "BLOCKED_BY_SOS",
    "BLOCKED_BY_VALIDATORS",
    "BLOCKED_BY_LANES",
    "BLOCKED_BY_WORKER_COUNT",
    "BLOCKED_BY_REPO_STATE",
)

PASS_STATUSES = {"PASS", "CLEAR", "OK", "GREEN"}
WARN_PASS_STATUSES = {"WARN_REVIEWED"}
SOS_ACTIVE_STATUSES = {"SOS_ACTIVE", "SOS", "SOS_HARD_STOP", "EMERGENCY", "CRITICAL"}

READY_COMMAND_DECISIONS = {
    "COMMAND_PREVIEW_READY_APPROVED_BUT_NOT_EXECUTED",
    "COMMAND_PREVIEW_READY_AWAITING_APPROVAL",
}

READY_PREFLIGHT_DECISIONS = {
    "PREFLIGHT_PASS_WORKER_LAUNCH_ELIGIBLE_BUT_NOT_EXECUTED",
    "PREFLIGHT_PASS_AWAITING_HUMAN_APPROVAL",
}

PROTECTED_LANES = {
    "runtime_execution",
    "scheduler",
    "daemon",
    "live_trading",
    "approval_mutation",
    "queue_mutation",
    "lock_mutation",
    "registry_mutation",
    "reports_write",
    "telemetry_write",
    "relay_write",
    "dashboard_ui",
    "trading_lab",
    "forex",
    "oanda",
    "webhook",
    "orders",
}

SECRET_OR_BROKER_LANES = {"broker", "secrets", "secret", "env", ".env", "live_trading", "oanda", "webhook", "orders"}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _normalized(value: Any) -> str:
    return _safe_str(value).upper().replace("-", "_").replace(" ", "_") or "UNKNOWN"


def _lane_key(value: Any) -> str:
    return _safe_str(value).lower().replace("-", "_").replace(" ", "_")


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = _safe_str(value).lower()
    if not text:
        return default
    return text in {"true", "1", "yes", "y", "on", "approved", "present"}


def _int_value(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        key = _safe_str(item)
        if key and key not in seen:
            result.append(key)
            seen.add(key)
    return result


def _approval_present(value: Any) -> bool:
    text = _safe_str(value)
    return bool(text and _normalized(text) not in {"NONE", "MISSING", "FALSE", "NO", "0", "NOT_SUPPLIED"})


def _status_is_pass(value: Any, allow_warn_reviewed: bool = False) -> bool:
    normalized = _normalized(value)
    return normalized in PASS_STATUSES or (allow_warn_reviewed and normalized in WARN_PASS_STATUSES)


def _requested_lanes(value: Any) -> list[str]:
    result: list[str] = []
    for item in _as_list(value):
        if isinstance(item, str):
            parts = item.split(",")
        else:
            parts = [item]
        for part in parts:
            lane = _lane_key(part)
            if lane:
                result.append(lane)
    return _dedupe(result)


def _repo_stop_conditions(repo_state: dict[str, Any]) -> list[str]:
    stops: list[str] = []
    if repo_state and not _bool(repo_state.get("branch_matches_expected"), default=True):
        stops.append("BRANCH_MISMATCH")
    if (
        _bool(repo_state.get("dirty"))
        and _bool(repo_state.get("fail_on_dirty_worktree"), default=True)
        and not _bool(repo_state.get("dirty_allowed_for_full_autonomy_worker_launch_guard_validation"))
    ):
        stops.append("DIRTY_WORKTREE")
    return stops


def _no_write_stop_conditions(no_write_proof: dict[str, Any]) -> list[str]:
    if _bool(no_write_proof.get("changed")):
        return ["WRITE_SURFACE_RISK"]
    return []


def _protected_lane_hits(lanes: list[str]) -> list[str]:
    protected = PROTECTED_LANES | SECRET_OR_BROKER_LANES
    return [lane for lane in lanes if lane in protected]


def _safety(status: str) -> dict[str, Any]:
    return {
        "status": status,
        "console_only": True,
        "writes_files": False,
        "writes_reports": False,
        "writes_telemetry": False,
        "writes_packet_drafts": False,
        "writes_proposed_packets": False,
        "creates_ready_stage": False,
        "mutates_registry": False,
        "mutates_queue": False,
        "mutates_locks": False,
        "mutates_approval": False,
        "mutates_approvals": False,
        "writes_relay": False,
        "starts_runtime": False,
        "launches_workers": False,
        "enables_scheduler": False,
        "starts_daemon": False,
        "touches_secrets_or_env": False,
        "secrets_or_env_access": False,
        "broker_or_live_trading": False,
        "protected_actions_blocked": True,
        "human_owner_required_before_worker_launch": True,
        "human_owner_required_before_protected_action": True,
        "launch_executed": False,
        "self_approval_allowed": False,
    }


def _decision(
    repo_stops: list[str],
    command_decision: str,
    approval_present: bool,
    identity_status: str,
    validator_status: str,
    approval_sos_status: str,
    preflight_decision: str,
    lanes: list[str],
    requested_worker_count: int,
    max_parallel_workers: int,
) -> tuple[str, list[str], list[str], str]:
    stops = list(repo_stops)
    missing: list[str] = []

    if "WRITE_SURFACE_RISK" in repo_stops or "BRANCH_MISMATCH" in repo_stops or "DIRTY_WORKTREE" in repo_stops:
        return "BLOCKED_BY_REPO_STATE", ["clean_repo_and_expected_branch"], stops, "No launch authorization. Restore expected clean repo state first."

    if _normalized(approval_sos_status) in SOS_ACTIVE_STATUSES:
        stops.append("SOS_ACTIVE")
        return "BLOCKED_BY_SOS", ["approval_sos_clear"], _dedupe(stops), "Wake the Human Owner and run approval/SOS hard-gate review."

    if not _status_is_pass(identity_status):
        return "BLOCKED_BY_VALIDATORS", ["identity_spine_pass"], stops, "Run identity spine validator before any future worker launch packet."

    if not _status_is_pass(validator_status, allow_warn_reviewed=True):
        return "BLOCKED_BY_VALIDATORS", ["validator_chain_pass_or_warn_reviewed"], stops, "Run orchestration validator chain before any future worker launch packet."

    if preflight_decision not in READY_PREFLIGHT_DECISIONS:
        return "LAUNCH_REVIEW_REQUIRED", ["preflight_pass_worker_launch_eligible"], stops, "Refresh worker launch preflight evidence before future launch authorization."

    if not lanes:
        return "BLOCKED_BY_LANES", ["allowed_lanes_non_empty"], stops, "Provide at least one allowed worker lane before future launch authorization."

    protected_hits = _protected_lane_hits(lanes)
    if protected_hits:
        return "BLOCKED_BY_LANES", [f"remove_protected_lane:{lane}" for lane in protected_hits], stops, "Remove protected, secret, broker, or live-trading lanes before future launch authorization."

    if requested_worker_count <= 0:
        return "BLOCKED_BY_WORKER_COUNT", ["requested_worker_count_positive"], stops, "Requested worker count must be positive before future launch authorization."

    if requested_worker_count > max_parallel_workers:
        return "BLOCKED_BY_WORKER_COUNT", ["worker_count_within_max_parallel_workers"], stops, "Reduce requested worker count to the maximum allowed worker count."

    if command_decision not in READY_COMMAND_DECISIONS:
        return "LAUNCH_REVIEW_REQUIRED", ["command_preview_ready"], stops, "Refresh worker launch command preview before future launch authorization."

    if not approval_present:
        return "LAUNCH_AWAITING_HUMAN_APPROVAL", ["human_owner_worker_launch_approval"], stops, "Obtain explicit Human Owner worker-launch approval before any future launch packet."

    return (
        "LAUNCH_APPROVED_FOR_FUTURE_PACKET_NOT_EXECUTED",
        [],
        stops,
        "Future launch packet may be prepared separately; this guard did not launch workers.",
    )


def build_full_autonomy_worker_launch_guard_result(payload: dict[str, Any]) -> dict[str, Any]:
    repo_state = _as_dict(payload.get("repo_state"))
    no_write_proof = _as_dict(payload.get("no_write_proof"))
    command_decision = _normalized(payload.get("command_decision") or "UNKNOWN")
    approval_present = _approval_present(payload.get("human_owner_worker_launch_approval"))
    identity_status = _normalized(payload.get("identity_spine_status") or "UNKNOWN")
    validator_status = _normalized(payload.get("validator_chain_status") or "UNKNOWN")
    approval_sos_status = _normalized(payload.get("approval_sos_status") or "UNKNOWN")
    preflight_decision = _normalized(payload.get("preflight_decision") or "UNKNOWN")
    lanes = _requested_lanes(payload.get("allowed_lanes"))
    requested_worker_count = max(0, _int_value(payload.get("requested_worker_count"), 0))
    max_parallel_workers = max(0, _int_value(payload.get("max_parallel_workers"), 0))
    repo_stops = _dedupe(_repo_stop_conditions(repo_state) + _no_write_stop_conditions(no_write_proof))

    guard_decision, missing, stop_conditions, next_safe_action = _decision(
        repo_stops,
        command_decision,
        approval_present,
        identity_status,
        validator_status,
        approval_sos_status,
        preflight_decision,
        lanes,
        requested_worker_count,
        max_parallel_workers,
    )
    if guard_decision not in GUARD_DECISIONS:
        guard_decision = "LAUNCH_REVIEW_REQUIRED"

    allowed_for_future = guard_decision == "LAUNCH_APPROVED_FOR_FUTURE_PACKET_NOT_EXECUTED"
    safety_status = "PASS" if allowed_for_future else "REVIEW_REQUIRED"
    if guard_decision.startswith("BLOCKED_BY_"):
        safety_status = "BLOCKED_BY_WRITE_SURFACE_RISK" if "WRITE_SURFACE_RISK" in stop_conditions else "BLOCKED"

    protected_hits = _protected_lane_hits(lanes)
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_utc": _safe_str(payload.get("generated_utc") or _now()),
        "repo_state": repo_state,
        "guard_decision": guard_decision,
        "input_command_summary": {
            "command_decision": command_decision,
            "preflight_decision": preflight_decision,
            "requested_worker_count": requested_worker_count,
            "max_parallel_workers": max_parallel_workers,
            "allowed_lanes": lanes,
        },
        "approval_state": {
            "human_owner_worker_launch_approval_present": approval_present,
            "human_owner_required_before_worker_launch": True,
            "self_approval_allowed": False,
            "missing_requirements": [item for item in missing if "approval" in item],
        },
        "validator_state": {
            "identity_spine_status": identity_status,
            "validator_chain_status": validator_status,
            "identity_spine_pass": _status_is_pass(identity_status),
            "validator_chain_pass_or_warn_reviewed": _status_is_pass(validator_status, allow_warn_reviewed=True),
        },
        "lane_state": {
            "allowed_lanes": lanes,
            "protected_lane_hits": protected_hits,
            "lanes_non_empty": bool(lanes),
            "protected_lanes_blocked": True,
        },
        "worker_count_state": {
            "requested_worker_count": requested_worker_count,
            "max_parallel_workers": max_parallel_workers,
            "within_limit": requested_worker_count > 0 and requested_worker_count <= max_parallel_workers,
        },
        "sos_state": {
            "approval_sos_status": approval_sos_status,
            "sos_active": _normalized(approval_sos_status) in SOS_ACTIVE_STATUSES,
            "wake_required": guard_decision == "BLOCKED_BY_SOS",
        },
        "launch_allowed_for_future_packet": allowed_for_future,
        "launch_executed": False,
        "safety": _safety(safety_status),
        "no_write_proof": no_write_proof,
        "missing_requirements": _dedupe(missing),
        "stop_conditions": _dedupe(stop_conditions),
        "next_safe_action": next_safe_action,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Build an AIOS full-autonomy worker launch guard result from JSON evidence.")
    parser.add_argument("--payload-base64", default="")
    args = parser.parse_args()
    if args.payload_base64:
        payload_text = base64.b64decode(args.payload_base64.encode("ascii")).decode("utf-8")
    else:
        payload_text = sys.stdin.read()
    result = build_full_autonomy_worker_launch_guard_result(json.loads(payload_text))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["safety"]["status"] in {"PASS", "REVIEW_REQUIRED"} else 1


if __name__ == "__main__":
    raise SystemExit(_main())
