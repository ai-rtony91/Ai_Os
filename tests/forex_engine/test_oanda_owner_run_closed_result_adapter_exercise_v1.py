from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_owner_run_closed_result_adapter_exercise_v1 import (  # noqa: E402
    OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID,
    OWNER_RUN_CLOSED_BREAKEVEN_OTHER,
    OWNER_RUN_CLOSED_BY_STOP_LOSS,
    OWNER_RUN_CLOSED_BY_TAKE_PROFIT,
    OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER,
    OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER,
    OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT,
    OWNER_RUN_TRADE_NOT_FOUND,
    evaluate_oanda_owner_run_closed_result_adapter_exercise_v1,
    oanda_owner_run_closed_result_adapter_exercise_default_samples_v1,
)
from scripts.forex_delivery.run_oanda_owner_run_closed_result_adapter_exercise_v1 import (  # noqa: E402
    main as script_main,
)


def samples() -> dict:
    return oanda_owner_run_closed_result_adapter_exercise_default_samples_v1()


def run_script(args: list[str]) -> tuple[int, dict]:
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def assert_exercise_safety_false(payload: dict) -> None:
    false_flags = (
        "broker_network_call_performed",
        "broker_api_call_performed",
        "broker_call_performed",
        "broker_write_performed",
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
        "next_order_authorized",
        "next_trade_authorized",
        "scheduler_started",
        "daemon_started",
        "webhook_called",
        "live_funding_performed",
    )
    for flag in false_flags:
        assert payload[flag] is False
        assert payload["safety_proof"][flag] is False
    assert all(value is False for value in payload["execution_authority"].values())
    assert payload["no_new_order_authorized"] is True
    assert payload["no_bucket_update_performed"] is True
    assert payload["no_live_funding_authorized"] is True


def test_still_open_sample_returns_owner_run_still_open() -> None:
    decision = evaluate_oanda_owner_run_closed_result_adapter_exercise_v1(
        samples()["still-open"]
    )

    assert decision["exercise_status"] == OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT
    assert decision["adapter_status"] == "ADAPTED_STILL_OPEN_NO_REALIZED_RESULT"
    assert decision["profit_claimed"] is False
    assert decision["unrealized_pl"] == "0.0008"
    assert_exercise_safety_false(decision)


def test_closed_by_tp_sample_returns_owner_run_tp_and_claims_profit() -> None:
    decision = evaluate_oanda_owner_run_closed_result_adapter_exercise_v1(
        samples()["closed-by-tp"]
    )

    assert decision["exercise_status"] == OWNER_RUN_CLOSED_BY_TAKE_PROFIT
    assert decision["adapter_status"] == "ADAPTED_CLOSED_BY_TAKE_PROFIT"
    assert decision["matched_take_profit_order_id"] == "329"
    assert decision["profit_claimed"] is True
    assert_exercise_safety_false(decision)


def test_closed_by_sl_sample_returns_owner_run_sl_without_profit() -> None:
    decision = evaluate_oanda_owner_run_closed_result_adapter_exercise_v1(
        samples()["closed-by-sl"]
    )

    assert decision["exercise_status"] == OWNER_RUN_CLOSED_BY_STOP_LOSS
    assert decision["adapter_status"] == "ADAPTED_CLOSED_BY_STOP_LOSS"
    assert decision["matched_stop_loss_order_id"] == "330"
    assert decision["profit_claimed"] is False
    assert_exercise_safety_false(decision)


def test_other_profit_sample_returns_owner_run_other_profit() -> None:
    decision = evaluate_oanda_owner_run_closed_result_adapter_exercise_v1(
        samples()["closed-other-profit"]
    )

    assert decision["exercise_status"] == OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER
    assert decision["profit_claimed"] is True


def test_other_loss_sample_returns_owner_run_other_loss() -> None:
    decision = evaluate_oanda_owner_run_closed_result_adapter_exercise_v1(
        samples()["closed-other-loss"]
    )

    assert decision["exercise_status"] == OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER
    assert decision["profit_claimed"] is False


def test_breakeven_sample_returns_owner_run_breakeven() -> None:
    decision = evaluate_oanda_owner_run_closed_result_adapter_exercise_v1(
        samples()["breakeven"]
    )

    assert decision["exercise_status"] == OWNER_RUN_CLOSED_BREAKEVEN_OTHER
    assert decision["realized_pl"] == "0.0000"
    assert decision["profit_claimed"] is False


def test_trade_not_found_sample_returns_owner_run_trade_not_found() -> None:
    decision = evaluate_oanda_owner_run_closed_result_adapter_exercise_v1(
        samples()["trade-not-found"]
    )

    assert decision["exercise_status"] == OWNER_RUN_TRADE_NOT_FOUND
    assert decision["profit_claimed"] is False


def test_unsafe_value_blocks_before_adapter() -> None:
    decision = evaluate_oanda_owner_run_closed_result_adapter_exercise_v1(
        {
            "token": "owner-runtime-token-value",
            "pl_evidence": {
                "open_trade_evidence": [],
                "realized_pl_values": [],
            },
        }
    )

    assert decision["exercise_status"] == OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID
    assert decision["adapter_decision"] is None
    assert "unsafe_owner_run_capture_json_token_present" in decision["blockers"]
    assert decision["profit_claimed"] is False


def test_open_unrealized_positive_does_not_claim_profit() -> None:
    capture = samples()["still-open"]
    capture["decision"]["pl_evidence"]["open_trade_evidence"][0][
        "unrealizedPL"
    ] = "0.0042"

    decision = evaluate_oanda_owner_run_closed_result_adapter_exercise_v1(capture)

    assert decision["exercise_status"] == OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT
    assert decision["unrealized_pl"] == "0.0042"
    assert decision["realized_pl"] is None
    assert decision["profit_claimed"] is False


def test_cli_template_prints_sanitized_false_safety_flags() -> None:
    code, payload = run_script(["--print-template"])

    assert code == 0
    assert payload["script_status"] == (
        "OANDA_OWNER_RUN_CLOSED_RESULT_ADAPTER_EXERCISE_TEMPLATE_ONLY"
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
        "OANDA_OWNER_RUN_CLOSED_RESULT_ADAPTER_EXERCISE_DRY_RUN_SAMPLES"
    )
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["bucket_update_performed"] is False
    assert set(payload["decisions"]) == set(samples())
    for decision in payload["decisions"].values():
        assert_exercise_safety_false(decision)


def test_cli_input_json_valid_object_works_using_tmp_path(tmp_path: Path) -> None:
    input_path = tmp_path / "owner_capture.json"
    input_path.write_text(json.dumps(samples()["closed-by-tp"]), encoding="utf-8")

    code, payload = run_script(["--input-json", str(input_path)])

    assert code == 0
    assert payload["script_status"] == (
        "OANDA_OWNER_RUN_CLOSED_RESULT_ADAPTER_EXERCISE_INPUT_JSON_EVALUATED"
    )
    assert payload["raw_input_persisted_here"] is False
    assert payload["decision"]["exercise_status"] == OWNER_RUN_CLOSED_BY_TAKE_PROFIT
    assert payload["decision"]["profit_claimed"] is True


def test_cli_invalid_json_returns_sanitized_blocked_json(tmp_path: Path) -> None:
    input_path = tmp_path / "invalid_owner_capture.json"
    input_path.write_text("{not valid json", encoding="utf-8")

    code, payload = run_script(["--input-json", str(input_path)])

    assert code == 1
    assert payload["script_status"] == (
        "OANDA_OWNER_RUN_CLOSED_RESULT_ADAPTER_EXERCISE_INPUT_JSON_BLOCKED"
    )
    assert payload["blockers"] == ["input_json_invalid_json"]
    assert payload["decision"]["exercise_status"] == OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID
    assert payload["raw_input_persisted_here"] is False
