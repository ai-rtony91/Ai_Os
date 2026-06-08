"""Classify Codex final responses into evidence fields."""

from __future__ import annotations

import re
from typing import Any

from .models import Classification, ParsedResult, ResultStatus

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

SECRET_PATTERNS = (
    "api key",
    "print token",
    "show token",
    "password",
    "private key",
    "seed phrase",
    "credential",
)

LIVE_TRADING_PATTERNS = (
    "broker",
    "oanda",
    "real order",
    "real webhook",
    "live trading",
    "live execution",
)


def classify_result(parsed: ParsedResult) -> Classification:
    raw_lower = parsed.raw_text.lower()
    status_text = parsed.sections.get("STATUS", "")
    status_upper = status_text.upper()
    blocked_reasons: list[str] = []
    risk_flags: list[str] = []

    files_changed = _extract_paths(parsed.sections.get("FILES CHANGED", ""))
    dirty_files = _extract_dirty(parsed.sections.get("REMAINING DIRTY FILES", ""))
    validation_results = _extract_validation(parsed.sections.get("VALIDATION", parsed.sections.get("WHAT WAS TESTED", "")))
    protected_actions = _detect_protected_actions(raw_lower)
    secret_risk = any(pattern in raw_lower for pattern in SECRET_PATTERNS)
    live_risk = any(pattern in raw_lower for pattern in LIVE_TRADING_PATTERNS)

    if secret_risk:
        blocked_reasons.append("SECRET_OR_CREDENTIAL_RISK")
        risk_flags.append("SECRET_OR_CREDENTIAL_RISK")
    if live_risk:
        blocked_reasons.append("BROKER_OR_LIVE_TRADING_RISK")
        risk_flags.append("BROKER_OR_LIVE_TRADING_RISK")

    validation_failed = any(item["status"] == "FAIL" for item in validation_results)
    if validation_failed:
        blocked_reasons.append("VALIDATION_FAILED")

    if protected_actions:
        risk_flags.append("PROTECTED_ACTION_REQUESTED")

    if "MISSING_STATUS_SECTION" in parsed.parse_warnings:
        status = ResultStatus.UNKNOWN
    elif "NEEDS_APPROVAL" in status_upper or protected_actions:
        status = ResultStatus.NEEDS_APPROVAL
    elif "BLOCKED" in status_upper:
        status = ResultStatus.BLOCKED
    elif "FAILED" in status_upper or validation_failed:
        status = ResultStatus.FAILED
    elif "DRY_RUN COMPLETE" in status_upper:
        status = ResultStatus.DRY_RUN_COMPLETE
    elif "COMPLETE" in status_upper:
        status = ResultStatus.COMPLETE
    else:
        status = ResultStatus.UNKNOWN

    if status == ResultStatus.BLOCKED and not blocked_reasons:
        blocked_reasons.append("BLOCKED_RESULT")
    if status == ResultStatus.FAILED and not blocked_reasons:
        blocked_reasons.append("FAILED_RESULT")

    approval_required = bool(protected_actions or secret_risk or live_risk)
    approval_status = "MISSING" if approval_required else "NOT_REQUIRED"
    commit_status = _commit_status(parsed.raw_text)
    push_status = _push_status(parsed.raw_text)
    dirty_state = _dirty_state(dirty_files, parsed.sections.get("REMAINING DIRTY FILES", ""))

    sos = status in {ResultStatus.BLOCKED, ResultStatus.NEEDS_APPROVAL} or secret_risk or live_risk
    if status == ResultStatus.FAILED:
        sos = True

    if sos and approval_required:
        wake_class = "APPROVAL_REQUIRED"
    elif sos and (secret_risk or live_risk):
        wake_class = "SAFETY_RISK"
    elif sos:
        wake_class = "BLOCKED_CONTINUATION"
    elif status in {ResultStatus.COMPLETE, ResultStatus.DRY_RUN_COMPLETE}:
        wake_class = "DISPLAY_ONLY"
    else:
        wake_class = "UNKNOWN"

    status_impact = {
        ResultStatus.COMPLETE: "DISPLAY_ONLY",
        ResultStatus.DRY_RUN_COMPLETE: "DISPLAY_ONLY",
        ResultStatus.NEEDS_APPROVAL: "APPROVAL_REQUIRED",
        ResultStatus.BLOCKED: "BLOCKS_CONTINUATION",
        ResultStatus.FAILED: "BLOCKS_CONTINUATION",
        ResultStatus.UNKNOWN: "OPERATOR_REVIEW",
    }[status]

    return Classification(
        status=status,
        status_impact=status_impact,
        blocked_reasons=_dedupe(blocked_reasons),
        risk_flags=_dedupe(risk_flags),
        files_changed=files_changed,
        validation_results=validation_results,
        dirty_files=dirty_files,
        dirty_state=dirty_state,
        commit_status=commit_status,
        push_status=push_status,
        approval_required=approval_required,
        approval_status=approval_status,
        protected_action_requested=bool(protected_actions),
        protected_actions=protected_actions,
        display_alert=True,
        sos_wake_required=sos,
        wake_class=wake_class,
        redaction_status="SECRET_RISK_BLOCKED" if secret_risk else "NO_SECRETS_DETECTED",
        secret_scan_status="SECRET_RISK_BLOCKED" if secret_risk else "NO_SECRETS_DETECTED",
        next_safe_action=_next_safe_action(parsed, status, approval_required),
    )


def _extract_paths(value: str) -> list[str]:
    paths: list[str] = []
    for line in value.splitlines():
        cleaned = line.strip().strip("-*` ")
        if not cleaned or cleaned.lower() in {"none", "no files changed"}:
            continue
        if "/" in cleaned or "\\" in cleaned or "." in cleaned:
            paths.append(cleaned)
    return paths


def _extract_dirty(value: str) -> list[str]:
    dirty: list[str] = []
    for line in value.splitlines():
        stripped = line.strip()
        if not stripped or stripped.lower() in {"none", "clean"}:
            continue
        match = re.match(r"^(M|\?\?|A|D|R)\s+(.+)$", stripped)
        dirty.append(match.group(2).strip() if match else stripped.strip("-*` "))
    return dirty


def _extract_validation(value: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for line in value.splitlines():
        stripped = line.strip().strip("-* ")
        if not stripped:
            continue
        lower = stripped.lower()
        status = "UNKNOWN"
        if "passed" in lower or "pass" in lower or "0" == lower[-1:]:
            status = "PASS"
        if "failed" in lower or "fail" in lower or "error" in lower:
            status = "FAIL"
        if "warning" in lower:
            status = "WARNING"
        if "not run" in lower or "unable to run" in lower:
            status = "NOT_RUN"
        results.append({"command": stripped, "status": status})
    return results


def _detect_protected_actions(raw_lower: str) -> list[str]:
    return [action for needle, action in PROTECTED_ACTIONS if needle in raw_lower]


def _commit_status(raw_text: str) -> str:
    upper = raw_text.upper()
    if "NO COMMIT" in upper:
        return "NO_COMMIT"
    if "COMMIT REQUEST" in upper or "COMMIT APPROVAL" in upper:
        return "COMMIT_REQUESTED"
    if re.search(r"\bCOMMIT\s+[0-9A-F]{7,40}\b", upper):
        return "COMMITTED"
    return "UNKNOWN"


def _push_status(raw_text: str) -> str:
    upper = raw_text.upper()
    if "NO PUSH" in upper:
        return "NO_PUSH"
    if "PUSH REQUEST" in upper or "PUSH APPROVAL" in upper:
        return "PUSH_REQUESTED"
    if "PUSHED" in upper:
        return "PUSHED"
    return "UNKNOWN"


def _dirty_state(dirty_files: list[str], dirty_section: str) -> str:
    if not dirty_section.strip():
        return "NOT_REPORTED"
    if not dirty_files or dirty_section.strip().lower() in {"none", "clean"}:
        return "CLEAN"
    lowered = dirty_section.lower()
    if "classified" in lowered or "existing" in lowered or "untracked" in lowered:
        return "DIRTY_KNOWN_CLASSIFIED"
    return "DIRTY_UNKNOWN"


def _next_safe_action(parsed: ParsedResult, status: ResultStatus, approval_required: bool) -> str:
    explicit = parsed.sections.get("SAFE NEXT COMMAND", parsed.sections.get("SAFE NEXT COMMAND OR PROMPT", "")).strip()
    if explicit:
        return explicit
    if approval_required:
        return "Request current-session Anthony approval for the exact protected action scope."
    if status in {ResultStatus.BLOCKED, ResultStatus.FAILED}:
        return "Stop and resolve the blocked or failed condition before continuing."
    return "Review normalized evidence before routing it to downstream display or supervisor layers."


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
