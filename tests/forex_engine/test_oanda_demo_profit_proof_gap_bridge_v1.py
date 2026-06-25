from __future__ import annotations

import json

import pytest

from automation.forex_engine.oanda_demo_profit_proof_gap_bridge_v1 import (
    OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_ACTUAL_DEMO_RESULT,
    OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_EXPECTANCY_SAMPLE,
    PROTECTED_PERMISSION_DEFAULTS,
    REQUIRED_OPERATOR_SENTENCE,
    bridge_oanda_demo_profit_proof_gap,
    build_sample_blocked_no_result_input,
    build_sample_current_repo_profit_gap_input,
    oanda_demo_profit_proof_gap_to_jsonable_dict,
    oanda_demo_profit_proof_gap_to_markdown,
    oanda_demo_profit_proof_gap_to_operator_text,
)


def _current_result():
    return bridge_oanda_demo_profit_proof_gap(build_sample_current_repo_profit_gap_input())


def test_profit_gap_detects_post_trade_evidence_capture_present():
    assert _current_result().evidence_map["post_trade_evidence_capture_present"] is True


def test_profit_gap_detects_profit_proof_ledger_present():
    assert _current_result().evidence_map["profit_proof_ledger_present"] is True


def test_profit_gap_detects_strategy_proof_engine_present():
    assert _current_result().evidence_map["strategy_proof_engine_present"] is True


def test_profit_gap_detects_expectancy_router_present():
    assert _current_result().evidence_map["expectancy_strength_router_present"] is True


def test_profit_gap_detects_no_actual_demo_result_blocks_profit_claim():
    blocked = bridge_oanda_demo_profit_proof_gap(build_sample_blocked_no_result_input())
    assert blocked.classification == OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_ACTUAL_DEMO_RESULT


def test_profit_gap_detects_no_repeated_sample_blocks_live_profit_claim():
    assert _current_result().classification == OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_EXPECTANCY_SAMPLE
    assert _current_result().evidence_map["repeated_profitable_sample_present"] is False


def test_profit_gap_says_profit_cannot_be_claimed_without_actual_result():
    blocked = bridge_oanda_demo_profit_proof_gap(build_sample_blocked_no_result_input())
    assert blocked.profit_proof_answer == REQUIRED_OPERATOR_SENTENCE


def test_profit_gap_permissions_false():
    assert all(value is False for value in _current_result().permissions.values())


def test_profit_gap_json_serializable():
    json.dumps(oanda_demo_profit_proof_gap_to_jsonable_dict(_current_result()))


def test_profit_gap_markdown_title():
    assert oanda_demo_profit_proof_gap_to_markdown(_current_result()).startswith(
        "# AIOS Forex OANDA Demo Profit Proof Gap Bridge V1"
    )


def test_profit_gap_plain_text_answer_short_and_accurate():
    text = oanda_demo_profit_proof_gap_to_operator_text(_current_result())
    assert text.splitlines()[0] == REQUIRED_OPERATOR_SENTENCE
    assert len(text.splitlines()) <= 5


def test_profit_gap_records_reconciled_pl_missing():
    assert _current_result().evidence_map["reconciled_demo_pl_present"] is False


@pytest.mark.parametrize(
    "field_name",
    (
        "post_trade_evidence_capture_present",
        "owner_run_post_trade_capture_present",
        "filled_trade_pl_capture_present",
        "result_to_bucket_allocation_present",
        "profit_proof_ledger_present",
        "strategy_proof_engine_present",
        "expectancy_strength_router_present",
        "real_evidence_depth_engine_present",
        "actual_demo_trade_result_present",
    ),
)
def test_current_repo_profit_evidence_present_fields_are_true(field_name):
    assert _current_result().evidence_map[field_name] is True


@pytest.mark.parametrize(
    "field_name",
    ("reconciled_demo_pl_present", "repeated_profitable_sample_present"),
)
def test_current_repo_profit_evidence_missing_fields_are_false(field_name):
    assert _current_result().evidence_map[field_name] is False


@pytest.mark.parametrize("flag_name", tuple(PROTECTED_PERMISSION_DEFAULTS))
def test_profit_gap_all_protected_flags_false(flag_name):
    payload = oanda_demo_profit_proof_gap_to_jsonable_dict(_current_result())
    assert payload[flag_name] is False
