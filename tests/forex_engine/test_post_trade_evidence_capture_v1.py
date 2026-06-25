from __future__ import annotations

import json
from dataclasses import replace
from decimal import Decimal

from automation.forex_engine.post_trade_evidence_capture_v1 import (
    POST_TRADE_EVIDENCE_BLOCKED_MISSING_RESULT,
    POST_TRADE_EVIDENCE_BLOCKED_NOT_RECONCILED,
    POST_TRADE_EVIDENCE_BLOCKED_UNSANITIZED,
    POST_TRADE_EVIDENCE_CAPTURED_BREAKEVEN,
    POST_TRADE_EVIDENCE_CAPTURED_LOSS,
    POST_TRADE_EVIDENCE_CAPTURED_PROFIT,
    build_sample_post_trade_loss_input,
    build_sample_post_trade_missing_input,
    build_sample_post_trade_profit_input,
    capture_post_trade_evidence,
    post_trade_evidence_to_jsonable_dict,
)


def test_profit_evidence_captured() -> None:
    result = capture_post_trade_evidence(build_sample_post_trade_profit_input())
    assert result.classification == POST_TRADE_EVIDENCE_CAPTURED_PROFIT


def test_loss_evidence_captured() -> None:
    result = capture_post_trade_evidence(build_sample_post_trade_loss_input())
    assert result.classification == POST_TRADE_EVIDENCE_CAPTURED_LOSS


def test_breakeven_evidence_captured() -> None:
    sample = replace(build_sample_post_trade_profit_input(), realized_pl=Decimal("0.00"), result="BREAKEVEN")
    result = capture_post_trade_evidence(sample)
    assert result.classification == POST_TRADE_EVIDENCE_CAPTURED_BREAKEVEN


def test_missing_result_blocks() -> None:
    result = capture_post_trade_evidence(build_sample_post_trade_missing_input())
    assert result.classification == POST_TRADE_EVIDENCE_BLOCKED_MISSING_RESULT


def test_unreconciled_evidence_blocks() -> None:
    sample = replace(build_sample_post_trade_profit_input(), broker_reconciled=False)
    result = capture_post_trade_evidence(sample)
    assert result.classification == POST_TRADE_EVIDENCE_BLOCKED_NOT_RECONCILED


def test_unsanitized_evidence_blocks() -> None:
    sample = replace(build_sample_post_trade_profit_input(), sanitized=False)
    result = capture_post_trade_evidence(sample)
    assert result.classification == POST_TRADE_EVIDENCE_BLOCKED_UNSANITIZED


def test_post_trade_output_includes_planned_vs_actual() -> None:
    data = post_trade_evidence_to_jsonable_dict(capture_post_trade_evidence())
    assert "planned_vs_actual" in data
    assert "entry" in data["planned_vs_actual"]


def test_post_trade_output_includes_realized_pl() -> None:
    data = post_trade_evidence_to_jsonable_dict(capture_post_trade_evidence())
    assert data["realized_pl"] == "185.40"
    json.dumps(data)


def test_no_account_id_leakage() -> None:
    data = json.dumps(post_trade_evidence_to_jsonable_dict(capture_post_trade_evidence()))
    assert "REAL-ACCOUNT" not in data
    assert "account_id" not in data.lower()
