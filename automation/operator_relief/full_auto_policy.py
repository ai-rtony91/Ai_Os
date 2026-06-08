"""Full-Auto eligibility policy for AI_OS Operator Relief.

This module decides whether a task may be handed to a future Codex Full-Auto
executor. It does not invoke Codex, mutate files, commit, push, or merge.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .task_classifier import PROTECTED_PATH_PREFIXES
from .validator_router import select_validator


FULL_AUTO_ALLOWED = "FULL_AUTO_ALLOWED"
FULL_AUTO_REQUIRES_APPROVAL = "FULL_AUTO_REQUIRES_APPROVAL"
FULL_AUTO_BLOCKED = "FULL_AUTO_BLOCKED"

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_CRITICAL = "CRITICAL"

BLOCKED_PATH_KEYWORDS = (
    ".env",
    "secrets/",
    "credentials/",
    "broker",
    "api/",
    "live-trading",
    "live_trading",
    "order_execution",
)


@dataclass(frozen=True)
class FullAutoTask:
    task_id: str
    description: str
    allowed_paths: list[str]
    forbidden_paths: list[str]
    changed_paths: list[str]
    requested_actions: list[str]
    validator_targets: list[str]
    expected_branch: str | None = None
    risk_tier: str = RISK_LOW
    live_trading: bool = False
    secrets: bool = False
    broker_api: bool = False
    commit_allowed: bool = False
    push_allowed: bool = False
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FullAutoPolicyDecision:
    status: str
    risk_tier: str
    reasons: list[str]
    allowed: bool
    requires_approval: bool
    blocked: bool
    notification_required: bool
    evidence_required: bool
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize(path_text: str) -> str:
    return Path(path_text).as_posix()


def _path_matches(path_text: str, pattern: str) -> bool:
    path = _normalize(path_text)
    prefix = _normalize(pattern).rstrip("/")
    if prefix.endswith("**"):
        prefix = prefix[:-2].rstrip("/")
    return path == prefix or path.startswith(prefix + "/")


def _any_path_matches(paths: list[str], patterns: list[str]) -> bool:
    return any(_path_matches(path, pattern) for path in paths for pattern in patterns)


def _touches_protected_path(paths: list[str]) -> bool:
    return any(_path_matches(path, prefix) for path in paths for prefix in PROTECTED_PATH_PREFIXES)


def _touches_blocked_keyword(paths: list[str]) -> bool:
    normalized = [_normalize(path).lower() for path in paths]
    return any(keyword in path for path in normalized for keyword in BLOCKED_PATH_KEYWORDS)


def _validators_available(targets: list[str]) -> bool:
    return all(select_validator(target) != "unsupported_extension" for target in targets)


def evaluate_full_auto_policy(task: FullAutoTask, repo_state: Any) -> FullAutoPolicyDecision:
    reasons: list[str] = []
    status = FULL_AUTO_ALLOWED
    blocked = False
    requires_approval = False

    if task.live_trading:
        reasons.append("Live trading is blocked.")
        blocked = True
    if task.secrets:
        reasons.append("Secret or credential handling is blocked.")
        blocked = True
    if task.broker_api:
        reasons.append("Broker/API/order execution is blocked.")
        blocked = True
    touched_scope = task.allowed_paths + task.changed_paths + task.validator_targets + task.requested_actions
    if _touches_blocked_keyword(touched_scope):
        reasons.append("Path scope includes blocked runtime, secret, broker, API, or live-trading keyword.")
        blocked = True
    if not _validators_available(task.validator_targets):
        reasons.append("One or more validator targets have no v1 validator.")
        blocked = True
    if not task.allowed_paths:
        reasons.append("Allowed paths are required.")
        blocked = True
    if not task.forbidden_paths:
        reasons.append("Forbidden paths are required.")
        blocked = True
    if _any_path_matches(task.changed_paths, task.forbidden_paths):
        reasons.append("Changed path overlaps forbidden paths.")
        blocked = True

    if getattr(repo_state, "dirty_state", "") == "DIRTY":
        reasons.append("Dirty worktree requires human approval.")
        requires_approval = True
    if task.expected_branch and getattr(repo_state, "branch", "") != task.expected_branch:
        reasons.append("Branch mismatch requires human approval.")
        requires_approval = True
    if task.risk_tier in {RISK_HIGH, RISK_CRITICAL}:
        reasons.append("High or critical risk requires human approval.")
        requires_approval = True
    if _touches_protected_path(task.changed_paths):
        reasons.append("Protected path change requires human approval.")
        requires_approval = True
    if task.commit_allowed:
        reasons.append("Commit request requires human approval.")
        requires_approval = True
    if task.push_allowed or "push" in task.requested_actions:
        reasons.append("Push request requires human approval.")
        requires_approval = True
    if "merge" in task.requested_actions or "rebase" in task.requested_actions or "force_push" in task.requested_actions:
        reasons.append("Merge, rebase, and force-push requests are not allowed for Full-Auto handoff.")
        blocked = True

    if blocked:
        status = FULL_AUTO_BLOCKED
    elif requires_approval:
        status = FULL_AUTO_REQUIRES_APPROVAL

    return FullAutoPolicyDecision(
        status=status,
        risk_tier=task.risk_tier,
        reasons=reasons,
        allowed=status == FULL_AUTO_ALLOWED,
        requires_approval=status == FULL_AUTO_REQUIRES_APPROVAL,
        blocked=status == FULL_AUTO_BLOCKED,
        notification_required=status != FULL_AUTO_ALLOWED,
        evidence_required=True,
        executable=False,
    )
