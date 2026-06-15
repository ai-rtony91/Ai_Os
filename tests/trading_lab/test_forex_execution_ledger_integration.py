from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_execution_ledger_integration.py"


def load_module():
    spec = importlib.util.spec_from_file_location("forex_execution_ledger_integration", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def execution(action: str = "buy") -> dict[str, object]:
    return {
        "allowed": True,
        "executed": action != "hold",
        "paper_order_id": f"PAPER-EURUSD-{action.upper()}-123",
        "pair": "EURUSD",
        "action": action,
        "filled_units": 1000 if action != "hold" else 0,
        "fill_price": 1.1002 if action != "hold" else None,
        "slippage_pips": 0.5,
        "spread_pips": 2.0,
        "paper_only": True,
    }


def test_module_imports():
    module = load_module()
    assert callable(module.build_execution_ledger_record)


def test_buy_execution_creates_ledger_record():
    module = load_module()
    record = module.build_execution_ledger_record(
        execution("buy"),
        {"pair": "EURUSD", "action": "buy"},
        metadata={"exit_price": 1.1012},
    )
    assert record["allowed"] is True
    assert record["status"] == "filled"
    assert record["ledger_event_type"] == "paper_execution_fill"
    assert record["realized_pnl"] == 1.0
    assert record["paper_only"] is True


def test_sell_execution_creates_ledger_record():
    module = load_module()
    sell = {**execution("sell"), "fill_price": 1.1002}
    record = module.build_execution_ledger_record(
        sell,
        {"pair": "EURUSD", "action": "sell"},
        metadata={"exit_price": 1.0992},
    )
    assert record["allowed"] is True
    assert record["action"] == "sell"
    assert record["realized_pnl"] == 1.0
    assert record["source"] == "forex_paper_execution_simulator"


def test_hold_creates_no_fill_hold_event():
    module = load_module()
    record = module.build_execution_ledger_record(
        execution("hold"),
        {"pair": "EURUSD", "action": "hold"},
    )
    assert record["allowed"] is True
    assert record["status"] == "no_fill_hold"
    assert record["ledger_event_type"] == "paper_hold"
    assert record["filled_units"] == 0


def test_execution_not_allowed_blocked():
    module = load_module()
    record = module.build_execution_ledger_record(
        {**execution("buy"), "allowed": False},
        {"pair": "EURUSD", "action": "buy"},
    )
    assert record["allowed"] is False
    assert record["blocked_reason"] == "execution_not_allowed"


def test_missing_paper_order_id_blocked():
    module = load_module()
    blocked = execution("buy")
    blocked.pop("paper_order_id")
    record = module.build_execution_ledger_record(blocked, {"pair": "EURUSD", "action": "buy"})
    assert record["blocked_reason"] == "missing_paper_order_id"


def test_missing_fill_price_blocked_for_buy_sell():
    module = load_module()
    blocked = {**execution("buy"), "fill_price": None}
    record = module.build_execution_ledger_record(blocked, {"pair": "EURUSD", "action": "buy"})
    assert record["blocked_reason"] == "missing_fill_price"


def test_invalid_pair_blocked():
    module = load_module()
    record = module.build_execution_ledger_record(
        {**execution("buy"), "pair": "AUDUSD"},
        {"pair": "AUDUSD", "action": "buy"},
    )
    assert record["blocked_reason"] == "invalid_pair"


def test_unsupported_action_blocked():
    module = load_module()
    record = module.build_execution_ledger_record(
        {**execution("buy"), "action": "scale"},
        {"pair": "EURUSD", "action": "scale"},
    )
    assert record["blocked_reason"] == "unsupported_action"


def test_unsafe_flags_blocked():
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
        record = module.build_execution_ledger_record(
            execution("buy"),
            {"pair": "EURUSD", "action": "buy"},
            **{flag: True},
        )
        assert record["allowed"] is False
        assert record["blocked_reason"] == f"safety_flag_{flag}"
        assert record["safety"][flag] is True


def test_source_has_no_network_file_write_or_subprocess_usage():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["subprocess", "requests", "socket", "urllib", "http.client", "write_text", "open("]:
        assert forbidden not in source
