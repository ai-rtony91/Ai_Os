"""Build non-executable packet drafts for human review."""

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
    lane: str = "operator-relief-follow-up",
    allowed_paths: list[str] | None = None,
    forbidden_paths: list[str] | None = None,
    validator_chain: list[str] | None = None,
    stop_point: str = "Stop after validation and a human-readable final report.",
) -> dict[str, Any]:
    branch = getattr(repo_state, "branch", "")
    worktree = getattr(repo_state, "repo_root", "")
    allowed = allowed_paths or ["SET_BY_OPERATOR_APPROVAL"]
    forbidden = forbidden_paths or [
        "scheduler activation",
        "live SOS delivery",
        "ADB wake APPLY",
        "auto-commit",
        "auto-push",
        "broker/live trading/cloud/provider runtime",
        "secrets",
    ]
    validators = validator_chain or [
        "python automation/validators/aios_governance_validator.py --sample-check",
        "python automation/validators/aios_generated_output_policy_validator.py --sample-check --repo-root .",
        "git diff --check",
    ]

    draft_text = "\n".join(
        [
            "NON-EXECUTABLE AI_OS PACKET DRAFT",
            "",
            "This draft intentionally omits Codex routing and execution-token markers.",
            "Anthony must create a fresh approved packet before Codex may execute it.",
            "",
            f"MODE: {mode}",
            f"LANE: {lane}",
            f"WORKTREE: {worktree}",
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
            *DEFAULT_FINAL_REPORT_FORMAT,
        ]
    )
    return {
        "mode": mode,
        "lane": lane,
        "worktree": worktree,
        "branch": branch,
        "allowed_paths": allowed,
        "forbidden_paths": forbidden,
        "validator_chain": validators,
        "stop_point": stop_point,
        "draft_text": draft_text,
        "human_review_required": True,
        "executable": False,
    }
