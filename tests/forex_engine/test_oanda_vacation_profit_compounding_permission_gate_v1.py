from __future__ import annotations

import json

import pytest

from automation.forex_engine import oanda_vacation_profit_compounding_permission_gate_v1 as compounding
from automation.forex_engine.oanda_vacation_profit_readiness_contract_v1 import (
    PROTECTED_FLAG_NAMES,
)


def _result(builder=compounding.build_sample_ready_for_review_input):
    return compounding.evaluate_oanda_vacation_profit_compounding_permission_gate(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (
            compounding.build_sample_ready_for_review_input,
            compounding.OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_READY_FOR_FUTURE_OWNER_REVIEW,
        ),
        (
            compounding.build_sample_compounding_blocked_input,
            compounding.OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_BLOCKED_BY_DEFAULT,
        ),
        (
            compounding.build_sample_unsafe_input,
            compounding.OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_BLOCKED_UNSAFE,
        ),
    ),
)
def test_compounding_permission_gate_classifications(builder, classification: str):
    assert _result(builder).classification == classification


def test_compounding_permission_gate_version_constant():
    assert compounding.VERSION == "oanda_vacation_profit_compounding_permission_gate_v1"


@pytest.mark.parametrize(
    "field_name",
    (
        "no_compounding_by_default",
        "no_reinvestment_by_default",
        "no_balance_scaling_by_default",
        "no_increased_risk_after_wins",
        "no_bank_movement",
        "no_withdrawal_automation",
        "no_deposit_automation",
    ),
)
def test_compounding_permission_gate_required_safety_fields_true(field_name: str):
    assert getattr(_result(), field_name) is True


@pytest.mark.parametrize(
    "field_name",
    (
        "no_compounding_by_default",
        "no_reinvestment_by_default",
        "no_balance_scaling_by_default",
        "no_increased_risk_after_wins",
        "no_bank_movement",
        "no_withdrawal_automation",
        "no_deposit_automation",
    ),
)
def test_compounding_permission_gate_blocks_disabled_safety_field(field_name: str):
    data = compounding.to_jsonable_dict(compounding.build_sample_ready_for_review_input())
    data[field_name] = False
    result = compounding.evaluate_oanda_vacation_profit_compounding_permission_gate(data)
    assert result.classification == compounding.OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_BLOCKED_UNSAFE
    assert field_name in result.blocked_items


@pytest.mark.parametrize("flag_name", PROTECTED_FLAG_NAMES)
def test_compounding_permission_gate_all_protected_flags_false(flag_name: str):
    result = _result()
    assert getattr(result, flag_name) is False
    assert result.protected_flags[flag_name] is False


def test_compounding_permission_gate_never_approves_compounding():
    assert _result().compounding_permission_approved is False
    assert _result().compounding_allowed is False


def test_compounding_permission_gate_json_serializable():
    json.dumps(compounding.to_jsonable_dict(_result()))


def test_compounding_permission_gate_markdown_output():
    assert compounding.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Vacation Profit Compounding Permission Gate V1"
    )


def test_compounding_permission_gate_operator_text_output():
    assert "Vacation profit compounding permission status" in compounding.to_operator_text(_result())


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
def test_compounding_permission_gate_markdown_safety_phrases(phrase: str):
    assert phrase in compounding.to_markdown(_result())

