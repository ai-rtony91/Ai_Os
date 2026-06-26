from __future__ import annotations

import json
from decimal import Decimal

import pytest

from automation.forex_engine import oanda_vacation_profit_trial_plan_v1 as trial
from automation.forex_engine.oanda_vacation_profit_readiness_contract_v1 import (
    PROTECTED_FLAG_NAMES,
)


def _result(builder=trial.build_sample_ready_for_review_input):
    return trial.build_oanda_vacation_profit_trial_plan(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (
            trial.build_sample_ready_for_review_input,
            trial.OANDA_VACATION_PROFIT_TRIAL_PLAN_READY_FOR_OWNER_REVIEW,
        ),
        (
            trial.build_sample_no_live_sample_input,
            trial.OANDA_VACATION_PROFIT_TRIAL_PLAN_REQUIRE_MORE_PROOF,
        ),
        (
            trial.build_sample_missing_autonomy_controls_input,
            trial.OANDA_VACATION_PROFIT_TRIAL_PLAN_REQUIRE_MORE_PROOF,
        ),
        (
            trial.build_sample_compounding_blocked_input,
            trial.OANDA_VACATION_PROFIT_TRIAL_PLAN_REQUIRE_MORE_PROOF,
        ),
        (
            trial.build_sample_unsafe_input,
            trial.OANDA_VACATION_PROFIT_TRIAL_PLAN_BLOCKED_UNSAFE,
        ),
    ),
)
def test_trial_plan_classifications(builder, classification: str):
    assert _result(builder).classification == classification


def test_trial_plan_version_constant():
    assert trial.VERSION == "oanda_vacation_profit_trial_plan_v1"


@pytest.mark.parametrize(
    ("field_name", "expected"),
    (
        ("trial_capital_placeholder", trial.TRIAL_CAPITAL_PLACEHOLDER),
        ("trial_duration_placeholder", trial.TRIAL_DURATION_PLACEHOLDER),
        ("trial_capital", Decimal("200.00")),
        ("max_total_drawdown_percent", Decimal("5.00")),
        ("max_daily_loss_percent", Decimal("2.00")),
        ("max_trade_risk_percent", Decimal("0.50")),
    ),
)
def test_trial_plan_required_values(field_name: str, expected):
    assert getattr(_result(), field_name) == expected


@pytest.mark.parametrize(
    "field_name",
    (
        "no_compounding",
        "no_withdrawals",
        "no_deposits",
        "no_unattended_approval_yet",
        "owner_review_required",
    ),
)
def test_trial_plan_boolean_boundaries(field_name: str):
    assert getattr(_result(), field_name) is True


@pytest.mark.parametrize(
    "required_item",
    (
        "live_sample_gate_ready_for_owner_review",
        "autonomy_control_gate_ready_for_owner_review",
        "compounding_permission_future_owner_review_ready",
        "owner_manual_review_before_any_trial",
    ),
)
def test_trial_plan_evidence_required_before_trial(required_item: str):
    assert required_item in _result().evidence_required_before_trial


@pytest.mark.parametrize(
    "abort_rule",
    (
        "abort_if_drawdown_limit_reached",
        "abort_if_daily_stop_reached",
        "abort_if_trade_risk_exceeds_contract",
        "abort_if_account_boundary_unclear",
        "abort_if_credential_boundary_unclear",
        "abort_if_monitoring_or_alerting_not_confirmed",
        "abort_if_owner_sos_escalation_not_confirmed",
    ),
)
def test_trial_plan_abort_rules(abort_rule: str):
    assert abort_rule in _result().abort_rules


@pytest.mark.parametrize(
    "review_item",
    (
        "capture_realized_pl_summary",
        "capture_drawdown_summary",
        "capture_trade_count_summary",
        "capture_reconciliation_summary",
        "capture_journal_summary",
        "route_result_back_to_evidence_ledger",
    ),
)
def test_trial_plan_post_trial_review_requirements(review_item: str):
    assert review_item in _result().post_trial_review_requirements


@pytest.mark.parametrize("flag_name", PROTECTED_FLAG_NAMES)
def test_trial_plan_all_protected_flags_false(flag_name: str):
    result = _result()
    assert getattr(result, flag_name) is False
    assert result.protected_flags[flag_name] is False


def test_trial_plan_preview_only():
    assert _result().plan_preview["preview_only"] is True


def test_trial_plan_json_serializable():
    json.dumps(trial.to_jsonable_dict(_result()))


def test_trial_plan_markdown_output():
    assert trial.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Vacation Profit Trial Plan V1"
    )


def test_trial_plan_operator_text_output():
    assert "Vacation profit trial plan status" in trial.to_operator_text(_result())


@pytest.mark.parametrize(
    "phrase",
    (
        "No trade placed by this packet.",
        "No broker call was made by this packet.",
        "No live approval was granted.",
        "No real money approval was granted.",
        "No compounding approval was granted.",
        "No bank movement approval was granted.",
        "No autonomous execution was granted.",
        "Unattended vacation mode remains blocked.",
        "Profit is not guaranteed.",
        "All protected flags remain false.",
    ),
)
def test_trial_plan_markdown_safety_phrases(phrase: str):
    assert phrase in trial.to_markdown(_result())

