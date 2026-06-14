from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_paper_ledger.py"


def load_ledger_module():
    spec = importlib.util.spec_from_file_location("forex_paper_ledger", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_ledger_imports():
    ledger = load_ledger_module()
    assert callable(ledger.record_paper_trade)
    assert callable(ledger.summarize_paper_ledger)


def test_valid_paper_trade_records():
    ledger = load_ledger_module()
    record = ledger.record_paper_trade(
        pair="EURUSD",
        direction="buy",
        entry=1.1000,
        stop=1.0950,
        target=1.1050,
        position_size=10000,
        timestamp="2026-06-14T00:00:00Z",
    )
    assert record["allowed"] is True
    assert record["pair"] == "EURUSD"
    assert record["direction"] == "buy"
    assert record["result_pips"] == 50.0
    assert record["pnl"] == 50.0
    assert record["paper_only"] is True
    assert record["execution_allowed"] is False


def test_pnl_summary_deterministic():
    ledger = load_ledger_module()
    summary = ledger.summarize_paper_ledger(
        [
            {
                "pair": "EURUSD",
                "direction": "buy",
                "entry": 1.1000,
                "stop": 1.0950,
                "target": 1.1050,
                "position_size": 10000,
                "timestamp": "2026-06-14T00:00:00Z",
            },
            {
                "pair": "GBPUSD",
                "direction": "sell",
                "entry": 1.2500,
                "stop": 1.2550,
                "target": 1.2450,
                "position_size": 10000,
                "timestamp": "2026-06-14T00:05:00Z",
            },
            {
                "pair": "USDJPY",
                "direction": "buy",
                "entry": 157.00,
                "stop": 156.50,
                "target": 156.80,
                "position_size": 1000,
                "timestamp": "2026-06-14T00:10:00Z",
            },
        ]
    )
    assert summary["trade_count"] == 3
    assert summary["winning_trades"] == 2
    assert summary["losing_trades"] == 1
    assert summary["total_pnl"] == -100.0
    assert summary["paper_only"] is True


def test_live_broker_credential_and_real_order_blocked():
    ledger = load_ledger_module()
    base = {
        "pair": "EURUSD",
        "direction": "buy",
        "entry": 1.1000,
        "stop": 1.0950,
        "target": 1.1050,
        "position_size": 10000,
        "timestamp": "2026-06-14T00:00:00Z",
    }
    assert ledger.record_paper_trade(**base, live_execution=True)["blocked_reason"] == "live_execution_blocked"
    assert ledger.record_paper_trade(**base, broker_order=True)["blocked_reason"] == "broker_order_blocked"
    assert ledger.record_paper_trade(**base, credentials={"token": "x"})["blocked_reason"] == "credentials_blocked"
    assert ledger.record_paper_trade(**base, api_key="x")["blocked_reason"] == "api_key_blocked"
    assert ledger.record_paper_trade(**base, real_order=True)["blocked_reason"] == "real_order_blocked"


def test_invalid_pair_blocked():
    ledger = load_ledger_module()
    record = ledger.record_paper_trade(
        pair="AUDUSD",
        direction="buy",
        entry=0.6500,
        stop=0.6450,
        target=0.6550,
        position_size=10000,
        timestamp="2026-06-14T00:00:00Z",
    )
    assert record["allowed"] is False
    assert record["blocked_reason"] == "unsupported_pair"
