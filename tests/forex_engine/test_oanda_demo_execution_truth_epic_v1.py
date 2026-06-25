from __future__ import annotations

import contextlib
import io
import json
import runpy
import sys
from pathlib import Path

import pytest

from automation.forex_engine.oanda_demo_execution_truth_audit_v1 import (
    OANDA_DEMO_EXECUTION_PATH_BLOCKED_MISSING_TRANSPORT,
    OANDA_DEMO_EXECUTION_PATH_PRESENT_OWNER_MANUAL_RUN_REQUIRED,
)
from automation.forex_engine.oanda_demo_execution_truth_epic_v1 import (
    EXACT_NEXT_CODEX_PACKET,
    EXACT_NEXT_OWNER_ACTION,
    PROTECTED_PERMISSION_DEFAULTS,
    REQUIRED_ONE_SENTENCE_ANSWER,
    build_sample_oanda_demo_execution_truth_epic_blocked_input,
    build_sample_oanda_demo_execution_truth_epic_current_repo_input,
    oanda_demo_execution_truth_epic_to_jsonable_dict,
    oanda_demo_execution_truth_epic_to_markdown,
    oanda_demo_execution_truth_epic_to_operator_text,
    run_oanda_demo_execution_truth_epic,
)
from automation.forex_engine.oanda_demo_profit_proof_gap_bridge_v1 import (
    OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_ACTUAL_DEMO_RESULT,
    OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_EXPECTANCY_SAMPLE,
)
from automation.forex_engine.oanda_demo_to_live_profit_readiness_truth_v1 import (
    LIVE_PROFITABLE_EXECUTION_BLOCKED_NO_LIVE_EVIDENCE_BUNDLE,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _current_result():
    return run_oanda_demo_execution_truth_epic(
        build_sample_oanda_demo_execution_truth_epic_current_repo_input()
    )


def _blocked_result():
    return run_oanda_demo_execution_truth_epic(
        build_sample_oanda_demo_execution_truth_epic_blocked_input()
    )


def _run_script(relative_path: str, *args: str) -> str:
    path = REPO_ROOT / relative_path
    old_argv = sys.argv[:]
    stream = io.StringIO()
    try:
        sys.argv = [str(path), *args]
        with contextlib.redirect_stdout(stream):
            try:
                runpy.run_path(str(path), run_name="__main__")
            except SystemExit as exc:
                assert exc.code in (0, None)
    finally:
        sys.argv = old_argv
    return stream.getvalue()


def test_epic_current_repo_sample_passes():
    assert _current_result().demo_execution_distance_classification == OANDA_DEMO_EXECUTION_PATH_PRESENT_OWNER_MANUAL_RUN_REQUIRED


def test_epic_blocked_sample_passes():
    assert _blocked_result().demo_execution_distance_classification == OANDA_DEMO_EXECUTION_PATH_BLOCKED_MISSING_TRANSPORT


def test_epic_includes_demo_execution_classification():
    assert _current_result().demo_execution_distance_classification


def test_epic_includes_profit_proof_classification():
    assert _current_result().profit_proof_classification == OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_EXPECTANCY_SAMPLE


def test_epic_includes_live_profit_readiness_classification():
    assert _current_result().live_profit_readiness_classification == LIVE_PROFITABLE_EXECUTION_BLOCKED_NO_LIVE_EVIDENCE_BUNDLE


def test_epic_includes_one_sentence_answer():
    assert _current_result().one_sentence_answer == REQUIRED_ONE_SENTENCE_ANSWER


def test_epic_includes_demo_execution_answer():
    assert "owner-run OANDA demo one-order path" in _current_result().demo_execution_answer


def test_epic_includes_profit_proof_answer():
    assert "Profit cannot be claimed" in _current_result().profit_proof_answer


def test_epic_includes_live_profit_answer():
    assert "Live profitable execution is blocked" in _current_result().live_profit_answer


def test_epic_includes_exact_next_owner_action():
    assert _current_result().exact_next_owner_action == EXACT_NEXT_OWNER_ACTION


def test_epic_includes_exact_next_codex_packet():
    assert _current_result().exact_next_codex_packet == EXACT_NEXT_CODEX_PACKET


def test_epic_includes_evidence_present():
    assert _current_result().evidence_present


def test_epic_includes_evidence_missing():
    assert _current_result().evidence_missing


def test_epic_says_close_to_owner_run_demo_order_attempt():
    assert "close to one owner-run OANDA demo order attempt" in _current_result().one_sentence_answer


def test_epic_says_live_profitable_execution_blocked():
    assert "live profitable execution is blocked" in _current_result().one_sentence_answer


def test_epic_says_no_trade_placed():
    assert oanda_demo_execution_truth_epic_to_jsonable_dict(_current_result())["no_trade_placed_by_this_packet"] is True


def test_epic_says_no_broker_call_made():
    assert oanda_demo_execution_truth_epic_to_jsonable_dict(_current_result())["no_broker_call_made_by_this_packet"] is True


@pytest.mark.parametrize("flag_name", tuple(PROTECTED_PERMISSION_DEFAULTS))
def test_epic_keeps_all_protected_flags_false(flag_name):
    payload = oanda_demo_execution_truth_epic_to_jsonable_dict(_current_result())
    assert payload[flag_name] is False


def test_runner_execution_truth_emits_text():
    output = _run_script("scripts/forex_delivery/run_oanda_demo_execution_truth_audit_v1.py", "--sample-current-repo")
    assert "owner-run OANDA demo one-order path" in output


def test_runner_execution_truth_emits_json():
    output = _run_script(
        "scripts/forex_delivery/run_oanda_demo_execution_truth_audit_v1.py",
        "--sample-current-repo",
        "--json",
    )
    assert json.loads(output)["classification"] == OANDA_DEMO_EXECUTION_PATH_PRESENT_OWNER_MANUAL_RUN_REQUIRED


def test_runner_execution_truth_emits_markdown():
    output = _run_script(
        "scripts/forex_delivery/run_oanda_demo_execution_truth_audit_v1.py",
        "--sample-current-repo",
        "--markdown",
    )
    assert output.startswith("# AIOS Forex OANDA Demo Execution Truth Audit V1")


def test_runner_profit_gap_emits_text():
    output = _run_script("scripts/forex_delivery/run_oanda_demo_profit_proof_gap_bridge_v1.py", "--sample-current-repo")
    assert "Profit cannot be claimed" in output


def test_runner_profit_gap_emits_json():
    output = _run_script(
        "scripts/forex_delivery/run_oanda_demo_profit_proof_gap_bridge_v1.py",
        "--sample-current-repo",
        "--json",
    )
    assert json.loads(output)["classification"] == OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_EXPECTANCY_SAMPLE


def test_runner_profit_gap_emits_markdown():
    output = _run_script(
        "scripts/forex_delivery/run_oanda_demo_profit_proof_gap_bridge_v1.py",
        "--sample-current-repo",
        "--markdown",
    )
    assert output.startswith("# AIOS Forex OANDA Demo Profit Proof Gap Bridge V1")


def test_runner_epic_emits_text():
    output = _run_script("scripts/forex_delivery/run_oanda_demo_execution_truth_epic_v1.py", "--sample-current-repo")
    assert REQUIRED_ONE_SENTENCE_ANSWER in output


def test_runner_epic_emits_json():
    output = _run_script(
        "scripts/forex_delivery/run_oanda_demo_execution_truth_epic_v1.py",
        "--sample-current-repo",
        "--json",
    )
    assert json.loads(output)["one_sentence_answer"] == REQUIRED_ONE_SENTENCE_ANSWER


def test_runner_epic_emits_markdown():
    output = _run_script(
        "scripts/forex_delivery/run_oanda_demo_execution_truth_epic_v1.py",
        "--sample-current-repo",
        "--markdown",
    )
    assert output.startswith("# AIOS Forex OANDA Demo Execution Truth Epic Report V1")


def test_current_repo_sample_deterministic():
    first = oanda_demo_execution_truth_epic_to_jsonable_dict(_current_result())
    second = oanda_demo_execution_truth_epic_to_jsonable_dict(_current_result())
    assert first == second


def test_blocked_sample_deterministic():
    first = oanda_demo_execution_truth_epic_to_jsonable_dict(_blocked_result())
    second = oanda_demo_execution_truth_epic_to_jsonable_dict(_blocked_result())
    assert first == second


def test_source_files_missing_are_recorded_not_invented():
    assert _current_result().execution_truth.source_files_missing == (
        "scripts/forex_delivery/run_oanda_demo_runtime_http_transport_one_order_v1.py",
    )


def test_source_evidence_map_includes_oanda_demo_owner_run_command_if_present():
    assert _current_result().execution_truth.evidence_map["owner_actual_command_present"] is True


def test_source_evidence_map_includes_runtime_transport_if_present():
    assert _current_result().execution_truth.evidence_map["runtime_http_transport_present"] is True


def test_source_evidence_map_includes_post_trade_capture_if_present():
    assert _current_result().profit_gap.evidence_map["post_trade_evidence_capture_present"] is True


def test_source_evidence_map_includes_live_execution_blocker_report_if_present():
    assert _current_result().live_truth.evidence_map["live_arming_gap_report_present"] is True


def test_classification_never_claims_live_ready_when_evidence_bundle_missing():
    assert _current_result().live_truth.evidence_map["completed_live_evidence_bundle_present"] is False
    assert _current_result().live_profit_readiness_classification != "LIVE_READY"


def test_classification_never_claims_profit_proven_when_actual_result_missing():
    assert _blocked_result().profit_proof_classification == OANDA_DEMO_PROFIT_PROOF_BLOCKED_NO_ACTUAL_DEMO_RESULT


def test_classification_never_claims_codex_may_execute():
    payload = oanda_demo_execution_truth_epic_to_jsonable_dict(_current_result())
    assert "codex_demo_order_execution" in payload["blocked_actions"]


def test_classification_never_sets_broker_action_true():
    assert _current_result().broker_action_allowed is False


def test_classification_never_sets_demo_execution_true():
    assert _current_result().demo_execution_allowed is False


def test_plain_text_answer_is_short_and_accurate():
    text = oanda_demo_execution_truth_epic_to_operator_text(_current_result())
    assert text.splitlines()[0] == REQUIRED_ONE_SENTENCE_ANSWER
    assert len(text.splitlines()) <= 8


def test_markdown_includes_exact_one_sentence_answer():
    assert REQUIRED_ONE_SENTENCE_ANSWER in oanda_demo_execution_truth_epic_to_markdown(_current_result())


def test_json_includes_exact_one_sentence_answer():
    assert oanda_demo_execution_truth_epic_to_jsonable_dict(_current_result())["one_sentence_answer"] == REQUIRED_ONE_SENTENCE_ANSWER


def test_report_names_exact_next_packet():
    report = (REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_EPIC_REPORT_V1.md").read_text()
    assert EXACT_NEXT_CODEX_PACKET in report


def test_report_names_exact_next_owner_action():
    report = (REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_EPIC_REPORT_V1.md").read_text()
    assert EXACT_NEXT_OWNER_ACTION in report


def test_manual_finalization_report_includes_exact_git_add_commands():
    report = (REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_MANUAL_FINALIZATION_V1.md").read_text()
    assert "git add automation/forex_engine/oanda_demo_execution_truth_audit_v1.py" in report
    assert "git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_EPIC_REPORT_V1.md" in report


def test_manual_finalization_report_says_no_git_add_dot():
    report = (REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_MANUAL_FINALIZATION_V1.md").read_text()
    assert "Do not use `git add .`." in report


def test_epic_report_says_no_trade_placed():
    report = (REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_EPIC_REPORT_V1.md").read_text()
    assert "No trade placed by this packet." in report


def test_epic_report_says_no_broker_call_made():
    report = (REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_EPIC_REPORT_V1.md").read_text()
    assert "No broker call made by this packet." in report


NEW_MODULES = (
    "automation/forex_engine/oanda_demo_execution_truth_audit_v1.py",
    "automation/forex_engine/oanda_demo_profit_proof_gap_bridge_v1.py",
    "automation/forex_engine/oanda_demo_to_live_profit_readiness_truth_v1.py",
    "automation/forex_engine/oanda_demo_execution_truth_epic_v1.py",
)
NEW_RUNNERS = (
    "scripts/forex_delivery/run_oanda_demo_execution_truth_audit_v1.py",
    "scripts/forex_delivery/run_oanda_demo_profit_proof_gap_bridge_v1.py",
    "scripts/forex_delivery/run_oanda_demo_execution_truth_epic_v1.py",
)


def _new_source_text() -> str:
    return "\n".join((REPO_ROOT / path).read_text() for path in (*NEW_MODULES, *NEW_RUNNERS))


@pytest.mark.parametrize("forbidden", ("import requests", "from requests", "import httpx", "from httpx"))
def test_no_requests_or_httpx_import(forbidden):
    assert forbidden not in _new_source_text()


@pytest.mark.parametrize("forbidden", ("import socket", "from socket", "import dotenv", "import keyring"))
def test_no_socket_dotenv_or_keyring_import(forbidden):
    assert forbidden not in _new_source_text()


@pytest.mark.parametrize("forbidden", ("import oandapy", "from oandapy", "import oanda", "from oanda"))
def test_no_oanda_broker_library_import(forbidden):
    assert forbidden.lower() not in _new_source_text().lower()


@pytest.mark.parametrize("forbidden", ("import credential", "from credential", "broker_execution", "broker_mutation"))
def test_no_credential_or_broker_execution_import(forbidden):
    assert forbidden not in _new_source_text()


def test_no_subprocess_in_module_logic():
    module_text = "\n".join((REPO_ROOT / path).read_text() for path in NEW_MODULES)
    assert "subprocess" not in module_text


@pytest.mark.parametrize("forbidden", ("def place_order", "def execute_order", "submit_live_order", "place_demo_order"))
def test_no_order_placement_function(forbidden):
    assert forbidden not in _new_source_text()


@pytest.mark.parametrize(
    "flag_name",
    (
        "live_trading_allowed",
        "real_money_allowed",
        "compounding_allowed",
        "bank_movement_allowed",
        "scheduler_allowed",
        "daemon_allowed",
        "webhook_allowed",
        "account_id_persistence_allowed",
        "credential_access_allowed",
    ),
)
def test_static_safety_permission_flags_false(flag_name):
    assert oanda_demo_execution_truth_epic_to_jsonable_dict(_current_result())[flag_name] is False


def test_all_protected_flags_false_in_every_top_level_output():
    payload = oanda_demo_execution_truth_epic_to_jsonable_dict(_current_result())
    nested_outputs = (payload, payload["execution_truth"], payload["profit_gap"], payload["live_truth"])
    for nested in nested_outputs:
        for flag_name in PROTECTED_PERMISSION_DEFAULTS:
            assert nested[flag_name] is False
