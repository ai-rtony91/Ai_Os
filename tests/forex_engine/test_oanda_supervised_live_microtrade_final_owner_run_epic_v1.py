from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from automation.forex_engine import oanda_supervised_live_microtrade_final_owner_run_epic_v1 as epic
from automation.forex_engine.oanda_supervised_live_microtrade_final_gate_v1 import (
    EXACT_LIVE_WARNING,
    EXACT_NEXT_CODEX_PACKET,
    EXACT_NEXT_OWNER_ACTION,
    EXACT_ONE_SENTENCE_ANSWER,
    EXACT_OWNER_WARNING,
    PROTECTED_FLAG_NAMES,
)
from scripts.forex_delivery import run_oanda_supervised_live_microtrade_final_gate_v1
from scripts.forex_delivery import run_oanda_supervised_live_microtrade_final_owner_run_epic_v1
from scripts.forex_delivery import run_oanda_supervised_live_microtrade_owner_runbook_v1
from scripts.forex_delivery import run_oanda_supervised_live_microtrade_ticket_preview_v1


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATHS = (
    REPO_ROOT / "automation/forex_engine/oanda_supervised_live_microtrade_final_gate_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_supervised_live_microtrade_ticket_preview_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_supervised_live_microtrade_disarm_recovery_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_supervised_live_microtrade_post_trade_capture_plan_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_supervised_live_microtrade_owner_runbook_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_supervised_live_microtrade_final_owner_run_epic_v1.py",
)
REPORT_PATHS = (
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_PLAN_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_EPIC_REPORT_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_MANUAL_FINALIZATION_V1.md",
)


def _result(builder=epic.build_sample_ready_input):
    return epic.run_oanda_supervised_live_microtrade_final_owner_run_epic(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (
            epic.build_sample_ready_input,
            epic.OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_READY_FOR_OWNER_REVIEW,
        ),
        (
            epic.build_sample_missing_input,
            epic.OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_REQUIRE_MORE_EVIDENCE,
        ),
        (
            epic.build_sample_unsafe_input,
            epic.OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_BLOCKED,
        ),
    ),
)
def test_final_owner_run_epic_sample_classifications(builder, classification: str):
    assert _result(builder).classification == classification


def test_final_owner_run_epic_version_constant():
    assert epic.VERSION == "oanda_supervised_live_microtrade_final_owner_run_epic_v1"


@pytest.mark.parametrize(
    "field_name",
    (
        "classification",
        "one_sentence_answer",
        "final_gate_status",
        "ticket_preview_status",
        "disarm_recovery_status",
        "post_trade_capture_status",
        "owner_runbook_status",
        "owner_final_review_allowed",
        "risk_summary",
        "ticket_preview",
        "disarm_recovery_preview",
        "owner_runbook_preview",
        "post_trade_capture_preview",
        "exact_next_owner_action",
        "exact_next_codex_packet",
        "owner_warning",
        "live_warning",
    ),
)
def test_final_owner_run_epic_required_fields(field_name: str):
    assert hasattr(_result(), field_name)


def test_final_owner_run_epic_one_sentence_answer_exact():
    assert _result().one_sentence_answer == EXACT_ONE_SENTENCE_ANSWER


def test_final_owner_run_epic_exact_next_owner_action():
    assert _result().exact_next_owner_action == EXACT_NEXT_OWNER_ACTION


def test_final_owner_run_epic_exact_next_codex_packet():
    assert _result().exact_next_codex_packet == EXACT_NEXT_CODEX_PACKET


def test_final_owner_run_epic_owner_warning_exact():
    assert _result().owner_warning == EXACT_OWNER_WARNING


def test_final_owner_run_epic_live_warning_exact():
    assert _result().live_warning == EXACT_LIVE_WARNING


@pytest.mark.parametrize("flag_name", PROTECTED_FLAG_NAMES)
def test_final_owner_run_epic_all_protected_flags_false(flag_name: str):
    result = _result()
    assert getattr(result, flag_name) is False
    assert result.protected_flags[flag_name] is False


@pytest.mark.parametrize(
    "summary_key",
    (
        "one_shot_only",
        "owner_run_only",
        "profit_guaranteed",
        "live_execution_allowed",
        "real_money_allowed",
        "compounding_allowed",
        "bank_movement_allowed",
        "autonomous_execution_allowed",
        "vacation_profit_trial_allowed",
    ),
)
def test_final_owner_run_epic_risk_summary_keys(summary_key: str):
    assert summary_key in _result().risk_summary


@pytest.mark.parametrize(
    "summary_key",
    (
        "profit_guaranteed",
        "live_execution_allowed",
        "real_money_allowed",
        "compounding_allowed",
        "bank_movement_allowed",
        "autonomous_execution_allowed",
        "vacation_profit_trial_allowed",
    ),
)
def test_final_owner_run_epic_risk_summary_false(summary_key: str):
    assert _result().risk_summary[summary_key] is False


def test_final_owner_run_epic_owner_final_review_only_ready():
    assert _result().owner_final_review_allowed is True
    assert _result(epic.build_sample_missing_input).owner_final_review_allowed is False
    assert _result(epic.build_sample_unsafe_input).owner_final_review_allowed is False


def test_final_owner_run_epic_json_serializable():
    json.dumps(epic.to_jsonable_dict(_result()))


def test_final_owner_run_epic_markdown_output():
    assert epic.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Supervised Live Microtrade Final Owner-Run Epic V1"
    )


def test_final_owner_run_epic_operator_text_output():
    assert "Final owner-run epic status" in epic.to_operator_text(_result())


def test_final_owner_run_epic_deterministic_ready_output():
    assert epic.to_jsonable_dict(_result()) == epic.to_jsonable_dict(_result())


def test_final_owner_run_epic_deterministic_missing_output():
    assert epic.to_jsonable_dict(_result(epic.build_sample_missing_input)) == epic.to_jsonable_dict(
        _result(epic.build_sample_missing_input)
    )


def test_final_owner_run_epic_deterministic_unsafe_output():
    assert epic.to_jsonable_dict(_result(epic.build_sample_unsafe_input)) == epic.to_jsonable_dict(
        _result(epic.build_sample_unsafe_input)
    )


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_static_safety_no_forbidden_imports(module_path: Path):
    text = module_path.read_text(encoding="utf-8").lower()
    forbidden_fragments = (
        "import requests",
        "import httpx",
        "import socket",
        "import dotenv",
        "import keyring",
        "broker_mutation",
        "subprocess",
        "api-fxtrade",
        ".env",
    )
    assert all(fragment not in text for fragment in forbidden_fragments)


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_static_safety_no_runtime_hooks(module_path: Path):
    text = module_path.read_text(encoding="utf-8").lower()
    assert "while true" not in text
    assert "schedule." not in text
    assert "daemonize" not in text
    assert "webhook" not in text.replace("webhook_allowed", "")


@pytest.mark.parametrize(
    ("runner_module", "argv", "expected"),
    (
        (
            run_oanda_supervised_live_microtrade_final_gate_v1,
            ["runner", "--sample-ready", "--json"],
            '"classification"',
        ),
        (
            run_oanda_supervised_live_microtrade_ticket_preview_v1,
            ["runner", "--sample-ready", "--json"],
            '"sanitized_local_ticket_id"',
        ),
        (
            run_oanda_supervised_live_microtrade_owner_runbook_v1,
            ["runner", "--sample-ready", "--markdown"],
            "# AIOS Forex OANDA Supervised Live Microtrade Owner Runbook V1",
        ),
        (
            run_oanda_supervised_live_microtrade_final_owner_run_epic_v1,
            ["runner", "--sample-unsafe", "--json"],
            epic.OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_BLOCKED,
        ),
    ),
)
def test_runner_outputs(monkeypatch, capsys, runner_module, argv, expected: str):
    monkeypatch.setattr(sys, "argv", argv)
    assert runner_module.main() == 0
    assert expected in capsys.readouterr().out


@pytest.mark.parametrize("report_path", REPORT_PATHS)
def test_reports_exist(report_path: Path):
    assert report_path.exists()


@pytest.mark.parametrize("report_path", REPORT_PATHS)
def test_reports_say_no_trade_placed(report_path: Path):
    assert "No trade placed by this packet." in report_path.read_text(encoding="utf-8")


@pytest.mark.parametrize("report_path", REPORT_PATHS)
def test_reports_say_no_broker_call(report_path: Path):
    assert "No broker call was made by this packet." in report_path.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "phrase",
    (
        "No live approval was granted.",
        "No real money approval was granted.",
        "No compounding approval was granted.",
        "No bank movement approval was granted.",
        "No autonomous execution was granted.",
        "Unattended vacation mode remains blocked.",
        "Vacation profit trial remains blocked unless Anthony separately approves.",
        "Profit is not guaranteed.",
        "All protected flags remain false.",
    ),
)
def test_epic_report_required_safety_phrases(phrase: str):
    assert phrase in REPORT_PATHS[5].read_text(encoding="utf-8")


def test_epic_report_source_files_read_heading():
    assert "## Source Files Read" in REPORT_PATHS[5].read_text(encoding="utf-8")


def test_epic_report_source_files_missing_heading():
    assert "## Source Files Missing" in REPORT_PATHS[5].read_text(encoding="utf-8")


def test_epic_report_static_safety_says_pass():
    assert "Static safety scan: PASS" in REPORT_PATHS[5].read_text(encoding="utf-8")


def test_manual_report_exact_git_add_commands():
    text = REPORT_PATHS[6].read_text(encoding="utf-8")
    assert "git add automation/forex_engine/oanda_supervised_live_microtrade_final_gate_v1.py" in text
    assert "git add ." not in text


def test_manual_report_validation_commands():
    text = REPORT_PATHS[6].read_text(encoding="utf-8")
    assert "python -m pytest tests/forex_engine/test_oanda_supervised_live_microtrade_final_gate_v1.py" in text
    assert "git diff --check" in text


def test_no_existing_vacation_readiness_file_mutated():
    text = REPORT_PATHS[6].read_text(encoding="utf-8")
    assert "git add automation/forex_engine/oanda_vacation_profit_readiness_epic_v1.py" not in text

