"""Commit/push recommendation gate for Operator Relief autonomy spine v1."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .full_auto_policy import FullAutoTask


COMMIT_RECOMMENDED = "COMMIT_RECOMMENDED"
PUSH_REQUIRES_HUMAN_APPROVAL = "PUSH_REQUIRES_HUMAN_APPROVAL"
BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class CommitPushGateDecision:
    status: str
    reasons: list[str]
    commit_executed: bool = False
    push_executed: bool = False
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_commit_push_gate(task: FullAutoTask, repo_state: Any, validators_passed: bool) -> CommitPushGateDecision:
    reasons: list[str] = []

    if getattr(repo_state, "dirty_state", "") == "DIRTY":
        reasons.append("Dirty worktree blocks autonomous commit/push recommendation.")
    if not validators_passed:
        reasons.append("Validators must pass before commit can be recommended.")
    if any(action in {"merge", "rebase", "force_push"} for action in task.requested_actions):
        reasons.append("Merge, rebase, and force-push are blocked.")
    if task.push_allowed or "push" in task.requested_actions:
        reasons.append("Push requires separate human approval in v1.")
        return CommitPushGateDecision(PUSH_REQUIRES_HUMAN_APPROVAL, reasons)
    if reasons:
        return CommitPushGateDecision(BLOCKED, reasons)
    return CommitPushGateDecision(COMMIT_RECOMMENDED, ["Commit could be recommended for human review; no commit was executed."])
