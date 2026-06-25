from __future__ import annotations

import json

from automation.forex_engine.demo_owner_approval_phrase_gate_v1 import (
    DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_BROKER_ACTION_SCOPE,
    DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_EXECUTION_SCOPE,
    DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_MISSING,
    DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_NOT_EXACT,
    DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_REAL_MONEY_SCOPE,
    DEMO_OWNER_APPROVAL_PHRASE_VALID_FOR_MANUAL_REVIEW,
    OWNER_WARNING,
    REQUIRED_OWNER_APPROVAL_PHRASE,
    DemoOwnerApprovalPhraseGateInput,
    build_sample_missing_owner_approval_phrase_input,
    build_sample_valid_owner_approval_phrase_input,
    build_sample_wrong_scope_owner_approval_phrase_input,
    demo_owner_approval_phrase_gate_to_jsonable_dict,
    demo_owner_approval_phrase_gate_to_markdown,
    demo_owner_approval_phrase_gate_to_operator_text,
    evaluate_demo_owner_approval_phrase_gate,
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


def test_valid_approval_phrase_passes() -> None:
    result = evaluate_demo_owner_approval_phrase_gate(build_sample_valid_owner_approval_phrase_input())

    assert result.classification == DEMO_OWNER_APPROVAL_PHRASE_VALID_FOR_MANUAL_REVIEW
    assert result.approval_phrase_review_allowed is True


def test_missing_phrase_blocks() -> None:
    result = evaluate_demo_owner_approval_phrase_gate(build_sample_missing_owner_approval_phrase_input())

    assert result.classification == DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_MISSING
    assert result.approval_phrase_review_allowed is False


def test_wrong_phrase_blocks() -> None:
    result = evaluate_demo_owner_approval_phrase_gate(
        DemoOwnerApprovalPhraseGateInput(approval_phrase="Anthony approves local review.")
    )

    assert result.classification == DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_NOT_EXACT


def test_execution_scope_phrase_blocks() -> None:
    result = evaluate_demo_owner_approval_phrase_gate(build_sample_wrong_scope_owner_approval_phrase_input())

    assert result.classification == DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_EXECUTION_SCOPE


def test_real_money_phrase_blocks() -> None:
    result = evaluate_demo_owner_approval_phrase_gate(
        DemoOwnerApprovalPhraseGateInput(approval_phrase="I approve this for real money.")
    )

    assert result.classification == DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_REAL_MONEY_SCOPE


def test_broker_action_phrase_blocks() -> None:
    result = evaluate_demo_owner_approval_phrase_gate(
        DemoOwnerApprovalPhraseGateInput(approval_phrase="Broker action authorized by this phrase.")
    )

    assert result.classification == DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_BROKER_ACTION_SCOPE


def test_required_phrase_present() -> None:
    result = evaluate_demo_owner_approval_phrase_gate()

    assert result.required_phrase == REQUIRED_OWNER_APPROVAL_PHRASE
    assert "manual owner review only" in result.required_phrase


def test_owner_warning_exact() -> None:
    result = evaluate_demo_owner_approval_phrase_gate()

    assert result.owner_warning == OWNER_WARNING
    assert result.owner_warning == "Do not execute unless Anthony explicitly approves."


def test_phrase_output_json_serializable() -> None:
    payload = demo_owner_approval_phrase_gate_to_jsonable_dict(evaluate_demo_owner_approval_phrase_gate())

    assert json.loads(json.dumps(payload))["classification"] == (
        DEMO_OWNER_APPROVAL_PHRASE_VALID_FOR_MANUAL_REVIEW
    )


def test_phrase_operator_text_is_plain_english() -> None:
    text = demo_owner_approval_phrase_gate_to_operator_text(evaluate_demo_owner_approval_phrase_gate())

    assert "valid for manual review only" in text
    assert "No trade was placed" in text


def test_phrase_markdown_has_title() -> None:
    markdown = demo_owner_approval_phrase_gate_to_markdown(evaluate_demo_owner_approval_phrase_gate())

    assert markdown.startswith("# Demo Owner Approval Phrase Gate V1")


def test_phrase_permissions_false() -> None:
    result = evaluate_demo_owner_approval_phrase_gate()

    for flag in PERMISSION_FLAGS:
        assert getattr(result, flag) is False


def test_approval_phrase_never_sets_broker_action_allowed_true() -> None:
    result = evaluate_demo_owner_approval_phrase_gate(build_sample_valid_owner_approval_phrase_input())

    assert result.broker_action_allowed is False


def test_approval_phrase_never_sets_demo_execution_allowed_true() -> None:
    result = evaluate_demo_owner_approval_phrase_gate(build_sample_valid_owner_approval_phrase_input())

    assert result.demo_execution_allowed is False
