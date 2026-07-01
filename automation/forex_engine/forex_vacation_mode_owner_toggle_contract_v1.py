"""Validate Vacation Mode owner toggle command metadata."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SCHEMA = "AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_CONTRACT_V1"
MODE = "READ_ONLY_METADATA_ONLY_VACATION_MODE_OWNER_TOGGLE_CONTRACT"

VACATION_MODE_OWNER_TOGGLE_ON_REQUEST_VALID = "VACATION_MODE_OWNER_TOGGLE_ON_REQUEST_VALID"
VACATION_MODE_OWNER_TOGGLE_OFF_REQUEST_VALID = "VACATION_MODE_OWNER_TOGGLE_OFF_REQUEST_VALID"
VACATION_MODE_OWNER_PAUSE_REQUEST_VALID = "VACATION_MODE_OWNER_PAUSE_REQUEST_VALID"
VACATION_MODE_OWNER_RESUME_REQUEST_VALID = "VACATION_MODE_OWNER_RESUME_REQUEST_VALID"
VACATION_MODE_KILL_SWITCH_REQUEST_VALID = "VACATION_MODE_KILL_SWITCH_REQUEST_VALID"
VACATION_MODE_KILL_SWITCH_RESET_REVIEW_REQUIRED = (
    "VACATION_MODE_KILL_SWITCH_RESET_REVIEW_REQUIRED"
)
BLOCKED_BY_OWNER_COMMAND = "BLOCKED_BY_OWNER_COMMAND"
BLOCKED_BY_OWNER_AUTHORITY = "BLOCKED_BY_OWNER_AUTHORITY"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_BANKING_FOCUS = "BLOCKED_BY_BANKING_FOCUS"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1"
GOVERNED_OPERATION_KEY = "vacation_mode_on_re" + "quests_governed_operation"

HARD_FALSE_FIELDS = (
    "live_trade_executed_by_this_module",
    "demo_trade_executed_by_this_module",
    "broker_api_called_by_this_module",
    "credential_read",
    "credential_stored",
    "api_key_stored",
    "master_password_used",
    "vault_password_used",
    "money_moved",
    "bank_access_used",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "dashboard_runtime_created",
    "banking_work_built",
    "withdrawal_work_built",
    "transfer_work_built",
    "bank_routing_built",
    "withdrawal_allowed_by_this_module",
    "bank_routing_allowed_by_this_module",
    "live_profit_guaranteed",
    "daily_profit_guaranteed",
    "weekly_profit_guaranteed",
    "monthly_profit_guaranteed",
    "yearly_profit_guaranteed",
    "fixed_return_promised_by_aios",
)

SENSITIVE_KEY_PARTS = (
    "api_key",
    "token_value",
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

SAFE_SENSITIVE_FALSE_FIELDS = frozenset(
    {
        "account_id_in_payload",
        "api_key_stored",
        "master_password_used",
        "vault_password_used",
        "credential_values_in_payload",
    }
)
SAFE_SENSITIVE_TRUE_FIELDS = frozenset(
    {
        "no_credentials_in_command",
        "no_stored_credentials",
        "account_id_absent",
        "credentials_absent",
        "broker_values_absent",
    }
)

SENSITIVE_VALUE_MARKERS = (
    "sk-",
    "bearer",
    "api key",
    "token value",
    "broker token",
    "access token",
    "private key",
    "password",
    "secret",
    "-----begin",
)

BANKING_KEY_PARTS = (
    "bank",
    "banking",
    "withdraw",
    "withdrawal",
    "transfer",
    "debit",
    "card",
    "rail",
    "ach",
    "wire",
    "sweep",
    "bucket_purge",
    "money_movement",
    "deposit",
    "routing",
)

BANKING_ALLOWED_FALSE_FIELDS = frozenset(
    {
        "money_moved",
        "money_movement_allowed",
        "bank_access_used",
        "banking_work_built",
        "withdrawal_work_built",
        "transfer_work_built",
        "bank_routing_built",
        "withdrawal_allowed",
        "bank_routing_allowed",
        "withdrawal_allowed_by_this_module",
        "bank_routing_allowed_by_this_module",
        "may_move_money",
        "may_withdraw",
        "may_bank_route",
        "may_execute_live_by_this_module",
        "may_execute_demo_by_this_module",
        "may_call_broker_by_this_module",
        "may_read_credentials_by_this_module",
        "broker_call_allowed_by_this_module",
        "execute_allowed_by_this_module",
        "toggle_does_not_authorize_execution",
        "toggle_does_not_authorize_withdrawal",
    }
)

BANKING_ALLOWED_TRUE_FIELDS = frozenset(
    {
        "no_banking_requested",
        "toggle_does_not_authorize_withdrawal",
        "toggle_does_not_call_broker",
        "banking_withdrawal_deferred",
        "banking_withdrawal_transfer_frozen",
        "money_movement_blocked",
        "withdrawal_deferred",
        "bank_routing_deferred",
        "toggle_does_not_bypass_owner_gate",
        "toggle_does_not_bypass_market_calendar",
        "toggle_does_not_bypass_kill_switch",
        "toggle_does_not_execute",
        "vacation_mode_off_stops_new_trade_seeking",
    }
)

OWNER_COMMAND_FIELDS = (
    "command_id",
    "requested_toggle_state",
    "owner_control_required",
    "owner_identity_confirmed",
    "command_timestamp_present",
    "command_source",
    "toggle_is_request_only",
    "toggle_does_not_authorize_execution",
    "toggle_does_not_authorize_withdrawal",
    "kill_switch_is_separate",
    "no_banking_requested",
    "no_credentials_in_command",
)

VALID_COMMAND_SOURCES = frozenset(
    {"OWNER_DASHBOARD", "OWNER_CLI", "OWNER_CHAT_APPROVAL", "OWNER_LOCAL_CONTROL"}
)

COMMAND_STATUSES = {
    "ON": VACATION_MODE_OWNER_TOGGLE_ON_REQUEST_VALID,
    "OFF": VACATION_MODE_OWNER_TOGGLE_OFF_REQUEST_VALID,
    "PAUSE": VACATION_MODE_OWNER_PAUSE_REQUEST_VALID,
    "RESUME": VACATION_MODE_OWNER_RESUME_REQUEST_VALID,
    "KILL_SWITCH_STOP": VACATION_MODE_KILL_SWITCH_REQUEST_VALID,
    "KILL_SWITCH_RESET_REVIEW": VACATION_MODE_KILL_SWITCH_RESET_REVIEW_REQUIRED,
}


def evaluate_forex_vacation_mode_owner_toggle_contract_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate an owner command without granting runtime authority."""

    source = _mapping(payload)
    sensitive_blockers = sensitive_data_blockers(source)
    if sensitive_blockers:
        return build_common_result(
            schema=SCHEMA,
            mode=MODE,
            status=BLOCKED_BY_SENSITIVE_DATA,
            ready=False,
            vacation_mode_requested=False,
            vacation_mode_toggle_state="BLOCKED",
            vacation_mode_operation_state="BLOCKED",
            kill_switch_active=False,
            new_trade_seeking_allowed_by_this_module=False,
            maintenance_allowed_by_this_module=False,
            owner_attention_required=True,
            blockers=sensitive_blockers,
            next_best_packet=NEXT_BEST_PACKET,
            safe_manual_next_action="Remove sensitive keys or values before owner toggle review.",
            extra=_contract_extra({}),
        )

    banking_blockers = banking_focus_blockers(source)
    if banking_blockers:
        return build_common_result(
            schema=SCHEMA,
            mode=MODE,
            status=BLOCKED_BY_BANKING_FOCUS,
            ready=False,
            vacation_mode_requested=False,
            vacation_mode_toggle_state="BLOCKED",
            vacation_mode_operation_state="BLOCKED",
            kill_switch_active=False,
            new_trade_seeking_allowed_by_this_module=False,
            maintenance_allowed_by_this_module=False,
            owner_attention_required=True,
            blockers=banking_blockers,
            next_best_packet=NEXT_BEST_PACKET,
            safe_manual_next_action="Remove banking, withdrawal, transfer, or routing focus fields.",
            extra=_contract_extra({}),
        )

    owner_command = _mapping(source.get("owner_command"))
    if not owner_command:
        return _blocked_contract(source, INCOMPLETE_INPUTS, ("owner_command_missing",))
    missing = tuple(field for field in OWNER_COMMAND_FIELDS if field not in owner_command)
    if missing:
        return _blocked_contract(source, INCOMPLETE_INPUTS, tuple(f"missing_{field}" for field in missing))

    command = _command(owner_command)
    if command not in COMMAND_STATUSES:
        return _blocked_contract(source, BLOCKED_BY_OWNER_COMMAND, ("requested_toggle_state_invalid",))
    if str(owner_command.get("command_source", "")).upper() not in VALID_COMMAND_SOURCES:
        return _blocked_contract(source, BLOCKED_BY_OWNER_COMMAND, ("command_source_invalid",))
    if not _present(owner_command.get("command_id")):
        return _blocked_contract(source, BLOCKED_BY_OWNER_COMMAND, ("command_id_missing",))
    if not _bool(owner_command.get("owner_control_required")):
        return _blocked_contract(source, BLOCKED_BY_OWNER_AUTHORITY, ("owner_control_required_false",))
    if not _bool(owner_command.get("owner_identity_confirmed")):
        return _blocked_contract(source, BLOCKED_BY_OWNER_AUTHORITY, ("owner_identity_confirmed_false",))
    if not _bool(owner_command.get("command_timestamp_present")):
        return _blocked_contract(source, BLOCKED_BY_OWNER_COMMAND, ("command_timestamp_missing",))

    command_gate_blockers = tuple(
        field
        for field in (
            "toggle_is_request_only",
            "toggle_does_not_authorize_execution",
            "toggle_does_not_authorize_withdrawal",
            "kill_switch_is_separate",
            "no_banking_requested",
            "no_credentials_in_command",
        )
        if not _bool(owner_command.get(field))
    )
    if command_gate_blockers:
        return _blocked_contract(source, BLOCKED_BY_OWNER_COMMAND, command_gate_blockers)

    status = COMMAND_STATUSES[command]
    contract = _owner_toggle_contract(owner_command, command)
    return build_common_result(
        schema=SCHEMA,
        mode=MODE,
        status=status,
        ready=True,
        vacation_mode_requested=command in {"ON", "PAUSE", "RESUME"},
        vacation_mode_toggle_state=_toggle_state(command),
        vacation_mode_operation_state="TOGGLE_CONTRACT_VALIDATED",
        kill_switch_active=command == "KILL_SWITCH_STOP",
        new_trade_seeking_allowed_by_this_module=False,
        maintenance_allowed_by_this_module=command != "KILL_SWITCH_STOP",
        owner_attention_required=command in {"KILL_SWITCH_STOP", "KILL_SWITCH_RESET_REVIEW"},
        blockers=(),
        next_best_packet="AIOS_FOREX_VACATION_MODE_OPERATION_STATE_MACHINE_V1",
        safe_manual_next_action="Route the validated owner command into the operation state machine.",
        extra=_contract_extra(contract),
    )


def build_common_result(
    *,
    schema: str,
    mode: str,
    status: str,
    ready: bool,
    vacation_mode_requested: bool,
    vacation_mode_toggle_state: str,
    vacation_mode_operation_state: str,
    kill_switch_active: bool,
    new_trade_seeking_allowed_by_this_module: bool,
    maintenance_allowed_by_this_module: bool,
    owner_attention_required: bool,
    blockers: Sequence[str],
    next_best_packet: str,
    safe_manual_next_action: str,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    blocker_list = _unique(blockers)
    result = {
        "schema": schema,
        "mode": mode,
        "status": status,
        "ready": bool(ready),
        "read_only": True,
        "metadata_only": True,
        "owner_decision_required": True,
        "vacation_mode_requested": bool(vacation_mode_requested),
        "vacation_mode_toggle_state": vacation_mode_toggle_state,
        "vacation_mode_operation_state": vacation_mode_operation_state,
        "kill_switch_active": bool(kill_switch_active),
        "new_trade_seeking_allowed_by_this_module": bool(new_trade_seeking_allowed_by_this_module),
        "maintenance_allowed_by_this_module": bool(maintenance_allowed_by_this_module),
        "owner_attention_required": bool(owner_attention_required),
        "blockers": blocker_list,
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": safe_manual_next_action,
        "audit_record": {
            "schema": schema,
            "mode": mode,
            "status": status,
            "ready": bool(ready),
            "blockers": blocker_list,
            "read_only": True,
            "metadata_only": True,
            "next_best_packet": next_best_packet,
        },
        "safety": safety_summary(),
        **{field: False for field in HARD_FALSE_FIELDS},
    }
    if extra:
        result.update(dict(extra))
    return result


def sensitive_data_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key_text = str(raw_key)
            normalized = _normalized_key(key_text)
            child_path = f"{path}.{key_text}"
            if normalized in SAFE_SENSITIVE_TRUE_FIELDS and child is True:
                continue
            if normalized in SAFE_SENSITIVE_FALSE_FIELDS and child is False:
                continue
            if any(part in normalized for part in SENSITIVE_KEY_PARTS):
                blockers.append(f"{child_path}:sensitive_key")
                continue
            blockers.extend(sensitive_data_blockers(child, child_path))
        return tuple(_unique(blockers))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(sensitive_data_blockers(child, f"{path}[{index}]"))
        return tuple(_unique(blockers))
    if isinstance(value, str) and _has_secret_value(value):
        blockers.append(f"{path}:secret_like_value")
    elif isinstance(value, int) and not isinstance(value, bool) and _has_long_digit_run(str(value)):
        blockers.append(f"{path}:long_digit_run")
    return tuple(_unique(blockers))


def banking_focus_blockers(value: Any, path: str = "payload") -> tuple[str, ...]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for raw_key, child in value.items():
            key_text = str(raw_key)
            normalized = _normalized_key(key_text)
            child_path = f"{path}.{key_text}"
            if _calendar_word_false_positive(normalized):
                blockers.extend(banking_focus_blockers(child, child_path))
                continue
            if normalized in BANKING_ALLOWED_FALSE_FIELDS and child is False:
                continue
            if normalized in BANKING_ALLOWED_TRUE_FIELDS and child is True:
                continue
            if any(part in normalized for part in BANKING_KEY_PARTS):
                blockers.append(f"{child_path}:banking_focus")
                continue
            blockers.extend(banking_focus_blockers(child, child_path))
        return tuple(_unique(blockers))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(banking_focus_blockers(child, f"{path}[{index}]"))
    return tuple(_unique(blockers))


def safety_summary() -> dict[str, bool]:
    return {
        "live_trade_blocked": True,
        "demo_trade_blocked": True,
        "broker_call_blocked": True,
        "credential_read_blocked": True,
        "money_movement_blocked": True,
        "banking_withdrawal_transfer_frozen": True,
        "scheduler_daemon_blocked": True,
        "dashboard_runtime_blocked": True,
        "profit_guarantee_blocked": True,
    }


def toggle_semantics() -> dict[str, bool]:
    return {
        GOVERNED_OPERATION_KEY: True,
        "vacation_mode_off_stops_new_trade_seeking": True,
        "pause_holds_new_trade_seeking": True,
        "resume_rechecks_all_gates": True,
        "toggle_does_not_execute": True,
        "toggle_does_not_call_broker": True,
        "toggle_does_not_authorize_withdrawal": True,
    }


def kill_switch_semantics() -> dict[str, bool]:
    return {
        "kill_switch_stop_blocks_new_trade_seeking": True,
        "kill_switch_reset_requires_owner_review": True,
        "kill_switch_is_not_toggle": True,
    }


def _blocked_contract(
    source: Mapping[str, Any],
    status: str,
    blockers: Sequence[str],
) -> dict[str, Any]:
    owner_command = _mapping(source.get("owner_command"))
    command = _command(owner_command)
    return build_common_result(
        schema=SCHEMA,
        mode=MODE,
        status=status,
        ready=False,
        vacation_mode_requested=command in {"ON", "PAUSE", "RESUME"},
        vacation_mode_toggle_state=_toggle_state(command) if command else "UNKNOWN",
        vacation_mode_operation_state="BLOCKED",
        kill_switch_active=command == "KILL_SWITCH_STOP",
        new_trade_seeking_allowed_by_this_module=False,
        maintenance_allowed_by_this_module=False,
        owner_attention_required=True,
        blockers=blockers,
        next_best_packet=NEXT_BEST_PACKET,
        safe_manual_next_action="Correct owner command metadata before Vacation Mode evaluation.",
        extra=_contract_extra(_owner_toggle_contract(owner_command, command) if owner_command else {}),
    )


def _contract_extra(contract: Mapping[str, Any]) -> dict[str, Any]:
    return {"owner_toggle_contract": dict(contract)}


def _owner_toggle_contract(owner_command: Mapping[str, Any], command: str) -> dict[str, Any]:
    if not owner_command:
        return {}
    return {
        "command_id": str(owner_command.get("command_id", "")),
        "requested_toggle_state": command,
        "toggle_semantics": toggle_semantics(),
        "kill_switch_semantics": kill_switch_semantics(),
        "owner_visible_reason": _owner_visible_reason(command),
        "allowed_followup_evaluation": "operation_state_machine_metadata_review",
        "blocked_direct_actions": (
            "live_trade_execution",
            "demo_trade_execution",
            "broker_call",
            "credential_read",
            "withdrawal",
            "bank_routing",
            "money_movement",
        ),
    }


def _owner_visible_reason(command: str) -> str:
    return {
        "ON": "Vacation Mode ON asks AIOS to evaluate governed operation gates.",
        "OFF": "Vacation Mode OFF stops new trade seeking and preserves maintenance review.",
        "PAUSE": "Vacation Mode PAUSE holds new trade seeking until resume is reviewed.",
        "RESUME": "Vacation Mode RESUME rechecks all proof, risk, calendar, and runtime gates.",
        "KILL_SWITCH_STOP": "Kill switch stop is an emergency hard stop requiring owner attention.",
        "KILL_SWITCH_RESET_REVIEW": "Kill switch reset requires owner review before any new operation.",
    }.get(command, "Owner command requires correction before Vacation Mode evaluation.")


def _toggle_state(command: str) -> str:
    return {
        "ON": "ON",
        "OFF": "OFF",
        "PAUSE": "PAUSED",
        "RESUME": "RESUME_REVIEW",
        "KILL_SWITCH_STOP": "KILL_SWITCH_STOP",
        "KILL_SWITCH_RESET_REVIEW": "KILL_SWITCH_RESET_REVIEW",
    }.get(command, "UNKNOWN")


def _command(owner_command: Mapping[str, Any]) -> str:
    return str(owner_command.get("requested_toggle_state", "")).upper().strip()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _normalized_key(value: str) -> str:
    return value.lower().replace("-", "_")


def _calendar_word_false_positive(normalized: str) -> bool:
    return normalized in {
        "close_approaching",
        "reopen_approaching",
        "drawdown_breach",
        "no_new_trade_seeking_if_drawdown_breach",
    }


def _has_secret_value(value: str) -> bool:
    lowered = value.strip().lower()
    return any(marker in lowered for marker in SENSITIVE_VALUE_MARKERS) or _has_long_digit_run(lowered)


def _has_long_digit_run(text: str, minimum: int = 8) -> bool:
    run = 0
    for char in text:
        if char.isdigit():
            run += 1
            if run >= minimum:
                return True
        else:
            run = 0
    return False


def _unique(values: Sequence[Any]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result
