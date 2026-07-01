from automation.forex_engine.forex_burst_receipt_and_post_burst_review_v1 import (
    BLOCKED_BY_ORDER_COUNT_MISMATCH,
    BLOCKED_BY_POST_BURST_REVIEW,
    BLOCKED_BY_RECEIPT_UNSANITIZED,
    BURST_RECEIPT_AND_POST_BURST_REVIEW_READY,
    WAITING_FOR_BURST_RECEIPTS,
    evaluate_forex_burst_receipt_and_post_burst_review_v1,
)


def _intent():
    return {
        "order_count": 2,
        "pairs": ["EUR_USD", "GBP_USD"],
        "receipt_required": True,
        "post_burst_review_required": True,
    }


def _receipts(**overrides):
    receipts = {
        "receipts_present": True,
        "receipts": [{"pair": "EUR_USD"}, {"pair": "GBP_USD"}],
        "all_receipts_sanitized": True,
        "no_account_ids": True,
        "no_credentials": True,
        "all_order_ids_redacted": True,
        "broker_name": "OANDA",
        "mode": "OANDA_DEMO",
        "live_trade_executed_by_this_module": False,
        "broker_api_called_by_this_module": False,
        "money_moved": False,
    }
    receipts.update(overrides)
    return receipts


def _review(**overrides):
    review = {
        "post_burst_review_required": True,
        "post_burst_review_completed": True,
        "burst_pnl_recorded": True,
        "spread_slippage_recorded": True,
        "risk_review_recorded": True,
        "owner_review_required": True,
        "next_burst_blocked_until_review": True,
    }
    review.update(overrides)
    return review


def _payload(receipts=None, review=None):
    return {
        "governed_burst_requested": True,
        "burst_intent": _intent(),
        "burst_receipts": receipts if receipts is not None else _receipts(),
        "post_burst_review": review if review is not None else _review(),
    }


def test_missing_receipts_waits():
    result = evaluate_forex_burst_receipt_and_post_burst_review_v1(
        _payload(receipts=_receipts(receipts_present=False, receipts=[]))
    )
    assert result["status"] == WAITING_FOR_BURST_RECEIPTS


def test_unsanitized_receipts_block():
    result = evaluate_forex_burst_receipt_and_post_burst_review_v1(
        _payload(receipts=_receipts(all_receipts_sanitized=False))
    )
    assert result["status"] == BLOCKED_BY_RECEIPT_UNSANITIZED


def test_order_count_mismatch_blocks():
    result = evaluate_forex_burst_receipt_and_post_burst_review_v1(
        _payload(receipts=_receipts(receipts=[{"pair": "EUR_USD"}]))
    )
    assert result["status"] == BLOCKED_BY_ORDER_COUNT_MISMATCH


def test_missing_post_burst_review_blocks():
    result = evaluate_forex_burst_receipt_and_post_burst_review_v1(
        _payload(review={})
    )
    assert result["status"] == BLOCKED_BY_POST_BURST_REVIEW


def test_valid_burst_receipt_review_ready():
    result = evaluate_forex_burst_receipt_and_post_burst_review_v1(_payload())
    assert result["status"] == BURST_RECEIPT_AND_POST_BURST_REVIEW_READY
    assert result["burst_journal_entry"]["ready_for_repeatability_update"] is True
