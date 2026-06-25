from __future__ import annotations

import json
from dataclasses import replace
from decimal import Decimal
from types import SimpleNamespace

import pytest

from automation.forex_engine import demo_trade_readiness_bridge_v1 as bridge_mod
from automation.forex_engine.demo_position_sizer_v1 import build_sample_blocked_position_size_input
from automation.forex_engine.demo_trade_candidate_context_v1 import build_sample_blocked_candidate_context_input
from automation.forex_engine.demo_trade_readiness_bridge_v1 import (
    DEMO_TRADE_READINESS_BRIDGE_BLOCKED_ACCOUNT,
    DEMO_TRADE_READINESS_BRIDGE_BLOCKED_CANDIDATE,
    DEMO_TRADE_READINESS_BRIDGE_BLOCKED_OPERATOR_TICKET,
    DEMO_TRADE_READINESS_BRIDGE_BLOCKED_ORDER_PLAN,
    DEMO_TRADE_READINESS_BRIDGE_BLOCKED_POSITION_SIZE,
    DEMO_TRADE_READINESS_BRIDGE_BLOCKED_RISK,
    DEMO_TRADE_READINESS_BRIDGE_BLOCKED_SNAPSHOT,
    DEMO_TRADE_READINESS_BRIDGE_READY_FOR_OWNER_REVIEW,
    DemoTradeReadinessBridgeConfig,
    build_sample_demo_trade_readiness_bridge_blocked_input,
    build_sample_demo_trade_readiness_bridge_ready_input,
    demo_trade_readiness_bridge_to_jsonable_dict,
    demo_trade_readiness_bridge_to_markdown,
    demo_trade_readiness_bridge_to_operator_text,
    run_demo_trade_readiness_bridge,
)
from automation.forex_engine.demo_trade_risk_gate_v1 import build_sample_blocked_risk_input


PERMISSION_FLAGS = (
    "demo_execution_allowed",
    "broker_action_allowed",
    "real_money_allowed",
    "compounding_allowed",
    "bank_movement_allowed",
    "live_trading_allowed",
    "credential_access_allowed",
    "account_id_persistence_allowed",
)


def _fake_snapshot(classification: str, account_status: str = "DEMO_ACCOUNT_READY_FOR_REVIEW") -> SimpleNamespace:
    return SimpleNamespace(
        classification=classification,
        intake_status="SANITIZED_BROKER_SNAPSHOT_INTAKE_READY",
        account_status=account_status,
        review_packet_result=SimpleNamespace(
            classification="DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_ACCOUNT_READINESS",
            spread=Decimal("0.8"),
            blockers=("snapshot or account blocker",),
        ),
    )


def test_readiness_bridge_ready_sample_passes() -> None:
    result = run_demo_trade_readiness_bridge(build_sample_demo_trade_readiness_bridge_ready_input())

    assert result.classification == DEMO_TRADE_READINESS_BRIDGE_READY_FOR_OWNER_REVIEW
    assert result.proposed_units > 0


def test_readiness_bridge_blocked_sample_blocks() -> None:
    result = run_demo_trade_readiness_bridge(build_sample_demo_trade_readiness_bridge_blocked_input())

    assert result.classification == DEMO_TRADE_READINESS_BRIDGE_BLOCKED_SNAPSHOT
    assert result.blockers


def test_snapshot_block_blocks_bridge(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        bridge_mod,
        "run_supervised_demo_broker_snapshot_intake_epic",
        lambda _: _fake_snapshot("SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_CONTRACT"),
    )

    result = run_demo_trade_readiness_bridge(build_sample_demo_trade_readiness_bridge_ready_input())

    assert result.classification == DEMO_TRADE_READINESS_BRIDGE_BLOCKED_SNAPSHOT


def test_account_block_blocks_bridge(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        bridge_mod,
        "run_supervised_demo_broker_snapshot_intake_epic",
        lambda _: _fake_snapshot(
            "SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_BLOCKED_ACCOUNT",
            account_status="DEMO_ACCOUNT_BLOCKED_MARGIN",
        ),
    )

    result = run_demo_trade_readiness_bridge(build_sample_demo_trade_readiness_bridge_ready_input())

    assert result.classification == DEMO_TRADE_READINESS_BRIDGE_BLOCKED_ACCOUNT


def test_candidate_block_blocks_bridge() -> None:
    sample = build_sample_demo_trade_readiness_bridge_ready_input()
    result = run_demo_trade_readiness_bridge(
        replace(sample, candidate_input=build_sample_blocked_candidate_context_input())
    )

    assert result.classification == DEMO_TRADE_READINESS_BRIDGE_BLOCKED_CANDIDATE


def test_risk_block_blocks_bridge() -> None:
    sample = build_sample_demo_trade_readiness_bridge_ready_input()
    result = run_demo_trade_readiness_bridge(replace(sample, risk_input=build_sample_blocked_risk_input()))

    assert result.classification == DEMO_TRADE_READINESS_BRIDGE_BLOCKED_RISK


def test_position_size_block_blocks_bridge() -> None:
    sample = build_sample_demo_trade_readiness_bridge_ready_input()
    result = run_demo_trade_readiness_bridge(
        replace(sample, position_input=build_sample_blocked_position_size_input())
    )

    assert result.classification == DEMO_TRADE_READINESS_BRIDGE_BLOCKED_POSITION_SIZE


def test_order_plan_block_blocks_bridge() -> None:
    sample = build_sample_demo_trade_readiness_bridge_ready_input()
    config = DemoTradeReadinessBridgeConfig(order_plan_operator_review_required=False)
    result = run_demo_trade_readiness_bridge(replace(sample, config=config))

    assert result.classification == DEMO_TRADE_READINESS_BRIDGE_BLOCKED_ORDER_PLAN


def test_operator_ticket_block_blocks_bridge() -> None:
    sample = build_sample_demo_trade_readiness_bridge_ready_input()
    config = DemoTradeReadinessBridgeConfig(ticket_owner_approval_required=False)
    result = run_demo_trade_readiness_bridge(replace(sample, config=config))

    assert result.classification == DEMO_TRADE_READINESS_BRIDGE_BLOCKED_OPERATOR_TICKET


@pytest.mark.parametrize(
    "field_name",
    (
        "snapshot_intake_status",
        "snapshot_review_status",
        "account_status",
        "candidate_status",
        "risk_status",
        "position_size_status",
        "order_plan_status",
        "operator_ticket_status",
        "post_trade_capture_status",
        "feedback_router_status",
        "selected_strategy",
        "candidate_id",
        "instrument",
        "direction",
        "proposed_units",
        "entry_price",
        "stop_loss",
        "take_profit",
        "max_loss",
        "expected_reward",
        "reward_to_risk",
    ),
)
def test_bridge_includes_required_fields(field_name: str) -> None:
    result = run_demo_trade_readiness_bridge()

    assert getattr(result, field_name) not in ("", None)


def test_bridge_output_has_operator_summary() -> None:
    result = run_demo_trade_readiness_bridge()

    assert "execution remains locked" in result.operator_answer
    assert "review" in result.next_safe_action.lower()


def test_bridge_operator_text_is_plain_english() -> None:
    text = demo_trade_readiness_bridge_to_operator_text(run_demo_trade_readiness_bridge())

    assert "Demo trade readiness bridge status" in text
    assert "No trade was placed" in text


def test_bridge_markdown_has_title() -> None:
    markdown = demo_trade_readiness_bridge_to_markdown(run_demo_trade_readiness_bridge())

    assert markdown.startswith("# Demo Trade Readiness Bridge V1")


def test_bridge_json_has_required_keys() -> None:
    payload = demo_trade_readiness_bridge_to_jsonable_dict(run_demo_trade_readiness_bridge())

    for key in (
        "classification",
        "snapshot_intake_status",
        "account_status",
        "candidate_status",
        "risk_status",
        "position_size_status",
        "order_plan_status",
        "operator_ticket_status",
        "next_safe_action",
    ):
        assert key in payload
    assert json.loads(json.dumps(payload))["classification"] == DEMO_TRADE_READINESS_BRIDGE_READY_FOR_OWNER_REVIEW


def test_bridge_keeps_all_permissions_false() -> None:
    result = run_demo_trade_readiness_bridge()

    for flag in PERMISSION_FLAGS:
        assert getattr(result, flag) is False


def test_bridge_json_keeps_all_permissions_false() -> None:
    payload = demo_trade_readiness_bridge_to_jsonable_dict(run_demo_trade_readiness_bridge())

    for flag in PERMISSION_FLAGS:
        assert payload[flag] is False
