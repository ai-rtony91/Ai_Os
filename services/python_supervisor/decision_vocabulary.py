"""Shared AI_OS decision vocabulary for Python orchestration reports.

This module contains pure normalization and ranking helpers only. It performs
no file I/O, subprocess execution, network calls, Git operations, scheduling,
runtime control, packet movement, or approval mutation.
"""

from __future__ import annotations

from typing import Any


STATUS_PASS = "PASS"
STATUS_REVIEW = "REVIEW"
STATUS_BLOCKED = "BLOCKED"
STATUS_UNKNOWN = "UNKNOWN"
STATUS_NOT_RUN = "NOT_RUN"

SEVERITY_INFO = "INFO"
SEVERITY_REVIEW = "REVIEW"
SEVERITY_BLOCKED = "BLOCKED"
SEVERITY_UNKNOWN = "UNKNOWN"

APPROVAL_NONE = "none"
APPROVAL_REVIEW_ONLY = "review_only"
APPROVAL_HUMAN_BEFORE_MUTATION = "human_before_mutation"
APPROVAL_BLOCKED_UNTIL_FIXED = "blocked_until_fixed"

STOP_REPORT_ONLY = "report_only"
STOP_VALIDATION_ONLY = "validation_only"
STOP_HUMAN_REVIEW_REQUIRED = "human_review_required"
STOP_HUMAN_BEFORE_MUTATION = "human_before_mutation"
STOP_BLOCKED_UNTIL_FIXED = "blocked_until_fixed"

STATUS_ALIASES = {
    "PASS": STATUS_PASS,
    "SAFE_TO_COMMIT": STATUS_PASS,
    "SAFE_TO_PUSH": STATUS_PASS,
    "INFO": STATUS_PASS,
    "READY": STATUS_REVIEW,
    "RECOMMENDED": STATUS_REVIEW,
    "REVIEW": STATUS_REVIEW,
    "WARN": STATUS_REVIEW,
    "WARNING": STATUS_REVIEW,
    "REVIEW_REQUIRED": STATUS_REVIEW,
    "HUMAN_APPROVAL_REQUIRED": STATUS_REVIEW,
    "PENDING": STATUS_REVIEW,
    "PENDING_REVIEW": STATUS_REVIEW,
    "WAITING_APPROVAL": STATUS_REVIEW,
    "AWAITING_APPROVAL": STATUS_REVIEW,
    "FAIL": STATUS_BLOCKED,
    "FAILED": STATUS_BLOCKED,
    "BLOCKER": STATUS_BLOCKED,
    "BLOCKED": STATUS_BLOCKED,
    "STOP": STATUS_BLOCKED,
    "STOPPED": STATUS_BLOCKED,
    "ERROR": STATUS_BLOCKED,
    "MISSING": STATUS_UNKNOWN,
    "UNKNOWN": STATUS_UNKNOWN,
    "NO_ACTION": STATUS_UNKNOWN,
    "NOT_RUN": STATUS_NOT_RUN,
    "ASSIGNED":   STATUS_PASS,    # Worker attached — healthy routing state
    "COMPLETE":   STATUS_PASS,    # Terminal success — no escalation
    "VALIDATING": STATUS_REVIEW,  # In-flight — monitor, not block
    "STALE":      STATUS_REVIEW,  # Evidence stale — refresh required
}

# Supervisor-context status values from overnight_supervisor.schema.json.
# READY = system healthy. MUST NOT be mapped through STATUS_ALIASES.
# Use normalize_supervisor_status() wherever supervisor_status is produced/consumed.
SUPERVISOR_STATUS_PASSTHROUGH: frozenset[str] = frozenset({
    "READY", "REVIEW", "WARNING", "BLOCKED", "UNKNOWN"
})


def normalize_supervisor_status(value: object) -> str:
    """Normalize overnight_supervisor supervisor_status.

    Preserves READY as the healthy state — does NOT map READY to REVIEW.
    Use this instead of normalize_status() anywhere the value is
    overnight_supervisor.schema.json:supervisor_status.
    """
    token = _token(value)
    return token if token in SUPERVISOR_STATUS_PASSTHROUGH else STATUS_UNKNOWN


SEVERITY_ALIASES = {
    "INFO": SEVERITY_INFO,
    "PASS": SEVERITY_INFO,
    "READY": SEVERITY_REVIEW,
    "RECOMMENDED": SEVERITY_REVIEW,
    "WARN": SEVERITY_REVIEW,
    "WARNING": SEVERITY_REVIEW,
    "REVIEW": SEVERITY_REVIEW,
    "REVIEW_REQUIRED": SEVERITY_REVIEW,
    "HUMAN_APPROVAL_REQUIRED": SEVERITY_REVIEW,
    "PENDING": SEVERITY_REVIEW,
    "PENDING_REVIEW": SEVERITY_REVIEW,
    "FAIL": SEVERITY_BLOCKED,
    "FAILED": SEVERITY_BLOCKED,
    "BLOCKER": SEVERITY_BLOCKED,
    "BLOCKED": SEVERITY_BLOCKED,
    "STOP": SEVERITY_BLOCKED,
    "STOPPED": SEVERITY_BLOCKED,
    "ERROR": SEVERITY_BLOCKED,
    "UNKNOWN": SEVERITY_UNKNOWN,
    "MISSING": SEVERITY_UNKNOWN,
    "NO_ACTION": SEVERITY_UNKNOWN,
    "NOT_RUN": SEVERITY_UNKNOWN,
}

APPROVAL_CLASS_ALIASES = {
    "NONE": APPROVAL_NONE,
    "FALSE": APPROVAL_NONE,
    "NO": APPROVAL_NONE,
    "NOT_REQUIRED": APPROVAL_NONE,
    "REVIEW": APPROVAL_REVIEW_ONLY,
    "REVIEW_ONLY": APPROVAL_REVIEW_ONLY,
    "APPROVAL_REQUIRED": APPROVAL_HUMAN_BEFORE_MUTATION,
    "HUMAN_APPROVAL_REQUIRED": APPROVAL_HUMAN_BEFORE_MUTATION,
    "HUMAN_BEFORE_MUTATION": APPROVAL_HUMAN_BEFORE_MUTATION,
    "MUTATION_REQUIRED": APPROVAL_HUMAN_BEFORE_MUTATION,
    "TRUE": APPROVAL_HUMAN_BEFORE_MUTATION,
    "YES": APPROVAL_HUMAN_BEFORE_MUTATION,
    "BLOCKED": APPROVAL_BLOCKED_UNTIL_FIXED,
    "BLOCKED_UNTIL_FIXED": APPROVAL_BLOCKED_UNTIL_FIXED,
}

STOP_CONDITION_ALIASES = {
    "REPORT_ONLY": STOP_REPORT_ONLY,
    "REPORT_ONLY_NO_VALIDATOR_AUTO_RUN": STOP_REPORT_ONLY,
    "REPORT_ONLY_NO_MUTATION": STOP_REPORT_ONLY,
    "REPORT_ONLY_NO_PACKET_ADVANCEMENT": STOP_REPORT_ONLY,
    "REPORT_ONLY_NO_APPROVAL_MUTATION": STOP_REPORT_ONLY,
    "REPORT_ONLY_NO_STAGING_NO_COMMIT_NO_PUSH": STOP_REPORT_ONLY,
    "REPORT_ONLY_NO_APPLY_NO_COMMIT_NO_PUSH": STOP_REPORT_ONLY,
    "VALIDATION_ONLY": STOP_VALIDATION_ONLY,
    "HUMAN_REVIEW_REQUIRED": STOP_HUMAN_REVIEW_REQUIRED,
    "HUMAN_BEFORE_MUTATION": STOP_HUMAN_BEFORE_MUTATION,
    "BLOCKED_UNTIL_FIXED": STOP_BLOCKED_UNTIL_FIXED,
    "NO_COMMAND_RECOMMENDED": STOP_BLOCKED_UNTIL_FIXED,
    "STOP": STOP_BLOCKED_UNTIL_FIXED,
    "BLOCKED": STOP_BLOCKED_UNTIL_FIXED,
}

STATUS_RISK_RANK = {
    STATUS_BLOCKED: 4,
    STATUS_REVIEW: 3,
    STATUS_UNKNOWN: 2,
    STATUS_NOT_RUN: 1,
    STATUS_PASS: 0,
}

SEVERITY_RISK_RANK = {
    SEVERITY_BLOCKED: 3,
    SEVERITY_REVIEW: 2,
    SEVERITY_UNKNOWN: 1,
    SEVERITY_INFO: 0,
}


def _token(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    return str(value).strip().upper().replace("-", "_").replace(" ", "_")


def normalize_status(value: object) -> str:
    token = _token(value)
    if not token:
        return STATUS_UNKNOWN
    return STATUS_ALIASES.get(token, STATUS_UNKNOWN)


def normalize_severity(value: object) -> str:
    token = _token(value)
    if not token:
        return SEVERITY_UNKNOWN
    return SEVERITY_ALIASES.get(token, SEVERITY_UNKNOWN)


def normalize_approval_class(value: object) -> str:
    token = _token(value)
    if not token:
        return APPROVAL_NONE
    return APPROVAL_CLASS_ALIASES.get(token, APPROVAL_REVIEW_ONLY)


def normalize_stop_condition(value: object) -> str:
    token = _token(value)
    if not token:
        return STOP_REPORT_ONLY
    return STOP_CONDITION_ALIASES.get(token, STOP_HUMAN_REVIEW_REQUIRED)


def status_rank(value: object) -> int:
    return STATUS_RISK_RANK.get(normalize_status(value), STATUS_RISK_RANK[STATUS_UNKNOWN])


def severity_rank(value: object) -> int:
    return SEVERITY_RISK_RANK.get(
        normalize_severity(value),
        SEVERITY_RISK_RANK[SEVERITY_UNKNOWN],
    )


def choose_status(values: list[str], default: str = STATUS_UNKNOWN) -> str:
    if not values:
        return default
    return sorted(values, key=status_rank, reverse=True)[0]


def choose_severity(values: list[str], default: str = SEVERITY_UNKNOWN) -> str:
    if not values:
        return default
    return sorted(values, key=severity_rank, reverse=True)[0]


def requires_human_review(
    status: object,
    severity: object,
    approval_class: object | None = None,
) -> bool:
    normalized_status = normalize_status(status)
    normalized_severity = normalize_severity(severity)
    normalized_approval = normalize_approval_class(approval_class)

    return (
        normalized_status in {STATUS_REVIEW, STATUS_BLOCKED, STATUS_UNKNOWN}
        or normalized_severity in {SEVERITY_REVIEW, SEVERITY_BLOCKED, SEVERITY_UNKNOWN}
        or normalized_approval
        in {
            APPROVAL_REVIEW_ONLY,
            APPROVAL_HUMAN_BEFORE_MUTATION,
            APPROVAL_BLOCKED_UNTIL_FIXED,
        }
    )


def build_decision_summary(
    status: object,
    severity: object,
    approval_class: object | None = None,
    stop_condition: object | None = None,
) -> dict[str, Any]:
    normalized_status = normalize_status(status)
    normalized_severity = normalize_severity(severity)
    normalized_approval = normalize_approval_class(approval_class)
    normalized_stop = normalize_stop_condition(stop_condition)

    return {
        "status": normalized_status,
        "severity": normalized_severity,
        "approval_class": normalized_approval,
        "stop_condition_class": normalized_stop,
        "requires_human_review": requires_human_review(
            normalized_status,
            normalized_severity,
            normalized_approval,
        ),
        "status_rank": status_rank(normalized_status),
        "severity_rank": severity_rank(normalized_severity),
    }
