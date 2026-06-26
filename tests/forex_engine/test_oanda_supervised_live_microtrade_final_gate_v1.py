from __future__ import annotations

import json

import pytest

from automation.forex_engine import oanda_supervised_live_microtrade_final_gate_v1 as gate


def _result(builder=gate.build_sample_ready_input):
    return gate.evaluate_oanda_supervised_live_microtrade_final_gate(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (
            gate.build_sample_ready_input,
            gate.OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_READY_FOR_OWNER_REVIEW,
        ),
        (
            gate.build_sample_missing_input,
            gate.OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_REQUIRE_MORE_EVIDENCE,
        ),
        (
            gate.build_sample_unsafe_input,
            gate.OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_BLOCKED_UNSAFE,
        ),
    ),
)
def test_final_gate_sample_classifications(builder, classification: str):
    assert _result(builder).classification == classification


def test_final_gate_version_constant():
    assert gate.VERSION == "oanda_supervised_live_microtrade_final_gate_v1"


@pytest.mark.parametrize("check_name", gate.REQUIRED_READY_CHECKS)
def test_final_gate_ready_sample_has_all_checks(check_name: str):
    assert check_name in _result().ready_checks


@pytest.mark.parametrize("check_name", gate.REQUIRED_READY_CHECKS)
def test_final_gate_missing_each_check_requires_more_evidence(check_name: str):
    sample = gate.build_sample_ready_input()
    checks = dict(sample.checks)
    checks[check_name] = False
    result = gate.evaluate_oanda_supervised_live_microtrade_final_gate({"checks": checks})
    if check_name in {
        "compounding_permission_still_false",
        "codex_execution_authorization_false",
    }:
        assert result.classification == gate.OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_BLOCKED_UNSAFE
    else:
        assert result.classification == gate.OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_REQUIRE_MORE_EVIDENCE
        assert check_name in result.missing_checks


@pytest.mark.parametrize(
    "critical_check",
    ("compounding_permission_still_false", "codex_execution_authorization_false"),
)
def test_final_gate_blocks_critical_false_checks(critical_check: str):
    sample = gate.build_sample_ready_input()
    checks = dict(sample.checks)
    checks[critical_check] = False
    result = gate.evaluate_oanda_supervised_live_microtrade_final_gate({"checks": checks})
    assert result.classification == gate.OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_BLOCKED_UNSAFE


def test_final_gate_owner_final_review_allowed_only_when_ready():
    assert _result().owner_final_review_allowed is True
    assert _result(gate.build_sample_missing_input).owner_final_review_allowed is False
    assert _result(gate.build_sample_unsafe_input).owner_final_review_allowed is False


@pytest.mark.parametrize("flag_name", gate.PROTECTED_FLAG_NAMES)
def test_final_gate_all_protected_flags_false(flag_name: str):
    result = _result()
    assert getattr(result, flag_name) is False
    assert result.protected_flags[flag_name] is False


@pytest.mark.parametrize(
    "field_name",
    (
        "classification",
        "owner_final_review_allowed",
        "ready_checks",
        "missing_checks",
        "blocked_checks",
        "proof_summary",
        "next_safe_action",
        "owner_warning",
        "live_warning",
    ),
)
def test_final_gate_required_output_fields(field_name: str):
    assert hasattr(_result(), field_name)


def test_final_gate_consumes_vacation_readiness_check():
    assert "vacation_profit_readiness_review_gate_present" in _result().ready_checks


def test_final_gate_consumes_live_evidence_gap_check():
    assert "live_evidence_gap_bridge_ready" in _result().ready_checks


def test_final_gate_json_serializable():
    json.dumps(gate.to_jsonable_dict(_result()))


def test_final_gate_markdown_output():
    assert gate.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Supervised Live Microtrade Final Gate V1"
    )


def test_final_gate_operator_text_output():
    assert "Final owner-run gate status" in gate.to_operator_text(_result())


def test_final_gate_owner_warning_exact():
    assert _result().owner_warning == gate.EXACT_OWNER_WARNING


def test_final_gate_live_warning_exact():
    assert _result().live_warning == gate.EXACT_LIVE_WARNING


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
        "Vacation profit trial remains blocked unless Anthony separately approves.",
        "Profit is not guaranteed.",
        "All protected flags remain false.",
        "Owner-run only.",
        "One-shot only.",
    ),
)
def test_final_gate_markdown_safety_phrases(phrase: str):
    assert phrase in gate.to_markdown(_result())


@pytest.mark.parametrize(
    "forbidden_true",
    (
        '"live_trading_allowed": true',
        '"broker_action_allowed": true',
        '"real_money_allowed": true',
        '"compounding_allowed": true',
        '"bank_movement_allowed": true',
        '"autonomous_execution_allowed": true',
        '"unattended_vacation_mode_allowed": true',
        '"vacation_profit_trial_allowed": true',
        '"codex_live_execution_authorized": true',
    ),
)
def test_final_gate_json_has_no_protected_true_flags(forbidden_true: str):
    assert forbidden_true not in json.dumps(gate.to_jsonable_dict(_result())).lower()


def test_final_gate_deterministic_ready_output():
    assert gate.to_jsonable_dict(_result()) == gate.to_jsonable_dict(_result())

