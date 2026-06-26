from __future__ import annotations

import json

from automation.forex_engine import oanda_demo_repeated_expectancy_accumulator_v1 as m


PROTECTED_FLAGS = (
    "demo_execution_allowed",
    "broker_action_allowed",
    "real_money_allowed",
    "compounding_allowed",
    "bank_movement_allowed",
    "live_trading_allowed",
    "credential_access_allowed",
    "account_id_persistence_allowed",
    "autonomous_execution_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
)


def _json(sample=None):
    result = m.build_oanda_demo_repeated_expectancy_accumulator(
        sample or m.build_sample_strong_accumulator_input()
    )
    return m.oanda_demo_repeated_expectancy_accumulator_to_jsonable_dict(result)


def test_accumulator_strong_sample_strong():
    assert _json()["classification"] == "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_STRONG"


def test_accumulator_weak_sample_weak_or_reviewable():
    assert _json(m.build_sample_weak_accumulator_input())["classification"] in {
        "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_WEAK",
        "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_REVIEWABLE",
    }


def test_accumulator_insufficient_sample_accumulated_but_low_sample_count():
    data = _json(m.build_sample_insufficient_accumulator_input())
    assert data["classification"] == "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_WEAK"
    assert data["result_count"] == 2


def test_accumulator_losing_sample_losing():
    assert _json(m.build_sample_losing_accumulator_input())["classification"] == (
        "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_LOSING"
    )


def test_accumulator_blocked_if_intake_blocked():
    assert _json(m.build_sample_unsafe_accumulator_input())["classification"] == (
        "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATOR_BLOCKED"
    )


def test_profit_count_correct():
    assert _json()["profit_count"] == 7


def test_loss_count_correct():
    assert _json()["loss_count"] == 2


def test_breakeven_count_correct():
    assert _json()["breakeven_count"] == 1


def test_win_rate_calculated():
    assert _json()["win_rate"] == "0.7000"


def test_total_realized_pl_calculated():
    assert _json()["total_realized_pl"] == "6.8000"


def test_gross_profit_calculated():
    assert _json()["gross_profit"] == "7.7000"


def test_gross_loss_calculated():
    assert _json()["gross_loss_abs"] == "0.9000"


def test_profit_factor_calculated():
    assert _json()["profit_factor"] == "8.5556"


def test_expectancy_per_trade_calculated():
    assert _json()["expectancy_per_trade"] == "0.6800"


def test_total_r_calculated():
    assert _json()["total_r"] == "3.4000"


def test_average_r_calculated():
    assert _json()["average_r"] == "0.3400"


def test_best_r_calculated():
    assert _json()["best_r"] == "0.7000"


def test_worst_r_calculated():
    assert _json()["worst_r"] == "-0.2500"


def test_average_win_calculated():
    assert _json()["average_win"] == "1.1000"


def test_average_loss_calculated():
    assert _json()["average_loss_abs"] == "0.4500"


def test_max_observed_loss_calculated():
    assert _json()["max_observed_loss"] == "0.5000"


def test_positive_expectancy_true_for_strong():
    assert _json()["positive_expectancy"] is True


def test_profitable_sample_true_for_strong():
    assert _json()["profitable_sample"] is True


def test_loss_dominated_true_for_losing():
    assert _json(m.build_sample_losing_accumulator_input())["loss_dominated_sample"] is True


def test_accumulator_json_serializable():
    json.dumps(_json(), sort_keys=True)


def test_accumulator_markdown_title():
    result = m.build_oanda_demo_repeated_expectancy_accumulator(m.build_sample_strong_accumulator_input())
    assert m.oanda_demo_repeated_expectancy_accumulator_to_markdown(result).startswith(
        "# AIOS Forex OANDA Demo Repeated Expectancy Accumulator V1"
    )


def test_accumulator_operator_text_plain():
    result = m.build_oanda_demo_repeated_expectancy_accumulator(m.build_sample_strong_accumulator_input())
    text = m.oanda_demo_repeated_expectancy_accumulator_to_operator_text(result)
    assert "Repeated expectancy accumulator status:" in text
    assert "No trade placed by this packet." in text


def test_accumulator_permissions_false():
    data = _json()
    assert all(data[flag] is False for flag in PROTECTED_FLAGS)
    assert all(data["permissions"][flag] is False for flag in PROTECTED_FLAGS)


def test_breakeven_handled_without_division_error():
    data = _json(m.build_sample_weak_accumulator_input())
    assert data["breakeven_count"] == 1
    assert data["profit_factor"] == "1.3333"


def test_sample_size_threshold_enforced():
    data = _json(m.build_sample_insufficient_accumulator_input())
    assert data["result_count"] < m.OandaDemoRepeatedExpectancyAccumulatorConfig().min_review_sample_size
    assert data["classification"] == "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_WEAK"


def test_profit_factor_threshold_enforced():
    data = _json(m.build_sample_weak_accumulator_input())
    assert data["profit_factor"] == "1.3333"
    assert data["classification"] == "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_WEAK"


def test_average_r_threshold_enforced():
    data = _json(m.build_sample_weak_accumulator_input())
    assert data["average_r"] == "0.0200"
    assert data["classification"] == "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_WEAK"


def test_negative_expectancy_accumulated_as_losing():
    data = _json(m.build_sample_losing_accumulator_input())
    assert data["expectancy_per_trade"] == "-0.4000"
    assert data["classification"] == "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_LOSING"


def test_output_deterministic_for_weak():
    assert _json(m.build_sample_weak_accumulator_input()) == _json(
        m.build_sample_weak_accumulator_input()
    )


def test_output_deterministic_for_unsafe():
    assert _json(m.build_sample_unsafe_accumulator_input()) == _json(
        m.build_sample_unsafe_accumulator_input()
    )


def test_preview_only_true():
    assert _json()["preview_only"] is True


def test_no_existing_ledger_file_is_mutated():
    assert _json()["mutates_existing_ledger_file"] is False
