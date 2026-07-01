from pathlib import Path

from automation.forex_engine.forex_runtime_active_supervision_status_v1 import (
    ACTIVE_SUPERVISION_MAINTENANCE_FALLBACK,
    ACTIVE_SUPERVISION_READY,
    ACTIVE_SUPERVISION_WAITING_FOR_PROOF,
    ACTIVE_SUPERVISION_WAITING_FOR_RECEIPTS,
    ACTIVE_SUPERVISION_BALANCE_REVIEW_REQUIRED,
    ACTIVE_SUPERVISION_COMPOUNDING_REVIEW_REQUIRED,
    ACTIVE_SUPERVISION_PROFIT_PROTECTION_REVIEW_REQUIRED,
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_CALENDAR,
    BLOCKED_BY_PERMISSION_SNAPSHOT,
    BLOCKED_BY_POLICY,
    BLOCKED_BY_PROFIT_CLAIM,
    BLOCKED_BY_RECEIPT_STATE,
    BLOCKED_BY_RISK_STATE,
    BLOCKED_BY_SENSITIVE_DATA,
    HARD_FALSE_FIELDS,
    SCHEMA,
    evaluate_forex_runtime_active_supervision_status_v1,
)


REQUIRED_JOBS = {
    "risk_status_check",
    "kill_switch_state_check",
    "daily_loss_stop_check",
    "drawdown_check",
    "spread_policy_watch",
    "slippage_policy_watch",
    "receipt_capture_watch",
    "post_trade_review_watch",
    "balance_equity_watch",
    "compounding_scale_watch",
    "profit_protection_watch",
    "candidate_metadata_refresh",
    "proof_continuity_check",
    "owner_alert_readiness",
}

REQUIRED_BLOCKED_ACTIONS = {
    "execute_demo_by_this_module",
    "execute_live_by_this_module",
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
            "status": "RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION",
            "ready": True,
            "runtime_job_router_enabled": True,
            "current_runtime_posture": "ACTIVE_SUPERVISION",
            "primary_job_lane": "supervise_runtime",
            "trade_window_open": True,
            "execution_authorized_by_calendar": False,
            "next_best_packet": "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1",
            "blocked_job_queue": [],
            "vacation_mode_toggle_semantics": {"owner_toggle_required": True},
            "kill_switch_semantics": {"kill_switch_blocks_trade": True},
        },
        "vacation_mode_result": {
            "campaign_status": "VACATION_MODE_OWNER_TOGGLE_ACTIVE_SUPERVISION_READY",
            "campaign_ready": True,
            "vacation_mode_requested": True,
            "vacation_mode_toggle_state": "ON",
            "vacation_mode_operation_state": "VACATION_MODE_ON_ACTIVE_SUPERVISION_ELIGIBLE",
            "new_trade_seeking_allowed_by_this_module": False,
            "maintenance_allowed_by_this_module": True,
            "owner_attention_required": False,
            "next_best_packet": "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1",
            "safety": {"metadata_only": True},
        },
        "permission_snapshot": {
            "may_scan_metadata": True,
            "may_prepare_candidates": True,
            "may_prepare_demo_runtime_intent_metadata": True,
            "may_prepare_live_owner_review_metadata": True,
            "may_prepare_maintenance_work": True,
            "may_prepare_receipt_review": True,
            "may_prepare_balance_learning_review": True,
            "may_execute_demo_by_this_module": False,
            "may_execute_live_by_this_module": False,
            "may_call_broker_by_this_module": False,
            "may_read_credentials_by_this_module": False,
            "may_move_money": False,
            "may_withdraw": False,
            "may_bank_route": False,
            "owner_runtime_packet_required_for_execution": True,
        },
        "risk_state": {
            "kill_switch_active": False,
            "daily_loss_stop_active": False,
            "drawdown_within_limit": True,
            "current_drawdown_pct": 0.01,
            "max_drawdown_pct": 0.04,
            "current_daily_loss_pct": 0.002,
            "max_daily_loss_pct": 0.03,
            "max_risk_per_trade_pct": 0.01,
            "max_total_burst_risk_pct": 0.03,
            "risk_policy_owner_reviewed": True,
        },
        "receipt_state": {
            "receipt_required_after_execution": True,
            "outstanding_receipts": False,
            "receipts_sanitized": True,
            "post_trade_review_complete": True,
            "next_trade_blocked_until_receipts_reviewed": True,
        },
        "balance_state": {
            "balance_memory_ready": True,
            "compounding_observer_ready": True,
            "withdrawal_deferred": True,
            "bank_routing_deferred": True,
            "money_moved": False,
            "current_balance_present": True,
            "current_equity_present": True,
        },
        "compounding_state": {
            "compounding_scale_ready": True,
            "compounding_status": "GOVERNED_COMPOUNDING_SCALE_UP_ALLOWED",
            "scale_decision": "SCALE_UP",
            "scale_direction": "UP",
            "proposed_next_risk_budget_pct": 0.003,
            "owner_decision_required": True,
            "money_moved": False,
            "withdrawal_allowed_by_this_module": False,
            "bank_routing_allowed_by_this_module": False,
        },
        "profit_protection_state": {
            "profit_protection_ready": True,
            "profit_protection_status": "PROFIT_LOCK_READY",
            "realized_profit_only": True,
            "withdrawal_review_future_enabled": True,
            "withdrawal_execution_allowed": False,
            "bank_routing_allowed": False,
            "money_moved": False,
        },
        "proof_state": {
            "proof_required": True,
            "proof_ready": True,
            "proof_continuity_ready": True,
            "fake_proof_blocked": True,
            "repeatability_review_ready": True,
            "owner_review_required_for_live": True,
        },
        "candidate_policy": {
            "candidate_refresh_metadata_allowed": True,
            "strategy_mutation_allowed": False,
            "broker_call_allowed": False,
            "live_market_data_call_allowed": False,
            "require_stop_loss": True,
            "require_take_profit": True,
            "require_spread_policy": True,
            "require_slippage_policy": True,
            "require_news_blackout_policy": True,
            "owner_runtime_packet_required_for_execution": True,
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
    return evaluate_forex_runtime_active_supervision_status_v1(payload)


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


def test_market_open_active_supervision_ready() -> None:
    result = _run(_payload())
    assert result["status"] == ACTIVE_SUPERVISION_READY
    assert result["ready"] is True
    assert result["active_supervision_enabled"] is True
    assert result["read_only"] is True
    assert result["metadata_only"] is True


def test_output_schema_and_mode_present() -> None:
    result = _run(_payload())
    assert result["schema"] == SCHEMA
    assert result["mode"] == "READ_ONLY_METADATA_ONLY_RUNTIME_ACTIVE_SUPERVISION_STATUS"


def test_active_supervision_job_queue_includes_all_required_jobs() -> None:
    result = _run(_payload())
    jobs = {job["job_id"] for job in result["supervision_job_queue"]}
    assert jobs == REQUIRED_JOBS
    assert all(job["priority"] in {"P0", "P1", "P2", "P3"} for job in result["supervision_job_queue"])


def test_blocked_action_queue_includes_all_prohibited_actions() -> None:
    result = _run(_payload())
    actions = {action["action_id"] for action in result["blocked_action_queue"]}
    assert REQUIRED_BLOCKED_ACTIONS <= actions


def test_owner_review_queue_requires_runtime_execution_packet() -> None:
    result = _run(_payload())
    reviews = {item["review_id"]: item for item in result["owner_review_queue"]}
    assert "runtime_execution_packet_required_for_any_order" in reviews
    assert reviews["runtime_execution_packet_required_for_any_order"]["required_now"] is True


def test_calendar_not_open_blocks_by_calendar() -> None:
    result = _run(_replace(runtime_calendar_result={"trade_window_open": False}))
    assert result["status"] == BLOCKED_BY_CALENDAR


def test_calendar_execution_authorized_true_blocks_by_policy_or_calendar() -> None:
    result = _run(_replace(runtime_calendar_result={"execution_authorized_by_calendar": True}))
    assert result["status"] in {BLOCKED_BY_POLICY, BLOCKED_BY_CALENDAR}


def test_vacation_mode_off_routes_maintenance_fallback_or_blocks() -> None:
    result = _run(_replace(vacation_mode_result={"vacation_mode_toggle_state": "OFF"}))
    assert result["status"] in {ACTIVE_SUPERVISION_MAINTENANCE_FALLBACK, BLOCKED_BY_POLICY}


def test_vacation_mode_pause_routes_maintenance_fallback_or_blocks() -> None:
    result = _run(_replace(vacation_mode_result={"vacation_mode_toggle_state": "PAUSE"}))
    assert result["status"] in {ACTIVE_SUPERVISION_MAINTENANCE_FALLBACK, BLOCKED_BY_POLICY}


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


def test_permission_snapshot_execute_demo_true_blocks() -> None:
    result = _run(_replace(permission_snapshot={"may_execute_demo_by_this_module": True}))
    assert result["status"] == BLOCKED_BY_PERMISSION_SNAPSHOT


def test_permission_snapshot_execute_live_true_blocks() -> None:
    result = _run(_replace(permission_snapshot={"may_execute_live_by_this_module": True}))
    assert result["status"] == BLOCKED_BY_PERMISSION_SNAPSHOT


def test_permission_snapshot_broker_call_true_blocks() -> None:
    result = _run(_replace(permission_snapshot={"may_call_broker_by_this_module": True}))
    assert result["status"] == BLOCKED_BY_PERMISSION_SNAPSHOT


def test_permission_snapshot_credential_read_true_blocks() -> None:
    result = _run(_replace(permission_snapshot={"may_read_credentials_by_this_module": True}))
    assert result["status"] == BLOCKED_BY_PERMISSION_SNAPSHOT


def test_permission_snapshot_money_movement_true_blocks() -> None:
    result = _run(_replace(permission_snapshot={"may_move_money": True}))
    assert result["status"] == BLOCKED_BY_PERMISSION_SNAPSHOT


def test_outstanding_receipts_route_waiting_receipts() -> None:
    result = _run(_replace(receipt_state={"outstanding_receipts": True}))
    assert result["status"] == ACTIVE_SUPERVISION_WAITING_FOR_RECEIPTS


def test_unsanitized_receipts_block() -> None:
    result = _run(_replace(receipt_state={"receipts_sanitized": False}))
    assert result["status"] == BLOCKED_BY_RECEIPT_STATE


def test_post_trade_review_incomplete_blocks() -> None:
    result = _run(_replace(receipt_state={"post_trade_review_complete": False}))
    assert result["status"] == BLOCKED_BY_RECEIPT_STATE


def test_balance_memory_missing_routes_balance_review_required() -> None:
    result = _run(_replace(balance_state={"balance_memory_ready": False}))
    assert result["status"] == ACTIVE_SUPERVISION_BALANCE_REVIEW_REQUIRED


def test_compounding_not_ready_routes_compounding_review_required() -> None:
    result = _run(_replace(compounding_state={"compounding_scale_ready": False}))
    assert result["status"] == ACTIVE_SUPERVISION_COMPOUNDING_REVIEW_REQUIRED


def test_profit_protection_not_ready_routes_profit_review_required() -> None:
    result = _run(_replace(profit_protection_state={"profit_protection_ready": False}))
    assert result["status"] == ACTIVE_SUPERVISION_PROFIT_PROTECTION_REVIEW_REQUIRED


def test_proof_required_but_not_ready_routes_waiting_proof() -> None:
    result = _run(_replace(proof_state={"proof_ready": False}))
    assert result["status"] == ACTIVE_SUPERVISION_WAITING_FOR_PROOF


def test_proof_continuity_false_routes_waiting_proof() -> None:
    result = _run(_replace(proof_state={"proof_continuity_ready": False}))
    assert result["status"] == ACTIVE_SUPERVISION_WAITING_FOR_PROOF


def test_strategy_mutation_allowed_blocks() -> None:
    result = _run(_replace(candidate_policy={"strategy_mutation_allowed": True}))
    assert result["status"] == BLOCKED_BY_POLICY


def test_broker_call_allowed_blocks() -> None:
    result = _run(_replace(candidate_policy={"broker_call_allowed": True}))
    assert result["status"] == BLOCKED_BY_POLICY


def test_live_market_data_call_allowed_blocks() -> None:
    result = _run(_replace(candidate_policy={"live_market_data_call_allowed": True}))
    assert result["status"] == BLOCKED_BY_POLICY


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
    assert result["status"] == ACTIVE_SUPERVISION_READY


def test_profit_guarantee_blocks() -> None:
    result = _run(_replace(claims={"daily_profit_guaranteed": True}))
    assert result["status"] == BLOCKED_BY_PROFIT_CLAIM


def test_all_hard_false_fields_remain_false() -> None:
    result = _run(_payload())
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False


def test_may_execute_demo_false_always() -> None:
    result = _run(_payload())
    assert result["may_execute_demo_by_this_module"] is False


def test_may_execute_live_false_always() -> None:
    result = _run(_payload())
    assert result["may_execute_live_by_this_module"] is False


def test_may_call_broker_false_always() -> None:
    result = _run(_payload())
    assert result["may_call_broker_by_this_module"] is False


def test_may_move_money_false_always() -> None:
    result = _run(_payload())
    assert result["may_move_money"] is False


def test_ready_state_routes_demo_runtime_without_execution_payload() -> None:
    result = _run(_payload())
    assert result["next_best_packet"] == "AIOS_FOREX_OWNER_APPROVED_DEMO_MULTI_PAIR_BURST_RUNTIME_EXECUTION_V1"
    assert result["demo_execution_payload_created"] is False
    assert result["live_execution_payload_created"] is False
    assert "execution_payload" not in result
    assert "order_instruction" not in result
    assert "broker_instruction" not in result


def test_production_source_has_no_forbidden_runtime_markers() -> None:
    source = Path("automation/forex_engine/forex_runtime_active_supervision_status_v1.py").read_text(
        encoding="utf-8"
    ).lower()
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
