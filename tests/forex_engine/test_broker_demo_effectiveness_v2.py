from __future__ import annotations

from datetime import datetime, timedelta, timezone

from automation.forex_engine import broker_demo_effectiveness_v2 as effect


def _ready_contract() -> dict:
    return {
        "connector_mode": "DEMO_DRYRUN",
        "approved_by_human": True,
        "simulation_only": True,
        "broker_demo_only": True,
        "network_allowed": False,
        "credentials_present": False,
        "account_id_present": False,
        "endpoint_classification": "PRACTICE_DEMO",
        "kill_switch_enabled": True,
        "max_loss_gate_clear": True,
        "daily_stop_clear": True,
        "max_retry_attempts": 1,
    }


def _approved_connector() -> dict:
    return {
        "approved_for_demo": True,
        "connector_mode": "DEMO_DRYRUN",
        "network_allowed": False,
        "requires_order_route": False,
    }


def _account_envelope() -> dict:
    return {
        "account_id_present": False,
        "balance_placeholder": 10000.0,
        "equity_placeholder": 9999.0,
    }


def _instrument_envelope() -> dict:
    return {"symbol": "EUR/USD"}


def _quote_envelope() -> dict:
    return {
        "bid": 1.10,
        "ask": 1.1005,
        "spread": 0.0005,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


def test_probe_ready_with_valid_offline_readiness_inputs() -> None:
    result = effect.evaluate_demo_connector_readiness(
        connector_contract=_ready_contract(),
        connector=_approved_connector(),
        account_envelope=_account_envelope(),
        instrument_envelope=_instrument_envelope(),
        quote_envelope=_quote_envelope(),
    )
    summary = effect.summarize_broker_demo_probe_readiness(result)

    assert result.status == effect.BROKER_DEMO_PROBE_READY
    assert result.ready is True
    assert result.connector_status == "READY"
    assert result.sanitized_output["network_call_performed"] is False
    assert result.sanitized_output["evidence"]["probe_ready"] is True
    assert summary["status"] == effect.BROKER_DEMO_PROBE_READY
    assert summary["ready"] is True


def test_probe_rejects_live_endpoint_classification() -> None:
    contract = _ready_contract()
    contract["endpoint_classification"] = "LIVE"

    result = effect.evaluate_demo_connector_readiness(
        connector_contract=contract,
        connector=_approved_connector(),
        account_envelope=_account_envelope(),
        instrument_envelope=_instrument_envelope(),
        quote_envelope=_quote_envelope(),
    )

    assert result.status == effect.BROKER_DEMO_PROBE_BLOCKED
    assert result.ready is False
    assert any("endpoint_classification" in reason for reason in result.blocked_reasons)


def test_connector_is_required_and_fail_closed() -> None:
    result = effect.evaluate_demo_connector_readiness(
        connector_contract=_ready_contract(),
        connector=None,
        account_envelope=_account_envelope(),
        instrument_envelope=_instrument_envelope(),
        quote_envelope=_quote_envelope(),
    )

    assert result.status == effect.BROKER_DEMO_PROBE_CONNECTOR_REJECTED
    assert result.ready is False
    assert result.connector_status == "MISSING"
    assert "connector_required_for_review" in result.blocked_reasons


def test_connector_forbidden_live_flags_are_rejected() -> None:
    bad_connector = _approved_connector() | {"network_allowed": True}

    result = effect.evaluate_demo_connector_readiness(
        connector_contract=_ready_contract(),
        connector=bad_connector,
        account_envelope=_account_envelope(),
        instrument_envelope=_instrument_envelope(),
        quote_envelope=_quote_envelope(),
    )

    assert result.status == effect.BROKER_DEMO_PROBE_CONNECTOR_REJECTED
    assert result.ready is False
    assert any(reason == "connector_network_not_disabled" for reason in result.connector_result["blockers"])


def test_account_instrument_quote_envelope_validation() -> None:
    bad_quote = _quote_envelope()
    bad_quote["timestamp_utc"] = (datetime.now(timezone.utc) - timedelta(seconds=360)).isoformat()

    result = effect.evaluate_demo_connector_readiness(
        connector_contract=_ready_contract(),
        connector=_approved_connector(),
        account_envelope=_account_envelope(),
        instrument_envelope=_instrument_envelope(),
        quote_envelope=bad_quote,
    )

    assert result.status == effect.BROKER_DEMO_PROBE_BLOCKED
    assert "quote_quote_stale" in result.blocked_reasons or any(
        reason.startswith("quote_") and "stale" in reason for reason in result.blocked_reasons
    )


def test_sanitized_output_hides_sensitive_fields() -> None:
    poisoned = _ready_contract()
    poisoned["raw_request"] = "secret-token"
    poisoned["api_key"] = "should-not-persist"

    result = effect.evaluate_demo_connector_readiness(
        connector_contract=poisoned,
        connector=_approved_connector(),
        account_envelope={"account_id": "abc123", **_account_envelope()},
        instrument_envelope=_instrument_envelope(),
        quote_envelope=_quote_envelope(),
    )

    payload = result.sanitized_output
    assert payload.get("raw_request") is None
    assert payload.get("api_key") is None
    assert payload["account_evaluation"].get("account_id") is None
    assert payload["contains_private_data"] is False
    assert result.connector_status == "READY"
