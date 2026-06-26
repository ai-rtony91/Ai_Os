"""Owner-review decision gate for routed live microtrade proof previews."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Mapping

from automation.forex_engine.oanda_live_microtrade_result_to_next_proof_router_v1 import (
    OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_BLOCKED_NO_OWNER_RESULT,
    OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_BLOCKED_UNSAFE,
    OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_READY_FOR_OWNER_REVIEW,
    OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_REQUIRE_MORE_EVIDENCE,
    build_sample_breakeven_router_input,
    build_sample_loss_router_input,
    build_sample_missing_owner_result_router_input,
    build_sample_profit_router_input,
    build_sample_unsafe_router_input,
    route_oanda_live_microtrade_result_to_next_proof,
)


VERSION = "oanda_live_microtrade_routed_proof_owner_decision_gate_v1"
PACKET_ID = (
    "AIOS-FOREX-OANDA-LIVE-MICROTRADE-ROUTED-PROOF-OWNER-DECISION-GATE-V1"
)

OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_READY_FOR_OWNER_REVIEW = (
    "OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_READY_FOR_OWNER_REVIEW"
)
OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_REQUIRE_MORE_EVIDENCE = (
    "OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_REQUIRE_MORE_EVIDENCE"
)
OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_BLOCKED_NO_OWNER_RESULT = (
    "OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_BLOCKED_NO_OWNER_RESULT"
)
OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_BLOCKED_UNSAFE = (
    "OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_BLOCKED_UNSAFE"
)

EXACT_NEXT_OWNER_ACTION = (
    "Review the selected proof preview and decide whether to request a "
    "proof-review packet, loss-review packet, more-evidence packet, "
    "owner-result repair packet, or unsafe-result repair packet. This does not "
    "approve another trade."
)
EXACT_NEXT_CODEX_PACKET_POLICY = (
    "Use the selected packet preview only after Anthony separately approves "
    "that exact packet. Do not execute selected preview from this gate."
)
ONE_SENTENCE_ANSWER = (
    "AIOS can now convert the routed result preview into an owner-decision "
    "package, while next-trade authorization, broker action, vacation mode, "
    "compounding, and bank movement remain blocked."
)

PROFIT_PROOF_WARNING = (
    "Profit route is a proof candidate only, not approval for repeat trading."
)
PROFIT_STATISTICAL_WARNING = "One result does not prove statistical profitability."
LOSS_PROOF_WARNING = (
    "Loss route must repair candidate evidence before any future owner decision."
)
LOSS_STATISTICAL_WARNING = (
    "One loss does not prove the system is invalid, but it blocks profit proof."
)
MORE_EVIDENCE_PROOF_WARNING = "Evidence is insufficient for proof promotion."
MORE_EVIDENCE_STATISTICAL_WARNING = "Additional sanitized results are required."
MISSING_OWNER_PROOF_WARNING = "Owner result evidence is required before review."
MISSING_OWNER_STATISTICAL_WARNING = "No owner result exists for proof analysis."
UNSAFE_PROOF_WARNING = "Unsafe result material must be repaired before review."
UNSAFE_STATISTICAL_WARNING = "Unsafe result material blocks reliable proof analysis."

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
)


@dataclass(frozen=True)
class OandaLiveMicrotradeRoutedProofOwnerDecisionGateInput:
    router_input: Any
    owner_decision_label: str = "pending_owner_review"
    owner_notes_sanitized: str = ""


@dataclass(frozen=True)
class OandaLiveMicrotradeRoutedProofOwnerDecisionGateResult:
    version: str
    packet_id: str
    classification: str
    source_router_status: str
    source_next_proof_lane: str
    source_next_proof_packet_preview: str
    source_routing_reason: str
    selected_review_lane: str
    selected_packet_preview: str
    owner_decision_label: str
    owner_review_required: bool
    selected_packet_preview_only: bool
    preview_only: bool
    decision_gate_only: bool
    required_owner_action: str
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


@dataclass(frozen=True)
class _DecisionRoute:
    classification: str
    selected_review_lane: str
    selected_packet_preview: str
    blocked_items: tuple[str, ...]
    proof_warning: str
    statistical_warning: str
    next_safe_action: str


def build_sample_profit_decision_input() -> OandaLiveMicrotradeRoutedProofOwnerDecisionGateInput:
    return OandaLiveMicrotradeRoutedProofOwnerDecisionGateInput(
        router_input=route_oanda_live_microtrade_result_to_next_proof(
            build_sample_profit_router_input()
        )
    )


def build_sample_loss_decision_input() -> OandaLiveMicrotradeRoutedProofOwnerDecisionGateInput:
    return OandaLiveMicrotradeRoutedProofOwnerDecisionGateInput(
        router_input=route_oanda_live_microtrade_result_to_next_proof(
            build_sample_loss_router_input()
        )
    )


def build_sample_breakeven_decision_input() -> (
    OandaLiveMicrotradeRoutedProofOwnerDecisionGateInput
):
    return OandaLiveMicrotradeRoutedProofOwnerDecisionGateInput(
        router_input=route_oanda_live_microtrade_result_to_next_proof(
            build_sample_breakeven_router_input()
        )
    )


def build_sample_missing_owner_result_decision_input() -> (
    OandaLiveMicrotradeRoutedProofOwnerDecisionGateInput
):
    return OandaLiveMicrotradeRoutedProofOwnerDecisionGateInput(
        router_input=route_oanda_live_microtrade_result_to_next_proof(
            build_sample_missing_owner_result_router_input()
        )
    )


def build_sample_unsafe_decision_input() -> OandaLiveMicrotradeRoutedProofOwnerDecisionGateInput:
    return OandaLiveMicrotradeRoutedProofOwnerDecisionGateInput(
        router_input=route_oanda_live_microtrade_result_to_next_proof(
            build_sample_unsafe_router_input()
        )
    )


def evaluate_oanda_live_microtrade_routed_proof_owner_decision_gate(
    decision_input: (
        OandaLiveMicrotradeRoutedProofOwnerDecisionGateInput | Mapping[str, Any] | None
    ) = None,
) -> OandaLiveMicrotradeRoutedProofOwnerDecisionGateResult:
    active_input = _coerce_input(decision_input or build_sample_profit_decision_input())
    source_router_result = _source_router_result(active_input.router_input)
    route = _select_decision_route(source_router_result)
    protected_flags = protected_flags_false()
    return OandaLiveMicrotradeRoutedProofOwnerDecisionGateResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=route.classification,
        source_router_status=_field(source_router_result, "classification"),
        source_next_proof_lane=_field(source_router_result, "next_proof_lane"),
        source_next_proof_packet_preview=_field(
            source_router_result, "next_proof_packet_preview"
        ),
        source_routing_reason=_field(source_router_result, "routing_reason"),
        selected_review_lane=route.selected_review_lane,
        selected_packet_preview=route.selected_packet_preview,
        owner_decision_label=_safe_owner_decision_label(
            active_input.owner_decision_label
        ),
        owner_review_required=True,
        selected_packet_preview_only=True,
        preview_only=True,
        decision_gate_only=True,
        required_owner_action=EXACT_NEXT_OWNER_ACTION,
        blocked_items=route.blocked_items,
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


def to_operator_text(result: OandaLiveMicrotradeRoutedProofOwnerDecisionGateResult) -> str:
    return "\n".join(
        (
            f"Routed proof owner decision status: {result.classification}.",
            f"Selected review lane: {result.selected_review_lane}.",
            f"Selected packet preview: {result.selected_packet_preview}.",
            f"Proof warning: {result.proof_warning}",
            f"Statistical warning: {result.statistical_warning}",
            result.one_sentence_answer,
            "No selected packet execution approval was granted.",
            "No next trade approval was granted.",
        )
    )


def to_markdown(result: OandaLiveMicrotradeRoutedProofOwnerDecisionGateResult) -> str:
    rows = [
        "# AIOS Forex OANDA Live Microtrade Routed Proof Owner Decision Gate V1",
        "",
        f"- Packet ID: `{result.packet_id}`",
        f"- Classification: `{result.classification}`",
        f"- Source router status: `{result.source_router_status}`",
        f"- Source next proof lane: `{result.source_next_proof_lane}`",
        f"- Source next proof packet preview: `{result.source_next_proof_packet_preview}`",
        f"- Source routing reason: {result.source_routing_reason}",
        f"- Selected review lane: `{result.selected_review_lane}`",
        f"- Selected packet preview: `{result.selected_packet_preview}`",
        f"- Owner review required: `{str(result.owner_review_required).lower()}`",
        f"- Selected packet preview only: `{str(result.selected_packet_preview_only).lower()}`",
        f"- Preview only: `{str(result.preview_only).lower()}`",
        f"- Decision gate only: `{str(result.decision_gate_only).lower()}`",
        "",
        "## Warnings",
        f"- Proof warning: {result.proof_warning}",
        f"- Statistical warning: {result.statistical_warning}",
        "",
        "## Blocked Items",
    ]
    rows.extend(f"- `{item}`" for item in result.blocked_items)
    if not result.blocked_items:
        rows.append("- None.")
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
        "- No real money approval was granted.",
        "- No compounding approval was granted.",
        "- No bank movement approval was granted.",
        "- No autonomous execution was granted.",
        "- Unattended vacation mode remains blocked.",
        "- Vacation profit trial remains blocked unless Anthony separately approves.",
        "- Profit is not guaranteed.",
        "- One result does not prove statistical profitability.",
        "- All protected flags remain false.",
        "- Decision gate preview only.",
        "- Read-only only.",
    ]


def _select_decision_route(source_router_result: Any) -> _DecisionRoute:
    source_status = _field(source_router_result, "classification")
    source_lane = _field(source_router_result, "next_proof_lane")

    if (
        source_status == OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_READY_FOR_OWNER_REVIEW
        and source_lane == "live_proof_candidate_review"
    ):
        return _DecisionRoute(
            classification=(
                OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_READY_FOR_OWNER_REVIEW
            ),
            selected_review_lane="profit_proof_candidate_review",
            selected_packet_preview=(
                "AIOS-FOREX-OANDA-LIVE-MICROTRADE-PROFIT-PROOF-CANDIDATE-REVIEW-V1"
            ),
            blocked_items=(),
            proof_warning=PROFIT_PROOF_WARNING,
            statistical_warning=PROFIT_STATISTICAL_WARNING,
            next_safe_action=(
                "Anthony may review the profit proof candidate preview only; "
                "another trade still requires separate approval."
            ),
        )
    if (
        source_status == OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_READY_FOR_OWNER_REVIEW
        and source_lane == "loss_review_and_next_profit_candidate_gate"
    ):
        return _DecisionRoute(
            classification=(
                OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_READY_FOR_OWNER_REVIEW
            ),
            selected_review_lane="loss_review_and_next_profit_candidate_gate",
            selected_packet_preview=(
                "AIOS-FOREX-OANDA-LIVE-MICROTRADE-LOSS-TO-NEXT-PROFIT-CANDIDATE-GATE-V1"
            ),
            blocked_items=(),
            proof_warning=LOSS_PROOF_WARNING,
            statistical_warning=LOSS_STATISTICAL_WARNING,
            next_safe_action=(
                "Anthony may review the loss repair preview only; profit proof "
                "remains blocked."
            ),
        )
    if source_status == OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_REQUIRE_MORE_EVIDENCE:
        return _DecisionRoute(
            classification=(
                OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_REQUIRE_MORE_EVIDENCE
            ),
            selected_review_lane="more_evidence_required",
            selected_packet_preview=(
                "AIOS-FOREX-OANDA-LIVE-MICROTRADE-BREAKEVEN-MORE-EVIDENCE-V1"
            ),
            blocked_items=(),
            proof_warning=MORE_EVIDENCE_PROOF_WARNING,
            statistical_warning=MORE_EVIDENCE_STATISTICAL_WARNING,
            next_safe_action=(
                "Collect more sanitized owner-result evidence before any proof "
                "promotion review."
            ),
        )
    if source_status == OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_BLOCKED_NO_OWNER_RESULT:
        return _DecisionRoute(
            classification=(
                OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_BLOCKED_NO_OWNER_RESULT
            ),
            selected_review_lane="owner_result_evidence_required",
            selected_packet_preview=(
                "AIOS-FOREX-OANDA-LIVE-MICROTRADE-OWNER-RESULT-EVIDENCE-REQUIRED-V1"
            ),
            blocked_items=("owner_result_payload_missing",),
            proof_warning=MISSING_OWNER_PROOF_WARNING,
            statistical_warning=MISSING_OWNER_STATISTICAL_WARNING,
            next_safe_action=(
                "Provide sanitized owner-result evidence before a decision package "
                "can advance."
            ),
        )
    return _DecisionRoute(
        classification=OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_BLOCKED_UNSAFE,
        selected_review_lane="unsafe_result_repair",
        selected_packet_preview=(
            "AIOS-FOREX-OANDA-LIVE-MICROTRADE-UNSAFE-RESULT-REPAIR-V1"
        ),
        blocked_items=("unsafe_result_material_blocks_owner_decision",),
        proof_warning=UNSAFE_PROOF_WARNING,
        statistical_warning=UNSAFE_STATISTICAL_WARNING,
        next_safe_action=(
            "Stop and repair unsafe result material before Anthony reviews any "
            "proof packet preview."
        ),
    )


def _coerce_input(
    value: OandaLiveMicrotradeRoutedProofOwnerDecisionGateInput | Mapping[str, Any],
) -> OandaLiveMicrotradeRoutedProofOwnerDecisionGateInput:
    if isinstance(value, OandaLiveMicrotradeRoutedProofOwnerDecisionGateInput):
        return value
    raw = dict(value)
    return OandaLiveMicrotradeRoutedProofOwnerDecisionGateInput(
        router_input=raw.get("router_input", raw),
        owner_decision_label=_text(raw.get("owner_decision_label"), "pending_owner_review"),
        owner_notes_sanitized=_text(raw.get("owner_notes_sanitized")),
    )


def _source_router_result(value: Any) -> Any:
    if _looks_like_router_result(value):
        return value
    return route_oanda_live_microtrade_result_to_next_proof(value)


def _looks_like_router_result(value: Any) -> bool:
    if isinstance(value, Mapping):
        return (
            "classification" in value
            and "next_proof_lane" in value
            and "next_proof_packet_preview" in value
        )
    return (
        hasattr(value, "classification")
        and hasattr(value, "next_proof_lane")
        and hasattr(value, "next_proof_packet_preview")
    )


def _field(value: Any, name: str, default: Any = "") -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _safe_owner_decision_label(value: Any) -> str:
    text = _text(value, "pending_owner_review")
    if not text:
        return "pending_owner_review"
    unsafe_words = (
        "approve",
        "authorize",
        "trade",
        "broker",
        "compound",
        "bank",
        "execute",
        "live",
    )
    if any(word in text.lower() for word in unsafe_words):
        return "pending_owner_review"
    return text


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return value.strip() if isinstance(value, str) else str(value).strip()


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {field.name: _jsonable(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple | list):
        return [_jsonable(item) for item in value]
    return value
