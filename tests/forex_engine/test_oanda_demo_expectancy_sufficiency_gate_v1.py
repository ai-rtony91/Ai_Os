from __future__ import annotations

import json

from automation.forex_engine import oanda_demo_expectancy_sufficiency_gate_v1 as m
from automation.forex_engine import oanda_demo_repeated_expectancy_accumulator_v1 as a


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
    result = m.evaluate_oanda_demo_expectancy_sufficiency(
        sample or m.build_sample_ready_sufficiency_input(), config
    )
    return m.oanda_demo_expectancy_sufficiency_to_jsonable_dict(result)


def _accum_json(sample):
    return a.oanda_demo_repeated_expectancy_accumulator_to_jsonable_dict(
        a.build_oanda_demo_repeated_expectancy_accumulator(sample)
    )


def test_sufficiency_ready_for_strong():
    data = _json(m.build_sample_ready_sufficiency_input())
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SUFFICIENCY_READY_FOR_OWNER_PROOF_REVIEW"
    assert data["owner_proof_review_allowed"] is True


def test_sufficiency_more_evidence_for_insufficient_positive_sample():
    data = _json(m.build_sample_more_evidence_sufficiency_input())
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REQUIRE_MORE_EVIDENCE"
    assert data["requires_more_evidence"] is True


def test_sufficiency_rejected_for_negative_expectancy():
    data = _json(m.build_sample_rejected_sufficiency_input())
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REJECTED_NEGATIVE_EXPECTANCY"
    assert data["rejected"] is True


def test_sufficiency_rejected_for_low_profit_factor():
    strong = _accum_json(a.build_sample_strong_accumulator_input())
    strong["profit_factor"] = "1.0000"
    strong["expectancy_per_trade"] = "0.1000"
    strong["average_r"] = "0.2000"
    strong["win_rate"] = "0.5000"
    data = _json({"accumulator_result": strong})
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REJECTED_LOW_PROFIT_FACTOR"


def test_sufficiency_blocked_unsafe():
    data = _json(m.build_sample_blocked_sufficiency_input())
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SUFFICIENCY_BLOCKED_UNSAFE"


def test_sufficiency_metrics_summary_present():
    summary = _json()["metrics_summary"]
    assert summary["result_count"] == 10
    assert summary["profit_factor"] == "8.5556"


def test_sufficiency_proof_preview_allowed_only_when_ready():
    assert _json()["proof_preview_allowed"] is True
    assert _json(m.build_sample_more_evidence_sufficiency_input())["proof_preview_allowed"] is False


def test_sufficiency_never_allows_live_execution():
    assert _json()["live_execution_allowed"] is False


def test_sufficiency_json_serializable():
    json.dumps(_json(), sort_keys=True)


def test_sufficiency_markdown_title():
    result = m.evaluate_oanda_demo_expectancy_sufficiency(m.build_sample_ready_sufficiency_input())
    assert m.oanda_demo_expectancy_sufficiency_to_markdown(result).startswith(
        "# AIOS Forex OANDA Demo Expectancy Sufficiency Gate V1"
    )


def test_sufficiency_operator_text_plain():
    result = m.evaluate_oanda_demo_expectancy_sufficiency(m.build_sample_ready_sufficiency_input())
    text = m.oanda_demo_expectancy_sufficiency_to_operator_text(result)
    assert "Repeated expectancy sufficiency status:" in text
    assert "No broker call made by this packet." in text


def test_sufficiency_permissions_false():
    data = _json()
    assert all(data[flag] is False for flag in PROTECTED_FLAGS)
    assert all(data["permissions"][flag] is False for flag in PROTECTED_FLAGS)


def test_ready_evidence_gaps_empty():
    assert _json()["evidence_gaps"] == []


def test_more_evidence_gap_names_sample_size():
    assert "sample_size_below_ready_threshold" in _json(
        m.build_sample_more_evidence_sufficiency_input()
    )["evidence_gaps"]


def test_rejected_negative_has_ready_blocker():
    assert "negative_expectancy" in _json(m.build_sample_rejected_sufficiency_input())[
        "ready_blockers"
    ]


def test_low_average_r_requires_more_evidence():
    strong = _accum_json(a.build_sample_strong_accumulator_input())
    strong["average_r"] = "0.0100"
    data = _json({"accumulator_result": strong})
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REQUIRE_MORE_EVIDENCE"


def test_low_win_rate_requires_more_evidence():
    strong = _accum_json(a.build_sample_strong_accumulator_input())
    strong["win_rate"] = "0.3000"
    data = _json({"accumulator_result": strong})
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SUFFICIENCY_REQUIRE_MORE_EVIDENCE"


def test_zero_result_count_blocked_insufficient_sample():
    blocked = _accum_json(a.build_sample_strong_accumulator_input())
    blocked["result_count"] = 0
    blocked["expectancy_per_trade"] = "0.0000"
    data = _json({"accumulator_result": blocked})
    assert data["classification"] == "OANDA_DEMO_EXPECTANCY_SUFFICIENCY_BLOCKED_INSUFFICIENT_SAMPLE"


def test_exact_owner_warning_present():
    assert _json()["owner_warning"] == "Do not execute unless Anthony explicitly approves."


def test_exact_expectancy_warning_present():
    assert _json()["expectancy_warning"] == (
        "Repeated expectancy review only. Codex is not authorized to execute, "
        "call a broker, access credentials, or place orders."
    )


def test_preview_only_true():
    assert _json()["preview_only"] is True


def test_no_existing_ledger_file_is_mutated():
    assert _json()["mutates_existing_ledger_file"] is False
