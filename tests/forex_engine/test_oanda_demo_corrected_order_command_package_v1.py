import json
import subprocess
import sys

from automation.forex_engine.oanda_demo_corrected_order_command_package_v1 import (
    BLOCKED_BY_AUTONOMY_REQUEST,
    BLOCKED_BY_INVALID_TRADE_INTENT,
    BLOCKED_BY_LIVE_ENDPOINT,
    BLOCKED_BY_MISSING_REFERENCE_PRICE,
    BLOCKED_BY_PRIOR_ORDER_CAP,
    BLOCKED_BY_PROFIT_CLAIM,
    BLOCKED_BY_SLTP_VALIDATION,
    CORRECTED_ORDER_COMMAND_PACKAGE_READY,
    build_oanda_demo_corrected_order_command_package_v1,
)


SCRIPT = "scripts/forex_delivery/run_oanda_demo_corrected_order_command_package_v1.py"


def ready_context(**overrides):
    context = {
        "instrument": "EUR_USD",
        "direction": "BUY",
        "units": 1,
        "reference_price": "1.07050",
        "stop_loss": "1.07000",
        "take_profit": "1.07100",
        "risk_amount": "1.00",
        "client_order_id": "AIOS-DEMO-CORRECTED-ONE-ORDER-OWNER-RUNTIME-001",
        "order_type": "MARKET",
        "demo_only_confirmed": True,
        "sltp_validation_passed_confirmed": True,
        "one_prior_order_cap_consumed_confirmed": True,
        "new_owner_approval_required_before_any_future_order_confirmed": True,
        "owner_manual_runtime_only_confirmed": True,
        "no_live_endpoint_confirmed": True,
        "no_autonomous_order_confirmed": True,
        "post_trade_evidence_required_confirmed": True,
        "no_profit_claim_confirmed": True,
    }
    context.update(overrides)
    return context


def test_ready_buy_package_outputs_template_but_authorizes_no_order():
    result = build_oanda_demo_corrected_order_command_package_v1(ready_context())

    assert result["classification"] == CORRECTED_ORDER_COMMAND_PACKAGE_READY
    assert result["package_ready"] is True
    package = result["corrected_order_command_package"]
    assert package["order_authorized_by_this_package"] is False
    assert package["second_order_allowed_by_this_package"] is False
    assert package["future_order_requires_separate_owner_approval"] is True
    assert "--execute-vault-backed-demo-one-order" in package["owner_command_template"]
    assert "--stop-loss 1.07000" in package["owner_command_template"]
    assert "--take-profit 1.07100" in package["owner_command_template"]
    assert result["safety_boundaries"]["broker_network_call_performed"] is False


def test_prior_loss_side_buy_take_profit_blocks_before_transport():
    result = build_oanda_demo_corrected_order_command_package_v1(
        ready_context(reference_price="1.07150", take_profit="1.07100")
    )

    assert result["classification"] == BLOCKED_BY_SLTP_VALIDATION
    assert result["package_ready"] is False
    assert (
        result["sltp_validation"]["classification"]
        == "BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_REFERENCE"
    )
    assert result["corrected_order_command_package"]["owner_command_template"] is None


def test_missing_reference_price_has_specific_blocker():
    result = build_oanda_demo_corrected_order_command_package_v1(
        ready_context(reference_price=None)
    )

    assert result["classification"] == BLOCKED_BY_MISSING_REFERENCE_PRICE
    assert result["package_ready"] is False


def test_invalid_trade_intent_blocks():
    result = build_oanda_demo_corrected_order_command_package_v1(
        ready_context(order_type="LIMIT")
    )

    assert result["classification"] == BLOCKED_BY_INVALID_TRADE_INTENT
    assert result["package_ready"] is False


def test_prior_order_cap_confirmation_required():
    result = build_oanda_demo_corrected_order_command_package_v1(
        ready_context(one_prior_order_cap_consumed_confirmed=False)
    )

    assert result["classification"] == BLOCKED_BY_PRIOR_ORDER_CAP
    assert result["package_ready"] is False


def test_live_endpoint_confirmation_required():
    result = build_oanda_demo_corrected_order_command_package_v1(
        ready_context(no_live_endpoint_confirmed=False)
    )

    assert result["classification"] == BLOCKED_BY_LIVE_ENDPOINT
    assert result["package_ready"] is False


def test_autonomy_boundary_confirmation_required():
    result = build_oanda_demo_corrected_order_command_package_v1(
        ready_context(owner_manual_runtime_only_confirmed=False)
    )

    assert result["classification"] == BLOCKED_BY_AUTONOMY_REQUEST
    assert result["package_ready"] is False


def test_profit_claim_blocks():
    result = build_oanda_demo_corrected_order_command_package_v1(
        ready_context(profit_claim_made=True)
    )

    assert result["classification"] == BLOCKED_BY_PROFIT_CLAIM
    assert result["package_ready"] is False


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
    assert payload["template_status"]["order_authorized_by_template"] is False
    assert "EXAMPLE_REFERENCE_PRICE" in payload["template_command"]


def test_cli_build_corrected_command_package_ready():
    completed = subprocess.run(
        [
            sys.executable,
            SCRIPT,
            "--build-corrected-command-package",
            "--instrument",
            "EUR_USD",
            "--direction",
            "BUY",
            "--units",
            "1",
            "--reference-price",
            "1.07050",
            "--stop-loss",
            "1.07000",
            "--take-profit",
            "1.07100",
            "--risk-amount",
            "1.00",
            "--client-order-id",
            "AIOS-DEMO-CORRECTED-ONE-ORDER-OWNER-RUNTIME-001",
            "--order-type",
            "MARKET",
            "--i-confirm-demo-only",
            "--i-confirm-sltp-validation-passed",
            "--i-confirm-one-prior-order-cap-consumed",
            "--i-confirm-new-owner-approval-required-before-any-future-order",
            "--i-confirm-owner-manual-runtime-only",
            "--i-confirm-no-live-endpoint",
            "--i-confirm-no-autonomous-order",
            "--i-confirm-post-trade-evidence-required",
            "--i-confirm-no-profit-claim",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["classification"] == CORRECTED_ORDER_COMMAND_PACKAGE_READY
    assert payload["package_ready"] is True
    assert payload["safety_boundaries"]["vault_read_performed"] is False
