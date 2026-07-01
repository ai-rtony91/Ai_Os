from automation.forex_engine.forex_multi_pair_universe_v1 import (
    BLOCKED_BY_EMPTY_PAIR_UNIVERSE,
    BLOCKED_BY_EXCLUDED_PAIR,
    BLOCKED_BY_UNSUPPORTED_PAIR,
    MULTI_PAIR_UNIVERSE_READY,
    evaluate_forex_multi_pair_universe_v1,
)


def _payload(**overrides):
    pair_universe = {
        "allowed_pairs": ["EUR_USD", "GBP_USD", "USD_JPY"],
        "excluded_pairs": [],
        "candidate_pairs": ["EUR_USD", "GBP_USD"],
        "max_pairs_to_scan": 3,
        "all_pairs_scan_requested": False,
        "only_trade_allowed_pairs": True,
        "unsupported_pairs_block": True,
        "pair_universe_source": "OWNER_DECLARED",
        "owner_review_required": True,
    }
    pair_universe.update(overrides)
    return {"governed_burst_requested": True, "pair_universe": pair_universe}


def test_empty_allowed_pairs_blocks():
    result = evaluate_forex_multi_pair_universe_v1(_payload(allowed_pairs=[]))
    assert result["status"] == BLOCKED_BY_EMPTY_PAIR_UNIVERSE
    assert result["ready"] is False


def test_all_pairs_scan_requested_scans_declared_allowed_pairs_only():
    result = evaluate_forex_multi_pair_universe_v1(
        _payload(all_pairs_scan_requested=True, candidate_pairs=["EUR_USD"])
    )
    assert result["status"] == MULTI_PAIR_UNIVERSE_READY
    assert result["scan_pair_count"] == 3
    assert result["allowed_pairs_sanitized"] == ["EUR_USD", "GBP_USD", "USD_JPY"]


def test_unsupported_candidate_pair_blocks():
    result = evaluate_forex_multi_pair_universe_v1(
        _payload(candidate_pairs=["EUR_USD", "AUD_USD"])
    )
    assert result["status"] == BLOCKED_BY_UNSUPPORTED_PAIR


def test_excluded_pair_blocks():
    result = evaluate_forex_multi_pair_universe_v1(
        _payload(excluded_pairs=["GBP_USD"], candidate_pairs=["EUR_USD", "GBP_USD"])
    )
    assert result["status"] == BLOCKED_BY_EXCLUDED_PAIR


def test_valid_universe_ready():
    result = evaluate_forex_multi_pair_universe_v1(_payload())
    assert result["status"] == MULTI_PAIR_UNIVERSE_READY
    assert result["ready_for_opportunity_batch"] is True
    assert result["safety"]["broker_api_called_by_this_module"] is False
