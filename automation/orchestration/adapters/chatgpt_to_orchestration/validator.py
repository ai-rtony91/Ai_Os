"""Validation rules for ChatGPT-generated AI_OS packet text."""

from __future__ import annotations

from .models import BranchWorktreeValidation, ParsedPacket, RepoState, ValidationResult

REQUIRED_FIELDS = {
    "identity_marker": ("IDENTITY MARKER",),
    "supervisor_identity": ("SUPERVISOR IDENTITY",),
    "packet_id": ("PACKET ID",),
    "lane": ("LANE",),
    "zone": ("ZONE",),
    "worker_identity": ("WORKER IDENTITY",),
    "mode": ("MODE",),
    "branch": ("BRANCH",),
    "worktree": ("WORKTREE",),
    "approval_authority": ("APPROVAL AUTHORITY",),
    "allowed_paths": ("ALLOWED PATHS",),
    "forbidden_paths": ("FORBIDDEN PATHS", "PROTECTED PATHS"),
    "validator_chain": ("VALIDATOR CHAIN",),
    "mission": ("MISSION",),
    "stop_point": ("STOP POINT",),
    "final_report_format": ("FINAL RESPONSE FORMAT",),
}


def _has_section(packet: ParsedPacket, names: tuple[str, ...]) -> bool:
    return any(packet.sections.get(name, "").strip() for name in names)


def validate_packet(packet: ParsedPacket, repo_state: RepoState | None = None) -> ValidationResult:
    missing: list[str] = []
    blocked: list[str] = []

    if packet.first_line != "CODEX-ONLY PROMPT":
        blocked.append("MISSING_ROUTING_MARKER")
    if "AI_OS EXECUTION TOKEN" not in packet.markers:
        blocked.append("MISSING_EXECUTION_TOKEN")
    if "AI_OS BOOTSTRAP REQUIRED" not in packet.markers:
        blocked.append("MISSING_BOOTSTRAP")

    for canonical_name, section_names in REQUIRED_FIELDS.items():
        if not _has_section(packet, section_names):
            missing.append(canonical_name)

    if not _validator_includes_state(packet):
        missing.append("preflight")

    branch_state = _validate_branch_worktree(packet, repo_state)
    if branch_state == BranchWorktreeValidation.FAIL:
        blocked.append("STATE_MISMATCH")

    return ValidationResult(
        missing_fields=sorted(set(missing)),
        blocked_reasons=_dedupe(blocked),
        branch_worktree_validation=branch_state,
    )


def _validate_branch_worktree(packet: ParsedPacket, repo_state: RepoState | None) -> BranchWorktreeValidation:
    if repo_state is None:
        return BranchWorktreeValidation.UNKNOWN

    declared_branch = packet.sections.get("BRANCH", "").strip()
    declared_worktree = packet.sections.get("WORKTREE", "").strip()

    if declared_worktree and declared_worktree != repo_state.worktree:
        return BranchWorktreeValidation.FAIL
    if declared_branch == "resolve after preflight":
        return BranchWorktreeValidation.PASS
    if declared_branch and declared_branch != repo_state.branch:
        return BranchWorktreeValidation.FAIL
    if declared_branch and declared_worktree:
        return BranchWorktreeValidation.PASS
    return BranchWorktreeValidation.UNKNOWN


def _validator_includes_state(packet: ParsedPacket) -> bool:
    validator_chain = packet.sections.get("VALIDATOR CHAIN", "").lower()
    return (
        "branch" in validator_chain
        and "worktree" in validator_chain
        or "confirm branch/worktree state" in validator_chain
        or "git status --short --branch" in validator_chain
    )


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
