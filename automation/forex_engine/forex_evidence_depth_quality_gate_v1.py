"""Evidence-depth quality gate for build-only AIOS Forex review."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from automation.forex_engine.oanda_live_microtrade_profit_proof_evidence_depth_collection_v1 import (
    build_sample_complete_collection_input,
    build_sample_partial_collection_input,
    build_sample_schema_invalid_collection_input,
    build_sample_unsafe_collection_input,
    evaluate_oanda_live_microtrade_profit_proof_evidence_depth_collection,
)


VERSION = "forex_evidence_depth_quality_gate_v1"
PACKET_ID = "AIOS-FOREX-EVIDENCE-DEPTH-QUALITY-GATE-V1"
NEXT_PACKET_PREVIEW = "AIOS-FOREX-STATISTICAL-PROFIT-PROOF-GATE-V1"

EVIDENCE_DEPTH_QUALITY_READY = "EVIDENCE_DEPTH_QUALITY_READY"
EVIDENCE_DEPTH_REQUIRE_MORE_EVIDENCE = "EVIDENCE_DEPTH_REQUIRE_MORE_EVIDENCE"
EVIDENCE_DEPTH_BLOCKED_UNSAFE = "EVIDENCE_DEPTH_BLOCKED_UNSAFE"
EVIDENCE_DEPTH_BLOCKED_SCHEMA_INVALID = "EVIDENCE_DEPTH_BLOCKED_SCHEMA_INVALID"

SOURCE_READY_CLASSIFICATION = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_READY_FOR_OWNER_REVIEW"
)
SOURCE_MORE_EVIDENCE_CLASSIFICATION = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_REQUIRE_MORE_EVIDENCE"
)
SOURCE_UNSAFE_CLASSIFICATION = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_UNSAFE"
)
SOURCE_SCHEMA_INVALID_CLASSIFICATION = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_SCHEMA_INVALID"
)

QUALITY_SURFACES = (
    "minimum_sanitized_result_count_met",
    "minimum_independent_session_count_met",
    "minimum_market_condition_bucket_count_met",
    "profit_outcome_present",
    "loss_outcome_present",
    "breakeven_outcome_present",
    "positive_total_net_pnl_after_costs",
    "positive_average_r_multiple",
    "profit_factor_ready",
    "expectancy_ready",
    "max_drawdown_ready",
    "drawdown_recovery_ready",
    "win_loss_distribution_ready",
    "risk_reward_distribution_ready",
    "outlier_detection_ready",
    "overfit_warning_absent",
    "session_independence_ready",
    "market_regime_diversity_ready",
    "time_distribution_ready",
    "instrument_scope_ready",
    "walk_forward_support_ready",
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
    "evidence_quality_gate_authorizes_trading",
    "evidence_quality_gate_authorizes_execution",
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
    "statistical_profitability_final",
    "production_readiness",
    "vacation_mode_readiness",
    "autonomous_trading_readiness",
    "compounding_readiness",
    "live_execution_readiness",
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

READY_OWNER_ACTION = (
    "Review the sanitized evidence-depth quality result and decide whether to "
    "request the separate statistical profit proof gate; do not approve broker "
    "access, live execution, compounding, autonomous execution, SOS alerting, "
    "or Vacation Mode execution from this gate."
)
PARTIAL_OWNER_ACTION = (
    "Close the missing quality surfaces listed in missing_surfaces, then rerun "
    "this local evidence-depth quality gate before requesting a statistical "
    "profit proof gate."
)
UNSAFE_OWNER_ACTION = (
    "Stop and remove the unsafe signals listed in unsafe_fragments_detected "
    "before continuing evidence-depth quality work."
)
SCHEMA_OWNER_ACTION = (
    "Fix the source_collection_result and quality_surface_overrides input "
    "schema, then rerun the local evidence-depth quality gate."
)
EXACT_NEXT_CODEX_PACKET_POLICY = (
    "Codex may only generate or run a future tokenized statistical profit "
    "proof packet that keeps OANDA, broker calls, credentials, account IDs, "
    "live execution, autonomous execution, compounding, bank movement, SOS "
    "alert sending, schedulers, daemons, and webhooks forbidden unless "
    "Anthony separately approves a new exact packet under RISK_POLICY.md."
)


@dataclass(frozen=True)
class EvidenceDepthQualityGateInput:
    source_collection_result: Any
    quality_surface_overrides: Mapping[str, bool] = field(default_factory=dict)
    owner_quality_label: str = "pending_owner_review"
    owner_notes_sanitized: str = ""


@dataclass(frozen=True)
class EvidenceDepthQualityGateResult:
    version: str
    packet_id: str
    classification: str
    quality_status: str
    ready_surface_count: int
    total_surface_count: int
    quality_percent: float
    ready_surfaces: tuple[str, ...]
    missing_surfaces: tuple[str, ...]
    blocked_surfaces: tuple[str, ...]
    unsafe_fragments_detected: tuple[str, ...]
    source_collection_classification: str
    source_sanitized_result_count: int
    source_independent_session_count: int
    source_market_condition_bucket_count: int
    source_total_net_pnl_after_costs: str
    source_average_r_multiple: str
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
    evidence_quality_gate_authorizes_trading: bool
    evidence_quality_gate_authorizes_execution: bool


@dataclass(frozen=True)
class _SchemaState:
    invalid: bool
    missing_or_invalid: tuple[str, ...]


def build_sample_ready_input() -> EvidenceDepthQualityGateInput:
    source_result = evaluate_oanda_live_microtrade_profit_proof_evidence_depth_collection(
        build_sample_complete_collection_input()
    )
    return EvidenceDepthQualityGateInput(
        source_collection_result=source_result,
        quality_surface_overrides={},
        owner_quality_label="pending_owner_review",
        owner_notes_sanitized="sanitized quality gate preview",
    )


def build_sample_partial_input() -> EvidenceDepthQualityGateInput:
    source_result = evaluate_oanda_live_microtrade_profit_proof_evidence_depth_collection(
        build_sample_partial_collection_input()
    )
    return EvidenceDepthQualityGateInput(
        source_collection_result=source_result,
        quality_surface_overrides={},
        owner_quality_label="pending_more_evidence",
        owner_notes_sanitized="safe incomplete quality gate preview",
    )


def build_sample_unsafe_input() -> EvidenceDepthQualityGateInput:
    source_result = evaluate_oanda_live_microtrade_profit_proof_evidence_depth_collection(
        build_sample_unsafe_collection_input()
    )
    return EvidenceDepthQualityGateInput(
        source_collection_result=source_result,
        quality_surface_overrides={
            "broker_action_blocked": False,
            "live_execution_blocked": False,
            "compounding_blocked": False,
            "autonomous_execution_blocked": False,
            "vacation_authorization_blocked": False,
        },
        owner_quality_label="pending_owner_review",
        owner_notes_sanitized=(
            "Authorization Bearer blocked sample with account_id and live "
            "authorization markers"
        ),
    )


def build_sample_schema_invalid_input() -> Mapping[str, Any]:
    return {
        "source_collection_result": {
            "classification": 123,
            "sanitized_result_count": "thirty",
        },
        "quality_surface_overrides": {
            "minimum_sanitized_result_count_met": "yes",
            "unknown_quality_surface": True,
        },
        "owner_quality_label": "schema-invalid",
        "owner_notes_sanitized": "schema invalid sample",
    }


def evaluate_forex_evidence_depth_quality_gate(
    gate_input: EvidenceDepthQualityGateInput | Mapping[str, Any] | None = None,
) -> EvidenceDepthQualityGateResult:
    active_input = _coerce_input(gate_input or build_sample_ready_input())
    schema = _validate_schema(active_input)
    source = active_input.source_collection_result
    source_values = _source_values(source)
    surfaces = _quality_surfaces(source, source_values)
    override_errors = _apply_quality_surface_overrides(
        surfaces, active_input.quality_surface_overrides
    )
    if override_errors:
        schema = _SchemaState(
            invalid=True,
            missing_or_invalid=_unique_tuple(schema.missing_or_invalid + override_errors),
        )

    unsafe_fragments = _unsafe_fragments(active_input, source)
    ready_surfaces = tuple(name for name in QUALITY_SURFACES if surfaces.get(name) is True)
    not_ready_surfaces = tuple(
        name for name in QUALITY_SURFACES if surfaces.get(name) is not True
    )

    if schema.invalid:
        classification = EVIDENCE_DEPTH_BLOCKED_SCHEMA_INVALID
        quality_status = "blocked_schema_invalid"
        missing_surfaces = not_ready_surfaces
        blocked_surfaces: tuple[str, ...] = ()
        unsafe_output = schema.missing_or_invalid
        next_owner_action = SCHEMA_OWNER_ACTION
    elif unsafe_fragments:
        classification = EVIDENCE_DEPTH_BLOCKED_UNSAFE
        quality_status = "blocked_unsafe_fail_closed"
        missing_surfaces = ()
        blocked_surfaces = not_ready_surfaces or ("evidence_integrity_ready",)
        unsafe_output = unsafe_fragments
        next_owner_action = UNSAFE_OWNER_ACTION
    elif len(ready_surfaces) == len(QUALITY_SURFACES):
        classification = EVIDENCE_DEPTH_QUALITY_READY
        quality_status = "all_quality_surfaces_ready_build_only"
        missing_surfaces = ()
        blocked_surfaces = ()
        unsafe_output = ()
        next_owner_action = READY_OWNER_ACTION
    else:
        classification = EVIDENCE_DEPTH_REQUIRE_MORE_EVIDENCE
        quality_status = "safe_more_quality_evidence_required"
        missing_surfaces = not_ready_surfaces
        blocked_surfaces = ()
        unsafe_output = ()
        next_owner_action = PARTIAL_OWNER_ACTION

    protected_flags = protected_flags_false()
    return EvidenceDepthQualityGateResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=classification,
        quality_status=quality_status,
        ready_surface_count=len(ready_surfaces),
        total_surface_count=len(QUALITY_SURFACES),
        quality_percent=_quality_percent(len(ready_surfaces)),
        ready_surfaces=ready_surfaces,
        missing_surfaces=missing_surfaces,
        blocked_surfaces=blocked_surfaces,
        unsafe_fragments_detected=unsafe_output,
        source_collection_classification=source_values["classification"],
        source_sanitized_result_count=source_values["sanitized_result_count"],
        source_independent_session_count=source_values["independent_session_count"],
        source_market_condition_bucket_count=source_values[
            "market_condition_bucket_count"
        ],
        source_total_net_pnl_after_costs=source_values["total_net_pnl_after_costs"],
        source_average_r_multiple=source_values["average_r_multiple"],
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


def to_operator_text(result: EvidenceDepthQualityGateResult) -> str:
    return "\n".join(
        (
            f"Evidence-depth quality classification: {result.classification}.",
            f"Quality: {result.ready_surface_count}/{result.total_surface_count} "
            f"surfaces ({result.quality_percent:.2f}%).",
            result.one_sentence_answer,
            result.next_safe_action,
            "No trade placed by this packet.",
            "No broker call was made by this packet.",
            "No SOS alert was sent by this packet.",
            "All protected flags remain false.",
        )
    )


def to_markdown(result: EvidenceDepthQualityGateResult) -> str:
    rows = [
        "# AIOS Forex Evidence Depth Quality Gate V1",
        "",
        f"- Packet ID: `{result.packet_id}`",
        f"- Version: `{result.version}`",
        f"- Classification: `{result.classification}`",
        f"- Quality status: `{result.quality_status}`",
        f"- Ready surfaces: `{result.ready_surface_count}`",
        f"- Total surfaces: `{result.total_surface_count}`",
        f"- Quality percent: `{result.quality_percent:.2f}`",
        f"- Source collection classification: `{result.source_collection_classification}`",
        f"- Source sanitized result count: `{result.source_sanitized_result_count}`",
        f"- Source independent session count: `{result.source_independent_session_count}`",
        (
            "- Source market condition bucket count: "
            f"`{result.source_market_condition_bucket_count}`"
        ),
        f"- Source total net PnL after costs: `{result.source_total_net_pnl_after_costs}`",
        f"- Source average R multiple: `{result.source_average_r_multiple}`",
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
        "- Build-only evidence-depth quality evaluation.",
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
    value: EvidenceDepthQualityGateInput | Mapping[str, Any],
) -> EvidenceDepthQualityGateInput:
    if isinstance(value, EvidenceDepthQualityGateInput):
        return value
    raw = dict(value)
    overrides = raw.get("quality_surface_overrides", {})
    return EvidenceDepthQualityGateInput(
        source_collection_result=raw.get("source_collection_result"),
        quality_surface_overrides=dict(overrides) if isinstance(overrides, Mapping) else {},
        owner_quality_label=_safe_owner_quality_label(
            raw.get("owner_quality_label", "pending_owner_review")
        ),
        owner_notes_sanitized=_text(raw.get("owner_notes_sanitized", "")),
    )


def _validate_schema(active_input: EvidenceDepthQualityGateInput) -> _SchemaState:
    invalid: list[str] = []
    source = active_input.source_collection_result
    for field_name in (
        "classification",
        "sanitized_result_count",
        "independent_session_count",
        "market_condition_bucket_count",
        "total_net_pnl_after_costs",
        "average_r_multiple",
        "outcome_bucket_counts",
        "minimum_counts_met",
        "required_controls_met",
        "required_persistence_absence_met",
        "unsafe_payload_absent",
        "protected_flags",
    ):
        if not _has_field(source, field_name):
            invalid.append(f"source_collection_result.{field_name}_missing")
    if not isinstance(_field(source, "classification"), str):
        invalid.append("source_collection_result.classification_not_string")
    for field_name in (
        "sanitized_result_count",
        "independent_session_count",
        "market_condition_bucket_count",
    ):
        if not isinstance(_field(source, field_name), int):
            invalid.append(f"source_collection_result.{field_name}_not_integer")
    for field_name in ("total_net_pnl_after_costs", "average_r_multiple"):
        if _decimal_or_none(_field(source, field_name)) is None:
            invalid.append(f"source_collection_result.{field_name}_invalid_decimal")
    if not isinstance(_field(source, "outcome_bucket_counts"), Mapping):
        invalid.append("source_collection_result.outcome_bucket_counts_not_mapping")
    for field_name in (
        "minimum_counts_met",
        "required_controls_met",
        "required_persistence_absence_met",
        "unsafe_payload_absent",
    ):
        if not isinstance(_field(source, field_name), bool):
            invalid.append(f"source_collection_result.{field_name}_not_boolean")
    if not isinstance(_field(source, "protected_flags"), Mapping):
        invalid.append("source_collection_result.protected_flags_not_mapping")
    if not isinstance(active_input.quality_surface_overrides, Mapping):
        invalid.append("quality_surface_overrides_not_mapping")
    return _SchemaState(invalid=bool(invalid), missing_or_invalid=_unique_tuple(invalid))


def _quality_surfaces(source: Any, source_values: Mapping[str, Any]) -> dict[str, bool]:
    outcome_counts = _field(source, "outcome_bucket_counts", {})
    if not isinstance(outcome_counts, Mapping):
        outcome_counts = {}
    quality_readiness = _field(source, "quality_gate_readiness", {})
    if not isinstance(quality_readiness, Mapping):
        quality_readiness = {}
    protected_flags = _field(source, "protected_flags", {})
    if not isinstance(protected_flags, Mapping):
        protected_flags = {}

    profit_count = _int_mapping_value(outcome_counts, "profit")
    loss_count = _int_mapping_value(outcome_counts, "loss")
    breakeven_count = _int_mapping_value(outcome_counts, "breakeven")
    total_pnl = _decimal_or_none(source_values["total_net_pnl_after_costs"]) or Decimal("0")
    average_r = _decimal_or_none(source_values["average_r_multiple"]) or Decimal("0")
    minimum_counts = bool(_field(source, "minimum_counts_met", False))
    required_controls = bool(_field(source, "required_controls_met", False))
    persistence_absence = bool(_field(source, "required_persistence_absence_met", False))
    unsafe_absent = bool(_field(source, "unsafe_payload_absent", False))
    source_classification = source_values["classification"]
    protected_false = all(value is False for value in protected_flags.values())
    source_schema_clean = (
        source_classification != SOURCE_SCHEMA_INVALID_CLASSIFICATION
        and not _field(source, "missing_required_fields", ())
    )
    source_unsafe_clean = (
        source_classification != SOURCE_UNSAFE_CLASSIFICATION
        and unsafe_absent
        and not _field(source, "unsafe_fragments_detected", ())
    )

    return {
        "minimum_sanitized_result_count_met": (
            source_values["sanitized_result_count"] >= 30
        ),
        "minimum_independent_session_count_met": (
            source_values["independent_session_count"] >= 10
        ),
        "minimum_market_condition_bucket_count_met": (
            source_values["market_condition_bucket_count"] >= 3
        ),
        "profit_outcome_present": profit_count > 0,
        "loss_outcome_present": loss_count > 0,
        "breakeven_outcome_present": breakeven_count > 0,
        "positive_total_net_pnl_after_costs": total_pnl > Decimal("0"),
        "positive_average_r_multiple": average_r > Decimal("0"),
        "profit_factor_ready": bool(quality_readiness.get("profit_factor_gate", False)),
        "expectancy_ready": total_pnl > Decimal("0") and average_r > Decimal("0"),
        "max_drawdown_ready": bool(quality_readiness.get("max_drawdown_gate", False)),
        "drawdown_recovery_ready": minimum_counts and loss_count > 0 and total_pnl > Decimal("0"),
        "win_loss_distribution_ready": profit_count > loss_count > 0 and breakeven_count > 0,
        "risk_reward_distribution_ready": (
            profit_count > 0
            and loss_count > 0
            and average_r > Decimal("0")
            and bool(quality_readiness.get("profit_factor_gate", False))
        ),
        "outlier_detection_ready": bool(
            quality_readiness.get("outlier_dependency_gate", False)
        ),
        "overfit_warning_absent": minimum_counts
        and source_values["independent_session_count"] >= 10
        and source_values["market_condition_bucket_count"] >= 3,
        "session_independence_ready": source_values["independent_session_count"] >= 10,
        "market_regime_diversity_ready": (
            source_values["market_condition_bucket_count"] >= 3
        ),
        "time_distribution_ready": minimum_counts
        and source_values["independent_session_count"] >= 10,
        "instrument_scope_ready": source_values["sanitized_result_count"] > 0
        and source_unsafe_clean,
        "walk_forward_support_ready": minimum_counts
        and bool(quality_readiness.get("sample_sufficiency_gate", False)),
        "evidence_integrity_ready": source_unsafe_clean and required_controls,
        "schema_integrity_ready": source_schema_clean,
        "unsafe_payload_absent": source_unsafe_clean,
        "required_controls_met": required_controls,
        "required_persistence_absence_met": persistence_absence,
        "protected_flags_false": protected_false,
        "broker_action_blocked": protected_flags.get("broker_action_allowed") is False,
        "live_execution_blocked": protected_flags.get("live_execution_allowed") is False,
        "compounding_blocked": protected_flags.get("compounding_allowed") is False,
        "autonomous_execution_blocked": (
            protected_flags.get("autonomous_execution_allowed") is False
        ),
        "vacation_authorization_blocked": (
            protected_flags.get("unattended_vacation_mode_allowed") is False
            and protected_flags.get("vacation_profit_trial_allowed") is False
        ),
    }


def _apply_quality_surface_overrides(
    surfaces: dict[str, bool], overrides: Mapping[str, Any]
) -> tuple[str, ...]:
    errors: list[str] = []
    for name, value in overrides.items():
        if name not in QUALITY_SURFACES:
            errors.append(f"quality_surface_overrides.{name}_unknown")
            continue
        if not isinstance(value, bool):
            errors.append(f"quality_surface_overrides.{name}_not_boolean")
            continue
        surfaces[name] = value
    return tuple(errors)


def _source_values(source: Any) -> dict[str, Any]:
    return {
        "classification": _text(_field(source, "classification", "")),
        "sanitized_result_count": _safe_int(_field(source, "sanitized_result_count", 0)),
        "independent_session_count": _safe_int(
            _field(source, "independent_session_count", 0)
        ),
        "market_condition_bucket_count": _safe_int(
            _field(source, "market_condition_bucket_count", 0)
        ),
        "total_net_pnl_after_costs": _decimal_string(
            _decimal_or_none(_field(source, "total_net_pnl_after_costs", "0")) or Decimal("0")
        ),
        "average_r_multiple": _decimal_string(
            _decimal_or_none(_field(source, "average_r_multiple", "0")) or Decimal("0")
        ),
    }


def _unsafe_fragments(active_input: EvidenceDepthQualityGateInput, source: Any) -> tuple[str, ...]:
    fragments: list[str] = []
    fragments.extend(_source_unsafe_fragments(source))
    source_classification = _field(source, "classification", "")
    if source_classification == SOURCE_UNSAFE_CLASSIFICATION:
        fragments.append("source_collection_result.classification:block_unsafe")
    source_flags = _field(source, "protected_flags", {})
    if isinstance(source_flags, Mapping):
        fragments.extend(
            f"source_collection_result.protected_flags.{name}:true"
            for name, value in source_flags.items()
            if value is True
        )
    fragments.extend(
        _scan_string_value("owner_quality_label", active_input.owner_quality_label)
    )
    fragments.extend(
        _scan_string_value("owner_notes_sanitized", active_input.owner_notes_sanitized)
    )
    return _unique_tuple(fragments)


def _source_unsafe_fragments(source: Any) -> tuple[str, ...]:
    raw = _field(source, "unsafe_fragments_detected", ())
    if isinstance(raw, str):
        return (f"source_collection_result.unsafe_fragments_detected:{raw}",)
    if isinstance(raw, tuple | list):
        return tuple(
            f"source_collection_result.unsafe_fragments_detected:{_text(item)}"
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


def _int_mapping_value(values: Mapping[str, Any], name: str) -> int:
    raw = values.get(name, 0)
    return raw if isinstance(raw, int) else 0


def _safe_int(value: Any) -> int:
    return value if isinstance(value, int) else 0


def _safe_owner_quality_label(value: Any) -> str:
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


def _quality_percent(ready_count: int) -> float:
    return round((ready_count / len(QUALITY_SURFACES)) * 100, 2)


def _one_sentence_answer(classification: str) -> str:
    if classification == EVIDENCE_DEPTH_QUALITY_READY:
        return (
            "AIOS sanitized evidence depth is quality-ready for a future "
            "statistical profit proof gate, but this gate authorizes no "
            "trading, live execution, compounding, SOS alerting, or Vacation "
            "Mode execution."
        )
    if classification == EVIDENCE_DEPTH_REQUIRE_MORE_EVIDENCE:
        return (
            "AIOS sanitized evidence depth is safe but not quality-ready "
            "because one or more quality surfaces need more evidence."
        )
    if classification == EVIDENCE_DEPTH_BLOCKED_UNSAFE:
        return (
            "AIOS evidence-depth quality is blocked because unsafe credential, "
            "broker, account, live execution, autonomy, compounding, or "
            "automation signals were detected."
        )
    return (
        "AIOS evidence-depth quality cannot be evaluated until the required "
        "input schema is complete and valid."
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
