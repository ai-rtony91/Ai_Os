from automation.forex_engine.forex_multi_pair_opportunity_batch_v1 import (
    BLOCKED_BY_CANDIDATE_QUALITY,
    BLOCKED_BY_DUPLICATE_PAIR,
    BLOCKED_BY_EMPTY_CANDIDATES,
    BLOCKED_BY_NEWS_BLACKOUT,
    BLOCKED_BY_SPREAD_SLIPPAGE,
    MULTI_PAIR_OPPORTUNITY_BATCH_READY,
    evaluate_forex_multi_pair_opportunity_batch_v1,
)
from automation.forex_engine.forex_multi_pair_universe_v1 import (
    evaluate_forex_multi_pair_universe_v1,
)


def _universe_result():
    return evaluate_forex_multi_pair_universe_v1(
        {
            "governed_burst_requested": True,
            "pair_universe": {
                "allowed_pairs": ["EUR_USD", "GBP_USD", "USD_JPY"],
                "excluded_pairs": [],
                "candidate_pairs": ["EUR_USD", "GBP_USD", "USD_JPY"],
                "max_pairs_to_scan": 3,
                "all_pairs_scan_requested": True,
                "only_trade_allowed_pairs": True,
                "unsupported_pairs_block": True,
                "pair_universe_source": "OWNER_DECLARED",
                "owner_review_required": True,
            },
        }
    )


def _candidate(pair="EUR_USD", score=90, **overrides):
    candidate = {
        "pair": pair,
        "side": "BUY",
        "order_type": "MARKET",
        "units": 1000,
        "setup_id": f"SETUP-{pair}",
        "evidence_id": f"EVIDENCE-{pair}",
        "candidate_score": score,
        "expected_r_multiple": 1.8,
        "minimum_reward_risk_ratio": 1.2,
        "risk_pct": 0.005,
        "stop_loss_present": True,
        "take_profit_present": True,
        "session_allowed": True,
        "news_blackout_clear": True,
        "spread_within_limit": True,
        "slippage_within_limit": True,
    }
    candidate.update(overrides)
    return candidate


def _payload(candidates, **overrides):
    batch = {
        "candidates": candidates,
        "min_candidate_score": 70,
        "max_candidates_per_burst": 2,
        "require_stop_loss": True,
        "require_take_profit": True,
        "require_session_allowed": True,
        "require_news_blackout_clear": True,
        "require_spread_within_limit": True,
        "require_slippage_within_limit": True,
        "duplicate_pair_block": True,
    }
    batch.update(overrides)
    return {
        "governed_burst_requested": True,
        "pair_universe_result": _universe_result(),
        "opportunity_batch": batch,
    }


def test_empty_candidates_block():
    result = evaluate_forex_multi_pair_opportunity_batch_v1(_payload([]))
    assert result["status"] == BLOCKED_BY_EMPTY_CANDIDATES


def test_low_score_blocks_when_no_candidate_is_selected():
    result = evaluate_forex_multi_pair_opportunity_batch_v1(
        _payload([_candidate(score=40)])
    )
    assert result["status"] == BLOCKED_BY_CANDIDATE_QUALITY


def test_missing_stop_loss_blocks():
    result = evaluate_forex_multi_pair_opportunity_batch_v1(
        _payload([_candidate(stop_loss_present=False)])
    )
    assert result["status"] == BLOCKED_BY_CANDIDATE_QUALITY


def test_missing_take_profit_blocks():
    result = evaluate_forex_multi_pair_opportunity_batch_v1(
        _payload([_candidate(take_profit_present=False)])
    )
    assert result["status"] == BLOCKED_BY_CANDIDATE_QUALITY


def test_spread_or_slippage_blocks():
    result = evaluate_forex_multi_pair_opportunity_batch_v1(
        _payload([_candidate(spread_within_limit=False)])
    )
    assert result["status"] == BLOCKED_BY_SPREAD_SLIPPAGE


def test_news_blackout_blocks():
    result = evaluate_forex_multi_pair_opportunity_batch_v1(
        _payload([_candidate(news_blackout_clear=False)])
    )
    assert result["status"] == BLOCKED_BY_NEWS_BLACKOUT


def test_duplicate_pair_blocks():
    result = evaluate_forex_multi_pair_opportunity_batch_v1(
        _payload([_candidate("EUR_USD", 90), _candidate("EUR_USD", 95)])
    )
    assert result["status"] == BLOCKED_BY_DUPLICATE_PAIR


def test_top_ranked_candidates_selected():
    result = evaluate_forex_multi_pair_opportunity_batch_v1(
        _payload(
            [
                _candidate("EUR_USD", 80),
                _candidate("GBP_USD", 95),
                _candidate("USD_JPY", 88),
            ]
        )
    )
    assert result["status"] == MULTI_PAIR_OPPORTUNITY_BATCH_READY
    assert result["selected_count"] == 2
    assert [item["pair"] for item in result["selected_candidates"]] == [
        "GBP_USD",
        "USD_JPY",
    ]
