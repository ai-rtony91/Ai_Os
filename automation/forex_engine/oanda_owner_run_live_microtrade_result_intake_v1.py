"""Sanitized intake for one owner-provided live microtrade result."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from automation.forex_engine.oanda_owner_run_live_microtrade_result_contract_v1 import (
    ALLOWED_SANITIZED_RESULT_FIELDS,
    EXACT_OWNER_WARNING,
    EXACT_RESULT_WARNING,
    OandaOwnerRunLiveMicrotradeResultContractInput,
    PROTECTED_FLAG_NAMES,
    REQUIRED_SANITIZED_RESULT_FIELDS,
    VERSION as CONTRACT_VERSION,
    build_sample_breakeven_result_input as contract_breakeven_input,
    build_sample_loss_result_input as contract_loss_input,
    build_sample_missing_owner_result_input as contract_missing_input,
    build_sample_profit_result_input as contract_profit_input,
    build_sample_unsafe_result_input as contract_unsafe_input,
    jsonable,
    markdown_safety_lines,
    protected_flags_false,
    text_value,
    truthy_unsafe,
    unsafe_payload_blockers,
)


VERSION = "oanda_owner_run_live_microtrade_result_intake_v1"

OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_ACCEPTED = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_ACCEPTED"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_NO_OWNER_RESULT = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_NO_OWNER_RESULT"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_INCOMPLETE = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_INCOMPLETE"
)
OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_UNSAFE = (
    "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_UNSAFE"
)


@dataclass(frozen=True)
class OandaOwnerRunLiveMicrotradeResultIntakeInput:
    owner_result: Mapping[str, Any] | None
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class OandaOwnerRunLiveMicrotradeResultIntakeResult:
    version: str
    contract_version: str
    classification: str
    intake_accepted: bool
    sanitized_result_fields: Mapping[str, Any]
    missing_fields: tuple[str, ...]
    blocked_items: tuple[str, ...]
    result_reference: str
    result_capture_only: bool
    owner_warning: str
    result_warning: str
    protected_flags: Mapping[str, bool]
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    live_execution_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool
    autonomous_execution_allowed: bool
    scheduler_allowed: bool
    daemon_allowed: bool
    webhook_allowed: bool
    live_micro_trade_exception_allowed: bool
    owner_live_execution_approval_present: bool
    codex_live_execution_authorized: bool
    unattended_vacation_mode_allowed: bool
    vacation_profit_trial_allowed: bool
    repeat_live_trade_allowed: bool


def build_sample_profit_result_input() -> OandaOwnerRunLiveMicrotradeResultIntakeInput:
    return _from_contract_input(contract_profit_input())


def build_sample_loss_result_input() -> OandaOwnerRunLiveMicrotradeResultIntakeInput:
    return _from_contract_input(contract_loss_input())


def build_sample_breakeven_result_input() -> OandaOwnerRunLiveMicrotradeResultIntakeInput:
    return _from_contract_input(contract_breakeven_input())


def build_sample_missing_owner_result_input() -> OandaOwnerRunLiveMicrotradeResultIntakeInput:
    return _from_contract_input(contract_missing_input())


def build_sample_unsafe_result_input() -> OandaOwnerRunLiveMicrotradeResultIntakeInput:
    return _from_contract_input(contract_unsafe_input())


def intake_oanda_owner_run_live_microtrade_result(
    intake_input: OandaOwnerRunLiveMicrotradeResultIntakeInput | Mapping[str, Any] | None = None,
) -> OandaOwnerRunLiveMicrotradeResultIntakeResult:
    active_input = _coerce_input(intake_input or build_sample_profit_result_input())
    payload = _mapping_or_none(active_input.owner_result)
    missing_fields = _missing_fields(payload)
    blocked_items = _blocked_items(payload, active_input.unsafe_flags)
    if payload is None:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_NO_OWNER_RESULT
    elif blocked_items:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_UNSAFE
    elif missing_fields:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_BLOCKED_INCOMPLETE
    else:
        classification = OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_ACCEPTED
    sanitized = _sanitize_payload(payload or {})
    protected_flags = protected_flags_false()
    return OandaOwnerRunLiveMicrotradeResultIntakeResult(
        version=VERSION,
        contract_version=CONTRACT_VERSION,
        classification=classification,
        intake_accepted=classification
        == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_ACCEPTED,
        sanitized_result_fields=jsonable(sanitized),
        missing_fields=missing_fields,
        blocked_items=blocked_items,
        result_reference=text_value((payload or {}).get("result_reference")),
        result_capture_only=True,
        owner_warning=EXACT_OWNER_WARNING,
        result_warning=EXACT_RESULT_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return jsonable(result)


def to_operator_text(result: OandaOwnerRunLiveMicrotradeResultIntakeResult) -> str:
    return "\n".join(
        (
            f"Result intake status: {result.classification}.",
            f"Result reference: {result.result_reference or 'missing'}.",
            "Only sanitized owner-supplied result fields are preserved.",
            result.owner_warning,
            result.result_warning,
        )
    )


def to_markdown(result: OandaOwnerRunLiveMicrotradeResultIntakeResult) -> str:
    rows = [
        "# AIOS Forex OANDA Owner-Run Live Microtrade Result Intake V1",
        "",
        f"- Classification: `{result.classification}`",
        f"- Intake accepted: `{str(result.intake_accepted).lower()}`",
        f"- Result reference: `{result.result_reference or 'missing'}`",
        "",
        "## Missing Fields",
    ]
    rows.extend(f"- `{item}`" for item in result.missing_fields)
    rows.extend(("", "## Blocked Items"))
    rows.extend(f"- `{item}`" for item in result.blocked_items)
    rows.extend(markdown_safety_lines())
    return "\n".join(rows) + "\n"


def _from_contract_input(
    contract_input: OandaOwnerRunLiveMicrotradeResultContractInput,
) -> OandaOwnerRunLiveMicrotradeResultIntakeInput:
    return OandaOwnerRunLiveMicrotradeResultIntakeInput(
        owner_result=contract_input.owner_result,
        unsafe_flags=contract_input.unsafe_flags,
    )


def _coerce_input(
    value: OandaOwnerRunLiveMicrotradeResultIntakeInput | Mapping[str, Any],
) -> OandaOwnerRunLiveMicrotradeResultIntakeInput:
    if isinstance(value, OandaOwnerRunLiveMicrotradeResultIntakeInput):
        return value
    raw = dict(value)
    return OandaOwnerRunLiveMicrotradeResultIntakeInput(
        owner_result=_mapping_or_none(raw.get("owner_result")),
        unsafe_flags=dict(raw.get("unsafe_flags", {})),
    )


def _mapping_or_none(value: Any) -> Mapping[str, Any] | None:
    if value is None:
        return None
    return value if isinstance(value, Mapping) else {}


def _missing_fields(payload: Mapping[str, Any] | None) -> tuple[str, ...]:
    if payload is None:
        return REQUIRED_SANITIZED_RESULT_FIELDS
    missing: list[str] = []
    for field_name in REQUIRED_SANITIZED_RESULT_FIELDS:
        if field_name not in payload:
            missing.append(field_name)
            continue
        value = payload[field_name]
        if value is None or (isinstance(value, str) and not value.strip()):
            missing.append(field_name)
        elif isinstance(value, (tuple, list)) and not value:
            missing.append(field_name)
    return tuple(missing)


def _blocked_items(
    payload: Mapping[str, Any] | None,
    unsafe_flags: Mapping[str, bool],
) -> tuple[str, ...]:
    blocked = [name for name, value in unsafe_flags.items() if bool(value)]
    blocked.extend(unsafe_payload_blockers(payload, "intake_payload"))
    if payload:
        for flag_name in PROTECTED_FLAG_NAMES:
            if truthy_unsafe(payload.get(flag_name)):
                blocked.append(f"{flag_name}_true")
        if payload.get("owner_action_confirmed_outside_codex") is not True:
            blocked.append("owner_action_outside_codex_not_confirmed")
        if payload.get("one_shot_only_confirmed") is not True:
            blocked.append("one_shot_only_not_confirmed")
    return tuple(dict.fromkeys(blocked))


def _sanitize_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        field_name: payload[field_name]
        for field_name in ALLOWED_SANITIZED_RESULT_FIELDS
        if field_name in payload
    }

