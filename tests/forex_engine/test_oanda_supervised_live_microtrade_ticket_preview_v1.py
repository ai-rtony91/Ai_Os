from __future__ import annotations

import json
from decimal import Decimal

import pytest

from automation.forex_engine import oanda_supervised_live_microtrade_ticket_preview_v1 as ticket
from automation.forex_engine.oanda_supervised_live_microtrade_final_gate_v1 import (
    PROTECTED_FLAG_NAMES,
)


def _result(builder=ticket.build_sample_ready_input):
    return ticket.build_oanda_supervised_live_microtrade_ticket_preview(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (
            ticket.build_sample_ready_input,
            ticket.OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_READY_FOR_OWNER_REVIEW,
        ),
        (
            ticket.build_sample_missing_input,
            ticket.OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_REQUIRE_REPAIR,
        ),
        (
            ticket.build_sample_unsafe_input,
            ticket.OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_BLOCKED_UNSAFE,
        ),
    ),
)
def test_ticket_preview_sample_classifications(builder, classification: str):
    assert _result(builder).classification == classification


def test_ticket_preview_version_constant():
    assert ticket.VERSION == "oanda_supervised_live_microtrade_ticket_preview_v1"


@pytest.mark.parametrize(
    ("field_name", "expected"),
    (
        ("sanitized_local_ticket_id", "LOCAL-MICROTRADE-PREVIEW-001"),
        ("instrument", "EUR_USD"),
        ("direction", "long"),
        ("order_type", "market_owner_manual"),
        ("planned_units", Decimal("1")),
        ("max_units", Decimal("1")),
        ("planned_max_loss", Decimal("1.00")),
        ("planned_stop_distance", Decimal("0.0010")),
        ("planned_take_profit_distance", Decimal("0.0015")),
        ("planned_risk_r", Decimal("1.00")),
    ),
)
def test_ticket_preview_required_values(field_name: str, expected):
    assert getattr(_result(), field_name) == expected


@pytest.mark.parametrize(
    "field_name",
    (
        "one_shot_only",
        "no_compounding",
        "no_bank_movement",
        "no_autonomous_loop",
        "owner_final_approval_required",
        "preview_only",
    ),
)
def test_ticket_preview_required_true_fields(field_name: str):
    assert getattr(_result(), field_name) is True


def test_ticket_preview_no_profit_guarantee():
    assert _result().profit_guaranteed is False


def test_ticket_preview_no_live_approval():
    assert _result().live_approval_granted is False


@pytest.mark.parametrize(
    ("field_name", "value", "repair_item"),
    (
        ("planned_units", "0", "planned_units_positive"),
        ("planned_units", "2", "planned_units_tiny"),
        ("max_units", "0", "max_units_bounded"),
        ("max_units", "2", "max_units_bounded"),
        ("planned_max_loss", "0", "planned_max_loss_bounded"),
        ("planned_max_loss", "2.00", "planned_max_loss_bounded"),
        ("planned_stop_distance", "0", "planned_stop_distance_positive"),
        ("planned_take_profit_distance", "0", "planned_take_profit_distance_positive"),
        ("planned_risk_r", "0", "planned_risk_r_bounded"),
        ("planned_risk_r", "2.00", "planned_risk_r_bounded"),
    ),
)
def test_ticket_preview_repair_bounds(field_name: str, value: str, repair_item: str):
    data = ticket.to_jsonable_dict(ticket.build_sample_ready_input())
    data[field_name] = value
    result = ticket.build_oanda_supervised_live_microtrade_ticket_preview(data)
    assert result.classification == ticket.OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_REQUIRE_REPAIR
    assert repair_item in result.repair_items


@pytest.mark.parametrize(
    "field_name",
    (
        "one_shot_only",
        "no_compounding",
        "no_bank_movement",
        "no_autonomous_loop",
        "preview_only",
    ),
)
def test_ticket_preview_repairs_false_boundary_fields(field_name: str):
    data = ticket.to_jsonable_dict(ticket.build_sample_ready_input())
    data[field_name] = False
    result = ticket.build_oanda_supervised_live_microtrade_ticket_preview(data)
    assert result.classification == ticket.OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_REQUIRE_REPAIR
    assert field_name in result.repair_items


def test_ticket_preview_blocks_owner_approval_false():
    result = _result(ticket.build_sample_unsafe_input)
    assert result.classification == ticket.OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_BLOCKED_UNSAFE
    assert "owner_final_approval_required_false" in result.blocked_items


@pytest.mark.parametrize("flag_name", PROTECTED_FLAG_NAMES)
def test_ticket_preview_all_protected_flags_false(flag_name: str):
    result = _result()
    assert getattr(result, flag_name) is False
    assert result.protected_flags[flag_name] is False


@pytest.mark.parametrize(
    "forbidden_fragment",
    (
        "api-fxtrade",
        "sk-",
        "broker_order_id",
        "raw_broker_payload",
        "place_order",
        "execute_order",
    ),
)
def test_ticket_preview_no_sensitive_or_execution_fragments(forbidden_fragment: str):
    payload = json.dumps(ticket.to_jsonable_dict(_result())).lower()
    assert forbidden_fragment not in payload


def test_ticket_preview_json_serializable():
    json.dumps(ticket.to_jsonable_dict(_result()))


def test_ticket_preview_markdown_output():
    assert ticket.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Supervised Live Microtrade Ticket Preview V1"
    )


def test_ticket_preview_operator_text_output():
    assert "Ticket preview status" in ticket.to_operator_text(_result())


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
        "Vacation profit trial remains blocked unless Anthony separately approves.",
        "Profit is not guaranteed.",
        "All protected flags remain false.",
        "Owner-run only.",
        "One-shot only.",
    ),
)
def test_ticket_preview_markdown_safety_phrases(phrase: str):
    assert phrase in ticket.to_markdown(_result())
