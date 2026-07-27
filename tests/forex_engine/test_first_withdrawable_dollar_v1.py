from __future__ import annotations

import copy
import math

import pytest

from automation.forex_engine.first_withdrawable_dollar_v1 import (
    build_first_withdrawable_dollar,
    stable_json,
)


def receipt(**updates: object) -> dict[str, object]:
    value: dict[str, object] = {
        "packet_id": "PKT-1", "canonical": True,
        "evidence_provenance": "canonical_execution_receipt",
        "pr_id": "1323", "merged": True,
        "merge_commit_sha": "515f8fea756c7d30c9d292d292229305369b56ca",
        "test_command": "python -m pytest tests -q", "test_conclusion": "passed",
        "ci_check_id": "AIOS Governance", "ci_conclusion": "success",
        "engineering_hours": 10.0,
    }
    value.update(updates)
    return value


def evidence(*receipts: object, **updates: object) -> dict[str, object]:
    value: dict[str, object] = {
        "execution_receipts": list(receipts), "expected_packet_count": len(receipts),
        "remaining_hours": {"low": 40.0, "best": 90.0, "high": 140.0},
        "external_dependencies": ["SANITIZED_PRACTICE_RECEIPT"],
        "owner_action_required": True,
    }
    value.update(updates)
    return value


def test_presence_alone_and_missing_evidence_fail_closed() -> None:
    result = build_first_withdrawable_dollar({"repository_files": ["present.py"]})
    assert result["hours_completed"] == 0
    assert result["repository_presence_credit"] == 0
    assert result["derived_completion_percentage"] is None
    assert result["hours_remaining_best"] is None


def test_complete_receipt_and_bounds_are_projected() -> None:
    result = build_first_withdrawable_dollar(evidence(receipt()))
    assert result["hours_completed"] == 10
    assert result["credited_packet_count"] == 1
    assert result["weeks_remaining_50h_low"] == 0.8
    assert result["weeks_remaining_50h_best"] == 1.8
    assert result["weeks_remaining_50h_high"] == 2.8
    assert result["derived_completion_percentage"] == 10.0
    assert result["confidence"] == 100.0
    assert result["external_dependencies"] == ["SANITIZED_PRACTICE_RECEIPT"]
    assert result["owner_action_required"] is True


@pytest.mark.parametrize(("updates", "reason"), [
    ({"merged": False}, "merged_state_not_true"),
    ({"pr_id": ""}, "pr_id_missing_or_placeholder"),
    ({"merge_commit_sha": "invalid"}, "merge_commit_sha_invalid"),
    ({"test_command": ""}, "test_command_missing_or_placeholder"),
    ({"test_conclusion": "failed"}, "test_conclusion_not_passing"),
    ({"ci_check_id": ""}, "ci_check_id_missing_or_placeholder"),
    ({"ci_conclusion": "cancelled"}, "ci_conclusion_not_passing"),
    ({"evidence_provenance": "TODO"}, "evidence_provenance_missing_or_placeholder"),
    ({"canonical": False}, "canonical_marker_missing"),
])
def test_incomplete_receipts_receive_no_credit(updates: dict[str, object], reason: str) -> None:
    result = build_first_withdrawable_dollar(evidence(receipt(**updates)))
    assert result["hours_completed"] == 0
    assert result["credited_packet_count"] == 0
    assert reason in result["receipt_results"][0]["reasons"]


@pytest.mark.parametrize("value", [-1, "10", True, math.inf, math.nan])
def test_invalid_hours_fail_closed(value: object) -> None:
    result = build_first_withdrawable_dollar(evidence(receipt(engineering_hours=value)))
    assert result["hours_completed"] == 0
    assert "engineering_hours_invalid" in result["receipt_results"][0]["reasons"]


def test_duplicates_and_conflicting_shas_fail_closed() -> None:
    other = receipt(merge_commit_sha="abcdef1234567")
    result = build_first_withdrawable_dollar(evidence(receipt(), other))
    assert result["hours_completed"] == 0
    assert result["confidence_basis"]["conflicts"] == ["PKT-1"]
    assert result["highest_verified_blocker"] == "REPAIR_CONFLICTING_CANONICAL_EXECUTION_RECEIPTS"


@pytest.mark.parametrize("bounds", [
    {"low": 2, "best": 1, "high": 3}, {"low": -1, "best": 2, "high": 3},
    {"low": 1, "best": "2", "high": 3}, {},
])
def test_invalid_remaining_bounds_return_null(bounds: dict[str, object]) -> None:
    result = build_first_withdrawable_dollar(evidence(receipt(), remaining_hours=bounds))
    assert result["hours_remaining_low"] is None
    assert result["derived_completion_percentage"] is None
    assert result["confidence"] == 75.0


def test_input_immutability_stable_json_and_permissions() -> None:
    source = evidence(receipt())
    before = copy.deepcopy(source)
    first = build_first_withdrawable_dollar(source)
    second = build_first_withdrawable_dollar(source)
    assert source == before
    assert stable_json(first) == stable_json(second)
    assert first["source_evidence_modified"] is False
    assert first["protected_actions"] and not any(first["protected_actions"].values())
