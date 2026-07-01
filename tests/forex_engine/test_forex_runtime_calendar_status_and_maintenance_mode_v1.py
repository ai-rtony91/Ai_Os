from pathlib import Path

from automation.forex_engine.forex_runtime_calendar_status_and_maintenance_mode_v1 import (
    BLOCKED_BY_AUTONOMY_DRIFT,
    BLOCKED_BY_BANKING_FOCUS,
    BLOCKED_BY_PROFIT_CLAIM,
    BLOCKED_BY_SENSITIVE_DATA,
    HARD_FALSE_FIELDS,
    RUNTIME_HOLIDAY_DEGRADED_MAINTENANCE,
    RUNTIME_LOW_LIQUIDITY_DEGRADED_MAINTENANCE,
    RUNTIME_MARKET_CLOSED_MAINTENANCE,
    RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION,
    RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION,
    RUNTIME_MARKET_REOPEN_APPROACHING_PREP,
    RUNTIME_WEEKEND_HEAVY_MAINTENANCE,
    VACATION_MODE_YEAR_ROUND_RUNTIME_READY,
    evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1,
)


def _payload(**calendar_overrides):
    calendar = {
        "timezone": "America/New_York",
        "forex_week_window_defined": True,
        "market_open": True,
        "close_approaching": False,
        "reopen_approaching": False,
        "weekend_closed": False,
        "holiday_degraded": False,
        "low_liquidity_degraded": False,
        "broker_calendar_source": "DECLARED_OWNER_REVIEWED_CALENDAR",
        "runtime_uses_declared_calendar_only": True,
        "no_live_execution_authorized_by_calendar": True,
    }
    calendar.update(calendar_overrides)
    return {
        "runtime_supervision_requested": True,
        "runtime_calendar": calendar,
        "runtime_policy": {
            "ai_runtime_supervision_continuous_when_host_available": True,
            "market_calendar_controls_trade_windows": True,
            "maintenance_windows_control_non_trade_work": True,
            "night_optimization_allowed": True,
            "weekend_heavy_maintenance_allowed": True,
            "post_close_maintenance_allowed": True,
            "pre_open_preparation_allowed": True,
            "close_protection_required": True,
            "no_scheduler_created": True,
            "no_daemon_created": True,
            "no_runtime_trade_without_owner_gate": True,
            "no_unlimited_autonomous_trading": True,
        },
        "cadence_interpretation": {
            "daily_weekly_monthly_are_review_cadence": True,
            "yearly_means_vacation_mode_maturity": True,
            "yearly_profit_guarantee": False,
            "daily_profit_guarantee": False,
            "weekly_profit_guarantee": False,
            "monthly_profit_guarantee": False,
            "fixed_return_promised": False,
        },
    }


def _job_ids(result):
    return {job["job_id"] for job in result["job_queue"]}


def _blocked_job_ids(result):
    return {job["job_id"] for job in result["blocked_job_queue"]}


def _review_ids(result):
    return {review["review_id"] for review in result["owner_review_queue"]}


def test_market_open_returns_active_supervision_posture():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(_payload())

    assert result["status"] == RUNTIME_MARKET_OPEN_ACTIVE_SUPERVISION
    assert result["current_runtime_posture"] == "ACTIVE_SUPERVISION"
    assert result["primary_job_lane"] == "supervise_runtime"
    assert result["runtime_job_router_enabled"] is True
    assert result["next_best_packet"] == "AIOS_FOREX_RUNTIME_ACTIVE_SUPERVISION_STATUS_V1"


def test_market_open_job_queue_includes_p0_watch_jobs():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(_payload())

    assert {
        "risk_status_check",
        "kill_switch_state_check",
        "spread_slippage_watch",
        "receipt_capture_watch",
    }.issubset(_job_ids(result))


def test_close_approaching_returns_close_protection_posture():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(
        _payload(close_approaching=True)
    )

    assert result["status"] == RUNTIME_MARKET_CLOSE_APPROACHING_PROTECTION
    assert result["current_runtime_posture"] == "CLOSE_PROTECTION"
    assert result["primary_job_lane"] == "protect_close"


def test_close_approaching_does_not_false_positive_banking_block():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(
        _payload(close_approaching=True)
    )

    assert result["status"] != BLOCKED_BY_BANKING_FOCUS
    assert not any("close_approaching" in blocker for blocker in result["blockers"])


def test_close_approaching_job_queue_includes_protection_jobs():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(
        _payload(close_approaching=True)
    )

    assert {"no_new_risk_review", "close_boundary_protection"}.issubset(_job_ids(result))


def test_market_closed_returns_closed_maintenance_posture():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(
        _payload(market_open=False)
    )

    assert result["status"] == RUNTIME_MARKET_CLOSED_MAINTENANCE
    assert result["current_runtime_posture"] == "CLOSED_MAINTENANCE"
    assert result["primary_job_lane"] == "maintain_evidence"


def test_market_closed_job_queue_includes_maintenance_jobs():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(
        _payload(market_open=False)
    )

    assert {
        "receipt_review",
        "pnl_review",
        "evidence_compaction",
        "report_cleanup",
        "replay_validation",
        "next_session_candidate_prep",
    }.issubset(_job_ids(result))


def test_reopen_approaching_returns_reopen_preparation_posture():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(
        _payload(market_open=False, reopen_approaching=True)
    )

    assert result["status"] == RUNTIME_MARKET_REOPEN_APPROACHING_PREP
    assert result["current_runtime_posture"] == "REOPEN_PREPARATION"
    assert result["primary_job_lane"] == "prepare_next_session"


def test_reopen_approaching_does_not_false_positive_banking_block():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(
        _payload(market_open=False, reopen_approaching=True)
    )

    assert result["status"] != BLOCKED_BY_BANKING_FOCUS
    assert not any("reopen_approaching" in blocker for blocker in result["blockers"])


def test_weekend_closed_returns_weekend_heavy_maintenance_posture():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(
        _payload(market_open=False, weekend_closed=True)
    )

    assert result["status"] == RUNTIME_WEEKEND_HEAVY_MAINTENANCE
    assert result["current_runtime_posture"] == "WEEKEND_HEAVY_MAINTENANCE"
    assert result["primary_job_lane"] == "weekend_audit"


def test_weekend_job_queue_includes_heavy_review_jobs():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(
        _payload(market_open=False, weekend_closed=True)
    )

    assert {
        "weekly_expectancy_review",
        "drawdown_review",
        "strategy_retirement_review",
        "walk_forward_review",
        "pr_landing_prep",
    }.issubset(_job_ids(result))


def test_holiday_degraded_routes_degraded_safety_jobs():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(
        _payload(holiday_degraded=True)
    )

    assert result["status"] == RUNTIME_HOLIDAY_DEGRADED_MAINTENANCE
    assert result["current_runtime_posture"] == "HOLIDAY_DEGRADED_MAINTENANCE"
    assert result["primary_job_lane"] == "degraded_market_safety"
    assert "degraded_market_safety_review" in _job_ids(result)


def test_low_liquidity_degraded_routes_degraded_safety_jobs():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(
        _payload(low_liquidity_degraded=True)
    )

    assert result["status"] == RUNTIME_LOW_LIQUIDITY_DEGRADED_MAINTENANCE
    assert result["current_runtime_posture"] == "LOW_LIQUIDITY_MAINTENANCE"
    assert result["primary_job_lane"] == "degraded_market_safety"
    assert "spread_slippage_review" in _job_ids(result)


def test_vacation_mode_year_round_runtime_ready_routes_to_owner_toggle_lane():
    payload = _payload(vacation_mode_year_round_runtime_review_requested=True)
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(payload)

    assert result["status"] == VACATION_MODE_YEAR_ROUND_RUNTIME_READY
    assert result["current_runtime_posture"] == "VACATION_MODE_YEAR_ROUND_REVIEW"
    assert result["primary_job_lane"] == "vacation_mode_maturity_review"
    assert result["next_best_packet"] == "AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1"


def test_vacation_mode_toggle_semantics_do_not_authorize_execution_or_withdrawal():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(_payload())

    semantics = result["vacation_mode_toggle_semantics"]
    assert semantics["vacation_mode_on_means_request_governed_operation"] is True
    assert semantics["toggle_does_not_bypass_owner_gate"] is True
    assert semantics["toggle_does_not_bypass_market_calendar"] is True
    assert semantics["toggle_does_not_authorize_withdrawal"] is True
    assert result["next_window_preparation"]["execution_authorized_by_calendar"] is False


def test_kill_switch_semantics_are_present_and_separate_from_vacation_toggle():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(_payload())

    semantics = result["kill_switch_semantics"]
    assert semantics["kill_switch_is_emergency_hard_stop"] is True
    assert semantics["kill_switch_is_not_vacation_mode_toggle"] is True
    assert semantics["kill_switch_blocks_new_trades"] is True
    assert semantics["kill_switch_requires_owner_attention"] is True


def test_blocked_job_queue_includes_runtime_broker_and_banking_boundaries():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(_payload())

    assert {
        "live_trade_execution_by_this_module",
        "demo_trade_execution_by_this_module",
        "broker_call_by_this_module",
        "credential_read_by_this_module",
        "scheduler_creation_by_this_module",
        "daemon_creation_by_this_module",
        "dashboard_runtime_creation_by_this_module",
        "banking_work_by_this_module",
        "withdrawal_work_by_this_module",
        "transfer_work_by_this_module",
        "money_movement_by_this_module",
        "unlimited_autonomous_trading",
    }.issubset(_blocked_job_ids(result))


def test_owner_review_queue_contains_vacation_toggle_when_maturity_ready():
    payload = _payload(vacation_mode_year_round_runtime_review_requested=True)
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(payload)

    assert {
        "vacation_mode_owner_toggle_review",
        "year_round_runtime_maturity_review",
        "proof_and_receipt_readiness_review",
        "broker_runtime_boundary_review",
        "banking_withdrawal_deferred_review",
    }.issubset(_review_ids(result))


def test_profit_guarantee_still_blocks():
    payload = _payload()
    payload["cadence_interpretation"]["daily_profit_guarantee"] = True

    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(payload)

    assert result["status"] == BLOCKED_BY_PROFIT_CLAIM
    assert result["current_runtime_posture"] == "BLOCKED"
    assert result["runtime_job_router_enabled"] is False


def test_unlimited_autonomous_trading_still_blocks():
    payload = _payload()
    payload["runtime_policy"]["no_unlimited_autonomous_trading"] = False

    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(payload)

    assert result["status"] == BLOCKED_BY_AUTONOMY_DRIFT
    assert "no_unlimited_autonomous_trading_false" in result["blockers"]


def test_sensitive_data_blocks_and_does_not_echo_raw_value():
    payload = _payload()
    payload["runtime_calendar"]["api_key"] = "sk-secret-value"

    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(payload)

    assert result["status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "sk-secret-value" not in str(result)


def test_real_banking_or_withdrawal_focus_blocks():
    payload = _payload()
    payload["runtime_calendar"]["withdrawal_plan"] = "active"

    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(payload)

    assert result["status"] == BLOCKED_BY_BANKING_FOCUS


def test_all_hard_false_fields_remain_false():
    result = evaluate_forex_runtime_calendar_status_and_maintenance_mode_v1(_payload())

    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
        assert result["safety"][field] is False
    assert result["withdrawal_built"] is False
    assert result["bank_routing_built"] is False
    assert result["money_moved"] is False


def test_forbidden_runtime_marker_scan_has_no_hits():
    source = Path(
        "automation/forex_engine/forex_runtime_calendar_status_and_maintenance_mode_v1.py"
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

    assert {marker: marker in source for marker in forbidden} == {
        marker: False for marker in forbidden
    }
