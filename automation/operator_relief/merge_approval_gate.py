"""Human-only merge readiness gate for Operator Relief v1."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .auto_commit_push_executor import FEATURE_BRANCH


MERGE_BLOCKED = "MERGE_BLOCKED"
MERGE_REQUIRES_APPROVAL = "MERGE_REQUIRES_APPROVAL"
MERGE_READY_FOR_HUMAN = "MERGE_READY_FOR_HUMAN"


@dataclass(frozen=True)
class MergeApprovalDecision:
    status: str
    reasons: list[str]
    source_branch: str
    target_branch: str
    human_approval_required: bool
    merge_executed: bool = False
    rebase_executed: bool = False
    force_push_executed: bool = False
    main_mutated: bool = False
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_merge_approval_gate(
    repo_state: Any,
    validators_passed: bool,
    pr_ready: bool,
    human_approval_present: bool = False,
    source_branch: str = FEATURE_BRANCH,
    target_branch: str = "main",
) -> MergeApprovalDecision:
    reasons: list[str] = []
    branch = getattr(repo_state, "branch", "")
    if branch != source_branch:
        reasons.append(f"Current branch must be {source_branch}.")
    if target_branch != "main":
        reasons.append("Only main-target readiness can be evaluated in v1.")
    if not validators_passed:
        reasons.append("Validators must pass before merge can be considered.")
    if not pr_ready:
        reasons.append("PR readiness evidence is required.")
    if getattr(repo_state, "dirty_state", "") == "DIRTY":
        reasons.append("Dirty worktree blocks merge readiness.")

    if reasons:
        return MergeApprovalDecision(
            status=MERGE_BLOCKED,
            reasons=reasons,
            source_branch=source_branch,
            target_branch=target_branch,
            human_approval_required=True,
        )

    if not human_approval_present:
        return MergeApprovalDecision(
            status=MERGE_REQUIRES_APPROVAL,
            reasons=["Human merge approval is required; no merge can execute in v1."],
            source_branch=source_branch,
            target_branch=target_branch,
            human_approval_required=True,
        )

    return MergeApprovalDecision(
        status=MERGE_READY_FOR_HUMAN,
        reasons=["Ready for human-controlled merge lane; v1 still executes no merge."],
        source_branch=source_branch,
        target_branch=target_branch,
        human_approval_required=True,
    )
