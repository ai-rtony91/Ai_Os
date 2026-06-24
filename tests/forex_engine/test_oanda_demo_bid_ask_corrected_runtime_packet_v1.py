import json

import pytest

from automation.forex_engine.oanda_demo_bid_ask_corrected_runtime_packet_v1 import (
    BID_ASK_CORRECTED_RUNTIME_PACKET_READY,
    BLOCKED_BY_AUTONOMY_REQUEST,
    BLOCKED_BY_BID_ASK_VALIDATION,
    BLOCKED_BY_INVALID_BID_ASK,
    BLOCKED_BY_INVALID_TRADE_INTENT,
    BLOCKED_BY_LIVE_ENDPOINT,
    BLOCKED_BY_PROFIT_CLAIM,
    build_oanda_demo_bid_ask_corrected_runtime_packet_v1,
)
from scripts.forex_delivery.run_oanda_demo_bid_ask_corrected_runtime_packet_v1 import (
    main,
)


def valid_context(**overrides):
    context = {
        "instrument": "EUR_USD",
        "direction": "BUY",
        "units": "1",
        "bid": "1.07040",
        "ask": "1.07050",
        "stop_loss": "1.07010",
        "take_profit": "1.07080",
        "min_distance_pips": "2",
        "pip_size": "0.0001",
        "risk_amount": "1.00",
        "client_order_id": "AIOS-DEMO-BIDASK-CORRECTED-OWNER-RUNTIME-001",
        "order_type": "MARKET",
        "bid_ask_sltp_validation_ready_confirmed": True,
        "demo_only_confirmed": True,
        "owner_manual_runtime_only_confirmed": True,
        "no_live_endpoint_confirmed": True,
        "no_autonomous_order_confirmed": True,
        "post_trade_evidence_required_confirmed": True,
        "no_profit_claim_confirmed": True,
    }
    context.update(overrides)
    return context


def test_buy_runtime_packet_ready_with_owner_transport_template():
    result = build_oanda_demo_bid_ask_corrected_runtime_packet_v1(valid_context())

    assert result["classification"] == BID_ASK_CORRECTED_RUNTIME_PACKET_READY
    assert result["runtime_packet_ready"] is True
    command = result["runtime_packet"]["owner_command_template"]
    assert "run_oanda_demo_vault_backed_one_order_transport_v1.py" in command
    assert "--execute-vault-backed-demo-one-order" in command
    assert "--stop-loss 1.07010" in command
    assert "--take-profit 1.07080" in command
    assert "--token" not in command
    assert "--account-id" not in command
    assert result["safety_boundaries"]["broker_network_call_performed"] is False
    assert result["safety_boundaries"]["vault_read_performed"] is False


def test_sell_runtime_packet_ready():
    result = build_oanda_demo_bid_ask_corrected_runtime_packet_v1(
        valid_context(
            direction="SELL",
            stop_loss="1.07080",
            take_profit="1.07010",
        )
    )

    assert result["classification"] == BID_ASK_CORRECTED_RUNTIME_PACKET_READY
    assert "--direction SELL" in result["runtime_packet"]["owner_command_template"]


def test_runtime_packet_requires_bid_ask_validation_ready_confirmation():
    result = build_oanda_demo_bid_ask_corrected_runtime_packet_v1(
        valid_context(bid_ask_sltp_validation_ready_confirmed=False)
    )

    assert result["classification"] == BLOCKED_BY_BID_ASK_VALIDATION
    assert result["runtime_packet_ready"] is False


def test_runtime_packet_blocks_invalid_bid_ask_values():
    result = build_oanda_demo_bid_ask_corrected_runtime_packet_v1(
        valid_context(bid="EXAMPLE_BID")
    )

    assert result["classification"] == BLOCKED_BY_INVALID_BID_ASK
    assert result["runtime_packet_ready"] is False


def test_runtime_packet_blocks_side_validation_failure():
    result = build_oanda_demo_bid_ask_corrected_runtime_packet_v1(
        valid_context(take_profit="1.07045")
    )

    assert result["classification"] == BLOCKED_BY_BID_ASK_VALIDATION
    assert result["runtime_packet_ready"] is False


def test_runtime_packet_blocks_invalid_trade_intent():
    result = build_oanda_demo_bid_ask_corrected_runtime_packet_v1(
        valid_context(units="2")
    )

    assert result["classification"] == BLOCKED_BY_INVALID_TRADE_INTENT
    assert result["runtime_packet_ready"] is False


def test_runtime_packet_blocks_live_endpoint_request():
    result = build_oanda_demo_bid_ask_corrected_runtime_packet_v1(
        valid_context(live_endpoint_requested=True)
    )

    assert result["classification"] == BLOCKED_BY_LIVE_ENDPOINT
    assert result["runtime_packet_ready"] is False


def test_runtime_packet_blocks_autonomy_request():
    result = build_oanda_demo_bid_ask_corrected_runtime_packet_v1(
        valid_context(scheduler_requested=True)
    )

    assert result["classification"] == BLOCKED_BY_AUTONOMY_REQUEST
    assert result["runtime_packet_ready"] is False


def test_runtime_packet_blocks_profit_claim():
    result = build_oanda_demo_bid_ask_corrected_runtime_packet_v1(
        valid_context(profit_claim_made=True)
    )

    assert result["classification"] == BLOCKED_BY_PROFIT_CLAIM
    assert result["runtime_packet_ready"] is False


def test_cli_print_template_returns_sanitized_json(capsys):
    exit_code = main(["--print-template"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["script_status"] == "BID_ASK_CORRECTED_RUNTIME_PACKET_TEMPLATE_ONLY"
    assert payload["broker_network_call_performed"] is False
    assert payload["vault_read_performed"] is False
    assert payload["token_argument_supported"] is False


def test_cli_build_runtime_packet_ready(capsys):
    exit_code = main(
        [
            "--build-bid-ask-corrected-runtime-packet",
            "--instrument",
            "EUR_USD",
            "--direction",
            "BUY",
            "--units",
            "1",
            "--bid",
            "1.07040",
            "--ask",
            "1.07050",
            "--stop-loss",
            "1.07010",
            "--take-profit",
            "1.07080",
            "--min-distance-pips",
            "2",
            "--pip-size",
            "0.0001",
            "--risk-amount",
            "1.00",
            "--client-order-id",
            "AIOS-DEMO-BIDASK-CORRECTED-OWNER-RUNTIME-001",
            "--order-type",
            "MARKET",
            "--i-confirm-bid-ask-sltp-validation-ready",
            "--i-confirm-demo-only",
            "--i-confirm-owner-manual-runtime-only",
            "--i-confirm-no-live-endpoint",
            "--i-confirm-no-autonomous-order",
            "--i-confirm-post-trade-evidence-required",
            "--i-confirm-no-profit-claim",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["classification"] == BID_ASK_CORRECTED_RUNTIME_PACKET_READY
    assert payload["broker_network_call_performed"] is False
    assert payload["vault_read_performed"] is False


def test_cli_rejects_token_argument_with_sanitized_error(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--token", "SECRET"])
    payload = json.loads(capsys.readouterr().out)

    assert exc_info.value.code == 2
    assert payload["script_status"] == "BLOCKED_INVALID_ARGUMENTS"
    assert payload["token_argument_supported"] is False
    assert payload["account_id_argument_supported"] is False
