from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.forex_engine import oanda_owner_run_live_microtrade_result_contract_v1 as contract
from automation.forex_engine import oanda_owner_run_live_microtrade_result_ledger_bridge_v1 as ledger


REPO_ROOT = Path(__file__).resolve().parents[2]


def _result(builder=ledger.build_sample_profit_result_input):
    return ledger.bridge_oanda_owner_run_live_microtrade_result_to_ledger(builder())


@pytest.mark.parametrize(
    ("builder", "classification", "bucket", "target"),
    (
        (
            ledger.build_sample_profit_result_input,
            ledger.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_READY_FOR_OWNER_REVIEW,
            "profit",
            "live_proof_candidate_review",
        ),
        (
            ledger.build_sample_loss_result_input,
            ledger.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_READY_FOR_OWNER_REVIEW,
            "loss",
            "loss_review",
        ),
        (
            ledger.build_sample_breakeven_result_input,
            ledger.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_REQUIRE_MORE_EVIDENCE,
            "breakeven",
            "more_evidence",
        ),
        (
            ledger.build_sample_missing_owner_result_input,
            ledger.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_REQUIRE_MORE_EVIDENCE,
            "missing",
            "no_owner_result",
        ),
        (
            ledger.build_sample_unsafe_result_input,
            ledger.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_BLOCKED_UNSAFE,
            "unsafe",
            "blocked_unsafe",
        ),
    ),
)
def test_ledger_sample_routing(builder, classification: str, bucket: str, target: str):
    result = _result(builder)
    assert result.classification == classification
    assert result.result_bucket == bucket
    assert target in result.routing_targets


def test_ledger_version_constant():
    assert ledger.VERSION == "oanda_owner_run_live_microtrade_result_ledger_bridge_v1"


def test_ledger_preview_only_true():
    result = _result()
    assert result.preview_only is True
    assert result.ledger_preview["preview_only"] is True


@pytest.mark.parametrize(
    "field_name",
    (
        "repeat_live_trade_allowed",
        "vacation_profit_trial_allowed",
        "compounding_allowed",
        "bank_movement_allowed",
    ),
)
def test_ledger_preview_does_not_approve_restricted_paths(field_name: str):
    assert _result().ledger_preview[field_name] is False


@pytest.mark.parametrize("flag_name", contract.PROTECTED_FLAG_NAMES)
def test_ledger_output_protected_flags_false(flag_name: str):
    result = _result()
    assert result.protected_flags[flag_name] is False
    assert getattr(result, flag_name) is False


@pytest.mark.parametrize(
    "builder",
    (
        ledger.build_sample_profit_result_input,
        ledger.build_sample_loss_result_input,
        ledger.build_sample_breakeven_result_input,
        ledger.build_sample_missing_owner_result_input,
        ledger.build_sample_unsafe_result_input,
    ),
)
def test_ledger_json_serializable_outputs(builder):
    json.dumps(ledger.to_jsonable_dict(_result(builder)))


@pytest.mark.parametrize(
    "builder",
    (
        ledger.build_sample_profit_result_input,
        ledger.build_sample_loss_result_input,
        ledger.build_sample_breakeven_result_input,
        ledger.build_sample_missing_owner_result_input,
        ledger.build_sample_unsafe_result_input,
    ),
)
def test_ledger_deterministic_outputs(builder):
    assert ledger.to_jsonable_dict(_result(builder)) == ledger.to_jsonable_dict(_result(builder))


def test_ledger_operator_text_output():
    assert "Result ledger bridge status" in ledger.to_operator_text(_result())


def test_ledger_markdown_output():
    assert ledger.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Owner-Run Live Microtrade Result Ledger Bridge V1"
    )


def test_ledger_result_capture_only_true():
    assert _result().result_capture_only is True


def test_ledger_loss_routes_to_next_profit_candidate_gate():
    assert "next_profit_candidate_gate" in _result(ledger.build_sample_loss_result_input).routing_targets


def test_ledger_report_exists():
    assert (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_V1.md"
    ).exists()

