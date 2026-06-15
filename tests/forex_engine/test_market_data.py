import pytest

from automation.forex_engine.config import ForexEngineConfig
from automation.forex_engine.market_data import (
    load_candles_from_csv,
    load_fixture_candles,
    load_local_candle_csv,
    summarize_candles,
    validate_candle,
    validate_candle_sequence,
)
from automation.forex_engine.models import Candle


def valid_candle(**overrides):
    data = {
        "symbol": "EURUSD",
        "timeframe": "5m",
        "timestamp": "2026-06-06T09:00:00Z",
        "open": 1.0800,
        "high": 1.0810,
        "low": 1.0790,
        "close": 1.0805,
        "volume": 1000,
        "source": "local_test_fixture",
    }
    data.update(overrides)
    return Candle(**data)


def test_csv_loader_loads_candles():
    candles = load_candles_from_csv(
        "automation/forex_engine/fixtures/EURUSD_5m_sample.csv",
        ForexEngineConfig(),
    )
    assert len(candles) == 3
    assert candles[0].symbol == "EURUSD"


def test_candle_validation_accepts_valid_candle():
    validate_candle(valid_candle(), ForexEngineConfig())


def test_candle_validation_rejects_negative_prices():
    with pytest.raises(ValueError, match="positive"):
        validate_candle(valid_candle(open=-1.0), ForexEngineConfig())


def test_candle_validation_rejects_bad_ohlc_relationship():
    with pytest.raises(ValueError, match="high"):
        validate_candle(valid_candle(high=1.0795), ForexEngineConfig())


def test_sequence_validation_rejects_unsorted_timestamps():
    candles = [
        valid_candle(timestamp="2026-06-06T09:05:00Z"),
        valid_candle(timestamp="2026-06-06T09:00:00Z"),
    ]
    with pytest.raises(ValueError, match="sorted"):
        validate_candle_sequence(candles)


def test_sequence_validation_rejects_mixed_symbols():
    candles = [valid_candle(symbol="EURUSD"), valid_candle(symbol="GBPUSD")]
    with pytest.raises(ValueError, match="one symbol"):
        validate_candle_sequence(candles)


def test_fixture_loader_loads_eurusd_sample():
    candles = load_fixture_candles("EURUSD", "5m", ForexEngineConfig())
    assert len(candles) == 3
    assert candles[0].timeframe == "5m"


def test_fixture_loader_loads_all_four_configured_symbols():
    config = ForexEngineConfig()
    loaded = {symbol: load_fixture_candles(symbol, "5m", config) for symbol in config.symbols}
    assert set(loaded) == {"EURUSD", "GBPUSD", "USDJPY", "XAUUSD"}
    assert all(len(candles) == 3 for candles in loaded.values())


def test_summary_returns_count_and_first_last_timestamps():
    candles = load_fixture_candles("EURUSD", "5m", ForexEngineConfig())
    summary = summarize_candles(candles)
    assert summary["count"] == 3
    assert summary["first_timestamp"] == "2026-06-06T09:00:00Z"
    assert summary["last_timestamp"] == "2026-06-06T09:10:00Z"


def test_no_network_api_dependency_required():
    candles = load_fixture_candles("XAUUSD", "5m", ForexEngineConfig())
    assert candles
    assert candles[0].source.endswith("automation\\forex_engine\\fixtures\\XAUUSD_5m_sample.csv") or candles[
        0
    ].source.endswith("automation/forex_engine/fixtures/XAUUSD_5m_sample.csv")


def test_local_csv_import_accepts_required_ohlc_and_optional_volume(tmp_path):
    path = tmp_path / "manual_export.csv"
    path.write_text(
        "timestamp,open,high,low,close,volume\n"
        "2026-06-06T09:00:00Z,1.0800,1.0810,1.0790,1.0805,100\n"
        "2026-06-06T09:05:00Z,1.0805,1.0820,1.0800,1.0815,110\n",
        encoding="utf-8",
    )

    candles = load_local_candle_csv(path, ForexEngineConfig())

    assert len(candles) == 2
    assert candles[0].symbol == "EURUSD"
    assert candles[0].timeframe == "5m"


def test_local_csv_import_rejects_duplicate_timestamps(tmp_path):
    path = tmp_path / "duplicates.csv"
    path.write_text(
        "timestamp,open,high,low,close\n"
        "2026-06-06T09:00:00Z,1.0800,1.0810,1.0790,1.0805\n"
        "2026-06-06T09:00:00Z,1.0805,1.0820,1.0800,1.0815\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unique"):
        load_local_candle_csv(path, ForexEngineConfig())


def test_local_csv_import_rejects_high_low_not_containing_open_close(tmp_path):
    path = tmp_path / "bad_ohlc.csv"
    path.write_text(
        "timestamp,open,high,low,close\n"
        "2026-06-06T09:00:00Z,1.0800,1.0795,1.0790,1.0805\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="high"):
        load_local_candle_csv(path, ForexEngineConfig())
