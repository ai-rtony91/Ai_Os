"""Data models for the preview-only Codex result evidence adapter."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ResultStatus(str, Enum):
    COMPLETE = "COMPLETE"
    DRY_RUN_COMPLETE = "DRY_RUN_COMPLETE"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    NEEDS_APPROVAL = "NEEDS_APPROVAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ParsedResult:
    raw_text: str
    sections: dict[str, str]
    line_index: dict[str, int]
    parse_warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Classification:
    status: ResultStatus
    status_impact: str
    blocked_reasons: list[str]
    risk_flags: list[str]
    files_changed: list[str]
    validation_results: list[dict[str, Any]]
    dirty_files: list[str]
    dirty_state: str
    commit_status: str
    push_status: str
    approval_required: bool
    approval_status: str
    protected_action_requested: bool
    protected_actions: list[str]
    display_alert: bool
    sos_wake_required: bool
    wake_class: str
    redaction_status: str
    secret_scan_status: str
    next_safe_action: str


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
