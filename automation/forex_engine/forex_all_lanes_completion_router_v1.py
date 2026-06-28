"""Completion router for Forex all-lanes goal states."""

from __future__ import annotations

from typing import Any, Mapping

from . import forex_all_lanes_gap_classifier_v1 as classifier_lib
from . import forex_all_lanes_goal_manifest_v1 as manifest_lib


ROUTER_VERSION = "1.0"
ROUTE_ALL_REPO_ACTIONABLE_CLOSED = "ROUTE_ALL_REPO_ACTIONABLE_CLOSED"
ROUTE_REPO_ACTIONABLE_REPAIR_REQUIRED = "ROUTE_REPO_ACTIONABLE_REPAIR_REQUIRED"


def _goals_by_status(goals: list[Mapping[str, Any]], status: str) -> list[dict[str, Any]]:
    return [dict(goal) for goal in goals if goal.get("current_status") == status]


def route_all_lanes_completion(
    manifest_payload: Mapping[str, Any] | None = None,
    classifier_payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    manifest = (
        manifest_lib.build_all_lanes_goal_manifest()
        if manifest_payload is None
        else manifest_lib.manifest_to_jsonable_dict(manifest_payload)
    )
    classifier = (
        classifier_lib.classify_all_lanes_gaps(manifest)
        if classifier_payload is None
        else classifier_lib.classifier_to_jsonable_dict(classifier_payload)
    )
    goals = [dict(goal) for goal in manifest.get("goals", [])]
    repo_actionable_open = classifier.get("repo_actionable_open_goals", [])
    route = (
        ROUTE_REPO_ACTIONABLE_REPAIR_REQUIRED
        if repo_actionable_open
        else ROUTE_ALL_REPO_ACTIONABLE_CLOSED
    )
    owner_next_actions = [
        "Review owner-protected and live/broker boundary items before any execution.",
        "Collect sanitized external evidence for external evidence blockers.",
        "Keep broker/API, credential, demo/live order, money movement, and production activation disabled.",
        "Publish this branch through the protected PR lane only after local validation is complete.",
    ]
    return {
        "router_version": ROUTER_VERSION,
        "generated_at": manifest_lib.GENERATED_AT,
        "packet_id": manifest_lib.PACKET_ID,
        "route": route,
        "goal_count": len(goals),
        "closed_on_main": _goals_by_status(goals, manifest_lib.CLOSED_ON_MAIN),
        "closed_by_this_campaign": _goals_by_status(goals, manifest_lib.CLOSED_BY_THIS_CAMPAIGN),
        "owner_protected": _goals_by_status(goals, manifest_lib.OWNER_PROTECTED_BOUNDARY),
        "external_evidence_required": _goals_by_status(goals, manifest_lib.EXTERNAL_EVIDENCE_REQUIRED),
        "live_or_broker_permission_required": _goals_by_status(
            goals,
            manifest_lib.LIVE_OR_BROKER_PERMISSION_REQUIRED,
        ),
        "safety_blocked": _goals_by_status(goals, manifest_lib.SAFETY_BLOCKED),
        "deferred": _goals_by_status(goals, manifest_lib.DEFERRED_WITH_REASON),
        "unknown_owner_review": _goals_by_status(goals, manifest_lib.UNKNOWN_REQUIRES_OWNER_REVIEW),
        "repo_actionable_open": [dict(goal) for goal in repo_actionable_open],
        "target_artifacts": sorted(
            {
                str(goal.get("target_artifact"))
                for goal in goals
                if goal.get("target_artifact") and goal.get("target_artifact") != "source artifact"
            },
        ),
        "owner_next_actions": owner_next_actions,
        "safety": dict(manifest.get("safety", {})),
    }


def router_to_jsonable_dict(payload: Mapping[str, Any]) -> dict[str, Any]:
    keys = [
        "closed_on_main",
        "closed_by_this_campaign",
        "owner_protected",
        "external_evidence_required",
        "live_or_broker_permission_required",
        "safety_blocked",
        "deferred",
        "unknown_owner_review",
        "repo_actionable_open",
    ]
    result = {
        "router_version": payload.get("router_version", ROUTER_VERSION),
        "generated_at": payload.get("generated_at", manifest_lib.GENERATED_AT),
        "packet_id": payload.get("packet_id", manifest_lib.PACKET_ID),
        "route": payload.get("route"),
        "goal_count": int(payload.get("goal_count", 0)),
        "target_artifacts": list(payload.get("target_artifacts", [])),
        "owner_next_actions": list(payload.get("owner_next_actions", [])),
        "safety": dict(payload.get("safety", {})),
    }
    for key in keys:
        result[key] = [dict(goal) for goal in payload.get(key, [])]
        result[f"{key}_count"] = len(result[key])
    return result


def router_to_markdown(payload: Mapping[str, Any]) -> str:
    data = router_to_jsonable_dict(payload)
    lines = [
        "# AIOS Forex All-Lanes Completion Router V1",
        f"Generated: {data.get('generated_at')}",
        f"Route: {data.get('route')}",
        f"Goal count: {data.get('goal_count')}",
        "",
        "## Route Counts",
        f"- Closed on main: {data.get('closed_on_main_count', 0)}",
        f"- Closed by this campaign: {data.get('closed_by_this_campaign_count', 0)}",
        f"- Owner protected: {data.get('owner_protected_count', 0)}",
        f"- External evidence required: {data.get('external_evidence_required_count', 0)}",
        f"- Live or broker permission required: {data.get('live_or_broker_permission_required_count', 0)}",
        f"- Safety blocked: {data.get('safety_blocked_count', 0)}",
        f"- Deferred: {data.get('deferred_count', 0)}",
        f"- Unknown owner review: {data.get('unknown_owner_review_count', 0)}",
        "",
        "## Owner Next Actions",
    ]
    for action in data.get("owner_next_actions", []):
        lines.append(f"- {action}")
    lines.extend(
        [
            "",
            "## Boundary",
            "- Router output is a local handoff only and does not authorize broker/API, credential, demo/live trade, money movement, production activation, commit, push, PR creation, or merge.",
        ],
    )
    return "\n".join(lines) + "\n"


__all__ = [
    "ROUTE_ALL_REPO_ACTIONABLE_CLOSED",
    "ROUTE_REPO_ACTIONABLE_REPAIR_REQUIRED",
    "ROUTER_VERSION",
    "route_all_lanes_completion",
    "router_to_jsonable_dict",
    "router_to_markdown",
]
