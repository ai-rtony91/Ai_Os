from __future__ import annotations

import json
from pathlib import Path

from automation.orchestration.autonomy_control_plane.aios_self_build_decision_consumer import (
    consume_self_build_decision,
    consume_self_build_evidence_file,
)


FALSE_CAPABILITIES = (
    "can_apply",
    "can_commit",
    "can_push",
    "can_merge",
    "can_dispatch",
    "can_mutate_approval_inbox",
    "can_mutate_work_packets",
)


def payload(
    *,
    safety_status: str = "SAFE",
    requires_human: bool = False,
    runtime_gate: str = "READY_TO_REPORT",
    completion_verdict: str = "COMPLETION_VERIFIED",
) -> dict[str, object]:
    return {
        "schema": "AIOS_SELF_BUILD_CYCLE.v1",
        "cycle_id": "sbc-test",
        "generated_at": "2026-06-10T00:00:00Z",
        "mode": "DRY_RUN",
        "executed": False,
        "safety_status": safety_status,
        "requires_human": requires_human,
        "decision": {"action": "PROPOSE_NEXT_GOAL", "reason": "test reason"},
        "evidence_bundle": {
            "runtime": {"runtime_gate": runtime_gate},
            "completion": {"verdict": completion_verdict},
        },
    }


def assert_invariants(readout: dict[str, object]) -> None:
    assert readout["mode"] == "DRY_RUN"
    assert readout["observe_only"] is True
    for field in FALSE_CAPABILITIES:
        assert readout[field] is False


def test_missing_evidence_file_waits_for_evidence(tmp_path: Path) -> None:
    readout = consume_self_build_evidence_file(tmp_path / "missing.json")
    assert readout["normalized_status"] == "WAIT_FOR_EVIDENCE"
    assert readout["operator_route"] == "REPORT_ONLY"
    assert readout["escalation_level"] == "LOW"
    assert readout["approval_required"] is False
    assert readout["sos_required"] is False
    assert any("missing evidence" in reason for reason in readout["reasons"])
    assert_invariants(readout)


def test_malformed_json_blocks_with_sos(tmp_path: Path) -> None:
    evidence = tmp_path / "bad.json"
    evidence.write_text("{not-json", encoding="utf-8")
    readout = consume_self_build_evidence_file(evidence)
    assert readout["normalized_status"] == "BLOCKED_MALFORMED_EVIDENCE"
    assert readout["operator_route"] == "SOS_REVIEW_REQUIRED"
    assert readout["approval_required"] is True
    assert readout["sos_required"] is True
    assert_invariants(readout)


def test_blocked_safety_status_routes_sos() -> None:
    readout = consume_self_build_decision(payload(safety_status="BLOCKED"), "memory.json")
    assert readout["normalized_status"] == "BLOCKED"
    assert readout["operator_route"] == "SOS_REVIEW_REQUIRED"
    assert readout["sos_required"] is True
    assert_invariants(readout)


def test_trust_failed_runtime_gate_routes_sos() -> None:
    readout = consume_self_build_decision(payload(runtime_gate="TRUST_FAILED"), "memory.json")
    assert readout["normalized_status"] == "TRUST_FAILED"
    assert readout["operator_route"] == "SOS_REVIEW_REQUIRED"
    assert readout["sos_required"] is True
    assert_invariants(readout)


def test_completion_contradicted_routes_trust_failed() -> None:
    readout = consume_self_build_decision(payload(completion_verdict="COMPLETION_CONTRADICTED"), "memory.json")
    assert readout["normalized_status"] == "TRUST_FAILED"
    assert readout["sos_required"] is True
    assert_invariants(readout)


def test_human_required_routes_approval_review() -> None:
    readout = consume_self_build_decision(payload(safety_status="HUMAN_REQUIRED", requires_human=True), "memory.json")
    assert readout["normalized_status"] == "HUMAN_REVIEW_REQUIRED"
    assert readout["operator_route"] == "APPROVAL_REVIEW_REQUIRED"
    assert readout["approval_required"] is True
    assert readout["sos_required"] is False
    assert_invariants(readout)


def test_safe_ready_to_report_is_report_ready() -> None:
    readout = consume_self_build_decision(payload(), "memory.json")
    assert readout["normalized_status"] == "REPORT_READY"
    assert readout["operator_route"] == "REPORT_ONLY"
    assert readout["approval_required"] is False
    assert readout["sos_required"] is False
    assert readout["report_only"] is True
    assert_invariants(readout)


def test_completion_unproven_waits_for_evidence() -> None:
    readout = consume_self_build_decision(payload(completion_verdict="COMPLETION_UNPROVEN"), "memory.json")
    assert readout["normalized_status"] == "WAIT_FOR_EVIDENCE"
    assert readout["operator_route"] == "REPORT_ONLY"
    assert any("unproven" in reason for reason in readout["reasons"])
    assert_invariants(readout)


def test_not_evaluated_waits_for_evidence() -> None:
    readout = consume_self_build_decision(payload(completion_verdict="NOT_EVALUATED"), "memory.json")
    assert readout["normalized_status"] == "WAIT_FOR_EVIDENCE"
    assert readout["operator_route"] == "REPORT_ONLY"
    assert readout["sos_required"] is False
    assert_invariants(readout)


def test_output_can_be_loaded_from_file(tmp_path: Path) -> None:
    evidence = tmp_path / "cycle.json"
    evidence.write_text(json.dumps(payload()), encoding="utf-8")
    readout = consume_self_build_evidence_file(evidence)
    assert readout["source_evidence_path"] == str(evidence)
    assert readout["source_cycle_id"] == "sbc-test"
    assert readout["source_runtime_gate"] == "READY_TO_REPORT"
    assert readout["source_completion_verdict"] == "COMPLETION_VERIFIED"
    assert_invariants(readout)
