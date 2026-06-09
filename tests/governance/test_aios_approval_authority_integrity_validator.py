from __future__ import annotations

import hmac
import json
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from automation.validators.aios_approval_authority_integrity_validator import (
    _canonical_payload,
    validate_approval_gate,
)


def _approved_gate() -> dict[str, object]:
    return {
        "packet_id": "AIOS-TEST-APPLY",
        "requested_mode": "APPLY",
        "approved_mode": "APPLY",
        "approval_status": "approved_for_apply",
        "approved_by_human": True,
        "approval_timestamp_utc": "2026-06-08T15:20:30Z",
        "allowed_paths": ["automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json"],
        "blocked_paths": [".github/", "secrets/", ".env"],
        "validator_chain": ["approval_authority_integrity"],
        "validator_chain_required": True,
        "commit_package_required": True,
        "approval_evidence": {
            "type": "HMAC_SHA256",
            "approval_nonce": "test-nonce",
            "approval_hmac_sha256": "",
        },
    }


def _with_hmac(gate: dict[str, object], key: str) -> dict[str, object]:
    evidence = dict(gate["approval_evidence"])  # type: ignore[index]
    evidence["approval_hmac_sha256"] = hmac.new(
        key.encode("utf-8"),
        _canonical_payload({**gate, "approval_evidence": evidence}).encode("utf-8"),
        sha256,
    ).hexdigest()
    return {**gate, "approval_evidence": evidence}


def test_forged_460_style_gate_is_rejected() -> None:
    gate = {
        "packet_id": "AIOS-HEARTBEAT-ONLY-PROOF-HARNESS-APPLY-V1",
        "bound_by": "Anthony explicit approval gate update",
        "bound_at": "2026-06-08T00:00:00Z",
        "requested_mode": "APPLY",
        "approved_mode": "APPLY",
        "approval_status": "approved_for_apply",
        "approved_by_human": True,
        "allowed_paths": ["tests/orchestration/"],
        "blocked_paths": [".github/"],
        "validator_chain_required": True,
        "commit_package_required": True,
    }

    result = validate_approval_gate(gate)

    assert result.status == "BLOCKED"
    assert result.hardened_approval_verified is False
    assert "approval_timestamp_placeholder" in result.failed_checks
    assert "bound_by_free_text_without_hardened_evidence" in result.failed_checks
    assert "approval_hmac_missing_or_invalid" in result.failed_checks


def test_approved_by_human_without_hardened_evidence_is_rejected() -> None:
    gate = _approved_gate()
    gate["approval_evidence"] = {"type": "MISSING"}

    result = validate_approval_gate(gate)

    assert result.status == "BLOCKED"
    assert "approval_hmac_missing_or_invalid" in result.failed_checks


def test_placeholder_timestamp_is_rejected() -> None:
    gate = _with_hmac({**_approved_gate(), "approval_timestamp_utc": "2026-06-08T00:00:00Z"}, "test-key")

    result = validate_approval_gate(gate, hmac_key="test-key")

    assert result.status == "BLOCKED"
    assert "approval_timestamp_placeholder" in result.failed_checks


def test_valid_hardened_approval_fixture_is_accepted_with_test_key() -> None:
    gate = _with_hmac(_approved_gate(), "test-key")

    result = validate_approval_gate(gate, hmac_key="test-key")

    assert result.status == "PASS"
    assert result.hardened_approval_verified is True


def test_safe_pending_gate_is_not_apply_approved() -> None:
    result = validate_approval_gate(
        {
            "packet_id": "AIOS-TEST-APPLY",
            "requested_mode": "APPLY",
            "approved_mode": "DRY_RUN_ONLY",
            "approval_status": "pending_review",
            "approved_by_human": False,
            "allowed_paths": ["automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json"],
            "blocked_paths": [".github/"],
            "validator_chain_required": True,
            "commit_package_required": True,
        }
    )

    assert result.status == "PENDING_REVIEW"
    assert result.hardened_approval_verified is False


def test_dispatcher_does_not_trust_raw_approval_boolean(tmp_path: Path) -> None:
    from automation.orchestration.dispatcher.assignment_executor import summarize_state

    summary = summarize_state(
        {
            "approval_inbox": {"status": "PRESENT", "payload": {"approval_status": "completed"}},
            "apply_gate": {"status": "PRESENT", "payload": _approved_gate()},
            "active_work_packets": {"status": "PRESENT", "packets": []},
            "historical_queue": {"status": "PRESENT", "payload": {"status": "HISTORICAL"}},
            "lock_registry": {"status": "PRESENT", "payload": {"locks": []}},
            "proposed_backlog": {"contract_status": "PROPOSED_BACKLOG"},
            "worker_inbox": {"status": "PRESENT", "payload": {"items": []}},
            "worker_registry": {"status": "PRESENT", "payload": {"workers": []}},
            "pr_backlog": {"status": "UNKNOWN", "open_prs": []},
        }
    )

    assert summary["approval_state"]["future_apply_approved"] is False
    assert summary["approval_state"]["approval_gate_integrity"]["status"] == "BLOCKED"


def test_packet_state_move_blocks_raw_boolean_apply_transition(tmp_path: Path) -> None:
    packet = tmp_path / "packet.json"
    packet.write_text(
        json.dumps(
            {
                "packet_id": "AIOS-RAW-BOOLEAN",
                "status": "approved",
                "mode": "APPLY",
                "approval_required": True,
                "approved_by_human": True,
                "approval_status": "approved_for_apply",
                "validator_chain_status": "PASS",
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            "automation/orchestration/work_packets/Move-AiOsPacketState.ps1",
            "-PacketPath",
            str(packet),
            "-TargetState",
            "applying",
            "-Apply",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "raw approved_by_human is not sufficient" in (result.stdout + result.stderr)
