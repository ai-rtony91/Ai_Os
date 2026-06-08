"""Canonical envelope preview builder."""

from __future__ import annotations

import hashlib
from typing import Any

from .evidence import build_evidence
from .models import ClassificationResult, ParsedPacket, RepoState, ValidationResult, utc_now_iso
from .work_packet_preview import build_work_packet_preview


def build_envelope(
    packet: ParsedPacket,
    validation: ValidationResult,
    classification: ClassificationResult,
    repo_state: RepoState,
) -> dict[str, Any]:
    event_id = _event_id(packet.raw_text)
    work_packet_preview = build_work_packet_preview(packet, validation, classification, repo_state)
    evidence = build_evidence(packet, validation, classification, repo_state, event_id)
    declared_branch = packet.sections.get("BRANCH", "")

    return {
        "schema": "AIOS_CHATGPT_TO_ORCHESTRATION_ENVELOPE.v1",
        "event_id": event_id,
        "created_at_utc": utc_now_iso(),
        "source_party": "ChatGPT",
        "adapter_name": "ChatGptToOrchestrationAdapter",
        "source_input_type": "CHATGPT_PACKET_TEXT",
        "source_hash": hashlib.sha256(packet.raw_text.encode("utf-8")).hexdigest(),
        "packet_id": packet.sections.get("PACKET ID", ""),
        "lane": packet.sections.get("LANE", ""),
        "zone": packet.sections.get("ZONE", ""),
        "mode": packet.sections.get("MODE", ""),
        "identity_marker": packet.sections.get("IDENTITY MARKER", ""),
        "supervisor_identity": packet.sections.get("SUPERVISOR IDENTITY", ""),
        "worker_identity": packet.sections.get("WORKER IDENTITY", ""),
        "approval_authority": packet.sections.get("APPROVAL AUTHORITY", ""),
        "repo_root": repo_state.repo_root,
        "worktree": packet.sections.get("WORKTREE", ""),
        "branch_declared": declared_branch,
        "branch_observed": repo_state.branch,
        "git_status_short_branch": repo_state.git_status_short_branch,
        "dirty_state_class": repo_state.dirty_state_class,
        "allowed_paths": _lines(packet.sections.get("ALLOWED PATHS", "")),
        "forbidden_paths": _lines(packet.sections.get("FORBIDDEN PATHS", packet.sections.get("PROTECTED PATHS", ""))),
        "read_first_authority_files": _lines(packet.sections.get("READ-FIRST AUTHORITY FILES", "")),
        "validator_chain": _lines(packet.sections.get("VALIDATOR CHAIN", "")),
        "mission": packet.sections.get("MISSION", ""),
        "stop_point": packet.sections.get("STOP POINT", ""),
        "final_report_format": packet.sections.get("FINAL RESPONSE FORMAT", ""),
        "status": classification.status.value,
        "status_impact": "CURRENT_ACTIVE",
        "blocked_reasons": classification.blocked_reasons,
        "risk_flags": classification.risk_flags,
        "missing_fields": validation.missing_fields,
        "placeholder_findings": classification.placeholder_findings,
        "branch_worktree_validation": validation.branch_worktree_validation.value,
        "approval_required": classification.approval_required,
        "approval_status": classification.approval_status.value,
        "protected_action_requested": classification.protected_action_requested,
        "protected_action_type": classification.protected_action_type,
        "redaction_status": classification.redaction_status,
        "paper_only": "trading" in packet.raw_text.lower(),
        "executable": False,
        "canonical_work_packet_preview": work_packet_preview,
        "evidence_output": evidence,
        "display_alert": classification.display_alert,
        "sos_wake_required": classification.sos_wake_required,
        "wake_class": classification.wake_class,
        "next_safe_action": classification.next_safe_action,
    }


def _event_id(raw_text: str) -> str:
    digest = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()[:12].upper()
    return f"AIOS-CHATGPT-ADAPTER-{digest}"


def _lines(value: str) -> list[str]:
    return [line.strip("-* \t") for line in value.splitlines() if line.strip("-* \t")]
