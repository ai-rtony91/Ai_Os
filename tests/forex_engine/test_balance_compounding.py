"""Tests for automation/forex_engine/balance_compounding.py."""

from __future__ import annotations

from pathlib import Path

from automation.forex_engine.balance_compounding import (
    BALANCE_COMPOUNDING_ALLOWED,
    BALANCE_COMPOUNDING_BLOCKED,
    BALANCE_COMPOUNDING_MODE,
    REJECTION_REASON_EVIDENCE_PATH_INVALID,
    REJECTION_REASON_INVALID_BALANCE,
    REJECTION_REASON_INVALID_COMPOUNDING_CAP,
    REJECTION_REASON_INVALID_CLOSED_TRADE,
    REJECTION_REASON_INVALID_REALIZED_PNL,
    REJECTION_REASON_LIVE_TRADING_BLOCKED,
    REJECTION_REASON_MISSING_BALANCE,
    REJECTION_REASON_MISSING_REALIZED_PNL,
    REJECTION_REASON_MARTINGALE_BLOCKED,
    REJECTION_REASON_NON_PAPER_MODE,
    REJECTION_REASON_RECOVERY_SIZING_BLOCKED,
    REJECTION_REASON_DRAWDOWN_LIMIT_HIT,
    apply_closed_trade_to_balance,
    calculate_risk_base,
)


def _base_account() -> dict:
    return {
        "starting_balance": 10000.0,
        "current_balance": 10000.0,
        "cash_balance": 10000.0,
        "equity": 10000.0,
        "realized_pnl": 0.0,
        "daily_loss_used": 0.0,
        "trade_count": 0,
        "session_count": 0,
        "peak_balance": 10000.0,
        "drawdown_percent": 0.0,
        "compounding_enabled": True,
    }


def _base_closed_trade() -> dict:
    return {
        "trade_id": "tr-1",
        "pair": "EURUSD",
        "direction": "buy",
        "closed": True,
        "paper_only": True,
        "mode": BALANCE_COMPOUNDING_MODE,
        "close_reason": "take_profit",
        "realized_pnl": 250.0,
    }


def _assert_allowed(out: dict) -> None:
    assert out["allowed"] is True
    assert out["decision"] == BALANCE_COMPOUNDING_ALLOWED


def _assert_blocked(out: dict, reason: str) -> None:
    assert out["allowed"] is False
    assert out["decision"] == BALANCE_COMPOUNDING_BLOCKED
    assert out["blocked_reason"] == reason


def test_import_and_constants():
    assert BALANCE_COMPOUNDING_MODE == "PAPER_ONLY"
    assert BALANCE_COMPOUNDING_ALLOWED == "allowed"
    assert BALANCE_COMPOUNDING_BLOCKED == "blocked"


def test_valid_winning_closed_trade_increases_balance():
    out = apply_closed_trade_to_balance(_base_account(), {**_base_closed_trade(), "realized_pnl": 250.0})
    _assert_allowed(out)
    assert out["current_balance_before"] == 10000.0
    assert out["current_balance_after"] == 10250.0
    assert out["realized_pnl_total"] == 250.0
    assert out["peak_balance"] == 10250.0


def test_valid_losing_closed_trade_decreases_balance_and_tracks_daily_loss():
    out = apply_closed_trade_to_balance(_base_account(), {**_base_closed_trade(), "realized_pnl": -300.0})
    _assert_allowed(out)
    assert out["current_balance_after"] == 9700.0
    assert out["daily_loss_used"] == 300.0


def test_realized_pnl_total_updates_and_drawdown_calculated():
    account = _base_account()
    account["peak_balance"] = 11000.0
    out = apply_closed_trade_to_balance(account, {**_base_closed_trade(), "realized_pnl": -1000.0})
    _assert_allowed(out)
    assert out["realized_pnl_total"] == -1000.0
    assert out["drawdown"] == 1000.0
    assert out["drawdown_percent"] == 9.09090909


def test_compounding_disabled_caps_risk_base_at_starting_balance():
    out = calculate_risk_base(_base_account(), {"compounding_enabled": False})
    _assert_allowed(out)
    assert out["compounding_enabled"] is False
    assert out["risk_base"] == 10000.0


def test_compounding_enabled_allows_growth_within_cap():
    account = _base_account()
    account["current_balance"] = 10800.0
    out = calculate_risk_base(account, {"compounding_enabled": True, "compounding_cap_percent": 10.0})
    _assert_allowed(out)
    assert out["risk_base"] == 10800.0


def test_compounding_cap_blocks_excess_risk_base():
    account = _base_account()
    account["current_balance"] = 13000.0
    out = calculate_risk_base(account, {"compounding_enabled": True, "compounding_cap_percent": 10.0})
    _assert_blocked(out, REJECTION_REASON_INVALID_COMPOUNDING_CAP)


def test_profit_lock_and_available_compound_profit():
    account = _base_account()
    account["current_balance"] = 11000.0
    out = apply_closed_trade_to_balance(account, {**_base_closed_trade(), "realized_pnl": 1000.0})
    _assert_allowed(out)
    assert out["protected_profit"] == 2000.0
    assert out["available_compound_profit"] == 2000.0


def test_drawdown_reduces_risk_multiplier():
    account = _base_account()
    account["peak_balance"] = 12000.0
    account["current_balance"] = 9000.0
    out = calculate_risk_base(account, {"drawdown_reduce_threshold_percent": 20.0})
    _assert_allowed(out)
    assert out["recommended_risk_multiplier"] < 1.0


def test_loss_does_not_increase_risk_multiplier():
    account = _base_account()
    account["last_trade_realized_pnl"] = -100.0
    out = calculate_risk_base(account, {"recovery_risk_multiplier": 1.0})
    _assert_allowed(out)


def test_martingale_recovery_block_after_loss():
    account = _base_account()
    account["last_trade_realized_pnl"] = -100.0
    out = calculate_risk_base(
        account,
        {"recovery_risk_multiplier": 1.5, "max_recovery_multiplier_after_loss": 1.0},
    )
    _assert_blocked(out, REJECTION_REASON_RECOVERY_SIZING_BLOCKED)


def test_missing_balance_blocks():
    out = apply_closed_trade_to_balance({}, _base_closed_trade())
    _assert_blocked(out, REJECTION_REASON_MISSING_BALANCE)


def test_negative_balance_blocks():
    out = apply_closed_trade_to_balance(
        {**_base_account(), "current_balance": -1000.0},
        _base_closed_trade(),
    )
    _assert_blocked(out, REJECTION_REASON_INVALID_BALANCE)


def test_missing_realized_pnl_blocks():
    trade = _base_closed_trade()
    trade.pop("realized_pnl")
    out = apply_closed_trade_to_balance(_base_account(), trade)
    _assert_blocked(out, REJECTION_REASON_MISSING_REALIZED_PNL)


def test_invalid_realized_pnl_blocks():
    out = apply_closed_trade_to_balance(_base_account(), {**_base_closed_trade(), "realized_pnl": "bad"})
    _assert_blocked(out, REJECTION_REASON_INVALID_REALIZED_PNL)


def test_not_closed_trade_blocks():
    out = apply_closed_trade_to_balance(_base_account(), {**_base_closed_trade(), "closed": False})
    _assert_blocked(out, REJECTION_REASON_INVALID_CLOSED_TRADE)


def test_closed_trade_paper_only_false_blocks():
    out = apply_closed_trade_to_balance(_base_account(), {**_base_closed_trade(), "paper_only": False})
    _assert_blocked(out, REJECTION_REASON_NON_PAPER_MODE)


def test_live_demo_broker_mode_blocks():
    out = apply_closed_trade_to_balance(_base_account(), {**_base_closed_trade(), "mode": "live"})
    _assert_blocked(out, REJECTION_REASON_LIVE_TRADING_BLOCKED)
    out = apply_closed_trade_to_balance(_base_account(), {**_base_closed_trade(), "mode": "demo"})
    _assert_blocked(out, REJECTION_REASON_NON_PAPER_MODE)
    out = apply_closed_trade_to_balance(_base_account(), {**_base_closed_trade(), "mode": "broker"})
    _assert_blocked(out, REJECTION_REASON_NON_PAPER_MODE)


def test_invalid_evidence_path_blocks():
    out = apply_closed_trade_to_balance(
        _base_account(),
        _base_closed_trade(),
        evidence_path="/tmp/closed.json",
    )
    _assert_blocked(out, REJECTION_REASON_EVIDENCE_PATH_INVALID)


def test_drawdown_limit_hit_blocks():
    out = apply_closed_trade_to_balance(_base_account(), {**_base_closed_trade(), "realized_pnl": -10000.0}, limits={"max_drawdown_percent": 10.0})
    _assert_blocked(out, REJECTION_REASON_DRAWDOWN_LIMIT_HIT)


def test_safety_and_evidence_inline():
    out = apply_closed_trade_to_balance(_base_account(), _base_closed_trade())
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


def test_calculate_risk_base_standalone_matches_formula():
    out = calculate_risk_base(_base_account(), {"compounding_cap_percent": 10.0})
    _assert_allowed(out)
    assert out["risk_base"] == 10000.0


def test_multiple_blocked_reasons_deterministic():
    out = apply_closed_trade_to_balance(
        {**_base_account(), "daily_loss_used": 0},
        {**_base_closed_trade(), "realized_pnl": "bad"},
    )
    _assert_blocked(out, REJECTION_REASON_INVALID_REALIZED_PNL)


def test_source_safety_scan_no_io_or_network():
    source = Path("automation/forex_engine/balance_compounding.py").read_text(encoding="utf-8").lower()
    for blocked in [
        "import subprocess",
        "from subprocess",
        "import requests",
        "from requests",
        "import socket",
        "from socket",
        "import urllib",
        "from urllib",
        "open(",
        ".write_text",
        ".write_bytes",
        "import pathlib",
        "from pathlib",
        "os.system",
        "broker sdk",
        "os.getenv",
        "os.environ",
        "getenv(",
        "environ[",
        "api_key",
        "access_token",
        "refresh_token",
        "private_key",
        "password",
        "bearer ",
    ]:
        assert blocked not in source
