"""Final disarm, abort, rollback, and recovery checklist preview."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping

from automation.forex_engine.oanda_supervised_live_microtrade_final_gate_v1 import (
    EXACT_LIVE_WARNING,
    EXACT_OWNER_WARNING,
    jsonable,
    markdown_safety_lines,
    protected_flags_false,
)


VERSION = "oanda_supervised_live_microtrade_disarm_recovery_v1"

OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_READY_FOR_OWNER_REVIEW = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_READY_FOR_OWNER_REVIEW"
)
OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_REQUIRE_REPAIR = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_REQUIRE_REPAIR"
)
OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_BLOCKED_UNSAFE = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_BLOCKED_UNSAFE"
)

REQUIRED_CHECKLIST_ITEMS = (
    "abort_before_execution",
    "abort_on_timeout",
    "abort_on_unexpected_spread",
    "abort_on_market_closed",
    "abort_on_duplicate_order_risk",
    "abort_if_account_boundary_unclear",
    "abort_if_credential_boundary_unclear",
    "immediate_post_trade_disarm",
    "post_trade_reconciliation",
    "post_trade_journal",
    "no_repeat_execution",
    "kill_switch",
    "rollback_plan",
    "final_disarm",
    "duplicate_guard",
)


@dataclass(frozen=True)
class OandaSupervisedLiveMicrotradeDisarmRecoveryInput:
    checklist: Mapping[str, bool]
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class OandaSupervisedLiveMicrotradeDisarmRecoveryResult:
    version: str
    classification: str
    checklist: Mapping[str, bool]
    missing_items: tuple[str, ...]
    blocked_items: tuple[str, ...]
    recovery_preview: Mapping[str, Any]
    owner_warning: str
    live_warning: str
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


def build_sample_ready_input() -> OandaSupervisedLiveMicrotradeDisarmRecoveryInput:
    return OandaSupervisedLiveMicrotradeDisarmRecoveryInput(
        checklist={name: True for name in REQUIRED_CHECKLIST_ITEMS}
    )


def build_sample_missing_input() -> OandaSupervisedLiveMicrotradeDisarmRecoveryInput:
    checklist = {name: True for name in REQUIRED_CHECKLIST_ITEMS}
    checklist["rollback_plan"] = False
    checklist["post_trade_journal"] = False
    return OandaSupervisedLiveMicrotradeDisarmRecoveryInput(checklist=checklist)


def build_sample_unsafe_input() -> OandaSupervisedLiveMicrotradeDisarmRecoveryInput:
    checklist = {name: True for name in REQUIRED_CHECKLIST_ITEMS}
    checklist["no_repeat_execution"] = False
    return OandaSupervisedLiveMicrotradeDisarmRecoveryInput(
        checklist=checklist,
        unsafe_flags={"repeat_execution_risk": True},
    )


def build_oanda_supervised_live_microtrade_disarm_recovery(
    recovery_input: OandaSupervisedLiveMicrotradeDisarmRecoveryInput | Mapping[str, Any] | None = None,
) -> OandaSupervisedLiveMicrotradeDisarmRecoveryResult:
    active_input = _coerce_input(recovery_input or build_sample_ready_input())
    missing_items = tuple(
        name for name in REQUIRED_CHECKLIST_ITEMS if not bool(active_input.checklist.get(name, False))
    )
    blocked_items = tuple(
        dict.fromkeys(name for name, value in active_input.unsafe_flags.items() if bool(value))
    )
    if blocked_items:
        classification = OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_BLOCKED_UNSAFE
    elif missing_items:
        classification = OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_REQUIRE_REPAIR
    else:
        classification = OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_READY_FOR_OWNER_REVIEW
    protected_flags = protected_flags_false()
    return OandaSupervisedLiveMicrotradeDisarmRecoveryResult(
        version=VERSION,
        classification=classification,
        checklist=dict(active_input.checklist),
        missing_items=missing_items,
        blocked_items=blocked_items,
        recovery_preview={
            "preview_only": True,
            "required_checklist_items": list(REQUIRED_CHECKLIST_ITEMS),
            "no_repeat_execution": bool(active_input.checklist.get("no_repeat_execution", False)),
            "broker_action_allowed": False,
        },
        owner_warning=EXACT_OWNER_WARNING,
        live_warning=EXACT_LIVE_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return jsonable(result)


def to_operator_text(result: OandaSupervisedLiveMicrotradeDisarmRecoveryResult) -> str:
    return "\n".join(
        (
            f"Disarm recovery status: {result.classification}.",
            "Abort, rollback, kill-switch, disarm, and no-repeat checks are preview-only.",
            result.owner_warning,
            result.live_warning,
        )
    )


def to_markdown(result: OandaSupervisedLiveMicrotradeDisarmRecoveryResult) -> str:
    rows = [
        "# AIOS Forex OANDA Supervised Live Microtrade Disarm Recovery V1",
        "",
        f"- Classification: `{result.classification}`",
        "",
        "## Checklist",
    ]
    rows.extend(
        f"- `{name}`: `{str(bool(result.checklist.get(name, False))).lower()}`"
        for name in REQUIRED_CHECKLIST_ITEMS
    )
    rows.extend(markdown_safety_lines())
    return "\n".join(rows) + "\n"


def _coerce_input(
    value: OandaSupervisedLiveMicrotradeDisarmRecoveryInput | Mapping[str, Any],
) -> OandaSupervisedLiveMicrotradeDisarmRecoveryInput:
    if isinstance(value, OandaSupervisedLiveMicrotradeDisarmRecoveryInput):
        return value
    raw = dict(value)
    return OandaSupervisedLiveMicrotradeDisarmRecoveryInput(
        checklist=dict(raw.get("checklist", {})),
        unsafe_flags=dict(raw.get("unsafe_flags", {})),
    )

