from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

from automation.forex_engine import (
    forex_full_chainable_finish_line_orchestrator_v2 as orchestrator,
)
from automation.validators import aios_governance_validator


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = (
    ROOT
    / "scripts"
    / "forex_delivery"
    / "run_forex_full_chainable_finish_line_orchestrator_v2.py"
)
STATE_OUTPUT_PATH = orchestrator.DEFAULT_STATE_OUTPUT_PATH
REPORT_OUTPUT_PATH = orchestrator.DEFAULT_REPORT_OUTPUT_PATH
NEXT_PACKET_OUTPUT_PATH = orchestrator.DEFAULT_NEXT_PACKET_OUTPUT_PATH

EXPECTED_STAGES = [
    "first read-only broker probe review",
    "broker connection proof",
    "demo status and instrument probe",
    "demo readiness",
    "supervised demo execution readiness",
    "repeated demo P/L evidence intake",
    "strategy profitability evidence closure",
    "live micro exception review",
    "first live micro workflow readiness",
    "live monitoring evidence intake",
    "scaling and compounding policy",
    "long-session autonomy readiness",
    "22hr/day 6day/week governed operating readiness",
]
FORBIDDEN_IMPORT_ROOTS = {
    "requests",
    "socket",
    "urllib",
    "dotenv",
    "os",
    "oanda",
    "oandapyV20",
    "apscheduler",
    "schedule",
    "sched",
    "daemon",
    "webhook",
}


def test_stage_graph_contains_all_13_finish_line_stages():
    graph = orchestrator.build_stage_graph()

    assert [stage["name"] for stage in graph] == EXPECTED_STAGES
    assert len(graph) == 13


def test_current_stage_detected_from_existing_planner_state():
    result = orchestrator.run_forex_full_chainable_finish_line_orchestrator_v2()

    assert result["current_stage"] == "first read-only broker probe review"
    assert result["source_state_summary"]["selected_next_safe_packet"] == (
        "FIRST_READ_ONLY_BROKER_PROBE_REVIEW_DRY_RUN"
    )


def test_first_read_only_broker_probe_review_selected_when_repo_only():
    result = orchestrator.run_forex_full_chainable_finish_line_orchestrator_v2()

    assert result["next_stage"] == "broker connection proof"
    assert result["orchestrator_status"] == orchestrator.STATUS_OWNER_WAKE
    assert result["completed_repo_only_stage_count"] == 1
    assert result["repo_only_remaining_stage_count"] == 0
    assert result["protected_stage_count"] == 12
    assert result["safe_for_hours"] is False
    assert result["hours_ready"] is False
    assert result["owner_wake_required"] is True


@pytest.mark.parametrize(
    ("stage_name", "reason"),
    [
        ("broker connection proof", "broker contact"),
        ("broker connection proof", "credentials"),
        ("broker connection proof", ".env access"),
        ("broker connection proof", "account identifiers"),
        ("supervised demo execution readiness", "demo action"),
        ("first live micro workflow readiness", "live action"),
        ("supervised demo execution readiness", "trade evidence"),
        ("long-session autonomy readiness", "scheduler"),
        ("long-session autonomy readiness", "daemon"),
        ("long-session autonomy readiness", "webhook"),
        ("long-session autonomy readiness", "background loop"),
    ],
)
def test_protected_stage_classifications(stage_name: str, reason: str):
    graph = {stage["name"]: stage for stage in orchestrator.build_stage_graph()}

    assert graph[stage_name]["protected_action"] is True
    assert reason in graph[stage_name]["protected_action_reasons"]


def test_safe_for_hours_true_only_for_repo_only_dry_run_stage():
    graph = orchestrator.build_stage_graph()

    safe_stages = [stage["name"] for stage in graph if stage["safe_for_hours"]]
    assert safe_stages == ["first read-only broker probe review"]


def test_owner_wake_required_true_for_protected_action():
    graph = orchestrator.build_stage_graph()
    protected_stage = next(stage for stage in graph if stage["name"] == "broker connection proof")

    assert protected_stage["protected_action"] is True
    assert protected_stage["protected_action_reasons"]


def test_missing_source_state_fails_closed(monkeypatch, tmp_path):
    monkeypatch.setattr(orchestrator, "PLANNER_STATE_PATH", tmp_path / "missing.json")

    result = orchestrator.run_forex_full_chainable_finish_line_orchestrator_v2()

    assert result["orchestrator_status"] == orchestrator.STATUS_FAIL_CLOSED
    assert result["owner_wake_required"] is True
    assert result["source_errors"]


def test_invalid_next_packet_fails_closed():
    result = orchestrator.run_forex_full_chainable_finish_line_orchestrator_v2(
        packet_builder=lambda _result: "not a valid packet"
    )

    assert result["orchestrator_status"] == orchestrator.STATUS_FAIL_CLOSED
    assert result["owner_wake_required"] is True
    assert result["next_packet_governance_valid"] is False
    assert result["next_packet_validation_status"] == "BLOCKED"


def test_runner_writes_state_report_and_next_packet():
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "--write-state",
            "--write-report",
            "--write-next-packet",
        ],
        check=True,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )
    stdout_payload = json.loads(completed.stdout)
    state_payload = json.loads(STATE_OUTPUT_PATH.read_text(encoding="utf-8"))
    report_text = REPORT_OUTPUT_PATH.read_text(encoding="utf-8")
    next_packet_text = NEXT_PACKET_OUTPUT_PATH.read_text(encoding="utf-8")

    assert stdout_payload["state_output_path"] == str(STATE_OUTPUT_PATH)
    assert stdout_payload["report_output_path"] == str(REPORT_OUTPUT_PATH)
    assert stdout_payload["next_packet_output_path"] == str(NEXT_PACKET_OUTPUT_PATH)
    assert state_payload["orchestrator_status"] == orchestrator.STATUS_OWNER_WAKE
    assert state_payload["repo_only_remaining_stage_count"] == 0
    assert state_payload["next_stage"] == "broker connection proof"
    assert report_text.startswith(
        "# AIOS Forex Full Chainable Finish-Line Orchestrator V2 Report"
    )
    assert next_packet_text.startswith("CODEX-ONLY PROMPT")
    assert "AIOS_FOREX_BROKER_CONNECTION_PROOF_PROTECTED_BOUNDARY_REVIEW_V1" in next_packet_text


def test_generated_next_packet_passes_governance_validator():
    result = orchestrator.run_forex_full_chainable_finish_line_orchestrator_v2()
    packet_text = orchestrator.build_next_codex_packet(result)

    assert packet_text.startswith("CODEX-ONLY PROMPT")
    validation = aios_governance_validator.validate_packet_text(
        packet_text,
        str(NEXT_PACKET_OUTPUT_PATH),
    )
    assert validation["status"] == "PASS"


def test_repo_only_stage_completion_detected_from_owner_approval_boundary():
    result = orchestrator.run_forex_full_chainable_finish_line_orchestrator_v2()

    assert result["completed_repo_only_stages"] == ["first read-only broker probe review"]
    assert result["current_autonomy_level"] == "PROTECTED_OWNER_BOUNDARY_REQUIRED"
    assert result["forex_completion_percent"] == 7.69


def test_state_contains_required_safety_false_fields():
    result = orchestrator.run_forex_full_chainable_finish_line_orchestrator_v2()

    for field in [
        "broker_api_used",
        "credentials_used",
        "env_read",
        "account_identifiers_used",
        "order_execution",
        "demo_authorized",
        "live_authorized",
        "scheduler_started",
        "daemon_started",
        "webhook_started",
        "background_loop_started",
        "commit_created",
        "push_created",
        "pr_created",
    ]:
        assert result[field] is False


def test_no_forbidden_imports_or_environment_access():
    for path in [
        ROOT
        / "automation"
        / "forex_engine"
        / "forex_full_chainable_finish_line_orchestrator_v2.py",
        RUNNER_PATH,
    ]:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )

        assert imports.isdisjoint(FORBIDDEN_IMPORT_ROOTS)
        assert "os.environ" not in source
        assert ".environ" not in source
        assert "dotenv" not in source
