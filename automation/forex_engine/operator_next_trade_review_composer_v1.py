"""Operator-facing next-trade review composer for AI_OS Forex evidence.

This module is local-only. It composes existing local evidence gates into one
plain review/not-review answer for Anthony without authorizing broker action.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from automation.forex_engine.demo_loss_review_metrics_gate_v1 import (
    BLOCK_NEXT_DEMO_ORDER_MISSING_METRICS,
    REVIEW_READY_FOR_OWNER_APPROVAL as LOSS_REVIEW_READY,
    evaluate_demo_loss_review_metrics_gate,
)
from automation.forex_engine.trade_latency_baseline_reporter_v1 import (
    LATENCY_READY_FOR_REVIEW,
    evaluate_trade_latency_baseline,
)


PACKET_ID = "AIOS-FOREX-OPERATOR-NEXT-TRADE-REVIEW-COMPOSER-LOCAL-APPLY-V1"
MODE = "LOCAL_ONLY_OPERATOR_NEXT_TRADE_REVIEW_COMPOSER"

REVIEW_READY_FOR_OWNER_APPROVAL = "REVIEW_READY_FOR_OWNER_APPROVAL"
BLOCK_REVIEW_MISSING_PROOF = "BLOCK_REVIEW_MISSING_PROOF"
BLOCK_REVIEW_WEAK_TRADE_EVIDENCE = "BLOCK_REVIEW_WEAK_TRADE_EVIDENCE"
BLOCK_REVIEW_LATENCY_UNKNOWN = "BLOCK_REVIEW_LATENCY_UNKNOWN"
BLOCK_REVIEW_RISK_OR_SAFETY_NOT_CLEAR = "BLOCK_REVIEW_RISK_OR_SAFETY_NOT_CLEAR"
BLOCK_REVIEW_INVALID_EVIDENCE = "BLOCK_REVIEW_INVALID_EVIDENCE"

REQUIRED_SECTIONS: tuple[str, ...] = (
    "loss_review_metrics_gate",
    "trade_latency_baseline",
    "operator_context",
)

OPERATOR_CONTEXT_FIELDS: tuple[str, ...] = (
    "operator_name",
    "instrument",
    "direction",
    "strategy_name",
    "candidate_id",
    "last_trade_id",
    "last_trade_result",
    "wants_next_demo_review",
)

UNSAFE_SAFETY_KEYS: tuple[str, ...] = (
    "broker_calls_allowed",
    "credential_access_allowed",
    "order_placement_allowed",
    "order_close_allowed",
    "live_endpoint_allowed",
    "repo_mutation_outside_allowed_files",
)


def compose_operator_next_trade_review(evidence: dict | None = None) -> dict:
    """Compose nested evidence into one local operator review decision."""

    try:
        if not isinstance(evidence, Mapping):
            return _blocked_result(
                decision=BLOCK_REVIEW_INVALID_EVIDENCE,
                operator_answer=(
                    "Blocked: AIOS does not have enough proof for you to review this trade."
                ),
                blocks=["evidence must be a mapping"],
                missing_for_review=list(REQUIRED_SECTIONS),
                review_summary="Review blocked because composer evidence is missing or malformed.",
                loss_gate_result={},
                latency_result={},
            )

        missing_sections = [
            section
            for section in REQUIRED_SECTIONS
            if section not in evidence or _is_empty(evidence[section])
        ]
        if missing_sections:
            return _blocked_result(
                decision=BLOCK_REVIEW_MISSING_PROOF,
                operator_answer=(
                    "Blocked: AIOS does not have enough proof for you to review this trade."
                ),
                blocks=["required review evidence sections are missing"],
                missing_for_review=missing_sections,
                review_summary="Review blocked because required evidence sections are absent.",
                loss_gate_result={},
                latency_result={},
            )

        operator_context = evidence.get("operator_context")
        missing_context = _missing_context_fields(operator_context)
        if missing_context:
            return _blocked_result(
                decision=BLOCK_REVIEW_INVALID_EVIDENCE,
                operator_answer=(
                    "Blocked: AIOS does not have enough proof for you to review this trade."
                ),
                blocks=["operator context is incomplete"],
                missing_for_review=missing_context,
                review_summary="Review blocked because operator context is incomplete.",
                loss_gate_result={},
                latency_result={},
            )

        if not _wants_review(operator_context["wants_next_demo_review"]):
            return _blocked_result(
                decision=BLOCK_REVIEW_MISSING_PROOF,
                operator_answer="Blocked: no next demo review was requested.",
                blocks=["operator_context.wants_next_demo_review is false"],
                missing_for_review=[],
                review_summary="Review blocked because Anthony did not request next-demo review.",
                loss_gate_result={},
                latency_result={},
            )

        loss_gate_result = _coerce_loss_gate_result(evidence["loss_review_metrics_gate"])
        latency_result = _coerce_latency_result(evidence["trade_latency_baseline"])

        unsafe_blocks = _unsafe_nested_safety_blocks(loss_gate_result, latency_result)
        if unsafe_blocks:
            return _blocked_result(
                decision=BLOCK_REVIEW_RISK_OR_SAFETY_NOT_CLEAR,
                operator_answer=(
                    "Blocked: risk or safety is not clear enough for you to review this trade."
                ),
                blocks=unsafe_blocks,
                missing_for_review=unsafe_blocks,
                review_summary="Review blocked because nested safety evidence is not conservative.",
                loss_gate_result=loss_gate_result,
                latency_result=latency_result,
            )

        if not _is_allowed(loss_gate_result):
            decision = (
                BLOCK_REVIEW_MISSING_PROOF
                if _loss_missing_proof_is_dominant(loss_gate_result)
                else BLOCK_REVIEW_WEAK_TRADE_EVIDENCE
            )
            return _blocked_result(
                decision=decision,
                operator_answer=(
                    "Blocked: AIOS does not have enough proof for you to review this trade."
                ),
                blocks=_result_blocks(loss_gate_result, "loss-review gate did not pass"),
                missing_for_review=_missing_from_loss_result(loss_gate_result),
                review_summary="Review blocked because trade evidence is not review-ready.",
                loss_gate_result=loss_gate_result,
                latency_result=latency_result,
            )

        if not _is_allowed(latency_result):
            return _blocked_result(
                decision=BLOCK_REVIEW_LATENCY_UNKNOWN,
                operator_answer=(
                    "Blocked: timing is not clear enough for you to review this trade."
                ),
                blocks=_result_blocks(latency_result, "latency baseline did not pass"),
                missing_for_review=_missing_from_latency_result(latency_result),
                review_summary="Review blocked because timing evidence is not review-ready.",
                loss_gate_result=loss_gate_result,
                latency_result=latency_result,
            )

        return _ready_result(
            loss_gate_result=loss_gate_result,
            latency_result=latency_result,
            review_summary=(
                "Evidence is complete enough for Anthony to review. Broker action "
                "remains blocked until a separate explicit owner approval exists."
            ),
        )
    except Exception as exc:  # pragma: no cover - defensive final boundary
        return _blocked_result(
            decision=BLOCK_REVIEW_INVALID_EVIDENCE,
            operator_answer=(
                "Blocked: AIOS does not have enough proof for you to review this trade."
            ),
            blocks=[f"malformed composer evidence blocked safely: {exc}"],
            missing_for_review=["unhandled_validation_error"],
            review_summary="Review blocked because evidence could not be composed safely.",
            loss_gate_result={},
            latency_result={},
        )


def _coerce_loss_gate_result(value: Any) -> dict:
    if _looks_like_precomputed_result(value):
        return dict(value)
    return evaluate_demo_loss_review_metrics_gate(value if isinstance(value, dict) else None)


def _coerce_latency_result(value: Any) -> dict:
    if _looks_like_precomputed_result(value):
        return dict(value)
    return evaluate_trade_latency_baseline(value if isinstance(value, dict) else None)


def _looks_like_precomputed_result(value: Any) -> bool:
    return isinstance(value, Mapping) and "allowed" in value and "decision" in value


def _missing_context_fields(operator_context: Any) -> list[str]:
    if not isinstance(operator_context, Mapping):
        return list(OPERATOR_CONTEXT_FIELDS)
    return [
        field
        for field in OPERATOR_CONTEXT_FIELDS
        if field not in operator_context or _is_empty(operator_context[field])
    ]


def _is_empty(value: Any) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _wants_review(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "y", "1"}
    if isinstance(value, int):
        return value == 1
    return False


def _is_allowed(result: Mapping[str, Any]) -> bool:
    return bool(result.get("allowed") is True)


def _loss_missing_proof_is_dominant(loss_gate_result: Mapping[str, Any]) -> bool:
    decision = str(loss_gate_result.get("decision", ""))
    missing_metrics = loss_gate_result.get("missing_metrics")
    return decision == BLOCK_NEXT_DEMO_ORDER_MISSING_METRICS or bool(missing_metrics)


def _unsafe_nested_safety_blocks(
    loss_gate_result: Mapping[str, Any], latency_result: Mapping[str, Any]
) -> list[str]:
    blocks: list[str] = []
    for label, result in (
        ("loss_review_metrics_gate", loss_gate_result),
        ("trade_latency_baseline", latency_result),
    ):
        safety = result.get("safety")
        if not isinstance(safety, Mapping):
            blocks.append(f"{label}.safety is missing")
            continue
        for key in UNSAFE_SAFETY_KEYS:
            if safety.get(key) is True:
                blocks.append(f"{label}.{key} is true")
        local_only = safety.get("local_only")
        if local_only is False:
            blocks.append(f"{label}.local_only is false")
        if safety.get("uses_network") is True or safety.get("network_used") is True:
            blocks.append(f"{label}.network use is true")
    return blocks


def _result_blocks(result: Mapping[str, Any], fallback: str) -> list[str]:
    blocked_reasons = result.get("blocked_reasons")
    if isinstance(blocked_reasons, list) and blocked_reasons:
        return [str(reason) for reason in blocked_reasons]
    decision = result.get("decision")
    if decision:
        return [str(decision)]
    return [fallback]


def _missing_from_loss_result(loss_gate_result: Mapping[str, Any]) -> list[str]:
    missing = loss_gate_result.get("missing_metrics")
    if isinstance(missing, Mapping):
        flattened: list[str] = []
        for section, fields in missing.items():
            if isinstance(fields, list):
                flattened.extend(f"{section}.{field}" for field in fields)
            else:
                flattened.append(str(section))
        return flattened
    if missing:
        return [str(missing)]
    return _result_blocks(loss_gate_result, "loss-review evidence")


def _missing_from_latency_result(latency_result: Mapping[str, Any]) -> list[str]:
    missing = latency_result.get("missing_timestamps")
    if isinstance(missing, list) and missing:
        return [str(field) for field in missing]
    invalid = latency_result.get("invalid_timestamps")
    if isinstance(invalid, list) and invalid:
        return [str(field) for field in invalid]
    slow = latency_result.get("slow_segments")
    if isinstance(slow, list) and slow:
        return [str(segment.get("segment", segment)) for segment in slow]
    return _result_blocks(latency_result, "latency evidence")


def _operator_benefit() -> str:
    return (
        "Anthony/operator benefit: one plain review/not-review answer; less "
        "guessing; fewer reports to read; protects attention and capital; keeps "
        "broker action blocked until separately approved."
    )


def _safety() -> dict[str, bool]:
    return {
        "local_only": True,
        "broker_calls_allowed": False,
        "credential_access_allowed": False,
        "order_placement_allowed": False,
        "order_close_allowed": False,
        "live_endpoint_allowed": False,
        "owner_approval_required": True,
        "uses_network": False,
    }


def _blocked_result(
    *,
    decision: str,
    operator_answer: str,
    blocks: list[str],
    missing_for_review: list[str],
    review_summary: str,
    loss_gate_result: Mapping[str, Any],
    latency_result: Mapping[str, Any],
) -> dict:
    return _result(
        allowed=False,
        decision=decision,
        operator_answer=operator_answer,
        blocks=blocks,
        missing_for_review=missing_for_review,
        review_summary=review_summary,
        loss_gate_result=loss_gate_result,
        latency_result=latency_result,
    )


def _ready_result(
    *, loss_gate_result: Mapping[str, Any], latency_result: Mapping[str, Any], review_summary: str
) -> dict:
    return _result(
        allowed=True,
        decision=REVIEW_READY_FOR_OWNER_APPROVAL,
        operator_answer=(
            "Review-ready: evidence is complete enough for Anthony to review, "
            "but no broker action is authorized."
        ),
        blocks=[],
        missing_for_review=[],
        review_summary=review_summary,
        loss_gate_result=loss_gate_result,
        latency_result=latency_result,
    )


def _result(
    *,
    allowed: bool,
    decision: str,
    operator_answer: str,
    blocks: list[str],
    missing_for_review: list[str],
    review_summary: str,
    loss_gate_result: Mapping[str, Any],
    latency_result: Mapping[str, Any],
) -> dict:
    loss_decision = loss_gate_result.get("decision")
    latency_decision = latency_result.get("decision")
    risk_or_safety_clear = decision != BLOCK_REVIEW_RISK_OR_SAFETY_NOT_CLEAR
    timing_clear = bool(
        latency_result.get("allowed") is True
        and latency_decision == LATENCY_READY_FOR_REVIEW
    )
    trade_evidence_clear = bool(
        loss_gate_result.get("allowed") is True
        and loss_decision == LOSS_REVIEW_READY
    )

    return {
        "packet_id": PACKET_ID,
        "mode": MODE,
        "allowed": allowed,
        "decision": decision,
        "operator_answer": operator_answer,
        "operator_benefit": _operator_benefit(),
        "next_safe_action": _next_safe_action(decision),
        "blocks": blocks,
        "missing_for_review": missing_for_review,
        "review_summary": review_summary,
        "loss_gate_decision": loss_decision,
        "latency_decision": latency_decision,
        "risk_or_safety_clear": risk_or_safety_clear,
        "timing_clear": timing_clear,
        "trade_evidence_clear": trade_evidence_clear,
        "owner_approval_still_required": True,
        "broker_action_allowed": False,
        "safety": _safety(),
    }


def _next_safe_action(decision: str) -> str:
    if decision == REVIEW_READY_FOR_OWNER_APPROVAL:
        return "Anthony may review the evidence bundle; broker action still requires separate explicit approval."
    if decision == BLOCK_REVIEW_LATENCY_UNKNOWN:
        return "Capture or repair timing evidence before asking Anthony to review the next trade."
    if decision == BLOCK_REVIEW_WEAK_TRADE_EVIDENCE:
        return "Repair trade evidence, signal, lineage, or risk geometry before next-trade review."
    if decision == BLOCK_REVIEW_RISK_OR_SAFETY_NOT_CLEAR:
        return "Stop until nested safety evidence is conservative and broker action remains blocked."
    if decision == BLOCK_REVIEW_MISSING_PROOF:
        return "Collect the missing proof before asking Anthony to review the next trade."
    return "Fix malformed composer evidence before next-trade review."
