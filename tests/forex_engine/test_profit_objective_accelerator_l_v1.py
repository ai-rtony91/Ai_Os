"""Tests for the Forex profit objective acceleration gate."""
from __future__ import annotations

import inspect

from automation.forex_engine import profit_objective_accelerator_l_v1 as accelerator


def _candidate(direction: str, offset: float = 0.0) -> dict:
    return {
        "strategy_id": "MEAN_REVERSION",
        "candidate_id": f"{direction}_A",
        "direction": direction,
        "trade_pnl_list": [
            120.0 + offset,
            110.0 + offset,
            -40.0,
            130.0 + offset,
            115.0 + offset,
            -30.0,
            90.0 + offset,
            80.0 + offset,
            -25.0,
            150.0 + offset,
            70.0 + offset,
            -20.0,
            105.0 + offset,
            95.0 + offset,
            -35.0,
            60.0 + offset,
            140.0 + offset,
            -15.0,
            85.0 + offset,
            75.0 + offset,
            130.0 + offset,
        ],
    }


def _candidate_from_losses():
    return {
        "strategy_id": "TREND_BREAK",
        "candidate_id": "TREND_A",
        "direction": "LONG",
        "trade_pnl_list": [50, -120, 30, -70, -60, 20],
    }


def _candidate_from_drawdown():
    return {
        "strategy_id": "DRAWDOWN",
        "candidate_id": "DD_A",
        "direction": "SHORT",
        "trade_pnl_list": [
            4000.0,
            -6000.0,
            1500.0,
            1500.0,
            1500.0,
            1500.0,
            1500.0,
            1500.0,
            1500.0,
            1500.0,
            1500.0,
            1500.0,
            1500.0,
            1500.0,
            1500.0,
            1500.0,
            1500.0,
            1500.0,
            1500.0,
            1500.0,
        ],
    }


def test_long_candidate_accepted_and_ready():
    candidate = _candidate("LONG")
    result = accelerator.evaluate_profitability_candidate(
        strategy_id=candidate["strategy_id"],
        candidate_id=candidate["candidate_id"],
        direction=candidate["direction"],
        trade_pnl_list=candidate["trade_pnl_list"],
    )
    assert result["strategy_id"] == "MEAN_REVERSION"
    assert result["direction"] == "LONG"
    assert result["promotion_status"] == accelerator.PROMOTION_STATUS_PROFIT_OBJECTIVE_READY
    assert result["sample_size"] >= 20
    assert result["expectancy"] > 0
    assert result["profit_factor"] >= 1.25
    assert result["max_drawdown"] <= 10.0


def test_short_candidate_accepted_and_ready():
    candidate = _candidate("SHORT", offset=10.0)
    result = accelerator.evaluate_profitability_candidate(
        strategy_id=candidate["strategy_id"],
        candidate_id=candidate["candidate_id"],
        direction=candidate["direction"],
        trade_pnl_list=candidate["trade_pnl_list"],
    )
    assert result["direction"] == "SHORT"
    assert result["promotion_status"] == accelerator.PROMOTION_STATUS_PROFIT_OBJECTIVE_READY


def test_unsupported_direction_rejected():
    result = accelerator.evaluate_profitability_candidate(
        strategy_id="MEAN_REVERSION",
        candidate_id="BAD_001",
        direction="BIDIRECTIONAL",
        trade_pnl_list=[10.0] * 20,
    )
    assert result["promotion_status"] == accelerator.PROMOTION_STATUS_REJECT_DIRECTION_UNSUPPORTED
    assert result["blocked"] is True
    assert "unsupported_direction" in result["blocked_reasons"]


def test_negative_expectancy_rejected():
    candidate = {
        "strategy_id": "MEAN_REVERSION",
        "candidate_id": "NEG_001",
        "direction": "LONG",
        "trade_pnl_list": [5.0, -50.0] * 10,
    }
    result = accelerator.evaluate_profitability_candidate(**candidate)
    assert result["promotion_status"] == accelerator.PROMOTION_STATUS_REJECT_NEGATIVE_EXPECTANCY
    assert result["expectancy"] < 0
    assert result["blocked"] is True


def test_low_profit_factor_rejected():
    candidate = {
        "strategy_id": "MEAN_REVERSION",
        "candidate_id": "LOW_PF",
        "direction": "LONG",
        "trade_pnl_list": [100.0, -90.0] * 10,
    }
    result = accelerator.evaluate_profitability_candidate(**candidate)
    assert result["profit_factor"] < 1.25
    assert result["promotion_status"] == accelerator.PROMOTION_STATUS_REJECT_LOW_PROFIT_FACTOR


def test_excessive_drawdown_rejected():
    candidate = _candidate_from_drawdown()
    result = accelerator.evaluate_profitability_candidate(
        strategy_id=candidate["strategy_id"],
        candidate_id=candidate["candidate_id"],
        direction=candidate["direction"],
        trade_pnl_list=candidate["trade_pnl_list"],
    )
    assert result["promotion_status"] == accelerator.PROMOTION_STATUS_REJECT_EXCESSIVE_DRAWDOWN
    assert result["max_drawdown"] > 10.0
    assert result["blocked"] is True


def test_insufficient_sample_rejected():
    candidate = {"strategy_id": "MEAN_REVERSION", "candidate_id": "SMALL", "direction": "LONG", "trade_pnl_list": [12.0] * 10}
    result = accelerator.evaluate_profitability_candidate(**candidate)
    assert result["promotion_status"] == accelerator.PROMOTION_STATUS_REJECT_INSUFFICIENT_SAMPLE
    assert result["sample_size"] == 10
    assert result["blocked"] is True


def test_profitable_candidate_reaches_ready_status():
    result = accelerator.evaluate_profitability_candidate(
        strategy_id="MEAN_REVERSION",
        candidate_id="BEST",
        direction="LONG",
        trade_pnl_list=_candidate("LONG")["trade_pnl_list"],
    )
    assert result["promotion_status"] == accelerator.PROMOTION_STATUS_PROFIT_OBJECTIVE_READY


def test_best_candidate_ranking_selects_highest_quality_candidate():
    pool = [
        _candidate("LONG", 0.0),
        _candidate("SHORT", -20.0),
        {"strategy_id": "MEAN_REVERSION", "candidate_id": "MARGINAL", "direction": "SHORT", "trade_pnl_list": [20.0, -10.0] * 10},
    ]
    ranked = accelerator.rank_candidates(candidate_evals=pool)
    assert ranked["promotion_status"] == accelerator.PROMOTION_STATUS_PROFIT_OBJECTIVE_READY
    assert ranked["best_candidate"]["strategy_id"] == "MEAN_REVERSION"
    assert ranked["best_candidate"]["candidate_id"] == "LONG_A"
    assert len(ranked["ranked_candidates"]) == 3


def test_consecutive_win_and_loss_profile_calculated():
    result = accelerator.evaluate_profitability_candidate(
        strategy_id="MEAN_REVERSION",
        candidate_id="SERIES",
        direction="LONG",
        trade_pnl_list=[5.0, 10.0, -6.0, -7.0, 9.0, 11.0, 13.0, -4.0],
    )
    assert result["consecutive_wins"] == 3
    assert result["consecutive_losses"] == 2
    assert result["win_rate"] == 0.625


def test_ranker_requires_both_directions_present():
    ranked = accelerator.rank_candidates(
        candidate_evals=[
            _candidate("LONG"),
            _candidate("LONG", -50.0),
        ]
    )
    assert ranked["directional_readiness"]["supports_long"] is True
    assert ranked["directional_readiness"]["supports_short"] is False
    assert ranked["directional_readiness"]["both_supported"] is False
    assert ranked["next_safe_action"] in (
        "select_best_candidate_for_governed_paper_or_demo",
        "continue_paper_validation_and_collect_more_evidence",
    )


def test_source_has_no_forbidden_runtime_surface():
    source = inspect.getsource(accelerator)
    forbidden = (
        "requests",
        "urllib",
        "socket",
        "subprocess",
        "os.environ",
        "getenv(",
        "open(",
        "write_text",
        "write_bytes",
    )
    for token in forbidden:
        assert token not in source
