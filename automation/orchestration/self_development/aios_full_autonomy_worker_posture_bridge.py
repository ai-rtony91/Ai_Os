"""Pure AIOS full-autonomy worker posture bridge logic.

This module converts an activation-gate result into worker posture guidance.
It is advisory only: it does not reserve workers, launch workers, mutate
queues, mutate locks, mutate approvals, start runtime, or enable schedulers.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_FULL_AUTONOMY_WORKER_POSTURE_BRIDGE_RESULT.v1"
MODE = "DRY_RUN_READ_ONLY"

ACTIVATION_SCHEMA = "AIOS_FULL_AUTONOMY_ACTIVATION_GATE_RESULT.v1"

WORKER_POSTURES = (
    "NO_WORKERS",
    "READ_ONLY_VALIDATOR_CREW",
    "PACKET_PREVIEW_CREW",
    "SUPERVISED_DAY_CREW_12H",
    "SUPERVISED_DAY_NIGHT_CREW_24H",
    "WEEKEND_LOW_TOUCH_CREW",
    "VACATION_EMERGENCY_ONLY_CREW",
    "BLOCKED_BY_APPROVAL",
    "BLOCKED_BY_SOS",
    "BLOCKED_BY_VALIDATION",
)

BLOCKED_WORKER_LANES = [
    "runtime",
    "runtime_execution",
    "scheduler",
    "daemon",
    "trading",
    "live_trading",
    "broker",
    "oanda",
    "webhook",
    "real_orders",
    "secrets",
    "env_access",
    "queue",
    "queue_mutation",
    "lock",
    "lock_mutation",
    "approval",
    "approval_mutation",
    "registry",
    "registry_mutation",
    "reports_write",
    "telemetry_write",
    "relay_write",
    "dashboard_ui",
]

PROFILE_POLICIES = {
    "12H_SUPERVISED": {
        "worker_shift_mode": "12H_SUPERVISED",
        "recommended_worker_count": 1,
        "max_parallel_workers": 2,
        "allowed_worker_lanes": ["validator", "self_audit", "packet_preview", "readiness_review"],
        "human_wake_policy": "Wake for SOS, protected action, security, secrets, broker, live-trading, or repo-corruption boundary.",
        "next_safe_action": "Use advisory 12H supervised validator or packet-preview posture only; do not launch workers.",
    },
    "24H_SUPERVISED": {
        "worker_shift_mode": "24H_SUPERVISED",
        "recommended_worker_count": 1,
        "max_parallel_workers": 3,
        "allowed_worker_lanes": ["validator", "no_ready_stage_discovery", "packet_preview", "approval_sos_review"],
        "human_wake_policy": "Wake only for SOS, protected action, security, secrets, broker, live-trading, or repo-corruption boundary.",
        "next_safe_action": "Use advisory 24H monitoring posture only; do not launch workers.",
    },
    "WEEKEND": {
        "worker_shift_mode": "WEEKEND_LOW_TOUCH",
        "recommended_worker_count": 1,
        "max_parallel_workers": 1,
        "allowed_worker_lanes": ["validator", "status_review"],
        "human_wake_policy": "Low-touch weekend review; wake only for SOS or protected-action boundary.",
        "next_safe_action": "Use low-touch weekend status review only; do not recommend implementation.",
    },
    "VACATION": {
        "worker_shift_mode": "VACATION_EMERGENCY_ONLY",
        "recommended_worker_count": 0,
        "max_parallel_workers": 0,
        "allowed_worker_lanes": ["emergency_review"],
        "human_wake_policy": "Vacation mode: emergency-only review; wake only for SOS, security, secrets, broker, live-trading, or repo-corruption boundary.",
        "next_safe_action": "Do not recommend implementation; remain emergency-only.",
    },
    "OVERNIGHT": {
        "worker_shift_mode": "OVERNIGHT_READ_ONLY",
        "recommended_worker_count": 1,
        "max_parallel_workers": 1,
        "allowed_worker_lanes": ["validator", "status_review", "approval_sos_review"],
        "human_wake_policy": "Overnight read-only review; wake only for SOS, protected action, security, secrets, broker, live-trading, or repo-corruption boundary.",
        "next_safe_action": "Use overnight read-only monitoring only; do not launch workers.",
    },
    "EMERGENCY_REVIEW": {
        "worker_shift_mode": "EMERGENCY_REVIEW_ONLY",
        "recommended_worker_count": 0,
        "max_parallel_workers": 0,
        "allowed_worker_lanes": ["approval_sos_review"],
        "human_wake_policy": "Emergency review requires Human Owner attention.",
        "next_safe_action": "Wake the Human Owner and do not continue normal worker planning.",
    },
    "FULL_AUTONOMY_SUPERVISED": {
        "worker_shift_mode": "FULL_AUTONOMY_SUPERVISED_PREVIEW",
        "recommended_worker_count": 2,
        "max_parallel_workers": 3,
        "allowed_worker_lanes": ["validator", "packet_preview", "readiness_review", "approval_sos_review"],
        "human_wake_policy": "Supervised preview only; wake for SOS, protected action, security, secrets, broker, live-trading, or repo-corruption boundary.",
        "next_safe_action": "Classify as preview/validation posture unless separate explicit approval authorizes worker launch.",
    },
}

ACTIVATION_TO_POSTURE = {
    "READ_ONLY_MONITOR": "READ_ONLY_VALIDATOR_CREW",
    "VALIDATOR_ONLY_ALLOWED": "READ_ONLY_VALIDATOR_CREW",
    "PACKET_PREVIEW_ALLOWED": "PACKET_PREVIEW_CREW",
    "SUPERVISED_12H_ALLOWED": "SUPERVISED_DAY_CREW_12H",
    "SUPERVISED_24H_ALLOWED": "SUPERVISED_DAY_NIGHT_CREW_24H",
    "WEEKEND_MONITOR_ALLOWED": "WEEKEND_LOW_TOUCH_CREW",
    "VACATION_MONITOR_ALLOWED": "VACATION_EMERGENCY_ONLY_CREW",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _normalized(value: Any) -> str:
    return _safe_str(value).upper().replace("-", "_").replace(" ", "_") or "UNKNOWN"


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = _safe_str(value).lower()
    if not text:
        return default
    return text in {"true", "1", "yes", "y", "on"}


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        key = _safe_str(item)
        if key and key not in seen:
            result.append(key)
            seen.add(key)
    return result


def _repo_stop_conditions(repo_state: dict[str, Any]) -> list[str]:
    stops: list[str] = []
    if repo_state and not _bool(repo_state.get("branch_matches_expected"), default=True):
        stops.append("BRANCH_MISMATCH")
    if (
        _bool(repo_state.get("dirty"))
        and _bool(repo_state.get("fail_on_dirty_worktree"), default=True)
        and not _bool(repo_state.get("dirty_allowed_for_full_autonomy_worker_posture_bridge_validation"))
    ):
        stops.append("DIRTY_WORKTREE")
    return stops


def _no_write_stop_conditions(no_write_proof: dict[str, Any]) -> list[str]:
    if _bool(no_write_proof.get("changed")):
        return ["WRITE_SURFACE_RISK"]
    return []


def _activation_status(activation_gate_result: dict[str, Any]) -> str:
    decision = _as_dict(activation_gate_result.get("activation_decision"))
    return _normalized(decision.get("status") or "REVIEW_REQUIRED")


def _posture_from_activation(status: str, stop_conditions: list[str]) -> str:
    if "SOS_ACTIVE" in stop_conditions or status == "DENIED":
        return "BLOCKED_BY_SOS" if "SOS_ACTIVE" in stop_conditions else "BLOCKED_BY_VALIDATION"
    if status == "REVIEW_REQUIRED":
        return "BLOCKED_BY_VALIDATION"
    if status == "FULL_AUTONOMY_REQUESTED_NOT_APPROVED":
        return "BLOCKED_BY_APPROVAL"
    return ACTIVATION_TO_POSTURE.get(status, "NO_WORKERS")


def _bounded_policy(profile: str, posture: str) -> dict[str, Any]:
    policy = dict(PROFILE_POLICIES.get(profile, PROFILE_POLICIES["12H_SUPERVISED"]))
    if posture in {"NO_WORKERS", "BLOCKED_BY_APPROVAL", "BLOCKED_BY_SOS", "BLOCKED_BY_VALIDATION"}:
        policy["recommended_worker_count"] = 0
        policy["max_parallel_workers"] = 0
        policy["allowed_worker_lanes"] = [] if posture != "BLOCKED_BY_SOS" else ["approval_sos_review"]
    if posture == "READ_ONLY_VALIDATOR_CREW":
        policy["recommended_worker_count"] = min(int(policy["recommended_worker_count"]), 1)
    if posture == "PACKET_PREVIEW_CREW":
        policy["recommended_worker_count"] = min(max(int(policy["recommended_worker_count"]), 1), int(policy["max_parallel_workers"]))
    return policy


def _recommended_validators() -> list[dict[str, Any]]:
    return [
        {
            "validator_id": "full_autonomy_activation_gate",
            "path": "automation/orchestration/self_development/Test-AiOsFullAutonomyActivationGate.DRY_RUN.ps1",
            "purpose": "Refresh activation ceiling before worker posture guidance is trusted.",
        },
        {
            "validator_id": "identity_spine",
            "path": "automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1",
            "purpose": "Confirm worker identity and lane metadata before any future worker plan.",
        },
        {
            "validator_id": "orchestration_validator_chain",
            "path": "automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1",
            "purpose": "Refresh validator-chain evidence before posture escalation.",
        },
        {
            "validator_id": "approval_sos_hard_gate",
            "path": "automation/orchestration/operator_control/Test-AiOsApprovalSosHardGate.DRY_RUN.ps1",
            "purpose": "Confirm approval/SOS hard gate before any protected action.",
        },
    ]


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
        "worker_reservation_allowed": False,
        "enables_scheduler": False,
        "starts_daemon": False,
        "touches_secrets_or_env": False,
        "secrets_or_env_access": False,
        "broker_or_live_trading": False,
        "worker_launch_allowed": False,
        "advisory_only": True,
        "protected_actions_blocked": True,
        "human_owner_required_before_worker_launch": True,
        "human_owner_required_before_protected_action": True,
        "self_approval_allowed": False,
    }


def build_full_autonomy_worker_posture_bridge_result(payload: dict[str, Any]) -> dict[str, Any]:
    repo_state = _as_dict(payload.get("repo_state"))
    no_write_proof = _as_dict(payload.get("no_write_proof"))
    activation_gate_result = _as_dict(payload.get("activation_gate_result"))
    profile = _normalized(payload.get("operating_profile") or activation_gate_result.get("operating_profile") or "12H_SUPERVISED")
    if profile not in PROFILE_POLICIES:
        profile = "12H_SUPERVISED"

    activation_schema_ok = _safe_str(activation_gate_result.get("schema")) == ACTIVATION_SCHEMA
    activation_status = _activation_status(activation_gate_result)
    activation_stop_conditions = [_safe_str(item) for item in activation_gate_result.get("stop_conditions", []) if _safe_str(item)] if isinstance(activation_gate_result.get("stop_conditions"), list) else []
    stop_conditions = _dedupe(_repo_stop_conditions(repo_state) + _no_write_stop_conditions(no_write_proof) + ([] if activation_schema_ok else ["ACTIVATION_GATE_SCHEMA_INVALID"]) + activation_stop_conditions)
    posture = _posture_from_activation(activation_status, stop_conditions)
    policy = _bounded_policy(profile, posture)

    safety_status = "PASS"
    if "WRITE_SURFACE_RISK" in stop_conditions:
        safety_status = "BLOCKED_BY_WRITE_SURFACE_RISK"
    elif posture in {"BLOCKED_BY_APPROVAL", "BLOCKED_BY_SOS", "BLOCKED_BY_VALIDATION"}:
        safety_status = "REVIEW_REQUIRED" if posture == "BLOCKED_BY_APPROVAL" else "BLOCKED"
    elif "BRANCH_MISMATCH" in stop_conditions or "DIRTY_WORKTREE" in stop_conditions:
        safety_status = "BLOCKED"

    worker_launch_reason = "Advisory posture only; this bridge never launches workers, reserves workers, starts runtime, enables schedulers, or starts daemons."
    activation_summary = {
        "schema": _safe_str(activation_gate_result.get("schema")),
        "requested_autonomy_level": _safe_str(activation_gate_result.get("requested_autonomy_level")),
        "operating_profile": profile,
        "activation_status": activation_status,
        "activation_safety_status": _safe_str(_as_dict(activation_gate_result.get("safety")).get("status")),
        "human_owner_approval_evidence_present": _bool(
            _as_dict(activation_gate_result.get("input_evidence")).get("human_owner_approval_evidence_present")
        ),
        "worker_launch_allowed_by_activation_gate": _bool(
            _as_dict(activation_gate_result.get("activation_decision")).get("worker_launch_allowed")
        ),
    }

    next_safe_action = policy["next_safe_action"]
    if posture == "BLOCKED_BY_APPROVAL":
        next_safe_action = "No command recommended. Human Owner approval evidence is required before worker posture escalation."
    elif posture == "BLOCKED_BY_SOS":
        next_safe_action = "Wake the Human Owner and perform SOS review before any worker posture continuation."
    elif posture == "BLOCKED_BY_VALIDATION":
        next_safe_action = "Run the recommended validators and refresh activation-gate evidence before worker posture planning."

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_utc": _safe_str(payload.get("generated_utc") or _now()),
        "repo_state": repo_state,
        "activation_summary": activation_summary,
        "worker_posture": posture,
        "worker_shift_mode": policy["worker_shift_mode"],
        "recommended_worker_count": int(policy["recommended_worker_count"]),
        "max_parallel_workers": int(policy["max_parallel_workers"]),
        "allowed_worker_lanes": list(policy["allowed_worker_lanes"]),
        "blocked_worker_lanes": list(BLOCKED_WORKER_LANES),
        "worker_launch_allowed": False,
        "worker_launch_reason": worker_launch_reason,
        "human_wake_policy": policy["human_wake_policy"],
        "recommended_validators": _recommended_validators(),
        "safety": _safety(safety_status),
        "no_write_proof": no_write_proof,
        "stop_conditions": stop_conditions,
        "next_safe_action": next_safe_action,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Build an AIOS full-autonomy worker posture bridge result from JSON evidence.")
    parser.add_argument("--payload-base64", default="")
    args = parser.parse_args()
    if args.payload_base64:
        payload_text = base64.b64decode(args.payload_base64.encode("ascii")).decode("utf-8")
    else:
        payload_text = sys.stdin.read()
    result = build_full_autonomy_worker_posture_bridge_result(json.loads(payload_text))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["safety"]["status"] in {"PASS", "REVIEW_REQUIRED"} else 1


if __name__ == "__main__":
    raise SystemExit(_main())
