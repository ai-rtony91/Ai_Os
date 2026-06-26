from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

import pytest

from automation.forex_engine import oanda_demo_read_only_pl_profit_proof_epic_v1 as e


REPO_ROOT = Path(__file__).resolve().parents[2]

PROTECTED_FLAGS = (
    "demo_execution_allowed",
    "broker_action_allowed",
    "real_money_allowed",
    "compounding_allowed",
    "bank_movement_allowed",
    "live_trading_allowed",
    "credential_access_allowed",
    "account_id_persistence_allowed",
    "autonomous_execution_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
)

NEW_SOURCE_FILES = (
    "automation/forex_engine/oanda_demo_read_only_pl_result_intake_v1.py",
    "automation/forex_engine/oanda_demo_pl_result_quality_gate_v1.py",
    "automation/forex_engine/oanda_demo_profit_proof_ledger_bridge_v1.py",
    "automation/forex_engine/oanda_demo_read_only_pl_profit_proof_epic_v1.py",
    "scripts/forex_delivery/run_oanda_demo_read_only_pl_result_intake_v1.py",
    "scripts/forex_delivery/run_oanda_demo_profit_proof_ledger_bridge_v1.py",
    "scripts/forex_delivery/run_oanda_demo_read_only_pl_profit_proof_epic_v1.py",
)


def _json(input_obj=None):
    result = e.run_oanda_demo_read_only_pl_profit_proof_epic(
        input_obj or e.build_sample_profit_epic_input()
    )
    return e.oanda_demo_read_only_pl_profit_proof_epic_to_jsonable_dict(result)


def _run_script(monkeypatch, capsys, relative_path: str, *args: str) -> str:
    script = str(REPO_ROOT / relative_path)
    monkeypatch.setattr(sys, "argv", [script, *args])
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(script, run_name="__main__")
    assert exc.value.code == 0
    return capsys.readouterr().out


def test_epic_profit_sample_ready():
    data = _json(e.build_sample_profit_epic_input())
    assert data["classification"] == "OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_READY_FOR_OWNER_REVIEW"
    assert data["result_bucket"] == "PROFIT"


def test_epic_loss_sample_ready_for_review():
    data = _json(e.build_sample_loss_epic_input())
    assert data["classification"] == "OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_READY_FOR_OWNER_REVIEW"
    assert data["result_bucket"] == "LOSS"
    assert data["bucket_recommendation"] == "LOSS_SAMPLE_ACCEPTED_FOR_REVIEW"


def test_epic_breakeven_sample_ready_for_review():
    data = _json(e.build_sample_breakeven_epic_input())
    assert data["classification"] == "OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_READY_FOR_OWNER_REVIEW"
    assert data["result_bucket"] == "BREAKEVEN"


def test_epic_incomplete_blocked():
    data = _json(e.build_sample_incomplete_epic_input())
    assert data["classification"] == "OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_BLOCKED"
    assert data["profit_claim_status"] == "BLOCKED_RESULT_INCOMPLETE"


def test_epic_unsafe_blocked():
    data = _json(e.build_sample_unsafe_epic_input())
    assert data["classification"] == "OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_BLOCKED"
    assert data["profit_claim_status"] == "BLOCKED_UNSAFE"


def test_epic_includes_one_sentence_answer():
    assert _json()["one_sentence_answer"] == (
        "AIOS can now intake one sanitized OANDA demo filled-trade P/L result "
        "for profit-proof routing, but repeated expectancy proof and live evidence "
        "remain separate gates."
    )


def test_epic_includes_exact_next_owner_action():
    assert _json()["exact_next_owner_action"] == (
        "Review sanitized read-only P/L result and approve routing into the local "
        "profit proof ledger review lane if the evidence is accurate."
    )


def test_epic_includes_exact_next_codex_packet():
    assert _json()["exact_next_codex_packet"] == (
        "AIOS-FOREX-OANDA-DEMO-REPEATED-EXPECTANCY-SAMPLE-ACCUMULATOR-V1"
    )


def test_epic_includes_profit_claim_status():
    assert _json()["profit_claim_status"] == "FIRST_RESULT_READY_FOR_PROOF_REVIEW"


def test_epic_includes_live_profit_status():
    assert _json()["live_profit_status"] == (
        "LIVE_PROFITABLE_EXECUTION_STILL_BLOCKED_PENDING_REPEATED_DEMO_PROOF_AND_LIVE_EVIDENCE_BUNDLE"
    )


def test_epic_says_repeated_expectancy_sample_still_required():
    assert _json()["repeated_expectancy_gate"] == "REPEATED_EXPECTANCY_SAMPLE_STILL_REQUIRED"


def test_epic_says_live_evidence_bundle_still_required():
    assert "LIVE_EVIDENCE_BUNDLE" in _json()["live_profit_status"]


def test_epic_json_serializable():
    json.dumps(_json(), sort_keys=True)


def test_epic_markdown_title():
    result = e.run_oanda_demo_read_only_pl_profit_proof_epic(e.build_sample_profit_epic_input())
    assert e.oanda_demo_read_only_pl_profit_proof_epic_to_markdown(result).startswith(
        "# AIOS Forex OANDA Demo Read Only P/L Profit Proof Epic V1"
    )


def test_epic_operator_text_plain():
    result = e.run_oanda_demo_read_only_pl_profit_proof_epic(e.build_sample_profit_epic_input())
    text = e.oanda_demo_read_only_pl_profit_proof_epic_to_operator_text(result)
    assert "epic_classification:" in text
    assert "no_broker_call_made_by_this_packet: true" in text


def test_epic_permissions_false():
    data = _json()
    assert all(data[flag] is False for flag in PROTECTED_FLAGS)
    assert all(data["permissions"][flag] is False for flag in PROTECTED_FLAGS)


def test_all_protected_flags_false_in_every_top_level_output():
    for sample in (
        e.build_sample_profit_epic_input(),
        e.build_sample_loss_epic_input(),
        e.build_sample_breakeven_epic_input(),
        e.build_sample_incomplete_epic_input(),
        e.build_sample_unsafe_epic_input(),
    ):
        data = _json(sample)
        assert all(data[flag] is False for flag in PROTECTED_FLAGS)


def test_profit_result_does_not_approve_demo_execution():
    assert _json(e.build_sample_profit_epic_input())["demo_execution_allowed"] is False


def test_profit_result_does_not_approve_broker_action():
    assert _json(e.build_sample_profit_epic_input())["broker_action_allowed"] is False


def test_loss_result_does_not_approve_demo_execution():
    assert _json(e.build_sample_loss_epic_input())["demo_execution_allowed"] is False


def test_loss_result_does_not_approve_broker_action():
    assert _json(e.build_sample_loss_epic_input())["broker_action_allowed"] is False


def test_exact_owner_warning_present():
    assert _json()["owner_warning"] == "Do not execute unless Anthony explicitly approves."


def test_exact_read_only_warning_present():
    assert _json()["read_only_warning"] == (
        "Read-only P/L evidence intake only. Codex is not authorized to execute, "
        "call a broker, access credentials, or place orders."
    )


def test_exact_one_sentence_answer_present():
    assert "AIOS can now intake one sanitized OANDA demo filled-trade P/L result" in _json()[
        "one_sentence_answer"
    ]


def test_profit_proof_status_distinguishes_first_result_from_repeated_sample():
    data = _json()
    assert data["profit_claim_status"] == "FIRST_RESULT_READY_FOR_PROOF_REVIEW"
    assert data["repeated_expectancy_gate"] == "REPEATED_EXPECTANCY_SAMPLE_STILL_REQUIRED"


def test_live_profit_status_remains_blocked():
    assert "STILL_BLOCKED" in _json()["live_profit_status"]


def test_next_codex_packet_is_repeated_expectancy_sample_accumulator():
    assert _json()["exact_next_codex_packet"].endswith(
        "REPEATED-EXPECTANCY-SAMPLE-ACCUMULATOR-V1"
    )


def test_epic_planned_risk_propagated():
    assert _json()["planned_risk"] == "2.00"


def test_epic_realized_r_multiple_propagated():
    assert _json()["realized_r_multiple"] == "0.6000"


def test_epic_ledger_preview_present():
    assert _json()["ledger_entry_preview"]["preview_only"] is True


def test_epic_expectancy_preview_present():
    assert _json()["expectancy_sample_preview"]["single_result_only"] is True


def test_epic_routing_targets_present():
    assert "Profit Proof Ledger" in _json()["routing_targets"]


def test_runner_intake_emits_text(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_read_only_pl_result_intake_v1.py",
        "--sample-profit",
    )
    assert "Read-only P/L intake status:" in output


def test_runner_intake_emits_json(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_read_only_pl_result_intake_v1.py",
        "--sample-loss",
        "--json",
    )
    assert json.loads(output)["result_bucket"] == "LOSS"


def test_runner_intake_emits_markdown(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_read_only_pl_result_intake_v1.py",
        "--sample-breakeven",
        "--markdown",
    )
    assert output.startswith("# AIOS Forex OANDA Demo Read Only P/L Result Intake V1")


def test_runner_bridge_emits_text(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_profit_proof_ledger_bridge_v1.py",
        "--sample-profit",
    )
    assert "Profit proof ledger bridge status:" in output


def test_runner_bridge_emits_json(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_profit_proof_ledger_bridge_v1.py",
        "--sample-loss",
        "--json",
    )
    assert json.loads(output)["result_bucket"] == "LOSS"


def test_runner_bridge_emits_markdown(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_profit_proof_ledger_bridge_v1.py",
        "--sample-breakeven",
        "--markdown",
    )
    assert output.startswith("# AIOS Forex OANDA Demo Profit Proof Ledger Bridge V1")


def test_runner_epic_emits_text(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_read_only_pl_profit_proof_epic_v1.py",
        "--sample-profit",
    )
    assert "epic_classification:" in output


def test_runner_epic_emits_json(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_read_only_pl_profit_proof_epic_v1.py",
        "--sample-profit",
        "--json",
    )
    assert json.loads(output)["one_sentence_answer"] == e.EXACT_ONE_SENTENCE_ANSWER


def test_runner_epic_emits_markdown(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_read_only_pl_profit_proof_epic_v1.py",
        "--sample-profit",
        "--markdown",
    )
    assert output.startswith("# AIOS Forex OANDA Demo Read Only P/L Profit Proof Epic V1")


@pytest.mark.parametrize(
    "pattern",
    (
        "import requests",
        "from requests",
        "import httpx",
        "from httpx",
        "import socket",
        "from socket",
        "import dotenv",
        "from dotenv",
        "import keyring",
        "from keyring",
        "import subprocess",
        "from subprocess",
        "import oanda",
        "from oanda",
        "broker_mutation",
        "broker_execution",
    ),
)
def test_static_safety_forbidden_imports_absent(pattern):
    for path in NEW_SOURCE_FILES:
        text = (REPO_ROOT / path).read_text(encoding="utf-8").lower()
        assert pattern not in text


@pytest.mark.parametrize(
    "pattern",
    (
        "read_env",
        "open(\".env",
        "open('.env",
        "place_order",
        "submit_order",
        "create_order",
        "live trading approved",
        "real money approved",
        "compounding approved",
        "bank movement approved",
        "def scheduler",
        "def daemon",
        "def webhook",
    ),
)
def test_static_safety_forbidden_behaviors_absent(pattern):
    for path in NEW_SOURCE_FILES:
        text = (REPO_ROOT / path).read_text(encoding="utf-8").lower()
        assert pattern not in text


def test_manual_finalization_report_includes_exact_git_add_commands():
    text = (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_MANUAL_FINALIZATION_V1.md"
    ).read_text(encoding="utf-8")
    assert "git add automation/forex_engine/oanda_demo_read_only_pl_result_intake_v1.py" in text
    assert "git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_MANUAL_FINALIZATION_V1.md" in text


def test_manual_finalization_report_says_no_git_add_dot():
    text = (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_MANUAL_FINALIZATION_V1.md"
    ).read_text(encoding="utf-8")
    assert "Do not use `git add .`." in text


def test_epic_report_says_no_trade_placed():
    text = (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_EPIC_REPORT_V1.md"
    ).read_text(encoding="utf-8")
    assert "No trade placed by this packet." in text


def test_epic_report_says_no_broker_call_made():
    text = (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_EPIC_REPORT_V1.md"
    ).read_text(encoding="utf-8")
    assert "No broker call was made by this packet." in text


def test_epic_report_static_safety_says_pass():
    text = (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_EPIC_REPORT_V1.md"
    ).read_text(encoding="utf-8")
    assert "STATIC_SAFETY_RESULT: PASS" in text


def test_source_files_missing_are_recorded():
    text = (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_EPIC_REPORT_V1.md"
    ).read_text(encoding="utf-8")
    assert "SOURCE_FILES_MISSING: none" in text


def test_source_files_read_are_recorded():
    text = (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_EPIC_REPORT_V1.md"
    ).read_text(encoding="utf-8")
    assert "SOURCE_FILES_READ:" in text
    assert "automation/forex_engine/oanda_demo_execution_truth_epic_v1.py" in text


def test_report_names_exact_next_owner_action():
    text = (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_EPIC_REPORT_V1.md"
    ).read_text(encoding="utf-8")
    assert e.EXACT_NEXT_OWNER_ACTION in text


def test_report_names_exact_next_packet():
    text = (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_EPIC_REPORT_V1.md"
    ).read_text(encoding="utf-8")
    assert e.EXACT_NEXT_CODEX_PACKET in text


def test_markdown_includes_exact_one_sentence_answer():
    result = e.run_oanda_demo_read_only_pl_profit_proof_epic(e.build_sample_profit_epic_input())
    assert e.EXACT_ONE_SENTENCE_ANSWER in e.oanda_demo_read_only_pl_profit_proof_epic_to_markdown(result)


def test_json_includes_exact_one_sentence_answer():
    assert _json()["one_sentence_answer"] == e.EXACT_ONE_SENTENCE_ANSWER


def test_epic_version_constant_present():
    assert e.VERSION == "oanda_demo_read_only_pl_profit_proof_epic_v1"
    assert e.OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_EPIC_VERSION == e.VERSION
