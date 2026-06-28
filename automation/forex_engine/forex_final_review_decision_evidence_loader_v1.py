"""Evidence loader for Forex final review decision aggregation."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


FINAL_REVIEW_EVIDENCE_LOADER_VERSION = "1.0"

EVIDENCE_READY = "EVIDENCE_READY"
EVIDENCE_REPAIR_REQUIRED = "EVIDENCE_REPAIR_REQUIRED"
OWNER_EVIDENCE_REQUIRED = "OWNER_EVIDENCE_REQUIRED"
EXTERNAL_EVIDENCE_REQUIRED = "EXTERNAL_EVIDENCE_REQUIRED"
PROTECTED_AUTHORITY_REQUIRED = "PROTECTED_AUTHORITY_REQUIRED"
SAFETY_REJECTED = "SAFETY_REJECTED"
EVIDENCE_MISSING = "EVIDENCE_MISSING"

_PROTECTED_AUTH_KEYWORDS = (
    "broker/api",
    "broker_api",
    "credential access",
    "credential granted",
    "production activation",
    "order placed",
    "money moved",
    "demo trade authorized",
    "live trade authorized",
    "scheduler started",
    "daemon started",
    "webhook started",
)

_OWNER_KEYWORDS = (
    "owner evidence required",
    "owner approval",
    "owner decision pending",
)

_EXTERNAL_KEYWORDS = (
    "external evidence required",
    "broker/api required",
    "credential evidence required",
    "protected publish route",
    "account snapshot evidence required",
)

_SAFETY_KEYWORDS = (
    "safety blocked",
    "safety rejected",
    "profit claimed",
    "guaranteed profit",
)

_LOCAL_REPAIR_KEYWORDS = (
    "local repair",
    "repair required",
    "insufficient sample",
    "missing sections",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_path(path: str | Path | None) -> Path | None:
    if path is None:
        return None
    return Path(path).expanduser()


def _clean_text_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()


def _classify_status(
    status_value: str | None = None,
    text: str = "",
    source_family: str = "",
    source_family_payload: str | None = None,
) -> str:
    if status_value:
        if "repair" in status_value or "repair_required" in status_value:
            return EVIDENCE_REPAIR_REQUIRED
        if "owner" in status_value and "required" in status_value:
            return OWNER_EVIDENCE_REQUIRED
        if "external" in status_value and "required" in status_value:
            return EXTERNAL_EVIDENCE_REQUIRED
        if "protected" in status_value and "authority" in status_value:
            return PROTECTED_AUTHORITY_REQUIRED
        if "safety" in status_value or "blocked" in status_value:
            return SAFETY_REJECTED
        if "ready" in status_value:
            return EVIDENCE_READY
        if "missing" in status_value:
            return EVIDENCE_MISSING

    lowered = text.lower()
    if any(keyword in lowered for keyword in _SAFETY_KEYWORDS):
        return SAFETY_REJECTED
    if any(keyword in lowered for keyword in _PROTECTED_AUTH_KEYWORDS):
        return PROTECTED_AUTHORITY_REQUIRED
    if any(keyword in lowered for keyword in _OWNER_KEYWORDS):
        return OWNER_EVIDENCE_REQUIRED
    if any(keyword in lowered for keyword in _EXTERNAL_KEYWORDS):
        return EXTERNAL_EVIDENCE_REQUIRED
    if any(keyword in lowered for keyword in _LOCAL_REPAIR_KEYWORDS):
        return EVIDENCE_REPAIR_REQUIRED
    if source_family_payload and source_family_payload.lower().startswith("safety"):
        return SAFETY_REJECTED
    if source_family.lower() in {"owner evidence", "owner_evidence"}:
        return OWNER_EVIDENCE_REQUIRED
    if source_family.lower() in {"external", "broker", "api"}:
        return EXTERNAL_EVIDENCE_REQUIRED
    return EVIDENCE_READY


def normalize_final_review_evidence_payload(
    payload: Mapping[str, Any] | Any,
    *,
    source_path: str | Path | None = None,
    source_kind: str | None = None,
) -> list[dict[str, Any]]:
    if not isinstance(payload, Mapping):
        return [
            {
                "source_path": str(source_path) if source_path else None,
                "source_kind": str(source_kind or "payload"),
                "source_family": "unknown",
                "status": EVIDENCE_MISSING,
                "source_status": "invalid_payload",
                "redaction_status": "unknown",
                "evidence_count": 0,
                "notes": ["payload was not a mapping"],
            },
        ]

    source_family = (
        str(payload.get("source_family", "")).strip()
        or str(payload.get("family", "")).strip()
        or str(payload.get("module", "")).strip()
        or "final_review"
    )
    source_status = str(payload.get("status", "")).strip()
    redaction_status = str(
        payload.get("redaction_status", payload.get("redaction", "unknown")),
    ).strip() or "unknown"

    payload_items = payload.get("items", payload.get("entries", []))
    if isinstance(payload_items, list):
        evidence_count = len(payload_items)
    elif isinstance(payload_items, dict):
        evidence_count = len(payload_items)
    elif isinstance(payload_items, (str, int, float, bool)):
        evidence_count = 1
    else:
        evidence_count = 1 if payload else 0

    status = _classify_status(source_status, _payload_to_text(payload), source_family, source_status)
    if not source_status:
        status = _classify_status(None, _payload_to_text(payload), source_family, payload.get("evidence_type"))
    return [
        {
            "source_path": str(source_path) if source_path else None,
            "source_kind": source_kind or "payload",
            "source_family": source_family,
            "status": status,
            "source_status": source_status or status,
            "redaction_status": redaction_status,
            "evidence_count": int(evidence_count),
            "notes": list(_extract_notes(payload)),
        },
    ]


def _extract_notes(payload: Mapping[str, Any]) -> list[str]:
    notes = []
    for key, value in payload.items():
        if key in {"notes", "note", "blockers", "status_blockers"}:
            if isinstance(value, list):
                notes.extend(str(item) for item in value)
            else:
                notes.append(str(value))
        if key in {"next_steps", "route", "owner_gap_families", "local_gap_families"}:
            notes.append(f"{key}:{value}")
    if not notes:
        notes = ["auto-normalized payload"]
    return notes


def _payload_to_text(payload: Mapping[str, Any]) -> str:
    text_pieces: list[str] = []
    for value in payload.values():
        if isinstance(value, str):
            text_pieces.append(value)
        elif isinstance(value, (list, tuple)):
            text_pieces.extend(str(item) for item in value)
        elif isinstance(value, Mapping):
            text_pieces.extend([f"{k}:{v}" for k, v in value.items()])
    return "\n".join(text_pieces).lower()


def load_final_review_evidence_file(path: str | Path) -> list[dict[str, Any]]:
    source_path = _ensure_path(path)
    if source_path is None or not source_path.exists():
        return [
            {
                "source_path": str(source_path) if source_path else None,
                "source_kind": "missing",
                "source_family": "missing_file",
                "status": EVIDENCE_MISSING,
                "source_status": "missing_file",
                "redaction_status": "unknown",
                "evidence_count": 0,
                "notes": ["evidence file not found"],
            },
        ]

    if source_path.suffix.lower() == ".json":
        try:
            payload = json.loads(source_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return [
                {
                    "source_path": str(source_path),
                    "source_kind": "json",
                    "source_family": "invalid_json",
                    "status": EVIDENCE_MISSING,
                    "source_status": "invalid_json",
                    "redaction_status": "unknown",
                    "evidence_count": 0,
                    "notes": ["invalid JSON payload"],
                },
            ]
        if isinstance(payload, list):
            records = []
            for entry in payload:
                records.extend(
                    normalize_final_review_evidence_payload(
                        entry if isinstance(entry, Mapping) else {"status": str(entry)},
                        source_path=source_path,
                        source_kind="json",
                    ),
                )
            return records
        return normalize_final_review_evidence_payload(
            payload,
            source_path=source_path,
            source_kind="json",
        )

    lines = _clean_text_lines(source_path)
    joined = "\n".join(lines)
    status_text = " ".join(
        [
            line.split(":", 1)[1].strip()
            for line in lines
            if line.lower().startswith("status")
            and ":" in line
        ],
    )
    status = _classify_status(status_text, joined)
    family = "final_review_markdown"
    for line in lines:
        lowered = line.lower()
        if lowered.startswith("family:") or lowered.startswith("source_family:"):
            family = line.split(":", 1)[1].strip()
            break

    return [
        {
            "source_path": str(source_path),
            "source_kind": "markdown",
            "source_family": family,
            "status": status,
            "source_status": status_text or status,
            "redaction_status": "redacted" if "redacted" in joined.lower() else "not_redacted",
            "evidence_count": max(1, len([line for line in lines if line.strip()])),
            "notes": ["loaded from markdown evidence file"],
        },
    ]


def load_final_review_evidence_paths(
    paths: Iterable[str | Path] | None,
    *,
    strict: bool = False,
    source_family: str = "final_review",
) -> dict[str, Any]:
    del strict
    expanded: list[Path] = []
    for raw_path in paths or []:
        candidate = _ensure_path(raw_path)
        if candidate is None:
            continue
        if candidate.is_dir():
            expanded.extend(sorted(candidate.glob("*.json")))
            expanded.extend(sorted(candidate.glob("*.md")))
            continue
        expanded.append(candidate)

    records: list[dict[str, Any]] = []
    for source in expanded:
        for record in load_final_review_evidence_file(source):
            record["source_family"] = source_family if source_family else record["source_family"]
            records.append(record)

    if not records:
        records.append(
            {
                "source_path": None,
                "source_kind": "directory",
                "source_family": source_family or "final_review",
                "status": EVIDENCE_MISSING,
                "source_status": "no_paths",
                "redaction_status": "unknown",
                "evidence_count": 0,
                "notes": ["no evidence sources were provided"],
            },
        )

    return summarize_final_review_evidence({"records": records})


def summarize_final_review_evidence(result: Mapping[str, Any] | Iterable[dict[str, Any]]) -> dict[str, Any]:
    records = list(result.get("records", [])) if isinstance(result, Mapping) else list(result)  # type: ignore[arg-type]
    status_counts: dict[str, int] = {
        EVIDENCE_READY: 0,
        EVIDENCE_REPAIR_REQUIRED: 0,
        OWNER_EVIDENCE_REQUIRED: 0,
        EXTERNAL_EVIDENCE_REQUIRED: 0,
        PROTECTED_AUTHORITY_REQUIRED: 0,
        SAFETY_REJECTED: 0,
        EVIDENCE_MISSING: 0,
    }
    source_kind_counts: dict[str, int] = {}
    source_family_counts: dict[str, int] = {}
    redaction_counts: dict[str, int] = {}
    total_evidence = 0
    notes: list[str] = []

    for record in records:
        if not isinstance(record, Mapping):
            continue
        status = str(record.get("status", EVIDENCE_MISSING))
        status_counts[status] = status_counts.get(status, 0) + 1
        source_kind = str(record.get("source_kind", "unknown"))
        source_family = str(record.get("source_family", "unknown"))
        redaction_status = str(record.get("redaction_status", "unknown"))
        source_kind_counts[source_kind] = source_kind_counts.get(source_kind, 0) + 1
        source_family_counts[source_family] = source_family_counts.get(source_family, 0) + 1
        redaction_counts[redaction_status] = redaction_counts.get(redaction_status, 0) + 1
        total_evidence += int(record.get("evidence_count", 0) or 0)
        notes.extend(str(item) for item in record.get("notes", []))

    most_critical_status = EVIDENCE_READY
    if not records:
        most_critical_status = EVIDENCE_MISSING
        status_counts[EVIDENCE_MISSING] = 1
    if status_counts[SAFETY_REJECTED]:
        most_critical_status = SAFETY_REJECTED
    elif status_counts[PROTECTED_AUTHORITY_REQUIRED]:
        most_critical_status = PROTECTED_AUTHORITY_REQUIRED
    elif status_counts[EXTERNAL_EVIDENCE_REQUIRED]:
        most_critical_status = EXTERNAL_EVIDENCE_REQUIRED
    elif status_counts[OWNER_EVIDENCE_REQUIRED]:
        most_critical_status = OWNER_EVIDENCE_REQUIRED
    elif status_counts[EVIDENCE_REPAIR_REQUIRED]:
        most_critical_status = EVIDENCE_REPAIR_REQUIRED
    elif status_counts[EVIDENCE_MISSING]:
        most_critical_status = EVIDENCE_MISSING

    return {
        "loader_version": FINAL_REVIEW_EVIDENCE_LOADER_VERSION,
        "generated_at": _now_iso(),
        "record_count": len(records),
        "evidence_count": int(total_evidence),
        "most_critical_status": most_critical_status,
        "status_counts": status_counts,
        "source_kind_counts": source_kind_counts,
        "source_family_counts": source_family_counts,
        "redaction_status_counts": redaction_counts,
        "records": records,
        "notes": list(dict.fromkeys(notes)),
    }


def final_review_evidence_to_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Forex Final Review Decision Evidence Loader V1",
        f"Generated: {summary.get('generated_at')}",
        f"Record count: {summary.get('record_count', 0)}",
        f"Evidence count: {summary.get('evidence_count', 0)}",
        f"Most critical status: {summary.get('most_critical_status')}",
        "",
        "## Status counts",
    ]
    for status, count in sorted(summary.get("status_counts", {}).items()):
        lines.append(f"- {status}: {count}")

    lines.extend(["", "## Records"])
    for record in summary.get("records", []):
        if not isinstance(record, Mapping):
            continue
        lines.append(f"- {record.get('source_path')} [{record.get('source_kind')}]")
        lines.append(f"  - source_family: {record.get('source_family')}")
        lines.append(f"  - status: {record.get('status')}")
        lines.append(f"  - source_status: {record.get('source_status')}")
        lines.append(f"  - redaction_status: {record.get('redaction_status')}")
        lines.append(f"  - evidence_count: {record.get('evidence_count')}")
    return "\n".join(lines)


def final_review_evidence_to_jsonable_dict(summary: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "loader_version": summary.get("loader_version", FINAL_REVIEW_EVIDENCE_LOADER_VERSION),
        "generated_at": summary.get("generated_at"),
        "record_count": int(summary.get("record_count", 0)),
        "evidence_count": int(summary.get("evidence_count", 0)),
        "most_critical_status": summary.get("most_critical_status"),
        "status_counts": dict(summary.get("status_counts", {})),
        "source_kind_counts": dict(summary.get("source_kind_counts", {})),
        "source_family_counts": dict(summary.get("source_family_counts", {})),
        "redaction_status_counts": dict(summary.get("redaction_status_counts", {})),
        "notes": list(summary.get("notes", [])),
        "records": [dict(record) for record in summary.get("records", [])],
    }


__all__ = [
    "EVIDENCE_MISSING",
    "EVIDENCE_READY",
    "EVIDENCE_REPAIR_REQUIRED",
    "EXTERNAL_EVIDENCE_REQUIRED",
    "OWNER_EVIDENCE_REQUIRED",
    "PROTECTED_AUTHORITY_REQUIRED",
    "SAFETY_REJECTED",
    "FINAL_REVIEW_EVIDENCE_LOADER_VERSION",
    "final_review_evidence_to_jsonable_dict",
    "final_review_evidence_to_markdown",
    "load_final_review_evidence_file",
    "load_final_review_evidence_paths",
    "normalize_final_review_evidence_payload",
    "summarize_final_review_evidence",
]
