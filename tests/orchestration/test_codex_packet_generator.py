"""Contract tests for the governed AI_OS Codex packet generator."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKET_DIR = REPO_ROOT / "automation" / "orchestration" / "packet_generator"
GENERATOR = PACKET_DIR / "New-AiOsCodexPacket.DRY_RUN.ps1"
VALIDATOR = PACKET_DIR / "Test-AiOsCodexPacket.DRY_RUN.ps1"
CONTRACT = PACKET_DIR / "AiOsCodexPacketContract.ps1"
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")


def _ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _ps_array(values: list[str]) -> str:
    return "@(" + ", ".join(_ps_quote(item) for item in values) + ")"


def _run_command(command: str) -> str:
    if POWERSHELL is None:
        pytest.skip("PowerShell is not installed in this environment")
    return subprocess.check_output(
        [POWERSHELL, "-NoProfile", "-Command", command],
        text=True,
        cwd=REPO_ROOT,
    )


def _run_generator(**overrides: object) -> dict:
    values: dict[str, object] = {
        "IdentityMarker": "AIOS_CODEX_PACKET_GENERATOR_TEST_V2",
        "SupervisorIdentity": "CODEX_EAST_WORKSITE_SUPERVISOR",
        "MissionId": "MISSION-AIOS-001",
        "MissionName": "AIOS Governed Engineering Reliability",
        "ProgramId": "PRG-ORCH-001",
        "ProgramName": "AIOS Orchestration",
        "EpicId": "EPC-ORCH-001",
        "EpicName": "Packet Contract Reliability",
        "BucketId": "BKT-ORCH-001",
        "BucketName": "Packet Generator Repair",
        "PacketId": "PKT-EAST-001",
        "PacketName": "Repair Codex Packet Generator",
        "Mode": "APPLY",
        "Zone": "EAST",
        "Lane": "PACKET_GENERATOR",
        "WorkerIdentity": "EAST_OCC_01",
        "LockIdentity": "LOCK_EAST_PACKET_GENERATOR_OCC01",
        "Worktree": str(REPO_ROOT),
        "Branch": "work",
        "ApprovalAuthority": "Anthony approves only this bounded local APPLY.",
        "AllowedMutationFiles": [str(GENERATOR.relative_to(REPO_ROOT))],
        "ForbiddenPaths": ["Every other repository path"],
        "ReadFirst": ["AGENTS.md", "README.md"],
        "Validators": ["git diff --check", "focused packet-generator tests"],
        "StopPoint": "Stop after validation and final report without protected actions.",
    }
    values.update(overrides)
    parts = [f"& {_ps_quote(str(GENERATOR))}"]
    for name, value in values.items():
        parts.extend((f"-{name}", _ps_array(value) if isinstance(value, list) else _ps_quote(str(value))))
    parts.append("-OutputJson")
    return json.loads(_run_command(" ".join(parts)).strip())


def _run_validator(packet: str) -> dict:
    command = f"& {_ps_quote(str(VALIDATOR))} -PacketText {_ps_quote(packet)} -OutputJson"
    return json.loads(_run_command(command).strip())


def _remove_section(packet: str, label: str) -> str:
    lines = packet.splitlines()
    start = lines.index(f"{label}:")
    end = start + 1
    while end < len(lines):
        if lines[end].endswith(":") and lines[end].upper() == lines[end]:
            break
        end += 1
    return "\n".join(lines[:start] + lines[end:])


def test_complete_governed_apply_packet_passes_validation():
    result = _run_generator()
    assert result["schema"] == "AIOS_CODEX_PACKET_GENERATOR.v2"
    assert result["contract_schema"] == "AIOS_CODEX_PACKET_CONTRACT.v2"
    assert result["packet_valid"] is True
    validated = _run_validator(result["generated_packet_text"])
    assert validated["packet_valid"] is True
    assert validated["execution_allowed"] is False
    assert validated["protected_actions_authorized"] is False


def test_generator_emits_complete_identity_hierarchy():
    packet = _run_generator()["generated_packet_text"]
    fields = (
        "MISSION ID", "MISSION NAME", "PROGRAM ID", "PROGRAM NAME",
        "EPIC ID", "EPIC NAME", "BUCKET ID", "BUCKET NAME",
        "PACKET ID", "PACKET NAME",
    )
    positions = [packet.index(f"{field}:") for field in fields]
    assert positions == sorted(positions)


def test_missing_identity_hierarchy_fields_fail_validation():
    packet = _run_generator()["generated_packet_text"]
    for field in ("MISSION ID", "PROGRAM NAME", "EPIC ID", "BUCKET NAME", "PACKET NAME"):
        validated = _run_validator(_remove_section(packet, field))
        assert validated["packet_valid"] is False
        assert field in validated["missing_required_fields"]


def test_empty_and_whitespace_values_fail_validation():
    packet = _run_generator()["generated_packet_text"]
    for replacement in ("", "   "):
        malformed = packet.replace("MISSION ID:\nMISSION-AIOS-001", f"MISSION ID:\n{replacement}")
        validated = _run_validator(malformed)
        assert validated["packet_valid"] is False
        assert "MISSION ID" in validated["missing_required_fields"]


def test_required_governance_sections_fail_when_missing():
    packet = _run_generator()["generated_packet_text"]
    for field in (
        "WORKTREE", "BRANCH", "PREFLIGHT", "ALLOWED PATHS", "FORBIDDEN PATHS",
        "APPROVAL AUTHORITY", "VALIDATOR CHAIN", "STOP POINT", "FINAL REPORT FORMAT",
    ):
        validated = _run_validator(_remove_section(packet, field))
        assert validated["packet_valid"] is False
        assert field in validated["missing_required_fields"]


def test_first_line_routing_marker_must_be_exact():
    packet = _run_generator()["generated_packet_text"]
    validated = _run_validator(packet.replace("CODEX-ONLY PROMPT", "CODEX PROMPT", 1))
    assert validated["packet_valid"] is False
    assert "FIRST LINE" in validated["validation_defects"]


def test_unresolved_template_values_are_rejected():
    for bad_value in ("@filename", "path/to/file", "{feature}", "[REAL-FILENAME]", "TBD"):
        result = _run_generator(PacketName=bad_value)
        assert result["packet_valid"] is False
        assert result["generated_packet_text"] == ""
        assert "PACKET NAME" in result["missing_required_fields"]


def test_unresolved_read_first_value_is_rejected_before_packet_emission():
    result = _run_generator(ReadFirst=["AGENTS.md", "@filename"])

    assert result["packet_valid"] is False
    assert result["generated_packet_text"] == ""
    assert "UNRESOLVED VALUE" in result["missing_required_fields"]


def test_apply_does_not_authorize_protected_actions():
    packet = _run_generator()["generated_packet_text"]
    for field in (
        "STAGING AUTHORITY", "COMMIT AUTHORITY", "PUSH AUTHORITY",
        "PULL REQUEST AUTHORITY", "MERGE AUTHORITY",
    ):
        assert f"{field}:\nNOT AUTHORIZED" in packet
    assert "git add --" not in packet
    assert "git commit -m" not in packet
    assert "git push" not in packet
    assert "gh pr create" not in packet
    assert "gh pr merge" not in packet


def test_validator_rejects_claimed_protected_action_authority():
    packet = _run_generator()["generated_packet_text"]
    malformed = packet.replace("COMMIT AUTHORITY:\nNOT AUTHORIZED", "COMMIT AUTHORITY:\nAUTHORIZED")
    validated = _run_validator(malformed)
    assert validated["packet_valid"] is False
    assert "COMMIT AUTHORITY" in validated["validation_defects"]


def test_preflight_discovers_worktree_branch_dirty_state_remotes_and_head():
    packet = _run_generator()["generated_packet_text"]
    for command in (
        "pwd", "git status --short --branch", "git branch --show-current",
        "git remote -v", "git rev-parse HEAD",
    ):
        assert command in packet


def test_generator_requires_observed_branch_and_worktree():
    for override, field in (({"Worktree": ""}, "WORKTREE"), ({"Branch": ""}, "BRANCH")):
        result = _run_generator(**override)
        assert result["packet_valid"] is False
        assert field in result["missing_required_fields"]


def test_shared_contract_is_the_single_required_field_manifest():
    contract = CONTRACT.read_text(encoding="utf-8")
    generator = GENERATOR.read_text(encoding="utf-8")
    validator = VALIDATOR.read_text(encoding="utf-8")
    assert "required_fields = @(" in contract
    assert "Get-AiOsCodexPacketContract" in generator
    assert "Get-AiOsCodexPacketContract" in validator
    assert "$packetContract.required_fields" in validator
    assert "\n        required_fields = @(" not in generator
    assert "\n        required_fields = @(" not in validator


def test_dry_run_generator_does_not_write_files():
    before = subprocess.check_output(
        ["git", "status", "--short", "--untracked-files=all"], text=True, cwd=REPO_ROOT
    )
    _run_generator(Mode="DRY_RUN")
    after = subprocess.check_output(
        ["git", "status", "--short", "--untracked-files=all"], text=True, cwd=REPO_ROOT
    )
    assert before == after
