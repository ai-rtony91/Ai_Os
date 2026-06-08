"""Approval classification for Operator Relief autonomy spine v1."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .full_auto_policy import FullAutoTask, evaluate_full_auto_policy
from .task_classifier import PROTECTED_PATH_PREFIXES


AUTO_ALLOWED = "AUTO_ALLOWED"
APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class ApprovalDecision:
    status: str
    reasons: list[str]
    human_approval_required: bool
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _path_matches(path_text: str, pattern: str) -> bool:
    path = path_text.replace("\\", "/")
    prefix = pattern.replace("\\", "/").rstrip("/")
    return path == prefix or path.startswith(prefix + "/")


def _touches_protected_path(paths: list[str]) -> bool:
    return any(_path_matches(path, prefix) for path in paths for prefix in PROTECTED_PATH_PREFIXES)


def _has_valid_resume_approval(task: FullAutoTask) -> bool:
    metadata = task.metadata if isinstance(task.metadata, dict) else {}
    resume = metadata.get("approval_resume")
    if not isinstance(resume, dict):
        return False
    if resume.get("task_id") != task.task_id:
        return False
    if resume.get("decision") not in {"APPROVE", "CONTINUE_MISSION"}:
        return False
    return resume.get("human_approved") is True


def classify_approval(task: FullAutoTask, repo_state: Any) -> ApprovalDecision:
    policy = evaluate_full_auto_policy(task, repo_state)
    reasons = list(policy.reasons)

    if _touches_protected_path(task.changed_paths + task.allowed_paths):
        reasons.append("Protected paths are blocked for autonomous v1.")
        return ApprovalDecision(BLOCKED, reasons, True)

    blocked_actions = {"merge", "rebase", "force_push"}
    if any(action in blocked_actions for action in task.requested_actions):
        reasons.append("Merge, rebase, and force-push are blocked for autonomous v1.")
        return ApprovalDecision(BLOCKED, reasons, True)

    if policy.blocked:
        return ApprovalDecision(BLOCKED, reasons, True)

    resume_approved = _has_valid_resume_approval(task)
    protected_requested = (
        task.commit_allowed
        or task.push_allowed
        or any(action in {"commit", "push"} for action in task.requested_actions)
    )

    if (
        policy.requires_approval
        or getattr(repo_state, "dirty_state", "") == "DIRTY"
        or (task.expected_branch and getattr(repo_state, "branch", "") != task.expected_branch)
        or protected_requested
    ):
        if resume_approved and not protected_requested:
            reasons.append("Human approval resume evidence accepted for non-protected continuation.")
            return ApprovalDecision(AUTO_ALLOWED, reasons, False)
        if not reasons:
            reasons.append("Human approval is required by autonomous v1 safety policy.")
        return ApprovalDecision(APPROVAL_REQUIRED, reasons, True)

    return ApprovalDecision(AUTO_ALLOWED, reasons, False)
