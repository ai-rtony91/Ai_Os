"""Statistical profit proof gate for build-only AIOS Forex review."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from automation.forex_engine.forex_evidence_depth_quality_gate_v1 import (
    EVIDENCE_DEPTH_BLOCKED_SCHEMA_INVALID,
    EVIDENCE_DEPTH_BLOCKED_UNSAFE,
    EVIDENCE_DEPTH_QUALITY_READY,
    build_sample_partial_input as build_quality_sample_partial_input,
    build_sample_ready_input as build_quality_sample_ready_input,
    build_sample_unsafe_input as build_quality_sample_unsafe_input,
    evaluate_forex_evidence_depth_quality_gate,
)


VERSION = "forex_statistical_profit_proof_gate_v1"
PACKET_ID = "AIOS-FOREX-STATISTICAL-PROFIT-PROOF-GATE-V1"
NEXT_PACKET_PREVIEW = "AIOS-FOREX-SUPERVISED-COMPOUNDING-POLICY-GATE-V1"

STATISTICAL_PROFIT_PROOF_READY = "STATISTICAL_PROFIT_PROOF_READY"
STATISTICAL_PROFIT_REQUIRE_MORE_EVIDENCE = (
    "STATISTICAL_PROFIT_REQUIRE_MORE_EVIDENCE"
)
STATISTICAL_PROFIT_BLOCKED_UNSAFE = "STATISTICAL_PROFIT_BLOCKED_UNSAFE"
STATISTICAL_PROFIT_BLOCKED_SCHEMA_INVALID = (
    "STATISTICAL_PROFIT_BLOCKED_SCHEMA_INVALID"
)

SOURCE_MORE_EVIDENCE_CLASSIFICATION = "EVIDENCE_DEPTH_REQUIRE_MORE_EVIDENCE"

STATISTICAL_SURFACES = (
    "minimum_trade_count_met",
    "minimum_session_count_met",
    "minimum_market_bucket_count_met",
    "positive_total_net_pnl_after_costs",
    "positive_average_r_multiple",
    "positive_expectancy",
    "profit_factor_threshold_met",
    "win_rate_reasonable",
    "average_win_loss_ratio_ready",
    "max_drawdown_threshold_met",
    "drawdown_recovery_ready",
    "losing_streak_threshold_met",
    "result_distribution_ready",
    "outlier_control_ready",
    "overfit_warning_absent",
    "walk_forward_support_ready",
    "market_regime_diversity_ready",
    "session_independence_ready",
    "risk_adjusted_return_ready",
    "sample_quality_ready",
    "evidence_quality_gate_ready",
    "evidence_integrity_ready",
    "schema_integrity_ready",
    "unsafe_payload_absent",
    "required_controls_met",
    "required_persistence_absence_met",
    "protected_flags_false",
    "broker_action_blocked",
    "live_execution_blocked",
    "compounding_blocked",
    "autonomous_execution_blocked",
    "vacation_authorization_blocked",
)

PROTECTED_FLAG_NAMES = (
    "live_trading_allowed",
    "live_execution_allowed",
    "broker_action_allowed",
    "credential_access_allowed",
    "account_id_persistence_allowed",
    "autonomous_execution_allowed",
    "compounding_allowed",
    "bank_movement_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "unattended_vacation_mode_allowed",
    "vacation_profit_trial_allowed",
    "next_trade_authorized",
    "repeat_trade_authorized",
    "selected_packet_execution_authorized",
    "codex_live_execution_authorized",
    "owner_live_execution_approval_present",
    "statistical_profit_gate_authorizes_trading",
    "statistical_profit_gate_authorizes_execution",
    "statistical_profit_gate_authorizes_compounding",
    "statistical_profit_gate_authorizes_vacation_mode",
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
    "compounding",
    "bank_movement",
    "scheduler",
    "daemon",
    "webhook",
    "uncontrolled_retry",
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
    "compounding_readiness",
    "live_execution_readiness",
    "profitable_22_6_operation_confirmed",
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
    "compound",
    "bank movement",
    "bank transfer",
    "scheduler",
    "daemon",
    "webhook",
    "uncontrolled retry",
)

PROTECTIVE_SURFACES = (
    "unsafe_payload_absent",
    "required_persistence_absence_met",
    "protected_flags_false",
    "broker_action_blocked",
    "live_execution_blocked",
    "compounding_blocked",
    "autonomous_execution_blocked",
    "vacation_authorization_blocked",
)

READY_OWNER_ACTION = (
    "Review the statistical profit proof result and decide whether to request "
    "the separate supervised compounding policy gate; do not approve broker "
    "access, live execution, compounding, autonomous execution, SOS alerting, "
    "or Vacation Mode execution from this gate."
)
PARTIAL_OWNER_ACTION = (
    "Close the missing statistical surfaces listed in missing_surfaces, then "
    "rerun this local statistical profit proof gate before requesting any "
    "supervised compounding policy review."
)
UNSAFE_OWNER_ACTION = (
    "Stop and remove the unsafe signals listed in unsafe_fragments_detected "
    "before continuing statistical profit proof work."
)
SCHEMA_OWNER_ACTION = (
    "Fix the source_quality_gate_result and statistical_surface_overrides "
    "input schema, then rerun the local statistical profit proof gate."
)
EXACT_NEXT_CODEX_PACKET_POLICY = (
    "Codex may only generate or run a future tokenized supervised "
    "compounding policy packet that keeps OANDA, broker calls, credentials, "
    "account IDs, live execution, autonomous execution, compounding "
    "authorization, bank movement, SOS alert sending, schedulers, daemons, "
    "and webhooks forbidden unless Anthony separately approves a new exact "
    "packet under RISK_POLICY.md."
)


@dataclass(frozen=True)
class StatisticalProfitProofGateInput:
    source_quality_gate_result: Any
    statistical_surface_overrides: Mapping[str, bool] = field(default_factory=dict)
    owner_statistical_label: str = "pending_owner_review"
    owner_notes_sanitized: str = ""


@dataclass(frozen=True)
class StatisticalProfitProofGateResult:
    version: str
    packet_id: str
    classification: str
    statistical_status: str
    ready_surface_count: int
    total_surface_count: int
    statistical_percent: float
    ready_surfaces: tuple[str, ...]
    missing_surfaces: tuple[str, ...]
    blocked_surfaces: tuple[str, ...]
    unsafe_fragments_detected: tuple[str, ...]
    source_quality_classification: str
    source_quality_percent: float
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
    compounding_authorized: bool
    autonomous_execution_authorized: bool
    vacation_mode_execution_authorized: bool
    sos_alert_sent: bool
    live_trading_allowed: bool
    live_execution_allowed: bool
    broker_action_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool
    autonomous_execution_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    scheduler_allowed: bool
    daemon_allowed: bool
    webhook_allowed: bool
    unattended_vacation_mode_allowed: bool
    vacation_profit_trial_allowed: bool
    next_trade_authorized: bool
    repeat_trade_authorized: bool
    selected_packet_execution_authorized: bool
    codex_live_execution_authorized: bool
    owner_live_execution_approval_present: bool
    statistical_profit_gate_authorizes_trading: bool
    statistical_profit_gate_authorizes_execution: bool
    statistical_profit_gate_authorizes_compounding: bool
    statistical_profit_gate_authorizes_vacation_mode: bool


@dataclass(frozen=True)
class _SchemaState:
    invalid: bool
    missing_or_invalid: tuple[str, ...]


def build_sample_ready_input() -> StatisticalProfitProofGateInput:
    source_result = evaluate_forex_evidence_depth_quality_gate(
        build_quality_sample_ready_input()
    )
    return StatisticalProfitProofGateInput(
        source_quality_gate_result=source_result,
        statistical_surface_overrides={},
        owner_statistical_label="pending_owner_review",
        owner_notes_sanitized="sanitized statistical profit proof preview",
    )


def build_sample_partial_input() -> StatisticalProfitProofGateInput:
    source_result = evaluate_forex_evidence_depth_quality_gate(
        build_quality_sample_partial_input()
    )
    return StatisticalProfitProofGateInput(
        source_quality_gate_result=source_result,
        statistical_surface_overrides={},
        owner_statistical_label="pending_more_evidence",
        owner_notes_sanitized="safe incomplete statistical profit proof preview",
    )


def build_sample_unsafe_input() -> StatisticalProfitProofGateInput:
    source_result = evaluate_forex_evidence_depth_quality_gate(
        build_quality_sample_unsafe_input()
    )
    return StatisticalProfitProofGateInput(
        source_quality_gate_result=source_result,
        statistical_surface_overrides={
            "broker_action_blocked": False,
            "live_execution_blocked": False,
            "compounding_blocked": False,
            "autonomous_execution_blocked": False,
            "vacation_authorization_blocked": False,
        },
        owner_statistical_label="pending_owner_review",
        owner_notes_sanitized=(
            "Authorization Bearer blocked sample with account_id and live "
            "authorization markers"
        ),
    )


def build_sample_schema_invalid_input() -> Mapping[str, Any]:
    return {
        "source_quality_gate_result": {
            "classification": 123,
            "quality_percent": "one hundred",
            "ready_surface_count": "thirty-two",
            "ready_surfaces": "not-a-list",
            "unsafe_fragments_detected": "schema-invalid",
        },
        "statistical_surface_overrides": {
            "minimum_trade_count_met": "yes",
            "unknown_statistical_surface": True,
        },
        "owner_statistical_label": "schema-invalid",
        "owner_notes_sanitized": "schema invalid sample",
    }


def evaluate_forex_statistical_profit_proof_gate(
    gate_input: StatisticalProfitProofGateInput | Mapping[str, Any] | None = None,
) -> StatisticalProfitProofGateResult:
    active_input = _coerce_input(gate_input or build_sample_ready_input())
    schema = _validate_schema(active_input)
    source = active_input.source_quality_gate_result
    source_values = _source_values(source)
    surfaces = _statistical_surfaces(source, source_values)
    override_errors = _apply_statistical_surface_overrides(
        surfaces, active_input.statistical_surface_overrides
    )
    if override_errors:
        schema = _SchemaState(
            invalid=True,
            missing_or_invalid=_unique_tuple(schema.missing_or_invalid + override_errors),
        )

    unsafe_fragments = _unsafe_fragments(active_input, source)
    ready_surfaces = tuple(
        name for name in STATISTICAL_SURFACES if surfaces.get(name) is True
    )
    not_ready_surfaces = tuple(
        name for name in STATISTICAL_SURFACES if surfaces.get(name) is not True
    )

    if schema.invalid:
        classification = STATISTICAL_PROFIT_BLOCKED_SCHEMA_INVALID
        statistical_status = "blocked_schema_invalid"
        missing_surfaces = not_ready_surfaces
        blocked_surfaces: tuple[str, ...] = ()
        unsafe_output = schema.missing_or_invalid
        next_owner_action = SCHEMA_OWNER_ACTION
    elif unsafe_fragments:
        classification = STATISTICAL_PROFIT_BLOCKED_UNSAFE
        statistical_status = "blocked_unsafe_fail_closed"
        missing_surfaces = ()
        blocked_surfaces = not_ready_surfaces or ("unsafe_payload_absent",)
        unsafe_output = unsafe_fragments
        next_owner_action = UNSAFE_OWNER_ACTION
    elif len(ready_surfaces) == len(STATISTICAL_SURFACES):
        classification = STATISTICAL_PROFIT_PROOF_READY
        statistical_status = "all_statistical_surfaces_ready_build_only"
        missing_surfaces = ()
        blocked_surfaces = ()
        unsafe_output = ()
        next_owner_action = READY_OWNER_ACTION
    else:
        classification = STATISTICAL_PROFIT_REQUIRE_MORE_EVIDENCE
        statistical_status = "safe_more_statistical_evidence_required"
        missing_surfaces = not_ready_surfaces
        blocked_surfaces = ()
        unsafe_output = ()
        next_owner_action = PARTIAL_OWNER_ACTION

    protected_flags = protected_flags_false()
    return StatisticalProfitProofGateResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=classification,
        statistical_status=statistical_status,
        ready_surface_count=len(ready_surfaces),
        total_surface_count=len(STATISTICAL_SURFACES),
        statistical_percent=_statistical_percent(len(ready_surfaces)),
        ready_surfaces=ready_surfaces,
        missing_surfaces=missing_surfaces,
        blocked_surfaces=blocked_surfaces,
        unsafe_fragments_detected=unsafe_output,
        source_quality_classification=source_values["classification"],
        source_quality_percent=source_values["quality_percent"],
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
        compounding_authorized=False,
        autonomous_execution_authorized=False,
        vacation_mode_execution_authorized=False,
        sos_alert_sent=False,
        **protected_flags,
    )


def protected_flags_false() -> dict[str, bool]:
    return {name: False for name in PROTECTED_FLAG_NAMES}


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return _jsonable(result)


def to_operator_text(result: StatisticalProfitProofGateResult) -> str:
    return "\n".join(
        (
            f"Statistical profit proof classification: {result.classification}.",
            f"Statistical surfaces: {result.ready_surface_count}/"
            f"{result.total_surface_count} ({result.statistical_percent:.2f}%).",
            result.one_sentence_answer,
            result.next_safe_action,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
            "No SOS alert was sent by this packet.",
            "All protected flags remain false.",
        )
    )


def to_markdown(result: StatisticalProfitProofGateResult) -> str:
    rows = [
        "# AIOS Forex Statistical Profit Proof Gate V1",
        "",
        f"- Packet ID: `{result.packet_id}`",
        f"- Version: `{result.version}`",
        f"- Classification: `{result.classification}`",
        f"- Statistical status: `{result.statistical_status}`",
        f"- Ready surfaces: `{result.ready_surface_count}`",
        f"- Total surfaces: `{result.total_surface_count}`",
        f"- Statistical percent: `{result.statistical_percent:.2f}`",
        f"- Source quality classification: `{result.source_quality_classification}`",
        f"- Source quality percent: `{result.source_quality_percent:.2f}`",
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
        "- Build-only statistical profit proof evaluation.",
        "- No trade placed by this packet.",
        "- No OANDA call was made by this packet.",
        "- No broker call was made by this packet.",
        "- No credential access occurred.",
        "- No .env read occurred.",
        "- No account ID was persisted.",
        "- No live approval was granted.",
        "- No autonomous execution was approved.",
        "- No compounding approval was granted.",
        "- No Vacation Mode execution was authorized.",
        "- No SOS alert was sent.",
        "- No scheduler, daemon, or webhook was created.",
        "- All protected flags remain false.",
    ]


def _coerce_input(
    value: StatisticalProfitProofGateInput | Mapping[str, Any],
) -> StatisticalProfitProofGateInput:
    if isinstance(value, StatisticalProfitProofGateInput):
        return value
    if isinstance(value, Mapping):
        raw = dict(value)
    else:
        raw = {
            "source_quality_gate_result": getattr(
                value, "source_quality_gate_result", None
            ),
            "statistical_surface_overrides": getattr(
                value, "statistical_surface_overrides", {}
            ),
            "owner_statistical_label": getattr(
                value, "owner_statistical_label", "pending_owner_review"
            ),
            "owner_notes_sanitized": getattr(value, "owner_notes_sanitized", ""),
        }
    overrides = raw.get("statistical_surface_overrides", {})
    return StatisticalProfitProofGateInput(
        source_quality_gate_result=raw.get("source_quality_gate_result"),
        statistical_surface_overrides=(
            dict(overrides) if isinstance(overrides, Mapping) else {}
        ),
        owner_statistical_label=_safe_owner_statistical_label(
            raw.get("owner_statistical_label", "pending_owner_review")
        ),
        owner_notes_sanitized=_text(raw.get("owner_notes_sanitized", "")),
    )


def _validate_schema(active_input: StatisticalProfitProofGateInput) -> _SchemaState:
    invalid: list[str] = []
    source = active_input.source_quality_gate_result
    for field_name in (
        "classification",
        "quality_percent",
        "ready_surface_count",
        "total_surface_count",
        "ready_surfaces",
        "missing_surfaces",
        "blocked_surfaces",
        "unsafe_fragments_detected",
        "protected_flags",
        "source_total_net_pnl_after_costs",
        "source_average_r_multiple",
    ):
        if not _has_field(source, field_name):
            invalid.append(f"source_quality_gate_result.{field_name}_missing")

    classification = _field(source, "classification")
    if not isinstance(classification, str):
        invalid.append("source_quality_gate_result.classification_not_string")
    elif classification not in (
        EVIDENCE_DEPTH_QUALITY_READY,
        SOURCE_MORE_EVIDENCE_CLASSIFICATION,
        EVIDENCE_DEPTH_BLOCKED_UNSAFE,
        EVIDENCE_DEPTH_BLOCKED_SCHEMA_INVALID,
    ):
        invalid.append("source_quality_gate_result.classification_unknown")
    elif classification == EVIDENCE_DEPTH_BLOCKED_SCHEMA_INVALID:
        invalid.append("source_quality_gate_result.classification_schema_invalid")

    if _number_or_none(_field(source, "quality_percent")) is None:
        invalid.append("source_quality_gate_result.quality_percent_not_numeric")
    for field_name in ("ready_surface_count", "total_surface_count"):
        if not _is_integer(_field(source, field_name)):
            invalid.append(f"source_quality_gate_result.{field_name}_not_integer")
    if (
        _is_integer(_field(source, "ready_surface_count"))
        and _is_integer(_field(source, "total_surface_count"))
        and _field(source, "ready_surface_count") > _field(source, "total_surface_count")
    ):
        invalid.append("source_quality_gate_result.ready_count_exceeds_total")

    for field_name in (
        "ready_surfaces",
        "missing_surfaces",
        "blocked_surfaces",
        "unsafe_fragments_detected",
    ):
        if not isinstance(_field(source, field_name), tuple | list):
            invalid.append(f"source_quality_gate_result.{field_name}_not_sequence")
    if not isinstance(_field(source, "protected_flags"), Mapping):
        invalid.append("source_quality_gate_result.protected_flags_not_mapping")
    for field_name in ("source_total_net_pnl_after_costs", "source_average_r_multiple"):
        if _decimal_or_none(_field(source, field_name)) is None:
            invalid.append(f"source_quality_gate_result.{field_name}_invalid_decimal")
    if not isinstance(active_input.statistical_surface_overrides, Mapping):
        invalid.append("statistical_surface_overrides_not_mapping")
    return _SchemaState(invalid=bool(invalid), missing_or_invalid=_unique_tuple(invalid))


def _statistical_surfaces(
    source: Any, source_values: Mapping[str, Any]
) -> dict[str, bool]:
    source_ready = set(_unique_tuple(_field(source, "ready_surfaces", ())))
    source_flags = _field(source, "protected_flags", {})
    if not isinstance(source_flags, Mapping):
        source_flags = {}
    source_classification = source_values["classification"]
    source_quality_ready = (
        source_classification == EVIDENCE_DEPTH_QUALITY_READY
        and source_values["ready_surface_count"] == source_values["total_surface_count"]
        and source_values["quality_percent"] == 100.0
    )
    source_unsafe_clean = (
        source_classification != EVIDENCE_DEPTH_BLOCKED_UNSAFE
        and "unsafe_payload_absent" in source_ready
        and not _field(source, "unsafe_fragments_detected", ())
    )
    source_schema_clean = (
        source_classification != EVIDENCE_DEPTH_BLOCKED_SCHEMA_INVALID
        and "schema_integrity_ready" in source_ready
    )
    source_protected_false = bool(source_flags) and all(
        value is False for value in source_flags.values()
    )
    total_pnl = (
        _decimal_or_none(_field(source, "source_total_net_pnl_after_costs", "0"))
        or Decimal("0")
    )
    average_r = (
        _decimal_or_none(_field(source, "source_average_r_multiple", "0"))
        or Decimal("0")
    )
    positive_pnl = total_pnl > Decimal("0")
    positive_r = average_r > Decimal("0")
    profit_factor_ready = "profit_factor_ready" in source_ready
    drawdown_ready = "max_drawdown_ready" in source_ready
    drawdown_recovered = "drawdown_recovery_ready" in source_ready
    distribution_ready = (
        "win_loss_distribution_ready" in source_ready
        and "risk_reward_distribution_ready" in source_ready
        and "profit_outcome_present" in source_ready
        and "loss_outcome_present" in source_ready
        and "breakeven_outcome_present" in source_ready
    )

    return {
        "minimum_trade_count_met": "minimum_sanitized_result_count_met" in source_ready,
        "minimum_session_count_met": (
            "minimum_independent_session_count_met" in source_ready
        ),
        "minimum_market_bucket_count_met": (
            "minimum_market_condition_bucket_count_met" in source_ready
        ),
        "positive_total_net_pnl_after_costs": positive_pnl
        and "positive_total_net_pnl_after_costs" in source_ready,
        "positive_average_r_multiple": positive_r
        and "positive_average_r_multiple" in source_ready,
        "positive_expectancy": positive_pnl
        and positive_r
        and "expectancy_ready" in source_ready,
        "profit_factor_threshold_met": profit_factor_ready,
        "win_rate_reasonable": "win_loss_distribution_ready" in source_ready,
        "average_win_loss_ratio_ready": (
            "risk_reward_distribution_ready" in source_ready
        ),
        "max_drawdown_threshold_met": drawdown_ready,
        "drawdown_recovery_ready": drawdown_recovered,
        "losing_streak_threshold_met": drawdown_ready and drawdown_recovered,
        "result_distribution_ready": distribution_ready,
        "outlier_control_ready": "outlier_detection_ready" in source_ready,
        "overfit_warning_absent": "overfit_warning_absent" in source_ready,
        "walk_forward_support_ready": "walk_forward_support_ready" in source_ready,
        "market_regime_diversity_ready": (
            "market_regime_diversity_ready" in source_ready
        ),
        "session_independence_ready": "session_independence_ready" in source_ready,
        "risk_adjusted_return_ready": (
            positive_pnl
            and positive_r
            and profit_factor_ready
            and drawdown_ready
            and distribution_ready
        ),
        "sample_quality_ready": source_quality_ready,
        "evidence_quality_gate_ready": source_quality_ready,
        "evidence_integrity_ready": "evidence_integrity_ready" in source_ready,
        "schema_integrity_ready": source_schema_clean,
        "unsafe_payload_absent": source_unsafe_clean,
        "required_controls_met": "required_controls_met" in source_ready,
        "required_persistence_absence_met": (
            "required_persistence_absence_met" in source_ready
        ),
        "protected_flags_false": source_protected_false
        and "protected_flags_false" in source_ready,
        "broker_action_blocked": source_flags.get("broker_action_allowed") is False
        and "broker_action_blocked" in source_ready,
        "live_execution_blocked": source_flags.get("live_execution_allowed") is False
        and "live_execution_blocked" in source_ready,
        "compounding_blocked": source_flags.get("compounding_allowed") is False
        and "compounding_blocked" in source_ready,
        "autonomous_execution_blocked": (
            source_flags.get("autonomous_execution_allowed") is False
            and "autonomous_execution_blocked" in source_ready
        ),
        "vacation_authorization_blocked": (
            source_flags.get("unattended_vacation_mode_allowed") is False
            and source_flags.get("vacation_profit_trial_allowed") is False
            and "vacation_authorization_blocked" in source_ready
        ),
    }


def _apply_statistical_surface_overrides(
    surfaces: dict[str, bool], overrides: Mapping[str, Any]
) -> tuple[str, ...]:
    errors: list[str] = []
    for name, value in overrides.items():
        if name not in STATISTICAL_SURFACES:
            errors.append(f"statistical_surface_overrides.{name}_unknown")
            continue
        if not isinstance(value, bool):
            errors.append(f"statistical_surface_overrides.{name}_not_boolean")
            continue
        surfaces[name] = value
    return tuple(errors)


def _source_values(source: Any) -> dict[str, Any]:
    return {
        "classification": _text(_field(source, "classification", "")),
        "quality_percent": _safe_float(_field(source, "quality_percent", 0)),
        "ready_surface_count": _safe_int(_field(source, "ready_surface_count", 0)),
        "total_surface_count": _safe_int(_field(source, "total_surface_count", 0)),
    }


def _unsafe_fragments(
    active_input: StatisticalProfitProofGateInput, source: Any
) -> tuple[str, ...]:
    fragments: list[str] = []
    fragments.extend(_source_unsafe_fragments(source))
    source_classification = _field(source, "classification", "")
    if source_classification == EVIDENCE_DEPTH_BLOCKED_UNSAFE:
        fragments.append("source_quality_gate_result.classification:block_unsafe")
    source_flags = _field(source, "protected_flags", {})
    if isinstance(source_flags, Mapping):
        fragments.extend(
            f"source_quality_gate_result.protected_flags.{name}:true"
            for name, value in source_flags.items()
            if value is True
        )
    fragments.extend(
        f"statistical_surface_overrides.{name}:false"
        for name, value in active_input.statistical_surface_overrides.items()
        if name in PROTECTIVE_SURFACES and value is False
    )
    fragments.extend(
        _scan_string_value(
            "owner_statistical_label", active_input.owner_statistical_label
        )
    )
    fragments.extend(
        _scan_string_value("owner_notes_sanitized", active_input.owner_notes_sanitized)
    )
    return _unique_tuple(fragments)


def _source_unsafe_fragments(source: Any) -> tuple[str, ...]:
    raw = _field(source, "unsafe_fragments_detected", ())
    if isinstance(raw, str):
        return (f"source_quality_gate_result.unsafe_fragments_detected:{raw}",)
    if isinstance(raw, tuple | list):
        return tuple(
            f"source_quality_gate_result.unsafe_fragments_detected:{_text(item)}"
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


def _safe_owner_statistical_label(value: Any) -> str:
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


def _statistical_percent(ready_count: int) -> float:
    return round((ready_count / len(STATISTICAL_SURFACES)) * 100, 2)


def _one_sentence_answer(classification: str) -> str:
    if classification == STATISTICAL_PROFIT_PROOF_READY:
        return (
            "AIOS sanitized evidence is statistically profit-proof-ready for "
            "a future supervised compounding policy review, but this gate "
            "authorizes no trading, live execution, compounding, SOS "
            "alerting, or Vacation Mode execution."
        )
    if classification == STATISTICAL_PROFIT_REQUIRE_MORE_EVIDENCE:
        return (
            "AIOS sanitized evidence is safe but not statistically "
            "profit-proof-ready because one or more statistical surfaces "
            "need more evidence."
        )
    if classification == STATISTICAL_PROFIT_BLOCKED_UNSAFE:
        return (
            "AIOS statistical profit proof is blocked because unsafe "
            "credential, broker, account, live execution, autonomy, "
            "compounding, or automation signals were detected."
        )
    return (
        "AIOS statistical profit proof cannot be evaluated until the "
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
