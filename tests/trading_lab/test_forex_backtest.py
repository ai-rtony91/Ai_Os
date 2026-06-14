from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_backtest.py"


def load_backtest_module():
    spec = importlib.util.spec_from_file_location("forex_backtest", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_generated_forex_backtest_imports():
    backtest = load_backtest_module()
    assert callable(backtest.run_backtest)


def test_backtest_returns_paper_only_true():
    backtest = load_backtest_module()
    summary = backtest.run_backtest([])
    assert summary["paper_only"] is True
    assert summary["execution_allowed"] is False
    assert summary["broker_execution"] is False
    assert summary["real_orders"] is False


def test_valid_sample_candles_produce_deterministic_summary():
    backtest = load_backtest_module()
    summary = backtest.run_backtest(
        [
            {"pair": "EURUSD", "direction": "buy", "close": 1.10, "stop_loss": 1.09, "paper_result_r": 1.0},
            {"pair": "GBPUSD", "direction": "sell", "close": 1.25, "stop_loss": 1.26, "paper_result_r": -0.5},
            {"pair": "AUDUSD", "direction": "buy", "close": 0.65, "stop_loss": 0.64, "paper_result_r": 1.0},
        ],
        starting_balance=10000.0,
        max_risk_percent=1.0,
    )
    assert summary["trades_considered"] == 3
    assert summary["trades_allowed"] == 2
    assert summary["trades_blocked"] == 1
    assert summary["ending_balance"] == 10049.5
    assert summary["paper_only"] is True


def test_broker_live_and_credential_fields_are_blocked():
    backtest = load_backtest_module()
    summary = backtest.run_backtest(
        [
            {"pair": "EURUSD", "direction": "buy", "close": 1.10, "stop_loss": 1.09, "broker_order": True},
            {"pair": "EURUSD", "direction": "buy", "close": 1.10, "stop_loss": 1.09, "live_execution": True},
            {"pair": "EURUSD", "direction": "buy", "close": 1.10, "stop_loss": 1.09, "credentials": {"token": "x"}},
            {"pair": "EURUSD", "direction": "buy", "close": 1.10, "stop_loss": 1.09, "webhook_url": "https://example.invalid"},
        ],
    )
    assert summary["trades_considered"] == 4
    assert summary["trades_allowed"] == 0
    assert summary["trades_blocked"] == 4
    assert all(decision["allowed"] is False for decision in summary["decisions"])
    assert summary["execution_allowed"] is False
    assert summary["live_trading"] is False
