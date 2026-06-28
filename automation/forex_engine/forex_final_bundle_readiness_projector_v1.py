"""Final bundle projection for Forex remaining-closure readiness."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from . import forex_evidence_quality_validator_v1 as quality
from . import forex_review_ready_candidate_selector_v1 as selector
from . import forex_missing_evidence_catalog_v1 as catalog_lib


FINAL_BUNDLE_READY = "FINAL_BUNDLE_READY"
PARTIAL_EXTERNAL_EVIDENCE_REQUIRED = "PARTIAL_EXTERNAL_EVIDENCE_REQUIRED"
LOCAL_REPAIR_REQUIRED = "LOCAL_REPAIR_REQUIRED"
OWNER_APPROVAL_REQUIRED = "OWNER_APPROVAL_REQUIRED"
SAFETY_BLOCKED = "SAFETY_BLOCKED"
NOT_READY = "NOT_READY"


def _safe_time() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_final_bundle_map(
    catalog: Mapping[str, Any],
    quality_result: Mapping[str, Any],
    selector_result: Mapping[str, Any],
) -> dict[str, Any]:
    items = catalog.get("items", {})
    blocked: list[str] = []
    local_actions: list[str] = []
    owner_actions: list[str] = []
    forbidden_actions = [
        "broker_api_access",
        "live_trading",
        "money_movement",
        "production_activation",
    ]
    for entry in items.values():
        classification = str(entry.get("classification", catalog_lib.NOT_APPLICABLE))
        if entry.get("source") == "generated_catalog":
            continue
        if classification == catalog_lib.BROKER_API_REQUIRED:
            blocked.append("broker snapshot evidence")
        if classification == catalog_lib.CREDENTIAL_REQUIRED:
            blocked.append("credential boundary evidence")
            owner_actions.append("collect owner-approved credential evidence manifest")
        if classification == catalog_lib.TRADING_EXECUTION_REQUIRED:
            blocked.append("trading execution evidence")
            local_actions.append("collect deterministic execution readiness records")
        if classification == catalog_lib.PROTECTED_PUBLISH_REQUIRED:
            blocked.append("protected publish route")
            owner_actions.append("collect protected publish evidence")
    if selector_result.get("route") == selector.NEEDS_MORE_EVIDENCE:
        local_actions.append("complete missing evidence sections")
    if selector_result.get("route") in {selector.REVIEW_READY, selector.REJECT_LOW_SAMPLE}:
        owner_actions.append("confirm owner status and local evidence signoff")
    if quality_result.get("status") in {quality.INSUFFICIENT_SAMPLE, quality.EVIDENCE_REPAIRABLE}:
        local_actions.append("extend sample and evidence depth")
    return {
        "status_blockers": sorted(set(blocked)),
        "local_actions": local_actions,
        "owner_actions": owner_actions,
        "forbidden_actions": forbidden_actions,
        "bundle_items": len(items),
    }


def project_final_bundle_readiness(
    catalog: Mapping[str, Any],
    quality_result: Mapping[str, Any],
    selector_result: Mapping[str, Any],
    *,
    strict: bool = False,
) -> dict[str, Any]:
    del strict
    projector_map = build_final_bundle_map(catalog, quality_result, selector_result)
    blocked = projector_map.get("status_blockers", [])
    route = selector_result.get("route")
    quality_status = quality_result.get("status")
    has_external = any(
        entry.get("classification") in {
            catalog_lib.BROKER_API_REQUIRED,
            catalog_lib.CREDENTIAL_REQUIRED,
            catalog_lib.TRADING_EXECUTION_REQUIRED,
            catalog_lib.PROTECTED_PUBLISH_REQUIRED,
        }
        for entry in catalog.get("items", {}).values()
        if entry.get("source") != "generated_catalog"
    )
    if quality_status == quality.SAFETY_REJECT or route == selector.REJECT_UNSAFE:
        status = SAFETY_BLOCKED
    elif quality_status == quality.INSUFFICIENT_SAMPLE:
        status = LOCAL_REPAIR_REQUIRED
    elif route == selector.EXTERNAL_EVIDENCE_REQUIRED or has_external:
        status = PARTIAL_EXTERNAL_EVIDENCE_REQUIRED
    elif route == selector.REVIEW_READY and not blocked and quality_status == quality.EVIDENCE_PASS:
        status = FINAL_BUNDLE_READY
    elif route == selector.NEEDS_MORE_EVIDENCE:
        status = OWNER_APPROVAL_REQUIRED
    elif route in {selector.REJECT_LOW_SAMPLE, selector.REJECT_LOW_PROFIT_FACTOR, selector.REJECT_NEGATIVE_EXPECTANCY}:
        status = LOCAL_REPAIR_REQUIRED
    else:
        status = NOT_READY
    return {
        "projection_version": "1.0",
        "generated_at": _safe_time(),
        "status": status,
        "selector_route": route,
        "validator_status": quality_status,
        "bundle_map": projector_map,
        "items_reviewed": len(catalog.get("items", {})),
    }


def readiness_to_markdown(result: Mapping[str, Any]) -> str:
    bundle_map = result.get("bundle_map", {})
    lines = [
        "# Forex Final Bundle Readiness Projector V1",
        f"Generated: {result.get('generated_at')}",
        f"Status: {result.get('status')}",
        f"Selector route: {result.get('selector_route')}",
        f"Validator status: {result.get('validator_status')}",
        "",
        f"- Local actions: {len(bundle_map.get('local_actions', []))}",
        f"- Owner actions: {len(bundle_map.get('owner_actions', []))}",
        f"- Forbidden actions: {', '.join(bundle_map.get('forbidden_actions', []))}",
        "",
        "## Blockers",
    ]
    for item in bundle_map.get("status_blockers", []):
        lines.append(f"- {item}")
    return "\n".join(lines)


def readiness_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "projection_version": result.get("projection_version", "1.0"),
        "generated_at": result.get("generated_at"),
        "status": result.get("status"),
        "selector_route": result.get("selector_route"),
        "validator_status": result.get("validator_status"),
        "bundle_map": dict(result.get("bundle_map", {})),
        "items_reviewed": int(result.get("items_reviewed", 0)),
    }


__all__ = [
    "FINAL_BUNDLE_READY",
    "PARTIAL_EXTERNAL_EVIDENCE_REQUIRED",
    "LOCAL_REPAIR_REQUIRED",
    "OWNER_APPROVAL_REQUIRED",
    "SAFETY_BLOCKED",
    "NOT_READY",
    "build_final_bundle_map",
    "project_final_bundle_readiness",
    "readiness_to_markdown",
    "readiness_to_jsonable_dict",
]
