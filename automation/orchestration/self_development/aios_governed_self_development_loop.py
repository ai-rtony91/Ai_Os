"""Pure AIOS governed self-development loop logic.

The PowerShell runner gathers read-only evidence from existing DRY_RUN
surfaces. This module only classifies that evidence, selects an inert next
packet ID when safe, and returns a JSON-ready result. It writes no files,
starts no processes, and emits no packet body text.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_GOVERNED_SELF_DEVELOPMENT_LOOP_RESULT.v1"
MODE = "DRY_RUN_READ_ONLY"
NEXT_SAFE_PACKET = "AIOS-OPERATOR-CONTROL-SURFACE-CONTRACT-DRYRUN-V1"

SELF_AUDIT_SCHEMA = "AIOS_SELF_AUDIT_LOOP_RESULT.v1"
PACKET_ROUTER_SCHEMA = "AIOS_SELF_DEVELOPMENT_PACKET_ROUTER_RESULT.v1"
VALIDATOR_ROUTER_SCHEMA = "AIOS_VALIDATOR_EVIDENCE_ROUTER_RESULT.v1"
DAY_NIGHT_READINESS_SCHEMA = "AIOS_DAY_NIGHT_READINESS_RESULT.v1"

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
    r"\bNew-AiOsPacketApprovalRequest\b",
    r"\bInvoke-AiOsApprovalChain\b",
    r"\bClaim-AiOsFileLock\b",
    r"\bRelease-AiOsFileLock\b",
    r"\bStart-AiOsPersistentRuntimeSupervisor\b",
    r"\bStart-AiOsWorkerDaemon\b",
    r"\bStart-AiOsWorkerLoop\b",
    r"\bOpen-AiOsWorkerWindow\b",
    r"\bStart-AiOsAutonomousWorkerCycle\b",
    r"\bInvoke-AiOsWorkerSafeExecute\b",
    r"\bworker\s+launch\b",
    r"\bscheduler\b",
    r"\bdaemon\b",
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

PACKET_BODY_MARKERS = [
    "CODEX-ONLY PROMPT",
    "AI_OS EXECUTION TOKEN",
    "AI_OS BOOTSTRAP REQUIRED",
]

UNSAFE_SAFETY_FLAGS = [
    "writes_files",
    "writes_reports",
    "writes_telemetry",
    "writes_packets",
    "writes_packet_drafts",
    "writes_proposed_packets",
    "outputs_packet_body",
    "creates_ready_stage",
    "mutates_registry",
    "mutates_queue",
    "mutates_locks",
    "mutates_approvals",
    "writes_relay",
    "starts_runtime",
    "launches_workers",
    "scheduler_or_daemon",
    "protected_git_action",
    "protected_action_recommended",
    "secrets_or_env_access",
    "broker_or_live_trading",
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


def _status(source: dict[str, Any]) -> str:
    safety = _as_dict(source.get("safety"))
    return _safe_str(safety.get("status") or source.get("status") or "UNKNOWN")


def _schema_ok(source: dict[str, Any], expected: str) -> bool:
    return _safe_str(source.get("schema")) == expected


def command_is_safe_to_surface(command: Any) -> bool:
    text = _safe_str(command)
    if not text:
        return False
    if "\n" in text or "\r" in text:
        return False
    return not any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in COMMAND_BLOCK_PATTERNS)


def sanitize_command_field(command: Any) -> dict[str, Any]:
    """Classify a command-like field while withholding command text."""
    safe = command_is_safe_to_surface(command)
    return {
        "safe_to_surface": safe,
        "display_text": "Sanitized: command recommendation withheld; review packet ID only.",
        "blocked_reason": "" if safe else "command_or_protected_action_not_surfaceable",
    }


def _unsafe_flags(source: dict[str, Any]) -> list[str]:
    safety = _as_dict(source.get("safety"))
    return [flag for flag in UNSAFE_SAFETY_FLAGS if _bool(safety.get(flag))]


def _surface_status(name: str, path: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": name,
        "path": path,
        "available": bool(data),
        "schema": _safe_str(data.get("schema")),
        "status": _status(data) if data else "MISSING_OR_SKIPPED",
        "unsafe_flags": _unsafe_flags(data),
    }


def build_autonomy_chain_state(payload: dict[str, Any]) -> dict[str, Any]:
    self_audit = _as_dict(payload.get("self_audit_result"))
    packet_router = _as_dict(payload.get("packet_router_result"))
    validator_router = _as_dict(payload.get("validator_evidence_router_result"))
    day_night = _as_dict(payload.get("day_night_readiness_result"))
    campaign_no_ready = _as_dict(payload.get("campaign_no_ready"))
    campaign_next_task = _as_dict(payload.get("campaign_next_task"))
    action_recommendation = _as_dict(payload.get("action_recommendation"))
    return {
        "self_audit_status": _status(self_audit),
        "packet_router_status": _status(packet_router),
        "validator_evidence_router_status": _status(validator_router),
        "day_night_readiness_status": _status(day_night),
        "day_night_recommendation_allowed": bool(_as_dict(day_night.get("readiness")).get("recommendation_allowed")),
        "day_night_classification": _safe_str(_as_dict(day_night.get("readiness")).get("classification") or "UNKNOWN"),
        "campaign_overall_readiness": _safe_str(
            campaign_no_ready.get("overall_readiness") or campaign_next_task.get("overall_readiness") or "UNKNOWN"
        ),
        "no_ready_stage_classification": _safe_str(campaign_no_ready.get("no_ready_stage_classification") or "UNKNOWN"),
        "campaign_next_packet_candidate": _safe_str(campaign_next_task.get("next_packet_candidate")),
        "action_recommendation_command": sanitize_command_field(action_recommendation.get("recommended_command")),
    }


def build_validator_chain(payload: dict[str, Any]) -> list[dict[str, Any]]:
    self_audit = _as_dict(payload.get("self_audit_result"))
    packet_router = _as_dict(payload.get("packet_router_result"))
    validator_router = _as_dict(payload.get("validator_evidence_router_result"))
    day_night = _as_dict(payload.get("day_night_readiness_result"))
    return [
        _surface_status(
            "self_audit",
            "automation/orchestration/self_audit/Invoke-AiOsSelfAuditLoop.DRY_RUN.ps1",
            self_audit,
        ),
        _surface_status(
            "self_development_packet_router",
            "automation/orchestration/self_audit/Get-AiOsSelfDevelopmentPacketRouter.DRY_RUN.ps1",
            packet_router,
        ),
        _surface_status(
            "validator_evidence_router",
            "automation/orchestration/validators/Get-AiOsValidatorEvidenceRouter.DRY_RUN.ps1",
            validator_router,
        ),
        _surface_status(
            "day_night_readiness",
            "automation/orchestration/supervisor/Get-AiOsDayNightReadiness.DRY_RUN.ps1",
            day_night,
        ),
    ]


def build_readiness(payload: dict[str, Any]) -> dict[str, Any]:
    day_night = _as_dict(payload.get("day_night_readiness_result"))
    readiness = _as_dict(day_night.get("readiness"))
    approval_state = _as_dict(day_night.get("approval_state"))
    runtime_state = _as_dict(day_night.get("runtime_worker_state"))
    backup_state = _as_dict(day_night.get("backup_interference_state"))
    return {
        "classification": _safe_str(readiness.get("classification") or "UNKNOWN"),
        "recommendation_allowed": bool(readiness.get("recommendation_allowed", False)),
        "execution_allowed": False,
        "approval_state": {
            "status": _safe_str(approval_state.get("status") or "UNKNOWN"),
            "approval_required": bool(approval_state.get("approval_required", False)),
            "sos_hard_stop": bool(approval_state.get("sos_hard_stop", False)),
        },
        "runtime_worker_state": {
            "status": _safe_str(runtime_state.get("status") or "UNKNOWN"),
            "runtime_risk_detected": bool(runtime_state.get("runtime_risk_detected", False)),
            "worker_launch_detected": bool(runtime_state.get("worker_launch_detected", False)),
            "scheduler_or_daemon_detected": bool(runtime_state.get("scheduler_or_daemon_detected", False)),
        },
        "backup_interference_state": {
            "status": _safe_str(backup_state.get("status") or "UNKNOWN"),
            "interference_detected": bool(backup_state.get("interference_detected", False)),
            "repo_local_backup_lock_present": bool(backup_state.get("repo_local_backup_lock_present", False)),
            "backup_in_progress": bool(backup_state.get("backup_in_progress", False)),
            "snapshot_restore_candidate_present": bool(backup_state.get("snapshot_restore_candidate_present", False)),
        },
    }


def _repo_stop_conditions(repo_state: dict[str, Any]) -> list[str]:
    stops: list[str] = []
    if repo_state and not bool(repo_state.get("branch_matches_expected", True)):
        stops.append("BRANCH_MISMATCH")
    if (
        bool(repo_state.get("dirty", False))
        and bool(repo_state.get("fail_on_dirty_worktree", False))
        and not bool(repo_state.get("dirty_allowed_for_governed_loop_validation", False))
    ):
        stops.append("DIRTY_WORKTREE")
    return stops


def _chain_stop_conditions(payload: dict[str, Any], readiness: dict[str, Any]) -> list[str]:
    stops: list[str] = []
    self_audit = _as_dict(payload.get("self_audit_result"))
    packet_router = _as_dict(payload.get("packet_router_result"))
    validator_router = _as_dict(payload.get("validator_evidence_router_result"))
    day_night = _as_dict(payload.get("day_night_readiness_result"))

    for label, source, expected_schema in (
        ("SELF_AUDIT", self_audit, SELF_AUDIT_SCHEMA),
        ("PACKET_ROUTER", packet_router, PACKET_ROUTER_SCHEMA),
        ("VALIDATOR_EVIDENCE_ROUTER", validator_router, VALIDATOR_ROUTER_SCHEMA),
        ("DAY_NIGHT_READINESS", day_night, DAY_NIGHT_READINESS_SCHEMA),
    ):
        if not _schema_ok(source, expected_schema):
            stops.append(f"{label}_SCHEMA_INVALID")
        if _status(source) != "PASS":
            stops.append(f"{label}_NOT_PASS")
        for flag in _unsafe_flags(source):
            stops.append(f"{label}_UNSAFE_FLAG_{flag.upper()}")
        for condition in _as_list(source.get("stop_conditions")):
            if _safe_str(condition):
                stops.append(f"{label}_STOP_{_safe_str(condition).upper()}")

    if readiness["classification"] != "SUPERVISED_RECOMMENDATION_ALLOWED":
        stops.append("DAY_NIGHT_SUPERVISED_RECOMMENDATION_NOT_ALLOWED")
    if not bool(readiness["recommendation_allowed"]):
        stops.append("DAY_NIGHT_RECOMMENDATION_NOT_ALLOWED")
    if _safe_str(readiness["approval_state"]["status"]) != "CLEAR":
        stops.append("APPROVAL_OR_SOS_STOP_CONDITION")
    if bool(readiness["approval_state"]["approval_required"]) or bool(readiness["approval_state"]["sos_hard_stop"]):
        stops.append("APPROVAL_OR_SOS_STOP_CONDITION")
    if _safe_str(readiness["runtime_worker_state"]["status"]) != "CLEAR":
        stops.append("RUNTIME_OR_WORKER_STOP_CONDITION")
    if (
        bool(readiness["runtime_worker_state"]["runtime_risk_detected"])
        or bool(readiness["runtime_worker_state"]["worker_launch_detected"])
        or bool(readiness["runtime_worker_state"]["scheduler_or_daemon_detected"])
    ):
        stops.append("RUNTIME_OR_WORKER_STOP_CONDITION")
    if _safe_str(readiness["backup_interference_state"]["status"]) != "CLEAR":
        stops.append("BACKUP_INTERFERENCE")
    if (
        bool(readiness["backup_interference_state"]["interference_detected"])
        or bool(readiness["backup_interference_state"]["repo_local_backup_lock_present"])
        or bool(readiness["backup_interference_state"]["backup_in_progress"])
        or bool(readiness["backup_interference_state"]["snapshot_restore_candidate_present"])
    ):
        stops.append("BACKUP_INTERFERENCE")

    command = sanitize_command_field(_as_dict(payload.get("action_recommendation")).get("recommended_command"))
    if not command["safe_to_surface"]:
        stops.append("ACTION_RECOMMENDATION_COMMAND_UNSAFE")
    return stops


def _no_write_stop_conditions(no_write_proof: dict[str, Any]) -> list[str]:
    if bool(no_write_proof.get("changed", False)):
        return ["WRITE_SURFACE_RISK"]
    return []


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        key = _safe_str(item)
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(key)
    return result


def _safety_status(stop_conditions: list[str], no_write_proof: dict[str, Any]) -> str:
    if bool(no_write_proof.get("changed", False)):
        return "BLOCKED_BY_WRITE_SURFACE_RISK"
    if stop_conditions:
        return "BLOCKED"
    return "PASS"


def _blocked_surfaces(payload: dict[str, Any], stop_conditions: list[str]) -> list[dict[str, Any]]:
    configured = []
    for item in _as_list(payload.get("blocked_surfaces")):
        if isinstance(item, dict):
            configured.append(item)
        elif _safe_str(item):
            configured.append({"path": _safe_str(item), "reason": "blocked_by_contract"})
    for condition in stop_conditions:
        configured.append({"path": "", "reason": condition})
    return configured


def _safe_surface_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in _as_list(payload.get("safe_surfaces_used")):
        if isinstance(item, dict):
            records.append(item)
        elif _safe_str(item):
            records.append({"path": _safe_str(item), "ok": True})
    return records


def _approval_required() -> dict[str, Any]:
    return {
        "human_owner_required": True,
        "before_apply": True,
        "before_commit": True,
        "before_push": True,
        "before_pr": True,
        "before_merge": True,
        "before_runtime": True,
        "before_worker_launch": True,
        "before_queue_lock_or_approval_mutation": True,
        "validator_pass_is_not_approval": True,
    }


def build_governed_self_development_result(payload: dict[str, Any]) -> dict[str, Any]:
    repo_state = _as_dict(payload.get("repo_state"))
    no_write_proof = _as_dict(payload.get("no_write_proof"))
    readiness = build_readiness(payload)
    autonomy_chain_state = build_autonomy_chain_state(payload)
    validator_chain = build_validator_chain(payload)
    stop_conditions = _dedupe(
        _repo_stop_conditions(repo_state)
        + _chain_stop_conditions(payload, readiness)
        + _no_write_stop_conditions(no_write_proof)
    )
    status = _safety_status(stop_conditions, no_write_proof)

    recommended_next_packet = None
    if status == "PASS":
        recommended_next_packet = {
            "packet_id": NEXT_SAFE_PACKET,
            "mode": "DRY_RUN",
            "intent": "Define the operator control surface contract as a separate read-only packet and stop before implementation.",
            "packet_body_included": False,
        }

    next_safe_action = (
        f"Review {NEXT_SAFE_PACKET} as the next supervised packet ID; this loop emits no execution command."
        if recommended_next_packet
        else "Stop and review governed self-development loop blockers before selecting any next packet."
    )

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_utc": _safe_str(payload.get("generated_utc") or _now()),
        "repo_state": repo_state,
        "autonomy_chain_state": autonomy_chain_state,
        "safe_surfaces_used": _safe_surface_records(payload),
        "recommended_next_packet": recommended_next_packet,
        "validator_chain": validator_chain,
        "readiness": readiness,
        "approval_required": _approval_required(),
        "blocked_surfaces": _blocked_surfaces(payload, stop_conditions),
        "safety": {
            "status": status,
            "console_only": True,
            "writes_files": False,
            "writes_reports": False,
            "writes_telemetry": False,
            "writes_packet_drafts": False,
            "writes_proposed_packets": False,
            "outputs_packet_body": False,
            "creates_ready_stage": False,
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
            "next_safe_packet": NEXT_SAFE_PACKET if recommended_next_packet else None,
            "action_recommendation_command": autonomy_chain_state["action_recommendation_command"],
        },
        "no_write_proof": no_write_proof,
        "stop_conditions": stop_conditions,
        "next_safe_action": next_safe_action,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Build an AIOS governed self-development loop result from JSON evidence.")
    parser.add_argument("--payload-base64", default="")
    args = parser.parse_args()
    if args.payload_base64:
        payload_text = base64.b64decode(args.payload_base64.encode("ascii")).decode("utf-8")
    else:
        payload_text = sys.stdin.read()
    result = build_governed_self_development_result(json.loads(payload_text))
    text = json.dumps(result, indent=2, sort_keys=True)
    for marker in PACKET_BODY_MARKERS:
        text = text.replace(marker, "[withheld_packet_marker]")
    print(text)
    return 0 if result["safety"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(_main())
