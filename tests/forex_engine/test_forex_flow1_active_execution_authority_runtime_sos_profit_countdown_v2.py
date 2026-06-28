"""Tests for Flow 1 active execution authority runtime SOS profit countdown V2."""

from pathlib import Path

from automation.forex_engine import forex_flow1_active_execution_authority_runtime_sos_profit_countdown_v2 as flow1


def test_default_owner_input_blocked_to_required_defaults():
    result = flow1.evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown()
    assert result["flow1_status"] == "FLOW1_BLOCKED_OWNER_INPUT_REQUIRED"
    assert result["flow1_mode"] == "PAUSE_READY"
    assert result["owner_live_capital_intent_usd"] == 1000
    assert result["requested_max_open_positions"] == 4
    assert result["requested_quantity_scale"] == 4.0
    assert result["hardcoded_10000_baseline_forbidden"] is True
    assert result["target_return_band"] == "100_TO_120_PERCENT"
    assert result["target_return_claim_status"] == "TARGET_NOT_YET_VERIFIED"
    assert result["profit_return_rate_status"] == "COUNTDOWN_NOT_ACTIVE_BASELINE_REQUIRED"
    assert result["runtime_objective"] == "22_HOURS_PER_DAY_6_DAYS_PER_WEEK"
    assert result["runtime_status"] == "GATED_PENDING_SUPERVISED_EVIDENCE"
    assert result["vacation_mode_status"] == "TARGET_DEFINED_GATE_PENDING"
    assert result["sos_alert_integration_status"] == "REQUIRED_GATE_PENDING"


def test_continue_path_with_valid_input_activates_countdown_and_flow2_handoff():
    owner_input = {
        "flow1_action": "CONTINUE",
        "baseline_equity": 1000.0,
        "current_equity": 1250.0,
        "available_equity": 1250.0,
        "open_trade_count": 0,
        "requested_max_open_positions": 4,
        "configured_max_open_positions": 4,
        "max_open_positions": 4,
        "risk_per_trade_percent": 0.25,
        "max_aggregate_open_risk_percent": 1.00,
        "max_margin_utilization_percent": 25.00,
        "estimated_margin_per_position": 50.0,
        "estimated_risk_amount_per_position": 2.50,
        "daily_realized_loss_percent": 0.0,
        "weekly_realized_loss_percent": 0.0,
        "current_drawdown_percent": 0.0,
        "target_return_band_acknowledged": True,
        "profit_countdown_acknowledged": True,
        "runtime_objective_acknowledged": True,
        "vacation_mode_target_acknowledged": True,
        "sos_alerts_acknowledged": True,
        "risk_controls_acknowledged": True,
        "idempotency_acknowledged": True,
        "no_duplicate_order_acknowledged": True,
        "stale_price_guard_acknowledged": True,
        "kill_switch_acknowledged": True,
        "owner_supervised_demo_execution_acknowledged": True,
        "flow2_evidence_capture_acknowledged": True,
        "demo_account_marker": "DEMO_ONLY",
        "broker_environment": "DEMO_OR_PRACTICE_ONLY",
        "owner_attestation": True,
        "kill_switch_state": False,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "demo_order_placement_authorized": False,
        "live_trading_authorized": False,
        "execution_command_authorized": False,
        "runtime_22h6d_activated": False,
        "vacation_mode_activated": False,
        "autonomous_trading_authorized": False,
        "money_movement_authorized": False,
        "broker_connection_authorized": False,
        "order_submission_authorized": False,
    }
    result = flow1.evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown(owner_input)
    assert result["flow1_status"] == (
        "FLOW1_ACTIVE_GATE_READY_FOR_FLOW2_SUPERVISED_DEMO_EVIDENCE_CAPTURE"
    )
    assert result["flow1_mode"] == "CONTINUE_READY"
    assert result["flow2_handoff_status"] == "READY"
    assert result["publish_status"] == "READY_AFTER_HOST_VALIDATION"


def test_pause_action_sets_pause_mode():
    owner_input = {"flow1_action": "PAUSE"}
    result = flow1.evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown(owner_input)
    assert result["flow1_mode"] == "PAUSED"
    assert result["publish_status"] == "NOT_READY_PAUSED"


def test_stop_action_sets_stop_mode():
    owner_input = {"flow1_action": "STOP"}
    result = flow1.evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown(owner_input)
    assert result["flow1_mode"] == "STOPPED"
    assert result["publish_status"] == "NOT_READY_STOPPED"


def test_bridge_action_populates_bridge_map():
    owner_input = {"flow1_action": "BRIDGE"}
    result = flow1.evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown(owner_input)
    names = [entry["island_name"] for entry in result["flow1_bridge_map"]]
    assert result["flow1_mode"] == "BRIDGE_BUILDING"
    assert result["next_required_action"] == "CONTINUE_AFTER_BRIDGE_VALIDATION"
    assert "flow1_position_capacity_bridge" in names
    assert "flow1_target_countdown_bridge" in names
    assert "flow1_publish_clean_merge_bridge" in names
    assert "flow1_flow2_evidence_handoff_bridge" in names


def test_baseline_to_countdown_calculations():
    owner_input = {
        "baseline_equity": 1000.0,
        "current_equity": 1250.0,
    }
    evaluated = flow1.evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown(owner_input)
    assert evaluated["cumulative_return_percent"] == 25.0
    assert evaluated["target_equity_100_percent"] == 2000.0
    assert evaluated["target_equity_120_percent"] == 2200.0
    assert evaluated["remaining_to_100_percent"] == 75.0
    assert evaluated["remaining_to_120_percent"] == 95.0
    assert evaluated["milestone_alert"] == "TARGET_25_PROGRESS_ALERT"


def test_countdown_targets():
    evaluated_2000 = flow1.evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown(
        {"baseline_equity": 1000.0, "current_equity": 2000.0}
    )
    assert evaluated_2000["target_100_reached"] is True

    evaluated_2200 = flow1.evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown(
        {"baseline_equity": 1000.0, "current_equity": 2200.0}
    )
    assert evaluated_2200["target_120_reached"] is True


def test_drawdown_alert_levels():
    drawdown_5 = flow1.evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown(
        {"baseline_equity": 1000.0, "current_equity": 1100.0, "current_drawdown_percent": 5}
    )
    assert drawdown_5["drawdown_alert"] == "DRAWDOWN_WARNING_OWNER_REVIEW"

    drawdown_10 = flow1.evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown(
        {"baseline_equity": 1000.0, "current_equity": 1100.0, "current_drawdown_percent": 10}
    )
    assert drawdown_10["drawdown_alert"] == "DRAWDOWN_CRITICAL_SOS_STOP_REVIEW"


def test_valid_capacity_allows_max_four():
    owner_input = {
        "baseline_equity": 1000.0,
        "current_equity": 1000.0,
        "available_equity": 1000.0,
        "requested_max_open_positions": 4,
        "configured_max_open_positions": 4,
        "max_open_positions": 4,
        "open_trade_count": 0,
        "current_drawdown_percent": 0.0,
        "risk_per_trade_percent": 0.25,
        "max_aggregate_open_risk_percent": 1.0,
        "max_margin_utilization_percent": 25.0,
        "estimated_margin_per_position": 50.0,
        "estimated_risk_amount_per_position": 2.5,
    }
    capacity = flow1.calculate_position_capacity(owner_input)
    assert capacity["final_position_capacity"] == 4


def test_partial_capacity_ranges_between_one_and_three():
    owner_input = {
        "baseline_equity": 1000.0,
        "current_equity": 1000.0,
        "available_equity": 1000.0,
        "requested_max_open_positions": 4,
        "configured_max_open_positions": 4,
        "max_open_positions": 4,
        "open_trade_count": 3,
        "current_drawdown_percent": 0.0,
        "risk_per_trade_percent": 0.25,
        "max_aggregate_open_risk_percent": 1.0,
        "max_margin_utilization_percent": 25.0,
        "estimated_margin_per_position": 50.0,
        "estimated_risk_amount_per_position": 2.5,
    }
    capacity = flow1.calculate_position_capacity(owner_input)
    assert capacity["final_position_capacity"] >= 1
    assert capacity["final_position_capacity"] <= 3


def test_kill_switch_blocks_capacity_and_flow2():
    owner_input = {
        "baseline_equity": 1000.0,
        "current_equity": 1250.0,
        "available_equity": 1250.0,
        "open_trade_count": 0,
        "max_open_positions": 4,
        "kill_switch_state": True,
        "target_return_band_acknowledged": True,
        "profit_countdown_acknowledged": True,
        "runtime_objective_acknowledged": True,
        "vacation_mode_target_acknowledged": True,
        "sos_alerts_acknowledged": True,
        "risk_controls_acknowledged": True,
        "idempotency_acknowledged": True,
        "no_duplicate_order_acknowledged": True,
        "stale_price_guard_acknowledged": True,
        "kill_switch_acknowledged": True,
        "owner_supervised_demo_execution_acknowledged": True,
        "flow2_evidence_capture_acknowledged": True,
        "demo_account_marker": "DEMO_ONLY",
        "broker_environment": "DEMO_OR_PRACTICE_ONLY",
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "demo_order_placement_authorized": False,
        "live_trading_authorized": False,
        "execution_command_authorized": False,
        "runtime_22h6d_activated": False,
        "vacation_mode_activated": False,
        "autonomous_trading_authorized": False,
        "money_movement_authorized": False,
        "broker_connection_authorized": False,
        "order_submission_authorized": False,
    }
    result = flow1.evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown(owner_input)
    assert result["final_position_capacity"] == 0
    assert result["flow2_handoff_status"] != "READY"


def test_open_trade_cap_reaches_zero_capacity():
    owner_input = {
        "requested_max_open_positions": 4,
        "configured_max_open_positions": 4,
        "max_open_positions": 4,
        "open_trade_count": 4,
        "available_equity": 1250.0,
    }
    capacity = flow1.calculate_position_capacity(owner_input)
    assert capacity["final_position_capacity"] == 0


def test_forbidden_fields_fail():
    owner_input = {
        "account_id": "blocked",
        "baseline_equity": 1000.0,
        "current_equity": 1000.0,
    }
    result = flow1.evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown(owner_input)
    assert "FLOW1_BLOCKED_FORBIDDEN_FIELD_PRESENT" in result["flow1_status"]


def test_authorization_true_fields_fail():
    owner_input = {
        "live_trading_authorized": True,
        "baseline_equity": 1000.0,
        "current_equity": 1000.0,
    }
    result = flow1.evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown(owner_input)
    assert "FLOW1_BLOCKED_AUTHORIZATION_ENABLED" in result["flow1_status"]


def test_authorization_false_fields_pass():
    owner_input = {
        "baseline_equity": 1000.0,
        "current_equity": 1250.0,
        "available_equity": 1250.0,
        "open_trade_count": 0,
        "max_open_positions": 4,
        "target_return_band_acknowledged": True,
        "profit_countdown_acknowledged": True,
        "runtime_objective_acknowledged": True,
        "vacation_mode_target_acknowledged": True,
        "sos_alerts_acknowledged": True,
        "risk_controls_acknowledged": True,
        "idempotency_acknowledged": True,
        "no_duplicate_order_acknowledged": True,
        "stale_price_guard_acknowledged": True,
        "kill_switch_acknowledged": True,
        "owner_supervised_demo_execution_acknowledged": True,
        "flow2_evidence_capture_acknowledged": True,
        "broker_api_access_authorized": False,
        "credential_access_authorized": False,
        "demo_order_placement_authorized": False,
        "live_trading_authorized": False,
        "execution_command_authorized": False,
        "runtime_22h6d_activated": False,
        "vacation_mode_activated": False,
        "autonomous_trading_authorized": False,
        "money_movement_authorized": False,
        "broker_connection_authorized": False,
        "order_submission_authorized": False,
        "demo_account_marker": "DEMO_ONLY",
        "broker_environment": "DEMO_OR_PRACTICE_ONLY",
    }
    result = flow1.evaluate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown(owner_input)
    assert result["flow1_status"] in {
        "FLOW1_ACTIVE_GATE_READY_FOR_FLOW2_SUPERVISED_DEMO_EVIDENCE_CAPTURE",
        "FLOW1_BLOCKED_CONTINUE_GATES_MISSING",
    }


def test_artifacts_exist_and_no_banned_tokens():
    result = flow1.generate_artifacts()
    assert flow1.JSON_REPORT_PATH.exists()
    assert flow1.REPORT_PATH.exists()
    assert flow1.QUEUE_PATH.exists()
    assert flow1.HANDOFF_PATH.exists()
    report_text = flow1.REPORT_PATH.read_text(encoding="utf-8")
    queue_text = flow1.QUEUE_PATH.read_text(encoding="utf-8")
    handoff_text = flow1.HANDOFF_PATH.read_text(encoding="utf-8")
    for token in flow1.BANNED_OUTPUT_TOKENS:
        assert token.lower() not in report_text.lower()
        assert token.lower() not in queue_text.lower()
        assert token.lower() not in handoff_text.lower()


def test_validator_publish_handoff_files_exist():
    assert Path("scripts/forex_delivery/validate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown_v2.ps1").exists()
    assert Path("scripts/forex_delivery/publish_forex_flow1_active_execution_authority_runtime_sos_profit_countdown_v2.ps1").exists()
    assert Path("Reports/forex_delivery/AIOS_FOREX_FLOW1_TO_FLOW2_ACTIVE_SUPERVISED_DEMO_EVIDENCE_HANDOFF_V2.md").exists()
