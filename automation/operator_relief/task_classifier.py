"""Classify one-shot operator relief state into local next actions."""

from __future__ import annotations

from pathlib import Path
from typing import Any


ROUTINE_SUCCESS = "routine_success"
REPO_STATE_PROBLEM = "repo_state_problem"
VALIDATOR_FAILURE = "validator_failure"
PACKET_MISSING_FIELDS = "packet_missing_fields"
BRANCH_MISMATCH = "branch_mismatch"
DIRTY_WORKTREE = "dirty_worktree"
BLOCKED_ACTION = "blocked_action"
SOS_WORTHY = "sos_worthy"

FORBIDDEN_ACTIONS = {
    "adb_wake",
    "auto_apply",
    "auto_commit",
    "auto_fix",
    "auto_push",
    "call_openai_api",
    "delete_files",
    "load_credentials",
    "merge_pr",
    "notify_live",
    "register_scheduler",
    "run_background_loop",
    "send_live_http",
    "start_night_supervisor",
    "stash_changes",
    "touch_broker_api",
    "touch_runtime_trading",
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

SOS_TRIGGERS = {
    "corrupt_state",
    "loop_dead",
    "scheduler_activation_attempt",
    "live_trading_attempt",
    "secret_exposure_risk",
}


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
    sos_triggers: list[str] | None = None,
) -> dict[str, Any]:
    reasons: list[str] = []
    classification = ROUTINE_SUCCESS
    needs_operator = False
    sos_worthy = False
    blocked_action = False

    if not getattr(repo_state, "agents_md_present", False) or not getattr(repo_state, "readme_present", False):
        classification = REPO_STATE_PROBLEM
        reasons.append("Required AI_OS authority files are missing.")
        needs_operator = True

    if expected_branch and getattr(repo_state, "branch", "") != expected_branch:
        classification = BRANCH_MISMATCH
        reasons.append(f"Observed branch {getattr(repo_state, 'branch', '')}; expected {expected_branch}.")
        needs_operator = True

    if getattr(repo_state, "dirty_state", "") == "DIRTY":
        classification = DIRTY_WORKTREE
        reasons.append("Working tree has dirty files.")
        needs_operator = True

    if missing_packet_fields:
        classification = PACKET_MISSING_FIELDS
        reasons.append("Packet is missing required fields: " + ", ".join(missing_packet_fields))
        needs_operator = True

    if validation_result and validation_result.get("success") is False:
        classification = VALIDATOR_FAILURE
        reasons.append("Validator failed: " + str(validation_result.get("message", "unknown failure")))
        needs_operator = True

    if requested_action in FORBIDDEN_ACTIONS:
        classification = BLOCKED_ACTION
        reasons.append(f"Requested action is blocked in one-shot operator relief: {requested_action}")
        needs_operator = True
        blocked_action = True

    protected_paths = [path for path in touched_paths or [] if _path_is_protected(path)]
    if protected_paths:
        classification = BLOCKED_ACTION
        reasons.append("Protected path touched: " + ", ".join(protected_paths))
        needs_operator = True
        blocked_action = True

    trigger_hits = sorted(set(sos_triggers or []) & SOS_TRIGGERS)
    if trigger_hits:
        classification = SOS_WORTHY
        reasons.append("SOS-worthy trigger detected: " + ", ".join(trigger_hits))
        needs_operator = True
        sos_worthy = True

    next_action = (
        "Stop and review local SOS evidence before any APPLY work."
        if sos_worthy
        else (
            "Review the local evidence record and decide the next bounded packet."
            if needs_operator
            else "No human action needed; routine state captured as local evidence."
        )
    )

    return {
        "classification": classification,
        "needs_operator": needs_operator,
        "sos_worthy": sos_worthy,
        "blocked_action": blocked_action,
        "safe_next_action": next_action,
        "reasons": reasons,
        "executable": False,
    }
