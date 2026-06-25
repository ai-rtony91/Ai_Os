from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal
from typing import Any, Mapping


DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_VERSION = (
    "demo_manual_execution_exception_checklist_v1"
)

OWNER_WARNING = "Do not execute unless Anthony explicitly approves."
EXCEPTION_WARNING = (
    "Manual exception review only. Codex is not authorized to execute, call a broker, "
    "access credentials, or place orders."
)

DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_READY = (
    "DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_READY"
)
DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_INCOMPLETE = (
    "DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_INCOMPLETE"
)
DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_RISK_NOT_ACKNOWLEDGED = (
    "DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_RISK_NOT_ACKNOWLEDGED"
)
DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_PROTECTED_ACTION_MISUNDERSTOOD = (
    "DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_PROTECTED_ACTION_MISUNDERSTOOD"
)
DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_EVIDENCE_PLAN_MISSING = (
    "DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_EVIDENCE_PLAN_MISSING"
)

CHECKLIST_ITEM_NAMES = (
    "owner_approval_packet_reviewed",
    "readiness_package_reviewed",
    "strategy_and_candidate_reviewed",
    "instrument_direction_reviewed",
    "entry_stop_target_reviewed",
    "position_size_reviewed",
    "max_loss_reviewed",
    "reward_to_risk_reviewed",
    "spread_market_hours_reviewed",
    "duplicate_order_guard_understood",
    "kill_switch_understood",
    "manual_execution_only_understood",
    "codex_no_execution_understood",
    "codex_no_broker_call_understood",
    "codex_no_credentials_understood",
    "demo_only_understood",
    "no_real_money_understood",
    "no_compounding_understood",
    "no_bank_movement_understood",
    "post_trade_evidence_required_understood",
    "feedback_routing_required_understood",
    "loss_possible_understood",
)

RISK_ACKS = (
    "max_loss_reviewed",
    "reward_to_risk_reviewed",
    "spread_market_hours_reviewed",
    "duplicate_order_guard_understood",
    "kill_switch_understood",
    "loss_possible_understood",
)
PROTECTED_ACTION_ACKS = (
    "manual_execution_only_understood",
    "codex_no_execution_understood",
    "codex_no_broker_call_understood",
    "codex_no_credentials_understood",
    "demo_only_understood",
    "no_real_money_understood",
    "no_compounding_understood",
    "no_bank_movement_understood",
)
EVIDENCE_ACKS = (
    "post_trade_evidence_required_understood",
    "feedback_routing_required_understood",
)


@dataclass(frozen=True)
class DemoManualExecutionExceptionChecklistConfig:
    owner_warning: str = OWNER_WARNING
    exception_warning: str = EXCEPTION_WARNING


@dataclass(frozen=True)
class DemoManualExecutionExceptionChecklistInput:
    owner_approval_packet_reviewed: bool
    readiness_package_reviewed: bool
    strategy_and_candidate_reviewed: bool
    instrument_direction_reviewed: bool
    entry_stop_target_reviewed: bool
    position_size_reviewed: bool
    max_loss_reviewed: bool
    reward_to_risk_reviewed: bool
    spread_market_hours_reviewed: bool
    duplicate_order_guard_understood: bool
    kill_switch_understood: bool
    manual_execution_only_understood: bool
    codex_no_execution_understood: bool
    codex_no_broker_call_understood: bool
    codex_no_credentials_understood: bool
    demo_only_understood: bool
    no_real_money_understood: bool
    no_compounding_understood: bool
    no_bank_movement_understood: bool
    post_trade_evidence_required_understood: bool
    feedback_routing_required_understood: bool
    loss_possible_understood: bool
    config: DemoManualExecutionExceptionChecklistConfig = DemoManualExecutionExceptionChecklistConfig()


@dataclass(frozen=True)
class DemoManualExecutionExceptionChecklistResult:
    engine_version: str
    classification: str
    checklist_review_allowed: bool
    missing_items: tuple[str, ...]
    checklist_items: Mapping[str, bool]
    owner_warning: str
    exception_warning: str
    next_safe_action: str
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool


def build_sample_ready_manual_execution_exception_checklist_input() -> DemoManualExecutionExceptionChecklistInput:
    return DemoManualExecutionExceptionChecklistInput(**{name: True for name in CHECKLIST_ITEM_NAMES})


def build_sample_blocked_manual_execution_exception_checklist_input() -> DemoManualExecutionExceptionChecklistInput:
    sample = build_sample_ready_manual_execution_exception_checklist_input()
    return _replace_input(
        sample,
        owner_approval_packet_reviewed=False,
        max_loss_reviewed=False,
    )


def evaluate_demo_manual_execution_exception_checklist(
    checklist_input: DemoManualExecutionExceptionChecklistInput | Mapping[str, Any] | None = None,
) -> DemoManualExecutionExceptionChecklistResult:
    active = _coerce_input(checklist_input or build_sample_ready_manual_execution_exception_checklist_input())
    checklist_items = _checklist_items(active)
    missing_items = tuple(name for name, value in checklist_items.items() if not value)
    classification = _classify(checklist_items)
    return DemoManualExecutionExceptionChecklistResult(
        engine_version=DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_VERSION,
        classification=classification,
        checklist_review_allowed=classification == DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_READY,
        missing_items=missing_items,
        checklist_items=checklist_items,
        owner_warning=active.config.owner_warning,
        exception_warning=active.config.exception_warning,
        next_safe_action=_next_safe_action(classification),
        **_permission_defaults(),
    )


def demo_manual_execution_exception_checklist_to_jsonable_dict(
    result: DemoManualExecutionExceptionChecklistResult,
) -> dict[str, Any]:
    return _json_value(result)


def demo_manual_execution_exception_checklist_to_operator_text(
    result: DemoManualExecutionExceptionChecklistResult | None = None,
) -> str:
    active = result or evaluate_demo_manual_execution_exception_checklist()
    if active.checklist_review_allowed:
        return "Manual execution exception checklist is ready for owner review. No trade was placed."
    return f"Manual execution exception checklist is blocked: {', '.join(active.missing_items)}. No trade was placed."


def demo_manual_execution_exception_checklist_to_markdown(
    result: DemoManualExecutionExceptionChecklistResult | None = None,
) -> str:
    active = result or evaluate_demo_manual_execution_exception_checklist()
    lines = [
        "# Demo Manual Execution Exception Checklist V1",
        "",
        active.owner_warning,
        active.exception_warning,
        "",
        "No broker call was made. No trade was placed.",
        "",
        f"- Status: {active.classification}",
        f"- Checklist review allowed: {active.checklist_review_allowed}",
        "",
        "## Checklist Items",
    ]
    lines.extend(f"- {name}: {value}" for name, value in active.checklist_items.items())
    lines.extend(["", "## Missing Items"])
    lines.extend(f"- {item}" for item in active.missing_items)
    lines.extend(["", f"Next safe action: {active.next_safe_action}"])
    return "\n".join(lines)


def _classify(checklist_items: Mapping[str, bool]) -> str:
    if all(checklist_items.values()):
        return DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_READY
    if any(not checklist_items[name] for name in RISK_ACKS):
        return DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_RISK_NOT_ACKNOWLEDGED
    if any(not checklist_items[name] for name in PROTECTED_ACTION_ACKS):
        return DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_PROTECTED_ACTION_MISUNDERSTOOD
    if any(not checklist_items[name] for name in EVIDENCE_ACKS):
        return DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_EVIDENCE_PLAN_MISSING
    return DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_BLOCKED_INCOMPLETE


def _next_safe_action(classification: str) -> str:
    if classification == DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_READY:
        return "Continue local manual exception packet review; all protected permissions remain false."
    return "Complete every manual exception checklist item before owner review."


def _checklist_items(value: DemoManualExecutionExceptionChecklistInput) -> dict[str, bool]:
    return {name: bool(getattr(value, name)) for name in CHECKLIST_ITEM_NAMES}


def _replace_input(
    value: DemoManualExecutionExceptionChecklistInput,
    **updates: Any,
) -> DemoManualExecutionExceptionChecklistInput:
    raw = {field.name: getattr(value, field.name) for field in fields(value)}
    raw.update(updates)
    return DemoManualExecutionExceptionChecklistInput(**raw)


def _coerce_input(
    value: DemoManualExecutionExceptionChecklistInput | Mapping[str, Any],
) -> DemoManualExecutionExceptionChecklistInput:
    if isinstance(value, DemoManualExecutionExceptionChecklistInput):
        return value
    raw = dict(value)
    config = raw.get("config", DemoManualExecutionExceptionChecklistConfig())
    if not isinstance(config, DemoManualExecutionExceptionChecklistConfig):
        config = DemoManualExecutionExceptionChecklistConfig(**dict(config))
    data = {name: bool(raw.get(name, False)) for name in CHECKLIST_ITEM_NAMES}
    data["config"] = config
    return DemoManualExecutionExceptionChecklistInput(**data)


def _permission_defaults() -> dict[str, bool]:
    return {
        "demo_execution_allowed": False,
        "broker_action_allowed": False,
        "real_money_allowed": False,
        "compounding_allowed": False,
        "bank_movement_allowed": False,
        "live_trading_allowed": False,
        "credential_access_allowed": False,
        "account_id_persistence_allowed": False,
    }


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if is_dataclass(value):
        return {field.name: _json_value(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    return value
