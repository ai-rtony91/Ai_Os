"""Canonical, read-only engineering countdown for an AIOS mission."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from automation.orchestration.aios_packet_queue_planner import build_packet_queue_planner


SCHEMA = "AIOS_WORK_COUNTDOWN.v1"


def _hours(value: Any) -> float:
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return 0.0


def _receipt_is_creditable(receipt: Mapping[str, Any]) -> bool:
    status = str(receipt.get("status", "")).strip().lower()
    return bool(
        receipt.get("merged") is True
        and receipt.get("validated") is True
        and receipt.get("commit_sha")
        and status in {"complete", "completed", "passed"}
    )


def _estimate(item: Mapping[str, Any], key: str) -> float:
    estimates = item.get("engineering_hours", {})
    return _hours(estimates.get(key) if isinstance(estimates, Mapping) else 0)


def build_aios_work_countdown(
    *,
    mission: str,
    work_items: Sequence[Mapping[str, Any]],
    execution_receipts: Sequence[Mapping[str, Any]],
    workflow_state: Mapping[str, Any] | None = None,
    current_workflow_packet_id: str = "AIOS_WORK_COUNTDOWN_V1",
) -> dict[str, Any]:
    """Compose receipts, queue planning, controller state, and owner countdown."""

    controller_state = dict(workflow_state or {})
    receipt_by_packet = {
        str(receipt.get("packet_id")): receipt
        for receipt in execution_receipts
        if receipt.get("packet_id")
    }
    credited: list[dict[str, Any]] = []
    remaining: list[Mapping[str, Any]] = []
    hours_removed = 0.0

    for item in work_items:
        packet_id = str(item.get("packet_id", ""))
        receipt = receipt_by_packet.get(packet_id, {})
        if _receipt_is_creditable(receipt):
            removed = _estimate(item, "best")
            hours_removed += removed
            credited.append(
                {
                    "packet_id": packet_id,
                    "commit_sha": receipt.get("commit_sha"),
                    "engineering_hours_removed": removed,
                }
            )
        else:
            remaining.append(item)

    queue = build_packet_queue_planner(list(remaining))
    low = sum(_estimate(item, "low") for item in remaining)
    best = sum(_estimate(item, "best") for item in remaining)
    high = sum(_estimate(item, "high") for item in remaining)
    external_wait = sum(_hours(item.get("external_wait_hours")) for item in remaining)
    denominator = hours_removed + best
    completion = round((hours_removed / denominator) * 100, 1) if denominator else 100.0
    current_receipt = receipt_by_packet.get(current_workflow_packet_id, {})
    current_item = next(
        (item for item in work_items if str(item.get("packet_id")) == current_workflow_packet_id),
        {},
    )
    workflow_hours_removed = (
        _estimate(current_item, "best") if _receipt_is_creditable(current_receipt) else 0.0
    )
    selected = queue.get("selected_packet") or {}
    next_blocker = (
        selected.get("title")
        or selected.get("packet_id")
        or controller_state.get("next_safe_action")
        or "No verified engineering blocker is selectable."
    )
    confidence = "HIGH" if remaining and all(
        _estimate(item, "low") <= _estimate(item, "best") <= _estimate(item, "high")
        and _estimate(item, "best") > 0
        for item in remaining
    ) else "MEDIUM"

    return {
        "schema": SCHEMA,
        "mission": mission,
        "engineering_hours_remaining": {"low": low, "best": best, "high": high},
        "credited_merged_validated_engineering_hours": hours_removed,
        "hours_removed_by_this_workflow": workflow_hours_removed,
        "fifty_hour_work_weeks_remaining": {
            "low": round(low / 50, 2),
            "best": round(best / 50, 2),
            "high": round(high / 50, 2),
        },
        "derived_completion_percentage": completion,
        "forecast_confidence": confidence,
        "external_wait_hours": external_wait,
        "external_wait_excluded_from_engineering_hours": True,
        "credited_execution_receipts": credited,
        "uncredited_receipt_count": len(execution_receipts) - len(credited),
        "workflow_controller_state": controller_state,
        "queue_plan": queue,
        "next_verified_blocker": next_blocker,
        "owner_action": f"Review {selected.get('packet_id')}." if selected else "Review the countdown.",
        "protected_actions_performed": False,
    }


def build_owner_report(countdown: Mapping[str, Any]) -> str:
    hours = countdown["engineering_hours_remaining"]
    weeks = countdown["fifty_hour_work_weeks_remaining"]
    return "\n".join(
        [
            "PRIMARY ANCHOR",
            str(countdown.get("mission")),
            "",
            "ENGINEERING HOURS REMAINING",
            f"low={hours['low']} best={hours['best']} high={hours['high']}",
            "",
            "HOURS REMOVED THIS WORKFLOW",
            str(countdown.get("hours_removed_by_this_workflow")),
            "",
            "50-HOUR WORK WEEKS REMAINING",
            f"low={weeks['low']} best={weeks['best']} high={weeks['high']}",
            "",
            "EXTERNAL WAITING TIME",
            f"{countdown.get('external_wait_hours')} hours (excluded from engineering hours)",
            "",
            "COMPLETION",
            f"{countdown.get('derived_completion_percentage')}%",
            "",
            "CONFIDENCE",
            str(countdown.get("forecast_confidence")),
            "",
            "NEXT VERIFIED BLOCKER",
            str(countdown.get("next_verified_blocker")),
            "",
            "OWNER ACTION",
            str(countdown.get("owner_action")),
            "",
            "STATUS",
            "READY FOR OWNER REVIEW",
            "",
        ]
    )
