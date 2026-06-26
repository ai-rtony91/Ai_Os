from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from automation.forex_engine import oanda_owner_run_live_microtrade_result_capture_epic_v1 as epic
from automation.forex_engine import oanda_owner_run_live_microtrade_result_contract_v1 as contract
from scripts.forex_delivery import run_oanda_owner_run_live_microtrade_result_capture_epic_v1
from scripts.forex_delivery import run_oanda_owner_run_live_microtrade_result_contract_v1
from scripts.forex_delivery import run_oanda_owner_run_live_microtrade_result_intake_v1


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATHS = (
    REPO_ROOT / "automation/forex_engine/oanda_owner_run_live_microtrade_result_contract_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_owner_run_live_microtrade_result_intake_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_owner_run_live_microtrade_result_quality_gate_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_owner_run_live_microtrade_result_classifier_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_owner_run_live_microtrade_reconciliation_gate_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_owner_run_live_microtrade_result_ledger_bridge_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_owner_run_live_microtrade_result_capture_epic_v1.py",
)
RUNNER_PATHS = (
    REPO_ROOT / "scripts/forex_delivery/run_oanda_owner_run_live_microtrade_result_contract_v1.py",
    REPO_ROOT / "scripts/forex_delivery/run_oanda_owner_run_live_microtrade_result_intake_v1.py",
    REPO_ROOT / "scripts/forex_delivery/run_oanda_owner_run_live_microtrade_result_capture_epic_v1.py",
)
TEST_PATHS = (
    REPO_ROOT / "tests/forex_engine/test_oanda_owner_run_live_microtrade_result_contract_v1.py",
    REPO_ROOT / "tests/forex_engine/test_oanda_owner_run_live_microtrade_result_intake_v1.py",
    REPO_ROOT / "tests/forex_engine/test_oanda_owner_run_live_microtrade_result_quality_gate_v1.py",
    REPO_ROOT / "tests/forex_engine/test_oanda_owner_run_live_microtrade_result_classifier_v1.py",
    REPO_ROOT / "tests/forex_engine/test_oanda_owner_run_live_microtrade_reconciliation_gate_v1.py",
    REPO_ROOT / "tests/forex_engine/test_oanda_owner_run_live_microtrade_result_ledger_bridge_v1.py",
    REPO_ROOT / "tests/forex_engine/test_oanda_owner_run_live_microtrade_result_capture_epic_v1.py",
)
REPORT_PATHS = (
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_GATE_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CLASSIFIER_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_GATE_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_EPIC_REPORT_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_MANUAL_FINALIZATION_V1.md",
)


def _result(builder=epic.build_sample_profit_result_input):
    return epic.run_oanda_owner_run_live_microtrade_result_capture_epic(builder())


@pytest.mark.parametrize(
    ("builder", "classification", "bucket"),
    (
        (
            epic.build_sample_profit_result_input,
            epic.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_READY_FOR_OWNER_REVIEW,
            "profit",
        ),
        (
            epic.build_sample_loss_result_input,
            epic.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_READY_FOR_OWNER_REVIEW,
            "loss",
        ),
        (
            epic.build_sample_breakeven_result_input,
            epic.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_REQUIRE_MORE_EVIDENCE,
            "breakeven",
        ),
        (
            epic.build_sample_missing_owner_result_input,
            epic.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_BLOCKED_NO_OWNER_RESULT,
            "missing",
        ),
        (
            epic.build_sample_unsafe_result_input,
            epic.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_BLOCKED_UNSAFE,
            "unsafe",
        ),
    ),
)
def test_epic_sample_classifications(builder, classification: str, bucket: str):
    result = _result(builder)
    assert result.classification == classification
    assert result.result_bucket == bucket


def test_epic_version_constant():
    assert epic.VERSION == "oanda_owner_run_live_microtrade_result_capture_epic_v1"


@pytest.mark.parametrize(
    "field_name",
    (
        "classification",
        "one_sentence_answer",
        "contract_status",
        "intake_status",
        "quality_gate_status",
        "classifier_status",
        "reconciliation_status",
        "ledger_bridge_status",
        "result_bucket",
        "realized_pl",
        "realized_r",
        "risk_breach",
        "max_loss_respected",
        "ledger_preview",
        "routing_targets",
        "exact_next_owner_action",
        "exact_next_codex_packet",
        "owner_warning",
        "result_warning",
    ),
)
def test_epic_required_fields(field_name: str):
    assert hasattr(_result(), field_name)


@pytest.mark.parametrize("flag_name", contract.PROTECTED_FLAG_NAMES)
def test_epic_output_protected_flags_false(flag_name: str):
    result = _result()
    assert result.protected_flags[flag_name] is False
    assert getattr(result, flag_name) is False


@pytest.mark.parametrize(
    "flag_name",
    (
        "repeat_live_trade_allowed",
        "vacation_profit_trial_allowed",
        "live_execution_allowed",
        "broker_action_allowed",
        "real_money_allowed",
        "compounding_allowed",
        "bank_movement_allowed",
        "autonomous_execution_allowed",
        "codex_live_execution_authorized",
    ),
)
def test_epic_restricted_top_level_flags_false(flag_name: str):
    assert getattr(_result(), flag_name) is False


def test_epic_one_sentence_answer_exact():
    assert _result().one_sentence_answer == contract.EXACT_ONE_SENTENCE_ANSWER


def test_epic_exact_next_owner_action():
    assert _result().exact_next_owner_action == contract.EXACT_NEXT_OWNER_ACTION


def test_epic_exact_next_codex_packet():
    assert _result().exact_next_codex_packet == contract.EXACT_NEXT_CODEX_PACKET


def test_epic_owner_warning_exact():
    assert _result().owner_warning == contract.EXACT_OWNER_WARNING


def test_epic_result_warning_exact():
    assert _result().result_warning == contract.EXACT_RESULT_WARNING


@pytest.mark.parametrize(
    "builder",
    (
        epic.build_sample_profit_result_input,
        epic.build_sample_loss_result_input,
        epic.build_sample_breakeven_result_input,
        epic.build_sample_missing_owner_result_input,
        epic.build_sample_unsafe_result_input,
    ),
)
def test_epic_json_serializable_outputs(builder):
    json.dumps(epic.to_jsonable_dict(_result(builder)))


@pytest.mark.parametrize(
    "builder",
    (
        epic.build_sample_profit_result_input,
        epic.build_sample_loss_result_input,
        epic.build_sample_breakeven_result_input,
        epic.build_sample_missing_owner_result_input,
        epic.build_sample_unsafe_result_input,
    ),
)
def test_epic_deterministic_outputs(builder):
    assert epic.to_jsonable_dict(_result(builder)) == epic.to_jsonable_dict(_result(builder))


def test_epic_operator_text_output():
    assert "Result capture status" in epic.to_operator_text(_result())


def test_epic_markdown_output():
    assert epic.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Owner-Run Live Microtrade Result Capture Epic Report V1"
    )


def test_epic_includes_ledger_preview_and_routing_targets():
    result = _result()
    assert result.ledger_preview["preview_only"] is True
    assert "live_proof_candidate_review" in result.routing_targets


def test_epic_result_capture_only_true():
    assert _result().result_capture_only is True


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_static_safety_no_forbidden_imports(module_path: Path):
    text = module_path.read_text(encoding="utf-8").lower()
    forbidden_fragments = (
        "import requests",
        "import httpx",
        "import socket",
        "import dotenv",
        "import keyring",
        "from oanda",
        "import oanda",
        "broker_mutation",
        "urllib",
        "http.client",
    )
    assert all(fragment not in text for fragment in forbidden_fragments)


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_static_safety_no_runtime_or_git_actions_in_modules(module_path: Path):
    text = module_path.read_text(encoding="utf-8").lower()
    forbidden_fragments = (
        "subprocess",
        "git add",
        "git commit",
        "git push",
        "gh pr",
        "while true",
        "schedule.",
        "daemonize",
        "webhook(",
        "def place_order",
        "def submit_order",
        "def execute_order",
    )
    assert all(fragment not in text for fragment in forbidden_fragments)


@pytest.mark.parametrize("path", MODULE_PATHS + RUNNER_PATHS + TEST_PATHS + REPORT_PATHS)
def test_created_paths_exist(path: Path):
    assert path.exists()


@pytest.mark.parametrize("report_path", REPORT_PATHS)
def test_reports_say_no_trade_placed(report_path: Path):
    assert "No trade placed by this packet." in report_path.read_text(encoding="utf-8")


@pytest.mark.parametrize("report_path", REPORT_PATHS)
def test_reports_say_no_broker_call(report_path: Path):
    assert "No broker call was made by this packet." in report_path.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "phrase",
    (
        "No credential access occurred.",
        "No account ID was persisted.",
        "No broker order ID was persisted.",
        "No raw broker payload was persisted.",
        "No live approval was granted.",
        "No repeat trading approval was granted.",
        "No real money approval was granted.",
        "No compounding approval was granted.",
        "No bank movement approval was granted.",
        "No autonomous execution was granted.",
        "Unattended vacation mode remains blocked.",
        "Vacation profit trial remains blocked unless Anthony separately approves.",
        "Profit is not guaranteed.",
        "All protected flags remain false.",
        "Owner-run result capture only.",
        "Read-only only.",
    ),
)
def test_epic_report_required_safety_phrases(phrase: str):
    text = REPORT_PATHS[6].read_text(encoding="utf-8")
    assert phrase in text


def test_epic_report_required_headings():
    text = REPORT_PATHS[6].read_text(encoding="utf-8")
    assert "## Source Files Read" in text
    assert "## Source Files Missing" in text
    assert "## Validators Run" in text
    assert "## Validators Passed" in text
    assert "## Validators Failed" in text
    assert "Static safety scan: PASS" in text


def test_epic_report_sample_results():
    text = REPORT_PATHS[6].read_text(encoding="utf-8")
    assert epic.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_READY_FOR_OWNER_REVIEW in text
    assert epic.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_REQUIRE_MORE_EVIDENCE in text
    assert epic.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_BLOCKED_NO_OWNER_RESULT in text
    assert epic.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_BLOCKED_UNSAFE in text


def test_manual_report_validation_commands():
    text = REPORT_PATHS[7].read_text(encoding="utf-8")
    assert "python -m py_compile automation/forex_engine/oanda_owner_run_live_microtrade_result_contract_v1.py" in text
    assert "python -m pytest tests/forex_engine/test_oanda_owner_run_live_microtrade_result_contract_v1.py" in text
    assert "python scripts/forex_delivery/run_oanda_owner_run_live_microtrade_result_capture_epic_v1.py --sample-profit --json" in text
    assert "git diff --check" in text
    assert "git status --short --branch" in text


def test_manual_report_exact_git_add_commands():
    text = REPORT_PATHS[7].read_text(encoding="utf-8")
    for path in MODULE_PATHS + RUNNER_PATHS + TEST_PATHS + REPORT_PATHS:
        rel = path.relative_to(REPO_ROOT).as_posix()
        assert f"git add {rel}" in text
    assert "git add ." not in text


def test_no_required_source_chain_file_mutated_by_manual_commands():
    text = REPORT_PATHS[7].read_text(encoding="utf-8")
    assert "git add automation/forex_engine/oanda_supervised_live_microtrade_final_owner_run_epic_v1.py" not in text
    assert "git add automation/forex_engine/oanda_vacation_profit_readiness_epic_v1.py" not in text
    assert "git add Reports/forex_delivery/AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_EPIC_REPORT_V1.md" not in text
    assert "git add Reports/forex_delivery/AIOS_FOREX_OANDA_VACATION_PROFIT_READINESS_EPIC_REPORT_V1.md" not in text


@pytest.mark.parametrize(
    ("runner_module", "argv", "expected"),
    (
        (
            run_oanda_owner_run_live_microtrade_result_contract_v1,
            ["runner", "--sample-profit", "--json"],
            contract.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_READY,
        ),
        (
            run_oanda_owner_run_live_microtrade_result_intake_v1,
            ["runner", "--sample-loss", "--json"],
            "OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_ACCEPTED",
        ),
        (
            run_oanda_owner_run_live_microtrade_result_capture_epic_v1,
            ["runner", "--sample-profit", "--json"],
            epic.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_READY_FOR_OWNER_REVIEW,
        ),
        (
            run_oanda_owner_run_live_microtrade_result_capture_epic_v1,
            ["runner", "--sample-loss", "--json"],
            epic.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_READY_FOR_OWNER_REVIEW,
        ),
        (
            run_oanda_owner_run_live_microtrade_result_capture_epic_v1,
            ["runner", "--sample-breakeven", "--json"],
            epic.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_REQUIRE_MORE_EVIDENCE,
        ),
        (
            run_oanda_owner_run_live_microtrade_result_capture_epic_v1,
            ["runner", "--sample-missing", "--json"],
            epic.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_BLOCKED_NO_OWNER_RESULT,
        ),
        (
            run_oanda_owner_run_live_microtrade_result_capture_epic_v1,
            ["runner", "--sample-unsafe", "--json"],
            epic.OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_BLOCKED_UNSAFE,
        ),
        (
            run_oanda_owner_run_live_microtrade_result_capture_epic_v1,
            ["runner", "--sample-profit", "--markdown"],
            "# AIOS Forex OANDA Owner-Run Live Microtrade Result Capture Epic Report V1",
        ),
    ),
)
def test_runner_outputs(monkeypatch, capsys, runner_module, argv, expected: str):
    monkeypatch.setattr(sys, "argv", argv)
    assert runner_module.main() == 0
    assert expected in capsys.readouterr().out

