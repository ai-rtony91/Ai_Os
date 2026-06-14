"""Pure AIOS full-autonomy worker launch preflight gate logic.

This module evaluates whether AIOS has enough evidence for a future,
separately approved worker-launch step. It never launches workers, starts
runtime, enables schedulers, mutates queues, mutates locks, mutates approvals,
mutates registries, or writes operational evidence.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_FULL_AUTONOMY_WORKER_LAUNCH_PREFLIGHT_GATE_RESULT.v1"
MODE = "DRY_RUN_READ_ONLY"

REQUESTED_AUTONOMY_LEVELS = (
    "LEVEL_0_MANUAL",
    "LEVEL_1_ASSISTED",
    "LEVEL_2_SEMI_AUTONOMOUS",
    "LEVEL_3_SUPERVISED_AUTONOMY",
    "LEVEL_4_CONDITIONAL_FULL_AUTONOMY",
    "LEVEL_5_FULL_AUTONOMY_REQUESTED",
)

OPERATING_PROFILES = (
    "12H_SUPERVISED",
    "24H_SUPERVISED",
    "WEEKEND",
    "VACATION",
    "OVERNIGHT",
    "EMERGENCY_REVIEW",
    "FULL_AUTONOMY_SUPERVISED",
)

REQUESTED_WORKER_POSTURES = (
    "NO_WORKERS",
    "READ_ONLY_VALIDATOR_CREW",
    "PACKET_PREVIEW_CREW",
    "SUPERVISED_DAY_CREW_12H",
    "SUPERVISED_DAY_NIGHT_CREW_24H",
    "WEEKEND_LOW_TOUCH_CREW",
    "VACATION_EMERGENCY_ONLY_CREW",
    "FULL_AUTONOMY_SUPERVISED_CREW",
)

LAUNCH_DECISIONS = (
    "DENIED",
    "REVIEW_REQUIRED",
    "PREFLIGHT_PASS_ADVISORY_ONLY",
    "PREFLIGHT_PASS_AWAITING_HUMAN_APPROVAL",
    "PREFLIGHT_PASS_WORKER_LAUNCH_ELIGIBLE_BUT_NOT_EXECUTED",
    "BLOCKED_BY_SOS",
    "BLOCKED_BY_APPROVAL",
    "BLOCKED_BY_IDENTITY",
    "BLOCKED_BY_VALIDATORS",
    "BLOCKED_BY_LOCK_COLLISION",
    "BLOCKED_BY_EMPTY_ALLOWED_LANES",
    "BLOCKED_BY_PROTECTED_LANE",
    "BLOCKED_BY_REPO_STATE",
    "BLOCKED_BY_SECRETS_OR_BROKER_BOUNDARY",
)

PASS_STATUSES = {"PASS", "CLEAR", "OK", "GREEN"}
WARN_PASS_STATUSES = {"WARN_REVIEWED"}
SOS_ACTIVE_STATUSES = {"SOS_ACTIVE", "SOS", "SOS_HARD_STOP", "EMERGENCY", "CRITICAL"}
ALLOWED_ACTIVATION_STATUSES = {
    "PASS",
    "READ_ONLY_MONITOR",
    "VALIDATOR_ONLY_ALLOWED",
    "PACKET_PREVIEW_ALLOWED",
    "REVIEW_REQUIRED",
}

POSTURE_POLICIES: dict[str, dict[str, Any]] = {
    "NO_WORKERS": {
        "allowed_lanes": [],
        "max_parallel_workers": 0,
        "implementation_allowed": False,
        "requires_approval": False,
        "wake_policy": "No worker launch posture is selected; no wake is required unless SOS or protected boundary appears.",
    },
    "READ_ONLY_VALIDATOR_CREW": {
        "allowed_lanes": ["validator", "self_audit", "readiness_review", "approval_sos_review"],
        "max_parallel_workers": 2,
        "implementation_allowed": False,
        "requires_approval": False,
        "wake_policy": "Read-only validator posture; wake for SOS, protected action, security, secrets, broker, or live-trading boundary.",
    },
    "PACKET_PREVIEW_CREW": {
        "allowed_lanes": ["packet_preview", "validator", "readiness_review"],
        "max_parallel_workers": 2,
        "implementation_allowed": False,
        "requires_approval": False,
        "wake_policy": "Packet-preview posture; wake for SOS, protected action, security, secrets, broker, or live-trading boundary.",
    },
    "SUPERVISED_DAY_CREW_12H": {
        "allowed_lanes": ["validator", "self_audit", "packet_preview", "readiness_review"],
        "max_parallel_workers": 2,
        "implementation_allowed": False,
        "requires_approval": True,
        "wake_policy": "12H supervised posture; wake for SOS, protected action, security, secrets, broker, or live-trading boundary.",
    },
    "SUPERVISED_DAY_NIGHT_CREW_24H": {
        "allowed_lanes": ["validator", "no_ready_stage_discovery", "packet_preview", "approval_sos_review"],
        "max_parallel_workers": 3,
        "implementation_allowed": False,
        "requires_approval": True,
        "wake_policy": "24H supervised posture; wake only for SOS, protected action, security, secrets, broker, or live-trading boundary.",
    },
    "WEEKEND_LOW_TOUCH_CREW": {
        "allowed_lanes": ["validator", "status_review"],
        "max_parallel_workers": 1,
        "implementation_allowed": False,
        "requires_approval": False,
        "wake_policy": "Weekend low-touch posture; wake only for SOS or protected boundary.",
    },
    "VACATION_EMERGENCY_ONLY_CREW": {
        "allowed_lanes": ["approval_sos_review", "security_boundary_review"],
        "max_parallel_workers": 1,
        "implementation_allowed": False,
        "requires_approval": False,
        "wake_policy": "Vacation emergency-only posture; wake only for SOS, security, secrets, broker, or live-trading boundary.",
    },
    "FULL_AUTONOMY_SUPERVISED_CREW": {
        "allowed_lanes": ["validator", "packet_preview", "full_autonomy_prerequisite_review", "approval_sos_review"],
        "max_parallel_workers": 3,
        "implementation_allowed": False,
        "requires_approval": True,
        "wake_policy": "Full-autonomy supervised preview posture; wake for SOS, protected action, security, secrets, broker, or live-trading boundary.",
    },
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

BLOCKED_WORKER_LANES = sorted(PROTECTED_LANES | SECRET_OR_BROKER_LANES)

PROTECTED_ACTIONS = [
    ("worker_launch", "worker launch"),
    ("runtime_start", "runtime start"),
    ("scheduler_enablement", "scheduler enablement"),
    ("daemon_launch", "daemon launch"),
    ("queue_mutation", "queue mutation"),
    ("lock_mutation", "lock mutation"),
    ("approval_mutation", "approval mutation"),
    ("registry_mutation", "registry mutation"),
    ("ready_stage_creation", "READY stage creation"),
    ("packet_file_write", "packet file write"),
    ("reports_write", "Reports write"),
    ("telemetry_write", "telemetry write"),
    ("relay_write", "relay write"),
    ("dashboard_ui", "dashboard/UI work"),
    ("broker_live_trading", "broker/live trading/OANDA/webhook/order path"),
    ("secrets_env", "secrets/.env access"),
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
    if isinstance(value, list):
        return value
    return [value]


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
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        key = _safe_str(item)
        if key and key not in seen:
            result.append(key)
            seen.add(key)
    return result


def _status_is_pass(value: Any, allow_warn_reviewed: bool = False) -> bool:
    normalized = _normalized(value)
    return normalized in PASS_STATUSES or (allow_warn_reviewed and normalized in WARN_PASS_STATUSES)


def _approval_present(value: Any) -> bool:
    text = _safe_str(value)
    return bool(text and _normalized(text) not in {"NONE", "MISSING", "FALSE", "NO", "0", "NOT_SUPPLIED"})


def _repo_stop_conditions(repo_state: dict[str, Any]) -> list[str]:
    stops: list[str] = []
    if repo_state and not _bool(repo_state.get("branch_matches_expected"), default=True):
        stops.append("BRANCH_MISMATCH")
    if (
        _bool(repo_state.get("dirty"))
        and _bool(repo_state.get("fail_on_dirty_worktree"), default=True)
        and not _bool(repo_state.get("dirty_allowed_for_full_autonomy_worker_launch_preflight_gate_validation"))
    ):
        stops.append("DIRTY_WORKTREE")
    return stops


def _no_write_stop_conditions(no_write_proof: dict[str, Any]) -> list[str]:
    if _bool(no_write_proof.get("changed")):
        return ["WRITE_SURFACE_RISK"]
    return []


def _requested_lanes(value: Any) -> list[str]:
    result: list[str] = []
    for item in _as_list(value):
        if isinstance(item, str):
            parts = [part for part in item.split(",")]
        else:
            parts = [item]
        for part in parts:
            lane = _lane_key(part)
            if lane:
                result.append(lane)
    return _dedupe(result)


def _protected_lane_hits(lanes: list[str]) -> list[str]:
    return [lane for lane in lanes if lane in PROTECTED_LANES]


def _secret_or_broker_hits(lanes: list[str]) -> list[str]:
    return [lane for lane in lanes if lane in SECRET_OR_BROKER_LANES]


def _posture_incompatible_lanes(posture: str, lanes: list[str]) -> list[str]:
    policy = POSTURE_POLICIES[posture]
    allowed = {_lane_key(item) for item in policy["allowed_lanes"]}
    return [lane for lane in lanes if lane not in allowed]


def _protected_actions() -> list[dict[str, Any]]:
    return [
        {
            "action_id": action_id,
            "label": label,
            "status": "BLOCKED",
            "human_owner_required": True,
            "reason": "Worker launch preflight is evidence only and never executes protected actions.",
        }
        for action_id, label in PROTECTED_ACTIONS
    ]


def _recommended_validators(decision: str) -> list[dict[str, Any]]:
    validators = [
        {
            "validator_id": "identity_spine",
            "path": "automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1",
            "purpose": "Confirm packet, worker, lane, and stop-point metadata before worker launch approval.",
        },
        {
            "validator_id": "orchestration_validator_chain",
            "path": "automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1",
            "purpose": "Confirm current validator-chain evidence before worker launch approval.",
        },
        {
            "validator_id": "approval_sos_hard_gate",
            "path": "automation/orchestration/operator_control/Test-AiOsApprovalSosHardGate.DRY_RUN.ps1",
            "purpose": "Confirm no approval/SOS hard stop is active.",
        },
        {
            "validator_id": "governed_self_development_soak",
            "path": "automation/orchestration/self_development/Test-AiOsGovernedSelfDevelopmentSoak.DRY_RUN.ps1",
            "purpose": "Confirm governed soak evidence remains PASS.",
        },
        {
            "validator_id": "lock_collision_review",
            "path": "automation/orchestration/locks/PATH_CONFLICT_POLICY_001.md",
            "purpose": "Review lock collision evidence before any future worker launch.",
        },
    ]
    if decision == "BLOCKED_BY_IDENTITY":
        return [validators[0]]
    if decision == "BLOCKED_BY_VALIDATORS":
        return [validators[1], validators[3]]
    if decision == "BLOCKED_BY_SOS":
        return [validators[2]]
    if decision == "BLOCKED_BY_LOCK_COLLISION":
        return [validators[4]]
    return validators


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
        "worker_launch_executed": False,
        "self_approval_allowed": False,
    }


def _decision_details(
    repo_stops: list[str],
    requested_posture: str,
    approval_present: bool,
    identity_status: str,
    validator_status: str,
    approval_sos_status: str,
    soak_status: str,
    activation_gate_status: str,
    worker_posture_bridge_status: str,
    lock_collision_status: str,
    lanes: list[str],
) -> tuple[str, list[str], list[str], str, bool]:
    missing: list[str] = []
    stops: list[str] = list(repo_stops)
    wake_required = False

    if "WRITE_SURFACE_RISK" in repo_stops or "BRANCH_MISMATCH" in repo_stops or "DIRTY_WORKTREE" in repo_stops:
        return "BLOCKED_BY_REPO_STATE", ["clean_repo_and_expected_branch"], stops, "No command recommended. Restore expected clean repo state before worker launch preflight.", False

    if _normalized(approval_sos_status) in SOS_ACTIVE_STATUSES:
        stops.append("SOS_ACTIVE")
        return "BLOCKED_BY_SOS", ["approval_sos_clear"], _dedupe(stops), "Wake the Human Owner and run approval/SOS hard-gate review.", True

    if not _status_is_pass(identity_status):
        return "BLOCKED_BY_IDENTITY", ["identity_spine_pass"], stops, "Run identity spine validator before worker launch preflight.", wake_required

    if not _status_is_pass(validator_status, allow_warn_reviewed=True):
        return "BLOCKED_BY_VALIDATORS", ["validator_chain_pass_or_warn_reviewed"], stops, "Run orchestration validator chain before worker launch preflight.", wake_required

    if _normalized(approval_sos_status) not in PASS_STATUSES:
        return "REVIEW_REQUIRED", ["approval_sos_pass_or_clear"], stops, "Run approval/SOS hard-gate review before worker launch preflight.", wake_required

    if not _status_is_pass(soak_status):
        return "BLOCKED_BY_VALIDATORS", ["governed_soak_pass"], stops, "Run governed self-development soak before worker launch preflight.", wake_required

    if _normalized(activation_gate_status) not in ALLOWED_ACTIVATION_STATUSES:
        return "REVIEW_REQUIRED", ["activation_gate_safe_ceiling"], stops, "Refresh activation gate evidence before worker launch preflight.", wake_required

    if _normalized(worker_posture_bridge_status) == "BLOCKED":
        return "REVIEW_REQUIRED", ["worker_posture_bridge_pass"], stops, "Refresh worker posture bridge evidence before worker launch preflight.", wake_required

    if not _status_is_pass(worker_posture_bridge_status):
        return "REVIEW_REQUIRED", ["worker_posture_bridge_pass"], stops, "Refresh worker posture bridge evidence before worker launch preflight.", wake_required

    if _normalized(lock_collision_status) == "COLLISION":
        return "BLOCKED_BY_LOCK_COLLISION", ["lock_collision_clear"], stops, "Resolve lock collision before worker launch preflight.", wake_required

    if requested_posture == "NO_WORKERS":
        return "PREFLIGHT_PASS_ADVISORY_ONLY", [], stops, "No worker posture selected; no launch action is available.", wake_required

    if not lanes:
        return "BLOCKED_BY_EMPTY_ALLOWED_LANES", ["allowed_lanes_non_empty"], stops, "Provide at least one allowed read-only worker lane before worker launch preflight.", wake_required

    secret_hits = _secret_or_broker_hits(lanes)
    if secret_hits:
        return "BLOCKED_BY_SECRETS_OR_BROKER_BOUNDARY", [f"remove_secret_or_broker_lane:{lane}" for lane in secret_hits], stops, "Remove secrets, broker, OANDA, webhook, orders, or live-trading lanes before worker launch preflight.", wake_required

    protected_hits = _protected_lane_hits(lanes)
    if protected_hits:
        return "BLOCKED_BY_PROTECTED_LANE", [f"remove_protected_lane:{lane}" for lane in protected_hits], stops, "Remove protected lanes before worker launch preflight.", wake_required

    incompatible = _posture_incompatible_lanes(requested_posture, lanes)
    if incompatible:
        return "BLOCKED_BY_PROTECTED_LANE", [f"lane_not_allowed_for_posture:{lane}" for lane in incompatible], stops, "Align allowed lanes with the requested worker posture before worker launch preflight.", wake_required

    if not approval_present:
        return "PREFLIGHT_PASS_AWAITING_HUMAN_APPROVAL", ["human_owner_worker_launch_approval"], stops, "Obtain explicit Human Owner worker-launch approval before any separate launch packet.", wake_required

    return (
        "PREFLIGHT_PASS_WORKER_LAUNCH_ELIGIBLE_BUT_NOT_EXECUTED",
        [],
        stops,
        "Human Owner may run a separate approved worker-launch packet; this preflight did not launch workers.",
        wake_required,
    )


def build_full_autonomy_worker_launch_preflight_gate_result(payload: dict[str, Any]) -> dict[str, Any]:
    requested_level = _normalized(payload.get("requested_autonomy_level") or "LEVEL_4_CONDITIONAL_FULL_AUTONOMY")
    if requested_level not in REQUESTED_AUTONOMY_LEVELS:
        requested_level = "LEVEL_4_CONDITIONAL_FULL_AUTONOMY"
    operating_profile = _normalized(payload.get("operating_profile") or "24H_SUPERVISED")
    if operating_profile not in OPERATING_PROFILES:
        operating_profile = "24H_SUPERVISED"
    requested_posture = _normalized(payload.get("requested_worker_posture") or "READ_ONLY_VALIDATOR_CREW")
    if requested_posture not in REQUESTED_WORKER_POSTURES:
        requested_posture = "READ_ONLY_VALIDATOR_CREW"

    repo_state = _as_dict(payload.get("repo_state"))
    no_write_proof = _as_dict(payload.get("no_write_proof"))
    lanes = _requested_lanes(payload.get("allowed_lanes"))
    policy = POSTURE_POLICIES[requested_posture]
    posture_cap = int(policy["max_parallel_workers"])
    requested_worker_count = max(0, _int_value(payload.get("requested_worker_count"), 1))
    requested_max_parallel = max(0, _int_value(payload.get("max_parallel_workers"), posture_cap))
    max_parallel_workers = min(posture_cap, requested_max_parallel)
    recommended_worker_count = min(requested_worker_count, max_parallel_workers)

    approval_present = _approval_present(payload.get("human_owner_worker_launch_approval"))
    identity_status = _normalized(payload.get("identity_spine_status") or "UNKNOWN")
    validator_status = _normalized(payload.get("validator_chain_status") or "UNKNOWN")
    approval_sos_status = _normalized(payload.get("approval_sos_status") or "UNKNOWN")
    soak_status = _normalized(payload.get("governed_soak_status") or "UNKNOWN")
    activation_status = _normalized(payload.get("activation_gate_status") or "UNKNOWN")
    bridge_status = _normalized(payload.get("worker_posture_bridge_status") or "UNKNOWN")
    lock_status = _normalized(payload.get("lock_collision_status") or "UNKNOWN")
    repo_stops = _dedupe(_repo_stop_conditions(repo_state) + _no_write_stop_conditions(no_write_proof))

    decision, missing, stop_conditions, next_safe_action, wake_required = _decision_details(
        repo_stops,
        requested_posture,
        approval_present,
        identity_status,
        validator_status,
        approval_sos_status,
        soak_status,
        activation_status,
        bridge_status,
        lock_status,
        lanes,
    )
    if decision not in LAUNCH_DECISIONS:
        decision = "REVIEW_REQUIRED"

    eligible = decision == "PREFLIGHT_PASS_WORKER_LAUNCH_ELIGIBLE_BUT_NOT_EXECUTED"
    safety_status = "PASS" if decision.startswith("PREFLIGHT_PASS") else "REVIEW_REQUIRED"
    if decision.startswith("BLOCKED_BY_"):
        safety_status = "BLOCKED_BY_WRITE_SURFACE_RISK" if "WRITE_SURFACE_RISK" in stop_conditions else "BLOCKED"

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_utc": _safe_str(payload.get("generated_utc") or _now()),
        "repo_state": repo_state,
        "requested_autonomy_level": requested_level,
        "operating_profile": operating_profile,
        "requested_worker_posture": requested_posture,
        "input_evidence": {
            "human_owner_worker_launch_approval_present": approval_present,
            "identity_spine_status": identity_status,
            "validator_chain_status": validator_status,
            "approval_sos_status": approval_sos_status,
            "governed_soak_status": soak_status,
            "activation_gate_status": activation_status,
            "worker_posture_bridge_status": bridge_status,
            "lock_collision_status": lock_status,
            "allowed_lanes": lanes,
            "requested_worker_count": requested_worker_count,
            "requested_max_parallel_workers": requested_max_parallel,
        },
        "preflight_decision": {
            "decision": decision,
            "worker_launch_allowed_for_future_step": eligible,
            "worker_launch_executed": False,
            "reason": next_safe_action,
        },
        "worker_launch_allowed_for_future_step": eligible,
        "worker_launch_executed": False,
        "worker_posture": requested_posture,
        "recommended_worker_count": recommended_worker_count,
        "max_parallel_workers": max_parallel_workers,
        "allowed_worker_lanes": lanes,
        "blocked_worker_lanes": list(BLOCKED_WORKER_LANES),
        "human_wake_policy": {
            "wake_required": wake_required,
            "policy": str(policy["wake_policy"]),
            "wake_reasons": [
                "sos_active",
                "protected_action_attempt",
                "security_or_secret_boundary",
                "broker_or_live_trading_boundary",
            ],
        },
        "approval_required": {
            "human_owner_required": True,
            "human_owner_worker_launch_approval_present": approval_present,
            "required_before_worker_launch": True,
            "required_before_runtime_scheduler_or_daemon": True,
            "validator_pass_is_not_approval": True,
            "self_approval_allowed": False,
        },
        "missing_requirements": _dedupe(missing),
        "protected_actions": _protected_actions(),
        "recommended_validators": _recommended_validators(decision),
        "safety": _safety(safety_status),
        "no_write_proof": no_write_proof,
        "stop_conditions": _dedupe(stop_conditions),
        "next_safe_action": next_safe_action,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Build an AIOS full-autonomy worker launch preflight gate result from JSON evidence.")
    parser.add_argument("--payload-base64", default="")
    args = parser.parse_args()
    if args.payload_base64:
        payload_text = base64.b64decode(args.payload_base64.encode("ascii")).decode("utf-8")
    else:
        payload_text = sys.stdin.read()
    result = build_full_autonomy_worker_launch_preflight_gate_result(json.loads(payload_text))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["safety"]["status"] in {"PASS", "REVIEW_REQUIRED"} else 1


if __name__ == "__main__":
    raise SystemExit(_main())
