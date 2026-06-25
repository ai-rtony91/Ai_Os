from __future__ import annotations

import json
from dataclasses import replace

from automation.forex_engine.demo_manual_execution_exception_checklist_v1 import (
    CHECKLIST_ITEM_NAMES,
    DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_EVIDENCE_PLAN_MISSING,
    DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_INCOMPLETE,
    DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_PROTECTED_ACTION_MISUNDERSTOOD,
    DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_RISK_NOT_ACKNOWLEDGED,
    DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_READY,
    build_sample_blocked_manual_execution_exception_checklist_input,
    build_sample_ready_manual_execution_exception_checklist_input,
    demo_manual_execution_exception_checklist_to_jsonable_dict,
    demo_manual_execution_exception_checklist_to_markdown,
    demo_manual_execution_exception_checklist_to_operator_text,
    evaluate_demo_manual_execution_exception_checklist,
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
    result = evaluate_demo_manual_execution_exception_checklist(
        build_sample_ready_manual_execution_exception_checklist_input()
    )

    assert result.classification == DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_READY
    assert result.checklist_review_allowed is True


def test_incomplete_checklist_blocks() -> None:
    sample = build_sample_ready_manual_execution_exception_checklist_input()
    result = evaluate_demo_manual_execution_exception_checklist(
        replace(sample, readiness_package_reviewed=False)
    )

    assert result.classification == DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_INCOMPLETE


def test_missing_risk_acknowledgement_blocks() -> None:
    sample = build_sample_ready_manual_execution_exception_checklist_input()
    result = evaluate_demo_manual_execution_exception_checklist(
        replace(sample, max_loss_reviewed=False)
    )

    assert result.classification == DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_RISK_NOT_ACKNOWLEDGED


def test_protected_action_misunderstanding_blocks() -> None:
    sample = build_sample_ready_manual_execution_exception_checklist_input()
    result = evaluate_demo_manual_execution_exception_checklist(
        replace(sample, codex_no_execution_understood=False)
    )

    assert result.classification == DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_PROTECTED_ACTION_MISUNDERSTOOD


def test_missing_post_trade_evidence_acknowledgement_blocks() -> None:
    sample = build_sample_ready_manual_execution_exception_checklist_input()
    result = evaluate_demo_manual_execution_exception_checklist(
        replace(sample, post_trade_evidence_required_understood=False)
    )

    assert result.classification == DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_EVIDENCE_PLAN_MISSING


def test_missing_feedback_routing_acknowledgement_blocks() -> None:
    sample = build_sample_ready_manual_execution_exception_checklist_input()
    result = evaluate_demo_manual_execution_exception_checklist(
        replace(sample, feedback_routing_required_understood=False)
    )

    assert result.classification == DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_EVIDENCE_PLAN_MISSING


def test_blocked_checklist_sample_blocks() -> None:
    result = evaluate_demo_manual_execution_exception_checklist(
        build_sample_blocked_manual_execution_exception_checklist_input()
    )

    assert result.classification == DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_RISK_NOT_ACKNOWLEDGED
    assert result.missing_items


def test_checklist_markdown_has_title() -> None:
    markdown = demo_manual_execution_exception_checklist_to_markdown(
        evaluate_demo_manual_execution_exception_checklist()
    )

    assert markdown.startswith("# Demo Manual Execution Exception Checklist V1")


def test_checklist_output_json_serializable() -> None:
    payload = demo_manual_execution_exception_checklist_to_jsonable_dict(
        evaluate_demo_manual_execution_exception_checklist()
    )

    assert json.loads(json.dumps(payload))["classification"] == (
        DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_READY
    )


def test_checklist_operator_text_is_plain_english() -> None:
    text = demo_manual_execution_exception_checklist_to_operator_text(
        evaluate_demo_manual_execution_exception_checklist()
    )

    assert "checklist is ready" in text
    assert "No trade was placed" in text


def test_checklist_contains_all_required_items() -> None:
    result = evaluate_demo_manual_execution_exception_checklist()

    for item in CHECKLIST_ITEM_NAMES:
        assert item in result.checklist_items


def test_checklist_permissions_false() -> None:
    result = evaluate_demo_manual_execution_exception_checklist()

    for flag in PERMISSION_FLAGS:
        assert getattr(result, flag) is False


def test_checklist_json_permissions_false() -> None:
    payload = demo_manual_execution_exception_checklist_to_jsonable_dict(
        evaluate_demo_manual_execution_exception_checklist()
    )

    for flag in PERMISSION_FLAGS:
        assert payload[flag] is False
