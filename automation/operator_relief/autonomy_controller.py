"""Bounded execution controller for Operator Relief autonomy spine v1."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .autonomy_approval_processor import AUTO_ALLOWED, classify_approval
from .autonomy_commit_push_gate import evaluate_commit_push_gate
from .autonomy_packet_generator import build_autonomy_packet_draft
from .autonomy_scheduler import plan_next_run
from .autonomy_task_discovery import DiscoveredTask
from .autonomy_validator_orchestrator import build_validator_plan, run_validator_plan
from .full_auto_handoff import build_full_auto_handoff
from .full_auto_policy import FULL_AUTO_BLOCKED, FullAutoTask, evaluate_full_auto_policy


@dataclass(frozen=True)
class AutonomyControllerReport:
    task_id: str
    status: str
    policy: dict[str, Any]
    approval: dict[str, Any]
    handoff_summary: dict[str, Any] | None
    packet_draft: dict[str, Any] | None
    validator_plan: dict[str, Any] | None
    commit_push_gate: dict[str, Any] | None
    schedule: dict[str, Any]
    safety: dict[str, bool]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _handoff_summary(handoff: Any) -> dict[str, Any]:
    return {
        "task_id": handoff.task_id,
        "mode": handoff.mode,
        "lane": handoff.lane,
        "branch": handoff.branch,
        "validator_chain": handoff.validator_chain,
        "human_review_required": handoff.human_review_required,
        "executable": False,
    }


def run_autonomy_controller(task: FullAutoTask | DiscoveredTask, repo_state: Any, repo_root: Path | None = None) -> AutonomyControllerReport:
    full_task = task.task if isinstance(task, DiscoveredTask) else task
    policy = evaluate_full_auto_policy(full_task, repo_state)
    approval = classify_approval(full_task, repo_state)
    plan = build_validator_plan(full_task)
    schedule = plan_next_run().to_dict()
    handoff_summary = None
    packet_draft = None
    validator_result = None
    gate = None
    if policy.status == FULL_AUTO_BLOCKED:
        status = "STOPPED_BLOCKED"
    elif approval.status == "APPROVAL_REQUIRED":
        status = "STOPPED_APPROVAL_REQUIRED"
    elif approval.status != AUTO_ALLOWED:
        status = "STOPPED_BLOCKED"
    else:
        status = "READY"

    if policy.status != FULL_AUTO_BLOCKED:
        handoff_summary = _handoff_summary(build_full_auto_handoff(full_task, policy, repo_state))
        packet_draft = build_autonomy_packet_draft(
            full_task,
            repo_state,
            [f"{item.validator}:{item.path}" for item in plan.plan],
        ).to_dict()

    if approval.status == AUTO_ALLOWED and plan.status == "PLANNED":
        validator_result = run_validator_plan(full_task, repo_root).to_dict()
        if validator_result["status"] != "PASSED":
            status = "STOPPED_VALIDATOR_FAILED"
        else:
            gate = evaluate_commit_push_gate(full_task, repo_state, validators_passed=True).to_dict()
            status = "DRY_RUN_COMPLETE"
    elif approval.status == AUTO_ALLOWED and plan.status != "PLANNED":
        status = "STOPPED_UNSUPPORTED_VALIDATOR"

    return AutonomyControllerReport(
        task_id=full_task.task_id,
        status=status,
        policy=policy.to_dict(),
        approval=approval.to_dict(),
        handoff_summary=handoff_summary,
        packet_draft=packet_draft,
        validator_plan=validator_result or plan.to_dict(),
        commit_push_gate=gate,
        schedule=schedule,
        safety={
            "repo_files_written": False,
            "telemetry_files_written": False,
            "approval_files_written": False,
            "openai_api_invoked": False,
            "codex_invoked": False,
            "daemon_started": False,
            "commit_executed": False,
            "push_executed": False,
            "merge_executed": False,
            "shell_passthrough_used": False,
        },
        executable=False,
    )
