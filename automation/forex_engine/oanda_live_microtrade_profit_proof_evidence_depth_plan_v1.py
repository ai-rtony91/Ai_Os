"""Evidence-depth plan for weak OANDA microtrade profit proof candidates."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Mapping

from automation.forex_engine.oanda_live_microtrade_profit_proof_candidate_review_v1 import (
    OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_NOT_PROFIT_ROUTE,
    OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_NO_OWNER_RESULT,
    OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_UNSAFE,
    OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_READY_FOR_OWNER_REVIEW,
    OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_REQUIRE_MORE_EVIDENCE,
    build_sample_breakeven_review_input,
    build_sample_loss_review_input,
    build_sample_missing_owner_result_review_input,
    build_sample_profit_review_input,
    build_sample_unsafe_review_input,
    review_oanda_live_microtrade_profit_proof_candidate,
)


VERSION = "oanda_live_microtrade_profit_proof_evidence_depth_plan_v1"
PACKET_ID = (
    "AIOS-FOREX-OANDA-LIVE-MICROTRADE-PROFIT-PROOF-EVIDENCE-DEPTH-PLAN-V1"
)

OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_READY_FOR_OWNER_REVIEW = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_READY_FOR_OWNER_REVIEW"
)
OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_REQUIRE_MORE_EVIDENCE = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_REQUIRE_MORE_EVIDENCE"
)
OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_BLOCKED_NOT_PROFIT_CANDIDATE = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_BLOCKED_NOT_PROFIT_CANDIDATE"
)
OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_BLOCKED_UNSAFE = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_BLOCKED_UNSAFE"
)

LOSS_PACKET_PREVIEW = (
    "AIOS-FOREX-OANDA-LIVE-MICROTRADE-LOSS-TO-NEXT-PROFIT-CANDIDATE-GATE-V1"
)
BREAKEVEN_PACKET_PREVIEW = (
    "AIOS-FOREX-OANDA-LIVE-MICROTRADE-BREAKEVEN-MORE-EVIDENCE-V1"
)
MISSING_OWNER_RESULT_PACKET_PREVIEW = (
    "AIOS-FOREX-OANDA-LIVE-MICROTRADE-OWNER-RESULT-EVIDENCE-REQUIRED-V1"
)
UNSAFE_PACKET_PREVIEW = (
    "AIOS-FOREX-OANDA-LIVE-MICROTRADE-UNSAFE-RESULT-REPAIR-V1"
)
EVIDENCE_DEPTH_COLLECTION_PACKET_PREVIEW = (
    "AIOS-FOREX-OANDA-LIVE-MICROTRADE-PROFIT-PROOF-EVIDENCE-DEPTH-COLLECTION-V1"
)

EXACT_NEXT_OWNER_ACTION = (
    "Review the evidence-depth plan and decide whether to request a future "
    "evidence-depth collection packet. This does not approve another trade, "
    "selected packet execution, broker action, or profitability claims."
)
EXACT_NEXT_CODEX_PACKET_POLICY = (
    "Do not execute any selected proof packet from this plan. Generate or "
    "execute a future evidence-depth collection packet only after Anthony "
    "separately approves the exact next packet."
)
ONE_SENTENCE_ANSWER = (
    "AIOS can now define the evidence depth required beyond one weak profit "
    "result while blocking next-trade authorization, selected-packet "
    "execution, broker action, compounding, vacation mode, bank movement, "
    "and statistical profitability claims."
)

PROOF_WARNING = "Evidence depth plan does not approve another trade."
STATISTICAL_WARNING = (
    "One profit result does not prove statistical profitability or repeatable edge."
)

REQUIRED_EVIDENCE_CATEGORIES = (
    "sanitized_result_sequence",
    "per_trade_r_multiple",
    "net_pnl_after_costs",
    "max_loss_respected",
    "drawdown_trace",
    "loss_review_trace",
    "breakeven_handling_trace",
    "unsafe_result_exclusion_trace",
    "no_credential_or_account_persistence",
    "no_broker_order_id_persistence",
)
REQUIRED_QUALITY_GATES = (
    "sample_sufficiency_gate",
    "positive_expectancy_gate",
    "profit_factor_gate",
    "max_drawdown_gate",
    "loss_clustering_gate",
    "outlier_dependency_gate",
    "execution_safety_gate",
    "owner_approval_separation_gate",
)
REQUIRED_RISK_CONTROLS = (
    "one_order_per_owner_approval",
    "max_loss_per_trade",
    "daily_stop",
    "kill_switch_check",
    "no_compounding",
    "no_bank_movement",
    "no_autonomous_execution",
)
REQUIRED_BLOCKER_CHECKS = (
    "insufficient_sample",
    "negative_expectancy",
    "low_profit_factor",
    "drawdown_above_limit",
    "risk_breach",
    "unsafe_payload",
    "missing_owner_result",
    "credential_or_account_leak",
    "repeat_trade_request",
)
BLOCKED_CLAIMS = (
    "statistical_profitability",
    "future_profit",
    "repeatable_edge",
    "production_readiness",
    "vacation_mode_readiness",
)
BLOCKED_ACTIONS = (
    "broker_call",
    "oanda_api_call",
    "credential_access",
    "account_id_access",
    "order_placement",
    "repeat_trade",
    "next_trade_authorization",
    "selected_packet_execution",
    "selected_packet_commit",
    "selected_packet_push",
    "selected_packet_pr",
    "selected_packet_merge",
    "compounding",
    "bank_movement",
    "vacation_mode",
    "autonomous_execution",
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
)


@dataclass(frozen=True)
class OandaLiveMicrotradeProfitProofEvidenceDepthPlanInput:
    profit_review_input: Any
    owner_plan_label: str = "pending_owner_review"
    owner_notes_sanitized: str = ""


@dataclass(frozen=True)
class OandaLiveMicrotradeProfitProofEvidenceDepthPlanResult:
    version: str
    packet_id: str
    classification: str
    source_profit_review_status: str
    source_candidate_review_lane: str
    source_candidate_strength_label: str
    source_statistical_validity_status: str
    source_evidence_depth_status: str
    source_evidence_depth_next_packet_preview: str
    evidence_depth_plan_status: str
    evidence_depth_plan_label: str
    evidence_depth_reason: str
    minimum_sanitized_result_count: int
    minimum_independent_session_count: int
    minimum_market_condition_buckets: int
    required_evidence_categories: tuple[str, ...]
    required_quality_gates: tuple[str, ...]
    required_risk_controls: tuple[str, ...]
    required_blocker_checks: tuple[str, ...]
    blocked_claims: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    allowed_next_human_action: str
    next_packet_preview: str
    owner_review_required: bool
    single_result_candidate: bool
    evidence_depth_required: bool
    preview_only: bool
    plan_only: bool
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


@dataclass(frozen=True)
class _DepthPlanRoute:
    classification: str
    evidence_depth_plan_status: str
    evidence_depth_plan_label: str
    evidence_depth_reason: str
    minimum_sanitized_result_count: int
    minimum_independent_session_count: int
    minimum_market_condition_buckets: int
    blocked_claims: tuple[str, ...]
    allowed_next_human_action: str
    next_packet_preview: str
    single_result_candidate: bool
    evidence_depth_required: bool
    next_safe_action: str


def build_sample_profit_depth_plan_input() -> (
    OandaLiveMicrotradeProfitProofEvidenceDepthPlanInput
):
    return OandaLiveMicrotradeProfitProofEvidenceDepthPlanInput(
        profit_review_input=review_oanda_live_microtrade_profit_proof_candidate(
            build_sample_profit_review_input()
        )
    )


def build_sample_loss_depth_plan_input() -> (
    OandaLiveMicrotradeProfitProofEvidenceDepthPlanInput
):
    return OandaLiveMicrotradeProfitProofEvidenceDepthPlanInput(
        profit_review_input=review_oanda_live_microtrade_profit_proof_candidate(
            build_sample_loss_review_input()
        )
    )


def build_sample_breakeven_depth_plan_input() -> (
    OandaLiveMicrotradeProfitProofEvidenceDepthPlanInput
):
    return OandaLiveMicrotradeProfitProofEvidenceDepthPlanInput(
        profit_review_input=review_oanda_live_microtrade_profit_proof_candidate(
            build_sample_breakeven_review_input()
        )
    )


def build_sample_missing_owner_result_depth_plan_input() -> (
    OandaLiveMicrotradeProfitProofEvidenceDepthPlanInput
):
    return OandaLiveMicrotradeProfitProofEvidenceDepthPlanInput(
        profit_review_input=review_oanda_live_microtrade_profit_proof_candidate(
            build_sample_missing_owner_result_review_input()
        )
    )


def build_sample_unsafe_depth_plan_input() -> (
    OandaLiveMicrotradeProfitProofEvidenceDepthPlanInput
):
    return OandaLiveMicrotradeProfitProofEvidenceDepthPlanInput(
        profit_review_input=review_oanda_live_microtrade_profit_proof_candidate(
            build_sample_unsafe_review_input()
        )
    )


def build_oanda_live_microtrade_profit_proof_evidence_depth_plan(
    depth_plan_input: (
        OandaLiveMicrotradeProfitProofEvidenceDepthPlanInput | Mapping[str, Any] | None
    ) = None,
) -> OandaLiveMicrotradeProfitProofEvidenceDepthPlanResult:
    active_input = _coerce_input(
        depth_plan_input or build_sample_profit_depth_plan_input()
    )
    source_review = _source_profit_review_result(active_input.profit_review_input)
    route = _select_depth_plan_route(source_review)
    protected_flags = protected_flags_false()
    return OandaLiveMicrotradeProfitProofEvidenceDepthPlanResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=route.classification,
        source_profit_review_status=_field(source_review, "classification"),
        source_candidate_review_lane=_field(source_review, "candidate_review_lane"),
        source_candidate_strength_label=_field(
            source_review, "candidate_strength_label"
        ),
        source_statistical_validity_status=_field(
            source_review, "statistical_validity_status"
        ),
        source_evidence_depth_status=_field(source_review, "evidence_depth_status"),
        source_evidence_depth_next_packet_preview=_field(
            source_review, "evidence_depth_next_packet_preview"
        ),
        evidence_depth_plan_status=route.evidence_depth_plan_status,
        evidence_depth_plan_label=route.evidence_depth_plan_label,
        evidence_depth_reason=route.evidence_depth_reason,
        minimum_sanitized_result_count=route.minimum_sanitized_result_count,
        minimum_independent_session_count=route.minimum_independent_session_count,
        minimum_market_condition_buckets=route.minimum_market_condition_buckets,
        required_evidence_categories=REQUIRED_EVIDENCE_CATEGORIES,
        required_quality_gates=REQUIRED_QUALITY_GATES,
        required_risk_controls=REQUIRED_RISK_CONTROLS,
        required_blocker_checks=REQUIRED_BLOCKER_CHECKS,
        blocked_claims=route.blocked_claims,
        blocked_actions=BLOCKED_ACTIONS,
        allowed_next_human_action=route.allowed_next_human_action,
        next_packet_preview=route.next_packet_preview,
        owner_review_required=True,
        single_result_candidate=route.single_result_candidate,
        evidence_depth_required=route.evidence_depth_required,
        preview_only=True,
        plan_only=True,
        execution_blocked=True,
        statistical_claim_blocked=True,
        proof_warning=PROOF_WARNING,
        statistical_warning=STATISTICAL_WARNING,
        exact_next_owner_action=EXACT_NEXT_OWNER_ACTION,
        exact_next_codex_packet_policy=EXACT_NEXT_CODEX_PACKET_POLICY,
        one_sentence_answer=ONE_SENTENCE_ANSWER,
        next_safe_action=route.next_safe_action,
        protected_flags=protected_flags,
        **protected_flags,
    )


def protected_flags_false() -> dict[str, bool]:
    return {flag_name: False for flag_name in PROTECTED_FLAG_NAMES}


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    value = _jsonable(result)
    if isinstance(value, dict):
        return value
    return {"value": value}


def to_operator_text(
    result: OandaLiveMicrotradeProfitProofEvidenceDepthPlanResult,
) -> str:
    return "\n".join(
        (
            f"Evidence-depth plan status: {result.classification}.",
            f"Plan label: {result.evidence_depth_plan_label}.",
            f"Plan reason: {result.evidence_depth_reason}",
            (
                "Minimum evidence: "
                f"{result.minimum_sanitized_result_count} sanitized results, "
                f"{result.minimum_independent_session_count} independent sessions, "
                f"{result.minimum_market_condition_buckets} market condition buckets."
            ),
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
    result: OandaLiveMicrotradeProfitProofEvidenceDepthPlanResult,
) -> str:
    rows = [
        "# AIOS Forex OANDA Live Microtrade Profit Proof Evidence Depth Plan V1",
        "",
        f"- Packet ID: `{result.packet_id}`",
        f"- Classification: `{result.classification}`",
        f"- Source profit review status: `{result.source_profit_review_status}`",
        f"- Source candidate review lane: `{result.source_candidate_review_lane}`",
        f"- Source candidate strength: `{result.source_candidate_strength_label}`",
        f"- Source statistical validity: `{result.source_statistical_validity_status}`",
        f"- Source evidence depth status: `{result.source_evidence_depth_status}`",
        f"- Evidence depth plan status: `{result.evidence_depth_plan_status}`",
        f"- Evidence depth plan label: `{result.evidence_depth_plan_label}`",
        f"- Evidence depth reason: {result.evidence_depth_reason}",
        f"- Minimum sanitized result count: `{result.minimum_sanitized_result_count}`",
        (
            "- Minimum independent session count: "
            f"`{result.minimum_independent_session_count}`"
        ),
        (
            "- Minimum market condition buckets: "
            f"`{result.minimum_market_condition_buckets}`"
        ),
        f"- Next packet preview: `{result.next_packet_preview}`",
        f"- Owner review required: `{str(result.owner_review_required).lower()}`",
        f"- Single result candidate: `{str(result.single_result_candidate).lower()}`",
        f"- Evidence depth required: `{str(result.evidence_depth_required).lower()}`",
        f"- Preview only: `{str(result.preview_only).lower()}`",
        f"- Plan only: `{str(result.plan_only).lower()}`",
        f"- Execution blocked: `{str(result.execution_blocked).lower()}`",
        (
            "- Statistical claim blocked: "
            f"`{str(result.statistical_claim_blocked).lower()}`"
        ),
        "",
        "## Required Evidence Categories",
    ]
    rows.extend(f"- `{item}`" for item in result.required_evidence_categories)
    rows.append("")
    rows.append("## Required Quality Gates")
    rows.extend(f"- `{item}`" for item in result.required_quality_gates)
    rows.append("")
    rows.append("## Required Risk Controls")
    rows.extend(f"- `{item}`" for item in result.required_risk_controls)
    rows.append("")
    rows.append("## Required Blocker Checks")
    rows.extend(f"- `{item}`" for item in result.required_blocker_checks)
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
        "- Single-result proof candidate is weak evidence.",
        "- Evidence depth is required before any profitability claim.",
        "- Evidence depth plan does not authorize trading.",
        "- All protected flags remain false.",
        "- Profit proof evidence-depth plan only.",
        "- Read-only only.",
    ]


def _select_depth_plan_route(source_review: Any) -> _DepthPlanRoute:
    source_status = _field(source_review, "classification")
    if source_status == OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_READY_FOR_OWNER_REVIEW:
        return _DepthPlanRoute(
            classification=(
                OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_READY_FOR_OWNER_REVIEW
            ),
            evidence_depth_plan_status="evidence_depth_plan_ready_for_owner_review",
            evidence_depth_plan_label="weak_profit_candidate_needs_depth_plan",
            evidence_depth_reason=(
                "One profit result is not enough to prove repeatability."
            ),
            minimum_sanitized_result_count=30,
            minimum_independent_session_count=10,
            minimum_market_condition_buckets=3,
            blocked_claims=BLOCKED_CLAIMS,
            allowed_next_human_action=(
                "Anthony may request a future evidence-depth collection packet only."
            ),
            next_packet_preview=EVIDENCE_DEPTH_COLLECTION_PACKET_PREVIEW,
            single_result_candidate=True,
            evidence_depth_required=True,
            next_safe_action=EXACT_NEXT_OWNER_ACTION,
        )
    if source_status == OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_NOT_PROFIT_ROUTE:
        return _DepthPlanRoute(
            classification=(
                OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_BLOCKED_NOT_PROFIT_CANDIDATE
            ),
            evidence_depth_plan_status="blocked_not_profit_candidate",
            evidence_depth_plan_label="not_profit_candidate",
            evidence_depth_reason=(
                "The source review is not a profit candidate and cannot become proof."
            ),
            minimum_sanitized_result_count=0,
            minimum_independent_session_count=0,
            minimum_market_condition_buckets=0,
            blocked_claims=_unique_tuple(BLOCKED_CLAIMS + ("profit_proof_candidate",)),
            allowed_next_human_action=(
                "Anthony may request the loss-to-next-profit candidate gate only."
            ),
            next_packet_preview=LOSS_PACKET_PREVIEW,
            single_result_candidate=False,
            evidence_depth_required=False,
            next_safe_action=(
                "Route to the loss review gate; do not create a profit proof plan."
            ),
        )
    if source_status == OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_REQUIRE_MORE_EVIDENCE:
        return _DepthPlanRoute(
            classification=(
                OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_REQUIRE_MORE_EVIDENCE
            ),
            evidence_depth_plan_status="more_evidence_required_before_depth_plan",
            evidence_depth_plan_label="breakeven_more_evidence_required",
            evidence_depth_reason=(
                "The source review needs more evidence before a depth plan can advance."
            ),
            minimum_sanitized_result_count=0,
            minimum_independent_session_count=0,
            minimum_market_condition_buckets=0,
            blocked_claims=BLOCKED_CLAIMS,
            allowed_next_human_action=(
                "Anthony may request the breakeven more-evidence packet only."
            ),
            next_packet_preview=BREAKEVEN_PACKET_PREVIEW,
            single_result_candidate=False,
            evidence_depth_required=True,
            next_safe_action=(
                "Route to more evidence; do not claim profit proof or repeatability."
            ),
        )
    if source_status == OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_NO_OWNER_RESULT:
        return _DepthPlanRoute(
            classification=(
                OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_REQUIRE_MORE_EVIDENCE
            ),
            evidence_depth_plan_status="owner_result_required_before_depth_plan",
            evidence_depth_plan_label="owner_result_required",
            evidence_depth_reason=(
                "Sanitized owner result evidence is required before depth planning."
            ),
            minimum_sanitized_result_count=0,
            minimum_independent_session_count=0,
            minimum_market_condition_buckets=0,
            blocked_claims=BLOCKED_CLAIMS,
            allowed_next_human_action=(
                "Anthony may provide sanitized owner-result evidence only."
            ),
            next_packet_preview=MISSING_OWNER_RESULT_PACKET_PREVIEW,
            single_result_candidate=False,
            evidence_depth_required=True,
            next_safe_action=(
                "Route to owner-result evidence required; do not create a proof claim."
            ),
        )
    return _DepthPlanRoute(
        classification=OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_BLOCKED_UNSAFE,
        evidence_depth_plan_status="unsafe_result_repair_required_before_depth_plan",
        evidence_depth_plan_label="unsafe_result_repair_required",
        evidence_depth_reason=(
            "Unsafe result material must be repaired before any evidence-depth plan."
        ),
        minimum_sanitized_result_count=0,
        minimum_independent_session_count=0,
        minimum_market_condition_buckets=0,
        blocked_claims=BLOCKED_CLAIMS,
        allowed_next_human_action=(
            "Anthony may request unsafe-result repair only."
        ),
        next_packet_preview=UNSAFE_PACKET_PREVIEW,
        single_result_candidate=False,
        evidence_depth_required=False,
        next_safe_action=(
            "Route to unsafe-result repair; do not review proof depth until safe."
        ),
    )


def _coerce_input(
    value: OandaLiveMicrotradeProfitProofEvidenceDepthPlanInput | Mapping[str, Any],
) -> OandaLiveMicrotradeProfitProofEvidenceDepthPlanInput:
    if isinstance(value, OandaLiveMicrotradeProfitProofEvidenceDepthPlanInput):
        return value
    raw = dict(value)
    return OandaLiveMicrotradeProfitProofEvidenceDepthPlanInput(
        profit_review_input=raw.get("profit_review_input", raw),
        owner_plan_label=_safe_owner_plan_label(
            raw.get("owner_plan_label", "pending_owner_review")
        ),
        owner_notes_sanitized=_safe_owner_notes(raw.get("owner_notes_sanitized", "")),
    )


def _source_profit_review_result(value: Any) -> Any:
    if _looks_like_profit_review_result(value):
        return value
    return review_oanda_live_microtrade_profit_proof_candidate(value)


def _looks_like_profit_review_result(value: Any) -> bool:
    if isinstance(value, Mapping):
        return (
            "classification" in value
            and "candidate_review_lane" in value
            and "candidate_strength_label" in value
        )
    return (
        hasattr(value, "classification")
        and hasattr(value, "candidate_review_lane")
        and hasattr(value, "candidate_strength_label")
    )


def _field(value: Any, name: str, default: Any = "") -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _safe_owner_plan_label(value: Any) -> str:
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


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {field.name: _jsonable(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [_jsonable(item) for item in value]
    return value
