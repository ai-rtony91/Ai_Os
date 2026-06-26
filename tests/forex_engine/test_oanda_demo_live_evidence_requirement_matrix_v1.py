from __future__ import annotations

import json

import pytest

from automation.forex_engine.oanda_demo_live_evidence_requirement_matrix_v1 import (
    ALLOWED_EVIDENCE_STATUSES,
    CLASSIFICATION_BLOCKED_EMPTY,
    CLASSIFICATION_BLOCKED_UNSAFE,
    CLASSIFICATION_READY,
    LIVE_GAP_WARNING,
    OWNER_WARNING,
    PERMISSION_DEFAULTS,
    VERSION,
    build_default_oanda_demo_live_evidence_requirements,
    build_oanda_demo_live_evidence_requirement_matrix,
    build_sample_live_evidence_requirement_matrix_blocked_input,
    build_sample_live_evidence_requirement_matrix_ready_input,
    build_sample_live_evidence_requirement_matrix_unsafe_input,
    build_sample_rejected_expectancy_blocked_input,
    build_sample_strong_expectancy_missing_live_evidence_input,
    build_sample_strong_expectancy_partial_live_evidence_input,
    build_sample_unsafe_expectancy_blocked_input,
    build_sample_weak_expectancy_blocked_input,
    oanda_demo_live_evidence_requirement_matrix_to_jsonable_dict,
    oanda_demo_live_evidence_requirement_matrix_to_markdown,
    oanda_demo_live_evidence_requirement_matrix_to_operator_text,
)


REQUIRED_ITEM_IDS = tuple(
    requirement.item_id for requirement in build_default_oanda_demo_live_evidence_requirements()
)


def _ready_result():
    return build_oanda_demo_live_evidence_requirement_matrix(
        build_sample_live_evidence_requirement_matrix_ready_input()
    )


def test_requirement_matrix_ready_classification():
    assert _ready_result().classification == CLASSIFICATION_READY


def test_requirement_matrix_blocked_empty_classification():
    result = build_oanda_demo_live_evidence_requirement_matrix(
        build_sample_live_evidence_requirement_matrix_blocked_input()
    )
    assert result.classification == CLASSIFICATION_BLOCKED_EMPTY


def test_requirement_matrix_blocked_unsafe_classification():
    result = build_oanda_demo_live_evidence_requirement_matrix(
        build_sample_live_evidence_requirement_matrix_unsafe_input()
    )
    assert result.classification == CLASSIFICATION_BLOCKED_UNSAFE


def test_requirement_matrix_version_constant():
    assert VERSION == "oanda_demo_live_evidence_requirement_matrix_v1"


def test_requirement_matrix_exact_requirement_count_stable():
    assert _ready_result().requirement_count == 28


def test_requirement_matrix_includes_all_required_item_ids():
    assert _ready_result().required_item_ids == REQUIRED_ITEM_IDS


@pytest.mark.parametrize("item_id", REQUIRED_ITEM_IDS)
def test_requirement_matrix_contains_each_required_item_id(item_id: str):
    assert item_id in _ready_result().required_item_ids


@pytest.mark.parametrize("item_id", REQUIRED_ITEM_IDS)
def test_requirement_matrix_requirement_rows_are_required(item_id: str):
    requirement = next(row for row in _ready_result().requirements if row.item_id == item_id)
    assert requirement.required is True


@pytest.mark.parametrize("item_id", REQUIRED_ITEM_IDS)
def test_requirement_matrix_requirement_rows_have_categories(item_id: str):
    requirement = next(row for row in _ready_result().requirements if row.item_id == item_id)
    assert requirement.category


def test_requirement_matrix_supports_owner_action_required_status():
    assert "OWNER_ACTION_REQUIRED" in ALLOWED_EVIDENCE_STATUSES


def test_requirement_matrix_json_serializable():
    json.dumps(oanda_demo_live_evidence_requirement_matrix_to_jsonable_dict(_ready_result()))


def test_requirement_matrix_markdown_title():
    assert oanda_demo_live_evidence_requirement_matrix_to_markdown(_ready_result()).startswith(
        "# OANDA Demo Live Evidence Requirement Matrix V1"
    )


def test_requirement_matrix_operator_text_plain():
    text = oanda_demo_live_evidence_requirement_matrix_to_operator_text(_ready_result())
    assert "Live evidence requirement matrix status" in text


@pytest.mark.parametrize("flag", sorted(PERMISSION_DEFAULTS))
def test_requirement_matrix_permissions_false(flag: str):
    assert _ready_result().protected_permission_flags[flag] is False


def test_requirement_matrix_owner_warning_present():
    assert _ready_result().owner_warning == OWNER_WARNING


def test_requirement_matrix_live_gap_warning_present():
    assert _ready_result().live_gap_warning == LIVE_GAP_WARNING


def test_requirement_matrix_no_trade_placed_note_present():
    assert "No trade placed by this packet." in _ready_result().safety_notes


def test_requirement_matrix_no_broker_call_note_present():
    assert "No broker call was made by this packet." in _ready_result().safety_notes


def test_requirement_matrix_strong_missing_sample_builder_exists():
    assert build_sample_strong_expectancy_missing_live_evidence_input()


def test_requirement_matrix_strong_partial_sample_builder_exists():
    assert build_sample_strong_expectancy_partial_live_evidence_input()


def test_requirement_matrix_weak_blocked_sample_builder_exists():
    assert build_sample_weak_expectancy_blocked_input()


def test_requirement_matrix_rejected_blocked_sample_builder_exists():
    assert build_sample_rejected_expectancy_blocked_input()


def test_requirement_matrix_unsafe_blocked_sample_builder_exists():
    assert build_sample_unsafe_expectancy_blocked_input()
