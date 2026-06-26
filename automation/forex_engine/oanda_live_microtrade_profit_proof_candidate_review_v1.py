"""Profit proof candidate review for selected OANDA microtrade previews."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Mapping

from automation.forex_engine.oanda_live_microtrade_selected_proof_packet_preview_catalog_v1 import (
    build_sample_breakeven_catalog_input,
    build_sample_loss_catalog_input,
    build_sample_missing_owner_result_catalog_input,
    build_sample_profit_catalog_input,
    build_sample_unsafe_catalog_input,
    build_selected_proof_packet_preview_catalog,
)


VERSION = "oanda_live_microtrade_profit_proof_candidate_review_v1"
PACKET_ID = (
    "AIOS-FOREX-OANDA-LIVE-MICROTRADE-PROFIT-PROOF-CANDIDATE-REVIEW-V1"
)

OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_READY_FOR_OWNER_REVIEW = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_READY_FOR_OWNER_REVIEW"
)
OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_REQUIRE_MORE_EVIDENCE = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_REQUIRE_MORE_EVIDENCE"
)
OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_NOT_PROFIT_ROUTE = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_NOT_PROFIT_ROUTE"
)
OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_NO_OWNER_RESULT = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_NO_OWNER_RESULT"
)
OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_UNSAFE = (
    "OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_UNSAFE"
)

PROFIT_PACKET_PREVIEW = (
    "AIOS-FOREX-OANDA-LIVE-MICROTRADE-PROFIT-PROOF-CANDIDATE-REVIEW-V1"
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
EVIDENCE_DEPTH_NEXT_PACKET_PREVIEW = (
    "AIOS-FOREX-OANDA-LIVE-MICROTRADE-PROFIT-PROOF-EVIDENCE-DEPTH-PLAN-V1"
)

EXACT_NEXT_OWNER_ACTION = (
    "Review the profit proof candidate summary and decide whether to request "
    "an evidence-depth plan. This does not approve another trade, selected "
    "packet execution, broker action, or profitability claims."
)
EXACT_NEXT_CODEX_PACKET_POLICY = (
    "Do not execute any selected proof packet from this review. Generate or "
    "execute a future evidence-depth packet only after Anthony separately "
    "approves the exact next packet."
)
ONE_SENTENCE_ANSWER = (
    "AIOS can now review one selected profit proof preview as a weak "
    "single-result proof candidate while blocking next-trade authorization, "
    "selected-packet execution, broker action, compounding, vacation mode, "
    "bank movement, and statistical profitability claims."
)

PROFIT_PROOF_CANDIDATE_SUMMARY = (
    "One captured profit result can be reviewed as a proof candidate only."
)
PROOF_WARNING = "Profit candidate review does not approve another trade."
STATISTICAL_WARNING = (
    "One profit result does not prove repeatable edge or statistical profitability."
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
)

BASE_BLOCKED_ITEMS = (
    "broker_call",
    "credential_access",
    "account_id_persistence",
    "broker_order_id_persistence",
    "raw_broker_payload_persistence",
    "order_placement",
    "repeat_live_trade",
    "next_trade_authorization",
    "selected_packet_execution",
    "selected_packet_commit",
    "selected_packet_push",
    "selected_packet_pr",
    "selected_packet_merge",
    "live_execution",
    "real_money",
    "compounding",
    "bank_movement",
    "autonomous_execution",
    "scheduler",
    "daemon",
    "webhook",
    "vacation_mode",
    "vacation_profit_trial",
    "future_profit_claim",
    "statistical_profitability_claim",
)


@dataclass(frozen=True)
class OandaLiveMicrotradeProfitProofCandidateReviewInput:
    catalog_input: Any
    owner_review_label: str = "pending_owner_review"
    owner_notes_sanitized: str = ""


@dataclass(frozen=True)
class OandaLiveMicrotradeProfitProofCandidateReviewResult:
    version: str
    packet_id: str
    classification: str
    source_catalog_status: str
    source_selected_packet_preview: str
    source_selected_packet_title: str
    source_selected_packet_purpose: str
    source_selected_packet_non_execution_notice: str
    source_selected_packet_blocked_actions: tuple[str, ...]
    candidate_review_lane: str
    candidate_review_status: str
    candidate_strength_label: str
    proof_candidate_summary: str
    statistical_validity_status: str
    evidence_depth_status: str
    evidence_depth_next_packet_preview: str
    owner_review_required: bool
    single_result_candidate: bool
    evidence_depth_required: bool
    preview_only: bool
    review_only: bool
    execution_blocked: bool
    blocked_items: tuple[str, ...]
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


@dataclass(frozen=True)
class _ReviewRoute:
    classification: str
    candidate_review_lane: str
    candidate_review_status: str
    candidate_strength_label: str
    proof_candidate_summary: str
    statistical_validity_status: str
    evidence_depth_status: str
    evidence_depth_next_packet_preview: str
    single_result_candidate: bool
    evidence_depth_required: bool
    blocked_items: tuple[str, ...]
    proof_warning: str
    statistical_warning: str
    next_safe_action: str


def build_sample_profit_review_input() -> OandaLiveMicrotradeProfitProofCandidateReviewInput:
    return OandaLiveMicrotradeProfitProofCandidateReviewInput(
        catalog_input=build_selected_proof_packet_preview_catalog(
            build_sample_profit_catalog_input()
        )
    )


def build_sample_loss_review_input() -> OandaLiveMicrotradeProfitProofCandidateReviewInput:
    return OandaLiveMicrotradeProfitProofCandidateReviewInput(
        catalog_input=build_selected_proof_packet_preview_catalog(
            build_sample_loss_catalog_input()
        )
    )


def build_sample_breakeven_review_input() -> (
    OandaLiveMicrotradeProfitProofCandidateReviewInput
):
    return OandaLiveMicrotradeProfitProofCandidateReviewInput(
        catalog_input=build_selected_proof_packet_preview_catalog(
            build_sample_breakeven_catalog_input()
        )
    )


def build_sample_missing_owner_result_review_input() -> (
    OandaLiveMicrotradeProfitProofCandidateReviewInput
):
    return OandaLiveMicrotradeProfitProofCandidateReviewInput(
        catalog_input=build_selected_proof_packet_preview_catalog(
            build_sample_missing_owner_result_catalog_input()
        )
    )


def build_sample_unsafe_review_input() -> OandaLiveMicrotradeProfitProofCandidateReviewInput:
    return OandaLiveMicrotradeProfitProofCandidateReviewInput(
        catalog_input=build_selected_proof_packet_preview_catalog(
            build_sample_unsafe_catalog_input()
        )
    )


def review_oanda_live_microtrade_profit_proof_candidate(
    review_input: (
        OandaLiveMicrotradeProfitProofCandidateReviewInput | Mapping[str, Any] | None
    ) = None,
) -> OandaLiveMicrotradeProfitProofCandidateReviewResult:
    active_input = _coerce_input(review_input or build_sample_profit_review_input())
    catalog_result = _source_catalog_result(active_input.catalog_input)
    route = _select_review_route(catalog_result)
    protected_flags = protected_flags_false()
    source_blocked_actions = _tuple_field(
        catalog_result, "selected_packet_blocked_actions"
    )
    blocked_items = _unique_tuple(
        source_blocked_actions + BASE_BLOCKED_ITEMS + route.blocked_items
    )
    return OandaLiveMicrotradeProfitProofCandidateReviewResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=route.classification,
        source_catalog_status=_field(catalog_result, "classification"),
        source_selected_packet_preview=_field(catalog_result, "selected_packet_preview"),
        source_selected_packet_title=_field(catalog_result, "selected_packet_title"),
        source_selected_packet_purpose=_field(catalog_result, "selected_packet_purpose"),
        source_selected_packet_non_execution_notice=_field(
            catalog_result, "selected_packet_non_execution_notice"
        ),
        source_selected_packet_blocked_actions=source_blocked_actions,
        candidate_review_lane=route.candidate_review_lane,
        candidate_review_status=route.candidate_review_status,
        candidate_strength_label=route.candidate_strength_label,
        proof_candidate_summary=route.proof_candidate_summary,
        statistical_validity_status=route.statistical_validity_status,
        evidence_depth_status=route.evidence_depth_status,
        evidence_depth_next_packet_preview=route.evidence_depth_next_packet_preview,
        owner_review_required=True,
        single_result_candidate=route.single_result_candidate,
        evidence_depth_required=route.evidence_depth_required,
        preview_only=True,
        review_only=True,
        execution_blocked=True,
        blocked_items=blocked_items,
        proof_warning=route.proof_warning,
        statistical_warning=route.statistical_warning,
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


def to_operator_text(result: OandaLiveMicrotradeProfitProofCandidateReviewResult) -> str:
    return "\n".join(
        (
            f"Profit proof candidate review status: {result.classification}.",
            f"Candidate review lane: {result.candidate_review_lane}.",
            f"Candidate strength: {result.candidate_strength_label}.",
            f"Statistical validity: {result.statistical_validity_status}.",
            f"Evidence depth status: {result.evidence_depth_status}.",
            f"Next evidence-depth preview: {result.evidence_depth_next_packet_preview}.",
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


def to_markdown(result: OandaLiveMicrotradeProfitProofCandidateReviewResult) -> str:
    rows = [
        "# AIOS Forex OANDA Live Microtrade Profit Proof Candidate Review V1",
        "",
        f"- Packet ID: `{result.packet_id}`",
        f"- Classification: `{result.classification}`",
        f"- Source catalog status: `{result.source_catalog_status}`",
        f"- Source selected packet preview: `{result.source_selected_packet_preview}`",
        f"- Source selected packet title: {result.source_selected_packet_title}",
        f"- Source selected packet purpose: {result.source_selected_packet_purpose}",
        (
            "- Source selected packet non-execution notice: "
            f"{result.source_selected_packet_non_execution_notice}"
        ),
        f"- Candidate review lane: `{result.candidate_review_lane}`",
        f"- Candidate review status: `{result.candidate_review_status}`",
        f"- Candidate strength label: `{result.candidate_strength_label}`",
        f"- Proof candidate summary: {result.proof_candidate_summary}",
        f"- Statistical validity status: `{result.statistical_validity_status}`",
        f"- Evidence depth status: `{result.evidence_depth_status}`",
        (
            "- Evidence depth next packet preview: "
            f"`{result.evidence_depth_next_packet_preview}`"
        ),
        f"- Owner review required: `{str(result.owner_review_required).lower()}`",
        f"- Single result candidate: `{str(result.single_result_candidate).lower()}`",
        f"- Evidence depth required: `{str(result.evidence_depth_required).lower()}`",
        f"- Preview only: `{str(result.preview_only).lower()}`",
        f"- Review only: `{str(result.review_only).lower()}`",
        f"- Execution blocked: `{str(result.execution_blocked).lower()}`",
        "",
        "## Warnings",
        f"- Proof warning: {result.proof_warning}",
        f"- Statistical warning: {result.statistical_warning}",
        "",
        "## Blocked Items",
    ]
    rows.extend(f"- `{item}`" for item in result.blocked_items)
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
        "- All protected flags remain false.",
        "- Profit proof candidate review only.",
        "- Read-only only.",
    ]


def _select_review_route(catalog_result: Any) -> _ReviewRoute:
    selected_packet_preview = _field(catalog_result, "selected_packet_preview")
    if selected_packet_preview == PROFIT_PACKET_PREVIEW:
        return _ReviewRoute(
            classification=(
                OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_READY_FOR_OWNER_REVIEW
            ),
            candidate_review_lane="profit_proof_candidate_review",
            candidate_review_status="single_profit_result_candidate_ready_for_owner_review",
            candidate_strength_label="weak_single_result_candidate",
            proof_candidate_summary=PROFIT_PROOF_CANDIDATE_SUMMARY,
            statistical_validity_status="not_statistically_valid_single_result",
            evidence_depth_status="evidence_depth_required_before_profitability_claim",
            evidence_depth_next_packet_preview=EVIDENCE_DEPTH_NEXT_PACKET_PREVIEW,
            single_result_candidate=True,
            evidence_depth_required=True,
            blocked_items=("single_result_not_statistical_profitability_proof",),
            proof_warning=PROOF_WARNING,
            statistical_warning=STATISTICAL_WARNING,
            next_safe_action=(
                "Request an evidence-depth plan only if Anthony separately approves "
                "that exact future packet; do not approve another trade."
            ),
        )
    if selected_packet_preview == LOSS_PACKET_PREVIEW:
        return _ReviewRoute(
            classification=(
                OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_NOT_PROFIT_ROUTE
            ),
            candidate_review_lane="loss_review_and_next_profit_candidate_gate",
            candidate_review_status="blocked_not_profit_route_loss_review_required",
            candidate_strength_label="not_profit_candidate",
            proof_candidate_summary=(
                "Loss route cannot be treated as a profit proof candidate."
            ),
            statistical_validity_status="not_profit_route_not_profitability_proof",
            evidence_depth_status="route_to_loss_review_before_profit_candidate_review",
            evidence_depth_next_packet_preview=LOSS_PACKET_PREVIEW,
            single_result_candidate=False,
            evidence_depth_required=False,
            blocked_items=("non_profit_route_loss_review",),
            proof_warning="Loss route is not a profit proof candidate.",
            statistical_warning=(
                "A loss route cannot validate statistical profitability."
            ),
            next_safe_action=(
                "Route to loss review; do not treat the selected packet preview "
                "as profit proof."
            ),
        )
    if selected_packet_preview == BREAKEVEN_PACKET_PREVIEW:
        return _ReviewRoute(
            classification=(
                OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_REQUIRE_MORE_EVIDENCE
            ),
            candidate_review_lane="more_evidence_required",
            candidate_review_status="breakeven_requires_more_evidence",
            candidate_strength_label="insufficient_single_result_candidate",
            proof_candidate_summary=(
                "Breakeven route requires more evidence before profit proof review."
            ),
            statistical_validity_status="not_statistically_valid_more_evidence_required",
            evidence_depth_status="more_evidence_required_before_profit_candidate_review",
            evidence_depth_next_packet_preview=BREAKEVEN_PACKET_PREVIEW,
            single_result_candidate=False,
            evidence_depth_required=True,
            blocked_items=("breakeven_requires_more_evidence",),
            proof_warning="Breakeven route does not approve another trade.",
            statistical_warning=(
                "Breakeven evidence does not prove statistical profitability."
            ),
            next_safe_action=(
                "Route to more evidence; do not treat breakeven as profit proof."
            ),
        )
    if selected_packet_preview == MISSING_OWNER_RESULT_PACKET_PREVIEW:
        return _ReviewRoute(
            classification=(
                OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_NO_OWNER_RESULT
            ),
            candidate_review_lane="owner_result_evidence_required",
            candidate_review_status="blocked_no_owner_result_payload",
            candidate_strength_label="no_candidate_without_owner_result",
            proof_candidate_summary=(
                "Missing owner-result evidence blocks profit proof candidate review."
            ),
            statistical_validity_status="not_valid_no_owner_result",
            evidence_depth_status="owner_result_evidence_required_before_review",
            evidence_depth_next_packet_preview=MISSING_OWNER_RESULT_PACKET_PREVIEW,
            single_result_candidate=False,
            evidence_depth_required=False,
            blocked_items=("owner_result_payload_missing",),
            proof_warning="Owner result evidence is required before proof review.",
            statistical_warning=(
                "No owner result exists for statistical profitability review."
            ),
            next_safe_action=(
                "Route to owner-result evidence required; do not review profit proof."
            ),
        )
    return _ReviewRoute(
        classification=OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_BLOCKED_UNSAFE,
        candidate_review_lane="unsafe_result_repair",
        candidate_review_status="blocked_unsafe_result_material",
        candidate_strength_label="unsafe_not_a_candidate",
        proof_candidate_summary=(
            "Unsafe result material blocks profit proof candidate review."
        ),
        statistical_validity_status="not_valid_unsafe_result_material",
        evidence_depth_status="unsafe_result_repair_required_before_review",
        evidence_depth_next_packet_preview=UNSAFE_PACKET_PREVIEW,
        single_result_candidate=False,
        evidence_depth_required=False,
        blocked_items=("unsafe_result_material_blocks_profit_proof_review",),
        proof_warning="Unsafe result material blocks proof review.",
        statistical_warning=(
            "Unsafe result material blocks reliable statistical review."
        ),
        next_safe_action=(
            "Route to unsafe result repair; do not review profit proof until safe."
        ),
    )


def _coerce_input(
    value: OandaLiveMicrotradeProfitProofCandidateReviewInput | Mapping[str, Any],
) -> OandaLiveMicrotradeProfitProofCandidateReviewInput:
    if isinstance(value, OandaLiveMicrotradeProfitProofCandidateReviewInput):
        return value
    raw = dict(value)
    return OandaLiveMicrotradeProfitProofCandidateReviewInput(
        catalog_input=raw.get("catalog_input", raw),
        owner_review_label=_safe_owner_review_label(
            raw.get("owner_review_label", "pending_owner_review")
        ),
        owner_notes_sanitized=_safe_owner_notes(raw.get("owner_notes_sanitized", "")),
    )


def _source_catalog_result(value: Any) -> Any:
    if _looks_like_catalog_result(value):
        return value
    return build_selected_proof_packet_preview_catalog(value)


def _looks_like_catalog_result(value: Any) -> bool:
    if isinstance(value, Mapping):
        return (
            "classification" in value
            and "selected_packet_preview" in value
            and "selected_packet_title" in value
        )
    return (
        hasattr(value, "classification")
        and hasattr(value, "selected_packet_preview")
        and hasattr(value, "selected_packet_title")
    )


def _field(value: Any, name: str, default: Any = "") -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _tuple_field(value: Any, name: str) -> tuple[str, ...]:
    raw_value = _field(value, name, ())
    if isinstance(raw_value, str):
        return (raw_value,)
    if isinstance(raw_value, tuple):
        return tuple(_text(item) for item in raw_value if _text(item))
    if isinstance(raw_value, list):
        return tuple(_text(item) for item in raw_value if _text(item))
    return ()


def _safe_owner_review_label(value: Any) -> str:
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
