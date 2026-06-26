from __future__ import annotations

import json
from decimal import Decimal

import pytest

from automation.forex_engine import oanda_vacation_profit_readiness_contract_v1 as contract


def _result(builder=contract.build_sample_ready_for_review_input):
    return contract.evaluate_oanda_vacation_profit_readiness_contract(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (
            contract.build_sample_ready_for_review_input,
            contract.OANDA_VACATION_PROFIT_READINESS_CONTRACT_READY,
        ),
        (
            contract.build_sample_no_live_sample_input,
            contract.OANDA_VACATION_PROFIT_READINESS_CONTRACT_READY,
        ),
        (
            contract.build_sample_missing_autonomy_controls_input,
            contract.OANDA_VACATION_PROFIT_READINESS_CONTRACT_READY,
        ),
        (
            contract.build_sample_compounding_blocked_input,
            contract.OANDA_VACATION_PROFIT_READINESS_CONTRACT_READY,
        ),
        (
            contract.build_sample_unsafe_input,
            contract.OANDA_VACATION_PROFIT_READINESS_CONTRACT_BLOCKED_UNSAFE,
        ),
    ),
)
def test_contract_sample_classifications(builder, classification: str):
    assert _result(builder).classification == classification


def test_contract_version_constant():
    assert contract.VERSION == "oanda_vacation_profit_readiness_contract_v1"


@pytest.mark.parametrize(
    ("field_name", "expected"),
    (
        ("trial_capital", Decimal("200.00")),
        ("target_profit_mode", "small_lump_sum_non_guaranteed"),
        ("max_total_drawdown_percent", Decimal("5.00")),
        ("max_daily_loss_percent", Decimal("2.00")),
        ("max_trade_risk_percent", Decimal("0.50")),
        ("min_live_sample_trades", 20),
        ("min_live_profit_factor", Decimal("1.20")),
        ("min_live_expectancy_per_trade", Decimal("0.01")),
        ("min_kill_switch_proof_count", 3),
        ("min_disarm_proof_count", 3),
        ("min_reconciliation_proof_count", 3),
    ),
)
def test_contract_default_target_values(field_name: str, expected):
    assert getattr(_result(), field_name) == expected


@pytest.mark.parametrize(
    "field_name",
    (
        "small_funded_account_goal",
        "capital_preservation_first",
        "profit_is_not_guaranteed",
        "no_compounding_without_later_gate",
        "no_bank_movement",
        "unattended_mode_blocked_until_proof_exists",
        "owner_review_required",
        "owner_warning",
        "vacation_warning",
    ),
)
def test_contract_required_fields_present(field_name: str):
    assert hasattr(_result(), field_name)


@pytest.mark.parametrize("flag_name", contract.PROTECTED_FLAG_NAMES)
def test_contract_all_protected_flags_false(flag_name: str):
    result = _result()
    assert getattr(result, flag_name) is False
    assert result.protected_flags[flag_name] is False


def test_contract_json_serializable():
    json.dumps(contract.to_jsonable_dict(_result()))


def test_contract_markdown_output():
    assert contract.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Vacation Profit Readiness Contract V1"
    )


def test_contract_operator_text_output():
    assert "Vacation profit readiness contract status" in contract.to_operator_text(_result())


def test_contract_owner_warning_exact():
    assert _result().owner_warning == contract.EXACT_OWNER_WARNING


def test_contract_vacation_warning_exact():
    assert _result().vacation_warning == contract.EXACT_VACATION_WARNING


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
def test_contract_markdown_safety_phrases(phrase: str):
    assert phrase in contract.to_markdown(_result())


@pytest.mark.parametrize(
    "forbidden_true",
    (
        '"demo_execution_allowed": true',
        '"broker_action_allowed": true',
        '"real_money_allowed": true',
        '"compounding_allowed": true',
        '"bank_movement_allowed": true',
        '"live_trading_allowed": true',
        '"credential_access_allowed": true',
        '"account_id_persistence_allowed": true',
        '"autonomous_execution_allowed": true',
        '"scheduler_allowed": true',
        '"daemon_allowed": true',
        '"webhook_allowed": true',
        '"live_micro_trade_exception_allowed": true',
        '"owner_live_execution_approval_present": true',
        '"codex_live_execution_authorized": true',
        '"unattended_vacation_mode_allowed": true',
        '"vacation_profit_trial_allowed": true',
    ),
)
def test_contract_json_has_no_protected_true_flags(forbidden_true: str):
    payload = json.dumps(contract.to_jsonable_dict(_result())).lower()
    assert forbidden_true not in payload


@pytest.mark.parametrize(
    "bad_input",
    (
        {"trial_capital": "0"},
        {"max_total_drawdown_percent": "0"},
        {"max_daily_loss_percent": "0"},
        {"max_trade_risk_percent": "0"},
        {"min_live_sample_trades": 0},
        {"min_live_profit_factor": "1.00"},
        {"min_live_expectancy_per_trade": "0"},
    ),
)
def test_contract_blocks_unsafe_bounds(bad_input):
    result = contract.evaluate_oanda_vacation_profit_readiness_contract(bad_input)
    assert result.classification == contract.OANDA_VACATION_PROFIT_READINESS_CONTRACT_BLOCKED_UNSAFE

