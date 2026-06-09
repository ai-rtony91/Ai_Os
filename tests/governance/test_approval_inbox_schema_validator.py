from __future__ import annotations

import json
from pathlib import Path

from automation.validators.aios_approval_inbox_schema_validator import (
    DEFAULT_GATE_PATH,
    DEFAULT_INBOX_PATH,
    run_validator,
    validate_apply_gate_record,
    validate_approval_inbox_record,
    validate_file,
)


def test_valid_sample_approval_inbox_passes() -> None:
    payload = {
        "schema": "AIOS_APPROVAL_INBOX.v1",
        "approval_gate_id": "APPROVAL_INBOX_001",
        "authority_status": "active_authority",
        "packet_id": "SAMPLE-INBOX-001",
        "requested_action": "SAMPLE_APPROVAL",
        "requested_mode": "DRY_RUN",
        "approval_status": "completed",
        "approved_by_human": True,
        "risk_level": "low",
        "allowed_paths": [str(DEFAULT_INBOX_PATH)],
        "blocked_paths": ["services/"],
        "validator_chain_required": True,
        "commit_package_required": True,
        "push_blocked_until_final_review": True,
        "pending_approvals": [
            {
                "approval_id": "sample-001",
                "packet_id": "P-001",
                "requested_action": "DRY_RUN",
                "approval_status": "pending_review",
                "risk_level": "low",
            }
        ],
    }
    assert not validate_approval_inbox_record(payload)


def test_missing_required_field_returns_review_required() -> None:
    payload = {
        "schema": "AIOS_APPROVAL_INBOX.v1",
        "approval_gate_id": "APPROVAL_INBOX_001",
        "packet_id": "SAMPLE-INBOX-001",
        "requested_action": "SAMPLE_APPROVAL",
        "requested_mode": "DRY_RUN",
        "approval_status": "completed",
        "approved_by_human": True,
        "risk_level": "low",
        "allowed_paths": [str(DEFAULT_INBOX_PATH)],
        "blocked_paths": ["services/"],
        "validator_chain_required": True,
        "commit_package_required": True,
    }
    issues = validate_approval_inbox_record(payload)
    assert "inbox_missing:authority_status" in issues


def test_malformed_json_returns_blocked_without_crash(tmp_path: Path) -> None:
    malformed = tmp_path / "bad.json"
    malformed.write_text("{not-json", encoding="utf-8")

    result = validate_file(malformed)

    assert result.status == "BLOCKED"
    assert result.malformed is True
    assert "malformed_json" in result.issues


def test_apply_approval_without_human_review_evidence_is_rejected() -> None:
    gate_payload = {
        "approval_gate_id": "APPLY_APPROVAL_GATE_001",
        "packet_id": "SAMPLE-GATE-001",
        "requested_mode": "APPLY",
        "approved_mode": "APPLY",
        "approval_status": "approved_for_apply",
        "approved_by_human": True,
        "allowed_paths": [str(DEFAULT_GATE_PATH)],
        "blocked_paths": ["services/"],
        "validator_chain_required": True,
        "commit_package_required": True,
        # Missing approval_evidence object intentionally.
    }
    issues = validate_apply_gate_record(gate_payload)
    assert "gate_apply_ready_without_approval_evidence" in issues
    assert "gate_apply_ready_without_hmac" in issues


def test_validator_does_not_mutate_input_files(tmp_path: Path) -> None:
    inbox_input = tmp_path / "APPROVAL_INBOX_001.json"
    gate_input = tmp_path / "APPLY_APPROVAL_GATE_001.json"
    payload = {
        "schema": "AIOS_APPROVAL_INBOX.v1",
        "approval_gate_id": "APPROVAL_INBOX_001",
        "authority_status": "active_authority",
        "packet_id": "SAMPLE-INBOX-001",
        "requested_action": "SAMPLE_APPROVAL",
        "requested_mode": "DRY_RUN",
        "approval_status": "completed",
        "approved_by_human": True,
        "risk_level": "low",
        "allowed_paths": [str(inbox_input)],
        "blocked_paths": ["services/"],
        "validator_chain_required": True,
        "commit_package_required": True,
        "push_blocked_until_final_review": True,
    }
    gate = {
        "approval_gate_id": "APPLY_APPROVAL_GATE_001",
        "packet_id": "SAMPLE-GATE-001",
        "requested_mode": "DRY_RUN",
        "approved_mode": "DRY_RUN_ONLY",
        "approval_status": "pending_review",
        "approved_by_human": False,
        "allowed_paths": [str(gate_input)],
        "blocked_paths": ["services/"],
        "validator_chain_required": True,
        "commit_package_required": True,
    }

    inbox_input.write_text(json.dumps(payload), encoding="utf-8")
    gate_input.write_text(json.dumps(gate), encoding="utf-8")
    expected_inbox = inbox_input.read_text(encoding="utf-8")
    expected_gate = gate_input.read_text(encoding="utf-8")

    run_validator([inbox_input, gate_input], json_output=True)

    assert inbox_input.read_text(encoding="utf-8") == expected_inbox
    assert gate_input.read_text(encoding="utf-8") == expected_gate


def test_evidence_output_is_valid_json(tmp_path: Path) -> None:
    inbox_input = tmp_path / "APPROVAL_INBOX_001.json"
    gate_input = tmp_path / "APPLY_APPROVAL_GATE_001.json"
    inbox_input.write_text(
        json.dumps(
            {
                "schema": "AIOS_APPROVAL_INBOX.v1",
                "approval_gate_id": "APPROVAL_INBOX_001",
                "authority_status": "active_authority",
                "packet_id": "SAMPLE-INBOX-001",
                "requested_action": "SAMPLE_APPROVAL",
                "requested_mode": "DRY_RUN",
                "approval_status": "completed",
                "approved_by_human": True,
                "risk_level": "low",
                "allowed_paths": [str(inbox_input)],
                "blocked_paths": ["services/"],
                "validator_chain_required": True,
                "commit_package_required": True,
                "push_blocked_until_final_review": True,
            }
        ),
        encoding="utf-8",
    )
    gate_input.write_text(
        json.dumps(
            {
                "approval_gate_id": "APPLY_APPROVAL_GATE_001",
                "packet_id": "SAMPLE-GATE-001",
                "requested_mode": "DRY_RUN",
                "approved_mode": "DRY_RUN_ONLY",
                "approval_status": "pending_review",
                "approved_by_human": False,
                "allowed_paths": [str(gate_input)],
                "blocked_paths": ["services/"],
                "validator_chain_required": True,
                "commit_package_required": True,
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "approval_inbox_schema_validator_dry_run.example.json"
    returncode, payload = run_validator([inbox_input, gate_input], json_output=True, output=output)

    assert returncode in {0, 1}
    assert output.exists()
    parsed = json.loads(output.read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)
    assert parsed["validator"] == "aios_approval_inbox_schema_validator"


def test_forbidden_paths_are_not_touched(tmp_path: Path) -> None:
    # Ensure validator refuses input under forbidden paths and does not create output files there.
    forbidden_input = tmp_path / "AGENTS.md"
    forbidden_input.write_text("{}", encoding="utf-8")
    result = validate_file(forbidden_input)

    assert result.status == "BLOCKED"
    assert "input_path_is_forbidden" in result.issues
