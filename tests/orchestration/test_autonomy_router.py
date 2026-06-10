"""Tests for autonomy next-action router dry-run script."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "automation/orchestration/autonomy_router/Get-AiOsAutonomyNextAction.DRY_RUN.ps1"


def run_router(evidence: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-ControlPlaneEvidencePath",
            str(evidence),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_evidence(path: Path, status: str, *, packet_path: Path | None = None, reason: str | None = None) -> Path:
    payload = {
        "schema_version": "AIOS-AUTONOMY-CONTROL-PLANE-V1",
        "status": status,
        "packet_path": str(packet_path) if packet_path else None,
        "evidence_path": str(path),
    }
    if reason:
        payload["reason"] = reason
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def test_router_maps_ready_for_codex_with_packet(tmp_path: Path) -> None:
    packet_path = tmp_path / "packet.md"
    packet_path.write_text("CODEX-ONLY PROMPT\n", encoding="utf-8")
    evidence = write_evidence(tmp_path / "evidence.json", "READY_FOR_CODEX", packet_path=packet_path)

    result = run_router(evidence)
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout.strip())

    assert payload["next_action"] == "RUN_CODEX_WITH_PACKET"
    assert payload["packet_path"] == str(packet_path)
    assert payload["evidence_status"] == "READY_FOR_CODEX"
    assert "powershell -NoProfile" in payload["safe_command"]
    assert all(token.lower() not in payload["safe_command"].lower() for token in ["merge", "force", "delete", "apply", "broker", "secret", "live trading"])


def test_router_classifies_validation_and_request_approval(tmp_path: Path) -> None:
    bad = write_evidence(tmp_path / "validation.json", "VALIDATION_FAILED")
    result_validation = run_router(bad)
    assert result_validation.returncode == 1
    payload_validation = json.loads(result_validation.stdout.strip())
    assert payload_validation["next_action"] == "FIX_VALIDATION"

    protect = write_evidence(tmp_path / "protected.json", "PROTECTED_ACTION_REQUIRED")
    result_protected = run_router(protect)
    assert result_protected.returncode == 1
    payload_protected = json.loads(result_protected.stdout.strip())
    assert payload_protected["next_action"] == "REQUEST_APPROVAL"
    assert "PROTECTED" in payload_protected["reason"].upper()
