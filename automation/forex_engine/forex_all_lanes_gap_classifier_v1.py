"""Gap classifier for the Forex all-lanes campaign."""

from __future__ import annotations

from typing import Any, Mapping

from . import forex_all_lanes_goal_manifest_v1 as manifest_lib


CLASSIFIER_VERSION = "1.0"
CLASSIFIER_ALL_REPO_ACTIONABLE_CLOSED = "CLASSIFIER_ALL_REPO_ACTIONABLE_CLOSED"
CLASSIFIER_REPO_WORK_REQUIRED = "CLASSIFIER_REPO_WORK_REQUIRED"
CLASSIFIER_OWNER_REVIEW_REQUIRED = "CLASSIFIER_OWNER_REVIEW_REQUIRED"


def classify_all_lanes_gaps(manifest_payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = (
        manifest_lib.build_all_lanes_goal_manifest()
        if manifest_payload is None
        else manifest_lib.manifest_to_jsonable_dict(manifest_payload)
    )
    goals = [dict(goal) for goal in payload.get("goals", [])]
    remaining = [
        goal
        for goal in goals
        if goal.get("current_status")
        not in {
            manifest_lib.CLOSED_ON_MAIN,
            manifest_lib.CLOSED_BY_THIS_CAMPAIGN,
        }
    ]
    repo_actionable_open = [
        goal
        for goal in goals
        if goal.get("repo_actionable")
        and goal.get("current_status")
        not in {
            manifest_lib.CLOSED_ON_MAIN,
            manifest_lib.CLOSED_BY_THIS_CAMPAIGN,
        }
    ]
    if repo_actionable_open:
        status = CLASSIFIER_REPO_WORK_REQUIRED
    elif remaining:
        status = CLASSIFIER_OWNER_REVIEW_REQUIRED
    else:
        status = CLASSIFIER_ALL_REPO_ACTIONABLE_CLOSED
    blocker_counts: dict[str, int] = {}
    for goal in goals:
        blocker = str(goal.get("blocker_class", "unknown"))
        blocker_counts[blocker] = blocker_counts.get(blocker, 0) + 1
    return {
        "classifier_version": CLASSIFIER_VERSION,
        "generated_at": manifest_lib.GENERATED_AT,
        "packet_id": manifest_lib.PACKET_ID,
        "status": status,
        "goal_count": len(goals),
        "status_counts": dict(payload.get("status_counts", {})),
        "blocker_counts": blocker_counts,
        "remaining_gap_count": len(remaining),
        "repo_actionable_open_count": len(repo_actionable_open),
        "repo_actionable_closed_count": sum(
            1
            for goal in goals
            if goal.get("repo_actionable")
            and goal.get("current_status") == manifest_lib.CLOSED_BY_THIS_CAMPAIGN
        ),
        "owner_protected_count": sum(
            1 for goal in goals if goal.get("current_status") == manifest_lib.OWNER_PROTECTED_BOUNDARY
        ),
        "external_evidence_count": sum(
            1 for goal in goals if goal.get("current_status") == manifest_lib.EXTERNAL_EVIDENCE_REQUIRED
        ),
        "live_or_broker_permission_count": sum(
            1
            for goal in goals
            if goal.get("current_status") == manifest_lib.LIVE_OR_BROKER_PERMISSION_REQUIRED
        ),
        "safety_blocked_count": sum(
            1 for goal in goals if goal.get("current_status") == manifest_lib.SAFETY_BLOCKED
        ),
        "deferred_count": sum(
            1 for goal in goals if goal.get("current_status") == manifest_lib.DEFERRED_WITH_REASON
        ),
        "unknown_owner_review_count": sum(
            1
            for goal in goals
            if goal.get("current_status") == manifest_lib.UNKNOWN_REQUIRES_OWNER_REVIEW
        ),
        "remaining_gaps": remaining,
        "repo_actionable_open_goals": repo_actionable_open,
        "safety": dict(payload.get("safety", {})),
    }


def classifier_to_jsonable_dict(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "classifier_version": payload.get("classifier_version", CLASSIFIER_VERSION),
        "generated_at": payload.get("generated_at", manifest_lib.GENERATED_AT),
        "packet_id": payload.get("packet_id", manifest_lib.PACKET_ID),
        "status": payload.get("status"),
        "goal_count": int(payload.get("goal_count", 0)),
        "status_counts": dict(payload.get("status_counts", {})),
        "blocker_counts": dict(payload.get("blocker_counts", {})),
        "remaining_gap_count": int(payload.get("remaining_gap_count", 0)),
        "repo_actionable_open_count": int(payload.get("repo_actionable_open_count", 0)),
        "repo_actionable_closed_count": int(payload.get("repo_actionable_closed_count", 0)),
        "owner_protected_count": int(payload.get("owner_protected_count", 0)),
        "external_evidence_count": int(payload.get("external_evidence_count", 0)),
        "live_or_broker_permission_count": int(payload.get("live_or_broker_permission_count", 0)),
        "safety_blocked_count": int(payload.get("safety_blocked_count", 0)),
        "deferred_count": int(payload.get("deferred_count", 0)),
        "unknown_owner_review_count": int(payload.get("unknown_owner_review_count", 0)),
        "remaining_gaps": [dict(goal) for goal in payload.get("remaining_gaps", [])],
        "repo_actionable_open_goals": [
            dict(goal) for goal in payload.get("repo_actionable_open_goals", [])
        ],
        "safety": dict(payload.get("safety", {})),
    }


def classifier_to_markdown(payload: Mapping[str, Any]) -> str:
    lines = [
        "# AIOS Forex All-Lanes Gap Classifier V1",
        f"Generated: {payload.get('generated_at', manifest_lib.GENERATED_AT)}",
        f"Status: {payload.get('status')}",
        f"Goal count: {payload.get('goal_count', 0)}",
        f"Remaining gap count: {payload.get('remaining_gap_count', 0)}",
        f"Repo-actionable open count: {payload.get('repo_actionable_open_count', 0)}",
        "",
        "## Gap Counts",
        f"- Repo-actionable closed: {payload.get('repo_actionable_closed_count', 0)}",
        f"- Owner protected: {payload.get('owner_protected_count', 0)}",
        f"- External evidence: {payload.get('external_evidence_count', 0)}",
        f"- Live or broker permission: {payload.get('live_or_broker_permission_count', 0)}",
        f"- Safety blocked: {payload.get('safety_blocked_count', 0)}",
        f"- Deferred: {payload.get('deferred_count', 0)}",
        f"- Unknown owner review: {payload.get('unknown_owner_review_count', 0)}",
        "",
        "## Boundary",
        "- Classification only. No broker/API, credential, demo/live trade, order, money movement, or production activation occurred.",
    ]
    return "\n".join(lines) + "\n"


__all__ = [
    "CLASSIFIER_ALL_REPO_ACTIONABLE_CLOSED",
    "CLASSIFIER_OWNER_REVIEW_REQUIRED",
    "CLASSIFIER_REPO_WORK_REQUIRED",
    "CLASSIFIER_VERSION",
    "classifier_to_jsonable_dict",
    "classifier_to_markdown",
    "classify_all_lanes_gaps",
]
