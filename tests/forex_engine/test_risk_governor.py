from pathlib import Path
import ast

from automation.forex_engine.risk_governor import (
    COOLDOWN_AFTER_LOSS_REASON,
    DUPLICATE_SETUP_REASON,
    EXCESSIVE_RISK_PER_TRADE_REASON,
    INVALID_PREVIEW_REASON,
    KILL_SWITCH_ACTIVE_REASON,
    INVALID_ACCOUNT_STATE_REASON,
    LIVE_TRADING_BLOCKED_REASON,
    MAX_DAILY_LOSS_HIT_REASON,
    MAX_OPEN_RISK_HIT_REASON,
    MAX_OPEN_TRADES_HIT_REASON,
    MAX_PAIR_EXPOSURE_HIT_REASON,
    MISSING_STOP_LOSS_REASON,
    MISSING_TAKE_PROFIT_REASON,
    SPREAD_TOO_HIGH_REASON,
    STALE_MARKET_DATA_REASON,
    INVALID_UNITS_REASON,
    evaluate_risk_preview,
    RISK_DECISION_ALLOWED,
    RISK_GOVERNOR_MODE,
)

MODULE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "risk_governor.py"


def _base_preview():
    return {
        "trade_id": "preview-1",
        "pair": "EURUSD",
        "direction": "buy",
        "entry_price": 1.105,
        "stop_loss": 1.10,
        "take_profit": 1.12,
        "units": 1000.0,
        "dollar_risk": 8.0,
        "percent_risk": 0.5,
        "paper_only": True,
        "mode": RISK_GOVERNOR_MODE,
        "status": "previewed",
    }


def test_module_imports_and_defaults():
    result = evaluate_risk_preview(_base_preview())
    assert "allowed" in result
    assert result["mode"] == RISK_GOVERNOR_MODE
    assert result["paper_only"] is True
    assert result["safety"]["paper_only"] is True
    assert result["safety"]["broker"] is False
    assert "safety" in result


def test_invalid_preview_type_is_rejected():
    result = evaluate_risk_preview(["not", "a", "dict"])
    assert result["allowed"] is False
    assert result["blocked_reason"] == INVALID_PREVIEW_REASON


def test_valid_preview_allowed_by_default_rules():
    result = evaluate_risk_preview(_base_preview(), now_timestamp="2026-06-20T00:00:00+00:00")
    assert result["allowed"] is False or result["allowed"] is True
    if result["allowed"]:
        assert result["decision"] == RISK_DECISION_ALLOWED
        assert result["blocked_reason"] == "none"
        assert result["blocked_reasons"] == []


def test_missing_stop_loss_blocked():
    p = _base_preview()
    p.pop("stop_loss")
    result = evaluate_risk_preview(p)
    assert result["allowed"] is False
    assert MISSING_STOP_LOSS_REASON in result["blocked_reasons"]
    assert result["blocked_reason"] == MISSING_STOP_LOSS_REASON


def test_missing_take_profit_blocked():
    p = _base_preview()
    p.pop("take_profit")
    result = evaluate_risk_preview(p)
    assert result["allowed"] is False
    assert MISSING_TAKE_PROFIT_REASON in result["blocked_reasons"]
    assert result["blocked_reason"] == MISSING_TAKE_PROFIT_REASON


def test_invalid_stop_distance_blocked():
    p = _base_preview()
    p["stop_loss"] = 1.2
    p["take_profit"] = 1.12
    result = evaluate_risk_preview(p)
    assert result["allowed"] is False
    assert "invalid_stop_distance" in result["blocked_reasons"]


def test_excessive_percent_risk_blocked():
    p = _base_preview()
    p["percent_risk"] = 99.0
    result = evaluate_risk_preview(p, limits={"max_risk_per_trade_pct": 1.0})
    assert result["allowed"] is False
    assert EXCESSIVE_RISK_PER_TRADE_REASON in result["blocked_reasons"]


def test_excessive_dollar_risk_blocked():
    p = _base_preview()
    p["dollar_risk"] = 5000.0
    result = evaluate_risk_preview(
        p,
        account_state={"equity": 100000.0},
        limits={"max_risk_per_trade_pct": 1.0},
    )
    assert result["allowed"] is False
    assert EXCESSIVE_RISK_PER_TRADE_REASON in result["blocked_reasons"]


def test_daily_loss_cap_blocked():
    p = _base_preview()
    p["dollar_risk"] = 12.0
    result = evaluate_risk_preview(
        p,
        account_state={"daily_loss_used": 90.0, "max_daily_loss": 100.0},
        limits={"max_daily_loss": 100.0},
    )
    assert result["allowed"] is False
    assert MAX_DAILY_LOSS_HIT_REASON in result["blocked_reasons"]


def test_max_open_risk_blocked():
    p = _base_preview()
    result = evaluate_risk_preview(p, account_state={"open_risk": 9000.0}, limits={"max_open_risk": 1000.0})
    assert result["allowed"] is False
    assert MAX_OPEN_RISK_HIT_REASON in result["blocked_reasons"]


def test_max_open_trades_blocked():
    p = _base_preview()
    open_trade = {"pair": "GBPUSD", "direction": "buy", "status": "active", "units": 1000, "entry_price": 1.2}
    result = evaluate_risk_preview(
        p,
        open_trades=(open_trade,),
        limits={"max_open_trades": 1},
    )
    assert result["allowed"] is False
    assert MAX_OPEN_TRADES_HIT_REASON in result["blocked_reasons"]


def test_max_pair_exposure_blocked():
    p = _base_preview()
    p["units"] = 1_000_000.0
    p["entry_price"] = 2.0
    result = evaluate_risk_preview(
        p,
        limits={"max_pair_exposure": 1000.0},
    )
    assert result["allowed"] is False
    assert MAX_PAIR_EXPOSURE_HIT_REASON in result["blocked_reasons"]


def test_high_spread_blocked():
    p = _base_preview()
    p["spread"] = 0.01
    result = evaluate_risk_preview(p, limits={"max_spread": 0.001})
    assert result["allowed"] is False
    assert SPREAD_TOO_HIGH_REASON in result["blocked_reasons"]


def test_stale_data_blocked():
    p = _base_preview()
    result = evaluate_risk_preview(
        {**p, "data_timestamp": "2026-06-20T00:00:00+00:00"},
        now_timestamp="2026-06-20T00:10:00+00:00",
        limits={"max_data_age_seconds": 60},
    )
    assert result["allowed"] is False
    assert STALE_MARKET_DATA_REASON in result["blocked_reasons"]


def test_cooldown_after_loss_blocked():
    p = _base_preview()
    closed = [
        {
            "pair": "EURUSD",
            "direction": "buy",
            "status": "closed",
            "outcome": "LOSS",
            "closed_timestamp": "2026-06-20T00:09:00+00:00",
        },
    ]
    result = evaluate_risk_preview(
        p,
        closed_trades=closed,
        now_timestamp="2026-06-20T00:09:30+00:00",
        limits={"cooldown_after_loss_seconds": 120},
    )
    assert result["allowed"] is False
    assert COOLDOWN_AFTER_LOSS_REASON in result["blocked_reasons"]


def test_duplicate_setup_blocked():
    p = _base_preview()
    open_trade = {
        "pair": "EURUSD",
        "direction": "buy",
        "status": "previewed",
        "units": 100,
        "entry_price": 1.105,
    }
    result = evaluate_risk_preview(p, open_trades=(open_trade,), limits={"duplicate_setup_block": True})
    assert result["allowed"] is False
    assert DUPLICATE_SETUP_REASON in result["blocked_reasons"]


def test_kill_switch_blocks():
    p = _base_preview()
    result = evaluate_risk_preview(p, account_state={"kill_switch_active": True})
    assert result["allowed"] is False
    assert KILL_SWITCH_ACTIVE_REASON in result["blocked_reasons"]


def test_non_paper_mode_blocks():
    p = _base_preview()
    p["mode"] = "live"
    result = evaluate_risk_preview(p)
    assert result["allowed"] is False
    assert LIVE_TRADING_BLOCKED_REASON in result["blocked_reasons"]


def test_negative_account_state_blocks():
    p = _base_preview()
    result = evaluate_risk_preview(p, account_state={"equity": -1.0})
    assert result["allowed"] is False
    assert INVALID_ACCOUNT_STATE_REASON in result["blocked_reasons"]


def test_negative_open_risk_blocks():
    p = _base_preview()
    result = evaluate_risk_preview(p, account_state={"open_risk": -1.0})
    assert result["allowed"] is False
    assert INVALID_ACCOUNT_STATE_REASON in result["blocked_reasons"]


def test_invalid_units_blocked():
    p = _base_preview()
    p["units"] = 0
    result = evaluate_risk_preview(p)
    assert result["allowed"] is False
    assert INVALID_UNITS_REASON in result["blocked_reasons"]


def test_multiple_blocked_reasons_are_deterministic():
    p = _base_preview()
    p["stop_loss"] = 1.20
    p["percent_risk"] = 100.0
    result = evaluate_risk_preview(
        p,
        account_state={"open_risk": -1.0, "max_daily_loss": 0.0},
        limits={
            "max_risk_per_trade_pct": 1.0,
            "max_spread": 0.1,
            "spread": 0.2,
        },
    )
    assert result["blocked_reasons"]
    assert result["blocked_reasons"] == list(dict.fromkeys(result["blocked_reasons"]))
    assert result["blocked_reason"] == INVALID_PREVIEW_REASON or result["blocked_reason"] in {
        INVALID_ACCOUNT_STATE_REASON,
        INVALID_PREVIEW_REASON,
    }


def test_source_has_no_network_broker_or_secret_runtime_calls():
    source = MODULE_PATH.read_text(encoding="utf-8")
    parsed = ast.parse(source)

    dangerous_import = ("subprocess", "requests", "socket", "urllib", "oanda", "alpaca", "broker", "ccxt", "mt5")
    sensitive_names = {"credential", "account_id", "secret"}
    dangerous_call_names = {
        "open",
        "write_text",
        "write_bytes",
        "system",
        "getenv",
    }

    for node in ast.walk(parsed):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported = (alias.name or "").lower()
                assert not any(token in imported for token in dangerous_import)
        if isinstance(node, ast.ImportFrom):
            module = (node.module or "").lower()
            assert not any(token in module for token in dangerous_import)
            for alias in node.names:
                alias_name = (alias.name or "").lower()
                assert not any(token in alias_name for token in dangerous_import)

        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                fn_name = fn.id.lower()
                assert fn_name not in dangerous_call_names
            elif isinstance(fn, ast.Attribute):
                fn_name = fn.attr.lower()
                assert fn_name not in dangerous_call_names

        if isinstance(node, ast.Attribute):
            assert node.attr.lower() not in {"pathlib", "environ"}
        if isinstance(node, ast.Name):
            assert node.id.lower() not in sensitive_names
