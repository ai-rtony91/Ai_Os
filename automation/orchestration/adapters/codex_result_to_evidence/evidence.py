"""AIOS_CLI_EVIDENCE.v1-compatible evidence builder for Codex results."""

from __future__ import annotations

import hashlib
from typing import Any

from .classifier import classify_result
from .models import ParsedResult, utc_now_iso
from .parser import parse_result


def run_preview(raw_text: str) -> dict[str, Any]:
    parsed = parse_result(raw_text)
    return build_evidence(parsed)


def build_evidence(parsed: ParsedResult) -> dict[str, Any]:
    classification = classify_result(parsed)
    created_at = utc_now_iso()
    raw_hash = hashlib.sha256(parsed.raw_text.encode("utf-8")).hexdigest()
    return {
        "schema": "AIOS_CLI_EVIDENCE.v1",
        "adapter_schema": "AIOS_CODEX_RESULT_EVIDENCE.v1",
        "event_id": f"codex_result_{created_at.replace(':', '').replace('-', '')}_{raw_hash[:8]}",
        "created_at_utc": created_at,
        "source_party": "Codex CLI Worker",
        "source_command": "codex_final_response_parse",
        "packet_id": "UNKNOWN",
        "lane": "UNKNOWN",
        "mode": "UNKNOWN",
        "repo_root": "C:\\Dev\\Ai.Os",
        "branch": "UNKNOWN",
        "worktree": "C:\\Dev\\Ai.Os",
        "git_status_short_branch": "",
        "dirty_state_class": classification.dirty_state,
        "allowed_paths": [],
        "forbidden_paths": [],
        "read_paths": [],
        "write_paths": classification.files_changed,
        "output_paths": classification.files_changed,
        "status": classification.status.value,
        "status_impact": classification.status_impact,
        "blocked_reasons": classification.blocked_reasons,
        "risk_flags": classification.risk_flags,
        "validator_chain": [],
        "validator_results": classification.validation_results,
        "approval_required": classification.approval_required,
        "approval_status": classification.approval_status,
        "approval_authority": "Anthony / AI_OS Owner",
        "protected_action_requested": classification.protected_action_requested,
        "protected_action_type": ",".join(classification.protected_actions),
        "protected_actions": classification.protected_actions,
        "display_alert": classification.display_alert,
        "sos_wake_required": classification.sos_wake_required,
        "wake_class": classification.wake_class,
        "redaction_status": classification.redaction_status,
        "secret_scan_status": classification.secret_scan_status,
        "freshness_status": "ADAPTER_PARSE_TIME_ONLY",
        "freshness_timestamp_utc": created_at,
        "freshness_basis": "ADAPTER_PARSE_TIME",
        "raw_input_hash": raw_hash,
        "raw_input_stored": False,
        "files_changed": classification.files_changed,
        "dirty_files": classification.dirty_files,
        "commit_status": classification.commit_status,
        "push_status": classification.push_status,
        "executable": False,
        "next_safe_action": classification.next_safe_action,
        "stop_point": "Stop after evidence preview emission. No queue, approval, telemetry, Codex, OpenAI, or subprocess action.",
    }
