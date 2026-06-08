from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PROTECTED_ACTIONS = {"APPLY", "COMMIT", "PUSH", "MERGE", "STASH", "RESET", "CLEAN", "SCHEDULER", "LIVE_SOS"}
QUEUE_STATUSES = {"queued", "running", "blocked", "waiting_for_approval", "complete", "failed", "sos_required", "cancelled"}
APPROVAL_FIELDS = {
    "approval_id", "created_at", "requested_by_worker", "requested_action", "action_scope",
    "protected_paths", "risk_flags", "approval_status", "apply_packet_preparation_approved",
    "apply_execution_approved", "operator_authority_marker", "allowed_actions",
    "disallowed_actions", "evidence_links", "next_safe_action",
}
QUEUE_FIELDS = {
    "task_id", "title", "lane", "status", "priority", "created_at", "updated_at",
    "owner_worker", "allowed_workers", "branch", "pr_number", "protected_paths",
    "required_approval_id", "lock_id", "validation_contract", "output_contract",
    "blocked_reason", "next_safe_action", "completion_evidence", "sos_policy",
}
LOCK_FIELDS = {
    "lock_id", "worker_id", "worker_type", "lane", "task_id", "branch", "pr_number",
    "protected_paths", "acquired_at", "expires_at", "heartbeat_at", "status",
    "allowed_actions", "disallowed_actions", "next_safe_action",
}
WEEKEND_WEIGHTS = {
    "generated_output_clean": 10,
    "tier0_watchdog": 10,
    "operator_relief_one_shot": 5,
    "worker_dispatcher_control_plane": 5,
    "tier1_restart_safety": 15,
    "atomic_state_safety": 10,
    "approval_queue_locks": 15,
    "ci_hard_blockers": 10,
    "resource_endurance": 10,
    "live_sos_last_mile": 10,
    "supervised_24h_run": 5,
}


@dataclass
class Finding:
    code: str
    message: str


def _as_list(payload: Any, key: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        return [payload]
    return []


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _has_wildcard(values: Any) -> bool:
    return isinstance(values, list) and any(str(value).strip() in {"*", "**", "repo-root", "."} for value in values)


def validate_approvals(payload: Any, *, now: datetime | None = None) -> list[Finding]:
    current = now or datetime.now(timezone.utc)
    findings: list[Finding] = []
    for item in _as_list(payload, "approvals"):
        missing = sorted(APPROVAL_FIELDS - set(item))
        if missing:
            findings.append(Finding("AIOS-APPROVAL-MISSING-FIELDS", f"{item.get('approval_id', '<unknown>')}: {', '.join(missing)}"))
        paths = item.get("protected_paths")
        if not isinstance(paths, list) or not paths:
            findings.append(Finding("AIOS-APPROVAL-PROTECTED-PATHS-MISSING", f"{item.get('approval_id', '<unknown>')}: protected_paths required"))
        if _has_wildcard(paths) or _has_wildcard(item.get("allowed_actions")):
            findings.append(Finding("AIOS-APPROVAL-WILDCARD", f"{item.get('approval_id', '<unknown>')}: wildcard scope is blocked"))
        expires = _parse_time(item.get("expires_at") or item.get("stale_after"))
        if expires and expires <= current:
            findings.append(Finding("AIOS-APPROVAL-STALE", f"{item.get('approval_id', '<unknown>')}: approval is stale"))
        action = str(item.get("requested_action", "")).upper()
        if action == "APPLY" and item.get("apply_execution_approved") is not True:
            findings.append(Finding("AIOS-APPROVAL-APPLY-NOT-APPROVED", f"{item.get('approval_id', '<unknown>')}: APPLY execution not approved"))
        if action in {"SCHEDULER", "LIVE_TRADING", "BROKER", "CLOUD"}:
            findings.append(Finding("AIOS-APPROVAL-PROTECTED-RUNTIME-GATED", f"{item.get('approval_id', '<unknown>')}: {action} remains blocked"))
        if action in {"STASH", "RESET", "CLEAN"} and _has_wildcard(paths):
            findings.append(Finding("AIOS-APPROVAL-DESTRUCTIVE-TARGET-MISSING", f"{item.get('approval_id', '<unknown>')}: destructive action needs exact target"))
        if action == "PUSH" and str(item.get("branch", "")).lower() == "main":
            findings.append(Finding("AIOS-APPROVAL-DIRECT-MAIN-PUSH", f"{item.get('approval_id', '<unknown>')}: direct main push is blocked"))
    return findings


def validate_queue(payload: Any, *, now: datetime | None = None) -> list[Finding]:
    current = now or datetime.now(timezone.utc)
    findings: list[Finding] = []
    tasks = _as_list(payload, "tasks")
    seen: set[str] = set()
    running_paths: dict[str, str] = {}
    for item in tasks:
        task_id = str(item.get("task_id", "<unknown>"))
        if task_id in seen:
            findings.append(Finding("AIOS-QUEUE-DUPLICATE-TASK-ID", f"duplicate task_id: {task_id}"))
        seen.add(task_id)
        missing = sorted(QUEUE_FIELDS - set(item))
        if missing:
            findings.append(Finding("AIOS-QUEUE-MISSING-FIELDS", f"{task_id}: {', '.join(missing)}"))
        status = str(item.get("status", ""))
        if status not in QUEUE_STATUSES:
            findings.append(Finding("AIOS-QUEUE-INVALID-STATUS", f"{task_id}: invalid status {status}"))
        if status == "running" and not item.get("owner_worker"):
            findings.append(Finding("AIOS-QUEUE-RUNNING-WITHOUT-OWNER", f"{task_id}: running task has no owner"))
        paths = item.get("protected_paths")
        if not isinstance(paths, list) or not paths:
            findings.append(Finding("AIOS-QUEUE-PROTECTED-PATHS-MISSING", f"{task_id}: protected_paths required"))
        if status == "blocked" and not item.get("next_safe_action"):
            findings.append(Finding("AIOS-QUEUE-BLOCKED-NO-NEXT-ACTION", f"{task_id}: blocked task needs next_safe_action"))
        if str(item.get("mode", "")).upper() == "APPLY" and not item.get("required_approval_id"):
            findings.append(Finding("AIOS-QUEUE-APPLY-WITHOUT-APPROVAL", f"{task_id}: APPLY requires approval"))
        if re.search(r"live|broker|cloud|scheduler", " ".join(map(str, paths or [])), re.I) and status not in {"blocked", "waiting_for_approval"}:
            findings.append(Finding("AIOS-QUEUE-PROTECTED-RUNTIME-NOT-GATED", f"{task_id}: protected runtime task must be gated"))
        heartbeat = _parse_time(item.get("heartbeat_at"))
        if status == "running" and heartbeat and current - heartbeat > timedelta(minutes=60):
            findings.append(Finding("AIOS-QUEUE-STALE-RUNNING", f"{task_id}: stale running heartbeat"))
        if status == "running" and isinstance(paths, list):
            for path in paths:
                text = str(path)
                if text in running_paths:
                    findings.append(Finding("AIOS-QUEUE-PATH-COLLISION", f"{task_id} collides with {running_paths[text]} on {text}"))
                running_paths[text] = task_id
    return findings


def validate_locks(payload: Any, *, now: datetime | None = None) -> list[Finding]:
    current = now or datetime.now(timezone.utc)
    findings: list[Finding] = []
    active_paths: dict[str, str] = {}
    active_ids: set[str] = set()
    for item in _as_list(payload, "locks"):
        lock_id = str(item.get("lock_id", "<unknown>"))
        missing = sorted(LOCK_FIELDS - set(item))
        if missing:
            findings.append(Finding("AIOS-LOCK-MISSING-FIELDS", f"{lock_id}: {', '.join(missing)}"))
        status = str(item.get("status", ""))
        if status == "active":
            if lock_id in active_ids:
                findings.append(Finding("AIOS-LOCK-DUPLICATE-ACTIVE", f"duplicate active lock: {lock_id}"))
            active_ids.add(lock_id)
            expires = _parse_time(item.get("expires_at"))
            if expires and expires <= current:
                findings.append(Finding("AIOS-LOCK-STALE-ACTIVE", f"{lock_id}: stale active lock"))
            for path in item.get("protected_paths") or []:
                text = str(path)
                if text in active_paths:
                    findings.append(Finding("AIOS-LOCK-PATH-COLLISION", f"{lock_id} collides with {active_paths[text]} on {text}"))
                active_paths[text] = lock_id
        worker_type = str(item.get("worker_type", ""))
        allowed = {str(value).upper() for value in item.get("allowed_actions") or []}
        if worker_type not in {"ChatGPT supervisor/planner", "Codex CLI local executor", "Claude Code optional reviewer/branch worker", "OpenAI/Codex app review/remote worker", "GitHub PR/checks layer", "Anthony approval authority"} and "APPLY" in allowed:
            findings.append(Finding("AIOS-LOCK-UNKNOWN-WORKER-APPLY", f"{lock_id}: unknown worker cannot hold APPLY"))
        if "approval authority" in worker_type.lower() and str(item.get("worker_id", "")).lower() != "anthony":
            findings.append(Finding("AIOS-LOCK-WORKER-CLAIMS-APPROVAL", f"{lock_id}: non-Anthony worker claims approval authority"))
        if _has_wildcard(item.get("protected_paths")):
            findings.append(Finding("AIOS-LOCK-BROAD-ROOT", f"{lock_id}: broad repo-root lock is blocked"))
        if PROTECTED_ACTIONS & allowed and not item.get("next_safe_action"):
            findings.append(Finding("AIOS-LOCK-PROTECTED-ACTION-NO-NEXT-ACTION", f"{lock_id}: protected grant needs next_safe_action"))
    return findings


def score_readiness(evidence: dict[str, bool]) -> dict[str, Any]:
    total_weight = sum(WEEKEND_WEIGHTS.values())
    earned = sum(weight for key, weight in WEEKEND_WEIGHTS.items() if evidence.get(key) is True)
    weekend = round((earned / total_weight) * 100, 1)
    scheduler_required = [
        "generated_output_clean", "tier0_watchdog", "tier1_restart_safety", "atomic_state_safety",
        "approval_queue_locks", "ci_hard_blockers", "resource_endurance", "live_sos_last_mile",
        "supervised_24h_run",
    ]
    scheduler_allowed = all(evidence.get(key) is True for key in scheduler_required) and not evidence.get("broker_live_cloud_enabled", False)
    return {
        "scheduler_allowed": scheduler_allowed,
        "overall_aios_score": max(64.0, min(74.0, weekend - 3.0)),
        "weekend_ready_score": weekend,
        "full_sos_only_score": 40.0 if evidence.get("live_sos_last_mile") else 38.0,
        "scheduler_safe_score": 100.0 if scheduler_allowed else 0.0,
        "blockers": [key for key in scheduler_required if evidence.get(key) is not True],
        "evidence_paths": evidence.get("evidence_paths", []),
        "next_required_lane": "live SOS last-mile proof and supervised run ladder" if not scheduler_allowed else "operator scheduler approval gate",
    }


def validate_readiness(payload: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    score = score_readiness(payload.get("evidence", {}))
    if score["scheduler_allowed"] and score["blockers"]:
        findings.append(Finding("AIOS-READINESS-SCHEDULER-BLOCKERS", "scheduler_allowed cannot be true with blockers"))
    if payload.get("scheduler_requested") is True and not score["scheduler_allowed"]:
        findings.append(Finding("AIOS-READINESS-SCHEDULER-BLOCKED", "scheduler remains blocked until all gates pass"))
    return findings


def _sample_payloads() -> dict[str, Any]:
    future = "2099-01-01T00:00:00Z"
    return {
        "approval": {"approval_id": "APPROVAL-SAMPLE-001", "created_at": "2026-06-08T00:00:00Z", "expires_at": future, "requested_by_worker": "Codex CLI local executor", "requested_action": "DRY_RUN", "action_scope": "validator sample", "protected_paths": ["automation/validators/"], "risk_flags": [], "approval_status": "approved", "apply_packet_preparation_approved": False, "apply_execution_approved": False, "operator_authority_marker": "Anthony", "allowed_actions": ["DRY_RUN"], "disallowed_actions": ["SCHEDULER", "LIVE_SOS", "BROKER"], "evidence_links": [], "next_safe_action": "run validators"},
        "queue": {"tasks": [{"task_id": "QUEUE-SAMPLE-001", "title": "sample", "lane": "weekend-ready", "status": "blocked", "priority": 1, "created_at": "2026-06-08T00:00:00Z", "updated_at": "2026-06-08T00:00:00Z", "owner_worker": "", "allowed_workers": ["Codex CLI local executor"], "branch": "feature/weekend-ready-gap-closure-one-packet-v1", "pr_number": None, "protected_paths": ["automation/validators/"], "required_approval_id": "", "lock_id": "", "validation_contract": ["python -m pytest"], "output_contract": "local report", "blocked_reason": "sample blocked state", "next_safe_action": "operator review", "completion_evidence": [], "sos_policy": "local evidence only"}]},
        "locks": {"locks": [{"lock_id": "LOCK-SAMPLE-001", "worker_id": "codex-cli", "worker_type": "Codex CLI local executor", "lane": "weekend-ready", "task_id": "QUEUE-SAMPLE-001", "branch": "feature/weekend-ready-gap-closure-one-packet-v1", "pr_number": None, "protected_paths": ["automation/validators/"], "acquired_at": "2026-06-08T00:00:00Z", "expires_at": future, "heartbeat_at": "2026-06-08T00:00:00Z", "status": "active", "allowed_actions": ["DRY_RUN"], "disallowed_actions": ["SCHEDULER", "LIVE_SOS", "BROKER"], "next_safe_action": "finish validation"}]},
        "readiness": {"scheduler_requested": False, "evidence": {"generated_output_clean": True, "tier0_watchdog": True, "operator_relief_one_shot": True, "worker_dispatcher_control_plane": False, "tier1_restart_safety": True, "atomic_state_safety": True, "approval_queue_locks": True, "ci_hard_blockers": True, "resource_endurance": False, "live_sos_last_mile": False, "supervised_24h_run": False}},
    }


def _emit(name: str, findings: list[Finding]) -> dict[str, Any]:
    return {"name": name, "status": "PASS" if not findings else "FAIL", "findings": [asdict(item) for item in findings]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AI_OS weekend-readiness control gates.")
    parser.add_argument("--sample-check", action="store_true")
    parser.add_argument("--approval-json")
    parser.add_argument("--queue-json")
    parser.add_argument("--lock-json")
    parser.add_argument("--readiness-json")
    args = parser.parse_args()

    samples = _sample_payloads()
    results: list[dict[str, Any]] = []
    if args.sample_check:
        results.extend([
            _emit("approval", validate_approvals(samples["approval"])),
            _emit("queue", validate_queue(samples["queue"])),
            _emit("locks", validate_locks(samples["locks"])),
            _emit("readiness", validate_readiness(samples["readiness"])),
        ])
    for name, path, fn in [
        ("approval", args.approval_json, validate_approvals),
        ("queue", args.queue_json, validate_queue),
        ("locks", args.lock_json, validate_locks),
        ("readiness", args.readiness_json, validate_readiness),
    ]:
        if path:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            results.append(_emit(name, fn(payload)))
    status = "PASS" if results and all(item["status"] == "PASS" for item in results) else "FAIL"
    print(json.dumps({"validator": "aios_weekend_readiness_validator", "status": status, "results": results}, indent=2, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
