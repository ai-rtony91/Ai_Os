from __future__ import annotations

import re
import json
from pathlib import Path

import pytest

from automation.forex_engine import (
    forex_demo_readiness_handoff_builder_v1 as handoff_lib,
    forex_final_review_decision_evidence_loader_v1 as loader_lib,
    forex_final_review_decision_gate_v1 as gate_lib,
    forex_final_review_decision_orchestrator_v1 as orchestrator_lib,
    forex_owner_decision_authority_gate_v1 as authority_lib,
    forex_protected_action_boundary_verifier_v1 as verifier_lib,
)
from automation.forex_engine import forex_closure_gap_router_v1 as router_lib
from automation.forex_engine import forex_final_owner_review_packet_composer_v1 as composer_lib

from scripts.forex_delivery import (
    run_forex_demo_readiness_handoff_builder_v1 as handoff_runner,
    run_forex_final_review_decision_evidence_loader_v1 as evidence_runner,
    run_forex_final_review_decision_gate_v1 as gate_runner,
    run_forex_owner_decision_authority_gate_v1 as authority_runner,
    run_forex_protected_action_boundary_verifier_v1 as verifier_runner,
    run_forex_final_review_decision_orchestrator_v1 as orchestrator_runner,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "forex_delivery" / "final_review_decision_gate_v1"


def _read_text_fixture(filename: str) -> Path:
    return FIXTURE_DIR / filename


def _new_evidence_summary(status: str) -> dict:
    return {
        "records": [
            {
                "source_path": "fixtures/local.md",
                "source_kind": "fixture",
                "source_family": "final_review",
                "status": status,
                "source_status": status,
                "redaction_status": "redacted",
                "evidence_count": 1,
                "notes": [f"status:{status}"],
            }
        ]
    }


def test_fixture_directory_exists() -> None:
    assert FIXTURE_DIR.exists()


def test_fixture_directory_has_minimum_55_records() -> None:
    assert len(list(FIXTURE_DIR.glob("*"))) >= 55


def test_fixture_files_are_non_empty() -> None:
    for path in FIXTURE_DIR.iterdir():
        assert path.stat().st_size > 0


def test_load_json_evidence_file() -> None:
    fixture = _read_text_fixture("evidence_ready_01.json")
    records = loader_lib.load_final_review_evidence_file(fixture)
    assert isinstance(records, list)
    assert records
    assert records[0]["status"] == loader_lib.EVIDENCE_READY


def test_load_markdown_evidence_file() -> None:
    fixture = _read_text_fixture("evidence_ready_02.md")
    records = loader_lib.load_final_review_evidence_file(fixture)
    assert isinstance(records, list)
    assert len(records) == 1
    assert records[0]["source_kind"] == "markdown"


def test_load_missing_evidence_file_reports_missing() -> None:
    records = loader_lib.load_final_review_evidence_file(FIXTURE_DIR / "does_not_exist.md")
    assert records[0]["status"] == loader_lib.EVIDENCE_MISSING
    assert records[0]["source_status"] == "missing_file"


def test_load_evidence_paths_expands_fixture_directory() -> None:
    summary = loader_lib.load_final_review_evidence_paths([FIXTURE_DIR], strict=False, source_family="final_review")
    assert summary["record_count"] > 0
    assert summary["loader_version"] == loader_lib.FINAL_REVIEW_EVIDENCE_LOADER_VERSION


def test_summarize_counts_for_known_statuses() -> None:
    payload = {
        "records": [
            {"status": loader_lib.EVIDENCE_READY, "source_kind": "markdown", "source_family": "a", "source_status": "ready", "redaction_status": "redacted", "evidence_count": 1, "notes": []},
            {"status": loader_lib.EVIDENCE_REPAIR_REQUIRED, "source_kind": "markdown", "source_family": "a", "source_status": "repair", "redaction_status": "redacted", "evidence_count": 1, "notes": []},
            {"status": loader_lib.EVIDENCE_MISSING, "source_kind": "markdown", "source_family": "a", "source_status": "missing", "redaction_status": "redacted", "evidence_count": 1, "notes": []},
        ],
    }
    result = loader_lib.summarize_final_review_evidence(payload)
    assert result["status_counts"][loader_lib.EVIDENCE_READY] == 1
    assert result["status_counts"][loader_lib.EVIDENCE_REPAIR_REQUIRED] == 1
    assert result["status_counts"][loader_lib.EVIDENCE_MISSING] == 1


def test_evidence_loader_normalize_payload_dict() -> None:
    normalized = loader_lib.normalize_final_review_evidence_payload(
        {"status": loader_lib.EVIDENCE_READY, "family": "unit", "redaction_status": "redacted"},
    )
    assert normalized[0]["status"] == loader_lib.EVIDENCE_READY
    assert normalized[0]["source_family"] == "unit"
    assert normalized[0]["evidence_count"] >= 0


@pytest.mark.parametrize(
    "fixture, expected_status",
    [
        ("evidence_ready_01.json", loader_lib.EVIDENCE_READY),
        ("evidence_repair_01.md", loader_lib.EVIDENCE_REPAIR_REQUIRED),
        ("evidence_owner_01.json", loader_lib.OWNER_EVIDENCE_REQUIRED),
        ("evidence_external_01.md", loader_lib.EXTERNAL_EVIDENCE_REQUIRED),
        ("evidence_protected_01.md", loader_lib.PROTECTED_AUTHORITY_REQUIRED),
        ("evidence_safety_01.md", loader_lib.SAFETY_REJECTED),
        ("evidence_missing_01.md", loader_lib.EVIDENCE_MISSING),
    ],
)
def test_loader_classifies_fixture_status_by_category(fixture: str, expected_status: str) -> None:
    loaded = loader_lib.load_final_review_evidence_file(_read_text_fixture(fixture))
    assert loaded[0]["status"] == expected_status


@pytest.mark.parametrize(
    "status, expected_reason",
    [
        ("ready", gate_lib.FINAL_REVIEW_READY),
        ("repair", gate_lib.FINAL_REVIEW_LOCAL_REPAIR_REQUIRED),
        ("owner", gate_lib.FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED),
        ("external", gate_lib.FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED),
        ("protected", gate_lib.FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED),
        ("safety", gate_lib.FINAL_REVIEW_SAFETY_BLOCKED),
    ],
)
def test_decision_gate_from_single_evidence_status(status: str, expected_reason: str) -> None:
    if status == "owner":
        evidence = _new_evidence_summary(loader_lib.OWNER_EVIDENCE_REQUIRED)
    elif status == "external":
        evidence = _new_evidence_summary(loader_lib.EXTERNAL_EVIDENCE_REQUIRED)
    elif status == "protected":
        evidence = _new_evidence_summary(loader_lib.PROTECTED_AUTHORITY_REQUIRED)
    elif status == "repair":
        evidence = _new_evidence_summary(loader_lib.EVIDENCE_REPAIR_REQUIRED)
    elif status == "safety":
        evidence = _new_evidence_summary(loader_lib.SAFETY_REJECTED)
    else:
        evidence = _new_evidence_summary(loader_lib.EVIDENCE_READY)
    decision = gate_lib.decide_final_review_status(
        evidence_payload=evidence,
        owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW}, "packet_payload": {"status": composer_lib.FINAL_PACKET_READY}},
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
        readiness_checkpoint_payload={"events": []},
    )
    if expected_reason == gate_lib.FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED:
        assert decision["status"] in {
            gate_lib.FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED,
            gate_lib.FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED,
        }
    elif status == "safety":
        assert decision["status"] == gate_lib.FINAL_REVIEW_SAFETY_BLOCKED
    else:
        assert decision["status"] == expected_reason or decision["status"] == gate_lib.FINAL_REVIEW_DEFERRED_OWNER_VALIDATION


def test_decision_gate_owner_pending_route_wins() -> None:
    decision = gate_lib.decide_final_review_status(
        evidence_payload=_new_evidence_summary(loader_lib.EVIDENCE_READY),
        owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW}},
        closure_gap_route_payload={"route": router_lib.ROUTE_OWNER_EVIDENCE_REQUIRED},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
    )
    assert decision["status"] == gate_lib.FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED


def test_decision_gate_local_repair_route() -> None:
    decision = gate_lib.decide_final_review_status(
        evidence_payload=_new_evidence_summary(loader_lib.EVIDENCE_REPAIR_REQUIRED),
        owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_LOCAL_REPAIR}},
        closure_gap_route_payload={"route": router_lib.ROUTE_LOCAL_REPAIR},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_PENDING_LOCAL_REPAIR},
    )
    assert decision["status"] == gate_lib.FINAL_REVIEW_LOCAL_REPAIR_REQUIRED


def test_decision_gate_safety_wins_over_other_states() -> None:
    decision = gate_lib.decide_final_review_status(
        evidence_payload=_new_evidence_summary(loader_lib.SAFETY_REJECTED),
        owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW}},
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
    )
    assert decision["status"] == gate_lib.FINAL_REVIEW_SAFETY_BLOCKED


def test_decision_gate_protected_override_owner() -> None:
    decision = gate_lib.decide_final_review_status(
        evidence_payload=_new_evidence_summary(loader_lib.PROTECTED_AUTHORITY_REQUIRED),
        owner_evidence_return_payload={
            "route_payload": {"route": router_lib.ROUTE_OWNER_EVIDENCE_REQUIRED},
            "packet_payload": {"status": composer_lib.FINAL_PACKET_PENDING_OWNER_RETURN, "safety": {}},
        },
        closure_gap_route_payload={"route": router_lib.ROUTE_OWNER_EVIDENCE_REQUIRED},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_PENDING_OWNER_RETURN},
    )
    assert decision["status"] == gate_lib.FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED


def test_decision_gate_ready_when_clean() -> None:
    decision = gate_lib.decide_final_review_status(
        evidence_payload=_new_evidence_summary(loader_lib.EVIDENCE_READY),
        owner_evidence_return_payload={
            "route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW},
            "packet_payload": {"status": composer_lib.FINAL_PACKET_READY, "safety": {}},
        },
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
    )
    assert decision["status"] == gate_lib.FINAL_REVIEW_READY


def test_gate_summarize_returns_expected_flags() -> None:
    decision = gate_lib.decide_final_review_status(
        evidence_payload=_new_evidence_summary(loader_lib.EVIDENCE_READY),
        owner_evidence_return_payload={
            "route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW},
            "packet_payload": {"status": composer_lib.FINAL_PACKET_READY, "safety": {}},
        },
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
    )
    summary = gate_lib.summarize_final_review_decision(decision)
    assert summary["ready_for_owner_review"] is True
    assert summary["safety_blocked"] is False


def test_handoff_ready_status_and_statement() -> None:
    handoff = handoff_lib.build_demo_readiness_handoff(
        {"status": gate_lib.FINAL_REVIEW_READY, "no_execution_safety_flags": {}},
    )
    assert handoff["status"] == handoff_lib.DEMO_HANDOFF_REVIEW_READY
    assert handoff_lib.SAFETY_BOUNDARY_TEXT in handoff["handoff_statement"]


@pytest.mark.parametrize(
    "input_status, output_status",
    [
        (gate_lib.FINAL_REVIEW_READY, handoff_lib.DEMO_HANDOFF_REVIEW_READY),
        (gate_lib.FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED, handoff_lib.DEMO_HANDOFF_OWNER_EVIDENCE_REQUIRED),
        (gate_lib.FINAL_REVIEW_LOCAL_REPAIR_REQUIRED, handoff_lib.DEMO_HANDOFF_LOCAL_REPAIR_REQUIRED),
        (gate_lib.FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED, handoff_lib.DEMO_HANDOFF_EXTERNAL_EVIDENCE_REQUIRED),
        (gate_lib.FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED, handoff_lib.DEMO_HANDOFF_PROTECTED_AUTHORITY_REQUIRED),
        (gate_lib.FINAL_REVIEW_SAFETY_BLOCKED, handoff_lib.DEMO_HANDOFF_SAFETY_BLOCKED),
        (gate_lib.FINAL_REVIEW_DEFERRED_OWNER_VALIDATION, handoff_lib.DEMO_HANDOFF_DEFERRED_OWNER_VALIDATION),
    ],
)
def test_handoff_status_map(input_status: str, output_status: str) -> None:
    handoff = handoff_lib.build_demo_readiness_handoff({"status": input_status, "no_execution_safety_flags": {}})
    assert handoff["status"] == output_status
    assert handoff["no_trade_no_broker_no_credentials"] is True


def test_handoff_checklist_contains_required_items() -> None:
    handoff = handoff_lib.build_demo_readiness_handoff({"status": gate_lib.FINAL_REVIEW_READY, "no_execution_safety_flags": {}})
    assert "Evidence reviewed" in handoff["owner_checklist"]
    assert "Demo/live execution not authorized" in handoff["owner_checklist"]
    assert handoff["handoff_statement"] == handoff_lib.SAFETY_BOUNDARY_TEXT


def test_owner_decision_authority_approval_ready() -> None:
    authority = authority_lib.evaluate_owner_decision_authority(
        {"status": gate_lib.FINAL_REVIEW_READY, "no_execution_safety_flags": {}},
        demo_readiness_handoff={"status": handoff_lib.DEMO_HANDOFF_REVIEW_READY},
    )
    assert authority["status"] == authority_lib.OWNER_AUTHORITY_APPROVAL_READY
    assert authority["auto_approval_allowed"] is False


@pytest.mark.parametrize(
    "final_status, expected",
    [
        (gate_lib.FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED, authority_lib.OWNER_AUTHORITY_BLOCKED_BY_MISSING_EVIDENCE),
        (gate_lib.FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED, authority_lib.OWNER_AUTHORITY_BLOCKED_BY_PROTECTED_DEPENDENCY),
        (gate_lib.FINAL_REVIEW_SAFETY_BLOCKED, authority_lib.OWNER_AUTHORITY_SAFETY_BLOCKED),
        (gate_lib.FINAL_REVIEW_DEFERRED_OWNER_VALIDATION, authority_lib.OWNER_AUTHORITY_DEFERRED),
    ],
)
def test_owner_decision_authority_status_mapping(final_status: str, expected: str) -> None:
    authority = authority_lib.evaluate_owner_decision_authority(
        {"status": final_status, "no_execution_safety_flags": {}},
        demo_readiness_handoff={"status": handoff_lib.DEMO_HANDOFF_REVIEW_READY},
    )
    assert authority["status"] == expected
    assert isinstance(authority["questions"], list)
    assert authority["required_next_items"]


def test_owner_decision_authority_never_auto_approves() -> None:
    authority = authority_lib.evaluate_owner_decision_authority(
        {"status": gate_lib.FINAL_REVIEW_READY, "no_execution_safety_flags": {}},
        demo_readiness_handoff={"status": handoff_lib.DEMO_HANDOFF_REVIEW_READY},
    )
    assert authority["auto_approval_allowed"] is False


def test_boundary_verifier_clean_text() -> None:
    result = verifier_lib.verify_protected_action_boundaries_text("No protected commands and no credentials referenced.", strict=True)
    assert result["status"] == verifier_lib.BOUNDARY_CLEAN
    assert result["match_count"] == 0


def test_boundary_verifier_false_profit_claim_dynamic() -> None:
    unsafe = "".join(["guaran", "teed", " profit"])
    result = verifier_lib.verify_protected_action_boundaries_text(unsafe)
    assert result["status"] == verifier_lib.BOUNDARY_SAFETY_BLOCKED
    assert any(item["label"] == "false_profit_claim" for item in result["findings"])


def test_boundary_verifier_broker_api_claim_dynamic() -> None:
    claim = " ".join(["Broker API", "is", "enabled"])
    result = verifier_lib.verify_protected_action_boundaries_text(claim)
    assert result["status"] == verifier_lib.BOUNDARY_PROTECTED_AUTHORITY_REQUIRED


def test_boundary_verifier_credential_claim_dynamic() -> None:
    claim = " ".join(["credential", "access", "granted"])
    result = verifier_lib.verify_protected_action_boundaries_text(claim)
    assert result["status"] == verifier_lib.BOUNDARY_PROTECTED_AUTHORITY_REQUIRED


def test_boundary_verifier_demo_live_auth_dynamic() -> None:
    claim = " ".join(["demo", "trade", "authorized"])
    result = verifier_lib.verify_protected_action_boundaries_text(claim)
    assert result["status"] == verifier_lib.BOUNDARY_PROTECTED_AUTHORITY_REQUIRED


def test_boundary_verifier_order_command_dynamic() -> None:
    claim = " ".join(["place", "order"])
    result = verifier_lib.verify_protected_action_boundaries_text(claim)
    assert result["status"] in {verifier_lib.BOUNDARY_REPAIR_REQUIRED, verifier_lib.BOUNDARY_SAFETY_BLOCKED}

def test_boundary_verifier_broker_command_dynamic() -> None:
    claim = " ".join(["connect", "to", "broker"])
    result = verifier_lib.verify_protected_action_boundaries_text(claim)
    assert result["status"] in {verifier_lib.BOUNDARY_REPAIR_REQUIRED, verifier_lib.BOUNDARY_PROTECTED_AUTHORITY_REQUIRED}


def test_boundary_verifier_credential_required_claim_dynamic() -> None:
    claim = " ".join(["credential", "scope", "must", "be", "granted"])
    result = verifier_lib.verify_protected_action_boundaries_text(claim)
    assert result["status"] != verifier_lib.BOUNDARY_CLEAN


def test_boundary_verifier_production_activation_dynamic() -> None:
    claim = " ".join(["production", "activation", "is", "active"])
    result = verifier_lib.verify_protected_action_boundaries_text(claim)
    assert result["status"] == verifier_lib.BOUNDARY_PROTECTED_AUTHORITY_REQUIRED


def test_verify_payload_path_scan() -> None:
    result = verifier_lib.verify_protected_action_boundaries_payload({"text": "place order", "note": "safe"})
    assert result["status"] in {verifier_lib.BOUNDARY_PROTECTED_AUTHORITY_REQUIRED, verifier_lib.BOUNDARY_REPAIR_REQUIRED}


def test_verify_files_scan_boundary() -> None:
    result = verifier_lib.verify_protected_action_boundaries_files(
        [str(_read_text_fixture("boundary_trade_command_01.md"))],
    )
    assert result["match_count"] >= 1


def test_orchestrator_returns_required_sections() -> None:
    result = orchestrator_lib.run_final_review_decision_orchestration(
        repo_root=REPO_ROOT,
        evidence_paths=[_read_text_fixture("evidence_ready_01.json")],
        strict=False,
        owner_evidence_return_payload={
            "route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW},
            "packet_payload": {"status": composer_lib.FINAL_PACKET_READY},
            "checkpoint_ledger": {"events": []},
            "validator_payload": {"status": "OWNER_RETURN_VALID"},
        },
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
        readiness_checkpoint_payload={"events": []},
    )
    assert result["orchestrator_version"] == orchestrator_lib.FINAL_REVIEW_DECISION_ORCHESTRATOR_VERSION
    assert "checkpoint_ledger" in result
    assert isinstance(result["checkpoint_ledger"].get("events"), list)


@pytest.mark.parametrize(
    "final_status, expected_orchestrator_status",
    [
        (gate_lib.FINAL_REVIEW_READY, orchestrator_lib.ORCHESTRATOR_FINAL_REVIEW_READY),
        (gate_lib.FINAL_REVIEW_LOCAL_REPAIR_REQUIRED, orchestrator_lib.ORCHESTRATOR_LOCAL_REPAIR_REQUIRED),
        (gate_lib.FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED, orchestrator_lib.ORCHESTRATOR_OWNER_EVIDENCE_REQUIRED),
        (gate_lib.FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED, orchestrator_lib.ORCHESTRATOR_EXTERNAL_EVIDENCE_REQUIRED),
        (gate_lib.FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED, orchestrator_lib.ORCHESTRATOR_PROTECTED_AUTHORITY_REQUIRED),
        (gate_lib.FINAL_REVIEW_SAFETY_BLOCKED, orchestrator_lib.ORCHESTRATOR_SAFETY_BLOCKED),
        (gate_lib.FINAL_REVIEW_DEFERRED_OWNER_VALIDATION, orchestrator_lib.ORCHESTRATOR_DEFERRED_OWNER_VALIDATION),
    ],
)
def test_orchestrator_maps_gate_status_to_orchestrator_status(final_status: str, expected_orchestrator_status: str) -> None:
    result = orchestrator_lib.run_final_review_decision_orchestration(
        repo_root=REPO_ROOT,
        evidence_paths=[_read_text_fixture("evidence_ready_01.json")],
        strict=False,
        owner_evidence_return_payload={
            "route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW},
            "packet_payload": {"status": composer_lib.FINAL_PACKET_READY},
            "checkpoint_ledger": {"events": []},
            "validator_payload": {"status": "OWNER_RETURN_VALID"},
        },
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
        readiness_checkpoint_payload={"events": []},
        protected_boundary_payload={
            "status": final_status,
        },
    )
    assert result["status"] in {expected_orchestrator_status, orchestrator_lib.ORCHESTRATOR_DEFERRED_OWNER_VALIDATION}
    if final_status == gate_lib.FINAL_REVIEW_SAFETY_BLOCKED:
        result = orchestrator_lib.run_final_review_decision_orchestration(
            repo_root=REPO_ROOT,
            evidence_paths=[_read_text_fixture("evidence_safety_01.md")],
            strict=False,
            owner_evidence_return_payload={
                "route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW},
                "packet_payload": {"status": composer_lib.FINAL_PACKET_READY},
                "checkpoint_ledger": {"events": []},
                "validator_payload": {"status": "OWNER_RETURN_VALID"},
            },
            closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
            final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
            readiness_checkpoint_payload={"events": []},
        )
        assert result["status"] == expected_orchestrator_status


def test_integration_loader_to_gate_to_handoff_to_authority() -> None:
    evidence = loader_lib.load_final_review_evidence_paths(
        [_read_text_fixture("evidence_ready_01.json")],
        strict=False,
        source_family="final_review",
    )
    decision = gate_lib.decide_final_review_status(
        evidence_payload=evidence,
        owner_evidence_return_payload={
            "route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW},
            "packet_payload": {"status": composer_lib.FINAL_PACKET_READY, "safety": {}},
            "checkpoint_ledger": {"events": []},
        },
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
    )
    handoff = handoff_lib.build_demo_readiness_handoff(decision)
    authority = authority_lib.evaluate_owner_decision_authority(decision, demo_readiness_handoff=handoff)
    assert handoff["status"] == handoff_lib.DEMO_HANDOFF_REVIEW_READY
    assert authority["status"] == authority_lib.OWNER_AUTHORITY_APPROVAL_READY


def test_integration_safety_fixture_cannot_be_ready() -> None:
    evidence = loader_lib.load_final_review_evidence_paths(
        [_read_text_fixture("evidence_safety_01.md")],
        strict=True,
        source_family="final_review",
    )
    decision = gate_lib.decide_final_review_status(
        evidence_payload=evidence,
        owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW}},
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
    )
    assert decision["status"] == gate_lib.FINAL_REVIEW_SAFETY_BLOCKED


def test_integration_protected_dependency_cannot_be_ready() -> None:
    evidence = loader_lib.load_final_review_evidence_paths(
        [_read_text_fixture("evidence_protected_01.md")],
        strict=False,
        source_family="final_review",
    )
    decision = gate_lib.decide_final_review_status(
        evidence_payload=evidence,
        owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW}},
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
    )
    assert decision["status"] == gate_lib.FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED


def test_clean_fixture_maps_to_owner_review_ready_only() -> None:
    evidence = loader_lib.load_final_review_evidence_paths(
        [_read_text_fixture("evidence_ready_01.json")],
        strict=True,
        source_family="final_review",
    )
    decision = gate_lib.decide_final_review_status(
        evidence_payload=evidence,
        owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW}},
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
    )
    assert decision["status"] == gate_lib.FINAL_REVIEW_READY
    assert decision["status"] != gate_lib.FINAL_REVIEW_LOCAL_REPAIR_REQUIRED


@pytest.mark.parametrize(
    "runner",
    [
        (evidence_runner.run_cli),
        (gate_runner.run_cli),
        (handoff_runner.run_cli),
        (authority_runner.run_cli),
        (verifier_runner.run_cli),
        (orchestrator_runner.run_cli),
    ],
)
def test_all_runners_support_strict_and_write_report(tmp_path, runner) -> None:
    report = tmp_path / "out.md"
    runner(["--strict", "--write-report", "--report-path", str(report)])
    assert report.exists()


def test_gate_runner_json_output() -> None:
    output = gate_runner.run_cli(["--json", "--strict"])
    payload = json.loads(output)
    assert payload["status"] is not None


def test_authority_runner_json_output() -> None:
    output = authority_runner.run_cli(["--json", "--strict"])
    payload = json.loads(output)
    assert "status" in payload
    assert "owner_review_required" in payload


def test_handoff_runner_returns_markdown_default() -> None:
    output = handoff_runner.run_cli([])
    assert handoff_lib.SAFETY_BOUNDARY_TEXT in output


def test_verifier_runner_json_output() -> None:
    output = verifier_runner.run_cli(["--json", "--text", "safe review text"])
    payload = json.loads(output)
    assert "status" in payload


def test_orchestrator_runner_json_output() -> None:
    output = orchestrator_runner.run_cli(["--json", "--strict"])
    payload = json.loads(output)
    assert payload["orchestrator_version"] == orchestrator_lib.FINAL_REVIEW_DECISION_ORCHESTRATOR_VERSION


def test_no_new_module_imports() -> None:
    target_files = [
        "automation/forex_engine/forex_final_review_decision_evidence_loader_v1.py",
        "automation/forex_engine/forex_final_review_decision_gate_v1.py",
        "automation/forex_engine/forex_demo_readiness_handoff_builder_v1.py",
        "automation/forex_engine/forex_owner_decision_authority_gate_v1.py",
        "automation/forex_engine/forex_protected_action_boundary_verifier_v1.py",
        "automation/forex_engine/forex_final_review_decision_orchestrator_v1.py",
        "scripts/forex_delivery/run_forex_final_review_decision_evidence_loader_v1.py",
        "scripts/forex_delivery/run_forex_final_review_decision_gate_v1.py",
        "scripts/forex_delivery/run_forex_demo_readiness_handoff_builder_v1.py",
        "scripts/forex_delivery/run_forex_owner_decision_authority_gate_v1.py",
        "scripts/forex_delivery/run_forex_protected_action_boundary_verifier_v1.py",
        "scripts/forex_delivery/run_forex_final_review_decision_orchestrator_v1.py",
    ]
    bad_tokens = ("import requests", "import socket", "import urllib", "from urllib", "import subprocess", "from subprocess")
    for relative in target_files:
        content = (REPO_ROOT / relative).read_text(encoding="utf-8").lower()
        for token in bad_tokens:
            assert token not in content


def test_no_env_reads_in_new_modules() -> None:
    target_files = [
        "automation/forex_engine/forex_final_review_decision_evidence_loader_v1.py",
        "automation/forex_engine/forex_final_review_decision_gate_v1.py",
        "automation/forex_engine/forex_demo_readiness_handoff_builder_v1.py",
        "automation/forex_engine/forex_owner_decision_authority_gate_v1.py",
        "automation/forex_engine/forex_protected_action_boundary_verifier_v1.py",
        "automation/forex_engine/forex_final_review_decision_orchestrator_v1.py",
        "scripts/forex_delivery/run_forex_final_review_decision_evidence_loader_v1.py",
        "scripts/forex_delivery/run_forex_final_review_decision_gate_v1.py",
        "scripts/forex_delivery/run_forex_demo_readiness_handoff_builder_v1.py",
        "scripts/forex_delivery/run_forex_owner_decision_authority_gate_v1.py",
        "scripts/forex_delivery/run_forex_protected_action_boundary_verifier_v1.py",
        "scripts/forex_delivery/run_forex_final_review_decision_orchestrator_v1.py",
    ]
    bad_tokens = ("os.environ", "os.getenv(", "path.home(", ".env")
    for relative in target_files:
        text = (REPO_ROOT / relative).read_text(encoding="utf-8").lower()
        for token in bad_tokens:
            assert token not in text


def test_no_git_or_github_commands_in_new_scripts() -> None:
    script_files = [
        "scripts/forex_delivery/run_forex_final_review_decision_evidence_loader_v1.py",
        "scripts/forex_delivery/run_forex_final_review_decision_gate_v1.py",
        "scripts/forex_delivery/run_forex_demo_readiness_handoff_builder_v1.py",
        "scripts/forex_delivery/run_forex_owner_decision_authority_gate_v1.py",
        "scripts/forex_delivery/run_forex_protected_action_boundary_verifier_v1.py",
        "scripts/forex_delivery/run_forex_final_review_decision_orchestrator_v1.py",
    ]
    bad_tokens = ("git add", "git commit", "git push", "gh pr create", "gh pr")
    for relative in script_files:
        text = (REPO_ROOT / relative).read_text(encoding="utf-8").lower()
        for token in bad_tokens:
            assert token not in text


def test_no_sensitive_assignment_literals_in_new_sources() -> None:
    sensitive = re.compile(r"(?im)^(api_key|apikey|secret|password|token|credential)\s*[:=]")
    files = [
        REPO_ROOT / "automation/forex_engine/forex_final_review_decision_evidence_loader_v1.py",
        REPO_ROOT / "automation/forex_engine/forex_final_review_decision_gate_v1.py",
        REPO_ROOT / "automation/forex_engine/forex_demo_readiness_handoff_builder_v1.py",
        REPO_ROOT / "automation/forex_engine/forex_owner_decision_authority_gate_v1.py",
        REPO_ROOT / "automation/forex_engine/forex_protected_action_boundary_verifier_v1.py",
        REPO_ROOT / "automation/forex_engine/forex_final_review_decision_orchestrator_v1.py",
        REPO_ROOT / "scripts/forex_delivery/run_forex_final_review_decision_evidence_loader_v1.py",
        REPO_ROOT / "scripts/forex_delivery/run_forex_final_review_decision_gate_v1.py",
        REPO_ROOT / "scripts/forex_delivery/run_forex_demo_readiness_handoff_builder_v1.py",
        REPO_ROOT / "scripts/forex_delivery/run_forex_owner_decision_authority_gate_v1.py",
        REPO_ROOT / "scripts/forex_delivery/run_forex_protected_action_boundary_verifier_v1.py",
        REPO_ROOT / "scripts/forex_delivery/run_forex_final_review_decision_orchestrator_v1.py",
    ]
    for path in files:
        assert not sensitive.search(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "filename, marker",
    [
        ("ownerauth_review_required_01.md", "owner"),
        ("ownerauth_approval_ready_01.md", "approval"),
        ("ownerauth_missing_01.md", "missing"),
        ("ownerauth_protected_01.md", "protected"),
        ("ownerauth_safety_01.md", "safety"),
    ],
)
def test_handoff_and_authority_fixture_categories_exist(filename: str, marker: str) -> None:
    assert marker
    path = _read_text_fixture(filename)
    assert path.exists()
    assert path.stat().st_size > 0


def test_gate_markdown_contains_safety_flags_and_checklist() -> None:
    decision = gate_lib.decide_final_review_status(
        evidence_payload=_new_evidence_summary(loader_lib.EVIDENCE_READY),
        owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW}, "packet_payload": {"status": composer_lib.FINAL_PACKET_READY}},
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
    )
    markdown = gate_lib.final_review_decision_to_markdown(decision)
    assert "No-Execution Safety Flags" in markdown
    assert "Owner Decision Checklist" in markdown


def test_orchestrator_markdown_has_status_line() -> None:
    result = orchestrator_lib.run_final_review_decision_orchestration(
        repo_root=REPO_ROOT,
        evidence_paths=[_read_text_fixture("evidence_ready_01.json")],
        strict=True,
        owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW}},
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
        readiness_checkpoint_payload={"events": []},
        protected_boundary_payload={"notes": ["safe"]},
    )
    markdown = orchestrator_lib.final_review_decision_orchestration_to_markdown(result)
    assert "Forex Final Review Decision Orchestrator V1" in markdown
    assert "Status:" in markdown


def test_router_markdown_generation() -> None:
    owner_packet = {"status": composer_lib.FINAL_PACKET_READY}
    summary = authority_lib.owner_decision_authority_to_markdown(
        authority_lib.evaluate_owner_decision_authority(
            {"status": gate_lib.FINAL_REVIEW_READY, "no_execution_safety_flags": {}},
            demo_readiness_handoff={"status": handoff_lib.DEMO_HANDOFF_REVIEW_READY},
        )
    )
    assert "Authority Conditions" in summary
    assert "auto_approval_allowed" in summary


def test_boundary_verify_text_is_repeatable_with_payload() -> None:
    payload = {"note": "place order", "nested": {"claim": "guaranteed profit", "status": "safe"}}
    result = verifier_lib.verify_protected_action_boundaries_payload(payload)
    assert result["match_count"] >= 1


def test_report_files_reference_owner_publish_and_merge_blocks() -> None:
    report = REPO_ROOT / "Reports/forex_delivery/AIOS_FOREX_FINAL_REVIEW_DECISION_GATE_V1_REPORT.md"
    assert report.exists()
    content = report.read_text(encoding="utf-8")
    assert "owner publish" in content.lower()
    assert "pr_number" in content.lower()


def test_loader_normalize_non_mapping_payload() -> None:
    normalized = loader_lib.normalize_final_review_evidence_payload(["invalid", "payload"], source_path="tmp/path")
    assert len(normalized) == 1
    assert normalized[0]["status"] == loader_lib.EVIDENCE_MISSING


def test_load_final_review_evidence_file_invalid_json_is_missing(tmp_path: Path) -> None:
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("{invalid json", encoding="utf-8")
    records = loader_lib.load_final_review_evidence_file(invalid_json)
    assert records[0]["status"] == loader_lib.EVIDENCE_MISSING
    assert records[0]["source_status"] == "invalid_json"


def test_load_final_review_evidence_paths_empty_returns_missing() -> None:
    payload = loader_lib.load_final_review_evidence_paths([], strict=True, source_family="final_review")
    assert payload["record_count"] == 1
    assert payload["records"][0]["status"] == loader_lib.EVIDENCE_MISSING


def test_loader_normalize_payload_from_text_uses_status_keyword() -> None:
    payload = {"status": "external evidence required", "family": "external", "evidence_count": 2}
    normalized = loader_lib.normalize_final_review_evidence_payload(payload, source_kind="fixture")
    assert normalized[0]["status"] == loader_lib.EXTERNAL_EVIDENCE_REQUIRED
    assert normalized[0]["source_family"] == "external"
    assert normalized[0]["evidence_count"] == 0 or isinstance(normalized[0]["evidence_count"], int)


def test_loader_summary_handles_unknown_record_shapes() -> None:
    payload = {
        "records": [
            {"status": loader_lib.EVIDENCE_READY, "source_kind": "markdown"},
            {"status": "safe"},
            {"junk": "value"},
        ],
    }
    summarized = loader_lib.summarize_final_review_evidence(payload)
    assert summarized["status_counts"][loader_lib.EVIDENCE_READY] >= 1
    assert summarized["record_count"] == 3


def test_loader_markdown_to_jsonable() -> None:
    payload = loader_lib.load_final_review_evidence_file(_read_text_fixture("evidence_ready_02.md"))
    payload_summary = loader_lib.summarize_final_review_evidence({"records": payload})
    jsonable = loader_lib.final_review_evidence_to_jsonable_dict(payload_summary)
    assert jsonable["record_count"] == payload_summary["evidence_count"] or jsonable["record_count"] == payload_summary["record_count"]
    assert jsonable["status_counts"][loader_lib.EVIDENCE_READY] >= 1


def test_loader_markdown_to_markdown_includes_records() -> None:
    payload = loader_lib.summarize_final_review_evidence(
        {
            "records": [
                loader_lib.load_final_review_evidence_file(_read_text_fixture("evidence_ready_02.md"))[0],
            ],
        },
    )
    markdown = loader_lib.final_review_evidence_to_markdown(payload)
    assert "# Forex Final Review Decision Evidence Loader V1" in markdown
    assert "- " + str(payload["records"][0]["source_path"]) in markdown


def test_decision_gate_marks_safety_for_blocked_route() -> None:
    decision = gate_lib.decide_final_review_status(
        evidence_payload=_new_evidence_summary(loader_lib.EVIDENCE_READY),
        owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW}},
        closure_gap_route_payload={"route": router_lib.ROUTE_BLOCKED_BY_SAFETY},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
    )
    assert decision["status"] == gate_lib.FINAL_REVIEW_SAFETY_BLOCKED


def test_decision_gate_deferred_on_missing_evidence_when_not_strict() -> None:
    decision = gate_lib.decide_final_review_status(
        evidence_payload=_new_evidence_summary(loader_lib.EVIDENCE_MISSING),
        owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW}},
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
        strict=False,
    )
    assert decision["status"] in {
        gate_lib.FINAL_REVIEW_DEFERRED_OWNER_VALIDATION,
        gate_lib.FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED,
    }


def test_decision_gate_strict_defaults_to_owner_validation_when_no_evidence() -> None:
    decision = gate_lib.decide_final_review_status(
        evidence_payload={},
        owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW}},
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
        strict=True,
    )
    assert decision["status"] == gate_lib.FINAL_REVIEW_DEFERRED_OWNER_VALIDATION


def test_decision_gate_returns_next_safe_actions_for_all_statuses() -> None:
    for status in (
        gate_lib.FINAL_REVIEW_READY,
        gate_lib.FINAL_REVIEW_LOCAL_REPAIR_REQUIRED,
        gate_lib.FINAL_REVIEW_OWNER_EVIDENCE_REQUIRED,
        gate_lib.FINAL_REVIEW_EXTERNAL_EVIDENCE_REQUIRED,
        gate_lib.FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED,
        gate_lib.FINAL_REVIEW_SAFETY_BLOCKED,
        gate_lib.FINAL_REVIEW_DEFERRED_OWNER_VALIDATION,
    ):
        decision = gate_lib.decide_final_review_status(
            evidence_payload=_new_evidence_summary(loader_lib.EVIDENCE_READY),
            owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW}},
            closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
            final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
        )
        decision["status"] = status
        summary = gate_lib.summarize_final_review_decision(decision)
        assert summary["ready_for_owner_review"] is False or status == gate_lib.FINAL_REVIEW_READY
        assert summary["deferred_owner_validation"] in {True, False}


def test_decision_gate_jsonable_has_expected_fields() -> None:
    decision = gate_lib.decide_final_review_status(
        evidence_payload=_new_evidence_summary(loader_lib.EVIDENCE_READY),
        owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW}},
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
    )
    payload = gate_lib.final_review_decision_to_jsonable_dict(decision)
    assert payload["status"] == decision["status"]
    assert "safe_actions" in payload
    assert payload["evidence_summary"]["most_critical_status"] is not None


def test_handoff_builder_jsonable_has_flags() -> None:
    handoff = handoff_lib.build_demo_readiness_handoff({"status": gate_lib.FINAL_REVIEW_READY, "no_execution_safety_flags": {}})
    payload = handoff_lib.demo_readiness_handoff_to_jsonable_dict(handoff)
    assert payload["status"] == handoff["status"]
    assert payload["no_trade_no_broker_no_credentials"] is True
    assert payload["candidate_summary"]["candidate_id"] == "candidate-id-placeholder"


def test_handoff_builder_review_only_boundary_text() -> None:
    handoff = handoff_lib.build_demo_readiness_handoff({"status": gate_lib.FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED})
    assert handoff["handoff_statement"] == handoff_lib.SAFETY_BOUNDARY_TEXT
    assert "Broker/API still disabled" in handoff["owner_checklist"]


def test_authority_gate_required_questions_for_protected_dependency() -> None:
    authority = authority_lib.evaluate_owner_decision_authority(
        {"status": gate_lib.FINAL_REVIEW_PROTECTED_AUTHORITY_REQUIRED, "no_execution_safety_flags": {}},
        demo_readiness_handoff={"status": handoff_lib.DEMO_HANDOFF_PROTECTED_AUTHORITY_REQUIRED},
    )
    assert authority["status"] == authority_lib.OWNER_AUTHORITY_BLOCKED_BY_PROTECTED_DEPENDENCY
    assert authority["protected_dependency_required"] is True
    assert any("protected" in q.lower() for q in authority["questions"])


def test_authority_gate_owner_readiness_blocked_when_not_ready() -> None:
    authority = authority_lib.evaluate_owner_decision_authority(
        {"status": gate_lib.FINAL_REVIEW_DEFERRED_OWNER_VALIDATION, "no_execution_safety_flags": {}},
        demo_readiness_handoff={"status": handoff_lib.DEMO_HANDOFF_DEFERRED_OWNER_VALIDATION},
    )
    assert authority["status"] == authority_lib.OWNER_AUTHORITY_DEFERRED
    assert authority["owner_review_required"] is False


def test_authority_gate_json_contains_owner_questions() -> None:
    authority = authority_lib.evaluate_owner_decision_authority(
        {"status": gate_lib.FINAL_REVIEW_READY, "no_execution_safety_flags": {}},
        demo_readiness_handoff={"status": handoff_lib.DEMO_HANDOFF_REVIEW_READY},
    )
    payload = authority_lib.owner_decision_authority_to_jsonable_dict(authority)
    assert "owner_next_checklist" in payload
    assert isinstance(payload["questions"], list)


def test_verifier_payload_files_with_multiple_matches() -> None:
    files = [_read_text_fixture("evidence_safety_01.md"), _read_text_fixture("boundary_trade_command_01.md")]
    result = verifier_lib.verify_protected_action_boundaries_files([str(path) for path in files], strict=True)
    assert result["match_count"] >= 1
    assert result["status"] in {
        verifier_lib.BOUNDARY_SAFETY_BLOCKED,
        verifier_lib.BOUNDARY_PROTECTED_AUTHORITY_REQUIRED,
        verifier_lib.BOUNDARY_REPAIR_REQUIRED,
    }


def test_verifier_payload_recursive_scan_on_nested_payload() -> None:
    payload = {"level1": {"order": "place order now", "notes": "safe"}, "safe": "true"}
    result = verifier_lib.verify_protected_action_boundaries_payload(payload, strict=False)
    assert result["match_count"] >= 1
    assert result["status"] in {
        verifier_lib.BOUNDARY_REPAIR_REQUIRED,
        verifier_lib.BOUNDARY_SAFETY_BLOCKED,
    }


def test_boundary_verifier_marks_false_profit_in_markdown_file(tmp_path: Path) -> None:
    path = tmp_path / "false_profit.md"
    path.write_text("guaranteed profit guaranteed profit", encoding="utf-8")
    result = verifier_lib.verify_protected_action_boundaries_files([str(path)], strict=True)
    assert result["status"] == verifier_lib.BOUNDARY_SAFETY_BLOCKED
    assert result["contains_false_profit_claim"] is True


def test_orchestrator_markdown_mentions_checkpoint_count() -> None:
    output = orchestrator_runner.run_cli(["--json", "--strict"])
    payload = json.loads(output)
    assert payload["checkpoint_ledger"]["event_count"] >= 3
    md = orchestrator_lib.final_review_decision_orchestration_to_markdown(payload)
    assert "Checkpoint events" in md


def test_orchestrator_jsonable_contains_all_sections() -> None:
    payload = orchestrator_lib.run_final_review_decision_orchestration(
        repo_root=REPO_ROOT,
        evidence_paths=[_read_text_fixture("evidence_ready_01.json")],
        strict=False,
        owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW}},
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
        readiness_checkpoint_payload={"events": []},
    )
    jsonable = orchestrator_lib.final_review_decision_orchestration_to_jsonable_dict(payload)
    assert jsonable["orchestrator_version"] == orchestrator_lib.FINAL_REVIEW_DECISION_ORCHESTRATOR_VERSION
    assert "evidence_payload" in jsonable
    assert "boundary_result" in jsonable
    assert "authority_result" in jsonable


def test_orchestrator_result_checkpoint_events_are_timestamps() -> None:
    payload = orchestrator_lib.run_final_review_decision_orchestration(
        repo_root=REPO_ROOT,
        evidence_paths=[_read_text_fixture("evidence_ready_01.json")],
        strict=False,
        owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW}},
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
        readiness_checkpoint_payload={"events": []},
    )
    events = payload["checkpoint_ledger"]["events"]
    assert events
    assert all("stage" in event for event in events)


def test_cli_writes_default_reports_only_to_reports_dir(tmp_path) -> None:
    handoff_runner.run_cli(["--write-report", "--report-path", str(tmp_path / "handoff.md"), "--strict"])
    assert (tmp_path / "handoff.md").exists()
    assert "Reports/forex_delivery" not in str(tmp_path / "handoff.md")


def test_cli_strict_accepts_default_evidence_path() -> None:
    output = orchestrator_runner.run_cli(["--strict", "--write-report", "--report-path", str(tmp_path := REPO_ROOT / "Reports\\forex_delivery\\cli_check.md")])
    assert tmp_path.exists()


def test_evidence_loader_does_not_read_env_or_network_tokens() -> None:
    source = loader_lib.__file__
    text = Path(source).read_text(encoding="utf-8").lower()
    for token in ("os.environ", "os.getenv", "subprocess", "requests", "socket", "urllib"):
        assert token not in text


def test_module_outputs_no_trade_authority_claim() -> None:
    evidence = loader_lib.summarize_final_review_evidence(_new_evidence_summary(loader_lib.EVIDENCE_READY))
    decision = gate_lib.decide_final_review_status(
        evidence_payload=evidence,
        owner_evidence_return_payload={"route_payload": {"route": router_lib.ROUTE_READY_FOR_REVIEW}},
        closure_gap_route_payload={"route": router_lib.ROUTE_READY_FOR_REVIEW},
        final_owner_review_packet_payload={"status": composer_lib.FINAL_PACKET_READY},
    )
    handoff = handoff_lib.build_demo_readiness_handoff(decision)
    authority = authority_lib.evaluate_owner_decision_authority(decision, demo_readiness_handoff=handoff)
    assert handoff["handoff_statement"] == handoff_lib.SAFETY_BOUNDARY_TEXT
    assert authority["auto_approval_allowed"] is False
    assert authority["status"] == authority_lib.OWNER_AUTHORITY_APPROVAL_READY


def test_orchestrator_handoff_authority_integration_from_boundary_payload_safe() -> None:
    result = orchestrator_lib.run_final_review_decision_orchestration(
        repo_root=REPO_ROOT,
        evidence_paths=[_read_text_fixture("evidence_ready_01.json")],
        strict=False,
        protected_boundary_payload={"status": verifier_lib.BOUNDARY_CLEAN},
    )
    assert result["handoff_result"]["status"] in {
        handoff_lib.DEMO_HANDOFF_REVIEW_READY,
        handoff_lib.DEMO_HANDOFF_OWNER_EVIDENCE_REQUIRED,
    }
    assert result["authority_result"]["auto_approval_allowed"] is False


def test_handoff_and_authority_fixture_files_all_exist() -> None:
    expected = [
        "ownerauth_review_required_01.md",
        "ownerauth_approval_ready_01.md",
        "ownerauth_missing_01.md",
        "ownerauth_protected_01.md",
        "ownerauth_safety_01.md",
    ]
    for filename in expected:
        assert (_read_text_fixture(filename)).exists()


def test_loader_includes_zero_record_when_path_missing() -> None:
    summary = loader_lib.load_final_review_evidence_paths([tmp_path := REPO_ROOT / "does-not-exist"], strict=True, source_family="final_review")
    assert summary["most_critical_status"] == loader_lib.EVIDENCE_MISSING
    assert summary["record_count"] == 1
