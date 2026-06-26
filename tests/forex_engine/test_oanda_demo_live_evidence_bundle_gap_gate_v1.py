from __future__ import annotations

import json

import pytest

from automation.forex_engine.oanda_demo_live_evidence_bundle_gap_gate_v1 import (
    CLASSIFICATION_BLOCKED_EXPECTANCY,
    CLASSIFICATION_BLOCKED_UNSAFE,
    CLASSIFICATION_LIVE_APPROVAL_STILL_FALSE,
    CLASSIFICATION_OWNER_REVIEW_READY,
    CLASSIFICATION_REQUIRE_MORE_EVIDENCE,
    LIVE_GAP_WARNING,
    OWNER_WARNING,
    PERMISSION_DEFAULTS,
    VERSION,
    build_sample_blocked_live_evidence_gap_gate_input,
    build_sample_missing_live_evidence_gap_gate_input,
    build_sample_partial_live_evidence_gap_gate_input,
    build_sample_ready_live_evidence_gap_gate_input,
    build_sample_rejected_expectancy_blocked_input,
    build_sample_strong_expectancy_missing_live_evidence_input,
    build_sample_strong_expectancy_partial_live_evidence_input,
    build_sample_unsafe_expectancy_blocked_input,
    build_sample_unsafe_live_evidence_gap_gate_input,
    build_sample_weak_expectancy_blocked_input,
    evaluate_oanda_demo_live_evidence_bundle_gap_gate,
    oanda_demo_live_evidence_bundle_gap_gate_to_jsonable_dict,
    oanda_demo_live_evidence_bundle_gap_gate_to_markdown,
    oanda_demo_live_evidence_bundle_gap_gate_to_operator_text,
)


def _gate(builder):
    return evaluate_oanda_demo_live_evidence_bundle_gap_gate(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (build_sample_missing_live_evidence_gap_gate_input, CLASSIFICATION_REQUIRE_MORE_EVIDENCE),
        (build_sample_partial_live_evidence_gap_gate_input, CLASSIFICATION_REQUIRE_MORE_EVIDENCE),
        (build_sample_ready_live_evidence_gap_gate_input, CLASSIFICATION_OWNER_REVIEW_READY),
        (build_sample_blocked_live_evidence_gap_gate_input, CLASSIFICATION_BLOCKED_EXPECTANCY),
        (build_sample_unsafe_live_evidence_gap_gate_input, CLASSIFICATION_BLOCKED_UNSAFE),
    ),
)
def test_gap_gate_sample_classifications(builder, classification: str):
    assert _gate(builder).classification == classification


def test_gap_gate_version_constant():
    assert VERSION == "oanda_demo_live_evidence_bundle_gap_gate_v1"


def test_gap_gate_owner_review_ready_when_all_present():
    assert _gate(build_sample_ready_live_evidence_gap_gate_input).owner_gap_review_allowed is True


def test_gap_gate_requires_more_evidence_when_missing():
    assert _gate(build_sample_missing_live_evidence_gap_gate_input).requires_more_evidence is True


def test_gap_gate_blocks_expectancy_failure():
    assert _gate(build_sample_blocked_live_evidence_gap_gate_input).blocked is True


def test_gap_gate_blocks_unsafe():
    assert _gate(build_sample_unsafe_live_evidence_gap_gate_input).blocked is True


def test_gap_gate_live_approval_still_false():
    result = _gate(build_sample_ready_live_evidence_gap_gate_input)
    assert result.live_approval_still_false is True
    assert CLASSIFICATION_LIVE_APPROVAL_STILL_FALSE in result.secondary_classifications


def test_gap_gate_json_serializable():
    json.dumps(oanda_demo_live_evidence_bundle_gap_gate_to_jsonable_dict(_gate(build_sample_ready_live_evidence_gap_gate_input)))


def test_gap_gate_markdown_title():
    markdown = oanda_demo_live_evidence_bundle_gap_gate_to_markdown(
        _gate(build_sample_ready_live_evidence_gap_gate_input)
    )
    assert markdown.startswith("# OANDA Demo Live Evidence Bundle Gap Gate V1")


def test_gap_gate_operator_text_plain():
    text = oanda_demo_live_evidence_bundle_gap_gate_to_operator_text(
        _gate(build_sample_missing_live_evidence_gap_gate_input)
    )
    assert "Live evidence bundle gap gate status" in text


@pytest.mark.parametrize("flag", sorted(PERMISSION_DEFAULTS))
def test_gap_gate_permissions_false(flag: str):
    assert _gate(build_sample_ready_live_evidence_gap_gate_input).protected_permission_flags[flag] is False


def test_gap_gate_owner_warning_present():
    assert _gate(build_sample_missing_live_evidence_gap_gate_input).owner_warning == OWNER_WARNING


def test_gap_gate_live_gap_warning_present():
    assert _gate(build_sample_missing_live_evidence_gap_gate_input).live_gap_warning == LIVE_GAP_WARNING


def test_gap_gate_surfaces_evidence_gaps():
    result = _gate(build_sample_partial_live_evidence_gap_gate_input)
    assert result.missing_items
    assert result.owner_action_required_items
    assert result.blocked_items


def test_gap_gate_preview_is_preview_only():
    assert _gate(build_sample_ready_live_evidence_gap_gate_input).evidence_bundle_preview[
        "preview_only"
    ] is True


def test_gap_gate_ready_review_is_not_live_approval():
    result = _gate(build_sample_ready_live_evidence_gap_gate_input)
    assert result.evidence_bundle_preview["live_evidence_bundle_approved"] is False


@pytest.mark.parametrize(
    "builder",
    (
        build_sample_strong_expectancy_missing_live_evidence_input,
        build_sample_strong_expectancy_partial_live_evidence_input,
        build_sample_weak_expectancy_blocked_input,
        build_sample_rejected_expectancy_blocked_input,
        build_sample_unsafe_expectancy_blocked_input,
    ),
)
def test_gap_gate_global_sample_builders_exist(builder):
    assert builder()
