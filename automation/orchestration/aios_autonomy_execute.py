from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


SCHEMA = "AIOS_AUTONOMY_EXECUTE.v1"
SUPPORTED_GOALS = {"forex-paper-bot"}

FOREX_BOT_PATH = Path("apps/trading_lab/trading_lab/forex_paper_bot.py")
FOREX_BOT_TEST_PATH = Path("tests/trading_lab/test_forex_paper_bot.py")
FOREX_BOT_DOC_PATH = Path("docs/orchestration/AIOS_FOREX_PAPER_BOT.md")
FOREX_BACKTEST_PATH = Path("apps/trading_lab/trading_lab/forex_backtest.py")
FOREX_BACKTEST_TEST_PATH = Path("tests/trading_lab/test_forex_backtest.py")
FOREX_BACKTEST_DOC_PATH = Path("docs/orchestration/AIOS_FOREX_BACKTEST.md")
FOREX_LEDGER_PATH = Path("apps/trading_lab/trading_lab/forex_paper_ledger.py")
FOREX_LEDGER_TEST_PATH = Path("tests/trading_lab/test_forex_paper_ledger.py")
FOREX_LEDGER_DOC_PATH = Path("docs/orchestration/AIOS_FOREX_PAPER_LEDGER.md")
FOREX_SCAFFOLD_PATHS = (
    FOREX_BOT_PATH,
    FOREX_BOT_TEST_PATH,
    FOREX_BOT_DOC_PATH,
)
FOREX_BACKTEST_PATHS = (
    FOREX_BACKTEST_PATH,
    FOREX_BACKTEST_TEST_PATH,
    FOREX_BACKTEST_DOC_PATH,
)
FOREX_LEDGER_PATHS = (
    FOREX_LEDGER_PATH,
    FOREX_LEDGER_TEST_PATH,
    FOREX_LEDGER_DOC_PATH,
)

ValidatorRunner = Callable[[Path], dict[str, Any]]


def safety_flags() -> dict[str, bool]:
    return {
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
        "delete_reset": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "worker_launch": False,
        "runtime_launch": False,
        "scheduler": False,
        "daemon": False,
        "secrets": False,
        "broker_live_trading": False,
        "real_orders": False,
    }


def approval_required() -> dict[str, bool]:
    return {
        "local_paper_scaffold_apply": False,
        "git_add": True,
        "git_commit": True,
        "git_push": True,
        "merge": True,
        "secrets": True,
        "broker_live_trading": True,
        "scheduler_activation": True,
        "destructive_action": True,
        "queue_mutation": True,
        "approval_mutation": True,
        "worker_dispatch": True,
    }


def build_forex_bot_source() -> str:
    return '''from __future__ import annotations

from typing import Any


SUPPORTED_PAIRS = {"EURUSD", "GBPUSD", "USDJPY"}
SUPPORTED_DIRECTIONS = {"buy", "sell"}
MAX_RISK_PERCENT = 2.0

PAPER_SAFETY = {
    "paper_only": True,
    "execution_allowed": False,
    "broker_execution": False,
    "credential_use": False,
    "live_trading": False,
    "real_orders": False,
    "real_webhooks": False,
}


def blocked_decision(reason: str) -> dict[str, Any]:
    return {
        "allowed": False,
        "decision_type": "blocked",
        "blocked_reason": reason,
        **PAPER_SAFETY,
    }


def _unsafe_scope_reason(
    execution_mode: str,
    live_execution: bool,
    broker_order: bool,
    credentials: Any,
    real_order: bool,
    webhook_url: str | None,
) -> str | None:
    if execution_mode != "paper":
        return "execution_mode_must_be_paper"
    if live_execution:
        return "live_execution_blocked"
    if broker_order:
        return "broker_order_blocked"
    if credentials:
        return "credentials_blocked"
    if real_order:
        return "real_order_blocked"
    if webhook_url:
        return "real_webhook_blocked"
    return None


def validate_signal(
    pair: str,
    direction: str,
    entry_price: float,
    stop_loss: float | None,
    account_equity: float,
    max_risk_percent: float,
    *,
    execution_mode: str = "paper",
    live_execution: bool = False,
    broker_order: bool = False,
    credentials: Any = None,
    real_order: bool = False,
    webhook_url: str | None = None,
) -> dict[str, Any]:
    unsafe_reason = _unsafe_scope_reason(
        execution_mode=execution_mode,
        live_execution=live_execution,
        broker_order=broker_order,
        credentials=credentials,
        real_order=real_order,
        webhook_url=webhook_url,
    )
    if unsafe_reason:
        return blocked_decision(unsafe_reason)

    normalized_pair = str(pair).upper()
    normalized_direction = str(direction).lower()

    if normalized_pair not in SUPPORTED_PAIRS:
        return blocked_decision("unsupported_pair")
    if normalized_direction not in SUPPORTED_DIRECTIONS:
        return blocked_decision("unsupported_direction")
    if stop_loss is None:
        return blocked_decision("stop_loss_required")
    if account_equity <= 0:
        return blocked_decision("account_equity_must_be_positive")
    if entry_price <= 0 or stop_loss <= 0:
        return blocked_decision("prices_must_be_positive")
    if entry_price == stop_loss:
        return blocked_decision("stop_loss_must_differ_from_entry")
    if max_risk_percent <= 0 or max_risk_percent > MAX_RISK_PERCENT:
        return blocked_decision("max_risk_percent_exceeds_paper_limit")

    return {
        "allowed": True,
        "pair": normalized_pair,
        "direction": normalized_direction,
        "entry_price": float(entry_price),
        "stop_loss": float(stop_loss),
        "account_equity": float(account_equity),
        "max_risk_percent": float(max_risk_percent),
        **PAPER_SAFETY,
    }


def calculate_mock_position_size(
    account_equity: float,
    max_risk_percent: float,
    entry_price: float,
    stop_loss: float,
) -> dict[str, float]:
    risk_amount = float(account_equity) * (float(max_risk_percent) / 100.0)
    stop_distance = abs(float(entry_price) - float(stop_loss))
    if stop_distance == 0:
        return {"risk_amount": round(risk_amount, 2), "mock_units": 0.0}
    return {
        "risk_amount": round(risk_amount, 2),
        "mock_units": round(risk_amount / stop_distance, 2),
    }


def paper_decision(
    pair: str,
    direction: str,
    entry_price: float,
    stop_loss: float | None,
    account_equity: float,
    max_risk_percent: float,
    *,
    execution_mode: str = "paper",
    live_execution: bool = False,
    broker_order: bool = False,
    credentials: Any = None,
    real_order: bool = False,
    webhook_url: str | None = None,
) -> dict[str, Any]:
    validation = validate_signal(
        pair=pair,
        direction=direction,
        entry_price=entry_price,
        stop_loss=stop_loss,
        account_equity=account_equity,
        max_risk_percent=max_risk_percent,
        execution_mode=execution_mode,
        live_execution=live_execution,
        broker_order=broker_order,
        credentials=credentials,
        real_order=real_order,
        webhook_url=webhook_url,
    )
    if not validation["allowed"]:
        return validation

    position = calculate_mock_position_size(
        account_equity=validation["account_equity"],
        max_risk_percent=validation["max_risk_percent"],
        entry_price=validation["entry_price"],
        stop_loss=validation["stop_loss"],
    )
    return {
        "allowed": True,
        "decision_type": "paper_decision_only",
        "pair": validation["pair"],
        "direction": validation["direction"],
        "mock_position_size": position,
        "next_safe_action": "Review the paper decision locally. Do not route it to a broker.",
        **PAPER_SAFETY,
    }
'''


def build_forex_bot_test_source() -> str:
    return '''from __future__ import annotations

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
'''


def build_forex_bot_doc() -> str:
    return """# AIOS Forex Paper Bot

This generated scaffold is paper-only. It models a local Forex paper decision for
review and does not connect to a broker, credential store, real webhook, live
market feed, scheduler, worker dispatcher, or order route.

Supported pairs are EURUSD, GBPUSD, and USDJPY. Supported directions are buy and
sell. The bot blocks missing stop loss values, unsupported pairs, unsupported
directions, risk above the local paper limit, credentials, broker orders, live
execution, real orders, and real webhook routing.

The scaffold exists to prove that AIOS can apply one safe local build action,
run the focused validator, attempt one bounded repair when requested, and report
the result without staging, committing, pushing, dispatching workers, mutating
queues, or enabling live trading.
"""


def forex_scaffold_files() -> dict[Path, str]:
    return {
        FOREX_BOT_PATH: build_forex_bot_source(),
        FOREX_BOT_TEST_PATH: build_forex_bot_test_source(),
        FOREX_BOT_DOC_PATH: build_forex_bot_doc(),
    }


def build_forex_backtest_source() -> str:
    return '''from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


PAPER_BACKTEST_SAFETY = {
    "paper_only": True,
    "execution_allowed": False,
    "broker_execution": False,
    "credential_use": False,
    "live_trading": False,
    "real_orders": False,
    "real_webhooks": False,
}

BLOCKED_SCOPE_FIELDS = {
    "broker",
    "broker_order",
    "credentials",
    "api_key",
    "token",
    "live_execution",
    "real_order",
    "webhook_url",
    "real_webhook",
}


def _load_forex_paper_bot():
    try:
        from . import forex_paper_bot  # type: ignore

        return forex_paper_bot
    except ImportError:
        module_path = Path(__file__).with_name("forex_paper_bot.py")
        spec = importlib.util.spec_from_file_location("forex_paper_bot", module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module


def _blocked_scope_reason(candle: dict[str, Any]) -> str | None:
    for field in sorted(BLOCKED_SCOPE_FIELDS):
        if candle.get(field):
            return f"{field}_blocked"
    return None


def _paper_stop_loss(close: float, direction: str, candle: dict[str, Any]) -> float | None:
    if candle.get("stop_loss") is not None:
        return float(candle["stop_loss"])
    if direction == "buy":
        return round(close * 0.99, 6)
    if direction == "sell":
        return round(close * 1.01, 6)
    return None


def run_backtest(
    candles: list[dict[str, Any]],
    *,
    starting_balance: float = 10000.0,
    default_pair: str = "EURUSD",
    default_direction: str = "buy",
    max_risk_percent: float = 1.0,
) -> dict[str, Any]:
    bot = _load_forex_paper_bot()
    ending_balance = float(starting_balance)
    decisions: list[dict[str, Any]] = []
    trades_allowed = 0
    trades_blocked = 0

    for index, candle in enumerate(candles):
        blocked_scope = _blocked_scope_reason(candle)
        pair = str(candle.get("pair", default_pair)).upper()
        direction = str(candle.get("direction", default_direction)).lower()
        close = float(candle.get("close", candle.get("entry_price", 0)))
        stop_loss = _paper_stop_loss(close, direction, candle)

        if blocked_scope:
            trades_blocked += 1
            decisions.append(
                {
                    "index": index,
                    "allowed": False,
                    "blocked_reason": blocked_scope,
                    **PAPER_BACKTEST_SAFETY,
                }
            )
            continue

        decision = bot.paper_decision(
            pair=pair,
            direction=direction,
            entry_price=close,
            stop_loss=stop_loss,
            account_equity=ending_balance,
            max_risk_percent=max_risk_percent,
        )
        decision_record = {"index": index, **decision}
        if decision.get("allowed"):
            trades_allowed += 1
            risk_amount = decision["mock_position_size"]["risk_amount"]
            paper_result_r = float(candle.get("paper_result_r", 0.0))
            ending_balance += risk_amount * paper_result_r
        else:
            trades_blocked += 1
        decisions.append(decision_record)

    return {
        "trades_considered": len(candles),
        "trades_allowed": trades_allowed,
        "trades_blocked": trades_blocked,
        "ending_balance": round(ending_balance, 2),
        "decisions": decisions,
        **PAPER_BACKTEST_SAFETY,
    }
'''


def build_forex_backtest_test_source() -> str:
    return '''from __future__ import annotations

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
'''


def build_forex_backtest_doc() -> str:
    return """# AIOS Forex Backtest

This generated component is the second `forex-paper-bot` build step. It is a
deterministic, paper-only backtest helper that consumes local candle-like
dictionaries, calls the local Forex paper bot decision function, and returns a
summary for review.

The backtest summary includes `trades_considered`, `trades_allowed`,
`trades_blocked`, `ending_balance`, and `paper_only: true`.

The component blocks broker fields, credential fields, live execution flags,
real order fields, and real webhook fields. It does not mutate queues, approvals,
workers, runtime, schedulers, daemons, Git state, broker state, credentials, or
live trading paths.
"""


def build_forex_ledger_source() -> str:
    return '''from __future__ import annotations

from typing import Any


SUPPORTED_PAIRS = {"EURUSD", "GBPUSD", "USDJPY"}
SUPPORTED_DIRECTIONS = {"buy", "sell"}

PAPER_LEDGER_SAFETY = {
    "paper_only": True,
    "execution_allowed": False,
    "broker_execution": False,
    "credential_use": False,
    "live_trading": False,
    "real_orders": False,
    "real_webhooks": False,
}

BLOCKED_SCOPE_FIELDS = {
    "api_key",
    "broker_order",
    "credentials",
    "live_execution",
    "real_order",
    "webhook_url",
}


def blocked_record(reason: str) -> dict[str, Any]:
    return {
        "allowed": False,
        "record_type": "blocked",
        "blocked_reason": reason,
        **PAPER_LEDGER_SAFETY,
    }


def _pip_size(pair: str) -> float:
    return 0.01 if pair.endswith("JPY") else 0.0001


def _blocked_scope_reason(payload: dict[str, Any]) -> str | None:
    for field in sorted(BLOCKED_SCOPE_FIELDS):
        if payload.get(field):
            return f"{field}_blocked"
    return None


def _result_pips(pair: str, direction: str, entry: float, target: float) -> float:
    pip_size = _pip_size(pair)
    if direction == "buy":
        return round((target - entry) / pip_size, 1)
    return round((entry - target) / pip_size, 1)


def record_paper_trade(
    *,
    pair: str,
    direction: str,
    entry: float,
    stop: float,
    target: float,
    position_size: float,
    timestamp: str,
    live_execution: bool = False,
    broker_order: bool = False,
    credentials: Any = None,
    api_key: Any = None,
    real_order: bool = False,
    webhook_url: str | None = None,
) -> dict[str, Any]:
    payload = {
        "live_execution": live_execution,
        "broker_order": broker_order,
        "credentials": credentials,
        "api_key": api_key,
        "real_order": real_order,
        "webhook_url": webhook_url,
    }
    blocked_reason = _blocked_scope_reason(payload)
    if blocked_reason:
        return blocked_record(blocked_reason)

    normalized_pair = str(pair).upper()
    normalized_direction = str(direction).lower()
    if normalized_pair not in SUPPORTED_PAIRS:
        return blocked_record("unsupported_pair")
    if normalized_direction not in SUPPORTED_DIRECTIONS:
        return blocked_record("unsupported_direction")
    if position_size <= 0:
        return blocked_record("position_size_must_be_positive")

    entry_value = float(entry)
    stop_value = float(stop)
    target_value = float(target)
    size_value = float(position_size)
    result_pips = _result_pips(normalized_pair, normalized_direction, entry_value, target_value)
    if normalized_direction == "buy":
        pnl = (target_value - entry_value) * size_value
    else:
        pnl = (entry_value - target_value) * size_value

    return {
        "allowed": True,
        "record_type": "paper_trade",
        "pair": normalized_pair,
        "direction": normalized_direction,
        "entry": entry_value,
        "stop": stop_value,
        "target": target_value,
        "position_size": size_value,
        "result_pips": result_pips,
        "pnl": round(pnl, 2),
        "timestamp": timestamp,
        **PAPER_LEDGER_SAFETY,
    }


def summarize_paper_ledger(trades: list[dict[str, Any]]) -> dict[str, Any]:
    records = [record_paper_trade(**trade) for trade in trades]
    allowed_records = [record for record in records if record.get("allowed")]
    winning_trades = [record for record in allowed_records if record["pnl"] > 0]
    losing_trades = [record for record in allowed_records if record["pnl"] < 0]
    total_pnl = round(sum(record["pnl"] for record in allowed_records), 2)
    return {
        "trade_count": len(allowed_records),
        "winning_trades": len(winning_trades),
        "losing_trades": len(losing_trades),
        "blocked_trades": len(records) - len(allowed_records),
        "total_pnl": total_pnl,
        "records": records,
        **PAPER_LEDGER_SAFETY,
    }
'''


def build_forex_ledger_test_source() -> str:
    return '''from __future__ import annotations

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
'''


def build_forex_ledger_doc() -> str:
    return """# AIOS Forex Paper Ledger

This generated component is the third `forex-paper-bot` build step. It records
paper-only Forex trade outcomes for local review and does not create broker
orders, credential access, live execution, real orders, or real webhooks.

The ledger records pair, direction, entry, stop, target, position size,
deterministic result pips, paper PnL, and timestamp. The summary reports
`trade_count`, `winning_trades`, `losing_trades`, `total_pnl`, and
`paper_only: true`.

Unsupported pairs and unsafe live/broker/credential/order fields are blocked.
"""


def forex_backtest_files() -> dict[Path, str]:
    return {
        FOREX_BACKTEST_PATH: build_forex_backtest_source(),
        FOREX_BACKTEST_TEST_PATH: build_forex_backtest_test_source(),
        FOREX_BACKTEST_DOC_PATH: build_forex_backtest_doc(),
    }


def forex_ledger_files() -> dict[Path, str]:
    return {
        FOREX_LEDGER_PATH: build_forex_ledger_source(),
        FOREX_LEDGER_TEST_PATH: build_forex_ledger_test_source(),
        FOREX_LEDGER_DOC_PATH: build_forex_ledger_doc(),
    }


def write_text_if_changed(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def write_forex_scaffold(repo_root: Path) -> list[str]:
    files_written: list[str] = []
    for relative_path, content in forex_scaffold_files().items():
        target = repo_root / relative_path
        if write_text_if_changed(target, content):
            files_written.append(relative_path.as_posix())
    return files_written


def write_forex_backtest(repo_root: Path) -> list[str]:
    files_written: list[str] = []
    for relative_path, content in forex_backtest_files().items():
        target = repo_root / relative_path
        if write_text_if_changed(target, content):
            files_written.append(relative_path.as_posix())
    return files_written


def write_forex_ledger(repo_root: Path) -> list[str]:
    files_written: list[str] = []
    for relative_path, content in forex_ledger_files().items():
        target = repo_root / relative_path
        if write_text_if_changed(target, content):
            files_written.append(relative_path.as_posix())
    return files_written


def run_forex_bot_validator(repo_root: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        FOREX_BOT_TEST_PATH.as_posix(),
    ]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "name": "forex_paper_bot_tests",
        "command": " ".join(command),
        "returncode": completed.returncode,
        "passed": completed.returncode == 0,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
    }


def run_forex_backtest_validator(repo_root: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        FOREX_BACKTEST_TEST_PATH.as_posix(),
    ]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "name": "forex_backtest_tests",
        "command": " ".join(command),
        "returncode": completed.returncode,
        "passed": completed.returncode == 0,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
    }


def run_forex_ledger_validator(repo_root: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-p",
        "no:cacheprovider",
        FOREX_LEDGER_TEST_PATH.as_posix(),
    ]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "name": "forex_paper_ledger_tests",
        "command": " ".join(command),
        "returncode": completed.returncode,
        "passed": completed.returncode == 0,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
    }


def blocked_report(goal: str, mode: str, reason: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "goal": goal,
        "mode": mode,
        "files_written": [],
        "validators_run": [],
        "repair_attempts": 0,
        "result": "blocked",
        "blocked_reason": reason,
        "next_safe_action": "Choose a supported local paper-only goal.",
        "approval_required": approval_required(),
        "safety": safety_flags(),
    }


def select_forex_continue_action(repo_root: Path) -> str:
    if not (repo_root / FOREX_BOT_PATH).exists():
        return "build_scaffold"
    if not (repo_root / FOREX_BACKTEST_PATH).exists():
        return "build_backtest"
    if not (repo_root / FOREX_LEDGER_PATH).exists():
        return "build_ledger"
    return "done"


def _apply_writer_for_action(repo_root: Path, action: str) -> tuple[list[str], ValidatorRunner | None]:
    if action == "build_scaffold":
        return write_forex_scaffold(repo_root), run_forex_bot_validator
    if action == "build_backtest":
        return write_forex_backtest(repo_root), run_forex_backtest_validator
    if action == "build_ledger":
        return write_forex_ledger(repo_root), run_forex_ledger_validator
    return [], None


def _repair_for_action(repo_root: Path, action: str) -> list[str]:
    if action == "build_scaffold":
        return write_forex_scaffold(repo_root)
    if action == "build_backtest":
        return write_forex_backtest(repo_root)
    if action == "build_ledger":
        return write_forex_ledger(repo_root)
    return []


def execute_goal(
    repo_root: Path,
    goal: str,
    *,
    apply: bool = False,
    continue_goal: bool = False,
    max_repairs: int = 0,
    validator_runner: ValidatorRunner | None = None,
) -> dict[str, Any]:
    mode = "APPLY" if apply else "DRY_RUN"
    if goal not in SUPPORTED_GOALS:
        return blocked_report(goal, mode, "unsupported_goal")

    if max_repairs < 0:
        return blocked_report(goal, mode, "max_repairs_must_be_non_negative")

    report = {
        "schema": SCHEMA,
        "goal": goal,
        "mode": mode,
        "files_written": [],
        "validators_run": [],
        "repair_attempts": 0,
        "continue_action": select_forex_continue_action(repo_root) if continue_goal else "build_scaffold",
        "result": "preview_only",
        "next_safe_action": "Run with --apply only inside an approved local write boundary.",
        "approval_required": approval_required(),
        "safety": safety_flags(),
    }

    if not apply:
        return report

    action = report["continue_action"]
    if action == "done":
        report["result"] = "DONE"
        report["next_safe_action"] = "Forex paper bot scaffold, backtest, and ledger already exist. Review validators before the next build step."
        return report

    files_written, default_runner = _apply_writer_for_action(repo_root, action)
    runner = validator_runner or default_runner
    report["files_written"] = files_written
    if runner is None:
        report["result"] = "blocked"
        report["blocked_reason"] = "no_validator_for_continue_action"
        return report

    validation = runner(repo_root)
    report["validators_run"].append(validation)

    while not validation.get("passed", False) and report["repair_attempts"] < max_repairs:
        report["repair_attempts"] += 1
        repaired_files = _repair_for_action(repo_root, action)
        for relative_path in repaired_files:
            if relative_path not in report["files_written"]:
                report["files_written"].append(relative_path)
        validation = runner(repo_root)
        report["validators_run"].append(validation)

    if validation.get("passed", False):
        report["result"] = "passed"
        report["next_safe_action"] = "Review the paper-only scaffold diff. Commit and push still require Anthony approval."
    else:
        report["result"] = "failed"
        report["next_safe_action"] = "Inspect the validator output before attempting another bounded repair."

    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one bounded AIOS autonomy execute goal.")
    parser.add_argument("--goal", required=True, help="Goal to execute. Supported: forex-paper-bot.")
    parser.add_argument("--continue", dest="continue_goal", action="store_true", help="Continue the next missing goal component.")
    parser.add_argument("--apply", action="store_true", help="Write the supported local scaffold and run validators.")
    parser.add_argument("--max-repairs", type=int, default=0, help="Maximum bounded repair attempts.")
    parser.add_argument("--repo-root", default=None, help="Optional repository root for tests or sandbox runs.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[2]
    report = execute_goal(
        repo_root=repo_root,
        goal=args.goal,
        apply=args.apply,
        continue_goal=args.continue_goal,
        max_repairs=args.max_repairs,
    )
    print(json.dumps(report, indent=2, sort_keys=False))
    return 0 if report["result"] in {"passed", "preview_only", "blocked", "DONE"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
