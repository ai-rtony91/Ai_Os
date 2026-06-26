"""Explicit compounding permission blocker for vacation profit readiness."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from automation.forex_engine.oanda_vacation_profit_readiness_contract_v1 import (
    EXACT_OWNER_WARNING,
    EXACT_VACATION_WARNING,
    protected_flags_false,
)


VERSION = "oanda_vacation_profit_compounding_permission_gate_v1"

OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_BLOCKED_BY_DEFAULT = (
    "OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_BLOCKED_BY_DEFAULT"
)
OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_READY_FOR_FUTURE_OWNER_REVIEW = (
    "OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_READY_FOR_FUTURE_OWNER_REVIEW"
)
OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_BLOCKED_UNSAFE = (
    "OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_BLOCKED_UNSAFE"
)


@dataclass(frozen=True)
class OandaVacationProfitCompoundingPermissionGateInput:
    future_owner_review_ready: bool
    no_compounding_by_default: bool = True
    no_reinvestment_by_default: bool = True
    no_balance_scaling_by_default: bool = True
    no_increased_risk_after_wins: bool = True
    no_bank_movement: bool = True
    no_withdrawal_automation: bool = True
    no_deposit_automation: bool = True
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class OandaVacationProfitCompoundingPermissionGateResult:
    version: str
    classification: str
    future_owner_review_ready: bool
    no_compounding_by_default: bool
    no_reinvestment_by_default: bool
    no_balance_scaling_by_default: bool
    no_increased_risk_after_wins: bool
    no_bank_movement: bool
    no_withdrawal_automation: bool
    no_deposit_automation: bool
    compounding_permission_approved: bool
    owner_review_only: bool
    blocked_items: tuple[str, ...]
    owner_warning: str
    vacation_warning: str
    protected_flags: Mapping[str, bool]
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
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


def build_sample_ready_for_review_input() -> OandaVacationProfitCompoundingPermissionGateInput:
    return OandaVacationProfitCompoundingPermissionGateInput(
        future_owner_review_ready=True
    )


def build_sample_no_live_sample_input() -> OandaVacationProfitCompoundingPermissionGateInput:
    return build_sample_ready_for_review_input()


def build_sample_missing_autonomy_controls_input() -> OandaVacationProfitCompoundingPermissionGateInput:
    return build_sample_ready_for_review_input()


def build_sample_compounding_blocked_input() -> OandaVacationProfitCompoundingPermissionGateInput:
    return OandaVacationProfitCompoundingPermissionGateInput(
        future_owner_review_ready=False
    )


def build_sample_unsafe_input() -> OandaVacationProfitCompoundingPermissionGateInput:
    return OandaVacationProfitCompoundingPermissionGateInput(
        future_owner_review_ready=True,
        unsafe_flags={"compounding_permission_unsafe": True},
    )


def evaluate_oanda_vacation_profit_compounding_permission_gate(
    gate_input: OandaVacationProfitCompoundingPermissionGateInput | Mapping[str, Any] | None = None,
) -> OandaVacationProfitCompoundingPermissionGateResult:
    active_input = _coerce_input(gate_input or build_sample_ready_for_review_input())
    blocked_items = _blocked_items(active_input)
    if blocked_items:
        classification = OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_BLOCKED_UNSAFE
    elif active_input.future_owner_review_ready:
        classification = (
            OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_READY_FOR_FUTURE_OWNER_REVIEW
        )
    else:
        classification = OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_BLOCKED_BY_DEFAULT
    protected_flags = protected_flags_false()
    return OandaVacationProfitCompoundingPermissionGateResult(
        version=VERSION,
        classification=classification,
        future_owner_review_ready=active_input.future_owner_review_ready,
        no_compounding_by_default=active_input.no_compounding_by_default,
        no_reinvestment_by_default=active_input.no_reinvestment_by_default,
        no_balance_scaling_by_default=active_input.no_balance_scaling_by_default,
        no_increased_risk_after_wins=active_input.no_increased_risk_after_wins,
        no_bank_movement=active_input.no_bank_movement,
        no_withdrawal_automation=active_input.no_withdrawal_automation,
        no_deposit_automation=active_input.no_deposit_automation,
        compounding_permission_approved=False,
        owner_review_only=True,
        blocked_items=blocked_items,
        owner_warning=EXACT_OWNER_WARNING,
        vacation_warning=EXACT_VACATION_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return _jsonable(result)


def to_operator_text(
    result: OandaVacationProfitCompoundingPermissionGateResult,
) -> str:
    return "\n".join(
        (
            f"Vacation profit compounding permission status: {result.classification}.",
            "Compounding is blocked by default.",
            "Future owner review is not compounding approval.",
            result.owner_warning,
            result.vacation_warning,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
        )
    )


def to_markdown(result: OandaVacationProfitCompoundingPermissionGateResult) -> str:
    rows = [
        "# AIOS Forex OANDA Vacation Profit Compounding Permission Gate V1",
        "",
        f"- Classification: `{result.classification}`",
        "- No compounding by default.",
        "- No reinvestment by default.",
        "- No balance scaling by default.",
        "- No increased risk after wins.",
        "- No bank movement.",
        "- No withdrawal automation.",
        "- No deposit automation.",
        "- Compounding permission approved: `false`",
        "- Owner review only.",
        "",
        "## Safety",
        "- No trade placed by this packet.",
        "- No broker call was made by this packet.",
        "- No live approval was granted.",
        "- No real money approval was granted.",
        "- No compounding approval was granted.",
        "- No bank movement approval was granted.",
        "- No autonomous execution was granted.",
        "- Unattended vacation mode remains blocked.",
        "- Profit is not guaranteed.",
        "- All protected flags remain false.",
    ]
    return "\n".join(rows) + "\n"


def _coerce_input(
    value: OandaVacationProfitCompoundingPermissionGateInput | Mapping[str, Any],
) -> OandaVacationProfitCompoundingPermissionGateInput:
    if isinstance(value, OandaVacationProfitCompoundingPermissionGateInput):
        return value
    raw = dict(value)
    return OandaVacationProfitCompoundingPermissionGateInput(
        future_owner_review_ready=bool(raw.get("future_owner_review_ready", False)),
        no_compounding_by_default=bool(raw.get("no_compounding_by_default", True)),
        no_reinvestment_by_default=bool(raw.get("no_reinvestment_by_default", True)),
        no_balance_scaling_by_default=bool(
            raw.get("no_balance_scaling_by_default", True)
        ),
        no_increased_risk_after_wins=bool(
            raw.get("no_increased_risk_after_wins", True)
        ),
        no_bank_movement=bool(raw.get("no_bank_movement", True)),
        no_withdrawal_automation=bool(raw.get("no_withdrawal_automation", True)),
        no_deposit_automation=bool(raw.get("no_deposit_automation", True)),
        unsafe_flags=dict(raw.get("unsafe_flags", {})),
    )


def _blocked_items(
    active_input: OandaVacationProfitCompoundingPermissionGateInput,
) -> tuple[str, ...]:
    blocked: list[str] = []
    if any(bool(value) for value in active_input.unsafe_flags.values()):
        blocked.append("unsafe_compounding_permission_flag")
    safety_fields = {
        "no_compounding_by_default": active_input.no_compounding_by_default,
        "no_reinvestment_by_default": active_input.no_reinvestment_by_default,
        "no_balance_scaling_by_default": active_input.no_balance_scaling_by_default,
        "no_increased_risk_after_wins": active_input.no_increased_risk_after_wins,
        "no_bank_movement": active_input.no_bank_movement,
        "no_withdrawal_automation": active_input.no_withdrawal_automation,
        "no_deposit_automation": active_input.no_deposit_automation,
    }
    blocked.extend(name for name, enabled in safety_fields.items() if not enabled)
    return tuple(blocked)


def _jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value

