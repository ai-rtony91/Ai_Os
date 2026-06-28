"""Owner evidence return intake helpers for the new Forex orchestration lane."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from . import forex_missing_evidence_catalog_v1 as catalog_lib


OWNER_EVIDENCE_RETURN_INTAKE_VERSION = "1.0"

INTAKE_COMPLETE = "INTAKE_COMPLETE"
INTAKE_PARTIAL = "INTAKE_PARTIAL"
INTAKE_EMPTY = "INTAKE_EMPTY"
INTAKE_INVALID = "INTAKE_INVALID"

DEFAULT_MAX_SAMPLE_FOR_LOCAL_REPAIR = 60


@dataclass(frozen=True)
class OwnerEvidenceReturnIntakeItem:
    family: str
    classification: str
    evidence_present: bool
    requested: bool
    expected_filename: str
    reason: str
    source: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_family(raw: Any) -> str:
    value = "" if raw is None else str(raw)
    return value.strip().lower()


def _expand_catalog_paths(report_paths: Iterable[str | Path] | None) -> tuple[Path, ...]:
    if report_paths is None:
        return tuple()
    expanded: list[Path] = []
    for raw_path in report_paths:
        path = Path(raw_path)
        if path.is_dir():
            expanded.extend(sorted(path.glob("*")))
        elif path.exists():
            expanded.append(path)
        else:
            # Ignore missing paths so build_missing_evidence_catalog can proceed with defaults.
            continue
    return tuple(expanded)


def _slug(value: str) -> str:
    return "".join(char if char.isalnum() else "_" for char in value.strip().lower()).strip("_")


def _item_json(item: OwnerEvidenceReturnIntakeItem) -> dict[str, Any]:
    return {
        "family": item.family,
        "classification": item.classification,
        "evidence_present": item.evidence_present,
        "requested": item.requested,
        "expected_filename": item.expected_filename,
        "reason": item.reason,
        "source": item.source,
    }


def _build_item(entry: Mapping[str, Any], *, include_already_present: bool) -> OwnerEvidenceReturnIntakeItem:
    family = str(
        entry.get("name")
        or entry.get("family")
        or entry.get("evidence_family")
        or entry.get("evidence name", "")
        or entry.get("item", "")
    ).strip()
    if not family:
        family = "owner-evidence"
    normalized_family = _normalize_family(family)
    classification = str(entry.get("classification", catalog_lib.LOCAL_REPAIRABLE))
    evidence_present = bool(entry.get("evidence_present", entry.get("present", False)))
    requested = classification != catalog_lib.ALREADY_PRESENT or include_already_present
    expected_filename = f"{_slug(family)}_owner_evidence.md"
    if entry.get("expected_filename"):
        expected_filename = str(entry.get("expected_filename"))
    if classification == catalog_lib.LOCAL_REPAIRABLE and evidence_present is False:
        reason = "local review and closure repair required"
    elif classification == catalog_lib.OWNER_EVIDENCE_REQUIRED and evidence_present is False:
        reason = "owner evidence requested before readiness"
    elif classification == catalog_lib.BROKER_API_REQUIRED:
        reason = "external broker evidence required"
    elif classification == catalog_lib.CREDENTIAL_REQUIRED:
        reason = "credential boundary evidence required"
    elif classification == catalog_lib.TRADING_EXECUTION_REQUIRED:
        reason = "execution readiness evidence required"
    elif classification == catalog_lib.PROTECTED_PUBLISH_REQUIRED:
        reason = "protected publish route evidence required"
    else:
        reason = "no intake blocker"
    return OwnerEvidenceReturnIntakeItem(
        family=family,
        classification=classification,
        evidence_present=evidence_present,
        requested=requested,
        expected_filename=expected_filename,
        reason=reason,
        source=str(entry.get("source", "catalog")),
    )


def _build_summary(intake_items: list[OwnerEvidenceReturnIntakeItem]) -> dict[str, int]:
    counts: dict[str, int] = {
        catalog_lib.LOCAL_REPAIRABLE: 0,
        catalog_lib.OWNER_EVIDENCE_REQUIRED: 0,
        catalog_lib.BROKER_API_REQUIRED: 0,
        catalog_lib.CREDENTIAL_REQUIRED: 0,
        catalog_lib.TRADING_EXECUTION_REQUIRED: 0,
        catalog_lib.PROTECTED_PUBLISH_REQUIRED: 0,
    }
    for item in intake_items:
        counts[item.classification] = counts.get(item.classification, 0) + 1
    missing = [item.family for item in intake_items if item.requested and not item.evidence_present]
    owner = [item.family for item in intake_items if item.classification == catalog_lib.OWNER_EVIDENCE_REQUIRED]
    local = [item.family for item in intake_items if item.classification == catalog_lib.LOCAL_REPAIRABLE]
    blocked = [
        item.family
        for item in intake_items
        if item.classification
        in {
            catalog_lib.BROKER_API_REQUIRED,
            catalog_lib.CREDENTIAL_REQUIRED,
            catalog_lib.TRADING_EXECUTION_REQUIRED,
            catalog_lib.PROTECTED_PUBLISH_REQUIRED,
        }
    ]
    return {
        "total_items": len(intake_items),
        "requested_items": len([item for item in intake_items if item.requested]),
        "missing_items": len(missing),
        "owner_required_items": len(owner),
        "local_repair_items": len(local),
        "external_blocker_items": len(blocked),
        "blocked_items": len(blocked),
    }


def build_owner_evidence_return_intake(
    catalog_payload: Mapping[str, Any] | None = None,
    *,
    catalog_paths: Iterable[str | Path] | None = None,
    include_already_present: bool = False,
    strict: bool = False,
) -> dict[str, Any]:
    if catalog_payload is None:
        catalog_payload = catalog_lib.build_missing_evidence_catalog(
            report_paths=_expand_catalog_paths(catalog_paths),
        )
    if not isinstance(catalog_payload, Mapping):
        return {
            "intake_version": OWNER_EVIDENCE_RETURN_INTAKE_VERSION,
            "generated_at": _now_iso(),
            "status": INTAKE_INVALID,
            "strict_mode": strict,
            "error": "catalog payload must be a mapping",
            "intake_items": [],
            "summary": _build_summary([]),
            "owner_required_families": [],
            "external_blocker_families": [],
            "local_repair_families": [],
            "next_safe_action": "Provide a valid catalog payload first.",
        }

    raw_items = catalog_payload.get("items", {})
    intake_items: list[OwnerEvidenceReturnIntakeItem] = []
    if isinstance(raw_items, Mapping):
        iterable_items = raw_items.values()
    else:
        iterable_items = raw_items if isinstance(raw_items, list) else []
    for raw in iterable_items:
        if not isinstance(raw, Mapping):
            continue
        intake_items.append(
            _build_item(raw, include_already_present=include_already_present),
        )

    if not intake_items:
        return {
            "intake_version": OWNER_EVIDENCE_RETURN_INTAKE_VERSION,
            "generated_at": _now_iso(),
            "status": INTAKE_EMPTY,
            "strict_mode": strict,
            "intake_items": [],
            "summary": _build_summary([]),
            "owner_required_families": [],
            "external_blocker_families": [],
            "local_repair_families": [],
            "next_safe_action": "Load catalog families before intake routing.",
        }

    summary = _build_summary(intake_items)
    owner_required_families = [
        item.family for item in intake_items if item.classification == catalog_lib.OWNER_EVIDENCE_REQUIRED
    ]
    external_blocker_families = [
        item.family
        for item in intake_items
        if item.classification
        in {
            catalog_lib.BROKER_API_REQUIRED,
            catalog_lib.CREDENTIAL_REQUIRED,
            catalog_lib.TRADING_EXECUTION_REQUIRED,
            catalog_lib.PROTECTED_PUBLISH_REQUIRED,
        }
    ]
    local_repair_families = [
        item.family for item in intake_items if item.classification == catalog_lib.LOCAL_REPAIRABLE
    ]
    missing_requested = [item.family for item in intake_items if item.requested and not item.evidence_present]
    next_safe_action = (
        "Owner evidence requested families can proceed with local-only remediation first."
    )
    if missing_requested:
        next_safe_action = "Collect required evidence and re-run the lane in strict mode."
    status = INTAKE_PARTIAL if missing_requested else INTAKE_COMPLETE
    if strict and missing_requested:
        status = INTAKE_PARTIAL
    return {
        "intake_version": OWNER_EVIDENCE_RETURN_INTAKE_VERSION,
        "generated_at": _now_iso(),
        "status": status,
        "strict_mode": strict,
        "intake_items": [dict(_item_json(item)) for item in intake_items],
        "summary": summary,
        "owner_required_families": owner_required_families,
        "external_blocker_families": external_blocker_families,
        "local_repair_families": local_repair_families,
        "missing_requested_families": missing_requested,
        "next_safe_action": next_safe_action,
        "expected_max_sample_for_local_repair": DEFAULT_MAX_SAMPLE_FOR_LOCAL_REPAIR,
    }


def read_owner_evidence_payload(path: str | Path) -> list[dict[str, Any]]:
    payload_path = Path(path)
    if not payload_path.exists():
        return []
    if payload_path.suffix.lower() == ".json":
        content = json.loads(payload_path.read_text(encoding="utf-8"))
        if isinstance(content, list):
            return [item for item in content if isinstance(item, Mapping)]
        if isinstance(content, Mapping):
            return [dict(content)]
        return []
    lines = payload_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    payload: dict[str, Any] = {}
    for line in lines:
        lowered = line.strip()
        if ":" not in lowered:
            continue
        key, value = lowered.split(":", 1)
        payload[key.strip().lower()] = value.strip()
    if not payload:
        return []
    return [payload]


def load_owner_evidence_payloads(paths: Iterable[str | Path] | None) -> list[dict[str, str]]:
    all_payloads: list[dict[str, str]] = []
    if paths is None:
        return all_payloads
    for path in paths:
        all_payloads.extend(read_owner_evidence_payload(path))
    return all_payloads


def apply_owner_payloads_to_intake(
    intake_payload: Mapping[str, Any],
    payloads: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    if not isinstance(intake_payload, Mapping):
        return build_owner_evidence_return_intake(None)
    items = [dict(item) for item in intake_payload.get("intake_items", []) if isinstance(item, Mapping)]
    payload_by_family: dict[str, Mapping[str, Any]] = {}
    for payload in payloads:
        family = _normalize_family(
            payload.get("family")
            or payload.get("evidence_family")
            or payload.get("name")
            or payload.get("item")
        )
        if family:
            payload_by_family[family] = payload

    for item in items:
        family = _normalize_family(item.get("family"))
        if family not in payload_by_family:
            continue
        payload = payload_by_family[family]
        status = str(payload.get("status", "")).strip().lower()
        evidence_present = str(payload.get("evidence_present", "")).strip().lower() in {"true", "1", "yes", "present", "complete"}
        if status in {"complete", "provided", "received"}:
            evidence_present = True
        if evidence_present:
            item["evidence_present"] = True

    missing_requested = [item["family"] for item in items if item.get("requested") and not item.get("evidence_present")]
    status = INTAKE_COMPLETE if not missing_requested else INTAKE_PARTIAL
    if not items:
        status = INTAKE_EMPTY
    payload = dict(intake_payload)
    payload["intake_items"] = items
    payload["status"] = status
    payload["missing_requested_families"] = missing_requested
    payload["summary"]["missing_items"] = len(missing_requested)
    payload["summary"]["requested_items"] = len([item for item in items if item.get("requested")])
    return payload


def intake_to_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload.get("summary", {})
    lines = [
        "# Forex Owner Evidence Return Intake V1",
        f"Generated: {payload.get('generated_at')}",
        f"Status: {payload.get('status')}",
        f"- strict_mode: {payload.get('strict_mode', False)}",
        f"- total_items: {summary.get('total_items', 0)}",
        f"- requested_items: {summary.get('requested_items', 0)}",
        f"- missing_items: {summary.get('missing_items', 0)}",
        f"- owner_required_families: {', '.join(payload.get('owner_required_families', []))}",
        "",
        "## Missing Requested Families",
    ]
    for family in payload.get("missing_requested_families", []):
        lines.append(f"- {family}")
    lines.extend(
        [
            "",
            "## External Blockers",
        ]
    )
    for family in payload.get("external_blocker_families", []):
        lines.append(f"- {family}")
    lines.append("")
    lines.append("## Requested Items")
    for item in payload.get("intake_items", []):
        family = item.get("family", "UNKNOWN")
        lines.append(f"- {family} ({item.get('classification')}) -> evidence_present: {item.get('evidence_present')}")
        lines.append(f"  - requested: {item.get('requested', False)}")
        lines.append(f"  - expected_filename: {item.get('expected_filename')}")
        lines.append(f"  - reason: {item.get('reason')}")
    return "\n".join(lines)


def intake_to_jsonable_dict(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "intake_version": payload.get("intake_version", OWNER_EVIDENCE_RETURN_INTAKE_VERSION),
        "generated_at": payload.get("generated_at"),
        "status": payload.get("status"),
        "strict_mode": bool(payload.get("strict_mode", False)),
        "summary": dict(payload.get("summary", {})),
        "owner_required_families": list(payload.get("owner_required_families", [])),
        "external_blocker_families": list(payload.get("external_blocker_families", [])),
        "local_repair_families": list(payload.get("local_repair_families", [])),
        "missing_requested_families": list(payload.get("missing_requested_families", [])),
        "next_safe_action": payload.get("next_safe_action"),
        "intake_items": [dict(item) for item in payload.get("intake_items", [])],
    }


__all__ = [
    "DEFAULT_MAX_SAMPLE_FOR_LOCAL_REPAIR",
    "INTAKE_COMPLETE",
    "INTAKE_EMPTY",
    "INTAKE_INVALID",
    "INTAKE_PARTIAL",
    "OwnerEvidenceReturnIntakeItem",
    "OWNER_EVIDENCE_RETURN_INTAKE_VERSION",
    "apply_owner_payloads_to_intake",
    "build_owner_evidence_return_intake",
    "intake_to_jsonable_dict",
    "intake_to_markdown",
    "load_owner_evidence_payloads",
    "read_owner_evidence_payload",
]
