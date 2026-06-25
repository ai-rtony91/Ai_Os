from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal
from typing import Any, Mapping


DEMO_OWNER_APPROVAL_PHRASE_GATE_VERSION = "demo_owner_approval_phrase_gate_v1"

OWNER_WARNING = "Do not execute unless Anthony explicitly approves."
REQUIRED_OWNER_APPROVAL_PHRASE = (
    "I, Anthony, approve this supervised demo trade review packet for manual owner review only. "
    "I understand no broker action is authorized by Codex."
)

DEMO_OWNER_APPROVAL_PHRASE_VALID_FOR_MANUAL_REVIEW = (
    "DEMO_OWNER_APPROVAL_PHRASE_VALID_FOR_MANUAL_REVIEW"
)
DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_MISSING = "DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_MISSING"
DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_NOT_EXACT = "DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_NOT_EXACT"
DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_EXECUTION_SCOPE = (
    "DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_EXECUTION_SCOPE"
)
DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_REAL_MONEY_SCOPE = (
    "DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_REAL_MONEY_SCOPE"
)
DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_BROKER_ACTION_SCOPE = (
    "DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_BROKER_ACTION_SCOPE"
)


@dataclass(frozen=True)
class DemoOwnerApprovalPhraseGateConfig:
    required_phrase: str = REQUIRED_OWNER_APPROVAL_PHRASE
    owner_warning: str = OWNER_WARNING


@dataclass(frozen=True)
class DemoOwnerApprovalPhraseGateInput:
    approval_phrase: str
    config: DemoOwnerApprovalPhraseGateConfig = DemoOwnerApprovalPhraseGateConfig()


@dataclass(frozen=True)
class DemoOwnerApprovalPhraseGateResult:
    engine_version: str
    classification: str
    approval_phrase_review_allowed: bool
    approval_phrase: str
    required_phrase: str
    owner_warning: str
    blockers: tuple[str, ...]
    next_safe_action: str
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool


def build_sample_valid_owner_approval_phrase_input() -> DemoOwnerApprovalPhraseGateInput:
    return DemoOwnerApprovalPhraseGateInput(approval_phrase=REQUIRED_OWNER_APPROVAL_PHRASE)


def build_sample_missing_owner_approval_phrase_input() -> DemoOwnerApprovalPhraseGateInput:
    return DemoOwnerApprovalPhraseGateInput(approval_phrase="")


def build_sample_wrong_scope_owner_approval_phrase_input() -> DemoOwnerApprovalPhraseGateInput:
    return DemoOwnerApprovalPhraseGateInput(
        approval_phrase="I approve Codex to execute the demo trade now."
    )


def evaluate_demo_owner_approval_phrase_gate(
    phrase_input: DemoOwnerApprovalPhraseGateInput | Mapping[str, Any] | None = None,
) -> DemoOwnerApprovalPhraseGateResult:
    active = _coerce_input(phrase_input or build_sample_valid_owner_approval_phrase_input())
    classification = _classify(active)
    return DemoOwnerApprovalPhraseGateResult(
        engine_version=DEMO_OWNER_APPROVAL_PHRASE_GATE_VERSION,
        classification=classification,
        approval_phrase_review_allowed=classification
        == DEMO_OWNER_APPROVAL_PHRASE_VALID_FOR_MANUAL_REVIEW,
        approval_phrase=active.approval_phrase,
        required_phrase=active.config.required_phrase,
        owner_warning=active.config.owner_warning,
        blockers=tuple([] if classification == DEMO_OWNER_APPROVAL_PHRASE_VALID_FOR_MANUAL_REVIEW else [_blocker(classification)]),
        next_safe_action=_next_safe_action(classification),
        **_permission_defaults(),
    )


def demo_owner_approval_phrase_gate_to_jsonable_dict(
    result: DemoOwnerApprovalPhraseGateResult,
) -> dict[str, Any]:
    return _json_value(result)


def demo_owner_approval_phrase_gate_to_operator_text(
    result: DemoOwnerApprovalPhraseGateResult | None = None,
) -> str:
    active = result or evaluate_demo_owner_approval_phrase_gate()
    if active.approval_phrase_review_allowed:
        return (
            "Owner approval phrase is valid for manual review only. "
            "Broker action and demo execution remain false. No trade was placed."
        )
    return (
        f"Owner approval phrase is blocked: {'; '.join(active.blockers)}. "
        "No broker action is authorized and no trade was placed."
    )


def demo_owner_approval_phrase_gate_to_markdown(
    result: DemoOwnerApprovalPhraseGateResult | None = None,
) -> str:
    active = result or evaluate_demo_owner_approval_phrase_gate()
    return "\n".join(
        [
            "# Demo Owner Approval Phrase Gate V1",
            "",
            active.owner_warning,
            "",
            "No broker call was made. No trade was placed.",
            "",
            f"- Status: {active.classification}",
            f"- Approval phrase review allowed: {active.approval_phrase_review_allowed}",
            f"- Required phrase: {active.required_phrase}",
            f"- Demo execution allowed: {active.demo_execution_allowed}",
            f"- Broker action allowed: {active.broker_action_allowed}",
            f"- Next safe action: {active.next_safe_action}",
        ]
    )


def _classify(value: DemoOwnerApprovalPhraseGateInput) -> str:
    phrase = value.approval_phrase.strip()
    if not phrase:
        return DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_MISSING
    if phrase == value.config.required_phrase:
        return DEMO_OWNER_APPROVAL_PHRASE_VALID_FOR_MANUAL_REVIEW
    phrase_lower = phrase.lower()
    if any(term in phrase_lower for term in ("real money", "live money", "funded account")):
        return DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_REAL_MONEY_SCOPE
    if any(term in phrase_lower for term in ("broker action authorized", "authorize broker", "broker may")):
        return DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_BROKER_ACTION_SCOPE
    if any(term in phrase_lower for term in ("execute", "place trade", "submit trade", "send order")):
        return DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_EXECUTION_SCOPE
    return DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_NOT_EXACT


def _blocker(classification: str) -> str:
    if classification == DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_MISSING:
        return "approval phrase is missing"
    if classification == DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_EXECUTION_SCOPE:
        return "approval phrase attempts to approve execution"
    if classification == DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_REAL_MONEY_SCOPE:
        return "approval phrase attempts to approve real money scope"
    if classification == DEMO_OWNER_APPROVAL_PHRASE_BLOCKED_BROKER_ACTION_SCOPE:
        return "approval phrase attempts to approve broker action"
    return "approval phrase does not exactly match the manual-review-only requirement"


def _next_safe_action(classification: str) -> str:
    if classification == DEMO_OWNER_APPROVAL_PHRASE_VALID_FOR_MANUAL_REVIEW:
        return "Continue local owner review; broker action and execution remain locked."
    return "Use the exact manual-review-only phrase or keep the owner approval packet blocked."


def _coerce_input(
    value: DemoOwnerApprovalPhraseGateInput | Mapping[str, Any],
) -> DemoOwnerApprovalPhraseGateInput:
    if isinstance(value, DemoOwnerApprovalPhraseGateInput):
        return value
    raw = dict(value)
    config = raw.get("config", DemoOwnerApprovalPhraseGateConfig())
    if not isinstance(config, DemoOwnerApprovalPhraseGateConfig):
        config = DemoOwnerApprovalPhraseGateConfig(**dict(config))
    return DemoOwnerApprovalPhraseGateInput(
        approval_phrase=str(raw.get("approval_phrase", "")),
        config=config,
    )


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
