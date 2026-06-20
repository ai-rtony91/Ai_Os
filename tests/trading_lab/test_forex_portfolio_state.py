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
    assert result["current_balance"] == 1005.0
    assert result["starting_balance"] == 1000.0
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
    assert result["current_balance"] == 2012.5
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


def test_legacy_gates_still_work():
    module = load_module()
    loss_result = module.build_portfolio_state(
        [buy_record(pnl=-25.0)],
        limits={"daily_loss_limit": 20.0},
    )
    assert loss_result["allowed"] is True
    assert loss_result["daily_loss_used"] == 25.0
    assert loss_result["next_trade_allowed"] is False
    assert loss_result["next_trade_blocked_reason"] == "daily_loss_limit_hit"

    trade_limit_result = module.build_portfolio_state(
        [buy_record(), sell_record()],
        limits={"max_trades_per_day": 2},
    )
    assert trade_limit_result["trade_count"] == 2
    assert trade_limit_result["next_trade_allowed"] is False
    assert trade_limit_result["next_trade_blocked_reason"] == "max_trades_limit_hit"


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


def test_additional_account_state_fields_are_returned():
    module = load_module()
    result = module.build_portfolio_state(
        [buy_record(pnl=2.0)],
        account_snapshot={
            "starting_balance": 500.0,
            "cash_balance": 500.0,
            "max_daily_loss": 200.0,
            "session_count": 1,
            "last_update_timestamp": "2026-06-20T00:00:00Z",
        },
    )
    assert result["starting_balance"] == 500.0
    assert result["current_balance"] == 502.0
    assert result["equity"] == 502.0
    assert result["drawdown"] == 0.0
    assert result["available_risk"] == 200.0
    assert result["max_daily_loss"] == 200.0
    assert result["open_risk"] == 1100.0
    assert result["session_count"] == 1
    assert result["last_update_timestamp"] == "2026-06-20T00:00:00Z"


def test_winning_trade_increases_current_balance():
    module = load_module()
    result = module.build_portfolio_state([buy_record(pnl=7.5)], account_snapshot={"cash_balance": 100.0})
    assert result["current_balance"] == 107.5
    assert result["cash_balance"] == 107.5


def test_losing_trade_increases_daily_loss_and_drawdown():
    module = load_module()
    result = module.build_portfolio_state(
        [buy_record(pnl=-5.0)],
        account_snapshot={"starting_balance": 1000.0, "cash_balance": 1000.0},
    )
    assert result["daily_loss_used"] == 5.0
    assert result["equity"] == 995.0
    assert result["drawdown"] == 5.0
    assert result["drawdown_percent"] == 0.5


def test_available_risk_floors_at_zero():
    module = load_module()
    result = module.build_portfolio_state(
        [buy_record(pnl=-30.0, units=1000, price=1.1)],
        account_snapshot={
            "cash_balance": 1000.0,
            "starting_balance": 1000.0,
            "max_daily_loss": 20.0,
        },
    )
    assert result["available_risk"] == 0.0


def test_negative_starting_balance_is_blocked():
    module = load_module()
    result = module.build_portfolio_state([], account_snapshot={"starting_balance": -100.0})
    assert result["allowed"] is False
    assert result["blocked_reason"] == "negative_starting_balance"


def test_negative_cash_or_current_balance_is_blocked():
    module = load_module()
    neg_cash = module.build_portfolio_state([], account_snapshot={"cash_balance": -1.0})
    assert neg_cash["allowed"] is False
    assert neg_cash["blocked_reason"] == "negative_cash_balance"

    neg_current = module.build_portfolio_state([], account_snapshot={"cash_balance": 10.0, "current_balance": -1.0})
    assert neg_current["allowed"] is False
    assert neg_current["blocked_reason"] == "negative_current_balance"


def test_negative_max_daily_loss_is_blocked():
    module = load_module()
    result = module.build_portfolio_state([], account_snapshot={"cash_balance": 100.0, "max_daily_loss": -5.0})
    assert result["allowed"] is False
    assert result["blocked_reason"] == "negative_max_daily_loss"


def test_negative_open_risk_is_blocked_when_account_snapshot_supplies_it():
    module = load_module()
    result = module.build_portfolio_state(
        [buy_record()],
        account_snapshot={
            "cash_balance": 1000.0,
            "starting_balance": 1000.0,
            "max_daily_loss": 100.0,
            "open_risk": -10.0,
        },
    )
    assert result["allowed"] is False
    assert result["blocked_reason"] == "negative_open_risk"


def test_invalid_session_count_is_blocked():
    module = load_module()
    result = module.build_portfolio_state([], account_snapshot={"cash_balance": 100.0, "session_count": -1})
    assert result["allowed"] is False
    assert result["blocked_reason"] == "invalid_session_count"


def test_invalid_last_update_timestamp_type_is_blocked():
    module = load_module()
    result = module.build_portfolio_state([], account_snapshot={"cash_balance": 100.0, "last_update_timestamp": {"oops": 1}})
    assert result["allowed"] is False
    assert result["blocked_reason"] == "invalid_timestamp_type"


def test_source_has_no_network_file_write_or_broker_behavior():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    forbidden_terms = [
        "subprocess",
        "requests",
        "socket",
        "urllib",
        "open(",
        ".write_text",
        "pathlib",
        "os.system",
        "importlib",
        "http://",
        "https://",
        "broker_sdk",
        "ccxt",
        "oanda",
        " requests",
    ]
    for forbidden in forbidden_terms:
        assert forbidden not in source

