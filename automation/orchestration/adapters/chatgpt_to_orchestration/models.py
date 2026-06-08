"""Data models for the preview-only ChatGPT to orchestration adapter."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Status(str, Enum):
    PREVIEW = "PREVIEW"
    BLOCKED = "BLOCKED"
    NEEDS_APPROVAL = "NEEDS_APPROVAL"
    FAILED = "FAILED"


class ApprovalStatus(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    REQUIRED = "REQUIRED"
    UNKNOWN = "UNKNOWN"


class BranchWorktreeValidation(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class RepoState:
    repo_root: str = "C:\\Dev\\Ai.Os"
    branch: str = "UNKNOWN"
    worktree: str = "C:\\Dev\\Ai.Os"
    git_status_short_branch: str = "UNKNOWN"
    dirty_state_class: str = "UNKNOWN"


@dataclass(frozen=True)
class ParsedPacket:
    raw_text: str
    first_line: str
    markers: set[str]
    sections: dict[str, str]
    line_index: dict[str, int]
    parse_warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ValidationResult:
    missing_fields: list[str] = field(default_factory=list)
    blocked_reasons: list[str] = field(default_factory=list)
    branch_worktree_validation: BranchWorktreeValidation = BranchWorktreeValidation.UNKNOWN

    @property
    def is_valid(self) -> bool:
        return not self.missing_fields and not self.blocked_reasons


@dataclass(frozen=True)
class ClassificationResult:
    status: Status
    blocked_reasons: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    placeholder_findings: list[str] = field(default_factory=list)
    approval_required: bool = False
    approval_status: ApprovalStatus = ApprovalStatus.NOT_REQUIRED
    protected_action_requested: bool = False
    protected_action_type: str = ""
    redaction_status: str = "NO_SECRETS_DETECTED"
    secret_scan_status: str = "NO_SECRETS_DETECTED"
    display_alert: bool = False
    sos_wake_required: bool = False
    wake_class: str = "NONE"
    next_safe_action: str = "Review the preview and approve a separate implementation packet only if needed."


@dataclass(frozen=True)
class AdapterResult:
    parsed: ParsedPacket
    validation: ValidationResult
    classification: ClassificationResult
    envelope: dict[str, Any]
    work_packet_preview: dict[str, Any] | None
    evidence: dict[str, Any]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
