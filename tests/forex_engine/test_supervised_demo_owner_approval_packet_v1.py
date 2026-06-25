from __future__ import annotations

import json
from dataclasses import replace

import pytest

from automation.forex_engine.demo_owner_approval_checklist_v1 import (
    build_sample_blocked_owner_approval_checklist_input,
    build_sample_ready_owner_approval_checklist_input,
)
from automation.forex_engine.demo_owner_approval_phrase_gate_v1 import (
    build_sample_missing_owner_approval_phrase_input,
    build_sample_valid_owner_approval_phrase_input,
)
from automation.forex_engine.supervised_demo_owner_approval_packet_v1 import (
    SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_CHECKLIST,
    SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_PHRASE,
    SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_PROTECTED_ACTION,
    SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_READINESS,
    SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_READY_FOR_OWNER_REVIEW,
    SupervisedDemoOwnerApprovalPacketInput,
    build_sample_supervised_demo_owner_approval_packet_blocked_input,
    build_sample_supervised_demo_owner_approval_packet_ready_input,
    build_supervised_demo_owner_approval_packet,
    supervised_demo_owner_approval_packet_to_jsonable_dict,
    supervised_demo_owner_approval_packet_to_markdown,
    supervised_demo_owner_approval_packet_to_operator_text,
)
from automation.forex_engine.supervised_demo_trade_readiness_epic_v1 import (
    build_sample_supervised_demo_trade_readiness_blocked_input,
    build_sample_supervised_demo_trade_readiness_ready_input,
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


def _ready_packet_input() -> SupervisedDemoOwnerApprovalPacketInput:
    return build_sample_supervised_demo_owner_approval_packet_ready_input()


def test_owner_packet_ready_sample_passes() -> None:
    result = build_supervised_demo_owner_approval_packet(_ready_packet_input())

    assert result.classification == SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_READY_FOR_OWNER_REVIEW
    assert result.owner_packet_review_allowed is True


def test_owner_packet_blocked_sample_blocks() -> None:
    result = build_supervised_demo_owner_approval_packet(
        build_sample_supervised_demo_owner_approval_packet_blocked_input()
    )

    assert result.classification == SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_READINESS
    assert result.owner_packet_review_allowed is False


def test_readiness_blocked_blocks_packet() -> None:
    sample = _ready_packet_input()
    result = build_supervised_demo_owner_approval_packet(
        replace(sample, readiness_input=build_sample_supervised_demo_trade_readiness_blocked_input())
    )

    assert result.classification == SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_READINESS


def test_phrase_blocked_blocks_packet() -> None:
    sample = _ready_packet_input()
    result = build_supervised_demo_owner_approval_packet(
        replace(sample, phrase_input=build_sample_missing_owner_approval_phrase_input())
    )

    assert result.classification == SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_PHRASE


def test_checklist_blocked_blocks_packet() -> None:
    sample = _ready_packet_input()
    result = build_supervised_demo_owner_approval_packet(
        replace(sample, checklist_input=build_sample_blocked_owner_approval_checklist_input())
    )

    assert result.classification == SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_CHECKLIST


def test_protected_action_attempt_blocks_packet() -> None:
    sample = _ready_packet_input()
    result = build_supervised_demo_owner_approval_packet(
        replace(sample, protected_action_requested=True)
    )

    assert result.classification == SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_BLOCKED_PROTECTED_ACTION


@pytest.mark.parametrize(
    "field_name",
    (
        "readiness_status",
        "phrase_status",
        "checklist_status",
        "selected_strategy",
        "candidate_id",
        "instrument",
        "direction",
        "proposed_units",
        "entry_price",
        "stop_loss",
        "take_profit",
        "max_loss",
        "expected_reward",
        "reward_to_risk",
        "owner_warning",
        "required_phrase",
        "blocked_actions",
    ),
)
def test_packet_includes_required_field(field_name: str) -> None:
    result = build_supervised_demo_owner_approval_packet()

    assert getattr(result, field_name) not in ("", None, ())


def test_packet_markdown_has_title() -> None:
    markdown = supervised_demo_owner_approval_packet_to_markdown(build_supervised_demo_owner_approval_packet())

    assert markdown.startswith("# Supervised Demo Owner Approval Packet V1")


def test_packet_operator_text_is_plain_english() -> None:
    text = supervised_demo_owner_approval_packet_to_operator_text(build_supervised_demo_owner_approval_packet())

    assert "owner approval packet status" in text
    assert "No trade was placed" in text


def test_packet_json_has_required_keys() -> None:
    payload = supervised_demo_owner_approval_packet_to_jsonable_dict(
        build_supervised_demo_owner_approval_packet()
    )

    for key in (
        "classification",
        "owner_packet_review_allowed",
        "readiness_status",
        "phrase_status",
        "checklist_status",
        "selected_strategy",
        "required_phrase",
        "next_safe_action",
    ):
        assert key in payload
    assert json.loads(json.dumps(payload))["classification"] == (
        SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_READY_FOR_OWNER_REVIEW
    )


def test_packet_keeps_all_permissions_false() -> None:
    result = build_supervised_demo_owner_approval_packet()

    for flag in PERMISSION_FLAGS:
        assert getattr(result, flag) is False


def test_packet_json_keeps_all_permissions_false() -> None:
    payload = supervised_demo_owner_approval_packet_to_jsonable_dict(
        build_supervised_demo_owner_approval_packet()
    )

    for flag in PERMISSION_FLAGS:
        assert payload[flag] is False


def test_owner_packet_never_sets_broker_action_allowed_true() -> None:
    result = build_supervised_demo_owner_approval_packet(
        SupervisedDemoOwnerApprovalPacketInput(
            readiness_input=build_sample_supervised_demo_trade_readiness_ready_input(),
            phrase_input=build_sample_valid_owner_approval_phrase_input(),
            checklist_input=build_sample_ready_owner_approval_checklist_input(),
        )
    )

    assert result.broker_action_allowed is False


def test_owner_packet_never_sets_demo_execution_allowed_true() -> None:
    result = build_supervised_demo_owner_approval_packet()

    assert result.demo_execution_allowed is False
