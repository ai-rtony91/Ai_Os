from automation.forex_engine import final_live_operator_bridge_v1 as bridge
from automation.forex_engine import live_runtime_executor_v1
from automation.forex_engine import oanda_live_runtime_connector_v2


def ready_arm_request():
    return {
        "instrument": "EUR_USD",
        "side": "BUY",
        "units": 1000,
        "stop_loss": "1.0800",
        "take_profit": "1.0860",
        "authenticated_operator": True,
        "protected_action_authorized": True,
        "live_exception_requested": True,
        "understands_live_risk_ack": True,
        "allow_live_network_once": True,
        "credentials_runtime_only": True,
        "credentials_persisted": False,
        "account_id_persisted": False,
        "max_loss_gate_clear": True,
        "daily_stop_clear": True,
        "kill_switch_enabled": False,
        "single_order_only": True,
        "micro_size_only": True,
        "requested_order_count": 1,
        "max_order_count": 1,
        "existing_live_order_count": 0,
    }


def runtime_snapshot():
    return {
        "balance": 10000.0,
        "equity": 10000.0,
        "realized_pl": 0.0,
        "open_risk": 0.0,
        "active_trades": 0,
        "evidence_freshness": "fixture_current",
    }


def test_ready_bridge_builds_executor_and_oanda_plan_without_execution():
    result = bridge.build_final_live_runtime_execution_plan(
        ready_arm_request(),
        runtime_snapshot(),
        cleanup_candidates=[
            {"path": "apps/dashboard/mock-data/aios-live-operator-panel-v1.example.json", "fixture_data": True}
        ],
    )

    assert result["bridge_status"] == bridge.FINAL_LIVE_OPERATOR_BRIDGE_READY
    assert result["ready"] is True
    assert result["execute_requested"] is False
    assert result["order_executed"] is False
    assert result["broker_call_performed"] is False
    assert result["network_call_performed"] is False
    assert result["actual_credentials_supplied"] is False
    assert result["actual_transport_injected"] is False
    assert result["runtime_execution_request"]["request_status"] == live_runtime_executor_v1.LIVE_RUNTIME_REQUEST_READY
    assert result["oanda_connector_status"] == oanda_live_runtime_connector_v2.OANDA_LIVE_CONNECTOR_CONFIG_READY
    assert result["mobile_summary"]["dashboard_places_order"] is False
    assert result["cleanup_summary"]["categories"]["keep-active"] == (
        "apps/dashboard/mock-data/aios-live-operator-panel-v1.example.json",
    )


def test_state_includes_mobile_summary_and_stops_for_future_protected_action():
    result = bridge.build_final_live_operator_bridge_state(ready_arm_request(), runtime_snapshot())

    assert result["bridge_status"] == bridge.FINAL_LIVE_OPERATOR_BRIDGE_READY
    assert result["mobile_summary"]["live_bridge_status"] == bridge.FINAL_LIVE_OPERATOR_BRIDGE_READY
    assert result["mobile_summary"]["final_execution_requires_explicit_protected_live_action_authorization"] is True
    assert result["next_safe_action"] == "stop_and_wait_for_separate_human_protected_live_execution_command"
    assert result["safety_summary"]["order_executed"] is False


def test_review_required_when_human_live_authorization_is_missing():
    request = ready_arm_request()
    request["protected_action_authorized"] = False

    result = bridge.validate_final_live_operator_arm_request(request)

    assert result["bridge_status"] == bridge.FINAL_LIVE_OPERATOR_BRIDGE_REVIEW_REQUIRED
    assert "protected_live_action_authorization_required" in result["review_items"]
    assert result["next_safe_action"] == "obtain_explicit_human_protected_live_action_authorization"


def test_blocks_units_above_micro_size_policy():
    request = ready_arm_request()
    request["units"] = 1001

    result = bridge.validate_final_live_operator_arm_request(request)

    assert result["bridge_status"] == bridge.FINAL_LIVE_OPERATOR_BRIDGE_BLOCKED
    assert "units_above_micro_size_max" in result["blockers"]
    assert result["safety_summary"]["max_units"] == 1000


def test_invalid_when_sensitive_material_is_supplied():
    request = ready_arm_request()
    request["credentials"] = {"value": "not_allowed"}

    result = bridge.validate_final_live_operator_arm_request(request)

    assert result["bridge_status"] == bridge.FINAL_LIVE_OPERATOR_BRIDGE_INVALID
    assert "sensitive_field_detected" in result["invalid_fields"]
    assert "credentials" not in result["sanitized_arm_request"]


def test_mobile_payload_exposes_truth_fields_without_execution_controls():
    result = bridge.build_mobile_operator_panel_payload(
        arm_request=ready_arm_request(),
        runtime_snapshot=runtime_snapshot(),
    )

    expected_fields = {
        "mode",
        "live_bridge_status",
        "balance",
        "equity",
        "realized_pl",
        "open_risk",
        "active_trades",
        "instrument",
        "side",
        "units",
        "stop_loss",
        "take_profit",
        "max_loss_gate",
        "daily_stop_gate",
        "kill_switch",
        "broker_connector_status",
        "evidence_freshness",
        "blockers",
        "next_safe_action",
    }

    assert expected_fields.issubset(result.keys())
    assert result["dashboard_places_order"] is False
    assert result["final_execution_requires_explicit_protected_live_action_authorization"] is True
    assert result["credentials_present"] is False
    assert result["account_id_present"] is False


def test_cleanup_classifier_uses_only_supplied_files_and_required_categories():
    result = bridge.classify_scaffolding_cleanup_candidates(
        [
            "Reports/forex_delivery/AIOS_FOREX_CANDIDATE_INTAKE_DEMO.md",
            "apps/dashboard/mock-data/old-live-panel.example.json",
            {"path": "docs/forex_delivery/template-live-bridge.md"},
            {"path": "Reports/forex_delivery/duplicate-report.md", "duplicate_of": True},
            "@filename",
            {"path": "apps/dashboard/mock-data/aios-live-operator-panel-v1.example.json", "fixture_data": True},
        ]
    )

    assert result["delete_performed"] is False
    assert "Reports/forex_delivery/AIOS_FOREX_CANDIDATE_INTAKE_DEMO.md" in result["categories"]["demo-only residue"]
    assert "apps/dashboard/mock-data/old-live-panel.example.json" in result["categories"][
        "mock-data that needs fixture labeling"
    ]
    assert "docs/forex_delivery/template-live-bridge.md" in result["categories"]["stale scaffold"]
    assert "Reports/forex_delivery/duplicate-report.md" in result["categories"]["duplicate report"]
    assert "@filename" in result["categories"]["blocked placeholder"]
    assert "apps/dashboard/mock-data/aios-live-operator-panel-v1.example.json" in result["categories"]["keep-active"]

