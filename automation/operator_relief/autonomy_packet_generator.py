"""Non-executable packet generation for Operator Relief autonomy spine v1."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .full_auto_policy import FullAutoTask


FINAL_REPORT_FORMAT = [
    "SUMMARY:",
    "WHAT CHANGED:",
    "FILES CHANGED:",
    "VALIDATION:",
    "REMAINING DIRTY FILES:",
    "SAFE NEXT COMMAND:",
    "STATUS:",
]


@dataclass(frozen=True)
class AutonomyPacketDraft:
    task_id: str
    mode: str
    lane: str
    worktree: str
    branch: str
    allowed_paths: list[str]
    forbidden_paths: list[str]
    approval_authority: str
    validator_chain: list[str]
    stop_point: str
    final_report_format: list[str]
    draft_text: str
    executable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_autonomy_packet_draft(
    task: FullAutoTask,
    repo_state: Any,
    validator_chain: list[str],
    lane: str = "OPERATOR_RELIEF_AUTONOMY_SPINE_V1",
) -> AutonomyPacketDraft:
    worktree = getattr(repo_state, "repo_root", "")
    branch = getattr(repo_state, "branch", "")
    approval_authority = "Anthony / Human Owner approval required before APPLY, commit, push, merge, or protected action."
    stop_point = "Stop after DRY_RUN validation report. Do not commit, push, merge, call OpenAI, call Codex recursively, or start a daemon."

    lines = [
        "CODEX-ONLY PROMPT",
        "",
        "AI_OS EXECUTION TOKEN: PLACEHOLDER_REQUIRES_ANTHONY_APPROVAL",
        "AI_OS BOOTSTRAP REQUIRED: YES",
        "",
        "MODE: DRY_RUN",
        f"LANE: {lane}",
        f"WORKTREE: {worktree}",
        f"BRANCH: {branch}",
        "",
        "MISSION:",
        task.description,
        "",
        "ALLOWED PATHS:",
        *[f"- {path}" for path in task.allowed_paths],
        "",
        "FORBIDDEN PATHS:",
        *[f"- {path}" for path in task.forbidden_paths],
        "",
        "APPROVAL AUTHORITY:",
        approval_authority,
        "",
        "VALIDATOR CHAIN:",
        *[f"- {validator}" for validator in validator_chain],
        "",
        "STOP POINT:",
        stop_point,
        "",
        "FINAL REPORT FORMAT:",
        *FINAL_REPORT_FORMAT,
        "",
        "DRAFT NOTICE:",
        "This packet is non-executable authority until the Human Owner approves a complete APPLY packet.",
    ]

    return AutonomyPacketDraft(
        task_id=task.task_id,
        mode="DRY_RUN",
        lane=lane,
        worktree=worktree,
        branch=branch,
        allowed_paths=task.allowed_paths,
        forbidden_paths=task.forbidden_paths,
        approval_authority=approval_authority,
        validator_chain=validator_chain,
        stop_point=stop_point,
        final_report_format=FINAL_REPORT_FORMAT,
        draft_text="\n".join(lines),
        executable=False,
    )
