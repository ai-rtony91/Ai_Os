from __future__ import annotations

import json

import pytest

from automation.forex_engine.oanda_demo_execution_truth_audit_v1 import (
    OANDA_DEMO_EXECUTION_PATH_BLOCKED_MISSING_TRANSPORT,
    OANDA_DEMO_EXECUTION_PATH_PRESENT_OWNER_MANUAL_RUN_REQUIRED,
    PROTECTED_PERMISSION_DEFAULTS,
    REQUIRED_OPERATOR_SENTENCE,
    audit_oanda_demo_execution_truth,
    build_sample_blocked_missing_transport_input,
    build_sample_current_repo_execution_truth_input,
    oanda_demo_execution_truth_to_jsonable_dict,
    oanda_demo_execution_truth_to_markdown,
    oanda_demo_execution_truth_to_operator_text,
)


def _current_result():
    return audit_oanda_demo_execution_truth(build_sample_current_repo_execution_truth_input())


def test_execution_truth_detects_owner_run_path_present():
    assert _current_result().classification == OANDA_DEMO_EXECUTION_PATH_PRESENT_OWNER_MANUAL_RUN_REQUIRED


def test_execution_truth_detects_broker_call_implementation_present():
    assert _current_result().evidence_map["broker_call_implementation_present"] is True


def test_execution_truth_detects_owner_actual_command_present():
    assert _current_result().evidence_map["owner_actual_command_present"] is True


def test_execution_truth_detects_runtime_transport_present():
    assert _current_result().evidence_map["runtime_http_transport_present"] is True


def test_execution_truth_blocked_when_transport_missing():
    result = audit_oanda_demo_execution_truth(build_sample_blocked_missing_transport_input())
    assert result.classification == OANDA_DEMO_EXECUTION_PATH_BLOCKED_MISSING_TRANSPORT


def test_execution_truth_says_no_trade_placed():
    assert oanda_demo_execution_truth_to_jsonable_dict(_current_result())["no_trade_placed_by_this_packet"] is True


def test_execution_truth_says_no_broker_call_made():
    assert oanda_demo_execution_truth_to_jsonable_dict(_current_result())["no_broker_call_made_by_this_packet"] is True


def test_execution_truth_permissions_false():
    assert all(value is False for value in _current_result().permissions.values())


def test_execution_truth_json_serializable():
    json.dumps(oanda_demo_execution_truth_to_jsonable_dict(_current_result()))


def test_execution_truth_markdown_title():
    assert oanda_demo_execution_truth_to_markdown(_current_result()).startswith(
        "# AIOS Forex OANDA Demo Execution Truth Audit V1"
    )


def test_execution_truth_plain_english_answer_exact():
    assert oanda_demo_execution_truth_to_operator_text(_current_result()).splitlines()[0] == REQUIRED_OPERATOR_SENTENCE


def test_execution_truth_exact_owner_run_surface_includes_actual_runtime_runner():
    assert (
        "scripts/forex_delivery/run_oanda_demo_runtime_http_transport_one_order_owner_run_v1.py"
        in _current_result().exact_owner_run_surface
    )


def test_execution_truth_source_files_missing_are_recorded_not_invented():
    assert (
        "scripts/forex_delivery/run_oanda_demo_runtime_http_transport_one_order_v1.py"
        in _current_result().source_files_missing
    )


@pytest.mark.parametrize(
    "field_name",
    (
        "final_owner_runtime_run_present",
        "broker_call_implementation_present",
        "owner_actual_command_present",
        "runtime_http_transport_present",
        "vault_backed_transport_present",
        "owner_command_template_present",
        "manual_execution_window_present",
        "demo_endpoint_only_evidence_present",
        "one_order_only_evidence_present",
        "runtime_credentials_external_evidence_present",
        "account_id_external_evidence_present",
        "no_live_endpoint_evidence_present",
        "post_trade_evidence_plan_present",
        "owner_approval_gate_present",
    ),
)
def test_current_repo_execution_evidence_fields_are_true(field_name):
    assert _current_result().evidence_map[field_name] is True


@pytest.mark.parametrize("flag_name", tuple(PROTECTED_PERMISSION_DEFAULTS))
def test_execution_truth_all_protected_flags_false(flag_name):
    payload = oanda_demo_execution_truth_to_jsonable_dict(_current_result())
    assert payload[flag_name] is False
