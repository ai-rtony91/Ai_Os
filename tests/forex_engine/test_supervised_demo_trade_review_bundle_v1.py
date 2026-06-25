from __future__ import annotations

import json

import pytest

from automation.forex_engine.supervised_demo_trade_review_bundle_v1 import (
    SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_BLOCKED,
    SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_READY,
    build_sample_supervised_demo_trade_review_bundle_blocked_input,
    build_sample_supervised_demo_trade_review_bundle_ready_input,
    build_supervised_demo_trade_review_bundle,
    supervised_demo_trade_review_bundle_to_jsonable_dict,
    supervised_demo_trade_review_bundle_to_markdown,
    supervised_demo_trade_review_bundle_to_operator_text,
)


PERMISSION_FLAGS = (
    "demo_execution_allowed",
    "broker_action_allowed",
    "real_money_allowed",
    "compounding_allowed",
    "bank_movement_allowed",
    "live_trading_allowed",
    "credential_access_allowed",
    "account_id_persistence_allowed",
)


def test_review_bundle_ready_sample_passes() -> None:
    result = build_supervised_demo_trade_review_bundle(
        build_sample_supervised_demo_trade_review_bundle_ready_input()
    )

    assert result.classification == SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_READY
    assert result.bundle_review_allowed is True


def test_review_bundle_blocked_sample_blocks() -> None:
    result = build_supervised_demo_trade_review_bundle(
        build_sample_supervised_demo_trade_review_bundle_blocked_input()
    )

    assert result.classification == SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_BLOCKED
    assert result.bundle_review_allowed is False
    assert result.blocked_actions


@pytest.mark.parametrize(
    "section_name",
    (
        "Executive Summary",
        "Snapshot Review",
        "Candidate Review",
        "Risk Review",
        "Position Sizing",
        "Order Plan",
        "Operator Ticket",
        "Post-Trade Evidence",
        "Feedback Routing",
    ),
)
def test_bundle_includes_review_section(section_name: str) -> None:
    result = build_supervised_demo_trade_review_bundle()

    assert section_name in result.review_sections


def test_bundle_includes_blocked_actions() -> None:
    result = build_supervised_demo_trade_review_bundle()

    assert "broker action" in result.blocked_actions
    assert "real money" in result.blocked_actions


def test_bundle_includes_exact_owner_warning() -> None:
    result = build_supervised_demo_trade_review_bundle()

    assert result.owner_warning == "Do not execute unless Anthony explicitly approves."


def test_bundle_operator_text_is_plain_english() -> None:
    text = supervised_demo_trade_review_bundle_to_operator_text(build_supervised_demo_trade_review_bundle())

    assert "Supervised demo trade review bundle" in text
    assert "Do not execute unless Anthony explicitly approves." in text
    assert "No trade was placed" in text


def test_bundle_markdown_has_title() -> None:
    markdown = supervised_demo_trade_review_bundle_to_markdown(build_supervised_demo_trade_review_bundle())

    assert markdown.startswith("# Supervised Demo Trade Review Bundle V1")


def test_bundle_json_has_required_keys() -> None:
    payload = supervised_demo_trade_review_bundle_to_jsonable_dict(build_supervised_demo_trade_review_bundle())

    for key in (
        "classification",
        "bundle_review_allowed",
        "readiness_bridge_status",
        "operator_summary",
        "owner_warning",
        "blocked_actions",
        "review_sections",
        "next_safe_action",
    ):
        assert key in payload
    assert json.loads(json.dumps(payload))["classification"] == SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_READY


def test_bundle_keeps_all_permissions_false() -> None:
    result = build_supervised_demo_trade_review_bundle()

    for flag in PERMISSION_FLAGS:
        assert getattr(result, flag) is False


def test_bundle_json_keeps_all_permissions_false() -> None:
    payload = supervised_demo_trade_review_bundle_to_jsonable_dict(build_supervised_demo_trade_review_bundle())

    for flag in PERMISSION_FLAGS:
        assert payload[flag] is False
