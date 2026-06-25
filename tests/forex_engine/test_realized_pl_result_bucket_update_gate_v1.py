from __future__ import annotations

from contextlib import redirect_stdout
from copy import deepcopy
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.realized_pl_result_bucket_update_gate_v1 import (  # noqa: E402
    BUCKET_UPDATE_BLOCKED_ALREADY_APPLIED,
    BUCKET_UPDATE_BLOCKED_NO_REALIZED_PL,
    BUCKET_UPDATE_BLOCKED_STILL_OPEN,
    BUCKET_UPDATE_BLOCKED_TRADE_NOT_FOUND,
    BUCKET_UPDATE_BLOCKED_UNSAFE_OR_INVALID,
    BUCKET_UPDATE_ELIGIBLE_BREAKEVEN,
    BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS,
    BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT,
    OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID,
    OWNER_RUN_CLOSED_BREAKEVEN_OTHER,
    OWNER_RUN_CLOSED_BY_STOP_LOSS,
    OWNER_RUN_CLOSED_BY_TAKE_PROFIT,
    OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER,
    OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER,
    OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT,
    OWNER_RUN_TRADE_NOT_FOUND,
    evaluate_realized_pl_result_bucket_update_gate_v1,
    realized_pl_result_bucket_update_gate_samples_v1,
)
from scripts.forex_delivery.run_realized_pl_result_bucket_update_gate_v1 import (  # noqa: E402
    main as script_main,
)


def owner_decision(status: str, realized_pl: str | None = None, **overrides):
    payload = {
        "exercise_status": status,
        "trade_anchor": {"trade_id": "328"},
        "realized_pl": realized_pl,
        "no_new_order_authorized": True,
        "no_bucket_update_performed": True,
        "no_live_funding_authorized": True,
        "execution_authority": {
            "network_allowed": False,
            "broker_call_allowed": False,
            "bucket_update_allowed": False,
            "next_trade_authorized": False,
            "live_funding_allowed": False,
        },
        "safety_proof": {
            "broker_network_call_performed": False,
            "bucket_update_performed": False,
            "next_trade_authorized": False,
            "live_funding_performed": False,
        },
    }
    if status in {
        OWNER_RUN_CLOSED_BY_TAKE_PROFIT,
        OWNER_RUN_CLOSED_BY_STOP_LOSS,
        OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER,
        OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER,
        OWNER_RUN_CLOSED_BREAKEVEN_OTHER,
    }:
        payload["classifier_decision"] = {"is_closed": True}
    payload.update(overrides)
    return payload


def evaluate(decision: dict, bucket_state: dict | None = None):
    return evaluate_realized_pl_result_bucket_update_gate_v1(decision, bucket_state)


def run_script(args: list[str]) -> tuple[int, dict]:
    stream = StringIO()
    with redirect_stdout(stream):
        try:
            code = script_main(args)
        except SystemExit as exc:
            code = int(exc.code)
    return code, json.loads(stream.getvalue())


def assert_gate_safety_false(result: dict) -> None:
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
        "bucket_mutation_performed",
        "result_bucket_update_performed",
        "result_bucket_mutation_performed",
        "next_order_authorized",
        "next_trade_authorized",
        "next_allocation_authorized",
        "scheduler_started",
        "daemon_started",
        "webhook_called",
        "live_funding_performed",
    )
    for flag in false_flags:
        assert result[flag] is False
        assert result["safety_proof"][flag] is False
    assert all(value is False for value in result["execution_authority"].values())
    assert result["bucket_update_performed"] is False
    assert result["next_trade_authorized"] is False
    assert result["live_funding_authorized"] is False
    assert result["proposed_bucket_delta"]["bucket_delta_applied_here"] is False


def test_take_profit_status_is_profit_bucket_update_eligible() -> None:
    result = evaluate(owner_decision(OWNER_RUN_CLOSED_BY_TAKE_PROFIT, "0.0012"))

    assert result["gate_status"] == BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT
    assert result["bucket_update_authorized"] is True
    assert result["realized_pl"] == "0.0012"
    assert result["proposed_bucket_delta"]["bucket_delta"] == "0.0012"
    assert_gate_safety_false(result)


def test_other_profit_status_is_profit_bucket_update_eligible() -> None:
    result = evaluate(
        owner_decision(OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER, "0.0006")
    )

    assert result["gate_status"] == BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT
    assert result["proposed_bucket_delta"]["bucket_delta"] == "0.0006"


def test_stop_loss_status_is_loss_bucket_update_eligible() -> None:
    result = evaluate(owner_decision(OWNER_RUN_CLOSED_BY_STOP_LOSS, "-0.0010"))

    assert result["gate_status"] == BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS
    assert result["bucket_update_authorized"] is True
    assert result["proposed_bucket_delta"]["bucket_delta"] == "-0.0010"
    assert_gate_safety_false(result)


def test_other_loss_status_is_loss_bucket_update_eligible() -> None:
    result = evaluate(
        owner_decision(OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER, "-0.0006")
    )

    assert result["gate_status"] == BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS
    assert result["proposed_bucket_delta"]["bucket_delta"] == "-0.0006"


def test_breakeven_status_is_breakeven_bucket_update_eligible() -> None:
    result = evaluate(owner_decision(OWNER_RUN_CLOSED_BREAKEVEN_OTHER, "0.0000"))

    assert result["gate_status"] == BUCKET_UPDATE_ELIGIBLE_BREAKEVEN
    assert result["bucket_update_authorized"] is True
    assert result["proposed_bucket_delta"]["bucket_delta"] == "0.0000"
    assert_gate_safety_false(result)


def test_still_open_status_blocks_bucket_update() -> None:
    result = evaluate(owner_decision(OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT))

    assert result["gate_status"] == BUCKET_UPDATE_BLOCKED_STILL_OPEN
    assert result["bucket_update_authorized"] is False
    assert "owner_run_trade_still_open_no_realized_result" in result["blockers"]


def test_trade_not_found_status_blocks_bucket_update() -> None:
    result = evaluate(owner_decision(OWNER_RUN_TRADE_NOT_FOUND))

    assert result["gate_status"] == BUCKET_UPDATE_BLOCKED_TRADE_NOT_FOUND
    assert result["bucket_update_authorized"] is False
    assert "owner_run_trade_328_not_found" in result["blockers"]


def test_upstream_unsafe_status_blocks_bucket_update() -> None:
    result = evaluate(owner_decision(OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID))

    assert result["gate_status"] == BUCKET_UPDATE_BLOCKED_UNSAFE_OR_INVALID
    assert result["bucket_update_authorized"] is False
    assert "upstream_owner_run_blocked_unsafe_or_invalid" in result["blockers"]


def test_missing_realized_pl_blocks_closed_result() -> None:
    result = evaluate(owner_decision(OWNER_RUN_CLOSED_BY_TAKE_PROFIT))

    assert result["gate_status"] == BUCKET_UPDATE_BLOCKED_NO_REALIZED_PL
    assert "closed_owner_run_result_requires_numeric_realized_pl" in result["blockers"]


def test_realized_pl_sign_mismatch_blocks_as_invalid() -> None:
    result = evaluate(owner_decision(OWNER_RUN_CLOSED_BY_STOP_LOSS, "0.0010"))

    assert result["gate_status"] == BUCKET_UPDATE_BLOCKED_UNSAFE_OR_INVALID
    assert "closed_loss_owner_status_requires_negative_realized_pl" in result[
        "blockers"
    ]


def test_upstream_no_new_order_authorized_flag_is_required() -> None:
    result = evaluate(
        owner_decision(
            OWNER_RUN_CLOSED_BY_TAKE_PROFIT,
            "0.0012",
            no_new_order_authorized=False,
        )
    )

    assert result["gate_status"] == BUCKET_UPDATE_BLOCKED_UNSAFE_OR_INVALID
    assert "upstream_no_new_order_authorized_must_be_true" in result["blockers"]


def test_upstream_no_bucket_update_performed_flag_is_required() -> None:
    result = evaluate(
        owner_decision(
            OWNER_RUN_CLOSED_BY_TAKE_PROFIT,
            "0.0012",
            no_bucket_update_performed=False,
        )
    )

    assert result["gate_status"] == BUCKET_UPDATE_BLOCKED_UNSAFE_OR_INVALID
    assert "upstream_no_bucket_update_performed_must_be_true" in result["blockers"]


def test_upstream_no_live_funding_authorized_flag_is_required() -> None:
    result = evaluate(
        owner_decision(
            OWNER_RUN_CLOSED_BY_TAKE_PROFIT,
            "0.0012",
            no_live_funding_authorized=False,
        )
    )

    assert result["gate_status"] == BUCKET_UPDATE_BLOCKED_UNSAFE_OR_INVALID
    assert "upstream_no_live_funding_authorized_must_be_true" in result["blockers"]


def test_bucket_state_trade_328_already_applied_blocks_idempotently() -> None:
    result = evaluate(
        owner_decision(OWNER_RUN_CLOSED_BY_TAKE_PROFIT, "0.0012"),
        {"applied_trade_ids": ["328"]},
    )

    assert result["gate_status"] == BUCKET_UPDATE_BLOCKED_ALREADY_APPLIED
    assert result["bucket_update_authorized"] is False
    assert "trade_328_bucket_update_already_applied" in result["blockers"]
    assert result["proposed_bucket_delta"]["bucket_delta"] == "0"


def test_bucket_state_nested_applied_result_blocks_idempotently() -> None:
    result = evaluate(
        owner_decision(OWNER_RUN_CLOSED_BY_TAKE_PROFIT, "0.0012"),
        {"applied_results": [{"trade_id": "328", "realized_pl_applied": True}]},
    )

    assert result["gate_status"] == BUCKET_UPDATE_BLOCKED_ALREADY_APPLIED


def test_bucket_state_is_not_mutated() -> None:
    bucket_state = {"applied_trade_ids": [], "metadata": {"owner": "test"}}
    before = deepcopy(bucket_state)

    result = evaluate(owner_decision(OWNER_RUN_CLOSED_BY_TAKE_PROFIT, "0.0012"), bucket_state)

    assert result["gate_status"] == BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT
    assert bucket_state == before


def test_samples_cover_required_cli_names() -> None:
    samples = realized_pl_result_bucket_update_gate_samples_v1()

    assert set(samples) == {
        "profit",
        "loss",
        "breakeven",
        "still-open",
        "trade-not-found",
        "unsafe",
        "already-applied",
    }


def test_cli_print_template_outputs_json_only_and_false_safety_flags() -> None:
    code, payload = run_script(["--print-template"])

    assert code == 0
    assert payload["script_status"] == (
        "REALIZED_PL_RESULT_BUCKET_UPDATE_GATE_TEMPLATE_ONLY"
    )
    assert payload["template"]["runtime_input_rule"]["bucket_mutation_supported"] is False
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["bucket_update_performed"] is False
    assert payload["next_trade_authorized"] is False
    assert payload["live_funding_performed"] is False


def test_cli_sample_all_outputs_all_decisions_with_false_safety_flags() -> None:
    code, payload = run_script(["--sample", "all"])

    assert code == 0
    assert payload["script_status"] == (
        "REALIZED_PL_RESULT_BUCKET_UPDATE_GATE_DRY_RUN_SAMPLES"
    )
    assert set(payload["decisions"]) == set(
        realized_pl_result_bucket_update_gate_samples_v1()
    )
    assert payload["broker_network_call_performed"] is False
    assert payload["bucket_update_performed"] is False
    assert payload["next_trade_authorized"] is False
    for decision in payload["decisions"].values():
        assert_gate_safety_false(decision)


def test_cli_sample_already_applied_returns_already_applied_block() -> None:
    code, payload = run_script(["--sample", "already-applied"])

    assert code == 0
    decision = payload["decisions"]["already-applied"]
    assert decision["gate_status"] == BUCKET_UPDATE_BLOCKED_ALREADY_APPLIED
    assert decision["bucket_update_authorized"] is False


def test_cli_invalid_argument_prints_json_block() -> None:
    code, payload = run_script(["--unknown"])

    assert code == 2
    assert payload["script_status"] == (
        "REALIZED_PL_RESULT_BUCKET_UPDATE_GATE_INPUT_BLOCKED"
    )
    assert payload["broker_network_call_performed"] is False
    assert payload["bucket_update_performed"] is False
