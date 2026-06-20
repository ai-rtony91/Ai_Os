"""Tests for paper-only position sizing."""
from __future__ import annotations

import ast
import inspect

from automation.forex_engine import position_sizing as ps


def _base_preview() -> dict:
    return {
        "paper_only": True,
        "pair": "EURUSD",
        "direction": "buy",
        "entry_price": 1.1000,
        "stop_loss": 1.0950,
        "risk_percent": 1.0,
    }


def test_module_imports():
    assert ps.POSITION_SIZING_MODE == "PAPER_ONLY"
    assert ps.POSITION_SIZE_ALLOWED == "allowed"
    assert ps.POSITION_SIZE_BLOCKED == "blocked"


def test_default_result_shape():
    result = ps.calculate_position_size(_base_preview(), account_state={"equity": 10000})
    assert result["paper_only"] is True
    assert result["mode"] == ps.POSITION_SIZING_MODE
    assert result["pair"] == "EURUSD"
    assert set(
        [
            "allowed",
            "decision",
            "blocked_reason",
            "blocked_reasons",
            "warnings",
            "paper_only",
            "mode",
            "pair",
            "direction",
            "entry_price",
            "stop_loss",
            "stop_distance",
            "risk_base",
            "risk_percent",
            "risk_dollars",
            "pip_value",
            "raw_units",
            "units",
            "min_units",
            "max_units",
            "rounding_increment",
            "estimated_loss_at_stop",
            "safety",
            "next_safe_action",
            "metadata",
        ]
    ).issubset(set(result.keys()))
    assert result["safety"] == {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def test_valid_sizing_from_balance_and_risk_percent():
    result = ps.calculate_position_size(
        _base_preview(),
        account_state={"current_balance": 5000.0, "equity": 7500.0},
    )
    assert result["allowed"] is True
    assert result["decision"] == ps.POSITION_SIZE_ALLOWED
    assert result["risk_base"] == 7500.0
    assert result["risk_dollars"] == 75.0
    assert result["raw_units"] == 15000.0
    assert result["units"] == 15000.0
    assert result["estimated_loss_at_stop"] == result["units"] * 0.005 * 1.0


def test_equity_preferred_over_cash_balance():
    result = ps.calculate_position_size(
        _base_preview(),
        account_state={"cash_balance": 1000.0, "equity": 2500.0, "current_balance": 3000.0},
    )
    assert result["risk_base"] == 2500.0


def test_explicit_risk_dollars_override():
    preview = _base_preview()
    preview["risk_dollars"] = 40.0
    result = ps.calculate_position_size(preview, account_state={})
    assert result["allowed"] is True
    assert result["risk_percent"] == preview["risk_percent"]
    assert result["risk_dollars"] == 40.0
    assert result["raw_units"] == 8000.0


def test_zero_stop_distance_blocked():
    preview = _base_preview()
    preview["entry_price"] = 1.1000
    preview["stop_loss"] = 1.1000
    result = ps.calculate_position_size(preview, account_state={"equity": 10000})
    assert result["allowed"] is False
    assert ps.REASON_INVALID_STOP_DISTANCE in result["blocked_reasons"]
    assert result["decision"] == ps.POSITION_SIZE_BLOCKED


def test_negative_stop_loss_blocked():
    preview = _base_preview()
    preview["stop_loss"] = -1.0950
    result = ps.calculate_position_size(preview, account_state={"equity": 10000})
    assert result["allowed"] is False
    assert ps.REASON_INVALID_STOP_LOSS in result["blocked_reasons"]


def test_missing_balance_blocked():
    result = ps.calculate_position_size(_base_preview())
    assert result["allowed"] is False
    assert result["blocked_reason"] == ps.REASON_MISSING_BALANCE
    assert ps.REASON_MISSING_BALANCE in result["blocked_reasons"]


def test_negative_balance_blocked():
    result = ps.calculate_position_size(_base_preview(), account_state={"equity": -100.0})
    assert result["allowed"] is False
    assert result["blocked_reason"] == ps.REASON_INVALID_ACCOUNT_STATE


def test_excessive_risk_percent_blocked():
    preview = _base_preview()
    preview["risk_percent"] = 99.0
    result = ps.calculate_position_size(preview, account_state={"equity": 10000}, limits={"max_risk_percent": 1.0})
    assert result["allowed"] is False
    assert ps.REASON_RISK_EXCEEDS_CAP in result["blocked_reasons"]


def test_excessive_risk_dollars_blocked():
    preview = _base_preview()
    preview["risk_dollars"] = 9999.0
    result = ps.calculate_position_size(
        preview,
        account_state={"equity": 10000},
        limits={"max_risk_dollars": 100.0},
    )
    assert result["allowed"] is False
    assert ps.REASON_RISK_EXCEEDS_CAP in result["blocked_reasons"]
    assert result["risk_dollars"] == 9999.0


def test_max_units_cap_blocked():
    result = ps.calculate_position_size(
        _base_preview(),
        account_state={"equity": 10000},
        limits={"max_units": 10.0},
    )
    assert result["allowed"] is False
    assert ps.REASON_MAX_UNITS_EXCEEDED in result["blocked_reasons"]

    assert result["raw_units"] > result["max_units"]


def test_min_units_not_met_blocked():
    result = ps.calculate_position_size(
        _base_preview(),
        account_state={"equity": 10.0},
        limits={"min_units": 100.0},
    )
    assert result["allowed"] is False
    assert ps.REASON_MIN_UNITS_NOT_MET in result["blocked_reasons"]


def test_unsupported_pair_blocked():
    preview = _base_preview()
    preview["pair"] = "XAUUSD"
    result = ps.calculate_position_size(preview, account_state={"equity": 10000})
    assert result["allowed"] is False
    assert ps.REASON_UNSUPPORTED_PAIR in result["blocked_reasons"]


def test_invalid_pip_value_blocked():
    result = ps.calculate_position_size(
        _base_preview(),
        account_state={"equity": 10000},
        pair_config={"EURUSD": {"pip_value_per_unit": -1.0}},
    )
    assert result["allowed"] is False
    assert ps.REASON_INVALID_PIP_VALUE in result["blocked_reasons"]


def test_rounding_increment_floors_units():
    result = ps.calculate_position_size(
        _base_preview(),
        account_state={"equity": 10000},
        limits={"rounding_increment": 10.0, "allow_fractional_units": False},
    )
    assert result["allowed"] is True
    assert result["raw_units"] == 20000.0
    assert result["units"] == 20000.0
    assert result["units"] % 10.0 == 0.0


def test_fractional_units_disabled_by_default():
    result = ps.calculate_position_size(_base_preview(), account_state={"equity": 10000})
    assert result["allowed"] is True
    assert result["units"] % 1 == 0.0


def test_fractional_units_allowed():
    result = ps.calculate_position_size(
        _base_preview(),
        account_state={"equity": 10000},
        limits={"rounding_increment": 0.1, "allow_fractional_units": True},
    )
    assert result["allowed"] is True
    assert abs(result["units"] % 0.1) < 1e-8 or abs((result["units"] % 0.1) - 0.1) < 1e-8


def test_paper_only_false_blocks():
    preview = _base_preview()
    preview["paper_only"] = False
    result = ps.calculate_position_size(preview, account_state={"equity": 10000})
    assert result["allowed"] is False
    assert ps.REASON_NON_PAPER_MODE in result["blocked_reasons"]


def test_live_mode_blocked():
    preview = _base_preview()
    preview["mode"] = "live"
    result = ps.calculate_position_size(preview, account_state={"equity": 10000})
    assert result["allowed"] is False
    assert ps.REASON_NON_PAPER_MODE in result["blocked_reasons"]


def test_multiple_blocked_reasons_deterministic_order():
    preview = _base_preview()
    preview["mode"] = "live"
    preview["risk_percent"] = 99.0
    result = ps.calculate_position_size(
        preview,
        account_state={"equity": -100.0},
        limits={"max_risk_percent": 1.0},
    )
    assert result["allowed"] is False
    assert result["blocked_reasons"] == [
        ps.REASON_INVALID_ACCOUNT_STATE,
        ps.REASON_NON_PAPER_MODE,
        ps.REASON_RISK_EXCEEDS_CAP,
    ]


def test_estimated_loss_at_stop_deterministic():
    result = ps.calculate_position_size(_base_preview(), account_state={"equity": 10000})
    assert result["estimated_loss_at_stop"] == result["units"] * result["stop_distance"] * result["pip_value"]


def test_result_includes_risk_base_and_units():
    result = ps.calculate_position_size(_base_preview(), account_state={"equity": 10000})
    assert "risk_base" in result
    assert result["raw_units"] >= result["min_units"]
    assert result["units"] <= (result["max_units"] if result["max_units"] > 0 else result["raw_units"])


def test_position_sizing_source_scan_no_network_or_io():
    source = inspect.getsource(ps)
    banned = (
        "import subprocess",
        "from subprocess",
        "import requests",
        "from requests",
        "import socket",
        "from socket",
        "import urllib",
        "from urllib",
        "open(",
        ".write_text",
        ".write_bytes",
        "import pathlib",
        "from pathlib",
        "os.system",
        "os.getenv",
        "os.environ",
        "getenv(",
        "environ[",
        "api_key",
        "access_token",
        "refresh_token",
        "private_key",
        "password",
        "bearer ",
    )
    for token in banned:
        assert token not in source
