"""Compose final owner review packets from the owner evidence return lane."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

from . import forex_closure_gap_router_v1 as router_lib
from . import forex_owner_evidence_return_intake_v1 as intake_lib
from . import forex_owner_evidence_return_validator_v1 as validator_lib


FINAL_PACKET_READY = "FINAL_OWNER_REVIEW_PACKET_READY"
FINAL_PACKET_PENDING_OWNER_RETURN = "FINAL_OWNER_REVIEW_PACKET_PENDING_OWNER_RETURN"
FINAL_PACKET_PENDING_LOCAL_REPAIR = "FINAL_OWNER_REVIEW_PACKET_PENDING_LOCAL_REPAIR"
FINAL_PACKET_BLOCKED = "FINAL_OWNER_REVIEW_PACKET_BLOCKED"
FINAL_PACKET_INVALID = "FINAL_OWNER_REVIEW_PACKET_INVALID"

PACKET_ID = "AIOS-FOREX-OWNER-EVIDENCE-RETURN-ORCHESTRATION-V1"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _readable_action(action: str) -> str:
    return action.replace("_", " ").lower()


def compose_final_owner_review_packet(
    intake_payload: Mapping[str, Any],
    validator_payload: Mapping[str, Any],
    route_payload: Mapping[str, Any],
    *,
    strict: bool = False,
) -> dict[str, Any]:
    if not (
        isinstance(intake_payload, Mapping)
        and isinstance(validator_payload, Mapping)
        and isinstance(route_payload, Mapping)
    ):
        return {
            "packet_version": "1.0",
            "generated_at": _now_iso(),
            "packet_id": PACKET_ID,
            "status": FINAL_PACKET_INVALID,
            "route": router_lib.ROUTE_INVALID_STATE,
            "strict_mode": strict,
            "next_safe_action": "Re-run with valid payloads.",
            "safety": {
                "local_only": True,
                "broker_api": False,
                "trading": False,
                "money_movement": False,
            },
        }

    route = str(route_payload.get("route", router_lib.ROUTE_INVALID_STATE))
    owner_gap_families = list(route_payload.get("owner_gap_families", []))
    local_gap_families = list(route_payload.get("local_gap_families", []))
    validation_status = str(validator_payload.get("status"))
    intake_status = str(intake_payload.get("status"))
    route_blockers = list(route_payload.get("status_blockers", []))

    if route == router_lib.ROUTE_READY_FOR_REVIEW:
        packet_status = FINAL_PACKET_READY
        next_safe = "move packet to owner handoff and keep execution boundaries closed."
    elif route == router_lib.ROUTE_OWNER_EVIDENCE_REQUIRED or owner_gap_families:
        packet_status = FINAL_PACKET_PENDING_OWNER_RETURN
        next_safe = "owner evidence return is required before handoff."
    elif route == router_lib.ROUTE_LOCAL_REPAIR:
        packet_status = FINAL_PACKET_PENDING_LOCAL_REPAIR
        next_safe = "close local evidence gaps and rerun closure lane."
    elif route == router_lib.ROUTE_BLOCKED_BY_SAFETY:
        packet_status = FINAL_PACKET_BLOCKED
        next_safe = "sanitize sensitive/broker command text from evidence inputs."
    else:
        packet_status = FINAL_PACKET_INVALID
        next_safe = "repair payload types before handoff."

    packet_items = [
        {
            "family": item.get("family"),
            "classification": item.get("classification"),
            "requested": item.get("requested"),
            "evidence_present": item.get("evidence_present"),
            "expected_filename": item.get("expected_filename"),
        }
        for item in intake_payload.get("intake_items", [])
        if item.get("requested")
    ]
    packet_owner_actions = [
        f"Collect owner evidence for {family}" for family in owner_gap_families
    ]
    packet_local_actions = [
        f"Repair local evidence for {family}" for family in local_gap_families
    ]
    if validation_status == validator_lib.OWNER_RETURN_REPAIRABLE:
        packet_local_actions.append("Resolve validation repair instructions.")
    if route_blockers:
        packet_local_actions.extend(route_blockers)
    if strict and packet_status == FINAL_PACKET_READY:
        packet_owner_actions.append("Owner confirmation required in strict mode before final handoff.")

    return {
        "packet_version": "1.0",
        "generated_at": _now_iso(),
        "packet_id": PACKET_ID,
        "status": packet_status,
        "route": route,
        "strict_mode": strict,
        "intake_status": intake_status,
        "validator_status": validation_status,
        "owner_gap_families": owner_gap_families,
        "local_gap_families": local_gap_families,
        "owner_actions": packet_owner_actions,
        "local_actions": packet_local_actions,
        "requested_items": packet_items,
        "next_safe_action": next_safe,
        "summary_counts": {
            "requested_items": len(packet_items),
            "owner_gaps": len(owner_gap_families),
            "local_gaps": len(local_gap_families),
        },
        "safety": {
            "local_only": True,
            "broker_api": False,
            "broker_execution": False,
            "credential_access": False,
            "live_trading": False,
            "money_movement": False,
            "production_activation": False,
            "env_file_read": False,
            "network_calls": False,
            "order_submission": False,
        },
        "reopen_action": _readable_action(next_safe),
    }


def packet_to_markdown(payload: Mapping[str, Any]) -> str:
    summary = payload.get("summary_counts", {})
    lines = [
        "# Forex Final Owner Review Packet Composer V1",
        f"Generated: {payload.get('generated_at')}",
        f"packet_id: {payload.get('packet_id')}",
        f"Status: {payload.get('status')}",
        f"Route: {payload.get('route')}",
        f"Strict mode: {payload.get('strict_mode', False)}",
        "",
        f"- requested_items: {summary.get('requested_items', 0)}",
        f"- owner_gaps: {summary.get('owner_gaps', 0)}",
        f"- local_gaps: {summary.get('local_gaps', 0)}",
        "",
        "## Owner Actions",
    ]
    for item in payload.get("owner_actions", []):
        lines.append(f"- {item}")
    if not payload.get("owner_actions"):
        lines.append("- none")
    lines.append("")
    lines.append("## Local Actions")
    for item in payload.get("local_actions", []):
        lines.append(f"- {item}")
    if not payload.get("local_actions"):
        lines.append("- none")
    lines.append("")
    lines.append("## Requested Families")
    for family in payload.get("requested_items", []):
        lines.append(
            f"- {family.get('family', 'UNKNOWN')} ({family.get('classification')})"
        )
    lines.append("")
    lines.append(f"Next safe action: {payload.get('next_safe_action')}")
    lines.append("")
    lines.append("## Safety Boundaries")
    for key, value in payload.get("safety", {}).items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def packet_to_jsonable_dict(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "packet_version": payload.get("packet_version", "1.0"),
        "generated_at": payload.get("generated_at"),
        "packet_id": payload.get("packet_id"),
        "status": payload.get("status"),
        "route": payload.get("route"),
        "strict_mode": bool(payload.get("strict_mode", False)),
        "intake_status": payload.get("intake_status"),
        "validator_status": payload.get("validator_status"),
        "owner_actions": list(payload.get("owner_actions", [])),
        "local_actions": list(payload.get("local_actions", [])),
        "owner_gap_families": list(payload.get("owner_gap_families", [])),
        "local_gap_families": list(payload.get("local_gap_families", [])),
        "requested_items": list(payload.get("requested_items", [])),
        "summary_counts": dict(payload.get("summary_counts", {})),
        "safety": dict(payload.get("safety", {})),
        "next_safe_action": payload.get("next_safe_action"),
    }


__all__ = [
    "FINAL_PACKET_BLOCKED",
    "FINAL_PACKET_INVALID",
    "FINAL_PACKET_PENDING_LOCAL_REPAIR",
    "FINAL_PACKET_PENDING_OWNER_RETURN",
    "FINAL_PACKET_READY",
    "PACKET_ID",
    "compose_final_owner_review_packet",
    "packet_to_jsonable_dict",
    "packet_to_markdown",
]
