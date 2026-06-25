from __future__ import annotations

import json

from automation.forex_engine.demo_manual_execution_exception_scope_gate_v1 import (
    DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_BROKER_ACTION_AUTHORITY,
    DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_CODEX_EXECUTION_AUTHORITY,
    DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_CREDENTIAL_SCOPE,
    DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_LIVE_SCOPE,
    DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_MISSING,
    DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_REAL_MONEY_SCOPE,
    DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_VALID_FOR_REVIEW,
    EXCEPTION_WARNING,
    OWNER_WARNING,
    REQUIRED_EXCEPTION_PHRASE,
    DemoManualExecutionExceptionScopeInput,
    build_sample_execution_authority_blocked_input,
    build_sample_missing_manual_execution_exception_scope_input,
    build_sample_real_money_scope_blocked_input,
    build_sample_valid_manual_execution_exception_scope_input,
    demo_manual_execution_exception_scope_to_jsonable_dict,
    demo_manual_execution_exception_scope_to_markdown,
    demo_manual_execution_exception_scope_to_operator_text,
    evaluate_demo_manual_execution_exception_scope,
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


def test_valid_manual_exception_scope_passes() -> None:
    result = evaluate_demo_manual_execution_exception_scope(
        build_sample_valid_manual_execution_exception_scope_input()
    )

    assert result.classification == DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_VALID_FOR_REVIEW
    assert result.scope_review_allowed is True


def test_missing_exception_phrase_blocks() -> None:
    result = evaluate_demo_manual_execution_exception_scope(
        build_sample_missing_manual_execution_exception_scope_input()
    )

    assert result.classification == DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_MISSING


def test_codex_execution_authority_blocks() -> None:
    result = evaluate_demo_manual_execution_exception_scope(
        build_sample_execution_authority_blocked_input()
    )

    assert result.classification == DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_CODEX_EXECUTION_AUTHORITY


def test_broker_action_authority_blocks() -> None:
    result = evaluate_demo_manual_execution_exception_scope(
        DemoManualExecutionExceptionScopeInput(exception_phrase="OANDA action authorized for this request.")
    )

    assert result.classification == DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_BROKER_ACTION_AUTHORITY


def test_real_money_scope_blocks() -> None:
    result = evaluate_demo_manual_execution_exception_scope(
        build_sample_real_money_scope_blocked_input()
    )

    assert result.classification == DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_REAL_MONEY_SCOPE


def test_credential_scope_blocks() -> None:
    result = evaluate_demo_manual_execution_exception_scope(
        DemoManualExecutionExceptionScopeInput(exception_phrase="Credentials may be used for this exception.")
    )

    assert result.classification == DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_CREDENTIAL_SCOPE


def test_live_scope_blocks() -> None:
    result = evaluate_demo_manual_execution_exception_scope(
        DemoManualExecutionExceptionScopeInput(exception_phrase="Approve this live trading exception.")
    )

    assert result.classification == DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_LIVE_SCOPE


def test_required_exception_phrase_present() -> None:
    result = evaluate_demo_manual_execution_exception_scope()

    assert result.required_phrase == REQUIRED_EXCEPTION_PHRASE
    assert "Codex is not authorized" in result.required_phrase


def test_owner_warning_exact() -> None:
    result = evaluate_demo_manual_execution_exception_scope()

    assert result.owner_warning == OWNER_WARNING
    assert result.owner_warning == "Do not execute unless Anthony explicitly approves."


def test_exception_warning_exact() -> None:
    result = evaluate_demo_manual_execution_exception_scope()

    assert result.exception_warning == EXCEPTION_WARNING
    assert result.exception_warning == (
        "Manual exception review only. Codex is not authorized to execute, call a broker, "
        "access credentials, or place orders."
    )


def test_scope_output_json_serializable() -> None:
    payload = demo_manual_execution_exception_scope_to_jsonable_dict(
        evaluate_demo_manual_execution_exception_scope()
    )

    assert json.loads(json.dumps(payload))["classification"] == (
        DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_VALID_FOR_REVIEW
    )


def test_scope_operator_text_is_plain_english() -> None:
    text = demo_manual_execution_exception_scope_to_operator_text(
        evaluate_demo_manual_execution_exception_scope()
    )

    assert "valid for owner review only" in text
    assert "No trade was placed" in text


def test_scope_markdown_has_title() -> None:
    markdown = demo_manual_execution_exception_scope_to_markdown(
        evaluate_demo_manual_execution_exception_scope()
    )

    assert markdown.startswith("# Demo Manual Execution Exception Scope Gate V1")


def test_scope_permissions_false() -> None:
    result = evaluate_demo_manual_execution_exception_scope()

    for flag in PERMISSION_FLAGS:
        assert getattr(result, flag) is False


def test_exception_phrase_never_sets_broker_action_allowed_true() -> None:
    result = evaluate_demo_manual_execution_exception_scope()

    assert result.broker_action_allowed is False


def test_exception_phrase_never_sets_demo_execution_allowed_true() -> None:
    result = evaluate_demo_manual_execution_exception_scope()

    assert result.demo_execution_allowed is False


def test_sample_ready_still_says_codex_cannot_execute() -> None:
    result = evaluate_demo_manual_execution_exception_scope()

    assert "not authorized to execute" in result.exception_warning


def test_sample_ready_still_says_no_broker_call() -> None:
    text = demo_manual_execution_exception_scope_to_markdown(
        evaluate_demo_manual_execution_exception_scope()
    )

    assert "No broker call was made" in text
