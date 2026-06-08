from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUSES = {
    "READY",
    "DRY_RUN_ONLY",
    "WAITING_APPROVAL",
    "BLOCKED_BY_LOCK",
    "BLOCKED_BY_PR_DEPENDENCY",
    "BLOCKED_BY_PROTECTED_PATH",
    "BLOCKED_BY_COLLISION",
    "HISTORICAL_REFERENCE",
    "COMPLETE_OR_SUPERSEDED",
    "REVIEW_REQUIRED",
}
SURFACE_CONTRACT_STATUSES = {
    "ACTIVE_CONTRACT",
    "HISTORICAL_REFERENCE",
    "EVIDENCE_ONLY",
    "COMPLETED_RECORD",
    "EMPTY_ACTIVE_REGISTRY",
    "PROPOSED_BACKLOG",
    "GENERATED_OUTPUT",
    "UNKNOWN",
    "MISSING",
    "MALFORMED",
    "REVIEW_REQUIRED",
}
WALKIE_EVENT_TYPES = {
    "DISPATCH_READY",
    "DRY_RUN_ONLY",
    "WAITING_APPROVAL",
    "LOCK_COLLISION",
    "PR_DEPENDENCY_CHANGED",
    "PROTECTED_PATH_BLOCKED",
    "QUEUE_STATE_UNKNOWN",
    "APPROVAL_STATE_UNKNOWN",
    "NO_SAFE_LANE_FOUND",
    "SOS_CANDIDATE",
    "REVIEW_REQUIRED",
}
WALKIE_SEVERITIES = {"INFO", "NOTICE", "ACTION_REQUIRED", "SAFETY_BLOCK", "SOS_CANDIDATE"}
PR_CLASSIFICATIONS = {
    "PR_READY_FOR_REVIEW",
    "PR_MERGED_BASELINE",
    "PR_OPEN_DEPENDENCY",
    "PR_DRAFT_OR_SUPERSEDED",
    "PR_BLOCKED_BY_CONFLICT",
    "PR_REVIEW_REQUIRED",
    "PR_UNKNOWN",
}
PACKET_DRAFT_STATUSES = {
    "DRAFT_READY_FOR_OPERATOR_REVIEW",
    "DRAFT_BLOCKED_WAITING_APPROVAL",
    "DRAFT_BLOCKED_BY_LOCK",
    "DRAFT_BLOCKED_BY_PR_DEPENDENCY",
    "DRAFT_BLOCKED_BY_PROTECTED_PATH",
    "DRAFT_REVIEW_REQUIRED",
    "DRAFT_NOT_CREATED",
}
COMPLETE_STATES = {"complete", "completed", "done", "superseded", "archived_reference", "closed"}
WAITING_APPROVAL_STATES = {"awaiting_approval", "waiting_approval", "waiting_for_approval", "pending_review"}
ACTIVE_STATES = {"active", "ready", "queued", "assigned", "running", "dry_run_running", "ready_for_dry_run"}
APPLY_MODES = {"apply", "local_apply", "apply_running", "ready_for_apply"}
PROTECTED_TERMS = ("broker", "live_trading", "oanda", "webhooks", "secrets", ".env", "scheduler", "live_sos", "cloud")
DEFAULT_REPORT_PATH = "Reports/generated/dispatcher/assignment_executor_preview.json"


@dataclass
class Candidate:
    task_id: str
    source: str
    title: str
    lane: str
    assigned_worker: str | None
    status: str
    mode: str
    protected_paths: list[str]
    required_approval: str | None
    validator_chain: list[str]
    next_safe_action: str
    blockers: list[str] = field(default_factory=list)
    pr_dependencies: list[str] = field(default_factory=list)


@dataclass
class Decision:
    task_id: str
    source: str
    decision: str
    reasons: list[str]
    assigned_worker: str | None
    lane: str
    next_safe_action: str


@dataclass
class WalkieEvent:
    walkie_event_id: str
    event_type: str
    severity: str
    route_to: list[str]
    source: str
    reason: str
    candidate_id: str | None
    lane: str | None
    requires_anthony: bool
    safe_next_action: str
    blocked_actions: list[str]
    evidence: dict[str, Any]
    zero_external_wake_confirmation: bool
    zero_worker_launch_confirmation: bool


@dataclass
class PacketDraft:
    packet_id: str
    title: str
    status: str
    mode: str
    lane: str
    worker_identity: str
    supervisor_identity: str
    approval_authority: str
    baseline: list[str]
    mission: str
    allowed_paths: list[str]
    forbidden_paths: list[str]
    read_first: list[str]
    objectives: list[str]
    validation: list[str]
    stop_point: str
    safety_limits: list[str]
    expected_untracked_backlog: list[str]
    final_report_format: list[str]
    zero_launch_confirmation: dict[str, bool]
    not_approval_notice: str
    not_executable_until_operator_approval: bool
    source_dispatch_decision_id: str
    source_candidate_id: str
    source_walkie_event_ids: list[str]
    source_pr_dependency_status: str
    source_lock_status: str
    source_approval_status: str
    source_collision_status: str
    apply_approved: bool
    merge_approved: bool
    push_approved: bool
    direct_anthony_wake_approved: bool
    worker_launch_approved: bool
    draft_text: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def zero_launch_confirmation() -> dict[str, bool]:
    return {
        "zero_workers_launched": True,
        "zero_scheduler_started": True,
        "zero_night_supervisor_started": True,
        "zero_sos_armed": True,
        "zero_adb_calls": True,
        "zero_notifications_sent": True,
        "zero_broker_cloud_live_trading": True,
    }


def blocked_event_actions() -> list[str]:
    return [
        "direct_anthony_wake",
        "worker_launch",
        "scheduler_start",
        "night_supervisor_start",
        "live_sos_arm_or_send",
        "adb_call",
        "notification_send",
        "broker_cloud_live_trading",
        "secret_handling",
    ]


def draft_forbidden_actions() -> list[str]:
    return [
        "APPLY execution",
        "commit",
        "push",
        "merge",
        "worker launch",
        "scheduler start",
        "Night Supervisor start",
        "SOS send or arm",
        "ADB call",
        "notification send",
        "broker execution",
        "cloud deployment",
        "live trading",
        "secret handling",
        "cleanup command",
        "stash mutation",
        "force push",
        "main push",
    ]


def read_json_file(path: Path) -> tuple[str, Any | None, str | None]:
    if not path.exists():
        return "MISSING", None, None
    try:
        return "PRESENT", json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as exc:
        return "MALFORMED", None, f"{exc.__class__.__name__}: {exc}"


def _contract_status(value: str) -> str:
    return value if value in SURFACE_CONTRACT_STATUSES else "REVIEW_REQUIRED"


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _norm(text: Any) -> str:
    return str(text or "").strip()


def _lower(text: Any) -> str:
    return _norm(text).lower()


def _path_overlaps(left: list[str], right: list[str]) -> bool:
    normalized_left = [item.replace("\\", "/").rstrip("/") for item in left if item]
    normalized_right = [item.replace("\\", "/").rstrip("/") for item in right if item]
    for left_item in normalized_left:
        for right_item in normalized_right:
            if left_item == right_item or left_item.startswith(f"{right_item}/") or right_item.startswith(f"{left_item}/"):
                return True
    return False


def _protected_path(paths: list[str]) -> bool:
    joined = " ".join(paths).lower()
    return any(term in joined for term in PROTECTED_TERMS)


def _extract_paths(packet: dict[str, Any]) -> list[str]:
    for key in ("protected_paths", "allowed_paths", "related_files"):
        values = packet.get(key)
        if isinstance(values, list) and values:
            return [str(item) for item in values]
    return []


def _extract_lock_paths(lock: dict[str, Any]) -> list[str]:
    paths: list[str] = []
    for key in ("protected_paths", "paths", "allowed_paths", "locked_paths"):
        values = lock.get(key)
        if isinstance(values, list):
            paths.extend(str(item) for item in values)
    return paths


def _extract_pr_changed_paths(record: dict[str, Any]) -> list[str]:
    values = record.get("changed_paths") or record.get("files") or record.get("changedFiles")
    if isinstance(values, list):
        return [str(item) for item in values]
    return []


def _normalize_pr_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "pr_number": record.get("pr_number") or record.get("number"),
        "title": _norm(record.get("title")),
        "state": _lower(record.get("state") or ("open" if record.get("number") else "")),
        "draft": bool(record.get("draft") if "draft" in record else record.get("isDraft", False)),
        "merged": bool(record.get("merged", False)),
        "merge_state": _lower(record.get("merge_state") or record.get("mergeStateStatus")),
        "base_branch": _norm(record.get("base_branch") or record.get("baseRefName")),
        "head_branch": _norm(record.get("head_branch") or record.get("headRefName")),
        "head_sha": _norm(record.get("head_sha") or record.get("headRefOid")),
        "changed_paths": _extract_pr_changed_paths(record),
        "labels": [str(label).lower() for label in _as_list(record.get("labels"))],
        "updated_at": _norm(record.get("updated_at") or record.get("updatedAt")),
        "dependency_notes": _norm(record.get("dependency_notes")),
    }


def classify_pr_record(record: dict[str, Any]) -> str:
    state = _lower(record.get("state"))
    merge_state = _lower(record.get("merge_state"))
    labels = {str(label).lower() for label in _as_list(record.get("labels"))}
    title = _lower(record.get("title"))
    if record.get("merged") is True:
        return "PR_MERGED_BASELINE"
    if record.get("draft") is True or "superseded" in labels or "draft" in title or "superseded" in title:
        return "PR_DRAFT_OR_SUPERSEDED"
    if state in {"closed", "closed_unmerged"}:
        return "PR_DRAFT_OR_SUPERSEDED"
    if merge_state in {"dirty", "blocked", "conflicting", "has_hooks", "unstable"}:
        return "PR_BLOCKED_BY_CONFLICT"
    if state in {"", "unknown"} and merge_state in {"", "unknown"}:
        return "PR_UNKNOWN"
    if state in {"open", "opened"} and merge_state in {"clean", "has_hooks", "unstable", ""}:
        return "PR_READY_FOR_REVIEW" if merge_state == "clean" else "PR_REVIEW_REQUIRED"
    if merge_state in {"unknown", "behind"}:
        return "PR_REVIEW_REQUIRED"
    return "PR_REVIEW_REQUIRED"


def _load_pr_fixture(path: Path) -> dict[str, Any]:
    status, payload, error = read_json_file(path)
    if status == "MISSING":
        return {
            "status": "UNKNOWN",
            "source": "fixture",
            "reason": f"PR backlog fixture missing: {path.as_posix()}",
            "open_prs": [],
            "pr_records": [],
        }
    if status == "MALFORMED":
        return {
            "status": "MALFORMED",
            "source": "fixture",
            "reason": error or "PR backlog fixture malformed",
            "open_prs": [],
            "pr_records": [],
        }
    records = payload.get("prs") if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        return {
            "status": "MALFORMED",
            "source": "fixture",
            "reason": "PR backlog fixture must be a list or object with prs list",
            "open_prs": [],
            "pr_records": [],
        }
    normalized = [_normalize_pr_record(record) for record in records if isinstance(record, dict)]
    return {
        "status": "PRESENT",
        "source": "fixture",
        "reason": "local PR backlog fixture loaded",
        "open_pr_count": len([record for record in normalized if record["state"] in {"open", "opened"}]),
        "open_prs": normalized,
        "pr_records": normalized,
    }


def load_pr_backlog(repo_root: Path, *, allow_github: bool, pr_backlog_fixture: Path | None = None) -> dict[str, Any]:
    if pr_backlog_fixture is not None:
        return _load_pr_fixture(pr_backlog_fixture)
    if not allow_github:
        return {
            "status": "UNKNOWN",
            "source": "none",
            "reason": "PR backlog fixture not provided and live GitHub inspection disabled.",
            "open_prs": [],
            "pr_records": [],
        }
    result = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--limit",
            "30",
            "--json",
            "number,title,headRefName,baseRefName,isDraft,mergeStateStatus,updatedAt,url",
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return {"status": "UNKNOWN", "reason": result.stderr.strip() or "gh pr list failed", "open_prs": []}
    try:
        prs = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return {"status": "UNKNOWN", "reason": f"GitHub PR JSON malformed: {exc}", "open_prs": []}
    normalized = [_normalize_pr_record(record) for record in prs if isinstance(record, dict)]
    return {"status": "PRESENT", "source": "github_cli", "open_pr_count": len(normalized), "open_prs": normalized, "pr_records": normalized}


def load_state(repo_root: Path, *, allow_github: bool = False, pr_backlog_fixture: Path | None = None) -> dict[str, Any]:
    paths = {
        "worker_registry": repo_root / "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json",
        "worker_inbox": repo_root / "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json",
        "historical_queue": repo_root / "automation/orchestration/queue/DISPATCHER_QUEUE.json",
        "lock_registry": repo_root / "automation/orchestration/locks/FILE_LOCK_REGISTRY.json",
        "approval_inbox": repo_root / "automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json",
        "apply_gate": repo_root / "automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json",
    }
    state: dict[str, Any] = {}
    for key, path in paths.items():
        status, payload, error = read_json_file(path)
        state[key] = {"path": path.as_posix(), "status": status, "payload": payload, "error": error}
    active_dir = repo_root / "automation/orchestration/work_packets/active"
    packets: list[dict[str, Any]] = []
    packet_errors: list[str] = []
    if active_dir.exists():
        for path in sorted(active_dir.glob("*.json")):
            status, payload, error = read_json_file(path)
            if status == "PRESENT" and isinstance(payload, dict):
                payload["_source_path"] = path.as_posix()
                packets.append(payload)
            else:
                packet_errors.append(f"{path.as_posix()}: {status} {error or ''}".strip())
    state["active_work_packets"] = {
        "path": active_dir.as_posix(),
        "status": "PRESENT" if active_dir.exists() else "MISSING",
        "packets": packets,
        "errors": packet_errors,
    }
    proposed_dir = repo_root / "automation/orchestration/work_packets/proposed"
    state["proposed_backlog"] = {
        "path": proposed_dir.as_posix(),
        "status": "PRESENT" if proposed_dir.exists() else "MISSING",
        "contract_status": "PROPOSED_BACKLOG" if proposed_dir.exists() else "MISSING",
        "note": "Proposed backlog is not active queue input without explicit approval.",
    }
    state["pr_backlog"] = load_pr_backlog(repo_root, allow_github=allow_github, pr_backlog_fixture=pr_backlog_fixture)
    return state


def summarize_state(state: dict[str, Any]) -> dict[str, Any]:
    workers_payload = state["worker_registry"].get("payload") or {}
    inbox_payload = state["worker_inbox"].get("payload") or {}
    queue_payload = state["historical_queue"].get("payload") or {}
    locks_payload = state["lock_registry"].get("payload") or {}
    approval_payload = state["approval_inbox"].get("payload") or {}
    apply_payload = state["apply_gate"].get("payload") or {}
    locks = _as_list(locks_payload.get("locks") if isinstance(locks_payload, dict) else [])
    lock_paths = [
        path
        for lock in locks
        if isinstance(lock, dict)
        for path in _extract_lock_paths(lock)
    ]
    global_blocked_paths = _as_list(locks_payload.get("global_blocked_paths") if isinstance(locks_payload, dict) else [])
    queue_status = _norm(queue_payload.get("status") if isinstance(queue_payload, dict) else "")
    approval_status = _norm(approval_payload.get("approval_status") if isinstance(approval_payload, dict) else "")
    apply_status = _norm(apply_payload.get("approval_status") if isinstance(apply_payload, dict) else "")
    historical_contract = "HISTORICAL_REFERENCE" if queue_status.upper() == "HISTORICAL" else "REVIEW_REQUIRED"
    active_packets_status = state["active_work_packets"]["status"]
    active_packet_contract = "ACTIVE_CONTRACT" if active_packets_status == "PRESENT" else active_packets_status
    lock_surface_status = state["lock_registry"]["status"]
    if lock_surface_status == "PRESENT" and not locks:
        lock_contract = "EMPTY_ACTIVE_REGISTRY"
    elif lock_surface_status == "PRESENT":
        lock_contract = "ACTIVE_CONTRACT"
    elif lock_surface_status in {"MISSING", "MALFORMED"}:
        lock_contract = lock_surface_status
    else:
        lock_contract = "REVIEW_REQUIRED"
    approval_contract = "EVIDENCE_ONLY" if state["approval_inbox"]["status"] == "PRESENT" else state["approval_inbox"]["status"]
    worker_inbox_status = state["worker_inbox"]["status"]
    return {
        "worker_state": {
            "surface_status": state["worker_registry"]["status"],
            "worker_count": len(_as_list(workers_payload.get("workers") if isinstance(workers_payload, dict) else [])),
            "worker_registry_contract": _contract_status("ACTIVE_CONTRACT" if state["worker_registry"]["status"] == "PRESENT" else state["worker_registry"]["status"]),
            "worker_inbox_contract": _contract_status("ACTIVE_CONTRACT" if worker_inbox_status == "PRESENT" else worker_inbox_status),
        },
        "queue_state": {
            "historical_queue_status": queue_status or state["historical_queue"]["status"],
            "historical_queue_treatment": historical_contract,
            "active_work_packet_contract": _contract_status(active_packet_contract),
            "active_work_packet_count": len(state["active_work_packets"]["packets"]),
            "proposed_backlog_contract": state["proposed_backlog"]["contract_status"],
        },
        "lock_state": {
            "surface_status": state["lock_registry"]["status"],
            "active_lock_count": len([lock for lock in locks if isinstance(lock, dict)]),
            "classification": "NO_ACTIVE_LOCKS" if lock_contract == "EMPTY_ACTIVE_REGISTRY" else lock_contract,
            "contract_status": _contract_status(lock_contract),
            "global_blocked_paths": [str(path) for path in global_blocked_paths],
            "active_lock_paths": lock_paths,
        },
        "approval_state": {
            "inbox_status": approval_status or state["approval_inbox"]["status"],
            "apply_gate_status": apply_status or state["apply_gate"]["status"],
            "approval_contract": _contract_status(approval_contract),
            "apply_gate_contract": "EVIDENCE_ONLY" if state["apply_gate"]["status"] == "PRESENT" else state["apply_gate"]["status"],
            "future_apply_approved": bool(
                isinstance(apply_payload, dict)
                and apply_payload.get("approval_status") == "approved_for_apply"
                and apply_payload.get("approved_by_human") is True
            ),
            "authority_note": "Completed authority-repair records are evidence only, not future APPLY approval.",
        },
        "pr_backlog_state": state["pr_backlog"],
    }


def classify_pr_backlog(pr_backlog: dict[str, Any]) -> dict[str, Any]:
    records = [_normalize_pr_record(record) for record in _as_list(pr_backlog.get("pr_records") or pr_backlog.get("open_prs")) if isinstance(record, dict)]
    classifications = [
        {
            "pr_number": record.get("pr_number"),
            "title": record.get("title"),
            "head_branch": record.get("head_branch"),
            "changed_paths": record.get("changed_paths", []),
            "classification": classify_pr_record(record),
            "merge_approved": False,
            "apply_approved": False,
            "worker_launch_approved": False,
        }
        for record in records
    ]
    status = pr_backlog.get("status", "UNKNOWN")
    return {
        "status": status,
        "source": pr_backlog.get("source", "unknown"),
        "pr_records_read": len(records),
        "pr_classifications": classifications,
        "pr_backlog_unknown_reason": pr_backlog.get("reason") if status in {"UNKNOWN", "MALFORMED"} else None,
        "fixture_mode_deterministic": pr_backlog.get("source") == "fixture" or status == "UNKNOWN",
        "merge_approved": False,
        "apply_approved": False,
        "worker_launch_approved": False,
    }


def normalize_candidates(state: dict[str, Any]) -> list[Candidate]:
    candidates: list[Candidate] = []
    for packet in state["active_work_packets"]["packets"]:
        packet_id = _norm(packet.get("packet_id") or Path(_norm(packet.get("_source_path"))).stem)
        status = _lower(packet.get("status"))
        candidates.append(
            Candidate(
                task_id=packet_id,
                source="active_work_packet",
                title=_norm(packet.get("title") or packet.get("intent") or packet_id),
                lane=_norm(packet.get("owner_lane") or packet.get("lane") or "UNKNOWN"),
                assigned_worker=_norm(packet.get("assigned_worker")) or None,
                status=status,
                mode=_lower(packet.get("mode") or packet.get("approved_mode") or "dry_run"),
                protected_paths=_extract_paths(packet),
                required_approval=_norm(packet.get("required_approval") or packet.get("approval_id")) or None,
                validator_chain=[_norm(packet.get("validator"))] if packet.get("validator") else [],
                next_safe_action=_norm(packet.get("next_action") or packet.get("next_safe_action") or "Review packet state before dispatch."),
                blockers=[str(item) for item in _as_list(packet.get("blocked_by"))],
            )
        )
    inbox_payload = state["worker_inbox"].get("payload") or {}
    for item in _as_list(inbox_payload.get("items") if isinstance(inbox_payload, dict) else []):
        item_id = _norm(item.get("id") or item.get("task_id") or item.get("worker_id") or "worker_inbox_item")
        candidates.append(
            Candidate(
                task_id=item_id,
                source="worker_inbox",
                title=_norm(item.get("task") or item.get("title") or item_id),
                lane=_norm(item.get("worker_type") or item.get("lane") or "worker_inbox"),
                assigned_worker=_norm(item.get("worker_id")) or None,
                status=_lower(item.get("current_status") or item.get("status")),
                mode=_lower(item.get("mode") or "dry_run"),
                protected_paths=[],
                required_approval=_norm(item.get("approval_id")) or None,
                validator_chain=[],
                next_safe_action=_norm(item.get("state_note") or item.get("next_safe_action") or "Review inbox item before dispatch."),
            )
        )
    queue_payload = state["historical_queue"].get("payload") or {}
    if isinstance(queue_payload, dict) and _norm(queue_payload.get("status")).upper() == "HISTORICAL":
        for item in _as_list(queue_payload.get("items")):
            packet_id = _norm(item.get("packet_id") or item.get("title") or "historical_queue_item")
            candidates.append(
                Candidate(
                    task_id=packet_id,
                    source="historical_dispatcher_queue",
                    title=_norm(item.get("title") or packet_id),
                    lane=_norm(item.get("lane") or "historical"),
                    assigned_worker=_norm(item.get("assigned_worker")) or None,
                    status="historical",
                    mode="historical",
                    protected_paths=[],
                    required_approval=None,
                    validator_chain=[],
                    next_safe_action="Historical reference only. Do not dispatch from DISPATCHER_QUEUE.json.",
                )
            )
    return candidates


def build_pr_dependency_findings(candidates: list[Candidate], pr_backlog_report: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    active_candidates = [
        candidate
        for candidate in candidates
        if candidate.status in ACTIVE_STATES or candidate.status in WAITING_APPROVAL_STATES
    ]
    for candidate in active_candidates:
        candidate_paths = candidate.protected_paths
        if not candidate_paths:
            continue
        for pr_record in pr_backlog_report.get("pr_classifications", []):
            pr_paths = [str(path) for path in _as_list(pr_record.get("changed_paths"))]
            if not pr_paths or not _path_overlaps(candidate_paths, pr_paths):
                continue
            classification = pr_record.get("classification")
            if classification == "PR_MERGED_BASELINE":
                finding = "PR_MERGED_BASELINE"
            elif classification in {"PR_READY_FOR_REVIEW", "PR_OPEN_DEPENDENCY"}:
                finding = "PR_OPEN_DEPENDENCY"
            elif classification == "PR_BLOCKED_BY_CONFLICT":
                finding = "PR_BLOCKED_BY_CONFLICT"
            else:
                finding = "PR_REVIEW_REQUIRED"
            findings.append(
                {
                    "candidate_id": candidate.task_id,
                    "candidate_paths": candidate_paths,
                    "pr_number": pr_record.get("pr_number"),
                    "pr_title": pr_record.get("title"),
                    "pr_changed_paths": pr_paths,
                    "pr_classification": classification,
                    "dependency_classification": finding,
                    "merge_approved": False,
                    "apply_approved": False,
                    "worker_launch_approved": False,
                }
            )
    return findings


def classify_candidates(candidates: list[Candidate], state_summary: dict[str, Any], pr_backlog: dict[str, Any]) -> tuple[list[Decision], list[dict[str, Any]]]:
    decisions: list[Decision] = []
    collisions: list[dict[str, Any]] = []
    active_candidates = [candidate for candidate in candidates if candidate.status in ACTIVE_STATES or candidate.status in WAITING_APPROVAL_STATES]

    for index, left in enumerate(active_candidates):
        for right in active_candidates[index + 1 :]:
            if left.protected_paths and right.protected_paths and _path_overlaps(left.protected_paths, right.protected_paths):
                collisions.append({"left": left.task_id, "right": right.task_id, "reason": "protected_path_overlap"})

    pr_backlog_report = classify_pr_backlog(pr_backlog)
    pr_dependency_findings = build_pr_dependency_findings(candidates, pr_backlog_report)
    for candidate in candidates:
        reasons: list[str] = []
        decision = "REVIEW_REQUIRED"
        status = candidate.status
        if candidate.source == "historical_dispatcher_queue" or status == "historical":
            decision = "HISTORICAL_REFERENCE"
            reasons.append("historical_surface_not_active_queue")
        elif status in COMPLETE_STATES:
            decision = "COMPLETE_OR_SUPERSEDED"
            reasons.append(f"candidate_status_{status}")
        elif status in WAITING_APPROVAL_STATES:
            decision = "WAITING_APPROVAL"
            reasons.append("approval_required_or_pending")
        elif candidate.protected_paths and _path_overlaps(candidate.protected_paths, state_summary.get("lock_state", {}).get("active_lock_paths", [])):
            decision = "BLOCKED_BY_LOCK"
            reasons.append("active_lock_path_overlap")
        elif candidate.required_approval and state_summary["approval_state"]["future_apply_approved"] is False:
            decision = "WAITING_APPROVAL"
            reasons.append("required_approval_without_exact_future_apply_approval")
        elif candidate.mode in APPLY_MODES and state_summary["approval_state"]["future_apply_approved"] is False:
            decision = "WAITING_APPROVAL"
            reasons.append("apply_mode_without_exact_future_apply_approval")
        elif candidate.blockers:
            decision = "REVIEW_REQUIRED"
            reasons.extend([f"blocked_by:{item}" for item in candidate.blockers])
        elif _protected_path(candidate.protected_paths):
            decision = "BLOCKED_BY_PROTECTED_PATH"
            reasons.append("protected_runtime_or_forbidden_path")
        elif any(candidate.task_id in f"{collision['left']} {collision['right']}" for collision in collisions):
            decision = "BLOCKED_BY_COLLISION"
            reasons.append("candidate_collides_with_active_candidate")
        elif any(finding["candidate_id"] == candidate.task_id and finding["dependency_classification"] != "PR_MERGED_BASELINE" for finding in pr_dependency_findings):
            decision = "BLOCKED_BY_PR_DEPENDENCY"
            reasons.append("pr_changed_paths_overlap_candidate_paths")
        elif status in ACTIVE_STATES and state_summary["approval_state"]["future_apply_approved"] is False:
            decision = "DRY_RUN_ONLY"
            reasons.append("no_future_apply_approval")
        elif status in ACTIVE_STATES:
            decision = "READY"
            reasons.append("candidate_status_ready")
        elif state_summary["approval_state"]["future_apply_approved"] is False:
            decision = "DRY_RUN_ONLY"
            reasons.append("no_future_apply_approval")
        if decision not in STATUSES:
            decision = "REVIEW_REQUIRED"
            reasons.append("unknown_status_mapping")
        decisions.append(
            Decision(
                task_id=candidate.task_id,
                source=candidate.source,
                decision=decision,
                reasons=reasons,
                assigned_worker=candidate.assigned_worker,
                lane=candidate.lane,
                next_safe_action=candidate.next_safe_action,
            )
        )
    return decisions, collisions


def build_dispatch_packet_preview(decision: Decision) -> dict[str, Any]:
    return {
        "packet_preview_id": f"DISPATCH-PREVIEW-{decision.task_id}",
        "mode": "DRY_RUN",
        "lane": decision.lane,
        "assigned_worker": decision.assigned_worker,
        "decision": decision.decision,
        "contains_execution_token": False,
        "apply_execution_approved": False,
        "worker_launch_approved": False,
        "approval_authority": "Anthony",
        "validator_pass_is_evidence_only": True,
        "stop_point": "Stop after dispatch preview. Do not launch workers.",
        "next_safe_action": decision.next_safe_action,
    }


def _draft_status_for_decision(decision: Decision, related_walkie_events: list[WalkieEvent]) -> str:
    if decision.decision in {"READY", "DRY_RUN_ONLY"}:
        if any(event.severity in {"SAFETY_BLOCK", "SOS_CANDIDATE"} for event in related_walkie_events):
            return "DRAFT_REVIEW_REQUIRED"
        return "DRAFT_READY_FOR_OPERATOR_REVIEW"
    if decision.decision == "WAITING_APPROVAL":
        return "DRAFT_BLOCKED_WAITING_APPROVAL"
    if decision.decision == "BLOCKED_BY_LOCK":
        return "DRAFT_BLOCKED_BY_LOCK"
    if decision.decision == "BLOCKED_BY_PR_DEPENDENCY":
        return "DRAFT_BLOCKED_BY_PR_DEPENDENCY"
    if decision.decision == "BLOCKED_BY_PROTECTED_PATH":
        return "DRAFT_BLOCKED_BY_PROTECTED_PATH"
    if decision.decision in {"REVIEW_REQUIRED", "BLOCKED_BY_COLLISION"}:
        return "DRAFT_REVIEW_REQUIRED"
    return "DRAFT_NOT_CREATED"


def _packet_draft_mode(decision: Decision) -> str:
    return "DRY_RUN"


def _source_pr_dependency_status(candidate_id: str, pr_dependency_findings: list[dict[str, Any]]) -> str:
    statuses = [
        str(finding.get("dependency_classification"))
        for finding in pr_dependency_findings
        if finding.get("candidate_id") == candidate_id
    ]
    return ",".join(statuses) if statuses else "PR_UNKNOWN"


def _source_collision_status(candidate_id: str, collisions: list[dict[str, Any]]) -> str:
    for collision in collisions:
        if candidate_id in {collision.get("left"), collision.get("right")}:
            return "COLLISION_PRESENT"
    return "NO_COLLISION_DETECTED"


def _render_packet_draft_text(draft: PacketDraft) -> str:
    lines = [
        "CODEX-ONLY PROMPT",
        "",
        "AI_OS EXECUTION TOKEN: DRAFT_ONLY_NOT_OPERATOR_APPROVAL",
        "",
        "AI_OS BOOTSTRAP REQUIRED",
        "",
        "IDENTITY MARKER:",
        f"Worker identity: {draft.worker_identity}. This is a draft packet only.",
        "",
        "PACKET ID:",
        draft.packet_id,
        "",
        "MODE:",
        draft.mode,
        "",
        "WORKTREE:",
        "C:\\Dev\\Ai.Os",
        "",
        "BRANCH RULE:",
        "Resolve branch after operator approval and read-only preflight.",
        "",
        "MISSION:",
        draft.mission,
        "",
        "READ FIRST:",
        *[f"- {item}" for item in draft.read_first],
        "",
        "ALLOWED PATHS:",
        *[f"- {item}" for item in draft.allowed_paths],
        "",
        "FORBIDDEN PATHS AND ACTIONS:",
        *[f"- {item}" for item in draft.forbidden_paths],
        *[f"- {item}" for item in draft.safety_limits],
        "",
        "VALIDATION:",
        *[f"- {item}" for item in draft.validation],
        "",
        "STOP POINT:",
        draft.stop_point,
        "",
        "FINAL REPORT FORMAT:",
        *[f"- {item}" for item in draft.final_report_format],
        "",
        "DRAFT SAFETY NOTICE:",
        draft.not_approval_notice,
        "This draft is not executable until Anthony approves it.",
        "This draft does not approve APPLY, commit, push, merge, worker launch, scheduler, Night Supervisor, SOS, ADB, broker, cloud, live trading, secrets, cleanup, or stash mutation.",
    ]
    return "\n".join(lines)


def build_packet_draft_for_decision(
    decision: Decision,
    *,
    walkie_events: list[WalkieEvent],
    pr_dependency_findings: list[dict[str, Any]],
    lock_state: dict[str, Any],
    approval_state: dict[str, Any],
    collisions: list[dict[str, Any]],
) -> PacketDraft:
    related_walkie_events = [
        event for event in walkie_events if event.candidate_id in {decision.task_id, None}
    ]
    status = _draft_status_for_decision(decision, related_walkie_events)
    draft = PacketDraft(
        packet_id=f"DRAFT-{decision.task_id}",
        title=f"Dispatcher Next Packet Draft for {decision.task_id}",
        status=status,
        mode=_packet_draft_mode(decision),
        lane=decision.lane,
        worker_identity=decision.assigned_worker or "Codex CLI local executor",
        supervisor_identity="ChatGPT supervisor/planner",
        approval_authority="Anthony",
        baseline=[
            "PR #450 merged Dispatcher Control Plane V1",
            "PR #452 merged Assignment Executor DRY_RUN V1",
            "PR #453 merged active-state contracts V1",
            "PR #454 merged PR backlog fixture ingestion V1",
        ],
        mission=decision.next_safe_action or "Run the dispatcher-selected DRY_RUN lane after operator approval.",
        allowed_paths=["Resolve from source dispatcher candidate before execution."],
        forbidden_paths=[
            "broker/",
            "live_trading/",
            "oanda/",
            "webhooks/",
            "secrets/",
            "api_keys/",
            ".env",
            ".env.*",
        ],
        read_first=[
            "AGENTS.md",
            "README.md",
            "docs/AI_OS/worker_dispatcher/worker_dispatcher_assignment_executor_v1.md",
            "docs/AI_OS/worker_dispatcher/worker_dispatcher_active_state_contracts_v1.md",
            "docs/AI_OS/worker_dispatcher/worker_dispatcher_pr_backlog_fixture_ingestion_v1.md",
        ],
        objectives=[
            "Run read-only preflight.",
            "Confirm current branch and dirty state.",
            "Execute only after Anthony approval.",
            "Stop at report unless a later packet explicitly approves APPLY.",
        ],
        validation=[
            "Run focused tests for changed components.",
            "Run relevant validator sample-checks.",
            "Run git diff --check.",
            "Confirm no live activation behavior was introduced.",
        ],
        stop_point="Stop after DRY_RUN report. Do not APPLY, commit, push, merge, or launch workers.",
        safety_limits=draft_forbidden_actions(),
        expected_untracked_backlog=[
            "Reports/phase_0_to_4_bridge/AIOS_REMOTE_ACCESS_MODEL_NOTE_20260608.md",
            "Reports/phase_0_to_4_bridge/app_service_bridge_v0_remote_overlap_review_20260608.md",
            "automation/orchestration/work_packets/proposed/AIOS-SB-001-APPROVAL-INBOX-SCHEMA-VALIDATOR-DRY-RUN-FIRST.md",
        ],
        final_report_format=[
            "SUMMARY:",
            "VALIDATION:",
            "SAFETY GATES:",
            "STATUS:",
        ],
        zero_launch_confirmation=zero_launch_confirmation(),
        not_approval_notice="Dispatcher draft output is evidence only and does not grant approval.",
        not_executable_until_operator_approval=True,
        source_dispatch_decision_id=f"DECISION-{decision.task_id}",
        source_candidate_id=decision.task_id,
        source_walkie_event_ids=[event.walkie_event_id for event in related_walkie_events],
        source_pr_dependency_status=_source_pr_dependency_status(decision.task_id, pr_dependency_findings),
        source_lock_status=str(lock_state.get("classification") or lock_state.get("contract_status") or "UNKNOWN"),
        source_approval_status=str(approval_state.get("approval_contract") or approval_state.get("inbox_status") or "UNKNOWN"),
        source_collision_status=_source_collision_status(decision.task_id, collisions),
        apply_approved=False,
        merge_approved=False,
        push_approved=False,
        direct_anthony_wake_approved=False,
        worker_launch_approved=False,
        draft_text="",
    )
    draft.draft_text = _render_packet_draft_text(draft)
    return draft


def build_packet_drafts(
    decisions: list[Decision],
    *,
    walkie_events: list[WalkieEvent],
    pr_dependency_findings: list[dict[str, Any]],
    lock_state: dict[str, Any],
    approval_state: dict[str, Any],
    collisions: list[dict[str, Any]],
) -> list[PacketDraft]:
    draftable_statuses = {
        "READY",
        "DRY_RUN_ONLY",
        "WAITING_APPROVAL",
        "BLOCKED_BY_LOCK",
        "BLOCKED_BY_PR_DEPENDENCY",
        "BLOCKED_BY_PROTECTED_PATH",
        "REVIEW_REQUIRED",
        "BLOCKED_BY_COLLISION",
    }
    return [
        build_packet_draft_for_decision(
            decision,
            walkie_events=walkie_events,
            pr_dependency_findings=pr_dependency_findings,
            lock_state=lock_state,
            approval_state=approval_state,
            collisions=collisions,
        )
        for decision in decisions
        if decision.decision in draftable_statuses
    ]


def _walkie_route_for(severity: str) -> list[str]:
    if severity == "INFO":
        return ["dispatcher_report"]
    if severity == "NOTICE":
        return ["night_supervisor_review"]
    if severity == "ACTION_REQUIRED":
        return ["night_supervisor_review", "approval_inbox_evidence"]
    if severity == "SAFETY_BLOCK":
        return ["night_supervisor_review", "watchdog_review"]
    if severity == "SOS_CANDIDATE":
        return ["watchdog_pi5_review"]
    return ["night_supervisor_review"]


def _event_type_for_decision(decision: Decision) -> tuple[str, str, bool]:
    if decision.decision == "READY":
        return "DISPATCH_READY", "NOTICE", False
    if decision.decision == "DRY_RUN_ONLY":
        return "DRY_RUN_ONLY", "INFO", False
    if decision.decision == "WAITING_APPROVAL":
        return "WAITING_APPROVAL", "ACTION_REQUIRED", True
    if decision.decision == "BLOCKED_BY_LOCK":
        return "LOCK_COLLISION", "SAFETY_BLOCK", False
    if decision.decision == "BLOCKED_BY_PR_DEPENDENCY":
        return "PR_DEPENDENCY_CHANGED", "ACTION_REQUIRED", True
    if decision.decision == "BLOCKED_BY_PROTECTED_PATH":
        return "PROTECTED_PATH_BLOCKED", "SAFETY_BLOCK", True
    if decision.decision == "BLOCKED_BY_COLLISION":
        return "LOCK_COLLISION", "SAFETY_BLOCK", False
    if decision.decision == "REVIEW_REQUIRED":
        return "REVIEW_REQUIRED", "ACTION_REQUIRED", True
    return "REVIEW_REQUIRED", "NOTICE", False


def build_walkie_event(
    *,
    event_type: str,
    severity: str,
    source: str,
    reason: str,
    candidate_id: str | None,
    lane: str | None,
    requires_anthony: bool,
    safe_next_action: str,
    evidence: dict[str, Any],
) -> WalkieEvent:
    if event_type not in WALKIE_EVENT_TYPES:
        event_type = "REVIEW_REQUIRED"
    if severity not in WALKIE_SEVERITIES:
        severity = "ACTION_REQUIRED"
    clean_candidate = candidate_id or "state"
    return WalkieEvent(
        walkie_event_id=f"WALKIE-{event_type}-{clean_candidate}",
        event_type=event_type,
        severity=severity,
        route_to=_walkie_route_for(severity),
        source=source,
        reason=reason,
        candidate_id=candidate_id,
        lane=lane,
        requires_anthony=requires_anthony,
        safe_next_action=safe_next_action,
        blocked_actions=blocked_event_actions(),
        evidence=evidence,
        zero_external_wake_confirmation=True,
        zero_worker_launch_confirmation=True,
    )


def build_walkie_events(
    decisions: list[Decision],
    state_summary: dict[str, Any],
    recommended: list[Decision],
) -> list[WalkieEvent]:
    events: list[WalkieEvent] = []
    for decision in decisions:
        event_type, severity, requires_anthony = _event_type_for_decision(decision)
        if decision.decision in {"COMPLETE_OR_SUPERSEDED", "HISTORICAL_REFERENCE"}:
            continue
        events.append(
            build_walkie_event(
                event_type=event_type,
                severity=severity,
                source="dispatcher_assignment_executor",
                reason=";".join(decision.reasons) or decision.decision,
                candidate_id=decision.task_id,
                lane=decision.lane,
                requires_anthony=requires_anthony,
                safe_next_action=decision.next_safe_action,
                evidence={
                    "decision": decision.decision,
                    "candidate_source": decision.source,
                    "assigned_worker": decision.assigned_worker,
                },
            )
        )

    queue_treatment = state_summary["queue_state"].get("historical_queue_treatment")
    if queue_treatment == "REVIEW_REQUIRED":
        events.append(
            build_walkie_event(
                event_type="QUEUE_STATE_UNKNOWN",
                severity="ACTION_REQUIRED",
                source="dispatcher_assignment_executor",
                reason="queue surface is missing, malformed, or not marked historical/canonical",
                candidate_id=None,
                lane="queue",
                requires_anthony=False,
                safe_next_action="Night Supervisor review should classify queue source before dispatch.",
                evidence=state_summary["queue_state"],
            )
        )
    approval_state = state_summary["approval_state"]
    if approval_state.get("inbox_status") in {"MISSING", "MALFORMED"} or approval_state.get("apply_gate_status") == "MALFORMED":
        events.append(
            build_walkie_event(
                event_type="APPROVAL_STATE_UNKNOWN",
                severity="ACTION_REQUIRED",
                source="dispatcher_assignment_executor",
                reason="approval surface is missing or malformed",
                candidate_id=None,
                lane="approval",
                requires_anthony=False,
                safe_next_action="Night Supervisor review should gather approval evidence before APPLY.",
                evidence=approval_state,
            )
        )
    if not recommended:
        events.append(
            build_walkie_event(
                event_type="NO_SAFE_LANE_FOUND",
                severity="ACTION_REQUIRED",
                source="dispatcher_assignment_executor",
                reason="no READY or DRY_RUN_ONLY candidate was available",
                candidate_id=None,
                lane=None,
                requires_anthony=False,
                safe_next_action="Review blockers and approval state before dispatch.",
                evidence={"decision_count": len(decisions)},
            )
        )
    if any(decision.decision.startswith("BLOCKED") for decision in decisions):
        events.append(
            build_walkie_event(
                event_type="SOS_CANDIDATE",
                severity="SOS_CANDIDATE",
                source="dispatcher_assignment_executor",
                reason="blocked work may require Watchdog/Pi5 review if it becomes operationally urgent",
                candidate_id=None,
                lane="watchdog_review",
                requires_anthony=True,
                safe_next_action="Route to Watchdog/Pi5 review only; Dispatcher must not wake Anthony directly.",
                evidence={"blocked_decisions": [asdict(decision) for decision in decisions if decision.decision.startswith("BLOCKED")]},
            )
        )
    return events


def build_pr_walkie_events(pr_dependency_findings: list[dict[str, Any]], pr_backlog_report: dict[str, Any]) -> list[WalkieEvent]:
    events: list[WalkieEvent] = []
    if pr_backlog_report.get("status") in {"UNKNOWN", "MALFORMED"}:
        events.append(
            build_walkie_event(
                event_type="REVIEW_REQUIRED",
                severity="ACTION_REQUIRED",
                source="dispatcher_pr_backlog_fixture",
                reason=pr_backlog_report.get("pr_backlog_unknown_reason") or "PR backlog state unknown",
                candidate_id=None,
                lane="pr_backlog",
                requires_anthony=False,
                safe_next_action="Provide a local PR backlog fixture or continue with PR_UNKNOWN.",
                evidence={"pr_backlog_status": pr_backlog_report.get("status")},
            )
        )
    for finding in pr_dependency_findings:
        if finding["dependency_classification"] == "PR_MERGED_BASELINE":
            continue
        severity = "SAFETY_BLOCK" if finding["dependency_classification"] == "PR_BLOCKED_BY_CONFLICT" else "ACTION_REQUIRED"
        events.append(
            build_walkie_event(
                event_type="PR_DEPENDENCY_CHANGED",
                severity=severity,
                source="dispatcher_pr_backlog_fixture",
                reason=finding["dependency_classification"],
                candidate_id=finding["candidate_id"],
                lane="pr_backlog",
                requires_anthony=True,
                safe_next_action="Review PR dependency evidence before dispatch. Do not merge or APPLY from this signal.",
                evidence=finding,
            )
        )
    return events


def build_report(repo_root: Path, *, allow_github: bool = False, pr_backlog_fixture: Path | None = None) -> dict[str, Any]:
    state = load_state(repo_root, allow_github=allow_github, pr_backlog_fixture=pr_backlog_fixture)
    summary = summarize_state(state)
    candidates = normalize_candidates(state)
    decisions, collisions = classify_candidates(candidates, summary, state["pr_backlog"])
    pr_backlog_report = classify_pr_backlog(state["pr_backlog"])
    pr_dependency_findings = build_pr_dependency_findings(candidates, pr_backlog_report)
    recommended = [
        decision
        for decision in decisions
        if decision.decision in {"READY", "DRY_RUN_ONLY"} and decision.source == "active_work_packet"
    ][:3]
    if not recommended:
        recommended = [decision for decision in decisions if decision.decision == "DRY_RUN_ONLY"][:3]
    previews = [build_dispatch_packet_preview(decision) for decision in recommended]
    walkie_events = build_walkie_events(decisions, summary, recommended) + build_pr_walkie_events(pr_dependency_findings, pr_backlog_report)
    packet_drafts = build_packet_drafts(
        decisions,
        walkie_events=walkie_events,
        pr_dependency_findings=pr_dependency_findings,
        lock_state=summary["lock_state"],
        approval_state=summary["approval_state"],
        collisions=collisions,
    )
    blockers = [asdict(decision) for decision in decisions if decision.decision.startswith("BLOCKED") or decision.decision in {"WAITING_APPROVAL", "REVIEW_REQUIRED"}]
    return {
        "report_id": "AIOS_WORKER_DISPATCHER_ASSIGNMENT_EXECUTOR_DRY_RUN_V1",
        "generated_at_utc": utc_now(),
        "repo_state": {"repo_root": repo_root.as_posix(), "mode": "DRY_RUN_ONLY"},
        "worker_state": summary["worker_state"],
        "queue_state": summary["queue_state"],
        "lock_state": summary["lock_state"],
        "approval_state": summary["approval_state"],
        "work_packet_state": {
            "active_count": summary["queue_state"]["active_work_packet_count"],
            "candidate_count": len(candidates),
            "active_contract": summary["queue_state"]["active_work_packet_contract"],
            "proposed_backlog_contract": summary["queue_state"]["proposed_backlog_contract"],
        },
        "active_state_contracts": {
            "queue": summary["queue_state"],
            "locks": summary["lock_state"],
            "approval": summary["approval_state"],
            "worker_inbox": {
                "contract_status": summary["worker_state"]["worker_inbox_contract"],
                "completed_items_are_active": False,
            },
            "work_packets": {
                "contract_status": summary["queue_state"]["active_work_packet_contract"],
                "proposed_backlog_contract": summary["queue_state"]["proposed_backlog_contract"],
                "dispatch_previews_are_executable": False,
            },
            "validator_pass_is_approval": False,
            "github_check_pass_is_approval": False,
            "dispatcher_preview_is_approval": False,
        },
        "pr_backlog_state": {
            **summary["pr_backlog_state"],
            **pr_backlog_report,
            "pr_dependency_findings": pr_dependency_findings,
            "walkie_events_from_pr_backlog": [asdict(event) for event in build_pr_walkie_events(pr_dependency_findings, pr_backlog_report)],
        },
        "collision_findings": collisions,
        "candidate_decisions": [asdict(decision) for decision in decisions],
        "recommended_lanes": [asdict(decision) for decision in recommended],
        "dispatch_packet_previews": previews,
        "internal_walkie_events": [asdict(event) for event in walkie_events],
        "packet_drafts": [asdict(draft) for draft in packet_drafts],
        "blockers": blockers,
        "zero_launch_confirmation": zero_launch_confirmation(),
        "validator_pass_is_evidence_only": True,
        "approval_authority": "Anthony",
        "generated_report_path": DEFAULT_REPORT_PATH,
    }


def sample_report() -> dict[str, Any]:
    state = {
        "worker_registry": {"status": "PRESENT", "payload": {"workers": [{"worker_id": "codex"}]}},
        "worker_inbox": {"status": "PRESENT", "payload": {"items": [{"id": "done", "worker_id": "codex", "status": "complete", "current_status": "done", "task": "done task"}]}},
        "historical_queue": {"status": "PRESENT", "payload": {"status": "HISTORICAL", "items": [{"packet_id": "old", "status": "DONE", "title": "old"}]}},
        "lock_registry": {"status": "PRESENT", "payload": {"locks": []}},
        "approval_inbox": {"status": "PRESENT", "payload": {"approval_status": "completed"}},
        "apply_gate": {"status": "PRESENT", "payload": {"approval_status": "pending_review", "approved_by_human": False}},
        "active_work_packets": {
            "status": "PRESENT",
            "packets": [
                {
                    "packet_id": "dry-run-next",
                    "title": "Dry run next lane",
                    "owner_lane": "dispatcher",
                    "assigned_worker": "codex",
                    "status": "active",
                    "validator": "python -m pytest",
                    "next_action": "Run DRY_RUN preview only.",
                }
            ],
            "errors": [],
        },
        "proposed_backlog": {"status": "PRESENT", "contract_status": "PROPOSED_BACKLOG"},
        "pr_backlog": {"status": "UNKNOWN", "open_prs": []},
    }
    summary = summarize_state(state)
    candidates = normalize_candidates(state)
    decisions, collisions = classify_candidates(candidates, summary, state["pr_backlog"])
    pr_backlog_report = classify_pr_backlog(state["pr_backlog"])
    pr_dependency_findings = build_pr_dependency_findings(candidates, pr_backlog_report)
    recommended = [decision for decision in decisions if decision.decision == "DRY_RUN_ONLY"][:3]
    walkie_events = build_walkie_events(decisions, summary, recommended) + build_pr_walkie_events(pr_dependency_findings, pr_backlog_report)
    packet_drafts = build_packet_drafts(
        decisions,
        walkie_events=walkie_events,
        pr_dependency_findings=pr_dependency_findings,
        lock_state=summary["lock_state"],
        approval_state=summary["approval_state"],
        collisions=collisions,
    )
    return {
        "report_id": "AIOS_WORKER_DISPATCHER_ASSIGNMENT_EXECUTOR_DRY_RUN_V1_SAMPLE",
        "worker_state": summary["worker_state"],
        "queue_state": summary["queue_state"],
        "lock_state": summary["lock_state"],
        "approval_state": summary["approval_state"],
        "active_state_contracts": {
            "queue": summary["queue_state"],
            "locks": summary["lock_state"],
            "approval": summary["approval_state"],
            "worker_inbox": {
                "contract_status": summary["worker_state"]["worker_inbox_contract"],
                "completed_items_are_active": False,
            },
            "work_packets": {
                "contract_status": summary["queue_state"]["active_work_packet_contract"],
                "proposed_backlog_contract": summary["queue_state"]["proposed_backlog_contract"],
                "dispatch_previews_are_executable": False,
            },
            "validator_pass_is_approval": False,
            "github_check_pass_is_approval": False,
            "dispatcher_preview_is_approval": False,
        },
        "candidate_decisions": [asdict(decision) for decision in decisions],
        "collision_findings": collisions,
        "pr_backlog_state": {
            **state["pr_backlog"],
            **pr_backlog_report,
            "pr_dependency_findings": pr_dependency_findings,
            "walkie_events_from_pr_backlog": [asdict(event) for event in build_pr_walkie_events(pr_dependency_findings, pr_backlog_report)],
        },
        "recommended_lanes": [asdict(decision) for decision in recommended],
        "dispatch_packet_previews": [build_dispatch_packet_preview(decision) for decision in recommended],
        "internal_walkie_events": [asdict(event) for event in walkie_events],
        "packet_drafts": [asdict(draft) for draft in packet_drafts],
        "zero_launch_confirmation": zero_launch_confirmation(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="AI_OS Worker Dispatcher Assignment Executor DRY_RUN V1.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--include-github-prs", action="store_true")
    parser.add_argument("--pr-backlog-fixture")
    parser.add_argument("--sample-check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = sample_report() if args.sample_check else build_report(
        Path(args.repo_root).resolve(),
        allow_github=args.include_github_prs,
        pr_backlog_fixture=Path(args.pr_backlog_fixture) if args.pr_backlog_fixture else None,
    )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"{payload['report_id']}: DRY_RUN_COMPLETE")
        print(f"zero_workers_launched={payload['zero_launch_confirmation']['zero_workers_launched']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
