"""Pure vacation-mode watchdog heartbeat classification.

This module intentionally does not read files, write files, send notifications,
run git, call ADB, or contact external services. Callers provide observed state
as dictionaries and receive one heartbeat/status object.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


CLASSIFICATION_OK = "OK"
CLASSIFICATION_NON_SOS = "NON_SOS_ATTENTION"
CLASSIFICATION_SOS = "SOS_REQUIRED"

SECRET_LEAK = "secret/key/token leak"
LIVE_TRADING_RISK = "live broker/trading execution risk"
PROTECTED_GATE_BYPASS = "protected gate bypass"
MAIN_BRANCH_RISK = "main branch risk"
DATA_LOSS_RISK = "data loss risk"
REPO_CORRUPTION = "repo corruption"
VALIDATION_INVALIDATES_MERGE = "validator failure invalidates merge readiness"
SOS_NOTIFICATION_FAILURE = "notification failure defeats SOS-only vacation mode"

NON_SOS_STALE_QUEUE = "stale non-blocking queue item"
NON_SOS_DOCS_POLISH = "docs polish"
NON_SOS_NAMING_STYLE = "naming/style"
NON_SOS_OPTIONAL_REFACTOR = "optional refactor"
NON_SOS_STALE_REPORT = "stale but non-blocking report"
NON_SOS_TEST_COVERAGE = "non-critical test coverage improvement"
NON_SOS_FUTURE_NOTIFICATION = "future Telegram/Tasker work"
NON_SOS_MERGE_TIMING = "merge timing preference"

MINIMUM_HEARTBEAT_FIELDS = (
    "timestamp_utc",
    "repo_path",
    "branch",
    "git_clean",
    "upstream_state",
    "worker_last_seen",
    "queue_oldest_item_age",
    "queue_blocked_count",
    "lock_count",
    "stale_lock_count",
    "validator_status",
    "last_report_age",
    "approval_pending_count",
    "sos_pending_count",
    "notification_rail",
    "adb_sos_available",
    "trading_live_blocked",
    "secret_risk_status",
    "classification",
    "sos_required",
    "sos_findings",
    "non_sos_findings",
    "safe_next_action",
    "do_not_wake_reason",
)


def _state(mapping: dict[str, Any] | None) -> dict[str, Any]:
    return dict(mapping or {})


def _flag(mapping: dict[str, Any], *names: str) -> bool:
    return any(bool(mapping.get(name)) for name in names)


def _value(mapping: dict[str, Any], name: str, default: Any) -> Any:
    value = mapping.get(name, default)
    return default if value is None else value


def _as_findings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value if str(item)]
    return [str(value)]


def _append_unique(findings: list[str], finding: str) -> None:
    if finding not in findings:
        findings.append(finding)


def _classify_sos(
    git_state: dict[str, Any],
    validator_state: dict[str, Any],
    approval_state: dict[str, Any],
    notification_state: dict[str, Any],
    safety_state: dict[str, Any],
) -> list[str]:
    findings: list[str] = []

    if _flag(safety_state, "secret_leak", "key_leak", "token_leak"):
        _append_unique(findings, SECRET_LEAK)
    if _flag(safety_state, "live_trading_risk", "live_broker_risk", "live_execution_risk"):
        _append_unique(findings, LIVE_TRADING_RISK)
    if _flag(safety_state, "protected_gate_bypass") or _flag(approval_state, "protected_gate_bypass"):
        _append_unique(findings, PROTECTED_GATE_BYPASS)
    if _flag(git_state, "main_branch_risk", "main_mutation_risk"):
        _append_unique(findings, MAIN_BRANCH_RISK)
    if _flag(safety_state, "data_loss_risk"):
        _append_unique(findings, DATA_LOSS_RISK)
    if _flag(git_state, "repo_corruption") or _flag(safety_state, "repo_corruption"):
        _append_unique(findings, REPO_CORRUPTION)
    if _flag(validator_state, "invalidates_merge_readiness"):
        _append_unique(findings, VALIDATION_INVALIDATES_MERGE)

    sos_pending = int(_value(approval_state, "sos_pending_count", 0))
    adb_available = bool(_value(notification_state, "adb_sos_available", True))
    if sos_pending > 0 and not adb_available:
        _append_unique(findings, SOS_NOTIFICATION_FAILURE)

    findings.extend(_as_findings(safety_state.get("sos_findings")))
    return findings


def _classify_non_sos(
    queue_state: dict[str, Any],
    evidence_state: dict[str, Any],
    safety_state: dict[str, Any],
) -> list[str]:
    findings: list[str] = []

    if _flag(queue_state, "stale_non_blocking", "below_stale_threshold"):
        _append_unique(findings, NON_SOS_STALE_QUEUE)
    if _flag(evidence_state, "stale_non_blocking_report"):
        _append_unique(findings, NON_SOS_STALE_REPORT)

    non_sos_flags = {
        "docs_polish": NON_SOS_DOCS_POLISH,
        "naming_style": NON_SOS_NAMING_STYLE,
        "optional_refactor": NON_SOS_OPTIONAL_REFACTOR,
        "test_coverage_improvement": NON_SOS_TEST_COVERAGE,
        "future_telegram_tasker": NON_SOS_FUTURE_NOTIFICATION,
        "merge_timing_preference": NON_SOS_MERGE_TIMING,
    }
    for flag, finding in non_sos_flags.items():
        if _flag(safety_state, flag):
            _append_unique(findings, finding)

    findings.extend(_as_findings(safety_state.get("non_sos_findings")))
    return findings


def build_vacation_heartbeat(
    *,
    repo_state: dict[str, Any] | None = None,
    worker_state: dict[str, Any] | None = None,
    queue_state: dict[str, Any] | None = None,
    lock_state: dict[str, Any] | None = None,
    git_state: dict[str, Any] | None = None,
    validator_state: dict[str, Any] | None = None,
    evidence_state: dict[str, Any] | None = None,
    approval_state: dict[str, Any] | None = None,
    notification_state: dict[str, Any] | None = None,
    safety_state: dict[str, Any] | None = None,
    timestamp_utc: str | None = None,
) -> dict[str, Any]:
    """Return one read-only vacation watchdog heartbeat object."""

    repo = _state(repo_state)
    worker = _state(worker_state)
    queue = _state(queue_state)
    locks = _state(lock_state)
    git = _state(git_state)
    validator = _state(validator_state)
    evidence = _state(evidence_state)
    approval = _state(approval_state)
    notification = _state(notification_state)
    safety = _state(safety_state)

    sos_findings = _classify_sos(git, validator, approval, notification, safety)
    non_sos_findings = _classify_non_sos(queue, evidence, safety)

    classification = CLASSIFICATION_OK
    if sos_findings:
        classification = CLASSIFICATION_SOS
    elif non_sos_findings:
        classification = CLASSIFICATION_NON_SOS

    sos_required = classification == CLASSIFICATION_SOS
    safe_next_action = (
        "Escalate SOS to the approved ADB wake rail; do not mutate repo state."
        if sos_required
        else "Continue read-only monitoring or wait for Anthony approval."
    )
    do_not_wake_reason = (
        ""
        if sos_required
        else "No confirmed SOS condition is present; keep Anthony asleep and retain read-only status."
    )

    return {
        "timestamp_utc": timestamp_utc or datetime.now(timezone.utc).isoformat(),
        "repo_path": _value(repo, "repo_path", ""),
        "branch": _value(git, "branch", _value(repo, "branch", "")),
        "git_clean": bool(_value(git, "git_clean", _value(repo, "git_clean", True))),
        "upstream_state": _value(git, "upstream_state", "UNKNOWN"),
        "worker_last_seen": _value(worker, "last_seen", _value(worker, "worker_last_seen", None)),
        "queue_oldest_item_age": _value(queue, "oldest_item_age", 0),
        "queue_blocked_count": int(_value(queue, "blocked_count", 0)),
        "lock_count": int(_value(locks, "lock_count", 0)),
        "stale_lock_count": int(_value(locks, "stale_lock_count", 0)),
        "validator_status": _value(validator, "status", "UNKNOWN"),
        "last_report_age": _value(evidence, "last_report_age", 0),
        "approval_pending_count": int(_value(approval, "pending_count", 0)),
        "sos_pending_count": int(_value(approval, "sos_pending_count", 0)),
        "notification_rail": _value(notification, "notification_rail", "ADB_SOS"),
        "adb_sos_available": bool(_value(notification, "adb_sos_available", False)),
        "trading_live_blocked": bool(_value(safety, "trading_live_blocked", True)),
        "secret_risk_status": _value(safety, "secret_risk_status", "CLEAR"),
        "classification": classification,
        "sos_required": sos_required,
        "sos_findings": sos_findings,
        "non_sos_findings": non_sos_findings,
        "safe_next_action": safe_next_action,
        "do_not_wake_reason": do_not_wake_reason,
    }
