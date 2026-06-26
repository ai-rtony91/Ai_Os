"""Preview-only router from one captured owner-run result to the next proof lane."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from automation.forex_engine.oanda_owner_run_live_microtrade_result_capture_epic_v1 import (
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_BLOCKED_NO_OWNER_RESULT,
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_BLOCKED_UNSAFE,
    OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_READY_FOR_OWNER_REVIEW,
    build_sample_breakeven_result_input as capture_breakeven_input,
    build_sample_loss_result_input as capture_loss_input,
    build_sample_missing_owner_result_input as capture_missing_input,
    build_sample_profit_result_input as capture_profit_input,
    build_sample_unsafe_result_input as capture_unsafe_input,
    run_oanda_owner_run_live_microtrade_result_capture_epic,
)
from automation.forex_engine.oanda_owner_run_live_microtrade_result_contract_v1 import (
    jsonable,
)


VERSION = "oanda_live_microtrade_result_to_next_proof_router_v1"
PACKET_ID = "AIOS-FOREX-OANDA-LIVE-MICROTRADE-RESULT-TO-NEXT-PROOF-ROUTER-V1"

OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_READY_FOR_OWNER_REVIEW = (
    "OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_READY_FOR_OWNER_REVIEW"
)
OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_REQUIRE_MORE_EVIDENCE = (
    "OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_REQUIRE_MORE_EVIDENCE"
)
OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_BLOCKED_UNSAFE = (
    "OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_BLOCKED_UNSAFE"
)
OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_BLOCKED_NO_OWNER_RESULT = (
    "OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_BLOCKED_NO_OWNER_RESULT"
)

EXACT_NEXT_OWNER_ACTION = (
    "Review the routed next-proof preview and decide whether the captured "
    "owner-run result should move to proof review, loss review, more evidence, "
    "no-owner-result repair, or unsafe-result repair; do not treat this as "
    "approval for another trade."
)
EXACT_NEXT_CODEX_PACKET = (
    "Use the packet preview selected by the router result. Do not execute that "
    "preview unless Anthony separately approves."
)
EXACT_ONE_SENTENCE_ANSWER = (
    "AIOS can now route one captured owner-run live microtrade result into the "
    "next proof lane, while repeat trading, broker action, vacation mode, "
    "compounding, and bank movement remain blocked."
)

PROFIT_ROUTING_REASON = (
    "Profit result can be reviewed as one proof candidate, not as approval for "
    "repeat trading."
)
LOSS_ROUTING_REASON = (
    "Loss result routes to loss review and candidate repair before any future "
    "owner decision."
)
BREAKEVEN_ROUTING_REASON = (
    "Breakeven result needs more evidence before proof promotion."
)
MISSING_OWNER_ROUTING_REASON = "No owner-result payload exists to route."
UNSAFE_ROUTING_REASON = "Unsafe result material blocks next proof routing."

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
)


@dataclass(frozen=True)
class OandaLiveMicrotradeResultToNextProofRouterInput:
    result_capture_input: Any
    owner_review_decision: str = "pending_owner_review"
    owner_notes_sanitized: str = ""


@dataclass(frozen=True)
class OandaLiveMicrotradeResultToNextProofRouterResult:
    version: str
    packet_id: str
    classification: str
    source_result_capture_status: str
    source_result_bucket: str
    source_classifier_status: str
    source_reconciliation_status: str
    source_ledger_bridge_status: str
    realized_pl: Any
    realized_r: Any
    risk_breach: bool
    max_loss_respected: bool
    next_proof_lane: str
    next_proof_packet_preview: str
    routing_reason: str
    owner_review_required: bool
    preview_only: bool
    router_only: bool
    result_capture_only: bool
    required_owner_decision: str
    blocked_items: tuple[str, ...]
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
    exact_next_owner_action: str
    exact_next_codex_packet: str
    one_sentence_answer: str
    next_safe_action: str


@dataclass(frozen=True)
class _Route:
    classification: str
    next_proof_lane: str
    next_proof_packet_preview: str
    routing_reason: str
    blocked_items: tuple[str, ...]
    next_safe_action: str


def build_sample_profit_router_input() -> OandaLiveMicrotradeResultToNextProofRouterInput:
    return OandaLiveMicrotradeResultToNextProofRouterInput(
        result_capture_input=capture_profit_input()
    )


def build_sample_loss_router_input() -> OandaLiveMicrotradeResultToNextProofRouterInput:
    return OandaLiveMicrotradeResultToNextProofRouterInput(
        result_capture_input=capture_loss_input()
    )


def build_sample_breakeven_router_input() -> OandaLiveMicrotradeResultToNextProofRouterInput:
    return OandaLiveMicrotradeResultToNextProofRouterInput(
        result_capture_input=capture_breakeven_input()
    )


def build_sample_missing_owner_result_router_input() -> OandaLiveMicrotradeResultToNextProofRouterInput:
    return OandaLiveMicrotradeResultToNextProofRouterInput(
        result_capture_input=capture_missing_input()
    )


def build_sample_unsafe_router_input() -> OandaLiveMicrotradeResultToNextProofRouterInput:
    return OandaLiveMicrotradeResultToNextProofRouterInput(
        result_capture_input=capture_unsafe_input()
    )


def route_oanda_live_microtrade_result_to_next_proof(
    router_input: OandaLiveMicrotradeResultToNextProofRouterInput | Mapping[str, Any] | None = None,
) -> OandaLiveMicrotradeResultToNextProofRouterResult:
    active_input = _coerce_input(router_input or build_sample_profit_router_input())
    source_result = _source_capture_result(active_input.result_capture_input)
    route = _select_route(source_result)
    protected_flags = protected_flags_false()
    return OandaLiveMicrotradeResultToNextProofRouterResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=route.classification,
        source_result_capture_status=_field(source_result, "classification"),
        source_result_bucket=_field(source_result, "result_bucket"),
        source_classifier_status=_field(source_result, "classifier_status"),
        source_reconciliation_status=_field(source_result, "reconciliation_status"),
        source_ledger_bridge_status=_field(source_result, "ledger_bridge_status"),
        realized_pl=_field(source_result, "realized_pl"),
        realized_r=_field(source_result, "realized_r"),
        risk_breach=bool(_field(source_result, "risk_breach", False)),
        max_loss_respected=bool(_field(source_result, "max_loss_respected", False)),
        next_proof_lane=route.next_proof_lane,
        next_proof_packet_preview=route.next_proof_packet_preview,
        routing_reason=route.routing_reason,
        owner_review_required=True,
        preview_only=True,
        router_only=True,
        result_capture_only=True,
        required_owner_decision=_required_owner_decision(active_input.owner_review_decision),
        blocked_items=route.blocked_items,
        protected_flags=protected_flags,
        **protected_flags,
        exact_next_owner_action=EXACT_NEXT_OWNER_ACTION,
        exact_next_codex_packet=EXACT_NEXT_CODEX_PACKET,
        one_sentence_answer=EXACT_ONE_SENTENCE_ANSWER,
        next_safe_action=route.next_safe_action,
    )


def protected_flags_false() -> dict[str, bool]:
    return {flag_name: False for flag_name in PROTECTED_FLAG_NAMES}


def to_jsonable_dict(result: Any) -> dict[str, Any]:
    return jsonable(result)


def to_operator_text(result: OandaLiveMicrotradeResultToNextProofRouterResult) -> str:
    return "\n".join(
        (
            f"Result-to-next-proof router status: {result.classification}.",
            f"Next proof lane: {result.next_proof_lane}.",
            f"Packet preview: {result.next_proof_packet_preview}.",
            f"Routing reason: {result.routing_reason}",
            result.one_sentence_answer,
            "No next trade approval was granted.",
        )
    )


def to_markdown(result: OandaLiveMicrotradeResultToNextProofRouterResult) -> str:
    rows = [
        "# AIOS Forex OANDA Live Microtrade Result-To-Next-Proof Router V1",
        "",
        f"- Packet ID: `{result.packet_id}`",
        f"- Classification: `{result.classification}`",
        f"- Source result capture status: `{result.source_result_capture_status}`",
        f"- Source result bucket: `{result.source_result_bucket}`",
        f"- Source classifier status: `{result.source_classifier_status}`",
        f"- Source reconciliation status: `{result.source_reconciliation_status}`",
        f"- Source ledger bridge status: `{result.source_ledger_bridge_status}`",
        f"- Next proof lane: `{result.next_proof_lane}`",
        f"- Next proof packet preview: `{result.next_proof_packet_preview}`",
        f"- Routing reason: {result.routing_reason}",
        f"- Owner review required: `{str(result.owner_review_required).lower()}`",
        f"- Preview only: `{str(result.preview_only).lower()}`",
        f"- Router only: `{str(result.router_only).lower()}`",
        f"- Result capture only: `{str(result.result_capture_only).lower()}`",
        "",
        "## Blocked Items",
    ]
    rows.extend(f"- `{item}`" for item in result.blocked_items)
    rows.extend(
        (
            "",
            "## Next Actions",
            f"- Owner: {result.exact_next_owner_action}",
            f"- Codex packet policy: {result.exact_next_codex_packet}",
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
        "- No real money approval was granted.",
        "- No compounding approval was granted.",
        "- No bank movement approval was granted.",
        "- No autonomous execution was granted.",
        "- Unattended vacation mode remains blocked.",
        "- Vacation profit trial remains blocked unless Anthony separately approves.",
        "- Profit is not guaranteed.",
        "- One result does not prove statistical profitability.",
        "- All protected flags remain false.",
        "- Router preview only.",
        "- Read-only only.",
    ]


def _coerce_input(
    value: OandaLiveMicrotradeResultToNextProofRouterInput | Mapping[str, Any],
) -> OandaLiveMicrotradeResultToNextProofRouterInput:
    if isinstance(value, OandaLiveMicrotradeResultToNextProofRouterInput):
        return value
    raw = dict(value)
    return OandaLiveMicrotradeResultToNextProofRouterInput(
        result_capture_input=raw.get("result_capture_input", raw),
        owner_review_decision=_text(raw.get("owner_review_decision"), "pending_owner_review"),
        owner_notes_sanitized=_text(raw.get("owner_notes_sanitized")),
    )


def _source_capture_result(value: Any) -> Any:
    if _looks_like_capture_result(value):
        return value
    return run_oanda_owner_run_live_microtrade_result_capture_epic(value)


def _looks_like_capture_result(value: Any) -> bool:
    if isinstance(value, Mapping):
        return "classification" in value and "result_bucket" in value
    return hasattr(value, "classification") and hasattr(value, "result_bucket")


def _field(value: Any, name: str, default: Any = "") -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _select_route(source_result: Any) -> _Route:
    status = _field(source_result, "classification")
    bucket = _field(source_result, "result_bucket")
    risk_breach = bool(_field(source_result, "risk_breach", False))

    if status == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_BLOCKED_NO_OWNER_RESULT:
        return _Route(
            classification=OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_BLOCKED_NO_OWNER_RESULT,
            next_proof_lane="owner_result_evidence_required",
            next_proof_packet_preview=(
                "AIOS-FOREX-OANDA-LIVE-MICROTRADE-OWNER-RESULT-EVIDENCE-REQUIRED-V1"
            ),
            routing_reason=MISSING_OWNER_ROUTING_REASON,
            blocked_items=("owner_result_payload_missing",),
            next_safe_action=(
                "Provide one sanitized owner-result payload before any next proof "
                "packet can be reviewed."
            ),
        )
    if (
        status == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_BLOCKED_UNSAFE
        or bucket == "unsafe"
        or risk_breach
    ):
        return _Route(
            classification=OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_BLOCKED_UNSAFE,
            next_proof_lane="unsafe_result_repair",
            next_proof_packet_preview=(
                "AIOS-FOREX-OANDA-LIVE-MICROTRADE-UNSAFE-RESULT-REPAIR-V1"
            ),
            routing_reason=UNSAFE_ROUTING_REASON,
            blocked_items=("unsafe_result_material_blocks_next_proof_routing",),
            next_safe_action=(
                "Stop and repair unsafe result material before any proof review "
                "packet is considered."
            ),
        )
    if (
        status == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_READY_FOR_OWNER_REVIEW
        and bucket == "profit"
    ):
        return _Route(
            classification=OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_READY_FOR_OWNER_REVIEW,
            next_proof_lane="live_proof_candidate_review",
            next_proof_packet_preview=(
                "AIOS-FOREX-OANDA-LIVE-MICROTRADE-PROFIT-PROOF-CANDIDATE-REVIEW-V1"
            ),
            routing_reason=PROFIT_ROUTING_REASON,
            blocked_items=(),
            next_safe_action=(
                "Review the profit result as one proof candidate only; do not "
                "authorize another trade from this router."
            ),
        )
    if (
        status == OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_READY_FOR_OWNER_REVIEW
        and bucket == "loss"
    ):
        return _Route(
            classification=OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_READY_FOR_OWNER_REVIEW,
            next_proof_lane="loss_review_and_next_profit_candidate_gate",
            next_proof_packet_preview=(
                "AIOS-FOREX-OANDA-LIVE-MICROTRADE-LOSS-TO-NEXT-PROFIT-CANDIDATE-GATE-V1"
            ),
            routing_reason=LOSS_ROUTING_REASON,
            blocked_items=(),
            next_safe_action=(
                "Review the loss result and repair candidate evidence before any "
                "future owner decision."
            ),
        )
    return _Route(
        classification=OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_REQUIRE_MORE_EVIDENCE,
        next_proof_lane="more_evidence_required",
        next_proof_packet_preview=(
            "AIOS-FOREX-OANDA-LIVE-MICROTRADE-BREAKEVEN-MORE-EVIDENCE-V1"
        ),
        routing_reason=BREAKEVEN_ROUTING_REASON,
        blocked_items=(),
        next_safe_action=(
            "Collect more sanitized evidence before considering proof promotion."
        ),
    )


def _required_owner_decision(owner_review_decision: str) -> str:
    text = _text(owner_review_decision, "pending_owner_review")
    if not text:
        return "pending_owner_review"
    lowered = text.lower()
    unsafe_words = ("approve", "authorize", "trade", "broker", "compound", "bank")
    if any(word in lowered for word in unsafe_words):
        return "pending_owner_review"
    return text


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return value.strip() if isinstance(value, str) else str(value).strip()
