from __future__ import annotations

import json
from dataclasses import replace
from decimal import Decimal

from automation.forex_engine import oanda_demo_expectancy_sample_intake_v1 as m
from automation.forex_engine.oanda_demo_read_only_pl_result_intake_v1 import (
    build_sample_profit_pl_evidence,
    intake_oanda_demo_read_only_pl_result,
    oanda_demo_read_only_pl_result_intake_to_jsonable_dict,
)


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


def _json(sample=None, config=None):
    result = m.intake_oanda_demo_expectancy_sample(
        sample or m.build_sample_strong_expectancy_inputs(), config
    )
    return m.oanda_demo_expectancy_sample_intake_to_jsonable_dict(result)


def _mutated_first_sample(field: str, value: object):
    sample = list(m.build_sample_strong_expectancy_inputs().result_intake_objects)
    item = dict(sample[0])
    sanitized = dict(item["sanitized_evidence"])
    sanitized[field] = value
    item["sanitized_evidence"] = sanitized
    sample[0] = item
    return m.OandaDemoExpectancySampleInput(result_intake_objects=tuple(sample))


def test_strong_sample_intake_accepted():
    data = _json(m.build_sample_strong_expectancy_inputs())
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED"
    assert data["sample_review_allowed"] is True


def test_weak_sample_intake_accepted():
    data = _json(m.build_sample_weak_mixed_expectancy_inputs())
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED"
    assert data["result_count"] == 5


def test_insufficient_sample_intake_accepted():
    data = _json(m.build_sample_insufficient_expectancy_inputs())
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED"
    assert data["result_count"] == 2


def test_losing_sample_intake_accepted():
    data = _json(m.build_sample_losing_expectancy_inputs())
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED"
    assert "LOSS" in data["accepted_result_buckets"]


def test_unsafe_sample_intake_blocked():
    data = _json(m.build_sample_unsafe_expectancy_inputs())
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_UNSAFE_RESULT"
    assert data["sample_review_allowed"] is False


def test_empty_sample_blocked():
    data = _json(m.OandaDemoExpectancySampleInput(result_intake_objects=tuple()))
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_EMPTY"


def test_unsafe_result_blocked():
    sample = list(m.build_sample_strong_expectancy_inputs().result_intake_objects)
    item = dict(sample[0])
    item["broker_action_allowed"] = True
    sample[0] = item
    data = _json(m.OandaDemoExpectancySampleInput(tuple(sample)))
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_UNSAFE_RESULT"


def test_incomplete_result_blocked():
    sample = list(m.build_sample_strong_expectancy_inputs().result_intake_objects)
    item = dict(sample[0])
    item["classification"] = "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_INCOMPLETE"
    sample[0] = item
    data = _json(m.OandaDemoExpectancySampleInput(tuple(sample)))
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_INCOMPLETE_RESULT"


def test_mixed_strategy_blocked():
    data = _json(_mutated_first_sample("strategy_id", "different_strategy"))
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_MIXED_STRATEGY"


def test_mixed_candidate_blocked():
    data = _json(_mutated_first_sample("candidate_id", "different_candidate"))
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_MIXED_CANDIDATE"


def test_mixed_instrument_blocked():
    data = _json(_mutated_first_sample("instrument", "GBP_USD"))
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_MIXED_INSTRUMENT"


def test_sample_preserves_strategy_id():
    assert _json()["strategy_id"] == "strategy_supertrend_review_ready_v1"


def test_sample_preserves_candidate_id():
    assert _json()["candidate_id"] == "candidate_oanda_demo_pl_001"


def test_sample_preserves_instrument():
    assert _json()["instrument"] == "EUR_USD"


def test_intake_json_serializable():
    json.dumps(_json(), sort_keys=True)


def test_intake_markdown_title():
    result = m.intake_oanda_demo_expectancy_sample(m.build_sample_strong_expectancy_inputs())
    assert m.oanda_demo_expectancy_sample_intake_to_markdown(result).startswith(
        "# AIOS Forex OANDA Demo Expectancy Sample Intake V1"
    )


def test_intake_operator_text_plain():
    result = m.intake_oanda_demo_expectancy_sample(m.build_sample_strong_expectancy_inputs())
    text = m.oanda_demo_expectancy_sample_intake_to_operator_text(result)
    assert "Repeated expectancy sample intake status:" in text
    assert "No broker call made by this packet." in text


def test_intake_permissions_false():
    data = _json()
    assert all(data[flag] is False for flag in PROTECTED_FLAGS)
    assert all(data["permissions"][flag] is False for flag in PROTECTED_FLAGS)


def test_one_result_can_be_intaken_but_not_repeated_proof():
    item = m.build_sample_strong_expectancy_inputs().result_intake_objects[0]
    data = _json(m.OandaDemoExpectancySampleInput((item,)))
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED"
    assert data["result_count"] == 1


def test_mixed_strategy_can_be_allowed_by_config_when_explicitly_set():
    data = _json(
        _mutated_first_sample("strategy_id", "different_strategy"),
        m.OandaDemoExpectancySampleIntakeConfig(allow_mixed_strategy=True),
    )
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED"


def test_mixed_candidate_can_be_allowed_by_config_when_explicitly_set():
    data = _json(
        _mutated_first_sample("candidate_id", "different_candidate"),
        m.OandaDemoExpectancySampleIntakeConfig(allow_mixed_candidate=True),
    )
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED"


def test_mixed_instrument_can_be_allowed_by_config_when_explicitly_set():
    data = _json(
        _mutated_first_sample("instrument", "GBP_USD"),
        m.OandaDemoExpectancySampleIntakeConfig(allow_mixed_instrument=True),
    )
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED"


def test_sample_chronology_sorted_by_close_time():
    sample = list(m.build_sample_strong_expectancy_inputs().result_intake_objects)
    sample = [sample[3], sample[1], sample[0], *sample[4:]]
    data = _json(m.OandaDemoExpectancySampleInput(tuple(sample)))
    close_times = [item["close_time"] for item in data["sample_items"]]
    assert close_times == sorted(close_times)


def test_missing_close_time_blocks_result():
    data = _json(_mutated_first_sample("close_time", ""))
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_INCOMPLETE_RESULT"
    assert any("close_time_required" in blocker for blocker in data["blockers"])


def test_planned_risk_cannot_be_zero():
    evidence = replace(build_sample_profit_pl_evidence(), planned_risk=Decimal("0"))
    item = oanda_demo_read_only_pl_result_intake_to_jsonable_dict(
        intake_oanda_demo_read_only_pl_result(evidence)
    )
    data = _json(m.OandaDemoExpectancySampleInput((item,)))
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_INCOMPLETE_RESULT"


def test_accepted_sample_can_include_breakeven_result():
    data = _json(m.build_sample_weak_mixed_expectancy_inputs())
    assert "BREAKEVEN" in data["accepted_result_buckets"]


def test_exact_owner_warning_present():
    assert _json()["owner_warning"] == "Do not execute unless Anthony explicitly approves."


def test_exact_expectancy_warning_present():
    assert _json()["expectancy_warning"] == (
        "Repeated expectancy review only. Codex is not authorized to execute, "
        "call a broker, access credentials, or place orders."
    )


def test_non_demo_result_blocked():
    data = _json(_mutated_first_sample("environment", "PRACTICE"))
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_UNSAFE_RESULT"


def test_not_sanitized_result_blocked():
    data = _json(_mutated_first_sample("sanitized", False))
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_UNSAFE_RESULT"


def test_unreconciled_result_blocked():
    data = _json(_mutated_first_sample("broker_reconciled", False))
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_INCOMPLETE_RESULT"


def test_no_existing_ledger_file_is_mutated():
    assert _json()["mutates_existing_ledger_file"] is False


def test_preview_only_true():
    assert _json()["preview_only"] is True


def test_decimal_output_stable_in_items():
    first = _json()["sample_items"][0]
    assert first["realized_pl"] == "1.20"
    assert first["realized_r_multiple"] == "0.6000"


def test_output_deterministic_for_strong():
    assert _json(m.build_sample_strong_expectancy_inputs()) == _json(
        m.build_sample_strong_expectancy_inputs()
    )
