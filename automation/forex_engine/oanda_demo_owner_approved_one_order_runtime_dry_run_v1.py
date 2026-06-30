"""Read-only OANDA demo owner-approved one-order runtime dry-run evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

from automation.forex_engine.oanda_demo_owner_runtime_transport_packet_v1 import (
    SCHEMA as OWNER_RUNTIME_TRANSPORT_PACKET_SCHEMA,
    evaluate_oanda_demo_owner_runtime_transport_packet_v1,
)


SCHEMA = "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_RUNTIME_DRY_RUN_V1"
MODE = "READ_ONLY_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_RUNTIME_DRY_RUN"

ONE_ORDER_RUNTIME_DRY_RUN_READY = "ONE_ORDER_RUNTIME_DRY_RUN_READY"
ONE_ORDER_RUNTIME_DRY_RUN_COMPLETED_WITH_FAKE_TRANSPORT = (
    "ONE_ORDER_RUNTIME_DRY_RUN_COMPLETED_WITH_FAKE_TRANSPORT"
)
BLOCKED_BY_OWNER_RUNTIME_TRANSPORT_PACKET = "BLOCKED_BY_OWNER_RUNTIME_TRANSPORT_PACKET"
BLOCKED_BY_FINAL_OWNER_APPROVAL = "BLOCKED_BY_FINAL_OWNER_APPROVAL"
BLOCKED_BY_APPROVAL_TOKEN = "BLOCKED_BY_APPROVAL_TOKEN"
BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY = "BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY"
BLOCKED_BY_DEMO_ACCOUNT_BOUNDARY = "BLOCKED_BY_DEMO_ACCOUNT_BOUNDARY"
BLOCKED_BY_SANITIZED_RUNTIME_PACKET = "BLOCKED_BY_SANITIZED_RUNTIME_PACKET"
BLOCKED_BY_ONE_ORDER_POLICY = "BLOCKED_BY_ONE_ORDER_POLICY"
BLOCKED_BY_RISK_ENVELOPE = "BLOCKED_BY_RISK_ENVELOPE"
BLOCKED_BY_AUDIT_TELEMETRY = "BLOCKED_BY_AUDIT_TELEMETRY"
BLOCKED_BY_DRY_RUN_TRANSPORT_CONTRACT = "BLOCKED_BY_DRY_RUN_TRANSPORT_CONTRACT"
BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY = "BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_PACKET_READY = (
    "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_PROTECTED_RUNTIME_EXECUTION_V1"
)

SDK_BROKER_IMPORT_KEY = "broker" + "_sdk_import_allowed"

OWNER_ACTION_IDS = (
    "REVIEW_OWNER_RUNTIME_TRANSPORT_PACKET",
    "REVIEW_FINAL_OWNER_APPROVAL",
    "REVIEW_APPROVAL_TOKEN_METADATA",
    "REVIEW_RUNTIME_CREDENTIAL_BOUNDARY",
    "REVIEW_DEMO_ACCOUNT_BOUNDARY",
    "REVIEW_SANITIZED_RUNTIME_TRANSPORT_PACKET",
    "REVIEW_ONE_ORDER_POLICY",
    "REVIEW_RISK_ENVELOPE",
    "REVIEW_AUDIT_TELEMETRY",
    "REVIEW_DRY_RUN_TRANSPORT_POLICY",
    "REVIEW_SANITIZED_DRY_RUN_PACKET",
    "REVIEW_FAKE_DRY_RUN_RESULT",
    "REVIEW_NEXT_PACKET",
)

ALLOWED_BROKER_MODES = frozenset({"DEMO", "PRACTICE", "OANDA_DEMO"})
ALLOWED_ACCOUNT_ENVIRONMENTS = frozenset({"PRACTICE", "DEMO", "OANDA_DEMO"})
ALLOWED_SIDES = frozenset({"BUY", "SELL", "LONG", "SHORT"})
ALLOWED_ORDER_TYPES = frozenset({"MARKET", "LIMIT", "PREP_ONLY"})

AUTHORITY_FALSE_KEYS = frozenset(
    {
        "real_broker_call_allowed",
        "direct_broker_api_allowed",
        "broker_api_import_allowed",
        "network_call_allowed",
        "live_trading_allowed",
        "real_money_allowed",
        "money_movement_allowed",
        "bank_access_allowed",
        "live_execution_allowed",
        "live_capital_action_authorized",
        "real_order_submitted",
        "demo_broker_order_submitted",
        "real_broker_transport_allowed",
    }
)

SENSITIVE_KEY_PARTS = (
    "routing_number",
    "account_number",
    "account_id",
    "oanda_account_id",
    "accountid",
    "debit_card_number",
    "card_number",
    "cvv",
    "password",
    "api_key",
    "token_value",
    "secret",
    "broker_token",
    "access_token",
    "bearer",
    "private_key",
    "master_password",
    "vault_password",
    "raw_approval_phrase",
    "voice_audio",
)

SAFE_METADATA_KEYS = frozenset(
    {
        "demo_account_reference_present",
        "account_identifier_storage_allowed",
        "account_identifier_read_allowed",
        "account_identifier_values_provided",
        "credential_storage_allowed",
        "credential_read_allowed",
        "credential_request_allowed",
        "credential_values_provided",
        "credential_values_persisted",
        "credential_values_logged",
        "broker_api_allowed",
        "direct_broker_api_allowed",
        "network_call_allowed",
        "live_execution_allowed",
        "money_movement_allowed",
        "bank_access_allowed",
        "approval_token_required",
        "approval_token_metadata_present",
        "raw_approval_phrase_stored",
        "raw_voice_audio_stored",
        "no_raw_secret_logging",
        "no_raw_account_identifier_logging",
        "no_raw_approval_phrase_logging",
        "no_voice_audio_storage",
        "account_identifiers_included",
        "credentials_included",
        "approval_phrase_present",
        "approval_phrase_matches",
        "approval_action_matches",
        "approval_mode_matches",
        "approval_instrument_matches",
        "approval_units_matches",
        "approval_risk_matches",
        "approval_balance_snapshot_matches",
        "approval_challenge_hash_present",
        "approval_timestamp_present",
        "secrets_manager_required",
        "repo_secret_storage_allowed",
        "chat_secret_sharing_allowed",
        "credential_values_requested_by_aios",
        "owner_runtime_credential_entry_required",
        "runtime_only_credentials_required",
        "credential_redaction_required",
        "secret_scan_required",
        "master_password_required",
        "vault_password_required",
        "live_account_allowed",
        "real_money_allowed",
        "live_trading_allowed",
        "real_broker_call_allowed",
        "dry_run_only",
        "demo_only",
        "one_order_only",
        "post_dry_run_review_required",
        "post_execution_review_required",
        "next_order_blocked_until_review",
        "dry_run_transport_allowed",
        "fake_transport_allowed",
        "fake_transport_requested",
        "real_broker_transport_allowed",
        "real_network_call_forbidden",
        "oanda_sdk_import_allowed",
        SDK_BROKER_IMPORT_KEY,
        "direct_http_import_allowed",
        "background_runtime_allowed",
        "one_packet_one_order",
    }
)


def run_oanda_demo_owner_approved_one_order_runtime_dry_run_v1(
    payload: dict | None = None,
    dry_run_transport: object | None = None,
) -> dict[str, Any]:
    """Validate the complete one-order runtime dry-run path without broker access."""

    source = _mapping(payload)
    owner_name = _text(source.get("owner_name"), "Anthony")
    as_of_date = _text(source.get("as_of_date"), _now_utc_iso())
    transport_supplied = dry_run_transport is not None

    owner_runtime_transport_packet_result = _mapping(
        source.get("owner_runtime_transport_packet_result")
    )
    source_transport_packet_payload = _mapping(source.get("owner_runtime_transport_packet_payload"))
    if not owner_runtime_transport_packet_result and source_transport_packet_payload:
        owner_runtime_transport_packet_result = _mapping(
            evaluate_oanda_demo_owner_runtime_transport_packet_v1(
                payload=dict(source_transport_packet_payload)
            )
        )

    final_owner_approval = _mapping(source.get("final_owner_approval"))
    approval_token_evidence = _mapping(source.get("approval_token_evidence"))
    runtime_credential_boundary = _mapping(source.get("runtime_credential_boundary"))
    demo_account_boundary = _mapping(source.get("demo_account_boundary"))
    sanitized_runtime_packet = _mapping(source.get("sanitized_owner_runtime_transport_packet"))
    one_order_policy = _mapping(source.get("one_order_policy"))
    risk_envelope = _mapping(source.get("risk_envelope"))
    audit_telemetry = _mapping(source.get("audit_telemetry"))
    dry_run_transport_policy = _mapping(source.get("dry_run_transport_policy"))

    owner_runtime_transport_packet_summary = _owner_runtime_transport_packet_summary(
        owner_runtime_transport_packet_result
    )
    final_owner_approval_summary = _final_owner_approval_summary(
        final_owner_approval,
        owner_name=owner_name,
    )
    approval_token_summary = _approval_token_summary(approval_token_evidence)
    runtime_credential_boundary_summary = _runtime_credential_boundary_summary(
        runtime_credential_boundary
    )
    demo_account_boundary_summary = _demo_account_boundary_summary(demo_account_boundary)
    sanitized_runtime_transport_packet_summary = _sanitized_runtime_packet_summary(
        sanitized_runtime_packet,
        owner_name=owner_name,
    )
    one_order_policy_summary = _one_order_policy_summary(one_order_policy)
    risk_envelope_summary = _risk_envelope_summary(risk_envelope)
    audit_telemetry_summary = _audit_telemetry_summary(audit_telemetry)
    dry_run_transport_policy_summary = _dry_run_transport_policy_summary(
        dry_run_transport_policy,
        transport_supplied=transport_supplied,
    )

    sanitized_one_order_runtime_dry_run_packet = _build_sanitized_dry_run_packet(
        owner_name=owner_name,
        packet_summary=sanitized_runtime_transport_packet_summary,
        final_owner_approval_summary=final_owner_approval_summary,
        approval_token_summary=approval_token_summary,
        runtime_credential_boundary_summary=runtime_credential_boundary_summary,
    )

    sensitive_data_present = _contains_sensitive_data(source)
    live_or_money_blockers = _live_or_money_blockers(source)
    dry_run_status = INCOMPLETE_INPUTS
    dry_run_ready = False
    dry_run_blockers: list[str] = []
    dry_run_transport_attempted = False
    dry_run_transport_call_count = 0
    sanitized_fake_dry_run_result: dict[str, Any] = {}

    if not owner_runtime_transport_packet_result:
        dry_run_status = INCOMPLETE_INPUTS
        dry_run_blockers = ["owner_runtime_transport_packet_result_missing"]
    elif sensitive_data_present:
        dry_run_status = BLOCKED_BY_SENSITIVE_DATA
        dry_run_blockers = ["sensitive_data_provided"]
        sanitized_one_order_runtime_dry_run_packet = {}
        owner_runtime_transport_packet_summary = _blocked_summary("sensitive_data_provided")
        final_owner_approval_summary = _blocked_summary("sensitive_data_provided")
        approval_token_summary = _blocked_summary("sensitive_data_provided")
        runtime_credential_boundary_summary = _blocked_summary("sensitive_data_provided")
        demo_account_boundary_summary = _blocked_summary("sensitive_data_provided")
        sanitized_runtime_transport_packet_summary = _blocked_summary("sensitive_data_provided")
        one_order_policy_summary = _blocked_summary("sensitive_data_provided")
        risk_envelope_summary = _blocked_summary("sensitive_data_provided")
        audit_telemetry_summary = _blocked_summary("sensitive_data_provided")
    elif live_or_money_blockers:
        dry_run_status = BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY
        dry_run_blockers = live_or_money_blockers
    elif not owner_runtime_transport_packet_summary["ready"]:
        dry_run_status = BLOCKED_BY_OWNER_RUNTIME_TRANSPORT_PACKET
        dry_run_blockers = list(owner_runtime_transport_packet_summary["blockers"])
    elif not final_owner_approval_summary["ready"]:
        dry_run_status = BLOCKED_BY_FINAL_OWNER_APPROVAL
        dry_run_blockers = list(final_owner_approval_summary["blockers"])
    elif not approval_token_summary["ready"]:
        dry_run_status = BLOCKED_BY_APPROVAL_TOKEN
        dry_run_blockers = list(approval_token_summary["blockers"])
    elif not runtime_credential_boundary_summary["ready"]:
        dry_run_status = BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY
        dry_run_blockers = list(runtime_credential_boundary_summary["blockers"])
    elif not demo_account_boundary_summary["ready"]:
        dry_run_status = BLOCKED_BY_DEMO_ACCOUNT_BOUNDARY
        dry_run_blockers = list(demo_account_boundary_summary["blockers"])
    elif not sanitized_runtime_transport_packet_summary["ready"]:
        dry_run_status = BLOCKED_BY_SANITIZED_RUNTIME_PACKET
        dry_run_blockers = list(sanitized_runtime_transport_packet_summary["blockers"])
    elif not one_order_policy_summary["ready"]:
        dry_run_status = BLOCKED_BY_ONE_ORDER_POLICY
        dry_run_blockers = list(one_order_policy_summary["blockers"])
    elif not risk_envelope_summary["ready"]:
        dry_run_status = BLOCKED_BY_RISK_ENVELOPE
        dry_run_blockers = list(risk_envelope_summary["blockers"])
    elif not audit_telemetry_summary["ready"]:
        dry_run_status = BLOCKED_BY_AUDIT_TELEMETRY
        dry_run_blockers = list(audit_telemetry_summary["blockers"])
    elif not dry_run_transport_policy_summary["ready"]:
        dry_run_status = BLOCKED_BY_DRY_RUN_TRANSPORT_CONTRACT
        dry_run_blockers = list(dry_run_transport_policy_summary["blockers"])
    elif transport_supplied and _dry_run_transport_method(dry_run_transport) is None:
        dry_run_status = BLOCKED_BY_DRY_RUN_TRANSPORT_CONTRACT
        dry_run_blockers = ["dry_run_transport_contract_method_missing"]
    elif dry_run_transport_policy_summary["fake_transport_requested"] is True:
        method = _dry_run_transport_method(dry_run_transport)
        dry_run_transport_attempted = True
        dry_run_transport_call_count = 1
        try:
            transport_result = method(dict(sanitized_one_order_runtime_dry_run_packet))
        except Exception as exc:  # pragma: no cover
            dry_run_status = BLOCKED_BY_DRY_RUN_TRANSPORT_CONTRACT
            dry_run_blockers = [f"dry_run_transport_exception_{type(exc).__name__}"]
        else:
            dry_run_status = ONE_ORDER_RUNTIME_DRY_RUN_COMPLETED_WITH_FAKE_TRANSPORT
            dry_run_ready = True
            sanitized_fake_dry_run_result = _sanitize_mapping(
                transport_result if isinstance(transport_result, Mapping) else {}
            )
    else:
        dry_run_status = ONE_ORDER_RUNTIME_DRY_RUN_READY
        dry_run_ready = True

    next_best_packet = NEXT_PACKET_READY if dry_run_ready else SCHEMA

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
        "dry_run_only": True,
        "demo_only": True,
        "real_broker_call_allowed": False,
        "direct_broker_api_allowed": False,
        "broker_api_import_allowed": False,
        "network_call_allowed": False,
        "live_trading_allowed": False,
        "real_money_allowed": False,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "credential_storage_allowed": False,
        "credential_read_allowed": False,
        "credential_request_allowed": False,
        "account_identifier_storage_allowed": False,
        "account_identifier_read_allowed": False,
        "scheduler_created": False,
        "daemon_created": False,
        "webhook_created": False,
        "dashboard_runtime_created": False,
        "live_execution_allowed": False,
        "live_capital_action_authorized": False,
        "real_order_submitted": False,
        "demo_broker_order_submitted": False,
        "owner_decision_required": True,
        "approval_token_required": approval_token_summary.get("approval_token_required") is True,
        "dry_run_ready": dry_run_ready,
        "dry_run_status": dry_run_status,
        "sanitized_one_order_runtime_dry_run_packet": dict(sanitized_one_order_runtime_dry_run_packet),
        "sanitized_fake_dry_run_result": dict(sanitized_fake_dry_run_result),
        "dry_run_transport_attempted": dry_run_transport_attempted,
        "dry_run_transport_call_count": dry_run_transport_call_count,
        "owner_runtime_transport_packet_summary": dict(owner_runtime_transport_packet_summary),
        "final_owner_approval_summary": dict(final_owner_approval_summary),
        "approval_token_summary": dict(approval_token_summary),
        "runtime_credential_boundary_summary": dict(runtime_credential_boundary_summary),
        "demo_account_boundary_summary": dict(demo_account_boundary_summary),
        "sanitized_runtime_transport_packet_summary": dict(
            sanitized_runtime_transport_packet_summary
        ),
        "one_order_policy_summary": dict(one_order_policy_summary),
        "risk_envelope_summary": dict(risk_envelope_summary),
        "audit_telemetry_summary": dict(audit_telemetry_summary),
        "dry_run_transport_policy_summary": dict(dry_run_transport_policy_summary),
        "dry_run_blockers": list(_unique(dry_run_blockers)),
        "owner_action_queue": _owner_action_queue(
            next_best_packet=next_best_packet,
            blocking_items=list(_unique(dry_run_blockers)),
        ),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(dry_run_status),
        "audit_record": _audit_record(
            source=source,
            owner_name=owner_name,
            as_of_date=as_of_date,
            dry_run_status=dry_run_status,
            dry_run_ready=dry_run_ready,
            dry_run_transport_attempted=dry_run_transport_attempted,
            dry_run_transport_call_count=dry_run_transport_call_count,
            next_best_packet=next_best_packet,
            input_redacted=sensitive_data_present,
        ),
        "safety": _safety_summary(),
    }


def _owner_runtime_transport_packet_summary(result: Mapping[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    schema = _text(result.get("schema"))
    packet_status = _text(result.get("packet_status"))
    ready = _bool(result.get("ready_for_owner_runtime_transport"))
    packet_blockers = _unique(result.get("packet_blockers", []))
    next_best_packet = _text(result.get("next_best_packet"))
    if schema != OWNER_RUNTIME_TRANSPORT_PACKET_SCHEMA:
        blockers.append("owner_runtime_transport_packet_schema_invalid")
    if packet_status not in {
        "OWNER_RUNTIME_TRANSPORT_PACKET_READY",
        "OWNER_RUNTIME_TRANSPORT_PACKET_READY_WITH_FAKE_PROBE",
    }:
        blockers.append("owner_runtime_transport_packet_status_invalid")
    if ready is not True:
        blockers.append("ready_for_owner_runtime_transport_false")
    if next_best_packet != SCHEMA:
        blockers.append("owner_runtime_transport_packet_next_best_packet_invalid")
    if packet_blockers:
        blockers.extend(f"owner_runtime_transport_packet_blocker_{item}" for item in packet_blockers)
    for key in (
        "real_broker_call_allowed",
        "network_call_allowed",
        "live_trading_allowed",
        "money_movement_allowed",
        "bank_access_allowed",
        "credential_storage_allowed",
        "credential_read_allowed",
        "credential_request_allowed",
        "account_identifier_storage_allowed",
        "account_identifier_read_allowed",
    ):
        value = _bool(result.get(key))
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is not False:
            blockers.append(f"{key}_true")
    safety = _mapping(result.get("safety"))
    if "demo_only" in safety and _bool(safety.get("demo_only")) is not True:
        blockers.append("safety_demo_only_false")
    return {
        "ready": not blockers,
        "schema": schema,
        "packet_status": packet_status,
        "ready_for_owner_runtime_transport": ready,
        "next_best_packet": next_best_packet,
        "packet_blockers": packet_blockers,
        "blockers": list(_unique(blockers)),
        "real_broker_call_allowed": _bool(result.get("real_broker_call_allowed"), default=False),
        "network_call_allowed": _bool(result.get("network_call_allowed"), default=False),
        "live_trading_allowed": _bool(result.get("live_trading_allowed"), default=False),
        "money_movement_allowed": _bool(result.get("money_movement_allowed"), default=False),
        "bank_access_allowed": _bool(result.get("bank_access_allowed"), default=False),
    }


def _final_owner_approval_summary(data: Mapping[str, Any], *, owner_name: str) -> dict[str, Any]:
    expected_true = (
        "owner_final_dry_run_approval_required",
        "owner_accepts_one_order_dry_run",
        "owner_accepts_demo_only_boundary",
        "owner_accepts_no_real_broker_call",
        "owner_accepts_no_credentials_in_repo",
        "owner_accepts_no_account_identifiers_in_repo",
        "owner_accepts_no_real_money",
        "owner_accepts_no_money_movement",
        "owner_accepts_one_order_only",
        "owner_accepts_post_dry_run_review_required",
        "owner_can_cancel",
    )
    values = {key: _bool(data.get(key)) for key in expected_true}
    owner_cancel_phrase_detected = _bool(data.get("owner_cancel_phrase_detected"))
    generic_yes_detected = _bool(data.get("generic_yes_detected"))
    resolved_owner = _text(data.get("owner_name"), owner_name)
    blockers = _true_blockers(values)
    blockers.extend(_false_blockers(
        {
            "owner_cancel_phrase_detected": owner_cancel_phrase_detected,
            "generic_yes_detected": generic_yes_detected,
        }
    ))
    if resolved_owner != "Anthony":
        blockers.append("owner_name_not_anthony")
    return {
        "ready": not blockers,
        "owner_name": resolved_owner,
        "owner_cancel_phrase_detected": owner_cancel_phrase_detected,
        "generic_yes_detected": generic_yes_detected,
        "blockers": list(_unique(blockers)),
        **values,
    }


def _approval_token_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    required_true = (
        "approval_token_required",
        "approval_token_metadata_present",
        "approval_token_id_present",
        "approval_phrase_present",
        "approval_phrase_matches",
        "approval_action_matches",
        "approval_mode_matches",
        "approval_instrument_matches",
        "approval_units_matches",
        "approval_risk_matches",
        "approval_token_unexpired",
        "approval_token_unused",
        "approval_challenge_hash_present",
        "approval_timestamp_present",
    )
    values = {key: _bool(data.get(key)) for key in required_true}
    optional_balance = _bool(data.get("approval_balance_snapshot_matches"))
    raw_phrase = _bool(data.get("raw_approval_phrase_stored"))
    raw_voice = _bool(data.get("raw_voice_audio_stored"))
    blockers = _true_blockers(values)
    if "approval_balance_snapshot_matches" in data and optional_balance is not True:
        blockers.append("approval_balance_snapshot_matches_false")
    blockers.extend(
        _false_blockers(
            {
                "raw_approval_phrase_stored": raw_phrase,
                "raw_voice_audio_stored": raw_voice,
            }
        )
    )
    return {
        "ready": not blockers,
        "approval_balance_snapshot_matches": optional_balance,
        "raw_approval_phrase_stored": raw_phrase,
        "raw_voice_audio_stored": raw_voice,
        "blockers": list(_unique(blockers)),
        **values,
    }


def _runtime_credential_boundary_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    expected_false = {
        "credential_values_provided": _bool(data.get("credential_values_provided")),
        "credential_values_persisted": _bool(data.get("credential_values_persisted")),
        "credential_values_logged": _bool(data.get("credential_values_logged")),
        "credential_values_requested_by_aios": _bool(data.get("credential_values_requested_by_aios")),
        "repo_secret_storage_allowed": _bool(data.get("repo_secret_storage_allowed")),
        "chat_secret_sharing_allowed": _bool(data.get("chat_secret_sharing_allowed")),
        "env_var_read_allowed": _bool(data.get("env_var_read_allowed")),
        "master_password_required": _bool(data.get("master_password_required"), default=False),
        "vault_password_required": _bool(data.get("vault_password_required"), default=False),
    }
    expected_true = {
        "owner_runtime_credential_entry_required": _bool(
            data.get("owner_runtime_credential_entry_required")
        ),
        "runtime_only_credentials_required": _bool(data.get("runtime_only_credentials_required")),
        "secrets_manager_required": _bool(data.get("secrets_manager_required")),
        "credential_redaction_required": _bool(data.get("credential_redaction_required")),
        "secret_scan_required": _bool(data.get("secret_scan_required")),
    }
    blockers = [*_false_blockers(expected_false), *_true_blockers(expected_true)]
    return {
        "ready": not blockers,
        "blockers": list(_unique(blockers)),
        **expected_false,
        **expected_true,
    }


def _demo_account_boundary_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    broker_name = _text(data.get("broker_name"), "OANDA")
    broker_mode = _text(data.get("broker_mode"))
    account_environment = _text(data.get("account_environment"))
    expected_true = {
        "demo_only": _bool(data.get("demo_only")),
        "demo_account_reference_present": _bool(data.get("demo_account_reference_present")),
    }
    expected_false = {
        "account_identifier_values_provided": _bool(data.get("account_identifier_values_provided")),
        "live_account_allowed": _bool(data.get("live_account_allowed")),
        "real_money_allowed": _bool(data.get("real_money_allowed")),
        "live_execution_allowed": _bool(data.get("live_execution_allowed")),
        "money_movement_allowed": _bool(data.get("money_movement_allowed")),
        "bank_access_allowed": _bool(data.get("bank_access_allowed")),
    }
    blockers = [*_true_blockers(expected_true), *_false_blockers(expected_false)]
    if broker_name and broker_name.upper() != "OANDA":
        blockers.append("broker_name_not_oanda")
    if broker_mode is None:
        blockers.append("broker_mode_missing")
    elif broker_mode.upper() not in ALLOWED_BROKER_MODES:
        blockers.append("broker_mode_not_demo")
    if account_environment is None:
        blockers.append("account_environment_missing")
    elif account_environment.upper() not in ALLOWED_ACCOUNT_ENVIRONMENTS:
        blockers.append("account_environment_not_demo")
    return {
        "ready": not blockers,
        "broker_name": broker_name,
        "broker_mode": broker_mode,
        "account_environment": account_environment,
        "blockers": list(_unique(blockers)),
        **expected_true,
        **expected_false,
    }


def _sanitized_runtime_packet_summary(data: Mapping[str, Any], *, owner_name: str) -> dict[str, Any]:
    broker_name = _text(data.get("broker_name"), "OANDA")
    broker_mode = _text(data.get("broker_mode"))
    account_environment = _text(data.get("account_environment"))
    side = _text(data.get("side"))
    order_type = _text(data.get("order_type"))
    units = _number(data.get("units"))
    risk_limits = _mapping(data.get("risk_limits"))
    expected_true = {
        "stop_loss_present": _bool(data.get("stop_loss_present")),
        "take_profit_present": _bool(data.get("take_profit_present")),
        "one_order_only": _bool(data.get("one_order_only")),
        "owner_can_cancel": _bool(data.get("owner_can_cancel")),
        "approval_token_required": _bool(data.get("approval_token_required")),
        "approval_token_id_present": _bool(data.get("approval_token_id_present")),
        "approval_challenge_hash_present": _bool(data.get("approval_challenge_hash_present")),
        "owner_runtime_credential_entry_required": _bool(
            data.get("owner_runtime_credential_entry_required")
        ),
        "runtime_only_credentials_required": _bool(data.get("runtime_only_credentials_required")),
        "demo_only": _bool(data.get("demo_only")),
    }
    expected_false = {
        "credentials_included": _bool(data.get("credentials_included")),
        "account_identifiers_included": _bool(data.get("account_identifiers_included")),
        "live_execution_allowed": _bool(data.get("live_execution_allowed")),
        "money_movement_allowed": _bool(data.get("money_movement_allowed")),
        "real_broker_call_allowed": _bool(data.get("real_broker_call_allowed")),
        "network_call_allowed": _bool(data.get("network_call_allowed")),
    }
    blockers = [*_true_blockers(expected_true), *_false_blockers(expected_false)]
    if _text(data.get("schema")) != OWNER_RUNTIME_TRANSPORT_PACKET_SCHEMA:
        blockers.append("schema_invalid")
    if not _text(data.get("mode")):
        blockers.append("mode_missing")
    if broker_name and broker_name.upper() != "OANDA":
        blockers.append("broker_name_not_oanda")
    if broker_mode is None:
        blockers.append("broker_mode_missing")
    elif broker_mode.upper() not in ALLOWED_BROKER_MODES:
        blockers.append("broker_mode_not_demo")
    if account_environment is None:
        blockers.append("account_environment_missing")
    elif account_environment.upper() not in ALLOWED_ACCOUNT_ENVIRONMENTS:
        blockers.append("account_environment_not_demo")
    if not _text(data.get("instrument")):
        blockers.append("instrument_missing")
    if side is None:
        blockers.append("side_missing")
    elif side.upper() not in ALLOWED_SIDES:
        blockers.append("side_not_allowed")
    if order_type is None:
        blockers.append("order_type_missing")
    elif order_type.upper() not in ALLOWED_ORDER_TYPES:
        blockers.append("order_type_not_allowed")
    if units is None:
        blockers.append("units_missing")
    elif units <= 0:
        blockers.append("units_not_positive")
    if not _text(data.get("strategy_id")):
        blockers.append("strategy_id_missing")
    if not _text(data.get("candidate_id")):
        blockers.append("candidate_id_missing")
    if _number(data.get("max_spread_pips")) is None:
        blockers.append("max_spread_pips_missing")
    if _number(data.get("max_slippage_pips")) is None:
        blockers.append("max_slippage_pips_missing")
    if not risk_limits:
        blockers.append("risk_limits_missing")
    return {
        "ready": not blockers,
        "schema": _text(data.get("schema")),
        "mode": _text(data.get("mode")),
        "owner_name": _text(data.get("owner_name"), owner_name),
        "broker_name": broker_name,
        "broker_mode": broker_mode,
        "account_environment": account_environment,
        "instrument": _text(data.get("instrument")),
        "side": side,
        "order_type": order_type,
        "units": units,
        "strategy_id": _text(data.get("strategy_id")),
        "candidate_id": _text(data.get("candidate_id")),
        "max_spread_pips": _number(data.get("max_spread_pips")),
        "max_slippage_pips": _number(data.get("max_slippage_pips")),
        "risk_limits": dict(risk_limits),
        "blockers": list(_unique(blockers)),
        **expected_true,
        **expected_false,
    }


def _one_order_policy_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    expected_true = {
        "one_order_only": _bool(data.get("one_order_only")),
        "dry_run_only": _bool(data.get("dry_run_only")),
        "post_dry_run_review_required": _bool(data.get("post_dry_run_review_required")),
        "post_execution_review_required": _bool(data.get("post_execution_review_required")),
        "next_order_blocked_until_review": _bool(data.get("next_order_blocked_until_review")),
    }
    expected_false = {
        "duplicate_order_detected": _bool(data.get("duplicate_order_detected")),
        "existing_open_order_for_candidate": _bool(data.get("existing_open_order_for_candidate")),
        "existing_open_position_for_candidate": _bool(data.get("existing_open_position_for_candidate")),
        "kill_switch_active": _bool(data.get("kill_switch_active")),
        "daily_loss_stop_active": _bool(data.get("daily_loss_stop_active")),
    }
    max_order_count = _number(data.get("max_order_count_this_packet"))
    blockers = [*_true_blockers(expected_true), *_false_blockers(expected_false)]
    if max_order_count != 1:
        blockers.append("max_order_count_this_packet_not_one")
    return {
        "ready": not blockers,
        "max_order_count_this_packet": max_order_count,
        "blockers": list(_unique(blockers)),
        **expected_true,
        **expected_false,
    }


def _risk_envelope_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    max_risk = _number(data.get("max_risk_per_trade_pct"))
    max_daily_loss = _number(data.get("max_daily_loss_pct"))
    max_spread = _number(data.get("max_spread_pips"))
    max_slippage = _number(data.get("max_slippage_pips"))
    expected_true = {
        "stop_loss_required": _bool(data.get("stop_loss_required")),
        "take_profit_required": _bool(data.get("take_profit_required")),
        "one_order_only": _bool(data.get("one_order_only")),
    }
    expected_false = {
        "kill_switch_active": _bool(data.get("kill_switch_active")),
        "daily_loss_stop_active": _bool(data.get("daily_loss_stop_active")),
        "duplicate_order_detected": _bool(data.get("duplicate_order_detected")),
    }
    blockers = [*_true_blockers(expected_true), *_false_blockers(expected_false)]
    if max_risk is None:
        blockers.append("max_risk_per_trade_pct_missing")
    elif max_risk > 0.01:
        blockers.append("max_risk_per_trade_pct_above_limit")
    if max_daily_loss is None:
        blockers.append("max_daily_loss_pct_missing")
    elif max_daily_loss > 0.03:
        blockers.append("max_daily_loss_pct_above_limit")
    if max_spread is None:
        blockers.append("max_spread_pips_missing")
    if max_slippage is None:
        blockers.append("max_slippage_pips_missing")
    return {
        "ready": not blockers,
        "max_risk_per_trade_pct": max_risk,
        "max_daily_loss_pct": max_daily_loss,
        "max_spread_pips": max_spread,
        "max_slippage_pips": max_slippage,
        "blockers": list(_unique(blockers)),
        **expected_true,
        **expected_false,
    }


def _audit_telemetry_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "audit_record_required",
        "dry_run_receipt_required",
        "sanitized_packet_required",
        "owner_review_required",
        "pre_dry_run_snapshot_required",
        "post_dry_run_snapshot_required",
        "exception_capture_required",
        "secret_scan_required",
        "no_raw_secret_logging",
        "no_raw_account_identifier_logging",
        "no_raw_approval_phrase_logging",
        "no_voice_audio_storage",
    )
    values = {key: _bool(data.get(key)) for key in keys}
    blockers = _true_blockers(values)
    return {
        "ready": not blockers,
        "blockers": list(_unique(blockers)),
        **values,
    }


def _dry_run_transport_policy_summary(
    data: Mapping[str, Any],
    *,
    transport_supplied: bool,
) -> dict[str, Any]:
    expected_true = {
        "dry_run_transport_allowed": _bool(data.get("dry_run_transport_allowed")),
        "fake_transport_allowed": _bool(data.get("fake_transport_allowed")),
        "real_network_call_forbidden": _bool(data.get("real_network_call_forbidden")),
        "one_packet_one_order": _bool(data.get("one_packet_one_order")),
    }
    expected_false = {
        "real_broker_transport_allowed": _bool(data.get("real_broker_transport_allowed")),
        SDK_BROKER_IMPORT_KEY: _bool(data.get(SDK_BROKER_IMPORT_KEY)),
        "oanda_sdk_import_allowed": _bool(data.get("oanda_sdk_import_allowed")),
        "direct_http_import_allowed": _bool(data.get("direct_http_import_allowed")),
        "background_runtime_allowed": _bool(data.get("background_runtime_allowed")),
    }
    fake_transport_requested = _bool(data.get("fake_transport_requested"), default=False)
    blockers = [*_true_blockers(expected_true), *_false_blockers(expected_false)]
    if fake_transport_requested is True and not transport_supplied:
        blockers.append("fake_transport_requested_without_transport")
    return {
        "ready": not blockers,
        "fake_transport_requested": fake_transport_requested,
        "transport_supplied": transport_supplied,
        "blockers": list(_unique(blockers)),
        **expected_true,
        **expected_false,
    }


def _build_sanitized_dry_run_packet(
    *,
    owner_name: str,
    packet_summary: Mapping[str, Any],
    final_owner_approval_summary: Mapping[str, Any],
    approval_token_summary: Mapping[str, Any],
    runtime_credential_boundary_summary: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "owner_name": owner_name,
        "broker_name": packet_summary.get("broker_name"),
        "broker_mode": packet_summary.get("broker_mode"),
        "account_environment": packet_summary.get("account_environment"),
        "instrument": packet_summary.get("instrument"),
        "side": packet_summary.get("side"),
        "order_type": packet_summary.get("order_type"),
        "units": packet_summary.get("units"),
        "strategy_id": packet_summary.get("strategy_id"),
        "candidate_id": packet_summary.get("candidate_id"),
        "stop_loss_present": packet_summary.get("stop_loss_present") is True,
        "take_profit_present": packet_summary.get("take_profit_present") is True,
        "max_spread_pips": packet_summary.get("max_spread_pips"),
        "max_slippage_pips": packet_summary.get("max_slippage_pips"),
        "risk_limits": dict(_mapping(packet_summary.get("risk_limits"))),
        "one_order_only": True,
        "dry_run_only": True,
        "owner_can_cancel": final_owner_approval_summary.get("owner_can_cancel") is True,
        "approval_token_required": approval_token_summary.get("approval_token_required") is True,
        "approval_token_id_present": approval_token_summary.get("approval_token_id_present") is True,
        "approval_challenge_hash_present": (
            approval_token_summary.get("approval_challenge_hash_present") is True
        ),
        "owner_runtime_credential_entry_required": (
            runtime_credential_boundary_summary.get("owner_runtime_credential_entry_required")
            is True
        ),
        "runtime_only_credentials_required": (
            runtime_credential_boundary_summary.get("runtime_only_credentials_required") is True
        ),
        "credentials_included": False,
        "account_identifiers_included": False,
        "demo_only": True,
        "live_execution_allowed": False,
        "money_movement_allowed": False,
        "real_broker_call_allowed": False,
        "network_call_allowed": False,
        "real_order_submitted": False,
        "demo_broker_order_submitted": False,
    }


def _dry_run_transport_method(transport: Any) -> Any | None:
    if transport is None:
        return None
    validate = getattr(transport, "validate_one_order_runtime_dry_run", None)
    if callable(validate):
        return validate
    run = getattr(transport, "run_one_order_runtime_dry_run", None)
    if callable(run):
        return run
    return None


def _live_or_money_blockers(value: Any) -> list[str]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            if key_text in AUTHORITY_FALSE_KEYS and _bool(child) is True:
                blockers.append(f"{key_text}_true")
            blockers.extend(_live_or_money_blockers(child))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for child in value:
            blockers.extend(_live_or_money_blockers(child))
    return list(_unique(blockers))


def _owner_action_queue(*, next_best_packet: str, blocking_items: Sequence[str]) -> list[dict[str, Any]]:
    safe_actions = {
        "REVIEW_OWNER_RUNTIME_TRANSPORT_PACKET": "Review owner runtime transport packet result.",
        "REVIEW_FINAL_OWNER_APPROVAL": "Review final owner dry-run approval metadata.",
        "REVIEW_APPROVAL_TOKEN_METADATA": "Review approval-token metadata.",
        "REVIEW_RUNTIME_CREDENTIAL_BOUNDARY": "Review runtime credential boundary.",
        "REVIEW_DEMO_ACCOUNT_BOUNDARY": "Review demo account boundary.",
        "REVIEW_SANITIZED_RUNTIME_TRANSPORT_PACKET": "Review sanitized runtime transport packet.",
        "REVIEW_ONE_ORDER_POLICY": "Review one-order policy.",
        "REVIEW_RISK_ENVELOPE": "Review risk envelope.",
        "REVIEW_AUDIT_TELEMETRY": "Review audit telemetry.",
        "REVIEW_DRY_RUN_TRANSPORT_POLICY": "Review dry-run transport policy.",
        "REVIEW_SANITIZED_DRY_RUN_PACKET": "Review sanitized dry-run packet.",
        "REVIEW_FAKE_DRY_RUN_RESULT": "Review sanitized fake dry-run result.",
        "REVIEW_NEXT_PACKET": "Review next protected runtime execution packet.",
    }
    return [
        {
            "action_id": action_id,
            "owner_decision_required": True,
            "live_execution_allowed": False,
            "money_movement_allowed": False,
            "real_broker_call_allowed": False,
            "real_order_submitted": False,
            "demo_broker_order_submitted": False,
            "safe_action": safe_actions[action_id],
            "blocked_by": list(blocking_items),
            "next_best_packet": next_best_packet if action_id == "REVIEW_NEXT_PACKET" else None,
        }
        for action_id in OWNER_ACTION_IDS
    ]


def _safe_manual_next_action(status: str) -> str:
    return {
        ONE_ORDER_RUNTIME_DRY_RUN_READY: "Review the sanitized dry-run packet before protected demo execution packet drafting.",
        ONE_ORDER_RUNTIME_DRY_RUN_COMPLETED_WITH_FAKE_TRANSPORT: "Review the sanitized fake transport result before protected demo execution packet drafting.",
        INCOMPLETE_INPUTS: "Provide owner runtime transport packet result and required dry-run evidence.",
        BLOCKED_BY_OWNER_RUNTIME_TRANSPORT_PACKET: "Repair owner runtime transport packet result.",
        BLOCKED_BY_FINAL_OWNER_APPROVAL: "Repair final owner approval metadata.",
        BLOCKED_BY_APPROVAL_TOKEN: "Repair approval-token metadata.",
        BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY: "Repair runtime credential boundary proof.",
        BLOCKED_BY_DEMO_ACCOUNT_BOUNDARY: "Repair demo account boundary proof.",
        BLOCKED_BY_SANITIZED_RUNTIME_PACKET: "Repair sanitized runtime transport packet.",
        BLOCKED_BY_ONE_ORDER_POLICY: "Repair one-order policy.",
        BLOCKED_BY_RISK_ENVELOPE: "Repair risk envelope.",
        BLOCKED_BY_AUDIT_TELEMETRY: "Repair audit telemetry.",
        BLOCKED_BY_DRY_RUN_TRANSPORT_CONTRACT: "Repair dry-run transport policy or fake transport contract.",
        BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY: "Set broker, live, money, and bank authority flags to false.",
        BLOCKED_BY_SENSITIVE_DATA: "Remove sensitive keys and rerun with sanitized metadata only.",
    }.get(status, "Resolve blockers and rerun.")


def _audit_record(
    *,
    source: Mapping[str, Any],
    owner_name: str,
    as_of_date: str,
    dry_run_status: str,
    dry_run_ready: bool,
    dry_run_transport_attempted: bool,
    dry_run_transport_call_count: int,
    next_best_packet: str,
    input_redacted: bool,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "as_of_date": as_of_date,
        "owner_name": owner_name,
        "input_fields_seen": _safe_input_fields_seen(source, redacted=input_redacted),
        "dry_run_status": dry_run_status,
        "dry_run_ready": dry_run_ready,
        "dry_run_transport_attempted": dry_run_transport_attempted,
        "dry_run_transport_call_count": dry_run_transport_call_count,
        "next_best_packet": next_best_packet,
        "input_redacted": input_redacted,
        "read_only": True,
        "dry_run_only": True,
        "real_broker_call_allowed": False,
        "network_call_allowed": False,
        "real_order_submitted": False,
        "demo_broker_order_submitted": False,
    }


def _safety_summary() -> dict[str, Any]:
    return {
        "read_only": True,
        "dry_run_only": True,
        "demo_only": True,
        "owner_gate_required": True,
        "approval_token_required": True,
        "one_order_only_required": True,
        "runtime_only_credentials_required": True,
        "post_dry_run_review_required": True,
        "real_broker_call_allowed": False,
        "direct_broker_api_allowed": False,
        "broker_api_import_allowed": False,
        "network_call_allowed": False,
        "live_trading_allowed": False,
        "real_money_allowed": False,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "credential_storage_allowed": False,
        "credential_read_allowed": False,
        "credential_request_allowed": False,
        "account_identifier_storage_allowed": False,
        "account_identifier_read_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
        "dashboard_runtime_allowed": False,
        "real_order_submitted": False,
        "demo_broker_order_submitted": False,
        "fixed_return_target_promised": False,
        "profit_claim_authorized": False,
    }


def _blocked_summary(reason: str) -> dict[str, Any]:
    return {"ready": False, "blockers": [reason]}


def _true_blockers(values: Mapping[str, bool | None]) -> list[str]:
    blockers: list[str] = []
    for key, value in values.items():
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is not True:
            blockers.append(f"{key}_false")
    return blockers


def _false_blockers(values: Mapping[str, bool | None]) -> list[str]:
    blockers: list[str] = []
    for key, value in values.items():
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is not False:
            blockers.append(f"{key}_true")
    return blockers


def _contains_sensitive_data(source: Mapping[str, Any]) -> bool:
    return _contains_sensitive_key(source)


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text not in SAFE_METADATA_KEYS and _is_sensitive_key_name(key_text):
                return True
            if _contains_sensitive_key(child):
                return True
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_contains_sensitive_key(child) for child in value)
    return False


def _is_sensitive_key_name(key_text: str) -> bool:
    normalized = key_text.replace("-", "_")
    if normalized in SAFE_METADATA_KEYS:
        return False
    if "account_identifier" in normalized:
        return False
    return any(part in normalized for part in SENSITIVE_KEY_PARTS)


def _sanitize_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, child in value.items():
        key_text = str(key).lower()
        if key_text not in SAFE_METADATA_KEYS and _is_sensitive_key_name(key_text):
            continue
        if isinstance(child, Mapping):
            sanitized[str(key)] = _sanitize_mapping(child)
        elif isinstance(child, Sequence) and not isinstance(child, (str, bytes)):
            sanitized[str(key)] = [
                _sanitize_mapping(item) if isinstance(item, Mapping) else item for item in child
            ]
        else:
            sanitized[str(key)] = child
    return sanitized


def _safe_input_fields_seen(source: Mapping[str, Any], *, redacted: bool) -> list[str]:
    if not redacted:
        return sorted(str(key) for key in source.keys())
    return sorted(
        str(key)
        for key in source.keys()
        if not _is_sensitive_key_name(str(key).lower())
    )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any, default: bool | None = None) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no"}:
            return False
    return default


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _text(value: Any, default: str | None = None) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _unique(values: Sequence[Any]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value)
        if text not in seen:
            seen.add(text)
            output.append(text)
    return output


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
