from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal
from typing import Any, Mapping


DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_GATE_VERSION = (
    "demo_manual_execution_exception_scope_gate_v1"
)

OWNER_WARNING = "Do not execute unless Anthony explicitly approves."
EXCEPTION_WARNING = (
    "Manual exception review only. Codex is not authorized to execute, call a broker, "
    "access credentials, or place orders."
)
REQUIRED_EXCEPTION_PHRASE = (
    "I, Anthony, request manual review of this supervised demo execution exception packet only. "
    "I understand Codex is not authorized to execute, call a broker, or place orders."
)

DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_VALID_FOR_REVIEW = (
    "DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_VALID_FOR_REVIEW"
)
DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_MISSING = (
    "DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_MISSING"
)
DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_CODEX_EXECUTION_AUTHORITY = (
    "DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_CODEX_EXECUTION_AUTHORITY"
)
DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_BROKER_ACTION_AUTHORITY = (
    "DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_BROKER_ACTION_AUTHORITY"
)
DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_REAL_MONEY_SCOPE = (
    "DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_REAL_MONEY_SCOPE"
)
DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_CREDENTIAL_SCOPE = (
    "DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_CREDENTIAL_SCOPE"
)
DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_LIVE_SCOPE = (
    "DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_LIVE_SCOPE"
)


@dataclass(frozen=True)
class DemoManualExecutionExceptionScopeConfig:
    required_phrase: str = REQUIRED_EXCEPTION_PHRASE
    owner_warning: str = OWNER_WARNING
    exception_warning: str = EXCEPTION_WARNING


@dataclass(frozen=True)
class DemoManualExecutionExceptionScopeInput:
    exception_phrase: str
    config: DemoManualExecutionExceptionScopeConfig = DemoManualExecutionExceptionScopeConfig()


@dataclass(frozen=True)
class DemoManualExecutionExceptionScopeResult:
    engine_version: str
    classification: str
    scope_review_allowed: bool
    exception_phrase: str
    required_phrase: str
    owner_warning: str
    exception_warning: str
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


def build_sample_valid_manual_execution_exception_scope_input() -> DemoManualExecutionExceptionScopeInput:
    return DemoManualExecutionExceptionScopeInput(exception_phrase=REQUIRED_EXCEPTION_PHRASE)


def build_sample_missing_manual_execution_exception_scope_input() -> DemoManualExecutionExceptionScopeInput:
    return DemoManualExecutionExceptionScopeInput(exception_phrase="")


def build_sample_execution_authority_blocked_input() -> DemoManualExecutionExceptionScopeInput:
    return DemoManualExecutionExceptionScopeInput(
        exception_phrase="I authorize Codex to execute this supervised demo trade."
    )


def build_sample_real_money_scope_blocked_input() -> DemoManualExecutionExceptionScopeInput:
    return DemoManualExecutionExceptionScopeInput(
        exception_phrase="I request this exception for real money compounding."
    )


def evaluate_demo_manual_execution_exception_scope(
    scope_input: DemoManualExecutionExceptionScopeInput | Mapping[str, Any] | None = None,
) -> DemoManualExecutionExceptionScopeResult:
    active = _coerce_input(scope_input or build_sample_valid_manual_execution_exception_scope_input())
    classification = _classify(active)
    return DemoManualExecutionExceptionScopeResult(
        engine_version=DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_GATE_VERSION,
        classification=classification,
        scope_review_allowed=classification
        == DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_VALID_FOR_REVIEW,
        exception_phrase=active.exception_phrase,
        required_phrase=active.config.required_phrase,
        owner_warning=active.config.owner_warning,
        exception_warning=active.config.exception_warning,
        blockers=tuple(
            []
            if classification == DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_VALID_FOR_REVIEW
            else [_blocker(classification)]
        ),
        next_safe_action=_next_safe_action(classification),
        **_permission_defaults(),
    )


def demo_manual_execution_exception_scope_to_jsonable_dict(
    result: DemoManualExecutionExceptionScopeResult,
) -> dict[str, Any]:
    return _json_value(result)


def demo_manual_execution_exception_scope_to_operator_text(
    result: DemoManualExecutionExceptionScopeResult | None = None,
) -> str:
    active = result or evaluate_demo_manual_execution_exception_scope()
    if active.scope_review_allowed:
        return (
            "Manual execution exception scope is valid for owner review only. "
            "Codex cannot execute, call a broker, or place orders. No trade was placed."
        )
    return (
        f"Manual execution exception scope is blocked: {'; '.join(active.blockers)}. "
        "No broker call was made and no trade was placed."
    )


def demo_manual_execution_exception_scope_to_markdown(
    result: DemoManualExecutionExceptionScopeResult | None = None,
) -> str:
    active = result or evaluate_demo_manual_execution_exception_scope()
    return "\n".join(
        [
            "# Demo Manual Execution Exception Scope Gate V1",
            "",
            active.owner_warning,
            active.exception_warning,
            "",
            "No broker call was made. No trade was placed.",
            "",
            f"- Status: {active.classification}",
            f"- Scope review allowed: {active.scope_review_allowed}",
            f"- Required phrase: {active.required_phrase}",
            f"- Demo execution allowed: {active.demo_execution_allowed}",
            f"- Broker action allowed: {active.broker_action_allowed}",
            f"- Live trading allowed: {active.live_trading_allowed}",
            f"- Real money allowed: {active.real_money_allowed}",
            f"- Next safe action: {active.next_safe_action}",
        ]
    )


def _classify(value: DemoManualExecutionExceptionScopeInput) -> str:
    phrase = value.exception_phrase.strip()
    if not phrase:
        return DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_MISSING
    if phrase == value.config.required_phrase:
        return DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_VALID_FOR_REVIEW
    phrase_lower = phrase.lower()
    if any(term in phrase_lower for term in ("live trading", "live trade", "live account")):
        return DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_LIVE_SCOPE
    if any(term in phrase_lower for term in ("real money", "funded account", "compounding", "bank movement")):
        return DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_REAL_MONEY_SCOPE
    if any(term in phrase_lower for term in ("credential", "password", "secret", "token", "account id")):
        return DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_CREDENTIAL_SCOPE
    if any(term in phrase_lower for term in ("broker action authorized", "authorize broker", "oanda action")):
        return DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_BROKER_ACTION_AUTHORITY
    if any(term in phrase_lower for term in ("codex to execute", "ai may execute", "bot may execute")):
        return DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_CODEX_EXECUTION_AUTHORITY
    if any(term in phrase_lower for term in ("execute this", "place this", "submit this")):
        return DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_CODEX_EXECUTION_AUTHORITY
    return DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_MISSING


def _blocker(classification: str) -> str:
    if classification == DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_MISSING:
        return "manual exception phrase is missing or does not match the required review-only scope"
    if classification == DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_CODEX_EXECUTION_AUTHORITY:
        return "phrase attempts to grant Codex, AI, or bot execution authority"
    if classification == DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_BROKER_ACTION_AUTHORITY:
        return "phrase attempts to grant broker action authority"
    if classification == DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_REAL_MONEY_SCOPE:
        return "phrase attempts to include real money, compounding, or bank movement scope"
    if classification == DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_BLOCKED_CREDENTIAL_SCOPE:
        return "phrase attempts to include credentials or account identifiers"
    return "phrase attempts to include live trading scope"


def _next_safe_action(classification: str) -> str:
    if classification == DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_VALID_FOR_REVIEW:
        return "Continue local manual exception review; Codex execution and broker action remain locked."
    return "Use the exact manual-review-only exception phrase or keep the packet blocked."


def _coerce_input(
    value: DemoManualExecutionExceptionScopeInput | Mapping[str, Any],
) -> DemoManualExecutionExceptionScopeInput:
    if isinstance(value, DemoManualExecutionExceptionScopeInput):
        return value
    raw = dict(value)
    config = raw.get("config", DemoManualExecutionExceptionScopeConfig())
    if not isinstance(config, DemoManualExecutionExceptionScopeConfig):
        config = DemoManualExecutionExceptionScopeConfig(**dict(config))
    return DemoManualExecutionExceptionScopeInput(
        exception_phrase=str(raw.get("exception_phrase", "")),
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
