from pathlib import Path

from automation.forex_engine.forex_market_close_protection_and_receipt_capture_v1 import (
    BLOCKED_BY_ACTIVE_SUPERVISION_STATE,
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_CALENDAR,
    BLOCKED_BY_POLICY,
    BLOCKED_BY_PROFIT_CLAIM,
    BLOCKED_BY_RECEIPT_STATE,
    BLOCKED_BY_RISK_STATE,
    BLOCKED_BY_SENSITIVE_DATA,
    CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY,
    CLOSE_PROTECTION_RECEIPT_CAPTURE_READY,
    CLOSE_PROTECTION_WAITING_POST_TRADE_REVIEW,
    CLOSE_PROTECTION_WAITING_RECEIPTS,
    HARD_FALSE_FIELDS,
    SCHEMA,
    evaluate_forex_market_close_protection_and_receipt_capture_v1,
)


REQUIRED_JOBS = {
    "no_new_risk_review",
    "no_new_trade_seeking_review",
    "active_supervision_defer_review",
    "open_intent_receipt_check",
    "receipt_capture_watch",
    "receipt_sanitization_check",
    "post_trade_review_check",
    "close_boundary_protection",
    "owner_attention_if_unreviewed_receipts",
    "post_close_maintenance_prep",
}

REQUIRED_BLOCKED_ACTIONS = {
    "open_new_trade_by_this_module",
    "execute_demo_by_this_module",
    "execute_live_by_this_module",
    "close_trade_by_this_module",
    "call_broker_by_this_module",
    "read_credentials_by_this_module",
    "move_money_by_this_module",
    "withdraw_by_this_module",
    "bank_route_by_this_module",
    "create_scheduler_by_this_module",
    "create_daemon_by_this_module",
    "mutate_strategy_by_this_module",
    "promise_profit_by_this_module",
}


def _payload() -> dict:
    return {
        "runtime_calendar_result": {
            "status": "RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION",
            "ready": True,
            "runtime_job_router_enabled": True,
            "current_runtime_posture": "CLOSE_PROTECTION",
            "primary_job_lane": "protect_close",
            "close_protection_recommended": True,
            "trade_window_open": True,
            "close_window_active": True,
            "execution_authorized_by_calendar": False,
            "next_best_packet": "AIOS_FOREX_MARKET_CLOSE_PROTECTION_AND_RECEIPT_CAPTURE_V1",
            "blocked_job_queue": [],
            "kill_switch_semantics": {"kill_switch_blocks_trade": True},
        },
        "active_supervision_result": {
            "status": "ACTIVE_SUPERVISION_READY",
            "ready": True,
            "active_supervision_enabled": True,
            "trade_window_open": True,
            "may_execute_demo_by_this_module": False,
            "may_execute_live_by_this_module": False,
            "may_call_broker_by_this_module": False,
            "may_move_money": False,
            "next_best_packet": "AIOS_FOREX_OWNER_APPROVED_DEMO_MULTI_PAIR_BURST_RUNTIME_EXECUTION_V1",
            "blocked_action_queue": [],
            "owner_review_queue": [
                {"review_id": "runtime_execution_packet_required_for_any_order"}
            ],
            "safety": {
                "metadata_only": True,
                "no_broker_call": True,
                "no_money_movement": True,
            },
        },
        "receipt_state": {
            "receipt_required_after_execution": True,
            "outstanding_receipts": False,
            "receipts_sanitized": True,
            "post_trade_review_complete": True,
            "receipt_capture_ready": False,
            "receipt_capture_metadata_only": True,
            "next_trade_blocked_until_receipts_reviewed": True,
            "receipt_values_sanitized": True,
            "no_raw_broker_receipts": True,
        },
        "close_policy": {
            "no_new_risk_during_close_protection": True,
            "no_new_trade_seeking_during_close_protection": True,
            "close_boundary_owner_summary_required": True,
            "owner_attention_if_unreviewed_receipts": True,
            "post_close_maintenance_prep_allowed": True,
            "receipt_capture_allowed": True,
            "broker_call_allowed": False,
            "trade_execution_allowed": False,
            "live_market_data_call_allowed": False,
            "strategy_mutation_allowed": False,
            "scheduler_creation_allowed": False,
            "daemon_creation_allowed": False,
            "raw_values_echoed": False,
        },
        "risk_state": {
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "drawdown_within_limit": True,
            "close_boundary_risk_review_required": True,
            "max_risk_per_trade_pct": 0.01,
            "max_total_burst_risk_pct": 0.03,
        },
        "owner_attention_policy": {
            "owner_attention_if_unreviewed_receipts": True,
            "owner_attention_if_post_trade_review_incomplete": True,
            "owner_attention_if_risk_blocked": True,
            "close_boundary_owner_summary_required": True,
            "raw_values_echoed": False,
            "alert_channel_metadata_only": True,
            "no_alert_runtime_created": True,
        },
        "claims": {
            "guaranteed_profit_claimed": False,
            "fixed_return_promised": False,
            "daily_profit_guaranteed": False,
            "weekly_profit_guaranteed": False,
            "monthly_profit_guaranteed": False,
            "yearly_profit_guaranteed": False,
        },
    }


def _run(payload: dict | None = None) -> dict:
    return evaluate_forex_market_close_protection_and_receipt_capture_v1(payload)


def _replace(**updates: dict) -> dict:
    payload = _payload()
    for section, values in updates.items():
        if section == "top":
            payload.update(values)
        elif values is None:
            payload.pop(section, None)
        elif section in payload:
            payload[section].update(values)
        else:
            payload[section] = values
    return payload


def test_close_protection_clean_state_routes_post_close_maintenance() -> None:
    result = _run(_payload())
    assert result["status"] == CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY
    assert result["ready"] is True
    assert result["post_close_maintenance_ready"] is True
    assert result["next_best_packet"] == "AIOS_FOREX_RUNTIME_MAINTENANCE_WORKLOAD_EXECUTION_PLAN_V1"


def test_output_schema_and_mode_present() -> None:
    result = _run(_payload())
    assert result["schema"] == SCHEMA
    assert result["mode"] == "READ_ONLY_METADATA_ONLY_FOREX_MARKET_CLOSE_PROTECTION_AND_RECEIPT_CAPTURE"


def test_close_protection_job_queue_includes_all_required_jobs() -> None:
    result = _run(_payload())
    jobs = {job["job_id"] for job in result["close_protection_job_queue"]}
    assert jobs == REQUIRED_JOBS
    assert all(job["priority"] in {"P0", "P1", "P2", "P3"} for job in result["close_protection_job_queue"])


def test_blocked_action_queue_includes_all_prohibited_actions() -> None:
    result = _run(_payload())
    actions = {action["action_id"] for action in result["blocked_action_queue"]}
    assert REQUIRED_BLOCKED_ACTIONS <= actions


def test_owner_review_queue_requires_runtime_execution_packet() -> None:
    result = _run(_payload())
    reviews = {item["review_id"]: item for item in result["owner_review_queue"]}
    assert "runtime_execution_packet_required_for_any_order" in reviews
    assert reviews["runtime_execution_packet_required_for_any_order"]["required_now"] is True


def test_calendar_not_close_protection_blocks_by_calendar() -> None:
    result = _run(_replace(runtime_calendar_result={"current_runtime_posture": "ACTIVE_SUPERVISION"}))
    assert result["status"] == BLOCKED_BY_CALENDAR


def test_close_protection_recommended_false_blocks_by_calendar() -> None:
    result = _run(_replace(runtime_calendar_result={"close_protection_recommended": False}))
    assert result["status"] == BLOCKED_BY_CALENDAR


def test_close_window_active_false_blocks_by_calendar() -> None:
    result = _run(_replace(runtime_calendar_result={"close_window_active": False}))
    assert result["status"] == BLOCKED_BY_CALENDAR


def test_calendar_execution_authorized_true_blocks_by_policy_or_calendar() -> None:
    result = _run(_replace(runtime_calendar_result={"execution_authorized_by_calendar": True}))
    assert result["status"] in {BLOCKED_BY_POLICY, BLOCKED_BY_CALENDAR}


def test_active_supervision_result_execute_demo_true_blocks() -> None:
    result = _run(_replace(active_supervision_result={"may_execute_demo_by_this_module": True}))
    assert result["status"] == BLOCKED_BY_ACTIVE_SUPERVISION_STATE


def test_active_supervision_result_execute_live_true_blocks() -> None:
    result = _run(_replace(active_supervision_result={"may_execute_live_by_this_module": True}))
    assert result["status"] == BLOCKED_BY_ACTIVE_SUPERVISION_STATE


def test_active_supervision_result_broker_call_true_blocks() -> None:
    result = _run(_replace(active_supervision_result={"may_call_broker_by_this_module": True}))
    assert result["status"] == BLOCKED_BY_ACTIVE_SUPERVISION_STATE


def test_active_supervision_result_money_movement_true_blocks() -> None:
    result = _run(_replace(active_supervision_result={"may_move_money": True}))
    assert result["status"] == BLOCKED_BY_ACTIVE_SUPERVISION_STATE


def test_no_new_risk_false_blocks_by_policy() -> None:
    result = _run(_replace(close_policy={"no_new_risk_during_close_protection": False}))
    assert result["status"] == BLOCKED_BY_POLICY


def test_no_new_trade_seeking_false_blocks_by_policy() -> None:
    result = _run(_replace(close_policy={"no_new_trade_seeking_during_close_protection": False}))
    assert result["status"] == BLOCKED_BY_POLICY


def test_broker_call_allowed_true_blocks_by_policy() -> None:
    result = _run(_replace(close_policy={"broker_call_allowed": True}))
    assert result["status"] == BLOCKED_BY_POLICY


def test_trade_execution_allowed_true_blocks_by_policy() -> None:
    result = _run(_replace(close_policy={"trade_execution_allowed": True}))
    assert result["status"] == BLOCKED_BY_POLICY


def test_live_market_data_call_allowed_true_blocks_by_policy() -> None:
    result = _run(_replace(close_policy={"live_market_data_call_allowed": True}))
    assert result["status"] == BLOCKED_BY_POLICY


def test_strategy_mutation_allowed_true_blocks_by_policy() -> None:
    result = _run(_replace(close_policy={"strategy_mutation_allowed": True}))
    assert result["status"] == BLOCKED_BY_POLICY


def test_scheduler_creation_allowed_true_blocks_by_policy() -> None:
    result = _run(_replace(close_policy={"scheduler_creation_allowed": True}))
    assert result["status"] == BLOCKED_BY_POLICY


def test_daemon_creation_allowed_true_blocks_by_policy() -> None:
    result = _run(_replace(close_policy={"daemon_creation_allowed": True}))
    assert result["status"] == BLOCKED_BY_POLICY


def test_kill_switch_active_blocks_by_risk() -> None:
    result = _run(_replace(risk_state={"kill_switch_active": True}))
    assert result["status"] == BLOCKED_BY_RISK_STATE


def test_daily_loss_stop_active_blocks_by_risk() -> None:
    result = _run(_replace(risk_state={"daily_loss_stop_active": True}))
    assert result["status"] == BLOCKED_BY_RISK_STATE


def test_drawdown_breach_blocks_by_risk() -> None:
    result = _run(_replace(risk_state={"drawdown_within_limit": False}))
    assert result["status"] == BLOCKED_BY_RISK_STATE


def test_max_risk_per_trade_pct_above_limit_blocks() -> None:
    result = _run(_replace(risk_state={"max_risk_per_trade_pct": 0.02}))
    assert result["status"] == BLOCKED_BY_RISK_STATE


def test_max_total_burst_risk_pct_above_limit_blocks() -> None:
    result = _run(_replace(risk_state={"max_total_burst_risk_pct": 0.04}))
    assert result["status"] == BLOCKED_BY_RISK_STATE


def test_outstanding_receipts_route_waiting_receipts() -> None:
    result = _run(_replace(receipt_state={"outstanding_receipts": True}))
    assert result["status"] == CLOSE_PROTECTION_WAITING_RECEIPTS


def test_unsanitized_receipts_block() -> None:
    result = _run(_replace(receipt_state={"receipts_sanitized": False}))
    assert result["status"] == BLOCKED_BY_RECEIPT_STATE


def test_receipt_values_sanitized_false_blocks() -> None:
    result = _run(_replace(receipt_state={"receipt_values_sanitized": False}))
    assert result["status"] == BLOCKED_BY_RECEIPT_STATE


def test_no_raw_broker_receipts_false_blocks() -> None:
    result = _run(_replace(receipt_state={"no_raw_broker_receipts": False}))
    assert result["status"] == BLOCKED_BY_RECEIPT_STATE


def test_post_trade_review_incomplete_routes_waiting_post_trade_review() -> None:
    result = _run(_replace(receipt_state={"post_trade_review_complete": False}))
    assert result["status"] == CLOSE_PROTECTION_WAITING_POST_TRADE_REVIEW


def test_receipt_capture_ready_routes_receipt_capture_ready_when_clean() -> None:
    result = _run(_replace(receipt_state={"receipt_capture_ready": True}))
    assert result["status"] == CLOSE_PROTECTION_RECEIPT_CAPTURE_READY
    assert result["receipt_capture_ready"] is True


def test_owner_attention_required_when_outstanding_receipts() -> None:
    result = _run(_replace(receipt_state={"outstanding_receipts": True}))
    assert result["owner_attention_required"] is True


def test_sensitive_data_blocks_and_does_not_echo_raw_value() -> None:
    result = _run(_replace(top={"api_key": "sk-DO-NOT-ECHO"}))
    assert result["status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "sk-DO-NOT-ECHO" not in repr(result)


def test_active_banking_withdrawal_blocks() -> None:
    result = _run(_replace(top={"active_withdrawal_plan": True}))
    assert result["status"] == BLOCKED_BY_BANKING_FOCUS


def test_explicit_false_banking_fields_do_not_block() -> None:
    result = _run(
        _replace(
            top={
                "withdrawal_execution_allowed": False,
                "bank_routing_allowed": False,
                "money_movement_allowed": False,
                "transfer_allowed": False,
                "ach_allowed": False,
                "wire_allowed": False,
                "card_allowed": False,
                "deposit_allowed": False,
            }
        )
    )
    assert result["status"] == CLOSE_PROTECTION_POST_CLOSE_MAINTENANCE_READY


def test_close_approaching_does_not_false_positive_as_banking() -> None:
    result = _run(_replace(top={"close_approaching": True}))
    assert result["status"] != BLOCKED_BY_BANKING_FOCUS


def test_reopen_approaching_does_not_false_positive_as_banking() -> None:
    result = _run(_replace(top={"reopen_approaching": True}))
    assert result["status"] != BLOCKED_BY_BANKING_FOCUS


def test_close_boundary_does_not_false_positive_as_banking() -> None:
    result = _run(_replace(top={"close_boundary": "owner_review"}))
    assert result["status"] != BLOCKED_BY_BANKING_FOCUS


def test_profit_guarantee_blocks() -> None:
    result = _run(_replace(claims={"daily_profit_guaranteed": True}))
    assert result["status"] == BLOCKED_BY_PROFIT_CLAIM


def test_all_hard_false_fields_remain_false() -> None:
    result = _run(_payload())
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False


def test_new_risk_allowed_false_always() -> None:
    result = _run(_payload())
    assert result["new_risk_allowed_by_this_module"] is False


def test_new_trade_seeking_allowed_false_always() -> None:
    result = _run(_payload())
    assert result["new_trade_seeking_allowed_by_this_module"] is False


def test_close_order_instruction_created_false_always() -> None:
    result = _run(_payload())
    assert result["close_order_instruction_created"] is False


def test_broker_api_called_false_always() -> None:
    result = _run(_payload())
    assert result["broker_api_called_by_this_module"] is False


def test_money_moved_false_always() -> None:
    result = _run(_payload())
    assert result["money_moved"] is False


def test_production_source_has_no_forbidden_runtime_markers() -> None:
    source = Path(
        "automation/forex_engine/forex_market_close_protection_and_receipt_capture_v1.py"
    ).read_text(encoding="utf-8").lower()
    forbidden = [
        "requests",
        "socket",
        "urllib",
        "subprocess",
        "os.environ",
        "broker_sdk",
        "schedule.every",
        "start-process",
    ]
    assert {marker for marker in forbidden if marker in source} == set()
