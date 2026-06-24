from __future__ import annotations

import json

from automation.forex_engine.oanda_demo_sltp_validation_correction_v1 import (
    BLOCKED_BY_BUY_STOP_LOSS_NOT_BELOW_REFERENCE,
    BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_REFERENCE,
    BLOCKED_BY_INVALID_NUMERIC_PRICE,
    BLOCKED_BY_LIVE_ENDPOINT,
    BLOCKED_BY_MISSING_REFERENCE_PRICE,
    BLOCKED_BY_PROFIT_CLAIM,
    BLOCKED_BY_SECOND_ORDER_REQUEST,
    BLOCKED_BY_SELL_STOP_LOSS_NOT_ABOVE_REFERENCE,
    BLOCKED_BY_SELL_TAKE_PROFIT_NOT_BELOW_REFERENCE,
    SLTP_VALIDATION_READY,
    evaluate_oanda_demo_sltp_validation_correction_v1,
)
from scripts.forex_delivery.run_oanda_demo_sltp_validation_correction_v1 import main


def test_buy_validates_stop_loss_below_and_take_profit_above_reference() -> None:
    decision = evaluate_oanda_demo_sltp_validation_correction_v1(
        _context(direction="BUY", reference_price="1.07050")
    )

    assert decision["classification"] == SLTP_VALIDATION_READY
    assert decision["validation_ready"] is True
    assert decision["safety_proof"]["broker_call_performed"] is False
    assert decision["safety_proof"]["order_placement_performed"] is False


def test_prior_buy_cancel_pattern_blocks_loss_side_take_profit() -> None:
    decision = evaluate_oanda_demo_sltp_validation_correction_v1(
        _context(
            direction="BUY",
            reference_price="1.07150",
            stop_loss="1.07000",
            take_profit="1.07100",
        )
    )

    assert (
        decision["classification"]
        == BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_REFERENCE
    )
    assert decision["validation_ready"] is False


def test_buy_stop_loss_must_be_below_reference() -> None:
    decision = evaluate_oanda_demo_sltp_validation_correction_v1(
        _context(direction="BUY", reference_price="1.07050", stop_loss="1.07050")
    )

    assert (
        decision["classification"]
        == BLOCKED_BY_BUY_STOP_LOSS_NOT_BELOW_REFERENCE
    )


def test_sell_validates_stop_loss_above_and_take_profit_below_reference() -> None:
    decision = evaluate_oanda_demo_sltp_validation_correction_v1(
        _context(
            direction="SELL",
            reference_price="1.07050",
            stop_loss="1.07100",
            take_profit="1.07000",
        )
    )

    assert decision["classification"] == SLTP_VALIDATION_READY
    assert decision["validation_ready"] is True


def test_sell_stop_loss_must_be_above_reference() -> None:
    decision = evaluate_oanda_demo_sltp_validation_correction_v1(
        _context(
            direction="SELL",
            reference_price="1.07050",
            stop_loss="1.07000",
            take_profit="1.07000",
        )
    )

    assert (
        decision["classification"]
        == BLOCKED_BY_SELL_STOP_LOSS_NOT_ABOVE_REFERENCE
    )


def test_sell_take_profit_must_be_below_reference() -> None:
    decision = evaluate_oanda_demo_sltp_validation_correction_v1(
        _context(
            direction="SELL",
            reference_price="1.07050",
            stop_loss="1.07100",
            take_profit="1.07050",
        )
    )

    assert (
        decision["classification"]
        == BLOCKED_BY_SELL_TAKE_PROFIT_NOT_BELOW_REFERENCE
    )


def test_missing_reference_and_invalid_numeric_inputs_block() -> None:
    missing = evaluate_oanda_demo_sltp_validation_correction_v1(
        _context(reference_price="")
    )
    invalid = evaluate_oanda_demo_sltp_validation_correction_v1(
        _context(reference_price="EXAMPLE_REFERENCE_PRICE")
    )

    assert missing["classification"] == BLOCKED_BY_MISSING_REFERENCE_PRICE
    assert invalid["classification"] == BLOCKED_BY_INVALID_NUMERIC_PRICE


def test_boundary_confirmations_block_before_ready() -> None:
    live = _context()
    live["no_live_endpoint_confirmed"] = False
    second = _context()
    second["second_order_requested"] = True
    profit = _context()
    profit["profit_claim_made"] = True

    assert (
        evaluate_oanda_demo_sltp_validation_correction_v1(live)["classification"]
        == BLOCKED_BY_LIVE_ENDPOINT
    )
    assert (
        evaluate_oanda_demo_sltp_validation_correction_v1(second)["classification"]
        == BLOCKED_BY_SECOND_ORDER_REQUEST
    )
    assert (
        evaluate_oanda_demo_sltp_validation_correction_v1(profit)["classification"]
        == BLOCKED_BY_PROFIT_CLAIM
    )


def test_script_print_template_is_sanitized_and_does_not_call_broker(capsys) -> None:
    exit_code = main(["--print-template"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["script_status"] == "SLTP_VALIDATION_TEMPLATE_ONLY"
    assert payload["broker_call_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["live_endpoint_used"] is False
    assert "EXAMPLE_REFERENCE_PRICE" in payload["example_command"]


def test_script_validate_sltp_ready_outputs_sanitized_json(capsys) -> None:
    exit_code = main(
        [
            "--validate-sltp",
            "--instrument",
            "EUR_USD",
            "--direction",
            "BUY",
            "--reference-price",
            "1.07050",
            "--stop-loss",
            "1.07000",
            "--take-profit",
            "1.07100",
            "--i-confirm-demo-only",
            "--i-confirm-no-broker-call",
            "--i-confirm-no-second-order",
            "--i-confirm-no-live-endpoint",
            "--i-confirm-no-profit-claim",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["script_status"] == SLTP_VALIDATION_READY
    assert payload["validation_ready"] is True
    assert payload["broker_call_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["second_order_allowed"] is False


def _context(
    *,
    direction: str = "BUY",
    reference_price: str = "1.07050",
    stop_loss: str = "1.07000",
    take_profit: str = "1.07100",
) -> dict:
    return {
        "instrument": "EUR_USD",
        "direction": direction,
        "reference_price": reference_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "demo_only_confirmed": True,
        "no_broker_call_confirmed": True,
        "no_second_order_confirmed": True,
        "no_live_endpoint_confirmed": True,
        "no_profit_claim_confirmed": True,
        "live_endpoint_requested": False,
        "second_order_requested": False,
        "profit_claim_made": False,
    }
