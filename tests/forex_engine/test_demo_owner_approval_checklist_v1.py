from __future__ import annotations

import json
from dataclasses import replace

from automation.forex_engine.demo_owner_approval_checklist_v1 import (
    CHECKLIST_ITEM_NAMES,
    DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_INCOMPLETE,
    DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_PROTECTED_ACTION_MISUNDERSTOOD,
    DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_RISK_NOT_ACKNOWLEDGED,
    DEMO_OWNER_APPROVAL_CHECKLIST_READY,
    build_sample_blocked_owner_approval_checklist_input,
    build_sample_ready_owner_approval_checklist_input,
    demo_owner_approval_checklist_to_jsonable_dict,
    demo_owner_approval_checklist_to_markdown,
    demo_owner_approval_checklist_to_operator_text,
    evaluate_demo_owner_approval_checklist,
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


def test_ready_checklist_passes() -> None:
    result = evaluate_demo_owner_approval_checklist(build_sample_ready_owner_approval_checklist_input())

    assert result.classification == DEMO_OWNER_APPROVAL_CHECKLIST_READY
    assert result.checklist_review_allowed is True
    assert result.missing_items == ()


def test_incomplete_checklist_blocks() -> None:
    sample = build_sample_ready_owner_approval_checklist_input()
    result = evaluate_demo_owner_approval_checklist(replace(sample, snapshot_reviewed=False))

    assert result.classification == DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_INCOMPLETE
    assert "snapshot_reviewed" in result.missing_items


def test_missing_risk_acknowledgement_blocks() -> None:
    sample = build_sample_ready_owner_approval_checklist_input()
    result = evaluate_demo_owner_approval_checklist(replace(sample, max_loss_understood=False))

    assert result.classification == DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_RISK_NOT_ACKNOWLEDGED


def test_misunderstanding_broker_action_blocks() -> None:
    sample = build_sample_ready_owner_approval_checklist_input()
    result = evaluate_demo_owner_approval_checklist(
        replace(sample, no_broker_action_by_codex_understood=False)
    )

    assert result.classification == DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_PROTECTED_ACTION_MISUNDERSTOOD


def test_misunderstanding_real_money_blocks() -> None:
    sample = build_sample_ready_owner_approval_checklist_input()
    result = evaluate_demo_owner_approval_checklist(replace(sample, no_real_money_understood=False))

    assert result.classification == DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_PROTECTED_ACTION_MISUNDERSTOOD


def test_misunderstanding_compounding_blocks() -> None:
    sample = build_sample_ready_owner_approval_checklist_input()
    result = evaluate_demo_owner_approval_checklist(replace(sample, no_compounding_understood=False))

    assert result.classification == DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_PROTECTED_ACTION_MISUNDERSTOOD


def test_misunderstanding_bank_movement_blocks() -> None:
    sample = build_sample_ready_owner_approval_checklist_input()
    result = evaluate_demo_owner_approval_checklist(replace(sample, no_bank_movement_understood=False))

    assert result.classification == DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_PROTECTED_ACTION_MISUNDERSTOOD


def test_blocked_checklist_sample_blocks() -> None:
    result = evaluate_demo_owner_approval_checklist(build_sample_blocked_owner_approval_checklist_input())

    assert result.classification == DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_RISK_NOT_ACKNOWLEDGED
    assert result.missing_items


def test_checklist_markdown_has_title() -> None:
    markdown = demo_owner_approval_checklist_to_markdown(evaluate_demo_owner_approval_checklist())

    assert markdown.startswith("# Demo Owner Approval Checklist V1")


def test_checklist_output_json_serializable() -> None:
    payload = demo_owner_approval_checklist_to_jsonable_dict(evaluate_demo_owner_approval_checklist())

    assert json.loads(json.dumps(payload))["classification"] == DEMO_OWNER_APPROVAL_CHECKLIST_READY


def test_checklist_operator_text_is_plain_english() -> None:
    text = demo_owner_approval_checklist_to_operator_text(evaluate_demo_owner_approval_checklist())

    assert "Owner approval checklist is ready" in text
    assert "No trade was placed" in text


def test_checklist_contains_all_required_items() -> None:
    result = evaluate_demo_owner_approval_checklist()

    for item in CHECKLIST_ITEM_NAMES:
        assert item in result.checklist_items


def test_checklist_permissions_false() -> None:
    result = evaluate_demo_owner_approval_checklist()

    for flag in PERMISSION_FLAGS:
        assert getattr(result, flag) is False


def test_checklist_json_permissions_false() -> None:
    payload = demo_owner_approval_checklist_to_jsonable_dict(evaluate_demo_owner_approval_checklist())

    for flag in PERMISSION_FLAGS:
        assert payload[flag] is False
