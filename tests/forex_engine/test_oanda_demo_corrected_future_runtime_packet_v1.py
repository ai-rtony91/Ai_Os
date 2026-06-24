import json
import subprocess
import sys

from automation.forex_engine.oanda_demo_corrected_future_runtime_packet_v1 import (
    BLOCKED_BY_AUTONOMY_REQUEST,
    BLOCKED_BY_INVALID_TRADE_INTENT,
    BLOCKED_BY_LIVE_ENDPOINT,
    BLOCKED_BY_MISSING_APPROVAL_GATE,
    BLOCKED_BY_MISSING_CORRECTED_PACKAGE,
    BLOCKED_BY_PROFIT_CLAIM,
    BLOCKED_BY_SLTP_VALIDATION,
    CORRECTED_FUTURE_RUNTIME_PACKET_READY,
    build_oanda_demo_corrected_future_runtime_packet_v1,
)


SCRIPT = (
    "scripts/forex_delivery/"
    "run_oanda_demo_corrected_future_runtime_packet_v1.py"
)


def ready_context(**overrides):
    context = {
        "instrument": "EUR_USD",
        "direction": "BUY",
        "units": 1,
        "reference_price": "1.07050",
        "stop_loss": "1.06950",
        "take_profit": "1.07150",
        "risk_amount": "1.00",
        "client_order_id": "AIOS-DEMO-CORRECTED-FUTURE-OWNER-RUNTIME-001",
        "order_type": "MARKET",
        "corrected_package_ready_confirmed": True,
        "future_approval_gate_ready_confirmed": True,
        "sltp_validation_ready_confirmed": True,
        "demo_only_confirmed": True,
        "owner_manual_runtime_only_confirmed": True,
        "no_live_endpoint_confirmed": True,
        "no_autonomous_order_confirmed": True,
        "post_trade_evidence_required_confirmed": True,
        "no_profit_claim_confirmed": True,
    }
    context.update(overrides)
    return context


def test_ready_buy_packet_outputs_owner_only_vault_backed_template():
    result = build_oanda_demo_corrected_future_runtime_packet_v1(ready_context())

    assert result["classification"] == CORRECTED_FUTURE_RUNTIME_PACKET_READY
    assert result["runtime_packet_ready"] is True
    template = result["runtime_packet"]["owner_command_template"]
    assert "run_oanda_demo_vault_backed_one_order_transport_v1.py" in template
    assert "--execute-vault-backed-demo-one-order" in template
    assert "--stop-loss 1.06950" in template
    assert "--take-profit 1.07150" in template
    assert "AIOS-DEMO-CORRECTED-FUTURE-OWNER-RUNTIME-001" in template
    assert result["runtime_packet"]["codex_execution_authorized"] is False
    assert result["safety_boundaries"]["broker_network_call_performed"] is False
    assert result["safety_boundaries"]["vault_read_performed"] is False


def test_ready_sell_packet_uses_sell_side_rules():
    result = build_oanda_demo_corrected_future_runtime_packet_v1(
        ready_context(
            direction="SELL",
            reference_price="1.07050",
            stop_loss="1.07150",
            take_profit="1.06950",
        )
    )

    assert result["classification"] == CORRECTED_FUTURE_RUNTIME_PACKET_READY
    assert result["runtime_packet_ready"] is True
    assert "--direction SELL" in result["runtime_packet"]["owner_command_template"]


def test_buy_loss_side_take_profit_blocks():
    result = build_oanda_demo_corrected_future_runtime_packet_v1(
        ready_context(take_profit="1.07000")
    )

    assert result["classification"] == BLOCKED_BY_SLTP_VALIDATION
    assert BLOCKED_BY_SLTP_VALIDATION in result["blockers"]
    assert result["runtime_packet"]["owner_command_template"] is None


def test_missing_corrected_package_confirmation_blocks():
    result = build_oanda_demo_corrected_future_runtime_packet_v1(
        ready_context(corrected_package_ready_confirmed=False)
    )

    assert result["classification"] == BLOCKED_BY_MISSING_CORRECTED_PACKAGE
    assert result["runtime_packet_ready"] is False


def test_missing_approval_gate_confirmation_blocks():
    result = build_oanda_demo_corrected_future_runtime_packet_v1(
        ready_context(future_approval_gate_ready_confirmed=False)
    )

    assert result["classification"] == BLOCKED_BY_MISSING_APPROVAL_GATE
    assert result["runtime_packet_ready"] is False


def test_missing_sltp_validation_confirmation_blocks():
    result = build_oanda_demo_corrected_future_runtime_packet_v1(
        ready_context(sltp_validation_ready_confirmed=False)
    )

    assert result["classification"] == BLOCKED_BY_SLTP_VALIDATION
    assert result["runtime_packet_ready"] is False


def test_invalid_numeric_price_blocks_invalid_trade_intent():
    result = build_oanda_demo_corrected_future_runtime_packet_v1(
        ready_context(reference_price="EXAMPLE_REFERENCE_PRICE")
    )

    assert BLOCKED_BY_INVALID_TRADE_INTENT in result["blockers"]
    assert result["runtime_packet_ready"] is False


def test_live_endpoint_request_blocks():
    result = build_oanda_demo_corrected_future_runtime_packet_v1(
        ready_context(live_endpoint_requested=True)
    )

    assert result["classification"] == BLOCKED_BY_LIVE_ENDPOINT
    assert BLOCKED_BY_LIVE_ENDPOINT in result["blockers"]
    assert result["runtime_packet_ready"] is False


def test_autonomy_request_blocks():
    result = build_oanda_demo_corrected_future_runtime_packet_v1(
        ready_context(autonomous_order_requested=True)
    )

    assert result["classification"] == BLOCKED_BY_AUTONOMY_REQUEST
    assert BLOCKED_BY_AUTONOMY_REQUEST in result["blockers"]
    assert result["runtime_packet_ready"] is False


def test_profit_claim_blocks():
    result = build_oanda_demo_corrected_future_runtime_packet_v1(
        ready_context(profit_claim_made=True)
    )

    assert result["classification"] == BLOCKED_BY_PROFIT_CLAIM
    assert BLOCKED_BY_PROFIT_CLAIM in result["blockers"]
    assert result["runtime_packet_ready"] is False


def test_invalid_client_order_id_blocks():
    result = build_oanda_demo_corrected_future_runtime_packet_v1(
        ready_context(client_order_id="AIOS-DEMO-ONE-ORDER-OWNER-RUNTIME-001")
    )

    assert result["classification"] == BLOCKED_BY_INVALID_TRADE_INTENT
    assert result["runtime_packet_ready"] is False


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
    assert payload["template_status"]["codex_execution_authorized"] is False
    assert "--build-corrected-future-runtime-packet" in payload["template_command"]


def test_cli_build_ready_runtime_packet():
    completed = subprocess.run(
        [
            sys.executable,
            SCRIPT,
            "--build-corrected-future-runtime-packet",
            "--instrument",
            "EUR_USD",
            "--direction",
            "BUY",
            "--units",
            "1",
            "--reference-price",
            "1.07050",
            "--stop-loss",
            "1.06950",
            "--take-profit",
            "1.07150",
            "--risk-amount",
            "1.00",
            "--client-order-id",
            "AIOS-DEMO-CORRECTED-FUTURE-OWNER-RUNTIME-001",
            "--order-type",
            "MARKET",
            "--i-confirm-corrected-package-ready",
            "--i-confirm-future-approval-gate-ready",
            "--i-confirm-sltp-validation-ready",
            "--i-confirm-demo-only",
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
    assert payload["classification"] == CORRECTED_FUTURE_RUNTIME_PACKET_READY
    assert payload["runtime_packet_ready"] is True
    assert payload["safety_boundaries"]["environment_read_performed"] is False
