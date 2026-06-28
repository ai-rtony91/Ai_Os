"""Protected action boundary verifier for local-only review pathways."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

BOUNDARY_VERIFIER_VERSION = "1.0"

BOUNDARY_CLEAN = "BOUNDARY_CLEAN"
BOUNDARY_REPAIR_REQUIRED = "BOUNDARY_REPAIR_REQUIRED"
BOUNDARY_SAFETY_BLOCKED = "BOUNDARY_SAFETY_BLOCKED"
BOUNDARY_PROTECTED_AUTHORITY_REQUIRED = "BOUNDARY_PROTECTED_AUTHORITY_REQUIRED"

_FALSE_PROFIT_PATTERNS = [
    re.compile(r"(?i)\bguaranteed profit\b"),
    re.compile(r"(?i)\bno[- ]?risk profit\b"),
    re.compile(r"(?i)\binfinite profit\b"),
    re.compile(r"(?i)\bfree money\b"),
]

_BOUNDARY_PATTERNS = {
    "broker_api_enabled": re.compile(
        r"(?i)\bbroker[\s_-]?(api|connection|adapter)?\b.*\b(enabled|active|started|running|open)\b",
    ),
    "credential_access_granted": re.compile(
        r"(?i)\bcredential.*\b(granted|allowed|accessed|visible|read)\b",
    ),
    "demo_live_authorized": re.compile(r"(?i)\b(demo|live)\b.*\bauthorized\b"),
    "order_closed": re.compile(r"(?i)\border\b.*\b(closed|placed|submitted|executed|cancelled)\b"),
    "money_moved": re.compile(r"(?i)\bmoney\b.*\bmoved\b"),
    "production_activated": re.compile(r"(?i)\bproduction\b.*\b(activated|active)\b"),
    "scheduler_started": re.compile(r"(?i)\bscheduler\b.*\b(started|enabled|running)\b"),
    "daemon_started": re.compile(r"(?i)\bdaemon\b.*\b(started|enabled|running)\b"),
    "webhook_started": re.compile(r"(?i)\bwebhook\b.*\b(started|enabled|running|triggered)\b"),
}

_COMMAND_PATTERNS = [
    re.compile(r"(?i)\b(place|submit|send|execute)\s+(an?\s+)?order\b"),
    re.compile(r"(?i)\bbuy\b\s+\d+\s+\w+/\w+"),
    re.compile(r"(?i)\bsell\b\s+\d+\s+\w+/\w+"),
    re.compile(r"(?i)\bconnect\b.*\b(broker|api)\b"),
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _scan_text(text: str, *, source: str | None = None) -> dict[str, Any]:
    lowered = text.lower()
    findings: list[dict[str, str]] = []
    for label, pattern in _BOUNDARY_PATTERNS.items():
        for match in pattern.finditer(lowered):
            findings.append({"label": label, "value": match.group(0), "source": source or ""})
    for pattern in _COMMAND_PATTERNS:
        for match in pattern.finditer(lowered):
            findings.append({"label": "command_like_text", "value": match.group(0), "source": source or ""})
    safety = [match.group(0) for matcher in _FALSE_PROFIT_PATTERNS for match in matcher.finditer(lowered)]
    for value in safety:
        findings.append({"label": "false_profit_claim", "value": value, "source": source or ""})

    status = BOUNDARY_CLEAN
    if any(item["label"] in {"false_profit_claim"} for item in findings):
        status = BOUNDARY_SAFETY_BLOCKED
    elif any(
        item["label"] in {"broker_api_enabled", "credential_access_granted", "demo_live_authorized", "money_moved", "production_activated", "scheduler_started", "daemon_started", "webhook_started"}
        for item in findings
    ):
        status = BOUNDARY_PROTECTED_AUTHORITY_REQUIRED
    elif any(item["label"] == "command_like_text" for item in findings):
        status = BOUNDARY_REPAIR_REQUIRED

    return {
        "status": status,
        "matches": findings,
        "count": len(findings),
        "contains_false_profit": any(item["label"] == "false_profit_claim" for item in findings),
    }


def verify_protected_action_boundaries_text(
    text: str,
    *,
    source: str | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    result = _scan_text(text, source=source)
    status = result["status"]
    return {
        "verifier_version": BOUNDARY_VERIFIER_VERSION,
        "generated_at": _now_iso(),
        "status": status,
        "source": source,
        "match_count": result["count"],
        "findings": result["matches"],
        "strict_mode": bool(strict),
        "contains_false_profit_claim": result["contains_false_profit"],
    }


def _scan_payload(payload: Any, *, source: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    if isinstance(payload, str):
        findings.extend(_scan_text(payload, source=source)["matches"])
        return findings
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            findings.extend(_scan_payload(value, source=f"{source}.{key}"))
        return findings
    if isinstance(payload, list | tuple):
        for index, value in enumerate(payload):
            findings.extend(_scan_payload(value, source=f"{source}[{index}]"))
        return findings
    return []


def verify_protected_action_boundaries_payload(
    payload: Mapping[str, Any] | Any,
    *,
    source: str | None = None,
    strict: bool = False,
) -> dict[str, Any]:
    findings = _scan_payload(payload, source=source or "payload")
    status = BOUNDARY_CLEAN
    if any(item["label"] == "false_profit_claim" for item in findings):
        status = BOUNDARY_SAFETY_BLOCKED
    elif any(
        item["label"] in {"broker_api_enabled", "credential_access_granted", "demo_live_authorized", "money_moved", "production_activated", "scheduler_started", "daemon_started", "webhook_started"}
        for item in findings
    ):
        status = BOUNDARY_PROTECTED_AUTHORITY_REQUIRED
    elif any(item["label"] == "command_like_text" for item in findings):
        status = BOUNDARY_REPAIR_REQUIRED
    return {
        "verifier_version": BOUNDARY_VERIFIER_VERSION,
        "generated_at": _now_iso(),
        "status": status,
        "source": source or "payload",
        "match_count": len(findings),
        "findings": findings,
        "strict_mode": bool(strict),
        "contains_false_profit_claim": any(item["label"] == "false_profit_claim" for item in findings),
    }


def verify_protected_action_boundaries_files(
    paths: list[str] | tuple[str, ...] | set[str] | None,
    *,
    strict: bool = False,
) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    checked_files: list[str] = []
    if paths:
        for raw_path in paths:
            path = Path(raw_path)
            if path.exists() and path.is_file():
                checked_files.append(str(path))
                content = path.read_text(encoding="utf-8", errors="ignore")
                findings.extend(_scan_text(content, source=str(path))["matches"])
    status = BOUNDARY_CLEAN
    if any(item["label"] == "false_profit_claim" for item in findings):
        status = BOUNDARY_SAFETY_BLOCKED
    elif any(
        item["label"] in {
            "broker_api_enabled",
            "credential_access_granted",
            "demo_live_authorized",
            "money_moved",
            "production_activated",
            "scheduler_started",
            "daemon_started",
            "webhook_started",
        }
        for item in findings
    ):
        status = BOUNDARY_PROTECTED_AUTHORITY_REQUIRED
    elif any(item["label"] == "command_like_text" for item in findings):
        status = BOUNDARY_REPAIR_REQUIRED

    return {
        "verifier_version": BOUNDARY_VERIFIER_VERSION,
        "generated_at": _now_iso(),
        "status": status,
        "match_count": len(findings),
        "checked_files": checked_files,
        "paths": [str(path) for path in paths or []],
        "findings": findings,
        "strict_mode": bool(strict),
        "contains_false_profit_claim": any(item["label"] == "false_profit_claim" for item in findings),
    }


def protected_boundary_result_to_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# Forex Protected Action Boundary Verifier V1",
        f"Generated: {result.get('generated_at')}",
        f"Status: {result.get('status')}",
        f"Match count: {result.get('match_count', 0)}",
        "",
        "## Findings",
    ]
    for item in result.get("findings", []):
        if not isinstance(item, Mapping):
            continue
        lines.append(f"- {item.get('label')}: {item.get('value')} ({item.get('source', '')})")
    return "\n".join(lines)


def protected_boundary_result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "verifier_version": result.get("verifier_version", BOUNDARY_VERIFIER_VERSION),
        "generated_at": result.get("generated_at"),
        "status": result.get("status"),
        "match_count": int(result.get("match_count", 0)),
        "paths": list(result.get("paths", [])),
        "checked_files": list(result.get("checked_files", [])),
        "strict_mode": bool(result.get("strict_mode", False)),
        "contains_false_profit_claim": bool(result.get("contains_false_profit_claim", False)),
        "findings": [dict(item) for item in result.get("findings", [])],
    }


__all__ = [
    "BOUNDARY_CLEAN",
    "BOUNDARY_PROTECTED_AUTHORITY_REQUIRED",
    "BOUNDARY_REPAIR_REQUIRED",
    "BOUNDARY_SAFETY_BLOCKED",
    "BOUNDARY_VERIFIER_VERSION",
    "protected_boundary_result_to_jsonable_dict",
    "protected_boundary_result_to_markdown",
    "verify_protected_action_boundaries_files",
    "verify_protected_action_boundaries_payload",
    "verify_protected_action_boundaries_text",
]
