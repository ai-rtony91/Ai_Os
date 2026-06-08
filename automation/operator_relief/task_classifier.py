"""Classify operator-relief loop state into next safe actions."""

from __future__ import annotations

from pathlib import Path
from typing import Any


TASK_REPO_STATE_PROBLEM = "repo_state_problem"
TASK_VALIDATOR_FAILURE = "validator_failure"
TASK_PACKET_MISSING_FIELDS = "packet_missing_fields"
TASK_BRANCH_MISMATCH = "branch_mismatch"
TASK_DIRTY_WORKTREE = "dirty_worktree"
TASK_APPROVAL_NEEDED = "approval_needed"
TASK_SAFE_NEXT_ACTION = "safe_next_action"
TASK_BLOCKED_ACTION = "blocked_action"
TASK_ROUTINE_SUCCESS = "routine_success"

FORBIDDEN_ACTIONS = {
    "auto_apply",
    "auto_fix",
    "auto_commit",
    "auto_push",
    "call_codex",
    "call_openai_api",
    "touch_runtime_trading",
    "touch_broker_api",
    "load_credentials",
}

PROTECTED_PATH_PREFIXES = (
    "AGENTS.md",
    "README.md",
    "docs/governance/",
    "docs/security/",
    "docs/architecture/",
    "apps/",
    "services/",
    "automation/forex_engine/",
    "tests/forex_engine/",
)


def _path_is_protected(path_text: str) -> bool:
    normalized = Path(path_text).as_posix()
    return any(
        normalized == prefix.rstrip("/") or normalized.startswith(prefix)
        for prefix in PROTECTED_PATH_PREFIXES
    )


def classify_state(
    repo_state: Any,
    validation_result: dict[str, Any] | None = None,
    missing_packet_fields: list[str] | None = None,
    expected_branch: str | None = None,
    requested_action: str | None = None,
    touched_paths: list[str] | None = None,
) -> dict[str, Any]:
    reasons: list[str] = []
    classification = TASK_ROUTINE_SUCCESS
    approval_needed = False
    blocked_action = False

    if not getattr(repo_state, "agents_md_present", False) or not getattr(repo_state, "readme_present", False):
        classification = TASK_REPO_STATE_PROBLEM
        reasons.append("Required AI_OS authority files are missing.")
        approval_needed = True

    if expected_branch and getattr(repo_state, "branch", "") != expected_branch:
        classification = TASK_BRANCH_MISMATCH
        reasons.append(f"Observed branch {getattr(repo_state, 'branch', '')}; expected {expected_branch}.")
        approval_needed = True

    if getattr(repo_state, "dirty_state", "") == "DIRTY":
        classification = TASK_DIRTY_WORKTREE
        reasons.append("Working tree has dirty files.")
        approval_needed = True

    if missing_packet_fields:
        classification = TASK_PACKET_MISSING_FIELDS
        reasons.append("Packet is missing required fields: " + ", ".join(missing_packet_fields))
        approval_needed = True

    if validation_result and validation_result.get("success") is False:
        classification = TASK_VALIDATOR_FAILURE
        reasons.append("Validator failed: " + str(validation_result.get("message", "unknown failure")))
        approval_needed = True

    if requested_action in FORBIDDEN_ACTIONS:
        classification = TASK_BLOCKED_ACTION
        reasons.append(f"Requested action is blocked in operator-relief v1: {requested_action}")
        approval_needed = True
        blocked_action = True

    protected_paths = [path for path in touched_paths or [] if _path_is_protected(path)]
    if protected_paths:
        classification = TASK_BLOCKED_ACTION
        reasons.append("Protected path touched: " + ", ".join(protected_paths))
        approval_needed = True
        blocked_action = True

    if approval_needed and classification == TASK_ROUTINE_SUCCESS:
        classification = TASK_APPROVAL_NEEDED

    next_action = (
        "Review the approval queue item and decide the next APPLY packet."
        if approval_needed
        else "No human action needed; routine state captured as evidence."
    )

    return {
        "classification": classification,
        "approval_needed": approval_needed,
        "safe_next_action": next_action,
        "blocked_action": blocked_action,
        "reasons": reasons,
        "executable": False,
    }
