from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.oanda_demo_supervised_order_execution_v1 import (  # noqa: E402
    SCHEMA,
    execute_oanda_demo_supervised_order_v1,
)


MODULE_PATH = ROOT / "automation" / "forex_engine" / "oanda_demo_supervised_order_execution_v1.py"
FORBIDDEN_SOURCE_MARKERS = (
    "requests",
    "socket",
    "urllib",
    "subprocess",
    "os.environ",
    "broker_sdk",
    "schedule.every",
    "start-process",
)
HARD_FALSE_FIELDS = (
    "direct_broker_api_allowed",
    "live_trading_allowed",
    "real_money_allowed",
    "money_movement_allowed",
    "bank_access_allowed",
    "credential_storage_allowed",
    "credential_read_allowed",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "dashboard_runtime_created",
    "live_execution_allowed",
)


def execute(payload: dict | None = None, adapter: object | None = None) -> dict:
    return execute_oanda_demo_supervised_order_v1(payload, adapter)


def strong_payload() -> dict:
    return {
        "owner_name": "Anthony",
        "as_of_date": "2026-06-30",
        "execution_mode": "DEMO_PRACTICE",
        "runtime_handoff_package": {
            "handoff_status": "OANDA_DEMO_RUNTIME_HANDOFF_READY",
            "runtime_handoff_ready": True,
            "supervised_demo_execution_authorized": False,
            "next_best_packet": "AIOS_FOREX_OANDA_DEMO_SUPERVISED_ORDER_EXECUTION_V1",
            "handoff_blockers": [],
        },
        "owner_approval": {
            "owner_name": "Anthony",
            "execution_mode": "DEMO_PRACTICE",
            "owner_final_approval_for_demo_execution": True,
            "owner_accepts_order_preview": True,
            "owner_accepts_demo_only_boundary": True,
            "owner_accepts_risk_limits": True,
            "owner_accepts_one_order_only": True,
            "owner_can_cancel": True,
            "execution_allowed": True,
            "live_execution_allowed": False,
        },
        "oanda_demo_boundary": {
            "broker_name": "OANDA",
            "broker_mode": "OANDA_DEMO",
            "account_environment": "PRACTICE",
            "demo_account_only": True,
            "live_account_allowed": False,
            "real_money_allowed": False,
            "money_movement_allowed": False,
            "bank_access_allowed": False,
            "broker_api_allowed": False,
            "credential_use_allowed": False,
            "order_placement_allowed": True,
            "live_execution_allowed": False,
        },
        "order_preview": {
            "strategy_id": "edge-reversion-v1",
            "candidate_id": "demo-candidate-001",
            "instrument": "EUR_USD",
            "side": "BUY",
            "order_type": "MARKET",
            "units": 100,
            "max_position_units": 1000,
            "stop_loss_present": True,
            "take_profit_present": True,
            "max_spread_pips": 2.0,
            "max_slippage_pips": 0.5,
            "order_preview_accepted_by_owner": True,
            "order_preview_blocks": [],
            "raw_note": "this raw note must not reach the adapter",
        },
        "risk_gates": {
            "max_loss_gate_present": True,
            "daily_loss_stop_present": True,
            "kill_switch_present": True,
            "kill_switch_active": False,
            "position_size_limit_present": True,
            "max_risk_per_trade_pct": 0.01,
            "max_daily_loss_pct": 0.03,
            "one_order_only": True,
            "risk_gate_blocks": [],
        },
        "abort_conditions": {
            "abort_if_owner_approval_missing": True,
            "abort_if_credentials_missing": True,
            "abort_if_broker_mode_not_demo": True,
            "abort_if_spread_above_max": True,
            "abort_if_slippage_above_max": True,
            "abort_if_stop_loss_missing": True,
            "abort_if_take_profit_missing": True,
            "abort_if_daily_loss_hit": True,
            "abort_if_kill_switch_active": True,
            "abort_if_duplicate_order_detected": True,
            "abort_if_wrong_account_detected": True,
            "abort_if_live_account_detected": True,
            "abort_condition_blocks": [],
        },
        "telemetry": {
            "audit_log_required": True,
            "sanitized_ticket_required": True,
            "pre_trade_snapshot_required": True,
            "order_preview_snapshot_required": True,
            "post_trade_snapshot_required": True,
            "exception_capture_required": True,
            "owner_review_report_required": True,
            "execution_result_required": True,
            "telemetry_blocks": [],
        },
        "post_trade_review": {
            "post_trade_review_required": True,
            "pnl_review_required": True,
            "risk_review_required": True,
            "execution_quality_review_required": True,
            "next_trade_blocked_until_review": True,
            "post_trade_review_blocks": [],
        },
        "data_quality": {
            "data_quality_blocks": [],
            "missing_fields": [],
            "malformed_fields": [],
        },
    }


class FakeAdapter:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def submit_demo_order(self, order_request: dict) -> dict:
        self.calls.append(order_request)
        return {
            "adapter_status": "FAKE_DEMO_ACCEPTED",
            "ticket_id": "FAKE-TICKET-001",
            "credentials_included": False,
        }


class InvalidAdapter:
    def preview(self, order_request: dict) -> dict:
        return {"unexpected": order_request}


def assert_hard_false_safety(result: dict) -> None:
    assert result["schema"] == SCHEMA
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False
    for field in [
        "direct_broker_api_allowed",
        "live_trading_allowed",
        "real_money_allowed",
        "money_movement_allowed",
        "bank_access_allowed",
        "credential_storage_allowed",
        "credential_read_allowed",
        "scheduler_allowed",
        "daemon_allowed",
        "webhook_allowed",
        "dashboard_runtime_allowed",
        "fixed_return_target_promised",
        "profit_claim_authorized",
    ]:
        assert result["safety"][field] is False
    assert result["safety"]["owner_gate_required"] is True
    assert result["safety"]["demo_only"] is True


def test_all_hard_false_safety_fields_remain_false() -> None:
    assert_hard_false_safety(execute(strong_payload()))


def test_empty_payload_returns_incomplete_inputs() -> None:
    result = execute({})
    assert result["execution_status"] == "INCOMPLETE_INPUTS"
    assert result["supervised_demo_execution_attempted"] is False
    assert result["supervised_demo_execution_allowed"] is False
    for missing in [
        "runtime_handoff_package",
        "owner_approval",
        "oanda_demo_boundary",
        "order_preview",
        "risk_gates",
        "abort_conditions",
        "telemetry",
        "post_trade_review",
    ]:
        assert missing in result["missing_information"]


def test_sensitive_payload_is_blocked_and_not_echoed() -> None:
    payload = strong_payload()
    payload["api_key"] = "very-sensitive-value"
    result = execute(payload)
    assert result["execution_status"] == "BLOCKED_BY_DATA_QUALITY"
    assert result["supervised_demo_execution_attempted"] is False
    assert result["supervised_demo_execution_allowed"] is False
    assert "sensitive_data_provided" in result["execution_blockers"]
    assert "very-sensitive-value" not in repr(result)


def test_safety_boolean_keys_are_not_misclassified_as_sensitive() -> None:
    payload = strong_payload()
    payload["credential_use_allowed"] = False
    payload["broker_api_allowed"] = False
    payload["demo_execution_allowed"] = True
    payload["order_placement_allowed"] = True
    payload["live_execution_allowed"] = False
    result = execute(payload)
    assert result["execution_status"] == "READY_FOR_OWNER_SUPERVISED_DEMO_EXECUTION"
    assert "sensitive_data_provided" not in result["execution_blockers"]


def test_weak_runtime_handoff_returns_blocked_by_runtime_handoff() -> None:
    payload = strong_payload()
    payload["runtime_handoff_package"]["runtime_handoff_ready"] = False
    result = execute(payload)
    assert result["execution_status"] == "BLOCKED_BY_RUNTIME_HANDOFF"
    assert "runtime_handoff_ready_false" in result["execution_blockers"]


def test_weak_owner_approval_returns_blocked_by_owner_approval() -> None:
    payload = strong_payload()
    payload["owner_approval"]["owner_accepts_risk_limits"] = False
    result = execute(payload)
    assert result["execution_status"] == "BLOCKED_BY_OWNER_APPROVAL"
    assert "owner_accepts_risk_limits_false" in result["execution_blockers"]


def test_weak_oanda_demo_boundary_returns_blocked_by_oanda_demo_boundary() -> None:
    payload = strong_payload()
    payload["oanda_demo_boundary"]["broker_mode"] = "LIVE"
    result = execute(payload)
    assert result["execution_status"] == "BLOCKED_BY_OANDA_DEMO_BOUNDARY"
    assert "broker_mode_not_demo" in result["execution_blockers"]


def test_weak_order_preview_returns_blocked_by_order_preview() -> None:
    payload = strong_payload()
    payload["order_preview"]["side"] = "WAIT"
    result = execute(payload)
    assert result["execution_status"] == "BLOCKED_BY_ORDER_PREVIEW"
    assert "side_not_supported" in result["execution_blockers"]


def test_weak_risk_gates_returns_blocked_by_risk_gates() -> None:
    payload = strong_payload()
    payload["risk_gates"]["max_risk_per_trade_pct"] = 0.02
    result = execute(payload)
    assert result["execution_status"] == "BLOCKED_BY_RISK_GATES"
    assert "max_risk_per_trade_pct_above_limit" in result["execution_blockers"]


def test_weak_abort_conditions_returns_blocked_by_abort_conditions() -> None:
    payload = strong_payload()
    payload["abort_conditions"]["abort_if_live_account_detected"] = False
    result = execute(payload)
    assert result["execution_status"] == "BLOCKED_BY_ABORT_CONDITIONS"
    assert "abort_if_live_account_detected_false" in result["execution_blockers"]


def test_weak_telemetry_returns_blocked_by_telemetry() -> None:
    payload = strong_payload()
    payload["telemetry"]["audit_log_required"] = False
    result = execute(payload)
    assert result["execution_status"] == "BLOCKED_BY_TELEMETRY"
    assert "audit_log_required_false" in result["execution_blockers"]


def test_weak_post_trade_review_returns_blocked_by_post_trade_review() -> None:
    payload = strong_payload()
    payload["post_trade_review"]["next_trade_blocked_until_review"] = False
    result = execute(payload)
    assert result["execution_status"] == "BLOCKED_BY_POST_TRADE_REVIEW"
    assert "next_trade_blocked_until_review_false" in result["execution_blockers"]


def test_strong_payload_with_no_adapter_returns_ready_for_owner_supervised_demo_execution() -> None:
    result = execute(strong_payload())
    assert result["execution_status"] == "READY_FOR_OWNER_SUPERVISED_DEMO_EXECUTION"
    assert result["supervised_demo_execution_allowed"] is True
    assert result["next_best_packet"] == "AIOS_FOREX_OANDA_DEMO_BROKER_ADAPTER_RUNTIME_BINDING_V1"


def test_strong_payload_with_no_adapter_does_not_attempt_execution() -> None:
    result = execute(strong_payload())
    assert result["supervised_demo_execution_attempted"] is False
    assert result["execution_result"] is None
    assert result["adapter_summary"]["adapter_supplied"] is False


def test_strong_payload_with_fake_adapter_calls_fake_adapter_exactly_once() -> None:
    adapter = FakeAdapter()
    result = execute(strong_payload(), adapter)
    assert len(adapter.calls) == 1
    assert result["adapter_summary"]["adapter_called"] is True


def test_fake_adapter_receives_sanitized_order_request_only() -> None:
    adapter = FakeAdapter()
    result = execute(strong_payload(), adapter)
    order_request = adapter.calls[0]
    assert order_request == result["sanitized_order_request"]
    assert set(order_request) == set(result["sanitized_order_request"])
    assert "raw_note" not in repr(order_request)
    assert order_request["credentials_included"] is False
    assert order_request["live_execution_allowed"] is False


def test_fake_adapter_result_is_captured() -> None:
    adapter = FakeAdapter()
    result = execute(strong_payload(), adapter)
    assert result["execution_result"] == {
        "adapter_status": "FAKE_DEMO_ACCEPTED",
        "ticket_id": "FAKE-TICKET-001",
        "credentials_included": False,
    }


def test_strong_payload_with_fake_adapter_returns_executed_status() -> None:
    result = execute(strong_payload(), FakeAdapter())
    assert result["execution_status"] == "DEMO_ORDER_EXECUTED_WITH_INJECTED_ADAPTER"
    assert result["supervised_demo_execution_attempted"] is True
    assert result["supervised_demo_execution_allowed"] is True
    assert result["next_best_packet"] == "AIOS_FOREX_OANDA_DEMO_POST_EXECUTION_REVIEW_V1"


def test_invalid_adapter_contract_returns_blocked_by_adapter_contract() -> None:
    result = execute(strong_payload(), InvalidAdapter())
    assert result["execution_status"] == "BLOCKED_BY_ADAPTER_CONTRACT"
    assert result["supervised_demo_execution_attempted"] is False
    assert "adapter_submit_method_missing" in result["execution_blockers"]


def test_live_execution_allowed_always_false() -> None:
    for result in [
        execute({}),
        execute(strong_payload()),
        execute(strong_payload(), FakeAdapter()),
        execute(strong_payload(), InvalidAdapter()),
    ]:
        assert result["live_execution_allowed"] is False
        assert result["safety"]["live_trading_allowed"] is False


def test_direct_broker_api_allowed_always_false() -> None:
    for result in [
        execute({}),
        execute(strong_payload()),
        execute(strong_payload(), FakeAdapter()),
        execute(strong_payload(), InvalidAdapter()),
    ]:
        assert result["direct_broker_api_allowed"] is False
        assert result["safety"]["direct_broker_api_allowed"] is False


def test_credentials_are_never_included_in_sanitized_request() -> None:
    result = execute(strong_payload(), FakeAdapter())
    assert result["sanitized_order_request"]["credentials_included"] is False
    assert "password" not in repr(result["sanitized_order_request"]).lower()
    assert "api_key" not in repr(result["sanitized_order_request"]).lower()


def test_owner_action_queue_contains_review_next_packet() -> None:
    result = execute(strong_payload())
    action_ids = {action["action_id"] for action in result["owner_action_queue"]}
    assert "REVIEW_NEXT_PACKET" in action_ids
    assert all(action["owner_decision_required"] is True for action in result["owner_action_queue"])
    assert all(action["live_execution_allowed"] is False for action in result["owner_action_queue"])


def test_source_contains_no_forbidden_runtime_imports_or_launchers() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for marker in FORBIDDEN_SOURCE_MARKERS:
        assert marker not in source
