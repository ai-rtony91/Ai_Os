from __future__ import annotations

import json

from automation.forex_engine import broker_integration_effectiveness_v1 as effect
from automation.forex_engine import broker_specific_paper_demo
from automation.forex_engine.no_order_connector_contracts_g_v1 import (
    build_demo_no_order_contract,
)


def _approved_contract_payload() -> broker_specific_paper_demo.BrokerSpecificPaperDemoConfig:
    return broker_specific_paper_demo.BrokerSpecificPaperDemoConfig(
        external_auth_reference_present=True,
        paper_demo_mode_confirmation=True,
        broker_sdk_allowed=False,
        network_api_allowed=False,
        credentials_allowed=False,
        live_execution_allowed=False,
        live_orders_allowed=False,
    )


def _ready_envelope() -> dict:
    return {
        "instrument": "EUR_USD",
        "side": "BUY",
        "units_or_notional": 1,
        "risk_cap_usd": 10.0,
        "stop_loss": 1.07,
        "take_profit": 1.08,
        "kill_switch_active": False,
        "max_loss_usd": 10.0,
        "daily_stop_hit": False,
        "human_approval_required": True,
        "simulation_only": True,
        "broker_demo_only": True,
        "dry_run_connector_id": "AIOS-DRY-RUN-CONNECTOR-001",
        "endpoint_mode": "DEMO",
        "max_attempts": 1,
        "retry_loop_enabled": False,
        "order_route_requested": False,
        "account_state_requested": False,
        "market_data_requested": False,
        "live_order": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
    }


def test_contract_is_demo_dryrun_ready() -> None:
    adapter_contract = {
        "adapter_mode": "DEMO_DRYRUN",
        "live_ready": False,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
    }
    result = effect.check_broker_demo_contract(
        broker_adapter_contract=adapter_contract,
        broker_specific_config=_approved_contract_payload(),
    )

    assert result.status == effect.BROKER_DEMO_DRYRUN_READY
    assert result.ready is True
    assert result.runtime_evaluation["broker_specific_config"]["config_valid"] is True


def test_contract_invalid_when_adapter_mode_live() -> None:
    adapter_contract = {"adapter_mode": "LIVE", "live_ready": True}
    result = effect.check_broker_demo_contract(
        broker_adapter_contract=adapter_contract,
        broker_specific_config=_approved_contract_payload(),
    )

    assert result.status == effect.BROKER_DEMO_CONTRACT_INVALID
    assert result.ready is False
    assert "adapter_mode_invalid" in result.blocked_reasons


def test_envelope_validator_ready_when_gate_clear() -> None:
    result = effect.validate_broker_demo_envelope(
        envelope=_ready_envelope(),
        no_order_connector=build_demo_no_order_contract("connector-001"),
    )
    payload_json = json.dumps(result.sanitized_payload)

    assert result.status == effect.BROKER_DEMO_DRYRUN_READY
    assert result.ready is True
    assert result.connector_status == "READY"
    assert "account_id" not in payload_json
    assert result.sanitized_payload["broker_demo_only"] is True
    assert result.sanitized_payload["simulation_only"] is True
    assert result.sanitized_payload["live_ready"] is False
    assert result.runtime_evaluation["connector_status"] == "READY"


def test_envelope_rejects_missing_human_approval_and_live_intent() -> None:
    data = _ready_envelope()
    data["human_approval_required"] = False
    data["order_route_requested"] = True
    data["live_order"] = True

    result = effect.validate_broker_demo_envelope(
        envelope=data,
        no_order_connector=build_demo_no_order_contract("connector-001"),
    )

    assert result.status == effect.BROKER_DEMO_BLOCKED
    assert result.ready is False
    assert "human_owner_approval_required" in result.blocked_reasons
    assert "order_route_attempt_blocked" in result.blocked_reasons
    assert "privileged_flag:live_order" not in result.blocked_reasons


def test_envelope_rejects_retry_loop_and_forbidden_retry_marker() -> None:
    data = _ready_envelope()
    data["retry_loop_enabled"] = True
    data["max_attempts"] = 3

    result = effect.validate_broker_demo_envelope(
        envelope=data,
        no_order_connector=build_demo_no_order_contract("connector-001"),
    )

    assert result.status == effect.BROKER_DEMO_BLOCKED
    assert result.ready is False
    assert "retry_loop_blocked" in result.blocked_reasons
    assert "max_attempts_must_equal_one" in result.blocked_reasons


def test_envelope_rejects_forbidden_fields_without_persistence() -> None:
    data = _ready_envelope()
    data["api_key"] = "should-not-persist"

    result = effect.validate_broker_demo_envelope(
        envelope=data,
        no_order_connector=build_demo_no_order_contract("connector-001"),
    )
    serialized = json.dumps(result.sanitized_payload)

    assert result.status == effect.BROKER_DEMO_BLOCKED
    assert result.ready is False
    assert any("forbidden_field:api_key" in reason for reason in result.blocked_reasons)
    assert "should-not-persist" not in serialized
    assert result.sanitized_payload["broker_sdk_allowed"] is False


def test_envelope_without_connector_is_connector_rejected() -> None:
    result = effect.validate_broker_demo_envelope(envelope=_ready_envelope(), no_order_connector=None)

    assert result.status == effect.BROKER_DEMO_CONNECTOR_REJECTED
    assert result.ready is False
    assert "runtime_connector_required" in result.blocked_reasons
    assert result.connector_status == "MISSING"
    assert result.sanitized_payload["simulation_only"] is True


def test_map_candidate_includes_required_broker_dryrun_fields() -> None:
    candidate = {
        "symbol": "eurusd",
        "side": "sell",
        "units": 2,
        "stop_loss": 1.05,
        "take_profit": 1.07,
    }
    mapped = effect.map_paper_trade_candidate_to_broker_dryrun_intent(
        candidate,
        risk_cap_usd=5.0,
        max_loss_usd=1.0,
        kill_switch_active=False,
        daily_stop_hit=False,
        human_approval_required=True,
        dry_run_connector_id="CONNECTOR-V1",
    )

    assert mapped["schema"] == "AIOS_BROKER_DEMO_DRYRUN_INTENT_ENVELOPE.v1"
    assert mapped["instrument"] == "EURUSD".replace("-", "_").replace("/", "_")
    assert mapped["side"] == "SELL"
    assert mapped["risk_cap_usd"] == 5.0
    assert mapped["max_loss_usd"] == 1.0
    assert mapped["simulation_only"] is True
    assert mapped["broker_demo_only"] is True
    assert mapped["max_attempts"] == 1
    assert mapped["retry_loop_enabled"] is False
    assert mapped["live_order"] is False
    assert mapped["would_place_order"] is False
    assert mapped["broker_request_sent"] is False


def test_latency_budget_contract_is_offline_by_default() -> None:
    budget = effect.build_broker_integration_latency_budget()

    assert budget["schema"] == "AIOS_BROKER_INTEGRATION_LATENCY_BUDGET_V1_REPORT.v1"
    assert budget["contracted_but_offline_by_default"] is True
    assert budget["broker_call_by_default"] is False
    assert budget["gates"]["connector_call_placeholder_ms"]["budget"] == 0
    assert budget["gates"]["broker_response_placeholder_ms"]["budget"] == 0


def test_summary_ready_ready() -> None:
    contract_result = effect.check_broker_demo_contract(
        broker_adapter_contract={"adapter_mode": "DEMO_DRYRUN", "live_ready": False},
        broker_specific_config=_approved_contract_payload(),
    )
    envelope_result = effect.validate_broker_demo_envelope(
        envelope=_ready_envelope(),
        no_order_connector=build_demo_no_order_contract("connector-001"),
    )
    summary = effect.summarize_broker_integration_effectiveness(
        contract_eval=contract_result,
        envelope_eval=envelope_result,
    )

    assert summary["status"] == effect.BROKER_DEMO_DRYRUN_READY
    assert summary["ready"] is True
    assert summary["no_live_or_network_action"] is True
