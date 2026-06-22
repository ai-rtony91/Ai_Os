from __future__ import annotations

from pathlib import Path

from automation.forex_engine import final_live_operator_bridge_v1 as bridge
from automation.forex_engine import live_preflight_evidence_bundle_v1 as preflight
from automation.forex_engine import oanda_live_http_transport_v1 as transport
from automation.forex_engine import oanda_live_runtime_connector_v2 as connector
from automation.forex_engine import protected_runtime_credential_injection_v1 as injection


def _account(**overrides: object) -> dict:
    envelope = {
        "account_currency": "USD",
        "balance": 10000.0,
        "equity": 10000.0,
        "margin_available": 9000.0,
        "open_risk": 0.0,
        "max_loss_gate_clear": True,
        "daily_stop_clear": True,
        "kill_switch_enabled": False,
        "portfolio_exposure_clear": True,
        "micro_risk_cap_amount": 5.0,
        "account_id_present": False,
        "account_id_persisted": False,
    }
    envelope.update(overrides)
    return envelope


def _instrument(**overrides: object) -> dict:
    envelope = {
        "instrument": "EUR_USD",
        "trade_enabled": True,
        "market_open": True,
        "instrument_supported": True,
        "min_units": 1,
        "max_units": 1000,
        "requested_units": 10,
    }
    envelope.update(overrides)
    return envelope


def _quote(**overrides: object) -> dict:
    envelope = {
        "bid": 1.0800,
        "ask": 1.0802,
        "spread": 0.0002,
        "max_spread": 0.0005,
        "quote_fresh": True,
        "quote_age_seconds": 2,
        "max_quote_age_seconds": 10,
        "market_data_source_verified": True,
        "broker_call_performed": False,
    }
    envelope.update(overrides)
    return envelope


def _order(**overrides: object) -> dict:
    envelope = {
        "instrument": "EUR_USD",
        "side": "BUY",
        "units": 10,
        "stop_loss": "1.0780",
        "take_profit": "1.0840",
        "risk_reward_ratio": 2.0,
        "risk_cap_confirmed": True,
        "stop_loss_confirmed": True,
        "take_profit_confirmed": True,
        "one_trade_only": True,
        "micro_size_only": True,
        "order_executed": False,
        "broker_call_performed": False,
    }
    envelope.update(overrides)
    return envelope


def _operator(**overrides: object) -> dict:
    state = {
        "authenticated_operator": True,
        "protected_action_authorized": True,
        "live_exception_requested": True,
        "understands_live_risk_ack": True,
        "operator_approved_live_runtime": True,
        "credential_persisted": False,
        "account_id_persisted": False,
        "no_default_network": True,
        "no_retry": True,
        "no_loop": True,
        "one_order_only": True,
        "execution_requested": False,
        "order_executed": False,
        "broker_call_performed": False,
    }
    state.update(overrides)
    return state


def _bridge_state() -> dict:
    return {
        "bridge_status": bridge.FINAL_LIVE_OPERATOR_BRIDGE_READY,
        "ready": True,
        "final_bridge_ready": True,
    }


def _injection_state() -> dict:
    return {
        "status": injection.PROTECTED_RUNTIME_INJECTION_READY,
        "ready": True,
        "runtime_injection_ready": True,
    }


def _connector_state() -> dict:
    return connector.build_oanda_live_connector_config(
        {
            "operator_approved_live_runtime": True,
            "live_endpoint_confirmed": True,
            "credentials_runtime_only": True,
            "credentials_persisted": False,
            "account_id_persisted": False,
            "single_order_only": True,
            "micro_size_only": True,
            "no_retry": True,
            "no_loop": True,
            "max_order_count": 1,
            "transport_injected": True,
        }
    )


def _transport_state() -> dict:
    return transport.build_oanda_live_http_transport_config(
        {
            "operator_approved_live_runtime": True,
            "live_endpoint_confirmed": True,
            "allow_live_network_once": True,
            "credentials_runtime_only": True,
            "credentials_persisted": False,
            "account_id_persisted": False,
            "single_order_only": True,
            "micro_size_only": True,
            "no_retry": True,
            "no_loop": True,
            "max_order_count": 1,
            "http_client_injected": True,
            "runtime_auth_provider_injected": True,
        }
    )


def _mobile(**overrides: object) -> dict:
    state = {"mobile_operator_ready": True}
    state.update(overrides)
    return state


def _bundle(**overrides: object) -> dict:
    payload = {
        "final_bridge_state": _bridge_state(),
        "runtime_injection_state": _injection_state(),
        "oanda_connector_state": _connector_state(),
        "oanda_transport_state": _transport_state(),
        "account_risk_envelope": _account(),
        "instrument_envelope": _instrument(),
        "quote_spread_envelope": _quote(),
        "order_intent_envelope": _order(),
        "mobile_operator_state": _mobile(),
        "operator_state": _operator(),
    }
    payload.update(overrides)
    return preflight.build_live_preflight_evidence_bundle(**payload)


def test_missing_bundle_inputs_returns_invalid_or_blocked() -> None:
    result = preflight.build_live_preflight_evidence_bundle()

    assert result["status"] in {
        preflight.LIVE_PREFLIGHT_EVIDENCE_INVALID,
        preflight.LIVE_PREFLIGHT_EVIDENCE_BLOCKED,
    }
    assert "operator_state_missing" in result["blockers"]


def test_account_envelope_blocks_when_balance_is_zero() -> None:
    result = preflight.validate_account_risk_envelope(_account(balance=0))

    assert result["status"] == preflight.LIVE_PREFLIGHT_ACCOUNT_BLOCKED
    assert "balance_not_positive" in result["blockers"]


def test_account_envelope_blocks_when_kill_switch_is_enabled() -> None:
    result = preflight.validate_account_risk_envelope(_account(kill_switch_enabled=True))

    assert result["status"] == preflight.LIVE_PREFLIGHT_ACCOUNT_BLOCKED
    assert "kill_switch_enabled" in result["blockers"]


def test_account_envelope_blocks_when_account_id_is_present() -> None:
    result = preflight.validate_account_risk_envelope(
        _account(account_id_present=True, account_id="ACCOUNT_SHOULD_NOT_LEAK")
    )

    assert result["status"] == preflight.LIVE_PREFLIGHT_ACCOUNT_BLOCKED
    assert "account_id_present" in result["blockers"]
    assert "account_id" not in result["sanitized_evidence"]


def test_instrument_envelope_blocks_unsupported_symbol_format() -> None:
    result = preflight.validate_instrument_envelope(_instrument(instrument="EURUSD"))

    assert result["status"] == preflight.LIVE_PREFLIGHT_MARKET_BLOCKED
    assert "instrument_format_unsupported" in result["blockers"]


def test_instrument_envelope_blocks_requested_units_above_1000() -> None:
    result = preflight.validate_instrument_envelope(_instrument(requested_units=1001, max_units=2000))

    assert result["status"] == preflight.LIVE_PREFLIGHT_MARKET_BLOCKED
    assert "requested_units_above_micro_max" in result["blockers"]


def test_quote_envelope_blocks_stale_quote() -> None:
    result = preflight.validate_quote_spread_envelope(_quote(quote_fresh=False, quote_age_seconds=20))

    assert result["status"] == preflight.LIVE_PREFLIGHT_MARKET_BLOCKED
    assert "quote_not_fresh" in result["blockers"]
    assert "quote_age_above_max" in result["blockers"]


def test_quote_envelope_blocks_spread_above_max_spread() -> None:
    result = preflight.validate_quote_spread_envelope(_quote(spread=0.0010))

    assert result["status"] == preflight.LIVE_PREFLIGHT_MARKET_BLOCKED
    assert "spread_above_max" in result["blockers"]


def test_order_intent_blocks_missing_stop_loss() -> None:
    result = preflight.validate_live_order_intent_envelope(_order(stop_loss=None))

    assert result["status"] == preflight.LIVE_PREFLIGHT_ORDER_BLOCKED
    assert "stop_loss_missing" in result["blockers"]


def test_order_intent_blocks_missing_take_profit() -> None:
    result = preflight.validate_live_order_intent_envelope(_order(take_profit=""))

    assert result["status"] == preflight.LIVE_PREFLIGHT_ORDER_BLOCKED
    assert "take_profit_missing" in result["blockers"]


def test_order_intent_blocks_invalid_side() -> None:
    result = preflight.validate_live_order_intent_envelope(_order(side="HOLD"))

    assert result["status"] == preflight.LIVE_PREFLIGHT_ORDER_BLOCKED
    assert "side_invalid" in result["blockers"]


def test_order_intent_blocks_units_above_1000() -> None:
    result = preflight.validate_live_order_intent_envelope(_order(units=1001))

    assert result["status"] == preflight.LIVE_PREFLIGHT_ORDER_BLOCKED
    assert "units_above_micro_max" in result["blockers"]


def test_complete_injected_evidence_returns_ready() -> None:
    result = _bundle()

    assert result["status"] == preflight.LIVE_PREFLIGHT_EVIDENCE_READY
    assert result["ready"] is True


def test_bundle_remains_execution_allowed_false_even_when_ready() -> None:
    result = _bundle()

    assert result["ready"] is True
    assert result["execution_allowed"] is False
    assert result["order_executed"] is False
    assert result["broker_call_performed"] is False


def test_sanitized_output_never_includes_sensitive_values() -> None:
    result = _bundle(
        final_bridge_state={**_bridge_state(), "token": "TOKEN_SHOULD_NOT_LEAK"},
        account_risk_envelope={
            **_account(),
            "account_id": "ACCOUNT_SHOULD_NOT_LEAK",
            "authorization": "AUTH_SHOULD_NOT_LEAK",
        },
        oanda_transport_state={
            **_transport_state(),
            "broker_order_id": "ORDER_SHOULD_NOT_LEAK",
            "raw_request": {"value": "RAW_REQUEST_SHOULD_NOT_LEAK"},
            "raw_response": {"value": "RAW_RESPONSE_SHOULD_NOT_LEAK"},
            "raw_payload": {"value": "RAW_PAYLOAD_SHOULD_NOT_LEAK"},
        },
    )
    rendered = repr(result["sanitized_evidence"])

    assert "TOKEN_SHOULD_NOT_LEAK" not in rendered
    assert "ACCOUNT_SHOULD_NOT_LEAK" not in rendered
    assert "AUTH_SHOULD_NOT_LEAK" not in rendered
    assert "ORDER_SHOULD_NOT_LEAK" not in rendered
    assert "RAW_REQUEST_SHOULD_NOT_LEAK" not in rendered
    assert "RAW_RESPONSE_SHOULD_NOT_LEAK" not in rendered
    assert "RAW_PAYLOAD_SHOULD_NOT_LEAK" not in rendered


def test_mobile_summary_includes_required_operator_truth_fields() -> None:
    result = _bundle()
    summary = result["mobile_summary"]

    for key in (
        "mode",
        "status",
        "blockers",
        "next_safe_action",
        "instrument",
        "side",
        "units",
        "stop_loss",
        "take_profit",
        "max_loss_gate",
        "daily_stop_gate",
        "kill_switch",
        "spread",
        "quote_freshness",
    ):
        assert key in summary
    assert summary["instrument"] == "EUR_USD"
    assert summary["quote_freshness"] == "FRESH"


def test_integration_with_existing_readiness_dictionaries_succeeds() -> None:
    injection_contract = injection.build_runtime_injection_contract(
        {
            "authenticated_operator": True,
            "protected_action_authorized": True,
            "live_exception_requested": True,
            "understands_live_risk_ack": True,
            "operator_approved_live_runtime": True,
            "credentials_runtime_only": True,
            "credentials_persisted": False,
            "account_id_persisted": False,
            "allow_live_network_once": True,
            "one_trade_only": True,
            "micro_size_only": True,
            "no_retry": True,
            "no_loop": True,
            "max_order_count": 1,
            "runtime_auth_provider_injected": True,
            "http_client_injected": True,
            "final_bridge_ready": True,
            "oanda_transport_ready": True,
            "oanda_connector_ready": True,
        }
    )

    result = _bundle(runtime_injection_state=injection_contract)

    assert result["status"] == preflight.LIVE_PREFLIGHT_EVIDENCE_READY
    assert result["component_status"]["runtime_injection_ready"] is True
    assert result["component_status"]["oanda_connector_ready"] is True
    assert result["component_status"]["oanda_transport_ready"] is True


def test_source_scan_proves_no_forbidden_execution_triggers() -> None:
    source = Path("automation/forex_engine/live_preflight_evidence_bundle_v1.py").read_text(
        encoding="utf-8"
    ).lower()
    forbidden_snippets = (
        "import os",
        "from os",
        "os.environ",
        "getenv(",
        "dotenv",
        "import requests",
        "from requests",
        "open(",
        "scheduler",
        "daemon",
        "webhook",
        "retry loop",
        "urlopen(",
        "urllib.request",
        "socket.",
        "api-fxtrade",
    )

    for snippet in forbidden_snippets:
        assert snippet not in source
