"""AI_OS dirty tree classifier.

Classifies live git dirty state without mutating the repo, printing secret
values, or granting APPLY/protected-action authority.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_DIRTY_TREE_CLASSIFIER_RESULT.v1"

CLEAN = "CLEAN"
SAFE_DIRTY = "SAFE_DIRTY"
SAFE_EVIDENCE_DIRTY = "SAFE_EVIDENCE_DIRTY"
SAFE_REPORT_DIRTY = "SAFE_REPORT_DIRTY"
SAFE_SANDBOX_PREVIEW_DIRTY = "SAFE_SANDBOX_PREVIEW_DIRTY"
REVIEW_REQUIRED_DIRTY = "REVIEW_REQUIRED_DIRTY"
PROTECTED_AUTHORITY_DIRTY = "PROTECTED_AUTHORITY_DIRTY"
SECURITY_SOS_DIRTY = "SECURITY_SOS_DIRTY"
UNKNOWN_DIRTY = "UNKNOWN_DIRTY"

SAFE_CLASSIFICATIONS = {
    SAFE_EVIDENCE_DIRTY,
    SAFE_REPORT_DIRTY,
    SAFE_SANDBOX_PREVIEW_DIRTY,
}

TEXT_SCAN_SUFFIXES = {
    ".cfg",
    ".csv",
    ".json",
    ".jsonl",
    ".log",
    ".md",
    ".ps1",
    ".py",
    ".text",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
MAX_CONTENT_SCAN_BYTES = 256 * 1024

SECRET_VALUE_PATTERNS = (
    re.compile(r"\bsk-proj-[A-Za-z0-9_-]{8,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)

CONTENT_INDICATORS = (
    ("api_key_or_token_pattern", re.compile(r"(api[_-]?key|access[_-]?token|auth[_-]?token|bearer)\s*[:=]", re.I)),
    ("private_key_pattern", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I)),
    ("credential_pattern", re.compile(r"\b(credential|credentials|password|client[_-]?secret|secret)\b\s*[:=]", re.I)),
    ("broker_oanda_live_trading", re.compile(r"\b(enable|execute|place|submit|connect|credential|credentials)\b.{0,80}\b(broker|oanda|live[_ -]?trading)\b", re.I | re.S)),
    ("real_order_execution", re.compile(r"\b(place|submit|execute|send|create)\b.{0,80}\b(real[_ -]?order|live[_ -]?order|order[_ -]?execution)\b", re.I | re.S)),
    ("webhook_production_deploy", re.compile(r"\b(real[_ -]?webhook|production[_ -]?deploy|deploy[_ -]?production|prod[_ -]?deploy|webhook[_ -]?url\s*[:=])\b", re.I)),
    ("dashboard_mutation_control", re.compile(r"\bdashboard[_ -]?(mutation|mutate|execute|write|control)\b", re.I)),
    ("scheduler_daemon_worker_launch", re.compile(r"\b(register[_ -]?scheduledtask|start[_ -]?scheduledtask|daemon[_ -]?activation|worker[_ -]?launch|launch[_ -]?worker)\b", re.I)),
)

PATH_INDICATORS = (
    ("env_file_or_env_pattern", re.compile(r"(^|/)\.env($|[./_-])", re.I)),
    ("api_key_or_token_pattern", re.compile(r"\b(api[_-]?key|token)\b", re.I)),
    ("private_key_pattern", re.compile(r"(^|/)(id_rsa|id_dsa|id_ed25519)$|(\.pem|\.key)$", re.I)),
    ("credential_pattern", re.compile(r"\b(credential|credentials|password|secret)\b", re.I)),
    ("broker_oanda_live_trading", re.compile(r"\b(broker|oanda|live[_ -]?trading)\b", re.I)),
    ("real_order_execution", re.compile(r"\b(real[_ -]?order|live[_ -]?order|order[_ -]?execution)\b", re.I)),
    ("webhook_production_deploy", re.compile(r"\b(webhook|production|prod[_ -]?deploy|deployment)\b", re.I)),
    ("dashboard_mutation_control", re.compile(r"\bdashboard\b.*\b(mutation|mutate|control|execute)\b", re.I)),
    ("scheduler_daemon_worker_launch", re.compile(r"\b(scheduler|daemon|worker[_ -]?launch|launch[_ -]?worker)\b", re.I)),
)

PROTECTED_AUTHORITY_PREFIXES = (
    ".github/",
    "docs/governance/",
    "docs/security/",
    "services/runtime/",
    "services/dispatcher/",
)
PROTECTED_AUTHORITY_FILES = {
    "AGENTS.md",
    "README.md",
    "WHITEPAPER.md",
    "RISK_POLICY.md",
    "SECURITY.md",
    "SOURCE_LOG.md",
    "ERROR_LOG.md",
    "HALLUCINATION_LOG.md",
    "AAR.md",
    "DAILY_REPORT.md",
    "ARCHITECTURE.md",
    "DEPLOYMENT.md",
}

SAFE_REPORT_PREFIXES = (
    "Reports/",
    "reports/",
)
SAFE_SANDBOX_PREFIXES = (
    "Reports/sandbox/",
    "reports/sandbox/",
    "automation/orchestration/work_packets/preview/",
)
SAFE_EVIDENCE_PREFIXES = (
    "telemetry/",
    "control/cycle/",
    "automation/orchestration/runtime/logs/",
    "automation/orchestration/validator_evidence/",
)
REVIEW_REQUIRED_PREFIXES = (
    "control/review_bridge/",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_path(path: str) -> str:
    return str(path or "").strip().replace("\\", "/")


def parse_git_status_lines(status_lines: list[str]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for raw_line in status_lines:
        line = str(raw_line or "").rstrip("\n")
        if not line or line.startswith("##"):
            continue
        git_code = line[:2].strip() or "??"
        path_text = line[3:].strip() if len(line) > 3 else ""
        if " -> " in path_text:
            path_text = path_text.rsplit(" -> ", 1)[-1].strip()
        normalized = _normalize_path(path_text.strip('"'))
        if normalized:
            entries.append({"git_code": git_code, "path": normalized})
    return entries


def collect_live_git_status(repo_root: str | Path) -> tuple[list[str], str | None]:
    root = Path(repo_root)
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "status", "--short", "--branch", "--untracked-files=all"],
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except Exception as exc:
        return [], f"git_status_failed:{exc.__class__.__name__}"
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if result.returncode != 0:
        return lines, "git_status_returned_nonzero"
    return lines, None


def _scan_content(repo_root: Path, rel_path: str) -> str:
    path = (repo_root / rel_path).resolve()
    try:
        if not path.is_file():
            return ""
        if path.stat().st_size > MAX_CONTENT_SCAN_BYTES:
            return ""
        if path.suffix.lower() not in TEXT_SCAN_SUFFIXES and path.name.lower() not in {".env"}:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def security_indicators_for_path(path: str, repo_root: str | Path | None = None) -> list[str]:
    normalized = _normalize_path(path)
    lowered = normalized.lower()
    indicators: list[str] = []
    for name, pattern in PATH_INDICATORS:
        if pattern.search(lowered):
            indicators.append(name)

    content = ""
    if repo_root is not None:
        content = _scan_content(Path(repo_root), normalized)
    if content:
        for pattern in SECRET_VALUE_PATTERNS:
            if pattern.search(content):
                indicators.append("secret_value_pattern")
                break
        for name, pattern in CONTENT_INDICATORS:
            if pattern.search(content):
                indicators.append(name)

    return _dedupe(indicators)


def _has_prefix(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def classify_dirty_path(path: str, git_code: str = "", repo_root: str | Path | None = None) -> dict[str, Any]:
    normalized = _normalize_path(path)
    indicators = security_indicators_for_path(normalized, repo_root=repo_root)
    if indicators:
        classification = SECURITY_SOS_DIRTY
        reason = "Dirty path or content matches reserved security escalation indicators."
    elif normalized in PROTECTED_AUTHORITY_FILES or _has_prefix(normalized, PROTECTED_AUTHORITY_PREFIXES):
        classification = PROTECTED_AUTHORITY_DIRTY
        reason = "Dirty file is protected governance, security, runtime, dispatcher, or repository authority."
    elif _has_prefix(normalized, SAFE_SANDBOX_PREFIXES):
        classification = SAFE_SANDBOX_PREVIEW_DIRTY
        reason = "Dirty file is generated sandbox or work-packet preview evidence."
    elif _has_prefix(normalized, SAFE_REPORT_PREFIXES):
        classification = SAFE_REPORT_DIRTY
        reason = "Dirty file is generated report evidence."
    elif _has_prefix(normalized, SAFE_EVIDENCE_PREFIXES):
        classification = SAFE_EVIDENCE_DIRTY
        reason = "Dirty file is generated local evidence."
    elif _has_prefix(normalized, REVIEW_REQUIRED_PREFIXES):
        classification = REVIEW_REQUIRED_DIRTY
        reason = "Dirty file is review-bridge material that requires operator or lane review."
    else:
        classification = UNKNOWN_DIRTY
        reason = "Dirty file is not in an approved generated evidence/report/sandbox preview root."

    safe_for_dry_run = classification in SAFE_CLASSIFICATIONS
    return {
        "path": normalized,
        "git_code": str(git_code or "").strip() or "??",
        "classification": classification,
        "reason": reason,
        "security_indicators": indicators,
        "safe_for_dry_run": safe_for_dry_run,
        "safe_for_apply": False,
        "next_safe_action": _next_action_for_classification(classification),
    }


def _next_action_for_classification(classification: str) -> str:
    if classification in SAFE_CLASSIFICATIONS:
        return "Continue READ_ONLY/DRY_RUN only; stop before APPLY or protected actions."
    if classification == SECURITY_SOS_DIRTY:
        return "Stop AI_OS continuation and escalate SOS without printing secret values."
    if classification == PROTECTED_AUTHORITY_DIRTY:
        return "Stop and get Human Owner review before continuing."
    if classification == REVIEW_REQUIRED_DIRTY:
        return "Review exact dirty file ownership before continuation."
    return "Review unknown dirty file before continuation."


def _overall_classification(dirty_files: list[dict[str, Any]]) -> str:
    if not dirty_files:
        return CLEAN
    classifications = {str(item.get("classification")) for item in dirty_files}
    if SECURITY_SOS_DIRTY in classifications:
        return SECURITY_SOS_DIRTY
    if PROTECTED_AUTHORITY_DIRTY in classifications:
        return PROTECTED_AUTHORITY_DIRTY
    if classifications.issubset(SAFE_CLASSIFICATIONS):
        return SAFE_DIRTY
    if UNKNOWN_DIRTY in classifications:
        return UNKNOWN_DIRTY
    return REVIEW_REQUIRED_DIRTY


def build_dirty_tree_classification(
    status_lines: list[str] | None = None,
    repo_root: str | Path | None = None,
    generated_utc: str | None = None,
) -> dict[str, Any]:
    root = Path(repo_root or Path.cwd()).resolve()
    git_error: str | None = None
    status_source = "provided_status_lines"
    if status_lines is None:
        status_lines, git_error = collect_live_git_status(root)
        status_source = "git_status_short_branch_untracked_all"

    entries = parse_git_status_lines(status_lines)
    dirty_files = [
        classify_dirty_path(entry["path"], git_code=entry["git_code"], repo_root=root)
        for entry in entries
    ]
    overall = _overall_classification(dirty_files)
    dirty_count = len(dirty_files)
    safe_for_dry_run = overall in {CLEAN, SAFE_DIRTY}
    safe_for_apply = dirty_count == 0 and git_error is None
    sos_required = overall == SECURITY_SOS_DIRTY
    protected_stop_required = overall == PROTECTED_AUTHORITY_DIRTY
    review_required = dirty_count > 0 and not safe_for_dry_run and not sos_required and not protected_stop_required

    if git_error:
        safe_for_dry_run = False
        safe_for_apply = False
        review_required = True
        if overall == CLEAN:
            overall = UNKNOWN_DIRTY

    counts = Counter(str(item["classification"]) for item in dirty_files)
    next_safe_action_by_overall = {
        CLEAN: "Working tree is clean; continue governed routing.",
        SAFE_DIRTY: "Continue READ_ONLY/DRY_RUN only; stop before APPLY or protected actions.",
        SECURITY_SOS_DIRTY: "Stop AI_OS continuation and escalate SOS without printing secret values.",
        PROTECTED_AUTHORITY_DIRTY: "Stop and get Human Owner review before continuing.",
        REVIEW_REQUIRED_DIRTY: "Review exact dirty files before continuation.",
        UNKNOWN_DIRTY: "Review unknown dirty files before continuation.",
    }

    return {
        "schema": SCHEMA,
        "generated_utc": generated_utc or utc_now(),
        "repo_root": str(root),
        "status_source": status_source,
        "git_status_error": git_error,
        "dirty_count": dirty_count,
        "overall_classification": overall,
        "safe_for_dry_run": safe_for_dry_run,
        "safe_for_apply": safe_for_apply,
        "sos_required": sos_required,
        "protected_stop_required": protected_stop_required,
        "review_required": review_required,
        "category_counts": {key: counts.get(key, 0) for key in sorted(SAFE_CLASSIFICATIONS | {REVIEW_REQUIRED_DIRTY, PROTECTED_AUTHORITY_DIRTY, SECURITY_SOS_DIRTY, UNKNOWN_DIRTY})},
        "dirty_files": dirty_files,
        "next_safe_action": next_safe_action_by_overall.get(overall, "Review dirty files before continuation."),
        "safety": {
            "prints_secret_values": False,
            "writes_files": False,
            "mutates_repo": False,
            "allows_apply": False,
            "allows_protected_action": False,
            "uses_live_git_status": status_source == "git_status_short_branch_untracked_all",
        },
    }


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Classify AI_OS dirty tree state without mutating the repo.")
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect.")
    args = parser.parse_args()
    result = build_dirty_tree_classification(repo_root=args.repo_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
