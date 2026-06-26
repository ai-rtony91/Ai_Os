"""Selected proof packet preview catalog for routed live microtrade decisions."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Mapping

from automation.forex_engine.oanda_live_microtrade_routed_proof_owner_decision_gate_v1 import (
    OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_BLOCKED_NO_OWNER_RESULT,
    OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_BLOCKED_UNSAFE,
    OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_READY_FOR_OWNER_REVIEW,
    OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_REQUIRE_MORE_EVIDENCE,
    build_sample_breakeven_decision_input,
    build_sample_loss_decision_input,
    build_sample_missing_owner_result_decision_input,
    build_sample_profit_decision_input,
    build_sample_unsafe_decision_input,
    evaluate_oanda_live_microtrade_routed_proof_owner_decision_gate,
)


VERSION = "oanda_live_microtrade_selected_proof_packet_preview_catalog_v1"
PACKET_ID = (
    "AIOS-FOREX-OANDA-LIVE-MICROTRADE-SELECTED-PROOF-PACKET-"
    "PREVIEW-CATALOG-V1"
)

OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_READY_FOR_OWNER_REVIEW = (
    "OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_READY_FOR_OWNER_REVIEW"
)
OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_REQUIRE_MORE_EVIDENCE = (
    "OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_REQUIRE_MORE_EVIDENCE"
)
OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_BLOCKED_NO_OWNER_RESULT = (
    "OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_BLOCKED_NO_OWNER_RESULT"
)
OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_BLOCKED_UNSAFE = (
    "OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_BLOCKED_UNSAFE"
)

EXACT_NEXT_OWNER_ACTION = (
    "Review the selected proof packet preview catalog entry and decide whether "
    "to request that exact future packet prompt. This does not approve "
    "execution, commit, push, PR, merge, broker action, or another trade."
)
EXACT_NEXT_CODEX_PACKET_POLICY = (
    "Do not execute the selected packet preview from this catalog. Generate or "
    "execute a future packet only after Anthony separately approves the exact "
    "next packet."
)
ONE_SENTENCE_ANSWER = (
    "AIOS can now prepare non-executable selected proof packet previews for "
    "every routed owner-decision outcome while next-trade authorization, "
    "broker action, selected-packet execution, compounding, vacation mode, "
    "and bank movement remain blocked."
)

PROOF_WARNING = (
    "Selected proof packet previews are review material only; profit is not "
    "guaranteed."
)
STATISTICAL_WARNING = "One result does not prove statistical profitability."

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
)

SELECTED_PACKET_BLOCKED_ACTIONS = (
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


@dataclass(frozen=True)
class OandaLiveMicrotradeSelectedProofPacketPreviewCatalogInput:
    decision_gate_input: Any
    owner_preview_label: str = "pending_owner_review"
    owner_notes_sanitized: str = ""


@dataclass(frozen=True)
class OandaLiveMicrotradeSelectedProofPacketPreviewCatalogResult:
    version: str
    packet_id: str
    classification: str
    source_decision_status: str
    source_selected_review_lane: str
    source_selected_packet_preview: str
    selected_packet_preview: str
    selected_packet_title: str
    selected_packet_purpose: str
    selected_packet_non_execution_notice: str
    selected_packet_required_owner_review: bool
    selected_packet_blocked_actions: tuple[str, ...]
    selected_packet_allowed_next_human_action: str
    selected_packet_forbidden_actions: tuple[str, ...]
    preview_catalog_entry: Mapping[str, Any]
    proof_warning: str
    statistical_warning: str
    owner_review_required: bool
    selected_packet_preview_only: bool
    preview_only: bool
    catalog_only: bool
    execution_blocked: bool
    blocked_items: tuple[str, ...]
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


@dataclass(frozen=True)
class _CatalogRoute:
    classification: str
    selected_packet_preview: str
    selected_packet_title: str
    selected_packet_purpose: str
    selected_packet_non_execution_notice: str
    selected_packet_allowed_next_human_action: str
    next_safe_action: str


def build_sample_profit_catalog_input() -> (
    OandaLiveMicrotradeSelectedProofPacketPreviewCatalogInput
):
    return OandaLiveMicrotradeSelectedProofPacketPreviewCatalogInput(
        decision_gate_input=_decision_output(build_sample_profit_decision_input())
    )


def build_sample_loss_catalog_input() -> (
    OandaLiveMicrotradeSelectedProofPacketPreviewCatalogInput
):
    return OandaLiveMicrotradeSelectedProofPacketPreviewCatalogInput(
        decision_gate_input=_decision_output(build_sample_loss_decision_input())
    )


def build_sample_breakeven_catalog_input() -> (
    OandaLiveMicrotradeSelectedProofPacketPreviewCatalogInput
):
    return OandaLiveMicrotradeSelectedProofPacketPreviewCatalogInput(
        decision_gate_input=_decision_output(build_sample_breakeven_decision_input())
    )


def build_sample_missing_owner_result_catalog_input() -> (
    OandaLiveMicrotradeSelectedProofPacketPreviewCatalogInput
):
    return OandaLiveMicrotradeSelectedProofPacketPreviewCatalogInput(
        decision_gate_input=_decision_output(
            build_sample_missing_owner_result_decision_input()
        )
    )


def build_sample_unsafe_catalog_input() -> (
    OandaLiveMicrotradeSelectedProofPacketPreviewCatalogInput
):
    return OandaLiveMicrotradeSelectedProofPacketPreviewCatalogInput(
        decision_gate_input=_decision_output(build_sample_unsafe_decision_input())
    )


def build_selected_proof_packet_preview_catalog(
    catalog_input: (
        OandaLiveMicrotradeSelectedProofPacketPreviewCatalogInput
        | Mapping[str, Any]
        | None
    ) = None,
) -> OandaLiveMicrotradeSelectedProofPacketPreviewCatalogResult:
    active_input = _coerce_input(catalog_input or build_sample_profit_catalog_input())
    source_decision_result = _source_decision_result(active_input.decision_gate_input)
    route = _select_catalog_route(source_decision_result)
    protected_flags = protected_flags_false()
    source_blocked_items = tuple(_field(source_decision_result, "blocked_items", ()))
    blocked_items = _unique_tuple(source_blocked_items + SELECTED_PACKET_BLOCKED_ACTIONS)
    owner_preview_label = _safe_owner_preview_label(active_input.owner_preview_label)
    owner_notes = _safe_owner_notes(active_input.owner_notes_sanitized)
    preview_catalog_entry = {
        "classification": route.classification,
        "source_decision_status": _field(source_decision_result, "classification"),
        "source_selected_review_lane": _field(source_decision_result, "selected_review_lane"),
        "source_selected_packet_preview": _field(
            source_decision_result, "selected_packet_preview"
        ),
        "selected_packet_preview": route.selected_packet_preview,
        "selected_packet_title": route.selected_packet_title,
        "selected_packet_purpose": route.selected_packet_purpose,
        "selected_packet_non_execution_notice": route.selected_packet_non_execution_notice,
        "selected_packet_allowed_next_human_action": (
            route.selected_packet_allowed_next_human_action
        ),
        "selected_packet_blocked_actions": SELECTED_PACKET_BLOCKED_ACTIONS,
        "selected_packet_forbidden_actions": SELECTED_PACKET_BLOCKED_ACTIONS,
        "owner_preview_label": owner_preview_label,
        "owner_notes_sanitized": owner_notes,
        "proof_warning": PROOF_WARNING,
        "statistical_warning": STATISTICAL_WARNING,
        "exact_next_owner_action": EXACT_NEXT_OWNER_ACTION,
        "exact_next_codex_packet_policy": EXACT_NEXT_CODEX_PACKET_POLICY,
    }
    return OandaLiveMicrotradeSelectedProofPacketPreviewCatalogResult(
        version=VERSION,
        packet_id=PACKET_ID,
        classification=route.classification,
        source_decision_status=_field(source_decision_result, "classification"),
        source_selected_review_lane=_field(source_decision_result, "selected_review_lane"),
        source_selected_packet_preview=_field(
            source_decision_result, "selected_packet_preview"
        ),
        selected_packet_preview=route.selected_packet_preview,
        selected_packet_title=route.selected_packet_title,
        selected_packet_purpose=route.selected_packet_purpose,
        selected_packet_non_execution_notice=route.selected_packet_non_execution_notice,
        selected_packet_required_owner_review=True,
        selected_packet_blocked_actions=SELECTED_PACKET_BLOCKED_ACTIONS,
        selected_packet_allowed_next_human_action=(
            route.selected_packet_allowed_next_human_action
        ),
        selected_packet_forbidden_actions=SELECTED_PACKET_BLOCKED_ACTIONS,
        preview_catalog_entry=preview_catalog_entry,
        proof_warning=PROOF_WARNING,
        statistical_warning=STATISTICAL_WARNING,
        owner_review_required=True,
        selected_packet_preview_only=True,
        preview_only=True,
        catalog_only=True,
        execution_blocked=True,
        blocked_items=blocked_items,
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
    result: OandaLiveMicrotradeSelectedProofPacketPreviewCatalogResult,
) -> str:
    return "\n".join(
        (
            f"Selected proof packet preview catalog status: {result.classification}.",
            f"Selected packet preview: {result.selected_packet_preview}.",
            f"Selected packet title: {result.selected_packet_title}.",
            f"Purpose: {result.selected_packet_purpose}",
            f"Notice: {result.selected_packet_non_execution_notice}",
            f"Owner action: {result.exact_next_owner_action}",
            f"Codex packet policy: {result.exact_next_codex_packet_policy}",
            result.one_sentence_answer,
            "No selected packet execution approval was granted.",
            "No next trade approval was granted.",
            "No broker call was made by this packet.",
        )
    )


def to_markdown(
    result: OandaLiveMicrotradeSelectedProofPacketPreviewCatalogResult,
) -> str:
    rows = [
        "# AIOS Forex OANDA Live Microtrade Selected Proof Packet Preview Catalog V1",
        "",
        f"- Packet ID: `{result.packet_id}`",
        f"- Classification: `{result.classification}`",
        f"- Source decision status: `{result.source_decision_status}`",
        f"- Source selected review lane: `{result.source_selected_review_lane}`",
        f"- Source selected packet preview: `{result.source_selected_packet_preview}`",
        f"- Selected packet preview: `{result.selected_packet_preview}`",
        f"- Selected packet title: {result.selected_packet_title}",
        f"- Selected packet purpose: {result.selected_packet_purpose}",
        f"- Non-execution notice: {result.selected_packet_non_execution_notice}",
        f"- Owner review required: `{str(result.owner_review_required).lower()}`",
        f"- Selected packet preview only: `{str(result.selected_packet_preview_only).lower()}`",
        f"- Preview only: `{str(result.preview_only).lower()}`",
        f"- Catalog only: `{str(result.catalog_only).lower()}`",
        f"- Execution blocked: `{str(result.execution_blocked).lower()}`",
        "",
        "## Warnings",
        f"- Proof warning: {result.proof_warning}",
        f"- Statistical warning: {result.statistical_warning}",
        "",
        "## Blocked Selected-Packet Actions",
    ]
    rows.extend(f"- `{item}`" for item in result.selected_packet_blocked_actions)
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
        "- All protected flags remain false.",
        "- Selected proof packet preview catalog only.",
        "- Read-only only.",
    ]


def _decision_output(value: Any) -> Any:
    return evaluate_oanda_live_microtrade_routed_proof_owner_decision_gate(value)


def _select_catalog_route(source_decision_result: Any) -> _CatalogRoute:
    selected_review_lane = _field(source_decision_result, "selected_review_lane")
    source_status = _field(source_decision_result, "classification")
    if (
        source_status
        == OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_READY_FOR_OWNER_REVIEW
        and selected_review_lane == "profit_proof_candidate_review"
    ):
        return _CatalogRoute(
            classification=(
                OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_READY_FOR_OWNER_REVIEW
            ),
            selected_packet_preview=(
                "AIOS-FOREX-OANDA-LIVE-MICROTRADE-PROFIT-PROOF-CANDIDATE-REVIEW-V1"
            ),
            selected_packet_title="Profit Proof Candidate Review Preview",
            selected_packet_purpose=(
                "Review one captured profit result as a proof candidate only."
            ),
            selected_packet_non_execution_notice=(
                "This preview does not authorize trade execution or repeat trading."
            ),
            selected_packet_allowed_next_human_action=(
                "Anthony may approve a future proof-review packet prompt only."
            ),
            next_safe_action=EXACT_NEXT_OWNER_ACTION,
        )
    if (
        source_status
        == OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_READY_FOR_OWNER_REVIEW
        and selected_review_lane == "loss_review_and_next_profit_candidate_gate"
    ):
        return _CatalogRoute(
            classification=(
                OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_READY_FOR_OWNER_REVIEW
            ),
            selected_packet_preview=(
                "AIOS-FOREX-OANDA-LIVE-MICROTRADE-LOSS-TO-NEXT-PROFIT-CANDIDATE-GATE-V1"
            ),
            selected_packet_title="Loss Review And Next Profit Candidate Gate Preview",
            selected_packet_purpose="Route loss result to loss review and candidate repair.",
            selected_packet_non_execution_notice=(
                "This preview does not authorize revenge trading or immediate retry."
            ),
            selected_packet_allowed_next_human_action=(
                "Anthony may approve a future loss-review packet prompt only."
            ),
            next_safe_action=EXACT_NEXT_OWNER_ACTION,
        )
    if (
        source_status
        == OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_REQUIRE_MORE_EVIDENCE
        and selected_review_lane == "more_evidence_required"
    ):
        return _CatalogRoute(
            classification=(
                OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_REQUIRE_MORE_EVIDENCE
            ),
            selected_packet_preview=(
                "AIOS-FOREX-OANDA-LIVE-MICROTRADE-BREAKEVEN-MORE-EVIDENCE-V1"
            ),
            selected_packet_title="Breakeven More Evidence Preview",
            selected_packet_purpose="Require more sanitized evidence before proof promotion.",
            selected_packet_non_execution_notice=(
                "This preview does not authorize another live trade."
            ),
            selected_packet_allowed_next_human_action=(
                "Anthony may approve a future more-evidence collection packet only."
            ),
            next_safe_action=EXACT_NEXT_OWNER_ACTION,
        )
    if (
        source_status
        == OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_BLOCKED_NO_OWNER_RESULT
        and selected_review_lane == "owner_result_evidence_required"
    ):
        return _CatalogRoute(
            classification=(
                OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_BLOCKED_NO_OWNER_RESULT
            ),
            selected_packet_preview=(
                "AIOS-FOREX-OANDA-LIVE-MICROTRADE-OWNER-RESULT-EVIDENCE-REQUIRED-V1"
            ),
            selected_packet_title="Owner Result Evidence Required Preview",
            selected_packet_purpose=(
                "Require sanitized owner result evidence before proof review."
            ),
            selected_packet_non_execution_notice=(
                "This preview does not authorize broker access or result scraping."
            ),
            selected_packet_allowed_next_human_action=(
                "Anthony may provide sanitized owner result evidence."
            ),
            next_safe_action=(
                "Provide sanitized owner result evidence; do not request execution."
            ),
        )
    return _CatalogRoute(
        classification=(
            OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_BLOCKED_UNSAFE
        ),
        selected_packet_preview=(
            "AIOS-FOREX-OANDA-LIVE-MICROTRADE-UNSAFE-RESULT-REPAIR-V1"
        ),
        selected_packet_title="Unsafe Result Repair Preview",
        selected_packet_purpose="Repair unsafe result material before any proof review.",
        selected_packet_non_execution_notice=(
            "This preview blocks proof promotion and all execution."
        ),
        selected_packet_allowed_next_human_action=(
            "Anthony may approve an unsafe-result repair packet only."
        ),
        next_safe_action=(
            "Repair unsafe result material before any selected proof packet review."
        ),
    )


def _coerce_input(
    value: (
        OandaLiveMicrotradeSelectedProofPacketPreviewCatalogInput
        | Mapping[str, Any]
    ),
) -> OandaLiveMicrotradeSelectedProofPacketPreviewCatalogInput:
    if isinstance(value, OandaLiveMicrotradeSelectedProofPacketPreviewCatalogInput):
        return value
    raw = dict(value)
    return OandaLiveMicrotradeSelectedProofPacketPreviewCatalogInput(
        decision_gate_input=raw.get("decision_gate_input", raw),
        owner_preview_label=_text(raw.get("owner_preview_label"), "pending_owner_review"),
        owner_notes_sanitized=_text(raw.get("owner_notes_sanitized")),
    )


def _source_decision_result(value: Any) -> Any:
    if _looks_like_decision_result(value):
        return value
    return evaluate_oanda_live_microtrade_routed_proof_owner_decision_gate(value)


def _looks_like_decision_result(value: Any) -> bool:
    if isinstance(value, Mapping):
        return (
            "classification" in value
            and "selected_review_lane" in value
            and "selected_packet_preview" in value
        )
    return (
        hasattr(value, "classification")
        and hasattr(value, "selected_review_lane")
        and hasattr(value, "selected_packet_preview")
    )


def _field(value: Any, name: str, default: Any = "") -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _safe_owner_preview_label(value: Any) -> str:
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
