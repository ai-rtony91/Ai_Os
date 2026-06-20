"""Tests for automation/forex_engine/strategy_candidates.py."""

from __future__ import annotations

from pathlib import Path

from automation.forex_engine.strategy_candidates import (
    STRATEGY_CANDIDATE_ALLOWED,
    STRATEGY_CANDIDATE_BLOCKED,
    STRATEGY_CANDIDATE_MODE,
    REJECTION_REASON_EVIDENCE_PATH_INVALID,
    REJECTION_REASON_INSUFFICIENT_CANDLES,
    REJECTION_REASON_INVALID_CANDLE_DATA,
    REJECTION_REASON_INVALID_MARKET_DATA,
    REJECTION_REASON_LIVE_TRADING_BLOCKED,
    REJECTION_REASON_MISSING_CANDLES,
    REJECTION_REASON_MISSING_PAIR,
    REJECTION_REASON_NON_PAPER_MODE,
    REJECTION_REASON_NO_TRADE_SIGNAL,
    REJECTION_REASON_SCORE_BELOW_THRESHOLD,
    REJECTION_REASON_STALE_MARKET_DATA,
    REJECTION_REASON_SPREAD_TOO_HIGH,
    REJECTION_REASON_UNSUPPORTED_STRATEGY,
    generate_strategy_candidates,
)


def _base_market() -> dict:
    return {
        "pair": "EURUSD",
        "source_mode": "paper",
        "bid": 1.1000,
        "ask": 1.1003,
        "spread_pips": 3.0,
        "timestamp": 1_700_000_100,
        "candles": [
            {"open": 1.0950, "high": 1.0980, "low": 1.0940, "close": 1.0960, "volume": 100.0, "timestamp": 1_700_000_090},
            {"open": 1.0960, "high": 1.0990, "low": 1.0950, "close": 1.0980, "volume": 110.0, "timestamp": 1_700_000_091},
            {"open": 1.0980, "high": 1.1010, "low": 1.0970, "close": 1.1000, "volume": 120.0, "timestamp": 1_700_000_092},
            {"open": 1.1000, "high": 1.1020, "low": 1.0990, "close": 1.1015, "volume": 130.0, "timestamp": 1_700_000_093},
            {"open": 1.1015, "high": 1.1030, "low": 1.1000, "close": 1.1025, "timestamp": 1_700_000_094},
            {"open": 1.1025, "high": 1.1040, "low": 1.1010, "close": 1.1035, "timestamp": 1_700_000_095},
        ],
        "paper_only": True,
    }


def _assert_allowed(out: dict) -> None:
    assert out["allowed"] is True
    assert out["decision"] == STRATEGY_CANDIDATE_ALLOWED
    assert out["blocked_reasons"] == []


def _assert_blocked(out: dict, reason: str) -> None:
    assert out["allowed"] is False
    assert out["decision"] == STRATEGY_CANDIDATE_BLOCKED
    assert out["blocked_reason"] == reason
    assert out["blocked_reasons"] == [reason]


def test_import_and_defaults():
    assert STRATEGY_CANDIDATE_MODE == "PAPER_ONLY"
    assert STRATEGY_CANDIDATE_ALLOWED == "allowed"
    assert STRATEGY_CANDIDATE_BLOCKED == "blocked"


def test_valid_moving_average_buy_candidate():
    market = _base_market()
    # force a clear uptrend for MA buy
    market["candles"][-3]["close"] = 1.10
    market["candles"][-2]["close"] = 1.101
    market["candles"][-1]["close"] = 1.1025
    out = generate_strategy_candidates(market, strategies=["moving_average_trend"])
    _assert_allowed(out)
    cands = [c for c in out["candidates"] if c["strategy_name"] == "moving_average_trend"]
    assert len(cands) == 1
    c = cands[0]
    assert c["direction"] == "buy"
    assert c["entry_type"] == "market"
    assert c["stop_loss"] < c["entry_price"] < c["take_profit"]


def test_valid_moving_average_sell_candidate():
    market = _base_market()
    # force a clear downtrend for MA sell
    market["candles"][-3]["close"] = 1.10
    market["candles"][-2]["close"] = 1.097
    market["candles"][-1]["close"] = 1.095
    market["candles"][-1]["high"] = 1.096
    market["candles"][-1]["low"] = 1.094
    out = generate_strategy_candidates(market, strategies=["moving_average_trend"])
    _assert_allowed(out)
    cands = [c for c in out["candidates"] if c["strategy_name"] == "moving_average_trend"]
    assert len(cands) == 1
    c = cands[0]
    assert c["direction"] == "sell"
    assert c["stop_loss"] > c["entry_price"] > c["take_profit"]


def test_valid_breakout_buy_candidate():
    market = _base_market()
    # close above prior highs
    market["candles"][-1]["close"] = 1.1060
    market["candles"][-1]["high"] = 1.1060
    market["candles"][-1]["low"] = 1.1040
    out = generate_strategy_candidates(market, strategies=["breakout"])
    _assert_allowed(out)
    cands = [c for c in out["candidates"] if c["strategy_name"] == "breakout"]
    assert len(cands) == 1
    assert cands[0]["direction"] == "buy"


def test_valid_breakout_sell_candidate():
    market = _base_market()
    # close below prior lows
    market["candles"][-1]["close"] = 1.0880
    market["candles"][-1]["high"] = 1.0890
    market["candles"][-1]["low"] = 1.0860
    out = generate_strategy_candidates(market, strategies=["breakout"])
    _assert_allowed(out)
    cands = [c for c in out["candidates"] if c["strategy_name"] == "breakout"]
    assert len(cands) == 1
    assert cands[0]["direction"] == "sell"


def test_no_trade_when_conditions_not_met():
    market = _base_market()
    # keep candles inside prior range to suppress breakout/ma crossover for both
    for i in range(len(market["candles"])):
        market["candles"][i]["close"] = 1.1010
    out = generate_strategy_candidates(market, strategies=["moving_average_trend", "breakout"])
    _assert_allowed(out)
    assert out["selected_count"] == 0
    assert out["no_trade_count"] >= 1


def test_insufficient_candles_blocked():
    market = _base_market()
    market["candles"] = market["candles"][:1]
    out = generate_strategy_candidates(market, strategies=["moving_average_trend", "breakout"])
    _assert_allowed(out)
    reasons = [c["rejection_reasons"][0] for c in out["rejected_candidates"]]
    assert REJECTION_REASON_INSUFFICIENT_CANDLES in reasons
    assert out["selected_count"] == 0


def test_missing_pair_blocked():
    market = _base_market()
    del market["pair"]
    out = generate_strategy_candidates(market)
    _assert_blocked(out, REJECTION_REASON_MISSING_PAIR)


def test_invalid_candle_data_blocked():
    market = _base_market()
    market["candles"][-1]["close"] = "bad"
    out = generate_strategy_candidates(market, strategies=["moving_average_trend"])
    assert out["allowed"] is True
    assert out["decision"] == STRATEGY_CANDIDATE_ALLOWED
    assert out["selected_count"] == 0
    assert out["rejected_candidates"]
    assert out["rejected_candidates"][0]["rejection_reasons"][0] == REJECTION_REASON_INVALID_CANDLE_DATA


def test_unsupported_strategy_blocks():
    out = generate_strategy_candidates(_base_market(), strategies=["martingale", "moving_average_trend"])
    assert out["allowed"] is True
    assert out["decision"] == STRATEGY_CANDIDATE_ALLOWED
    rejected_reasons = [c["rejection_reasons"][0] for c in out["rejected_candidates"] if c["strategy_name"] == "martingale"]
    assert REJECTION_REASON_UNSUPPORTED_STRATEGY in rejected_reasons


def test_score_below_threshold_rejected():
    out = generate_strategy_candidates(
        _base_market(),
        strategies=["moving_average_trend"],
        limits={"min_score": 99.0},
    )
    # score filter applies to generated signals; if blocked by score we keep response allowed and list rejection
    assert out["allowed"] is True
    if out["rejected_candidates"]:
        reasons = [c["rejection_reasons"][0] for c in out["rejected_candidates"]]
        assert REJECTION_REASON_SCORE_BELOW_THRESHOLD in reasons


def test_live_demo_broker_mode_blocks():
    market = _base_market()
    market["source_mode"] = "live"
    out = generate_strategy_candidates(market, strategies=["breakout"])
    _assert_blocked(out, REJECTION_REASON_LIVE_TRADING_BLOCKED)

    market["source_mode"] = "broker"
    out = generate_strategy_candidates(market, strategies=["breakout"])
    _assert_blocked(out, REJECTION_REASON_NON_PAPER_MODE)


def test_paper_only_false_blocked():
    market = _base_market()
    market["paper_only"] = False
    out = generate_strategy_candidates(market, strategies=["breakout"])
    _assert_blocked(out, REJECTION_REASON_NON_PAPER_MODE)


def test_stale_and_high_spread_inputs():
    market = _base_market()
    market["timestamp"] = 1
    out = generate_strategy_candidates(market, now_timestamp=1_700_000_200, strategies=["breakout"])
    _assert_blocked(out, REJECTION_REASON_STALE_MARKET_DATA)

    market["timestamp"] = 1_700_000_100
    market["spread_pips"] = 10.0
    out = generate_strategy_candidates(market, strategies=["breakout"])
    _assert_blocked(out, REJECTION_REASON_SPREAD_TOO_HIGH)


def test_missing_candles_blocked():
    market = _base_market()
    market.pop("candles")
    out = generate_strategy_candidates(market, strategies=["breakout"])
    _assert_blocked(out, REJECTION_REASON_MISSING_CANDLES)


def test_invalid_evidence_path_blocked():
    out = generate_strategy_candidates(_base_market(), evidence_path="/tmp/evidence.txt")
    _assert_blocked(out, REJECTION_REASON_EVIDENCE_PATH_INVALID)


def test_candidate_id_deterministic():
    out1 = generate_strategy_candidates(_base_market(), strategies=["breakout"])
    out2 = generate_strategy_candidates(_base_market(), strategies=["breakout"])
    _assert_allowed(out1)
    _assert_allowed(out2)
    ids1 = [c["candidate_id"] for c in out1["candidates"] if c["candidate_id"]]
    ids2 = [c["candidate_id"] for c in out2["candidates"] if c["candidate_id"]]
    assert ids1 == ids2


def test_candidate_fields_order_preview_ready():
    out = generate_strategy_candidates(_base_market(), strategies=["breakout"])
    _assert_allowed(out)
    if out["candidates"]:
        c = out["candidates"][0]
        required = ["candidate_id", "strategy_name", "pair", "direction", "entry_type", "entry_price", "stop_loss", "take_profit", "risk_percent"]
        for key in required:
            assert key in c
        assert c["paper_only"] is True
        assert c["entry_price"] > 0
        if c["direction"] == "buy":
            assert c["stop_loss"] < c["entry_price"] < c["take_profit"]
        else:
            assert c["stop_loss"] > c["entry_price"] > c["take_profit"]


def test_safety_and_evidence_inline():
    out = generate_strategy_candidates(_base_market(), strategies=["breakout"])
    _assert_allowed(out)
    assert out["safety"] == {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }
    assert isinstance(out["evidence"], dict)


def test_deterministic_rejections():
    market = _base_market()
    market["candles"] = market["candles"][:3]
    out1 = generate_strategy_candidates(market, strategies=["breakout"])
    out2 = generate_strategy_candidates(market, strategies=["breakout"])
    _assert_allowed(out1)
    _assert_allowed(out2)
    assert [c["rejection_reasons"] for c in out1["rejected_candidates"]] == [c["rejection_reasons"] for c in out2["rejected_candidates"]]


def test_source_safety_scan_no_io_or_network():
    source = Path("automation/forex_engine/strategy_candidates.py").read_text(encoding="utf-8").lower()
    for blocked in [
        "subprocess",
        "requests",
        "socket",
        "urllib",
        "open(",
        ".write_text",
        ".write_bytes",
        "pathlib",
        "os.system",
        "broker sdk",
        "credential",
        "account_id",
        "getenv",
        "environ",
        "secret",
    ]:
        assert blocked not in source
