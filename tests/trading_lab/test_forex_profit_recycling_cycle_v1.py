from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_paper_session_controller.py"
RISK_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_risk_controls.py"
PORTFOLIO_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_portfolio_state.py"


def load_module():
    spec = importlib.util.spec_from_file_location("forex_paper_session_controller", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def market() -> dict[str, object]:
    return {"EURUSD": {"bid": 1.1000, "ask": 1.1002}}


def limits(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "max_position_size_units": 5000,
        "max_risk_percent": 1.0,
        "daily_loss_limit": 100.0,
        "max_trades_per_day": 20,
    }
    base.update(overrides)
    return base


def evaluate_signal() -> dict[str, object]:
    return {
        "pair": "EURUSD",
        "cycle_phase": "evaluate",
        "ranked_pairs": [{"pair": "EURUSD", "rank": 1, "proposed_allocation_percent": 0.5}],
        "confidence_score": 84.0,
        "spread_score": 92.0,
        "volatility_score": 76.0,
        "liquidity_score": 88.0,
        "expectancy_score": 79.0,
        "drawdown_score": 91.0,
        "risk_adjusted_score": 81.0,
    }


def enter_signal(action: str = "buy", units: int = 1000, **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "pair": "EURUSD",
        "cycle_phase": "enter",
        "action": action,
        "position_size_units": units,
        "risk_percent": 0.5,
    }
    payload.update(overrides)
    return payload


def monitor_signal(action: str = "hold") -> dict[str, object]:
    return {"pair": "EURUSD", "cycle_phase": "monitor", "action": action}


def exit_signal(action: str = "close", exit_price: float = 1.0990) -> dict[str, object]:
    return {
        "pair": "EURUSD",
        "cycle_phase": "exit",
        "action": action,
        "position_size_units": 1000,
        "risk_percent": 0.5,
        "exit_price": exit_price,
    }


def run_cycle(signals: list[dict[str, object]], **kwargs: object) -> dict[str, object]:
    module = load_module()
    options: dict[str, object] = {
        "account_snapshot": {"cash_balance": 1000.0, "starting_balance": 1000.0},
        "limits": limits(),
        "market": market(),
        "config": {"slippage_pips": 0.0, "max_spread_pips": 3.0},
    }
    options.update(kwargs)
    return module.run_paper_session(signals, **options)


def test_strict_cycle_requires_evaluate_before_enter() -> None:
    result = run_cycle([enter_signal()])
    assert result["allowed"] is False
    assert result["block_reasons"] == ["cycle_phase_mismatch"]


def test_enter_monitor_and_exit_phase_action_gates() -> None:
    enter_block = run_cycle([evaluate_signal(), enter_signal("sell")])
    assert enter_block["block_reasons"] == ["enter_requires_buy_action"]

    monitor_block = run_cycle([evaluate_signal(), enter_signal(), monitor_signal("sell")])
    assert monitor_block["block_reasons"] == ["monitor_disallows_trade_action"]

    exit_block = run_cycle([evaluate_signal(), enter_signal(), monitor_signal(), exit_signal("buy")])
    assert exit_block["block_reasons"] == ["exit_requires_sell_or_close_action"]


def test_close_normalizes_to_sell_and_profit_returns_to_balance_bucket() -> None:
    result = run_cycle([evaluate_signal(), enter_signal(), monitor_signal(), exit_signal("close", 1.0990)])

    assert result["allowed"] is True
    assert result["cycle_reassessment_required"] is True
    assert result["ledger_records"][-1]["action"] == "sell"
    assert result["realized_pnl"] == 1.0
    assert result["final_cash"] == 1001.0
    assert result["realized_gain_bucket"] == 1.0
    assert result["final_portfolio_state"]["profit_bucket"] == 1.0
    assert result["open_positions"] == {}


def test_realized_loss_updates_loss_bucket_and_daily_loss_used() -> None:
    result = run_cycle([evaluate_signal(), enter_signal(), monitor_signal(), exit_signal("sell", 1.1010)])

    assert result["realized_pnl"] == -1.0
    assert result["final_cash"] == 999.0
    assert result["realized_loss_bucket"] == 1.0
    assert result["final_portfolio_state"]["loss_bucket"] == 1.0
    assert result["daily_loss_used"] == 1.0


def test_no_immediate_reentry_without_fresh_evaluate_phase() -> None:
    result = run_cycle([
        evaluate_signal(),
        enter_signal(),
        monitor_signal(),
        exit_signal(),
        enter_signal(),
    ])

    assert result["allowed"] is False
    assert result["block_reasons"] == ["cycle_phase_mismatch"]
    assert result["cycle_reassessment_required"] is True


def test_daily_loss_and_consecutive_loss_stops_block_next_evaluate() -> None:
    loss_cycle = [evaluate_signal(), enter_signal(), monitor_signal(), exit_signal("sell", 1.1010), evaluate_signal()]

    daily_stop = run_cycle(loss_cycle, limits=limits(daily_loss_limit=1.0))
    assert daily_stop["block_reasons"] == ["daily_loss_limit_hit"]

    consecutive_stop = run_cycle(loss_cycle, limits=limits(max_consecutive_losses=1))
    assert consecutive_stop["block_reasons"] == ["max_consecutive_losses_limit_hit"]


def test_max_open_trade_count_blocks_next_trade_evaluation() -> None:
    result = run_cycle(
        [evaluate_signal()],
        account_snapshot={
            "cash_balance": 1000.0,
            "starting_balance": 1000.0,
            "open_positions": {"EURUSD": {"units": 1000, "average_entry_price": 1.1}},
        },
        limits=limits(max_open_trades=1),
    )

    assert result["allowed"] is False
    assert result["block_reasons"] == ["max_open_trades_limit_hit"]


def test_martingale_revenge_and_unapproved_compounding_are_blocked() -> None:
    martingale = run_cycle([evaluate_signal(), enter_signal(is_martingale=True)])
    assert martingale["block_reasons"] == ["forbidden_sizing_model"]

    revenge = run_cycle([evaluate_signal(), enter_signal(is_revenge=True)])
    assert revenge["block_reasons"] == ["forbidden_sizing_model"]

    compounding = run_cycle(
        [evaluate_signal(), enter_signal(units=2000)],
        account_snapshot={"cash_balance": 1000.0, "starting_balance": 1000.0, "previous_position_size_units": 1000},
    )
    assert compounding["block_reasons"] == ["forbidden_compounding_growth"]

    approved = run_cycle(
        [evaluate_signal(), enter_signal(units=2000, owner_approved_compounding=True)],
        account_snapshot={"cash_balance": 1000.0, "starting_balance": 1000.0, "previous_position_size_units": 1000},
    )
    assert approved["allowed"] is True
    assert approved["block_reasons"] == []


def test_profit_cycle_sources_have_no_forbidden_runtime_tokens() -> None:
    for path in (MODULE_PATH, RISK_PATH, PORTFOLIO_PATH):
        source = path.read_text(encoding="utf-8").lower()
        for token in (
            "requests",
            "socket",
            "urllib",
            "subprocess",
            "os.environ",
            "broker_sdk",
            "schedule.every",
            "start-process",
        ):
            assert token not in source
