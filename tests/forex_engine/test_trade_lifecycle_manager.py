"""Tests for automation/forex_engine/trade_lifecycle_manager."""

from __future__ import annotations

from pathlib import Path

from automation.forex_engine.trade_lifecycle_manager import (
    TRADE_LIFECYCLE_ALLOWED,
    TRADE_LIFECYCLE_BLOCKED,
    TRADE_LIFECYCLE_MODE,
    process_trade_update,
)


def _base_trade() -> dict:
    return {
        "trade_id": "t1",
        "pair": "eurusd",
        "direction": "buy",
        "entry_type": "market",
        "entry_price": 1.0,
        "stop_loss": 0.9,
        "take_profit": 1.1,
        "units": 1000.0,
        "paper_only": True,
        "status": "active",
        "opened_timestamp": 1_700_000_000.0,
        "lifecycle_history": [],
        "safety": {
            "paper_only": True,
            "broker": False,
            "live_trading": False,
            "credentials": False,
            "real_orders": False,
            "network_access": False,
        },
    }


def _result_allowed(result: dict) -> bool:
    return result.get("allowed") is True and result.get("decision") == TRADE_LIFECYCLE_ALLOWED


def _result_blocked(result: dict, reason: str) -> bool:
    return result.get("allowed") is False and result.get("decision") == TRADE_LIFECYCLE_BLOCKED and result.get("blocked_reason") == reason


def test_import_and_defaults():
    assert TRADE_LIFECYCLE_MODE == "PAPER_ONLY"
    assert TRADE_LIFECYCLE_ALLOWED == "allowed"
    assert TRADE_LIFECYCLE_BLOCKED == "blocked"


def test_no_close_active_update_keeps_position_open():
    trade = _base_trade()
    out = process_trade_update(trade, price_update={"bid": 1.01, "ask": 1.02}, timestamp=1_700_000_100)
    assert _result_allowed(out)
    assert out["closed"] is False
    assert out["status"] == "active"
    assert out["close_reason"] == "none"
    assert out["realized_pnl"] == 0.0


def test_active_buy_closes_on_stop_loss():
    trade = _base_trade()
    out = process_trade_update(trade, price_update={"bid": 0.89, "ask": 0.9}, timestamp=1_700_000_100)
    assert _result_allowed(out)
    assert out["closed"] is True
    assert out["status"] == "closed"
    assert out["close_reason"] == "stop_loss"
    assert out["realized_pnl"] == -110.0


def test_active_buy_closes_on_take_profit():
    trade = _base_trade()
    out = process_trade_update(trade, price_update={"bid": 1.11, "ask": 1.12}, timestamp=1_700_000_100)
    assert _result_allowed(out)
    assert out["closed"] is True
    assert out["status"] == "closed"
    assert out["close_reason"] == "take_profit"
    assert out["realized_pnl"] == 110.0


def test_active_sell_closes_on_stop_loss():
    trade = _base_trade()
    trade["direction"] = "sell"
    out = process_trade_update(trade, price_update={"bid": 1.2, "ask": 1.21}, timestamp=1_700_000_100)
    assert _result_allowed(out)
    assert out["closed"] is True
    assert out["status"] == "closed"
    assert out["close_reason"] == "stop_loss"
    assert out["realized_pnl"] == 110.0


def test_active_sell_closes_on_take_profit():
    trade = _base_trade()
    trade["direction"] = "sell"
    out = process_trade_update(trade, price_update={"bid": 0.79, "ask": 0.8}, timestamp=1_700_000_100)
    assert _result_allowed(out)
    assert out["closed"] is True
    assert out["status"] == "closed"
    assert out["close_reason"] == "take_profit"
    assert out["realized_pnl"] == 210.0


def test_manual_close_calculates_pnl():
    trade = _base_trade()
    out = process_trade_update(trade, manual_close_price=1.05, timestamp=1_700_000_100)
    assert _result_allowed(out)
    assert out["closed"] is True
    assert out["close_reason"] == "manual_close"
    assert out["realized_pnl"] == 50.0


def test_expiry_close_uses_current_price():
    trade = _base_trade()
    out = process_trade_update(trade, price_update={"bid": 1.08, "ask": 1.09}, timestamp=1_700_000_200, expire_at=1_700_000_150)
    assert _result_allowed(out)
    assert out["closed"] is True
    assert out["close_reason"] == "expiry"
    assert out["realized_pnl"] == 80.0


def test_kill_switch_close_uses_current_price():
    trade = _base_trade()
    out = process_trade_update(trade, price_update={"bid": 1.07, "ask": 1.08}, timestamp=1_700_000_120, kill_switch=True)
    assert _result_allowed(out)
    assert out["closed"] is True
    assert out["close_reason"] == "kill_switch"
    assert out["status"] == "killed"


def test_inactive_trade_blocked():
    trade = _base_trade()
    trade["status"] = "closed"
    out = process_trade_update(trade, price_update={"bid": 1.07, "ask": 1.08}, timestamp=1_700_000_120)
    assert _result_blocked(out, "trade_not_active")


def test_trade_paper_only_false_blocked():
    trade = _base_trade()
    trade["paper_only"] = False
    out = process_trade_update(trade, price_update={"bid": 1.05, "ask": 1.06}, timestamp=1_700_000_120)
    assert _result_blocked(out, "non_paper_mode")


def test_live_or_demo_or_broker_mode_blocked():
    trade = _base_trade()
    trade["mode"] = "live"
    out = process_trade_update(trade, price_update={"bid": 1.05, "ask": 1.06}, timestamp=1_700_000_120)
    assert _result_blocked(out, "non_paper_mode")

    trade["mode"] = "demo"
    out = process_trade_update(trade, price_update={"bid": 1.05, "ask": 1.06}, timestamp=1_700_000_121)
    assert _result_blocked(out, "non_paper_mode")

    trade["mode"] = "broker"
    out = process_trade_update(trade, price_update={"bid": 1.05, "ask": 1.06}, timestamp=1_700_000_122)
    assert _result_blocked(out, "non_paper_mode")


def test_missing_required_fields_blocked():
    trade = _base_trade()
    del trade["pair"]
    out = process_trade_update(trade, price_update={"bid": 1.05, "ask": 1.06}, timestamp=1_700_000_120)
    assert _result_blocked(out, "missing_pair")

    trade = _base_trade()
    del trade["direction"]
    out = process_trade_update(trade, price_update={"bid": 1.05, "ask": 1.06}, timestamp=1_700_000_120)
    assert _result_blocked(out, "missing_direction")


def test_invalid_evidence_path_blocked():
    trade = _base_trade()
    out = process_trade_update(
        trade,
        price_update={"bid": 1.08, "ask": 1.09},
        timestamp=1_700_000_120,
        evidence_path="/tmp/evidence.txt",
    )
    assert _result_blocked(out, "evidence_path_invalid")


def test_deterministic_pnl_is_mathematically_expected():
    trade = _base_trade()
    out = process_trade_update(trade, manual_close_price=1.123456, timestamp=1_700_000_200)
    assert _result_allowed(out)
    assert abs(out["realized_pnl"] - 123.456) < 0.0001


def test_safety_and_evidence_only():
    trade = _base_trade()
    out = process_trade_update(trade, manual_close_price=1.05, timestamp=1_700_000_150, metadata={"note": "unit-test"})
    assert out["evidence"] is not None
    assert isinstance(out["evidence"], dict) or isinstance(out["evidence"], list) or out["evidence"]
    assert out["safety"] == {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def test_lifecycle_transition_present():
    trade = _base_trade()
    out = process_trade_update(trade, manual_close_price=1.05, timestamp=1_700_000_150)
    assert _result_allowed(out)
    assert out["trade"]["status"] == "closed"
    history = out["trade"].get("lifecycle_history") or []
    assert history, "expected lifecycle history to include transition events"


def test_source_safety_scan_no_network_or_file_io():
    source = Path("automation/forex_engine/trade_lifecycle_manager.py").read_text(encoding="utf-8").lower()
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
