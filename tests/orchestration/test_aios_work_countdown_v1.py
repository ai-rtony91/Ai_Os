from __future__ import annotations

from automation.orchestration.aios_work_countdown_v1 import (
    SCHEMA,
    build_aios_work_countdown,
    build_owner_report,
)


def _item(packet_id: str, low: int, best: int, high: int, priority: str = "high") -> dict:
    return {
        "packet_id": packet_id,
        "title": f"Close {packet_id}",
        "lane": "forex-finish-line",
        "priority": priority,
        "milestone_value": best,
        "risk_level": "bounded",
        "status": "ready",
        "required_files": [f"automation/{packet_id.lower()}.py"],
        "validators": [f"pytest {packet_id}"],
        "engineering_hours": {"low": low, "best": best, "high": high},
        "external_wait_hours": 24,
    }


def test_countdown_credits_only_merged_validated_receipts() -> None:
    result = build_aios_work_countdown(
        mission="FIRST WITHDRAWABLE DOLLAR",
        work_items=[_item("DONE", 4, 5, 6), _item("NEXT", 8, 10, 15)],
        execution_receipts=[
            {"packet_id": "DONE", "status": "complete", "merged": True, "validated": True, "commit_sha": "abc"},
            {"packet_id": "NEXT", "status": "complete", "merged": False, "validated": True, "commit_sha": "def"},
        ],
        workflow_state={"controller_status": "BLOCKED"},
        current_workflow_packet_id="DONE",
    )
    assert result["schema"] == SCHEMA
    assert result["credited_merged_validated_engineering_hours"] == 5
    assert result["hours_removed_by_this_workflow"] == 5
    assert result["engineering_hours_remaining"] == {"low": 8, "best": 10, "high": 15}
    assert result["fifty_hour_work_weeks_remaining"]["best"] == 0.2
    assert result["derived_completion_percentage"] == 33.3
    assert result["external_wait_hours"] == 24
    assert result["external_wait_excluded_from_engineering_hours"] is True
    assert result["queue_plan"]["selected_packet"]["packet_id"] == "NEXT"
    assert result["owner_action"] == "Review NEXT."
    assert result["protected_actions_performed"] is False


def test_unmerged_or_unvalidated_work_never_reduces_remaining_hours() -> None:
    result = build_aios_work_countdown(
        mission="FIRST WITHDRAWABLE DOLLAR",
        work_items=[_item("OPEN", 2, 3, 5)],
        execution_receipts=[
            {"packet_id": "OPEN", "status": "complete", "merged": True, "validated": False, "commit_sha": "abc"}
        ],
        workflow_state={},
    )
    assert result["credited_merged_validated_engineering_hours"] == 0
    assert result["hours_removed_by_this_workflow"] == 0
    assert result["engineering_hours_remaining"]["best"] == 3
    assert result["uncredited_receipt_count"] == 1


def test_owner_report_has_exactly_one_owner_action_heading() -> None:
    result = build_aios_work_countdown(
        mission="FIRST WITHDRAWABLE DOLLAR",
        work_items=[_item("NEXT", 1, 2, 3)],
        execution_receipts=[],
        workflow_state={},
    )
    report = build_owner_report(result)
    assert report.count("OWNER ACTION") == 1
    assert "low=1.0 best=2.0 high=3.0" in report
    assert "READY FOR OWNER REVIEW" in report
