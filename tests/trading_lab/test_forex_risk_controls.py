from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_risk_controls.py"


def load_module():
    spec = importlib.util.spec_from_file_location("forex_risk_controls", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def signal(action: str = "buy") -> dict[str, object]:
    return {
        "pair": "EURUSD",
        "action": action,
        "position_size_units": 10000,
        "risk_percent": 1.0,
    }


def account() -> dict[str, object]:
    return {"daily_pnl": 0.0, "trades_today": 1}


def limits() -> dict[str, object]:
    return {
        "max_position_size_units": 25000,
        "max_risk_percent": 2.0,
        "daily_loss_limit": 500.0,
        "max_trades_per_day": 5,
    }


def test_module_imports():
    module = load_module()
    assert module.SUPPORTED_PAIRS == {"EURUSD", "GBPUSD", "USDJPY"}
    assert callable(module.evaluate_risk_controls)


def test_buy_under_limits_allowed():
    module = load_module()
    result = module.evaluate_risk_controls(signal("buy"), account(), limits())
    assert result["allowed"] is True
    assert result["blocked_reason"] == "none"
    assert result["paper_only"] is True
    assert result["safety"]["broker_execution"] is False


def test_sell_under_limits_allowed():
    module = load_module()
    sell_signal = signal("sell")
    sell_signal["pair"] = "GBPUSD"
    result = module.evaluate_risk_controls(sell_signal, account(), limits())
    assert result["allowed"] is True
    assert result["action"] == "sell"


def test_hold_allowed_with_zero_size():
    module = load_module()
    hold_signal = {"pair": "USDJPY", "action": "hold", "position_size_units": 0, "risk_percent": 0}
    result = module.evaluate_risk_controls(hold_signal, account(), limits())
    assert result["allowed"] is True
    assert result["action"] == "hold"
    assert result["position_size_units"] == 0.0
    assert result["risk_percent"] == 0.0


def test_invalid_pair_blocked():
    module = load_module()
    bad_signal = signal("buy")
    bad_signal["pair"] = "AUDUSD"
    result = module.evaluate_risk_controls(bad_signal, account(), limits())
    assert result["allowed"] is False
    assert result["blocked_reason"] == "invalid_pair"


def test_missing_action_blocked():
    module = load_module()
    bad_signal = signal("buy")
    bad_signal.pop("action")
    result = module.evaluate_risk_controls(bad_signal, account(), limits())
    assert result["allowed"] is False
    assert result["blocked_reason"] == "missing_action"


def test_unsupported_action_blocked():
    module = load_module()
    result = module.evaluate_risk_controls(signal("scale_in"), account(), limits())
    assert result["allowed"] is False
    assert result["blocked_reason"] == "unsupported_action"


def test_position_size_limit_blocked():
    module = load_module()
    bad_signal = signal("buy")
    bad_signal["position_size_units"] = 30000
    result = module.evaluate_risk_controls(bad_signal, account(), limits())
    assert result["allowed"] is False
    assert result["blocked_reason"] == "position_size_above_max"


def test_risk_percent_limit_blocked():
    module = load_module()
    bad_signal = signal("buy")
    bad_signal["risk_percent"] = 3.0
    result = module.evaluate_risk_controls(bad_signal, account(), limits())
    assert result["allowed"] is False
    assert result["blocked_reason"] == "risk_percent_above_max"


def test_daily_loss_blocked():
    module = load_module()
    bad_account = {"daily_pnl": -500.0, "trades_today": 1}
    result = module.evaluate_risk_controls(signal("buy"), bad_account, limits())
    assert result["allowed"] is False
    assert result["blocked_reason"] == "daily_loss_limit_hit"
    assert result["daily_loss_limit_hit"] is True


def test_max_trades_blocked():
    module = load_module()
    bad_account = {"daily_pnl": 0.0, "trades_today": 5}
    result = module.evaluate_risk_controls(signal("buy"), bad_account, limits())
    assert result["allowed"] is False
    assert result["blocked_reason"] == "max_trades_limit_hit"
    assert result["max_trades_limit_hit"] is True


def test_broker_live_and_external_scope_flags_blocked_with_safe_placeholders():
    module = load_module()
    assert module.evaluate_risk_controls(signal(), account(), limits(), broker_order=True)["blocked_reason"] == "broker_order_blocked"
    assert module.evaluate_risk_controls(signal(), account(), limits(), live_execution=True)["blocked_reason"] == "live_execution_blocked"
    assert module.evaluate_risk_controls(signal(), account(), limits(), credentials={"sample": "safe-placeholder"})["blocked_reason"] == "credentials_blocked"
    assert module.evaluate_risk_controls(signal(), account(), limits(), api_key="placeholder-safe")["blocked_reason"] == "api_key_blocked"
    assert module.evaluate_risk_controls(signal(), account(), limits(), real_order=True)["blocked_reason"] == "real_order_blocked"
    assert module.evaluate_risk_controls(signal(), account(), limits(), webhook_url="https://example.invalid/hook")["blocked_reason"] == "real_webhook_blocked"
    assert module.evaluate_risk_controls(signal(), account(), limits(), network=True)["blocked_reason"] == "network_blocked"


def test_no_network_or_file_write_usage():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["open(", "write_text", "write_bytes", "with open", "requests", "socket", "urllib", "http.client"]:
        assert forbidden not in source
