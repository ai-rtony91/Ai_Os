from __future__ import annotations

import json
from decimal import Decimal

import pytest

from automation.forex_engine.demo_broker_snapshot_review_packet_v1 import (
    DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_ACCOUNT_READINESS,
    DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_INTAKE,
    DEMO_BROKER_SNAPSHOT_REVIEW_READY,
    build_demo_broker_snapshot_review_packet,
    build_sample_blocked_review_packet_input,
    build_sample_review_packet_input,
    demo_broker_snapshot_review_packet_to_jsonable_dict,
    demo_broker_snapshot_review_packet_to_markdown,
    demo_broker_snapshot_review_packet_to_operator_text,
)
from automation.forex_engine.sanitized_broker_snapshot_intake_v1 import (
    build_sample_sanitized_snapshot_intake_input,
)


def _low_margin_mapping() -> dict[str, object]:
    raw = dict(build_sample_sanitized_snapshot_intake_input().snapshot)
    raw["margin_available"] = "50.00"
    return raw


def test_review_packet_ready_sample_passes() -> None:
    result = build_demo_broker_snapshot_review_packet(build_sample_review_packet_input())
    assert result.classification == DEMO_BROKER_SNAPSHOT_REVIEW_READY
    assert result.snapshot_review_allowed is True


def test_blocked_intake_blocks_review_packet() -> None:
    result = build_demo_broker_snapshot_review_packet(build_sample_blocked_review_packet_input())
    assert result.classification == DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_INTAKE
    assert result.account_review_allowed is False


def test_blocked_account_readiness_blocks_review_packet() -> None:
    result = build_demo_broker_snapshot_review_packet({"intake_input": _low_margin_mapping()})
    assert result.classification == DEMO_BROKER_SNAPSHOT_REVIEW_BLOCKED_ACCOUNT_READINESS
    assert result.account_review_allowed is False


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("balance", Decimal("10000.00")),
        ("margin_available", Decimal("9500.00")),
        ("open_trades", 0),
        ("open_positions", 0),
        ("pending_orders", 0),
        ("spread", Decimal("0.8")),
        ("market_hours_open", True),
        ("instrument_tradeable", True),
        ("read_only_reconciled", True),
        ("sanitized", True),
    ],
)
def test_review_packet_includes_snapshot_fields(field: str, expected: object) -> None:
    result = build_demo_broker_snapshot_review_packet()
    assert getattr(result, field) == expected


def test_review_packet_includes_operator_summary() -> None:
    result = build_demo_broker_snapshot_review_packet()
    assert "Broker snapshot review is ready" in result.operator_summary


def test_review_packet_markdown_has_title() -> None:
    assert demo_broker_snapshot_review_packet_to_markdown().startswith("# Demo Broker Snapshot Review Packet V1")


def test_review_packet_operator_text_is_plain_english() -> None:
    text = demo_broker_snapshot_review_packet_to_operator_text()
    assert "No trade was placed." in text
    assert "DEMO_BROKER" not in text


@pytest.mark.parametrize(
    "permission",
    [
        "demo_execution_allowed",
        "broker_action_allowed",
        "real_money_allowed",
        "compounding_allowed",
        "bank_movement_allowed",
        "live_trading_allowed",
        "credential_access_allowed",
        "account_id_persistence_allowed",
    ],
)
def test_review_packet_permission_flags_remain_false(permission: str) -> None:
    result = build_demo_broker_snapshot_review_packet()
    assert getattr(result, permission) is False


def test_review_packet_output_json_serializable() -> None:
    payload = demo_broker_snapshot_review_packet_to_jsonable_dict(build_demo_broker_snapshot_review_packet())
    assert json.loads(json.dumps(payload))["classification"] == DEMO_BROKER_SNAPSHOT_REVIEW_READY


def test_review_packet_repeated_output_deterministic() -> None:
    first = demo_broker_snapshot_review_packet_to_jsonable_dict(build_demo_broker_snapshot_review_packet())
    second = demo_broker_snapshot_review_packet_to_jsonable_dict(build_demo_broker_snapshot_review_packet())
    assert first == second
