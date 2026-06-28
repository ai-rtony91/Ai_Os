"""Gap router for the Forex owner evidence return lane."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from . import forex_evidence_quality_validator_v1 as quality
from . import forex_owner_evidence_return_intake_v1 as intake_lib
from . import forex_owner_evidence_return_validator_v1 as owner_validator


ROUTE_READY_FOR_REVIEW = "ROUTE_READY_FOR_REVIEW"
ROUTE_OWNER_EVIDENCE_REQUIRED = "ROUTE_OWNER_EVIDENCE_REQUIRED"
ROUTE_LOCAL_REPAIR = "ROUTE_LOCAL_REPAIR"
ROUTE_BLOCKED_BY_SAFETY = "ROUTE_BLOCKED_BY_SAFETY"
ROUTE_INVALID_STATE = "ROUTE_INVALID_STATE"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def route_owner_evidence_closure(
    intake_payload: Mapping[str, Any],
    validator_payload: Mapping[str, Any],
    *,
    strict: bool = False,
) -> dict[str, Any]:
    if not isinstance(intake_payload, Mapping) or not isinstance(validator_payload, Mapping):
        return {
            "router_version": "1.0",
            "route": ROUTE_INVALID_STATE,
            "generated_at": _now_iso(),
            "status_blockers": ["invalid payload types provided"],
            "next_steps": ["provide deterministic intake and validator payloads"],
            "owner_gap_families": [],
            "local_gap_families": [],
            "strict_mode": strict,
        }

    intake_items = list(intake_payload.get("intake_items", []))
    if not intake_items and strict:
        route = ROUTE_INVALID_STATE
        blockers = ["intake payload has no items in strict mode"]
        next_steps = ["run intake with a populated catalog"]
    else:
        owner_gap_families = list(intake_payload.get("owner_required_families", []))
        local_gap_families = list(intake_payload.get("local_repair_families", []))
        if validator_payload.get("status") == owner_validator.OWNER_RETURN_BLOCKED:
            route = ROUTE_BLOCKED_BY_SAFETY
            blockers = [
                "validator flagged sensitive assignment or broker command content",
            ]
            next_steps = ["replace sensitive content and rerun validator"]
        elif owner_gap_families:
            route = ROUTE_OWNER_EVIDENCE_REQUIRED
            blockers = [f"owner evidence missing for {family}" for family in owner_gap_families]
            next_steps = ["collect owner evidence for missing families"]
        elif local_gap_families and validator_payload.get("status") != quality.EVIDENCE_PASS:
            route = ROUTE_LOCAL_REPAIR
            blockers = ["local evidence quality and sample depth need completion"]
            next_steps = ["repair local evidence payloads and rerun"]
        elif validator_payload.get("status") == owner_validator.OWNER_RETURN_REPAIRABLE:
            route = ROUTE_LOCAL_REPAIR
            blockers = ["validator returned repairable status"]
            next_steps = ["resolve missing sections and sample count in owner return evidence"]
        else:
            route = ROUTE_READY_FOR_REVIEW
            blockers = []
            next_steps = ["compose owner review packet for final handoff"]
            if strict:
                next_steps.append("strict mode owner confirmation remains required for human review")

    return {
        "router_version": "1.0",
        "generated_at": _now_iso(),
        "route": route,
        "strict_mode": strict,
        "owner_gap_families": list(intake_payload.get("owner_required_families", [])),
        "local_gap_families": list(intake_payload.get("local_repair_families", [])),
        "status_blockers": blockers,
        "next_steps": next_steps,
    }


def router_to_markdown(payload: Mapping[str, Any]) -> str:
    lines = [
        "# Forex Closure Gap Router V1",
        f"Generated: {payload.get('generated_at')}",
        f"Route: {payload.get('route')}",
        f"Strict mode: {payload.get('strict_mode', False)}",
        f"- Owner gap families: {', '.join(payload.get('owner_gap_families', []))}",
        f"- Local gap families: {', '.join(payload.get('local_gap_families', []))}",
        "",
        "## Status Blockers",
    ]
    for blocker in payload.get("status_blockers", []):
        lines.append(f"- {blocker}")
    if not payload.get("status_blockers"):
        lines.append("- none")
    lines.append("")
    lines.append("## Next Steps")
    for step in payload.get("next_steps", []):
        lines.append(f"- {step}")
    if not payload.get("next_steps"):
        lines.append("- none")
    return "\n".join(lines)


def router_to_jsonable_dict(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "router_version": payload.get("router_version", "1.0"),
        "generated_at": payload.get("generated_at"),
        "route": payload.get("route"),
        "strict_mode": bool(payload.get("strict_mode", False)),
        "owner_gap_families": list(payload.get("owner_gap_families", [])),
        "local_gap_families": list(payload.get("local_gap_families", [])),
        "status_blockers": list(payload.get("status_blockers", [])),
        "next_steps": list(payload.get("next_steps", [])),
    }


__all__ = [
    "ROUTE_BLOCKED_BY_SAFETY",
    "ROUTE_INVALID_STATE",
    "ROUTE_LOCAL_REPAIR",
    "ROUTE_OWNER_EVIDENCE_REQUIRED",
    "ROUTE_READY_FOR_REVIEW",
    "route_owner_evidence_closure",
    "router_to_jsonable_dict",
    "router_to_markdown",
]
