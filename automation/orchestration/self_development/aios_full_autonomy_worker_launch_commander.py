"""Pure AIOS full-autonomy worker launch command composer.

This module builds a structured preview for a future, separately approved
worker-launch packet. It never launches workers, starts runtime, enables
schedulers, mutates queues, mutates locks, mutates approvals, mutates
registries, writes reports, writes telemetry, or writes relay state.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_FULL_AUTONOMY_WORKER_LAUNCH_COMMAND_RESULT.v1"
MODE = "DRY_RUN_READ_ONLY"

COMMAND_DECISIONS = (
    "NO_COMMAND",
    "COMMAND_PREVIEW_BLOCKED",
    "COMMAND_PREVIEW_REVIEW_REQUIRED",
    "COMMAND_PREVIEW_READY_AWAITING_APPROVAL",
    "COMMAND_PREVIEW_READY_APPROVED_BUT_NOT_EXECUTED",
)

READY_PREFLIGHT_DECISIONS = {
    "PREFLIGHT_PASS_WORKER_LAUNCH_ELIGIBLE_BUT_NOT_EXECUTED",
    "PREFLIGHT_PASS_AWAITING_HUMAN_APPROVAL",
}

REVIEW_PREFLIGHT_DECISIONS = {
    "REVIEW_REQUIRED",
    "PREFLIGHT_PASS_ADVISORY_ONLY",
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
BLOCKED_LANES = sorted(PROTECTED_LANES | SECRET_OR_BROKER_LANES)

PROTECTED_SURFACE_BLOCKS = [
    "runtime_start",
    "worker_launch_execution",
    "scheduler_enablement",
    "daemon_launch",
    "queue_mutation",
    "lock_mutation",
    "approval_mutation",
    "registry_mutation",
    "ready_stage_creation",
    "packet_file_write",
    "reports_write",
    "telemetry_write",
    "relay_write",
    "dashboard_ui",
    "secrets_env_access",
    "broker_live_trading",
]

REQUIRED_VALIDATORS = [
    {
        "validator_id": "full_autonomy_worker_launch_preflight_gate",
        "path": "automation/orchestration/self_development/Test-AiOsFullAutonomyWorkerLaunchPreflightGate.DRY_RUN.ps1",
        "purpose": "Confirm future worker launch remains eligible before any separate launch packet.",
    },
    {
        "validator_id": "identity_spine",
        "path": "automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1",
        "purpose": "Confirm worker identity, lane, branch, and stop-point metadata.",
    },
    {
        "validator_id": "orchestration_validator_chain",
        "path": "automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1",
        "purpose": "Refresh validator-chain evidence before a future launch packet.",
    },
    {
        "validator_id": "approval_sos_hard_gate",
        "path": "automation/orchestration/operator_control/Test-AiOsApprovalSosHardGate.DRY_RUN.ps1",
        "purpose": "Confirm no SOS or approval hard stop is active.",
    },
]


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
        and not _bool(repo_state.get("dirty_allowed_for_full_autonomy_worker_launch_commander_validation"))
    ):
        stops.append("DIRTY_WORKTREE")
    return stops


def _no_write_stop_conditions(no_write_proof: dict[str, Any]) -> list[str]:
    if _bool(no_write_proof.get("changed")):
        return ["WRITE_SURFACE_RISK"]
    return []


def _protected_lane_hits(lanes: list[str]) -> list[str]:
    return [lane for lane in lanes if lane in PROTECTED_LANES]


def _secret_or_broker_hits(lanes: list[str]) -> list[str]:
    return [lane for lane in lanes if lane in SECRET_OR_BROKER_LANES]


def _safe_worker_count(requested: int, maximum: int) -> tuple[int, int]:
    safe_max = max(0, maximum)
    safe_requested = max(0, requested)
    return safe_requested, safe_max


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


def _empty_command_preview(reason: str) -> dict[str, Any]:
    return {
        "emitted": False,
        "executable_in_this_packet": False,
        "requires_separate_approved_launch_packet": True,
        "command_line_preview": "",
        "reason": reason,
        "launch_executed": False,
    }


def _command_preview(
    worker_count: int,
    worker_posture: str,
    operating_profile: str,
    allowed_lanes: list[str],
    timebox_minutes: int,
    stop_on_first_failure: bool,
    approved: bool,
) -> dict[str, Any]:
    lanes_text = ",".join(allowed_lanes)
    approval_arg = "<HUMAN_OWNER_WORKER_LAUNCH_APPROVAL_REQUIRED>"
    if approved:
        approval_arg = "<SUPPLIED_IN_FUTURE_APPROVED_PACKET>"
    command_line = (
        "powershell -NoProfile -ExecutionPolicy Bypass -File "
        "automation/orchestration/workers/Invoke-AiOsApprovedWorkerLaunch.FUTURE_PACKET.ps1 "
        f"-WorkerPosture {worker_posture} "
        f"-OperatingProfile {operating_profile} "
        f"-WorkerCount {worker_count} "
        f"-AllowedLanes {lanes_text} "
        f"-TimeboxMinutes {timebox_minutes} "
        f"-HumanOwnerWorkerLaunchApproval {approval_arg} "
        f"-StopOnFirstFailure ${str(stop_on_first_failure).lower()}"
    )
    return {
        "emitted": True,
        "executable_in_this_packet": False,
        "requires_separate_approved_launch_packet": True,
        "command_line_preview": command_line,
        "worker_count": worker_count,
        "worker_posture": worker_posture,
        "allowed_lanes": allowed_lanes,
        "timebox_minutes": timebox_minutes,
        "stop_on_first_failure": stop_on_first_failure,
        "approval_evidence_required": True,
        "launch_executed": False,
    }


def _rollback_preview() -> dict[str, Any]:
    return {
        "executable_in_this_packet": False,
        "requires_separate_approved_stop_packet": True,
        "instruction": "If a future approved launch packet fails, stop workers through that packet's approved stop path and wake the Human Owner for SOS or protected-boundary review.",
        "command_line_preview": "No command emitted by this DRY_RUN_READ_ONLY composer.",
    }


def _decision(
    repo_stops: list[str],
    preflight_decision: str,
    approval_present: bool,
    lanes: list[str],
    worker_count: int,
    max_workers: int,
) -> tuple[str, list[str], list[str], str]:
    stops = list(repo_stops)
    missing: list[str] = []
    if "WRITE_SURFACE_RISK" in repo_stops or "BRANCH_MISMATCH" in repo_stops or "DIRTY_WORKTREE" in repo_stops:
        return "COMMAND_PREVIEW_BLOCKED", ["clean_repo_and_expected_branch"], stops, "No command preview emitted. Restore expected clean repo state first."

    if not lanes:
        return "COMMAND_PREVIEW_BLOCKED", ["allowed_lanes_non_empty"], stops, "No command preview emitted. Provide at least one allowed worker lane."

    secret_hits = _secret_or_broker_hits(lanes)
    if secret_hits:
        return (
            "COMMAND_PREVIEW_BLOCKED",
            [f"remove_secret_or_broker_lane:{lane}" for lane in secret_hits],
            stops,
            "No command preview emitted. Remove secrets, broker, OANDA, webhook, orders, or live-trading lanes.",
        )

    protected_hits = _protected_lane_hits(lanes)
    if protected_hits:
        return (
            "COMMAND_PREVIEW_BLOCKED",
            [f"remove_protected_lane:{lane}" for lane in protected_hits],
            stops,
            "No command preview emitted. Remove protected lanes before composing worker launch.",
        )

    if worker_count <= 0:
        return "COMMAND_PREVIEW_REVIEW_REQUIRED", ["requested_worker_count_positive"], stops, "Requested worker count must be positive for a launch command preview."

    if worker_count > max_workers:
        return "COMMAND_PREVIEW_REVIEW_REQUIRED", ["worker_count_within_max_parallel_workers"], stops, "Reduce requested worker count to the maximum allowed worker count."

    if preflight_decision in READY_PREFLIGHT_DECISIONS:
        if approval_present:
            return (
                "COMMAND_PREVIEW_READY_APPROVED_BUT_NOT_EXECUTED",
                [],
                stops,
                "Future launch command preview is approved for a separate packet only; this packet did not execute it.",
            )
        return (
            "COMMAND_PREVIEW_READY_AWAITING_APPROVAL",
            ["human_owner_worker_launch_approval"],
            stops,
            "Future launch command preview is ready, but explicit Human Owner worker-launch approval is still required.",
        )

    if preflight_decision in REVIEW_PREFLIGHT_DECISIONS:
        return "COMMAND_PREVIEW_REVIEW_REQUIRED", ["preflight_pass_worker_launch_eligible"], stops, "Refresh preflight gate evidence before composing launch command."

    return "COMMAND_PREVIEW_BLOCKED", ["preflight_pass_worker_launch_eligible"], stops, "No command preview emitted because preflight did not pass."


def build_full_autonomy_worker_launch_command_result(payload: dict[str, Any]) -> dict[str, Any]:
    repo_state = _as_dict(payload.get("repo_state"))
    no_write_proof = _as_dict(payload.get("no_write_proof"))
    generated_utc = _safe_str(payload.get("generated_utc") or _now())
    preflight_decision = _normalized(payload.get("preflight_decision") or "UNKNOWN")
    requested_posture = _normalized(payload.get("requested_worker_posture") or "READ_ONLY_VALIDATOR_CREW")
    operating_profile = _normalized(payload.get("operating_profile") or "24H_SUPERVISED")
    lanes = _requested_lanes(payload.get("allowed_lanes"))
    requested_worker_count, max_parallel_workers = _safe_worker_count(
        _int_value(payload.get("requested_worker_count"), 1),
        _int_value(payload.get("max_parallel_workers"), 1),
    )
    timebox_minutes = max(1, _int_value(payload.get("launch_timebox_minutes"), 60))
    stop_on_first_failure = _bool(payload.get("stop_on_first_failure"), default=True)
    approval_present = _approval_present(payload.get("human_owner_worker_launch_approval"))
    repo_stops = _dedupe(_repo_stop_conditions(repo_state) + _no_write_stop_conditions(no_write_proof))

    command_decision, missing, stop_conditions, next_safe_action = _decision(
        repo_stops,
        preflight_decision,
        approval_present,
        lanes,
        requested_worker_count,
        max_parallel_workers,
    )

    preview_allowed = command_decision in {
        "COMMAND_PREVIEW_READY_AWAITING_APPROVAL",
        "COMMAND_PREVIEW_READY_APPROVED_BUT_NOT_EXECUTED",
    }
    worker_count = min(requested_worker_count, max_parallel_workers) if preview_allowed else 0
    if preview_allowed:
        command_preview = _command_preview(
            worker_count,
            requested_posture,
            operating_profile,
            lanes,
            timebox_minutes,
            stop_on_first_failure,
            command_decision == "COMMAND_PREVIEW_READY_APPROVED_BUT_NOT_EXECUTED",
        )
    else:
        command_preview = _empty_command_preview(next_safe_action)

    safety_status = "PASS" if command_decision == "COMMAND_PREVIEW_READY_APPROVED_BUT_NOT_EXECUTED" else "REVIEW_REQUIRED"
    if command_decision == "COMMAND_PREVIEW_BLOCKED":
        safety_status = "BLOCKED_BY_WRITE_SURFACE_RISK" if "WRITE_SURFACE_RISK" in stop_conditions else "BLOCKED"

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_utc": generated_utc,
        "repo_state": repo_state,
        "input_preflight_summary": {
            "preflight_decision": preflight_decision,
            "requested_worker_posture": requested_posture,
            "operating_profile": operating_profile,
            "human_owner_worker_launch_approval_present": approval_present,
        },
        "command_decision": command_decision,
        "worker_launch_command_preview": command_preview,
        "worker_count": worker_count,
        "worker_posture": requested_posture,
        "allowed_lanes": lanes,
        "blocked_lanes": list(BLOCKED_LANES),
        "timebox_minutes": timebox_minutes,
        "stop_conditions": _dedupe(stop_conditions),
        "required_validators_before_launch": list(REQUIRED_VALIDATORS),
        "human_owner_approval_required": {
            "required": True,
            "present": approval_present,
            "required_before_future_launch_packet": True,
            "validator_pass_is_not_approval": True,
            "self_approval_allowed": False,
        },
        "launch_executed": False,
        "rollback_or_stop_command_preview": _rollback_preview(),
        "evidence_required": [
            "preflight_gate_pass",
            "identity_spine_pass",
            "validator_chain_pass_or_warn_reviewed",
            "approval_sos_clear",
            "explicit_human_owner_worker_launch_approval",
            "clean_repo_and_expected_branch",
        ],
        "protected_surface_blocks": list(PROTECTED_SURFACE_BLOCKS),
        "safety": _safety(safety_status),
        "no_write_proof": no_write_proof,
        "missing_requirements": _dedupe(missing),
        "next_safe_action": next_safe_action,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Build an AIOS full-autonomy worker launch command preview from JSON evidence.")
    parser.add_argument("--payload-base64", default="")
    args = parser.parse_args()
    if args.payload_base64:
        payload_text = base64.b64decode(args.payload_base64.encode("ascii")).decode("utf-8")
    else:
        payload_text = sys.stdin.read()
    result = build_full_autonomy_worker_launch_command_result(json.loads(payload_text))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["safety"]["status"] in {"PASS", "REVIEW_REQUIRED"} else 1


if __name__ == "__main__":
    raise SystemExit(_main())
