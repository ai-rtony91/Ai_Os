"""Owner boundary gate for Forex all-lanes campaign output."""

from __future__ import annotations

from typing import Any, Mapping

from . import forex_all_lanes_goal_manifest_v1 as manifest_lib
from . import forex_all_lanes_operating_readiness_projector_v1 as projector_lib


OWNER_BOUNDARY_GATE_VERSION = "1.0"
OWNER_BOUNDARY_ENFORCED = "OWNER_BOUNDARY_ENFORCED"

PROTECTED_ACTIONS_NOT_PERFORMED = (
    "git add",
    "git commit",
    "git push",
    "gh pr create",
    "gh pr checks",
    "gh pr merge",
    "branch deletion",
    "reset / clean / stash",
    "file deletion",
    "broker/API connection",
    "credential access",
    "account access",
    "demo/live trade execution",
    "order placement",
    "order closure",
    "money movement",
    "production activation",
    "scheduler/daemon/webhook activation",
    "final operating approval",
)


def evaluate_all_lanes_owner_boundary(
    projector_payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    projector = (
        projector_lib.project_all_lanes_operating_readiness()
        if projector_payload is None
        else projector_lib.projector_to_jsonable_dict(projector_payload)
    )
    flags = dict(projector.get("readiness_flags", {}))
    return {
        "owner_boundary_gate_version": OWNER_BOUNDARY_GATE_VERSION,
        "generated_at": manifest_lib.GENERATED_AT,
        "packet_id": manifest_lib.PACKET_ID,
        "status": OWNER_BOUNDARY_ENFORCED,
        "final_operating_readiness_status": projector.get(
            "final_operating_readiness_status",
            projector_lib.DEFERRED_OWNER_VALIDATION,
        ),
        "protected_actions_not_performed": list(PROTECTED_ACTIONS_NOT_PERFORMED),
        "owner_required_before": [
            "broker/API connection",
            "credential or account access",
            "demo/live order placement or closure",
            "money movement",
            "production activation",
            "commit, push, PR creation, check watch, merge, or branch deletion",
        ],
        "boundary_flags": {
            "auto_approval_allowed": False,
            "broker_api_called": False,
            "credentials_read": False,
            "demo_live_trade_authorized": False,
            "orders_placed": False,
            "orders_closed": False,
            "money_moved": False,
            "production_activated": False,
            "profit_claim_made": False,
            "owner_validation_required": bool(flags.get("owner_validation_required", True)),
        },
        "owner_next_actions": [
            "Review generated all-lanes reports.",
            "Run the owner publish/check block if local validation is acceptable.",
            "Open a protected PR lane; do not push directly to main.",
            "Provide separate approval before any broker, credential, account, demo/live, or production action.",
        ],
    }


def owner_boundary_to_jsonable_dict(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "owner_boundary_gate_version": payload.get(
            "owner_boundary_gate_version",
            OWNER_BOUNDARY_GATE_VERSION,
        ),
        "generated_at": payload.get("generated_at", manifest_lib.GENERATED_AT),
        "packet_id": payload.get("packet_id", manifest_lib.PACKET_ID),
        "status": payload.get("status"),
        "final_operating_readiness_status": payload.get("final_operating_readiness_status"),
        "protected_actions_not_performed": list(payload.get("protected_actions_not_performed", [])),
        "owner_required_before": list(payload.get("owner_required_before", [])),
        "boundary_flags": dict(payload.get("boundary_flags", {})),
        "owner_next_actions": list(payload.get("owner_next_actions", [])),
    }


def owner_boundary_to_markdown(payload: Mapping[str, Any]) -> str:
    data = owner_boundary_to_jsonable_dict(payload)
    lines = [
        "# AIOS Forex All-Lanes Owner Boundary Gate V1",
        f"Generated: {data.get('generated_at')}",
        f"Status: {data.get('status')}",
        f"Final operating-readiness status: {data.get('final_operating_readiness_status')}",
        "",
        "## Protected Actions Not Performed",
    ]
    for action in data.get("protected_actions_not_performed", []):
        lines.append(f"- {action}")
    lines.append("")
    lines.append("## Owner Required Before")
    for action in data.get("owner_required_before", []):
        lines.append(f"- {action}")
    lines.extend(
        [
            "",
            "## Boundary Language",
            "- This report is local evidence only.",
            "- It does not authorize broker/API access, credential access, account access, demo/live trading, order placement, order closure, money movement, production activation, commit, push, PR creation, check watch, merge, or branch deletion.",
        ],
    )
    return "\n".join(lines) + "\n"


__all__ = [
    "OWNER_BOUNDARY_ENFORCED",
    "OWNER_BOUNDARY_GATE_VERSION",
    "PROTECTED_ACTIONS_NOT_PERFORMED",
    "evaluate_all_lanes_owner_boundary",
    "owner_boundary_to_jsonable_dict",
    "owner_boundary_to_markdown",
]
