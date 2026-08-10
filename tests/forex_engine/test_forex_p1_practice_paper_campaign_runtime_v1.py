from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

import automation.forex_engine.forex_p1_practice_paper_campaign_runtime_v1 as runtime
from automation.forex_engine.forex_p1_supervised_paper_campaign_v1 import (
    CampaignHalt, CampaignWait, StaleMarketDataWait,
)
from automation.forex_engine.oanda_read_only_client import OandaReadOnlyClient

NOW = datetime(2026, 8, 10, 10, 30, tzinfo=timezone.utc)


def candles():
    result = []
    for index in range(3):
        stamp = NOW - timedelta(minutes=15 - index * 5)
        close = 1.1000 + index * 0.0007
        result.append({
            "time": stamp.isoformat().replace("+00:00", "Z"), "complete": True,
            "volume": 100 + index,
            "mid": {"o": str(close - .0002), "h": str(close + .0005),
                    "l": str(close - .0005), "c": str(close)},
        })
    return {"instrument": "EUR_USD", "granularity": "M5", "candles": result}


def pricing(price: float, stamp: datetime = NOW):
    return {"prices": [{"instrument": "EUR_USD", "time": stamp.isoformat().replace("+00:00", "Z"),
                         "bids": [{"price": str(price)}], "asks": [{"price": str(price + .0002)}]}]}


def client(prices):
    item = OandaReadOnlyClient(api_token="runtime-only", account_id="runtime-only", environment="practice")
    item.candles = lambda *_args, **_kwargs: candles()
    values = iter(prices)
    item.pricing = lambda *_args, **_kwargs: next(values)
    return item


def test_runtime_opens_then_closes_one_paper_position(monkeypatch, tmp_path):
    monkeypatch.setattr(runtime, "build_signal_state", lambda *_args, **_kwargs: {
        "status": "BUY", "signal_id": "canonical-signal", "strategy_id": "sprint-4",
        "stop_price": 1.099, "target_price": 1.102,
    })
    moments = iter([NOW, NOW + timedelta(minutes=5)])
    records = list(runtime.completed_paper_records(
        client([pricing(1.1000), pricing(1.1021, NOW + timedelta(minutes=5))]),
        cycles=2, reviewer_identity="Anthony", runtime_path=tmp_path / "active.json",
        now=lambda: next(moments), sleep=lambda _seconds: None,
    ))
    assert len([item for item in records if isinstance(item, dict)]) == 1
    assert records[0]["evidence_type"] == "paper"
    assert records[0]["realized_pl"] > 0
    assert isinstance(records[-1], CampaignHalt)
    assert not (tmp_path / "active.json").exists()


def test_no_signal_stops_without_manufacturing_trade(monkeypatch, tmp_path):
    monkeypatch.setattr(runtime, "build_signal_state", lambda *_args, **_kwargs: {"status": "NO_SIGNAL"})
    result = list(runtime.completed_paper_records(
        client([pricing(1.1), pricing(1.1)]), cycles=2, reviewer_identity="Anthony",
        runtime_path=tmp_path / "active.json", now=lambda: NOW, sleep=lambda _seconds: None,
    ))
    assert result == [CampaignWait(1, 2), CampaignWait(2, 2), CampaignHalt("OWNER_SESSION_CYCLE_LIMIT")]
    assert not (tmp_path / "active.json").exists()


def test_multiple_no_signals_can_be_followed_by_valid_paper_trade(monkeypatch, tmp_path):
    decisions = iter([
        {"status": "NO_SIGNAL"}, {"status": "NO_SIGNAL"},
        {"status": "BUY", "signal_id": "later-signal", "strategy_id": "sprint-4",
         "stop_price": 1.099, "target_price": 1.102},
        {"status": "NO_SIGNAL"},
    ])
    monkeypatch.setattr(runtime, "build_signal_state", lambda *_args, **_kwargs: next(decisions))
    moments = iter([NOW, NOW, NOW, NOW + timedelta(minutes=5)])
    prices = [pricing(1.1), pricing(1.1), pricing(1.1)] + [
        pricing(1.1021, NOW + timedelta(minutes=5))
    ]
    result = list(runtime.completed_paper_records(
        client(prices), cycles=4, reviewer_identity="Anthony",
        runtime_path=tmp_path / "active.json", now=lambda: next(moments),
        sleep=lambda _seconds: None,
    ))
    assert result[:2] == [CampaignWait(1, 4), CampaignWait(2, 4)]
    assert result[2]["evidence_type"] == "paper"
    assert result[2]["realized_pl"] > 0
    assert result[-1] == CampaignHalt("OWNER_SESSION_CYCLE_LIMIT")


def test_288_no_signal_cycles_are_bounded(monkeypatch, tmp_path):
    monkeypatch.setattr(runtime, "_capture", lambda *_args: ({"status": "NO_SIGNAL"}, {"ask": 1.1}))
    sleeps = []
    result = list(runtime.completed_paper_records(
        client([]), cycles=288, reviewer_identity="Anthony",
        runtime_path=tmp_path / "active.json", now=lambda: NOW, sleep=sleeps.append,
    ))
    assert len([item for item in result if isinstance(item, CampaignWait)]) == 288
    assert result[-1] == CampaignHalt("OWNER_SESSION_CYCLE_LIMIT")
    assert len(sleeps) == 287


@pytest.mark.parametrize(("callback", "reason"), [
    ("owner_cancelled", "OWNER_CANCELLATION"),
    ("kill_switch_active", "KILL_SWITCH_ACTIVE"),
    ("risk_halt_active", "RISK_HALT"),
])
def test_runtime_control_halts_are_immediate(tmp_path, callback, reason):
    kwargs = {callback: lambda: True}
    result = list(runtime.completed_paper_records(
        client([]), cycles=288, reviewer_identity="Anthony",
        runtime_path=tmp_path / "active.json", sleep=lambda _seconds: None, **kwargs,
    ))
    assert result == [CampaignHalt(reason)]


def test_practice_data_failure_halts_fail_closed(monkeypatch, tmp_path):
    monkeypatch.setattr(
        runtime, "_capture",
        lambda *_args: (_ for _ in ()).throw(runtime.OandaReadOnlyClientError("NETWORK_ERROR_SANITIZED")),
    )
    result = list(runtime.completed_paper_records(
        client([]), cycles=1, reviewer_identity="Anthony",
        runtime_path=tmp_path / "active.json", sleep=lambda _seconds: None,
    ))
    assert result == [CampaignHalt("PRACTICE_DATA_UNAVAILABLE")]


def test_transient_stale_waits_without_trade_or_evidence(tmp_path):
    runtime_path = tmp_path / "active.json"
    result = list(runtime.completed_paper_records(
        client([pricing(1.1)]), cycles=1, reviewer_identity="Anthony", runtime_path=runtime_path,
        now=lambda: NOW + timedelta(hours=1), sleep=lambda _seconds: None,
    ))
    assert result == [StaleMarketDataWait(1, 1, 1, 3), CampaignHalt("OWNER_SESSION_CYCLE_LIMIT")]
    assert not runtime_path.exists()


def test_three_stale_cycles_wait_and_fourth_halts(monkeypatch, tmp_path):
    monkeypatch.setattr(
        runtime, "_capture",
        lambda *_args: (_ for _ in ()).throw(ValueError("stale_market_data")),
    )
    sleeps = []
    result = list(runtime.completed_paper_records(
        client([]), cycles=5, reviewer_identity="Anthony", runtime_path=tmp_path / "active.json",
        now=lambda: NOW, sleep=sleeps.append,
    ))
    assert result[:3] == [
        StaleMarketDataWait(1, 5, 1, 3), StaleMarketDataWait(2, 5, 2, 3),
        StaleMarketDataWait(3, 5, 3, 3),
    ]
    assert result[3] == CampaignHalt("PERSISTENT_STALE_MARKET_DATA")
    assert sleeps == [runtime.POLL_INTERVAL_SECONDS] * 3


def test_fresh_capture_resets_stale_streak(monkeypatch, tmp_path):
    runtime_path = tmp_path / "active.json"
    outcomes = iter([
        ValueError("stale_market_data"),
        ({"status": "NO_SIGNAL"}, {"ask": 1.1002}),
        ValueError("stale_market_data"),
    ])
    def capture(*_args):
        outcome = next(outcomes)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome
    monkeypatch.setattr(runtime, "_capture", capture)
    result = list(runtime.completed_paper_records(
        client([]), cycles=3, reviewer_identity="Anthony", runtime_path=runtime_path,
        now=lambda: NOW, sleep=lambda _seconds: None,
    ))
    assert result[0] == StaleMarketDataWait(1, 3, 1, 3)
    assert result[1] == CampaignWait(2, 3)
    assert result[2] == StaleMarketDataWait(3, 3, 1, 3)
    assert not runtime_path.exists()


def test_stale_cycle_cannot_change_active_paper_position(monkeypatch, tmp_path):
    runtime_path = tmp_path / "active.json"
    original = b'{"active": "paper-position"}\n'
    runtime_path.write_bytes(original)
    monkeypatch.setattr(
        runtime, "_capture",
        lambda *_args: (_ for _ in ()).throw(ValueError("stale_market_data")),
    )
    result = list(runtime.completed_paper_records(
        client([]), cycles=1, reviewer_identity="Anthony", runtime_path=runtime_path,
        now=lambda: NOW, sleep=lambda _seconds: None,
    ))
    assert isinstance(result[0], StaleMarketDataWait)
    assert runtime_path.read_bytes() == original


def test_invalid_non_stale_market_data_still_halts_fail_closed(monkeypatch, tmp_path):
    monkeypatch.setattr(
        runtime, "_capture",
        lambda *_args: (_ for _ in ()).throw(ValueError("invalid_market_data")),
    )
    result = list(runtime.completed_paper_records(
        client([]), cycles=1, reviewer_identity="Anthony", runtime_path=tmp_path / "active.json", sleep=lambda _seconds: None,
    ))
    assert result == [CampaignHalt("INVALID_MARKET_DATA")]


def test_runtime_is_practice_get_only_and_safety_flags_false():
    state = runtime.runtime_safety_state()
    assert state["environment"] == "PRACTICE"
    assert state["http_methods"] == ["GET"]
    assert state["maximum_open_paper_positions"] == 1
    assert all(value is False for key, value in state.items() if key.endswith("performed") or key.endswith("persisted"))


def test_live_transport_and_unbounded_cycles_are_rejected(tmp_path):
    live = OandaReadOnlyClient(api_token="x", account_id="x", environment="live")
    with pytest.raises(ValueError, match="practice_environment"):
        list(runtime.completed_paper_records(live, cycles=1, reviewer_identity="Anthony", runtime_path=tmp_path/"x", sleep=lambda _: None))
    with pytest.raises(ValueError, match="positive_cycle"):
        list(runtime.completed_paper_records(client([]), cycles=0, reviewer_identity="Anthony", runtime_path=tmp_path/"x", sleep=lambda _: None))
