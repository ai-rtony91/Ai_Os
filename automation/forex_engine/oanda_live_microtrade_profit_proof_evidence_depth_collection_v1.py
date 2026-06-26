"""Sanitized evidence-depth collection validator for OANDA microtrade proof review."""

from __future__ import annotations

import json
from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping

from automation.forex_engine.oanda_live_microtrade_profit_proof_evidence_depth_plan_v1 import (
    BLOCKED_ACTIONS,
    BLOCKED_CLAIMS,
    EVIDENCE_DEPTH_COLLECTION_PACKET_PREVIEW,
    REQUIRED_BLOCKER_CHECKS,
    REQUIRED_EVIDENCE_CATEGORIES,
    REQUIRED_QUALITY_GATES,
    REQUIRED_RISK_CONTROLS,
    build_oanda_live_microtrade_profit_proof_evidence_depth_plan,
    build_sample_profit_depth_plan_input,
)


VERSION = "oanda_live_microtrade_profit_proof_evidence_depth_collection_v1"
PACKET_ID = (
    "AIOS-FOREX-OANDA-LIVE-MICROTRADE-PROFIT-PROOF-EVIDENCE-DEPTH-COLLECTION-V1"
)

OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_READY_FOR_OWNER_REVIEW = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_READY_FOR_OWNER_REVIEW"
)
OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_REQUIRE_MORE_EVIDENCE = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_REQUIRE_MORE_EVIDENCE"
)
OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_UNSAFE = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_UNSAFE"
)
OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_SCHEMA_INVALID = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_SCHEMA_INVALID"
)

QUALITY_GATE_PACKET_PREVIEW = (
    "AIOS-FOREX-OANDA-LIVE-MICROTRADE-PROFIT-PROOF-EVIDENCE-DEPTH-QUALITY-GATE-V1"
)
ALLOWED_NEXT_HUMAN_ACTION = (
    "Anthony may review the sanitized evidence-depth collection summary and "
    "decide whether to request a future profitability-gate review packet. "
    "This does not approve another trade."
)
EXACT_NEXT_OWNER_ACTION = (
    "Review the sanitized evidence-depth collection summary and decide whether "
    "to request a future quality-gate review packet. This does not approve "
    "another trade, selected packet execution, broker action, or profitability "
    "claims."
)
EXACT_NEXT_CODEX_PACKET_POLICY = (
    "Do not execute any selected proof packet from this collection. Generate "
    "or execute a future quality-gate packet only after Anthony separately "
    "approves the exact next packet."
)
ONE_SENTENCE_ANSWER = (
    "AIOS can now validate a sanitized evidence-depth collection toward proof "
    "review while blocking next-trade authorization, selected-packet execution, "
    "broker action, compounding, vacation mode, bank movement, and statistical "
    "profitability claims."
)
PROOF_WARNING = "Evidence depth collection does not approve another trade."
STATISTICAL_WARNING = (
    "Evidence depth collection does not prove statistical profitability."
)

MARKET_CONDITION_BUCKETS = (
    "trending",
    "ranging",
    "volatile",
    "quiet",
    "news_excluded",
    "other",
)
OUTCOME_BUCKETS = ("profit", "loss", "breakeven")
DIRECTIONS = ("long", "short")
DECIMAL_FIELDS = ("r_multiple", "net_pnl_after_costs")
CONTROL_FIELDS = (
    "max_loss_respected",
    "daily_stop_respected",
    "kill_switch_available",
    "one_order_only_confirmed",
    "no_compounding_confirmed",
    "no_bank_movement_confirmed",
    "no_autonomous_execution_confirmed",
    "owner_approval_separated",
)
PERSISTENCE_ABSENCE_FIELDS = (
    "credential_persistence_absent",
    "account_id_persistence_absent",
    "broker_order_id_persistence_absent",
    "raw_broker_payload_absent",
)
REQUIRED_RESULT_FIELDS = (
    "result_reference",
    "session_reference",
    "market_condition_bucket",
    "outcome_bucket",
    "instrument",
    "direction",
    "r_multiple",
    "net_pnl_after_costs",
    "max_loss_respected",
    "daily_stop_respected",
    "kill_switch_available",
    "one_order_only_confirmed",
    "no_compounding_confirmed",
    "no_bank_movement_confirmed",
    "no_autonomous_execution_confirmed",
    "credential_persistence_absent",
    "account_id_persistence_absent",
    "broker_order_id_persistence_absent",
    "raw_broker_payload_absent",
    "unsafe_payload_absent",
    "owner_approval_separated",
)
STRING_RESULT_FIELDS = (
    "result_reference",
    "session_reference",
    "market_condition_bucket",
    "outcome_bucket",
    "instrument",
    "direction",
    "r_multiple",
    "net_pnl_after_costs",
)
BOOLEAN_RESULT_FIELDS = (
    "max_loss_respected",
    "daily_stop_respected",
    "kill_switch_available",
    "one_order_only_confirmed",
    "no_compounding_confirmed",
    "no_bank_movement_confirmed",
    "no_autonomous_execution_confirmed",
    "credential_persistence_absent",
    "account_id_persistence_absent",
    "broker_order_id_persistence_absent",
    "raw_broker_payload_absent",
    "unsafe_payload_absent",
    "owner_approval_separated",
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
    "fxtrade",
    "raw_transaction_id",
    "raw_order_id",
    "broker_order_id",
    "account_number",
)

PROTECTED_FLAG_NAMES = (
    "demo_execution_allowed",
    "broker_action_allowed",
    "real_money_allowed",
    "compounding_allowed",
    "bank_movement_allowed",
    "live_trading_allowed",
    "live_execution_allowed",
    "credential_access_allowed",
    "account_id_persistence_allowed",
    "autonomous_execution_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "live_micro_trade_exception_allowed",
    "owner_live_execution_approval_present",
    "codex_live_execution_authorized",
    "unattended_vacation_mode_allowed",
    "vacation_profit_trial_allowed",
    "repeat_live_trade_allowed",
    "next_trade_authorized",
    "result_proves_profitability",
    "statistical_profitability_confirmed",
    "selected_packet_execution_authorized",
    "selected_packet_commit_authorized",
    "selected_packet_push_authorized",
    "selected_packet_pr_authorized",
    "selected_packet_merge_authorized",
    "profit_proof_validated_as_statistical",
    "future_profit_claim_allowed",
    "evidence_depth_plan_authorizes_trading",
    "evidence_depth_plan_authorizes_execution",
    "evidence_depth_collection_authorizes_trading",
    "evidence_depth_collection_authorizes_execution",
)


@dataclass(frozen=True)
class OandaLiveMicrotradeProfitProofEvidenceDepthCollectionInput:
    depth_plan_input: Any
    sanitized_results: tuple[Mapping[str, Any], ...]
    owner_collection_label: str = "pending_owner_review"
    owner_notes_sanitized: str = ""


@dataclass(frozen=True)
class OandaLiveMicrotradeProfitProofEvidenceDepthCollectionResult:
    version: str
    packet_id: str
    classification: str
    source_depth_plan_status: str
    source_next_packet_preview: str
    source_minimum_sanitized_result_count: int
    source_minimum_independent_session_count: int
    source_minimum_market_condition_buckets: int
    collection_status: str
    collection_label: str
    sanitized_result_count: int
    independent_session_count: int
    market_condition_bucket_count: int
    market_condition_buckets: tuple[str, ...]
    outcome_bucket_counts: Mapping[str, int]
    total_net_pnl_after_costs: str
    average_r_multiple: str
    minimum_counts_met: bool
    required_controls_met: bool
    required_persistence_absence_met: bool
    unsafe_payload_absent: bool
    rejected_result_references: tuple[str, ...]
    missing_required_fields: tuple[str, ...]
    unsafe_fragments_detected: tuple[str, ...]
    blocker_flags: Mapping[str, bool]
    evidence_categories_present: Mapping[str, bool]
    quality_gate_readiness: Mapping[str, bool]
    risk_control_readiness: Mapping[str, bool]
    blocked_claims: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    allowed_next_human_action: str
    next_packet_preview: str
    owner_review_required: bool
    preview_only: bool
    collection_only: bool
    execution_blocked: bool
    statistical_claim_blocked: bool
    proof_warning: str
    statistical_warning: str
    exact_next_owner_action: str
    exact_next_codex_packet_policy: str
    one_sentence_answer: str
    next_safe_action: str
    protected_flags: Mapping[str, bool]
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    live_execution_allowed: bool
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
    repeat_live_trade_allowed: bool
    next_trade_authorized: bool
    result_proves_profitability: bool
    statistical_profitability_confirmed: bool
    selected_packet_execution_authorized: bool
    selected_packet_commit_authorized: bool
    selected_packet_push_authorized: bool
    selected_packet_pr_authorized: bool
    selected_packet_merge_authorized: bool
    profit_proof_validated_as_statistical: bool
    future_profit_claim_allowed: bool
    evidence_depth_plan_authorizes_trading: bool
    evidence_depth_plan_authorizes_execution: bool
    evidence_depth_collection_authorizes_trading: bool
    evidence_depth_collection_authorizes_execution: bool


@dataclass(frozen=True)
class _ValidationState:
    schema_invalid: bool
    missing_required_fields: tuple[str, ...]
    invalid_decimal_fields: tuple[str, ...]
    unsafe_fragments_detected: tuple[str, ...]
    rejected_result_references: tuple[str, ...]
    r_values: tuple[Decimal, ...]
    pnl_values: tuple[Decimal, ...]
    required_controls_met: bool
    required_persistence_absence_met: bool
    unsafe_payload_absent: bool


def build_sample_complete_collection_input() -> (
    OandaLiveMicrotradeProfitProofEvidenceDepthCollectionInput
):
    return OandaLiveMicrotradeProfitProofEvidenceDepthCollectionInput(
        depth_plan_input=build_oanda_live_microtrade_profit_proof_evidence_depth_plan(
            build_sample_profit_depth_plan_input()
        ),
        sanitized_results=tuple(_build_sample_record(index) for index in range(1, 31)),
    )


def build_sample_partial_collection_input() -> (
    OandaLiveMicrotradeProfitProofEvidenceDepthCollectionInput
):
    return OandaLiveMicrotradeProfitProofEvidenceDepthCollectionInput(
        depth_plan_input=build_oanda_live_microtrade_profit_proof_evidence_depth_plan(
            build_sample_profit_depth_plan_input()
        ),
        sanitized_results=tuple(_build_sample_record(index) for index in range(1, 13)),
    )


def build_sample_empty_collection_input() -> (
    OandaLiveMicrotradeProfitProofEvidenceDepthCollectionInput
):
    return OandaLiveMicrotradeProfitProofEvidenceDepthCollectionInput(
        depth_plan_input=build_oanda_live_microtrade_profit_proof_evidence_depth_plan(
            build_sample_profit_depth_plan_input()
        ),
        sanitized_results=(),
    )


def build_sample_unsafe_collection_input() -> (
    OandaLiveMicrotradeProfitProofEvidenceDepthCollectionInput
):
    unsafe_record = dict(_build_sample_record(1))
    unsafe_record.update(
        {
            "result_reference": "unsafe_result_001",
            "instrument": "Authorization Bearer blocked sanitized sample",
            "unsafe_payload_absent": False,
            "credential_persistence_absent": False,
        }
    )
    return OandaLiveMicrotradeProfitProofEvidenceDepthCollectionInput(
        depth_plan_input=build_oanda_live_microtrade_profit_proof_evidence_depth_plan(
            build_sample_profit_depth_plan_input()
        ),
        sanitized_results=(unsafe_record,),
    )


def build_sample_schema_invalid_collection_input() -> (
    OandaLiveMicrotradeProfitProofEvidenceDepthCollectionInput
):
    return OandaLiveMicrotradeProfitProofEvidenceDepthCollectionInput(
        depth_plan_input=build_oanda_live_microtrade_profit_proof_evidence_depth_plan(
            build_sample_profit_depth_plan_input()
        ),
        sanitized_results=(
            {
                "result_reference": "schema_invalid_001",
                "session_reference": "",
                "market_condition_bucket": "trending",
                "outcome_bucket": "profit",
                "instrument": "EUR_USD_SANITIZED",
                "direction": "long",
                "r_multiple": "not_decimal",
            },
        ),
    )


def evaluate_oanda_live_microtrade_profit_proof_evidence_depth_collection(
    collection_input: (
        OandaLiveMicrotradeProfitProofEvidenceDepthCollectionInput
        | Mapping[str, Any]
        | None
    ) = None,
) -> OandaLiveMicrotradeProfitProofEvidenceDepthCollectionResult:
    active_input = _coerce_input(
        collection_input or build_sample_complete_collection_input()
    )
    depth_plan_result = _source_depth_plan_result(active_input.depth_plan_input)
    records = tuple(_coerce_record(record) for record in active_input.sanitized_results)
    validation = _validate_records(records)
    sanitized_result_count = len(records)
    session_count = len(_unique_nonempty(_field(record, "session_reference") for record in records))
    market_buckets = tuple(
        sorted(_unique_nonempty(_field(record, "market_condition_bucket") for record in records))
    )
    outcome_counts = _outcome_counts(records)
    minimum_counts_met = (
        sanitized_result_count >= _int_field(depth_plan_result, "minimum_sanitized_result_count", 30)
        and session_count >= _int_field(depth_plan_result, "minimum_independent_session_count", 10)
        and len(market_buckets) >= _int_field(depth_plan_result, "minimum_market_condition_buckets", 3)
    )
    total_pnl = sum(validation.pnl_values, Decimal("0"))
    average_r = (
        sum(validation.r_values, Decimal("0")) / Decimal(sanitized_result_count)
        if sanitized_result_count and len(validation.r_values) == sanitized_result_count
        else Decimal("0")
    )
    evidence_categories_present = _evidence_categories_present(
        records, validation, minimum_counts_met
    )
    risk_control_readiness = _risk_control_readiness(records)
    quality_gate_readiness = _quality_gate_readiness(
        records=records,
        total_pnl=total_pnl,
        average_r=average_r,
        minimum_counts_met=minimum_counts_met,
        required_controls_met=validation.required_controls_met,
        required_persistence_absence_met=validation.required_persistence_absence_met,
        unsafe_payload_absent=validation.unsafe_payload_absent,
    )
    classification = _classify_collection(validation, minimum_counts_met)
    collection_status = _collection_status(classification)
    blocker_flags = _blocker_flags(validation, minimum_counts_met, session_count, len(market_buckets), sanitized_result_count)
    protected_flags = protected_flags_false()
    return OandaLiveMicrotradeProfitProofEvidenceDepthCollectionResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=classification,
        source_depth_plan_status=_field(depth_plan_result, "classification"),
        source_next_packet_preview=_field(depth_plan_result, "next_packet_preview"),
        source_minimum_sanitized_result_count=_int_field(
            depth_plan_result, "minimum_sanitized_result_count", 30
        ),
        source_minimum_independent_session_count=_int_field(
            depth_plan_result, "minimum_independent_session_count", 10
        ),
        source_minimum_market_condition_buckets=_int_field(
            depth_plan_result, "minimum_market_condition_buckets", 3
        ),
        collection_status=collection_status,
        collection_label=_safe_owner_collection_label(active_input.owner_collection_label),
        sanitized_result_count=sanitized_result_count,
        independent_session_count=session_count,
        market_condition_bucket_count=len(market_buckets),
        market_condition_buckets=market_buckets,
        outcome_bucket_counts=outcome_counts,
        total_net_pnl_after_costs=_decimal_string(total_pnl),
        average_r_multiple=_decimal_string(average_r),
        minimum_counts_met=minimum_counts_met,
        required_controls_met=validation.required_controls_met,
        required_persistence_absence_met=validation.required_persistence_absence_met,
        unsafe_payload_absent=validation.unsafe_payload_absent,
        rejected_result_references=validation.rejected_result_references,
        missing_required_fields=_unique_tuple(
            validation.missing_required_fields + validation.invalid_decimal_fields
        ),
        unsafe_fragments_detected=validation.unsafe_fragments_detected,
        blocker_flags=blocker_flags,
        evidence_categories_present=evidence_categories_present,
        quality_gate_readiness=quality_gate_readiness,
        risk_control_readiness=risk_control_readiness,
        blocked_claims=BLOCKED_CLAIMS,
        blocked_actions=BLOCKED_ACTIONS,
        allowed_next_human_action=ALLOWED_NEXT_HUMAN_ACTION,
        next_packet_preview=QUALITY_GATE_PACKET_PREVIEW,
        owner_review_required=True,
        preview_only=True,
        collection_only=True,
        execution_blocked=True,
        statistical_claim_blocked=True,
        proof_warning=PROOF_WARNING,
        statistical_warning=STATISTICAL_WARNING,
        exact_next_owner_action=EXACT_NEXT_OWNER_ACTION,
        exact_next_codex_packet_policy=EXACT_NEXT_CODEX_PACKET_POLICY,
        one_sentence_answer=ONE_SENTENCE_ANSWER,
        next_safe_action=EXACT_NEXT_OWNER_ACTION,
        protected_flags=protected_flags,
        **protected_flags,
    )


def load_collection_json(path: str) -> dict[str, Any]:
    candidate = Path(path)
    lowered = str(candidate).lower()
    if candidate.suffix.lower() != ".json":
        raise ValueError("Only local JSON evidence collection files are supported.")
    if any(fragment.lower() in lowered for fragment in UNSAFE_STRING_FRAGMENTS):
        raise ValueError("Unsafe evidence collection path rejected.")
    with candidate.open("r", encoding="utf-8") as file_handle:
        loaded = json.load(file_handle)
    if not isinstance(loaded, Mapping):
        raise ValueError("Evidence collection JSON must contain an object.")
    return dict(loaded)


def protected_flags_false() -> dict[str, bool]:
    return {flag_name: False for flag_name in PROTECTED_FLAG_NAMES}


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    value = _jsonable(result)
    if isinstance(value, dict):
        return value
    return {"value": value}


def to_operator_text(
    result: OandaLiveMicrotradeProfitProofEvidenceDepthCollectionResult,
) -> str:
    return "\n".join(
        (
            f"Evidence-depth collection status: {result.classification}.",
            f"Collection status: {result.collection_status}.",
            (
                "Counts: "
                f"{result.sanitized_result_count} sanitized results, "
                f"{result.independent_session_count} independent sessions, "
                f"{result.market_condition_bucket_count} market condition buckets."
            ),
            f"Outcome counts: {dict(result.outcome_bucket_counts)}",
            f"Total net PnL after costs: {result.total_net_pnl_after_costs}.",
            f"Average R multiple: {result.average_r_multiple}.",
            f"Next packet preview: {result.next_packet_preview}.",
            f"Proof warning: {result.proof_warning}",
            f"Statistical warning: {result.statistical_warning}",
            f"Owner action: {result.exact_next_owner_action}",
            f"Codex packet policy: {result.exact_next_codex_packet_policy}",
            result.one_sentence_answer,
            "No selected packet execution approval was granted.",
            "No next trade approval was granted.",
            "No broker call was made by this packet.",
        )
    )


def to_markdown(
    result: OandaLiveMicrotradeProfitProofEvidenceDepthCollectionResult,
) -> str:
    rows = [
        "# AIOS Forex OANDA Live Microtrade Profit Proof Evidence Depth Collection V1",
        "",
        f"- Packet ID: `{result.packet_id}`",
        f"- Classification: `{result.classification}`",
        f"- Source depth plan status: `{result.source_depth_plan_status}`",
        f"- Source next packet preview: `{result.source_next_packet_preview}`",
        f"- Collection status: `{result.collection_status}`",
        f"- Collection label: `{result.collection_label}`",
        f"- Sanitized result count: `{result.sanitized_result_count}`",
        f"- Independent session count: `{result.independent_session_count}`",
        f"- Market condition bucket count: `{result.market_condition_bucket_count}`",
        f"- Market condition buckets: `{', '.join(result.market_condition_buckets)}`",
        f"- Outcome bucket counts: `{dict(result.outcome_bucket_counts)}`",
        f"- Total net PnL after costs: `{result.total_net_pnl_after_costs}`",
        f"- Average R multiple: `{result.average_r_multiple}`",
        f"- Minimum counts met: `{str(result.minimum_counts_met).lower()}`",
        f"- Required controls met: `{str(result.required_controls_met).lower()}`",
        (
            "- Required persistence absence met: "
            f"`{str(result.required_persistence_absence_met).lower()}`"
        ),
        f"- Unsafe payload absent: `{str(result.unsafe_payload_absent).lower()}`",
        f"- Next packet preview: `{result.next_packet_preview}`",
        "",
        "## Evidence Categories Present",
    ]
    rows.extend(_markdown_bool_map(result.evidence_categories_present))
    rows.append("")
    rows.append("## Quality Gate Readiness")
    rows.extend(_markdown_bool_map(result.quality_gate_readiness))
    rows.append("")
    rows.append("## Risk Control Readiness")
    rows.extend(_markdown_bool_map(result.risk_control_readiness))
    rows.append("")
    rows.append("## Blocker Flags")
    rows.extend(_markdown_bool_map(result.blocker_flags))
    rows.append("")
    rows.append("## Blocked Claims")
    rows.extend(f"- `{item}`" for item in result.blocked_claims)
    rows.append("")
    rows.append("## Blocked Actions")
    rows.extend(f"- `{item}`" for item in result.blocked_actions)
    rows.extend(
        (
            "",
            "## Warnings",
            f"- Proof warning: {result.proof_warning}",
            f"- Statistical warning: {result.statistical_warning}",
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
        "- No trade placed by this packet.",
        "- No broker call was made by this packet.",
        "- No credential access occurred.",
        "- No account ID was persisted.",
        "- No broker order ID was persisted.",
        "- No raw broker payload was persisted.",
        "- No live approval was granted.",
        "- No repeat trading approval was granted.",
        "- No next trade approval was granted.",
        "- No selected packet execution approval was granted.",
        "- No selected packet commit approval was granted.",
        "- No selected packet push approval was granted.",
        "- No selected packet PR approval was granted.",
        "- No selected packet merge approval was granted.",
        "- No real money approval was granted.",
        "- No compounding approval was granted.",
        "- No bank movement approval was granted.",
        "- No autonomous execution was granted.",
        "- Unattended vacation mode remains blocked.",
        "- Vacation profit trial remains blocked unless Anthony separately approves.",
        "- Profit is not guaranteed.",
        "- One result does not prove statistical profitability.",
        "- Evidence depth collection does not prove statistical profitability.",
        "- Evidence depth collection does not authorize trading.",
        "- All protected flags remain false.",
        "- Profit proof evidence-depth collection only.",
        "- Read-only only.",
    ]


def _build_sample_record(index: int) -> dict[str, Any]:
    if index <= 20:
        outcome = "profit"
        r_multiple = "0.20"
        net_pnl = "2.00"
    elif index <= 25:
        outcome = "loss"
        r_multiple = "-0.20"
        net_pnl = "-2.00"
    else:
        outcome = "breakeven"
        r_multiple = "0.00"
        net_pnl = "0.00"
    return {
        "result_reference": f"sanitized_result_{index:03d}",
        "session_reference": f"session_{((index - 1) % 10) + 1:02d}",
        "market_condition_bucket": ("trending", "ranging", "volatile")[
            (index - 1) % 3
        ],
        "outcome_bucket": outcome,
        "instrument": "EUR_USD_SANITIZED",
        "direction": "long" if index % 2 else "short",
        "r_multiple": r_multiple,
        "net_pnl_after_costs": net_pnl,
        "max_loss_respected": True,
        "daily_stop_respected": True,
        "kill_switch_available": True,
        "one_order_only_confirmed": True,
        "no_compounding_confirmed": True,
        "no_bank_movement_confirmed": True,
        "no_autonomous_execution_confirmed": True,
        "credential_persistence_absent": True,
        "account_id_persistence_absent": True,
        "broker_order_id_persistence_absent": True,
        "raw_broker_payload_absent": True,
        "unsafe_payload_absent": True,
        "owner_approval_separated": True,
    }


def _classify_collection(
    validation: _ValidationState, minimum_counts_met: bool
) -> str:
    if validation.schema_invalid:
        return (
            OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_SCHEMA_INVALID
        )
    if (
        validation.unsafe_fragments_detected
        or not validation.unsafe_payload_absent
        or not validation.required_persistence_absence_met
        or not validation.required_controls_met
    ):
        return OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_UNSAFE
    if minimum_counts_met:
        return (
            OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_READY_FOR_OWNER_REVIEW
        )
    return OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_REQUIRE_MORE_EVIDENCE


def _collection_status(classification: str) -> str:
    if (
        classification
        == OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_READY_FOR_OWNER_REVIEW
    ):
        return "sanitized_evidence_depth_collection_ready_for_owner_review"
    if (
        classification
        == OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_REQUIRE_MORE_EVIDENCE
    ):
        return "more_sanitized_evidence_required"
    if (
        classification
        == OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_BLOCKED_UNSAFE
    ):
        return "blocked_unsafe_collection"
    return "blocked_schema_invalid_collection"


def _validate_records(records: tuple[Mapping[str, Any], ...]) -> _ValidationState:
    missing: list[str] = []
    invalid_decimals: list[str] = []
    unsafe_fragments: list[str] = []
    rejected_refs: list[str] = []
    r_values: list[Decimal] = []
    pnl_values: list[Decimal] = []

    for index, record in enumerate(records, start=1):
        reference = _record_reference(record, index)
        record_rejected = False
        for field_name in REQUIRED_RESULT_FIELDS:
            if field_name not in record:
                missing.append(f"{reference}.{field_name}")
                record_rejected = True
        for field_name in STRING_RESULT_FIELDS:
            value = record.get(field_name)
            if not isinstance(value, str) or not value.strip():
                missing.append(f"{reference}.{field_name}")
                record_rejected = True
        if record.get("market_condition_bucket") not in MARKET_CONDITION_BUCKETS:
            missing.append(f"{reference}.market_condition_bucket_invalid")
            record_rejected = True
        if record.get("outcome_bucket") not in OUTCOME_BUCKETS:
            missing.append(f"{reference}.outcome_bucket_invalid")
            record_rejected = True
        if record.get("direction") not in DIRECTIONS:
            missing.append(f"{reference}.direction_invalid")
            record_rejected = True
        for field_name in BOOLEAN_RESULT_FIELDS:
            if not isinstance(record.get(field_name), bool):
                missing.append(f"{reference}.{field_name}_not_boolean")
                record_rejected = True
        for field_name in DECIMAL_FIELDS:
            try:
                decimal_value = Decimal(str(record.get(field_name)))
            except (InvalidOperation, ValueError):
                invalid_decimals.append(f"{reference}.{field_name}_invalid_decimal")
                record_rejected = True
                continue
            if field_name == "r_multiple":
                r_values.append(decimal_value)
            else:
                pnl_values.append(decimal_value)
        for field_name in STRING_RESULT_FIELDS:
            value = str(record.get(field_name, ""))
            for fragment in UNSAFE_STRING_FRAGMENTS:
                if fragment.lower() in value.lower():
                    unsafe_fragments.append(f"{reference}.{field_name}:{fragment}")
                    record_rejected = True
        if record_rejected:
            rejected_refs.append(reference)

    required_controls_met = _all_boolean_fields_true(records, CONTROL_FIELDS)
    required_persistence_absence_met = _all_boolean_fields_true(
        records, PERSISTENCE_ABSENCE_FIELDS
    )
    unsafe_payload_absent = _all_boolean_fields_true(
        records, ("unsafe_payload_absent",)
    ) and not unsafe_fragments
    return _ValidationState(
        schema_invalid=bool(missing or invalid_decimals),
        missing_required_fields=_unique_tuple(tuple(missing)),
        invalid_decimal_fields=_unique_tuple(tuple(invalid_decimals)),
        unsafe_fragments_detected=_unique_tuple(tuple(unsafe_fragments)),
        rejected_result_references=_unique_tuple(tuple(rejected_refs)),
        r_values=tuple(r_values),
        pnl_values=tuple(pnl_values),
        required_controls_met=required_controls_met,
        required_persistence_absence_met=required_persistence_absence_met,
        unsafe_payload_absent=unsafe_payload_absent,
    )


def _evidence_categories_present(
    records: tuple[Mapping[str, Any], ...],
    validation: _ValidationState,
    minimum_counts_met: bool,
) -> dict[str, bool]:
    has_records = bool(records)
    no_schema_errors = not validation.schema_invalid
    return {
        "sanitized_result_sequence": has_records,
        "per_trade_r_multiple": has_records and no_schema_errors,
        "net_pnl_after_costs": has_records and no_schema_errors,
        "max_loss_respected": _all_boolean_fields_true(records, ("max_loss_respected",)),
        "drawdown_trace": has_records and minimum_counts_met,
        "loss_review_trace": any(record.get("outcome_bucket") == "loss" for record in records),
        "breakeven_handling_trace": any(
            record.get("outcome_bucket") == "breakeven" for record in records
        ),
        "unsafe_result_exclusion_trace": validation.unsafe_payload_absent,
        "no_credential_or_account_persistence": (
            _all_boolean_fields_true(records, ("credential_persistence_absent",))
            and _all_boolean_fields_true(records, ("account_id_persistence_absent",))
        ),
        "no_broker_order_id_persistence": _all_boolean_fields_true(
            records, ("broker_order_id_persistence_absent",)
        ),
    }


def _quality_gate_readiness(
    *,
    records: tuple[Mapping[str, Any], ...],
    total_pnl: Decimal,
    average_r: Decimal,
    minimum_counts_met: bool,
    required_controls_met: bool,
    required_persistence_absence_met: bool,
    unsafe_payload_absent: bool,
) -> dict[str, bool]:
    pnl_values = tuple(_safe_decimal(record.get("net_pnl_after_costs")) for record in records)
    gross_profit = sum(
        (value for value in pnl_values if value > Decimal("0")),
        Decimal("0"),
    )
    gross_loss = abs(
        sum((value for value in pnl_values if value < Decimal("0")), Decimal("0"))
    )
    profit_factor_ready = gross_loss > Decimal("0") and gross_profit / gross_loss > Decimal("1")
    return {
        "sample_sufficiency_gate": minimum_counts_met,
        "positive_expectancy_gate": total_pnl > Decimal("0") and average_r > Decimal("0"),
        "profit_factor_gate": profit_factor_ready,
        "max_drawdown_gate": _all_boolean_fields_true(records, ("max_loss_respected",)),
        "loss_clustering_gate": _outcome_counts(records)["loss"] < len(records) // 2 if records else False,
        "outlier_dependency_gate": minimum_counts_met,
        "execution_safety_gate": (
            required_controls_met
            and required_persistence_absence_met
            and unsafe_payload_absent
        ),
        "owner_approval_separation_gate": _all_boolean_fields_true(
            records, ("owner_approval_separated",)
        ),
    }


def _risk_control_readiness(records: tuple[Mapping[str, Any], ...]) -> dict[str, bool]:
    return {
        "one_order_per_owner_approval": _all_boolean_fields_true(
            records, ("one_order_only_confirmed",)
        ),
        "max_loss_per_trade": _all_boolean_fields_true(records, ("max_loss_respected",)),
        "daily_stop": _all_boolean_fields_true(records, ("daily_stop_respected",)),
        "kill_switch_check": _all_boolean_fields_true(records, ("kill_switch_available",)),
        "no_compounding": _all_boolean_fields_true(records, ("no_compounding_confirmed",)),
        "no_bank_movement": _all_boolean_fields_true(records, ("no_bank_movement_confirmed",)),
        "no_autonomous_execution": _all_boolean_fields_true(
            records, ("no_autonomous_execution_confirmed",)
        ),
    }


def _blocker_flags(
    validation: _ValidationState,
    minimum_counts_met: bool,
    session_count: int,
    market_bucket_count: int,
    result_count: int,
) -> dict[str, bool]:
    return {
        "schema_invalid": validation.schema_invalid,
        "invalid_decimal_values": bool(validation.invalid_decimal_fields),
        "unsafe_fragments_detected": bool(validation.unsafe_fragments_detected),
        "unsafe_payload_absent_failed": not validation.unsafe_payload_absent,
        "persistence_absence_failed": not validation.required_persistence_absence_met,
        "required_controls_failed": not validation.required_controls_met,
        "minimum_counts_met": minimum_counts_met,
        "insufficient_sanitized_results": result_count < 30,
        "insufficient_independent_sessions": session_count < 10,
        "insufficient_market_condition_buckets": market_bucket_count < 3,
    }


def _coerce_input(
    value: OandaLiveMicrotradeProfitProofEvidenceDepthCollectionInput | Mapping[str, Any],
) -> OandaLiveMicrotradeProfitProofEvidenceDepthCollectionInput:
    if isinstance(value, OandaLiveMicrotradeProfitProofEvidenceDepthCollectionInput):
        return value
    raw = dict(value)
    raw_results = raw.get("sanitized_results", ())
    if not isinstance(raw_results, list | tuple):
        raw_results = ()
    return OandaLiveMicrotradeProfitProofEvidenceDepthCollectionInput(
        depth_plan_input=raw.get(
            "depth_plan_input",
            build_oanda_live_microtrade_profit_proof_evidence_depth_plan(
                build_sample_profit_depth_plan_input()
            ),
        ),
        sanitized_results=tuple(_coerce_record(record) for record in raw_results),
        owner_collection_label=_safe_owner_collection_label(
            raw.get("owner_collection_label", "pending_owner_review")
        ),
        owner_notes_sanitized=_safe_owner_notes(raw.get("owner_notes_sanitized", "")),
    )


def _source_depth_plan_result(value: Any) -> Any:
    if _looks_like_depth_plan_result(value):
        return value
    return build_oanda_live_microtrade_profit_proof_evidence_depth_plan(value)


def _looks_like_depth_plan_result(value: Any) -> bool:
    if isinstance(value, Mapping):
        return (
            "classification" in value
            and "minimum_sanitized_result_count" in value
            and "next_packet_preview" in value
        )
    return (
        hasattr(value, "classification")
        and hasattr(value, "minimum_sanitized_result_count")
        and hasattr(value, "next_packet_preview")
    )


def _coerce_record(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _field(value: Any, name: str, default: Any = "") -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _int_field(value: Any, name: str, default: int) -> int:
    raw_value = _field(value, name, default)
    return raw_value if isinstance(raw_value, int) else default


def _record_reference(record: Mapping[str, Any], index: int) -> str:
    value = record.get("result_reference")
    return value.strip() if isinstance(value, str) and value.strip() else f"record_{index:03d}"


def _outcome_counts(records: tuple[Mapping[str, Any], ...]) -> dict[str, int]:
    counts = {outcome: 0 for outcome in OUTCOME_BUCKETS}
    for record in records:
        outcome = record.get("outcome_bucket")
        if outcome in counts:
            counts[outcome] += 1
    return counts


def _all_boolean_fields_true(
    records: tuple[Mapping[str, Any], ...], field_names: tuple[str, ...]
) -> bool:
    return all(record.get(field_name) is True for record in records for field_name in field_names)


def _safe_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _decimal_string(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")


def _unique_nonempty(values: Any) -> tuple[str, ...]:
    return _unique_tuple(tuple(_text(value) for value in values if _text(value)))


def _safe_owner_collection_label(value: Any) -> str:
    text = _text(value, "pending_owner_review")
    unsafe_words = (
        "approve",
        "authorize",
        "trade",
        "broker",
        "compound",
        "bank",
        "execute",
        "live",
        "credential",
        "account",
        "order",
    )
    if not text or any(word in text.lower() for word in unsafe_words):
        return "pending_owner_review"
    return text


def _safe_owner_notes(value: Any) -> str:
    text = _text(value)
    blocked_words = (
        "credential",
        "account",
        "secret",
        "token",
        "password",
        "order id",
        "broker payload",
    )
    if any(word in text.lower() for word in blocked_words):
        return ""
    return text


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return value.strip() if isinstance(value, str) else str(value).strip()


def _unique_tuple(values: tuple[Any, ...]) -> tuple[str, ...]:
    unique: list[str] = []
    for value in values:
        text = _text(value)
        if text and text not in unique:
            unique.append(text)
    return tuple(unique)


def _markdown_bool_map(values: Mapping[str, bool]) -> list[str]:
    return [f"- `{key}`: `{str(value).lower()}`" for key, value in values.items()]


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {field.name: _jsonable(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, Decimal):
        return _decimal_string(value)
    if isinstance(value, tuple | list):
        return [_jsonable(item) for item in value]
    return value
