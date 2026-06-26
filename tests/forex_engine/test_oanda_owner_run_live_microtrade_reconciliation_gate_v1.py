from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from automation.forex_engine import oanda_owner_run_live_microtrade_reconciliation_gate_v1 as reconcile
from automation.forex_engine import oanda_owner_run_live_microtrade_result_contract_v1 as contract


REPO_ROOT = Path(__file__).resolve().parents[2]


def _result(builder=reconcile.build_sample_profit_result_input):
    return reconcile.evaluate_oanda_owner_run_live_microtrade_reconciliation_gate(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (
            reconcile.build_sample_profit_result_input,
            reconcile.OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_READY_FOR_OWNER_REVIEW,
        ),
        (
            reconcile.build_sample_loss_result_input,
            reconcile.OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_READY_FOR_OWNER_REVIEW,
        ),
        (
            reconcile.build_sample_breakeven_result_input,
            reconcile.OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_READY_FOR_OWNER_REVIEW,
        ),
        (
            reconcile.build_sample_missing_owner_result_input,
            reconcile.OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_REQUIRE_MORE_EVIDENCE,
        ),
        (
            reconcile.build_sample_unsafe_result_input,
            reconcile.OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_BLOCKED_UNSAFE,
        ),
    ),
)
def test_reconciliation_sample_classifications(builder, classification: str):
    assert _result(builder).classification == classification


def test_reconciliation_version_constant():
    assert reconcile.VERSION == "oanda_owner_run_live_microtrade_reconciliation_gate_v1"


@pytest.mark.parametrize("check_name", reconcile.REQUIRED_RECONCILIATION_CHECKS)
def test_reconciliation_profit_sample_has_ready_checks(check_name: str):
    assert check_name in _result().ready_checks


@pytest.mark.parametrize(
    ("field_name", "value", "missing_check"),
    (
        ("planned_instrument", "GBP_USD", "planned_instrument_matches_actual_instrument"),
        ("planned_direction", "short", "planned_direction_matches_actual_direction"),
        ("actual_units", Decimal("2"), "actual_units_within_max_units"),
        ("close_time_utc", "2026-06-25T13:59:00Z", "close_time_after_open_time"),
        ("evidence_references_sanitized", ("owner_journal",), "evidence_references_sanitized"),
        ("post_trade_capture_complete", False, "post_trade_capture_complete"),
    ),
)
def test_reconciliation_requires_more_evidence_for_mismatch(field_name: str, value, missing_check: str):
    sample = reconcile.build_sample_profit_result_input()
    payload = dict(sample.intake_input.owner_result or {})
    payload[field_name] = value
    result = reconcile.evaluate_oanda_owner_run_live_microtrade_reconciliation_gate(
        {"intake_input": {"owner_result": payload}}
    )
    assert result.classification == reconcile.OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_REQUIRE_MORE_EVIDENCE
    assert missing_check in result.missing_checks


def test_reconciliation_actual_units_within_max_units():
    result = _result()
    assert result.actual_units == Decimal("1")
    assert result.max_units == Decimal("1")
    assert "actual_units_within_max_units" in result.ready_checks


def test_reconciliation_close_after_open():
    assert "close_time_after_open_time" in _result().ready_checks


@pytest.mark.parametrize("flag_name", contract.PROTECTED_FLAG_NAMES)
def test_reconciliation_output_protected_flags_false(flag_name: str):
    result = _result()
    assert result.protected_flags[flag_name] is False
    assert getattr(result, flag_name) is False


@pytest.mark.parametrize(
    "builder",
    (
        reconcile.build_sample_profit_result_input,
        reconcile.build_sample_loss_result_input,
        reconcile.build_sample_breakeven_result_input,
        reconcile.build_sample_missing_owner_result_input,
        reconcile.build_sample_unsafe_result_input,
    ),
)
def test_reconciliation_json_serializable_outputs(builder):
    json.dumps(reconcile.to_jsonable_dict(_result(builder)))


@pytest.mark.parametrize(
    "builder",
    (
        reconcile.build_sample_profit_result_input,
        reconcile.build_sample_loss_result_input,
        reconcile.build_sample_breakeven_result_input,
        reconcile.build_sample_missing_owner_result_input,
        reconcile.build_sample_unsafe_result_input,
    ),
)
def test_reconciliation_deterministic_outputs(builder):
    assert reconcile.to_jsonable_dict(_result(builder)) == reconcile.to_jsonable_dict(_result(builder))


def test_reconciliation_operator_text_output():
    assert "Result reconciliation status" in reconcile.to_operator_text(_result())


def test_reconciliation_markdown_output():
    assert reconcile.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Owner-Run Live Microtrade Reconciliation Gate V1"
    )


def test_reconciliation_result_capture_only_true():
    assert _result().result_capture_only is True


def test_reconciliation_report_exists():
    assert (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_GATE_V1.md"
    ).exists()

