"""Tests for the governed multi-pair opportunity scorer."""
from __future__ import annotations

import inspect
import importlib

from automation.forex_engine.forex_multi_pair_opportunity_scorer_v1 import (
    SCORER_SCHEMA,
    score_multi_pair_opportunities,
)


def _pair(symbol: str, **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "pair": symbol,
        "confidence_score": 62.0,
        "spread_bps": 1.0,
        "volatility": 0.8,
        "liquidity_score": 70.0,
        "expectancy_score": 72.0,
        "max_drawdown_pct": 4.0,
        "sample_size": 80,
        "evidence_age_days": 6,
        "evidence_quality_score": 82.0,
    }
    payload.update(overrides)
    return payload


def test_rank_and_cap_allocations_for_multiple_pairs_in_review_mode() -> None:
    result = score_multi_pair_opportunities(
        [
            _pair("EURUSD", confidence_score=95.0, evidence_quality_score=95.0, expectancy_score=82.0),
            _pair("USDJPY", confidence_score=78.0, evidence_quality_score=76.0, expectancy_score=75.0),
            _pair("GBPUSD", confidence_score=73.0, evidence_quality_score=74.0, expectancy_score=70.0),
        ]
    )

    assert result["schema"] == SCORER_SCHEMA
    assert result["mode"] == "PAPER_ONLY"
    assert result["review_only"] is True
    assert result["total_portfolio_risk_percent"] == 6.0
    assert result["max_pair_risk_percent"] == 2.0
    assert result["safe_next_action"].startswith("Paper/simulation-only multi-pair allocation")

    ranked = result["ranked_pairs"]
    assert ranked[0]["pair"] == "EURUSD"
    assert ranked[0]["rank"] == 1
    assert ranked[1]["rank"] == 2
    assert ranked[2]["rank"] == 3
    assert all(pair["eligible"] for pair in ranked if pair["proposed_allocation_percent"] > 0)
    assert all(pair["proposed_allocation_percent"] <= 2.0 for pair in ranked)
    assert sum(pair["proposed_allocation_percent"] for pair in ranked) == 6.0


def test_correlation_penalizes_clustered_pairs_to_spread_allocations() -> None:
    pairs = [
        _pair("EURUSD", confidence_score=78.0, expectancy_score=78.0, evidence_quality_score=86.0),
        _pair("USDJPY", confidence_score=78.0, expectancy_score=78.0, evidence_quality_score=86.0),
        _pair("GBPUSD", confidence_score=78.0, expectancy_score=78.0, evidence_quality_score=86.0),
    ]
    correlation_matrix = {
        "EURUSD": {"USDJPY": 0.93, "GBPUSD": 0.01},
        "USDJPY": {"EURUSD": 0.93, "GBPUSD": 0.02},
        "GBPUSD": {"EURUSD": 0.01, "USDJPY": 0.02},
    }
    correlated_result = score_multi_pair_opportunities(
        pairs,
        pair_correlation_matrix=correlation_matrix,
        risk_policy={"max_pair_risk_percent": 3.0, "max_total_portfolio_risk_percent": 6.0},
    )
    uncorrelated_result = score_multi_pair_opportunities(
        pairs,
        risk_policy={"max_pair_risk_percent": 3.0, "max_total_portfolio_risk_percent": 6.0},
    )

    correlated_pairs = {item["pair"]: item for item in correlated_result["ranked_pairs"]}
    uncorrelated_pairs = {item["pair"]: item for item in uncorrelated_result["ranked_pairs"]}

    assert correlated_pairs["USDJPY"]["proposed_allocation_percent"] < uncorrelated_pairs["USDJPY"]["proposed_allocation_percent"]
    assert correlated_pairs["EURUSD"]["proposed_allocation_percent"] > 0
    assert correlated_pairs["GBPUSD"]["proposed_allocation_percent"] >= correlated_pairs["USDJPY"]["proposed_allocation_percent"]
    assert sum(pair["proposed_allocation_percent"] for pair in correlated_pairs.values()) == 6.0


def test_read_only_global_blockers_prevent_allocation_and_mark_rejections() -> None:
    result = score_multi_pair_opportunities(
        [
            _pair("EURUSD", confidence_score=85.0, expectancy_score=85.0),
            _pair("USDJPY", confidence_score=84.0, expectancy_score=84.0),
        ],
        execution_context={
            "kill_switch_active": True,
            "daily_loss_stop_reached": True,
            "margin_guard_active": False,
            "scheduler_enabled": True,
            "daemon_enabled": True,
            "webhook_enabled": True,
            "broker_integration_enabled": True,
            "live_execution_requested": True,
        },
    )

    assert set(result["rejection_reasons"]) >= {
        "kill_switch_active",
        "daily_loss_stop_reached",
        "margin_guard_blocked",
        "broker_integration_not_allowed",
        "live_execution_requested_not_allowed",
        "scheduler_enabled_not_allowed",
        "daemon_enabled_not_allowed",
        "webhook_enabled_not_allowed",
    }
    assert result["total_portfolio_risk_percent"] == 0.0
    assert all(pair["proposed_allocation_percent"] == 0.0 for pair in result["ranked_pairs"])
    assert "Repair" in result["safe_next_action"] or "repair" in result["safe_next_action"]
    assert result["safety"]["scheduler_allowed"] is False


def test_no_input_does_not_allocate_and_reports_read_only_reasons() -> None:
    result = score_multi_pair_opportunities(None)
    assert result["total_portfolio_risk_percent"] == 0.0
    assert result["proposed_allocation_percent"] == 0.0
    assert result["safe_next_action"] == "Collect and provide valid read-only pair metrics before rerunning scoring."
    assert "input_must_be_sequence" not in result["rejection_reasons"]
    assert "no_valid_pair_metrics" in result["rejection_reasons"]
    assert result["review_only"] is True


def test_input_must_be_sequence_is_reported_for_non_sequence_payload() -> None:
    result = score_multi_pair_opportunities(123)
    assert "input_must_be_sequence" in result["rejection_reasons"]
    assert "no_valid_pair_metrics" in result["rejection_reasons"]
    assert result["ranked_pairs"] == []
    assert "read-only" in result["safe_next_action"] or "Collect" in result["safe_next_action"]


def test_policy_caps_prevent_all_in_and_enforce_required_output_fields() -> None:
    result = score_multi_pair_opportunities(
        [_pair("EURUSD", confidence_score=92.0, expectancy_score=85.0, evidence_quality_score=98.0)],
        risk_policy={"max_pair_risk_percent": 140.0, "max_total_portfolio_risk_percent": 140.0},
    )

    assert result["total_portfolio_risk_percent"] < 100.0
    assert result["max_pair_risk_percent"] <= 99.0
    assert result["proposed_allocation_percent"] == result["total_portfolio_risk_percent"]

    for key in (
        "ranked_pairs",
        "confidence_score",
        "spread_score",
        "volatility_score",
        "liquidity_score",
        "expectancy_score",
        "risk_adjusted_score",
        "proposed_allocation_percent",
        "max_pair_risk_percent",
        "total_portfolio_risk_percent",
        "rejection_reasons",
        "safe_next_action",
    ):
        assert key in result


def test_source_is_read_only_and_forbidden_calls_are_absent() -> None:
    module = importlib.import_module("automation.forex_engine.forex_multi_pair_opportunity_scorer_v1")
    source = inspect.getsource(module)
    for token in (
        "requests",
        "socket",
        "urllib",
        "subprocess",
        "os.environ",
        "broker_sdk",
        "schedule.every",
        "start-process",
    ):
        assert token not in source
