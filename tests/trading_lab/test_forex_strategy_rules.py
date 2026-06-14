from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_strategy_rules.py"


def load_strategy_module():
    spec = importlib.util.spec_from_file_location("forex_strategy_rules", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_strategy_module_imports():
    strategy = load_strategy_module()
    assert callable(strategy.evaluate_strategy)


def test_buy_signal_deterministic():
    strategy = load_strategy_module()
    signal = strategy.evaluate_strategy("EURUSD", {"fast_ma": 1.1050, "slow_ma": 1.1000, "momentum": 0.8})
    assert signal["allowed"] is True
    assert signal["signal"] == "buy"
    assert signal["paper_only"] is True
    assert signal["execution_allowed"] is False


def test_sell_signal_deterministic():
    strategy = load_strategy_module()
    signal = strategy.evaluate_strategy("GBPUSD", {"fast_ma": 1.2450, "slow_ma": 1.2500, "momentum": -0.4})
    assert signal["allowed"] is True
    assert signal["signal"] == "sell"
    assert signal["paper_only"] is True


def test_hold_on_insufficient_data():
    strategy = load_strategy_module()
    signal = strategy.evaluate_strategy("USDJPY", {"fast_ma": 157.2})
    assert signal["allowed"] is True
    assert signal["signal"] == "hold"
    assert signal["reason"] == "insufficient_data"


def test_invalid_pair_blocked():
    strategy = load_strategy_module()
    signal = strategy.evaluate_strategy("AUDUSD", {"fast_ma": 0.66, "slow_ma": 0.65, "momentum": 0.1})
    assert signal["allowed"] is False
    assert signal["blocked_reason"] == "unsupported_pair"


def test_live_broker_credential_real_order_and_webhook_blocked():
    strategy = load_strategy_module()
    data = {"fast_ma": 1.1050, "slow_ma": 1.1000, "momentum": 0.8}
    assert strategy.evaluate_strategy("EURUSD", data, live_execution=True)["blocked_reason"] == "live_execution_blocked"
    assert strategy.evaluate_strategy("EURUSD", data, broker_order=True)["blocked_reason"] == "broker_order_blocked"
    assert strategy.evaluate_strategy("EURUSD", data, credentials={"token": "x"})["blocked_reason"] == "credentials_blocked"
    assert strategy.evaluate_strategy("EURUSD", data, real_order=True)["blocked_reason"] == "real_order_blocked"
    assert strategy.evaluate_strategy("EURUSD", data, webhook_url="https://example.invalid")["blocked_reason"] == "webhook_url_blocked"
