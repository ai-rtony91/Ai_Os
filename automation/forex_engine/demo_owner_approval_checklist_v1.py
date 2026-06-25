from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal
from typing import Any, Mapping


DEMO_OWNER_APPROVAL_CHECKLIST_VERSION = "demo_owner_approval_checklist_v1"

OWNER_WARNING = "Do not execute unless Anthony explicitly approves."

DEMO_OWNER_APPROVAL_CHECKLIST_READY = "DEMO_OWNER_APPROVAL_CHECKLIST_READY"
DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_INCOMPLETE = (
    "DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_INCOMPLETE"
)
DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_RISK_NOT_ACKNOWLEDGED = (
    "DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_RISK_NOT_ACKNOWLEDGED"
)
DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_PROTECTED_ACTION_MISUNDERSTOOD = (
    "DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_PROTECTED_ACTION_MISUNDERSTOOD"
)

CHECKLIST_ITEM_NAMES = (
    "readiness_package_reviewed",
    "snapshot_reviewed",
    "candidate_reviewed",
    "risk_reviewed",
    "position_size_reviewed",
    "order_plan_reviewed",
    "operator_ticket_reviewed",
    "max_loss_understood",
    "post_trade_evidence_plan_understood",
    "feedback_routing_plan_understood",
    "no_broker_action_by_codex_understood",
    "no_real_money_understood",
    "no_compounding_understood",
    "no_bank_movement_understood",
    "explicit_owner_approval_required_understood",
)

PROTECTED_ACTION_ACKS = (
    "no_broker_action_by_codex_understood",
    "no_real_money_understood",
    "no_compounding_understood",
    "no_bank_movement_understood",
    "explicit_owner_approval_required_understood",
)


@dataclass(frozen=True)
class DemoOwnerApprovalChecklistConfig:
    owner_warning: str = OWNER_WARNING


@dataclass(frozen=True)
class DemoOwnerApprovalChecklistInput:
    readiness_package_reviewed: bool
    snapshot_reviewed: bool
    candidate_reviewed: bool
    risk_reviewed: bool
    position_size_reviewed: bool
    order_plan_reviewed: bool
    operator_ticket_reviewed: bool
    max_loss_understood: bool
    post_trade_evidence_plan_understood: bool
    feedback_routing_plan_understood: bool
    no_broker_action_by_codex_understood: bool
    no_real_money_understood: bool
    no_compounding_understood: bool
    no_bank_movement_understood: bool
    explicit_owner_approval_required_understood: bool
    config: DemoOwnerApprovalChecklistConfig = DemoOwnerApprovalChecklistConfig()


@dataclass(frozen=True)
class DemoOwnerApprovalChecklistResult:
    engine_version: str
    classification: str
    checklist_review_allowed: bool
    missing_items: tuple[str, ...]
    checklist_items: Mapping[str, bool]
    owner_warning: str
    next_safe_action: str
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool


def build_sample_ready_owner_approval_checklist_input() -> DemoOwnerApprovalChecklistInput:
    return DemoOwnerApprovalChecklistInput(**{name: True for name in CHECKLIST_ITEM_NAMES})


def build_sample_blocked_owner_approval_checklist_input() -> DemoOwnerApprovalChecklistInput:
    sample = build_sample_ready_owner_approval_checklist_input()
    return _replace_input(
        sample,
        readiness_package_reviewed=False,
        max_loss_understood=False,
    )


def evaluate_demo_owner_approval_checklist(
    checklist_input: DemoOwnerApprovalChecklistInput | Mapping[str, Any] | None = None,
) -> DemoOwnerApprovalChecklistResult:
    active = _coerce_input(checklist_input or build_sample_ready_owner_approval_checklist_input())
    checklist_items = _checklist_items(active)
    missing_items = tuple(name for name, value in checklist_items.items() if not value)
    classification = _classify(checklist_items)
    return DemoOwnerApprovalChecklistResult(
        engine_version=DEMO_OWNER_APPROVAL_CHECKLIST_VERSION,
        classification=classification,
        checklist_review_allowed=classification == DEMO_OWNER_APPROVAL_CHECKLIST_READY,
        missing_items=missing_items,
        checklist_items=checklist_items,
        owner_warning=active.config.owner_warning,
        next_safe_action=_next_safe_action(classification),
        **_permission_defaults(),
    )


def demo_owner_approval_checklist_to_jsonable_dict(
    result: DemoOwnerApprovalChecklistResult,
) -> dict[str, Any]:
    return _json_value(result)


def demo_owner_approval_checklist_to_operator_text(
    result: DemoOwnerApprovalChecklistResult | None = None,
) -> str:
    active = result or evaluate_demo_owner_approval_checklist()
    if active.checklist_review_allowed:
        return "Owner approval checklist is ready for manual review. No trade was placed."
    return f"Owner approval checklist is blocked: {', '.join(active.missing_items)}. No trade was placed."


def demo_owner_approval_checklist_to_markdown(
    result: DemoOwnerApprovalChecklistResult | None = None,
) -> str:
    active = result or evaluate_demo_owner_approval_checklist()
    lines = [
        "# Demo Owner Approval Checklist V1",
        "",
        active.owner_warning,
        "",
        "No broker call was made. No trade was placed.",
        "",
        f"- Status: {active.classification}",
        f"- Checklist review allowed: {active.checklist_review_allowed}",
        "",
        "## Checklist Items",
    ]
    lines.extend(f"- {name}: {value}" for name, value in active.checklist_items.items())
    lines.extend(
        [
            "",
            "## Missing Items",
            *(f"- {item}" for item in active.missing_items),
            "",
            f"Next safe action: {active.next_safe_action}",
        ]
    )
    return "\n".join(lines)


def _classify(checklist_items: Mapping[str, bool]) -> str:
    if all(checklist_items.values()):
        return DEMO_OWNER_APPROVAL_CHECKLIST_READY
    if not checklist_items["max_loss_understood"] or not checklist_items["risk_reviewed"]:
        return DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_RISK_NOT_ACKNOWLEDGED
    if any(not checklist_items[name] for name in PROTECTED_ACTION_ACKS):
        return DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_PROTECTED_ACTION_MISUNDERSTOOD
    return DEMO_OWNER_APPROVAL_CHECKLIST_BLOCKED_INCOMPLETE


def _next_safe_action(classification: str) -> str:
    if classification == DEMO_OWNER_APPROVAL_CHECKLIST_READY:
        return "Continue local owner packet review; protected permissions remain false."
    return "Complete every owner checklist item before treating the packet as review-ready."


def _checklist_items(value: DemoOwnerApprovalChecklistInput) -> dict[str, bool]:
    return {name: bool(getattr(value, name)) for name in CHECKLIST_ITEM_NAMES}


def _replace_input(
    value: DemoOwnerApprovalChecklistInput,
    **updates: Any,
) -> DemoOwnerApprovalChecklistInput:
    raw = {field.name: getattr(value, field.name) for field in fields(value)}
    raw.update(updates)
    return DemoOwnerApprovalChecklistInput(**raw)


def _coerce_input(
    value: DemoOwnerApprovalChecklistInput | Mapping[str, Any],
) -> DemoOwnerApprovalChecklistInput:
    if isinstance(value, DemoOwnerApprovalChecklistInput):
        return value
    raw = dict(value)
    config = raw.get("config", DemoOwnerApprovalChecklistConfig())
    if not isinstance(config, DemoOwnerApprovalChecklistConfig):
        config = DemoOwnerApprovalChecklistConfig(**dict(config))
    data = {name: bool(raw.get(name, False)) for name in CHECKLIST_ITEM_NAMES}
    data["config"] = config
    return DemoOwnerApprovalChecklistInput(**data)


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
