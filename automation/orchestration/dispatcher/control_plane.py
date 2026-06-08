from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORKER_STATES = {"available", "busy", "blocked", "stale", "unknown"}
ACTIVE_ASSIGNMENT_STATES = {"assigned", "running", "busy", "waiting_for_approval"}
APPLY_ACTIONS = {"apply", "apply_files", "apply_scoped_files", "mutate_repo"}
PROTECTED_ACTIONS = {
    "direct_main_push",
    "force_push",
    "branch_delete",
    "delete_branch",
    "stash",
    "stash_mutation",
    "live_sos",
    "arm_live_sos",
    "scheduler_activation",
    "launch_scheduler",
}
GATED_LANE_TERMS = {"scheduler", "live_sos", "live-trading", "live_trading", "broker", "cloud", "trading"}
GENERATED_EVIDENCE_PATH = "Reports/generated/dispatcher/worker_dispatcher_preview.json"


@dataclass
class Finding:
    code: str
    severity: str
    message: str
    evidence: str

    def as_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "evidence": self.evidence,
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _has_overlap(left: list[str], right: list[str]) -> bool:
    left_values = [item.rstrip("/\\") for item in left if item]
    right_values = [item.rstrip("/\\") for item in right if item]
    for left_item in left_values:
        for right_item in right_values:
            if left_item == right_item or left_item.startswith(f"{right_item}/") or right_item.startswith(f"{left_item}/"):
                return True
    return False


def _lane_is_gated(lane_name: str) -> bool:
    lower = lane_name.lower()
    return any(term in lower for term in GATED_LANE_TERMS)


def _worker_map(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        worker.get("worker_id", ""): worker
        for worker in _list(registry.get("workers"))
        if isinstance(worker, dict)
    }


def validate_control_plane(registry: dict[str, Any], assignments: dict[str, Any], repo_root: Path | None = None) -> dict[str, Any]:
    findings: list[Finding] = []
    workers = _list(registry.get("workers"))
    worker_ids: list[str] = []

    for worker in workers:
        if not isinstance(worker, dict):
            findings.append(Finding("AIOS-DISPATCHER-WORKER-SHAPE", "FAIL", "Worker record must be an object.", repr(worker)))
            continue
        worker_id = str(worker.get("worker_id", ""))
        if not worker_id:
            findings.append(Finding("AIOS-DISPATCHER-WORKER-ID-MISSING", "FAIL", "Worker is missing worker_id.", json.dumps(worker, sort_keys=True)))
        worker_ids.append(worker_id)
        authority = str(worker.get("authority_level", "")).lower()
        if "approval" in authority and worker_id != "anthony_approval_authority":
            findings.append(Finding("AIOS-DISPATCHER-AUTHORITY-CLAIM", "BLOCK", "Only Anthony may be approval authority.", worker_id))
        if worker.get("can_merge") is True:
            findings.append(Finding("AIOS-DISPATCHER-MERGE-GRANT", "BLOCK", "Worker registry must not grant merge authority.", worker_id))
        if worker.get("can_launch_workers") is True:
            findings.append(Finding("AIOS-DISPATCHER-LAUNCH-GRANT", "BLOCK", "Worker registry must not grant worker launch authority.", worker_id))
        for blocked_flag, code in [
            ("can_touch_scheduler", "AIOS-DISPATCHER-SCHEDULER-GRANT"),
            ("can_touch_live_sos", "AIOS-DISPATCHER-LIVE-SOS-GRANT"),
            ("can_touch_broker_or_trading", "AIOS-DISPATCHER-BROKER-TRADING-GRANT"),
            ("can_touch_cloud_provider", "AIOS-DISPATCHER-CLOUD-GRANT"),
        ]:
            if worker.get(blocked_flag) is True:
                findings.append(Finding(code, "BLOCK", f"Worker registry must not grant {blocked_flag}.", worker_id))
        if worker.get("default_status") not in WORKER_STATES:
            findings.append(Finding("AIOS-DISPATCHER-WORKER-STATE", "FAIL", "Worker default_status is invalid.", f"{worker_id}:{worker.get('default_status')}"))

    duplicates = sorted({worker_id for worker_id in worker_ids if worker_ids.count(worker_id) > 1 and worker_id})
    for worker_id in duplicates:
        findings.append(Finding("AIOS-DISPATCHER-DUPLICATE-WORKER", "FAIL", "Worker IDs must be unique.", worker_id))

    worker_by_id = _worker_map(registry)
    lane_claims: dict[str, list[str]] = {}
    active_assignments: list[dict[str, Any]] = []

    for assignment in _list(assignments.get("assignments")):
        if not isinstance(assignment, dict):
            findings.append(Finding("AIOS-DISPATCHER-ASSIGNMENT-SHAPE", "FAIL", "Assignment record must be an object.", repr(assignment)))
            continue
        lane_id = str(assignment.get("lane_id", ""))
        lane_name = str(assignment.get("lane_name", ""))
        worker_id = str(assignment.get("assigned_worker_id", ""))
        status = str(assignment.get("status", ""))
        protected_paths = _list(assignment.get("protected_paths"))
        allowed_actions = set(_list(assignment.get("allowed_actions")))
        forbidden_actions = set(_list(assignment.get("forbidden_actions")))
        required_approval = assignment.get("required_approval")
        is_active = status in ACTIVE_ASSIGNMENT_STATES
        worker = worker_by_id.get(worker_id, {})
        worker_state = worker.get("default_status", "unknown")

        if not lane_id and not lane_name:
            findings.append(Finding("AIOS-DISPATCHER-LANE-MISSING", "FAIL", "Assignment must include lane_id or lane_name.", json.dumps(assignment, sort_keys=True)))
        if not protected_paths:
            findings.append(Finding("AIOS-DISPATCHER-PROTECTED-PATHS-MISSING", "FAIL", "Assignment must include protected_paths.", lane_id or lane_name))
        if worker_id not in worker_by_id:
            findings.append(Finding("AIOS-DISPATCHER-UNKNOWN-WORKER", "FAIL", "Assignment references unknown worker.", worker_id))
        if is_active:
            lane_claims.setdefault(lane_id or lane_name, []).append(worker_id)
            active_assignments.append(assignment)
        if worker_state == "stale" and allowed_actions & APPLY_ACTIONS:
            findings.append(Finding("AIOS-DISPATCHER-STALE-APPLY", "BLOCK", "Stale worker cannot receive APPLY work.", worker_id))
        if worker_state == "unknown" and allowed_actions & APPLY_ACTIONS:
            findings.append(Finding("AIOS-DISPATCHER-UNKNOWN-APPLY", "BLOCK", "Unknown worker cannot receive APPLY work.", worker_id))
        if worker_state == "blocked" and is_active:
            findings.append(Finding("AIOS-DISPATCHER-BLOCKED-ASSIGNMENT", "BLOCK", "Blocked worker cannot receive new assignments.", worker_id))
        if allowed_actions & APPLY_ACTIONS and not required_approval:
            findings.append(Finding("AIOS-DISPATCHER-APPLY-APPROVAL-MISSING", "BLOCK", "APPLY assignment requires approval reference.", lane_id or lane_name))
        if _lane_is_gated(f"{lane_id} {lane_name}") and "blocked" not in status and "gate_required" not in forbidden_actions:
            findings.append(Finding("AIOS-DISPATCHER-GATED-LANE-UNBLOCKED", "BLOCK", "Scheduler/live/broker/cloud/trading lanes must remain blocked or gated.", lane_id or lane_name))
        forbidden_grants = sorted(PROTECTED_ACTIONS & allowed_actions)
        for action in forbidden_grants:
            findings.append(Finding("AIOS-DISPATCHER-PROTECTED-ACTION-GRANT", "BLOCK", "Dispatcher assignment must not grant protected action.", action))
        if "execute" in allowed_actions and str(assignment.get("output_contract", "")).lower() == "dispatch_packet":
            findings.append(Finding("AIOS-DISPATCHER-EXECUTABLE-PACKET", "BLOCK", "Dispatch packet output must be non-executable by default.", lane_id or lane_name))

    for lane_id, claimers in lane_claims.items():
        if lane_id and len(claimers) > 1:
            findings.append(Finding("AIOS-DISPATCHER-LANE-COLLISION", "FAIL", "No two active assignments may own the same protected lane.", f"{lane_id}:{','.join(claimers)}"))

    for index, left in enumerate(active_assignments):
        for right in active_assignments[index + 1 :]:
            if _has_overlap(_list(left.get("protected_paths")), _list(right.get("protected_paths"))):
                findings.append(
                    Finding(
                        "AIOS-DISPATCHER-PATH-COLLISION",
                        "FAIL",
                        "No two active assignments may own overlapping protected paths.",
                        f"{left.get('lane_id')}:{right.get('lane_id')}",
                    )
                )

    if repo_root is not None and not is_ignored(repo_root, GENERATED_EVIDENCE_PATH):
        findings.append(
            Finding(
                "AIOS-DISPATCHER-GENERATED-OUTPUT-NOT-IGNORED",
                "FAIL",
                "Dispatcher generated evidence path must be ignored.",
                GENERATED_EVIDENCE_PATH,
            )
        )

    status = "PASS"
    if any(finding.severity == "BLOCK" for finding in findings):
        status = "BLOCKED"
    elif findings:
        status = "FAIL"

    return {
        "validator": "aios_worker_dispatcher_validator",
        "version": "1.0",
        "timestamp_utc": utc_now(),
        "status": status,
        "findings": [finding.as_dict() for finding in findings],
        "safe_next_action": "Repair dispatcher registry or assignments before using previews." if status != "PASS" else "Use dispatcher output for read-only preview only.",
    }


def build_dispatch_preview(registry: dict[str, Any], assignments: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    worker_by_id = _worker_map(registry)
    requested_worker_id = str(task.get("assigned_worker_id") or task.get("preferred_worker_id") or "")
    worker = worker_by_id.get(requested_worker_id)
    protected_paths = _list(task.get("protected_paths"))
    allowed_actions = set(_list(task.get("allowed_actions")))
    decision = "can_assign"
    reasons: list[str] = []

    if not worker:
        decision = "cannot_assign"
        reasons.append("unknown_worker")
        worker_state = "unknown"
    else:
        worker_state = str(worker.get("default_status", "unknown"))
        if worker_state in {"stale", "unknown"} and allowed_actions & APPLY_ACTIONS:
            decision = "cannot_assign"
            reasons.append(f"{worker_state}_worker_apply_block")
        if worker_state == "blocked":
            decision = "cannot_assign"
            reasons.append("blocked_worker")

    for assignment in _list(assignments.get("assignments")):
        if str(assignment.get("status", "")) not in ACTIVE_ASSIGNMENT_STATES:
            continue
        if _has_overlap(protected_paths, _list(assignment.get("protected_paths"))):
            decision = "cannot_assign"
            reasons.append(f"protected_path_collision:{assignment.get('lane_id')}")

    if _lane_is_gated(str(task.get("lane_id", "")) + " " + str(task.get("lane_name", ""))):
        decision = "cannot_assign"
        reasons.append("gated_lane_blocked")

    approval_needed = bool(allowed_actions & APPLY_ACTIONS)
    return {
        "preview_id": "AIOS_WORKER_DISPATCHER_PREVIEW_V1",
        "generated_at_utc": utc_now(),
        "task_id": task.get("task_id"),
        "decision": decision,
        "assigned_worker_id": requested_worker_id or None,
        "worker_state": worker_state,
        "reasons": reasons,
        "queue_state_missing": assignments.get("queue_state_present") is not True,
        "locks_missing_or_stale": assignments.get("locks_state") in {None, "missing", "stale"},
        "operator_approval_needed": approval_needed,
        "sos_needed": False,
        "dispatch_packet": {
            "format": "DRAFT_ONLY_NON_EXECUTABLE",
            "contains_execution_token": False,
            "apply_execution_approved": False,
            "stop_point": "Stop after preview. Do not execute without a complete AI_OS packet and Anthony approval.",
        },
        "evidence_path": GENERATED_EVIDENCE_PATH,
    }


def is_ignored(repo_root: Path, relative_path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", relative_path],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def sample_registry() -> dict[str, Any]:
    return {
        "schema": "AIOS_WORKER_DISPATCHER_REGISTRY_V1",
        "workers": [
            {
                "worker_id": "chatgpt_supervisor",
                "worker_type": "ChatGPT supervisor/planner",
                "display_name": "ChatGPT Supervisor",
                "authority_level": "planner_only",
                "allowed_lanes": ["planning", "packet_drafting"],
                "forbidden_lanes": ["local_apply", "scheduler", "live_sos", "broker", "cloud"],
                "allowed_actions": ["plan", "summarize", "draft_non_executable_packet"],
                "forbidden_actions": ["apply", "merge", "launch_worker", "approve"],
                "can_apply": False,
                "can_merge": False,
                "can_launch_workers": False,
                "can_touch_scheduler": False,
                "can_touch_live_sos": False,
                "can_touch_broker_or_trading": False,
                "can_touch_cloud_provider": False,
                "default_status": "available",
                "evidence_path": GENERATED_EVIDENCE_PATH,
                "next_safe_action": "Draft non-executable packets for Anthony review.",
            },
            {
                "worker_id": "codex_cli_local_executor",
                "worker_type": "Codex CLI local executor",
                "display_name": "Codex CLI",
                "authority_level": "packet_scoped_executor",
                "allowed_lanes": ["worker-dispatcher-control-plane-v1"],
                "forbidden_lanes": ["scheduler", "live_sos", "broker", "cloud", "approval_authority"],
                "allowed_actions": ["read", "dry_run", "apply_scoped_files", "validate", "open_pr"],
                "forbidden_actions": ["self_approve", "merge", "direct_main_push", "force_push", "branch_delete", "stash"],
                "can_apply": True,
                "can_merge": False,
                "can_launch_workers": False,
                "can_touch_scheduler": False,
                "can_touch_live_sos": False,
                "can_touch_broker_or_trading": False,
                "can_touch_cloud_provider": False,
                "default_status": "available",
                "evidence_path": GENERATED_EVIDENCE_PATH,
                "next_safe_action": "Execute only complete scoped packets approved by Anthony.",
            },
            {
                "worker_id": "claude_code_reviewer",
                "worker_type": "Claude Code reviewer/branch worker",
                "display_name": "Claude Code Reviewer",
                "authority_level": "review_or_assigned_branch_worker",
                "allowed_lanes": ["review", "bounded_refinement"],
                "forbidden_lanes": ["approval_authority", "scheduler", "live_sos", "broker", "cloud"],
                "allowed_actions": ["review", "report", "bounded_refinement"],
                "forbidden_actions": ["approve", "merge", "direct_main_push"],
                "can_apply": False,
                "can_merge": False,
                "can_launch_workers": False,
                "can_touch_scheduler": False,
                "can_touch_live_sos": False,
                "can_touch_broker_or_trading": False,
                "can_touch_cloud_provider": False,
                "default_status": "unknown",
                "evidence_path": GENERATED_EVIDENCE_PATH,
                "next_safe_action": "Use only when assigned by explicit packet.",
            },
            {
                "worker_id": "openai_codex_app_reviewer",
                "worker_type": "OpenAI/Codex app review/remote worker",
                "display_name": "OpenAI Codex App Reviewer",
                "authority_level": "remote_review_only",
                "allowed_lanes": ["review"],
                "forbidden_lanes": ["approval_authority", "scheduler", "live_sos", "broker", "cloud"],
                "allowed_actions": ["review", "report"],
                "forbidden_actions": ["approve", "merge", "launch_worker"],
                "can_apply": False,
                "can_merge": False,
                "can_launch_workers": False,
                "can_touch_scheduler": False,
                "can_touch_live_sos": False,
                "can_touch_broker_or_trading": False,
                "can_touch_cloud_provider": False,
                "default_status": "unknown",
                "evidence_path": GENERATED_EVIDENCE_PATH,
                "next_safe_action": "Report review evidence only.",
            },
            {
                "worker_id": "github_pr_checks_layer",
                "worker_type": "GitHub PR/checks layer",
                "display_name": "GitHub PR Checks",
                "authority_level": "checks_layer_not_executor",
                "allowed_lanes": ["pr_checks"],
                "forbidden_lanes": ["local_apply", "approval_authority", "scheduler", "live_sos", "broker", "cloud"],
                "allowed_actions": ["report_checks", "host_pr"],
                "forbidden_actions": ["execute_local_files", "approve", "merge_without_approval"],
                "can_apply": False,
                "can_merge": False,
                "can_launch_workers": False,
                "can_touch_scheduler": False,
                "can_touch_live_sos": False,
                "can_touch_broker_or_trading": False,
                "can_touch_cloud_provider": False,
                "default_status": "available",
                "evidence_path": GENERATED_EVIDENCE_PATH,
                "next_safe_action": "Provide PR and check status only.",
            },
            {
                "worker_id": "anthony_approval_authority",
                "worker_type": "Anthony approval authority",
                "display_name": "Anthony",
                "authority_level": "approval_authority",
                "allowed_lanes": ["approval"],
                "forbidden_lanes": [],
                "allowed_actions": ["approve", "reject", "stop"],
                "forbidden_actions": ["automated_execution"],
                "can_apply": False,
                "can_merge": False,
                "can_launch_workers": False,
                "can_touch_scheduler": False,
                "can_touch_live_sos": False,
                "can_touch_broker_or_trading": False,
                "can_touch_cloud_provider": False,
                "default_status": "available",
                "evidence_path": GENERATED_EVIDENCE_PATH,
                "next_safe_action": "Approve or reject specific protected actions.",
            },
        ],
    }


def sample_assignments() -> dict[str, Any]:
    return {
        "schema": "AIOS_WORKER_DISPATCHER_ASSIGNMENTS_V1",
        "queue_state_present": False,
        "locks_state": "missing",
        "assignments": [
            {
                "lane_id": "worker-dispatcher-control-plane-v1",
                "lane_name": "Worker Dispatcher Control Plane V1",
                "assigned_worker_id": "codex_cli_local_executor",
                "status": "assigned",
                "priority": "high",
                "protected_paths": [
                    "automation/orchestration/dispatcher/",
                    "automation/validators/",
                    "tests/orchestration/",
                    "tests/governance/",
                    "docs/AI_OS/worker_dispatcher/",
                ],
                "related_branch": "feature/worker-dispatcher-control-plane-v1",
                "related_pr": None,
                "required_approval": "OPERATOR_APPROVED_WORKER_DISPATCHER_CONTROL_PLANE_V1_BRANCH_SWITCH_OK",
                "lock_id": "LOCK-WORKER-DISPATCHER-V1",
                "allowed_actions": ["read", "dry_run", "apply_scoped_files", "validate", "open_pr"],
                "forbidden_actions": ["direct_main_push", "force_push", "branch_delete", "stash", "launch_scheduler", "arm_live_sos"],
                "validation_contract": "worker-dispatcher focused tests and validator sample-check",
                "output_contract": "dispatch_preview_non_executable",
                "next_safe_action": "Validate and open PR without merge.",
            }
        ],
    }


def sample_task() -> dict[str, Any]:
    return {
        "task_id": "AIOS-WORKER-DISPATCHER-CONTROL-PLANE-V1",
        "lane_id": "worker-dispatcher-read-only-preview",
        "lane_name": "Worker Dispatcher Read-Only Preview",
        "preferred_worker_id": "codex_cli_local_executor",
        "protected_paths": ["docs/architecture/worker-dispatcher-preview.md"],
        "allowed_actions": ["read", "dry_run"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="AI_OS worker dispatcher control-plane preview.")
    parser.add_argument("--sample-check", action="store_true")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.sample_check:
        print(json.dumps({"status": "BLOCKED", "reason": "--sample-check required"}, indent=2))
        return 2
    repo_root = Path(args.repo_root).resolve()
    validation = validate_control_plane(sample_registry(), sample_assignments(), repo_root)
    preview = build_dispatch_preview(sample_registry(), sample_assignments(), sample_task())
    payload = {"validation": validation, "preview": preview}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"aios_worker_dispatcher_control_plane: {validation['status']}")
        print(f"dispatch_decision: {preview['decision']}")
    return 0 if validation["status"] == "PASS" and preview["dispatch_packet"]["contains_execution_token"] is False else 1


if __name__ == "__main__":
    raise SystemExit(main())
