"""Supervised compounding policy gate for build-only AIOS Forex review."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from automation.forex_engine.forex_statistical_profit_proof_gate_v1 import (
    STATISTICAL_PROFIT_BLOCKED_SCHEMA_INVALID,
    STATISTICAL_PROFIT_BLOCKED_UNSAFE,
    STATISTICAL_PROFIT_PROOF_READY,
    STATISTICAL_PROFIT_REQUIRE_MORE_EVIDENCE,
    build_sample_partial_input as build_statistical_sample_partial_input,
    build_sample_ready_input as build_statistical_sample_ready_input,
    build_sample_unsafe_input as build_statistical_sample_unsafe_input,
    evaluate_forex_statistical_profit_proof_gate,
)


VERSION = "forex_supervised_compounding_policy_gate_v1"
PACKET_ID = "AIOS-FOREX-SUPERVISED-COMPOUNDING-POLICY-GATE-V1"
NEXT_PACKET_PREVIEW = "AIOS-FOREX-SOS-OWNER-ALERT-BRIDGE-V1"

SUPERVISED_COMPOUNDING_POLICY_READY = "SUPERVISED_COMPOUNDING_POLICY_READY"
SUPERVISED_COMPOUNDING_REQUIRE_MORE_EVIDENCE = (
    "SUPERVISED_COMPOUNDING_REQUIRE_MORE_EVIDENCE"
)
SUPERVISED_COMPOUNDING_BLOCKED_UNSAFE = "SUPERVISED_COMPOUNDING_BLOCKED_UNSAFE"
SUPERVISED_COMPOUNDING_BLOCKED_SCHEMA_INVALID = (
    "SUPERVISED_COMPOUNDING_BLOCKED_SCHEMA_INVALID"
)

COMPOUNDING_POLICY_SURFACES = (
    "source_statistical_profit_proof_ready",
    "source_evidence_quality_ready",
    "owner_approval_required",
    "owner_approval_separated",
    "compounding_disabled_by_default",
    "compounding_requires_explicit_arming",
    "compounding_requires_profit_lock_threshold",
    "compounding_requires_drawdown_cooldown",
    "compounding_requires_daily_loss_cap",
    "compounding_requires_max_drawdown_cap",
    "compounding_requires_kill_switch",
    "compounding_requires_one_order_only",
    "compounding_requires_duplicate_order_prevention",
    "compounding_requires_position_size_cap",
    "compounding_requires_risk_per_trade_cap",
    "compounding_requires_equity_curve_health",
    "compounding_requires_profit_factor_health",
    "compounding_requires_expectancy_health",
    "compounding_requires_session_quality_health",
    "compounding_requires_market_regime_filter",
    "compounding_requires_spread_slippage_filter",
    "compounding_requires_news_filter",
    "compounding_requires_pause_on_degradation",
    "compounding_requires_owner_intervention_path",
    "compounding_requires_audit_logging",
    "compounding_requires_evidence_logging",
    "compounding_requires_sos_readiness",
    "bank_movement_blocked",
    "withdrawal_blocked",
    "deposit_blocked",
    "broker_action_blocked",
    "live_execution_blocked",
    "autonomous_execution_blocked",
    "vacation_authorization_blocked",
    "protected_flags_false",
    "unsafe_payload_absent",
)

PROTECTED_FLAG_NAMES = (
    "live_trading_allowed",
    "live_execution_allowed",
    "broker_action_allowed",
    "credential_access_allowed",
    "account_id_persistence_allowed",
    "autonomous_execution_allowed",
    "compounding_allowed",
    "compounding_execution_authorized",
    "bank_movement_allowed",
    "withdrawal_allowed",
    "deposit_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "sos_alert_send_allowed",
    "unattended_vacation_mode_allowed",
    "vacation_profit_trial_allowed",
    "next_trade_authorized",
    "repeat_trade_authorized",
    "selected_packet_execution_authorized",
    "codex_live_execution_authorized",
    "owner_live_execution_approval_present",
    "supervised_compounding_gate_authorizes_trading",
    "supervised_compounding_gate_authorizes_execution",
    "supervised_compounding_gate_authorizes_compounding",
    "supervised_compounding_gate_authorizes_vacation_mode",
)

BLOCKED_ACTIONS = (
    "broker_call",
    "oanda_api_call",
    "credential_access",
    "env_read",
    "account_id_access",
    "account_id_persistence",
    "order_placement",
    "live_execution",
    "autonomous_execution",
    "compounding_execution",
    "bank_movement",
    "withdrawal",
    "deposit",
    "scheduler",
    "daemon",
    "webhook",
    "uncontrolled_retry",
    "sos_alert_send",
    "selected_packet_execution",
    "commit",
    "push",
    "pr",
    "merge",
    "vacation_mode_execution",
)

BLOCKED_CLAIMS = (
    "guaranteed_profit",
    "future_profit",
    "final_statistical_profitability",
    "production_readiness",
    "vacation_mode_readiness",
    "autonomous_trading_readiness",
    "compounding_execution_readiness",
    "live_execution_readiness",
    "profitable_22_6_operation_confirmed",
    "unattended_account_management_confirmed",
)

UNSAFE_STRING_FRAGMENTS = (
    "Authorization",
    "Bearer",
    "access_token",
    "refresh_token",
    "api_key",
    "password",
    "secret",
    "credential",
    "accountID",
    "account_id",
    "AccountID",
    "OANDA-ACCOUNT",
    "v3/accounts/",
    "api-fxtrade.oanda.com",
    "api-fxpractice.oanda.com",
    "raw_transaction_id",
    "raw_order_id",
    "broker_order_id",
    "account_number",
    "live authorization",
    "live execution",
    "autonomous execution",
    "compound execution",
    "compounding execution",
    "bank movement",
    "bank transfer",
    "withdrawal",
    "deposit",
    "send sos",
    "sos alert send",
    "scheduler",
    "daemon",
    "webhook",
    "uncontrolled retry",
)

UNSAFE_FALSE_SURFACES = (
    "owner_approval_required",
    "owner_approval_separated",
    "compounding_disabled_by_default",
    "compounding_requires_explicit_arming",
    "bank_movement_blocked",
    "withdrawal_blocked",
    "deposit_blocked",
    "broker_action_blocked",
    "live_execution_blocked",
    "autonomous_execution_blocked",
    "vacation_authorization_blocked",
    "protected_flags_false",
    "unsafe_payload_absent",
)

READY_OWNER_ACTION = (
    "Review the supervised compounding policy result and decide whether to "
    "request the separate SOS owner alert bridge packet; do not approve "
    "broker access, live execution, compounding execution, autonomous "
    "execution, bank movement, withdrawal, deposit, SOS alert sending, or "
    "Vacation Mode execution from this gate."
)
PARTIAL_OWNER_ACTION = (
    "Close the missing compounding policy surfaces listed in "
    "missing_surfaces, then rerun this local supervised compounding policy "
    "gate before requesting an SOS owner alert bridge packet."
)
UNSAFE_OWNER_ACTION = (
    "Stop and remove the unsafe signals listed in unsafe_fragments_detected "
    "before continuing supervised compounding policy work."
)
SCHEMA_OWNER_ACTION = (
    "Fix the source_statistical_profit_result and compounding_policy_surfaces "
    "input schema, then rerun the local supervised compounding policy gate."
)
EXACT_NEXT_CODEX_PACKET_POLICY = (
    "Codex may only generate or run a future tokenized SOS owner alert "
    "bridge packet that keeps OANDA, broker calls, credentials, account IDs, "
    "live execution, autonomous execution, compounding execution, bank "
    "movement, withdrawal, deposit, schedulers, daemons, webhooks, and "
    "actual SOS alert sending forbidden unless Anthony separately approves "
    "a new exact packet under RISK_POLICY.md."
)


@dataclass(frozen=True)
class SupervisedCompoundingPolicyGateInput:
    source_statistical_profit_result: Any
    compounding_policy_surfaces: Mapping[str, bool] = field(default_factory=dict)
    owner_compounding_label: str = "pending_owner_review"
    owner_notes_sanitized: str = ""


@dataclass(frozen=True)
class SupervisedCompoundingPolicyGateResult:
    version: str
    packet_id: str
    classification: str
    compounding_policy_status: str
    ready_surface_count: int
    total_surface_count: int
    compounding_policy_percent: float
    ready_surfaces: tuple[str, ...]
    missing_surfaces: tuple[str, ...]
    blocked_surfaces: tuple[str, ...]
    unsafe_fragments_detected: tuple[str, ...]
    source_statistical_classification: str
    source_statistical_percent: float
    source_ready_surface_count: int
    source_total_surface_count: int
    protected_flags: Mapping[str, bool]
    blocked_actions: tuple[str, ...]
    blocked_claims: tuple[str, ...]
    exact_next_owner_action: str
    exact_next_codex_packet_policy: str
    one_sentence_answer: str
    next_packet_preview: str
    next_safe_action: str
    broker_action_authorized: bool
    live_trading_authorized: bool
    autonomous_execution_authorized: bool
    bank_movement_authorized: bool
    withdrawal_authorized: bool
    deposit_authorized: bool
    vacation_mode_execution_authorized: bool
    sos_alert_sent: bool
    live_trading_allowed: bool
    live_execution_allowed: bool
    broker_action_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool
    autonomous_execution_allowed: bool
    compounding_allowed: bool
    compounding_execution_authorized: bool
    bank_movement_allowed: bool
    withdrawal_allowed: bool
    deposit_allowed: bool
    scheduler_allowed: bool
    daemon_allowed: bool
    webhook_allowed: bool
    sos_alert_send_allowed: bool
    unattended_vacation_mode_allowed: bool
    vacation_profit_trial_allowed: bool
    next_trade_authorized: bool
    repeat_trade_authorized: bool
    selected_packet_execution_authorized: bool
    codex_live_execution_authorized: bool
    owner_live_execution_approval_present: bool
    supervised_compounding_gate_authorizes_trading: bool
    supervised_compounding_gate_authorizes_execution: bool
    supervised_compounding_gate_authorizes_compounding: bool
    supervised_compounding_gate_authorizes_vacation_mode: bool


@dataclass(frozen=True)
class _SchemaState:
    invalid: bool
    missing_or_invalid: tuple[str, ...]


def build_sample_ready_input() -> SupervisedCompoundingPolicyGateInput:
    source_result = evaluate_forex_statistical_profit_proof_gate(
        build_statistical_sample_ready_input()
    )
    return SupervisedCompoundingPolicyGateInput(
        source_statistical_profit_result=source_result,
        compounding_policy_surfaces=_ready_policy_surface_map(),
        owner_compounding_label="pending_owner_review",
        owner_notes_sanitized="sanitized supervised compounding policy preview",
    )


def build_sample_partial_input() -> SupervisedCompoundingPolicyGateInput:
    source_result = evaluate_forex_statistical_profit_proof_gate(
        build_statistical_sample_partial_input()
    )
    policy_surfaces = _ready_policy_surface_map()
    for name in (
        "compounding_requires_profit_factor_health",
        "compounding_requires_expectancy_health",
        "compounding_requires_session_quality_health",
        "compounding_requires_market_regime_filter",
        "compounding_requires_spread_slippage_filter",
        "compounding_requires_news_filter",
        "compounding_requires_pause_on_degradation",
    ):
        policy_surfaces.pop(name)
    return SupervisedCompoundingPolicyGateInput(
        source_statistical_profit_result=source_result,
        compounding_policy_surfaces=policy_surfaces,
        owner_compounding_label="pending_more_evidence",
        owner_notes_sanitized="safe incomplete supervised compounding policy preview",
    )


def build_sample_unsafe_input() -> SupervisedCompoundingPolicyGateInput:
    source_result = evaluate_forex_statistical_profit_proof_gate(
        build_statistical_sample_unsafe_input()
    )
    policy_surfaces = _ready_policy_surface_map()
    policy_surfaces.update(
        {
            "compounding_disabled_by_default": False,
            "bank_movement_blocked": False,
            "withdrawal_blocked": False,
            "deposit_blocked": False,
            "broker_action_blocked": False,
            "live_execution_blocked": False,
            "autonomous_execution_blocked": False,
            "vacation_authorization_blocked": False,
        }
    )
    return SupervisedCompoundingPolicyGateInput(
        source_statistical_profit_result=source_result,
        compounding_policy_surfaces=policy_surfaces,
        owner_compounding_label="pending_owner_review",
        owner_notes_sanitized=(
            "Authorization Bearer blocked sample with account_id, live "
            "authorization, compounding execution, withdrawal, deposit, "
            "bank movement, and sos alert send markers"
        ),
    )


def build_sample_schema_invalid_input() -> Mapping[str, Any]:
    return {
        "source_statistical_profit_result": {
            "classification": 123,
            "statistical_percent": "one hundred",
            "ready_surface_count": "thirty-two",
            "ready_surfaces": "not-a-list",
            "unsafe_fragments_detected": "schema-invalid",
        },
        "compounding_policy_surfaces": {
            "owner_approval_required": "yes",
            "unknown_compounding_policy_surface": True,
        },
        "owner_compounding_label": "schema-invalid",
        "owner_notes_sanitized": "schema invalid sample",
    }


def evaluate_forex_supervised_compounding_policy_gate(
    gate_input: SupervisedCompoundingPolicyGateInput | Mapping[str, Any] | None = None,
) -> SupervisedCompoundingPolicyGateResult:
    active_input = _coerce_input(gate_input or build_sample_ready_input())
    schema = _validate_schema(active_input)
    source = active_input.source_statistical_profit_result
    source_values = _source_values(source)
    surfaces = _compounding_surfaces(active_input, source, source_values)
    policy_errors = _validate_policy_surface_values(
        active_input.compounding_policy_surfaces
    )
    if policy_errors:
        schema = _SchemaState(
            invalid=True,
            missing_or_invalid=_unique_tuple(schema.missing_or_invalid + policy_errors),
        )

    unsafe_fragments = _unsafe_fragments(active_input, source)
    ready_surfaces = tuple(
        name for name in COMPOUNDING_POLICY_SURFACES if surfaces.get(name) is True
    )
    not_ready_surfaces = tuple(
        name for name in COMPOUNDING_POLICY_SURFACES if surfaces.get(name) is not True
    )

    if schema.invalid:
        classification = SUPERVISED_COMPOUNDING_BLOCKED_SCHEMA_INVALID
        compounding_policy_status = "blocked_schema_invalid"
        missing_surfaces = not_ready_surfaces
        blocked_surfaces: tuple[str, ...] = ()
        unsafe_output = schema.missing_or_invalid
        next_owner_action = SCHEMA_OWNER_ACTION
    elif unsafe_fragments:
        classification = SUPERVISED_COMPOUNDING_BLOCKED_UNSAFE
        compounding_policy_status = "blocked_unsafe_fail_closed"
        missing_surfaces = ()
        blocked_surfaces = not_ready_surfaces or ("unsafe_payload_absent",)
        unsafe_output = unsafe_fragments
        next_owner_action = UNSAFE_OWNER_ACTION
    elif len(ready_surfaces) == len(COMPOUNDING_POLICY_SURFACES):
        classification = SUPERVISED_COMPOUNDING_POLICY_READY
        compounding_policy_status = "all_compounding_policy_surfaces_ready_build_only"
        missing_surfaces = ()
        blocked_surfaces = ()
        unsafe_output = ()
        next_owner_action = READY_OWNER_ACTION
    else:
        classification = SUPERVISED_COMPOUNDING_REQUIRE_MORE_EVIDENCE
        compounding_policy_status = "safe_more_compounding_policy_evidence_required"
        missing_surfaces = not_ready_surfaces
        blocked_surfaces = ()
        unsafe_output = ()
        next_owner_action = PARTIAL_OWNER_ACTION

    protected_flags = protected_flags_false()
    return SupervisedCompoundingPolicyGateResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=classification,
        compounding_policy_status=compounding_policy_status,
        ready_surface_count=len(ready_surfaces),
        total_surface_count=len(COMPOUNDING_POLICY_SURFACES),
        compounding_policy_percent=_compounding_policy_percent(len(ready_surfaces)),
        ready_surfaces=ready_surfaces,
        missing_surfaces=missing_surfaces,
        blocked_surfaces=blocked_surfaces,
        unsafe_fragments_detected=unsafe_output,
        source_statistical_classification=source_values["classification"],
        source_statistical_percent=source_values["statistical_percent"],
        source_ready_surface_count=source_values["ready_surface_count"],
        source_total_surface_count=source_values["total_surface_count"],
        protected_flags=protected_flags,
        blocked_actions=BLOCKED_ACTIONS,
        blocked_claims=BLOCKED_CLAIMS,
        exact_next_owner_action=next_owner_action,
        exact_next_codex_packet_policy=EXACT_NEXT_CODEX_PACKET_POLICY,
        one_sentence_answer=_one_sentence_answer(classification),
        next_packet_preview=NEXT_PACKET_PREVIEW,
        next_safe_action=next_owner_action,
        broker_action_authorized=False,
        live_trading_authorized=False,
        autonomous_execution_authorized=False,
        bank_movement_authorized=False,
        withdrawal_authorized=False,
        deposit_authorized=False,
        vacation_mode_execution_authorized=False,
        sos_alert_sent=False,
        **protected_flags,
    )


def protected_flags_false() -> dict[str, bool]:
    return {name: False for name in PROTECTED_FLAG_NAMES}


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return _jsonable(result)


def to_operator_text(result: SupervisedCompoundingPolicyGateResult) -> str:
    return "\n".join(
        (
            f"Supervised compounding policy classification: {result.classification}.",
            f"Compounding policy surfaces: {result.ready_surface_count}/"
            f"{result.total_surface_count} "
            f"({result.compounding_policy_percent:.2f}%).",
            result.one_sentence_answer,
            result.next_safe_action,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
            "No money movement was authorized by this packet.",
            "No SOS alert was sent by this packet.",
            "All protected flags remain false.",
        )
    )


def to_markdown(result: SupervisedCompoundingPolicyGateResult) -> str:
    rows = [
        "# AIOS Forex Supervised Compounding Policy Gate V1",
        "",
        f"- Packet ID: `{result.packet_id}`",
        f"- Version: `{result.version}`",
        f"- Classification: `{result.classification}`",
        f"- Compounding policy status: `{result.compounding_policy_status}`",
        f"- Ready surfaces: `{result.ready_surface_count}`",
        f"- Total surfaces: `{result.total_surface_count}`",
        f"- Compounding policy percent: `{result.compounding_policy_percent:.2f}`",
        (
            "- Source statistical classification: "
            f"`{result.source_statistical_classification}`"
        ),
        f"- Source statistical percent: `{result.source_statistical_percent:.2f}`",
        f"- Source ready surface count: `{result.source_ready_surface_count}`",
        f"- Source total surface count: `{result.source_total_surface_count}`",
        f"- Next packet preview: `{result.next_packet_preview}`",
        "",
        "## Ready Surfaces",
    ]
    rows.extend(f"- `{name}`" for name in result.ready_surfaces)
    rows.extend(("", "## Missing Surfaces"))
    rows.extend(f"- `{name}`" for name in result.missing_surfaces)
    rows.extend(("", "## Blocked Surfaces"))
    rows.extend(f"- `{name}`" for name in result.blocked_surfaces)
    rows.extend(("", "## Unsafe Fragments Detected"))
    rows.extend(f"- `{name}`" for name in result.unsafe_fragments_detected)
    rows.extend(("", "## Protected Flags"))
    rows.extend(_markdown_bool_map(result.protected_flags))
    rows.extend(("", "## Blocked Actions"))
    rows.extend(f"- `{name}`" for name in result.blocked_actions)
    rows.extend(("", "## Blocked Claims"))
    rows.extend(f"- `{name}`" for name in result.blocked_claims)
    rows.extend(
        (
            "",
            "## Next Actions",
            f"- Owner: {result.exact_next_owner_action}",
            f"- Codex packet policy: {result.exact_next_codex_packet_policy}",
            f"- Next safe action: {result.next_safe_action}",
            "",
            f"One sentence answer: {result.one_sentence_answer}",
        )
    )
    rows.extend(markdown_safety_lines())
    return "\n".join(rows) + "\n"


def markdown_safety_lines() -> list[str]:
    return [
        "",
        "## Safety",
        "- Build-only supervised compounding policy evaluation.",
        "- No trade placed by this packet.",
        "- No OANDA call was made by this packet.",
        "- No broker call was made by this packet.",
        "- No credential access occurred.",
        "- No .env read occurred.",
        "- No account ID was persisted.",
        "- No live approval was granted.",
        "- No autonomous execution was approved.",
        "- No compounding execution approval was granted.",
        "- No bank movement was authorized.",
        "- No withdrawal was authorized.",
        "- No deposit was authorized.",
        "- No Vacation Mode execution was authorized.",
        "- No SOS alert was sent.",
        "- No scheduler, daemon, or webhook was created.",
        "- All protected flags remain false.",
    ]


def _ready_policy_surface_map() -> dict[str, bool]:
    return {name: True for name in COMPOUNDING_POLICY_SURFACES}


def _coerce_input(
    value: SupervisedCompoundingPolicyGateInput | Mapping[str, Any],
) -> SupervisedCompoundingPolicyGateInput:
    if isinstance(value, SupervisedCompoundingPolicyGateInput):
        return value
    if isinstance(value, Mapping):
        raw = dict(value)
    else:
        raw = {
            "source_statistical_profit_result": getattr(
                value, "source_statistical_profit_result", None
            ),
            "compounding_policy_surfaces": getattr(
                value, "compounding_policy_surfaces", {}
            ),
            "owner_compounding_label": getattr(
                value, "owner_compounding_label", "pending_owner_review"
            ),
            "owner_notes_sanitized": getattr(value, "owner_notes_sanitized", ""),
        }
    policy_surfaces = raw.get("compounding_policy_surfaces", {})
    return SupervisedCompoundingPolicyGateInput(
        source_statistical_profit_result=raw.get("source_statistical_profit_result"),
        compounding_policy_surfaces=(
            dict(policy_surfaces)
            if isinstance(policy_surfaces, Mapping)
            else policy_surfaces
        ),
        owner_compounding_label=_safe_owner_compounding_label(
            raw.get("owner_compounding_label", "pending_owner_review")
        ),
        owner_notes_sanitized=_text(raw.get("owner_notes_sanitized", "")),
    )


def _validate_schema(active_input: SupervisedCompoundingPolicyGateInput) -> _SchemaState:
    invalid: list[str] = []
    source = active_input.source_statistical_profit_result
    for field_name in (
        "classification",
        "statistical_percent",
        "ready_surface_count",
        "total_surface_count",
        "ready_surfaces",
        "missing_surfaces",
        "blocked_surfaces",
        "unsafe_fragments_detected",
        "protected_flags",
    ):
        if not _has_field(source, field_name):
            invalid.append(f"source_statistical_profit_result.{field_name}_missing")

    classification = _field(source, "classification")
    if not isinstance(classification, str):
        invalid.append("source_statistical_profit_result.classification_not_string")
    elif classification not in (
        STATISTICAL_PROFIT_PROOF_READY,
        STATISTICAL_PROFIT_REQUIRE_MORE_EVIDENCE,
        STATISTICAL_PROFIT_BLOCKED_UNSAFE,
        STATISTICAL_PROFIT_BLOCKED_SCHEMA_INVALID,
    ):
        invalid.append("source_statistical_profit_result.classification_unknown")
    elif classification == STATISTICAL_PROFIT_BLOCKED_SCHEMA_INVALID:
        invalid.append("source_statistical_profit_result.classification_schema_invalid")

    if _number_or_none(_field(source, "statistical_percent")) is None:
        invalid.append("source_statistical_profit_result.statistical_percent_not_numeric")
    for field_name in ("ready_surface_count", "total_surface_count"):
        if not _is_integer(_field(source, field_name)):
            invalid.append(f"source_statistical_profit_result.{field_name}_not_integer")
    if (
        _is_integer(_field(source, "ready_surface_count"))
        and _is_integer(_field(source, "total_surface_count"))
        and _field(source, "ready_surface_count") > _field(source, "total_surface_count")
    ):
        invalid.append("source_statistical_profit_result.ready_count_exceeds_total")

    for field_name in (
        "ready_surfaces",
        "missing_surfaces",
        "blocked_surfaces",
        "unsafe_fragments_detected",
    ):
        if not isinstance(_field(source, field_name), tuple | list):
            invalid.append(f"source_statistical_profit_result.{field_name}_not_sequence")
    if not isinstance(_field(source, "protected_flags"), Mapping):
        invalid.append("source_statistical_profit_result.protected_flags_not_mapping")
    if not isinstance(active_input.compounding_policy_surfaces, Mapping):
        invalid.append("compounding_policy_surfaces_not_mapping")
    return _SchemaState(invalid=bool(invalid), missing_or_invalid=_unique_tuple(invalid))


def _validate_policy_surface_values(policy_surfaces: Any) -> tuple[str, ...]:
    if not isinstance(policy_surfaces, Mapping):
        return ("compounding_policy_surfaces_not_mapping",)
    errors: list[str] = []
    for name, value in policy_surfaces.items():
        if name not in COMPOUNDING_POLICY_SURFACES:
            errors.append(f"compounding_policy_surfaces.{name}_unknown")
            continue
        if not isinstance(value, bool):
            errors.append(f"compounding_policy_surfaces.{name}_not_boolean")
    return tuple(errors)


def _compounding_surfaces(
    active_input: SupervisedCompoundingPolicyGateInput,
    source: Any,
    source_values: Mapping[str, Any],
) -> dict[str, bool]:
    policy_surfaces = (
        active_input.compounding_policy_surfaces
        if isinstance(active_input.compounding_policy_surfaces, Mapping)
        else {}
    )
    source_ready = set(_unique_tuple(_field(source, "ready_surfaces", ())))
    source_flags = _field(source, "protected_flags", {})
    if not isinstance(source_flags, Mapping):
        source_flags = {}
    source_classification = source_values["classification"]
    source_safe = source_classification not in (
        STATISTICAL_PROFIT_BLOCKED_UNSAFE,
        STATISTICAL_PROFIT_BLOCKED_SCHEMA_INVALID,
    )
    source_is_ready = (
        source_classification == STATISTICAL_PROFIT_PROOF_READY
        and source_values["ready_surface_count"] == source_values["total_surface_count"]
        and source_values["statistical_percent"] == 100.0
    )
    source_protected_false = bool(source_flags) and all(
        value is False for value in source_flags.values()
    )
    source_unsafe_absent = (
        source_safe
        and "unsafe_payload_absent" in source_ready
        and not _field(source, "unsafe_fragments_detected", ())
    )

    return {
        "source_statistical_profit_proof_ready": source_is_ready,
        "source_evidence_quality_ready": (
            source_is_ready and "evidence_quality_gate_ready" in source_ready
        ),
        "owner_approval_required": _policy_true(policy_surfaces, "owner_approval_required"),
        "owner_approval_separated": _policy_true(
            policy_surfaces, "owner_approval_separated"
        ),
        "compounding_disabled_by_default": _policy_true(
            policy_surfaces, "compounding_disabled_by_default"
        ),
        "compounding_requires_explicit_arming": _policy_true(
            policy_surfaces, "compounding_requires_explicit_arming"
        ),
        "compounding_requires_profit_lock_threshold": _policy_true(
            policy_surfaces, "compounding_requires_profit_lock_threshold"
        ),
        "compounding_requires_drawdown_cooldown": _policy_true(
            policy_surfaces, "compounding_requires_drawdown_cooldown"
        ),
        "compounding_requires_daily_loss_cap": _policy_true(
            policy_surfaces, "compounding_requires_daily_loss_cap"
        ),
        "compounding_requires_max_drawdown_cap": _policy_true(
            policy_surfaces, "compounding_requires_max_drawdown_cap"
        ),
        "compounding_requires_kill_switch": _policy_true(
            policy_surfaces, "compounding_requires_kill_switch"
        ),
        "compounding_requires_one_order_only": _policy_true(
            policy_surfaces, "compounding_requires_one_order_only"
        ),
        "compounding_requires_duplicate_order_prevention": _policy_true(
            policy_surfaces, "compounding_requires_duplicate_order_prevention"
        ),
        "compounding_requires_position_size_cap": _policy_true(
            policy_surfaces, "compounding_requires_position_size_cap"
        ),
        "compounding_requires_risk_per_trade_cap": _policy_true(
            policy_surfaces, "compounding_requires_risk_per_trade_cap"
        ),
        "compounding_requires_equity_curve_health": _policy_true(
            policy_surfaces, "compounding_requires_equity_curve_health"
        ),
        "compounding_requires_profit_factor_health": _policy_true(
            policy_surfaces, "compounding_requires_profit_factor_health"
        ),
        "compounding_requires_expectancy_health": _policy_true(
            policy_surfaces, "compounding_requires_expectancy_health"
        ),
        "compounding_requires_session_quality_health": _policy_true(
            policy_surfaces, "compounding_requires_session_quality_health"
        ),
        "compounding_requires_market_regime_filter": _policy_true(
            policy_surfaces, "compounding_requires_market_regime_filter"
        ),
        "compounding_requires_spread_slippage_filter": _policy_true(
            policy_surfaces, "compounding_requires_spread_slippage_filter"
        ),
        "compounding_requires_news_filter": _policy_true(
            policy_surfaces, "compounding_requires_news_filter"
        ),
        "compounding_requires_pause_on_degradation": _policy_true(
            policy_surfaces, "compounding_requires_pause_on_degradation"
        ),
        "compounding_requires_owner_intervention_path": _policy_true(
            policy_surfaces, "compounding_requires_owner_intervention_path"
        ),
        "compounding_requires_audit_logging": _policy_true(
            policy_surfaces, "compounding_requires_audit_logging"
        ),
        "compounding_requires_evidence_logging": _policy_true(
            policy_surfaces, "compounding_requires_evidence_logging"
        ),
        "compounding_requires_sos_readiness": _policy_true(
            policy_surfaces, "compounding_requires_sos_readiness"
        ),
        "bank_movement_blocked": _policy_true(policy_surfaces, "bank_movement_blocked"),
        "withdrawal_blocked": _policy_true(policy_surfaces, "withdrawal_blocked"),
        "deposit_blocked": _policy_true(policy_surfaces, "deposit_blocked"),
        "broker_action_blocked": _policy_true(policy_surfaces, "broker_action_blocked")
        and source_flags.get("broker_action_allowed") is False,
        "live_execution_blocked": _policy_true(policy_surfaces, "live_execution_blocked")
        and source_flags.get("live_execution_allowed") is False,
        "autonomous_execution_blocked": _policy_true(
            policy_surfaces, "autonomous_execution_blocked"
        )
        and source_flags.get("autonomous_execution_allowed") is False,
        "vacation_authorization_blocked": _policy_true(
            policy_surfaces, "vacation_authorization_blocked"
        )
        and source_flags.get("unattended_vacation_mode_allowed") is False
        and source_flags.get("vacation_profit_trial_allowed") is False,
        "protected_flags_false": _policy_true(policy_surfaces, "protected_flags_false")
        and source_protected_false,
        "unsafe_payload_absent": _policy_true(policy_surfaces, "unsafe_payload_absent")
        and source_unsafe_absent,
    }


def _policy_true(policy_surfaces: Mapping[str, Any], name: str) -> bool:
    return policy_surfaces.get(name) is True


def _source_values(source: Any) -> dict[str, Any]:
    return {
        "classification": _text(_field(source, "classification", "")),
        "statistical_percent": _safe_float(_field(source, "statistical_percent", 0)),
        "ready_surface_count": _safe_int(_field(source, "ready_surface_count", 0)),
        "total_surface_count": _safe_int(_field(source, "total_surface_count", 0)),
    }


def _unsafe_fragments(
    active_input: SupervisedCompoundingPolicyGateInput, source: Any
) -> tuple[str, ...]:
    fragments: list[str] = []
    fragments.extend(_source_unsafe_fragments(source))
    source_classification = _field(source, "classification", "")
    if source_classification == STATISTICAL_PROFIT_BLOCKED_UNSAFE:
        fragments.append("source_statistical_profit_result.classification:block_unsafe")
    source_flags = _field(source, "protected_flags", {})
    if isinstance(source_flags, Mapping):
        fragments.extend(
            f"source_statistical_profit_result.protected_flags.{name}:true"
            for name, value in source_flags.items()
            if value is True
        )
    policy_surfaces = active_input.compounding_policy_surfaces
    if isinstance(policy_surfaces, Mapping):
        fragments.extend(
            f"compounding_policy_surfaces.{name}:false"
            for name, value in policy_surfaces.items()
            if name in UNSAFE_FALSE_SURFACES and value is False
        )
    fragments.extend(
        _scan_string_value(
            "owner_compounding_label", active_input.owner_compounding_label
        )
    )
    fragments.extend(
        _scan_string_value("owner_notes_sanitized", active_input.owner_notes_sanitized)
    )
    return _unique_tuple(fragments)


def _source_unsafe_fragments(source: Any) -> tuple[str, ...]:
    raw = _field(source, "unsafe_fragments_detected", ())
    if isinstance(raw, str):
        return (f"source_statistical_profit_result.unsafe_fragments_detected:{raw}",)
    if isinstance(raw, tuple | list):
        return tuple(
            f"source_statistical_profit_result.unsafe_fragments_detected:{_text(item)}"
            for item in raw
            if _text(item)
        )
    return ()


def _has_field(value: Any, field_name: str) -> bool:
    if isinstance(value, Mapping):
        return field_name in value
    return hasattr(value, field_name)


def _field(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _is_integer(value: Any) -> bool:
    return type(value) is int


def _safe_int(value: Any) -> int:
    return value if _is_integer(value) else 0


def _number_or_none(value: Any) -> Decimal | None:
    if isinstance(value, bool):
        return None
    return _decimal_or_none(value)


def _safe_float(value: Any) -> float:
    number = _number_or_none(value)
    if number is None:
        return 0.0
    return float(round(number, 2))


def _safe_owner_compounding_label(value: Any) -> str:
    text = _text(value, "pending_owner_review")
    if not text:
        return "pending_owner_review"
    return text


def _scan_string_value(path: str, value: Any) -> tuple[str, ...]:
    if not isinstance(value, str):
        return ()
    lowered = value.lower()
    return tuple(
        f"{path}:{fragment}"
        for fragment in UNSAFE_STRING_FRAGMENTS
        if fragment.lower() in lowered
    )


def _compounding_policy_percent(ready_count: int) -> float:
    return round((ready_count / len(COMPOUNDING_POLICY_SURFACES)) * 100, 2)


def _one_sentence_answer(classification: str) -> str:
    if classification == SUPERVISED_COMPOUNDING_POLICY_READY:
        return (
            "AIOS has a build-only supervised compounding policy path ready "
            "for a future SOS owner alert bridge review, but this gate "
            "authorizes no trading, live execution, compounding execution, "
            "bank movement, SOS alert sending, or Vacation Mode execution."
        )
    if classification == SUPERVISED_COMPOUNDING_REQUIRE_MORE_EVIDENCE:
        return (
            "AIOS supervised compounding policy is safe but incomplete "
            "because one or more policy surfaces need more evidence."
        )
    if classification == SUPERVISED_COMPOUNDING_BLOCKED_UNSAFE:
        return (
            "AIOS supervised compounding policy is blocked because unsafe "
            "credential, broker, account, live execution, compounding "
            "execution, money movement, SOS, or automation signals were "
            "detected."
        )
    return (
        "AIOS supervised compounding policy cannot be evaluated until the "
        "required input schema is complete and valid."
    )


def _decimal_or_none(value: Any) -> Decimal | None:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _decimal_string(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")


def _markdown_bool_map(values: Mapping[str, bool]) -> list[str]:
    return [f"- `{key}`: `{str(value).lower()}`" for key, value in values.items()]


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return value.strip() if isinstance(value, str) else str(value).strip()


def _unique_tuple(values: Any) -> tuple[str, ...]:
    unique: list[str] = []
    for value in values:
        text = _text(value)
        if text and text not in unique:
            unique.append(text)
    return tuple(unique)


def _jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, Decimal):
        return _decimal_string(value)
    return value
