from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone

import pytest

import automation.forex_engine.forex_p1_practice_paper_campaign_runtime_v1 as runtime
from automation.forex_engine.forex_p1_supervised_paper_campaign_v1 import CampaignHalt, CampaignWait
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
    moments = iter([
        NOW, NOW, NOW + timedelta(minutes=5), NOW + timedelta(minutes=5),
    ])
    records = list(runtime.completed_paper_records(
        client([pricing(1.1000), pricing(1.1021, NOW + timedelta(minutes=5))]),
        cycles=2, reviewer_identity="Anthony", runtime_path=tmp_path / "active.json",
        now=lambda: next(moments), sleep=lambda _seconds: None,
    ))
    assert len([item for item in records if isinstance(item, dict)]) == 1
    assert records[0]["evidence_type"] == "paper"
    assert records[0]["realized_pl"] > 0
    assert isinstance(records[-1], CampaignHalt)
    closed = json.loads((tmp_path / "active.json").read_text(encoding="utf-8"))
    assert closed["status"] == "CLOSED"
    assert closed["closed_reason"] == "paper_target"


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
    moments = iter([
        NOW, NOW, NOW, NOW, NOW, NOW,
        NOW + timedelta(minutes=5), NOW + timedelta(minutes=5),
    ])
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
    def no_signal_capture(*_args, **kwargs):
        assert callable(kwargs.get("pricing_now"))
        return {"status": "NO_SIGNAL"}, {"ask": 1.1}

    monkeypatch.setattr(runtime, "_capture", no_signal_capture)
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
    def unavailable_capture(*_args, **kwargs):
        assert callable(kwargs.get("pricing_now"))
        raise runtime.OandaReadOnlyClientError("NETWORK_ERROR_SANITIZED")

    monkeypatch.setattr(runtime, "_capture", unavailable_capture)
    result = list(runtime.completed_paper_records(
        client([]), cycles=1, reviewer_identity="Anthony",
        runtime_path=tmp_path / "active.json", now=lambda: NOW,
        sleep=lambda _seconds: None,
    ))
    waits = [item for item in result if isinstance(item, CampaignWait)]
    assert waits == [CampaignWait(
        1,
        1,
        action=runtime.WAIT_FOR_DATA,
        observed_at_utc=runtime._stamp(NOW),
        rejection_reasons=("data_unavailable",),
    )]
    assert result[-1] == CampaignHalt("OWNER_SESSION_CYCLE_LIMIT")
    assert not any(isinstance(item, dict) for item in result)


def test_stale_or_invalid_data_halts_fail_closed(tmp_path):
    stale_now = NOW + timedelta(hours=1)
    result = list(runtime.completed_paper_records(
        client([pricing(1.1)]), cycles=1, reviewer_identity="Anthony",
        runtime_path=tmp_path / "active.json", now=lambda: stale_now, sleep=lambda _seconds: None,
    ))
    assert result == [CampaignHalt("STALE_MARKET_DATA")]


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


def test_resolve_signal_source_preserves_default_source():
    assert runtime.resolve_signal_source() == runtime.SPRINT_4_SIGNAL_SOURCE


def test_resolve_signal_source_requires_supertrend_gate_for_supertrend_source():
    with pytest.raises(ValueError, match="supertrend_paper_demo_only_confirmation_required"):
        runtime.resolve_signal_source(runtime.SUPERTREND_SIGNAL_SOURCE)


def test_resolve_signal_source_accepts_supertrend_with_demo_gate():
    assert runtime.resolve_signal_source(
        runtime.SUPERTREND_SIGNAL_SOURCE,
        supertrend_paper_demo_only=True,
    ) == runtime.SUPERTREND_SIGNAL_SOURCE


def test_resolve_signal_source_rejects_unknown_source():
    with pytest.raises(ValueError, match="unsupported_signal_source"):
        runtime.resolve_signal_source("invalid")


def test_supertrend_lock_acquisition_and_release_in_tmp_directory(tmp_path):
    lock_path = tmp_path / "isolated.supertrend.paper.runtime.lock"
    first = NOW
    assert runtime._read_lock_record(lock_path) is None
    assert runtime._acquire_supertrend_lock(lock_path, now=first) is True
    assert lock_path.exists()
    try:
        record = runtime._read_lock_record(lock_path)
        assert record is not None
        assert record["status"] == "ACTIVE"
        assert record["pid"] == os.getpid()
    finally:
        runtime._release_supertrend_lock(lock_path)
    assert not lock_path.exists()


def test_supertrend_lock_touches_heartbeat_for_owned_lock(tmp_path):
    lock_path = tmp_path / "isolated.supertrend.paper.runtime.lock"
    assert runtime._acquire_supertrend_lock(lock_path, now=NOW) is True
    try:
        runtime._touch_supertrend_lock(lock_path, now=NOW + timedelta(minutes=1))
        record = runtime._read_lock_record(lock_path)
        assert record is not None
        assert record["heartbeat_at_utc"] == runtime._stamp(NOW + timedelta(minutes=1))
    finally:
        runtime._release_supertrend_lock(lock_path)


def test_supertrend_lock_release_only_removes_owned_lock(tmp_path):
    lock_path = tmp_path / "isolated.supertrend.paper.runtime.lock"
    try:
        runtime._write_lock_record(
            lock_path,
            runtime._supertrend_lock_record(
                heartbeat_utc=runtime._stamp(NOW),
                pid=999,
                owner="non_owner_runtime",
            ),
        )
        runtime._release_supertrend_lock(lock_path)
        assert lock_path.exists()
    finally:
        lock_path.unlink(missing_ok=True)


def test_supertrend_lock_double_acquire_returns_false_for_active_lock(tmp_path):
    lock_path = tmp_path / "isolated.supertrend.paper.runtime.lock"
    assert runtime._acquire_supertrend_lock(lock_path, now=NOW) is True
    try:
        original_record = runtime._read_lock_record(lock_path)
        assert original_record is not None
        assert runtime._acquire_supertrend_lock(lock_path, now=NOW) is False
        assert runtime._read_lock_record(lock_path) == original_record
    finally:
        runtime._release_supertrend_lock(lock_path)
