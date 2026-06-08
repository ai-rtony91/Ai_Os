"""Build non-executable Codex packet drafts for human review."""

from __future__ import annotations

from typing import Any


DEFAULT_FINAL_REPORT_FORMAT = [
    "SUMMARY:",
    "WHAT CHANGED:",
    "VALIDATION:",
    "SAFE NEXT COMMAND:",
    "STATUS:",
]


def build_packet_draft(
    repo_state: Any,
    mode: str = "DRY_RUN",
    lane: str = "FULL_OPERATOR_RELIEF_CLOSED_LOOP",
    worktree: str | None = None,
    allowed_paths: list[str] | None = None,
    forbidden_paths: list[str] | None = None,
    validator_chain: list[str] | None = None,
    stop_point: str = "Stop after validation and human-readable final report.",
    final_report_format: list[str] | None = None,
) -> dict[str, Any]:
    branch = getattr(repo_state, "branch", "")
    resolved_worktree = worktree or getattr(repo_state, "repo_root", "")
    allowed = allowed_paths or ["SET_BY_HUMAN_APPROVAL"]
    forbidden = forbidden_paths or ["SET_BY_HUMAN_APPROVAL"]
    validators = validator_chain or ["git status --short --branch", "relevant local validator", "git diff --check"]
    report_lines = final_report_format or DEFAULT_FINAL_REPORT_FORMAT

    draft_text = "\n".join(
        [
            "CODEX-ONLY PROMPT",
            "",
            "AI_OS EXECUTION TOKEN: PLACEHOLDER_REQUIRES_ANTHONY_APPROVAL",
            "AI_OS BOOTSTRAP REQUIRED: YES",
            "",
            f"MODE: {mode}",
            f"LANE: {lane}",
            f"WORKTREE: {resolved_worktree}",
            f"BRANCH: {branch}",
            "",
            "ALLOWED PATHS:",
            *[f"- {item}" for item in allowed],
            "",
            "FORBIDDEN PATHS:",
            *[f"- {item}" for item in forbidden],
            "",
            "VALIDATOR CHAIN:",
            *[f"- {item}" for item in validators],
            "",
            "STOP POINT:",
            stop_point,
            "",
            "FINAL REPORT FORMAT:",
            *report_lines,
            "",
            "DRAFT NOTICE:",
            "This draft is not executable until Anthony replaces the placeholder token and approves it.",
        ]
    )
    return {
        "mode": mode,
        "lane": lane,
        "worktree": resolved_worktree,
        "branch": branch,
        "allowed_paths": allowed,
        "forbidden_paths": forbidden,
        "validator_chain": validators,
        "stop_point": stop_point,
        "final_report_format": report_lines,
        "draft_text": draft_text,
        "human_review_required": True,
        "executable": False,
    }
