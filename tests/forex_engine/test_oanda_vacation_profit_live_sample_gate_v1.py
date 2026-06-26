from __future__ import annotations

import json
from decimal import Decimal

import pytest

from automation.forex_engine import oanda_vacation_profit_live_sample_gate_v1 as live_gate
from automation.forex_engine.oanda_vacation_profit_readiness_contract_v1 import (
    PROTECTED_FLAG_NAMES,
)


def _result(builder=live_gate.build_sample_ready_for_review_input):
    return live_gate.evaluate_oanda_vacation_profit_live_sample_gate(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (
            live_gate.build_sample_ready_for_review_input,
            live_gate.OANDA_VACATION_PROFIT_LIVE_SAMPLE_READY_FOR_OWNER_REVIEW,
        ),
        (
            live_gate.build_sample_no_live_sample_input,
            live_gate.OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_NO_LIVE_SAMPLE,
        ),
        (
            live_gate.build_sample_missing_autonomy_controls_input,
            live_gate.OANDA_VACATION_PROFIT_LIVE_SAMPLE_READY_FOR_OWNER_REVIEW,
        ),
        (
            live_gate.build_sample_compounding_blocked_input,
            live_gate.OANDA_VACATION_PROFIT_LIVE_SAMPLE_READY_FOR_OWNER_REVIEW,
        ),
        (
            live_gate.build_sample_unsafe_input,
            live_gate.OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_UNSAFE,
        ),
    ),
)
def test_live_sample_gate_classifications(builder, classification: str):
    assert _result(builder).classification == classification


def test_live_sample_gate_version_constant():
    assert live_gate.VERSION == "oanda_vacation_profit_live_sample_gate_v1"


@pytest.mark.parametrize(
    "field_name",
    (
        "repeated_demo_expectancy_ready",
        "live_evidence_gap_bridge_ready",
        "live_microtrade_result_sample_exists",
        "live_sample_trade_count",
        "live_profit_factor",
        "live_expectancy_per_trade",
        "max_total_drawdown_percent_observed",
        "reconciliation_complete",
        "post_trade_capture_complete",
        "missing_proof_items",
        "blocked_items",
    ),
)
def test_live_sample_gate_required_fields(field_name: str):
    assert hasattr(_result(), field_name)


def test_live_sample_gate_ready_threshold_values():
    result = _result()
    assert result.live_sample_trade_count >= result.min_live_sample_trades
    assert result.live_profit_factor >= result.min_live_profit_factor
    assert result.live_expectancy_per_trade >= result.min_live_expectancy_per_trade


def test_live_sample_gate_no_live_sample_blocked():
    result = _result(live_gate.build_sample_no_live_sample_input)
    assert result.live_microtrade_result_sample_exists is False
    assert result.classification == live_gate.OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_NO_LIVE_SAMPLE


@pytest.mark.parametrize(
    ("field_name", "value", "missing_item"),
    (
        ("repeated_demo_expectancy_ready", False, "repeated_demo_expectancy_ready"),
        ("live_evidence_gap_bridge_ready", False, "live_evidence_gap_bridge_ready"),
        ("live_sample_trade_count", 19, "live_sample_size_threshold"),
        ("live_profit_factor", Decimal("1.10"), "live_profit_factor_threshold"),
        ("max_total_drawdown_percent_observed", Decimal("7.00"), "max_drawdown_under_threshold"),
        ("reconciliation_complete", False, "reconciliation_complete"),
        ("post_trade_capture_complete", False, "post_trade_capture_complete"),
    ),
)
def test_live_sample_gate_requires_each_proof(field_name: str, value, missing_item: str):
    sample = live_gate.build_sample_ready_for_review_input()
    data = live_gate.to_jsonable_dict(sample)
    data[field_name] = value
    result = live_gate.evaluate_oanda_vacation_profit_live_sample_gate(data)
    assert missing_item in result.missing_proof_items


def test_live_sample_gate_blocks_negative_expectancy():
    sample = live_gate.to_jsonable_dict(live_gate.build_sample_ready_for_review_input())
    sample["live_expectancy_per_trade"] = "-0.01"
    result = live_gate.evaluate_oanda_vacation_profit_live_sample_gate(sample)
    assert result.classification == live_gate.OANDA_VACATION_PROFIT_LIVE_SAMPLE_BLOCKED_NEGATIVE_EXPECTANCY


def test_live_sample_gate_blocks_unresolved_loss_spike():
    result = _result(live_gate.build_sample_unsafe_input)
    assert "unresolved_loss_spike_present" in result.blocked_items


@pytest.mark.parametrize("flag_name", PROTECTED_FLAG_NAMES)
def test_live_sample_gate_all_protected_flags_false(flag_name: str):
    result = _result()
    assert getattr(result, flag_name) is False
    assert result.protected_flags[flag_name] is False


def test_live_sample_gate_json_serializable():
    json.dumps(live_gate.to_jsonable_dict(_result()))


def test_live_sample_gate_markdown_output():
    assert live_gate.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Vacation Profit Live Sample Gate V1"
    )


def test_live_sample_gate_operator_text_output():
    assert "Vacation profit live sample gate status" in live_gate.to_operator_text(_result())


@pytest.mark.parametrize(
    "phrase",
    (
        "No trade placed by this packet.",
        "No broker call was made by this packet.",
        "No live approval was granted.",
        "No real money approval was granted.",
        "No compounding approval was granted.",
        "No bank movement approval was granted.",
        "No autonomous execution was granted.",
        "Unattended vacation mode remains blocked.",
        "Profit is not guaranteed.",
        "All protected flags remain false.",
    ),
)
def test_live_sample_gate_markdown_safety_phrases(phrase: str):
    assert phrase in live_gate.to_markdown(_result())


@pytest.mark.parametrize(
    "forbidden_text",
    (
        '"live_trading_allowed": true',
        '"broker_action_allowed": true',
        '"real_money_allowed": true',
        '"compounding_allowed": true',
        '"bank_movement_allowed": true',
        '"autonomous_execution_allowed": true',
        '"vacation_profit_trial_allowed": true',
    ),
)
def test_live_sample_gate_no_protected_true_json(forbidden_text: str):
    assert forbidden_text not in json.dumps(live_gate.to_jsonable_dict(_result())).lower()

