from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_portfolio_state.py"


def load_module():
    spec = importlib.util.spec_from_file_location("forex_portfolio_state", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def buy_record(pair: str = "EURUSD", units: int = 1000, price: float = 1.1, pnl: float = 0.0) -> dict[str, object]:
    return {
        "allowed": True,
        "paper_only": True,
        "paper_order_id": f"paper-{pair}-buy",
        "pair": pair,
        "action": "buy",
        "filled_units": units,
        "fill_price": price,
        "slippage_pips": 0.1,
        "spread_pips": 1.0,
        "realized_pnl": pnl,
        "status": "filled",
    }


def sell_record(pair: str = "GBPUSD", units: int = 500, price: float = 1.25, pnl: float = 12.5) -> dict[str, object]:
    return {
        "allowed": True,
        "paper_only": True,
        "paper_order_id": f"paper-{pair}-sell",
        "pair": pair,
        "action": "sell",
        "filled_units": units,
        "fill_price": price,
        "slippage_pips": 0.1,
        "spread_pips": 1.0,
        "realized_pnl": pnl,
        "status": "filled",
    }


def test_module_imports():
    module = load_module()
    assert callable(module.build_portfolio_state)


def test_buy_record_creates_long_position_and_cash_balance():
    module = load_module()
    result = module.build_portfolio_state(
        [buy_record(pnl=5.0)],
        account_snapshot={"cash_balance": 1000.0},
        limits={"max_trades_per_day": 5},
    )
    assert result["allowed"] is True
    assert result["cash_balance"] == 1005.0
    assert result["realized_pnl"] == 5.0
    assert result["trade_count"] == 1
    assert result["open_positions"]["EURUSD"]["side"] == "long"
    assert result["open_positions"]["EURUSD"]["units"] == 1000.0
    assert result["exposure_by_symbol"]["EURUSD"] == 1100.0
    assert result["unrealized_pnl"] == 0.0
    assert result["next_trade_allowed"] is True


def test_sell_record_creates_short_position_and_realized_pnl():
    module = load_module()
    result = module.build_portfolio_state([sell_record()], account_snapshot={"balance": 2000.0})
    assert result["allowed"] is True
    assert result["cash_balance"] == 2012.5
    assert result["open_positions"]["GBPUSD"]["side"] == "short"
    assert result["open_positions"]["GBPUSD"]["units"] == -500.0
    assert result["realized_pnl"] == 12.5


def test_hold_and_blocked_records_do_not_create_positions():
    module = load_module()
    result = module.build_portfolio_state(
        [
            {
                "allowed": True,
                "paper_only": True,
                "pair": "USDJPY",
                "action": "hold",
                "filled_units": 0,
                "realized_pnl": 0,
            },
            {
                "allowed": False,
                "paper_only": True,
                "pair": "EURUSD",
                "action": "buy",
            },
        ],
        account_snapshot={"cash_balance": 500.0},
    )
    assert result["allowed"] is True
    assert result["cash_balance"] == 500.0
    assert result["open_positions"] == {}
    assert result["trade_count"] == 0


def test_unrealized_pnl_uses_safe_zero_without_market_price():
    module = load_module()
    result = module.build_portfolio_state([buy_record()])
    assert result["unrealized_pnl"] == 0.0


def test_unrealized_pnl_uses_market_price_when_provided():
    module = load_module()
    result = module.build_portfolio_state(
        [buy_record(units=1000, price=1.1)],
        market_prices={"EURUSD": {"bid": 1.101}},
    )
    assert result["unrealized_pnl"] == 1.0


def test_daily_loss_blocks_next_trade():
    module = load_module()
    result = module.build_portfolio_state(
        [buy_record(pnl=-25.0)],
        limits={"daily_loss_limit": 20.0},
    )
    assert result["allowed"] is True
    assert result["daily_loss_used"] == 25.0
    assert result["next_trade_allowed"] is False
    assert result["next_trade_blocked_reason"] == "daily_loss_limit_hit"


def test_max_trades_blocks_next_trade():
    module = load_module()
    result = module.build_portfolio_state(
        [buy_record(), sell_record()],
        limits={"max_trades_per_day": 2},
    )
    assert result["trade_count"] == 2
    assert result["next_trade_allowed"] is False
    assert result["next_trade_blocked_reason"] == "max_trades_limit_hit"


def test_exposure_blocks_next_trade():
    module = load_module()
    result = module.build_portfolio_state(
        [buy_record(units=1000, price=1.1)],
        limits={"max_exposure_per_symbol": 1000.0},
    )
    assert result["next_trade_allowed"] is False
    assert result["next_trade_blocked_reason"] == "exposure_limit_hit"


def test_invalid_pair_blocked():
    module = load_module()
    result = module.build_portfolio_state([buy_record(pair="AUDUSD")])
    assert result["allowed"] is False
    assert result["blocked_reason"] == "invalid_pair"


def test_unsupported_action_blocked():
    module = load_module()
    record = buy_record()
    record["action"] = "close"
    result = module.build_portfolio_state([record])
    assert result["allowed"] is False
    assert result["blocked_reason"] == "unsupported_action"


def test_missing_fill_price_blocked_for_trade():
    module = load_module()
    record = buy_record()
    record["fill_price"] = 0
    result = module.build_portfolio_state([record])
    assert result["allowed"] is False
    assert result["blocked_reason"] == "missing_fill_price"


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
        result = module.build_portfolio_state([buy_record()], **{flag: True})
        assert result["allowed"] is False
        assert result["blocked_reason"] == f"unsafe_flag_{flag}"


def test_source_has_no_network_file_write_or_subprocess_usage():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["subprocess", "requests", "socket", "urllib", "open(", ".write_text", "pathlib"]:
        assert forbidden not in source
