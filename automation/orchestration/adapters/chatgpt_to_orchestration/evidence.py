"""AIOS_CLI_EVIDENCE.v1-compatible evidence builder."""

from __future__ import annotations

from typing import Any

from .models import ClassificationResult, ParsedPacket, RepoState, ValidationResult, utc_now_iso


def build_evidence(
    packet: ParsedPacket,
    validation: ValidationResult,
    classification: ClassificationResult,
    repo_state: RepoState,
    event_id: str,
) -> dict[str, Any]:
    return {
        "schema": "AIOS_CLI_EVIDENCE.v1",
        "event_id": event_id,
        "created_at_utc": utc_now_iso(),
        "source_party": "ChatGPT",
        "source_command": "ChatGptToOrchestrationAdapter validate packet",
        "packet_id": packet.sections.get("PACKET ID", ""),
        "lane": packet.sections.get("LANE", ""),
        "mode": packet.sections.get("MODE", ""),
        "repo_root": repo_state.repo_root,
        "branch": repo_state.branch,
        "worktree": repo_state.worktree,
        "git_status_short_branch": repo_state.git_status_short_branch,
        "dirty_state_class": repo_state.dirty_state_class,
        "allowed_paths": _lines(packet.sections.get("ALLOWED PATHS", "")),
        "forbidden_paths": _lines(packet.sections.get("FORBIDDEN PATHS", packet.sections.get("PROTECTED PATHS", ""))),
        "read_paths": ["AGENTS.md", "README.md", "WHITEPAPER.md"],
        "write_paths": [],
        "output_paths": [],
        "status": classification.status.value,
        "status_impact": "CURRENT_ACTIVE",
        "blocked_reasons": classification.blocked_reasons,
        "risk_flags": classification.risk_flags,
        "validator_chain": _lines(packet.sections.get("VALIDATOR CHAIN", "")),
        "validator_results": {
            "missing_fields": validation.missing_fields,
            "branch_worktree_validation": validation.branch_worktree_validation.value,
        },
        "approval_required": classification.approval_required,
        "approval_status": classification.approval_status.value,
        "approval_authority": packet.sections.get("APPROVAL AUTHORITY", ""),
        "protected_action_requested": classification.protected_action_requested,
        "protected_action_type": classification.protected_action_type,
        "display_alert": classification.display_alert,
        "sos_wake_required": classification.sos_wake_required,
        "wake_class": classification.wake_class,
        "redaction_status": classification.redaction_status,
        "secret_scan_status": classification.secret_scan_status,
        "executable": False,
        "next_safe_action": classification.next_safe_action,
        "stop_point": packet.sections.get("STOP POINT", ""),
    }


def _lines(value: str) -> list[str]:
    return [line.strip("-* \t") for line in value.splitlines() if line.strip("-* \t")]
