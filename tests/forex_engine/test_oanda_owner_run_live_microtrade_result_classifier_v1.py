from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from automation.forex_engine import oanda_owner_run_live_microtrade_result_classifier_v1 as classifier
from automation.forex_engine import oanda_owner_run_live_microtrade_result_contract_v1 as contract


REPO_ROOT = Path(__file__).resolve().parents[2]


def _result(builder=classifier.build_sample_profit_result_input):
    return classifier.classify_oanda_owner_run_live_microtrade_result(builder())


@pytest.mark.parametrize(
    ("builder", "classification", "bucket"),
    (
        (
            classifier.build_sample_profit_result_input,
            classifier.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_PROFIT,
            "profit",
        ),
        (
            classifier.build_sample_loss_result_input,
            classifier.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LOSS,
            "loss",
        ),
        (
            classifier.build_sample_breakeven_result_input,
            classifier.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BREAKEVEN,
            "breakeven",
        ),
        (
            classifier.build_sample_missing_owner_result_input,
            classifier.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_REQUIRE_MORE_EVIDENCE,
            "requires_more_evidence",
        ),
        (
            classifier.build_sample_unsafe_result_input,
            classifier.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BLOCKED_UNSAFE,
            "unsafe",
        ),
    ),
)
def test_classifier_sample_classifications(builder, classification: str, bucket: str):
    result = _result(builder)
    assert result.classification == classification
    assert result.result_bucket == bucket


def test_classifier_version_constant():
    assert classifier.VERSION == "oanda_owner_run_live_microtrade_result_classifier_v1"


def test_classifier_profit_metrics():
    result = _result(classifier.build_sample_profit_result_input)
    assert result.realized_pl == Decimal("0.20")
    assert result.realized_r == Decimal("0.20")
    assert result.profit_loss_label == "profit"
    assert result.max_loss_respected is True
    assert result.risk_limit_respected is True


def test_classifier_loss_metrics():
    result = _result(classifier.build_sample_loss_result_input)
    assert result.realized_pl == Decimal("-0.25")
    assert result.realized_r == Decimal("-0.25")
    assert result.profit_loss_label == "loss"
    assert result.max_loss_respected is True


def test_classifier_breakeven_metrics():
    result = _result(classifier.build_sample_breakeven_result_input)
    assert result.realized_pl == Decimal("0.00")
    assert result.realized_r == Decimal("0.00")
    assert result.profit_loss_label == "breakeven"


def test_classifier_detects_risk_breach():
    sample = contract.build_sample_loss_result_input()
    payload = dict(sample.owner_result or {})
    payload["realized_pl"] = Decimal("-1.25")
    payload["realized_r"] = Decimal("-1.25")
    result = classifier.classify_oanda_owner_run_live_microtrade_result(
        {"quality_gate_input": {"intake_input": {"owner_result": payload}}}
    )
    assert result.classification == classifier.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_BLOCKED_UNSAFE
    assert result.risk_breach is True
    assert result.max_loss_respected is False
    assert "loss_exceeds_planned_max_loss" in result.blocked_items


@pytest.mark.parametrize("flag_name", contract.PROTECTED_FLAG_NAMES)
def test_classifier_output_protected_flags_false(flag_name: str):
    result = _result()
    assert result.protected_flags[flag_name] is False
    assert getattr(result, flag_name) is False


@pytest.mark.parametrize(
    "builder",
    (
        classifier.build_sample_profit_result_input,
        classifier.build_sample_loss_result_input,
        classifier.build_sample_breakeven_result_input,
        classifier.build_sample_missing_owner_result_input,
        classifier.build_sample_unsafe_result_input,
    ),
)
def test_classifier_json_serializable_outputs(builder):
    json.dumps(classifier.to_jsonable_dict(_result(builder)))


@pytest.mark.parametrize(
    "builder",
    (
        classifier.build_sample_profit_result_input,
        classifier.build_sample_loss_result_input,
        classifier.build_sample_breakeven_result_input,
        classifier.build_sample_missing_owner_result_input,
        classifier.build_sample_unsafe_result_input,
    ),
)
def test_classifier_deterministic_outputs(builder):
    assert classifier.to_jsonable_dict(_result(builder)) == classifier.to_jsonable_dict(_result(builder))


@pytest.mark.parametrize(
    ("builder", "expected_text"),
    (
        (classifier.build_sample_profit_result_input, "repeat trading remains blocked"),
        (classifier.build_sample_loss_result_input, "loss review"),
        (classifier.build_sample_breakeven_result_input, "more evidence"),
        (classifier.build_sample_missing_owner_result_input, "requires more evidence"),
        (classifier.build_sample_unsafe_result_input, "blocks routing"),
    ),
)
def test_classifier_owner_review_summary_routes(builder, expected_text: str):
    assert expected_text in _result(builder).owner_review_summary


def test_classifier_operator_text_output():
    assert "Result classifier status" in classifier.to_operator_text(_result())


def test_classifier_markdown_output():
    assert classifier.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Owner-Run Live Microtrade Result Classifier V1"
    )


def test_classifier_result_capture_only_true():
    assert _result().result_capture_only is True


def test_classifier_report_exists():
    assert (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CLASSIFIER_V1.md"
    ).exists()

