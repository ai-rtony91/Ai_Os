"""Local-only catalog helpers for remaining Forex evidence closure."""

from __future__ import annotations

import json
import re
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional


EVIDENCE_FAMILY_NAMES = (
    "candidate evidence",
    "walk-forward evidence",
    "out-of-sample evidence",
    "demo trade telemetry",
    "broker snapshot evidence",
    "execution readiness evidence",
    "risk control evidence",
    "expectancy/profit-factor evidence",
    "drawdown evidence",
    "sample sufficiency evidence",
    "owner approval evidence",
    "live exception evidence",
    "credential boundary evidence",
    "kill-switch evidence",
    "monitoring/alert evidence",
    "audit log evidence",
    "final bundle evidence",
)

LOCAL_REPAIRABLE = "LOCAL_REPAIRABLE"
OWNER_EVIDENCE_REQUIRED = "OWNER_EVIDENCE_REQUIRED"
BROKER_API_REQUIRED = "BROKER_API_REQUIRED"
CREDENTIAL_REQUIRED = "CREDENTIAL_REQUIRED"
TRADING_EXECUTION_REQUIRED = "TRADING_EXECUTION_REQUIRED"
PROTECTED_PUBLISH_REQUIRED = "PROTECTED_PUBLISH_REQUIRED"
ALREADY_PRESENT = "ALREADY_PRESENT"
NOT_APPLICABLE = "NOT_APPLICABLE"
UNKNOWN_REVIEW_REQUIRED = "UNKNOWN_REVIEW_REQUIRED"

LINE_CAPTURE = re.compile(
    r"(?P<name>[A-Za-z0-9 _/\\-]+)\s*[:=]\s*(?P<value>.+)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class EvidenceItem:
    name: str
    classification: str
    reason: str
    source: str
    evidence_present: bool = False
    severity: str = "medium"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_name(raw: str) -> str:
    return raw.strip().lower()


def _default_classification(family_name: str) -> str:
    normalized = _normalize_name(family_name)
    if normalized == "broker snapshot evidence":
        return BROKER_API_REQUIRED
    if "credential" in normalized:
        return CREDENTIAL_REQUIRED
    if normalized == "execution readiness evidence" or normalized == "demo trade telemetry":
        return TRADING_EXECUTION_REQUIRED
    if normalized == "live exception evidence":
        return PROTECTED_PUBLISH_REQUIRED
    if "owner" in normalized:
        return OWNER_EVIDENCE_REQUIRED
    if normalized in {"candidate evidence", "walk-forward evidence", "out-of-sample evidence"}:
        return LOCAL_REPAIRABLE
    return LOCAL_REPAIRABLE


def classify_evidence_item(item_name: str, hint: Optional[Mapping[str, Any]] = None) -> str:
    normalized = _normalize_name(item_name)
    if normalized not in {name.lower() for name in EVIDENCE_FAMILY_NAMES}:
        return UNKNOWN_REVIEW_REQUIRED
    hint_value = None if hint is None else hint.get("classification")
    if hint_value:
        normalized_hint = _normalize_name(str(hint_value))
        valid = {value.lower() for value in (
            ALREADY_PRESENT,
            LOCAL_REPAIRABLE,
            OWNER_EVIDENCE_REQUIRED,
            BROKER_API_REQUIRED,
            CREDENTIAL_REQUIRED,
            TRADING_EXECUTION_REQUIRED,
            PROTECTED_PUBLISH_REQUIRED,
            NOT_APPLICABLE,
            UNKNOWN_REVIEW_REQUIRED,
        )}
        if normalized_hint in valid:
            return str(hint_value)
    return _default_classification(item_name)


def load_catalog_from_reports(report_paths: Iterable[Path | str]) -> list[EvidenceItem]:
    items: list[EvidenceItem] = []
    for report_path in report_paths:
        path = Path(report_path)
        if not path.exists():
            continue
        if path.suffix.lower() == ".json":
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            raw_items = payload.get("items", []) if isinstance(payload, dict) else []
            for raw_item in raw_items:
                if not isinstance(raw_item, dict):
                    continue
                name = str(raw_item.get("name") or raw_item.get("family") or "")
                if not name:
                    continue
                classification = str(raw_item.get("classification") or _default_classification(name))
                reason = str(raw_item.get("reason") or "loaded from json report")
                source = str(raw_item.get("source", path))
                evidence_present = bool(
                    raw_item.get("evidence_present", raw_item.get("present", False))
                )
                items.append(
                    EvidenceItem(
                        name=name,
                        classification=classification,
                        reason=reason,
                        source=source,
                        evidence_present=evidence_present,
                        severity=str(raw_item.get("severity", "medium")),
                    )
                )
            continue
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not (line.startswith("-") or line.startswith("*")):
                continue
            match = LINE_CAPTURE.search(line.lstrip("-* ").strip())
            if not match:
                continue
            raw_name = match.group("name")
            normalized_name = _normalize_name(raw_name)
            if normalized_name not in {name.lower() for name in EVIDENCE_FAMILY_NAMES}:
                continue
            classification = _default_classification(raw_name)
            value = match.group("value").lower().strip()
            evidence_present = value in {"present", "available", "ok"}
            items.append(
                EvidenceItem(
                    name=raw_name,
                    classification=classification,
                    reason=f"derived from report: {value}",
                    source=str(path),
                    evidence_present=evidence_present,
                )
            )
    return items


def build_missing_evidence_catalog(
    report_paths: Optional[Iterable[Path | str]] = None,
    explicit_records: Optional[Iterable[Mapping[str, Any]]] = None,
) -> dict[str, Any]:
    discovered: dict[str, EvidenceItem] = {}
    loaded: list[EvidenceItem] = []
    if report_paths is not None:
        loaded.extend(load_catalog_from_reports(report_paths))
    if explicit_records:
        for raw in explicit_records:
            if not isinstance(raw, Mapping):
                continue
            raw_name = str(raw.get("name") or raw.get("family") or raw.get("evidence_family") or "")
            if not raw_name:
                continue
            loaded.append(
                EvidenceItem(
                    name=raw_name,
                    classification=classify_evidence_item(raw_name, raw),
                    reason=str(raw.get("reason", "explicit record")),
                    source=str(raw.get("source", "explicit_records")),
                    evidence_present=bool(raw.get("present", False)),
                    severity=str(raw.get("severity", "medium")),
                )
            )
    for family in EVIDENCE_FAMILY_NAMES:
        exact = [item for item in loaded if _normalize_name(item.name) == family]
        if exact:
            selected = sorted(exact, key=lambda each: each.source)[0]
            discovered[family] = selected
            continue
        discovered[family] = EvidenceItem(
            name=family,
            classification=_default_classification(family),
            reason="no local report entry found",
            source="generated_catalog",
            evidence_present=False,
            severity="medium",
        )
    ordered = OrderedDict((name, {
        "name": entry.name,
        "classification": entry.classification,
        "reason": entry.reason,
        "source": entry.source,
        "evidence_present": entry.evidence_present,
        "severity": entry.severity,
    }) for name, entry in discovered.items())
    return {
        "catalog_version": "1.0",
        "generated_at": _now_iso(),
        "item_count": len(ordered),
        "items": ordered,
    }


def summarize_catalog(catalog: Mapping[str, Any]) -> dict[str, Any]:
    items = catalog.get("items", {})
    counts: dict[str, int] = {}
    for entry in items.values():
        status = str(entry.get("classification", UNKNOWN_REVIEW_REQUIRED))
        counts[status] = counts.get(status, 0) + 1
    remaining = [name for name, entry in items.items() if entry.get("classification") != ALREADY_PRESENT]
    return {
        "catalog_version": catalog.get("catalog_version", "1.0"),
        "generated_at": catalog.get("generated_at"),
        "item_count": len(items),
        "classification_counts": counts,
        "remaining_item_count": len(remaining),
        "remaining_items": remaining,
    }


def catalog_to_markdown(catalog: Mapping[str, Any]) -> str:
    summary = summarize_catalog(catalog)
    lines = [
        "# Forex Missing Evidence Catalog V1",
        f"Generated: {summary['generated_at']}",
        "",
        f"- Item count: {summary['item_count']}",
        f"- Remaining items: {summary['remaining_item_count']}",
        "",
        "## Classification Counts",
    ]
    for name in sorted(summary["classification_counts"]):
        lines.append(f"- {name}: {summary['classification_counts'][name]}")
    lines.extend(["", "## Missing Families"])
    for name, payload in catalog.get("items", {}).items():
        lines.append(f"- {name}")
        lines.append(f"  - classification: {payload.get('classification')}")
        lines.append(f"  - reason: {payload.get('reason')}")
        lines.append(f"  - evidence_present: {payload.get('evidence_present', False)}")
        lines.append(f"  - source: {payload.get('source')}")
    return "\n".join(lines)


def catalog_to_jsonable_dict(catalog: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "catalog_version": catalog.get("catalog_version", "1.0"),
        "generated_at": catalog.get("generated_at"),
        "item_count": int(catalog.get("item_count", 0)),
        "items": list(catalog.get("items", {}).values()),
    }


EVIDENCE_FAMILIES = EVIDENCE_FAMILY_NAMES

__all__ = [
    "ALREADY_PRESENT",
    "BROKER_API_REQUIRED",
    "CREDENTIAL_REQUIRED",
    "EVIDENCE_FAMILIES",
    "EVIDENCE_FAMILY_NAMES",
    "LOCAL_REPAIRABLE",
    "NOT_APPLICABLE",
    "NOT_APPLICABLE",
    "OWNER_EVIDENCE_REQUIRED",
    "PROTECTED_PUBLISH_REQUIRED",
    "TRADING_EXECUTION_REQUIRED",
    "UNKNOWN_REVIEW_REQUIRED",
    "build_missing_evidence_catalog",
    "classify_evidence_item",
    "load_catalog_from_reports",
    "summarize_catalog",
    "catalog_to_markdown",
    "catalog_to_jsonable_dict",
]
