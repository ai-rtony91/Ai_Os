"""Non-executing Full-Auto handoff packet builder."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .full_auto_policy import FULL_AUTO_ALLOWED, FullAutoPolicyDecision, FullAutoTask


DEFAULT_EVIDENCE_PATH = "telemetry/operator_relief/evidence.jsonl"
DEFAULT_NOTIFICATION_TRIGGERS = [
    "approval_needed",
    "validator_failed",
    "packet_invalid",
    "branch_mismatch",
    "dirty_worktree",
    "protected_path_touched",
    "forbidden_action_requested",
    "loop_failure",
]


@dataclass(frozen=True)
class FullAutoHandoffPacket:
    task_id: str
    mode: str
    lane: str
    worktree: str
    branch: str
    allowed_paths: list[str]
    forbidden_paths: list[str]
    validator_chain: list[str]
    stop_condition: str
    evidence_output_path: str
    notification_triggers: list[str]
    no_push_unless_approved: bool
    no_merge_unless_approved: bool
    human_review_required: bool
    executable: bool
    draft_text: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_full_auto_handoff(
    task: FullAutoTask,
    decision: FullAutoPolicyDecision,
    repo_state: Any,
    lane: str = "OPERATOR_RELIEF_FULL_AUTO_POLICY",
    evidence_output_path: str = DEFAULT_EVIDENCE_PATH,
) -> FullAutoHandoffPacket:
    branch = getattr(repo_state, "branch", "")
    worktree = getattr(repo_state, "repo_root", str(Path.cwd()))
    validators = [f"validate {target}" for target in task.validator_targets]
    stop_condition = "Stop after validators and evidence report. Do not commit, push, merge, or continue recursively."
    human_review_required = decision.status != FULL_AUTO_ALLOWED

    draft_lines = [
        "CODEX-ONLY PROMPT",
        "",
        "AI_OS EXECUTION TOKEN: PLACEHOLDER_REQUIRES_ANTHONY_APPROVAL",
        "AI_OS BOOTSTRAP REQUIRED: YES",
        "",
        "MODE: APPLY",
        f"LANE: {lane}",
        f"WORKTREE: {worktree}",
        f"BRANCH: {branch}",
        "",
        "FULL-AUTO POLICY STATUS:",
        decision.status,
        "",
        "ALLOWED PATHS:",
        *[f"- {path}" for path in task.allowed_paths],
        "",
        "FORBIDDEN PATHS:",
        *[f"- {path}" for path in task.forbidden_paths],
        "",
        "VALIDATOR CHAIN:",
        *[f"- {validator}" for validator in validators],
        "",
        "STOP CONDITION:",
        stop_condition,
        "",
        "EVIDENCE OUTPUT PATH:",
        evidence_output_path,
        "",
        "NOTIFICATION TRIGGER RULES:",
        *[f"- {trigger}" for trigger in DEFAULT_NOTIFICATION_TRIGGERS],
        "",
        "BOUNDARIES:",
        "- no push unless explicitly approved",
        "- no merge unless explicitly approved",
        "- no recursive Codex call",
        "- no daemon",
        "- no live trading, broker/API/order execution, or secrets",
        "",
        "DRAFT NOTICE:",
        "This handoff is non-executable scaffolding until Anthony approves it.",
    ]

    return FullAutoHandoffPacket(
        task_id=task.task_id,
        mode="APPLY",
        lane=lane,
        worktree=worktree,
        branch=branch,
        allowed_paths=task.allowed_paths,
        forbidden_paths=task.forbidden_paths,
        validator_chain=validators,
        stop_condition=stop_condition,
        evidence_output_path=evidence_output_path,
        notification_triggers=DEFAULT_NOTIFICATION_TRIGGERS,
        no_push_unless_approved=True,
        no_merge_unless_approved=True,
        human_review_required=human_review_required,
        executable=False,
        draft_text="\n".join(draft_lines),
    )
