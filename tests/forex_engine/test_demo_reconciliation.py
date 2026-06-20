from __future__ import annotations

import inspect

from automation.forex_engine import demo_reconciliation as dr


def _snapshot() -> dict:
    return {
        "allowed": True,
        "decision": "allowed",
        "mode": "DEMO_READONLY",
        "fresh": True,
        "prices": [{"instrument": "EUR_USD", "bid": 1.0998, "ask": 1.1002}],
        "positions_summary": [
            {
                "instrument": "EUR_USD",
                "side": "BUY",
                "units": 1000.0,
                "entry_price": 1.1,
                "stop_loss": 1.095,
                "take_profit": 1.11,
            }
        ],
        "orders": [
            {
                "instrument": "EUR_USD",
                "side": "BUY",
                "units": 1000.0,
                "entry_price": 1.1,
                "stop_loss": 1.095,
                "take_profit": 1.11,
            }
        ],
    }


def _intent() -> dict:
    return {
        "pair": "EUR_USD",
        "side": "BUY",
        "units": 1000.0,
        "order_type": "MARKET",
        "entry_price": 1.1,
        "stop_loss": 1.095,
        "take_profit": 1.11,
        "client_order_id": "preview-eurusd-buy-1",
        "idempotency_key": "demo-map-example",
        "mode": "DEMO_MAPPING_ONLY",
        "submit_enabled": False,
        "broker_write_enabled": False,
        "live_trading": False,
    }


def test_valid_match_reports_matched() -> None:
    result = dr.reconcile_demo_snapshot(_snapshot(), _intent())

    assert result["allowed"] is True
    assert result["decision"] == dr.DECISION_ALLOWED
    assert result["matched"] is True
    assert result["match_score"] == 1.0
    assert result["pair_match"] is True
    assert result["side_match"] is True
    assert result["units_match"] is True
    assert result["price_within_tolerance"] is True
    assert result["stop_loss_match"] is True
    assert result["take_profit_match"] is True
    assert result["position_seen"] is True
    assert result["order_seen"] is True
    assert result["mismatches"] == []


def test_units_mismatch_reports_evidence() -> None:
    snapshot = _snapshot()
    snapshot["positions_summary"][0]["units"] = 999.0
    snapshot["orders"][0]["units"] = 999.0

    result = dr.reconcile_demo_snapshot(snapshot, _intent())

    assert result["allowed"] is True
    assert result["matched"] is False
    assert result["units_match"] is False
    assert "units_match" in result["mismatches"]


def test_pair_mismatch_reports_evidence() -> None:
    intent = _intent()
    intent["pair"] = "GBP_USD"

    result = dr.reconcile_demo_snapshot(_snapshot(), intent)

    assert result["allowed"] is True
    assert result["matched"] is False
    assert result["pair_match"] is False
    assert "pair_match" in result["mismatches"]


def test_side_mismatch_reports_evidence() -> None:
    snapshot = _snapshot()
    snapshot["positions_summary"][0]["side"] = "SELL"
    snapshot["orders"][0]["side"] = "SELL"

    result = dr.reconcile_demo_snapshot(snapshot, _intent())

    assert result["allowed"] is True
    assert result["matched"] is False
    assert result["side_match"] is False


def test_price_tolerance_mismatch_reports_evidence() -> None:
    snapshot = _snapshot()
    snapshot["positions_summary"][0]["entry_price"] = 1.2
    snapshot["orders"][0]["entry_price"] = 1.2

    result = dr.reconcile_demo_snapshot(snapshot, _intent(), price_tolerance=0.0001)

    assert result["allowed"] is True
    assert result["matched"] is False
    assert result["price_within_tolerance"] is False
    assert "price_within_tolerance" in result["mismatches"]


def test_stale_snapshot_blocks() -> None:
    snapshot = _snapshot()
    snapshot["fresh"] = False

    result = dr.reconcile_demo_snapshot(snapshot, _intent())

    assert result["allowed"] is False
    assert dr.REASON_STALE_DATA in result["blocked_reasons"]
    assert result["stale_data"] is True


def test_missing_intent_blocks() -> None:
    result = dr.reconcile_demo_snapshot(_snapshot(), {})

    assert result["allowed"] is False
    assert dr.REASON_INVALID_INTENT in result["blocked_reasons"]
    assert dr.REASON_MISSING_PAIR in result["blocked_reasons"]
    assert dr.REASON_MISSING_SIDE in result["blocked_reasons"]
    assert dr.REASON_MISSING_UNITS in result["blocked_reasons"]


def test_account_identifier_blocks() -> None:
    snapshot = _snapshot()
    snapshot["account_id"] = "101-222-333333-001"

    result = dr.reconcile_demo_snapshot(snapshot, _intent())

    assert result["allowed"] is False
    assert dr.REASON_ACCOUNT_ID_PRESENT in result["blocked_reasons"]


def test_credentials_loaded_blocks() -> None:
    snapshot = _snapshot()
    snapshot["credentials_loaded"] = True

    result = dr.reconcile_demo_snapshot(snapshot, _intent())

    assert result["allowed"] is False
    assert dr.REASON_CREDENTIALS_LOADED in result["blocked_reasons"]


def test_order_submit_and_live_blockers() -> None:
    for field, reason in (
        ("order_submit_enabled", dr.REASON_ORDER_SUBMIT_ENABLED),
        ("live_trading_enabled", dr.REASON_LIVE_TRADING_ENABLED),
        ("broker_write_enabled", dr.REASON_BROKER_WRITE_ENABLED),
        ("network_submit_enabled", dr.REASON_NETWORK_SUBMIT_ENABLED),
    ):
        snapshot = _snapshot()
        snapshot[field] = True
        result = dr.reconcile_demo_snapshot(snapshot, _intent())
        assert result["allowed"] is False
        assert reason in result["blocked_reasons"]


def test_safety_dict_present() -> None:
    result = dr.reconcile_demo_snapshot(_snapshot(), _intent())

    assert result["safety"] == {
        "paper_only": True,
        "demo_readonly": True,
        "broker_write": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_submit": False,
    }


def test_source_scan_has_no_broker_network_filesystem_or_sensitive_access() -> None:
    source = inspect.getsource(dr).lower()
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
