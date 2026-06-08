"""Risk and approval classification for preview-only adapter outputs."""

from __future__ import annotations

import re

from .models import ApprovalStatus, BranchWorktreeValidation, ClassificationResult, ParsedPacket, Status, ValidationResult

PLACEHOLDER_PATTERNS = (
    "@filename",
    "path/to/file",
    "[REAL-FILENAME]",
    "{feature}",
    "TODO",
    "TBD",
)

SECRET_PATTERNS = (
    "api key",
    "print token",
    "read token",
    "show token",
    "password",
    "private key",
    "seed phrase",
    "credential",
    "env dump",
    "environment variables",
)

LIVE_TRADING_PATTERNS = (
    "broker",
    "oanda",
    "real order",
    "real webhook",
    "live trading",
    "live execution",
)

PROTECTED_ACTIONS: tuple[tuple[str, str], ...] = (
    ("git add", "GIT_ADD"),
    ("git commit", "GIT_COMMIT"),
    ("git push", "GIT_PUSH"),
    ("gh pr create", "GH_PR_CREATE"),
    ("gh pr merge", "GH_PR_MERGE"),
    ("git merge", "GIT_MERGE"),
    ("git reset", "GIT_RESET"),
    ("git clean", "GIT_CLEAN"),
    ("branch deletion", "BRANCH_DELETE"),
)

PROTECTED_PATHS = (
    "automation/orchestration/work_packets/",
    "automation/orchestration/approval_inbox/",
    "automation/orchestration/workers/",
    "automation/orchestration/validators/",
    "automation/orchestration/commit_packages/",
    "AGENTS.md",
    "README.md",
    "WHITEPAPER.md",
    "tools/",
    "scripts/",
    "src/",
    "config/",
    "control/",
    "Relay/",
    ".github/",
    "schemas/",
    "telemetry/",
)


def classify_packet(packet: ParsedPacket, validation: ValidationResult) -> ClassificationResult:
    raw = packet.raw_text
    raw_lower = raw.lower()
    blocked = list(validation.blocked_reasons)
    risks: list[str] = []

    placeholders = [pattern for pattern in PLACEHOLDER_PATTERNS if pattern in raw]
    if placeholders:
        blocked.append("PLACEHOLDER_PRESENT")

    secret_risk = any(pattern in raw_lower for pattern in SECRET_PATTERNS)
    if secret_risk:
        blocked.append("SECRET_OR_CREDENTIAL_RISK")
        risks.append("SECRET_OR_CREDENTIAL_RISK")

    live_risk = any(pattern in raw_lower for pattern in LIVE_TRADING_PATTERNS)
    if live_risk:
        blocked.append("BROKER_OR_LIVE_TRADING_RISK")
        risks.append("BROKER_OR_LIVE_TRADING_RISK")

    if _creates_duplicate_authority(raw_lower):
        blocked.append("DUPLICATE_AUTHORITY_RISK")
        risks.append("DUPLICATE_AUTHORITY_RISK")

    protected_type = _detect_protected_action(raw_lower)
    protected_requested = bool(protected_type)
    approval_required = protected_requested
    approval_status = ApprovalStatus.REQUIRED if approval_required else ApprovalStatus.NOT_REQUIRED

    if _targets_protected_path(packet):
        blocked.append("FORBIDDEN_PATH_TARGETED")
        risks.append("FORBIDDEN_PATH_TARGETED")

    if validation.missing_fields:
        blocked.append("MISSING_IDENTITY_FIELD")

    if validation.branch_worktree_validation == BranchWorktreeValidation.FAIL:
        blocked.append("AIOS-PROMPT-AUTH-STATE-MISMATCH")

    blocked = _dedupe(blocked)
    risks = _dedupe(risks)

    if blocked:
        status = Status.BLOCKED
        display_alert = True
        sos = bool(secret_risk or live_risk or validation.branch_worktree_validation == BranchWorktreeValidation.FAIL)
        wake_class = "SOS" if sos else "REVIEW_ONLY"
        next_action = "Generate a complete tokenized packet with observed state, exact paths, validators, approval authority, and stop point."
    elif approval_required:
        status = Status.NEEDS_APPROVAL
        display_alert = True
        sos = True
        wake_class = "SOS"
        next_action = "Request current-session Anthony approval for the exact protected action scope."
    else:
        status = Status.PREVIEW
        display_alert = False
        sos = False
        wake_class = "NONE"
        next_action = "Review the preview and approve a separate implementation packet only if needed."

    return ClassificationResult(
        status=status,
        blocked_reasons=blocked,
        risk_flags=risks,
        placeholder_findings=placeholders,
        approval_required=approval_required,
        approval_status=approval_status,
        protected_action_requested=protected_requested,
        protected_action_type=protected_type,
        redaction_status="SECRET_RISK_BLOCKED" if secret_risk else "NO_SECRETS_DETECTED",
        secret_scan_status="SECRET_RISK_BLOCKED" if secret_risk else "NO_SECRETS_DETECTED",
        display_alert=display_alert,
        sos_wake_required=sos,
        wake_class=wake_class,
        next_safe_action=next_action,
    )


def _detect_protected_action(raw_lower: str) -> str:
    for needle, action_type in PROTECTED_ACTIONS:
        if needle in raw_lower:
            return action_type
    return ""


def _targets_protected_path(packet: ParsedPacket) -> bool:
    allowed = packet.sections.get("ALLOWED PATHS", "")
    task_text = "\n".join(
        packet.sections.get(name, "")
        for name in ("TASK", "MISSION", "ALLOWED PATHS")
    )
    for path in PROTECTED_PATHS:
        if path in allowed:
            return True
        if re.search(rf"(create|edit|write|modify).*{re.escape(path)}", task_text, re.IGNORECASE):
            return True
    return False


def _creates_duplicate_authority(raw_lower: str) -> bool:
    duplicate_terms = (
        "new approval authority",
        "new queue authority",
        "new governance authority",
        "new bridge head",
        "create a new bridge",
    )
    return any(term in raw_lower for term in duplicate_terms)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
