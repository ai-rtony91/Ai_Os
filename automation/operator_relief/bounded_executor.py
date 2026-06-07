"""Bounded executor facade for Operator Relief v1.

V1 does not mutate repo files. It only runs approved internal validators,
builds non-executable packet and handoff summaries, and returns commit/push
recommendations after policy, approval, and validator gates pass.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .autonomy_approval_processor import AUTO_ALLOWED, classify_approval
from .autonomy_commit_push_gate import evaluate_commit_push_gate
from .autonomy_packet_generator import build_autonomy_packet_draft
from .autonomy_validator_orchestrator import build_validator_plan, run_validator_plan
from .full_auto_handoff import build_full_auto_handoff
from .full_auto_policy import FULL_AUTO_BLOCKED, FullAutoTask, evaluate_full_auto_policy


MODE_DRY_RUN = "DRY_RUN"
MODE_APPLY_SIMULATION = "APPLY_SIMULATION"
ALLOWED_MODES = {MODE_DRY_RUN, MODE_APPLY_SIMULATION}


@dataclass(frozen=True)
class BoundedExecutorReport:
    task_id: str
    mode: str
    status: str
    policy: dict[str, Any]
    approval: dict[str, Any]
    validator_plan: dict[str, Any]
    handoff_summary: dict[str, Any] | None
    packet_draft: dict[str, Any] | None
    commit_push_recommendation: dict[str, Any] | None
    actions_performed: list[str]
    safety: dict[str, bool]
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _base_safety() -> dict[str, bool]:
    return {
        "repo_files_mutated": False,
        "telemetry_files_written": False,
        "approval_queue_files_written": False,
        "openai_api_invoked": False,
        "codex_invoked": False,
        "daemon_started": False,
        "watcher_started": False,
        "service_started": False,
        "shell_passthrough_used": False,
        "protected_path_mutated": False,
        "commit_executed": False,
        "push_executed": False,
        "merge_executed": False,
        "apply_simulated_only": True,
    }


def _handoff_summary(handoff: Any) -> dict[str, Any]:
    return {
        "task_id": handoff.task_id,
        "mode": handoff.mode,
        "lane": handoff.lane,
        "branch": handoff.branch,
        "allowed_paths": handoff.allowed_paths,
        "forbidden_paths": handoff.forbidden_paths,
        "validator_chain": handoff.validator_chain,
        "human_review_required": handoff.human_review_required,
        "executable": False,
    }


def _stopped_report(
    task: FullAutoTask,
    mode: str,
    status: str,
    policy: Any,
    approval: Any,
    validator_plan: Any,
) -> BoundedExecutorReport:
    return BoundedExecutorReport(
        task_id=task.task_id,
        mode=mode,
        status=status,
        policy=policy.to_dict(),
        approval=approval.to_dict(),
        validator_plan=validator_plan.to_dict(),
        handoff_summary=None,
        packet_draft=None,
        commit_push_recommendation=None,
        actions_performed=[],
        safety=_base_safety(),
        executable=False,
    )


def run_bounded_executor(
    task: FullAutoTask,
    repo_state: Any,
    repo_root: Path | None = None,
    mode: str = MODE_DRY_RUN,
) -> BoundedExecutorReport:
    if mode not in ALLOWED_MODES:
        raise ValueError("Bounded executor mode must be DRY_RUN or APPLY_SIMULATION.")

    policy = evaluate_full_auto_policy(task, repo_state)
    approval = classify_approval(task, repo_state)
    plan = build_validator_plan(task)

    if policy.status == FULL_AUTO_BLOCKED:
        return _stopped_report(task, mode, "STOPPED_BLOCKED", policy, approval, plan)
    if approval.status != AUTO_ALLOWED:
        return _stopped_report(task, mode, "STOPPED_APPROVAL_REQUIRED", policy, approval, plan)
    if plan.status != "PLANNED":
        return _stopped_report(task, mode, "STOPPED_UNSUPPORTED_VALIDATOR", policy, approval, plan)

    validator_result = run_validator_plan(task, repo_root)
    actions = ["validator_plan_ran"]
    if validator_result.status != "PASSED":
        return BoundedExecutorReport(
            task_id=task.task_id,
            mode=mode,
            status="STOPPED_VALIDATOR_FAILED",
            policy=policy.to_dict(),
            approval=approval.to_dict(),
            validator_plan=validator_result.to_dict(),
            handoff_summary=None,
            packet_draft=None,
            commit_push_recommendation=None,
            actions_performed=actions,
            safety=_base_safety(),
            executable=False,
        )

    handoff = build_full_auto_handoff(task, policy, repo_state)
    packet = build_autonomy_packet_draft(
        task,
        repo_state,
        [f"{item.validator}:{item.path}" for item in validator_result.plan],
    )
    recommendation = evaluate_commit_push_gate(task, repo_state, validators_passed=True)
    actions.extend(["handoff_summary_built", "packet_draft_built", "commit_push_recommendation_built"])

    return BoundedExecutorReport(
        task_id=task.task_id,
        mode=mode,
        status="APPLY_SIMULATION_COMPLETE" if mode == MODE_APPLY_SIMULATION else "DRY_RUN_COMPLETE",
        policy=policy.to_dict(),
        approval=approval.to_dict(),
        validator_plan=validator_result.to_dict(),
        handoff_summary=_handoff_summary(handoff),
        packet_draft=packet.to_dict(),
        commit_push_recommendation=recommendation.to_dict(),
        actions_performed=actions,
        safety=_base_safety(),
        executable=False,
    )
