from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.oanda_demo_broker_adapter_runtime_binding_v1 import (  # noqa: E402
    MODE as BINDING_MODE,
    SCHEMA as BINDING_SCHEMA,
    bind_oanda_demo_broker_adapter_runtime_v1,
)
from automation.forex_engine.oanda_demo_owner_runtime_transport_packet_v1 import (  # noqa: E402
    SCHEMA as OWNER_RUNTIME_TRANSPORT_PACKET_SCHEMA,
    evaluate_oanda_demo_owner_runtime_transport_packet_v1,
)
from automation.forex_engine.oanda_demo_owner_approved_one_order_runtime_dry_run_v1 import (  # noqa: E402
    BLOCKED_BY_APPROVAL_TOKEN,
    BLOCKED_BY_AUDIT_TELEMETRY,
    BLOCKED_BY_DEMO_ACCOUNT_BOUNDARY,
    BLOCKED_BY_DRY_RUN_TRANSPORT_CONTRACT,
    BLOCKED_BY_FINAL_OWNER_APPROVAL,
    BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY,
    BLOCKED_BY_ONE_ORDER_POLICY,
    BLOCKED_BY_OWNER_RUNTIME_TRANSPORT_PACKET,
    BLOCKED_BY_RISK_ENVELOPE,
    BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY,
    BLOCKED_BY_SANITIZED_RUNTIME_PACKET,
    BLOCKED_BY_SENSITIVE_DATA,
    INCOMPLETE_INPUTS,
    MODE,
    ONE_ORDER_RUNTIME_DRY_RUN_COMPLETED_WITH_FAKE_TRANSPORT,
    ONE_ORDER_RUNTIME_DRY_RUN_READY,
    SCHEMA,
    run_oanda_demo_owner_approved_one_order_runtime_dry_run_v1,
)


MODULE_PATH = (
    ROOT
    / "automation"
    / "forex_engine"
    / "oanda_demo_owner_approved_one_order_runtime_dry_run_v1.py"
)
DOC_PATH = (
    ROOT
    / "docs"
    / "trading_lab"
    / "FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_RUNTIME_DRY_RUN_V1.md"
)
REPORT_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_RUNTIME_DRY_RUN_V1_REPORT.md"
)

SDK_BROKER_KEY = "broker" + "_sdk_import_allowed"

FORBIDDEN_SOURCE_MARKERS = (
    "re" + "quests",
    "so" + "cket",
    "ur" + "llib",
    "sub" + "process",
    "os." + "environ",
    "broker" + "_sdk",
    "schedule" + ".every",
    "start" + "-process",
)

UNSAFE_MARKERS = (
    "100" + "-120",
    "100" + " to " + "120",
    "120%" + " return",
    "100%" + " return",
    "guaranteed " + "return",
    "guaranteed " + "profit",
    "trade " + "now",
    "withdraw " + "now",
    "autonomous " + "withdrawal",
    "autonomous " + "deposit",
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
    "real_order_submitted",
    "demo_broker_order_submitted",
)

EXPECTED_SANITIZED_PACKET_KEYS = {
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
    "dry_run_only",
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
    "real_order_submitted",
    "demo_broker_order_submitted",
}


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


def _safe_transport_packet_payload() -> dict:
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
            SDK_BROKER_KEY: False,
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
            "schema": OWNER_RUNTIME_TRANSPORT_PACKET_SCHEMA,
            "mode": "READ_ONLY_OANDA_DEMO_OWNER_RUNTIME_TRANSPORT_PACKET",
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


def _safe_payload() -> dict:
    packet_result = evaluate_oanda_demo_owner_runtime_transport_packet_v1(
        _safe_transport_packet_payload()
    )
    return {
        "owner_name": "Anthony",
        "as_of_date": "2026-06-30",
        "owner_runtime_transport_packet_result": packet_result,
        "final_owner_approval": {
            "owner_name": "Anthony",
            "owner_final_dry_run_approval_required": True,
            "owner_accepts_one_order_dry_run": True,
            "owner_accepts_demo_only_boundary": True,
            "owner_accepts_no_real_broker_call": True,
            "owner_accepts_no_credentials_in_repo": True,
            "owner_accepts_no_account_identifiers_in_repo": True,
            "owner_accepts_no_real_money": True,
            "owner_accepts_no_money_movement": True,
            "owner_accepts_one_order_only": True,
            "owner_accepts_post_dry_run_review_required": True,
            "owner_can_cancel": True,
            "owner_cancel_phrase_detected": False,
            "generic_yes_detected": False,
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
            "approval_balance_snapshot_matches": True,
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
            "master_password_required": False,
            "vault_password_required": False,
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
        "sanitized_owner_runtime_transport_packet": packet_result[
            "sanitized_owner_runtime_transport_packet"
        ],
        "one_order_policy": {
            "one_order_only": True,
            "dry_run_only": True,
            "duplicate_order_detected": False,
            "existing_open_order_for_candidate": False,
            "existing_open_position_for_candidate": False,
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "post_dry_run_review_required": True,
            "post_execution_review_required": True,
            "next_order_blocked_until_review": True,
            "max_order_count_this_packet": 1,
        },
        "risk_envelope": {
            "max_risk_per_trade_pct": 0.01,
            "max_daily_loss_pct": 0.03,
            "stop_loss_required": True,
            "take_profit_required": True,
            "max_spread_pips": 2.5,
            "max_slippage_pips": 1.0,
            "one_order_only": True,
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "duplicate_order_detected": False,
        },
        "audit_telemetry": {
            "audit_record_required": True,
            "dry_run_receipt_required": True,
            "sanitized_packet_required": True,
            "owner_review_required": True,
            "pre_dry_run_snapshot_required": True,
            "post_dry_run_snapshot_required": True,
            "exception_capture_required": True,
            "secret_scan_required": True,
            "no_raw_secret_logging": True,
            "no_raw_account_identifier_logging": True,
            "no_raw_approval_phrase_logging": True,
            "no_voice_audio_storage": True,
        },
        "dry_run_transport_policy": {
            "dry_run_transport_allowed": True,
            "fake_transport_allowed": True,
            "fake_transport_requested": False,
            "real_broker_transport_allowed": False,
            "real_network_call_forbidden": True,
            "oanda_sdk_import_allowed": False,
            SDK_BROKER_KEY: False,
            "direct_http_import_allowed": False,
            "background_runtime_allowed": False,
            "one_packet_one_order": True,
        },
    }


class FakeDryRunTransport:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def validate_one_order_runtime_dry_run(self, packet: dict) -> dict:
        self.calls.append(dict(packet))
        return {
            "status": "FAKE_OK",
            "token_value": "should-not-echo",
            "api_key": "also-hidden",
            "nested": {"private_key": "hidden", "kept": True},
        }


class FakeDryRunTransportWithRun:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def run_one_order_runtime_dry_run(self, packet: dict) -> dict:
        self.calls.append(dict(packet))
        return {"status": "RUN_OK"}


class InvalidFakeDryRunTransport:
    def ping(self) -> dict:
        return {"status": "NOOP"}


def _run(payload: dict | None = None, transport: object | None = None) -> dict:
    return run_oanda_demo_owner_approved_one_order_runtime_dry_run_v1(
        payload if payload is not None else _safe_payload(),
        dry_run_transport=transport,
    )


def _assert_hard_false_authority_fields(result: dict) -> None:
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
    for field in (
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
        "scheduler_allowed",
        "daemon_allowed",
        "webhook_allowed",
        "dashboard_runtime_allowed",
        "real_order_submitted",
        "demo_broker_order_submitted",
        "fixed_return_target_promised",
        "profit_claim_authorized",
    ):
        assert result["safety"][field] is False
    assert result["safety"]["read_only"] is True
    assert result["safety"]["dry_run_only"] is True
    assert result["safety"]["demo_only"] is True
    assert result["safety"]["owner_gate_required"] is True
    assert result["safety"]["approval_token_required"] is True
    assert result["safety"]["one_order_only_required"] is True
    assert result["safety"]["runtime_only_credentials_required"] is True
    assert result["safety"]["post_dry_run_review_required"] is True


def test_strong_payload_without_transport_returns_ready() -> None:
    result = _run()
    assert result["schema"] == SCHEMA
    assert result["mode"] == MODE
    assert result["dry_run_status"] == ONE_ORDER_RUNTIME_DRY_RUN_READY
    assert result["dry_run_ready"] is True
    assert result["dry_run_transport_attempted"] is False
    assert result["dry_run_transport_call_count"] == 0
    assert result["next_best_packet"] == (
        "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_PROTECTED_RUNTIME_EXECUTION_V1"
    )
    assert set(result["sanitized_one_order_runtime_dry_run_packet"]) == EXPECTED_SANITIZED_PACKET_KEYS
    _assert_hard_false_authority_fields(result)


def test_strong_payload_with_valid_fake_transport_completes() -> None:
    payload = _safe_payload()
    payload["dry_run_transport_policy"]["fake_transport_requested"] = True
    transport = FakeDryRunTransport()
    result = _run(payload, transport)
    assert result["dry_run_status"] == ONE_ORDER_RUNTIME_DRY_RUN_COMPLETED_WITH_FAKE_TRANSPORT
    assert result["dry_run_ready"] is True
    assert result["dry_run_transport_attempted"] is True
    assert result["dry_run_transport_call_count"] == 1
    assert result["sanitized_fake_dry_run_result"]["status"] == "FAKE_OK"
    assert "token_value" not in result["sanitized_fake_dry_run_result"]
    assert "api_key" not in result["sanitized_fake_dry_run_result"]
    assert "private_key" not in result["sanitized_fake_dry_run_result"]["nested"]
    _assert_hard_false_authority_fields(result)


def test_fake_transport_is_called_exactly_once() -> None:
    payload = _safe_payload()
    payload["dry_run_transport_policy"]["fake_transport_requested"] = True
    transport = FakeDryRunTransportWithRun()
    _run(payload, transport)
    assert len(transport.calls) == 1


def test_fake_transport_receives_only_sanitized_packet() -> None:
    payload = _safe_payload()
    payload["dry_run_transport_policy"]["fake_transport_requested"] = True
    transport = FakeDryRunTransport()
    result = _run(payload, transport)
    assert transport.calls[0] == result["sanitized_one_order_runtime_dry_run_packet"]
    assert set(transport.calls[0]) == EXPECTED_SANITIZED_PACKET_KEYS
    assert transport.calls[0]["credentials_included"] is False
    assert transport.calls[0]["account_identifiers_included"] is False
    assert transport.calls[0]["real_order_submitted"] is False
    assert transport.calls[0]["demo_broker_order_submitted"] is False


def test_missing_owner_runtime_transport_packet_returns_incomplete_or_blocked() -> None:
    payload = _safe_payload()
    payload.pop("owner_runtime_transport_packet_result")
    result = _run(payload)
    assert result["dry_run_status"] in {
        INCOMPLETE_INPUTS,
        BLOCKED_BY_OWNER_RUNTIME_TRANSPORT_PACKET,
    }


def test_weak_owner_runtime_transport_packet_blocks() -> None:
    payload = _safe_payload()
    payload["owner_runtime_transport_packet_result"]["packet_status"] = "NO"
    result = _run(payload)
    assert result["dry_run_status"] == BLOCKED_BY_OWNER_RUNTIME_TRANSPORT_PACKET


def test_weak_final_owner_approval_blocks() -> None:
    payload = _safe_payload()
    payload["final_owner_approval"]["owner_accepts_one_order_dry_run"] = False
    result = _run(payload)
    assert result["dry_run_status"] == BLOCKED_BY_FINAL_OWNER_APPROVAL
    assert "owner_accepts_one_order_dry_run_false" in result["dry_run_blockers"]


def test_generic_yes_approval_blocks_final_owner_approval() -> None:
    payload = _safe_payload()
    payload["final_owner_approval"]["generic_yes_detected"] = True
    result = _run(payload)
    assert result["dry_run_status"] == BLOCKED_BY_FINAL_OWNER_APPROVAL
    assert "generic_yes_detected_true" in result["dry_run_blockers"]


def test_weak_approval_token_blocks() -> None:
    payload = _safe_payload()
    payload["approval_token_evidence"]["approval_token_id_present"] = False
    result = _run(payload)
    assert result["dry_run_status"] == BLOCKED_BY_APPROVAL_TOKEN


def test_weak_credential_boundary_blocks() -> None:
    payload = _safe_payload()
    payload["runtime_credential_boundary"]["secret_scan_required"] = False
    result = _run(payload)
    assert result["dry_run_status"] == BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY


def test_weak_demo_account_boundary_blocks() -> None:
    payload = _safe_payload()
    payload["demo_account_boundary"]["demo_only"] = False
    result = _run(payload)
    assert result["dry_run_status"] == BLOCKED_BY_DEMO_ACCOUNT_BOUNDARY


def test_weak_sanitized_runtime_packet_blocks() -> None:
    payload = _safe_payload()
    payload["sanitized_owner_runtime_transport_packet"]["side"] = "WAIT"
    result = _run(payload)
    assert result["dry_run_status"] == BLOCKED_BY_SANITIZED_RUNTIME_PACKET


def test_weak_one_order_policy_blocks() -> None:
    payload = _safe_payload()
    payload["one_order_policy"]["duplicate_order_detected"] = True
    result = _run(payload)
    assert result["dry_run_status"] == BLOCKED_BY_ONE_ORDER_POLICY


def test_weak_risk_envelope_blocks() -> None:
    payload = _safe_payload()
    payload["risk_envelope"]["max_risk_per_trade_pct"] = 0.02
    result = _run(payload)
    assert result["dry_run_status"] == BLOCKED_BY_RISK_ENVELOPE


def test_weak_audit_telemetry_blocks() -> None:
    payload = _safe_payload()
    payload["audit_telemetry"]["secret_scan_required"] = False
    result = _run(payload)
    assert result["dry_run_status"] == BLOCKED_BY_AUDIT_TELEMETRY


def test_weak_dry_run_transport_policy_blocks() -> None:
    payload = _safe_payload()
    payload["dry_run_transport_policy"]["direct_http_import_allowed"] = True
    result = _run(payload)
    assert result["dry_run_status"] == BLOCKED_BY_DRY_RUN_TRANSPORT_CONTRACT


def test_invalid_fake_transport_contract_blocks() -> None:
    result = _run(_safe_payload(), InvalidFakeDryRunTransport())
    assert result["dry_run_status"] == BLOCKED_BY_DRY_RUN_TRANSPORT_CONTRACT
    assert "dry_run_transport_contract_method_missing" in result["dry_run_blockers"]


def test_live_money_authority_true_blocks() -> None:
    payload = _safe_payload()
    payload["demo_account_boundary"]["money_movement_allowed"] = True
    result = _run(payload)
    assert result["dry_run_status"] == BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY
    assert "money_movement_allowed_true" in result["dry_run_blockers"]


def test_sensitive_payload_is_blocked_and_value_not_echoed() -> None:
    payload = _safe_payload()
    payload["api_key"] = "VERY-SENSITIVE-VALUE"
    result = _run(payload)
    assert result["dry_run_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert result["dry_run_ready"] is False
    assert "sensitive_data_provided" in result["dry_run_blockers"]
    assert "VERY-SENSITIVE-VALUE" not in repr(result)


def test_sensitive_key_names_are_blocked() -> None:
    for key in (
        "account_id",
        "oanda_account_id",
        "token_value",
        "api_key",
        "private_key",
        "master_password",
        "vault_password",
    ):
        payload = _safe_payload()
        payload[key] = f"blocked-{key}"
        result = _run(payload)
        assert result["dry_run_status"] == BLOCKED_BY_SENSITIVE_DATA
        assert f"blocked-{key}" not in repr(result)


def test_allowed_safety_metadata_keys_are_not_misclassified_as_sensitive() -> None:
    payload = _safe_payload()
    payload.update(
        {
            "demo_account_reference_present": True,
            "account_identifier_storage_allowed": False,
            "account_identifier_read_allowed": False,
            "account_identifier_values_provided": False,
            "credential_storage_allowed": False,
            "credential_read_allowed": False,
            "credential_request_allowed": False,
            "credential_values_provided": False,
            "credential_values_persisted": False,
            "credential_values_logged": False,
            "broker_api_allowed": False,
            "direct_broker_api_allowed": False,
            "network_call_allowed": False,
            "live_execution_allowed": False,
            "money_movement_allowed": False,
            "bank_access_allowed": False,
            "approval_token_required": True,
            "approval_token_metadata_present": True,
            "raw_approval_phrase_stored": False,
            "raw_voice_audio_stored": False,
            "no_raw_secret_logging": True,
            "no_raw_account_identifier_logging": True,
        }
    )
    result = _run(payload)
    assert result["dry_run_status"] == ONE_ORDER_RUNTIME_DRY_RUN_READY
    assert result["dry_run_blockers"] == []


def test_all_hard_false_authority_fields_remain_false() -> None:
    _assert_hard_false_authority_fields(_run())


def test_no_order_submitted_even_when_fake_transport_completes() -> None:
    payload = _safe_payload()
    payload["dry_run_transport_policy"]["fake_transport_requested"] = True
    result = _run(payload, FakeDryRunTransport())
    assert result["real_order_submitted"] is False
    assert result["demo_broker_order_submitted"] is False
    assert result["sanitized_one_order_runtime_dry_run_packet"]["real_order_submitted"] is False
    assert result["sanitized_one_order_runtime_dry_run_packet"]["demo_broker_order_submitted"] is False


def test_owner_action_queue_contains_review_next_packet() -> None:
    result = _run()
    action_ids = {action["action_id"] for action in result["owner_action_queue"]}
    assert "REVIEW_NEXT_PACKET" in action_ids
    assert "REVIEW_SANITIZED_DRY_RUN_PACKET" in action_ids
    for action in result["owner_action_queue"]:
        assert action["owner_decision_required"] is True
        assert action["live_execution_allowed"] is False
        assert action["money_movement_allowed"] is False
        assert action["real_broker_call_allowed"] is False
        assert action["real_order_submitted"] is False
        assert action["demo_broker_order_submitted"] is False
        assert action["safe_action"]


def test_next_best_packet_routes_to_protected_runtime_execution_when_ready() -> None:
    result = _run()
    assert result["next_best_packet"] == (
        "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_PROTECTED_RUNTIME_EXECUTION_V1"
    )


def test_integration_with_owner_runtime_transport_packet_output() -> None:
    payload = _safe_payload()
    assert payload["owner_runtime_transport_packet_result"]["schema"] == (
        OWNER_RUNTIME_TRANSPORT_PACKET_SCHEMA
    )
    result = _run(payload)
    assert result["dry_run_status"] == ONE_ORDER_RUNTIME_DRY_RUN_READY
    assert result["owner_runtime_transport_packet_summary"]["ready"] is True


def test_production_module_source_contains_no_direct_runtime_api_process_imports() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source


def test_no_unsafe_phrases_in_packet_sources() -> None:
    for path in (MODULE_PATH, DOC_PATH, REPORT_PATH, Path(__file__)):
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8").lower()
        for marker in UNSAFE_MARKERS:
            assert marker not in content
