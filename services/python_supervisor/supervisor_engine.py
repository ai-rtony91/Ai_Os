"""AI_OS Night Supervisor read-only brainstem orchestrator.

Schema/contract reference: schemas/aios/orchestration/overnight_supervisor.schema.json
Mode: DRY_RUN
blocked_capabilities: worker_launch, packet_movement, approval_mutation,
telemetry_append, evidence_collect, report_write, scheduler_registration,
runtime_launch, git_stage_commit_push
next_safe_action: Review DRY_RUN JSON output; do not mutate state from this report.
commit_performed: NO / push_performed: NO
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from escalation_engine import build_escalation_items
from freshness_scoring import summarize_freshness
from queue_scanner import scan_queue
from runtime_state import build_runtime_state
from worker_assignment import assign_workers


BLOCKED_CAPABILITIES = [
    "worker_launch",
    "packet_movement",
    "approval_mutation",
    "telemetry_append",
    "evidence_collect",
    "report_write",
    "scheduler_registration",
    "runtime_launch",
    "stage_files",
    "commit",
    "push",
    "merge",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _assignment_by_packet(assignments: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(item.get("packet_id")): item for item in assignments}


def _packet_state(queue_status: str) -> str:
    return {
        "BLOCKED": "BLOCKED",
        "FAILED": "BLOCKED",
        "STALE": "STALE",
        "WAITING_APPROVAL": "APPROVAL_REQUIRED",
        "VALIDATING": "VALIDATOR_REQUIRED",
        "PENDING": "READY_FOR_REVIEW",
        "ASSIGNED": "READY_FOR_REVIEW",
        "COMPLETE": "READY_FOR_REVIEW",
    }.get(queue_status, "UNKNOWN")


def _repo_health(runtime: dict[str, Any]) -> dict[str, Any]:
    changed_paths = [str(path) for path in runtime.get("changed_paths", [])]
    untracked = [path for path in changed_paths if path.startswith("?? ")]
    if runtime.get("bundle_integrity") == "BLOCKED" or runtime.get("lock_conflicts"):
        risk = "BLOCKED"
    elif changed_paths:
        risk = "WATCH"
    elif runtime.get("bundle_integrity") in {"REVIEW", "UNKNOWN"}:
        risk = "WATCH"
    else:
        risk = "SAFE"
    return {
        "branch": str(runtime.get("branch") or "UNKNOWN"),
        "status_summary": f"Runtime bundle integrity {runtime.get('bundle_integrity', 'UNKNOWN')}; read-only brainstem pass.",
        "changed_files": changed_paths,
        "untracked_items": untracked,
        "risk_level": risk,
    }


def _packet_flow(queue_items: list[dict[str, Any]], assignments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_packet = _assignment_by_packet(assignments)
    packet_flow = []
    for item in queue_items:
        packet_id = str(item.get("packet_id") or "UNKNOWN")
        assignment = by_packet.get(packet_id, {})
        packet_flow.append(
            {
                "packet_id": packet_id,
                "lane": str(item.get("lane") or assignment.get("lane") or "UNKNOWN"),
                "worker_identity": str(assignment.get("worker_id") or item.get("worker_id") or "UNASSIGNED"),
                "validator_chain": ["DRY_RUN_VALIDATOR_CHAIN_NOT_RUN"],
                "approval_required": bool(item.get("approval_required")),
                "escalation_reason": str(item.get("status_reason") or "Read-only packet intake evidence."),
                "stop_condition": "DRY_RUN_REPORT_ONLY",
                "packet_state": _packet_state(str(item.get("status") or "UNKNOWN")),
                "report_target": "morning_brief_preview",
                "commit_package_candidate": False,
                "next_safe_action": str(item.get("next_safe_action") or "Review packet before protected action."),
            }
        )
    return packet_flow


def _stale_packets(queue_items: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "packet_id": str(item.get("packet_id") or "UNKNOWN"),
            "state": "STALE",
            "reason": str(item.get("status_reason") or "Packet freshness is stale."),
            "next_safe_action": "Refresh evidence in an approved DRY_RUN collection pass.",
        }
        for item in queue_items
        if str(item.get("status")) == "STALE"
    ]


def _approval_required(queue_items: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "packet_id": str(item.get("packet_id") or "UNKNOWN"),
            "reason": str(item.get("status_reason") or "Human approval is required before mutation."),
            "approval_authority": "Anthony Meza",
            "next_safe_action": "Surface item to Human Owner; do not self-approve.",
        }
        for item in queue_items
        if bool(item.get("approval_required")) or str(item.get("status")) == "WAITING_APPROVAL"
    ]


def _supervisor_status(escalations: list[dict[str, str]], repo_health: dict[str, Any]) -> str:
    severities = {item["severity"] for item in escalations}
    if "BLOCKED" in severities or repo_health["risk_level"] == "BLOCKED":
        return "BLOCKED"
    if "WARNING" in severities or repo_health["risk_level"] == "WARNING":
        return "WARNING"
    if severities or repo_health["risk_level"] == "WATCH":
        return "REVIEW"
    return "READY"


def build_supervisor_report(repo_root: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_root).resolve()
    runtime_state = build_runtime_state(root).to_dict()
    queue_items = scan_queue(root)
    assignments = assign_workers(queue_items, root)
    freshness_items = [item.get("freshness", {}) for item in queue_items]
    freshness_summary = summarize_freshness(freshness_items) if freshness_items else {}
    validator_results = [
        {
            "validator_id": "orchestration_validator_chain",
            "state": "NOT_RUN",
            "evidence": "Night Supervisor brainstem packet does not run validators.",
            "next_safe_action": "Run approved validator chain in a separate DRY_RUN validation packet.",
        }
    ]
    escalations = build_escalation_items(
        queue_items,
        freshness_summary=freshness_summary,
        validator_results=validator_results,
    )
    health = _repo_health(runtime_state)
    supervisor_status = _supervisor_status(escalations, health)

    return {
        "supervisor_status": supervisor_status,
        "repo_health": health,
        "stale_packets": _stale_packets(queue_items),
        "packet_flow": _packet_flow(queue_items, assignments),
        "validator_recommendations": [
            {
                "validator_id": "orchestration_validator_chain",
                "priority": "MEDIUM",
                "reason": "Validators are intentionally not run by the read-only brainstem layer.",
                "next_safe_action": "Run validator chain in the approved validation lane.",
            }
        ],
        "validator_results": validator_results,
        "approval_required": _approval_required(queue_items),
        "commit_package_candidates": [],
        "escalation_items": escalations,
        "next_safe_actions": [
            {
                "rank": 1,
                "action": "Review Night Supervisor DRY_RUN brainstem output before any protected action.",
                "requires_human_approval": bool(escalations),
                "blocked_actions": BLOCKED_CAPABILITIES,
            }
        ],
        "packet_drafts": [],
        "morning_brief": {
            "summary": f"Read-only Night Supervisor brainstem scanned {len(queue_items)} packet(s) and produced {len(escalations)} escalation item(s).",
            "blockers": [item["evidence"] for item in escalations if item["severity"] == "BLOCKED"],
            "approval_needed": bool(_approval_required(queue_items)),
            "review_items": [item["evidence"] for item in escalations if item["severity"] in {"REVIEW", "WARNING"}],
            "recommended_first_action": "Review escalation list and validator recommendation; do not mutate state from this report.",
            "safe_to_ignore": ["No worker launch was performed.", "No packet or approval state was mutated."],
            "today_focus": "Use this output as read-only queue, assignment, and escalation evidence.",
        },
        "generated_at": _utc_now(),
        "mode": "DRY_RUN",
        "authority_boundary": {
            "read_only": True,
            "approval_authority": "Anthony Meza",
            "blocked_capabilities": BLOCKED_CAPABILITIES,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AI_OS Night Supervisor brainstem in DRY_RUN mode.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON.")
    args = parser.parse_args()
    print(json.dumps(build_supervisor_report(args.repo_root), indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
