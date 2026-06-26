from __future__ import annotations

import json
from dataclasses import replace

import pytest

from automation.forex_engine.demo_manual_execution_exception_checklist_v1 import (
    build_sample_blocked_manual_execution_exception_checklist_input,
)
from automation.forex_engine.demo_manual_execution_exception_scope_gate_v1 import (
    build_sample_execution_authority_blocked_input,
)
from automation.forex_engine.supervised_demo_manual_execution_exception_packet_v1 import (
    SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_CHECKLIST,
    SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_OWNER_APPROVAL,
    SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_PROTECTED_ACTION,
    SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_SCOPE,
    SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_READY_FOR_OWNER_REVIEW,
    build_sample_supervised_demo_manual_execution_exception_packet_blocked_input,
    build_sample_supervised_demo_manual_execution_exception_packet_ready_input,
    build_supervised_demo_manual_execution_exception_packet,
    supervised_demo_manual_execution_exception_packet_to_jsonable_dict,
    supervised_demo_manual_execution_exception_packet_to_markdown,
    supervised_demo_manual_execution_exception_packet_to_operator_text,
)
from automation.forex_engine.supervised_demo_owner_approval_epic_v1 import (
    build_sample_supervised_demo_owner_approval_blocked_input,
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


def test_exception_packet_ready_sample_passes() -> None:
    result = build_supervised_demo_manual_execution_exception_packet(
        build_sample_supervised_demo_manual_execution_exception_packet_ready_input()
    )

    assert result.classification == SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_READY_FOR_OWNER_REVIEW
    assert result.exception_packet_review_allowed is True


def test_exception_packet_blocked_sample_blocks() -> None:
    result = build_supervised_demo_manual_execution_exception_packet(
        build_sample_supervised_demo_manual_execution_exception_packet_blocked_input()
    )

    assert result.classification == SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_OWNER_APPROVAL
    assert result.exception_packet_review_allowed is False


def test_owner_approval_blocked_blocks_packet() -> None:
    sample = build_sample_supervised_demo_manual_execution_exception_packet_ready_input()
    result = build_supervised_demo_manual_execution_exception_packet(
        replace(sample, owner_approval_input=build_sample_supervised_demo_owner_approval_blocked_input())
    )

    assert result.classification == SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_OWNER_APPROVAL


def test_scope_blocked_blocks_packet() -> None:
    sample = build_sample_supervised_demo_manual_execution_exception_packet_ready_input()
    result = build_supervised_demo_manual_execution_exception_packet(
        replace(sample, scope_input=build_sample_execution_authority_blocked_input())
    )

    assert result.classification == SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_SCOPE


def test_checklist_blocked_blocks_packet() -> None:
    sample = build_sample_supervised_demo_manual_execution_exception_packet_ready_input()
    result = build_supervised_demo_manual_execution_exception_packet(
        replace(sample, checklist_input=build_sample_blocked_manual_execution_exception_checklist_input())
    )

    assert result.classification == SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_CHECKLIST


def test_protected_action_attempt_blocks_packet() -> None:
    sample = build_sample_supervised_demo_manual_execution_exception_packet_ready_input()
    result = build_supervised_demo_manual_execution_exception_packet(
        replace(sample, protected_action_requested=True)
    )

    assert result.classification == SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_BLOCKED_PROTECTED_ACTION


@pytest.mark.parametrize(
    "field_name",
    (
        "owner_approval_status",
        "scope_status",
        "checklist_status",
        "selected_strategy",
        "candidate_id",
        "instrument",
        "direction",
        "entry_type",
        "proposed_units",
        "entry_price",
        "stop_loss",
        "take_profit",
        "max_loss",
        "expected_reward",
        "reward_to_risk",
        "owner_warning",
        "exception_warning",
        "required_phrase",
        "blocked_actions",
        "post_trade_evidence_required",
        "feedback_routing_required",
    ),
)
def test_packet_includes_required_field(field_name: str) -> None:
    result = build_supervised_demo_manual_execution_exception_packet()

    assert getattr(result, field_name) not in ("", None, ())


def test_packet_markdown_has_title() -> None:
    markdown = supervised_demo_manual_execution_exception_packet_to_markdown(
        build_supervised_demo_manual_execution_exception_packet()
    )

    assert markdown.startswith("# Supervised Demo Manual Execution Exception Packet V1")


def test_packet_operator_text_is_plain_english() -> None:
    text = supervised_demo_manual_execution_exception_packet_to_operator_text(
        build_supervised_demo_manual_execution_exception_packet()
    )

    assert "manual execution exception packet status" in text
    assert "No trade was placed" in text


def test_packet_json_has_required_keys() -> None:
    payload = supervised_demo_manual_execution_exception_packet_to_jsonable_dict(
        build_supervised_demo_manual_execution_exception_packet()
    )

    for key in (
        "classification",
        "exception_packet_review_allowed",
        "owner_approval_status",
        "scope_status",
        "checklist_status",
        "entry_type",
        "post_trade_evidence_required",
        "feedback_routing_required",
        "next_safe_action",
    ):
        assert key in payload
    assert json.loads(json.dumps(payload))["classification"] == (
        SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_READY_FOR_OWNER_REVIEW
    )


@pytest.mark.parametrize("flag", PERMISSION_FLAGS)
def test_packet_keeps_permissions_false(flag: str) -> None:
    result = build_supervised_demo_manual_execution_exception_packet()

    assert getattr(result, flag) is False


def test_exception_packet_never_sets_broker_action_allowed_true() -> None:
    result = build_supervised_demo_manual_execution_exception_packet()

    assert result.broker_action_allowed is False


def test_exception_packet_never_sets_demo_execution_allowed_true() -> None:
    result = build_supervised_demo_manual_execution_exception_packet()

    assert result.demo_execution_allowed is False
