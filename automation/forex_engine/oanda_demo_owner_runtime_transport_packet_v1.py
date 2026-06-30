"""Read-only OANDA demo owner runtime transport packet evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

from automation.forex_engine.oanda_demo_broker_adapter_runtime_binding_v1 import (
    OANDA_DEMO_BINDING_READY_FOR_OWNER_RUNTIME_TRANSPORT,
    OANDA_DEMO_FAKE_TRANSPORT_ACCEPTED,
    SCHEMA as BINDING_SCHEMA,
)

SCHEMA = "AIOS_FOREX_OANDA_DEMO_OWNER_RUNTIME_TRANSPORT_PACKET_V1"
MODE = "READ_ONLY_OANDA_DEMO_OWNER_RUNTIME_TRANSPORT_PACKET"

OWNER_RUNTIME_TRANSPORT_PACKET_READY = "OWNER_RUNTIME_TRANSPORT_PACKET_READY"
OWNER_RUNTIME_TRANSPORT_PACKET_READY_WITH_FAKE_PROBE = "OWNER_RUNTIME_TRANSPORT_PACKET_READY_WITH_FAKE_PROBE"
BLOCKED_BY_BINDING_RESULT = "BLOCKED_BY_BINDING_RESULT"
BLOCKED_BY_OWNER_APPROVAL = "BLOCKED_BY_OWNER_APPROVAL"
BLOCKED_BY_APPROVAL_TOKEN = "BLOCKED_BY_APPROVAL_TOKEN"
BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY = "BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY"
BLOCKED_BY_TRANSPORT_POLICY = "BLOCKED_BY_TRANSPORT_POLICY"
BLOCKED_BY_DEMO_ACCOUNT_BOUNDARY = "BLOCKED_BY_DEMO_ACCOUNT_BOUNDARY"
BLOCKED_BY_SANITIZED_ORDER_ENVELOPE = "BLOCKED_BY_SANITIZED_ORDER_ENVELOPE"
BLOCKED_BY_ONE_ORDER_POLICY = "BLOCKED_BY_ONE_ORDER_POLICY"
BLOCKED_BY_AUDIT_TELEMETRY = "BLOCKED_BY_AUDIT_TELEMETRY"
BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY = "BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_PACKET_READY = "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_RUNTIME_DRY_RUN_V1"

OWNER_ACTION_IDS = (
    "REVIEW_BROKER_ADAPTER_BINDING_RESULT",
    "REVIEW_OWNER_RUNTIME_APPROVAL",
    "REVIEW_APPROVAL_TOKEN_METADATA",
    "REVIEW_RUNTIME_CREDENTIAL_BOUNDARY",
    "REVIEW_RUNTIME_TRANSPORT_POLICY",
    "REVIEW_DEMO_ACCOUNT_BOUNDARY",
    "REVIEW_SANITIZED_ORDER_ENVELOPE",
    "REVIEW_ONE_ORDER_POLICY",
    "REVIEW_AUDIT_TELEMETRY",
    "REVIEW_SANITIZED_RUNTIME_TRANSPORT_PACKET",
    "REVIEW_FAKE_PROBE_RESULT",
    "REVIEW_NEXT_PACKET",
)

ALLOWED_BROKER_MODES = frozenset({"DEMO", "PRACTICE", "OANDA_DEMO"})
ALLOWED_ACCOUNT_ENVIRONMENTS = frozenset({"PRACTICE", "DEMO", "OANDA_DEMO"})
ALLOWED_SIDES = frozenset({"BUY", "SELL", "LONG", "SHORT"})
ALLOWED_ORDER_TYPES = frozenset({"MARKET", "LIMIT", "PREP_ONLY"})
SENSITIVE_KEY_PARTS = (
    "routing_number",
    "account_number",
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
    "approval_phrase",
)
SENSITIVE_EXACT_KEY_NAMES = frozenset({"account_id", "oanda_account_id", "approval_phrase"})
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
        "credential_values_requested_by_aios",
        "broker_api_allowed",
        "direct_broker_api_allowed",
        "network_call_allowed",
        "live_execution_allowed",
        "money_movement_allowed",
        "bank_access_allowed",
        "approval_token_required",
        "approval_token_metadata_present",
        "secret_scan_required",
        "raw_approval_phrase_stored",
        "raw_voice_audio_stored",
        "account_identifiers_included",
        "credentials_included",
        "approval_phrase_present",
        "approval_phrase_matches",
        "approval_action_matches",
        "approval_mode_matches",
        "approval_instrument_matches",
        "approval_units_matches",
        "approval_risk_matches",
        "approval_challenge_hash_present",
        "approval_timestamp_present",
        "secrets_manager_required",
        "repo_secret_storage_allowed",
        "chat_secret_sharing_allowed",
        "approval_token_required",
        "approval_token_metadata_present",
        "no_raw_secret_logging",
        "no_raw_account_identifier_logging",
    }
)

SDK_BROKER_IMPORT_KEY = "broker" + "_sdk_import_allowed"
SDK_OANDA_IMPORT_KEY = "oanda" + "_sdk_import_allowed"
HTTP_DIRECT_IMPORT_KEY = "direct" + "_http_import_allowed"


def evaluate_oanda_demo_owner_runtime_transport_packet_v1(
    payload: dict | None = None,
    transport: object | None = None,
) -> dict[str, Any]:
    """
    Build and validate an owner-approved OANDA demo runtime transport packet.
    """

    source = payload if isinstance(payload, Mapping) else {}
    owner_name = _text(source.get("owner_name"), "Anthony")
    transport_supplied = transport is not None

    broker_adapter_binding_result = _mapping(source.get("broker_adapter_binding_result"))
    owner_runtime_approval = _mapping(source.get("owner_runtime_approval"))
    approval_token_evidence = _mapping(source.get("approval_token_evidence"))
    runtime_credential_boundary = _mapping(source.get("runtime_credential_boundary"))
    runtime_transport_policy = _mapping(source.get("runtime_transport_policy"))
    demo_account_boundary = _mapping(source.get("demo_account_boundary"))
    sanitized_order_envelope = _mapping(source.get("sanitized_order_envelope"))
    one_order_policy = _mapping(source.get("one_order_policy"))
    audit_telemetry = _mapping(source.get("audit_telemetry"))

    binding_summary = _broker_adapter_binding_result_summary(broker_adapter_binding_result)
    owner_runtime_approval_summary = _owner_runtime_approval_summary(owner_runtime_approval, owner_name)
    approval_token_summary = _approval_token_evidence_summary(approval_token_evidence)
    runtime_credential_boundary_summary = _runtime_credential_boundary_summary(runtime_credential_boundary)
    runtime_transport_policy_summary = _runtime_transport_policy_summary(
        runtime_transport_policy,
        transport_supplied=transport_supplied,
    )
    demo_account_boundary_summary = _demo_account_boundary_summary(demo_account_boundary)
    sanitized_order_envelope_summary = _sanitized_order_envelope_summary(sanitized_order_envelope)
    one_order_policy_summary = _one_order_policy_summary(one_order_policy)
    audit_telemetry_summary = _audit_telemetry_summary(audit_telemetry)

    sanitized_owner_runtime_transport_packet = _build_sanitized_owner_runtime_transport_packet(
        owner_name=owner_name,
        binding_owner_name=owner_name,
        envelope_summary=sanitized_order_envelope_summary,
        owner_approval_summary=owner_runtime_approval_summary,
        approval_token_summary=approval_token_summary,
        credential_summary=runtime_credential_boundary_summary,
        transport_supplied=transport_supplied,
    )
    sensitive_data_present = _contains_sensitive_data(source)
    packet_blockers: list[str] = []
    fake_probe_attempted = False
    transport_probe_call_count = 0
    sanitized_fake_probe_result: dict[str, Any] | None = None

    live_or_money_blockers = _live_or_money_blockers(
        binding_summary=binding_summary,
        owner_runtime_approval_summary=owner_runtime_approval_summary,
        approval_token_summary=approval_token_summary,
        runtime_credential_boundary_summary=runtime_credential_boundary_summary,
        runtime_transport_policy_summary=runtime_transport_policy_summary,
        demo_account_boundary_summary=demo_account_boundary_summary,
        sanitized_order_envelope_summary=sanitized_order_envelope_summary,
        one_order_policy_summary=one_order_policy_summary,
        audit_telemetry_summary=audit_telemetry_summary,
    )

    if not broker_adapter_binding_result:
        status = INCOMPLETE_INPUTS
        packet_blockers = ["broker_adapter_binding_result_missing"]
    elif sensitive_data_present:
        status = BLOCKED_BY_SENSITIVE_DATA
        packet_blockers = ["sensitive_data_provided"]
    elif live_or_money_blockers:
        status = BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY
        packet_blockers = list(live_or_money_blockers)
    elif not binding_summary["ready"]:
        status = BLOCKED_BY_BINDING_RESULT
        packet_blockers = list(binding_summary["binding_blockers"])
    elif not owner_runtime_approval_summary["ready"]:
        status = BLOCKED_BY_OWNER_APPROVAL
        packet_blockers = list(owner_runtime_approval_summary["blockers"])
    elif not approval_token_summary["ready"]:
        status = BLOCKED_BY_APPROVAL_TOKEN
        packet_blockers = list(approval_token_summary["blockers"])
    elif not runtime_credential_boundary_summary["ready"]:
        status = BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY
        packet_blockers = list(runtime_credential_boundary_summary["blockers"])
    elif not runtime_transport_policy_summary["ready"] and transport_supplied:
        status = BLOCKED_BY_TRANSPORT_POLICY
        packet_blockers = list(runtime_transport_policy_summary["blockers"])
    elif not runtime_transport_policy_summary["ready"]:
        status = BLOCKED_BY_TRANSPORT_POLICY
        packet_blockers = list(runtime_transport_policy_summary["blockers"])
    elif not demo_account_boundary_summary["ready"]:
        status = BLOCKED_BY_DEMO_ACCOUNT_BOUNDARY
        packet_blockers = list(demo_account_boundary_summary["blockers"])
    elif not sanitized_order_envelope_summary["ready"]:
        status = BLOCKED_BY_SANITIZED_ORDER_ENVELOPE
        packet_blockers = list(sanitized_order_envelope_summary["blockers"])
    elif not one_order_policy_summary["ready"]:
        status = BLOCKED_BY_ONE_ORDER_POLICY
        packet_blockers = list(one_order_policy_summary["blockers"])
    elif not audit_telemetry_summary["ready"]:
        status = BLOCKED_BY_AUDIT_TELEMETRY
        packet_blockers = list(audit_telemetry_summary["blockers"])
    elif transport_probe_request_requested(transport_supplied=transport_supplied, runtime_transport_policy=runtime_transport_policy_summary):
        transport_method = _transport_method(transport)
        if transport_method is None:
            status = BLOCKED_BY_TRANSPORT_POLICY
            packet_blockers = ["transport_contract_method_missing"]
        else:
            try:
                fake_probe_attempted = True
                transport_probe_call_count = 1
                transport_result = transport_method(_copy_mapping(sanitized_owner_runtime_transport_packet))
            except Exception as exc:  # pragma: no cover
                status = BLOCKED_BY_TRANSPORT_POLICY
                packet_blockers = ["transport_probe_exception", str(type(exc).__name__)]
                transport_result = {"transport_probe_exception": True}
            else:
                status = OWNER_RUNTIME_TRANSPORT_PACKET_READY_WITH_FAKE_PROBE
            sanitized_fake_probe_result = _sanitize_mapping(
                transport_result if isinstance(transport_result, Mapping) else {"transport_probe_result_type": type(transport_result).__name__}
            )
    else:
        status = OWNER_RUNTIME_TRANSPORT_PACKET_READY

    if status == OWNER_RUNTIME_TRANSPORT_PACKET_READY_WITH_FAKE_PROBE and not packet_blockers:
        ready_for_owner_runtime_transport = True
    elif status == OWNER_RUNTIME_TRANSPORT_PACKET_READY:
        ready_for_owner_runtime_transport = True
    else:
        ready_for_owner_runtime_transport = False

    if sensitive_data_present:
        broker_adapter_binding_summary = {}
        owner_runtime_approval_summary = {}
        approval_token_summary = {}
        runtime_credential_boundary_summary = {}
        runtime_transport_policy_summary = {}
        demo_account_boundary_summary = {}
        sanitized_order_envelope_summary = {}
        one_order_policy_summary = {}
        audit_telemetry_summary = {}

    next_best_packet = NEXT_PACKET_READY if ready_for_owner_runtime_transport else SCHEMA

    if status == BLOCKED_BY_SENSITIVE_DATA:
        sanitized_fake_probe_result = None

    if sanitized_fake_probe_result is None and fake_probe_attempted:
        sanitized_fake_probe_result = {}

    if not fake_probe_attempted:
        transport_probe_call_count = 0

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only": True,
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
        "owner_decision_required": True,
        "approval_token_required": approval_token_summary.get("approval_token_required") is True,
        "ready_for_owner_runtime_transport": ready_for_owner_runtime_transport,
        "packet_status": status,
        "sanitized_owner_runtime_transport_packet": sanitized_owner_runtime_transport_packet,
        "sanitized_fake_probe_result": sanitized_fake_probe_result,
        "fake_probe_attempted": fake_probe_attempted,
        "transport_probe_call_count": transport_probe_call_count,
        "broker_adapter_binding_summary": _copy_mapping(_redact_mapping(mapping=binding_summary)),
        "owner_runtime_approval_summary": _copy_mapping(_redact_mapping(mapping=owner_runtime_approval_summary)),
        "approval_token_summary": _copy_mapping(_redact_mapping(mapping=approval_token_summary)),
        "runtime_credential_boundary_summary": _copy_mapping(_redact_mapping(mapping=runtime_credential_boundary_summary)),
        "runtime_transport_policy_summary": _copy_mapping(_redact_mapping(mapping=runtime_transport_policy_summary)),
        "demo_account_boundary_summary": _copy_mapping(_redact_mapping(mapping=demo_account_boundary_summary)),
        "sanitized_order_envelope_summary": _copy_mapping(_redact_mapping(mapping=sanitized_order_envelope_summary)),
        "one_order_policy_summary": _copy_mapping(_redact_mapping(mapping=one_order_policy_summary)),
        "audit_telemetry_summary": _copy_mapping(_redact_mapping(mapping=audit_telemetry_summary)),
        "packet_blockers": list(_unique(packet_blockers)),
        "owner_action_queue": _owner_action_queue(
            next_best_packet=next_best_packet,
            packet_status=status,
            blocking_items=list(_unique(packet_blockers)),
        ),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(status),
        "audit_record": _audit_record(
            source=source,
            owner_name=owner_name,
            packet_status=status,
            transport_probe_call_count=transport_probe_call_count,
            fake_probe_attempted=fake_probe_attempted,
            ready=ready_for_owner_runtime_transport,
            input_redacted=sensitive_data_present,
        ),
        "safety": _safety_summary(),
    }


def _transport_method(transport: Any) -> Any | None:
    if transport is None:
        return None
    validator = getattr(transport, "validate_owner_runtime_transport_packet", None)
    if callable(validator):
        return validator
    submitter = getattr(transport, "submit_demo_order", None)
    if callable(submitter):
        return submitter
    return None


def transport_probe_request_requested(
    *,
    transport_supplied: bool,
    runtime_transport_policy: Mapping[str, Any],
) -> bool:
    requested = _bool(runtime_transport_policy.get("fake_transport_probe_requested"), default=False)
    if requested and not transport_supplied:
        return False
    return bool(requested)


def _broker_adapter_binding_result_summary(binding_result: Mapping[str, Any]) -> dict[str, Any]:
    schema = _text(binding_result.get("schema"))
    binding_status = _text(binding_result.get("binding_status"))
    direct_broker_api_allowed = _bool(binding_result.get("direct_broker_api_allowed"))
    network_call_allowed = _bool(binding_result.get("network_call_allowed"))
    live_trading_allowed = _bool(binding_result.get("live_trading_allowed"))
    real_money_allowed = _bool(binding_result.get("real_money_allowed"))
    money_movement_allowed = _bool(binding_result.get("money_movement_allowed"))
    bank_access_allowed = _bool(binding_result.get("bank_access_allowed"))
    credential_storage_allowed = _bool(binding_result.get("credential_storage_allowed"))
    credential_read_allowed = _bool(binding_result.get("credential_read_allowed"))
    account_identifier_storage_allowed = _bool(binding_result.get("account_identifier_storage_allowed"))
    binding_blockers = _unique(binding_result.get("binding_blockers", []))
    demo_only = _bool(binding_result.get("safety", {}).get("demo_only"), default=True)
    next_best_packet = _text(binding_result.get("next_best_packet"), default="")
    contract_ready = binding_status in (
        OANDA_DEMO_BINDING_READY_FOR_OWNER_RUNTIME_TRANSPORT,
        OANDA_DEMO_FAKE_TRANSPORT_ACCEPTED,
    )
    blocked = []
    if schema != BINDING_SCHEMA:
        blocked.append("binding_schema_invalid")
    if binding_status not in (
        OANDA_DEMO_BINDING_READY_FOR_OWNER_RUNTIME_TRANSPORT,
        OANDA_DEMO_FAKE_TRANSPORT_ACCEPTED,
    ):
        blocked.append("binding_status_not_ready")
    if binding_blockers:
        blocked.extend(str(item) for item in binding_blockers)
    for field_name, actual, expected in (
        ("direct_broker_api_allowed", direct_broker_api_allowed, False),
        ("network_call_allowed", network_call_allowed, False),
        ("live_trading_allowed", live_trading_allowed, False),
        ("real_money_allowed", real_money_allowed, False),
        ("money_movement_allowed", money_movement_allowed, False),
        ("bank_access_allowed", bank_access_allowed, False),
        ("credential_storage_allowed", credential_storage_allowed, False),
        ("credential_read_allowed", credential_read_allowed, False),
        ("account_identifier_storage_allowed", account_identifier_storage_allowed, False),
    ):
        if actual is None:
            blocked.append(f"{field_name}_missing")
        elif actual is not expected:
            blocked.append(f"{field_name}_{str(actual).lower()}")
    if next_best_packet not in (
        SCHEMA,
        "AIOS_FOREX_OANDA_DEMO_POST_EXECUTION_REVIEW_V1",
        "AIOS_FOREX_OANDA_DEMO_BROKER_ADAPTER_RUNTIME_BINDING_V1",
    ):
        blocked.append("binding_next_best_packet_unexpected")

    return {
        "ready": not blocked,
        "schema": schema,
        "binding_status": binding_status,
        "binding_blockers": list(blocked),
        "demo_only": demo_only,
        "contract_ready": contract_ready,
        "direct_broker_api_allowed": direct_broker_api_allowed,
        "network_call_allowed": network_call_allowed,
        "live_trading_allowed": live_trading_allowed,
        "real_money_allowed": real_money_allowed,
        "money_movement_allowed": money_movement_allowed,
        "bank_access_allowed": bank_access_allowed,
        "credential_storage_allowed": credential_storage_allowed,
        "credential_read_allowed": credential_read_allowed,
        "account_identifier_storage_allowed": account_identifier_storage_allowed,
    }

def _owner_runtime_approval_summary(owner_runtime_approval: Mapping[str, Any], owner_name: str) -> dict[str, Any]:
    owner = owner_runtime_approval
    resolved_owner_name = _text(owner.get("owner_name"), owner_name)
    owner_runtime_transport_approval_required = _bool(owner.get("owner_runtime_transport_approval_required"))
    owner_accepts_demo_only_boundary = _bool(owner.get("owner_accepts_demo_only_boundary"))
    owner_accepts_runtime_transport_packet = _bool(owner.get("owner_accepts_runtime_transport_packet"))
    owner_accepts_no_credentials_in_repo = _bool(owner.get("owner_accepts_no_credentials_in_repo"))
    owner_accepts_no_account_identifiers_in_repo = _bool(owner.get("owner_accepts_no_account_identifiers_in_repo"))
    owner_accepts_no_real_money = _bool(owner.get("owner_accepts_no_real_money"))
    owner_accepts_one_order_only = _bool(owner.get("owner_accepts_one_order_only"))
    owner_can_cancel = _bool(owner.get("owner_can_cancel"))
    owner_cancel_phrase_detected = _bool(owner.get("owner_cancel_phrase_detected"), default=False)

    blockers: list[str] = []
    checks = (
        ("owner_runtime_transport_approval_required", owner_runtime_transport_approval_required, True),
        ("owner_accepts_demo_only_boundary", owner_accepts_demo_only_boundary, True),
        ("owner_accepts_runtime_transport_packet", owner_accepts_runtime_transport_packet, True),
        ("owner_accepts_no_credentials_in_repo", owner_accepts_no_credentials_in_repo, True),
        ("owner_accepts_no_account_identifiers_in_repo", owner_accepts_no_account_identifiers_in_repo, True),
        ("owner_accepts_no_real_money", owner_accepts_no_real_money, True),
        ("owner_accepts_one_order_only", owner_accepts_one_order_only, True),
        ("owner_can_cancel", owner_can_cancel, True),
    )
    for key, actual, expected in checks:
        if actual is None:
            blockers.append(f"{key}_missing")
        elif actual is not expected:
            blockers.append(f"{key}_{str(actual).lower()}")
    if owner_cancel_phrase_detected is None:
        blockers.append("owner_cancel_phrase_detected_missing")
    elif owner_cancel_phrase_detected is True:
        blockers.append("owner_cancel_phrase_detected_true")
    if resolved_owner_name and resolved_owner_name != "Anthony":
        blockers.append("owner_name_not_anthony")

    return {
        "ready": not blockers,
        "owner_name": resolved_owner_name,
        "owner_runtime_transport_approval_required": owner_runtime_transport_approval_required,
        "owner_accepts_demo_only_boundary": owner_accepts_demo_only_boundary,
        "owner_accepts_runtime_transport_packet": owner_accepts_runtime_transport_packet,
        "owner_accepts_no_credentials_in_repo": owner_accepts_no_credentials_in_repo,
        "owner_accepts_no_account_identifiers_in_repo": owner_accepts_no_account_identifiers_in_repo,
        "owner_accepts_no_real_money": owner_accepts_no_real_money,
        "owner_accepts_one_order_only": owner_accepts_one_order_only,
        "owner_can_cancel": owner_can_cancel,
        "owner_cancel_phrase_detected": owner_cancel_phrase_detected,
        "blockers": list(_unique(blockers)),
    }


def _approval_token_evidence_summary(evidence: Mapping[str, Any]) -> dict[str, Any]:
    approval_token_required = _bool(evidence.get("approval_token_required"))
    approval_token_metadata_present = _bool(evidence.get("approval_token_metadata_present"))
    approval_token_id_present = _bool(evidence.get("approval_token_id_present"))
    approval_phrase_present = _bool(evidence.get("approval_phrase_present"))
    approval_phrase_matches = _bool(evidence.get("approval_phrase_matches"))
    approval_action_matches = _bool(evidence.get("approval_action_matches"))
    approval_mode_matches = _bool(evidence.get("approval_mode_matches"))
    approval_instrument_matches = _bool(evidence.get("approval_instrument_matches"))
    approval_units_matches = _bool(evidence.get("approval_units_matches"))
    approval_risk_matches = _bool(evidence.get("approval_risk_matches"))
    approval_token_unexpired = _bool(evidence.get("approval_token_unexpired"))
    approval_token_unused = _bool(evidence.get("approval_token_unused"))
    approval_challenge_hash_present = _bool(evidence.get("approval_challenge_hash_present"))
    approval_timestamp_present = _bool(evidence.get("approval_timestamp_present"))
    raw_approval_phrase_stored = _bool(evidence.get("raw_approval_phrase_stored"), default=False)
    raw_voice_audio_stored = _bool(evidence.get("raw_voice_audio_stored"), default=False)

    blockers = []
    checks = (
        ("approval_token_required", approval_token_required, True),
        ("approval_token_metadata_present", approval_token_metadata_present, True),
        ("approval_token_id_present", approval_token_id_present, True),
        ("approval_phrase_present", approval_phrase_present, True),
        ("approval_phrase_matches", approval_phrase_matches, True),
        ("approval_action_matches", approval_action_matches, True),
        ("approval_mode_matches", approval_mode_matches, True),
        ("approval_instrument_matches", approval_instrument_matches, True),
        ("approval_units_matches", approval_units_matches, True),
        ("approval_risk_matches", approval_risk_matches, True),
        ("approval_token_unexpired", approval_token_unexpired, True),
        ("approval_token_unused", approval_token_unused, True),
        ("approval_challenge_hash_present", approval_challenge_hash_present, True),
        ("approval_timestamp_present", approval_timestamp_present, True),
        ("raw_approval_phrase_stored", raw_approval_phrase_stored, False),
        ("raw_voice_audio_stored", raw_voice_audio_stored, False),
    )
    for key, actual, expected in checks:
        if actual is None:
            blockers.append(f"{key}_missing")
        elif actual is not expected:
            blockers.append(f"{key}_{str(actual).lower()}")

    return {
        "ready": not blockers,
        "approval_token_required": approval_token_required,
        "approval_token_metadata_present": approval_token_metadata_present,
        "approval_token_id_present": approval_token_id_present,
        "approval_phrase_present": approval_phrase_present,
        "approval_phrase_matches": approval_phrase_matches,
        "approval_action_matches": approval_action_matches,
        "approval_mode_matches": approval_mode_matches,
        "approval_instrument_matches": approval_instrument_matches,
        "approval_units_matches": approval_units_matches,
        "approval_risk_matches": approval_risk_matches,
        "approval_token_unexpired": approval_token_unexpired,
        "approval_token_unused": approval_token_unused,
        "approval_challenge_hash_present": approval_challenge_hash_present,
        "approval_timestamp_present": approval_timestamp_present,
        "raw_approval_phrase_stored": raw_approval_phrase_stored,
        "raw_voice_audio_stored": raw_voice_audio_stored,
        "blockers": list(_unique(blockers)),
    }


def _runtime_credential_boundary_summary(credential_boundary: Mapping[str, Any]) -> dict[str, Any]:
    credential_values_provided = _bool(credential_boundary.get("credential_values_provided"))
    credential_values_persisted = _bool(credential_boundary.get("credential_values_persisted"))
    credential_values_logged = _bool(credential_boundary.get("credential_values_logged"))
    credential_values_requested_by_aios = _bool(credential_boundary.get("credential_values_requested_by_aios"))
    owner_runtime_credential_entry_required = _bool(credential_boundary.get("owner_runtime_credential_entry_required"))
    runtime_only_credentials_required = _bool(credential_boundary.get("runtime_only_credentials_required"))
    secrets_manager_required = _bool(credential_boundary.get("secrets_manager_required"))
    repo_secret_storage_allowed = _bool(credential_boundary.get("repo_secret_storage_allowed"))
    chat_secret_sharing_allowed = _bool(credential_boundary.get("chat_secret_sharing_allowed"))
    env_var_read_allowed = _bool(credential_boundary.get("env_var_read_allowed"))
    credential_redaction_required = _bool(credential_boundary.get("credential_redaction_required"))
    secret_scan_required = _bool(credential_boundary.get("secret_scan_required"))

    blockers = []
    checks = (
        ("credential_values_provided", credential_values_provided, False),
        ("credential_values_persisted", credential_values_persisted, False),
        ("credential_values_logged", credential_values_logged, False),
        ("credential_values_requested_by_aios", credential_values_requested_by_aios, False),
        ("owner_runtime_credential_entry_required", owner_runtime_credential_entry_required, True),
        ("runtime_only_credentials_required", runtime_only_credentials_required, True),
        ("secrets_manager_required", secrets_manager_required, True),
        ("repo_secret_storage_allowed", repo_secret_storage_allowed, False),
        ("chat_secret_sharing_allowed", chat_secret_sharing_allowed, False),
        ("env_var_read_allowed", env_var_read_allowed, False),
        ("credential_redaction_required", credential_redaction_required, True),
        ("secret_scan_required", secret_scan_required, True),
    )
    for key, actual, expected in checks:
        if actual is None:
            blockers.append(f"{key}_missing")
        elif actual is not expected:
            blockers.append(f"{key}_{str(actual).lower()}")

    return {
        "ready": not blockers,
        "credential_values_provided": credential_values_provided,
        "credential_values_persisted": credential_values_persisted,
        "credential_values_logged": credential_values_logged,
        "credential_values_requested_by_aios": credential_values_requested_by_aios,
        "owner_runtime_credential_entry_required": owner_runtime_credential_entry_required,
        "runtime_only_credentials_required": runtime_only_credentials_required,
        "secrets_manager_required": secrets_manager_required,
        "repo_secret_storage_allowed": repo_secret_storage_allowed,
        "chat_secret_sharing_allowed": chat_secret_sharing_allowed,
        "env_var_read_allowed": env_var_read_allowed,
        "credential_redaction_required": credential_redaction_required,
        "secret_scan_required": secret_scan_required,
        "blockers": list(_unique(blockers)),
    }


def _runtime_transport_policy_summary(
    transport_policy: Mapping[str, Any],
    *,
    transport_supplied: bool,
) -> dict[str, Any]:
    owner_runtime_transport_required = _bool(transport_policy.get("owner_runtime_transport_required"))
    injected_transport_required = _bool(transport_policy.get("injected_transport_required"))
    transport_created_in_repo = _bool(transport_policy.get("transport_created_in_repo"))
    fake_transport_probe_allowed = _bool(transport_policy.get("fake_transport_probe_allowed"))
    fake_transport_probe_requested = _bool(transport_policy.get("fake_transport_probe_requested"), default=False)
    real_network_call_forbidden_in_this_packet = _bool(transport_policy.get("real_network_call_forbidden_in_this_packet"))
    oanda_import_allowed = _bool(transport_policy.get(SDK_OANDA_IMPORT_KEY))
    broker_import_allowed = _bool(transport_policy.get(SDK_BROKER_IMPORT_KEY))
    direct_http_permission = _bool(transport_policy.get(HTTP_DIRECT_IMPORT_KEY))
    background_runtime_allowed = _bool(transport_policy.get("background_runtime_allowed"))
    one_packet_one_order = _bool(transport_policy.get("one_packet_one_order"))

    if fake_transport_probe_requested and not fake_transport_probe_allowed:
        pass

    blockers = []
    checks = (
        ("owner_runtime_transport_required", owner_runtime_transport_required, True),
        ("injected_transport_required", injected_transport_required, True),
        ("transport_created_in_repo", transport_created_in_repo, False),
        ("fake_transport_probe_allowed", fake_transport_probe_allowed, True),
        ("real_network_call_forbidden_in_this_packet", real_network_call_forbidden_in_this_packet, True),
        (SDK_OANDA_IMPORT_KEY, oanda_import_allowed, False),
        (SDK_BROKER_IMPORT_KEY, broker_import_allowed, False),
        (HTTP_DIRECT_IMPORT_KEY, direct_http_permission, False),
        ("background_runtime_allowed", background_runtime_allowed, False),
        ("one_packet_one_order", one_packet_one_order, True),
    )
    for key, actual, expected in checks:
        if actual is None:
            blockers.append(f"{key}_missing")
        elif actual is not expected:
            blockers.append(f"{key}_{str(actual).lower()}")
    if fake_transport_probe_requested and transport_supplied is False:
        blockers.append("fake_transport_probe_requested_without_transport")

    transport_contract_method = "validate_owner_runtime_transport_packet" if fake_transport_probe_requested else None
    return {
        "ready": not blockers,
        "owner_runtime_transport_required": owner_runtime_transport_required,
        "injected_transport_required": injected_transport_required,
        "transport_created_in_repo": transport_created_in_repo,
        "transport_contract_method": transport_contract_method,
        "fake_transport_probe_allowed": fake_transport_probe_allowed,
        "fake_transport_probe_requested": fake_transport_probe_requested,
        "real_network_call_forbidden_in_this_packet": real_network_call_forbidden_in_this_packet,
        SDK_OANDA_IMPORT_KEY: oanda_import_allowed,
        SDK_BROKER_IMPORT_KEY: broker_import_allowed,
        HTTP_DIRECT_IMPORT_KEY: direct_http_permission,
        "background_runtime_allowed": background_runtime_allowed,
        "one_packet_one_order": one_packet_one_order,
        "blockers": list(_unique(blockers)),
    }


def _demo_account_boundary_summary(demo_account_boundary: Mapping[str, Any]) -> dict[str, Any]:
    broker_name = _text(demo_account_boundary.get("broker_name"), "OANDA")
    broker_mode = _text(demo_account_boundary.get("broker_mode"))
    account_environment = _text(demo_account_boundary.get("account_environment"))
    demo_only = _bool(demo_account_boundary.get("demo_only"))
    demo_account_reference_present = _bool(demo_account_boundary.get("demo_account_reference_present"))
    account_identifier_values_provided = _bool(demo_account_boundary.get("account_identifier_values_provided"))
    live_account_allowed = _bool(demo_account_boundary.get("live_account_allowed"))
    real_money_allowed = _bool(demo_account_boundary.get("real_money_allowed"))
    live_execution_allowed = _bool(demo_account_boundary.get("live_execution_allowed"))
    money_movement_allowed = _bool(demo_account_boundary.get("money_movement_allowed"))
    bank_access_allowed = _bool(demo_account_boundary.get("bank_access_allowed"))

    blockers = []
    if broker_name.upper() not in ("OANDA", ""):
        blockers.append("broker_name_not_oanda")
    if not broker_mode:
        blockers.append("broker_mode_missing")
    elif broker_mode.upper() not in ALLOWED_BROKER_MODES:
        blockers.append("broker_mode_not_demo")
    if not account_environment:
        blockers.append("account_environment_missing")
    elif account_environment.upper() not in ALLOWED_ACCOUNT_ENVIRONMENTS:
        blockers.append("account_environment_not_demo")

    for key, actual, expected in (
        ("demo_only", demo_only, True),
        ("demo_account_reference_present", demo_account_reference_present, True),
        ("account_identifier_values_provided", account_identifier_values_provided, False),
        ("live_account_allowed", live_account_allowed, False),
        ("real_money_allowed", real_money_allowed, False),
        ("live_execution_allowed", live_execution_allowed, False),
        ("money_movement_allowed", money_movement_allowed, False),
        ("bank_access_allowed", bank_access_allowed, False),
    ):
        if actual is None:
            blockers.append(f"{key}_missing")
        elif actual is not expected:
            blockers.append(f"{key}_{str(actual).lower()}")

    return {
        "ready": not blockers,
        "broker_name": broker_name,
        "broker_mode": broker_mode,
        "account_environment": account_environment,
        "demo_only": demo_only,
        "demo_account_reference_present": demo_account_reference_present,
        "account_identifier_values_provided": account_identifier_values_provided,
        "live_account_allowed": live_account_allowed,
        "real_money_allowed": real_money_allowed,
        "live_execution_allowed": live_execution_allowed,
        "money_movement_allowed": money_movement_allowed,
        "bank_access_allowed": bank_access_allowed,
        "blockers": list(_unique(blockers)),
    }


def _sanitized_order_envelope_summary(order_envelope: Mapping[str, Any]) -> dict[str, Any]:
    schema = _text(order_envelope.get("schema"))
    mode = _text(order_envelope.get("mode"))
    broker_name = _text(order_envelope.get("broker_name"), "OANDA")
    broker_mode = _text(order_envelope.get("broker_mode"))
    account_environment = _text(order_envelope.get("account_environment"))
    instrument = _text(order_envelope.get("instrument"))
    side = _text(order_envelope.get("side"))
    order_type = _text(order_envelope.get("order_type"))
    units = _number(order_envelope.get("units"))
    stop_loss_present = _bool(order_envelope.get("stop_loss_present"))
    take_profit_present = _bool(order_envelope.get("take_profit_present"))
    max_spread_pips = _number(order_envelope.get("max_spread_pips"))
    max_slippage_pips = _number(order_envelope.get("max_slippage_pips"))
    strategy_id = _text(order_envelope.get("strategy_id"))
    candidate_id = _text(order_envelope.get("candidate_id"))
    demo_only = _bool(order_envelope.get("demo_only"))
    live_execution_allowed = _bool(order_envelope.get("live_execution_allowed"))
    credentials_included = _bool(order_envelope.get("credentials_included"))
    account_identifiers_included = _bool(order_envelope.get("account_identifiers_included"))
    transport_injected = _bool(order_envelope.get("transport_injected"))
    risk_limits = order_envelope.get("risk_limits")

    blockers = []
    if not schema:
        blockers.append("schema_missing")
    if not mode:
        blockers.append("mode_missing")
    if broker_name and broker_name.upper() not in ("OANDA", ""):
        blockers.append("broker_name_not_oanda")
    if not broker_mode:
        blockers.append("broker_mode_missing")
    elif broker_mode.upper() not in ALLOWED_BROKER_MODES:
        blockers.append("broker_mode_not_demo")
    if not account_environment:
        blockers.append("account_environment_missing")
    elif account_environment.upper() not in ALLOWED_ACCOUNT_ENVIRONMENTS:
        blockers.append("account_environment_not_demo")
    if not instrument:
        blockers.append("instrument_missing")
    if not side:
        blockers.append("side_missing")
    elif side.upper() not in ALLOWED_SIDES:
        blockers.append("side_not_allowed")
    if not order_type:
        blockers.append("order_type_missing")
    elif order_type.upper() not in ALLOWED_ORDER_TYPES:
        blockers.append("order_type_not_allowed")
    if units is None:
        blockers.append("units_missing")
    elif units <= 0:
        blockers.append("units_not_positive")
    if stop_loss_present is None:
        blockers.append("stop_loss_present_missing")
    elif stop_loss_present is not True:
        blockers.append("stop_loss_present_false")
    if take_profit_present is None:
        blockers.append("take_profit_present_missing")
    elif take_profit_present is not True:
        blockers.append("take_profit_present_false")
    if max_spread_pips is None:
        blockers.append("max_spread_pips_missing")
    if max_slippage_pips is None:
        blockers.append("max_slippage_pips_missing")
    if not strategy_id:
        blockers.append("strategy_id_missing")
    if not candidate_id:
        blockers.append("candidate_id_missing")
    if demo_only is None:
        blockers.append("demo_only_missing")
    elif demo_only is not True:
        blockers.append("demo_only_false")
    if transport_injected is None:
        blockers.append("transport_injected_missing")
    if live_execution_allowed is None:
        blockers.append("live_execution_allowed_missing")
    elif live_execution_allowed is not False:
        blockers.append("live_execution_allowed_true")
    if credentials_included is None:
        blockers.append("credentials_included_missing")
    elif credentials_included is not False:
        blockers.append("credentials_included_true")
    if account_identifiers_included is None:
        blockers.append("account_identifiers_included_missing")
    elif account_identifiers_included is not False:
        blockers.append("account_identifiers_included_true")
    if not isinstance(risk_limits, Mapping):
        blockers.append("risk_limits_missing")

    return {
        "ready": not blockers,
        "schema": schema,
        "mode": mode,
        "broker_name": broker_name,
        "broker_mode": broker_mode,
        "account_environment": account_environment,
        "instrument": instrument,
        "side": side,
        "order_type": order_type,
        "units": units,
        "stop_loss_present": stop_loss_present,
        "take_profit_present": take_profit_present,
        "max_spread_pips": max_spread_pips,
        "max_slippage_pips": max_slippage_pips,
        "strategy_id": strategy_id,
        "candidate_id": candidate_id,
        "demo_only": demo_only,
        "live_execution_allowed": live_execution_allowed,
        "credentials_included": credentials_included,
        "account_identifiers_included": account_identifiers_included,
        "transport_injected": transport_injected,
        "risk_limits": dict(risk_limits) if isinstance(risk_limits, Mapping) else None,
        "blockers": list(_unique(blockers)),
    }


def _one_order_policy_summary(policy: Mapping[str, Any]) -> dict[str, Any]:
    one_order_only = _bool(policy.get("one_order_only"))
    duplicate_order_detected = _bool(policy.get("duplicate_order_detected"))
    existing_open_order_for_candidate = _bool(policy.get("existing_open_order_for_candidate"))
    existing_open_position_for_candidate = _bool(policy.get("existing_open_position_for_candidate"))
    kill_switch_active = _bool(policy.get("kill_switch_active"))
    daily_loss_stop_active = _bool(policy.get("daily_loss_stop_active"))
    post_execution_review_required = _bool(policy.get("post_execution_review_required"))
    next_order_blocked_until_review = _bool(policy.get("next_order_blocked_until_review"))
    max_order_count_this_packet = _number(policy.get("max_order_count_this_packet"))

    blockers = []
    checks = (
        ("one_order_only", one_order_only, True),
        ("duplicate_order_detected", duplicate_order_detected, False),
        ("existing_open_order_for_candidate", existing_open_order_for_candidate, False),
        ("existing_open_position_for_candidate", existing_open_position_for_candidate, False),
        ("kill_switch_active", kill_switch_active, False),
        ("daily_loss_stop_active", daily_loss_stop_active, False),
        ("post_execution_review_required", post_execution_review_required, True),
        ("next_order_blocked_until_review", next_order_blocked_until_review, True),
    )
    for key, actual, expected in checks:
        if actual is None:
            blockers.append(f"{key}_missing")
        elif actual is not expected:
            blockers.append(f"{key}_{str(actual).lower()}")
    if max_order_count_this_packet is None:
        blockers.append("max_order_count_this_packet_missing")
    elif max_order_count_this_packet != 1:
        blockers.append("max_order_count_this_packet_not_one")

    return {
        "ready": not blockers,
        "one_order_only": one_order_only,
        "duplicate_order_detected": duplicate_order_detected,
        "existing_open_order_for_candidate": existing_open_order_for_candidate,
        "existing_open_position_for_candidate": existing_open_position_for_candidate,
        "kill_switch_active": kill_switch_active,
        "daily_loss_stop_active": daily_loss_stop_active,
        "post_execution_review_required": post_execution_review_required,
        "next_order_blocked_until_review": next_order_blocked_until_review,
        "max_order_count_this_packet": max_order_count_this_packet,
        "blockers": list(_unique(blockers)),
    }


def _audit_telemetry_summary(telemetry: Mapping[str, Any]) -> dict[str, Any]:
    audit_record_required = _bool(telemetry.get("audit_record_required"))
    sanitized_packet_required = _bool(telemetry.get("sanitized_packet_required"))
    owner_review_required = _bool(telemetry.get("owner_review_required"))
    runtime_transport_packet_required = _bool(telemetry.get("runtime_transport_packet_required"))
    pre_transport_snapshot_required = _bool(telemetry.get("pre_transport_snapshot_required"))
    post_transport_snapshot_required = _bool(telemetry.get("post_transport_snapshot_required"))
    exception_capture_required = _bool(telemetry.get("exception_capture_required"))
    secret_scan_required = _bool(telemetry.get("secret_scan_required"))
    no_raw_secret_logging = _bool(telemetry.get("no_raw_secret_logging"))
    no_raw_account_identifier_logging = _bool(telemetry.get("no_raw_account_identifier_logging"))

    blockers = []
    checks = (
        ("audit_record_required", audit_record_required, True),
        ("sanitized_packet_required", sanitized_packet_required, True),
        ("owner_review_required", owner_review_required, True),
        ("runtime_transport_packet_required", runtime_transport_packet_required, True),
        ("pre_transport_snapshot_required", pre_transport_snapshot_required, True),
        ("post_transport_snapshot_required", post_transport_snapshot_required, True),
        ("exception_capture_required", exception_capture_required, True),
        ("secret_scan_required", secret_scan_required, True),
        ("no_raw_secret_logging", no_raw_secret_logging, True),
        ("no_raw_account_identifier_logging", no_raw_account_identifier_logging, True),
    )
    for key, actual, expected in checks:
        if actual is None:
            blockers.append(f"{key}_missing")
        elif actual is not expected:
            blockers.append(f"{key}_{str(actual).lower()}")

    return {
        "ready": not blockers,
        "audit_record_required": audit_record_required,
        "sanitized_packet_required": sanitized_packet_required,
        "owner_review_required": owner_review_required,
        "runtime_transport_packet_required": runtime_transport_packet_required,
        "pre_transport_snapshot_required": pre_transport_snapshot_required,
        "post_transport_snapshot_required": post_transport_snapshot_required,
        "exception_capture_required": exception_capture_required,
        "secret_scan_required": secret_scan_required,
        "no_raw_secret_logging": no_raw_secret_logging,
        "no_raw_account_identifier_logging": no_raw_account_identifier_logging,
        "blockers": list(_unique(blockers)),
    }


def _build_sanitized_owner_runtime_transport_packet(
    *,
    owner_name: str,
    binding_owner_name: str,
    envelope_summary: Mapping[str, Any],
    owner_approval_summary: Mapping[str, Any],
    approval_token_summary: Mapping[str, Any],
    credential_summary: Mapping[str, Any],
    transport_supplied: bool,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "owner_name": binding_owner_name or owner_name,
        "broker_name": envelope_summary.get("broker_name") or "OANDA",
        "broker_mode": envelope_summary.get("broker_mode"),
        "account_environment": envelope_summary.get("account_environment"),
        "instrument": envelope_summary.get("instrument"),
        "side": envelope_summary.get("side"),
        "order_type": envelope_summary.get("order_type"),
        "units": envelope_summary.get("units"),
        "strategy_id": envelope_summary.get("strategy_id"),
        "candidate_id": envelope_summary.get("candidate_id"),
        "stop_loss_present": envelope_summary.get("stop_loss_present", False),
        "take_profit_present": envelope_summary.get("take_profit_present", False),
        "max_spread_pips": envelope_summary.get("max_spread_pips"),
        "max_slippage_pips": envelope_summary.get("max_slippage_pips"),
        "risk_limits": envelope_summary.get("risk_limits", {}),
        "one_order_only": owner_approval_summary.get("owner_accepts_one_order_only"),
        "owner_can_cancel": owner_approval_summary.get("owner_can_cancel"),
        "approval_token_required": approval_token_summary.get("approval_token_required"),
        "approval_token_id_present": approval_token_summary.get("approval_token_id_present"),
        "approval_challenge_hash_present": approval_token_summary.get("approval_challenge_hash_present"),
        "owner_runtime_credential_entry_required": credential_summary.get("owner_runtime_credential_entry_required"),
        "runtime_only_credentials_required": credential_summary.get("runtime_only_credentials_required"),
        "credentials_included": False,
        "account_identifiers_included": False,
        "demo_only": True,
        "live_execution_allowed": False,
        "money_movement_allowed": False,
        "real_broker_call_allowed": False,
        "network_call_allowed": False,
        "transport_injected": bool(transport_supplied),
    }


def _live_or_money_blockers(
    *,
    binding_summary: Mapping[str, Any],
    owner_runtime_approval_summary: Mapping[str, Any],
    approval_token_summary: Mapping[str, Any],
    runtime_credential_boundary_summary: Mapping[str, Any],
    runtime_transport_policy_summary: Mapping[str, Any],
    demo_account_boundary_summary: Mapping[str, Any],
    sanitized_order_envelope_summary: Mapping[str, Any],
    one_order_policy_summary: Mapping[str, Any],
    audit_telemetry_summary: Mapping[str, Any],
) -> list[str]:
    checks = {
        "live_trading_allowed": (
            _bool(binding_summary.get("live_trading_allowed"))
            or owner_runtime_approval_summary.get("owner_accepts_no_real_money") is False
        ),
        "real_money_allowed": (
            _bool(binding_summary.get("real_money_allowed"))
            or _bool(demo_account_boundary_summary.get("real_money_allowed"))
        ),
        "money_movement_allowed": (
            _bool(binding_summary.get("money_movement_allowed"))
            or _bool(demo_account_boundary_summary.get("money_movement_allowed"))
            or _bool(sanitized_order_envelope_summary.get("money_movement_allowed"))
        ),
        "bank_access_allowed": _bool(demo_account_boundary_summary.get("bank_access_allowed")),
        "live_execution_allowed": (
            _bool(demo_account_boundary_summary.get("live_execution_allowed"))
            or _bool(sanitized_order_envelope_summary.get("live_execution_allowed"))
        ),
    }
    return [name for name, value in checks.items() if value is True]


def _owner_action_queue(
    *,
    next_best_packet: str,
    packet_status: str,
    blocking_items: list[str],
) -> list[dict[str, Any]]:
    safe_actions = {
        "REVIEW_BROKER_ADAPTER_BINDING_RESULT": "Validate the upstream adapter binding record and boundary flags.",
        "REVIEW_OWNER_RUNTIME_APPROVAL": "Validate owner runtime transport approval intent and cancel behavior.",
        "REVIEW_APPROVAL_TOKEN_METADATA": "Validate immutable approval token evidence and freshness.",
        "REVIEW_RUNTIME_CREDENTIAL_BOUNDARY": "Verify runtime-only credential boundaries and no repo persistence.",
        "REVIEW_RUNTIME_TRANSPORT_POLICY": "Validate transport policy and fake probe configuration.",
        "REVIEW_DEMO_ACCOUNT_BOUNDARY": "Validate demo account boundary and account identifier handling.",
        "REVIEW_SANITIZED_ORDER_ENVELOPE": "Validate sanitized order envelope fields before transport handoff.",
        "REVIEW_ONE_ORDER_POLICY": "Validate one-order policy and open-order invariants.",
        "REVIEW_AUDIT_TELEMETRY": "Validate audit telemetry completeness and no raw secret logging.",
        "REVIEW_SANITIZED_RUNTIME_TRANSPORT_PACKET": "Review sanitized transport packet for any sensitive fields.",
        "REVIEW_FAKE_PROBE_RESULT": "Review sanitized fake transport result and probe contract behavior.",
        "REVIEW_NEXT_PACKET": "Advance to the next owner-approved dry-run packet.",
    }
    return [
        {
            "action_id": action_id,
            "owner_decision_required": True,
            "live_execution_allowed": False,
            "money_movement_allowed": False,
            "real_broker_call_allowed": False,
            "safe_action": safe_actions[action_id],
            "blocked_by": list(blocking_items),
            "next_best_packet": next_best_packet if action_id == "REVIEW_NEXT_PACKET" else None,
        }
        for action_id in OWNER_ACTION_IDS
    ]


def _safe_manual_next_action(status: str) -> str:
    return {
        OWNER_RUNTIME_TRANSPORT_PACKET_READY: "Route packet into the owner-approved one-order runtime dry-run next packet.",
        OWNER_RUNTIME_TRANSPORT_PACKET_READY_WITH_FAKE_PROBE: "Review fake-probe result and route to one-order dry-run.",
        INCOMPLETE_INPUTS: "Supply broker_adapter_binding_result and rerun.",
        BLOCKED_BY_SENSITIVE_DATA: "Remove sensitive keys and values before rerun.",
        BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY: "Set live/money authority flags to false in all input sections.",
        BLOCKED_BY_BINDING_RESULT: "Repair binding result, flags, and required false-authority fields.",
        BLOCKED_BY_OWNER_APPROVAL: "Repair owner runtime approval evidence.",
        BLOCKED_BY_APPROVAL_TOKEN: "Repair approval token evidence for matching intent and validity.",
        BLOCKED_BY_RUNTIME_CREDENTIAL_BOUNDARY: "Repair runtime credential boundary proof and redaction checks.",
        BLOCKED_BY_TRANSPORT_POLICY: "Repair transport policy and provide a callable fake transport when requested.",
        BLOCKED_BY_DEMO_ACCOUNT_BOUNDARY: "Repair account boundary values for demo-only execution.",
        BLOCKED_BY_SANITIZED_ORDER_ENVELOPE: "Repair sanitized order envelope fields.",
        BLOCKED_BY_ONE_ORDER_POLICY: "Repair one-order controls and packet cap limits.",
        BLOCKED_BY_AUDIT_TELEMETRY: "Repair audit telemetry evidence and redaction requirements.",
    }.get(status, "Resolve blockers and rerun.")


def _audit_record(
    *,
    source: Mapping[str, Any],
    owner_name: str,
    packet_status: str,
    transport_probe_call_count: int,
    fake_probe_attempted: bool,
    ready: bool,
    input_redacted: bool,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "as_of_date": _text(source.get("as_of_date"), _now_utc_iso()),
        "owner_name": owner_name,
        "input_fields_seen": sorted(str(key) for key in source.keys()),
        "packet_status": packet_status,
        "ready_for_owner_runtime_transport": ready,
        "sanitized_owner_runtime_transport_packet_required": True,
        "transport_probe_call_count": transport_probe_call_count,
        "fake_probe_attempted": fake_probe_attempted,
        "input_redacted": input_redacted,
        "live_execution_allowed": False,
        "money_movement_allowed": False,
        "next_best_packet": NEXT_PACKET_READY,
    }


def _safety_summary() -> dict[str, Any]:
    return {
        "read_only": True,
        "demo_only": True,
        "owner_gate_required": True,
        "approval_token_required": True,
        "one_order_only_required": True,
        "runtime_only_credentials_required": True,
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
        "fixed_return_target_promised": False,
        "profit_claim_authorized": False,
    }


def _contains_sensitive_data(source: Mapping[str, Any]) -> bool:
    return _contains_sensitive_key(source)


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text in SAFE_METADATA_KEYS:
                if isinstance(child, (Mapping, list, tuple)):
                    continue
                continue
            if _is_sensitive_key_name(key_text):
                return True
            if _contains_sensitive_key(child):
                return True
        return False
    if isinstance(value, (list, tuple)):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def _redact_mapping(mapping: Mapping[str, Any]) -> dict[str, Any]:
    return _sanitize_mapping(mapping)


def _sanitize_mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {
            "transport_payload_type": type(value).__name__,
        }
    sanitized: dict[str, Any] = {}
    for key, child in value.items():
        key_text = str(key).lower()
        if key_text in SAFE_METADATA_KEYS:
            sanitized[str(key)] = child
            continue
        if _is_sensitive_key_name(key_text):
            continue
        if isinstance(child, Mapping):
            sanitized[str(key)] = _sanitize_mapping(child)
        elif isinstance(child, (list, tuple)):
            sanitized[str(key)] = [
                _sanitize_mapping(item) if isinstance(item, Mapping) else item for item in child
            ]
        else:
            sanitized[str(key)] = child
    return sanitized


def _is_sensitive_key_name(key_text: str) -> bool:
    if key_text in SENSITIVE_EXACT_KEY_NAMES:
        return True
    if key_text in SAFE_METADATA_KEYS:
        return False
    if "account_id" in key_text and "identifier" not in key_text:
        return True
    return any(part in key_text for part in SENSITIVE_KEY_PARTS)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _copy_mapping(value: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(value or {})


def _text(value: Any, default: str | None = None) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


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
