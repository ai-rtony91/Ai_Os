from __future__ import annotations

import math

from automation.forex_engine import long_only_profitability_evidence_depth_gate_v1 as gate


def _valid_evidence():
    return {
        "candidate_id": "c1-eur-buy",
        "strategy_id": "long-only-eur-usd-v1",
        "instrument": "EUR_USD",
        "direction": "LONG",
        "evidence_source": "deterministic_paper_demo_review",
        "evidence_timestamp": "2026-06-23T00:00:00+00:00",
        "sample_size": 30,
        "closed_trades": 30,
        "winning_trades": 19,
        "losing_trades": 9,
        "breakeven_trades": 2,
        "expectancy": 0.18,
        "profit_factor": 1.35,
        "max_drawdown": 0.04,
        "max_drawdown_allowed": 0.08,
        "walk_forward_folds": 4,
        "out_of_sample_folds": 3,
        "out_of_sample_folds_passed": 3,
        "min_required_trades": 30,
        "min_required_walk_forward_folds": 3,
        "min_required_out_of_sample_folds": 3,
        "min_expectancy": 0.0,
        "min_profit_factor": 1.2,
        "negative_expectancy": False,
        "mitigation_worsened": False,
        "overfit_flag": False,
        "risk_gate_cleared": True,
        "evidence_gate_cleared": True,
        "long_only": True,
        "short_side_disabled": True,
        "sanitized_evidence_only": True,
    }


def _blocked(evidence):
    result = gate.evaluate_long_only_profitability_evidence_depth(evidence)
    assert result["status"] == gate.PROFITABILITY_EVIDENCE_DEPTH_BLOCKED
    assert result["ready"] is False
    return result


def test_missing_evidence_blocks():
    assert "missing_candidate_evidence" in _blocked(None)["blockers"]


def test_non_dict_evidence_blocks():
    assert "missing_candidate_evidence" in _blocked(["bad"])["blockers"]


def test_missing_candidate_id_blocks():
    evidence = _valid_evidence()
    evidence.pop("candidate_id")
    assert "missing_required_field:candidate_id" in _blocked(evidence)["blockers"]


def test_direction_short_blocks():
    evidence = _valid_evidence()
    evidence["direction"] = "SHORT"
    assert "direction_not_long" in _blocked(evidence)["blockers"]


def test_long_only_false_blocks():
    evidence = _valid_evidence()
    evidence["long_only"] = False
    assert "long_only_not_confirmed" in _blocked(evidence)["blockers"]


def test_short_side_disabled_false_blocks():
    evidence = _valid_evidence()
    evidence["short_side_disabled"] = False
    assert "short_side_not_disabled" in _blocked(evidence)["blockers"]


def test_sanitized_evidence_only_false_blocks():
    evidence = _valid_evidence()
    evidence["sanitized_evidence_only"] = False
    assert "sanitized_evidence_only_not_confirmed" in _blocked(evidence)["blockers"]


def test_risk_gate_cleared_false_blocks():
    evidence = _valid_evidence()
    evidence["risk_gate_cleared"] = False
    assert "risk_gate_not_cleared" in _blocked(evidence)["blockers"]


def test_evidence_gate_cleared_false_blocks():
    evidence = _valid_evidence()
    evidence["evidence_gate_cleared"] = False
    assert "evidence_gate_not_cleared" in _blocked(evidence)["blockers"]


def test_insufficient_sample_blocks():
    evidence = _valid_evidence()
    evidence["sample_size"] = 29
    assert "insufficient_sample_size" in _blocked(evidence)["blockers"]


def test_insufficient_closed_trades_blocks():
    evidence = _valid_evidence()
    evidence["closed_trades"] = 29
    assert "insufficient_closed_trades" in _blocked(evidence)["blockers"]


def test_expectancy_below_threshold_blocks():
    evidence = _valid_evidence()
    evidence["expectancy"] = 0.0
    assert "expectancy_not_above_threshold" in _blocked(evidence)["blockers"]


def test_profit_factor_below_threshold_blocks():
    evidence = _valid_evidence()
    evidence["profit_factor"] = 1.19
    assert "profit_factor_below_threshold" in _blocked(evidence)["blockers"]


def test_drawdown_above_max_blocks():
    evidence = _valid_evidence()
    evidence["max_drawdown"] = 0.09
    assert "max_drawdown_above_allowed" in _blocked(evidence)["blockers"]


def test_insufficient_walk_forward_folds_blocks():
    evidence = _valid_evidence()
    evidence["walk_forward_folds"] = 2
    assert "insufficient_walk_forward_folds" in _blocked(evidence)["blockers"]


def test_insufficient_oos_folds_blocks():
    evidence = _valid_evidence()
    evidence["out_of_sample_folds"] = 2
    assert "insufficient_out_of_sample_folds" in _blocked(evidence)["blockers"]


def test_negative_expectancy_true_blocks():
    evidence = _valid_evidence()
    evidence["negative_expectancy"] = True
    assert "negative_expectancy" in _blocked(evidence)["blockers"]


def test_mitigation_worsened_true_blocks():
    evidence = _valid_evidence()
    evidence["mitigation_worsened"] = True
    assert "mitigation_worsened" in _blocked(evidence)["blockers"]


def test_overfit_flag_true_blocks():
    evidence = _valid_evidence()
    evidence["overfit_flag"] = True
    assert "overfit_flag" in _blocked(evidence)["blockers"]


def test_nan_numeric_blocks():
    evidence = _valid_evidence()
    evidence["profit_factor"] = math.nan
    assert "invalid_numeric_field:profit_factor" in _blocked(evidence)["blockers"]


def test_infinity_numeric_blocks():
    evidence = _valid_evidence()
    evidence["sample_size"] = math.inf
    assert "invalid_numeric_field:sample_size" in _blocked(evidence)["blockers"]


def test_sensitive_material_blocks():
    evidence = _valid_evidence()
    evidence["proof"] = "Bearer secret"
    assert "sensitive_material_detected" in _blocked(evidence)["blockers"]


def test_valid_long_only_evidence_returns_ready():
    result = gate.evaluate_long_only_profitability_evidence_depth(_valid_evidence())
    assert result["status"] == gate.PROFITABILITY_EVIDENCE_DEPTH_READY
    assert result["ready"] is True
    assert result["evidence_depth_ready_for_demo_preparation"] is True


def test_valid_evidence_still_keeps_execution_allowed_false():
    result = gate.evaluate_long_only_profitability_evidence_depth(_valid_evidence())
    assert result["execution_allowed"] is False
    assert result["ready_to_execute"] is False
    assert result["demo_order_allowed"] is False
    assert result["live_autonomy_allowed"] is False
