from __future__ import annotations

import json

import pytest

from automation.forex_engine import oanda_vacation_profit_autonomy_control_gate_v1 as autonomy
from automation.forex_engine.oanda_vacation_profit_readiness_contract_v1 import (
    PROTECTED_FLAG_NAMES,
)


def _result(builder=autonomy.build_sample_ready_for_review_input):
    return autonomy.evaluate_oanda_vacation_profit_autonomy_control_gate(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (
            autonomy.build_sample_ready_for_review_input,
            autonomy.OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_READY_FOR_OWNER_REVIEW,
        ),
        (
            autonomy.build_sample_missing_autonomy_controls_input,
            autonomy.OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_REQUIRE_MORE_PROOF,
        ),
        (
            autonomy.build_sample_unsafe_input,
            autonomy.OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_BLOCKED_UNSAFE,
        ),
    ),
)
def test_autonomy_control_gate_classifications(builder, classification: str):
    assert _result(builder).classification == classification


def test_autonomy_control_gate_version_constant():
    assert autonomy.VERSION == "oanda_vacation_profit_autonomy_control_gate_v1"


@pytest.mark.parametrize("control_name", autonomy.REQUIRED_CONTROL_FIELDS)
def test_autonomy_control_gate_requires_control(control_name: str):
    sample = autonomy.build_sample_ready_for_review_input()
    data = autonomy.to_jsonable_dict(sample)
    data["control_proofs"][control_name] = False
    result = autonomy.evaluate_oanda_vacation_profit_autonomy_control_gate(data)
    assert result.classification == autonomy.OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_REQUIRE_MORE_PROOF
    assert control_name in result.missing_control_proofs


@pytest.mark.parametrize(
    "count_field",
    (
        "kill_switch_proof_count",
        "timeout_abort_proof_count",
        "final_disarm_proof_count",
        "duplicate_order_guard_proof_count",
        "reconciliation_proof_count",
    ),
)
def test_autonomy_control_gate_requires_minimum_counts(count_field: str):
    data = autonomy.to_jsonable_dict(autonomy.build_sample_ready_for_review_input())
    data[count_field] = 0
    result = autonomy.evaluate_oanda_vacation_profit_autonomy_control_gate(data)
    assert result.classification == autonomy.OANDA_VACATION_PROFIT_AUTONOMY_CONTROLS_REQUIRE_MORE_PROOF


@pytest.mark.parametrize("flag_name", PROTECTED_FLAG_NAMES)
def test_autonomy_control_gate_all_protected_flags_false(flag_name: str):
    result = _result()
    assert getattr(result, flag_name) is False
    assert result.protected_flags[flag_name] is False


def test_autonomy_control_gate_unattended_operation_not_approved():
    assert _result().unattended_operation_approved is False


def test_autonomy_control_gate_owner_review_allowed_only_when_ready():
    assert _result().owner_review_allowed is True
    assert _result(autonomy.build_sample_missing_autonomy_controls_input).owner_review_allowed is False


def test_autonomy_control_gate_json_serializable():
    json.dumps(autonomy.to_jsonable_dict(_result()))


def test_autonomy_control_gate_markdown_output():
    assert autonomy.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Vacation Profit Autonomy Control Gate V1"
    )


def test_autonomy_control_gate_operator_text_output():
    assert "Vacation profit autonomy controls status" in autonomy.to_operator_text(_result())


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
def test_autonomy_control_gate_markdown_safety_phrases(phrase: str):
    assert phrase in autonomy.to_markdown(_result())

