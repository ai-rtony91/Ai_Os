from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

import pytest

from automation.forex_engine import oanda_demo_repeated_expectancy_sample_epic_v1 as m


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
    "automation/forex_engine/oanda_demo_expectancy_sample_intake_v1.py",
    "automation/forex_engine/oanda_demo_repeated_expectancy_accumulator_v1.py",
    "automation/forex_engine/oanda_demo_expectancy_sufficiency_gate_v1.py",
    "automation/forex_engine/oanda_demo_repeated_expectancy_sample_epic_v1.py",
    "scripts/forex_delivery/run_oanda_demo_expectancy_sample_intake_v1.py",
    "scripts/forex_delivery/run_oanda_demo_repeated_expectancy_accumulator_v1.py",
    "scripts/forex_delivery/run_oanda_demo_repeated_expectancy_sample_epic_v1.py",
)


def _json(sample=None):
    result = m.run_oanda_demo_repeated_expectancy_sample_epic(
        sample or m.build_sample_strong_repeated_expectancy_epic_input()
    )
    return m.oanda_demo_repeated_expectancy_sample_epic_to_jsonable_dict(result)


def _run_script(monkeypatch, capsys, relative_path: str, *args: str) -> str:
    script = str(REPO_ROOT / relative_path)
    monkeypatch.setattr(sys, "argv", [script, *args])
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(script, run_name="__main__")
    assert exc.value.code == 0
    return capsys.readouterr().out


def test_epic_strong_ready_for_owner_review():
    assert _json()["classification"] == "OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_READY_FOR_OWNER_REVIEW"


def test_epic_weak_require_more_evidence():
    assert _json(m.build_sample_weak_repeated_expectancy_epic_input())["classification"] == (
        "OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_REQUIRE_MORE_EVIDENCE"
    )


def test_epic_insufficient_require_more_evidence():
    assert _json(m.build_sample_insufficient_repeated_expectancy_epic_input())["classification"] == (
        "OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_REQUIRE_MORE_EVIDENCE"
    )


def test_epic_losing_rejected():
    assert _json(m.build_sample_losing_repeated_expectancy_epic_input())["classification"] == (
        "OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_REJECTED"
    )


def test_epic_unsafe_blocked():
    assert _json(m.build_sample_unsafe_repeated_expectancy_epic_input())["classification"] == (
        "OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_BLOCKED"
    )


def test_epic_includes_one_sentence_answer():
    assert _json()["one_sentence_answer"] == m.EXACT_ONE_SENTENCE_ANSWER


def test_epic_includes_sample_intake_status():
    assert _json()["sample_intake_status"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED"


def test_epic_includes_accumulator_status():
    assert _json()["accumulator_status"] == "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_STRONG"


def test_epic_includes_sufficiency_status():
    assert _json()["sufficiency_status"] == (
        "OANDA_DEMO_EXPECTANCY_SUFFICIENCY_READY_FOR_OWNER_PROOF_REVIEW"
    )


def test_epic_includes_result_count():
    assert _json()["result_count"] == 10


def test_epic_includes_win_rate():
    assert _json()["win_rate"] == "0.7000"


def test_epic_includes_profit_factor():
    assert _json()["profit_factor"] == "8.5556"


def test_epic_includes_expectancy_per_trade():
    assert _json()["expectancy_per_trade"] == "0.6800"


def test_epic_includes_average_r():
    assert _json()["average_r"] == "0.3400"


def test_epic_includes_proof_packet_preview():
    preview = _json()["proof_packet_preview"]
    assert preview["preview_only"] is True
    assert preview["proof_type"] == "repeated_demo_expectancy_sample"


def test_epic_includes_routing_targets():
    assert "Profit Proof Ledger" in _json()["routing_targets"]


def test_epic_includes_profit_claim_status():
    assert _json()["profit_claim_status"] == "REPEATED_EXPECTANCY_READY_FOR_OWNER_PROOF_REVIEW"


def test_epic_includes_live_profit_status():
    assert _json()["live_profit_status"] == (
        "LIVE_PROFITABLE_EXECUTION_STILL_BLOCKED_PENDING_LIVE_EVIDENCE_BUNDLE"
    )


def test_epic_includes_exact_next_owner_action():
    assert _json()["exact_next_owner_action"] == m.EXACT_NEXT_OWNER_ACTION


def test_epic_includes_exact_next_codex_packet():
    assert _json()["exact_next_codex_packet"] == m.EXACT_NEXT_CODEX_PACKET


def test_epic_says_repeated_expectancy_proof_is_not_live_authority():
    payload = json.dumps(_json(), sort_keys=True).lower()
    assert "live_execution_authority" in payload
    assert "repeated expectancy proof is not live execution authority" in (
        m.oanda_demo_repeated_expectancy_sample_epic_to_operator_text(
            m.run_oanda_demo_repeated_expectancy_sample_epic(
                m.build_sample_strong_repeated_expectancy_epic_input()
            )
        ).lower()
    )


def test_epic_says_live_evidence_bundle_still_required():
    assert "LIVE_EVIDENCE_BUNDLE" in _json()["live_profit_status"]


def test_epic_json_serializable():
    json.dumps(_json(), sort_keys=True)


def test_epic_markdown_title():
    result = m.run_oanda_demo_repeated_expectancy_sample_epic(
        m.build_sample_strong_repeated_expectancy_epic_input()
    )
    assert m.oanda_demo_repeated_expectancy_sample_epic_to_markdown(result).startswith(
        "# AIOS Forex OANDA Demo Repeated Expectancy Sample Epic V1"
    )


def test_epic_operator_text_plain():
    result = m.run_oanda_demo_repeated_expectancy_sample_epic(
        m.build_sample_strong_repeated_expectancy_epic_input()
    )
    text = m.oanda_demo_repeated_expectancy_sample_epic_to_operator_text(result)
    assert "repeated_expectancy_sample_status:" in text
    assert "no_broker_call_made_by_this_packet: true" in text


def test_epic_permissions_false():
    data = _json()
    assert all(data[flag] is False for flag in PROTECTED_FLAGS)
    assert all(data["permissions"][flag] is False for flag in PROTECTED_FLAGS)


def test_all_protected_flags_false_in_every_top_level_output():
    for sample in (
        m.build_sample_strong_repeated_expectancy_epic_input(),
        m.build_sample_weak_repeated_expectancy_epic_input(),
        m.build_sample_insufficient_repeated_expectancy_epic_input(),
        m.build_sample_losing_repeated_expectancy_epic_input(),
        m.build_sample_unsafe_repeated_expectancy_epic_input(),
    ):
        data = _json(sample)
        assert all(data[flag] is False for flag in PROTECTED_FLAGS)


def test_strong_sample_does_not_approve_demo_execution():
    assert _json()["demo_execution_allowed"] is False


def test_strong_sample_does_not_approve_broker_action():
    assert _json()["broker_action_allowed"] is False


def test_strong_sample_does_not_approve_live_trading():
    assert _json()["live_trading_allowed"] is False


def test_losing_sample_does_not_approve_demo_execution():
    assert _json(m.build_sample_losing_repeated_expectancy_epic_input())["demo_execution_allowed"] is False


def test_losing_sample_does_not_approve_broker_action():
    assert _json(m.build_sample_losing_repeated_expectancy_epic_input())["broker_action_allowed"] is False


def test_no_raw_account_data_appears_in_json():
    assert "RAW_ACCOUNT" not in json.dumps(_json(), sort_keys=True)


def test_no_raw_credential_data_appears_in_json():
    payload = json.dumps(_json(), sort_keys=True)
    assert "RAW_CREDENTIAL" not in payload
    assert "sk-" not in payload


def test_no_raw_broker_order_id_appears_in_json():
    assert "RAW_BROKER_ORDER" not in json.dumps(_json(), sort_keys=True)


def test_no_live_endpoint_text_appears_in_output():
    assert "live endpoint" not in json.dumps(_json(), sort_keys=True).lower()


def test_no_live_execution_wording_appears_as_approved():
    payload = json.dumps(_json(), sort_keys=True).lower()
    assert "live execution approved" not in payload
    assert '"live_trading_allowed": true' not in payload


def test_next_codex_packet_is_live_evidence_bundle_gap_bridge():
    assert _json()["exact_next_codex_packet"] == (
        "AIOS-FOREX-OANDA-DEMO-EXPECTANCY-TO-LIVE-EVIDENCE-BUNDLE-GAP-BRIDGE-V1"
    )


def test_output_deterministic_for_strong():
    assert _json(m.build_sample_strong_repeated_expectancy_epic_input()) == _json(
        m.build_sample_strong_repeated_expectancy_epic_input()
    )


def test_output_deterministic_for_weak():
    assert _json(m.build_sample_weak_repeated_expectancy_epic_input()) == _json(
        m.build_sample_weak_repeated_expectancy_epic_input()
    )


def test_output_deterministic_for_unsafe():
    assert _json(m.build_sample_unsafe_repeated_expectancy_epic_input()) == _json(
        m.build_sample_unsafe_repeated_expectancy_epic_input()
    )


def test_decimal_output_stable():
    data = _json()
    assert data["total_realized_pl"] == "6.8000"
    assert data["average_r"] == "0.3400"


def test_exact_owner_warning_present():
    assert _json()["owner_warning"] == "Do not execute unless Anthony explicitly approves."


def test_exact_expectancy_warning_present():
    assert _json()["expectancy_warning"] == (
        "Repeated expectancy review only. Codex is not authorized to execute, "
        "call a broker, access credentials, or place orders."
    )


def test_exact_one_sentence_answer_present():
    assert _json()["one_sentence_answer"] == m.EXACT_ONE_SENTENCE_ANSWER


def test_routing_targets_include_profit_proof_ledger():
    assert "Profit Proof Ledger" in _json()["routing_targets"]


def test_routing_targets_include_strategy_proof_engine():
    assert "Strategy Proof Engine" in _json()["routing_targets"]


def test_routing_targets_include_expectancy_strength_router():
    assert "Expectancy Strength Router" in _json()["routing_targets"]


def test_routing_targets_include_real_evidence_depth_engine():
    assert "Real Evidence Depth Engine" in _json()["routing_targets"]


def test_routing_targets_include_demo_review_engine():
    assert "Demo Review Engine" in _json()["routing_targets"]


def test_routing_targets_include_strategy_promotion_router():
    assert "Strategy Promotion Router" in _json()["routing_targets"]


def test_loss_sample_routes_to_loss_to_next_profit_candidate_gate():
    data = _json(m.build_sample_losing_repeated_expectancy_epic_input())
    assert "Loss To Next Profit Candidate Gate" in data["routing_targets"]


def test_proof_packet_preview_is_preview_only_true():
    assert _json()["proof_packet_preview"]["preview_only"] is True


def test_no_existing_ledger_file_is_mutated():
    assert _json()["proof_packet_preview"]["mutates_existing_ledger_file"] is False


def test_runner_intake_emits_text(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_expectancy_sample_intake_v1.py",
        "--sample-strong",
    )
    assert "Repeated expectancy sample intake status:" in output


def test_runner_intake_emits_json(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_expectancy_sample_intake_v1.py",
        "--sample-strong",
        "--json",
    )
    assert json.loads(output)["classification"] == "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED"


def test_runner_intake_emits_markdown(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_expectancy_sample_intake_v1.py",
        "--sample-losing",
        "--markdown",
    )
    assert output.startswith("# AIOS Forex OANDA Demo Expectancy Sample Intake V1")


def test_runner_accumulator_emits_text(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_repeated_expectancy_accumulator_v1.py",
        "--sample-strong",
    )
    assert "Repeated expectancy accumulator status:" in output


def test_runner_accumulator_emits_json(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_repeated_expectancy_accumulator_v1.py",
        "--sample-losing",
        "--json",
    )
    assert json.loads(output)["classification"] == "OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATED_LOSING"


def test_runner_accumulator_emits_markdown(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_repeated_expectancy_accumulator_v1.py",
        "--sample-weak",
        "--markdown",
    )
    assert output.startswith("# AIOS Forex OANDA Demo Repeated Expectancy Accumulator V1")


def test_runner_epic_emits_text(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_repeated_expectancy_sample_epic_v1.py",
        "--sample-strong",
    )
    assert "repeated_expectancy_sample_status:" in output


def test_runner_epic_emits_json(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_repeated_expectancy_sample_epic_v1.py",
        "--sample-strong",
        "--json",
    )
    assert json.loads(output)["one_sentence_answer"] == m.EXACT_ONE_SENTENCE_ANSWER


def test_runner_epic_emits_markdown(monkeypatch, capsys):
    output = _run_script(
        monkeypatch,
        capsys,
        "scripts/forex_delivery/run_oanda_demo_repeated_expectancy_sample_epic_v1.py",
        "--sample-strong",
        "--markdown",
    )
    assert output.startswith("# AIOS Forex OANDA Demo Repeated Expectancy Sample Epic V1")


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


def test_no_git_add_dot_in_report():
    text = (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_MANUAL_FINALIZATION_V1.md"
    ).read_text(encoding="utf-8")
    assert "Do not use `git add .`." in text


def test_manual_finalization_report_includes_exact_git_add_commands():
    text = (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_MANUAL_FINALIZATION_V1.md"
    ).read_text(encoding="utf-8")
    assert "git add automation/forex_engine/oanda_demo_expectancy_sample_intake_v1.py" in text
    assert "git add Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_MANUAL_FINALIZATION_V1.md" in text


def test_epic_report_says_no_trade_placed():
    text = (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_EPIC_REPORT_V1.md"
    ).read_text(encoding="utf-8")
    assert "No trade placed by this packet." in text


def test_epic_report_says_no_broker_call_made():
    text = (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_EPIC_REPORT_V1.md"
    ).read_text(encoding="utf-8")
    assert "No broker call was made by this packet." in text


def test_static_safety_says_pass():
    text = (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_EPIC_REPORT_V1.md"
    ).read_text(encoding="utf-8")
    assert "STATIC_SAFETY_RESULT: PASS" in text


def test_source_files_missing_are_recorded():
    text = (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_EPIC_REPORT_V1.md"
    ).read_text(encoding="utf-8")
    assert "SOURCE_FILES_MISSING: none" in text


def test_source_files_read_are_recorded():
    text = (
        REPO_ROOT
        / "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_EPIC_REPORT_V1.md"
    ).read_text(encoding="utf-8")
    assert "SOURCE_FILES_READ:" in text
    assert "automation/forex_engine/oanda_demo_read_only_pl_profit_proof_epic_v1.py" in text


def test_all_reports_mention_permissions_false():
    for path in (
        "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_V1.md",
        "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATOR_V1.md",
        "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXPECTANCY_SUFFICIENCY_GATE_V1.md",
        "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_EPIC_REPORT_V1.md",
    ):
        assert "permissions false" in (REPO_ROOT / path).read_text(encoding="utf-8").lower()


def test_all_reports_mention_no_broker_call_no_trade_placed():
    for path in (
        "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_V1.md",
        "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATOR_V1.md",
        "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_EXPECTANCY_SUFFICIENCY_GATE_V1.md",
        "Reports/forex_delivery/AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_EPIC_REPORT_V1.md",
    ):
        text = (REPO_ROOT / path).read_text(encoding="utf-8")
        assert "No trade placed by this packet." in text
        assert "No broker call" in text


def test_epic_version_constant_present():
    assert m.VERSION == "oanda_demo_repeated_expectancy_sample_epic_v1"
    assert m.OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_EPIC_VERSION == m.VERSION
