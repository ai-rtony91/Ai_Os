from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_closed_trade_tpsl_result_capture_v1 import (  # noqa: E402
    BLOCKED_INVALID_EVIDENCE,
    BLOCKED_UNSAFE_EVIDENCE,
    CLOSED_BREAKEVEN_OTHER,
    CLOSED_BY_OTHER_OR_MANUAL,
    CLOSED_BY_STOP_LOSS,
    CLOSED_BY_TAKE_PROFIT,
    CLOSED_REALIZED_LOSS_OTHER,
    CLOSED_REALIZED_PROFIT_OTHER,
    STILL_OPEN_NO_REALIZED_RESULT,
    TRADE_NOT_FOUND,
    evaluate_oanda_closed_trade_tpsl_result_capture_v1,
)
from scripts.forex_delivery.run_oanda_closed_trade_tpsl_result_capture_v1 import (  # noqa: E402
    main as script_main,
)


def safe_flags() -> dict:
    return {
        "execution_authority": {
            "network_allowed": False,
            "broker_call_allowed": False,
            "credential_access_allowed": False,
            "order_placement_allowed": False,
            "order_close_allowed": False,
            "order_mutation_allowed": False,
            "trade_mutation_allowed": False,
            "position_mutation_allowed": False,
            "live_endpoint_allowed": False,
            "live_trading_allowed": False,
            "bucket_update_allowed": False,
        },
        "safety_proof": {
            "broker_network_call_performed": False,
            "credential_read_performed": False,
            "order_placement_performed": False,
            "order_close_performed": False,
            "bucket_update_performed": False,
        },
    }


def open_trade(unrealized_pl: str = "-0.0001") -> dict:
    return {
        **safe_flags(),
        "open_trade_evidence": [
            {
                "id": "328",
                "instrument": "EUR_USD",
                "currentUnits": "1",
                "unrealizedPL": unrealized_pl,
                "takeProfitOrder": {"id": "329"},
                "stopLossOrder": {"id": "330"},
            }
        ],
        "pl_evidence": {
            "open_trade_evidence": [
                {
                    "trade_id": "328",
                    "instrument": "EUR_USD",
                    "currentUnits": "1",
                    "unrealizedPL": unrealized_pl,
                }
            ],
            "realized_pl_values": [],
            "realized_pl_total": "0",
        },
    }


def closed_trade(
    *,
    realized_pl: str,
    order_id: str | None = None,
    reason: str = "CLIENT_ORDER",
    order_field: str | None = None,
) -> dict:
    trade = {
        "id": "328",
        "instrument": "EUR_USD",
        "state": "CLOSED",
        "currentUnits": "0",
        "closeTime": "SANITIZED_TIMESTAMP",
        "realizedPL": realized_pl,
    }
    if order_field == "tp":
        trade["takeProfitOrder"] = {"id": "329"}
    if order_field == "sl":
        trade["stopLossOrder"] = {"id": "330"}
    transaction = {
        "id": order_id or "410",
        "type": "ORDER_FILL",
        "reason": reason,
        "tradesClosed": [{"tradeID": "328", "realizedPL": realized_pl}],
    }
    if order_id:
        transaction["orderID"] = order_id
    return {
        **safe_flags(),
        "open_trade_evidence": [],
        "closed_trade_evidence": [trade],
        "transactions": [transaction],
    }


def run_script(args: list[str]) -> tuple[int, dict]:
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def test_still_open_trade_328_returns_no_realized_result() -> None:
    result = evaluate_oanda_closed_trade_tpsl_result_capture_v1(open_trade())

    assert result["status"] == STILL_OPEN_NO_REALIZED_RESULT
    assert result["is_open"] is True
    assert result["is_closed"] is False
    assert result["realized_pl"] is None
    assert result["profit_claimed"] is False
    assert result["no_new_order_authorized"] is True


def test_closed_by_tp_positive_claims_profit() -> None:
    result = evaluate_oanda_closed_trade_tpsl_result_capture_v1(
        closed_trade(
            realized_pl="0.0012",
            order_id="329",
            reason="TAKE_PROFIT_ORDER",
            order_field="tp",
        )
    )

    assert result["status"] == CLOSED_BY_TAKE_PROFIT
    assert result["matched_take_profit_order_id"] == "329"
    assert result["realized_pl"] == "0.0012"
    assert result["profit_claimed"] is True
    assert result["no_bucket_update_performed"] is True


def test_closed_by_sl_negative_does_not_claim_profit() -> None:
    result = evaluate_oanda_closed_trade_tpsl_result_capture_v1(
        closed_trade(
            realized_pl="-0.0010",
            order_id="330",
            reason="STOP_LOSS_ORDER",
            order_field="sl",
        )
    )

    assert result["status"] == CLOSED_BY_STOP_LOSS
    assert result["matched_stop_loss_order_id"] == "330"
    assert result["profit_claimed"] is False


def test_closed_manual_other_positive_returns_other_profit() -> None:
    result = evaluate_oanda_closed_trade_tpsl_result_capture_v1(
        closed_trade(realized_pl="0.0006")
    )

    assert result["status"] == CLOSED_REALIZED_PROFIT_OTHER
    assert result["profit_claimed"] is True


def test_closed_manual_other_loss_returns_other_loss() -> None:
    result = evaluate_oanda_closed_trade_tpsl_result_capture_v1(
        closed_trade(realized_pl="-0.0006")
    )

    assert result["status"] == CLOSED_REALIZED_LOSS_OTHER
    assert result["profit_claimed"] is False


def test_closed_breakeven_returns_breakeven_other() -> None:
    result = evaluate_oanda_closed_trade_tpsl_result_capture_v1(
        closed_trade(realized_pl="0.0000")
    )

    assert result["status"] == CLOSED_BREAKEVEN_OTHER
    assert result["profit_claimed"] is False


def test_closed_manual_without_realized_pl_returns_other_or_manual() -> None:
    result = evaluate_oanda_closed_trade_tpsl_result_capture_v1(
        {
            **safe_flags(),
            "open_trade_evidence": [],
            "trade_evidence": {
                "tradeID": "328",
                "instrument": "EUR_USD",
                "is_closed": True,
                "currentUnits": "0",
            },
        }
    )

    assert result["status"] == CLOSED_BY_OTHER_OR_MANUAL
    assert result["is_closed"] is True
    assert result["realized_pl"] is None
    assert result["profit_claimed"] is False


def test_trade_not_found_returns_trade_not_found() -> None:
    result = evaluate_oanda_closed_trade_tpsl_result_capture_v1(
        {
            **safe_flags(),
            "open_trade_evidence": [],
            "closed_trade_evidence": [],
            "transactions": [],
        }
    )

    assert result["status"] == TRADE_NOT_FOUND
    assert result["is_open"] is False
    assert result["is_closed"] is False


def test_invalid_conflicting_tp_sl_evidence_blocks_without_profit_claim() -> None:
    result = evaluate_oanda_closed_trade_tpsl_result_capture_v1(
        {
            **safe_flags(),
            "open_trade_evidence": [],
            "closed_trade_evidence": [
                {
                    "tradeID": "328",
                    "instrument": "EUR_USD",
                    "state": "CLOSED",
                    "currentUnits": "0",
                    "realizedPL": "0.0012",
                    "takeProfitOrder": {"id": "329"},
                    "stopLossOrder": {"id": "330"},
                }
            ],
            "transactions": [
                {
                    "orderID": "329",
                    "reason": "TAKE_PROFIT_ORDER",
                    "tradesClosed": [{"tradeID": "328", "realizedPL": "0.0012"}],
                },
                {
                    "orderID": "330",
                    "reason": "STOP_LOSS_ORDER",
                    "tradesClosed": [{"tradeID": "328", "realizedPL": "0.0012"}],
                },
            ],
        }
    )

    assert result["status"] == BLOCKED_INVALID_EVIDENCE
    assert "conflicting_take_profit_and_stop_loss_order_match" in result["blockers"]
    assert result["profit_claimed"] is False


def test_unsafe_authority_or_performed_flag_rejects() -> None:
    evidence = open_trade()
    evidence["broker_network_call_performed"] = True

    result = evaluate_oanda_closed_trade_tpsl_result_capture_v1(evidence)

    assert result["status"] == BLOCKED_UNSAFE_EVIDENCE
    assert "unsafe_read_only_trade_result_evidence_broker_network_call_performed_true" in result["blockers"]
    assert result["profit_claimed"] is False


def test_open_unrealized_positive_does_not_claim_profit() -> None:
    result = evaluate_oanda_closed_trade_tpsl_result_capture_v1(
        open_trade(unrealized_pl="0.0008")
    )

    assert result["status"] == STILL_OPEN_NO_REALIZED_RESULT
    assert result["unrealized_pl"] == "0.0008"
    assert result["profit_claimed"] is False


def test_decision_pl_evidence_shape_is_supported() -> None:
    result = evaluate_oanda_closed_trade_tpsl_result_capture_v1(
        {
            **safe_flags(),
            "open_trade_evidence": [],
            "decision": {
                "pl_evidence": {
                    "realized_pl_values": ["0.0002", "0.0003"],
                    "open_trade_evidence": [],
                }
            },
            "trade_evidence": {
                "tradeID": "328",
                "state": "CLOSED",
                "currentUnits": "0",
            },
        }
    )

    assert result["status"] == CLOSED_REALIZED_PROFIT_OTHER
    assert result["realized_pl"] == "0.0005"
    assert result["profit_claimed"] is True


def test_cli_template_prints_sanitized_json() -> None:
    code, payload = run_script(["--print-template"])

    assert code == 0
    assert payload["script_status"] == (
        "OANDA_CLOSED_TRADE_TPSL_RESULT_CAPTURE_TEMPLATE_ONLY"
    )
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["order_close_performed"] is False
    assert payload["bucket_update_performed"] is False


def test_cli_packet_sample_alias_closed_by_tp_prints_sanitized_json() -> None:
    code, payload = run_script(["--sample", "closed-by-tp"])

    assert code == 0
    assert payload["sample"] == "closed-by-tp"
    assert set(payload["decisions"]) == {"closed-by-tp"}
    assert payload["decisions"]["closed-by-tp"]["status"] == CLOSED_BY_TAKE_PROFIT
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False


def test_cli_default_samples_print_sanitized_json_with_false_flags() -> None:
    code, payload = run_script([])

    assert code == 0
    assert payload["script_status"] == (
        "OANDA_CLOSED_TRADE_TPSL_RESULT_CAPTURE_DRY_RUN_SAMPLES"
    )
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["order_close_performed"] is False
    assert payload["bucket_update_performed"] is False
    assert set(payload["decisions"]) >= {
        "still-open",
        "closed-by-tp",
        "closed-by-sl",
        "closed-other-profit",
        "closed-other-loss",
        "breakeven",
        "trade-not-found",
    }
    for decision in payload["decisions"].values():
        assert decision["broker_network_call_performed"] is False
        assert decision["credential_read_performed"] is False
        assert decision["order_placement_performed"] is False
        assert decision["order_close_performed"] is False
        assert decision["bucket_update_performed"] is False
