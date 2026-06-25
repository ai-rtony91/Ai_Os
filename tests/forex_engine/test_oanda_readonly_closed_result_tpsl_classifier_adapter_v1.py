from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_readonly_closed_result_tpsl_classifier_adapter_v1 import (  # noqa: E402
    ADAPTED_BLOCKED_UNSAFE_EVIDENCE,
    ADAPTED_CLOSED_BY_STOP_LOSS,
    ADAPTED_CLOSED_BY_TAKE_PROFIT,
    ADAPTED_CLOSED_REALIZED_LOSS_OTHER,
    ADAPTED_CLOSED_REALIZED_PROFIT_OTHER,
    ADAPTED_STILL_OPEN_NO_REALIZED_RESULT,
    ADAPTED_TRADE_NOT_FOUND,
    evaluate_oanda_readonly_closed_result_tpsl_classifier_adapter_v1,
    oanda_readonly_closed_result_tpsl_classifier_adapter_default_samples_v1,
)
from scripts.forex_delivery.run_oanda_readonly_closed_result_tpsl_classifier_adapter_v1 import (  # noqa: E402
    main as script_main,
)


def samples() -> dict:
    return oanda_readonly_closed_result_tpsl_classifier_adapter_default_samples_v1()


def run_script(args: list[str]) -> tuple[int, dict]:
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def assert_adapter_safety_false(payload: dict) -> None:
    false_flags = (
        "broker_network_call_performed",
        "broker_api_call_performed",
        "credential_read_performed",
        "account_id_read_performed",
        "vault_read_performed",
        "windows_vault_read_performed",
        "dotenv_read",
        "env_read",
        "order_placement_performed",
        "order_close_performed",
        "order_mutation_performed",
        "trade_mutation_performed",
        "position_mutation_performed",
        "orders_endpoint_called",
        "live_endpoint_used",
        "raw_broker_payload_persisted",
        "file_persistence_performed",
        "write_performed",
        "bucket_update_performed",
        "result_bucket_update_performed",
        "scheduler_started",
        "daemon_started",
        "webhook_called",
        "live_funding_performed",
        "next_order_authorized",
        "next_trade_authorized",
    )
    for flag in false_flags:
        assert payload[flag] is False
        assert payload["safety_proof"][flag] is False
    assert all(value is False for value in payload["execution_authority"].values())


def test_still_open_capture_adapts_to_still_open_no_realized_result() -> None:
    decision = evaluate_oanda_readonly_closed_result_tpsl_classifier_adapter_v1(
        samples()["capture-still-open"]
    )

    assert decision["adapter_status"] == ADAPTED_STILL_OPEN_NO_REALIZED_RESULT
    assert decision["classifier_status"] == "STILL_OPEN_NO_REALIZED_RESULT"
    assert decision["profit_claimed"] is False
    assert decision["classifier_decision"]["is_open"] is True
    assert_adapter_safety_false(decision)


def test_closed_by_tp_capture_adapts_and_claims_profit() -> None:
    decision = evaluate_oanda_readonly_closed_result_tpsl_classifier_adapter_v1(
        samples()["capture-closed-by-tp"]
    )

    assert decision["adapter_status"] == ADAPTED_CLOSED_BY_TAKE_PROFIT
    assert decision["classifier_decision"]["matched_take_profit_order_id"] == "329"
    assert decision["profit_claimed"] is True
    assert decision["no_new_order_authorized"] is True
    assert decision["no_bucket_update_performed"] is True
    assert_adapter_safety_false(decision)


def test_closed_by_sl_capture_adapts_without_profit_claim() -> None:
    decision = evaluate_oanda_readonly_closed_result_tpsl_classifier_adapter_v1(
        samples()["capture-closed-by-sl"]
    )

    assert decision["adapter_status"] == ADAPTED_CLOSED_BY_STOP_LOSS
    assert decision["classifier_decision"]["matched_stop_loss_order_id"] == "330"
    assert decision["profit_claimed"] is False
    assert_adapter_safety_false(decision)


def test_other_profit_capture_adapts_to_other_profit() -> None:
    decision = evaluate_oanda_readonly_closed_result_tpsl_classifier_adapter_v1(
        samples()["capture-closed-other-profit"]
    )

    assert decision["adapter_status"] == ADAPTED_CLOSED_REALIZED_PROFIT_OTHER
    assert decision["profit_claimed"] is True


def test_other_loss_capture_adapts_to_other_loss() -> None:
    decision = evaluate_oanda_readonly_closed_result_tpsl_classifier_adapter_v1(
        samples()["capture-closed-other-loss"]
    )

    assert decision["adapter_status"] == ADAPTED_CLOSED_REALIZED_LOSS_OTHER
    assert decision["profit_claimed"] is False


def test_trade_not_found_capture_adapts_to_trade_not_found() -> None:
    decision = evaluate_oanda_readonly_closed_result_tpsl_classifier_adapter_v1(
        samples()["capture-trade-not-found"]
    )

    assert decision["adapter_status"] == ADAPTED_TRADE_NOT_FOUND
    assert decision["profit_claimed"] is False


def test_unsafe_flag_blocks_before_classifier() -> None:
    decision = evaluate_oanda_readonly_closed_result_tpsl_classifier_adapter_v1(
        samples()["capture-unsafe"]
    )

    assert decision["adapter_status"] == ADAPTED_BLOCKED_UNSAFE_EVIDENCE
    assert decision["classifier_decision"] is None
    assert "unsafe_read_only_capture_output_order_placement_allowed_true" in decision[
        "blockers"
    ]
    assert decision["profit_claimed"] is False


def test_sensitive_value_blocks_before_classifier() -> None:
    capture = {
        "pl_evidence": {
            "open_trade_evidence": [],
            "realized_pl_values": [],
        },
        "token": "owner-runtime-token-value",
    }

    decision = evaluate_oanda_readonly_closed_result_tpsl_classifier_adapter_v1(capture)

    assert decision["adapter_status"] == ADAPTED_BLOCKED_UNSAFE_EVIDENCE
    assert decision["classifier_decision"] is None
    assert "unsafe_read_only_capture_output_token_present" in decision["blockers"]


def test_open_unrealized_positive_does_not_claim_profit() -> None:
    capture = samples()["capture-still-open"]
    capture["decision"]["pl_evidence"]["open_trade_evidence"][0][
        "unrealizedPL"
    ] = "0.0042"

    decision = evaluate_oanda_readonly_closed_result_tpsl_classifier_adapter_v1(capture)

    assert decision["adapter_status"] == ADAPTED_STILL_OPEN_NO_REALIZED_RESULT
    assert decision["classifier_decision"]["unrealized_pl"] == "0.0042"
    assert decision["profit_claimed"] is False


def test_cli_template_prints_sanitized_false_safety_flags() -> None:
    code, payload = run_script(["--print-template"])

    assert code == 0
    assert payload["script_status"] == (
        "OANDA_READONLY_CLOSED_RESULT_TPSL_CLASSIFIER_ADAPTER_TEMPLATE_ONLY"
    )
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["bucket_update_performed"] is False
    assert payload["template"]["runtime_input_rule"][
        "oanda_capture_execution_supported"
    ] is False


def test_cli_default_samples_print_sanitized_false_safety_flags() -> None:
    code, payload = run_script([])

    assert code == 0
    assert payload["script_status"] == (
        "OANDA_READONLY_CLOSED_RESULT_TPSL_CLASSIFIER_ADAPTER_DRY_RUN_SAMPLES"
    )
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["bucket_update_performed"] is False
    assert set(payload["decisions"]) == set(samples())
    for decision in payload["decisions"].values():
        assert_adapter_safety_false(decision)
