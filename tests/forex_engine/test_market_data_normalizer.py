"""Tests for automation/forex_engine/market_data_normalizer.py."""

from __future__ import annotations

from pathlib import Path

from automation.forex_engine.market_data_normalizer import (
    MARKET_DATA_ALLOWED,
    MARKET_DATA_BLOCKED,
    MARKET_DATA_MODE,
    REJECTION_INVALID_CANDLE,
    REJECTION_INVALID_MARKET_DATA,
    REJECTION_INVALID_OHLCV,
    REJECTION_INVALID_SOURCE_MODE,
    REJECTION_INVALID_TIMESTAMP,
    REJECTION_INVALID_BID,
    REJECTION_INVALID_ASK,
    REJECTION_INVALID_SPREAD,
    REJECTION_LIVE_TRADING_BLOCKED,
    REJECTION_MISSING_ASK,
    REJECTION_MISSING_BID,
    REJECTION_MISSING_CANDLE,
    REJECTION_MISSING_PAIR,
    REJECTION_MISSING_TIMESTAMP,
    REJECTION_NON_PAPER_MODE,
    REJECTION_SPREAD_TOO_HIGH,
    REJECTION_STALE_DATA,
    REJECTION_UNSUPPORTED_PAIR,
    REJECTION_NONE,
    REJECTION_EVIDENCE_PATH_INVALID,
    normalize_market_snapshot,
)


def _assert_allowed(out: dict) -> None:
    assert out["allowed"] is True
    assert out["decision"] == MARKET_DATA_ALLOWED
    assert out["blocked_reason"] == REJECTION_NONE
    assert out["blocked_reasons"] == []


def _assert_blocked(out: dict, reason: str) -> None:
    assert out["allowed"] is False
    assert out["decision"] == MARKET_DATA_BLOCKED
    assert out["blocked_reason"] == reason
    assert out["blocked_reasons"] == [reason]


def test_import_and_defaults():
    assert MARKET_DATA_MODE == "PAPER_ONLY"


def test_valid_eur_usd_with_separator_normalizes_pair():
    out = normalize_market_snapshot({"pair": "eur_usd", "bid": 1.1000, "ask": 1.1002, "timestamp": 1000})
    _assert_allowed(out)
    assert out["pair"] == "EURUSD"


def test_valid_bid_ask_and_spread_calculation():
    out = normalize_market_snapshot({"pair": "EURUSD", "bid": 1.1, "ask": 1.1004, "timestamp": 1000}, now_timestamp=1005, limits={"max_spread_pips": 10})
    _assert_allowed(out)
    assert out["mid"] == 1.1002
    assert out["spread"] == 0.0004
    assert out["spread_pips"] == 4.0
    assert out["pip_size"] == 0.0001


def test_jpy_pip_size_works():
    out = normalize_market_snapshot({"pair": "USDJPY", "bid": 110.0, "ask": 110.03, "timestamp": 1000}, limits={"max_spread_pips": 5})
    _assert_allowed(out)
    assert out["pip_size"] == 0.01
    assert out["spread_pips"] == 3.0


def test_missing_bid_blocks():
    out = normalize_market_snapshot({"pair": "EURUSD", "ask": 1.2, "timestamp": 1000})
    _assert_blocked(out, REJECTION_MISSING_BID)


def test_missing_ask_blocks():
    out = normalize_market_snapshot({"pair": "EURUSD", "bid": 1.2, "timestamp": 1000})
    _assert_blocked(out, REJECTION_MISSING_ASK)


def test_negative_bid_blocks():
    out = normalize_market_snapshot({"pair": "EURUSD", "bid": -1.2, "ask": 1.3, "timestamp": 1000})
    _assert_blocked(out, REJECTION_INVALID_BID)


def test_ask_below_bid_blocks():
    out = normalize_market_snapshot({"pair": "EURUSD", "bid": 1.3000, "ask": 1.2990, "timestamp": 1000})
    _assert_blocked(out, REJECTION_INVALID_SPREAD)


def test_high_spread_blocks():
    out = normalize_market_snapshot(
        {"pair": "EURUSD", "bid": 1.1, "ask": 1.2, "timestamp": 1000},
        limits={"max_spread_pips": 1.0},
    )
    _assert_blocked(out, REJECTION_SPREAD_TOO_HIGH)


def test_missing_timestamp_blocks_when_required():
    out = normalize_market_snapshot({"pair": "EURUSD", "bid": 1.1, "ask": 1.1001})
    _assert_blocked(out, REJECTION_MISSING_TIMESTAMP)


def test_stale_data_blocks_with_fixed_now():
    out = normalize_market_snapshot(
        {"pair": "EURUSD", "bid": 1.1, "ask": 1.1001, "timestamp": 100},
        now_timestamp=1000,
        limits={"max_data_age_seconds": 10},
    )
    _assert_blocked(out, REJECTION_STALE_DATA)


def test_fresh_data_passes_with_fixed_now():
    out = normalize_market_snapshot(
        {"pair": "EURUSD", "bid": 1.1, "ask": 1.1001, "timestamp": 100},
        now_timestamp=350,
        limits={"max_data_age_seconds": 300},
    )
    _assert_allowed(out)
    assert out["fresh"] is True


def test_source_mode_sample_and_paper_pass():
    _assert_allowed(normalize_market_snapshot({"pair": "EURUSD", "bid": 1.1, "ask": 1.1001, "source_mode": "sample", "timestamp": 1}))
    _assert_allowed(normalize_market_snapshot({"pair": "EURUSD", "bid": 1.1, "ask": 1.1001, "source_mode": "paper", "timestamp": 1}))


def test_live_and_broker_modes_blocked():
    _assert_blocked(
        normalize_market_snapshot({"pair": "EURUSD", "bid": 1.1, "ask": 1.1001, "source_mode": "live", "timestamp": 1}),
        REJECTION_LIVE_TRADING_BLOCKED,
    )
    _assert_blocked(
        normalize_market_snapshot({"pair": "EURUSD", "bid": 1.1, "ask": 1.1001, "source_mode": "broker", "timestamp": 1}),
        REJECTION_NON_PAPER_MODE,
    )
    _assert_blocked(
        normalize_market_snapshot({"pair": "EURUSD", "bid": 1.1, "ask": 1.1001, "source_mode": "demo", "timestamp": 1}),
        REJECTION_INVALID_SOURCE_MODE,
    )


def test_valid_single_candle_passes():
    out = normalize_market_snapshot(
        {
            "pair": "EURUSD",
            "bid": 1.1,
            "ask": 1.1002,
            "timestamp": 1000,
            "candle": {"open": 1.1, "high": 1.12, "low": 1.09, "close": 1.11, "volume": 100.0, "timestamp": 999},
        }
    )
    _assert_allowed(out)
    assert out["candle"]["open"] == 1.1
    assert out["normalized_for_strategy"]["candle"]["close"] == 1.11


def test_invalid_candle_ohlcv_blocks():
    out = normalize_market_snapshot(
        {
            "pair": "EURUSD",
            "bid": 1.1,
            "ask": 1.1002,
            "timestamp": 1000,
            "candle": {"open": 1.1, "high": 1.08, "low": 1.09, "close": 1.11, "volume": 100.0, "timestamp": 999},
        }
    )
    _assert_blocked(out, REJECTION_INVALID_CANDLE)


def test_multiple_candles_normalized():
    out = normalize_market_snapshot(
        {
            "pair": "EURUSD",
            "bid": 1.1,
            "ask": 1.1001,
            "timestamp": 1000,
            "candles": [
                {"open": 1.1, "high": 1.12, "low": 1.09, "close": 1.11, "volume": 2, "timestamp": 990},
                {"open": 1.11, "high": 1.13, "low": 1.1, "close": 1.12, "volume": 3, "timestamp": 999},
            ],
        }
    )
    _assert_allowed(out)
    assert len(out["candles"]) == 2
    assert out["normalized_for_strategy"]["candles"][1]["volume"] == 3.0


def test_require_candle_blocks_missing():
    out = normalize_market_snapshot(
        {"pair": "EURUSD", "bid": 1.1, "ask": 1.1001, "timestamp": 1000},
        limits={"require_candle": True},
    )
    _assert_blocked(out, REJECTION_MISSING_CANDLE)


def test_invalid_evidence_path_blocks():
    out = normalize_market_snapshot(
        {"pair": "EURUSD", "bid": 1.1, "ask": 1.1001, "timestamp": 1},
        evidence_path="/tmp/evidence.json",
    )
    _assert_blocked(out, REJECTION_EVIDENCE_PATH_INVALID)


def test_normalized_payload_shapes():
    out = normalize_market_snapshot(
        {
            "pair": "EURUSD",
            "bid": 1.1,
            "ask": 1.1001,
            "timestamp": 1000,
            "source_mode": "paper",
        },
        now_timestamp=1000,
    )
    _assert_allowed(out)
    assert "pair" in out["normalized_for_preview"]
    assert out["normalized_for_preview"]["entry_price"] == out["mid"]
    assert out["normalized_for_strategy"]["pair"] == out["pair"]
    assert out["normalized_for_strategy"]["paper_only"] is True
    assert out["normalized_for_preview"]["paper_only"] is True


def test_safety_dict_present():
    out = normalize_market_snapshot({"pair": "EURUSD", "bid": 1.1, "ask": 1.1001, "timestamp": 1})
    assert out["safety"] == {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def test_deterministic_blocked_reason_order():
    out = normalize_market_snapshot({"pair": "EURJPY", "bid": 1.1, "ask": 1.0, "timestamp": 1})
    _assert_blocked(out, REJECTION_UNSUPPORTED_PAIR)


def test_source_safety_scan_no_io_or_network():
    source = Path("automation/forex_engine/market_data_normalizer.py").read_text(encoding="utf-8").lower()
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
