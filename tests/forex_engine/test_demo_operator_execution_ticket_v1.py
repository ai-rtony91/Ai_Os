from __future__ import annotations

from automation.forex_engine.demo_operator_execution_ticket_v1 import (
    DEMO_OPERATOR_TICKET_BLOCKED_NO_ORDER_PLAN,
    DEMO_OPERATOR_TICKET_READY_FOR_OWNER_REVIEW,
    DO_NOT_EXECUTE_WARNING,
    build_blocked_operator_ticket_input,
    build_demo_operator_execution_ticket,
    build_sample_operator_ticket_input,
    demo_operator_ticket_to_markdown,
)


def test_ready_ticket_created() -> None:
    result = build_demo_operator_execution_ticket(build_sample_operator_ticket_input())
    assert result.classification == DEMO_OPERATOR_TICKET_READY_FOR_OWNER_REVIEW


def test_missing_order_plan_blocks_ticket() -> None:
    result = build_demo_operator_execution_ticket(build_blocked_operator_ticket_input())
    assert result.classification == DEMO_OPERATOR_TICKET_BLOCKED_NO_ORDER_PLAN


def test_ticket_says_owner_approval_required() -> None:
    result = build_demo_operator_execution_ticket(build_sample_operator_ticket_input())
    assert result.owner_approval_required is True
    assert "Anthony" in result.exact_warning


def test_ticket_markdown_contains_exact_do_not_execute_warning() -> None:
    markdown = demo_operator_ticket_to_markdown(build_demo_operator_execution_ticket())
    assert DO_NOT_EXECUTE_WARNING in markdown
