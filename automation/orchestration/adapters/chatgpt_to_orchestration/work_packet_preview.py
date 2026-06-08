"""Canonical work packet preview builder."""

from __future__ import annotations

from typing import Any

from .models import ClassificationResult, ParsedPacket, RepoState, Status, ValidationResult


def build_work_packet_preview(
    packet: ParsedPacket,
    validation: ValidationResult,
    classification: ClassificationResult,
    repo_state: RepoState,
) -> dict[str, Any] | None:
    if classification.status in {Status.BLOCKED, Status.FAILED}:
        return None

    branch = packet.sections.get("BRANCH", "").strip()
    if branch == "resolve after preflight":
        branch = repo_state.branch

    return {
        "schema": "AIOS_CANONICAL_WORK_PACKET_PREVIEW.v1",
        "packet_id": packet.sections.get("PACKET ID", ""),
        "origin": "CHATGPT_GENERATED_PACKET",
        "adapter_name": "ChatGptToOrchestrationAdapter",
        "canonical_harness_owner": "AI_OS Orchestration Harness",
        "queue_owner": "automation/orchestration/work_packets/",
        "approval_owner": "automation/orchestration/approval_inbox/",
        "worker_owner": "automation/orchestration/workers/",
        "validator_owner": "automation/orchestration/validators/",
        "commit_package_owner": "automation/orchestration/commit_packages/",
        "lane": packet.sections.get("LANE", ""),
        "zone": packet.sections.get("ZONE", ""),
        "mode": packet.sections.get("MODE", ""),
        "branch": branch,
        "worktree": packet.sections.get("WORKTREE", ""),
        "allowed_paths": _lines(packet.sections.get("ALLOWED PATHS", "")),
        "forbidden_paths": _lines(packet.sections.get("FORBIDDEN PATHS", packet.sections.get("PROTECTED PATHS", ""))),
        "read_first_authority_files": _lines(packet.sections.get("READ-FIRST AUTHORITY FILES", "")),
        "validator_chain": _lines(packet.sections.get("VALIDATOR CHAIN", "")),
        "mission": packet.sections.get("MISSION", ""),
        "task_summary": packet.sections.get("TASK", packet.sections.get("MISSION", "")).strip().splitlines()[0:1],
        "strict_rules": _lines(packet.sections.get("STRICT RULES", "")),
        "stop_point": packet.sections.get("STOP POINT", ""),
        "approval_classification": "HUMAN_APPROVAL_REQUIRED" if classification.approval_required else "SAFE_NO_APPROVAL_REQUIRED",
        "protected_action_classification": classification.protected_action_type or "NOT_REQUESTED",
        "state_alignment": validation.branch_worktree_validation.value,
        "evidence_contract": "AIOS_CLI_EVIDENCE.v1-compatible",
        "executable": False,
        "preview_only": True,
    }


def _lines(value: str) -> list[str]:
    return [line.strip("-* \t") for line in value.splitlines() if line.strip("-* \t")]
