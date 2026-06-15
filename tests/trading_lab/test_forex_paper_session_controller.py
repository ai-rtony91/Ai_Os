from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_paper_session_controller.py"


def load_module():
    spec = importlib.util.spec_from_file_location("forex_paper_session_controller", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def market() -> dict[str, object]:
    return {
        "EURUSD": {"bid": 1.1000, "ask": 1.1002},
        "GBPUSD": {"bid": 1.2500, "ask": 1.2502},
        "USDJPY": {"bid": 155.10, "ask": 155.12},
    }


def limits(**overrides: object) -> dict[str, object]:
    base = {
        "max_position_size_units": 5000,
        "max_risk_percent": 1.0,
        "daily_loss_limit": 100.0,
        "max_trades_per_day": 5,
    }
    base.update(overrides)
    return base


def signal(
    pair: str = "EURUSD",
    action: str = "buy",
    units: int = 1000,
    risk_percent: float = 0.5,
    exit_price: float | None = None,
) -> dict[str, object]:
    output: dict[str, object] = {
        "pair": pair,
        "action": action,
        "position_size_units": units,
        "risk_percent": risk_percent,
    }
    if exit_price is not None:
        output["exit_price"] = exit_price
    return output


def test_module_imports():
    module = load_module()
    assert module.SCHEMA == "AIOS_FOREX_PAPER_SESSION_CONTROLLER.v1"
    assert callable(module.run_paper_session)


def test_session_chains_risk_execution_ledger_and_portfolio():
    module = load_module()
    result = module.run_paper_session(
        [
            signal(exit_price=1.1012),
            signal("GBPUSD", "sell", 2000, exit_price=1.2492),
        ],
        account_snapshot={"cash_balance": 1000.0},
        limits=limits(),
        market=market(),
        config={"slippage_pips": 0.0, "max_spread_pips": 3.0},
    )
    assert result["session_status"] == "completed"
    assert result["trades_attempted"] == 2
    assert result["trades_accepted"] == 2
    assert result["trades_blocked"] == 0
    assert result["realized_pnl"] == 2.6
    assert result["final_cash"] == 1002.6
    assert result["open_positions"]["EURUSD"]["side"] == "long"
    assert result["open_positions"]["GBPUSD"]["side"] == "short"
    assert len(result["ledger_records"]) == 2
    assert result["paper_only"] is True


def test_session_stops_when_risk_controls_block():
    module = load_module()
    result = module.run_paper_session(
        [signal(units=6000), signal("GBPUSD", "sell")],
        account_snapshot={"cash_balance": 1000.0},
        limits=limits(max_position_size_units=5000),
        market=market(),
    )
    assert result["session_status"] == "stopped_blocked"
    assert result["trades_attempted"] == 1
    assert result["trades_accepted"] == 0
    assert result["trades_blocked"] == 1
    assert result["block_reasons"] == ["position_size_above_max"]
    assert result["ledger_records"] == []


def test_session_stops_when_execution_blocks():
    module = load_module()
    result = module.run_paper_session(
        [signal("EURUSD", "buy")],
        account_snapshot={"cash_balance": 1000.0},
        limits=limits(),
        market={"EURUSD": {"bid": 1.1000}},
    )
    assert result["session_status"] == "stopped_blocked"
    assert result["trades_attempted"] == 1
    assert result["trades_accepted"] == 0
    assert result["trades_blocked"] == 1
    assert result["block_reasons"] == ["missing_market_price"]
    assert result["ledger_records"][0]["allowed"] is False


def test_session_stops_when_portfolio_next_trade_blocks():
    module = load_module()
    result = module.run_paper_session(
        [signal(exit_price=1.1012), signal("GBPUSD", "sell", 1000)],
        account_snapshot={"cash_balance": 1000.0},
        limits=limits(max_trades_per_day=1),
        market=market(),
    )
    assert result["session_status"] == "stopped_blocked"
    assert result["trades_attempted"] == 2
    assert result["trades_accepted"] == 1
    assert result["trades_blocked"] == 1
    assert result["block_reasons"] == ["max_trades_limit_hit"]
    assert result["final_portfolio_state"]["next_trade_allowed"] is False


def test_session_tracks_daily_loss_used():
    module = load_module()
    result = module.run_paper_session(
        [signal(exit_price=1.0992)],
        account_snapshot={"cash_balance": 1000.0},
        limits=limits(),
        market=market(),
        config={"slippage_pips": 0.0},
    )
    assert result["realized_pnl"] == -1.0
    assert result["daily_loss_used"] == 1.0
    assert result["final_cash"] == 999.0


def test_unsafe_flags_blocked_with_scanner_safe_values():
    module = load_module()
    for flag in [
        "live_execution",
        "broker_order",
        "credentials",
        "api_key",
        "real_order",
        "webhook_url",
        "network",
        "network_access",
    ]:
        result = module.run_paper_session(
            [signal()],
            account_snapshot={"cash_balance": 1000.0},
            limits=limits(),
            market=market(),
            **{flag: True},
        )
        assert result["session_status"] == "blocked"
        assert result["block_reasons"] == [f"unsafe_flag_{flag}"]


def test_source_has_no_network_file_write_or_subprocess_usage():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["subprocess", "requests", "socket", "urllib", ".write_text", "open("]:
        assert forbidden not in source
