"""Quality validation for owner evidence return payloads."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


OWNER_EVIDENCE_RETURN_VALIDATOR_VERSION = "1.0"

OWNER_RETURN_VALID = "OWNER_RETURN_VALID"
OWNER_RETURN_REPAIRABLE = "OWNER_RETURN_REPAIRABLE"
OWNER_RETURN_BLOCKED = "OWNER_RETURN_BLOCKED"
OWNER_RETURN_INVALID = "OWNER_RETURN_INVALID"

REQUIRED_SECTIONS = (
    "owner evidence return",
    "family",
    "sample count",
    "evidence location",
)

SENSITIVE_PATTERNS = [
    re.compile(r"(?im)\b(api[_-]?key|secret|password|access[_-]?token)\b"),
    re.compile(r"(?im)\baccount[_-]?id\s*[:=]\b"),
    re.compile(r"(?im)\bsession[_-]?id\s*[:=]\b"),
    re.compile(r"(?im)account[_-]?id\s*[:=]"),
]

BROKER_COMMAND_PATTERNS = [
    re.compile(r"(?im)\b(place|send|submit)\s+(an?\s+)?order\b"),
    re.compile(r"(?im)\bconnect\s+to\s+(oanda|broker)\b"),
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def scan_sensitive_patterns(text: str) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    for pattern in SENSITIVE_PATTERNS + BROKER_COMMAND_PATTERNS:
        for hit in pattern.finditer(text):
            matches.append({"pattern": pattern.pattern, "value": hit.group(0)})
    return matches


def validate_owner_evidence_return_text(
    text: str,
    *,
    strict: bool = False,
    min_sample: int = 30,
) -> dict[str, Any]:
    content = (text or "").strip()
    if not content:
        return {
            "validator_version": OWNER_EVIDENCE_RETURN_VALIDATOR_VERSION,
            "validation_timestamp": _now_iso(),
            "status": OWNER_RETURN_INVALID,
            "required_sections": list(REQUIRED_SECTIONS),
            "missing_sections": list(REQUIRED_SECTIONS),
            "sample_count": None,
            "sensitive_hits": [],
            "repair_instructions": ["add owner evidence return content for validation"],
            "owner_confirmation_required": strict,
        }

    lowered = content.lower()
    missing_sections = [
        section for section in REQUIRED_SECTIONS if section not in lowered
    ]
    sample_match = re.search(r"sample\s*count\s*[:=]\s*(\d+)", lowered)
    sample_count = int(sample_match.group(1)) if sample_match else None
    sensitive_hits = scan_sensitive_patterns(content)

    blockers: list[str] = []
    repair_instructions: list[str] = []
    status = OWNER_RETURN_VALID
    owner_confirmation_required = False
    if sensitive_hits:
        status = OWNER_RETURN_BLOCKED
        blockers.append("sensitive or command pattern detected")
        repair_instructions.append("remove sensitive lines and command text before owner review")
    elif sample_count is None:
        status = OWNER_RETURN_REPAIRABLE
        blockers.append("sample_count not present")
        repair_instructions.append("add explicit sample_count value")
    elif sample_count < min_sample:
        status = OWNER_RETURN_REPAIRABLE
        blockers.append(f"sample_count below minimum {min_sample}")
        repair_instructions.append("append additional local evidence samples")
    elif missing_sections:
        status = OWNER_RETURN_REPAIRABLE
        blockers.append("required evidence sections are missing")
        repair_instructions.append("include all required sections for deterministic validation")
    elif strict and "owner confirmation: confirmed" not in lowered:
        status = OWNER_RETURN_REPAIRABLE
        blockers.append("strict mode requires explicit owner confirmation")
        owner_confirmation_required = True
        repair_instructions.append("append owner_confirmation: confirmed")

    if status == OWNER_RETURN_VALID:
        repair_instructions.append("no repair action required")
    return {
        "validator_version": OWNER_EVIDENCE_RETURN_VALIDATOR_VERSION,
        "validation_timestamp": _now_iso(),
        "status": status,
        "required_sections": list(REQUIRED_SECTIONS),
        "missing_sections": missing_sections,
        "sample_count": sample_count,
        "sensitive_hits": sensitive_hits,
        "blockers": blockers,
        "repair_instructions": repair_instructions,
        "owner_confirmation_required": owner_confirmation_required or strict,
        "sample_limit": min_sample,
    }


def validate_owner_evidence_return_files(
    paths: Iterable[str | Path] | None,
    *,
    strict: bool = False,
    min_sample: int = 30,
) -> dict[str, Any]:
    if paths is None:
        paths = []
    results: list[dict[str, Any]] = []
    for raw_path in list(paths):
        payload_path = Path(raw_path)
        text = payload_path.read_text(encoding="utf-8", errors="ignore")
        result = validate_owner_evidence_return_text(text, strict=strict, min_sample=min_sample)
        result["path"] = str(payload_path)
        results.append(result)

    if not results:
        status = OWNER_RETURN_INVALID
        blockers = ["no evidence return files were provided"]
        missing_sections = list(REQUIRED_SECTIONS)
    elif any(item["status"] == OWNER_RETURN_BLOCKED for item in results):
        status = OWNER_RETURN_BLOCKED
        blockers = [
            item["blockers"][0]
            for item in results
            if item.get("blockers")
        ]
    elif any(item["status"] == OWNER_RETURN_REPAIRABLE for item in results):
        status = OWNER_RETURN_REPAIRABLE
        blockers = [
            item["blockers"][0]
            for item in results
            if item.get("blockers")
        ]
    elif all(item["status"] == OWNER_RETURN_VALID for item in results):
        status = OWNER_RETURN_VALID
        blockers = []
    else:
        status = OWNER_RETURN_INVALID
        blockers = ["mixed or unknown validation state detected"]

    return {
        "validator_version": OWNER_EVIDENCE_RETURN_VALIDATOR_VERSION,
        "validation_timestamp": _now_iso(),
        "status": status,
        "path_count": len(results),
        "results": results,
        "blockers": blockers,
        "owner_confirmation_required": strict and status != OWNER_RETURN_VALID,
    }


def result_to_markdown(result: Mapping[str, Any]) -> str:
    lines = [
        "# Forex Owner Evidence Return Validator V1",
        f"Generated: {result.get('validation_timestamp')}",
        f"Status: {result.get('status')}",
        f"- Path count: {result.get('path_count', 0)}",
        f"- Owner confirmation required: {result.get('owner_confirmation_required', False)}",
        "",
        "## Validation Details",
    ]
    for item in result.get("results", []):
        lines.append(f"- {item.get('path')}")
        lines.append(f"  - status: {item.get('status')}")
        lines.append(f"  - sample_count: {item.get('sample_count')}")
        if item.get("missing_sections"):
            lines.append(f"  - missing_sections: {item.get('missing_sections')}")
        if item.get("sensitive_hits"):
            lines.append("  - sensitive_hits:")
            for hit in item["sensitive_hits"]:
                lines.append(f"    - {hit['pattern']}: {hit['value']}")
        lines.append("  - repair_instructions:")
        for item_instruction in item.get("repair_instructions", []):
            lines.append(f"    - {item_instruction}")
    return "\n".join(lines)


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "validator_version": result.get("validator_version", OWNER_EVIDENCE_RETURN_VALIDATOR_VERSION),
        "validation_timestamp": result.get("validation_timestamp"),
        "status": result.get("status"),
        "path_count": int(result.get("path_count", 0)),
        "owner_confirmation_required": bool(result.get("owner_confirmation_required", False)),
        "blockers": list(result.get("blockers", [])),
        "results": [
            {
                "path": item.get("path"),
                "status": item.get("status"),
                "sample_count": item.get("sample_count"),
                "missing_sections": list(item.get("missing_sections", [])),
                "sensitive_hits": list(item.get("sensitive_hits", [])),
                "repair_instructions": list(item.get("repair_instructions", [])),
            }
            for item in result.get("results", [])
        ],
    }


__all__ = [
    "OWNER_RETURN_INVALID",
    "OWNER_EVIDENCE_RETURN_VALIDATOR_VERSION",
    "OWNER_RETURN_BLOCKED",
    "OWNER_RETURN_INVALID",
    "OWNER_RETURN_REPAIRABLE",
    "OWNER_RETURN_VALID",
    "BROKER_COMMAND_PATTERNS",
    "REQUIRED_SECTIONS",
    "validate_owner_evidence_return_files",
    "validate_owner_evidence_return_text",
    "result_to_jsonable_dict",
    "result_to_markdown",
    "scan_sensitive_patterns",
]
