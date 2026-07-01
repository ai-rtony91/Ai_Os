"""Read-only Forex live-execution and capital-operation campaign evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any


SCHEMA = "AIOS_FOREX_LIVE_EXECUTION_AND_CAPITAL_OPERATION_CAMPAIGN_V1"
MODE = "READ_ONLY_LIVE_EXECUTION_AND_CAPITAL_OPERATION_CAMPAIGN"

CAMPAIGN_READY_FOR_OWNER_LIVE_EXCEPTION_REVIEW = (
    "CAMPAIGN_READY_FOR_OWNER_LIVE_EXCEPTION_REVIEW"
)
READY_FOR_PROTECTED_DEMO_EXECUTION_PACKET = (
    "READY_FOR_PROTECTED_DEMO_EXECUTION_PACKET"
)
READY_FOR_RUNTIME_CREDENTIAL_SESSION_BRIDGE = (
    "READY_FOR_RUNTIME_CREDENTIAL_SESSION_BRIDGE"
)
READY_FOR_OWNER_VALUE_ENTRY_REVIEW = "READY_FOR_OWNER_VALUE_ENTRY_REVIEW"
READY_FOR_CAPITAL_REDISTRIBUTION_REVIEW = (
    "READY_FOR_CAPITAL_REDISTRIBUTION_REVIEW"
)
BLOCKED_BY_PROTECTED_EXECUTION_GATE = "BLOCKED_BY_PROTECTED_EXECUTION_GATE"
BLOCKED_BY_CREDENTIAL_SESSION_BOUNDARY = (
    "BLOCKED_BY_CREDENTIAL_SESSION_BOUNDARY"
)
BLOCKED_BY_OWNER_APPROVAL_TOKEN = "BLOCKED_BY_OWNER_APPROVAL_TOKEN"
BLOCKED_BY_RISK_GATES = "BLOCKED_BY_RISK_GATES"
BLOCKED_BY_CAPITAL_POLICY = "BLOCKED_BY_CAPITAL_POLICY"
BLOCKED_BY_SOS_READINESS = "BLOCKED_BY_SOS_READINESS"
BLOCKED_BY_22H_6D_READINESS = "BLOCKED_BY_22H_6D_READINESS"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_PACKET_BY_STATUS = {
    BLOCKED_BY_SENSITIVE_DATA: SCHEMA,
    INCOMPLETE_INPUTS: SCHEMA,
    READY_FOR_OWNER_VALUE_ENTRY_REVIEW: (
        "AIOS_FOREX_OWNER_VALUE_ENTRY_REVIEW_PACKET_V1"
    ),
    READY_FOR_RUNTIME_CREDENTIAL_SESSION_BRIDGE: (
        "AIOS_FOREX_OWNER_LIVE_EXCEPTION_AND_RUNTIME_SECRET_SESSION_BRIDGE_V1"
    ),
    READY_FOR_PROTECTED_DEMO_EXECUTION_PACKET: (
        "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_PROTECTED_RUNTIME_EXECUTION_V1"
    ),
    READY_FOR_CAPITAL_REDISTRIBUTION_REVIEW: (
        "AIOS_FOREX_CAPITAL_REDISTRIBUTION_OWNER_REVIEW_PACKET_V1"
    ),
    CAMPAIGN_READY_FOR_OWNER_LIVE_EXCEPTION_REVIEW: (
        "AIOS_FOREX_OWNER_LIVE_EXCEPTION_AND_RUNTIME_SECRET_SESSION_BRIDGE_V1"
    ),
}

PROTECTED_RUNTIME_READY_STATUSES = frozenset(
    {
        "PROTECTED_ONE_ORDER_GATE_CLEARED",
        "ONE_ORDER_PROTECTED_EXECUTION_METADATA_READY",
        "PROTECTED_RUNTIME_EXECUTION_REVIEW_READY",
    }
)

ALLOWED_OANDA_MODES = frozenset(
    {"PRACTICE", "DEMO", "OANDA_DEMO", "LIVE_EXCEPTION_REVIEW_ONLY"}
)

HARD_FALSE_FIELDS = (
    "live_trade_executed",
    "demo_trade_executed",
    "money_moved",
    "bank_access_used",
    "broker_api_called",
    "credential_read",
    "credential_stored",
    "api_key_stored",
    "master_password_used",
    "vault_password_used",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "dashboard_runtime_created",
)

SAFETY_FALSE_FIELDS = (
    "real_broker_call_allowed",
    "direct_broker_api_allowed",
    "broker_api_import_allowed",
    "network_call_allowed",
    "live_trading_allowed",
    "real_money_allowed",
    "money_movement_allowed",
    "bank_access_allowed",
    "credential_storage_allowed",
    "credential_request_allowed",
    "account_identifier_storage_allowed",
    "account_identifier_read_allowed",
    "live_execution_allowed",
    "live_capital_action_authorized",
    "deposit_allowed",
    "withdrawal_allowed",
    "ach_allowed",
    "wire_allowed",
    "card_transfer_allowed",
    "fixed_return_target_promised",
    "profit_claim_authorized",
)

SENSITIVE_KEY_PARTS = (
    "api_key",
    "token_value",
    "secret",
    "password",
    "master_password",
    "vault_password",
    "account_number",
    "routing_number",
    "card_number",
    "debit_card_number",
    "cvv",
    "account_id",
    "oanda_account_id",
    "bearer",
    "broker_token",
    "access_token",
    "private_key",
    "raw_approval_phrase",
    "raw_voice_audio",
)

SAFE_METADATA_KEYS = frozenset(
    {
        "approval_token_required",
        "approval_token_metadata_present",
        "approval_token_id_present",
        "approval_token_unexpired",
        "approval_token_unused",
        "approval_challenge_hash_present",
        "approval_timestamp_present",
        "secret_scan_required",
        "secrets_manager_required",
        "no_raw_secret_logging",
        "credential_redaction_required",
        "credential_storage_allowed",
        "credential_read_allowed",
        "credential_request_allowed",
        "credential_stored",
        "credential_read",
        "api_key_stored",
        "master_password_used",
        "vault_password_used",
        "account_identifier_storage_allowed",
        "account_identifier_read_allowed",
        "account_id_provided",
        "no_stored_account_id",
        "no_stored_api_key",
        "no_master_password",
        "no_vault_password",
        "no_raw_token",
        "credential_values_provided",
        "credential_values_persisted",
        "credential_values_logged",
        "credential_values_requested_by_aios",
        "repo_secret_storage_allowed",
        "chat_secret_sharing_allowed",
        "env_var_read_allowed",
        "raw_approval_phrase_stored",
        "raw_voice_audio_stored",
        "no_raw_account_identifier_logging",
        "no_voice_audio_storage",
    }
)

OWNER_VALUE_ENTRY_ALLOWED_FIELDS = frozenset(
    {
        "account_balance_snapshot",
        "equity_snapshot",
        "risk_amount",
        "max_loss_amount",
        "instrument",
        "units",
        "pair_allocation_targets",
        "compounding_percent",
        "sweep_percent",
        "reserve_percent",
        "bank_or_card_rail_label",
    }
)

CAPITAL_RECOMMENDATIONS = frozenset(
    {
        "COMPOUND_INTO_SAME_PAIR",
        "REDISTRIBUTE_INTO_ALLOWED_PAIR_BASKET",
        "HOLD_PROFIT_RESERVE",
        "OWNER_REVIEW_WITHDRAWAL",
        "OWNER_REVIEW_DEBIT_CARD_OR_BANK_TRANSFER",
        "NO_CAPITAL_ACTION_RECOMMENDED",
        "BLOCKED_BY_BROKER_POLICY",
        "BLOCKED_BY_OPEN_RISK",
        "BLOCKED_BY_COOLDOWN",
        "BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS",
    }
)

TRANSFER_REVIEW_RECOMMENDATIONS = frozenset(
    {"OWNER_REVIEW_WITHDRAWAL", "OWNER_REVIEW_DEBIT_CARD_OR_BANK_TRANSFER"}
)

CAPITAL_REVIEW_RECOMMENDATIONS = frozenset(
    {
        "COMPOUND_INTO_SAME_PAIR",
        "REDISTRIBUTE_INTO_ALLOWED_PAIR_BASKET",
        "HOLD_PROFIT_RESERVE",
        "OWNER_REVIEW_WITHDRAWAL",
        "OWNER_REVIEW_DEBIT_CARD_OR_BANK_TRANSFER",
    }
)

READINESS_COMPONENTS = (
    "broker_session_readiness",
    "monitoring_readiness",
    "kill_switch_readiness",
    "post_trade_review_readiness",
    "audit_readiness",
    "capital_planner_readiness",
    "sos_readiness",
    "owner_approval_readiness",
    "credential_boundary_readiness",
    "recovery_readiness",
)

OWNER_ACTION_IDS = (
    "REVIEW_SENSITIVE_DATA_BOUNDARY",
    "REVIEW_RUNTIME_CREDENTIAL_SESSION_BOUNDARY",
    "REVIEW_OWNER_APPROVAL_TOKEN_METADATA",
    "REVIEW_RISK_GATES",
    "REVIEW_PROTECTED_ONE_ORDER_GATE",
    "REVIEW_OWNER_VALUE_ENTRY_WORKFLOW",
    "REVIEW_CAPITAL_REDISTRIBUTION_PLANNER",
    "REVIEW_SOS_REMINDER_PACKET",
    "REVIEW_22H_6D_READINESS_INDEX",
    "REVIEW_POST_EXECUTION_REVIEW_LOOP",
    "REVIEW_NEXT_PACKET",
)


def evaluate_live_execution_and_capital_operation_campaign_v1(
    payload: dict | None = None,
) -> dict:
    """Evaluate live-operation campaign readiness without runtime side effects."""

    source = _mapping(payload)
    owner_value_entry_workflow = _owner_value_entry_workflow_summary(source)
    sensitive_data_blockers = _unique(
        [
            *_sensitive_blockers(source),
            *owner_value_entry_workflow["sensitive_data_blockers"],
        ]
    )
    sensitive_data_detected = bool(sensitive_data_blockers)

    if sensitive_data_detected:
        runtime_credential_session_boundary = _redacted_summary(
            "runtime_credential_session_boundary", sensitive_data_blockers
        )
        owner_live_approval_token = _redacted_summary(
            "owner_live_approval_token_metadata", sensitive_data_blockers
        )
        oanda_mode_declaration = _redacted_summary(
            "oanda_mode_declaration", sensitive_data_blockers
        )
        one_order_policy = _redacted_summary("one_order_policy", sensitive_data_blockers)
        risk_limits = _redacted_summary("risk_limits", sensitive_data_blockers)
        execution_controls = _redacted_summary(
            "execution_controls", sensitive_data_blockers
        )
        post_execution_review_loop = _redacted_summary(
            "post_execution_review_loop", sensitive_data_blockers
        )
        protected_runtime_execution = _redacted_summary(
            "protected_runtime_execution_result", sensitive_data_blockers
        )
        capital_redistribution_planner = _redacted_summary(
            "capital_redistribution_planner", sensitive_data_blockers
        )
        twenty_two_hour_six_day_readiness_index = _redacted_summary(
            "twenty_two_hour_six_day_readiness_index", sensitive_data_blockers
        )
        sos_reminder_packet = _redacted_summary(
            "sos_reminder_packet", sensitive_data_blockers
        )
        live_execution_readiness_gate = _redacted_summary(
            "live_execution_readiness_gate", sensitive_data_blockers
        )
    else:
        runtime_credential_session_boundary = _credential_session_boundary_summary(
            _mapping(source.get("credential_session_boundary"))
        )
        owner_live_approval_token = _owner_approval_token_summary(
            _mapping(source.get("owner_live_approval_token_metadata"))
        )
        oanda_mode_declaration = _oanda_mode_summary(
            _mapping(source.get("oanda_mode_declaration"))
        )
        one_order_policy = _one_order_policy_summary(_mapping(source.get("one_order_policy")))
        risk_limits = _risk_limits_summary(_mapping(source.get("risk_limits")))
        execution_controls = _execution_controls_summary(
            _mapping(source.get("execution_controls"))
        )
        post_execution_review_loop = _post_execution_review_loop_summary(source)
        protected_runtime_execution = _protected_runtime_execution_summary(
            _mapping(source.get("protected_runtime_execution_result"))
        )
        capital_redistribution_planner = _capital_redistribution_planner_summary(
            source=source
        )
        twenty_two_hour_six_day_readiness_index = _readiness_index_summary(source)
        sos_reminder_packet = _sos_reminder_packet_summary(
            source=source,
            approval_token_summary=owner_live_approval_token,
            credential_summary=runtime_credential_session_boundary,
            post_review_summary=post_execution_review_loop,
            execution_controls=execution_controls,
            capital_summary=capital_redistribution_planner,
            readiness_index=twenty_two_hour_six_day_readiness_index,
        )
        live_execution_readiness_gate = _live_execution_readiness_gate_summary(
            protected_runtime_execution=protected_runtime_execution,
            owner_live_approval_token=owner_live_approval_token,
            oanda_mode_declaration=oanda_mode_declaration,
            one_order_policy=one_order_policy,
            risk_limits=risk_limits,
            execution_controls=execution_controls,
            post_execution_review_loop=post_execution_review_loop,
        )

    campaign_status, campaign_blockers, missing_inputs = _campaign_status(
        source=source,
        sensitive_data_detected=sensitive_data_detected,
        sensitive_data_blockers=sensitive_data_blockers,
        owner_value_entry_workflow=owner_value_entry_workflow,
        credential_summary=runtime_credential_session_boundary,
        owner_live_approval_token=owner_live_approval_token,
        oanda_mode_declaration=oanda_mode_declaration,
        risk_limits=risk_limits,
        execution_controls=execution_controls,
        protected_runtime_execution=protected_runtime_execution,
        one_order_policy=one_order_policy,
        post_execution_review_loop=post_execution_review_loop,
        capital_summary=capital_redistribution_planner,
        sos_reminder_packet=sos_reminder_packet,
        readiness_index=twenty_two_hour_six_day_readiness_index,
    )
    next_best_packet = _next_best_packet(campaign_status)
    campaign_ready = campaign_status == CAMPAIGN_READY_FOR_OWNER_LIVE_EXCEPTION_REVIEW

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "mode": MODE,
        "campaign_status": campaign_status,
        "campaign_ready": campaign_ready,
        "owner_decision_required": True,
        "approval_token_required": True,
        "read_only": True,
        "metadata_only": True,
        "sensitive_data_detected": sensitive_data_detected,
        "sensitive_data_blockers": list(sensitive_data_blockers),
        "campaign_blockers": list(campaign_blockers),
        "missing_inputs": list(missing_inputs),
        "live_execution_readiness_gate": live_execution_readiness_gate,
        "runtime_credential_session_boundary": runtime_credential_session_boundary,
        "owner_value_entry_workflow": owner_value_entry_workflow,
        "capital_redistribution_planner": capital_redistribution_planner,
        "sos_reminder_packet": sos_reminder_packet,
        "twenty_two_hour_six_day_readiness_index": (
            twenty_two_hour_six_day_readiness_index
        ),
        "post_execution_review_loop": post_execution_review_loop,
        "owner_action_queue": _owner_action_queue(
            campaign_status=campaign_status,
            campaign_blockers=campaign_blockers,
            next_best_packet=next_best_packet,
        ),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(campaign_status),
        "audit_record": _audit_record(
            source=source,
            campaign_status=campaign_status,
            campaign_ready=campaign_ready,
            next_best_packet=next_best_packet,
            sensitive_data_detected=sensitive_data_detected,
            campaign_blockers=campaign_blockers,
        ),
        "safety": _safety_summary(),
    }
    for field in HARD_FALSE_FIELDS:
        result[field] = False
    for field in SAFETY_FALSE_FIELDS:
        result[field] = False
    return result


def _campaign_status(
    *,
    source: Mapping[str, Any],
    sensitive_data_detected: bool,
    sensitive_data_blockers: Sequence[str],
    owner_value_entry_workflow: Mapping[str, Any],
    credential_summary: Mapping[str, Any],
    owner_live_approval_token: Mapping[str, Any],
    oanda_mode_declaration: Mapping[str, Any],
    risk_limits: Mapping[str, Any],
    execution_controls: Mapping[str, Any],
    protected_runtime_execution: Mapping[str, Any],
    one_order_policy: Mapping[str, Any],
    post_execution_review_loop: Mapping[str, Any],
    capital_summary: Mapping[str, Any],
    sos_reminder_packet: Mapping[str, Any],
    readiness_index: Mapping[str, Any],
) -> tuple[str, list[str], list[str]]:
    if not source:
        return INCOMPLETE_INPUTS, ["payload_mapping_required"], ["payload_mapping_required"]

    if sensitive_data_detected:
        blockers = list(sensitive_data_blockers or ["sensitive_data_provided"])
        return BLOCKED_BY_SENSITIVE_DATA, blockers, []

    if (
        owner_value_entry_workflow.get("present") is True
        and owner_value_entry_workflow.get("ready_for_owner_review") is True
        and not _campaign_execution_metadata_present(source)
    ):
        return READY_FOR_OWNER_VALUE_ENTRY_REVIEW, [], []

    if (
        credential_summary.get("present") is True
        and credential_summary.get("bridge_ready_for_review") is True
        and protected_runtime_execution.get("present") is not True
    ):
        return READY_FOR_RUNTIME_CREDENTIAL_SESSION_BRIDGE, [], []

    if credential_summary.get("ready") is not True:
        blockers = _list(credential_summary.get("blockers"))
        return (
            BLOCKED_BY_CREDENTIAL_SESSION_BOUNDARY,
            blockers,
            _missing_from_blockers(blockers),
        )

    if owner_live_approval_token.get("ready") is not True:
        blockers = _list(owner_live_approval_token.get("blockers"))
        return (
            BLOCKED_BY_OWNER_APPROVAL_TOKEN,
            blockers,
            _missing_from_blockers(blockers),
        )

    risk_gate_blockers = _risk_gate_blockers(
        oanda_mode_declaration=oanda_mode_declaration,
        risk_limits=risk_limits,
        execution_controls=execution_controls,
    )
    if risk_gate_blockers:
        return BLOCKED_BY_RISK_GATES, risk_gate_blockers, _missing_from_blockers(risk_gate_blockers)

    if (
        protected_runtime_execution.get("present") is not True
        and _upstream_metadata_ready(
            credential_summary=credential_summary,
            owner_live_approval_token=owner_live_approval_token,
            oanda_mode_declaration=oanda_mode_declaration,
            risk_limits=risk_limits,
            execution_controls=execution_controls,
        )
    ):
        return READY_FOR_PROTECTED_DEMO_EXECUTION_PACKET, [], []

    protected_gate_blockers = _protected_gate_blockers(
        protected_runtime_execution=protected_runtime_execution,
        one_order_policy=one_order_policy,
        post_execution_review_loop=post_execution_review_loop,
    )
    if protected_gate_blockers:
        return (
            BLOCKED_BY_PROTECTED_EXECUTION_GATE,
            protected_gate_blockers,
            _missing_from_blockers(protected_gate_blockers),
        )

    if capital_summary.get("blocked") is True:
        blockers = _list(capital_summary.get("blockers"))
        return BLOCKED_BY_CAPITAL_POLICY, blockers, _missing_from_blockers(blockers)

    if capital_summary.get("ready_for_owner_review") is True:
        return READY_FOR_CAPITAL_REDISTRIBUTION_REVIEW, [], []

    if sos_reminder_packet.get("ready") is not True:
        blockers = _list(sos_reminder_packet.get("blockers"))
        return BLOCKED_BY_SOS_READINESS, blockers, _missing_from_blockers(blockers)

    if readiness_index.get("readiness_passed") is not True:
        blockers = _list(readiness_index.get("blockers"))
        return (
            BLOCKED_BY_22H_6D_READINESS,
            blockers,
            _missing_from_blockers(blockers),
        )

    return CAMPAIGN_READY_FOR_OWNER_LIVE_EXCEPTION_REVIEW, [], []


def _live_execution_readiness_gate_summary(
    *,
    protected_runtime_execution: Mapping[str, Any],
    owner_live_approval_token: Mapping[str, Any],
    oanda_mode_declaration: Mapping[str, Any],
    one_order_policy: Mapping[str, Any],
    risk_limits: Mapping[str, Any],
    execution_controls: Mapping[str, Any],
    post_execution_review_loop: Mapping[str, Any],
) -> dict[str, Any]:
    blockers = _unique(
        [
            *_list(protected_runtime_execution.get("blockers")),
            *_list(owner_live_approval_token.get("blockers")),
            *_list(oanda_mode_declaration.get("blockers")),
            *_list(one_order_policy.get("blockers")),
            *_list(risk_limits.get("blockers")),
            *_list(execution_controls.get("blockers")),
            *_list(post_execution_review_loop.get("blockers")),
        ]
    )
    return {
        "ready": not blockers,
        "metadata_only": True,
        "protected_runtime_execution_result": dict(protected_runtime_execution),
        "owner_live_approval_token_metadata": dict(owner_live_approval_token),
        "oanda_mode_declaration": dict(oanda_mode_declaration),
        "one_order_policy": dict(one_order_policy),
        "risk_limits": dict(risk_limits),
        "execution_controls": dict(execution_controls),
        "post_trade_review": dict(post_execution_review_loop),
        "blockers": blockers,
    }


def _credential_session_boundary_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    expected_true = (
        "owner_enters_credentials_outside_repo_chat",
        "runtime_only_credential_handoff",
        "no_stored_api_key",
        "no_stored_account_id",
        "no_master_password",
        "no_vault_password",
        "no_raw_token",
        "secret_scan_required",
        "redaction_required",
        "session_expiry_required",
        "session_unexpired",
        "one_order_session_scope",
    )
    expected_false = (
        "credential_values_provided",
        "credential_values_persisted",
        "credential_values_logged",
        "credential_values_requested_by_aios",
        "repo_secret_storage_allowed",
        "chat_secret_sharing_allowed",
        "env_var_read_allowed",
        "account_id_provided",
    )
    blockers = [
        *_expected_true_blockers(data, expected_true),
        *_expected_false_blockers(data, expected_false),
    ]
    present = bool(data)
    bridge_ready_for_review = _bool(data.get("bridge_ready_for_review"), default=False)
    return {
        "present": present,
        "ready": present and not blockers,
        "bridge_ready_for_review": bridge_ready_for_review is True,
        "metadata_only": True,
        "owner_enters_credentials_outside_repo_chat": _bool(
            data.get("owner_enters_credentials_outside_repo_chat")
        ),
        "runtime_only_credential_handoff": _bool(
            data.get("runtime_only_credential_handoff")
        ),
        "session_unexpired": _bool(data.get("session_unexpired")),
        "one_order_session_scope": _bool(data.get("one_order_session_scope")),
        "credential_values_provided": _bool(
            data.get("credential_values_provided"), default=False
        ),
        "credential_values_persisted": _bool(
            data.get("credential_values_persisted"), default=False
        ),
        "credential_values_logged": _bool(
            data.get("credential_values_logged"), default=False
        ),
        "credential_values_requested_by_aios": _bool(
            data.get("credential_values_requested_by_aios"), default=False
        ),
        "repo_secret_storage_allowed": _bool(
            data.get("repo_secret_storage_allowed"), default=False
        ),
        "chat_secret_sharing_allowed": _bool(
            data.get("chat_secret_sharing_allowed"), default=False
        ),
        "env_var_read_allowed": _bool(data.get("env_var_read_allowed"), default=False),
        "account_id_provided": _bool(data.get("account_id_provided"), default=False),
        "blockers": _unique(blockers),
    }


def _owner_approval_token_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    expected_true = (
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
    expected_false = ("generic_yes_detected", "raw_approval_phrase_stored")
    blockers = [
        *_expected_true_blockers(data, expected_true),
        *_expected_false_blockers(data, expected_false),
    ]
    return {
        "present": bool(data),
        "ready": bool(data) and not blockers,
        "approval_token_required": _bool(data.get("approval_token_required"), default=True),
        "approval_token_metadata_present": _bool(
            data.get("approval_token_metadata_present")
        ),
        "approval_token_id_present": _bool(data.get("approval_token_id_present")),
        "approval_phrase_present": _bool(data.get("approval_phrase_present")),
        "approval_phrase_matches": _bool(data.get("approval_phrase_matches")),
        "approval_action_matches": _bool(data.get("approval_action_matches")),
        "approval_mode_matches": _bool(data.get("approval_mode_matches")),
        "approval_instrument_matches": _bool(data.get("approval_instrument_matches")),
        "approval_units_matches": _bool(data.get("approval_units_matches")),
        "approval_risk_matches": _bool(data.get("approval_risk_matches")),
        "approval_token_unexpired": _bool(data.get("approval_token_unexpired")),
        "approval_token_unused": _bool(data.get("approval_token_unused")),
        "approval_challenge_hash_present": _bool(
            data.get("approval_challenge_hash_present")
        ),
        "approval_timestamp_present": _bool(data.get("approval_timestamp_present")),
        "generic_yes_detected": _bool(data.get("generic_yes_detected"), default=False),
        "raw_approval_phrase_stored": _bool(
            data.get("raw_approval_phrase_stored"), default=False
        ),
        "blockers": _unique(blockers),
    }


def _oanda_mode_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    broker_name = _text(data.get("broker_name"))
    mode = _text(data.get("mode"))
    account_id_provided = _bool(data.get("account_id_provided"))
    if not data:
        blockers.append("oanda_mode_declaration_missing")
    if broker_name != "OANDA":
        blockers.append("broker_name_not_oanda")
    if mode not in ALLOWED_OANDA_MODES:
        blockers.append("mode_not_allowed")
    if account_id_provided is None:
        blockers.append("account_id_provided_missing")
    elif account_id_provided is not False:
        blockers.append("account_id_provided_true")
    return {
        "present": bool(data),
        "ready": bool(data) and not blockers,
        "broker_name": broker_name,
        "mode": mode,
        "account_id_provided": account_id_provided,
        "blockers": _unique(blockers),
    }


def _one_order_policy_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    blockers = [
        *_expected_true_blockers(
            data,
            (
                "one_order_only",
                "next_order_blocked_until_review",
            ),
        ),
        *_expected_false_blockers(
            data,
            (
                "duplicate_order_detected",
                "existing_open_order_for_candidate",
            ),
        ),
    ]
    max_order_count = _decimal(data.get("max_order_count_this_packet"))
    if max_order_count != Decimal("1"):
        blockers.append("max_order_count_this_packet_not_one")
    return {
        "present": bool(data),
        "ready": bool(data) and not blockers,
        "one_order_only": _bool(data.get("one_order_only")),
        "max_order_count_this_packet": max_order_count,
        "duplicate_order_detected": _bool(
            data.get("duplicate_order_detected"), default=False
        ),
        "existing_open_order_for_candidate": _bool(
            data.get("existing_open_order_for_candidate"), default=False
        ),
        "next_order_blocked_until_review": _bool(
            data.get("next_order_blocked_until_review")
        ),
        "blockers": _unique(blockers),
    }


def _risk_limits_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    max_risk = _decimal(data.get("max_risk_per_trade_pct"))
    max_daily_loss = _decimal(data.get("max_daily_loss_pct"))
    max_spread = _decimal(data.get("max_spread_pips"))
    max_slippage = _decimal(data.get("max_slippage_pips"))
    stop_loss_present = _bool(data.get("stop_loss_present"))
    take_profit_present = _bool(data.get("take_profit_present"))
    if not data:
        blockers.append("risk_limits_missing")
    if max_risk is None:
        blockers.append("max_risk_per_trade_pct_missing")
    elif max_risk > Decimal("0.01"):
        blockers.append("max_risk_per_trade_pct_above_limit")
    if max_daily_loss is None:
        blockers.append("max_daily_loss_pct_missing")
    elif max_daily_loss > Decimal("0.03"):
        blockers.append("max_daily_loss_pct_above_limit")
    if stop_loss_present is not True:
        blockers.append("stop_loss_present_missing_or_false")
    if take_profit_present is not True:
        blockers.append("take_profit_present_missing_or_false")
    if max_spread is None:
        blockers.append("max_spread_pips_missing")
    elif max_spread <= Decimal("0"):
        blockers.append("max_spread_pips_not_positive")
    if max_slippage is None:
        blockers.append("max_slippage_pips_missing")
    elif max_slippage < Decimal("0"):
        blockers.append("max_slippage_pips_negative")
    return {
        "present": bool(data),
        "ready": bool(data) and not blockers,
        "max_risk_per_trade_pct": max_risk,
        "max_daily_loss_pct": max_daily_loss,
        "stop_loss_present": stop_loss_present,
        "take_profit_present": take_profit_present,
        "max_spread_pips": max_spread,
        "max_slippage_pips": max_slippage,
        "blockers": _unique(blockers),
    }


def _execution_controls_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    blockers = _expected_false_blockers(
        data,
        (
            "kill_switch_active",
            "daily_loss_stop_active",
        ),
    )
    if not data:
        blockers.append("execution_controls_missing")
    return {
        "present": bool(data),
        "ready": bool(data) and not blockers,
        "kill_switch_active": _bool(data.get("kill_switch_active"), default=False),
        "daily_loss_stop_active": _bool(
            data.get("daily_loss_stop_active"), default=False
        ),
        "blockers": _unique(blockers),
    }


def _protected_runtime_execution_summary(data: Mapping[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    status = _text(data.get("status"))
    if not data:
        blockers.append("protected_runtime_execution_result_missing")
    if status not in PROTECTED_RUNTIME_READY_STATUSES:
        blockers.append("protected_runtime_execution_status_not_ready")
    for key in (
        "real_broker_call_allowed",
        "broker_api_called",
        "live_trade_executed",
        "demo_trade_executed",
        "money_moved",
    ):
        value = _bool(data.get(key))
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is not False:
            blockers.append(f"{key}_true")
    return {
        "present": bool(data),
        "ready": bool(data) and not blockers,
        "status": status,
        "real_broker_call_allowed": _bool(
            data.get("real_broker_call_allowed"), default=False
        ),
        "broker_api_called": _bool(data.get("broker_api_called"), default=False),
        "live_trade_executed": _bool(data.get("live_trade_executed"), default=False),
        "demo_trade_executed": _bool(data.get("demo_trade_executed"), default=False),
        "money_moved": _bool(data.get("money_moved"), default=False),
        "blockers": _unique(blockers),
    }


def _post_execution_review_loop_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    data = _mapping(source.get("post_execution_review_loop"))
    if not data:
        data = _mapping(source.get("post_trade_review"))
    blockers = _expected_true_blockers(
        data,
        (
            "post_trade_review_required",
            "post_trade_review_completed",
            "sanitized_execution_receipt_present",
            "next_order_blocked_until_review",
            "owner_review_required",
        ),
    )
    pnl_review_recorded = _bool(data.get("pnl_review_recorded"))
    metadata_only_na = _bool(data.get("not_applicable_for_metadata_only"), default=False)
    if pnl_review_recorded is not True and metadata_only_na is not True:
        blockers.append("pnl_review_recorded_or_metadata_not_applicable_missing")
    return {
        "present": bool(data),
        "ready": bool(data) and not blockers,
        "post_trade_review_required": _bool(data.get("post_trade_review_required")),
        "post_trade_review_completed": _bool(data.get("post_trade_review_completed")),
        "sanitized_execution_receipt_present": _bool(
            data.get("sanitized_execution_receipt_present")
        ),
        "pnl_review_recorded": pnl_review_recorded,
        "not_applicable_for_metadata_only": metadata_only_na,
        "next_order_blocked_until_review": _bool(
            data.get("next_order_blocked_until_review")
        ),
        "owner_review_required": _bool(data.get("owner_review_required")),
        "blockers": _unique(blockers),
    }


def _owner_value_entry_workflow_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    data = _mapping(source.get("owner_value_entry_workflow"))
    if not data:
        data = _mapping(source.get("owner_value_entry_metadata"))
    if not data:
        data = _mapping(source.get("owner_value_entry"))

    safe_fields: dict[str, Any] = {}
    omitted_fields: list[str] = []
    sensitive_data_blockers: list[str] = []
    for key, value in data.items():
        key_text = str(key)
        normalized = _normalize_key(key_text)
        if normalized not in OWNER_VALUE_ENTRY_ALLOWED_FIELDS:
            omitted_fields.append(key_text)
            continue
        field_blockers = _sensitive_blockers(
            value, f"owner_value_entry_workflow.{key_text}"
        )
        if field_blockers:
            sensitive_data_blockers.extend(field_blockers)
            continue
        if normalized == "bank_or_card_rail_label" and _label_has_sensitive_digits(value):
            sensitive_data_blockers.append("bank_or_card_rail_label_contains_sensitive_number")
            continue
        safe_fields[key_text] = _safe_owner_value(value)

    if sensitive_data_blockers:
        safe_fields = {}

    return {
        "present": bool(data),
        "ready_for_owner_review": bool(data) and not sensitive_data_blockers,
        "metadata_only": True,
        "allowed_fields_present": sorted(safe_fields),
        "sanitized_values": safe_fields,
        "omitted_fields": sorted(omitted_fields),
        "sensitive_data_blockers": _unique(sensitive_data_blockers),
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "credential_storage_allowed": False,
        "safe_manual_next_action": "Owner may review sanitized value metadata only.",
    }


def _capital_redistribution_planner_summary(*, source: Mapping[str, Any]) -> dict[str, Any]:
    capital_policy = _mapping(source.get("capital_policy"))
    capital_state = _mapping(source.get("capital_state"))
    open_risk = _mapping(source.get("open_risk"))
    broker_policy_snapshot = _mapping(source.get("broker_policy_snapshot"))
    cooldown_state = _mapping(source.get("cooldown_state"))
    drawdown_state = _mapping(source.get("drawdown_state"))
    pair_allocation_targets = source.get("pair_allocation_targets")
    owner_workflow = _mapping(source.get("owner_value_entry_workflow"))
    if pair_allocation_targets is None and owner_workflow:
        pair_allocation_targets = owner_workflow.get("pair_allocation_targets")

    present = any(
        bool(item)
        for item in (
            capital_policy,
            capital_state,
            open_risk,
            broker_policy_snapshot,
            cooldown_state,
            drawdown_state,
            pair_allocation_targets,
        )
    )
    blockers: list[str] = []
    requested = _text(
        capital_policy.get("requested_recommendation"),
        _text(capital_policy.get("requested_capital_action"), ""),
    )
    requested = requested.upper() if requested else ""
    transfer_like_requested = requested in TRANSFER_REVIEW_RECOMMENDATIONS or _bool(
        capital_policy.get("transfer_review_requested"), default=False
    )
    open_risk_active = _open_risk_active(open_risk)
    broker_policy_present = bool(broker_policy_snapshot) and _bool(
        broker_policy_snapshot.get("broker_policy_missing"), default=False
    ) is not True
    cooldown_active = _bool(cooldown_state.get("cooldown_active"), default=False)
    drawdown_active = (
        _bool(drawdown_state.get("drawdown_active"), default=False) is True
        or _bool(drawdown_state.get("daily_loss_active"), default=False) is True
        or _bool(drawdown_state.get("daily_loss_stop_active"), default=False) is True
    )
    all_in_requested = _bool(capital_policy.get("all_in_requested"), default=False) is True
    all_in_allocation = all_in_requested or _allocation_is_all_in(pair_allocation_targets)

    recommendation = "NO_CAPITAL_ACTION_RECOMMENDED"
    if not present:
        blockers.append("capital_planner_metadata_missing")
    elif all_in_allocation:
        blockers.append("all_in_allocation_blocked")
    elif transfer_like_requested:
        if open_risk_active:
            recommendation = "BLOCKED_BY_OPEN_RISK"
            blockers.append("open_risk_blocks_transfer_review")
        elif not broker_policy_present:
            recommendation = "BLOCKED_BY_BROKER_POLICY"
            blockers.append("broker_policy_snapshot_missing")
        elif cooldown_active:
            recommendation = "BLOCKED_BY_COOLDOWN"
            blockers.append("cooldown_active")
        elif drawdown_active:
            recommendation = "BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS"
            blockers.append("drawdown_or_daily_loss_active")
        else:
            recommendation = (
                requested
                if requested in TRANSFER_REVIEW_RECOMMENDATIONS
                else "OWNER_REVIEW_WITHDRAWAL"
            )
    elif drawdown_active and requested:
        recommendation = "BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS"
        blockers.append("drawdown_or_daily_loss_active")
    elif requested == "COMPOUND_INTO_SAME_PAIR" or _bool(
        capital_policy.get("compound_same_pair_requested"), default=False
    ) is True:
        if _bool(capital_policy.get("evidence_quality_stronger"), default=False) is True:
            recommendation = "COMPOUND_INTO_SAME_PAIR"
        else:
            recommendation = "REDISTRIBUTE_INTO_ALLOWED_PAIR_BASKET"
    elif requested == "REDISTRIBUTE_INTO_ALLOWED_PAIR_BASKET" or _has_pair_targets(
        pair_allocation_targets
    ):
        recommendation = "REDISTRIBUTE_INTO_ALLOWED_PAIR_BASKET"
    elif requested == "HOLD_PROFIT_RESERVE" or _bool(
        capital_state.get("profit_reserve_ready"), default=False
    ) is True:
        recommendation = "HOLD_PROFIT_RESERVE"

    blocked = bool(blockers) or recommendation.startswith("BLOCKED_BY_")
    ready_for_owner_review = (
        not blocked and recommendation in CAPITAL_REVIEW_RECOMMENDATIONS
    )
    return {
        "present": present,
        "ready": present and not blocked,
        "blocked": blocked,
        "recommended_capital_action": recommendation,
        "owner_decision_required": recommendation in CAPITAL_REVIEW_RECOMMENDATIONS,
        "ready_for_owner_review": ready_for_owner_review,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "deposit_allowed": False,
        "withdrawal_allowed": False,
        "ach_allowed": False,
        "wire_allowed": False,
        "card_transfer_allowed": False,
        "open_risk_active": open_risk_active,
        "broker_policy_present": broker_policy_present,
        "cooldown_active": cooldown_active,
        "drawdown_or_daily_loss_active": drawdown_active,
        "all_in_allocation_blocked": all_in_allocation,
        "pair_allocation_targets_present": _has_pair_targets(pair_allocation_targets),
        "blockers": _unique(blockers),
        "safe_manual_next_action": _capital_safe_action(recommendation, blockers),
    }


def _sos_reminder_packet_summary(
    *,
    source: Mapping[str, Any],
    approval_token_summary: Mapping[str, Any],
    credential_summary: Mapping[str, Any],
    post_review_summary: Mapping[str, Any],
    execution_controls: Mapping[str, Any],
    capital_summary: Mapping[str, Any],
    readiness_index: Mapping[str, Any],
) -> dict[str, Any]:
    data = _mapping(source.get("sos_reminder_packet"))
    ready = bool(data) and _bool(data.get("sos_ready"), default=False) is True
    if _bool(data.get("alerts_enabled"), default=True) is False:
        ready = False
    blockers: list[str] = []
    if not data:
        blockers.append("sos_reminder_packet_missing")
    elif ready is not True:
        blockers.append("sos_reminder_packet_disabled_or_not_ready")

    reminders: list[dict[str, Any]] = []
    if approval_token_summary.get("ready") is not True:
        reminders.append(
            _reminder(
                "APPROVAL_TOKEN_REVIEW",
                "HIGH",
                "approval token metadata is missing or incomplete",
                "Review approval-token metadata without entering raw token values.",
            )
        )
    if credential_summary.get("session_unexpired") is False:
        reminders.append(
            _reminder(
                "CREDENTIAL_SESSION_EXPIRED",
                "HIGH",
                "credential session metadata is expired",
                "Restart runtime-only credential session review outside repo and chat.",
            )
        )
    if post_review_summary.get("ready") is not True:
        reminders.append(
            _reminder(
                "POST_TRADE_REVIEW_REQUIRED",
                "MEDIUM",
                "post-execution review metadata is missing or incomplete",
                "Complete sanitized post-execution review metadata.",
            )
        )
    if execution_controls.get("daily_loss_stop_active") is True:
        reminders.append(
            _reminder(
                "DAILY_LOSS_STOP_ACTIVE",
                "CRITICAL",
                "daily loss stop metadata is active",
                "Stop execution review until daily loss stop is cleared by owner review.",
            )
        )
    if execution_controls.get("kill_switch_active") is True:
        reminders.append(
            _reminder(
                "KILL_SWITCH_ACTIVE",
                "CRITICAL",
                "kill switch metadata is active",
                "Stop execution review until kill switch state is reviewed.",
            )
        )
    if capital_summary.get("recommended_capital_action") == "BLOCKED_BY_OPEN_RISK":
        reminders.append(
            _reminder(
                "OPEN_RISK_BLOCKS_TRANSFER",
                "HIGH",
                "open risk blocks transfer-like capital review",
                "Close or review open risk before capital redistribution review.",
            )
        )
    if capital_summary.get("recommended_capital_action") == "BLOCKED_BY_BROKER_POLICY":
        reminders.append(
            _reminder(
                "BROKER_POLICY_MISSING",
                "HIGH",
                "broker policy metadata is missing",
                "Add sanitized broker policy metadata before transfer review.",
            )
        )
    if capital_summary.get("blocked") is True:
        reminders.append(
            _reminder(
                "CAPITAL_REDISTRIBUTION_BLOCKED",
                "MEDIUM",
                "capital redistribution planner has blockers",
                "Repair capital planner metadata without authorizing money movement.",
            )
        )
    if readiness_index.get("readiness_passed") is not True:
        reminders.append(
            _reminder(
                "READINESS_22H_6D_INCOMPLETE",
                "MEDIUM",
                "22h/6d readiness index is incomplete",
                "Complete all readiness components before live exception review.",
            )
        )

    return {
        "present": bool(data),
        "ready": ready,
        "metadata_only": True,
        "reminders": reminders,
        "reminder_count": len(reminders),
        "blockers": _unique(blockers),
    }


def _readiness_index_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    data = _mapping(source.get("twenty_two_hour_six_day_readiness_index"))
    if not data:
        data = _mapping(source.get("twenty_two_hour_six_day_readiness"))
    component_scores: dict[str, int] = {}
    blockers: list[str] = []
    for component in READINESS_COMPONENTS:
        ready = _component_ready(data.get(component))
        component_scores[component] = 10 if ready else 0
        if not ready:
            blockers.append(f"{component}_incomplete")
    total_score = sum(component_scores.values())
    return {
        "present": bool(data),
        "component_scores": component_scores,
        "total_score": total_score,
        "readiness_passed": total_score == 100
        and all(score == 10 for score in component_scores.values()),
        "blockers": _unique(blockers),
    }


def _risk_gate_blockers(
    *,
    oanda_mode_declaration: Mapping[str, Any],
    risk_limits: Mapping[str, Any],
    execution_controls: Mapping[str, Any],
) -> list[str]:
    return _unique(
        [
            *_list(oanda_mode_declaration.get("blockers")),
            *_list(risk_limits.get("blockers")),
            *_list(execution_controls.get("blockers")),
        ]
    )


def _protected_gate_blockers(
    *,
    protected_runtime_execution: Mapping[str, Any],
    one_order_policy: Mapping[str, Any],
    post_execution_review_loop: Mapping[str, Any],
) -> list[str]:
    return _unique(
        [
            *_list(protected_runtime_execution.get("blockers")),
            *_list(one_order_policy.get("blockers")),
            *_list(post_execution_review_loop.get("blockers")),
        ]
    )


def _upstream_metadata_ready(
    *,
    credential_summary: Mapping[str, Any],
    owner_live_approval_token: Mapping[str, Any],
    oanda_mode_declaration: Mapping[str, Any],
    risk_limits: Mapping[str, Any],
    execution_controls: Mapping[str, Any],
) -> bool:
    return all(
        summary.get("ready") is True
        for summary in (
            credential_summary,
            owner_live_approval_token,
            oanda_mode_declaration,
            risk_limits,
            execution_controls,
        )
    )


def _campaign_execution_metadata_present(source: Mapping[str, Any]) -> bool:
    return any(
        bool(_mapping(source.get(key)))
        for key in (
            "protected_runtime_execution_result",
            "owner_live_approval_token_metadata",
            "oanda_mode_declaration",
            "one_order_policy",
            "risk_limits",
            "execution_controls",
            "post_execution_review_loop",
            "post_trade_review",
        )
    )


def _sensitive_blockers(value: Any, path: str = "") -> list[str]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = _normalize_key(key_text)
            key_path = f"{path}.{key_text}" if path else key_text
            if normalized in SAFE_METADATA_KEYS:
                if not _safe_metadata_value_allowed(child):
                    blockers.append(f"{key_path}:unsafe_metadata_value")
                continue
            if _is_sensitive_key_name(normalized):
                blockers.append(f"sensitive_key:{key_path}")
                continue
            blockers.extend(_sensitive_blockers(child, key_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_sensitive_blockers(child, f"{path}[{index}]"))
    elif isinstance(value, str) and _looks_like_sensitive_value(value):
        blockers.append(f"{path}:sensitive_value")
    return blockers


def _is_sensitive_key_name(normalized_key: str) -> bool:
    if normalized_key in SAFE_METADATA_KEYS:
        return False
    if "account_identifier" in normalized_key:
        return False
    return any(part in normalized_key for part in SENSITIVE_KEY_PARTS)


def _safe_metadata_value_allowed(value: Any) -> bool:
    if isinstance(value, bool):
        return True
    if isinstance(value, str):
        return not _looks_like_sensitive_value(value)
    if isinstance(value, Mapping):
        return not _sensitive_blockers(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return not _sensitive_blockers(value)
    return False


def _looks_like_sensitive_value(value: str) -> bool:
    lowered = value.strip().lower()
    if not lowered:
        return False
    sensitive_markers = (
        "sk-",
        "bearer ",
        "api key",
        "token value",
        "broker token",
        "access token",
        "private key",
        "password",
        "secret",
        "-----begin",
    )
    if any(marker in lowered for marker in sensitive_markers):
        return True
    return _has_long_digit_run(lowered, minimum=8)


def _label_has_sensitive_digits(value: Any) -> bool:
    return isinstance(value, str) and _has_long_digit_run(value, minimum=6)


def _has_long_digit_run(text: str, *, minimum: int) -> bool:
    run = 0
    for char in text:
        if char.isdigit():
            run += 1
            if run >= minimum:
                return True
        else:
            run = 0
    return False


def _expected_true_blockers(data: Mapping[str, Any], keys: Sequence[str]) -> list[str]:
    blockers: list[str] = []
    for key in keys:
        value = _bool(data.get(key))
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is not True:
            blockers.append(f"{key}_false")
    return blockers


def _expected_false_blockers(data: Mapping[str, Any], keys: Sequence[str]) -> list[str]:
    blockers: list[str] = []
    for key in keys:
        value = _bool(data.get(key))
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is not False:
            blockers.append(f"{key}_true")
    return blockers


def _owner_action_queue(
    *,
    campaign_status: str,
    campaign_blockers: Sequence[str],
    next_best_packet: str,
) -> list[dict[str, Any]]:
    safe_actions = {
        "REVIEW_SENSITIVE_DATA_BOUNDARY": "Confirm payload contains no raw credentials, account identifiers, bank data, or card data.",
        "REVIEW_RUNTIME_CREDENTIAL_SESSION_BOUNDARY": "Review runtime-only credential session metadata.",
        "REVIEW_OWNER_APPROVAL_TOKEN_METADATA": "Review owner approval-token metadata without raw token values.",
        "REVIEW_RISK_GATES": "Review stop loss, take profit, spread, slippage, kill-switch, and daily-loss metadata.",
        "REVIEW_PROTECTED_ONE_ORDER_GATE": "Review one-order protected execution gate metadata.",
        "REVIEW_OWNER_VALUE_ENTRY_WORKFLOW": "Review sanitized owner value-entry metadata.",
        "REVIEW_CAPITAL_REDISTRIBUTION_PLANNER": "Review capital redistribution recommendation metadata.",
        "REVIEW_SOS_REMINDER_PACKET": "Review SOS reminder readiness metadata.",
        "REVIEW_22H_6D_READINESS_INDEX": "Review 22h/6d readiness component scores.",
        "REVIEW_POST_EXECUTION_REVIEW_LOOP": "Review sanitized post-execution review metadata.",
        "REVIEW_NEXT_PACKET": "Route to the next governed packet after owner review.",
    }
    return [
        {
            "action_id": action_id,
            "owner_decision_required": True,
            "live_execution_allowed": False,
            "money_movement_allowed": False,
            "broker_api_called": False,
            "credential_read": False,
            "safe_action": safe_actions[action_id],
            "campaign_status": campaign_status,
            "blocked_by": list(campaign_blockers),
            "next_best_packet": next_best_packet if action_id == "REVIEW_NEXT_PACKET" else None,
        }
        for action_id in OWNER_ACTION_IDS
    ]


def _next_best_packet(status: str) -> str:
    if status in NEXT_PACKET_BY_STATUS:
        return NEXT_PACKET_BY_STATUS[status]
    if status.startswith("BLOCKED_BY_"):
        return SCHEMA
    return SCHEMA


def _safe_manual_next_action(status: str) -> str:
    return {
        CAMPAIGN_READY_FOR_OWNER_LIVE_EXCEPTION_REVIEW: (
            "Prepare owner live exception review; do not enter credentials or execute trades in this packet."
        ),
        READY_FOR_PROTECTED_DEMO_EXECUTION_PACKET: (
            "Draft the protected demo execution packet after owner review."
        ),
        READY_FOR_RUNTIME_CREDENTIAL_SESSION_BRIDGE: (
            "Route to runtime credential session bridge; credentials stay outside repo and chat."
        ),
        READY_FOR_OWNER_VALUE_ENTRY_REVIEW: (
            "Owner may review sanitized value-entry metadata only."
        ),
        READY_FOR_CAPITAL_REDISTRIBUTION_REVIEW: (
            "Owner may review capital redistribution metadata; no money movement is authorized."
        ),
        BLOCKED_BY_SENSITIVE_DATA: "Remove sensitive keys or values and rerun with metadata only.",
        BLOCKED_BY_CREDENTIAL_SESSION_BOUNDARY: "Repair runtime credential/session boundary metadata.",
        BLOCKED_BY_OWNER_APPROVAL_TOKEN: "Repair owner approval-token metadata.",
        BLOCKED_BY_RISK_GATES: "Repair risk, stop, spread, slippage, kill-switch, or daily-loss metadata.",
        BLOCKED_BY_PROTECTED_EXECUTION_GATE: "Repair protected one-order gate or post-review metadata.",
        BLOCKED_BY_CAPITAL_POLICY: "Repair capital policy or redistribution planner metadata.",
        BLOCKED_BY_SOS_READINESS: "Enable SOS reminder readiness metadata.",
        BLOCKED_BY_22H_6D_READINESS: "Complete every 22h/6d readiness component.",
        INCOMPLETE_INPUTS: "Provide a mapping payload with campaign metadata.",
    }.get(status, "Resolve blockers and rerun.")


def _audit_record(
    *,
    source: Mapping[str, Any],
    campaign_status: str,
    campaign_ready: bool,
    next_best_packet: str,
    sensitive_data_detected: bool,
    campaign_blockers: Sequence[str],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "evaluated_at_utc": _now_utc_iso(),
        "input_fields_seen": _safe_input_fields_seen(
            source, redacted=sensitive_data_detected
        ),
        "campaign_status": campaign_status,
        "campaign_ready": campaign_ready,
        "next_best_packet": next_best_packet,
        "input_redacted": sensitive_data_detected,
        "campaign_blockers": list(campaign_blockers),
        "read_only": True,
        "metadata_only": True,
        "broker_api_called": False,
        "live_trade_executed": False,
        "demo_trade_executed": False,
        "money_moved": False,
    }


def _safety_summary() -> dict[str, Any]:
    safety = {
        "read_only": True,
        "metadata_only": True,
        "owner_gate_required": True,
        "approval_token_required": True,
        "one_order_only_required": True,
        "runtime_only_credentials_required": True,
        "post_execution_review_required": True,
        "secret_scan_required": True,
        "no_raw_secret_logging": True,
    }
    for field in HARD_FALSE_FIELDS:
        safety[field] = False
    for field in SAFETY_FALSE_FIELDS:
        safety[field] = False
    return safety


def _reminder(
    reminder_id: str,
    severity: str,
    reason: str,
    safe_manual_next_action: str,
) -> dict[str, Any]:
    return {
        "reminder_id": reminder_id,
        "severity": severity,
        "reason": reason,
        "owner_action_required": True,
        "safe_manual_next_action": safe_manual_next_action,
    }


def _capital_safe_action(recommendation: str, blockers: Sequence[str]) -> str:
    if blockers:
        return "Resolve capital planner blockers before owner review."
    if recommendation in TRANSFER_REVIEW_RECOMMENDATIONS:
        return "Owner may review transfer metadata only; no transfer is authorized."
    if recommendation == "COMPOUND_INTO_SAME_PAIR":
        return "Owner may review same-pair compounding metadata only."
    if recommendation == "REDISTRIBUTE_INTO_ALLOWED_PAIR_BASKET":
        return "Owner may review allowed pair-basket redistribution metadata only."
    if recommendation == "HOLD_PROFIT_RESERVE":
        return "Owner may review profit reserve metadata only."
    return "No capital action is recommended."


def _component_ready(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, Mapping):
        for key in ("ready", "readiness_passed", "passed"):
            if _bool(value.get(key), default=False) is True:
                return True
    return False


def _open_risk_active(open_risk: Mapping[str, Any]) -> bool:
    return (
        _decimal(open_risk.get("open_positions_count"), Decimal("0")) > Decimal("0")
        or _decimal(open_risk.get("margin_used"), Decimal("0")) > Decimal("0")
        or _bool(open_risk.get("open_risk_present"), default=False) is True
        or _bool(open_risk.get("pending_settlement"), default=False) is True
        or _bool(open_risk.get("unsettled_pnl"), default=False) is True
    )


def _allocation_is_all_in(value: Any) -> bool:
    if not isinstance(value, Mapping) or not value:
        return False
    amounts = [_decimal(item, Decimal("0")) for item in value.values()]
    if len(amounts) == 1 and amounts[0] >= Decimal("1"):
        return True
    return any(amount >= Decimal("100") for amount in amounts)


def _has_pair_targets(value: Any) -> bool:
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return False


def _safe_owner_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _safe_owner_value(child)
            for key, child in value.items()
            if not _is_sensitive_key_name(_normalize_key(str(key)))
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_safe_owner_value(item) for item in value]
    if isinstance(value, (str, int, float, bool, Decimal)) or value is None:
        return value
    return str(type(value).__name__)


def _redacted_summary(summary_name: str, blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "summary": summary_name,
        "input_redacted": True,
        "present": False,
        "ready": False,
        "metadata_only": True,
        "blockers": list(blockers),
    }


def _missing_from_blockers(blockers: Sequence[str]) -> list[str]:
    return [item for item in blockers if "missing" in item]


def _safe_input_fields_seen(source: Mapping[str, Any], *, redacted: bool) -> list[str]:
    if not redacted:
        return sorted(str(key) for key in source.keys())
    return sorted(
        str(key)
        for key in source.keys()
        if not _is_sensitive_key_name(_normalize_key(str(key)))
    )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[str]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [str(item) for item in value]
    return []


def _bool(value: Any, default: bool | None = None) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y", "on"}:
            return True
        if lowered in {"false", "0", "no", "n", "off"}:
            return False
    return default


def _decimal(value: Any, default: Decimal | None = None) -> Decimal | None:
    if isinstance(value, bool):
        return default
    if value is None:
        return default
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return default


def _text(value: Any, default: str | None = None) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default or ""


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_")


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


__all__ = [
    "SCHEMA",
    "MODE",
    "CAMPAIGN_READY_FOR_OWNER_LIVE_EXCEPTION_REVIEW",
    "READY_FOR_PROTECTED_DEMO_EXECUTION_PACKET",
    "READY_FOR_RUNTIME_CREDENTIAL_SESSION_BRIDGE",
    "READY_FOR_OWNER_VALUE_ENTRY_REVIEW",
    "READY_FOR_CAPITAL_REDISTRIBUTION_REVIEW",
    "BLOCKED_BY_PROTECTED_EXECUTION_GATE",
    "BLOCKED_BY_CREDENTIAL_SESSION_BOUNDARY",
    "BLOCKED_BY_OWNER_APPROVAL_TOKEN",
    "BLOCKED_BY_RISK_GATES",
    "BLOCKED_BY_CAPITAL_POLICY",
    "BLOCKED_BY_SOS_READINESS",
    "BLOCKED_BY_22H_6D_READINESS",
    "BLOCKED_BY_SENSITIVE_DATA",
    "INCOMPLETE_INPUTS",
    "HARD_FALSE_FIELDS",
    "SAFETY_FALSE_FIELDS",
    "evaluate_live_execution_and_capital_operation_campaign_v1",
]
