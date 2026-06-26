"""Read-only post-trade evidence capture plan for owner-run microtrade results."""

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


VERSION = "oanda_supervised_live_microtrade_post_trade_capture_plan_v1"

OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_READY_FOR_OWNER_REVIEW = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_READY_FOR_OWNER_REVIEW"
)
OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_REQUIRE_REPAIR = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_REQUIRE_REPAIR"
)
OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_BLOCKED_UNSAFE = (
    "OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_BLOCKED_UNSAFE"
)

REQUIRED_CAPTURE_ITEMS = (
    "filled_trade_evidence_checklist",
    "realized_pl_capture_checklist",
    "spread_slippage_capture_checklist",
    "reconciliation_checklist",
    "screenshot_evidence_checklist",
    "journal_checklist",
    "route_live_result_back_to_evidence_ledger",
    "no_broker_call_from_codex",
)


@dataclass(frozen=True)
class OandaSupervisedLiveMicrotradePostTradeCapturePlanInput:
    capture_items: Mapping[str, bool]
    unsafe_flags: Mapping[str, bool] = field(default_factory=dict)


@dataclass(frozen=True)
class OandaSupervisedLiveMicrotradePostTradeCapturePlanResult:
    version: str
    classification: str
    capture_items: Mapping[str, bool]
    missing_items: tuple[str, ...]
    blocked_items: tuple[str, ...]
    post_trade_capture_preview: Mapping[str, Any]
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


def build_sample_ready_input() -> OandaSupervisedLiveMicrotradePostTradeCapturePlanInput:
    return OandaSupervisedLiveMicrotradePostTradeCapturePlanInput(
        capture_items={name: True for name in REQUIRED_CAPTURE_ITEMS}
    )


def build_sample_missing_input() -> OandaSupervisedLiveMicrotradePostTradeCapturePlanInput:
    capture_items = {name: True for name in REQUIRED_CAPTURE_ITEMS}
    capture_items["screenshot_evidence_checklist"] = False
    capture_items["journal_checklist"] = False
    return OandaSupervisedLiveMicrotradePostTradeCapturePlanInput(capture_items=capture_items)


def build_sample_unsafe_input() -> OandaSupervisedLiveMicrotradePostTradeCapturePlanInput:
    capture_items = {name: True for name in REQUIRED_CAPTURE_ITEMS}
    capture_items["no_broker_call_from_codex"] = False
    return OandaSupervisedLiveMicrotradePostTradeCapturePlanInput(
        capture_items=capture_items,
        unsafe_flags={"codex_broker_call_boundary_not_false": True},
    )


def build_oanda_supervised_live_microtrade_post_trade_capture_plan(
    capture_input: OandaSupervisedLiveMicrotradePostTradeCapturePlanInput | Mapping[str, Any] | None = None,
) -> OandaSupervisedLiveMicrotradePostTradeCapturePlanResult:
    active_input = _coerce_input(capture_input or build_sample_ready_input())
    missing_items = tuple(
        name for name in REQUIRED_CAPTURE_ITEMS if not bool(active_input.capture_items.get(name, False))
    )
    blocked_items = tuple(
        dict.fromkeys(name for name, value in active_input.unsafe_flags.items() if bool(value))
    )
    if blocked_items:
        classification = OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_BLOCKED_UNSAFE
    elif missing_items:
        classification = OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_REQUIRE_REPAIR
    else:
        classification = OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_READY_FOR_OWNER_REVIEW
    protected_flags = protected_flags_false()
    return OandaSupervisedLiveMicrotradePostTradeCapturePlanResult(
        version=VERSION,
        classification=classification,
        capture_items=dict(active_input.capture_items),
        missing_items=missing_items,
        blocked_items=blocked_items,
        post_trade_capture_preview={
            "preview_only": True,
            "read_only_after_owner_action": True,
            "required_capture_items": list(REQUIRED_CAPTURE_ITEMS),
            "broker_action_allowed": False,
        },
        owner_warning=EXACT_OWNER_WARNING,
        live_warning=EXACT_LIVE_WARNING,
        protected_flags=protected_flags,
        **protected_flags,
    )


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return jsonable(result)


def to_operator_text(result: OandaSupervisedLiveMicrotradePostTradeCapturePlanResult) -> str:
    return "\n".join(
        (
            f"Post-trade capture status: {result.classification}.",
            "Capture is read-only after Anthony acts outside Codex.",
            result.owner_warning,
            result.live_warning,
        )
    )


def to_markdown(result: OandaSupervisedLiveMicrotradePostTradeCapturePlanResult) -> str:
    rows = [
        "# AIOS Forex OANDA Supervised Live Microtrade Post-Trade Capture Plan V1",
        "",
        f"- Classification: `{result.classification}`",
        "",
        "## Capture Items",
    ]
    rows.extend(
        f"- `{name}`: `{str(bool(result.capture_items.get(name, False))).lower()}`"
        for name in REQUIRED_CAPTURE_ITEMS
    )
    rows.extend(markdown_safety_lines())
    return "\n".join(rows) + "\n"


def _coerce_input(
    value: OandaSupervisedLiveMicrotradePostTradeCapturePlanInput | Mapping[str, Any],
) -> OandaSupervisedLiveMicrotradePostTradeCapturePlanInput:
    if isinstance(value, OandaSupervisedLiveMicrotradePostTradeCapturePlanInput):
        return value
    raw = dict(value)
    return OandaSupervisedLiveMicrotradePostTradeCapturePlanInput(
        capture_items=dict(raw.get("capture_items", {})),
        unsafe_flags=dict(raw.get("unsafe_flags", {})),
    )

