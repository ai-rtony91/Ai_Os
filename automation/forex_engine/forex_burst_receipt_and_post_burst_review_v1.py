"""Validate receipt and post-burst review metadata after external burst execution."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from automation.forex_engine.forex_multi_pair_universe_v1 import (
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_SENSITIVE_DATA,
    _bool,
    _governed_requested,
    _int,
    _mapping,
    banking_focus_blockers,
    build_common_result,
    sensitive_data_blockers,
)

SCHEMA = "AIOS_FOREX_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1"
MODE = "READ_ONLY_METADATA_ONLY_BURST_RECEIPT_AND_POST_BURST_REVIEW"

BURST_RECEIPT_AND_POST_BURST_REVIEW_READY = "BURST_RECEIPT_AND_POST_BURST_REVIEW_READY"
WAITING_FOR_BURST_RECEIPTS = "WAITING_FOR_BURST_RECEIPTS"
BLOCKED_BY_RECEIPT_MISSING = "BLOCKED_BY_RECEIPT_MISSING"
BLOCKED_BY_RECEIPT_UNSANITIZED = "BLOCKED_BY_RECEIPT_UNSANITIZED"
BLOCKED_BY_ORDER_COUNT_MISMATCH = "BLOCKED_BY_ORDER_COUNT_MISMATCH"
BLOCKED_BY_POST_BURST_REVIEW = "BLOCKED_BY_POST_BURST_REVIEW"
BLOCKED_BY_PNL_RECORD = "BLOCKED_BY_PNL_RECORD"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_BEST_PACKET = "AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1"
ALLOWED_RECEIPT_MODES = frozenset({"DEMO", "OANDA_DEMO", "PRACTICE", "OANDA_LIVE", "LIVE"})


def evaluate_forex_burst_receipt_and_post_burst_review_v1(
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate sanitized burst receipts without executing or contacting brokers."""

    source = _mapping(payload)
    sensitive_blockers = sensitive_data_blockers(source)
    if sensitive_blockers:
        return _receipt_result(source, BLOCKED_BY_SENSITIVE_DATA, sensitive_blockers)
    banking_blockers = banking_focus_blockers(source)
    if banking_blockers:
        return _receipt_result(source, BLOCKED_BY_BANKING_FOCUS, banking_blockers)

    intent = _mapping(source.get("burst_intent"))
    receipts = _mapping(source.get("burst_receipts"))
    review = _mapping(source.get("post_burst_review"))
    if not intent:
        return _receipt_result(source, INCOMPLETE_INPUTS, ("burst_intent_missing",))
    if not receipts:
        return _receipt_result(source, BLOCKED_BY_RECEIPT_MISSING, ("burst_receipts_missing",))

    order_count = _int(intent.get("order_count"))
    pairs = list(intent.get("pairs", [])) if isinstance(intent.get("pairs"), Sequence) and not isinstance(intent.get("pairs"), (str, bytes, bytearray)) else []
    if order_count < 1 or not pairs or not _bool(intent.get("receipt_required")) or not _bool(intent.get("post_burst_review_required")):
        return _receipt_result(source, INCOMPLETE_INPUTS, ("burst_intent_incomplete",))

    if not _bool(receipts.get("receipts_present")):
        return _receipt_result(
            source,
            WAITING_FOR_BURST_RECEIPTS,
            ("burst_receipts_not_present_yet",),
            burst_journal_entry=_journal(order_count=order_count, pairs=pairs, ready=False),
            next_packet=NEXT_BEST_PACKET,
        )

    receipt_list = receipts.get("receipts")
    if not isinstance(receipt_list, Sequence) or isinstance(receipt_list, (str, bytes, bytearray)):
        return _receipt_result(source, BLOCKED_BY_RECEIPT_MISSING, ("receipts_list_missing",))
    if len(receipt_list) != order_count:
        return _receipt_result(source, BLOCKED_BY_ORDER_COUNT_MISMATCH, ("receipt_count_does_not_match_intent",))

    receipt_gates = {
        "all_receipts_sanitized": _bool(receipts.get("all_receipts_sanitized")),
        "no_account_ids": _bool(receipts.get("no_account_ids")),
        "no_credentials": _bool(receipts.get("no_credentials")),
        "all_order_ids_redacted": _bool(receipts.get("all_order_ids_redacted")),
        "broker_name_oanda": str(receipts.get("broker_name", "")).upper() == "OANDA",
        "mode_allowed": str(receipts.get("mode", "")).upper() in ALLOWED_RECEIPT_MODES,
        "live_trade_executed_by_this_module_false": receipts.get("live_trade_executed_by_this_module") is False,
        "broker_api_called_by_this_module_false": receipts.get("broker_api_called_by_this_module") is False,
        "money_moved_false": receipts.get("money_moved") is False,
    }
    receipt_blockers = tuple(key for key, value in receipt_gates.items() if not value)
    if receipt_blockers:
        return _receipt_result(source, BLOCKED_BY_RECEIPT_UNSANITIZED, receipt_blockers)

    if not review:
        return _receipt_result(source, BLOCKED_BY_POST_BURST_REVIEW, ("post_burst_review_missing",))
    review_gates = {
        "post_burst_review_required": _bool(review.get("post_burst_review_required")),
        "post_burst_review_completed": _bool(review.get("post_burst_review_completed")),
        "burst_pnl_recorded": _bool(review.get("burst_pnl_recorded")),
        "spread_slippage_recorded": _bool(review.get("spread_slippage_recorded")),
        "risk_review_recorded": _bool(review.get("risk_review_recorded")),
        "owner_review_required": _bool(review.get("owner_review_required")),
        "next_burst_blocked_until_review": _bool(review.get("next_burst_blocked_until_review")),
    }
    if not review_gates["burst_pnl_recorded"]:
        return _receipt_result(source, BLOCKED_BY_PNL_RECORD, ("burst_pnl_recorded_false",))
    review_blockers = tuple(key for key, value in review_gates.items() if not value)
    if review_blockers:
        return _receipt_result(source, BLOCKED_BY_POST_BURST_REVIEW, review_blockers)

    journal = _journal(order_count=order_count, pairs=pairs, ready=True)
    return build_common_result(
        schema=SCHEMA,
        mode=MODE,
        status=BURST_RECEIPT_AND_POST_BURST_REVIEW_READY,
        ready=True,
        governed_burst_requested=_governed_requested(source),
        multi_pair_enabled=True,
        blockers=(),
        next_best_packet="AIOS_FOREX_PROFIT_REPEATABILITY_EVIDENCE_V1",
        safe_manual_next_action="Route burst journal entry into repeatability evidence update.",
        extra={"burst_journal_entry": journal},
    )


def _receipt_result(
    source: Mapping[str, Any],
    status: str,
    blockers: Sequence[str],
    *,
    burst_journal_entry: Mapping[str, Any] | None = None,
    next_packet: str = NEXT_BEST_PACKET,
) -> dict[str, Any]:
    return build_common_result(
        schema=SCHEMA,
        mode=MODE,
        status=status,
        ready=False,
        governed_burst_requested=_governed_requested(source),
        multi_pair_enabled=False,
        blockers=blockers,
        next_best_packet=next_packet,
        safe_manual_next_action=_safe_manual_next_action(status),
        extra={"burst_journal_entry": dict(burst_journal_entry or {})},
    )


def _journal(*, order_count: int, pairs: Sequence[Any], ready: bool) -> dict[str, Any]:
    return {
        "burst_reviewed": bool(ready),
        "order_count": order_count,
        "pairs": [str(pair) for pair in pairs],
        "burst_pnl_recorded": bool(ready),
        "ready_for_repeatability_update": bool(ready),
        "no_next_burst_without_review": True,
    }


def _safe_manual_next_action(status: str) -> str:
    if status == WAITING_FOR_BURST_RECEIPTS:
        return "Wait for sanitized burst receipts from the separate runtime packet."
    if status == BLOCKED_BY_RECEIPT_MISSING:
        return "Provide burst receipt metadata."
    if status == BLOCKED_BY_RECEIPT_UNSANITIZED:
        return "Provide redacted and sanitized receipt metadata only."
    if status == BLOCKED_BY_ORDER_COUNT_MISMATCH:
        return "Match receipt count to the governed burst intent order count."
    if status == BLOCKED_BY_POST_BURST_REVIEW:
        return "Complete post-burst review before any next burst."
    if status == BLOCKED_BY_PNL_RECORD:
        return "Record burst PnL before repeatability update."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys or values."
    if status == BLOCKED_BY_BANKING_FOCUS:
        return "Remove banking, withdrawal, transfer, or money-movement focus fields."
    return "Provide complete burst intent and receipt-review metadata."
