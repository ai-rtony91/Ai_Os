from __future__ import annotations

import json

import pytest

from automation.forex_engine.oanda_demo_to_live_profit_readiness_truth_v1 import (
    LIVE_PROFITABLE_EXECUTION_BLOCKED_NO_LIVE_EVIDENCE_BUNDLE,
    PROTECTED_PERMISSION_DEFAULTS,
    REQUIRED_OPERATOR_SENTENCE,
    build_sample_current_repo_live_profit_truth_input,
    evaluate_oanda_demo_to_live_profit_readiness_truth,
    oanda_demo_to_live_profit_readiness_truth_to_jsonable_dict,
    oanda_demo_to_live_profit_readiness_truth_to_markdown,
    oanda_demo_to_live_profit_readiness_truth_to_operator_text,
)


def _current_result():
    return evaluate_oanda_demo_to_live_profit_readiness_truth(
        build_sample_current_repo_live_profit_truth_input()
    )


def test_live_truth_detects_live_execution_path_report_present():
    assert _current_result().evidence_map["live_micro_trade_execution_path_report_present"] is True


def test_live_truth_detects_live_evidence_bundle_missing():
    assert _current_result().evidence_map["completed_live_evidence_bundle_present"] is False


def test_live_truth_detects_repeated_demo_proof_missing():
    assert _current_result().evidence_map["repeated_demo_profit_proof_present"] is False


def test_live_truth_classifies_blocked_no_live_evidence_bundle():
    assert _current_result().classification == LIVE_PROFITABLE_EXECUTION_BLOCKED_NO_LIVE_EVIDENCE_BUNDLE


def test_live_truth_says_live_profitable_execution_blocked():
    assert _current_result().live_profit_distance_answer == REQUIRED_OPERATOR_SENTENCE


def test_live_truth_permissions_false():
    assert all(value is False for value in _current_result().permissions.values())


def test_live_truth_json_serializable():
    json.dumps(oanda_demo_to_live_profit_readiness_truth_to_jsonable_dict(_current_result()))


def test_live_truth_markdown_title():
    assert oanda_demo_to_live_profit_readiness_truth_to_markdown(_current_result()).startswith(
        "# AIOS Forex OANDA Demo To Live Profit Readiness Truth V1"
    )


def test_live_truth_plain_text_answer_short_and_accurate():
    text = oanda_demo_to_live_profit_readiness_truth_to_operator_text(_current_result())
    assert text.splitlines()[0] == REQUIRED_OPERATOR_SENTENCE
    assert len(text.splitlines()) <= 5


@pytest.mark.parametrize(
    "field_name",
    (
        "live_micro_trade_execution_path_report_present",
        "risk_policy_present",
        "single_live_micro_trade_exception_template_present",
        "live_arming_evidence_bundle_template_present",
        "live_arming_gap_report_present",
        "demo_practice_broker_proof_present",
    ),
)
def test_current_repo_live_evidence_present_fields_are_true(field_name):
    assert _current_result().evidence_map[field_name] is True


@pytest.mark.parametrize(
    "field_name",
    (
        "completed_live_evidence_bundle_present",
        "human_owner_live_exception_present",
        "external_credential_boundary_proof_present",
        "external_account_boundary_proof_present",
        "live_endpoint_denial_proof_present",
        "kill_switch_proof_present",
        "timeout_proof_present",
        "rollback_proof_present",
        "final_disarm_proof_present",
        "post_trade_journal_proof_present",
        "reconciliation_proof_present",
        "repeated_demo_profit_proof_present",
    ),
)
def test_current_repo_live_evidence_missing_fields_are_false(field_name):
    assert _current_result().evidence_map[field_name] is False


@pytest.mark.parametrize("flag_name", tuple(PROTECTED_PERMISSION_DEFAULTS))
def test_live_truth_all_protected_flags_false(flag_name):
    payload = oanda_demo_to_live_profit_readiness_truth_to_jsonable_dict(_current_result())
    assert payload[flag_name] is False
