from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_data_import.py"


def load_data_import_module():
    spec = importlib.util.spec_from_file_location("forex_data_import", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def valid_row(**overrides):
    row = {
        "timestamp": "2026-06-14T00:00:00Z",
        "pair": "EURUSD",
        "open": "1.1000",
        "high": "1.1060",
        "low": "1.0950",
        "close": "1.1040",
    }
    row.update(overrides)
    return row


def test_module_imports():
    data_import = load_data_import_module()
    assert callable(data_import.normalize_csv_row)
    assert callable(data_import.normalize_csv_rows)


def test_valid_rows_normalize():
    data_import = load_data_import_module()
    summary = data_import.normalize_csv_rows(
        [
            valid_row(pair="GBPUSD"),
            valid_row(pair="USDJPY", open="157.0", high="157.5", low="156.8", close="157.2"),
        ]
    )
    assert summary["paper_only"] is True
    assert summary["network_access"] is False
    assert summary["candles_normalized"] == 2
    assert summary["rows_blocked"] == 0


def test_numeric_strings_convert():
    data_import = load_data_import_module()
    candle = data_import.normalize_csv_row(valid_row(volume="1000", fast_ma="1.103", slow_ma="1.101", momentum="0.5"))
    assert candle["allowed"] is True
    assert candle["open"] == 1.1
    assert candle["volume"] == 1000.0
    assert candle["momentum"] == 0.5


def test_missing_field_blocked():
    data_import = load_data_import_module()
    row = valid_row()
    del row["close"]
    result = data_import.normalize_csv_row(row)
    assert result["allowed"] is False
    assert result["blocked_reason"] == "missing_close"


def test_invalid_pair_blocked():
    data_import = load_data_import_module()
    result = data_import.normalize_csv_row(valid_row(pair="AUDUSD"))
    assert result["allowed"] is False
    assert result["blocked_reason"] == "unsupported_pair"


def test_live_broker_credential_api_key_real_order_and_webhook_blocked():
    data_import = load_data_import_module()
    assert data_import.normalize_csv_row(valid_row(live_execution=True))["blocked_reason"] == "live_execution_blocked"
    assert data_import.normalize_csv_row(valid_row(broker_order=True))["blocked_reason"] == "broker_order_blocked"
    assert data_import.normalize_csv_row(valid_row(credentials={"token": "x"}))["blocked_reason"] == "credentials_blocked"
    assert data_import.normalize_csv_row(valid_row(api_key="placeholder"))["blocked_reason"] == "api_key_blocked"
    assert data_import.normalize_csv_row(valid_row(real_order=True))["blocked_reason"] == "real_order_blocked"
    assert data_import.normalize_csv_row(valid_row(webhook_url="https://example.invalid"))["blocked_reason"] == "webhook_url_blocked"


def test_no_network_usage():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["requests", "urllib", "http.client", "socket", "websocket"]:
        assert forbidden not in source
