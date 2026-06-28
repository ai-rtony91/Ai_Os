"""Tests for the new Forex owner evidence return orchestration lane."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from automation.forex_engine import forex_closure_gap_router_v1 as router_lib
from automation.forex_engine import (
    forex_final_owner_review_packet_composer_v1 as composer_lib,
)
from automation.forex_engine import (
    forex_owner_evidence_return_intake_v1 as intake_lib,
)
from automation.forex_engine import (
    forex_owner_evidence_return_orchestrator_v1 as orchestrator_lib,
)
from automation.forex_engine import (
    forex_owner_evidence_return_validator_v1 as validator_lib,
)
from automation.forex_engine import forex_readiness_checkpoint_ledger_v1 as ledger_lib

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "forex_delivery" / "owner_evidence_return_v1"
SCRIPTS_DIR = REPO_ROOT / "scripts" / "forex_delivery"

NEW_PYTHON_FILES = [
    REPO_ROOT / "automation/forex_engine/forex_owner_evidence_return_intake_v1.py",
    REPO_ROOT / "automation/forex_engine/forex_owner_evidence_return_validator_v1.py",
    REPO_ROOT / "automation/forex_engine/forex_closure_gap_router_v1.py",
    REPO_ROOT / "automation/forex_engine/forex_final_owner_review_packet_composer_v1.py",
    REPO_ROOT / "automation/forex_engine/forex_readiness_checkpoint_ledger_v1.py",
    REPO_ROOT / "automation/forex_engine/forex_owner_evidence_return_orchestrator_v1.py",
    REPO_ROOT / "scripts/forex_delivery/run_forex_owner_evidence_return_intake_v1.py",
    REPO_ROOT / "scripts/forex_delivery/run_forex_owner_evidence_return_validator_v1.py",
    REPO_ROOT / "scripts/forex_delivery/run_forex_closure_gap_router_v1.py",
    REPO_ROOT / "scripts/forex_delivery/run_forex_final_owner_review_packet_composer_v1.py",
    REPO_ROOT / "scripts/forex_delivery/run_forex_owner_evidence_return_orchestrator_v1.py",
]


@pytest.fixture(scope="module")
def fixture_paths() -> list[Path]:
    return sorted(FIXTURE_DIR.glob("*"))


def test_fixture_directory_exists() -> None:
    assert FIXTURE_DIR.exists()


def test_fixture_directory_has_minimum_45_records(fixture_paths: list[Path]) -> None:
    assert len(fixture_paths) >= 45


@pytest.mark.parametrize("path", [p for p in Path(__file__).resolve().parents[1].glob("fixtures/forex_delivery/owner_evidence_return_v1/*")])
def test_fixture_files_are_non_empty(path: Path) -> None:
    assert path.exists()
    assert path.stat().st_size > 0


@pytest.mark.parametrize("path", [p for p in Path(__file__).resolve().parents[1].glob("fixtures/forex_delivery/owner_evidence_return_v1/*")])
def test_fixture_payloads_load_for_intake(path: Path) -> None:
    if path.suffix.lower() == ".json":
        payload = intake_lib.read_owner_evidence_payload(path)
        assert isinstance(payload, list)
        assert payload
        assert isinstance(payload[0], dict)
    else:
        payload = intake_lib.read_owner_evidence_payload(path)
        assert isinstance(payload, list)
        assert payload
        entry = payload[0]
        assert "family" in entry or "evidence family" in entry


def test_intake_build_is_deterministic() -> None:
    catalog_path = REPO_ROOT / "tests" / "fixtures" / "forex_delivery" / "owner_evidence_return_v1"
    catalog_inputs = tuple(sorted(catalog_path.glob("*")))
    first = intake_lib.build_owner_evidence_return_intake(catalog_payload=intake_lib.catalog_lib.build_missing_evidence_catalog(report_paths=catalog_inputs))
    second = intake_lib.build_owner_evidence_return_intake(catalog_payload=intake_lib.catalog_lib.build_missing_evidence_catalog(report_paths=catalog_inputs))
    assert first["summary"]["total_items"] == second["summary"]["total_items"]


def test_intake_markdown_contains_route_info() -> None:
    payload = intake_lib.build_owner_evidence_return_intake(None, catalog_paths=(FIXTURE_DIR,))
    markdown = intake_lib.intake_to_markdown(payload)
    assert "Forex Owner Evidence Return Intake V1" in markdown
    assert "Missing Requested Families" in markdown


def test_validator_detects_sensitive_markers() -> None:
    payload = "family: candidate evidence\nsample count: 100\nevidence location: account_id = 1234\nowner confirmation: confirmed\n"
    result = validator_lib.validate_owner_evidence_return_text(payload, strict=False)
    assert result["status"] == validator_lib.OWNER_RETURN_BLOCKED
    assert result["sensitive_hits"]


def test_validator_repairable_when_sample_low() -> None:
    payload = "family: candidate evidence\nsample count: 10\nevidence location: local_reports/sample.md\nowner confirmation: confirmed\n"
    result = validator_lib.validate_owner_evidence_return_text(payload, strict=False, min_sample=30)
    assert result["status"] == validator_lib.OWNER_RETURN_REPAIRABLE
    assert result["sample_count"] == 10


def test_validator_allows_clean_payload() -> None:
    payload = (
        "Owner evidence return\nfamily: candidate evidence\nsample count: 40\n"
        "evidence location: local_reports/sample.md\nowner confirmation: confirmed\n"
    )
    result = validator_lib.validate_owner_evidence_return_text(payload, strict=False)
    assert result["status"] == validator_lib.OWNER_RETURN_VALID


def test_router_ready_route_when_no_gaps() -> None:
    intake_payload = {
        "owner_required_families": [],
        "local_repair_families": [],
        "summary": {"missing_items": 0},
    }
    validator_payload = {"status": validator_lib.OWNER_RETURN_VALID}
    result = router_lib.route_owner_evidence_closure(intake_payload, validator_payload)
    assert result["route"] == router_lib.ROUTE_READY_FOR_REVIEW


def test_router_owner_required_route() -> None:
    intake_payload = {
        "owner_required_families": ["owner approval evidence"],
        "local_repair_families": [],
    }
    validator_payload = {"status": validator_lib.OWNER_RETURN_VALID}
    result = router_lib.route_owner_evidence_closure(intake_payload, validator_payload)
    assert result["route"] == router_lib.ROUTE_OWNER_EVIDENCE_REQUIRED


def test_router_local_repair_route() -> None:
    intake_payload = {
        "owner_required_families": [],
        "local_repair_families": ["walk-forward evidence"],
    }
    validator_payload = {
        "status": validator_lib.OWNER_RETURN_REPAIRABLE,
    }
    result = router_lib.route_owner_evidence_closure(intake_payload, validator_payload)
    assert result["route"] == router_lib.ROUTE_LOCAL_REPAIR


def test_router_blocked_route() -> None:
    intake_payload = {"owner_required_families": [], "local_repair_families": []}
    validator_payload = {"status": validator_lib.OWNER_RETURN_BLOCKED}
    result = router_lib.route_owner_evidence_closure(intake_payload, validator_payload)
    assert result["route"] == router_lib.ROUTE_BLOCKED_BY_SAFETY


def test_composer_ready_status() -> None:
    packet = composer_lib.compose_final_owner_review_packet(
        {"status": "INTAKE_COMPLETE", "intake_items": []},
        {"status": validator_lib.OWNER_RETURN_VALID},
        {"route": router_lib.ROUTE_READY_FOR_REVIEW, "owner_gap_families": [], "local_gap_families": []},
    )
    assert packet["status"] == composer_lib.FINAL_PACKET_READY


def test_composer_owner_return_status() -> None:
    packet = composer_lib.compose_final_owner_review_packet(
        {"status": "INTAKE_PARTIAL", "intake_items": []},
        {"status": validator_lib.OWNER_RETURN_VALID},
        {"route": router_lib.ROUTE_OWNER_EVIDENCE_REQUIRED, "owner_gap_families": ["owner approval evidence"], "local_gap_families": []},
    )
    assert packet["status"] == composer_lib.FINAL_PACKET_PENDING_OWNER_RETURN
    assert "owner evidence return is required" in packet["next_safe_action"]


def test_composer_local_repair_status() -> None:
    packet = composer_lib.compose_final_owner_review_packet(
        {"status": "INTAKE_PARTIAL", "intake_items": []},
        {"status": validator_lib.OWNER_RETURN_REPAIRABLE},
        {"route": router_lib.ROUTE_LOCAL_REPAIR, "owner_gap_families": [], "local_gap_families": ["candidate evidence"]},
    )
    assert packet["status"] == composer_lib.FINAL_PACKET_PENDING_LOCAL_REPAIR


def test_ledger_event_count_is_monotonic() -> None:
    ledger = ledger_lib.build_readiness_checkpoint_ledger("packet-id", branch="test", worktree="w")
    first = ledger_lib.ledger_to_jsonable_dict(ledger)["event_count"]
    updated = ledger_lib.append_checkpoint_event(
        ledger,
        stage="test",
        status="OK",
        notes=["first"],
    )
    assert ledger_lib.ledger_to_jsonable_dict(updated)["event_count"] == first + 1


def test_orchestrator_returns_expected_sections() -> None:
    payload = orchestrator_lib.orchestrate_owner_evidence_return(repo_root=REPO_ROOT, strict=False)
    assert payload["orchestrator_version"] == "1.0"
    assert "intake_payload" in payload
    assert "validator_payload" in payload
    assert "route_payload" in payload
    assert "packet_payload" in payload
    assert "checkpoint_ledger" in payload


def test_orchestrator_jsonable_has_valid_type() -> None:
    payload = orchestrator_lib.orchestrate_owner_evidence_return(repo_root=REPO_ROOT, strict=False)
    jsonable = orchestrator_lib.orchestrate_to_jsonable_dict(payload)
    assert isinstance(jsonable, dict)
    assert jsonable["orchestrator_version"] == payload["orchestrator_version"]


def _run_script(script_name: str, report_path: Path, strict: bool = True) -> None:
    script = SCRIPTS_DIR / script_name
    cmd = [
        sys.executable,
        str(script),
        "--write-report",
        "--strict",
        "--report-path",
        str(report_path),
    ]
    subprocess.check_call(cmd)


def test_cli_intake_script_runs_with_strict(tmp_path: Path) -> None:
    output = tmp_path / "intake_report.md"
    _run_script("run_forex_owner_evidence_return_intake_v1.py", output)
    assert output.exists()
    assert "Forex Owner Evidence Return Intake V1" in output.read_text(encoding="utf-8")


def test_cli_validator_script_runs_with_strict(tmp_path: Path) -> None:
    output = tmp_path / "validator_report.md"
    _run_script("run_forex_owner_evidence_return_validator_v1.py", output)
    assert output.exists()
    assert "Forex Owner Evidence Return Validator V1" in output.read_text(encoding="utf-8")


def test_cli_router_script_runs_with_strict(tmp_path: Path) -> None:
    output = tmp_path / "router_report.md"
    _run_script("run_forex_closure_gap_router_v1.py", output)
    assert output.exists()
    assert "Forex Closure Gap Router V1" in output.read_text(encoding="utf-8")


def test_cli_composer_script_runs_with_strict(tmp_path: Path) -> None:
    output = tmp_path / "composer_report.md"
    _run_script("run_forex_final_owner_review_packet_composer_v1.py", output)
    assert output.exists()
    assert "Forex Final Owner Review Packet Composer V1" in output.read_text(encoding="utf-8")


def test_cli_orchestrator_script_runs_with_strict(tmp_path: Path) -> None:
    output = tmp_path / "orchestrator_report.md"
    checkpoint = tmp_path / "checkpoint_report.json"
    script = SCRIPTS_DIR / "run_forex_owner_evidence_return_orchestrator_v1.py"
    cmd = [
        sys.executable,
        str(script),
        "--write-report",
        "--strict",
        "--report-path",
        str(output),
        "--checkpoint-report-path",
        str(checkpoint),
    ]
    subprocess.check_call(cmd)
    assert output.exists()
    assert checkpoint.exists()
    assert "Forex Owner Evidence Return Orchestration V1" in output.read_text(encoding="utf-8")


def test_forbidden_imports_absent_in_new_python_files() -> None:
    bad_tokens = ("import requests", "import socket", "import urllib", "from urllib", "import subprocess", "from subprocess")
    for path in NEW_PYTHON_FILES:
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for token in bad_tokens:
            assert token not in lowered


def test_no_env_access_in_new_python_files() -> None:
    bad_tokens = ("os.environ", "os.getenv(", "Path.home(", ".env")
    for path in NEW_PYTHON_FILES:
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for token in bad_tokens:
            assert token not in lowered


def test_no_git_or_github_commands_in_new_python_files() -> None:
    bad_tokens = ("git add", "git commit", "git push", "gh pr create", "gh pr")
    for path in NEW_PYTHON_FILES:
        text = path.read_text(encoding="utf-8").lower()
        for token in bad_tokens:
            assert token not in text


def test_no_sensitive_assignment_literals_in_new_python_files() -> None:
    sensitive = re.compile(r"(?im)^(api_key|apikey|secret|password|token|credential)\\s*[:=]")
    for path in NEW_PYTHON_FILES:
        text = path.read_text(encoding="utf-8")
        assert not sensitive.search(text)


def test_router_markdown_is_readable() -> None:
    intake_payload = intake_lib.build_owner_evidence_return_intake(None, catalog_paths=(FIXTURE_DIR,))
    validator_payload = validator_lib.validate_owner_evidence_return_files(sorted(FIXTURE_DIR.glob("*.md"))[:3], strict=False)
    route = router_lib.route_owner_evidence_closure(intake_payload, validator_payload)
    markdown = router_lib.router_to_markdown(route)
    assert "Forex Closure Gap Router V1" in markdown


def test_intake_and_validator_integration_smoke() -> None:
    intake_payload = intake_lib.build_owner_evidence_return_intake(None, catalog_paths=(FIXTURE_DIR,))
    validator_payload = validator_lib.validate_owner_evidence_return_files(sorted(FIXTURE_DIR.glob("*.md")), strict=True)
    packet = composer_lib.compose_final_owner_review_packet(intake_payload, validator_payload, {
        "route": router_lib.ROUTE_READY_FOR_REVIEW,
        "owner_gap_families": intake_payload.get("owner_required_families", []),
        "local_gap_families": intake_payload.get("local_repair_families", []),
    }, strict=True)
    jsonable = composer_lib.packet_to_jsonable_dict(packet)
    assert jsonable["safety"]["local_only"] is True


def test_checkpoint_ledger_markdown() -> None:
    ledger = ledger_lib.build_readiness_checkpoint_ledger("TEST", branch="b", worktree="w")
    ledger = ledger_lib.append_checkpoint_event(ledger, "done", "PASS")
    markdown = ledger_lib.ledger_to_markdown(ledger)
    assert "Forex Owner Evidence Return Readiness Ledger V1" in markdown
    assert "done" in markdown


@pytest.mark.parametrize(
    "route_expected",
    [
        (router_lib.ROUTE_OWNER_EVIDENCE_REQUIRED, True),
        (router_lib.ROUTE_LOCAL_REPAIR, True),
        (router_lib.ROUTE_BLOCKED_BY_SAFETY, False),
        (router_lib.ROUTE_READY_FOR_REVIEW, False),
    ],
)
def test_router_accepts_valid_route_values(route_expected) -> None:
    route, _ = route_expected
    payload = {
        "route": route,
        "owner_gap_families": [],
        "local_gap_families": [],
        "status_blockers": ["x"],
        "next_steps": ["y"],
        "strict_mode": False,
        "router_version": "1.0",
        "generated_at": "2026-01-01T00:00:00+00:00",
    }
    jsonable = router_lib.router_to_jsonable_dict(payload)
    assert jsonable["route"] == route
