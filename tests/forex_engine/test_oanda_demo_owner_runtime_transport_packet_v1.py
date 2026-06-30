from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.oanda_demo_broker_adapter_runtime_binding_v1 import (  # noqa: E402
    OANDA_DEMO_BINDING_READY_FOR_OWNER_RUNTIME_TRANSPORT,
    OANDA_DEMO_FAKE_TRANSPORT_ACCEPTED,
    bind_oanda_demo_broker_adapter_runtime_v1,
    SCHEMA as BINDING_SCHEMA,
    MODE as BINDING_MODE,
)
from automation.forex_engine.oanda_demo_owner_runtime_transport_packet_v1 import (  # noqa: E402
    BLOCKED_BY_APPROVAL_TOKEN,
    BLOCKED_BY_AUDIT_TELEMETRY,
    BLOCKED_BY_BINDING_RESULT,
    BLOCKED_BY_OWNER_APPROVAL,
    BLOCKED_BY_DEMO_ACCOUNT_BOUNDARY,
    BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY,
    BLOCKED_BY_ONE_ORDER_POLICY,
    BLOCKED_BY_SANITIZED_ORDER_ENVELOPE,
    BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY,
    BLOCKED_BY_SENSITIVE_DATA,
    BLOCKED_BY_TRANSPORT_POLICY,
    INCOMPLETE_INPUTS,
    OWNER_RUNTIME_TRANSPORT_PACKET_READY,
    OWNER_RUNTIME_TRANSPORT_PACKET_READY_WITH_FAKE_PROBE,
    SCHEMA,
    MODE,
    evaluate_oanda_demo_owner_runtime_transport_packet_v1,
)

MODULE_PATH = ROOT / "automation" / "forex_engine" / "oanda_demo_owner_runtime_transport_packet_v1.py"
DOC_PATH = ROOT / "docs" / "trading_lab" / "FOREX_OANDA_DEMO_OWNER_RUNTIME_TRANSPORT_PACKET_V1.md"
REPORT_PATH = ROOT / "Reports" / "forex_delivery" / "AIOS_FOREX_OANDA_DEMO_OWNER_RUNTIME_TRANSPORT_PACKET_V1_REPORT.md"

FORBIDDEN_SOURCE_MARKERS = (
    "re" + "quests",
    "so" + "cket",
    "ur" + "llib",
    "sub" + "process",
    "os." + "environ",
    "broker" + "_sdk",
    "sched" + "ule.every",
    "start" + "-process",
)

UNSAFE_MARKERS = (
    "100" + "-120",
    "100" + " to " + "120",
    "100%" + " return",
    "100% " + "return",
    "gu" + "aranteed return",
    "gu" + "aranteed profit",
    "tr" + "ade now",
    "with" + "draw now",
    "auton" + "omous withdrawal",
    "auton" + "omous deposit",
    "store " + "credentials",
)

HARD_FALSE_FIELDS = (
    "real_broker_call_allowed",
    "direct_broker_api_allowed",
    "broker_api_import_allowed",
    "network_call_allowed",
    "live_trading_allowed",
    "real_money_allowed",
    "money_movement_allowed",
    "bank_access_allowed",
    "credential_storage_allowed",
    "credential_read_allowed",
    "credential_request_allowed",
    "account_identifier_storage_allowed",
    "account_identifier_read_allowed",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "dashboard_runtime_created",
    "live_execution_allowed",
    "live_capital_action_authorized",
)


def _safe_binding_payload() -> dict:
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
            "approval_token_metadata_present": True,
            "approval_phrase_matches": True,
            "approval_action_matches": True,
            "approval_mode_matches": True,
            "approval_phrase_present": True,
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
            "broker_api_allowed": False,
        },
        "order_request": {
            "schema": BINDING_SCHEMA,
            "mode": BINDING_MODE,
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
        "telemetry": {
            "audit": True,
            "telemetry_fields_seen": ["ok"],
        },
        "as_of_date": "2026-06-30",
    }


def _safe_transport_payload() -> dict:
    binding = bind_oanda_demo_broker_adapter_runtime_v1(_safe_binding_payload())
    return {
        "broker_adapter_binding_result": binding,
        "owner_name": "Anthony",
        "owner_runtime_approval": {
            "owner_name": "Anthony",
            "owner_runtime_transport_approval_required": True,
            "owner_accepts_demo_only_boundary": True,
            "owner_accepts_runtime_transport_packet": True,
            "owner_accepts_no_credentials_in_repo": True,
            "owner_accepts_no_account_identifiers_in_repo": True,
            "owner_accepts_no_real_money": True,
            "owner_accepts_one_order_only": True,
            "owner_can_cancel": True,
            "owner_cancel_phrase_detected": False,
        },
        "approval_token_evidence": {
            "approval_token_required": True,
            "approval_token_metadata_present": True,
            "approval_token_id_present": True,
            "approval_phrase_present": True,
            "approval_phrase_matches": True,
            "approval_action_matches": True,
            "approval_mode_matches": True,
            "approval_instrument_matches": True,
            "approval_units_matches": True,
            "approval_risk_matches": True,
            "approval_token_unexpired": True,
            "approval_token_unused": True,
            "approval_challenge_hash_present": True,
            "approval_timestamp_present": True,
            "raw_approval_phrase_stored": False,
            "raw_voice_audio_stored": False,
        },
        "runtime_credential_boundary": {
            "credential_values_provided": False,
            "credential_values_persisted": False,
            "credential_values_logged": False,
            "credential_values_requested_by_aios": False,
            "owner_runtime_credential_entry_required": True,
            "runtime_only_credentials_required": True,
            "secrets_manager_required": True,
            "repo_secret_storage_allowed": False,
            "chat_secret_sharing_allowed": False,
            "env_var_read_allowed": False,
            "credential_redaction_required": True,
            "secret_scan_required": True,
        },
        "runtime_transport_policy": {
            "owner_runtime_transport_required": True,
            "injected_transport_required": True,
            "transport_created_in_repo": False,
            "fake_transport_probe_allowed": True,
            "fake_transport_probe_requested": False,
            "real_network_call_forbidden_in_this_packet": True,
            "oanda_sdk_import_allowed": False,
            "broker_sdk_import_allowed": False,
            "direct_http_import_allowed": False,
            "background_runtime_allowed": False,
            "one_packet_one_order": True,
        },
        "demo_account_boundary": {
            "broker_name": "OANDA",
            "broker_mode": "DEMO",
            "account_environment": "DEMO",
            "demo_only": True,
            "demo_account_reference_present": True,
            "account_identifier_values_provided": False,
            "live_account_allowed": False,
            "real_money_allowed": False,
            "live_execution_allowed": False,
            "money_movement_allowed": False,
            "bank_access_allowed": False,
        },
        "sanitized_order_envelope": {
            "schema": SCHEMA,
            "mode": MODE,
            "broker_name": "OANDA",
            "broker_mode": "DEMO",
            "account_environment": "DEMO",
            "instrument": "EUR_USD",
            "side": "BUY",
            "order_type": "MARKET",
            "units": 1000,
            "strategy_id": "edge-reversion-v1",
            "candidate_id": "candidate-001",
            "stop_loss_present": True,
            "take_profit_present": True,
            "max_spread_pips": 2.5,
            "max_slippage_pips": 1.0,
            "demo_only": True,
            "live_execution_allowed": False,
            "credentials_included": False,
            "account_identifiers_included": False,
            "transport_injected": False,
            "risk_limits": {"max_risk_per_trade_pct": 0.01, "max_daily_loss_pct": 0.03},
        },
        "one_order_policy": {
            "one_order_only": True,
            "duplicate_order_detected": False,
            "existing_open_order_for_candidate": False,
            "existing_open_position_for_candidate": False,
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "post_execution_review_required": True,
            "next_order_blocked_until_review": True,
            "max_order_count_this_packet": 1,
        },
        "audit_telemetry": {
            "audit_record_required": True,
            "sanitized_packet_required": True,
            "owner_review_required": True,
            "runtime_transport_packet_required": True,
            "pre_transport_snapshot_required": True,
            "post_transport_snapshot_required": True,
            "exception_capture_required": True,
            "secret_scan_required": True,
            "no_raw_secret_logging": True,
            "no_raw_account_identifier_logging": True,
        },
        "as_of_date": "2026-06-30",
    }


class FakeTransportWithValidate:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def validate_owner_runtime_transport_packet(self, packet: dict) -> dict:
        self.calls.append(dict(packet))
        return {
            "status": "ACCEPTED",
            "token_value": "should-not-return",
            "raw_approval_phrase": "hidden-phrase",
            "message": "ok",
        }


class FakeTransportWithSubmit:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def submit_demo_order(self, packet: dict) -> dict:
        self.calls.append(dict(packet))
        return {"status": "OK"}


class FakeTransportWithoutContract:
    def ping(self) -> dict:
        return {"status": "noop"}


def _assert_hard_false_authority_fields(result: dict) -> None:
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
    assert result["safety"]["read_only"] is True
    assert result["safety"]["demo_only"] is True
    assert result["safety"]["owner_gate_required"] is True
    assert result["safety"]["approval_token_required"] is True
    assert result["safety"]["one_order_only_required"] is True
    assert result["safety"]["runtime_only_credentials_required"] is True
    assert result["safety"]["real_broker_call_allowed"] is False
    assert result["safety"]["direct_broker_api_allowed"] is False
    assert result["safety"]["broker_api_import_allowed"] is False
    assert result["safety"]["network_call_allowed"] is False
    assert result["safety"]["live_trading_allowed"] is False
    assert result["safety"]["real_money_allowed"] is False
    assert result["safety"]["money_movement_allowed"] is False
    assert result["safety"]["bank_access_allowed"] is False
    assert result["safety"]["credential_storage_allowed"] is False
    assert result["safety"]["credential_read_allowed"] is False
    assert result["safety"]["credential_request_allowed"] is False
    assert result["safety"]["account_identifier_storage_allowed"] is False
    assert result["safety"]["account_identifier_read_allowed"] is False
    assert result["safety"]["scheduler_allowed"] is False
    assert result["safety"]["daemon_allowed"] is False
    assert result["safety"]["webhook_allowed"] is False
    assert result["safety"]["dashboard_runtime_allowed"] is False
    assert result["safety"]["fixed_return_target_promised"] is False
    assert result["safety"]["profit_claim_authorized"] is False


def test_strong_payload_no_transport_returns_ready() -> None:
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(_safe_transport_payload())
    assert result["schema"] == SCHEMA
    assert result["mode"] == MODE
    assert result["packet_status"] == OWNER_RUNTIME_TRANSPORT_PACKET_READY
    assert result["ready_for_owner_runtime_transport"] is True
    assert result["fake_probe_attempted"] is False
    assert result["transport_probe_call_count"] == 0
    assert result["next_best_packet"] == "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_RUNTIME_DRY_RUN_V1"
    assert result["packet_blockers"] == []
    _assert_hard_false_authority_fields(result)


def test_strong_payload_with_fake_transport_probe_returns_ready_with_fake_probe() -> None:
    payload = _safe_transport_payload()
    payload["runtime_transport_policy"]["fake_transport_probe_requested"] = True
    transport = FakeTransportWithValidate()
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload, transport)
    assert result["packet_status"] == OWNER_RUNTIME_TRANSPORT_PACKET_READY_WITH_FAKE_PROBE
    assert result["fake_probe_attempted"] is True
    assert result["transport_probe_call_count"] == 1
    assert result["sanitized_fake_probe_result"]["status"] == "ACCEPTED"
    assert "token_value" not in result["sanitized_fake_probe_result"]
    assert "raw_approval_phrase" not in result["sanitized_fake_probe_result"]
    _assert_hard_false_authority_fields(result)


def test_fake_transport_is_called_once() -> None:
    payload = _safe_transport_payload()
    payload["runtime_transport_policy"]["fake_transport_probe_requested"] = True
    transport = FakeTransportWithSubmit()
    evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload, transport)
    assert len(transport.calls) == 1


def test_fake_transport_receives_only_sanitized_packet() -> None:
    payload = _safe_transport_payload()
    payload["runtime_transport_policy"]["fake_transport_probe_requested"] = True
    transport = FakeTransportWithValidate()
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload, transport)
    assert result["packet_status"] == OWNER_RUNTIME_TRANSPORT_PACKET_READY_WITH_FAKE_PROBE
    envelope = transport.calls[0]
    expected_keys = {
        "schema",
        "mode",
        "owner_name",
        "broker_name",
        "broker_mode",
        "account_environment",
        "instrument",
        "side",
        "order_type",
        "units",
        "strategy_id",
        "candidate_id",
        "stop_loss_present",
        "take_profit_present",
        "max_spread_pips",
        "max_slippage_pips",
        "risk_limits",
        "one_order_only",
        "owner_can_cancel",
        "approval_token_required",
        "approval_token_id_present",
        "approval_challenge_hash_present",
        "owner_runtime_credential_entry_required",
        "runtime_only_credentials_required",
        "credentials_included",
        "account_identifiers_included",
        "demo_only",
        "live_execution_allowed",
        "money_movement_allowed",
        "real_broker_call_allowed",
        "network_call_allowed",
        "transport_injected",
    }
    assert set(envelope.keys()) <= expected_keys
    assert "token_value" not in envelope
    assert envelope["transport_injected"] is True
    assert "raw_approval_phrase_stored" not in envelope
    assert envelope["live_execution_allowed"] is False
    assert envelope["demo_only"] is True
    assert result["sanitized_owner_runtime_transport_packet"] == envelope


def test_missing_broker_binding_result_returns_incomplete_or_blocked() -> None:
    payload = _safe_transport_payload()
    payload.pop("broker_adapter_binding_result", None)
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload)
    assert result["packet_status"] in {INCOMPLETE_INPUTS, BLOCKED_BY_BINDING_RESULT}


def test_binding_status_not_ready_blocks() -> None:
    payload = _safe_transport_payload()
    payload["broker_adapter_binding_result"]["binding_status"] = "INVALID_STATUS"
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload)
    assert result["packet_status"] == BLOCKED_BY_BINDING_RESULT
    assert "binding_status_not_ready" in result["packet_blockers"]


def test_owner_approval_blocked() -> None:
    payload = _safe_transport_payload()
    payload["owner_runtime_approval"]["owner_runtime_transport_approval_required"] = False
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload)
    assert result["packet_status"] == BLOCKED_BY_OWNER_APPROVAL
    assert "owner_runtime_transport_approval_required_false" in result["packet_blockers"]


def test_approval_token_blocked() -> None:
    payload = _safe_transport_payload()
    payload["approval_token_evidence"]["approval_token_id_present"] = False
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload)
    assert result["packet_status"] == BLOCKED_BY_APPROVAL_TOKEN
    assert "approval_token_id_present_false" in result["packet_blockers"]


def test_runtime_credential_boundary_blocked() -> None:
    payload = _safe_transport_payload()
    payload["runtime_credential_boundary"]["secret_scan_required"] = False
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload)
    assert result["packet_status"] == BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY
    assert "secret_scan_required_false" in result["packet_blockers"]


def test_transport_policy_blocked() -> None:
    payload = _safe_transport_payload()
    payload["runtime_transport_policy"]["broker_sdk_import_allowed"] = True
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload)
    assert result["packet_status"] == BLOCKED_BY_TRANSPORT_POLICY
    assert "broker_sdk_import_allowed_true" in result["packet_blockers"]


def test_transport_contract_invalid_blocks_when_requested() -> None:
    payload = _safe_transport_payload()
    payload["runtime_transport_policy"]["fake_transport_probe_requested"] = True
    payload["runtime_transport_policy"]["fake_transport_probe_allowed"] = True
    transport = FakeTransportWithoutContract()
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload, transport)
    assert result["packet_status"] == BLOCKED_BY_TRANSPORT_POLICY
    assert "transport_contract_method_missing" in result["packet_blockers"]

def test_demo_account_boundary_blocked() -> None:
    payload = _safe_transport_payload()
    payload["demo_account_boundary"]["demo_only"] = False
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload)
    assert result["packet_status"] == BLOCKED_BY_DEMO_ACCOUNT_BOUNDARY
    assert "demo_only_false" in result["packet_blockers"]


def test_sanitized_order_envelope_blocked() -> None:
    payload = _safe_transport_payload()
    payload["sanitized_order_envelope"]["side"] = "INVALID"
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload)
    assert result["packet_status"] == BLOCKED_BY_SANITIZED_ORDER_ENVELOPE
    assert "side_not_allowed" in result["packet_blockers"]


def test_one_order_policy_blocked() -> None:
    payload = _safe_transport_payload()
    payload["one_order_policy"]["duplicate_order_detected"] = True
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload)
    assert result["packet_status"] == BLOCKED_BY_ONE_ORDER_POLICY
    assert "duplicate_order_detected_true" in result["packet_blockers"]


def test_audit_telemetry_blocked() -> None:
    payload = _safe_transport_payload()
    payload["audit_telemetry"]["secret_scan_required"] = False
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload)
    assert result["packet_status"] == BLOCKED_BY_AUDIT_TELEMETRY
    assert "secret_scan_required_false" in result["packet_blockers"]


def test_live_money_authority_blocks_packet() -> None:
    payload = _safe_transport_payload()
    payload["demo_account_boundary"]["money_movement_allowed"] = True
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload)
    assert result["packet_status"] == BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY
    assert "money_movement_allowed" in result["packet_blockers"]


def test_sensitive_payload_blocked_and_not_echoed() -> None:
    payload = _safe_transport_payload()
    payload["account_id"] = "acct-001"
    payload["runtime_transport_policy"]["approval_phrase"] = "top-secret"
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload)
    assert result["packet_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert result["sanitized_owner_runtime_transport_packet"]["schema"] == SCHEMA
    result_repr = repr(result)
    assert "acct-001" not in result_repr
    assert "top-secret" not in result_repr
    assert "approval_phrase" not in result_repr


def test_sensitive_keys_in_payload_blocked() -> None:
    for key in ("api_key", "token_value", "oanda_account_id", "private_key"):
        payload = _safe_transport_payload()
        payload[key] = f"blocked-{key}"
        result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload)
        assert result["packet_status"] == BLOCKED_BY_SENSITIVE_DATA
        assert f"blocked-{key}" not in repr(result)


def test_safe_metadata_keys_not_misclassified() -> None:
    payload = _safe_transport_payload()
    payload["account_identifier_storage_allowed"] = False
    payload["account_identifier_read_allowed"] = False
    payload["account_identifier_values_provided"] = False
    payload["credential_storage_allowed"] = False
    payload["credential_read_allowed"] = False
    payload["credential_request_allowed"] = False
    payload["broker_api_allowed"] = False
    payload["direct_broker_api_allowed"] = False
    payload["network_call_allowed"] = False
    payload["live_execution_allowed"] = False
    payload["money_movement_allowed"] = False
    payload["bank_access_allowed"] = False
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload)
    assert result["packet_status"] == OWNER_RUNTIME_TRANSPORT_PACKET_READY
    assert result["packet_blockers"] == []


def test_hard_false_authority_fields_are_false() -> None:
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(_safe_transport_payload())
    _assert_hard_false_authority_fields(result)


def test_owner_action_queue_contains_review_next_packet_and_required_fields() -> None:
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(_safe_transport_payload())
    action_ids = {action["action_id"] for action in result["owner_action_queue"]}
    assert "REVIEW_NEXT_PACKET" in action_ids
    for action in result["owner_action_queue"]:
        assert action["owner_decision_required"] is True
        assert action["live_execution_allowed"] is False
        assert action["money_movement_allowed"] is False
        assert action["real_broker_call_allowed"] is False
        assert action["safe_action"]


def test_next_packet_routes_to_owner_approved_one_order_runtime_dry_run() -> None:
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(_safe_transport_payload())
    assert result["next_best_packet"] == "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_RUNTIME_DRY_RUN_V1"
    assert result["packet_status"] == OWNER_RUNTIME_TRANSPORT_PACKET_READY


def test_integration_with_binding_output() -> None:
    payload = _safe_transport_payload()
    result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(payload)
    assert result["packet_status"] == OWNER_RUNTIME_TRANSPORT_PACKET_READY
    binding = result["broker_adapter_binding_summary"]
    assert binding["schema"] == BINDING_SCHEMA
    assert binding["binding_status"] in {
        OANDA_DEMO_BINDING_READY_FOR_OWNER_RUNTIME_TRANSPORT,
        OANDA_DEMO_FAKE_TRANSPORT_ACCEPTED,
    }


def test_source_contains_no_runtime_or_api_process_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source


def test_no_unsafe_phrases_in_packet_sources() -> None:
    files = [
        MODULE_PATH,
        DOC_PATH,
        REPORT_PATH,
        Path(__file__),
    ]
    for file_path in files:
        if not file_path.exists():
            continue
        content = file_path.read_text(encoding="utf-8").lower()
        for marker in UNSAFE_MARKERS:
            assert marker not in content
