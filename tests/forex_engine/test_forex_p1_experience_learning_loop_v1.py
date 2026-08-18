from __future__ import annotations

import json

from automation.forex_engine.forex_p1_experience_learning_loop_v1 import (
    SCHEMA, append_experience_event, build_experience_event, classify_experience,
    config_hash, export_csv, filter_value_scorecard, near_threshold_bucket,
    postmortem_learning_summary, read_experience_ledger, similarity_bucket,
    walk_forward_scorecard,
)


def event(number: int, source: str, decision: str, outcome: float | None, gate: str = "atr"):
    return build_experience_event(
        experience_id=str(number), event_type="DECISION_OUTCOME", strategy_name="supertrend_pullback_v1",
        strategy_config={"atr_period": 3}, git_commit="abc123", dataset_identity={"window": "fixture"},
        decision_utc=f"2026-01-01T00:0{number}:00Z", production_decision=decision,
        shadow_classification=source, outcome_r=outcome, features={"first_failed_gate": gate, "session_bucket": "LONDON"},
    )


def test_four_way_classification_and_unresolved():
    assert classify_experience(production_decision="ACCEPTED", outcome_r=1) == "TRUE_POSITIVE"
    assert classify_experience(production_decision="ACCEPTED", outcome_r=-1) == "FALSE_POSITIVE"
    assert classify_experience(production_decision="REJECTED", outcome_r=1) == "FALSE_NEGATIVE"
    assert classify_experience(production_decision="REJECTED", outcome_r=-1) == "TRUE_NEGATIVE"
    assert classify_experience(production_decision="REJECTED", outcome_r=None) == "UNRESOLVED"


def test_append_sanitization_hash_and_csv(tmp_path):
    record = event(1, "SHADOW_COUNTERFACTUAL", "REJECTED", 1)
    record["api_token"] = "secret"
    ledger = tmp_path / "ledger.jsonl"
    append_experience_event(ledger, record)
    loaded = read_experience_ledger(ledger)
    assert loaded[0]["schema"] == SCHEMA
    assert loaded[0]["strategy_config_hash"] == config_hash({"atr_period": 3})
    assert "api_token" not in loaded[0]
    assert all(json.loads(line)["schema"] == SCHEMA for line in ledger.read_text().splitlines())
    csv_path = tmp_path / "ledger.csv"
    export_csv(loaded, csv_path)
    assert "outcome_classification" in csv_path.read_text()


def test_scorecard_walkforward_separation_and_similarity():
    records = [event(1, "SHADOW_COUNTERFACTUAL", "REJECTED", 1), event(2, "SHADOW_COUNTERFACTUAL", "REJECTED", -1), event(3, "ACTUAL_PAPER", "ACCEPTED", 1)]
    scorecard = filter_value_scorecard(records)
    assert scorecard["atr"]["would_win"] == 1
    assert scorecard["atr"]["would_lose"] == 1
    assert walk_forward_scorecard(records)["selection_uses_test"] is False
    assert postmortem_learning_summary(records)["mixed_accounting"] is False
    assert near_threshold_bucket(4.9) == "0_5_PERCENT"
    assert near_threshold_bucket(21) == "OVER_20_PERCENT"
    assert similarity_bucket({"volatility_regime": "NORMAL", "session_bucket": "LONDON", "supertrend_age_bucket": 3, "spread_risk_bucket": "LOW"}) == "NORMAL|LONDON|3|LOW"
