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
COMPLETE_STATES = {"complete", "completed", "done", "superseded", "archived_reference", "closed"}
WAITING_APPROVAL_STATES = {"awaiting_approval", "waiting_approval", "waiting_for_approval", "pending_review"}
ACTIVE_STATES = {"active", "ready", "queued", "assigned", "running", "dry_run_running", "ready_for_dry_run"}
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


def read_json_file(path: Path) -> tuple[str, Any | None, str | None]:
    if not path.exists():
        return "MISSING", None, None
    try:
        return "PRESENT", json.loads(path.read_text(encoding="utf-8")), None
    except json.JSONDecodeError as exc:
        return "MALFORMED", None, f"{exc.__class__.__name__}: {exc}"


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


def load_pr_backlog(repo_root: Path, *, allow_github: bool) -> dict[str, Any]:
    if not allow_github:
        return {"status": "UNKNOWN", "reason": "GitHub PR inspection disabled for this run.", "open_prs": []}
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
    return {"status": "PRESENT", "open_pr_count": len(prs), "open_prs": prs}


def load_state(repo_root: Path, *, allow_github: bool = False) -> dict[str, Any]:
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
    state["pr_backlog"] = load_pr_backlog(repo_root, allow_github=allow_github)
    return state


def summarize_state(state: dict[str, Any]) -> dict[str, Any]:
    workers_payload = state["worker_registry"].get("payload") or {}
    inbox_payload = state["worker_inbox"].get("payload") or {}
    queue_payload = state["historical_queue"].get("payload") or {}
    locks_payload = state["lock_registry"].get("payload") or {}
    approval_payload = state["approval_inbox"].get("payload") or {}
    apply_payload = state["apply_gate"].get("payload") or {}
    locks = _as_list(locks_payload.get("locks") if isinstance(locks_payload, dict) else [])
    queue_status = _norm(queue_payload.get("status") if isinstance(queue_payload, dict) else "")
    approval_status = _norm(approval_payload.get("approval_status") if isinstance(approval_payload, dict) else "")
    apply_status = _norm(apply_payload.get("approval_status") if isinstance(apply_payload, dict) else "")
    return {
        "worker_state": {
            "surface_status": state["worker_registry"]["status"],
            "worker_count": len(_as_list(workers_payload.get("workers") if isinstance(workers_payload, dict) else [])),
        },
        "queue_state": {
            "historical_queue_status": queue_status or state["historical_queue"]["status"],
            "historical_queue_treatment": "HISTORICAL_REFERENCE" if queue_status.upper() == "HISTORICAL" else "REVIEW_REQUIRED",
            "active_work_packet_count": len(state["active_work_packets"]["packets"]),
        },
        "lock_state": {
            "surface_status": state["lock_registry"]["status"],
            "active_lock_count": len([lock for lock in locks if isinstance(lock, dict)]),
            "classification": "NO_ACTIVE_LOCKS" if state["lock_registry"]["status"] == "PRESENT" and not locks else "ACTIVE_LOCKS_PRESENT",
        },
        "approval_state": {
            "inbox_status": approval_status or state["approval_inbox"]["status"],
            "apply_gate_status": apply_status or state["apply_gate"]["status"],
            "future_apply_approved": bool(
                isinstance(apply_payload, dict)
                and apply_payload.get("approval_status") == "approved_for_apply"
                and apply_payload.get("approved_by_human") is True
            ),
            "authority_note": "Completed authority-repair records are evidence only, not future APPLY approval.",
        },
        "pr_backlog_state": state["pr_backlog"],
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
                    protected_paths=[],
                    required_approval=None,
                    validator_chain=[],
                    next_safe_action="Historical reference only. Do not dispatch from DISPATCHER_QUEUE.json.",
                )
            )
    return candidates


def classify_candidates(candidates: list[Candidate], state_summary: dict[str, Any], pr_backlog: dict[str, Any]) -> tuple[list[Decision], list[dict[str, Any]]]:
    decisions: list[Decision] = []
    collisions: list[dict[str, Any]] = []
    active_candidates = [candidate for candidate in candidates if candidate.status in ACTIVE_STATES or candidate.status in WAITING_APPROVAL_STATES]

    for index, left in enumerate(active_candidates):
        for right in active_candidates[index + 1 :]:
            if left.protected_paths and right.protected_paths and _path_overlaps(left.protected_paths, right.protected_paths):
                collisions.append({"left": left.task_id, "right": right.task_id, "reason": "protected_path_overlap"})

    open_titles = " ".join(str(pr.get("title", "")) for pr in _as_list(pr_backlog.get("open_prs")))
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
        elif candidate.blockers:
            decision = "REVIEW_REQUIRED"
            reasons.extend([f"blocked_by:{item}" for item in candidate.blockers])
        elif _protected_path(candidate.protected_paths):
            decision = "BLOCKED_BY_PROTECTED_PATH"
            reasons.append("protected_runtime_or_forbidden_path")
        elif any(candidate.task_id in f"{collision['left']} {collision['right']}" for collision in collisions):
            decision = "BLOCKED_BY_COLLISION"
            reasons.append("candidate_collides_with_active_candidate")
        elif pr_backlog.get("status") == "PRESENT" and candidate.task_id and candidate.task_id in open_titles:
            decision = "BLOCKED_BY_PR_DEPENDENCY"
            reasons.append("matching_open_pr_title")
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


def build_report(repo_root: Path, *, allow_github: bool = False) -> dict[str, Any]:
    state = load_state(repo_root, allow_github=allow_github)
    summary = summarize_state(state)
    candidates = normalize_candidates(state)
    decisions, collisions = classify_candidates(candidates, summary, state["pr_backlog"])
    recommended = [
        decision
        for decision in decisions
        if decision.decision in {"READY", "DRY_RUN_ONLY"} and decision.source == "active_work_packet"
    ][:3]
    if not recommended:
        recommended = [decision for decision in decisions if decision.decision == "DRY_RUN_ONLY"][:3]
    previews = [build_dispatch_packet_preview(decision) for decision in recommended]
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
        },
        "pr_backlog_state": summary["pr_backlog_state"],
        "collision_findings": collisions,
        "candidate_decisions": [asdict(decision) for decision in decisions],
        "recommended_lanes": [asdict(decision) for decision in recommended],
        "dispatch_packet_previews": previews,
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
        "pr_backlog": {"status": "UNKNOWN", "open_prs": []},
    }
    summary = summarize_state(state)
    candidates = normalize_candidates(state)
    decisions, collisions = classify_candidates(candidates, summary, state["pr_backlog"])
    recommended = [decision for decision in decisions if decision.decision == "DRY_RUN_ONLY"][:3]
    return {
        "report_id": "AIOS_WORKER_DISPATCHER_ASSIGNMENT_EXECUTOR_DRY_RUN_V1_SAMPLE",
        "worker_state": summary["worker_state"],
        "queue_state": summary["queue_state"],
        "lock_state": summary["lock_state"],
        "approval_state": summary["approval_state"],
        "candidate_decisions": [asdict(decision) for decision in decisions],
        "collision_findings": collisions,
        "recommended_lanes": [asdict(decision) for decision in recommended],
        "dispatch_packet_previews": [build_dispatch_packet_preview(decision) for decision in recommended],
        "zero_launch_confirmation": zero_launch_confirmation(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="AI_OS Worker Dispatcher Assignment Executor DRY_RUN V1.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--include-github-prs", action="store_true")
    parser.add_argument("--sample-check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = sample_report() if args.sample_check else build_report(Path(args.repo_root).resolve(), allow_github=args.include_github_prs)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"{payload['report_id']}: DRY_RUN_COMPLETE")
        print(f"zero_workers_launched={payload['zero_launch_confirmation']['zero_workers_launched']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
