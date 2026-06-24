import json
import subprocess
import sys

from automation.forex_engine.oanda_demo_future_order_approval_gate_v1 import (
    BLOCKED_BY_AUTONOMY_REQUEST,
    BLOCKED_BY_LIVE_ENDPOINT,
    BLOCKED_BY_MISSING_CORRECTED_PACKAGE,
    BLOCKED_BY_MISSING_OWNER_APPROVAL,
    BLOCKED_BY_MISSING_SLTP_VALIDATION,
    BLOCKED_BY_ORDER_CAP_NOT_ACKNOWLEDGED,
    BLOCKED_BY_PRIOR_CANCEL_NOT_CAPTURED,
    BLOCKED_BY_PROFIT_CLAIM,
    OWNER_APPROVAL_GATE_READY_FOR_MANUAL_DECISION,
    evaluate_oanda_demo_future_order_approval_gate_v1,
)


SCRIPT = "scripts/forex_delivery/run_oanda_demo_future_order_approval_gate_v1.py"


def ready_context(**overrides):
    context = {
        "corrected_order_package_ready": True,
        "sltp_validation_ready": True,
        "prior_cancel_evidence_captured": True,
        "prior_order_cap_consumed_acknowledged": True,
        "explicit_new_owner_approval": True,
        "demo_only": True,
        "one_order_only": True,
        "no_live_endpoint": True,
        "no_autonomous_order": True,
        "post_trade_evidence_required": True,
        "no_profit_claim": True,
    }
    context.update(overrides)
    return context


def test_ready_gate_is_manual_decision_only_not_execution_authority():
    result = evaluate_oanda_demo_future_order_approval_gate_v1(ready_context())

    assert result["classification"] == OWNER_APPROVAL_GATE_READY_FOR_MANUAL_DECISION
    assert result["ready_for_manual_decision"] is True
    assert result["approval_gate"]["order_execution_authorized"] is False
    assert result["approval_gate"]["automatic_order_authorized"] is False
    assert result["approval_gate"]["broker_command_authorized_for_codex"] is False
    assert result["safety_boundaries"]["broker_network_call_performed"] is False


def test_missing_corrected_package_blocks():
    result = evaluate_oanda_demo_future_order_approval_gate_v1(
        ready_context(corrected_order_package_ready=False)
    )

    assert result["classification"] == BLOCKED_BY_MISSING_CORRECTED_PACKAGE
    assert result["ready_for_manual_decision"] is False


def test_missing_sltp_validation_blocks():
    result = evaluate_oanda_demo_future_order_approval_gate_v1(
        ready_context(sltp_validation_ready=False)
    )

    assert result["classification"] == BLOCKED_BY_MISSING_SLTP_VALIDATION
    assert result["ready_for_manual_decision"] is False


def test_missing_prior_cancel_capture_blocks():
    result = evaluate_oanda_demo_future_order_approval_gate_v1(
        ready_context(prior_cancel_evidence_captured=False)
    )

    assert result["classification"] == BLOCKED_BY_PRIOR_CANCEL_NOT_CAPTURED
    assert result["ready_for_manual_decision"] is False


def test_order_cap_acknowledgement_blocks():
    result = evaluate_oanda_demo_future_order_approval_gate_v1(
        ready_context(prior_order_cap_consumed_acknowledged=False)
    )

    assert result["classification"] == BLOCKED_BY_ORDER_CAP_NOT_ACKNOWLEDGED
    assert result["ready_for_manual_decision"] is False


def test_missing_owner_approval_blocks():
    result = evaluate_oanda_demo_future_order_approval_gate_v1(
        ready_context(explicit_new_owner_approval=False)
    )

    assert result["classification"] == BLOCKED_BY_MISSING_OWNER_APPROVAL
    assert result["ready_for_manual_decision"] is False


def test_live_endpoint_blocks():
    result = evaluate_oanda_demo_future_order_approval_gate_v1(
        ready_context(live_endpoint_requested=True)
    )

    assert result["classification"] == BLOCKED_BY_LIVE_ENDPOINT
    assert result["ready_for_manual_decision"] is False


def test_autonomy_request_blocks():
    result = evaluate_oanda_demo_future_order_approval_gate_v1(
        ready_context(autonomous_order_requested=True)
    )

    assert result["classification"] == BLOCKED_BY_AUTONOMY_REQUEST
    assert result["ready_for_manual_decision"] is False


def test_profit_claim_blocks():
    result = evaluate_oanda_demo_future_order_approval_gate_v1(
        ready_context(profit_claim_made=True)
    )

    assert result["classification"] == BLOCKED_BY_PROFIT_CLAIM
    assert result["ready_for_manual_decision"] is False


def test_cli_print_template_is_sanitized_json():
    completed = subprocess.run(
        [sys.executable, SCRIPT, "--print-template"],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["script_status"] == "TEMPLATE_ONLY"
    assert payload["broker_network_call_performed"] is False
    assert payload["template_status"]["order_execution_authorized"] is False
    assert "--evaluate-future-order-approval" in payload["template_command"]


def test_cli_ready_gate_outputs_manual_decision_classification():
    completed = subprocess.run(
        [
            sys.executable,
            SCRIPT,
            "--evaluate-future-order-approval",
            "--corrected-order-package-ready",
            "--sltp-validation-ready",
            "--prior-cancel-evidence-captured",
            "--prior-order-cap-consumed-acknowledged",
            "--explicit-new-owner-approval",
            "--demo-only",
            "--one-order-only",
            "--no-live-endpoint",
            "--no-autonomous-order",
            "--post-trade-evidence-required",
            "--no-profit-claim",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["classification"] == OWNER_APPROVAL_GATE_READY_FOR_MANUAL_DECISION
    assert payload["ready_for_manual_decision"] is True
    assert payload["approval_gate"]["order_execution_authorized"] is False
    assert payload["safety_boundaries"]["environment_read_performed"] is False
