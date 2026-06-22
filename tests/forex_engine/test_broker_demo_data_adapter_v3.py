from __future__ import annotations

from datetime import datetime, timedelta, timezone

from automation.forex_engine import broker_demo_data_adapter_v3 as adapter


NOW = datetime(2026, 6, 22, 19, 45, tzinfo=timezone.utc)


def _account() -> dict:
    return {
        "balance": 10000.0,
        "equity": 10025.0,
        "margin_available": 9500.0,
        "account_id_present": False,
    }


def _instrument() -> dict:
    return {
        "symbol": "EUR_USD",
        "min_units": 1,
        "max_units": 1000,
        "pip_location": 4,
        "precision": 5,
    }


def _quote() -> dict:
    return {
        "bid": 1.1000,
        "ask": 1.1002,
        "timestamp": NOW.isoformat(),
    }


def _gates() -> dict:
    return {
        "kill_switch_enabled": False,
        "max_loss_gate_clear": True,
        "daily_stop_clear": True,
    }


def test_ready_path_normalizes_demo_data_without_network_or_execution() -> None:
    result = adapter.evaluate_demo_data_readiness(_account(), _instrument(), _quote(), _gates(), now=NOW)

    assert result["status"] == adapter.BROKER_DEMO_DATA_READY
    assert result["ready"] is True
    assert result["blockers"] == ()
    assert result["normalized"]["instrument"]["symbol"] == "EUR_USD"
    assert result["normalized"]["quote"]["spread"] == 0.00019999999999997797
    assert result["sanitized_output"]["network_call_performed"] is False
    assert result["sanitized_output"]["order_execution_performed"] is False
    assert result["safety"]["live_trading"] is False
    assert result["safety"]["credentials_read"] is False


def test_account_rejects_account_identifier_and_sensitive_fields() -> None:
    account = _account()
    account["account_id_present"] = True
    account["account_" + "id"] = "DEMO-ACCOUNT-123"

    result = adapter.evaluate_demo_data_readiness(account, _instrument(), _quote(), _gates(), now=NOW)

    assert result["status"] == adapter.BROKER_DEMO_DATA_INVALID
    assert "account_account_id_present_forbidden" in result["blockers"]
    assert "account_sensitive_account_field_detected" in result["blockers"]
    assert "account_id" not in result["sanitized_output"]
    assert result["sanitized_output"]["contains_account_identifier"] is False


def test_instrument_rejects_live_route_marker() -> None:
    instrument = _instrument()
    instrument["symbol"] = "OANDA-LIVE-EUR-USD"

    result = adapter.evaluate_demo_data_readiness(_account(), instrument, _quote(), _gates(), now=NOW)

    assert result["status"] == adapter.BROKER_DEMO_DATA_INVALID
    assert "instrument_symbol_live_route_forbidden" in result["blockers"]


def test_quote_rejects_stale_timestamp() -> None:
    quote = _quote()
    quote["timestamp"] = (NOW - timedelta(seconds=301)).isoformat()

    result = adapter.evaluate_demo_data_readiness(_account(), _instrument(), quote, _gates(), now=NOW)

    assert result["status"] == adapter.BROKER_DEMO_DATA_BLOCKED
    assert "quote_quote_stale" in result["blockers"]


def test_quote_rejects_ask_below_bid() -> None:
    quote = _quote()
    quote["bid"] = 1.1010
    quote["ask"] = 1.1000

    result = adapter.evaluate_demo_data_readiness(_account(), _instrument(), quote, _gates(), now=NOW)

    assert result["status"] == adapter.BROKER_DEMO_DATA_INVALID
    assert "quote_ask_lt_bid" in result["blockers"]


def test_spread_too_wide_blocks_readiness_without_execution() -> None:
    quote = _quote()
    quote["bid"] = 1.1000
    quote["ask"] = 1.1060

    result = adapter.evaluate_demo_data_readiness(_account(), _instrument(), quote, _gates(), now=NOW)

    assert result["status"] == adapter.BROKER_DEMO_DATA_BLOCKED
    assert "quote_spread_too_wide" in result["blockers"]
    assert result["sanitized_output"]["order_execution_performed"] is False


def test_kill_switch_blocks_readiness() -> None:
    gates = _gates()
    gates["kill_switch_enabled"] = True

    result = adapter.evaluate_demo_data_readiness(_account(), _instrument(), _quote(), gates, now=NOW)

    assert result["status"] == adapter.BROKER_DEMO_DATA_BLOCKED
    assert "kill_switch_enabled" in result["blockers"]


def test_latency_budget_excludes_network_latency() -> None:
    budget = adapter.latency_budget()

    assert budget["account_normalization_ms"] >= 0
    assert budget["instrument_normalization_ms"] >= 0
    assert budget["quote_normalization_ms"] >= 0
    assert budget["spread_calculation_ms"] >= 0
    assert budget["risk_readiness_mapping_ms"] >= 0
    assert budget["network_latency_ms"] == "excluded_offline_default"
    assert budget["total_budget_ms"] > 0
