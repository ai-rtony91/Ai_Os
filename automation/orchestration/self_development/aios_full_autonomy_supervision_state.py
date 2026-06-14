"""Pure AIOS full-autonomy supervision state resolver.

The PowerShell runner gathers read-only repo and no-write evidence. This
module classifies autonomy posture, worker supervision, prerequisite coverage,
approval/SOS gates, and safety boundaries. It writes no files, starts no
processes, launches no workers, and emits no executable command text.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_FULL_AUTONOMY_SUPERVISION_STATE_RESULT.v1"
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

LEVEL_DETAILS = {
    "LEVEL_0_MANUAL": {
        "resolved": "LEVEL_0_MANUAL",
        "state_status": "MANUAL_ONLY",
        "worker_status": "MANUAL_ONLY",
        "summary": "Human drives all work; AIOS reports status and next safe actions only.",
        "max_workers": 0,
        "continuation_allowed": False,
    },
    "LEVEL_1_ASSISTED": {
        "resolved": "LEVEL_1_ASSISTED",
        "state_status": "ASSISTED_RECOMMENDATION_ONLY",
        "worker_status": "RECOMMENDATION_ONLY",
        "summary": "AIOS can recommend commands and validators only.",
        "max_workers": 0,
        "continuation_allowed": False,
    },
    "LEVEL_2_SEMI_AUTONOMOUS": {
        "resolved": "LEVEL_2_SEMI_AUTONOMOUS",
        "state_status": "SEMI_AUTONOMOUS_PLANNING_ONLY",
        "worker_status": "PACKET_AND_VALIDATOR_PLANNING_ONLY",
        "summary": "AIOS can prepare packets, previews, validators, and structured next actions.",
        "max_workers": 1,
        "continuation_allowed": False,
    },
    "LEVEL_3_SUPERVISED_AUTONOMY": {
        "resolved": "LEVEL_3_SUPERVISED_AUTONOMY",
        "state_status": "SUPERVISED_AUTONOMY_READ_ONLY",
        "worker_status": "SUPERVISED_CONTINUATION_READ_ONLY",
        "summary": "AIOS can recommend multi-step plans and worker assignments, but cannot self-approve.",
        "max_workers": 2,
        "continuation_allowed": True,
    },
    "LEVEL_4_CONDITIONAL_FULL_AUTONOMY": {
        "resolved": "LEVEL_4_CONDITIONAL_FULL_AUTONOMY",
        "state_status": "CONDITIONAL_FULL_AUTONOMY_READ_ONLY",
        "worker_status": "CONDITIONAL_FULL_AUTONOMY_READ_ONLY",
        "summary": "AIOS can prepare for full autonomy inside read-only, preview, and validator lanes only.",
        "max_workers": 2,
        "continuation_allowed": True,
    },
    "LEVEL_5_FULL_AUTONOMY_REQUESTED": {
        "resolved": "FULL_AUTONOMY_REQUESTED_BUT_NOT_APPROVED",
        "state_status": "FULL_AUTONOMY_REQUESTED_BUT_NOT_APPROVED",
        "worker_status": "FULL_AUTONOMY_REQUESTED_NOT_APPROVED",
        "summary": "Full autonomy was requested, but explicit Human Owner approval evidence was not supplied.",
        "max_workers": 0,
        "continuation_allowed": False,
    },
}

PROFILE_DETAILS = {
    "12H_SUPERVISED": {
        "worker_shift_mode": "BOUNDED_12H_SUPERVISED",
        "recommended_worker_count": 1,
        "max_parallel_workers": 2,
        "implementation_recommendation_allowed": True,
        "wake_class": "PROTECTED_ACTION_OR_SOS",
        "next_action": "Continue bounded supervised planning and validator review; get Human Owner approval before protected actions.",
    },
    "24H_SUPERVISED": {
        "worker_shift_mode": "READ_ONLY_24H_MONITORING",
        "recommended_worker_count": 1,
        "max_parallel_workers": 1,
        "implementation_recommendation_allowed": False,
        "wake_class": "CRITICAL_ONLY",
        "next_action": "Run read-only overnight monitoring and validator recommendations only.",
    },
    "WEEKEND": {
        "worker_shift_mode": "LOW_INTERVENTION_WEEKEND_REVIEW",
        "recommended_worker_count": 1,
        "max_parallel_workers": 1,
        "implementation_recommendation_allowed": False,
        "wake_class": "LOW_INTERVENTION_REVIEW",
        "next_action": "Use review-only discovery; do not recommend implementation unless the Human Owner explicitly requests it.",
    },
    "VACATION": {
        "worker_shift_mode": "MINIMUM_DISTURBANCE_VACATION",
        "recommended_worker_count": 0,
        "max_parallel_workers": 0,
        "implementation_recommendation_allowed": False,
        "wake_class": "CRITICAL_ONLY",
        "next_action": "Idle, monitor, or perform read-only review only; do not recommend new implementation.",
    },
    "OVERNIGHT": {
        "worker_shift_mode": "READ_ONLY_OVERNIGHT",
        "recommended_worker_count": 1,
        "max_parallel_workers": 1,
        "implementation_recommendation_allowed": False,
        "wake_class": "CRITICAL_ONLY",
        "next_action": "Recommend read-only health checks and validators only.",
    },
    "EMERGENCY_REVIEW": {
        "worker_shift_mode": "EMERGENCY_HARD_STOP_REVIEW",
        "recommended_worker_count": 0,
        "max_parallel_workers": 0,
        "implementation_recommendation_allowed": False,
        "wake_class": "SOS",
        "next_action": "Stop normal work and wake the Human Owner for emergency review.",
    },
    "FULL_AUTONOMY_SUPERVISED": {
        "worker_shift_mode": "FULL_AUTONOMY_SUPERVISED_PREVIEW",
        "recommended_worker_count": 2,
        "max_parallel_workers": 2,
        "implementation_recommendation_allowed": False,
        "wake_class": "PROTECTED_ACTION_OR_SOS",
        "next_action": "Review full-autonomy prerequisites and select only read-only packet-preview or validator lanes.",
    },
}

SAFE_WORKER_LANES = [
    "self_audit",
    "validator",
    "packet_preview",
    "readiness_review",
    "no_ready_stage_discovery",
    "semi_autonomy_planning",
    "full_autonomy_prerequisite_review",
    "approval_sos_review",
]

BLOCKED_WORKER_LANES = [
    "runtime_execution",
    "scheduler",
    "daemon",
    "live_trading",
    "broker",
    "secrets",
    "approval_mutation",
    "queue_mutation",
    "lock_mutation",
    "registry_mutation",
    "reports_write",
    "telemetry_write",
    "relay_write",
    "dashboard_ui",
]

PROTECTED_ACTIONS = [
    ("apply", "APPLY without exact Human Owner approval"),
    ("commit", "commit without exact Human Owner approval"),
    ("push", "push without exact Human Owner approval"),
    ("pr", "PR creation without exact Human Owner approval"),
    ("merge", "merge without exact Human Owner approval"),
    ("runtime_start", "runtime start"),
    ("worker_launch", "worker launch"),
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

AUTHORITY_FILE_KEYS = {
    "AGENTS.md": "AGENTS.md",
    "README.md": "README.md",
    "RISK_POLICY.md": "RISK_POLICY.md",
    "docs/AI_OS/autonomy/AIOS_SELF_AUDIT_LOOP_CONTRACT_V1.md": "docs/AI_OS/autonomy/AIOS_SELF_AUDIT_LOOP_CONTRACT_V1.md",
    "docs/governance/aios-identity-and-lane-governance.md": "docs/governance/aios-identity-and-lane-governance.md",
    "docs/governance/AI_OS_REPO_MEMORY.md": "docs/governance/AI_OS_REPO_MEMORY.md",
}

PREREQUISITE_FILE_KEYS = {
    "approval_sos_hard_gate_present": "automation/orchestration/operator_control/Test-AiOsApprovalSosHardGate.DRY_RUN.ps1",
    "governed_soak_present": "automation/orchestration/self_development/Test-AiOsGovernedSelfDevelopmentSoak.DRY_RUN.ps1",
    "no_ready_stage_discovery_available": "automation/orchestration/campaign_registry/Get-AiOsCampaignNoReadyStageDiscovery.DRY_RUN.ps1",
    "worker_identity_registry_present": "schemas/aios/orchestration/WORKER_REGISTRY_SCHEMA.json",
    "worker_lane_policy_present": "docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md",
    "lock_conflict_policy_present": "automation/orchestration/locks/PATH_CONFLICT_POLICY_001.md",
    "protected_action_gate_present": "automation/orchestration/operator_control/Test-AiOsApprovalSosHardGate.DRY_RUN.ps1",
}

PASS_STATUSES = {"PASS", "CLEAR", "OK", "GREEN"}
REVIEW_STATUSES = {"WARN", "WARNING", "REVIEW", "REVIEW_REQUIRED", "UNKNOWN", "APPROVAL_GATE_WARN", "COMMIT_PACKAGE_WARN"}
BLOCKED_STATUSES = {"FAIL", "FAILED", "BLOCKED", "ERROR", "SOS", "SOS_HARD_STOP", "CRITICAL"}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _normalized(value: Any) -> str:
    text = _safe_str(value).upper().replace("-", "_").replace(" ", "_")
    return text or "UNKNOWN"


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
    return text in {"true", "1", "yes", "y", "on"}


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


def _status_class(value: Any) -> str:
    normalized = _normalized(value)
    if normalized in PASS_STATUSES:
        return "PASS"
    if normalized in BLOCKED_STATUSES:
        return "BLOCKED"
    return "REVIEW_REQUIRED"


def _file_present(file_presence: dict[str, Any], relative_path: str, default: bool = True) -> bool:
    if relative_path not in file_presence:
        return default
    value = file_presence[relative_path]
    if isinstance(value, dict):
        return _bool(value.get("exists"), default=default)
    return _bool(value, default=default)


def _authority_files_present(authority_context: dict[str, Any], file_presence: dict[str, Any]) -> bool:
    if "all_required_loaded" in authority_context:
        return _bool(authority_context.get("all_required_loaded"))
    return all(_file_present(file_presence, path, default=True) for path in AUTHORITY_FILE_KEYS.values())


def _prereq(satisfied: bool, status: str, reason: str, required_for_true_full_autonomy: bool = True) -> dict[str, Any]:
    return {
        "satisfied": bool(satisfied),
        "status": status,
        "reason": reason,
        "required_for_true_full_autonomy": required_for_true_full_autonomy,
    }


def _repo_stop_conditions(repo_state: dict[str, Any]) -> list[str]:
    stops: list[str] = []
    if repo_state and not _bool(repo_state.get("branch_matches_expected"), default=True):
        stops.append("BRANCH_MISMATCH")
    if (
        _bool(repo_state.get("dirty"))
        and _bool(repo_state.get("fail_on_dirty_worktree"), default=True)
        and not _bool(repo_state.get("dirty_allowed_for_full_autonomy_supervision_state_validation"))
    ):
        stops.append("DIRTY_WORKTREE")
    return stops


def _no_write_stop_conditions(no_write_proof: dict[str, Any]) -> list[str]:
    if _bool(no_write_proof.get("changed")):
        return ["WRITE_SURFACE_RISK"]
    return []


def _build_sos_gate(profile: str, recent_sos_status: str) -> dict[str, Any]:
    normalized = _normalized(recent_sos_status)
    status_class = _status_class(normalized)
    profile_emergency = profile == "EMERGENCY_REVIEW"
    hard_stop_active = profile_emergency or status_class == "BLOCKED"
    return {
        "status": "SOS_HARD_STOP" if hard_stop_active else ("CLEAR" if status_class == "PASS" else "REVIEW_REQUIRED"),
        "recent_sos_status": normalized,
        "sos_hard_stop_active": hard_stop_active,
        "wake_required": hard_stop_active,
        "reason": (
            "Emergency review or SOS status blocks normal work."
            if hard_stop_active
            else "No SOS hard stop is active."
        ),
    }


def _build_human_wake_policy(
    profile: str,
    human_available: bool,
    weekend_mode: bool,
    vacation_mode: bool,
    sleep_window_active: bool,
    sos_gate: dict[str, Any],
) -> dict[str, Any]:
    profile_detail = PROFILE_DETAILS[profile]
    wake_reasons = [
        "sos_hard_stop",
        "security_or_secret_boundary",
        "broker_or_live_trading_boundary",
        "critical_repo_corruption",
    ]
    if profile in {"12H_SUPERVISED", "WEEKEND", "FULL_AUTONOMY_SUPERVISED"}:
        wake_reasons.append("protected_action_attempt")
    wake_required = _bool(sos_gate.get("wake_required")) or profile == "EMERGENCY_REVIEW"
    if sleep_window_active and not wake_required:
        wake_class = "SLEEP_WINDOW_CRITICAL_ONLY"
    elif vacation_mode or profile == "VACATION":
        wake_class = "VACATION_CRITICAL_ONLY"
    elif weekend_mode or profile == "WEEKEND":
        wake_class = "WEEKEND_LOW_INTERVENTION"
    else:
        wake_class = profile_detail["wake_class"]
    return {
        "profile": profile,
        "human_available": bool(human_available),
        "weekend_mode": bool(weekend_mode),
        "vacation_mode": bool(vacation_mode),
        "sleep_window_active": bool(sleep_window_active),
        "wake_required": bool(wake_required),
        "wake_class": wake_class,
        "wake_reasons": wake_reasons if wake_required or profile in {"24H_SUPERVISED", "VACATION", "OVERNIGHT", "EMERGENCY_REVIEW"} else ["protected_action_attempt", "sos_hard_stop"],
        "do_not_wake_for": [
            "routine_review",
            "validator_warn_without_blocker",
            "recommendation_only_defer",
            "dashboard_or_production_readiness_candidate",
        ],
    }


def _allowed_lanes_for_level(resolved_level: str, profile: str) -> list[str]:
    if profile == "EMERGENCY_REVIEW":
        return ["approval_sos_review"]
    if profile == "VACATION":
        return ["self_audit", "readiness_review"]
    if resolved_level == "LEVEL_0_MANUAL":
        return []
    if resolved_level == "LEVEL_1_ASSISTED":
        return ["readiness_review", "validator"]
    if resolved_level == "LEVEL_2_SEMI_AUTONOMOUS":
        return ["validator", "packet_preview", "readiness_review", "semi_autonomy_planning"]
    if resolved_level in {"LEVEL_3_SUPERVISED_AUTONOMY", "LEVEL_4_CONDITIONAL_FULL_AUTONOMY"}:
        return list(SAFE_WORKER_LANES)
    return ["full_autonomy_prerequisite_review", "approval_sos_review"]


def _build_worker_supervision(
    requested_level: str,
    resolved_level: str,
    profile: str,
    max_autonomy_hours: int,
    human_wake_policy: dict[str, Any],
) -> dict[str, Any]:
    level_detail = LEVEL_DETAILS[requested_level]
    profile_detail = PROFILE_DETAILS[profile]
    profile_worker_cap = int(profile_detail["max_parallel_workers"])
    level_worker_cap = int(level_detail["max_workers"])
    hour_cap = 0 if max_autonomy_hours <= 0 else profile_worker_cap
    max_parallel_workers = max(0, min(profile_worker_cap, level_worker_cap, hour_cap))
    recommended_worker_count = max(0, min(int(profile_detail["recommended_worker_count"]), max_parallel_workers))
    continuation_allowed = (
        bool(level_detail["continuation_allowed"])
        and profile not in {"VACATION", "EMERGENCY_REVIEW"}
        and max_autonomy_hours > 0
    )
    return {
        "worker_supervision_status": level_detail["worker_status"],
        "worker_shift_mode": profile_detail["worker_shift_mode"],
        "recommended_worker_count": recommended_worker_count,
        "max_parallel_workers": max_parallel_workers,
        "allowed_worker_lanes": _allowed_lanes_for_level(resolved_level, profile),
        "blocked_worker_lanes": list(BLOCKED_WORKER_LANES),
        "worker_launch_allowed": False,
        "worker_launch_reason": "This runner is DRY_RUN_READ_ONLY and never launches runtime, workers, scheduler, or daemon.",
        "supervisor_review_required": True,
        "human_wake_policy": human_wake_policy,
        "autonomous_continuation_allowed": bool(continuation_allowed),
        "autonomous_continuation_limits": {
            "max_autonomy_hours": max(0, max_autonomy_hours),
            "read_only_or_preview_only": True,
            "protected_actions_require_human_owner": True,
            "runtime_worker_scheduler_daemon_launch_blocked": True,
            "queue_lock_approval_registry_mutation_blocked": True,
        },
    }


def _build_prerequisites(payload: dict[str, Any], repo_state: dict[str, Any]) -> dict[str, Any]:
    authority_context = _as_dict(payload.get("authority_context"))
    file_presence = _as_dict(payload.get("file_presence"))
    recent_validator_status = _normalized(payload.get("recent_validator_status") or "UNKNOWN")
    validator_class = _status_class(recent_validator_status)
    repo_clean = not _bool(repo_state.get("dirty"))
    branch_confirmed = _bool(repo_state.get("branch_matches_expected"), default=True)
    authority_present = _authority_files_present(authority_context, file_presence)

    prerequisites: dict[str, Any] = {
        "repo_clean": _prereq(repo_clean, "PASS" if repo_clean else "REVIEW_REQUIRED", "Working tree must be clean for true future full autonomy."),
        "main_or_expected_branch_confirmed": _prereq(
            branch_confirmed,
            "PASS" if branch_confirmed else "BLOCKED",
            "Current branch must match the expected branch before autonomy escalation.",
        ),
        "authority_files_present": _prereq(
            authority_present,
            "PASS" if authority_present else "BLOCKED",
            "Required AI_OS authority files must be present and readable.",
        ),
        "identity_spine_passed_or_required": _prereq(
            True,
            "PASS" if validator_class == "PASS" else "REQUIRED",
            "Identity-spine validation must pass before true full autonomy; this resolver records the requirement.",
        ),
        "validator_chain_passed_or_required": _prereq(
            True,
            "PASS" if validator_class == "PASS" else "REQUIRED",
            "Validator-chain evidence must pass before true full autonomy; WARN remains review-required, not fail.",
        ),
        "human_wake_policy_defined": _prereq(True, "PASS", "Human wake policy is defined by operating profile."),
        "vacation_mode_defined": _prereq(True, "PASS", "Vacation profile is defined."),
        "weekend_mode_defined": _prereq(True, "PASS", "Weekend profile is defined."),
        "12h_mode_defined": _prereq(True, "PASS", "12H supervised profile is defined."),
        "24h_mode_defined": _prereq(True, "PASS", "24H supervised profile is defined."),
        "full_autonomy_denial_reason_when_not_approved": _prereq(
            True,
            "PRESENT",
            "Full autonomy remains denied unless explicit Human Owner approval evidence is supplied.",
        ),
        "broker_live_trading_blocked": _prereq(True, "PASS", "Broker/live trading remains blocked by policy."),
        "secrets_env_blocked": _prereq(True, "PASS", "Secrets and .env access remain blocked by policy."),
    }

    for field, path in PREREQUISITE_FILE_KEYS.items():
        present = _file_present(file_presence, path, default=True)
        prerequisites[field] = _prereq(
            present,
            "PASS" if present else "REVIEW_REQUIRED",
            f"Required supporting surface: {path}",
        )
    return prerequisites


def _missing_true_full_autonomy_prerequisites(prerequisites: dict[str, Any], recent_validator_status: str) -> list[str]:
    missing: list[str] = ["explicit_human_owner_full_autonomy_approval"]
    for name, detail in prerequisites.items():
        if isinstance(detail, dict) and detail.get("required_for_true_full_autonomy") and not _bool(detail.get("satisfied")):
            missing.append(name)
    if _status_class(recent_validator_status) != "PASS":
        missing.append("identity_spine_validator_pass")
        missing.append("validator_chain_pass")
    return _dedupe(missing)


def _build_full_autonomy_state(
    requested_level: str,
    resolved_level: str,
    prerequisites: dict[str, Any],
    recent_validator_status: str,
) -> dict[str, Any]:
    requested_full_autonomy = requested_level == "LEVEL_5_FULL_AUTONOMY_REQUESTED"
    missing = _missing_true_full_autonomy_prerequisites(prerequisites, recent_validator_status)
    denial_reason = "Explicit Human Owner full-autonomy approval evidence was not supplied."
    return {
        "status": LEVEL_DETAILS[requested_level]["state_status"],
        "requested_full_autonomy": requested_full_autonomy,
        "true_full_autonomy_approved": False,
        "resolved_autonomy_level": resolved_level,
        "effective_autonomy_ceiling": "LEVEL_4_CONDITIONAL_FULL_AUTONOMY",
        "explicit_human_owner_approval_evidence_present": False,
        "denial_reason": denial_reason,
        "missing_prerequisites_for_true_full_autonomy": missing,
        "protected_actions_remain_blocked": True,
        "self_approval_allowed": False,
    }


def _protected_actions() -> list[dict[str, Any]]:
    return [
        {
            "action_id": action_id,
            "label": label,
            "status": "BLOCKED_WITHOUT_EXPLICIT_HUMAN_OWNER_APPROVAL",
            "human_owner_required": True,
            "reason": "Validator output, recommendation output, or autonomy state is evidence only.",
        }
        for action_id, label in PROTECTED_ACTIONS
    ]


def _approval_gate(requested_level: str, recent_validator_status: str) -> dict[str, Any]:
    validator_class = _status_class(recent_validator_status)
    review_conditions: list[str] = []
    if requested_level == "LEVEL_5_FULL_AUTONOMY_REQUESTED":
        review_conditions.append("FULL_AUTONOMY_APPROVAL_MISSING")
    if validator_class == "REVIEW_REQUIRED":
        review_conditions.append(f"VALIDATOR_STATUS_{_normalized(recent_validator_status)}")
    if _normalized(recent_validator_status) == "APPROVAL_GATE_WARN":
        review_conditions.append("APPROVAL_GATE_WARN_REVIEW_REQUIRED")
    if _normalized(recent_validator_status) == "COMMIT_PACKAGE_WARN":
        review_conditions.append("COMMIT_PACKAGE_WARN_REVIEW_REQUIRED")
    return {
        "status": "REVIEW_REQUIRED" if review_conditions else "CLEAR",
        "explicit_human_owner_approval_present": False,
        "self_approval_allowed": False,
        "human_owner_required": True,
        "before_apply": True,
        "before_commit": True,
        "before_push": True,
        "before_pr": True,
        "before_merge": True,
        "before_runtime": True,
        "before_worker_launch": True,
        "before_queue_lock_or_approval_registry_mutation": True,
        "validator_pass_is_not_approval": True,
        "review_conditions": _dedupe(review_conditions),
    }


def _recommended_validators() -> list[dict[str, Any]]:
    return [
        {
            "validator_id": "git_diff_check",
            "path": "git diff --check",
            "purpose": "Whitespace and patch integrity check before commit.",
        },
        {
            "validator_id": "full_autonomy_state_tests",
            "path": "tests/orchestration/test_aios_full_autonomy_supervision_state.py",
            "purpose": "Validate autonomy levels, profiles, worker policy, prerequisites, and safety flags.",
        },
        {
            "validator_id": "full_autonomy_state_runner_tests",
            "path": "tests/orchestration/test_aios_full_autonomy_supervision_state_runner.py",
            "purpose": "Validate the DRY_RUN_READ_ONLY runner, JSON mode, console mode, and no-write proof.",
        },
        {
            "validator_id": "approval_sos_hard_gate",
            "path": "tests/orchestration/test_aios_approval_sos_hard_gate.py",
            "purpose": "Confirm protected actions and SOS boundaries remain blocked.",
        },
        {
            "validator_id": "governed_self_development_soak",
            "path": "tests/orchestration/test_aios_governed_self_development_soak.py",
            "purpose": "Confirm existing governed soak safety remains intact.",
        },
        {
            "validator_id": "governed_self_development_loop",
            "path": "tests/orchestration/test_aios_governed_self_development_loop.py",
            "purpose": "Confirm existing governed loop safety remains intact.",
        },
        {
            "validator_id": "identity_spine",
            "path": "automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1",
            "purpose": "Required evidence before true future full-autonomy approval.",
        },
        {
            "validator_id": "orchestration_validator_chain",
            "path": "automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1",
            "purpose": "Required chain review before protected actions.",
        },
    ]


def _safety(status: str) -> dict[str, Any]:
    return {
        "status": status,
        "console_only": True,
        "writes_files": False,
        "mutates_registry": False,
        "creates_ready_stage": False,
        "mutates_queue": False,
        "mutates_locks": False,
        "mutates_approval": False,
        "writes_reports": False,
        "writes_telemetry": False,
        "writes_relay": False,
        "starts_runtime": False,
        "launches_workers": False,
        "enables_scheduler": False,
        "starts_daemon": False,
        "touches_secrets_or_env": False,
        "broker_or_live_trading": False,
        "protected_actions_blocked": True,
        "human_owner_required_before_protected_action": True,
        "self_approval_allowed": False,
    }


def _recommended_next_action(status: str, requested_level: str, profile: str, approval_gate: dict[str, Any]) -> str:
    if status == "BLOCKED":
        return "Stop and review hard-stop conditions before continuing autonomy supervision."
    if profile == "EMERGENCY_REVIEW":
        return "Wake the Human Owner and perform emergency review only."
    if requested_level == "LEVEL_5_FULL_AUTONOMY_REQUESTED":
        return "Review missing full-autonomy prerequisites and obtain explicit Human Owner approval before any protected action."
    if approval_gate["status"] == "REVIEW_REQUIRED":
        return "Resolve review-required validator or approval evidence before autonomy escalation; protected actions remain blocked."
    return str(PROFILE_DETAILS[profile]["next_action"])


def build_full_autonomy_supervision_state_result(payload: dict[str, Any]) -> dict[str, Any]:
    requested_level = _normalized(payload.get("requested_autonomy_level") or "LEVEL_3_SUPERVISED_AUTONOMY")
    if requested_level not in REQUESTED_AUTONOMY_LEVELS:
        requested_level = "LEVEL_3_SUPERVISED_AUTONOMY"
    operating_profile = _normalized(payload.get("operating_profile") or "12H_SUPERVISED")
    if operating_profile not in OPERATING_PROFILES:
        operating_profile = "12H_SUPERVISED"

    repo_state = _as_dict(payload.get("repo_state"))
    no_write_proof = _as_dict(payload.get("no_write_proof"))
    recent_validator_status = _normalized(payload.get("recent_validator_status") or "UNKNOWN")
    recent_sos_status = _normalized(payload.get("recent_sos_status") or "CLEAR")
    max_autonomy_hours = max(0, _int_value(payload.get("max_autonomy_hours"), 12))

    resolved_level = str(LEVEL_DETAILS[requested_level]["resolved"])
    sos_gate = _build_sos_gate(operating_profile, recent_sos_status)
    human_wake_policy = _build_human_wake_policy(
        operating_profile,
        _bool(payload.get("human_available"), default=True),
        _bool(payload.get("weekend_mode")),
        _bool(payload.get("vacation_mode")),
        _bool(payload.get("sleep_window_active")),
        sos_gate,
    )
    worker_supervision = _build_worker_supervision(
        requested_level,
        resolved_level,
        operating_profile,
        max_autonomy_hours,
        human_wake_policy,
    )
    prerequisites = _build_prerequisites(payload, repo_state)
    full_autonomy_state = _build_full_autonomy_state(
        requested_level,
        resolved_level,
        prerequisites,
        recent_validator_status,
    )
    approval_gate = _approval_gate(requested_level, recent_validator_status)
    protected_actions = _protected_actions()

    hard_stop_conditions = _dedupe(_repo_stop_conditions(repo_state) + _no_write_stop_conditions(no_write_proof))
    if _bool(sos_gate.get("sos_hard_stop_active")):
        hard_stop_conditions.append("SOS_HARD_STOP")
    if operating_profile == "EMERGENCY_REVIEW":
        hard_stop_conditions.append("EMERGENCY_REVIEW_ACTIVE")
    hard_stop_conditions = _dedupe(hard_stop_conditions)

    if hard_stop_conditions:
        status = "BLOCKED_BY_WRITE_SURFACE_RISK" if "WRITE_SURFACE_RISK" in hard_stop_conditions else "BLOCKED"
    elif approval_gate["status"] == "REVIEW_REQUIRED":
        status = "REVIEW_REQUIRED"
    else:
        status = "PASS"

    recommended_next_action = _recommended_next_action(status, requested_level, operating_profile, approval_gate)
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_utc": _safe_str(payload.get("generated_utc") or _now()),
        "repo_state": repo_state,
        "requested_autonomy_level": requested_level,
        "resolved_autonomy_level": resolved_level,
        "operating_profile": operating_profile,
        "full_autonomy_state": full_autonomy_state,
        "full_autonomy_prerequisites": prerequisites,
        "worker_supervision": worker_supervision,
        "human_wake_policy": human_wake_policy,
        "approval_gate": approval_gate,
        "sos_gate": sos_gate,
        "protected_actions": protected_actions,
        "recommended_validators": _recommended_validators(),
        "recommended_next_action": recommended_next_action,
        "safety": _safety(status),
        "no_write_proof": no_write_proof,
        "stop_conditions": hard_stop_conditions,
        "next_safe_action": recommended_next_action,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Build an AIOS full-autonomy supervision state result from JSON evidence.")
    parser.add_argument("--payload-base64", default="")
    args = parser.parse_args()
    if args.payload_base64:
        payload_text = base64.b64decode(args.payload_base64.encode("ascii")).decode("utf-8")
    else:
        payload_text = sys.stdin.read()
    result = build_full_autonomy_supervision_state_result(json.loads(payload_text))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["safety"]["status"] in {"PASS", "REVIEW_REQUIRED"} else 1


if __name__ == "__main__":
    raise SystemExit(_main())
