from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_paper_execution_simulator.py"


def load_module():
    spec = importlib.util.spec_from_file_location("forex_paper_execution_simulator", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def safe_risk(pair: str = "EURUSD", action: str = "buy", units: int = 1000) -> dict[str, object]:
    return {
        "allowed": True,
        "pair": pair,
        "action": action,
        "position_size_units": units,
        "paper_only": True,
    }


def market() -> dict[str, object]:
    return {
        "EURUSD": {"bid": 1.1000, "ask": 1.1002},
        "GBPUSD": {"bid": 1.2500, "ask": 1.2503},
        "USDJPY": {"bid": 155.10, "ask": 155.12},
    }


def test_module_imports():
    module = load_module()
    assert callable(module.simulate_paper_execution)


def test_buy_execution_fills_deterministically():
    module = load_module()
    first = module.simulate_paper_execution(
        {"pair": "EURUSD", "action": "buy", "position_size_units": 1000},
        safe_risk(),
        market(),
        {"slippage_pips": 0.5, "max_spread_pips": 3.0, "max_slippage_pips": 1.0},
    )
    second = module.simulate_paper_execution(
        {"pair": "EURUSD", "action": "buy", "position_size_units": 1000},
        safe_risk(),
        market(),
        {"slippage_pips": 0.5, "max_spread_pips": 3.0, "max_slippage_pips": 1.0},
    )
    assert first["allowed"] is True
    assert first["executed"] is True
    assert first["filled_units"] == 1000
    assert first["requested_price"] == 1.1002
    assert first["fill_price"] == 1.10025
    assert first["paper_order_id"] == second["paper_order_id"]


def test_sell_execution_fills_deterministically():
    module = load_module()
    result = module.simulate_paper_execution(
        {"pair": "GBPUSD", "action": "sell", "position_size_units": 2000},
        safe_risk("GBPUSD", "sell", 2000),
        market(),
        {"slippage_pips": 0.5, "max_spread_pips": 4.0, "max_slippage_pips": 1.0},
    )
    assert result["allowed"] is True
    assert result["executed"] is True
    assert result["filled_units"] == 2000
    assert result["requested_price"] == 1.25
    assert result["fill_price"] == 1.24995
    assert result["execution_quality"]["accepted"] is True


def test_hold_does_not_execute_and_remains_allowed():
    module = load_module()
    result = module.simulate_paper_execution(
        {"pair": "USDJPY", "action": "hold", "position_size_units": 0},
        safe_risk("USDJPY", "hold", 0),
        market(),
    )
    assert result["allowed"] is True
    assert result["executed"] is False
    assert result["requested_units"] == 0
    assert result["filled_units"] == 0
    assert result["fill_price"] is None


def test_risk_control_blocked_input_blocks_execution():
    module = load_module()
    result = module.simulate_paper_execution(
        {"pair": "EURUSD", "action": "buy", "position_size_units": 1000},
        {"allowed": False, "blocked_reason": "risk_percent_limit_exceeded"},
        market(),
    )
    assert result["allowed"] is False
    assert result["blocked_reason"] == "risk_controls_blocked"
    assert result["executed"] is False


def test_invalid_pair_blocked():
    module = load_module()
    result = module.simulate_paper_execution(
        {"pair": "AUDUSD", "action": "buy", "position_size_units": 1000},
        safe_risk("AUDUSD", "buy", 1000),
        market(),
    )
    assert result["blocked_reason"] == "invalid_pair"


def test_unsupported_action_blocked():
    module = load_module()
    result = module.simulate_paper_execution(
        {"pair": "EURUSD", "action": "short", "position_size_units": 1000},
        safe_risk(),
        market(),
    )
    assert result["blocked_reason"] == "unsupported_action"


def test_missing_market_price_blocked():
    module = load_module()
    result = module.simulate_paper_execution(
        {"pair": "EURUSD", "action": "buy", "position_size_units": 1000},
        safe_risk(),
        {"EURUSD": {"bid": 1.1000}},
    )
    assert result["blocked_reason"] == "missing_market_price"


def test_spread_limit_blocked():
    module = load_module()
    result = module.simulate_paper_execution(
        {"pair": "EURUSD", "action": "buy", "position_size_units": 1000},
        safe_risk(),
        {"EURUSD": {"bid": 1.1000, "ask": 1.1005}},
        {"max_spread_pips": 2.0},
    )
    assert result["blocked_reason"] == "spread_limit_exceeded"


def test_slippage_limit_blocked():
    module = load_module()
    result = module.simulate_paper_execution(
        {"pair": "EURUSD", "action": "buy", "position_size_units": 1000},
        safe_risk(),
        market(),
        {"slippage_pips": 2.0, "max_slippage_pips": 1.0},
    )
    assert result["blocked_reason"] == "slippage_limit_exceeded"


def test_safety_flags_block_execution():
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
        result = module.simulate_paper_execution(
            {"pair": "EURUSD", "action": "buy", "position_size_units": 1000},
            safe_risk(),
            market(),
            **{flag: True},
        )
        assert result["allowed"] is False
        assert result["blocked_reason"] == f"safety_flag_{flag}"
        assert result["safety"][flag] is True


def test_source_has_no_network_file_write_or_subprocess_usage():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["subprocess", "requests", "socket", "urllib", "http.client", "write_text", "open("]:
        assert forbidden not in source
