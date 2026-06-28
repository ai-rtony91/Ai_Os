"""Operating-readiness projector for the Forex all-lanes campaign."""

from __future__ import annotations

from typing import Any, Mapping

from . import forex_all_lanes_completion_router_v1 as router_lib
from . import forex_all_lanes_goal_manifest_v1 as manifest_lib


PROJECTOR_VERSION = "1.0"
DEFERRED_OWNER_VALIDATION = "DEFERRED_OWNER_VALIDATION"
REPO_REVIEW_READY_NO_EXECUTION = "REPO_REVIEW_READY_NO_EXECUTION"
REPO_REPAIR_REQUIRED_NO_EXECUTION = "REPO_REPAIR_REQUIRED_NO_EXECUTION"


def project_all_lanes_operating_readiness(
    router_payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    router = (
        router_lib.route_all_lanes_completion()
        if router_payload is None
        else router_lib.router_to_jsonable_dict(router_payload)
    )
    remaining_blockers = (
        int(router.get("owner_protected_count", 0))
        + int(router.get("external_evidence_required_count", 0))
        + int(router.get("live_or_broker_permission_required_count", 0))
        + int(router.get("safety_blocked_count", 0))
        + int(router.get("deferred_count", 0))
        + int(router.get("unknown_owner_review_count", 0))
        + int(router.get("repo_actionable_open_count", 0))
    )
    if int(router.get("repo_actionable_open_count", 0)):
        status = REPO_REPAIR_REQUIRED_NO_EXECUTION
    elif remaining_blockers:
        status = DEFERRED_OWNER_VALIDATION
    else:
        status = REPO_REVIEW_READY_NO_EXECUTION
    return {
        "projector_version": PROJECTOR_VERSION,
        "generated_at": manifest_lib.GENERATED_AT,
        "packet_id": manifest_lib.PACKET_ID,
        "status": status,
        "final_operating_readiness_status": DEFERRED_OWNER_VALIDATION,
        "dashboard_safe_summary": {
            "status": status,
            "repo_actionable_open": int(router.get("repo_actionable_open_count", 0)),
            "remaining_owner_or_external_blockers": remaining_blockers,
            "message": "Forex repo-actionable campaign work is classified locally; operating approval remains deferred to Human Owner validation.",
        },
        "readiness_flags": {
            "repo_actionable_closed": int(router.get("repo_actionable_open_count", 0)) == 0,
            "owner_validation_required": True,
            "external_evidence_required": int(router.get("external_evidence_required_count", 0)) > 0,
            "broker_permission_required": int(router.get("live_or_broker_permission_required_count", 0)) > 0,
            "safety_review_required": int(router.get("safety_blocked_count", 0)) > 0,
            "demo_live_execution_allowed": False,
            "broker_api_allowed": False,
            "credential_access_allowed": False,
            "money_movement_allowed": False,
            "production_activation_allowed": False,
            "profit_claim_supported": False,
        },
        "remaining_blockers_count": remaining_blockers,
        "owner_next_actions": list(router.get("owner_next_actions", [])),
    }


def projector_to_jsonable_dict(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "projector_version": payload.get("projector_version", PROJECTOR_VERSION),
        "generated_at": payload.get("generated_at", manifest_lib.GENERATED_AT),
        "packet_id": payload.get("packet_id", manifest_lib.PACKET_ID),
        "status": payload.get("status"),
        "final_operating_readiness_status": payload.get(
            "final_operating_readiness_status",
            DEFERRED_OWNER_VALIDATION,
        ),
        "dashboard_safe_summary": dict(payload.get("dashboard_safe_summary", {})),
        "readiness_flags": dict(payload.get("readiness_flags", {})),
        "remaining_blockers_count": int(payload.get("remaining_blockers_count", 0)),
        "owner_next_actions": list(payload.get("owner_next_actions", [])),
    }


def projector_to_markdown(payload: Mapping[str, Any]) -> str:
    data = projector_to_jsonable_dict(payload)
    flags = data.get("readiness_flags", {})
    lines = [
        "# AIOS Forex All-Lanes Operating Readiness Projector V1",
        f"Generated: {data.get('generated_at')}",
        f"Status: {data.get('status')}",
        f"Final operating-readiness status: {data.get('final_operating_readiness_status')}",
        f"Remaining blockers: {data.get('remaining_blockers_count')}",
        "",
        "## Dashboard-Safe Summary",
        f"- {data.get('dashboard_safe_summary', {}).get('message')}",
        "",
        "## Readiness Flags",
    ]
    for key in sorted(flags):
        lines.append(f"- {key}: {flags[key]}")
    lines.extend(
        [
            "",
            "## Boundary",
            "- This is not autonomous trading readiness, profitable trading readiness, broker readiness, or production approval.",
        ],
    )
    return "\n".join(lines) + "\n"


__all__ = [
    "DEFERRED_OWNER_VALIDATION",
    "PROJECTOR_VERSION",
    "REPO_REPAIR_REQUIRED_NO_EXECUTION",
    "REPO_REVIEW_READY_NO_EXECUTION",
    "project_all_lanes_operating_readiness",
    "projector_to_jsonable_dict",
    "projector_to_markdown",
]
