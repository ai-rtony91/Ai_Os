from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.oanda_demo_broker_adapter_runtime_binding_v1 import (
    BLOCKED_BY_DEMO_BOUNDARY,
    BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY,
    BLOCKED_BY_ORDER_REQUEST,
    BLOCKED_BY_RISK_ENVELOPE,
    BLOCKED_BY_RUNTIME_CONTEXT,
    BLOCKED_BY_SENSITIVE_DATA,
    BLOCKED_BY_TRANSPORT_CONTRACT,
    INCOMPLETE_INPUTS,
    OANDA_DEMO_BINDING_READY_FOR_OWNER_RUNTIME_TRANSPORT,
    OANDA_DEMO_FAKE_TRANSPORT_ACCEPTED,
    OANDA_DEMO_BINDING_READY_WITH_INJECTED_FAKE_TRANSPORT,
    SCHEMA,
    MODE,
    bind_oanda_demo_broker_adapter_runtime_v1,
    build_oanda_demo_broker_adapter_runtime_binding_v1,
)
from automation.forex_engine.oanda_demo_supervised_order_execution_v1 import (
    execute_oanda_demo_supervised_order_v1,
)

MODULE_PATH = ROOT / "automation" / "forex_engine" / "oanda_demo_broker_adapter_runtime_binding_v1.py"
SUPER_MODULE_PATH = ROOT / "automation" / "forex_engine" / "oanda_demo_supervised_order_execution_v1.py"


FORBIDDEN_SOURCE_MARKERS = (
    "re" + "quests",
    "so" + "cket",
    "ur" + "llib",
    "sub" + "process",
    "os." + "environ",
    "bro" + "ker_sdk",
    "sched" + "ule.every",
    "st" + "art-process",
)

MARKET_BOUNDARY_RISK_MARKERS = (
    "100" + "-120",
    "100" + " to " + "120",
    "100%" + " return",
    "100% " + "return",
    "gu" + "aranteed return",
    "gu" + "aranteed profit",
    "tr" + "ade" + " now",
    "with" + "draw now",
    "auton" + "omous withdrawal",
    "auto" + "nomous deposit",
    "store " + "credentials",
)

HARD_FALSE_FIELDS = (
    "direct_broker_api_allowed",
    "broker_api_import_allowed",
    "network_call_allowed",
    "live_trading_allowed",
    "real_money_allowed",
    "money_movement_allowed",
    "bank_access_allowed",
    "credential_storage_allowed",
    "credential_read_allowed",
    "account_identifier_storage_allowed",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "dashboard_runtime_created",
)


def _safe_transport_payload() -> dict:
    return {
        "runtime_context": {
            "broker_name": "OANDA",
            "broker_mode": "DEMO",
            "account_environment": "DEMO",
            "demo_account_reference_present": True,
            "account_identifier_values_provided": False,
            "credential_values_provided": False,
            "runtime_credentials_managed_by_owner": True,
            "live_account_allowed": False,
            "real_money_allowed": False,
            "live_execution_allowed": False,
            "money_movement_allowed": False,
            "bank_access_allowed": False,
            "direct_broker_api_allowed": False,
            "broker_api_allowed": False,
            "network_call_allowed": False,
        },
        "owner_name": "Anthony",
        "owner_approval": {
            "owner_approval_required": True,
            "owner_accepts_demo_only_boundary": True,
            "owner_accepts_injected_transport_only": True,
            "owner_accepts_no_credentials_in_repo": True,
            "owner_accepts_no_real_money": True,
            "owner_can_cancel": True,
            "approval_phrase_matches": True,
            "approval_action_matches": True,
            "approval_mode_matches": True,
            "owner_cancel_phrase_detected": False,
        },
        "approval_token_evidence": {
            "approval_token_metadata_present": True,
            "approval_token_unexpired": True,
            "approval_token_unused": True,
        },
        "demo_boundary": {
            "demo_only": True,
            "broker_name": "OANDA",
            "broker_mode": "DEMO",
            "account_environment": "DEMO",
            "live_account_allowed": False,
            "real_money_allowed": False,
            "live_execution_allowed": False,
            "money_movement_allowed": False,
            "bank_access_allowed": False,
        },
        "order_request": {
            "schema": SCHEMA,
            "mode": MODE,
            "broker_name": "OANDA",
            "broker_mode": "DEMO",
            "account_environment": "DEMO",
            "strategy_id": "edge-reversion-v1",
            "candidate_id": "candidate-001",
            "instrument": "EUR_USD",
            "side": "BUY",
            "order_type": "MARKET",
            "units": 1000,
            "stop_loss_present": True,
            "take_profit_present": True,
            "max_spread_pips": 2.5,
            "max_slippage_pips": 1.0,
            "demo_only": True,
            "live_execution_allowed": False,
            "credentials_included": False,
        },
        "risk_envelope": {
            "max_risk_per_trade_pct": 0.01,
            "max_daily_loss_pct": 0.03,
            "one_order_only": True,
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "duplicate_order_detected": False,
        },
        "telemetry": {"audit": True},
        "as_of_date": "2026-06-30",
    }


def _supervised_payload() -> dict:
    return {
        "owner_name": "Anthony",
        "as_of_date": "2026-06-30",
        "execution_mode": "DEMO_PRACTICE",
        "runtime_handoff_package": {
            "handoff_status": "OANDA_DEMO_RUNTIME_HANDOFF_READY",
            "runtime_handoff_ready": True,
            "supervised_demo_execution_authorized": True,
            "handoff_blockers": [],
        },
        "owner_approval": {
            "owner_name": "Anthony",
            "execution_mode": "DEMO_PRACTICE",
            "owner_final_approval_for_demo_execution": True,
            "owner_accepts_order_preview": True,
            "owner_accepts_demo_only_boundary": True,
            "owner_accepts_risk_limits": True,
            "owner_accepts_one_order_only": True,
            "owner_can_cancel": True,
            "execution_allowed": True,
            "live_execution_allowed": False,
            "owner_approval_required": True,
        },
        "oanda_demo_boundary": {
            "broker_name": "OANDA",
            "broker_mode": "DEMO",
            "account_environment": "PRACTICE",
            "demo_account_only": True,
            "live_account_allowed": False,
            "real_money_allowed": False,
            "money_movement_allowed": False,
            "bank_access_allowed": False,
            "live_execution_allowed": False,
            "broker_api_allowed": False,
            "credential_use_allowed": False,
            "order_placement_allowed": True,
        },
        "order_preview": {
            "strategy_id": "edge-reversion-v1",
            "candidate_id": "candidate-001",
            "instrument": "EUR_USD",
            "side": "BUY",
            "order_type": "MARKET",
            "units": 100,
            "max_position_units": 2000,
            "stop_loss_present": True,
            "take_profit_present": True,
            "max_spread_pips": 2.5,
            "max_slippage_pips": 1.0,
            "order_preview_accepted_by_owner": True,
            "order_preview_blocks": [],
            "raw_note": "this raw note must not reach the adapter",
        },
        "risk_gates": {
            "max_loss_gate_present": True,
            "daily_loss_stop_present": True,
            "kill_switch_present": True,
            "max_risk_per_trade_pct": 0.01,
            "max_daily_loss_pct": 0.03,
            "one_order_only": True,
            "position_size_limit_present": True,
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "duplicate_order_detected": False,
            "risk_gate_blocks": [],
        },
        "abort_conditions": {
            "abort_if_owner_approval_missing": True,
            "abort_if_credentials_missing": True,
            "abort_if_broker_mode_not_demo": True,
            "abort_if_spread_above_max": True,
            "abort_if_slippage_above_max": True,
            "abort_if_stop_loss_missing": True,
            "abort_if_take_profit_missing": True,
            "abort_if_daily_loss_hit": True,
            "abort_if_kill_switch_active": True,
            "abort_if_duplicate_order_detected": True,
            "abort_if_wrong_account_detected": True,
            "abort_if_live_account_detected": True,
            "abort_condition_blocks": [],
        },
        "telemetry": {
            "audit_log_required": True,
            "sanitized_ticket_required": True,
            "pre_trade_snapshot_required": True,
            "order_preview_snapshot_required": True,
            "post_trade_snapshot_required": True,
            "exception_capture_required": True,
            "owner_review_report_required": True,
            "execution_result_required": True,
            "telemetry_blocks": [],
        },
        "post_trade_review": {
            "post_trade_review_required": True,
            "pnl_review_required": True,
            "risk_review_required": True,
            "execution_quality_review_required": True,
            "next_trade_blocked_until_review": True,
            "post_trade_review_blocks": [],
        },
        "data_quality": {
            "data_quality_blocks": [],
            "missing_fields": [],
            "malformed_fields": [],
        },
    }
class FakeTransport:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def submit_oanda_demo_order(self, order_request: dict) -> dict:
        self.calls.append(dict(order_request))
        return {
            "status": "ACCEPTED",
            "ticket": "DEMO-001",
            "credentials_included": False,
            "token_value": "secret-token-value",
        }


class FakeTransportWithoutMethod:
    def preview(self, payload: dict) -> dict:
        return payload


class IntegrationFakeTransport:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def submit_demo_order(self, order_request: dict) -> dict:
        self.calls.append(dict(order_request))
        return {
            "status": "ACCEPTED",
            "ticket": "INTEGRATION-DEMO-001",
            "credentials_included": False,
        }


def assert_hard_false_authority_flags(result: dict) -> None:
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
    assert result["safety"]["read_only_binding"] is True
    assert result["safety"]["injected_transport_only"] is True
    assert result["safety"]["direct_broker_api_allowed"] is False
    assert result["safety"]["broker_api_import_allowed"] is False
    assert result["safety"]["network_call_allowed"] is False
    assert result["safety"]["live_trading_allowed"] is False
    assert result["safety"]["real_money_allowed"] is False
    assert result["safety"]["money_movement_allowed"] is False
    assert result["safety"]["bank_access_allowed"] is False
    assert result["safety"]["credential_storage_allowed"] is False
    assert result["safety"]["credential_read_allowed"] is False
    assert result["safety"]["account_identifier_storage_allowed"] is False
    assert result["safety"]["scheduler_allowed"] is False
    assert result["safety"]["daemon_allowed"] is False
    assert result["safety"]["webhook_allowed"] is False
    assert result["safety"]["dashboard_runtime_allowed"] is False
    assert result["safety"]["fixed_return_target_promised"] is False
    assert result["safety"]["profit_claim_authorized"] is False


def test_no_transport_with_strong_payload_returns_owner_runtime_transport_packet() -> None:
    result = bind_oanda_demo_broker_adapter_runtime_v1(_safe_transport_payload())
    assert result["schema"] == SCHEMA
    assert result["binding_status"] == OANDA_DEMO_BINDING_READY_FOR_OWNER_RUNTIME_TRANSPORT
    assert result["transport_supplied"] is False
    assert result["transport_contract_ready"] is False
    assert result["transport_call_attempted"] is False
    assert result["transport_call_count"] == 0
    assert result["next_best_packet"] == "AIOS_FOREX_OANDA_DEMO_OWNER_RUNTIME_TRANSPORT_PACKET_V1"
    assert result["binding_blockers"] == []
    assert_hard_false_authority_flags(result)


def test_valid_fake_transport_with_strong_payload_returns_fake_transport_accepted() -> None:
    transport = FakeTransport()
    result = bind_oanda_demo_broker_adapter_runtime_v1(_safe_transport_payload(), transport)
    assert result["binding_status"] == OANDA_DEMO_FAKE_TRANSPORT_ACCEPTED
    assert result["transport_supplied"] is True
    assert result["transport_contract_ready"] is True
    assert result["adapter_available"] is True
    assert result["transport_call_attempted"] is True
    assert result["transport_call_count"] == 1
    assert result["sanitized_transport_result"]["status"] == "ACCEPTED"
    assert result["sanitized_transport_result"]["ticket"] == "DEMO-001"
    assert "token_value" not in result["sanitized_transport_result"]
    assert_hard_false_authority_flags(result)


def test_adapter_submit_demo_order_called_exactly_once() -> None:
    transport = FakeTransport()
    adapter = build_oanda_demo_broker_adapter_runtime_binding_v1(_safe_transport_payload(), transport)
    fake_order = {"schema": SCHEMA, "mode": MODE, "live_execution_allowed": False}
    first = adapter.submit_demo_order(fake_order)
    assert transport.calls == [fake_order]
    assert first["status"] == "ACCEPTED"
    assert adapter.transport_call_count == 1


def test_fake_transport_receives_only_sanitized_order_request() -> None:
    transport = FakeTransport()
    result = bind_oanda_demo_broker_adapter_runtime_v1(_safe_transport_payload(), transport)
    assert result["binding_status"] == OANDA_DEMO_FAKE_TRANSPORT_ACCEPTED
    envelope = result["sanitized_order_envelope"]
    assert transport.calls == [envelope]
    assert envelope["schema"] == SCHEMA
    assert envelope["mode"] == MODE
    assert envelope["broker_name"] == "OANDA"
    assert envelope["live_execution_allowed"] is False
    assert envelope["credentials_included"] is False
    assert envelope["account_identifiers_included"] is False
    assert "api_key" not in repr(envelope)
    assert "password" not in repr(envelope)
    assert envelope["transport_injected"] is True


def test_invalid_transport_contract_returns_blocked_by_transport_contract() -> None:
    result = bind_oanda_demo_broker_adapter_runtime_v1(_safe_transport_payload(), FakeTransportWithoutMethod())
    assert result["binding_status"] == BLOCKED_BY_TRANSPORT_CONTRACT
    assert result["transport_contract_ready"] is False
    assert result["transport_call_attempted"] is False
    assert "submit_method_missing" in result["binding_blockers"]
    assert_hard_false_authority_flags(result)


def test_missing_runtime_context_returns_incomplete_inputs() -> None:
    payload = _safe_transport_payload()
    payload.pop("runtime_context", None)
    result = bind_oanda_demo_broker_adapter_runtime_v1(payload)
    assert result["binding_status"] == INCOMPLETE_INPUTS
    assert "missing_runtime_context" in result["binding_blockers"]


def test_weak_runtime_context_blocked() -> None:
    payload = _safe_transport_payload()
    payload["runtime_context"]["broker_mode"] = "LIVE"
    result = bind_oanda_demo_broker_adapter_runtime_v1(payload)
    assert result["binding_status"] == BLOCKED_BY_RUNTIME_CONTEXT
    assert "broker_mode_not_demo" in result["binding_blockers"]


def test_weak_owner_approval_blocked() -> None:
    payload = _safe_transport_payload()
    payload["owner_approval"]["owner_approval_required"] = False
    result = bind_oanda_demo_broker_adapter_runtime_v1(payload)
    assert result["binding_status"] == "BLOCKED_BY_OWNER_APPROVAL"
    assert "owner_approval_required_false" in result["binding_blockers"]


def test_weak_demo_boundary_blocked() -> None:
    payload = _safe_transport_payload()
    payload["demo_boundary"]["demo_only"] = False
    result = bind_oanda_demo_broker_adapter_runtime_v1(payload)
    assert result["binding_status"] == BLOCKED_BY_DEMO_BOUNDARY
    assert "demo_only_false" in result["binding_blockers"]


def test_weak_order_request_blocked() -> None:
    payload = _safe_transport_payload()
    payload["order_request"]["side"] = "WAIT"
    result = bind_oanda_demo_broker_adapter_runtime_v1(payload)
    assert result["binding_status"] == BLOCKED_BY_ORDER_REQUEST
    assert "side_not_allowed" in result["binding_blockers"]


def test_weak_risk_envelope_blocked() -> None:
    payload = _safe_transport_payload()
    payload["risk_envelope"]["max_risk_per_trade_pct"] = 0.02
    result = bind_oanda_demo_broker_adapter_runtime_v1(payload)
    assert result["binding_status"] == BLOCKED_BY_RISK_ENVELOPE
    assert "max_risk_per_trade_pct_above_limit" in result["binding_blockers"]


def test_sensitive_payload_blocked_and_not_echoed() -> None:
    payload = _safe_transport_payload()
    payload["api_key"] = "super-secret-value"
    result = bind_oanda_demo_broker_adapter_runtime_v1(payload)
    assert result["binding_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "sensitive_data_provided" in result["binding_blockers"]
    payload_repr = repr(result)
    assert "super-secret-value" not in payload_repr


def test_order_request_sensitive_values_blocked() -> None:
    payload = _safe_transport_payload()
    payload["order_request"]["account_id"] = "acct-001"
    result = bind_oanda_demo_broker_adapter_runtime_v1(payload)
    assert result["binding_status"] == BLOCKED_BY_SENSITIVE_DATA


def test_demo_boundary_or_order_sensitive_fields_blocked() -> None:
    payload = _safe_transport_payload()
    payload["risk_envelope"]["account_id"] = "acct-002"
    result = bind_oanda_demo_broker_adapter_runtime_v1(payload)
    assert result["binding_status"] == BLOCKED_BY_SENSITIVE_DATA


def test_sensitive_fields_list_blocked_for_common_keys() -> None:
    sensitive_cases = ["api_key", "token_value", "oanda_account_id", "account_id"]
    for key in sensitive_cases:
        payload = _safe_transport_payload()
        payload[key] = f"value-{key}"
        result = bind_oanda_demo_broker_adapter_runtime_v1(payload)
        assert result["binding_status"] == BLOCKED_BY_SENSITIVE_DATA
        assert f"value-{key}" not in repr(result)


def test_safe_metadata_keys_not_misclassified_as_sensitive() -> None:
    payload = _safe_transport_payload()
    payload["account_identifier_storage_allowed"] = False
    payload["credential_storage_allowed"] = False
    payload["credential_read_allowed"] = False
    payload["broker_api_allowed"] = False
    payload["direct_broker_api_allowed"] = False
    payload["network_call_allowed"] = False
    payload["live_trading_allowed"] = False
    payload["money_movement_allowed"] = False
    result = bind_oanda_demo_broker_adapter_runtime_v1(payload)
    assert result["binding_status"] == OANDA_DEMO_BINDING_READY_FOR_OWNER_RUNTIME_TRANSPORT
    assert result["binding_blockers"] == []


def test_live_or_money_authority_blocks_binding() -> None:
    payload = _safe_transport_payload()
    payload["runtime_context"]["money_movement_allowed"] = True
    result = bind_oanda_demo_broker_adapter_runtime_v1(payload)
    assert result["binding_status"] == BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY
    assert "money_movement_allowed" in result["binding_blockers"]


def test_owner_action_queue_contains_review_next_packet() -> None:
    result = bind_oanda_demo_broker_adapter_runtime_v1(_safe_transport_payload())
    action_ids = {entry["action_id"] for entry in result["owner_action_queue"]}
    assert "REVIEW_NEXT_PACKET" in action_ids
    assert len(result["owner_action_queue"]) == 9
    for action in result["owner_action_queue"]:
        assert action["owner_decision_required"] is True
        assert action["live_execution_allowed"] is False
        assert "safe_action" in action


def test_next_packet_routes_to_owner_runtime_or_post_execution() -> None:
    no_transport = bind_oanda_demo_broker_adapter_runtime_v1(_safe_transport_payload())
    with_transport = bind_oanda_demo_broker_adapter_runtime_v1(_safe_transport_payload(), FakeTransport())
    assert no_transport["next_best_packet"] == "AIOS_FOREX_OANDA_DEMO_OWNER_RUNTIME_TRANSPORT_PACKET_V1"
    assert with_transport["next_best_packet"] == "AIOS_FOREX_OANDA_DEMO_POST_EXECUTION_REVIEW_V1"


def test_integration_with_execute_oanda_demo_supervised_order_v1_uses_adapter() -> None:
    transport = IntegrationFakeTransport()
    binding_transport = build_oanda_demo_broker_adapter_runtime_binding_v1(
        _safe_transport_payload(),
        transport,
    )
    exec_result = execute_oanda_demo_supervised_order_v1(_supervised_payload(), binding_transport)
    assert exec_result["supervised_demo_execution_attempted"] is True
    assert exec_result["execution_status"] == "DEMO_ORDER_EXECUTED_WITH_INJECTED_ADAPTER"
    assert transport.calls, "Fake transport must be called once by supervised execution."
    assert len(transport.calls) == 1
    assert exec_result["execution_result"]["status"] == "ACCEPTED"
    assert exec_result["execution_result"]["credentials_included"] is False


def test_binding_produces_legacy_bound_constant_reference() -> None:
    assert OANDA_DEMO_BINDING_READY_WITH_INJECTED_FAKE_TRANSPORT == (
        "OANDA_DEMO_BINDING_READY_WITH_INJECTED_FAKE_TRANSPORT"
    )


def test_source_contains_no_runtime_or_api_import_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source

