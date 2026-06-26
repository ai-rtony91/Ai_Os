from __future__ import annotations

import json

import pytest

from automation.forex_engine import oanda_supervised_live_microtrade_post_trade_capture_plan_v1 as capture
from automation.forex_engine.oanda_supervised_live_microtrade_final_gate_v1 import (
    PROTECTED_FLAG_NAMES,
)


def _result(builder=capture.build_sample_ready_input):
    return capture.build_oanda_supervised_live_microtrade_post_trade_capture_plan(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (
            capture.build_sample_ready_input,
            capture.OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_READY_FOR_OWNER_REVIEW,
        ),
        (
            capture.build_sample_missing_input,
            capture.OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_REQUIRE_REPAIR,
        ),
        (
            capture.build_sample_unsafe_input,
            capture.OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_BLOCKED_UNSAFE,
        ),
    ),
)
def test_post_trade_capture_sample_classifications(builder, classification: str):
    assert _result(builder).classification == classification


def test_post_trade_capture_version_constant():
    assert capture.VERSION == "oanda_supervised_live_microtrade_post_trade_capture_plan_v1"


@pytest.mark.parametrize("item", capture.REQUIRED_CAPTURE_ITEMS)
def test_post_trade_capture_ready_has_required_item(item: str):
    assert _result().capture_items[item] is True


@pytest.mark.parametrize("item", capture.REQUIRED_CAPTURE_ITEMS)
def test_post_trade_capture_missing_item_requires_repair(item: str):
    sample = capture.build_sample_ready_input()
    capture_items = dict(sample.capture_items)
    capture_items[item] = False
    result = capture.build_oanda_supervised_live_microtrade_post_trade_capture_plan(
        {"capture_items": capture_items}
    )
    if item == "no_broker_call_from_codex":
        assert result.classification == capture.OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_REQUIRE_REPAIR
    else:
        assert result.classification == capture.OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_REQUIRE_REPAIR
    assert item in result.missing_items


def test_post_trade_capture_unsafe_blocks_codex_broker_boundary():
    result = _result(capture.build_sample_unsafe_input)
    assert "codex_broker_call_boundary_not_false" in result.blocked_items


@pytest.mark.parametrize(
    "expected_item",
    (
        "filled_trade_evidence_checklist",
        "realized_pl_capture_checklist",
        "spread_slippage_capture_checklist",
        "reconciliation_checklist",
        "screenshot_evidence_checklist",
        "journal_checklist",
        "route_live_result_back_to_evidence_ledger",
        "no_broker_call_from_codex",
    ),
)
def test_post_trade_capture_named_required_coverage(expected_item: str):
    assert expected_item in capture.REQUIRED_CAPTURE_ITEMS


@pytest.mark.parametrize("flag_name", PROTECTED_FLAG_NAMES)
def test_post_trade_capture_all_protected_flags_false(flag_name: str):
    result = _result()
    assert getattr(result, flag_name) is False
    assert result.protected_flags[flag_name] is False


def test_post_trade_capture_json_serializable():
    json.dumps(capture.to_jsonable_dict(_result()))


def test_post_trade_capture_markdown_output():
    assert capture.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Supervised Live Microtrade Post-Trade Capture Plan V1"
    )


def test_post_trade_capture_operator_text_output():
    assert "Post-trade capture status" in capture.to_operator_text(_result())


def test_post_trade_capture_preview_read_only():
    assert _result().post_trade_capture_preview["read_only_after_owner_action"] is True
    assert _result().post_trade_capture_preview["broker_action_allowed"] is False


@pytest.mark.parametrize(
    "phrase",
    (
        "No trade placed by this packet.",
        "No broker call was made by this packet.",
        "No live approval was granted.",
        "No real money approval was granted.",
        "No compounding approval was granted.",
        "No bank movement approval was granted.",
        "No autonomous execution was granted.",
        "Unattended vacation mode remains blocked.",
        "Profit is not guaranteed.",
        "All protected flags remain false.",
    ),
)
def test_post_trade_capture_markdown_safety_phrases(phrase: str):
    assert phrase in capture.to_markdown(_result())

