"""Pure helpers for AI_OS 12-hour vacation-mode trial classification.

This module does not run the trial loop, write files, send notifications, run
ADB, or mutate git state. It classifies observed state provided by a caller.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import PurePosixPath
from typing import Any


CLASSIFICATION_OK = "OK"
CLASSIFICATION_NON_SOS = "NON_SOS_ATTENTION"
CLASSIFICATION_SOS = "SOS_REQUIRED"

APPROVED_TRIAL_OUTPUT_PREFIXES = (
    "Reports/vacation_candidate/12_hour_trial/",
    "telemetry/operator_relief/12_hour_trial/",
)


@dataclass(frozen=True)
class DirtyScopeReport:
    git_clean: bool
    approved_evidence_only: bool
    approved_paths: tuple[str, ...]
    unauthorized_paths: tuple[str, ...]
    raw_status_lines: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ValidatorResult:
    name: str
    exit_code: int
    output: str = ""
    wrapper_error: str = ""

    @property
    def passed(self) -> bool:
        return self.exit_code == 0 and not self.wrapper_error

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["passed"] = self.passed
        return payload


def _normalize_path(path: str) -> str:
    normalized = path.strip().strip('"').replace("\\", "/")
    return PurePosixPath(normalized).as_posix()


def _path_from_status_line(line: str) -> str:
    text = line.rstrip()
    if not text or text.startswith("##"):
        return ""
    if " -> " in text:
        text = text.rsplit(" -> ", 1)[-1]
    if len(text) >= 3 and text[2] == " ":
        return _normalize_path(text[3:])
    return _normalize_path(text)


def is_approved_trial_output(path: str) -> bool:
    normalized = _normalize_path(path)
    return any(
        normalized == prefix.rstrip("/") or normalized.startswith(prefix)
        for prefix in APPROVED_TRIAL_OUTPUT_PREFIXES
    )


def classify_dirty_scope(status_lines: list[str] | tuple[str, ...]) -> DirtyScopeReport:
    approved: list[str] = []
    unauthorized: list[str] = []
    raw_dirty: list[str] = []

    for line in status_lines:
        path = _path_from_status_line(line)
        if not path:
            continue
        raw_dirty.append(line)
        if is_approved_trial_output(path):
            approved.append(path)
        else:
            unauthorized.append(path)

    return DirtyScopeReport(
        git_clean=not raw_dirty,
        approved_evidence_only=bool(raw_dirty) and not unauthorized,
        approved_paths=tuple(approved),
        unauthorized_paths=tuple(unauthorized),
        raw_status_lines=tuple(raw_dirty),
    )


def classify_trial_start(
    *,
    status_lines: list[str] | tuple[str, ...],
    diff_check: ValidatorResult,
    branch: str,
    expected_branch: str = "feature/full-operator-relief-closed-loop-v1",
) -> dict[str, Any]:
    dirty = classify_dirty_scope(status_lines)
    sos_findings: list[str] = []
    non_sos_findings: list[str] = []

    if branch != expected_branch:
        sos_findings.append("main branch risk or branch mismatch")
    if dirty.unauthorized_paths:
        sos_findings.append("dirty branch state outside approved trial evidence only")
    if not diff_check.passed:
        sos_findings.append("git diff --check failed")
    if dirty.approved_evidence_only:
        non_sos_findings.append("ordinary heartbeat evidence writes inside approved output scope")

    classification = CLASSIFICATION_OK
    if sos_findings:
        classification = CLASSIFICATION_SOS
    elif non_sos_findings:
        classification = CLASSIFICATION_NON_SOS

    sos_required = classification == CLASSIFICATION_SOS
    return {
        "classification": classification,
        "sos_required": sos_required,
        "sos_findings": sos_findings,
        "non_sos_findings": non_sos_findings,
        "git_clean": dirty.git_clean,
        "approved_evidence_only": dirty.approved_evidence_only,
        "approved_dirty_paths": list(dirty.approved_paths),
        "unauthorized_dirty_paths": list(dirty.unauthorized_paths),
        "validator_status": "PASS" if diff_check.passed else "FAIL",
        "safe_next_action": (
            "Stop trial and inspect SOS condition; do not mutate repo state."
            if sos_required
            else "Continue evidence-only monitoring."
        ),
        "do_not_wake_reason": (
            ""
            if sos_required
            else "Only approved trial evidence output is dirty; no confirmed SOS condition is present."
        ),
    }
