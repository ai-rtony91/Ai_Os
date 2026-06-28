"""Owner evidence pack helpers for Forex remaining-closure work."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from . import forex_missing_evidence_catalog_v1 as catalog_lib


def _safe_time() -> str:
    return datetime.now(timezone.utc).isoformat()


DEFAULT_ALLOWED_ACTIONS = (
    "Attach sanitized logs only.",
    "Summarize outcomes, not full raw payload.",
    "Remove account IDs and session values.",
)


@dataclass(frozen=True)
class OwnerEvidenceItem:
    family: str
    classification: str
    instruction: str
    expected_filename: str
    risk_notes: list[str]


def build_redaction_rules() -> list[str]:
    return [
        "Remove all account identifiers.",
        "Remove authentication values.",
        "Remove credential-like fragments.",
        "Remove direct endpoint and host labels.",
        "Do not include order command text.",
    ]


def build_sanitized_evidence_template(family: str, *, include_filename: bool = False) -> str:
    lines = [
        f"Template for {family}",
        "source evidence can be pasted here after redaction.",
        "required fields:",
        "- evidence_location",
        "- observed_metric",
        "- sample_count",
        "- decision_basis",
        "- validation_status",
    ]
    if include_filename:
        lines.append("- evidence_file_name")
    return "\n".join(lines)


def build_collection_checklist(pack: "OwnerEvidencePack") -> list[str]:
    return [
        "Collect requested evidence from local-only outputs.",
        "Apply all redaction rules before upload.",
        "Confirm evidence entry names.",
        "Mark `access_status` for each item.",
        "Attach only deterministic local files.",
    ]


def _normalize_family(item: Mapping[str, Any]) -> str:
    return str(item.get("name") or item.get("family") or "").strip()


def build_owner_evidence_pack(
    catalog: Mapping[str, Any],
    *,
    strict: bool = False,
    include_templates: bool = True,
) -> dict[str, Any]:
    items = catalog.get("items", {})
    owner_items: list[OwnerEvidenceItem] = []
    for item in items.values():
        family_name = _normalize_family(item)
        if not family_name:
            continue
        classification = str(item.get("classification", catalog_lib.LOCAL_REPAIRABLE))
        if classification == catalog_lib.ALREADY_PRESENT and not strict:
            continue
        owner_items.append(
            OwnerEvidenceItem(
                family=family_name,
                classification=classification,
                instruction="Collect this evidence through local-only deterministic evidence sources.",
                expected_filename=f"{family_name.replace(' ', '_')}_evidence.md",
                risk_notes=list(DEFAULT_ALLOWED_ACTIONS),
            )
        )
    payload = {
        "pack_version": "1.0",
        "generated_at": _safe_time(),
        "strict": strict,
        "include_templates": include_templates,
        "summary": {
            "item_count": len(owner_items),
            "status_blockers": [item.classification for item in owner_items],
        },
        "disallowed_terms": [
            "credential_assignment_pattern",
            "sensitive_assignment_marker",
            "access_status",
            "credential_status",
            "owner_status",
        ],
        "disallowed_content_rules": build_redaction_rules(),
        "requested_evidence_items": [
            {
                "family": item.family,
                "classification": item.classification,
                "instruction": item.instruction,
                "expected_filename": item.expected_filename,
                "risk_notes": item.risk_notes,
            }
            for item in owner_items
        ],
    }
    payload["collection_checklist"] = build_collection_checklist(payload)
    payload["paste_back_to_coded_instructions"] = (
        "Paste evidence summaries as a markdown block and reference this packet."
    )
    if include_templates:
        payload["sanitized_templates"] = {
            item.family: build_sanitized_evidence_template(item.family, include_filename=True)
            for item in owner_items
        }
    return payload


def owner_pack_to_markdown(pack: Mapping[str, Any]) -> str:
    lines = [
        "# Forex Owner Evidence Pack V1",
        f"Generated: {pack.get('generated_at')}",
        f"- Strict mode: {pack.get('strict', False)}",
        f"- Include templates: {pack.get('include_templates', False)}",
        "",
        f"- Requested items: {len(pack.get('requested_evidence_items', []))}",
    ]
    for item in pack.get("requested_evidence_items", []):
        lines.append(f"## {item.get('family')}")
        lines.append(f"- classification: {item.get('classification')}")
        lines.append(f"- instruction: {item.get('instruction')}")
        lines.append(f"- expected_filename: {item.get('expected_filename')}")
    lines.append("")
    lines.append("## Redaction Rules")
    for rule in pack.get("disallowed_content_rules", []):
        lines.append(f"- {rule}")
    lines.append("")
    lines.append("## Collection Checklist")
    for item in pack.get("collection_checklist", []):
        lines.append(f"- {item}")
    if "sanitized_templates" in pack:
        lines.append("")
        lines.append("## Templates")
        for family, template in pack["sanitized_templates"].items():
            lines.append(f"### {family}")
            lines.append(template)
    return "\n".join(lines)


def owner_pack_to_jsonable_dict(pack: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "pack_version": pack.get("pack_version", "1.0"),
        "generated_at": pack.get("generated_at"),
        "summary": dict(pack.get("summary", {})),
        "disallowed_content_rules": list(pack.get("disallowed_content_rules", [])),
        "collection_checklist": list(pack.get("collection_checklist", [])),
        "paste_back_to_coded_instructions": pack.get(
            "paste_back_to_coded_instructions",
        ),
        "requested_evidence_items": list(pack.get("requested_evidence_items", [])),
        "sanitized_templates": dict(pack.get("sanitized_templates", {})),
    }


def _as_text(pack: Mapping[str, Any]) -> str:
    return json.dumps(owner_pack_to_jsonable_dict(pack), indent=2, sort_keys=True)


__all__ = [
    "OwnerEvidenceItem",
    "build_owner_evidence_pack",
    "build_sanitized_evidence_template",
    "build_redaction_rules",
    "build_collection_checklist",
    "owner_pack_to_markdown",
    "owner_pack_to_jsonable_dict",
    "_as_text",
]
