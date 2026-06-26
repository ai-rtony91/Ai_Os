from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from automation.forex_engine import oanda_vacation_profit_readiness_epic_v1 as epic
from automation.forex_engine.oanda_vacation_profit_readiness_contract_v1 import (
    EXACT_NEXT_CODEX_PACKET,
    EXACT_NEXT_OWNER_ACTION,
    EXACT_ONE_SENTENCE_ANSWER,
    EXACT_OWNER_WARNING,
    EXACT_VACATION_WARNING,
    PROFIT_CLAIM_STATUS,
    PROTECTED_FLAG_NAMES,
    VACATION_PROFIT_STATUS,
)
from scripts.forex_delivery import run_oanda_vacation_profit_live_sample_gate_v1
from scripts.forex_delivery import run_oanda_vacation_profit_readiness_contract_v1
from scripts.forex_delivery import run_oanda_vacation_profit_readiness_epic_v1
from scripts.forex_delivery import run_oanda_vacation_profit_trial_plan_v1


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATHS = (
    REPO_ROOT / "automation/forex_engine/oanda_vacation_profit_readiness_contract_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_vacation_profit_live_sample_gate_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_vacation_profit_autonomy_control_gate_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_vacation_profit_compounding_permission_gate_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_vacation_profit_trial_plan_v1.py",
    REPO_ROOT / "automation/forex_engine/oanda_vacation_profit_readiness_epic_v1.py",
)
RUNNER_PATHS = (
    REPO_ROOT / "scripts/forex_delivery/run_oanda_vacation_profit_readiness_contract_v1.py",
    REPO_ROOT / "scripts/forex_delivery/run_oanda_vacation_profit_live_sample_gate_v1.py",
    REPO_ROOT / "scripts/forex_delivery/run_oanda_vacation_profit_trial_plan_v1.py",
    REPO_ROOT / "scripts/forex_delivery/run_oanda_vacation_profit_readiness_epic_v1.py",
)
REPORT_PATHS = (
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_VACATION_PROFIT_READINESS_CONTRACT_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_VACATION_PROFIT_LIVE_SAMPLE_GATE_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_VACATION_PROFIT_AUTONOMY_CONTROL_GATE_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_GATE_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_VACATION_PROFIT_TRIAL_PLAN_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_VACATION_PROFIT_READINESS_EPIC_REPORT_V1.md",
    REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_OANDA_VACATION_PROFIT_READINESS_MANUAL_FINALIZATION_V1.md",
)


def _result(builder=epic.build_sample_ready_for_review_input):
    return epic.run_oanda_vacation_profit_readiness_epic(builder())


@pytest.mark.parametrize(
    ("builder", "classification"),
    (
        (
            epic.build_sample_ready_for_review_input,
            epic.AIOS_VACATION_PROFIT_READY_FOR_OWNER_REVIEW,
        ),
        (
            epic.build_sample_no_live_sample_input,
            epic.AIOS_VACATION_PROFIT_BLOCKED_NO_LIVE_SAMPLE,
        ),
        (
            epic.build_sample_missing_autonomy_controls_input,
            epic.AIOS_VACATION_PROFIT_BLOCKED_NO_AUTONOMY_CONTROLS,
        ),
        (
            epic.build_sample_compounding_blocked_input,
            epic.AIOS_VACATION_PROFIT_BLOCKED_NO_COMPOUNDING_PERMISSION,
        ),
        (
            epic.build_sample_unsafe_input,
            epic.AIOS_VACATION_PROFIT_BLOCKED_UNSAFE,
        ),
    ),
)
def test_epic_sample_classifications(builder, classification: str):
    assert _result(builder).classification == classification


def test_epic_version_constant():
    assert epic.VERSION == "oanda_vacation_profit_readiness_epic_v1"


@pytest.mark.parametrize(
    "field_name",
    (
        "classification",
        "one_sentence_answer",
        "contract_status",
        "live_sample_status",
        "autonomy_control_status",
        "compounding_permission_status",
        "trial_plan_status",
        "trial_capital",
        "max_total_drawdown_percent",
        "max_daily_loss_percent",
        "max_trade_risk_percent",
        "min_live_sample_trades",
        "profit_claim_status",
        "vacation_profit_status",
        "missing_proof_items",
        "blocked_items",
        "trial_plan_preview",
        "exact_next_owner_action",
        "exact_next_codex_packet",
        "owner_warning",
        "vacation_warning",
    ),
)
def test_epic_required_top_level_fields(field_name: str):
    assert hasattr(_result(), field_name)


def test_epic_one_sentence_answer_exact():
    assert _result().one_sentence_answer == EXACT_ONE_SENTENCE_ANSWER


def test_epic_exact_next_owner_action():
    assert _result().exact_next_owner_action == EXACT_NEXT_OWNER_ACTION


def test_epic_exact_next_codex_packet():
    assert _result().exact_next_codex_packet == EXACT_NEXT_CODEX_PACKET


def test_epic_owner_warning_exact():
    assert _result().owner_warning == EXACT_OWNER_WARNING


def test_epic_vacation_warning_exact():
    assert _result().vacation_warning == EXACT_VACATION_WARNING


def test_epic_profit_claim_status():
    assert _result().profit_claim_status == PROFIT_CLAIM_STATUS


def test_epic_vacation_profit_status():
    assert _result().vacation_profit_status == VACATION_PROFIT_STATUS


def test_epic_ready_owner_final_review_allowed():
    assert _result().owner_final_review_allowed is True


@pytest.mark.parametrize(
    "builder",
    (
        epic.build_sample_no_live_sample_input,
        epic.build_sample_missing_autonomy_controls_input,
        epic.build_sample_compounding_blocked_input,
        epic.build_sample_unsafe_input,
    ),
)
def test_epic_non_ready_owner_final_review_not_allowed(builder):
    assert _result(builder).owner_final_review_allowed is False


@pytest.mark.parametrize("flag_name", PROTECTED_FLAG_NAMES)
def test_epic_all_protected_flags_false(flag_name: str):
    result = _result()
    assert getattr(result, flag_name) is False
    assert result.protected_flags[flag_name] is False


@pytest.mark.parametrize(
    "forbidden_text",
    (
        '"demo_execution_allowed": true',
        '"broker_action_allowed": true',
        '"real_money_allowed": true',
        '"compounding_allowed": true',
        '"bank_movement_allowed": true',
        '"live_trading_allowed": true',
        '"credential_access_allowed": true',
        '"account_id_persistence_allowed": true',
        '"autonomous_execution_allowed": true',
        '"scheduler_allowed": true',
        '"daemon_allowed": true',
        '"webhook_allowed": true',
        '"live_micro_trade_exception_allowed": true',
        '"owner_live_execution_approval_present": true',
        '"codex_live_execution_authorized": true',
        '"unattended_vacation_mode_allowed": true',
        '"vacation_profit_trial_allowed": true',
    ),
)
def test_epic_json_has_no_protected_true_flags(forbidden_text: str):
    assert forbidden_text not in json.dumps(epic.to_jsonable_dict(_result())).lower()


def test_epic_json_serializable():
    json.dumps(epic.to_jsonable_dict(_result()))


def test_epic_markdown_output():
    assert epic.to_markdown(_result()).startswith(
        "# AIOS Forex OANDA Vacation Profit Readiness Epic Report V1"
    )


def test_epic_operator_text_output():
    assert "Vacation profit readiness epic status" in epic.to_operator_text(_result())


@pytest.mark.parametrize(
    ("builder", "expected_item"),
    (
        (epic.build_sample_no_live_sample_input, "reconciliation_complete"),
        (epic.build_sample_missing_autonomy_controls_input, "kill_switch_proof"),
        (epic.build_sample_compounding_blocked_input, "compounding_permission_future_owner_review_ready"),
    ),
)
def test_epic_missing_items_for_blocked_samples(builder, expected_item: str):
    assert expected_item in _result(builder).missing_proof_items


def test_epic_unsafe_sample_has_blocked_items():
    assert _result(epic.build_sample_unsafe_input).blocked_items


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_static_safety_no_forbidden_imports(module_path: Path):
    text = module_path.read_text(encoding="utf-8").lower()
    forbidden_fragments = (
        "import requests",
        "import httpx",
        "import socket",
        "import dotenv",
        "import keyring",
        "subprocess",
        "api-fxtrade",
        "order placement",
        "order_create",
        ".env",
    )
    assert all(fragment not in text for fragment in forbidden_fragments)


@pytest.mark.parametrize("module_path", MODULE_PATHS)
def test_static_safety_no_runtime_loops(module_path: Path):
    text = module_path.read_text(encoding="utf-8").lower()
    assert "while true" not in text
    assert "schedule." not in text
    assert "daemonize" not in text
    assert "webhook" not in text.replace("webhook_allowed", "")


@pytest.mark.parametrize("runner_path", RUNNER_PATHS)
def test_runners_exist(runner_path: Path):
    assert runner_path.exists()


@pytest.mark.parametrize(
    ("runner_module", "argv", "expected"),
    (
        (
            run_oanda_vacation_profit_readiness_contract_v1,
            ["runner", "--sample-ready-review"],
            "Vacation profit readiness contract status",
        ),
        (
            run_oanda_vacation_profit_live_sample_gate_v1,
            ["runner", "--sample-no-live-sample", "--json"],
            '"classification"',
        ),
        (
            run_oanda_vacation_profit_trial_plan_v1,
            ["runner", "--sample-ready-review", "--markdown"],
            "# AIOS Forex OANDA Vacation Profit Trial Plan V1",
        ),
        (
            run_oanda_vacation_profit_readiness_epic_v1,
            ["runner", "--sample-unsafe", "--json"],
            epic.AIOS_VACATION_PROFIT_BLOCKED_UNSAFE,
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
        "Profit is not guaranteed.",
        "All protected flags remain false.",
    ),
)
def test_epic_report_required_safety_phrases(phrase: str):
    report = REPORT_PATHS[5].read_text(encoding="utf-8")
    assert phrase in report


def test_epic_report_source_files_read_heading():
    assert "## Source Files Read" in REPORT_PATHS[5].read_text(encoding="utf-8")


def test_epic_report_source_files_missing_heading():
    assert "## Source Files Missing" in REPORT_PATHS[5].read_text(encoding="utf-8")


def test_epic_report_static_safety_says_pass():
    assert "Static safety scan: PASS" in REPORT_PATHS[5].read_text(encoding="utf-8")


def test_manual_report_exact_git_add_commands():
    text = REPORT_PATHS[6].read_text(encoding="utf-8")
    assert "git add automation/forex_engine/oanda_vacation_profit_readiness_contract_v1.py" in text
    assert "git add ." not in text


def test_manual_report_validation_commands():
    text = REPORT_PATHS[6].read_text(encoding="utf-8")
    assert "python -m pytest tests/forex_engine/test_oanda_vacation_profit_readiness_contract_v1.py" in text
    assert "git diff --check" in text

