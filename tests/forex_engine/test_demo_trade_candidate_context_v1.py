from __future__ import annotations

import json
from dataclasses import replace

from automation.forex_engine.demo_trade_candidate_context_v1 import (
    DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_EVIDENCE,
    DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_DIRECTION,
    DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_INSTRUMENT,
    DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_STRATEGY,
    DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_NOT_REVIEW_READY,
    DEMO_TRADE_CANDIDATE_CONTEXT_READY,
    build_sample_blocked_candidate_context_input,
    build_sample_ready_candidate_context_input,
    demo_trade_candidate_context_to_jsonable_dict,
    demo_trade_candidate_context_to_operator_text,
    evaluate_demo_trade_candidate_context,
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


def test_ready_candidate_context_passes() -> None:
    result = evaluate_demo_trade_candidate_context(build_sample_ready_candidate_context_input())

    assert result.classification == DEMO_TRADE_CANDIDATE_CONTEXT_READY
    assert result.candidate_context_review_allowed is True
    assert result.selected_strategy == "Supertrend"


def test_missing_strategy_blocks() -> None:
    sample = build_sample_ready_candidate_context_input()
    result = evaluate_demo_trade_candidate_context(replace(sample, selected_strategy=""))

    assert result.classification == DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_STRATEGY
    assert result.candidate_context_review_allowed is False


def test_missing_instrument_blocks() -> None:
    sample = build_sample_ready_candidate_context_input()
    result = evaluate_demo_trade_candidate_context(replace(sample, instrument=""))

    assert result.classification == DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_INSTRUMENT


def test_missing_direction_blocks() -> None:
    sample = build_sample_ready_candidate_context_input()
    result = evaluate_demo_trade_candidate_context(replace(sample, direction=""))

    assert result.classification == DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_MISSING_DIRECTION


def test_not_review_ready_blocks() -> None:
    result = evaluate_demo_trade_candidate_context(build_sample_blocked_candidate_context_input())

    assert result.classification == DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_NOT_REVIEW_READY
    assert result.blockers


def test_evidence_blocked_blocks() -> None:
    sample = build_sample_ready_candidate_context_input()
    result = evaluate_demo_trade_candidate_context(replace(sample, evidence_status="EVIDENCE_BLOCKED"))

    assert result.classification == DEMO_TRADE_CANDIDATE_CONTEXT_BLOCKED_EVIDENCE


def test_candidate_output_json_serializable() -> None:
    result = evaluate_demo_trade_candidate_context()
    payload = demo_trade_candidate_context_to_jsonable_dict(result)

    assert json.loads(json.dumps(payload))["classification"] == DEMO_TRADE_CANDIDATE_CONTEXT_READY


def test_candidate_text_is_plain_english() -> None:
    text = demo_trade_candidate_context_to_operator_text(evaluate_demo_trade_candidate_context())

    assert "Candidate context is review-ready" in text
    assert "No trade was placed" in text


def test_candidate_output_keeps_all_permissions_false() -> None:
    result = evaluate_demo_trade_candidate_context()

    for flag in PERMISSION_FLAGS:
        assert getattr(result, flag) is False


def test_candidate_json_keeps_all_permissions_false() -> None:
    payload = demo_trade_candidate_context_to_jsonable_dict(evaluate_demo_trade_candidate_context())

    for flag in PERMISSION_FLAGS:
        assert payload[flag] is False
