from pathlib import Path
import importlib.util
import json
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from automation.forex_engine.oanda_demo_auth_handoff import (  # noqa: E402
    build_example_sanitized_demo_auth_handoff,
)
from automation.forex_engine.oanda_demo_connection_gate import (  # noqa: E402
    build_example_oanda_demo_connection_gate_approval,
)
from automation.forex_engine.oanda_demo_protected_connection_attempt import (  # noqa: E402
    build_example_oanda_demo_protected_connection_attempt_request,
)
from automation.forex_engine.oanda_demo_runtime_handoff_intake import (  # noqa: E402
    build_example_oanda_demo_runtime_handoff_intake,
)
from automation.forex_engine.oanda_demo_runtime_handoff import (  # noqa: E402
    build_example_oanda_demo_runtime_handoff,
)
from forex_delivery.governed_readiness import (  # noqa: E402
    LiveExecutionBlocked,
    build_demo_connection_proof_preflight_dry_run,
    build_demo_runtime_readiness_dry_run,
    build_live_arming_checklist,
    build_order_payload,
    run_governed_paper_flow,
    submit_live_order,
    validate_order_request,
)


def _base_live_exception_fields():
    return {
        "broker_path": "external-operator-controlled-oanda-practice-reference",
        "instrument": "EUR_USD",
        "side": "BUY",
        "units_or_notional_limit": 1,
        "maximum_loss": 1.0,
        "daily_loss_cap": 2.0,
        "stop_loss": 1.075,
        "order_type": "MARKET",
        "approval_window": "2026-06-17T00:00:00Z/2026-06-17T00:05:00Z",
        "evidence_bundle_path": "Reports/forex_delivery/sanitized-evidence-bundle.md",
        "arming_step": "manual-human-owner-arm",
        "stop_point": "stop-after-fill-rejection-error-timeout-expiry-or-manual-kill",
        "human_owner_approval": "Anthony Meza",
        "timestamp": "2026-06-17T00:00:00Z",
        "account_mode": "LIVE",
        "paper_live_mode_confirmation": "LIVE",
    }


def _complete_sanitized_live_review_package():
    fields = _base_live_exception_fields()
    fields.update(
        {
            "one_order_only": True,
            "no_retry_loop": True,
            "no_autonomous_reentry": True,
            "kill_switch_confirmed": True,
            "timeout_confirmed": True,
            "final_disarm_confirmed": True,
            "rollback_plan_confirmed": True,
            "post_trade_journal_path": "Reports/forex_delivery/sanitized-terminal-journal.md",
            "reconciliation_proof": True,
            "evidence_bundle_complete": True,
            "demo_or_practice_broker_proof": True,
            "credential_boundary_confirmed": True,
            "account_id_boundary_confirmed": True,
            "live_endpoint_denial_confirmed": True,
        }
    )
    return fields


def _complete_demo_runtime_dry_run_fields():
    return {
        "broker_family_label": "OANDA_PRACTICE",
        "practice_demo_mode_confirmed": True,
        "runtime_auth_reference_label": "SANITIZED_REFERENCE_ONLY",
        "external_connector_readiness_flag": True,
        "network_approval_status": False,
        "account_identifier_status": "ABSENT",
        "endpoint_class": "OANDA_PRACTICE_DEMO",
        "no_order_route_approval": True,
        "no_live_endpoint": True,
        "no_credential_value": True,
        "no_account_id_value": True,
        "timeout_seconds": 10,
        "one_shot_stop_requirement": True,
        "evidence_bundle_path": "Reports/forex_delivery/sanitized-demo-runtime-proof.md",
        "human_owner_approval_future_proof": "Anthony Meza",
    }


def _complete_demo_connection_preflight_dry_run_fields():
    return {
        "broker_family_label": "OANDA_PRACTICE",
        "demo_practice_mode_confirmed": True,
        "runtime_auth_reference_label": "SANITIZED_REFERENCE_ONLY",
        "external_connector_readiness_flag": True,
        "protected_action_approval_status": False,
        "network_approval_status": False,
        "endpoint_class": "OANDA_PRACTICE_DEMO",
        "account_identifier_status": "ABSENT",
        "credential_material_status": "ABSENT",
        "order_route_approval": False,
        "market_data_fetch_approval": False,
        "timeout_seconds": 10,
        "one_shot_stop_requirement": True,
        "retry_count": 0,
        "scheduler_enabled": False,
        "daemon_enabled": False,
        "webhook_enabled": False,
        "evidence_bundle_path": "Reports/forex_delivery/sanitized-demo-connection-preflight.md",
        "human_owner_approval_future_proof": "Anthony Meza",
    }


def test_missing_external_broker_path_fails_safely():
    checklist = build_live_arming_checklist(
        {
            "instrument": "EUR_USD",
            "side": "buy",
            "units_or_notional_limit": 1,
            "maximum_loss": 1.0,
            "daily_loss_cap": 2.0,
            "stop_loss": 1.0,
            "order_type": "market",
            "approval_window": "active-window-record",
            "evidence_bundle_path": "Reports/forex_delivery/AIOS_FOREX_DELIVERY_GOVERNED_APPLY_V2_REPORT.md",
            "arming_step": "manual-human-owner-arm",
            "stop_point": "hard-stop-before-live-submit",
            "human_owner_approval": "Anthony Meza",
            "timestamp": "2026-06-17T00:00:00Z",
            "account_mode": "LIVE",
            "paper_live_mode_confirmation": "LIVE",
        }
    )

    assert checklist["ready_for_human_review"] is False
    assert checklist["live_execution_allowed"] is False
    assert "broker_path" in checklist["missing_fields"]


def test_paper_mode_cannot_hit_live_endpoint():
    result = run_governed_paper_flow()

    assert result["mode"] == "PAPER_ONLY"
    assert result["broker_adapter"]["adapter_name"] == "AIOS_PAPER_DEMO_BROKER_ADAPTER"
    assert result["broker_adapter"]["paper_demo_only"] is True
    assert result["broker_connect"]["broker_connection_allowed"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["live_order_placed"] is False


def test_live_mode_refuses_without_exact_approval_fields():
    checklist = build_live_arming_checklist({})

    assert checklist["ready_for_human_review"] is False
    assert checklist["live_execution_allowed"] is False
    assert checklist["order_submit_allowed"] is False
    assert checklist["broker_request_sent"] is False
    assert checklist["network_used"] is False
    assert checklist["passed_gates"] == ["no_forbidden_live_fields"]
    assert "required_exception_fields_present" in checklist["failed_gates"]
    assert len(checklist["missing_fields"]) >= 16
    with pytest.raises(LiveExecutionBlocked):
        submit_live_order({})


def test_existing_required_fields_alone_are_not_review_ready():
    checklist = build_live_arming_checklist(_base_live_exception_fields())

    assert checklist["ready_for_human_review"] is False
    assert checklist["live_execution_allowed"] is False
    assert "kill_switch_confirmed" in checklist["missing_fields"]
    assert "final_disarm_confirmed" in checklist["missing_fields"]
    assert "evidence_bundle_complete" in checklist["missing_fields"]
    assert "kill_switch_confirmed" in checklist["failed_gates"]
    assert checklist["next_required_action"] == "complete_sanitized_live_arming_review_package"


def test_missing_human_owner_approval_fails_closed():
    fields = _complete_sanitized_live_review_package()
    fields.pop("human_owner_approval")

    checklist = build_live_arming_checklist(fields)

    assert checklist["ready_for_human_review"] is False
    assert checklist["live_execution_allowed"] is False
    assert checklist["order_submit_allowed"] is False
    assert checklist["broker_request_sent"] is False
    assert checklist["network_used"] is False
    assert "human_owner_approval" in checklist["missing_fields"]
    assert "human_owner_approval" in checklist["failed_gates"]


def test_demo_runtime_missing_runtime_auth_reference_fails_closed():
    fields = _complete_demo_runtime_dry_run_fields()
    fields.pop("runtime_auth_reference_label")

    readiness = build_demo_runtime_readiness_dry_run(fields)

    assert readiness["demo_runtime_ready"] is False
    assert readiness["broker_request_sent"] is False
    assert readiness["network_used"] is False
    assert readiness["order_placed"] is False
    assert "runtime_auth_reference_label" in readiness["missing_fields"]
    assert "runtime_auth_reference_label" in readiness["failed_gates"]


def test_demo_runtime_credential_like_values_fail_closed():
    fields = _complete_demo_runtime_dry_run_fields()
    fields["runtime_auth_reference_label"] = "token=not-a-real-value"

    readiness = build_demo_runtime_readiness_dry_run(fields)

    assert readiness["demo_runtime_ready"] is False
    assert readiness["broker_request_sent"] is False
    assert readiness["network_used"] is False
    assert "no_forbidden_demo_runtime_fields" in readiness["failed_gates"]
    assert "forbidden_field:runtime_auth_reference_label" in readiness["blocker_reasons"]


def test_demo_runtime_account_id_like_values_fail_closed():
    fields = _complete_demo_runtime_dry_run_fields()
    fields["runtime_auth_reference_label"] = "123-456-789"

    readiness = build_demo_runtime_readiness_dry_run(fields)

    assert readiness["demo_runtime_ready"] is False
    assert readiness["account_access_allowed"] is False
    assert readiness["order_placed"] is False
    assert "forbidden_field:runtime_auth_reference_label" in readiness["blocker_reasons"]


def test_demo_runtime_live_endpoint_references_fail_closed():
    fields = _complete_demo_runtime_dry_run_fields()
    fields["endpoint_class"] = "OANDA_LIVE"

    readiness = build_demo_runtime_readiness_dry_run(fields)

    assert readiness["demo_runtime_ready"] is False
    assert readiness["live_endpoint_allowed"] is False
    assert "endpoint_class" in readiness["failed_gates"]
    assert "endpoint_class_must_be_demo_or_practice_only" in readiness["blocker_reasons"]


def test_demo_runtime_order_route_approval_attempts_fail_closed():
    fields = _complete_demo_runtime_dry_run_fields()
    fields["order_route_approval"] = True

    readiness = build_demo_runtime_readiness_dry_run(fields)

    assert readiness["demo_runtime_ready"] is False
    assert readiness["order_route_allowed"] is False
    assert readiness["order_placed"] is False
    assert "order_route_approval" in readiness["failed_gates"]
    assert "order_route_approval_attempt_blocked" in readiness["blocker_reasons"]


def test_complete_sanitized_demo_runtime_fixture_passes_dry_run_readiness_only():
    readiness = build_demo_runtime_readiness_dry_run(
        _complete_demo_runtime_dry_run_fields()
    )

    assert readiness["demo_runtime_ready"] is True
    assert readiness["future_broker_demo_proof_review_ready"] is True
    assert readiness["dry_run_only"] is True
    assert readiness["broker_connection_allowed"] is False
    assert readiness["connection_attempt_performed"] is False
    assert readiness["broker_request_sent"] is False
    assert readiness["network_used"] is False
    assert readiness["order_submit_allowed"] is False
    assert readiness["order_placed"] is False
    assert readiness["live_execution_allowed"] is False
    assert readiness["credential_material_present"] is False
    assert readiness["runtime_handoff"]["runtime_handoff_ready"] is True


def test_demo_connection_preflight_missing_protected_action_approval_fails_closed():
    fields = _complete_demo_connection_preflight_dry_run_fields()
    fields.pop("protected_action_approval_status")

    preflight = build_demo_connection_proof_preflight_dry_run(fields)

    assert preflight["demo_connection_preflight_ready"] is False
    assert preflight["proof_executable_now"] is False
    assert preflight["connection_attempt_performed"] is False
    assert "protected_action_approval_status" in preflight["missing_fields"]
    assert "protected_action_approval_status" in preflight["failed_gates"]


def test_demo_connection_preflight_missing_runtime_auth_reference_fails_closed():
    fields = _complete_demo_connection_preflight_dry_run_fields()
    fields.pop("runtime_auth_reference_label")

    preflight = build_demo_connection_proof_preflight_dry_run(fields)

    assert preflight["demo_connection_preflight_ready"] is False
    assert preflight["broker_request_sent"] is False
    assert preflight["network_used"] is False
    assert "runtime_auth_reference_label" in preflight["missing_fields"]
    assert "runtime_auth_reference_label" in preflight["failed_gates"]


def test_demo_connection_preflight_credential_like_values_fail_closed():
    fields = _complete_demo_connection_preflight_dry_run_fields()
    fields["runtime_auth_reference_label"] = "token=not-a-real-value"

    preflight = build_demo_connection_proof_preflight_dry_run(fields)

    assert preflight["demo_connection_preflight_ready"] is False
    assert preflight["credentials_used"] is False
    assert preflight["credential_material_present"] is False
    assert "no_forbidden_demo_connection_preflight_fields" in preflight["failed_gates"]
    assert "forbidden_field:runtime_auth_reference_label" in preflight["blocker_reasons"]


def test_demo_connection_preflight_account_id_like_values_fail_closed():
    fields = _complete_demo_connection_preflight_dry_run_fields()
    fields["runtime_auth_reference_label"] = "123-456-789"

    preflight = build_demo_connection_proof_preflight_dry_run(fields)

    assert preflight["demo_connection_preflight_ready"] is False
    assert preflight["account_access_allowed"] is False
    assert preflight["order_placed"] is False
    assert "forbidden_field:runtime_auth_reference_label" in preflight["blocker_reasons"]


def test_demo_connection_preflight_live_endpoint_references_fail_closed():
    fields = _complete_demo_connection_preflight_dry_run_fields()
    fields["endpoint_class"] = "OANDA_LIVE"

    preflight = build_demo_connection_proof_preflight_dry_run(fields)

    assert preflight["demo_connection_preflight_ready"] is False
    assert preflight["live_endpoint_allowed"] is False
    assert "endpoint_class" in preflight["failed_gates"]
    assert "endpoint_class_must_be_demo_or_practice_only" in preflight["blocker_reasons"]


def test_demo_connection_preflight_network_approval_false_keeps_proof_non_executable():
    preflight = build_demo_connection_proof_preflight_dry_run(
        _complete_demo_connection_preflight_dry_run_fields()
    )

    assert preflight["demo_connection_preflight_ready"] is True
    assert preflight["protected_action_approval_status"] is False
    assert preflight["network_approval_status"] is False
    assert preflight["proof_executable_now"] is False
    assert preflight["network_allowed"] is False
    assert preflight["network_used"] is False
    assert preflight["connection_attempt_performed"] is False


def test_demo_connection_preflight_order_route_approval_attempts_fail_closed():
    fields = _complete_demo_connection_preflight_dry_run_fields()
    fields["order_route_approval"] = True

    preflight = build_demo_connection_proof_preflight_dry_run(fields)

    assert preflight["demo_connection_preflight_ready"] is False
    assert preflight["order_route_allowed"] is False
    assert preflight["order_placed"] is False
    assert "order_route_approval" in preflight["failed_gates"]
    assert "order_route_approval_must_remain_false" in preflight["blocker_reasons"]


def test_demo_connection_preflight_market_data_fetch_approval_attempts_fail_closed():
    fields = _complete_demo_connection_preflight_dry_run_fields()
    fields["market_data_fetch_approval"] = True

    preflight = build_demo_connection_proof_preflight_dry_run(fields)

    assert preflight["demo_connection_preflight_ready"] is False
    assert preflight["market_data_allowed"] is False
    assert preflight["market_data_fetched"] is False
    assert "market_data_fetch_approval" in preflight["failed_gates"]
    assert "market_data_fetch_approval_must_remain_false" in preflight["blocker_reasons"]


def test_demo_connection_preflight_retry_count_above_zero_fails_closed():
    fields = _complete_demo_connection_preflight_dry_run_fields()
    fields["retry_count"] = 1

    preflight = build_demo_connection_proof_preflight_dry_run(fields)

    assert preflight["demo_connection_preflight_ready"] is False
    assert preflight["retry_loop_present"] is False
    assert "retry_count" in preflight["failed_gates"]
    assert "retry_count_must_be_zero" in preflight["blocker_reasons"]


@pytest.mark.parametrize("flag_name", ["scheduler_enabled", "daemon_enabled", "webhook_enabled"])
def test_demo_connection_preflight_scheduler_daemon_webhook_flags_fail_closed(flag_name):
    fields = _complete_demo_connection_preflight_dry_run_fields()
    fields[flag_name] = True

    preflight = build_demo_connection_proof_preflight_dry_run(fields)

    assert preflight["demo_connection_preflight_ready"] is False
    assert preflight[flag_name] is False
    assert flag_name in preflight["failed_gates"]


def test_complete_sanitized_demo_connection_preflight_passes_dry_run_readiness_only():
    preflight = build_demo_connection_proof_preflight_dry_run(
        _complete_demo_connection_preflight_dry_run_fields()
    )

    assert preflight["demo_connection_preflight_ready"] is True
    assert preflight["future_demo_connection_proof_review_ready"] is True
    assert preflight["dry_run_only"] is True
    assert preflight["proof_executable_now"] is False
    assert preflight["broker_connection_allowed"] is False
    assert preflight["connection_attempt_performed"] is False
    assert preflight["broker_request_sent"] is False
    assert preflight["network_used"] is False
    assert preflight["market_data_fetched"] is False
    assert preflight["credentials_used"] is False
    assert preflight["credential_material_present"] is False
    assert preflight["order_placed"] is False
    assert preflight["live_execution_allowed"] is False
    assert preflight["demo_runtime_readiness"]["demo_runtime_ready"] is True


def test_complete_sanitized_review_package_is_ready_for_human_review_only():
    checklist = build_live_arming_checklist(_complete_sanitized_live_review_package())

    assert checklist["ready_for_human_review"] is True
    assert checklist["live_execution_allowed"] is False
    assert checklist["order_submit_allowed"] is False
    assert checklist["broker_request_sent"] is False
    assert checklist["network_used"] is False
    assert checklist["missing_fields"] == []
    assert checklist["failed_gates"] == []
    assert "kill_switch_confirmed" in checklist["passed_gates"]
    assert "final_disarm_confirmed" in checklist["passed_gates"]
    assert (
        checklist["next_required_action"]
        == "human_owner_review_only_live_execution_remains_blocked"
    )


def test_credentials_fail_closed_even_with_complete_review_package():
    fields = _complete_sanitized_live_review_package()
    fields["credential_value"] = "not-a-real-demo-value"

    checklist = build_live_arming_checklist(fields)

    assert checklist["ready_for_human_review"] is False
    assert checklist["live_execution_allowed"] is False
    assert "no_forbidden_live_fields" in checklist["failed_gates"]
    assert "forbidden_field:credential_value" in checklist["blocker_reasons"]


def test_account_identifiers_fail_closed_even_with_complete_review_package():
    fields = _complete_sanitized_live_review_package()
    fields["account_id"] = "not-a-real-account-reference"

    checklist = build_live_arming_checklist(fields)

    assert checklist["ready_for_human_review"] is False
    assert checklist["live_execution_allowed"] is False
    assert "no_forbidden_live_fields" in checklist["failed_gates"]
    assert "forbidden_field:account_id" in checklist["blocker_reasons"]


def test_retry_true_fails_closed_even_with_no_retry_confirmation():
    fields = _complete_sanitized_live_review_package()
    fields["retry_loop"] = True

    checklist = build_live_arming_checklist(fields)

    assert checklist["ready_for_human_review"] is False
    assert checklist["live_execution_allowed"] is False
    assert "retry_loop" in checklist["failed_gates"]
    assert "retry_loop_must_not_be_enabled" in checklist["blocker_reasons"]


def test_autonomous_reentry_true_fails_closed():
    fields = _complete_sanitized_live_review_package()
    fields["autonomous_reentry"] = True

    checklist = build_live_arming_checklist(fields)

    assert checklist["ready_for_human_review"] is False
    assert checklist["live_execution_allowed"] is False
    assert "autonomous_reentry" in checklist["failed_gates"]
    assert "autonomous_reentry_must_not_be_enabled" in checklist["blocker_reasons"]


def test_missing_kill_switch_fails_closed():
    fields = _complete_sanitized_live_review_package()
    fields.pop("kill_switch_confirmed")

    checklist = build_live_arming_checklist(fields)

    assert checklist["ready_for_human_review"] is False
    assert checklist["live_execution_allowed"] is False
    assert "kill_switch_confirmed" in checklist["missing_fields"]
    assert "kill_switch_confirmed" in checklist["failed_gates"]


def test_missing_final_disarm_fails_closed():
    fields = _complete_sanitized_live_review_package()
    fields.pop("final_disarm_confirmed")

    checklist = build_live_arming_checklist(fields)

    assert checklist["ready_for_human_review"] is False
    assert checklist["live_execution_allowed"] is False
    assert "final_disarm_confirmed" in checklist["missing_fields"]
    assert "final_disarm_confirmed" in checklist["failed_gates"]


def test_live_submit_remains_blocked_after_review_ready_package():
    checklist = build_live_arming_checklist(_complete_sanitized_live_review_package())

    assert checklist["ready_for_human_review"] is True
    assert checklist["live_execution_allowed"] is False
    with pytest.raises(LiveExecutionBlocked):
        submit_live_order(_complete_sanitized_live_review_package())


def test_non_allowlisted_pair_is_rejected():
    risk = validate_order_request(
        {
            "instrument": "AUD_USD",
            "side": "BUY",
            "order_type": "MARKET",
            "units": 1,
            "spread_pips": 1.0,
            "stop_loss": 0.65,
            "max_loss_usd": 1.0,
        }
    )

    assert risk["risk_passed"] is False
    assert "pair_not_allowlisted" in risk["rejection_reasons"]


def test_oversized_position_is_rejected():
    risk = validate_order_request(
        {
            "instrument": "EUR_USD",
            "side": "BUY",
            "order_type": "MARKET",
            "units": 2,
            "spread_pips": 1.0,
            "stop_loss": 1.075,
            "max_loss_usd": 1.0,
        }
    )

    assert risk["risk_passed"] is False
    assert "position_size_exceeds_max_trade_size" in risk["rejection_reasons"]


def test_missing_stop_loss_is_rejected():
    risk = validate_order_request(
        {
            "instrument": "EUR_USD",
            "side": "BUY",
            "order_type": "MARKET",
            "units": 1,
            "spread_pips": 1.0,
            "max_loss_usd": 1.0,
        }
    )

    assert risk["risk_passed"] is False
    assert "stop_loss_required" in risk["rejection_reasons"]


def test_order_payload_is_valid_after_risk_passes():
    request = {
        "instrument": "EUR_USD",
        "side": "BUY",
        "order_type": "MARKET",
        "units": 1,
        "spread_pips": 1.0,
        "stop_loss": 1.075,
        "take_profit": 1.09,
        "max_loss_usd": 1.0,
    }
    risk = validate_order_request(request)
    payload = build_order_payload(request, risk)

    assert risk["risk_passed"] is True
    assert payload["paper_only"] is True
    assert payload["execution_allowed"] is False
    assert payload["broker_request_sent"] is False
    assert payload["network_used"] is False


def test_fill_verification_records_evidence():
    result = run_governed_paper_flow()

    assert result["fill_verify"]["fill_verified"] is True
    assert result["fill_verify"]["evidence_recorded"] is True
    assert result["paper_execution"]["fill"]["status"] == "PAPER_FILL_SIMULATED"
    assert any(event["event"] == "fill" for event in result["evidence_log"]["events"])


def test_position_close_records_pl():
    result = run_governed_paper_flow()

    assert result["position_state"]["open_position_count"] == 1
    assert result["position_close"]["position_closed"] is True
    assert result["position_close"]["pl_capture_status"] == "RECORDED"
    assert result["position_close"]["realized_pl_usd"] == 0.0


def test_governed_flow_records_adapter_evidence():
    result = run_governed_paper_flow()

    assert result["broker_adapter_contract"]["mode"] == "PAPER_DEMO"
    assert result["broker_adapter_contract"]["network_api_allowed"] is False
    assert result["broker_adapter_contract"]["credentials_allowed"] is False
    assert result["broker_adapter_contract"]["live_orders_allowed"] is False
    assert any(event["event"] == "adapter_evidence" for event in result["evidence_log"]["events"])
    assert result["evidence_log"]["adapter_evidence"]["status"] == "PAPER_DEMO_EVIDENCE_READY"


def test_governed_flow_records_oanda_paper_demo_mapping():
    result = run_governed_paper_flow()
    mapping = result["broker_specific_integration"]

    assert mapping["broker_id"] == "OANDA"
    assert mapping["broker_reference"] == "OANDA_PAPER_DEMO_REFERENCE_ONLY"
    assert mapping["status"] == "BROKER_SPECIFIC_PAPER_DEMO_MAPPING_READY"
    assert mapping["config_validation"]["config_valid"] is True
    assert mapping["account_mapping"]["schema"] == "AIOS_OANDA_PAPER_DEMO_ACCOUNT_STATE_MAPPING.v1"
    assert mapping["market_data_mapping"]["oanda_instrument"] == "EUR_USD"
    assert mapping["order_state_mapping"]["route_allowed"] is False
    assert mapping["fill_state_mapping"]["oanda_transaction_identifier_present"] is False
    assert mapping["evidence_mapping"]["evidence_ready"] is True
    assert mapping["broker_request_sent"] is False
    assert mapping["network_used"] is False
    assert mapping["live_execution_allowed"] is False


def test_governed_flow_wires_oanda_demo_auth_readiness_fail_closed_by_default():
    result = run_governed_paper_flow()
    auth = result["oanda_demo_auth_readiness"]

    assert "OANDA DEMO AUTH HANDOFF READINESS" in result["chain_links"]
    assert result["oanda_demo_auth_contracts"]["contracts_ready_for_future_external_handoff"] is True
    assert auth["status"] == "OANDA_DEMO_AUTH_HANDOFF_BLOCKED"
    assert auth["auth_handoff_ready"] is False
    assert "MISSING_CREDENTIALS" in auth["failure_states"]
    assert auth["audit_event"]["contains_real_credentials"] is False
    assert auth["audit_event"]["contains_account_identifier"] is False
    assert any(event["event"] == "auth_readiness" for event in result["evidence_log"]["events"])
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["live_order_placed"] is False


def test_governed_flow_accepts_sanitized_demo_auth_metadata_without_execution():
    result = run_governed_paper_flow(
        auth_handoff=build_example_sanitized_demo_auth_handoff()
    )
    auth = result["oanda_demo_auth_readiness"]

    assert auth["status"] == "OANDA_DEMO_AUTH_HANDOFF_READY"
    assert auth["auth_handoff_ready"] is True
    assert auth["credential_boundary_passed"] is True
    assert auth["account_validation_passed"] is True
    assert auth["blockers"] == []
    assert auth["contains_real_credentials"] is False
    assert auth["contains_account_identifier"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["live_order_placed"] is False


def test_governed_flow_wires_oanda_demo_connection_gate_fail_closed_by_default():
    result = run_governed_paper_flow()
    gate = result["oanda_demo_connection_gate"]

    assert "OANDA DEMO CONNECTION GATE" in result["chain_links"]
    assert result["oanda_demo_connection_gate_contracts"][
        "contracts_ready_for_future_connection_packet_review"
    ] is True
    assert gate["status"] == "OANDA_DEMO_CONNECTION_GATE_BLOCKED"
    assert gate["connection_readiness_gate_ready"] is False
    assert "human_owner_connection_gate_approval_required" in gate["blockers"]
    assert gate["audit_event"]["contains_real_credentials"] is False
    assert gate["audit_event"]["contains_account_identifier"] is False
    assert any(event["event"] == "connection_gate" for event in result["evidence_log"]["events"])
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["live_order_placed"] is False


def test_governed_flow_wires_oanda_protected_connection_attempt_fail_closed_by_default():
    result = run_governed_paper_flow()
    protected_attempt = result["oanda_demo_protected_connection_attempt"]

    assert "OANDA PROTECTED DEMO CONNECTION ATTEMPT" in result["chain_links"]
    assert result["oanda_demo_protected_connection_attempt_contracts"][
        "contracts_ready_for_protected_demo_connection_attempt"
    ] is True
    assert protected_attempt["status"] == "OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_BLOCKED"
    assert protected_attempt["connection_attempt_preflight_passed"] is False
    assert protected_attempt["connection_attempt_performed"] is False
    assert "human_owner_protected_demo_connection_approval_required" in protected_attempt["blockers"]
    assert protected_attempt["audit_event"]["contains_real_credentials"] is False
    assert protected_attempt["audit_event"]["contains_account_identifier"] is False
    assert any(
        event["event"] == "protected_connection_attempt"
        for event in result["evidence_log"]["events"]
    )
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["live_order_placed"] is False


def test_governed_flow_wires_oanda_demo_runtime_handoff_fail_closed_by_default():
    result = run_governed_paper_flow()
    runtime = result["oanda_demo_runtime_handoff"]

    assert "OANDA DEMO RUNTIME HANDOFF" in result["chain_links"]
    assert result["oanda_demo_runtime_handoff_contracts"][
        "contracts_ready_for_future_runtime_handoff"
    ] is True
    assert runtime["status"] == "OANDA_DEMO_RUNTIME_HANDOFF_BLOCKED"
    assert runtime["runtime_handoff_ready"] is False
    assert "runtime_reference_required" in runtime["blockers"]
    assert runtime["audit_event"]["contains_real_credentials"] is False
    assert runtime["audit_event"]["contains_account_identifier"] is False
    assert any(event["event"] == "runtime_handoff" for event in result["evidence_log"]["events"])
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["live_order_placed"] is False


def test_governed_flow_wires_oanda_demo_runtime_handoff_intake_fail_closed_by_default():
    result = run_governed_paper_flow()
    intake = result["oanda_demo_runtime_handoff_intake"]

    assert "OANDA DEMO RUNTIME HANDOFF INTAKE" in result["chain_links"]
    assert result["oanda_demo_runtime_handoff_intake_contracts"][
        "contracts_ready_for_future_runtime_handoff_intake"
    ] is True
    assert intake["status"] == "OANDA_DEMO_RUNTIME_HANDOFF_INTAKE_BLOCKED"
    assert intake["runtime_handoff_intake_ready"] is False
    assert "runtime_reference_required" in intake["blockers"]
    assert intake["audit_event"]["contains_real_credentials"] is False
    assert intake["audit_event"]["contains_account_identifier"] is False
    assert any(event["event"] == "runtime_handoff_intake" for event in result["evidence_log"]["events"])
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["live_order_placed"] is False


def test_governed_flow_accepts_runtime_handoff_intake_metadata_without_execution():
    result = run_governed_paper_flow(
        runtime_handoff_intake=build_example_oanda_demo_runtime_handoff_intake(),
    )
    intake = result["oanda_demo_runtime_handoff_intake"]

    assert intake["status"] == "OANDA_DEMO_RUNTIME_HANDOFF_INTAKE_READY"
    assert intake["runtime_handoff_intake_ready"] is True
    assert intake["metadata_accepted"] is True
    assert intake["runtime_boundary_enforced"] is True
    assert intake["audit_event"]["credential_values_recorded"] is False
    assert intake["audit_event"]["account_identifiers_recorded"] is False
    assert intake["broker_request_sent"] is False
    assert intake["network_used"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["live_order_placed"] is False


def test_governed_flow_accepts_runtime_handoff_metadata_without_execution():
    result = run_governed_paper_flow(
        auth_handoff=build_example_sanitized_demo_auth_handoff(),
        runtime_handoff_intake=build_example_oanda_demo_runtime_handoff_intake(),
        runtime_handoff=build_example_oanda_demo_runtime_handoff(),
        connection_gate_approval=build_example_oanda_demo_connection_gate_approval(),
    )
    runtime = result["oanda_demo_runtime_handoff"]
    intake = result["oanda_demo_runtime_handoff_intake"]

    assert intake["status"] == "OANDA_DEMO_RUNTIME_HANDOFF_INTAKE_READY"
    assert intake["runtime_handoff_intake_ready"] is True
    assert runtime["status"] == "OANDA_DEMO_RUNTIME_HANDOFF_READY"
    assert runtime["runtime_handoff_ready"] is True
    assert runtime["runtime_handoff_intake_ready"] is True
    assert runtime["runtime_boundary_enforced"] is True
    assert runtime["audit_event"]["credential_values_recorded"] is False
    assert runtime["audit_event"]["account_identifiers_recorded"] is False
    assert runtime["broker_request_sent"] is False
    assert runtime["network_used"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["live_order_placed"] is False


def test_governed_flow_accepts_demo_connection_gate_metadata_without_execution():
    result = run_governed_paper_flow(
        auth_handoff=build_example_sanitized_demo_auth_handoff(),
        connection_gate_approval=build_example_oanda_demo_connection_gate_approval(),
    )
    gate = result["oanda_demo_connection_gate"]

    assert gate["status"] == "OANDA_DEMO_CONNECTION_GATE_READY"
    assert gate["connection_readiness_gate_ready"] is True
    assert gate["connection_readiness_only"] is True
    assert gate["future_connection_packet_ready_for_human_review"] is True
    assert gate["connection_attempt_allowed_now"] is False
    assert gate["connection_attempt_performed"] is False
    assert gate["broker_request_sent"] is False
    assert gate["network_used"] is False
    assert gate["order_placed"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["live_order_placed"] is False


def test_governed_flow_accepts_protected_connection_attempt_metadata_without_connector():
    result = run_governed_paper_flow(
        auth_handoff=build_example_sanitized_demo_auth_handoff(),
        runtime_handoff_intake=build_example_oanda_demo_runtime_handoff_intake(),
        runtime_handoff=build_example_oanda_demo_runtime_handoff(),
        connection_gate_approval=build_example_oanda_demo_connection_gate_approval(),
        protected_connection_attempt_request=(
            build_example_oanda_demo_protected_connection_attempt_request()
        ),
    )
    protected_attempt = result["oanda_demo_protected_connection_attempt"]

    assert protected_attempt["connection_attempt_preflight_passed"] is True
    assert protected_attempt["outcome"] == "RUNTIME_CONNECTOR_MISSING_SANITIZED"
    assert protected_attempt["connection_attempt_performed"] is False
    assert protected_attempt["broker_request_sent"] is False
    assert protected_attempt["network_used"] is False
    assert protected_attempt["order_placed"] is False
    assert protected_attempt["contains_real_credentials"] is False
    assert protected_attempt["contains_account_identifier"] is False
    assert result["broker_request_sent"] is False
    assert result["network_used"] is False
    assert result["live_order_placed"] is False


def test_final_report_is_produced():
    result = run_governed_paper_flow()

    assert result["final_trade_report"]["report_status"] == "PRODUCED"
    assert result["final_trade_report"]["live_order_placed"] is False
    assert result["final_trade_report"]["real_credentials_added"] is False


def test_readiness_script_main_prints_paper_result(monkeypatch, capsys):
    script_path = REPO_ROOT / "scripts" / "forex_delivery" / "validate_forex_delivery_readiness.py"
    spec = importlib.util.spec_from_file_location("validate_forex_delivery_readiness", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    monkeypatch.setattr(sys, "argv", [str(script_path), "--mode", "paper"])
    assert module.main() == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["mode"] == "PAPER_ONLY"
    assert payload["live_order_placed"] is False
    assert payload["broker_request_sent"] is False
