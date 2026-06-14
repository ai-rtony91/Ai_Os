from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_report.py"


def load_report_module():
    spec = importlib.util.spec_from_file_location("forex_report", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def sample_backtest():
    return {
        "trades_considered": 3,
        "trades_allowed": 2,
        "trades_blocked": 1,
        "ending_balance": 10049.5,
        "paper_only": True,
    }


def sample_ledger():
    return {
        "trade_count": 3,
        "winning_trades": 2,
        "losing_trades": 1,
        "total_pnl": -100.0,
        "paper_only": True,
    }


def sample_strategy():
    return {"name": "ma_momentum", "version": "paper-v1", "signal": "buy"}


def test_module_imports():
    report = load_report_module()
    assert callable(report.build_report)


def test_valid_report_generated():
    report = load_report_module()
    scorecard = report.build_report(sample_backtest(), sample_ledger(), sample_strategy())
    assert scorecard["allowed"] is True
    assert scorecard["report_type"] == "paper_scorecard"
    assert scorecard["paper_only"] is True
    assert scorecard["network_access"] is False
    assert scorecard["file_writes"] is False


def test_win_rate_calculated():
    report = load_report_module()
    scorecard = report.build_report(sample_backtest(), sample_ledger(), sample_strategy())
    assert scorecard["trade_count"] == 3
    assert scorecard["win_rate"] == 66.67
    assert scorecard["total_pnl"] == -100.0


def test_risk_flags_present():
    report = load_report_module()
    scorecard = report.build_report(sample_backtest(), sample_ledger(), sample_strategy())
    assert "negative_total_pnl" in scorecard["risk_flags"]
    assert "blocked_backtest_trades_present" in scorecard["risk_flags"]


def test_broker_live_credential_real_order_webhook_and_network_blocked():
    report = load_report_module()
    assert report.build_report(sample_backtest(), sample_ledger(), sample_strategy(), broker_order=True)["blocked_reason"] == "broker_order_blocked"
    assert report.build_report(sample_backtest(), sample_ledger(), sample_strategy(), live_execution=True)["blocked_reason"] == "live_execution_blocked"
    assert report.build_report(sample_backtest(), sample_ledger(), sample_strategy(), credentials={"token": "x"})["blocked_reason"] == "credentials_blocked"
    assert report.build_report(sample_backtest(), sample_ledger(), sample_strategy(), real_order=True)["blocked_reason"] == "real_order_blocked"
    assert report.build_report(sample_backtest(), sample_ledger(), sample_strategy(), webhook_url="https://example.invalid")["blocked_reason"] == "webhook_url_blocked"
    assert report.build_report(sample_backtest(), sample_ledger(), sample_strategy(), network=True)["blocked_reason"] == "network_blocked"


def test_no_file_writes():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["open(", "write_text", "write_bytes", "with open", "pathlib"]:
        assert forbidden not in source
