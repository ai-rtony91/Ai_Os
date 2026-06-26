from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.forex_engine import oanda_owner_run_live_microtrade_result_contract_v1 as contract
from automation.forex_engine import oanda_owner_run_live_microtrade_result_quality_gate_v1 as quality


REPO_ROOT = Path(__file__).resolve().parents[2]


def _result(builder=quality.build_sample_profit_result_input):
    return quality.evaluate_oanda_owner_run_live_microtrade_result_quality_gate(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (
            quality.build_sample_profit_result_input,
            quality.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_READY_FOR_OWNER_REVIEW,
        ),
        (
            quality.build_sample_loss_result_input,
            quality.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_READY_FOR_OWNER_REVIEW,
        ),
        (
            quality.build_sample_breakeven_result_input,
            quality.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_READY_FOR_OWNER_REVIEW,
        ),
        (
            quality.build_sample_missing_owner_result_input,
            quality.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_REQUIRE_MORE_EVIDENCE,
        ),
        (
            quality.build_sample_unsafe_result_input,
            quality.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_BLOCKED_UNSAFE,
        ),
    ),
)
def test_quality_sample_classifications(builder, classification: str):
    assert _result(builder).classification == classification


def test_quality_version_constant():
    assert quality.VERSION == "oanda_owner_run_live_microtrade_result_quality_gate_v1"


@pytest.mark.parametrize("check_name", quality.REQUIRED_QUALITY_CHECKS)
def test_quality_profit_sample_has_required_ready_checks(check_name: str):
    assert check_name in _result().ready_checks


@pytest.mark.parametrize(
    ("field_name", "missing_check"),
    (
        ("trade_closed", "trade_closed"),
        ("realized_pl", "realized_pl_present"),
        ("realized_r", "realized_r_present"),
        ("spread_observed", "spread_observed_present"),
        ("slippage_observed", "slippage_observed_present"),
        ("planned_max_loss", "planned_max_loss_present"),
        ("one_shot_only_confirmed", "one_shot_confirmed"),
        ("no_repeat_execution_confirmed", "no_repeat_confirmed"),
        ("evidence_references_sanitized", "evidence_references_sanitized"),
        ("post_trade_capture_evidence_present", "post_trade_capture_evidence_present"),
    ),
)
def test_quality_requires_more_evidence_when_quality_field_missing(field_name: str, missing_check: str):
    sample = quality.build_sample_profit_result_input()
    payload = dict(sample.intake_input.owner_result or {})
    if field_name in {
        "trade_closed",
        "one_shot_only_confirmed",
        "no_repeat_execution_confirmed",
        "post_trade_capture_evidence_present",
    }:
        payload[field_name] = False
    else:
        payload.pop(field_name)
    result = quality.evaluate_oanda_owner_run_live_microtrade_result_quality_gate(
        {"intake_input": {"owner_result": payload}}
    )
    assert result.classification in {
        quality.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_REQUIRE_MORE_EVIDENCE,
        quality.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_BLOCKED_UNSAFE,
    }
    assert missing_check in result.missing_checks or result.blocked_items


@pytest.mark.parametrize("flag_name", contract.PROTECTED_FLAG_NAMES)
def test_quality_output_protected_flags_false(flag_name: str):
    result = _result()
    assert result.protected_flags[flag_name] is False
    assert getattr(result, flag_name) is False


@pytest.mark.parametrize(
    "builder",
    (
        quality.build_sample_profit_result_input,
        quality.build_sample_loss_result_input,
        quality.build_sample_breakeven_result_input,
        quality.build_sample_missing_owner_result_input,
        quality.build_sample_unsafe_result_input,
    ),
)
def test_quality_json_serializable_outputs(builder):
    json.dumps(quality.to_jsonable_dict(_result(builder)))


@pytest.mark.parametrize(
    "builder",
    (
        quality.build_sample_profit_result_input,
        quality.build_sample_loss_result_input,
        quality.build_sample_breakeven_result_input,
        quality.build_sample_missing_owner_result_input,
        quality.build_sample_unsafe_result_input,
    ),
)
def test_quality_deterministic_outputs(builder):
    assert quality.to_jsonable_dict(_result(builder)) == quality.to_jsonable_dict(_result(builder))


def test_quality_operator_text_output():
    assert "Result quality status" in quality.to_operator_text(_result())


def test_quality_markdown_output():
    assert quality.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Owner-Run Live Microtrade Result Quality Gate V1"
    )


def test_quality_missing_owner_not_owner_review_allowed():
    assert _result(quality.build_sample_missing_owner_result_input).owner_review_allowed is False


def test_quality_profit_owner_review_allowed():
    assert _result().owner_review_allowed is True


def test_quality_blocks_unsanitized_evidence_reference():
    sample = quality.build_sample_profit_result_input()
    payload = dict(sample.intake_input.owner_result or {})
    payload["evidence_references_sanitized"] = ("owner_journal",)
    result = quality.evaluate_oanda_owner_run_live_microtrade_result_quality_gate(
        {"intake_input": {"owner_result": payload}}
    )
    assert result.classification == quality.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_REQUIRE_MORE_EVIDENCE
    assert "evidence_references_sanitized" in result.missing_checks


def test_quality_result_capture_only_true():
    assert _result().result_capture_only is True


def test_quality_report_exists():
    assert (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_GATE_V1.md"
    ).exists()

