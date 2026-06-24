import json

import pytest

from automation.forex_engine.oanda_demo_bid_ask_sltp_validation_v1 import (
    BID_ASK_SLTP_VALIDATION_READY,
    BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_ASK,
    BLOCKED_BY_INVALID_NUMERIC_INPUT,
    BLOCKED_BY_MIN_DISTANCE,
    BLOCKED_BY_MISSING_BID_ASK,
    BLOCKED_BY_SELL_TAKE_PROFIT_NOT_BELOW_BID,
    evaluate_oanda_demo_bid_ask_sltp_validation_v1,
)
from scripts.forex_delivery.run_oanda_demo_bid_ask_sltp_validation_v1 import (
    main,
)


def valid_context(**overrides):
    context = {
        "instrument": "EUR_USD",
        "direction": "BUY",
        "bid": "1.07040",
        "ask": "1.07060",
        "stop_loss": "1.07010",
        "take_profit": "1.07090",
        "min_distance_pips": "2",
        "pip_size": "0.0001",
        "demo_only_confirmed": True,
        "no_broker_call_confirmed": True,
        "no_order_confirmed": True,
        "no_live_endpoint_confirmed": True,
        "no_profit_claim_confirmed": True,
    }
    context.update(overrides)
    return context


def test_buy_bid_ask_sltp_validation_ready():
    result = evaluate_oanda_demo_bid_ask_sltp_validation_v1(valid_context())

    assert result["classification"] == BID_ASK_SLTP_VALIDATION_READY
    assert result["validation_ready"] is True
    assert result["safety_proof"]["broker_call_performed"] is False
    assert result["safety_proof"]["order_placement_performed"] is False
    assert result["safety_proof"]["credential_read_performed"] is False


def test_sell_bid_ask_sltp_validation_ready():
    result = evaluate_oanda_demo_bid_ask_sltp_validation_v1(
        valid_context(
            direction="SELL",
            stop_loss="1.07090",
            take_profit="1.07010",
        )
    )

    assert result["classification"] == BID_ASK_SLTP_VALIDATION_READY
    assert result["validation_ready"] is True


def test_missing_bid_ask_blocks_before_side_rules():
    result = evaluate_oanda_demo_bid_ask_sltp_validation_v1(
        valid_context(bid="", ask="")
    )

    assert result["classification"] == BLOCKED_BY_MISSING_BID_ASK
    assert result["validation_ready"] is False


def test_invalid_numeric_blocks_placeholder_values():
    result = evaluate_oanda_demo_bid_ask_sltp_validation_v1(
        valid_context(bid="EXAMPLE_BID")
    )

    assert result["classification"] == BLOCKED_BY_INVALID_NUMERIC_INPUT
    assert result["validation_ready"] is False


def test_buy_take_profit_must_be_above_ask():
    result = evaluate_oanda_demo_bid_ask_sltp_validation_v1(
        valid_context(take_profit="1.07050")
    )

    assert result["classification"] == BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_ASK
    assert result["validation_ready"] is False


def test_sell_take_profit_must_be_below_bid():
    result = evaluate_oanda_demo_bid_ask_sltp_validation_v1(
        valid_context(direction="SELL", stop_loss="1.07090", take_profit="1.07040")
    )

    assert result["classification"] == BLOCKED_BY_SELL_TAKE_PROFIT_NOT_BELOW_BID
    assert result["validation_ready"] is False


def test_minimum_distance_blocks_too_close_values():
    result = evaluate_oanda_demo_bid_ask_sltp_validation_v1(
        valid_context(stop_loss="1.07025")
    )

    assert result["classification"] == BLOCKED_BY_MIN_DISTANCE
    assert result["validation_ready"] is False


def test_cli_print_template_returns_sanitized_json(capsys):
    exit_code = main(["--print-template"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["script_status"] == "BID_ASK_SLTP_VALIDATION_TEMPLATE_ONLY"
    assert payload["broker_call_performed"] is False
    assert payload["order_placement_performed"] is False


def test_cli_validate_ready_returns_zero_and_json(capsys):
    exit_code = main(
        [
            "--validate-bid-ask-sltp",
            "--instrument",
            "EUR_USD",
            "--direction",
            "BUY",
            "--bid",
            "1.07040",
            "--ask",
            "1.07060",
            "--stop-loss",
            "1.07010",
            "--take-profit",
            "1.07090",
            "--min-distance-pips",
            "2",
            "--pip-size",
            "0.0001",
            "--i-confirm-demo-only",
            "--i-confirm-no-broker-call",
            "--i-confirm-no-order",
            "--i-confirm-no-live-endpoint",
            "--i-confirm-no-profit-claim",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["classification"] == BID_ASK_SLTP_VALIDATION_READY
    assert payload["broker_quote_lookup_performed"] is False


def test_cli_invalid_arguments_return_sanitized_error(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--not-supported"])
    payload = json.loads(capsys.readouterr().out)

    assert exc_info.value.code == 2
    assert payload["script_status"] == "BLOCKED_INVALID_ARGUMENTS"
    assert payload["broker_call_performed"] is False
