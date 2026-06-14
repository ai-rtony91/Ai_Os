"""Pure AIOS full-autonomy activation gate logic.

The PowerShell runner gathers read-only repo evidence. This module turns that
evidence into an activation decision, approval requirement, posture ceiling,
and next safe action. It writes no files, starts no processes, launches no
workers, and grants no protected-action authority.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_FULL_AUTONOMY_ACTIVATION_GATE_RESULT.v1"
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

ACTIVATION_STATUSES = (
    "DENIED",
    "REVIEW_REQUIRED",
    "READ_ONLY_MONITOR",
    "PACKET_PREVIEW_ALLOWED",
    "VALIDATOR_ONLY_ALLOWED",
    "SUPERVISED_12H_ALLOWED",
    "SUPERVISED_24H_ALLOWED",
    "WEEKEND_MONITOR_ALLOWED",
    "VACATION_MONITOR_ALLOWED",
    "FULL_AUTONOMY_REQUESTED_NOT_APPROVED",
)

PASS_STATUSES = {"PASS", "CLEAR", "OK", "GREEN"}
WARN_PASS_STATUSES = {"WARN_REVIEWED"}
SOS_ACTIVE_STATUSES = {"SOS_ACTIVE", "SOS", "SOS_HARD_STOP", "EMERGENCY", "CRITICAL"}

PROTECTED_ACTIONS = [
    ("apply", "APPLY/protected execution"),
    ("commit", "local commit"),
    ("push", "push"),
    ("pr", "PR creation"),
    ("merge", "merge"),
    ("runtime_start", "runtime start"),
    ("worker_launch", "worker launch"),
    ("worker_reservation", "worker reservation"),
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

PROFILE_SAFE_CEILING_WITHOUT_APPROVAL = {
    "12H_SUPERVISED": "PACKET_PREVIEW_ALLOWED",
    "24H_SUPERVISED": "READ_ONLY_MONITOR",
    "WEEKEND": "READ_ONLY_MONITOR",
    "VACATION": "VALIDATOR_ONLY_ALLOWED",
    "OVERNIGHT": "READ_ONLY_MONITOR",
    "EMERGENCY_REVIEW": "DENIED",
    "FULL_AUTONOMY_SUPERVISED": "PACKET_PREVIEW_ALLOWED",
}

PROFILE_APPROVED_CEILING = {
    "12H_SUPERVISED": "SUPERVISED_12H_ALLOWED",
    "24H_SUPERVISED": "SUPERVISED_24H_ALLOWED",
    "WEEKEND": "WEEKEND_MONITOR_ALLOWED",
    "VACATION": "VACATION_MONITOR_ALLOWED",
    "OVERNIGHT": "SUPERVISED_24H_ALLOWED",
    "EMERGENCY_REVIEW": "DENIED",
    "FULL_AUTONOMY_SUPERVISED": "PACKET_PREVIEW_ALLOWED",
}

NEXT_ACTION_BY_VALIDATOR = {
    "identity_spine": "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1",
    "validator_chain": "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1",
    "approval_sos": "Wake the Human Owner and perform SOS review before any continuation.",
    "governed_soak": "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/self_development/Test-AiOsGovernedSelfDevelopmentSoak.DRY_RUN.ps1 -OutputJson",
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
    return text in {"true", "1", "yes", "y", "on", "present", "approved"}


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
        and not _bool(repo_state.get("dirty_allowed_for_full_autonomy_activation_gate_validation"))
    ):
        stops.append("DIRTY_WORKTREE")
    return stops


def _no_write_stop_conditions(no_write_proof: dict[str, Any]) -> list[str]:
    if _bool(no_write_proof.get("changed")):
        return ["WRITE_SURFACE_RISK"]
    return []


def _protected_actions() -> list[dict[str, Any]]:
    return [
        {
            "action_id": action_id,
            "label": label,
            "status": "BLOCKED",
            "human_owner_required": True,
            "reason": "Activation gate output is evidence only and does not authorize protected execution.",
        }
        for action_id, label in PROTECTED_ACTIONS
    ]


def _recommended_validators(missing_requirements: list[str]) -> list[dict[str, Any]]:
    validators = [
        {
            "validator_id": "identity_spine",
            "path": "automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1",
            "required_when": "identity_spine_status is not PASS",
        },
        {
            "validator_id": "orchestration_validator_chain",
            "path": "automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1",
            "required_when": "validator_chain_status is not PASS or WARN_REVIEWED",
        },
        {
            "validator_id": "approval_sos_hard_gate",
            "path": "automation/orchestration/operator_control/Test-AiOsApprovalSosHardGate.DRY_RUN.ps1",
            "required_when": "approval_sos_status is SOS_ACTIVE or review is unclear",
        },
        {
            "validator_id": "governed_self_development_soak",
            "path": "automation/orchestration/self_development/Test-AiOsGovernedSelfDevelopmentSoak.DRY_RUN.ps1",
            "required_when": "governed_soak_status is not PASS",
        },
    ]
    if not missing_requirements:
        return validators
    required = set(missing_requirements)
    return [
        item
        for item in validators
        if item["validator_id"] in required
        or (item["validator_id"] == "orchestration_validator_chain" and "validator_chain" in required)
    ] or validators


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
        "protected_actions_blocked": True,
        "human_owner_required_before_protected_action": True,
        "self_approval_allowed": False,
        "true_full_autonomy_approved": False,
    }


def _allowed_postures_for(status: str) -> list[str]:
    if status in {"DENIED", "REVIEW_REQUIRED", "FULL_AUTONOMY_REQUESTED_NOT_APPROVED"}:
        return []
    order = [
        "READ_ONLY_MONITOR",
        "VALIDATOR_ONLY_ALLOWED",
        "PACKET_PREVIEW_ALLOWED",
        "SUPERVISED_12H_ALLOWED",
        "SUPERVISED_24H_ALLOWED",
        "WEEKEND_MONITOR_ALLOWED",
        "VACATION_MONITOR_ALLOWED",
    ]
    if status not in order:
        return []
    index = order.index(status)
    return order[: index + 1]


def _blocked_postures_for(status: str) -> list[str]:
    allowed = set(_allowed_postures_for(status))
    always_blocked = {"DENIED", "REVIEW_REQUIRED", "FULL_AUTONOMY_REQUESTED_NOT_APPROVED"}
    if status in always_blocked:
        allowed.add(status)
    return [item for item in ACTIVATION_STATUSES if item not in allowed]


def _decision_from_evidence(
    requested_level: str,
    operating_profile: str,
    approval_present: bool,
    identity_status: str,
    validator_status: str,
    approval_sos_status: str,
    soak_status: str,
    repo_stop_conditions: list[str],
) -> tuple[str, str, list[str], str]:
    if "WRITE_SURFACE_RISK" in repo_stop_conditions:
        return "DENIED", "No-write proof detected a forbidden surface delta.", ["no_write_proof"], "No command recommended."
    if "BRANCH_MISMATCH" in repo_stop_conditions or "DIRTY_WORKTREE" in repo_stop_conditions:
        return "DENIED", "Repo state does not match activation-gate requirements.", ["repo_state"], "No command recommended."
    if _normalized(approval_sos_status) in SOS_ACTIVE_STATUSES:
        return "DENIED", "Approval/SOS hard gate reports SOS active.", ["approval_sos"], NEXT_ACTION_BY_VALIDATOR["approval_sos"]
    if not _status_is_pass(identity_status):
        return "REVIEW_REQUIRED", "Identity spine evidence is not PASS.", ["identity_spine"], NEXT_ACTION_BY_VALIDATOR["identity_spine"]
    if not _status_is_pass(validator_status, allow_warn_reviewed=True):
        return "REVIEW_REQUIRED", "Validator-chain evidence is not PASS or WARN_REVIEWED.", ["validator_chain"], NEXT_ACTION_BY_VALIDATOR["validator_chain"]
    if not _status_is_pass(soak_status):
        return "REVIEW_REQUIRED", "Governed soak evidence is not PASS.", ["governed_self_development_soak"], NEXT_ACTION_BY_VALIDATOR["governed_soak"]
    if requested_level == "LEVEL_5_FULL_AUTONOMY_REQUESTED" and not approval_present:
        return (
            "FULL_AUTONOMY_REQUESTED_NOT_APPROVED",
            "LEVEL_5 was requested without explicit Human Owner approval evidence.",
            ["human_owner_approval_evidence"],
            "No command recommended. Human Owner approval evidence is required before true full-autonomy review can continue.",
        )
    if operating_profile == "EMERGENCY_REVIEW":
        return "DENIED", "Emergency profile blocks normal autonomy activation.", ["emergency_review"], NEXT_ACTION_BY_VALIDATOR["approval_sos"]
    if approval_present:
        status = PROFILE_APPROVED_CEILING[operating_profile]
        return (
            status,
            "Fresh evidence passed and Human Owner approval evidence was supplied; protected actions still require separate approval.",
            [],
            "Continue advisory posture review only; do not launch workers or perform protected actions from this result.",
        )
    status = PROFILE_SAFE_CEILING_WITHOUT_APPROVAL[operating_profile]
    return (
        status,
        "Fresh evidence passed, but explicit Human Owner approval evidence was not supplied; protected execution remains blocked.",
        ["human_owner_approval_evidence_for_higher_posture"],
        "Continue read-only, validator, or packet-preview posture only; obtain explicit Human Owner approval before protected execution.",
    )


def build_full_autonomy_activation_gate_result(payload: dict[str, Any]) -> dict[str, Any]:
    requested_level = _normalized(payload.get("requested_autonomy_level") or "LEVEL_4_CONDITIONAL_FULL_AUTONOMY")
    if requested_level not in REQUESTED_AUTONOMY_LEVELS:
        requested_level = "LEVEL_4_CONDITIONAL_FULL_AUTONOMY"
    operating_profile = _normalized(payload.get("operating_profile") or "12H_SUPERVISED")
    if operating_profile not in OPERATING_PROFILES:
        operating_profile = "12H_SUPERVISED"

    repo_state = _as_dict(payload.get("repo_state"))
    no_write_proof = _as_dict(payload.get("no_write_proof"))
    human_owner_approval_evidence = _safe_str(payload.get("human_owner_approval_evidence"))
    approval_present = _approval_present(human_owner_approval_evidence)
    identity_status = _normalized(payload.get("identity_spine_status") or "PASS")
    validator_status = _normalized(payload.get("validator_chain_status") or "PASS")
    approval_sos_status = _normalized(payload.get("approval_sos_status") or "CLEAR")
    soak_status = _normalized(payload.get("governed_soak_status") or "PASS")

    stop_conditions = _dedupe(_repo_stop_conditions(repo_state) + _no_write_stop_conditions(no_write_proof))
    status, reason, missing_requirements, next_safe_action = _decision_from_evidence(
        requested_level,
        operating_profile,
        approval_present,
        identity_status,
        validator_status,
        approval_sos_status,
        soak_status,
        stop_conditions,
    )
    if status == "DENIED" and _normalized(approval_sos_status) in SOS_ACTIVE_STATUSES:
        stop_conditions = _dedupe(stop_conditions + ["SOS_ACTIVE"])
    if status == "REVIEW_REQUIRED":
        safety_status = "REVIEW_REQUIRED"
    elif status == "DENIED":
        safety_status = "BLOCKED_BY_WRITE_SURFACE_RISK" if "WRITE_SURFACE_RISK" in stop_conditions else "BLOCKED"
    elif status == "FULL_AUTONOMY_REQUESTED_NOT_APPROVED":
        safety_status = "REVIEW_REQUIRED"
    else:
        safety_status = "PASS"

    allowed_postures = _allowed_postures_for(status)
    blocked_postures = _blocked_postures_for(status)
    protected_actions = _protected_actions()
    worker_recommendation_allowed = bool(allowed_postures) and status != "DENIED"
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_utc": _safe_str(payload.get("generated_utc") or _now()),
        "repo_state": repo_state,
        "requested_autonomy_level": requested_level,
        "operating_profile": operating_profile,
        "input_evidence": {
            "human_owner_approval_evidence_present": approval_present,
            "human_owner_approval_evidence_label": "SUPPLIED" if approval_present else "MISSING",
            "identity_spine_status": identity_status,
            "validator_chain_status": validator_status,
            "approval_sos_status": approval_sos_status,
            "governed_soak_status": soak_status,
            "warn_reviewed_counts_as_validator_chain_evidence": True,
        },
        "activation_decision": {
            "status": status,
            "reason": reason,
            "true_full_autonomy_approved": False,
            "protected_execution_allowed": False,
            "worker_recommendation_allowed": worker_recommendation_allowed,
            "worker_reservation_allowed": False,
            "worker_launch_allowed": False,
        },
        "activation_ceiling": {
            "posture": status,
            "allowed_postures": allowed_postures,
            "true_full_autonomy_allowed": False,
            "protected_execution_allowed": False,
            "worker_launch_allowed": False,
        },
        "missing_requirements": _dedupe(missing_requirements),
        "allowed_postures": allowed_postures,
        "blocked_postures": blocked_postures,
        "approval_required": {
            "human_owner_required": True,
            "explicit_human_owner_approval_evidence_present": approval_present,
            "required_for_true_full_autonomy": True,
            "required_before_protected_actions": True,
            "required_before_worker_launch": True,
            "required_before_scheduler_daemon_or_runtime": True,
            "validator_pass_is_not_approval": True,
            "self_approval_allowed": False,
        },
        "protected_actions": protected_actions,
        "recommended_validators": _recommended_validators(_dedupe(missing_requirements)),
        "safety": _safety(safety_status),
        "no_write_proof": no_write_proof,
        "stop_conditions": stop_conditions,
        "next_safe_action": next_safe_action,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Build an AIOS full-autonomy activation gate result from JSON evidence.")
    parser.add_argument("--payload-base64", default="")
    args = parser.parse_args()
    if args.payload_base64:
        payload_text = base64.b64decode(args.payload_base64.encode("ascii")).decode("utf-8")
    else:
        payload_text = sys.stdin.read()
    result = build_full_autonomy_activation_gate_result(json.loads(payload_text))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["safety"]["status"] in {"PASS", "REVIEW_REQUIRED"} else 1


if __name__ == "__main__":
    raise SystemExit(_main())
