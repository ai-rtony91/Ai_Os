from __future__ import annotations

import inspect

from automation.forex_engine import demo_order_mapping as dom


def _approved_preview() -> dict:
    return {
        "allowed": True,
        "decision": "allowed",
        "approval_state": "paper_preview_ready",
        "preview_id": "preview-eurusd-buy-1",
        "pair": "EURUSD",
        "direction": "buy",
        "entry_type": "market",
        "entry_price": 1.1,
        "stop_loss": 1.095,
        "take_profit": 1.11,
        "units": 1000.0,
        "paper_only": True,
    }


def _readonly_state() -> dict:
    return {
        "allowed": True,
        "decision": "allowed",
        "mode": "DEMO_READONLY",
        "fresh": True,
        "demo_readonly": True,
        "paper_only": True,
        "safety": {
            "paper_only": True,
            "demo_readonly": True,
            "broker_write": False,
            "live_trading": False,
            "credentials": False,
            "real_orders": False,
            "network_submit": False,
        },
    }


def test_valid_preview_maps_to_demo_order_intent() -> None:
    result = dom.build_demo_order_intent(_approved_preview(), _readonly_state())

    assert result["allowed"] is True
    assert result["decision"] == dom.DECISION_ALLOWED
    intent = result["demo_order_intent"]
    assert intent["pair"] == "EUR_USD"
    assert intent["side"] == "BUY"
    assert intent["units"] == 1000.0
    assert intent["order_type"] == "MARKET"
    assert intent["entry_price"] == 1.1
    assert intent["stop_loss"] == 1.095
    assert intent["take_profit"] == 1.11
    assert intent["mode"] == dom.DEMO_MAPPING_MODE
    assert intent["submit_enabled"] is False
    assert intent["broker_write_enabled"] is False
    assert intent["live_trading"] is False


def test_paper_fill_maps_when_sanitized_fields_present() -> None:
    fill = {
        "allowed": True,
        "fill_id": "fill-eurusd-buy-1",
        "pair": "EUR_USD",
        "direction": "buy",
        "entry_type": "market",
        "requested_price": 1.1,
        "filled_units": 500,
        "trade": {"stop_loss": 1.095, "take_profit": 1.11},
    }

    result = dom.build_demo_order_intent(fill, _readonly_state())

    assert result["allowed"] is True
    assert result["demo_order_intent"]["client_order_id"] == "fill-eurusd-buy-1"
    assert result["demo_order_intent"]["units"] == 500.0


def test_blocked_submit_and_write_flags() -> None:
    for field, reason in (
        ("broker_write_enabled", dom.REASON_BROKER_WRITE_ENABLED),
        ("order_submit_enabled", dom.REASON_ORDER_SUBMIT_ENABLED),
        ("network_submit_enabled", dom.REASON_NETWORK_SUBMIT_ENABLED),
    ):
        preview = _approved_preview()
        preview[field] = True
        result = dom.build_demo_order_intent(preview, _readonly_state())
        assert result["allowed"] is False
        assert reason in result["blocked_reasons"]


def test_account_identifier_credentials_and_live_flags_block() -> None:
    cases = (
        ("account_id", "101-222-333333-001", dom.REASON_ACCOUNT_ID_PRESENT),
        ("credentials_loaded", True, dom.REASON_CREDENTIALS_LOADED),
        ("live_trading_enabled", True, dom.REASON_LIVE_TRADING_ENABLED),
        ("order_submit_enabled", True, dom.REASON_ORDER_SUBMIT_ENABLED),
    )
    for field, value, reason in cases:
        preview = _approved_preview()
        preview[field] = value
        result = dom.build_demo_order_intent(preview, _readonly_state())
        assert result["allowed"] is False
        assert reason in result["blocked_reasons"]


def test_preview_must_be_allowed_and_ready() -> None:
    preview = _approved_preview()
    preview["allowed"] = False
    preview["approval_state"] = "blocked"

    result = dom.build_demo_order_intent(preview, _readonly_state())

    assert result["allowed"] is False
    assert dom.REASON_PREVIEW_NOT_ALLOWED in result["blocked_reasons"]
    assert dom.REASON_APPROVAL_NOT_READY in result["blocked_reasons"]


def test_connector_must_be_allowed_and_fresh() -> None:
    connector = _readonly_state()
    connector["allowed"] = False
    connector["fresh"] = False

    result = dom.build_demo_order_intent(_approved_preview(), connector)

    assert result["allowed"] is False
    assert dom.REASON_CONNECTOR_NOT_ALLOWED in result["blocked_reasons"]
    assert dom.REASON_STALE_READONLY_DATA in result["blocked_reasons"]


def test_invalid_mapping_fields_block() -> None:
    preview = _approved_preview()
    preview["units"] = 0
    preview["stop_loss"] = None
    preview["take_profit"] = None
    preview["pair"] = "AUDUSD"
    preview["direction"] = "hold"
    preview["entry_type"] = "limit"

    result = dom.build_demo_order_intent(preview, _readonly_state())

    assert result["allowed"] is False
    assert dom.REASON_INVALID_UNITS in result["blocked_reasons"]
    assert dom.REASON_MISSING_STOP_LOSS in result["blocked_reasons"]
    assert dom.REASON_MISSING_TAKE_PROFIT in result["blocked_reasons"]
    assert dom.REASON_UNSUPPORTED_PAIR in result["blocked_reasons"]
    assert dom.REASON_UNSUPPORTED_SIDE in result["blocked_reasons"]
    assert dom.REASON_UNSUPPORTED_ORDER_TYPE in result["blocked_reasons"]


def test_idempotency_key_is_deterministic() -> None:
    first = dom.build_demo_order_intent(_approved_preview(), _readonly_state())
    second = dom.build_demo_order_intent(_approved_preview(), _readonly_state())

    assert first["demo_order_intent"]["idempotency_key"] == second["demo_order_intent"]["idempotency_key"]
    assert first["demo_order_intent"]["idempotency_key"].startswith("demo-map-")


def test_safety_dict_present() -> None:
    result = dom.build_demo_order_intent(_approved_preview(), _readonly_state())
    safety = result["demo_order_intent"]["safety"]

    assert safety["paper_only"] is True
    assert safety["demo_mapping_only"] is True
    assert safety["submit_enabled"] is False
    assert safety["broker_write_enabled"] is False
    assert safety["live_trading"] is False
    assert safety["credentials"] is False
    assert safety["real_orders"] is False
    assert safety["network_submit"] is False


def test_source_scan_has_no_broker_network_filesystem_or_sensitive_access() -> None:
    source = inspect.getsource(dom).lower()
    banned = (
        "import subprocess",
        "from subprocess",
        "import requests",
        "from requests",
        "import socket",
        "from socket",
        "import urllib",
        "from urllib",
        "import pathlib",
        "from pathlib",
        "open(",
        ".write(",
        "write_text(",
        "write_bytes(",
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
        "oanda",
        "broker_sdk",
    )
    for token in banned:
        assert token not in source
