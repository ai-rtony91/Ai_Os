from pathlib import Path

from automation.forex_engine.forex_continuous_bridge_to_profit_controller_v1 import (
    BANNED_OUTPUT_TOKENS,
    JSON_REPORT_PATH,
    REPORT_PATH,
    QUEUE_PATH,
    evaluate_forex_continuous_bridge_to_profit_controller,
    generate_artifacts,
    render_owner_report,
    render_next_action_queue,
)


def _valid_continue_input() -> dict:
    return {
        "controller_action": "CONTINUE",
        "baseline_equity": 1000.0,
        "current_equity": 1250.0,
        "closed_trade_count": 0,
        "open_trade_count": 0,
        "max_open_positions": 2,
        "current_drawdown_percent": 0.0,
        "daily_realized_loss_percent": 0.0,
        "weekly_realized_loss_percent": 0.0,
        "kill_switch_state": False,
        "owner_attestation": True,
        "demo_account_marker": "DEMO-ACCOUNT",
        "broker_environment": "DEMO",
        "runtime_objective_acknowledged": True,
        "target_return_band_acknowledged": True,
        "profit_countdown_acknowledged": True,
        "live_profitable_week_target_acknowledged": True,
        "vacation_mode_target_acknowledged": True,
        "sos_alerts_acknowledged": True,
    }


def test_default_owner_input_blocked() -> None:
    result = evaluate_forex_continuous_bridge_to_profit_controller()
    assert result["controller_status"] == (
        "FOREX_CONTINUOUS_CONTROLLER_BLOCKED_OWNER_INPUT_REQUIRED"
    )
    assert result["controller_mode"] == "PAUSE_READY"
    assert result["owner_live_capital_intent_usd"] == 1000
    assert result["hardcoded_10000_baseline_forbidden"] is True
    assert result["target_return_band"] == "100_TO_120_PERCENT"
    assert result["target_return_claim_status"] == "TARGET_NOT_YET_VERIFIED"
    assert result["profit_return_rate_status"] == "COUNTDOWN_NOT_ACTIVE_BASELINE_REQUIRED"
    assert result["runtime_objective"] == "22_HOURS_PER_DAY_6_DAYS_PER_WEEK"
    assert result["runtime_status"] == "NOT_ACTIVATED_PENDING_SUPERVISOR_GATE"
    assert result["vacation_mode_status"] == "TARGET_DEFINED_NOT_ACTIVE"
    assert result["sos_alert_integration_status"] == "REQUIRED_NOT_ACTIVE"


def test_continue_input_activates_countdown_and_flow_1() -> None:
    result = evaluate_forex_continuous_bridge_to_profit_controller(_valid_continue_input())
    assert result["controller_mode"] == "CONTINUE_READY"
    assert result["profit_return_countdown_status"] == "COUNTDOWN_ACTIVE"
    assert result["profit_return_rate_status"] == "COUNTDOWN_ACTIVE"
    assert result["execution_status"] == "FLOW_1_READY"
    assert result["next_required_flow"] == (
        "FLOW_1_EXECUTION_AUTHORITY_TARGET_COUNTDOWN_RUNTIME_SOS_GATE"
    )


def test_pause_action_sets_paused_mode() -> None:
    result = evaluate_forex_continuous_bridge_to_profit_controller({"controller_action": "PAUSE"})
    assert result["controller_mode"] == "PAUSED"


def test_stop_action_sets_stopped_mode() -> None:
    result = evaluate_forex_continuous_bridge_to_profit_controller({"controller_action": "STOP"})
    assert result["controller_mode"] == "STOPPED"


def test_bridge_action_populates_missing_islands() -> None:
    result = evaluate_forex_continuous_bridge_to_profit_controller({"controller_action": "BRIDGE"})
    assert result["controller_mode"] == "BRIDGE_BUILDING"
    assert len(result["missing_island_bridge_map"]) == 11
    required_islands = [
        "baseline_equity_bridge",
        "broker_snapshot_bridge",
        "credential_gate_bridge",
        "supervised_demo_execution_bridge",
        "post_trade_evidence_bridge",
        "profit_countdown_update_bridge",
        "sos_alert_bridge",
        "runtime_supervisor_22h6d_bridge",
        "vacation_mode_activation_bridge",
        "live_profitable_week_bridge",
        "publish_clean_merge_bridge",
    ]
    observed = sorted(
        item["island_name"] for item in result["missing_island_bridge_map"]
    )
    assert observed == sorted(required_islands)


def test_target_return_math_for_1000_to_1250() -> None:
    result = evaluate_forex_continuous_bridge_to_profit_controller(_valid_continue_input())
    assert result["cumulative_return_percent"] == 25.0
    assert result["target_equity_100_percent"] == 2000.0
    assert result["target_equity_120_percent"] == 2200.0
    assert result["remaining_to_100_percent"] == 75.0
    assert result["remaining_to_120_percent"] == 95.0
    assert result["milestone_alert"] == "TARGET_25_PROGRESS_ALERT"


def test_target_100_and_120_reached() -> None:
    data = _valid_continue_input()
    data["current_equity"] = 2000.0
    assert evaluate_forex_continuous_bridge_to_profit_controller(data)["target_100_reached"] is True

    data = _valid_continue_input()
    data["current_equity"] = 2200.0
    assert evaluate_forex_continuous_bridge_to_profit_controller(data)["target_120_reached"] is True


def test_drawdown_alert_levels() -> None:
    data = _valid_continue_input()
    data["current_drawdown_percent"] = 5
    assert (
        evaluate_forex_continuous_bridge_to_profit_controller(data)["drawdown_alert"]
        == "DRAWDOWN_WARNING_OWNER_REVIEW"
    )

    data = _valid_continue_input()
    data["current_drawdown_percent"] = 10
    assert (
        evaluate_forex_continuous_bridge_to_profit_controller(data)["drawdown_alert"]
        == "DRAWDOWN_CRITICAL_SOS_STOP_REVIEW"
    )


def test_compressed_flow_map_count() -> None:
    result = evaluate_forex_continuous_bridge_to_profit_controller(_valid_continue_input())
    assert len(result["compressed_flow_map"]) == 3
    assert (
        result["compressed_flow_map"][0]["flow_id"]
        == "FLOW_1_EXECUTION_AUTHORITY_TARGET_COUNTDOWN_RUNTIME_SOS_GATE"
    )


def test_forbidden_fields_fail() -> None:
    data = _valid_continue_input()
    data["account_identifier"] = "acct-1"
    result = evaluate_forex_continuous_bridge_to_profit_controller(data)
    assert result["controller_status"] == (
        "FOREX_CONTINUOUS_CONTROLLER_BLOCKED_FORBIDDEN_FIELD_PRESENT"
    )


def test_authorization_true_fields_fail() -> None:
    data = _valid_continue_input()
    data["broker_api_access_authorized"] = True
    result = evaluate_forex_continuous_bridge_to_profit_controller(data)
    assert result["controller_status"] == (
        "FOREX_CONTINUOUS_CONTROLLER_BLOCKED_UNSAFE_AUTHORIZATION_TRUE"
    )
    assert result["broker_api_access_authorized"] is True


def test_authorization_false_fields_pass() -> None:
    data = _valid_continue_input()
    data["broker_api_access_authorized"] = False
    data["credential_access_authorized"] = False
    data["demo_order_placement_authorized"] = False
    data["live_trading_authorized"] = False
    data["execution_command_authorized"] = False
    data["runtime_22h6d_activated"] = False
    data["vacation_mode_activated"] = False
    data["autonomous_trading_authorized"] = False
    data["money_movement_authorized"] = False
    result = evaluate_forex_continuous_bridge_to_profit_controller(data)
    assert result["broker_api_access_authorized"] is False
    assert result["credential_access_authorized"] is False
    assert result["demo_order_placement_authorized"] is False
    assert result["live_trading_authorized"] is False
    assert result["execution_command_authorized"] is False
    assert result["runtime_22h6d_activated"] is False
    assert result["vacation_mode_activated"] is False
    assert result["autonomous_trading_authorized"] is False
    assert result["money_movement_authorized"] is False
    assert result["controller_mode"] == "CONTINUE_READY"


def test_generate_artifacts_and_outputs() -> None:
    generate_artifacts()
    for path in (JSON_REPORT_PATH, REPORT_PATH, QUEUE_PATH):
        assert path.exists()

    for path in (JSON_REPORT_PATH, REPORT_PATH, QUEUE_PATH):
        text = Path(path).read_text(encoding="utf-8")
        for token in BANNED_OUTPUT_TOKENS:
            assert token not in text


def test_report_render_contains_required_sections() -> None:
    result = evaluate_forex_continuous_bridge_to_profit_controller(_valid_continue_input())
    report = render_owner_report(result)
    queue = render_next_action_queue(result)
    for required in [
        "# AIOS Forex Continuous Bridge To Profit Controller V1 Report",
        "## Real Forex End-State",
        "## Final Owner Sentence",
    ]:
        assert required in report
    for required in [
        "# AIOS Forex Continuous Bridge To Profit Controller Next Action Queue V1",
        "## Controller Status",
        "## Final Owner Sentence",
    ]:
        assert required in queue


def test_validator_and_publish_scripts_exist() -> None:
    assert Path(
        "scripts/forex_delivery/validate_forex_continuous_bridge_to_profit_controller_v1.ps1"
    ).exists()
    assert Path(
        "scripts/forex_delivery/publish_forex_continuous_bridge_to_profit_controller_v1.ps1"
    ).exists()
