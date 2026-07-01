"""Metadata-only protected one-order runtime execution gate for AIOS Forex."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_FOREX_OANDA_DEMO_OWNER_APPROVED_ONE_ORDER_PROTECTED_RUNTIME_EXECUTION_V1"
MODE = "READ_ONLY_METADATA_ONLY_PROTECTED_ONE_ORDER_RUNTIME_GATE"

PROTECTED_ONE_ORDER_GATE_CLEARED = "PROTECTED_ONE_ORDER_GATE_CLEARED"
READY_FOR_RUNTIME_CREDENTIAL_SESSION_BRIDGE = (
    "READY_FOR_RUNTIME_CREDENTIAL_SESSION_BRIDGE"
)
READY_FOR_POST_EXECUTION_REVIEW_LOOP = "READY_FOR_POST_EXECUTION_REVIEW_LOOP"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_OWNER_APPROVAL_TOKEN = "BLOCKED_BY_OWNER_APPROVAL_TOKEN"
BLOCKED_BY_CREDENTIAL_SESSION_BOUNDARY = (
    "BLOCKED_BY_CREDENTIAL_SESSION_BOUNDARY"
)
BLOCKED_BY_ONE_ORDER_POLICY = "BLOCKED_BY_ONE_ORDER_POLICY"
BLOCKED_BY_RISK_GATES = "BLOCKED_BY_RISK_GATES"
BLOCKED_BY_KILL_SWITCH = "BLOCKED_BY_KILL_SWITCH"
BLOCKED_BY_DAILY_LOSS_STOP = "BLOCKED_BY_DAILY_LOSS_STOP"
BLOCKED_BY_DUPLICATE_ORDER = "BLOCKED_BY_DUPLICATE_ORDER"
BLOCKED_BY_POST_EXECUTION_REVIEW = "BLOCKED_BY_POST_EXECUTION_REVIEW"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_PACKET_READY = "AIOS_FOREX_OWNER_RUNTIME_CREDENTIAL_SESSION_BRIDGE_V1"

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
        "account_identifier_values_provided",
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
        "redaction_required",
        "no_raw_account_identifier_logging",
        "approval_phrase_present",
        "approval_phrase_matches",
        "approval_action_matches",
        "approval_mode_matches",
        "approval_instrument_matches",
        "approval_units_matches",
        "approval_risk_matches",
        "generic_yes_detected",
        "session_expiry_required",
        "session_unexpired",
        "one_order_session_scope",
    }
)


def evaluate_oanda_demo_owner_approved_one_order_protected_runtime_execution_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Evaluate one protected order gate without touching runtime systems."""

    source = _mapping(payload)
    sensitive_data_blockers = find_sensitive_data_blockers(source)
    sensitive_data_detected = bool(sensitive_data_blockers)

    if sensitive_data_detected:
        approval = _redacted_summary("owner_approval_summary", sensitive_data_blockers)
        credential_boundary = _redacted_summary(
            "credential_boundary_summary", sensitive_data_blockers
        )
        execution_gate = _redacted_summary(
            "execution_gate_summary", sensitive_data_blockers
        )
        risk_gate = _redacted_summary("risk_gate_summary", sensitive_data_blockers)
        post_review = _redacted_summary(
            "post_execution_review_summary", sensitive_data_blockers
        )
    else:
        approval = _summary_owner_approval(
            _first_mapping(source, "owner_approval_metadata", "owner_approval_token_metadata", "approval_token_metadata")
        )
        credential_boundary = _summary_credential_boundary(
            _first_mapping(source, "credential_session_boundary", "runtime_credential_session_boundary")
        )
        execution_gate = _summary_execution_gate(source)
        risk_gate = _summary_risk_gate(source)
        post_review = _summary_post_execution_review(
            _first_mapping(source, "post_execution_review_metadata", "post_execution_review_loop")
        )

    status, blockers = _protected_runtime_status(
        source=source,
        sensitive_data_blockers=sensitive_data_blockers,
        approval=approval,
        credential_boundary=credential_boundary,
        execution_gate=execution_gate,
        risk_gate=risk_gate,
        post_review=post_review,
    )
    protected_runtime_ready = status == PROTECTED_ONE_ORDER_GATE_CLEARED
    next_best_packet = NEXT_PACKET_READY if protected_runtime_ready else SCHEMA

    protected_order_envelope = (
        {}
        if sensitive_data_detected
        else {
            "oanda_mode": execution_gate["oanda_mode"],
            "one_order_only": execution_gate["one_order_only"],
            "max_order_count_this_packet": execution_gate[
                "max_order_count_this_packet"
            ],
            "stop_loss_present": risk_gate["stop_loss_present"],
            "take_profit_present": risk_gate["take_profit_present"],
            "max_risk_per_trade_pct": risk_gate["max_risk_per_trade_pct"],
            "max_daily_loss_pct": risk_gate["max_daily_loss_pct"],
            "max_spread_pips": risk_gate["max_spread_pips"],
            "max_slippage_pips": risk_gate["max_slippage_pips"],
            "post_execution_review_required": post_review[
                "post_execution_review_required"
            ],
            "next_order_blocked_until_review": post_review[
                "next_order_blocked_until_review"
            ],
            **hard_false_result(),
            **safety_false_result(),
        }
    )

    result = {
        "schema": SCHEMA,
        "mode": MODE,
        "protected_runtime_status": status,
        "protected_runtime_ready": protected_runtime_ready,
        "owner_decision_required": True,
        "approval_token_required": True,
        "read_only": True,
        "metadata_only": True,
        **hard_false_result(),
        "protected_order_envelope": protected_order_envelope,
        "execution_gate_summary": execution_gate,
        "risk_gate_summary": risk_gate,
        "owner_approval_summary": approval,
        "credential_boundary_summary": credential_boundary,
        "post_execution_review_summary": post_review,
        "sensitive_data_detected": sensitive_data_detected,
        "sensitive_data_blockers": sensitive_data_blockers,
        "protected_runtime_blockers": blockers,
        "owner_action_queue": _owner_action_queue(blockers, next_best_packet),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(status),
        "audit_record": _audit_record(
            source=source,
            status=status,
            ready=protected_runtime_ready,
            input_redacted=sensitive_data_detected,
            next_best_packet=next_best_packet,
        ),
        "safety": safety_summary(),
        **safety_false_result(),
    }
    return result


def _protected_runtime_status(
    *,
    source: Mapping[str, Any],
    sensitive_data_blockers: Sequence[str],
    approval: Mapping[str, Any],
    credential_boundary: Mapping[str, Any],
    execution_gate: Mapping[str, Any],
    risk_gate: Mapping[str, Any],
    post_review: Mapping[str, Any],
) -> tuple[str, list[str]]:
    if sensitive_data_blockers:
        return BLOCKED_BY_SENSITIVE_DATA, list(sensitive_data_blockers)
    if not source:
        return INCOMPLETE_INPUTS, ["payload_missing"]

    missing = []
    if not approval["metadata_present"]:
        missing.append("owner_approval_metadata_missing")
    if not credential_boundary["metadata_present"]:
        missing.append("credential_session_boundary_missing")
    if not execution_gate["metadata_present"]:
        missing.append("execution_gate_metadata_missing")
    if not risk_gate["metadata_present"]:
        missing.append("risk_gate_metadata_missing")
    if not post_review["metadata_present"]:
        missing.append("post_execution_review_metadata_missing")
    if missing:
        return INCOMPLETE_INPUTS, missing

    if not approval["ready"]:
        return BLOCKED_BY_OWNER_APPROVAL_TOKEN, list(approval["blockers"])
    if not credential_boundary["ready"]:
        return BLOCKED_BY_CREDENTIAL_SESSION_BOUNDARY, list(
            credential_boundary["blockers"]
        )
    if execution_gate["duplicate_order_detected"] is True:
        return BLOCKED_BY_DUPLICATE_ORDER, ["duplicate_order_detected_true"]
    if not execution_gate["ready"]:
        return BLOCKED_BY_ONE_ORDER_POLICY, list(execution_gate["blockers"])
    if risk_gate["kill_switch_active"] is True:
        return BLOCKED_BY_KILL_SWITCH, ["kill_switch_active_true"]
    if risk_gate["daily_loss_stop_active"] is True:
        return BLOCKED_BY_DAILY_LOSS_STOP, ["daily_loss_stop_active_true"]
    if not risk_gate["ready"]:
        return BLOCKED_BY_RISK_GATES, list(risk_gate["blockers"])
    if not post_review["ready"]:
        return BLOCKED_BY_POST_EXECUTION_REVIEW, list(post_review["blockers"])
    return PROTECTED_ONE_ORDER_GATE_CLEARED, []


def _summary_owner_approval(data: Mapping[str, Any]) -> dict[str, Any]:
    true_checks = {
        "approval_token_required": _bool(data.get("approval_token_required")),
        "approval_token_metadata_present": _bool(
            data.get("approval_token_metadata_present")
        ),
        "approval_token_id_present": _bool(data.get("approval_token_id_present")),
        "approval_token_unexpired": _bool(data.get("approval_token_unexpired")),
        "approval_token_unused": _bool(data.get("approval_token_unused")),
        "approval_challenge_hash_present": _bool(
            data.get("approval_challenge_hash_present")
        ),
        "approval_timestamp_present": _bool(
            data.get("approval_timestamp_present")
        ),
        "approval_phrase_matches": _bool(data.get("approval_phrase_matches")),
        "approval_action_matches": _bool(data.get("approval_action_matches")),
        "approval_mode_matches": _bool(data.get("approval_mode_matches")),
        "approval_instrument_matches": _bool(
            data.get("approval_instrument_matches")
        ),
        "approval_units_matches": _bool(data.get("approval_units_matches")),
        "approval_risk_matches": _bool(data.get("approval_risk_matches")),
    }
    false_checks = {
        "generic_yes_detected": _bool(data.get("generic_yes_detected")),
    }
    blockers = [
        *true_blockers(true_checks),
        *false_blockers(false_checks),
    ]
    return {
        "metadata_present": bool(data),
        "ready": bool(data) and not blockers,
        "blockers": unique(blockers),
        **true_checks,
        **false_checks,
    }


def _summary_credential_boundary(data: Mapping[str, Any]) -> dict[str, Any]:
    true_checks = {
        "owner_enters_credentials_outside_repo_chat": _bool(
            data.get("owner_enters_credentials_outside_repo_chat")
        ),
        "runtime_only_credential_handoff": _bool(
            data.get("runtime_only_credential_handoff")
        ),
        "no_stored_api_key": _bool(data.get("no_stored_api_key")),
        "no_stored_account_id": _bool(data.get("no_stored_account_id")),
        "no_master_password": _bool(data.get("no_master_password")),
        "no_vault_password": _bool(data.get("no_vault_password")),
        "no_raw_token": _bool(data.get("no_raw_token")),
        "secret_scan_required": _bool(data.get("secret_scan_required")),
        "redaction_required": _bool(data.get("redaction_required")),
        "session_expiry_required": _bool(data.get("session_expiry_required")),
        "session_unexpired": _bool(data.get("session_unexpired")),
        "one_order_session_scope": _bool(data.get("one_order_session_scope")),
    }
    false_checks = {
        "credential_values_provided": _bool(data.get("credential_values_provided")),
        "credential_values_persisted": _bool(
            data.get("credential_values_persisted")
        ),
        "credential_values_logged": _bool(data.get("credential_values_logged")),
        "credential_values_requested_by_aios": _bool(
            data.get("credential_values_requested_by_aios")
        ),
        "repo_secret_storage_allowed": _bool(
            data.get("repo_secret_storage_allowed")
        ),
        "chat_secret_sharing_allowed": _bool(
            data.get("chat_secret_sharing_allowed")
        ),
        "env_var_read_allowed": _bool(data.get("env_var_read_allowed")),
        "account_id_provided": _bool(data.get("account_id_provided")),
    }
    blockers = [*true_blockers(true_checks), *false_blockers(false_checks)]
    return {
        "metadata_present": bool(data),
        "ready": bool(data) and not blockers,
        "blockers": unique(blockers),
        **true_checks,
        **false_checks,
    }


def _summary_execution_gate(source: Mapping[str, Any]) -> dict[str, Any]:
    data = _first_mapping(source, "execution_gate_metadata", "one_order_policy")
    mode_data = _first_mapping(source, "oanda_mode_declaration", "broker_mode_metadata")
    mode = _text(mode_data.get("mode"), _text(source.get("oanda_mode")))
    mode_ok = mode in ALLOWED_OANDA_MODES
    one_order_only = _bool(data.get("one_order_only"))
    max_order_count = _number(data.get("max_order_count_this_packet"))
    duplicate_order_detected = _bool(data.get("duplicate_order_detected"))
    existing_order = _bool(data.get("existing_open_order_for_candidate"))
    existing_position = _bool(data.get("existing_open_position_for_candidate"))
    account_id_provided = _bool(
        mode_data.get("account_id_provided"),
        default=_bool(source.get("account_id_provided")),
    )
    blockers = []
    if mode is None:
        blockers.append("oanda_mode_missing")
    elif not mode_ok:
        blockers.append("oanda_mode_not_allowed")
    if account_id_provided is not False:
        blockers.append("account_id_provided_not_false")
    if one_order_only is not True:
        blockers.append("one_order_only_missing_or_false")
    if max_order_count != 1:
        blockers.append("max_order_count_this_packet_not_one")
    if duplicate_order_detected is not False:
        blockers.append("duplicate_order_detected_true")
    if existing_order is not False:
        blockers.append("existing_open_order_for_candidate_true")
    if existing_position is not False:
        blockers.append("existing_open_position_for_candidate_true")
    return {
        "metadata_present": bool(data) or bool(mode_data),
        "ready": (bool(data) or bool(mode_data)) and not blockers,
        "blockers": unique(blockers),
        "oanda_mode": mode,
        "oanda_mode_allowed": mode_ok,
        "account_id_provided": account_id_provided,
        "one_order_only": one_order_only,
        "max_order_count_this_packet": max_order_count,
        "duplicate_order_detected": duplicate_order_detected,
        "existing_open_order_for_candidate": existing_order,
        "existing_open_position_for_candidate": existing_position,
    }


def _summary_risk_gate(source: Mapping[str, Any]) -> dict[str, Any]:
    data = _first_mapping(source, "risk_gate_metadata", "risk_limits", "risk_envelope")
    controls = _first_mapping(source, "execution_controls", "risk_controls")
    stop_loss = _bool(data.get("stop_loss_present"))
    take_profit = _bool(data.get("take_profit_present"))
    max_trade_risk = _number(data.get("max_risk_per_trade_pct"))
    max_daily_loss = _number(data.get("max_daily_loss_pct"))
    max_spread = _number(data.get("max_spread_pips"))
    max_slippage = _number(data.get("max_slippage_pips"))
    kill_switch_active = _bool(controls.get("kill_switch_active"))
    daily_loss_stop_active = _bool(controls.get("daily_loss_stop_active"))
    blockers = []
    if stop_loss is not True:
        blockers.append("stop_loss_present_missing_or_false")
    if take_profit is not True:
        blockers.append("take_profit_present_missing_or_false")
    if max_trade_risk is None or max_trade_risk > 0.01:
        blockers.append("max_risk_per_trade_pct_above_limit")
    if max_daily_loss is None or max_daily_loss > 0.03:
        blockers.append("max_daily_loss_pct_above_limit")
    if max_spread is None or max_spread <= 0:
        blockers.append("max_spread_pips_not_positive")
    if max_slippage is None or max_slippage < 0:
        blockers.append("max_slippage_pips_negative")
    if kill_switch_active is not False:
        blockers.append("kill_switch_active_true")
    if daily_loss_stop_active is not False:
        blockers.append("daily_loss_stop_active_true")
    return {
        "metadata_present": bool(data) or bool(controls),
        "ready": (bool(data) or bool(controls)) and not blockers,
        "blockers": unique(blockers),
        "stop_loss_present": stop_loss,
        "take_profit_present": take_profit,
        "max_risk_per_trade_pct": max_trade_risk,
        "max_daily_loss_pct": max_daily_loss,
        "max_spread_pips": max_spread,
        "max_slippage_pips": max_slippage,
        "kill_switch_active": kill_switch_active,
        "daily_loss_stop_active": daily_loss_stop_active,
    }


def _summary_post_execution_review(data: Mapping[str, Any]) -> dict[str, Any]:
    post_required = _bool(data.get("post_execution_review_required"))
    next_blocked = _bool(data.get("next_order_blocked_until_review"))
    blockers = []
    if post_required is not True:
        blockers.append("post_execution_review_required_missing_or_false")
    if next_blocked is not True:
        blockers.append("next_order_blocked_until_review_missing_or_false")
    return {
        "metadata_present": bool(data),
        "ready": bool(data) and not blockers,
        "blockers": unique(blockers),
        "post_execution_review_required": post_required,
        "next_order_blocked_until_review": next_blocked,
    }


def hard_false_result() -> dict[str, bool]:
    return {key: False for key in HARD_FALSE_FIELDS}


def safety_false_result() -> dict[str, bool]:
    return {key: False for key in SAFETY_FALSE_FIELDS}


def safety_summary() -> dict[str, Any]:
    return {
        "read_only": True,
        "metadata_only": True,
        "owner_approval_required": True,
        "approval_token_required": True,
        "post_execution_review_required": True,
        **hard_false_result(),
        **safety_false_result(),
    }


def find_sensitive_data_blockers(value: Any, path: str = "payload") -> list[str]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.lower().replace("-", "_")
            child_path = f"{path}.{key_text}"
            if _is_sensitive_key(normalized):
                blockers.append(f"{child_path}:sensitive_key")
                continue
            if normalized in SAFE_METADATA_KEYS and _value_looks_sensitive(child):
                blockers.append(f"{child_path}:sensitive_value")
                continue
            blockers.extend(find_sensitive_data_blockers(child, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for index, child in enumerate(value):
            blockers.extend(find_sensitive_data_blockers(child, f"{path}[{index}]"))
    elif _value_looks_sensitive(value):
        blockers.append(f"{path}:sensitive_value")
    return unique(blockers)


def _is_sensitive_key(normalized_key: str) -> bool:
    if normalized_key in SAFE_METADATA_KEYS:
        return False
    if "account_identifier" in normalized_key:
        return False
    return any(part in normalized_key for part in SENSITIVE_KEY_PARTS)


def _value_looks_sensitive(value: Any) -> bool:
    if isinstance(value, str):
        lowered = value.strip().lower()
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
        return any(marker in lowered for marker in sensitive_markers) or _has_long_digit_run(
            lowered, minimum=8
        )
    if isinstance(value, Mapping):
        return bool(find_sensitive_data_blockers(value))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_value_looks_sensitive(item) for item in value)
    return False


def _redacted_summary(summary_name: str, blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "summary": summary_name,
        "input_redacted": True,
        "ready": False,
        "metadata_present": False,
        "blockers": list(blockers),
    }


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


def true_blockers(values: Mapping[str, bool | None]) -> list[str]:
    blockers: list[str] = []
    for key, value in values.items():
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is not True:
            blockers.append(f"{key}_false")
    return blockers


def false_blockers(values: Mapping[str, bool | None]) -> list[str]:
    blockers: list[str] = []
    for key, value in values.items():
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is not False:
            blockers.append(f"{key}_true")
    return blockers


def _owner_action_queue(
    blockers: Sequence[str],
    next_best_packet: str,
) -> list[dict[str, Any]]:
    actions = (
        "REVIEW_PROTECTED_ORDER_ENVELOPE",
        "REVIEW_OWNER_APPROVAL_TOKEN",
        "REVIEW_CREDENTIAL_SESSION_BOUNDARY",
        "REVIEW_RISK_GATES",
        "REVIEW_POST_EXECUTION_REVIEW",
        "REVIEW_NEXT_PACKET",
    )
    return [
        {
            "action_id": action,
            "owner_decision_required": True,
            "blocked_by": list(blockers),
            "next_best_packet": next_best_packet if action == "REVIEW_NEXT_PACKET" else None,
            **hard_false_result(),
            **safety_false_result(),
        }
        for action in actions
    ]


def _safe_manual_next_action(status: str) -> str:
    if status == PROTECTED_ONE_ORDER_GATE_CLEARED:
        return "Review the sanitized protected order envelope before any owner credential session bridge."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys or values and rerun with sanitized metadata only."
    if status == BLOCKED_BY_OWNER_APPROVAL_TOKEN:
        return "Provide exact owner approval-token metadata; a generic yes is not enough."
    if status == BLOCKED_BY_CREDENTIAL_SESSION_BOUNDARY:
        return "Repair runtime-only credential session metadata before continuing."
    if status == BLOCKED_BY_POST_EXECUTION_REVIEW:
        return "Require post-execution review and keep the next order blocked until review."
    return "Resolve blockers and rerun this metadata evaluator."


def _audit_record(
    *,
    source: Mapping[str, Any],
    status: str,
    ready: bool,
    input_redacted: bool,
    next_best_packet: str,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "as_of_utc": _now_utc_iso(),
        "input_fields_seen": _safe_input_fields_seen(source, redacted=input_redacted),
        "protected_runtime_status": status,
        "protected_runtime_ready": ready,
        "input_redacted": input_redacted,
        "next_best_packet": next_best_packet,
        "read_only": True,
        "metadata_only": True,
        **hard_false_result(),
        **safety_false_result(),
    }


def _safe_input_fields_seen(source: Mapping[str, Any], *, redacted: bool) -> list[str]:
    if not redacted:
        return sorted(str(key) for key in source.keys())
    return sorted(
        str(key)
        for key in source.keys()
        if not _is_sensitive_key(str(key).lower().replace("-", "_"))
    )


def _first_mapping(source: Mapping[str, Any], *keys: str) -> Mapping[str, Any]:
    for key in keys:
        value = source.get(key)
        if isinstance(value, Mapping):
            return value
    return {}


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
        return value.strip().upper()
    return default


def unique(values: Sequence[Any]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value)
        if text and text not in seen:
            seen.add(text)
            output.append(text)
    return output


def _now_utc_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
