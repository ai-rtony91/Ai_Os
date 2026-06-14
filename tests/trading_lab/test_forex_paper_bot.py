from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_paper_bot.py"


def load_bot_module():
    spec = importlib.util.spec_from_file_location("forex_paper_bot", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_valid_eurusd_paper_signal_allowed():
    bot = load_bot_module()
    decision = bot.paper_decision("EURUSD", "buy", 1.10, 1.09, 10000, 1.0)
    assert decision["allowed"] is True
    assert decision["decision_type"] == "paper_decision_only"
    assert decision["execution_allowed"] is False
    assert decision["broker_execution"] is False
    assert decision["real_orders"] is False


def test_valid_sell_signal_allowed():
    bot = load_bot_module()
    decision = bot.paper_decision("GBPUSD", "sell", 1.25, 1.26, 10000, 1.0)
    assert decision["allowed"] is True
    assert decision["direction"] == "sell"


def test_unsafe_scope_is_blocked():
    bot = load_bot_module()
    assert bot.paper_decision("EURUSD", "buy", 1.10, 1.09, 10000, 1.0, live_execution=True)["allowed"] is False
    assert bot.paper_decision("EURUSD", "buy", 1.10, 1.09, 10000, 1.0, broker_order=True)["allowed"] is False
    assert bot.paper_decision("EURUSD", "buy", 1.10, 1.09, 10000, 1.0, credentials={"token": "x"})["allowed"] is False
    assert bot.paper_decision("EURUSD", "buy", 1.10, 1.09, 10000, 1.0, real_order=True)["allowed"] is False
    assert bot.paper_decision("EURUSD", "buy", 1.10, 1.09, 10000, 1.0, webhook_url="https://example.invalid")["allowed"] is False


def test_invalid_inputs_are_blocked():
    bot = load_bot_module()
    assert bot.paper_decision("AUDUSD", "buy", 1.10, 1.09, 10000, 1.0)["blocked_reason"] == "unsupported_pair"
    assert bot.paper_decision("EURUSD", "hold", 1.10, 1.09, 10000, 1.0)["blocked_reason"] == "unsupported_direction"
    assert bot.paper_decision("EURUSD", "buy", 1.10, None, 10000, 1.0)["blocked_reason"] == "stop_loss_required"
    assert bot.paper_decision("EURUSD", "buy", 1.10, 1.09, 10000, 5.0)["blocked_reason"] == "max_risk_percent_exceeds_paper_limit"
