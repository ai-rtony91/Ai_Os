"""Pure AIOS day/night readiness router logic.

This module classifies readiness for supervised self-development without
starting runtime, launching workers, scheduling tasks, writing files, or
surfacing protected commands.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_DAY_NIGHT_READINESS_RESULT.v1"
MODE = "DRY_RUN_READ_ONLY"
NEXT_SAFE_PACKET = "AIOS-GOVERNED-SELF-DEVELOPMENT-LOOP-APPLY-V1"

READINESS_CLASSIFICATIONS = {
    "OFF",
    "OBSERVE_ALLOWED",
    "SUPERVISED_RECOMMENDATION_ALLOWED",
    "PAUSE_REQUIRED",
    "SOS_HARD_STOP",
    "BLOCKED_BY_DIRTY_REPO",
    "BLOCKED_BY_UNSAFE_SURFACE",
    "BLOCKED_BY_APPROVAL_STATE",
    "BLOCKED_BY_RUNTIME_RISK",
    "BLOCKED_BY_VALIDATOR_RISK",
    "BLOCKED_BY_BACKUP_INTERFERENCE",
}

COMMAND_BLOCK_PATTERNS = [
    r"\bgit\s+add\b",
    r"\bgit\s+commit\b",
    r"\bgit\s+push\b",
    r"\bgit\s+merge\b",
    r"\bgit\s+reset\b",
    r"\bgit\s+clean\b",
    r"\bgh\s+pr\b",
    r"\b-Mode\s+APPLY\b",
    r"\bmode\s*[:=]\s*APPLY\b",
    r"\bInvoke-AiOsExactCommitPackage\b",
    r"\bNew-AiOsRelayMessage\b",
    r"\bInvoke-AiOsApprovalChain\b",
    r"\bClaim-AiOsFileLock\b",
    r"\bRelease-AiOsFileLock\b",
    r"\bStart-AiOsPersistentRuntimeSupervisor\b",
    r"\bStart-AiOsWorkerDaemon\b",
    r"\bStart-AiOsWorkerLoop\b",
    r"\bOpen-AiOsWorkerWindow\b",
    r"\bscheduler\b",
    r"\bdaemon\b",
    r"\bworker\s+launch\b",
    r"\bbroker\b",
    r"\boanda\b",
    r"\bwebhook\b",
    r"\border\b",
    r"\blive[-_\s]?trading\b",
    r"\bsecret\b",
    r"\btoken\b",
    r"\bapi[-_ ]?key\b",
    r"\.env\b",
    r"code[xX].*prompt",
    r"execution.*token",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return _safe_str(value).lower() in {"true", "1", "yes", "y"}


def command_is_safe_to_surface(command: Any) -> bool:
    text = _safe_str(command)
    if not text:
        return False
    if "\n" in text or "\r" in text:
        return False
    return not any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in COMMAND_BLOCK_PATTERNS)


def sanitize_command_field(command: Any) -> dict[str, Any]:
    text = _safe_str(command)
    if command_is_safe_to_surface(text):
        return {"safe_to_surface": True, "display_text": text, "blocked_reason": ""}
    return {
        "safe_to_surface": False,
        "display_text": "Sanitized: executable recommendation withheld; review readiness classification and intent only.",
        "blocked_reason": "command_or_protected_action_not_surfaceable",
    }


def _safety_status(source: dict[str, Any]) -> str:
    return _safe_str(_as_dict(source.get("safety")).get("status") or source.get("status") or "UNKNOWN")


def _surface_has_runtime_risk(surface: dict[str, Any]) -> bool:
    classification = _safe_str(surface.get("classification"))
    path = _safe_str(surface.get("path")).lower()
    return classification == "RUNTIME_OR_WORKER_BLOCKED" or any(
        term in path for term in ("runtime", "worker", "scheduler", "daemon", "launcher")
    ) and classification.endswith("_BLOCKED")


def build_validator_status(validator_router: dict[str, Any]) -> dict[str, Any]:
    safety = _as_dict(validator_router.get("safety"))
    excluded = [_as_dict(item) for item in _as_list(validator_router.get("excluded_surfaces"))]
    unsafe_flags = [
        "writes_files",
        "writes_reports",
        "writes_telemetry",
        "writes_packet_drafts",
        "mutates_registry",
        "mutates_queue",
        "mutates_locks",
        "mutates_approvals",
        "writes_relay",
        "starts_runtime",
        "launches_workers",
        "protected_action_recommended",
        "secrets_or_env_access",
        "broker_or_live_trading",
    ]
    unsafe_flag_names = [flag for flag in unsafe_flags if _bool(safety.get(flag))]
    runtime_blocked_surfaces = [
        surface.get("surface_id") or surface.get("path") for surface in excluded if _surface_has_runtime_risk(surface)
    ]
    return {
        "source_schema": _safe_str(validator_router.get("schema")),
        "status": _safety_status(validator_router),
        "stop_conditions": _as_list(validator_router.get("stop_conditions")),
        "unsafe_flags": unsafe_flag_names,
        "runtime_blocked_surfaces": runtime_blocked_surfaces,
        "safe_validator_count": len(_as_list(validator_router.get("validator_catalog"))),
        "safe_evidence_count": len(_as_list(validator_router.get("evidence_sources"))),
    }


def build_approval_state(action_recommendation: dict[str, Any], approval_summary: dict[str, Any]) -> dict[str, Any]:
    pending = int(approval_summary.get("pending_count") or approval_summary.get("pending") or 0)
    blocked = int(approval_summary.get("blocked_count") or approval_summary.get("blocked") or 0)
    matches = int(action_recommendation.get("approval_matches") or 0)
    packet_status = _safe_str(action_recommendation.get("packet_status")).lower()
    approval_required = matches > 0 or pending > 0 or packet_status == "awaiting_approval"
    sos_required = _bool(action_recommendation.get("relay_sos_anthony_required")) or _safe_str(
        action_recommendation.get("relay_sos_escalation_status")
    ) == "SOS_ESCALATION"
    return {
        "approval_required": approval_required,
        "pending_count": pending,
        "blocked_count": blocked,
        "approval_matches": matches,
        "sos_hard_stop": sos_required,
        "status": "SOS_HARD_STOP" if sos_required else ("BLOCKED_BY_APPROVAL_STATE" if approval_required or blocked > 0 else "CLEAR"),
    }


def build_runtime_worker_state(payload: dict[str, Any], validator_status: dict[str, Any]) -> dict[str, Any]:
    state = _as_dict(payload.get("runtime_worker_state"))
    risk = _bool(state.get("runtime_risk_detected")) or _bool(state.get("worker_risk_detected"))
    risk = risk or bool(validator_status.get("runtime_blocked_surfaces")) and _bool(
        payload.get("runtime_worker_surface_selected")
    )
    return {
        "runtime_risk_detected": risk,
        "worker_launch_detected": _bool(state.get("worker_launch_detected")),
        "scheduler_or_daemon_detected": _bool(state.get("scheduler_or_daemon_detected")),
        "runtime_state_source": _safe_str(state.get("runtime_state_source") or "read_only_evidence"),
        "status": "BLOCKED_BY_RUNTIME_RISK"
        if risk or _bool(state.get("worker_launch_detected")) or _bool(state.get("scheduler_or_daemon_detected"))
        else "CLEAR",
    }


def build_backup_interference_state(payload: dict[str, Any]) -> dict[str, Any]:
    state = _as_dict(payload.get("backup_interference_state"))
    interference = any(
        _bool(state.get(flag))
        for flag in (
            "interference_detected",
            "repo_local_backup_lock_present",
            "backup_in_progress",
            "snapshot_restore_candidate_present",
        )
    )
    return {
        "interference_detected": interference,
        "repo_local_backup_lock_present": _bool(state.get("repo_local_backup_lock_present")),
        "backup_in_progress": _bool(state.get("backup_in_progress")),
        "snapshot_restore_candidate_present": _bool(state.get("snapshot_restore_candidate_present")),
        "status": "BLOCKED_BY_BACKUP_INTERFERENCE" if interference else "CLEAR",
    }


def _source_item(name: str, path: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "path": path,
        "available": bool(data),
        "schema": _safe_str(data.get("schema")),
        "status": _safety_status(data) if data else "MISSING_OR_SKIPPED",
    }


def build_autonomy_chain_state(payload: dict[str, Any]) -> dict[str, Any]:
    self_audit = _as_dict(payload.get("self_audit_result"))
    packet_router = _as_dict(payload.get("packet_router_result"))
    validator_router = _as_dict(payload.get("validator_evidence_router_result"))
    campaign_no_ready = _as_dict(payload.get("campaign_no_ready"))
    campaign_next_task = _as_dict(payload.get("campaign_next_task"))
    return {
        "self_audit_status": _safety_status(self_audit),
        "packet_router_status": _safety_status(packet_router),
        "validator_evidence_router_status": _safety_status(validator_router),
        "campaign_overall_readiness": _safe_str(
            campaign_no_ready.get("overall_readiness") or campaign_next_task.get("overall_readiness") or "UNKNOWN"
        ),
        "no_ready_stage_classification": _safe_str(campaign_no_ready.get("no_ready_stage_classification") or "UNKNOWN"),
        "next_packet_candidate": _safe_str(campaign_next_task.get("next_packet_candidate")),
    }


def _classification(payload: dict[str, Any], validator_status: dict[str, Any], approval_state: dict[str, Any], runtime_state: dict[str, Any], backup_state: dict[str, Any], no_write_proof: dict[str, Any]) -> tuple[str, list[str]]:
    repo_state = _as_dict(payload.get("repo_state"))
    requested_mode = _safe_str(payload.get("requested_operator_mode") or "AUTO").upper()
    stop_conditions: list[str] = []

    if requested_mode == "OFF":
        return "OFF", ["OPERATOR_MODE_OFF"]
    if bool(repo_state.get("dirty", False)) and bool(repo_state.get("fail_on_dirty_worktree", False)) and not bool(
        repo_state.get("dirty_allowed_for_day_night_readiness_validation", False)
    ):
        return "BLOCKED_BY_DIRTY_REPO", ["DIRTY_WORKTREE"]
    if bool(no_write_proof.get("changed", False)):
        return "BLOCKED_BY_UNSAFE_SURFACE", ["WRITE_SURFACE_RISK"]
    if backup_state["status"] != "CLEAR":
        return "BLOCKED_BY_BACKUP_INTERFERENCE", [backup_state["status"]]
    if approval_state["sos_hard_stop"]:
        return "SOS_HARD_STOP", ["SOS_HARD_STOP"]
    if approval_state["status"] != "CLEAR":
        return "BLOCKED_BY_APPROVAL_STATE", [approval_state["status"]]
    if runtime_state["status"] != "CLEAR":
        return "BLOCKED_BY_RUNTIME_RISK", [runtime_state["status"]]
    if validator_status["status"] != "PASS" or validator_status["stop_conditions"] or validator_status["unsafe_flags"]:
        stop_conditions.append("VALIDATOR_EVIDENCE_ROUTER_NOT_PASS")
        if validator_status["stop_conditions"]:
            stop_conditions.extend(str(item) for item in validator_status["stop_conditions"])
        if validator_status["unsafe_flags"]:
            stop_conditions.extend("UNSAFE_VALIDATOR_FLAG_" + flag.upper() for flag in validator_status["unsafe_flags"])
        return "BLOCKED_BY_VALIDATOR_RISK", stop_conditions
    if requested_mode == "OBSERVE":
        return "OBSERVE_ALLOWED", []
    if requested_mode == "PAUSE":
        return "PAUSE_REQUIRED", ["OPERATOR_MODE_PAUSE"]
    return "SUPERVISED_RECOMMENDATION_ALLOWED", []


def _operator_modes(readiness: str) -> tuple[list[str], list[str]]:
    base_blocked = [
        "APPLY_EXECUTION",
        "RUNTIME_START",
        "WORKER_LAUNCH",
        "SCHEDULER",
        "DAEMON",
        "QUEUE_MUTATION",
        "LOCK_MUTATION",
        "APPROVAL_MUTATION",
        "REPORT_WRITE",
        "TELEMETRY_WRITE",
        "RELAY_WRITE",
        "PROTECTED_GIT_ACTION",
        "BROKER_OR_LIVE_TRADING",
    ]
    if readiness == "SUPERVISED_RECOMMENDATION_ALLOWED":
        return ["IDLE", "OBSERVE_READ_ONLY", "SUPERVISED_RECOMMENDATION"], base_blocked
    if readiness == "OBSERVE_ALLOWED":
        return ["IDLE", "OBSERVE_READ_ONLY"], base_blocked + ["SUPERVISED_RECOMMENDATION"]
    if readiness == "PAUSE_REQUIRED":
        return ["IDLE"], base_blocked + ["OBSERVE_READ_ONLY", "SUPERVISED_RECOMMENDATION"]
    return [], base_blocked + ["IDLE", "OBSERVE_READ_ONLY", "SUPERVISED_RECOMMENDATION"]


def build_readiness_result(payload: dict[str, Any]) -> dict[str, Any]:
    no_write_proof = _as_dict(payload.get("no_write_proof"))
    action_recommendation = _as_dict(payload.get("action_recommendation"))
    validator_router = _as_dict(payload.get("validator_evidence_router_result"))
    validator_status = build_validator_status(validator_router)
    approval_state = build_approval_state(action_recommendation, _as_dict(payload.get("approval_inbox_summary")))
    runtime_worker_state = build_runtime_worker_state(payload, validator_status)
    backup_interference_state = build_backup_interference_state(payload)
    readiness, stop_conditions = _classification(
        payload,
        validator_status,
        approval_state,
        runtime_worker_state,
        backup_interference_state,
        no_write_proof,
    )
    allowed_modes, blocked_modes = _operator_modes(readiness)
    recommended_next_packet = NEXT_SAFE_PACKET if readiness == "SUPERVISED_RECOMMENDATION_ALLOWED" else None
    evidence_sources = [
        _source_item("self_audit", "automation/orchestration/self_audit/Invoke-AiOsSelfAuditLoop.DRY_RUN.ps1", _as_dict(payload.get("self_audit_result"))),
        _source_item("self_development_packet_router", "automation/orchestration/self_audit/Get-AiOsSelfDevelopmentPacketRouter.DRY_RUN.ps1", _as_dict(payload.get("packet_router_result"))),
        _source_item("validator_evidence_router", "automation/orchestration/validators/Get-AiOsValidatorEvidenceRouter.DRY_RUN.ps1", validator_router),
        _source_item("campaign_no_ready", "automation/orchestration/campaign_registry/Get-AiOsCampaignNoReadyStageDiscovery.DRY_RUN.ps1", _as_dict(payload.get("campaign_no_ready"))),
        _source_item("campaign_next_task", "automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1", _as_dict(payload.get("campaign_next_task"))),
        _source_item("action_recommendation", "automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1", action_recommendation),
        _source_item("approval_inbox_summary", "automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1", _as_dict(payload.get("approval_inbox_summary"))),
        _source_item("lock_status", "automation/orchestration/locks/Get-AiOsWorkerLockStatus.DRY_RUN.ps1", _as_dict(payload.get("lock_status"))),
        _source_item("worker_inbox", "automation/orchestration/workers/inbox/Get-AiOsWorkerInbox.DRY_RUN.ps1", _as_dict(payload.get("worker_inbox"))),
    ]
    next_safe_action = (
        f"Review {NEXT_SAFE_PACKET} in a separate APPLY packet with Human Owner approval. No execution command is recommended here."
        if recommended_next_packet
        else "Stop or remain read-only until readiness blockers are cleared by a separate approved packet."
    )

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_utc": _safe_str(payload.get("generated_utc") or _now()),
        "repo_state": _as_dict(payload.get("repo_state")),
        "autonomy_chain_state": build_autonomy_chain_state(payload),
        "readiness": {
            "classification": readiness,
            "recommendation_allowed": readiness == "SUPERVISED_RECOMMENDATION_ALLOWED",
            "execution_allowed": False,
            "human_owner_required": readiness.startswith("BLOCKED_") or readiness == "SOS_HARD_STOP",
        },
        "allowed_operator_modes": allowed_modes,
        "blocked_operator_modes": blocked_modes,
        "evidence_sources": evidence_sources,
        "validator_status": validator_status,
        "approval_state": approval_state,
        "runtime_worker_state": runtime_worker_state,
        "backup_interference_state": backup_interference_state,
        "recommended_next_packet": recommended_next_packet,
        "required_before_supervised_mode": [
            "Authority context loaded.",
            "Repo is clean or dirty only within exact validation allowlist.",
            "Self-audit, packet router, and validator/evidence router report PASS.",
            "No approval, SOS, runtime, worker, scheduler, daemon, backup, secret, broker, or live-trading blocker is active.",
        ],
        "required_before_runtime_or_worker": [
            "This readiness router never authorizes runtime or worker launch.",
            "A separate Human Owner-approved packet, runtime validator chain, and stop controls are required before any runtime, worker, scheduler, or daemon path.",
        ],
        "safety": {
            "status": "PASS" if readiness in {"OBSERVE_ALLOWED", "SUPERVISED_RECOMMENDATION_ALLOWED", "PAUSE_REQUIRED", "OFF"} else readiness,
            "console_only": True,
            "writes_files": False,
            "writes_reports": False,
            "writes_telemetry": False,
            "writes_packet_drafts": False,
            "outputs_packet_body": False,
            "mutates_registry": False,
            "mutates_queue": False,
            "mutates_locks": False,
            "mutates_approvals": False,
            "writes_relay": False,
            "starts_runtime": False,
            "launches_workers": False,
            "scheduler_or_daemon": False,
            "protected_action_recommended": False,
            "commands_sanitized": True,
            "secrets_or_env_access": False,
            "broker_or_live_trading": False,
            "action_recommendation_command": sanitize_command_field(action_recommendation.get("recommended_command")),
        },
        "no_write_proof": no_write_proof,
        "stop_conditions": stop_conditions,
        "next_safe_action": next_safe_action,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Build an AIOS day/night readiness result from JSON evidence.")
    parser.add_argument("--payload-base64", default="")
    args = parser.parse_args()
    if args.payload_base64:
        payload_text = base64.b64decode(args.payload_base64.encode("ascii")).decode("utf-8")
    else:
        payload_text = sys.stdin.read()
    result = build_readiness_result(json.loads(payload_text))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["safety"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(_main())
