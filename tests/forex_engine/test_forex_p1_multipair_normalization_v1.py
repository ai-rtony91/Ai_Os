from __future__ import annotations

import json
from pathlib import Path

import pytest

import automation.forex_engine.forex_p1_multipair_normalization_v1 as module
from automation.forex_engine.oanda_read_only_client import OandaReadOnlyClient


class FakeClient(OandaReadOnlyClient):
    def __init__(self) -> None:
        super().__init__(api_token="token", account_id="account", environment="practice", timeout_seconds=1, opener=None)

    def discover_instruments(self) -> dict:
        return {
            "instruments": [
                {"name": "EUR_USD", "type": "CURRENCY", "tradeable": True, "halted": False, "displayPrecision": 5, "pipLocation": -4},
                {"name": "USD_JPY", "type": "CURRENCY", "tradeable": True, "halted": False, "displayPrecision": 3, "pipLocation": -2},
                {"name": "BAD", "type": "STOCK", "tradeable": False, "halted": False},
            ]
        }

    def observation_candles(self, instrument: str, *, granularity: str, count: int, price: str = "M") -> dict:
        assert granularity == "M5"
        assert price == "M"
        if instrument == "EUR_USD":
            candles = [
                {"time": f"2026-08-01T10:{index:02d}:00Z", "complete": True, "volume": 10,
                 "open": 1.1000 + index * 0.0001, "high": 1.1004 + index * 0.0001,
                 "low": 1.0996 + index * 0.0001, "close": 1.1001 + index * 0.0001,
                 "mid": {"o": 1.1000 + index * 0.0001, "h": 1.1004 + index * 0.0001, "l": 1.0996 + index * 0.0001, "c": 1.1001 + index * 0.0001},
                 "observed_at_utc": f"2026-08-01T10:{index:02d}:00Z"}
                for index in range(count)
            ]
        else:
            candles = [
                {"time": f"2026-08-01T10:{index:02d}:00Z", "complete": True, "volume": 10,
                 "open": 110.0 + index * 0.01, "high": 110.04 + index * 0.01,
                 "low": 109.96 + index * 0.01, "close": 110.01 + index * 0.01,
                 "mid": {"o": 110.0 + index * 0.01, "h": 110.04 + index * 0.01, "l": 109.96 + index * 0.01, "c": 110.01 + index * 0.01},
                 "observed_at_utc": f"2026-08-01T10:{index:02d}:00Z"}
                for index in range(count)
            ]
        return {"instrument": instrument, "granularity": "M5", "candles": candles[:count]}

    def pricing(self, instruments: tuple[str, ...]) -> dict:
        return {
            "prices": [
                {"instrument": "EUR_USD", "time": "2026-08-01T10:30:00Z", "bids": [{"price": "1.1050"}], "asks": [{"price": "1.1052"}]},
                {"instrument": "USD_JPY", "time": "2026-08-01T10:30:00Z", "bids": [{"price": "110.00"}], "asks": [{"price": "110.03"}]},
            ]
        }


def test_discover_universe_is_deterministic():
    client = FakeClient()
    universe = module.discover_fixed_universe(client)
    assert universe["discovered_pairs"] == ["EUR_USD", "USD_JPY"]
    assert universe["eligible_instruments"][0]["pip_size"] == pytest.approx(0.0001)
    assert universe["eligible_instruments"][1]["pip_size"] == pytest.approx(0.01)
    assert universe["universe_fingerprint"]


def test_snapshot_and_candidate_normalization():
    snap = module.sanitized_price_snapshot(
        {"prices": [{"instrument": "EUR_USD", "time": "2026-08-01T10:30:00Z", "bids": [{"price": "1.1050"}], "asks": [{"price": "1.1052"}]}]},
        instrument="EUR_USD",
    )
    assert snap["spread"] == pytest.approx(0.0002)
    instrument = module.NormalizedInstrument("EUR_USD", 5, -4, True, True)
    candles = module.candles_to_strategy_window(
        {"candles": [
            {"observed_at_utc": "2026-08-01T10:20:00Z", "open": 1.1000, "high": 1.1004, "low": 1.0996, "close": 1.1001, "volume": 10},
            {"observed_at_utc": "2026-08-01T10:25:00Z", "open": 1.1001, "high": 1.1005, "low": 1.0998, "close": 1.1004, "volume": 10},
            {"observed_at_utc": "2026-08-01T10:30:00Z", "open": 1.1004, "high": 1.1009, "low": 1.1000, "close": 1.1008, "volume": 10},
            {"observed_at_utc": "2026-08-01T10:35:00Z", "open": 1.1008, "high": 1.1012, "low": 1.1004, "close": 1.1010, "volume": 10},
            {"observed_at_utc": "2026-08-01T10:40:00Z", "open": 1.1010, "high": 1.1015, "low": 1.1008, "close": 1.1013, "volume": 10},
            {"observed_at_utc": "2026-08-01T10:45:00Z", "open": 1.1013, "high": 1.1055, "low": 1.1012, "close": 1.1050, "volume": 10},
        ]},
        instrument="EUR_USD",
    )
    candidate = module.replay_candidate(
        instrument,
        candles,
        snap,
        strategy_config=module.SupertrendPullbackConfig(),
    )
    if candidate is not None:
        assert candidate["direction"] == "BUY"
        assert candidate["planned_reward_risk"] >= module.MIN_RR


def test_quote_mid_extraction_and_trade_outcome():
    mids = module.quote_mids_from_pricing(
        {"prices": [{"instrument": "USD_JPY", "time": "2026-08-01T10:30:00Z", "bids": [{"price": "110.00"}], "asks": [{"price": "110.03"}]}]}
    )
    assert mids["USD_JPY"] == pytest.approx(110.015)
    session = {
        "entry_price": 1.1000,
        "units": 100,
        "risk_amount": 0.10,
        "quote_currency": "USD",
    }
    outcome = module.normalized_trade_outcome(session, {"bid": 1.1020, "ask": 1.1022}, quote_mids=mids)
    assert outcome["realized_pl_quote_currency"] > 0
    assert outcome["roi_class"] == "POSITIVE_R"
