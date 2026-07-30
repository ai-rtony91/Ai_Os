"""Contract and host-dependent tests for the AI_OS Codex packet generator v2."""

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
    return "@(" + ",".join(_ps_quote(value) for value in values) + ")"


def _run_script(script: Path, arguments: list[tuple[str, object]]) -> dict:
    if POWERSHELL is None:
        pytest.skip("No PowerShell host found; static v2 contract tests still run.")
    parts = [f"& {_ps_quote(str(script))}"]
    for name, value in arguments:
        parts.append(name)
        if isinstance(value, list):
            parts.append(_ps_array(value))
        elif value is not True:
            parts.append(_ps_quote(str(value)))
    output = subprocess.check_output(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", " ".join(parts)],
        cwd=REPO_ROOT,
        text=True,
    )
    return json.loads(output)


def _valid_args() -> list[tuple[str, object]]:
    values = {
        "MissionId": "AIOS-MISSION", "MissionName": "First Dollar",
        "ProgramId": "AIOS-FOREX", "ProgramName": "Governed Forex",
        "EpicId": "AIOS-EPIC", "EpicName": "Orchestration",
        "BucketId": "AIOS-BUCKET", "BucketName": "Packet Contract",
        "PacketId": "AIOS-PACKET-V2", "PacketName": "Harden Contract",
        "IdentityMarker": "AI_OS OWNER-SUPERVISED", "SupervisorIdentity": "Anthony Human Owner",
        "WorkerIdentity": "EAST_OCC_01", "LockIdentity": "AIOS-PACKET-V2-LOCK",
        "Mode": "APPLY", "Zone": "LOCAL_REPOSITORY", "Lane": "ORCHESTRATION_PACKET_CONTRACT",
        "Worktree": str(REPO_ROOT), "Branch": "work",
        "ApprovalAuthority": "Anthony authorizes bounded local apply.",
        "StopPoint": "Stop after validation and one commit.",
        "StagingAuthority": "AUTHORIZED for named files only.",
        "CommitAuthority": "AUTHORIZED for one commit.", "PushAuthority": "NOT AUTHORIZED.",
        "PullRequestAuthority": "PREPARE ONLY.", "MergeAuthority": "NOT AUTHORIZED.",
    }
    args: list[tuple[str, object]] = [(f"-{key}", value) for key, value in values.items()]
    args += [
        ("-AllowedPaths", ["tests/orchestration/test_codex_packet_generator.py"]),
        ("-ForbiddenPaths", ["every other path"]),
        ("-Preflight", ["pwd", "git status --short --branch", "git branch --show-current", "git remote -v", "git rev-parse HEAD", "git diff --name-only"]),
        ("-Validators", ["git diff --check"]),
        ("-FinalReportFormat", ["STATUS", "Files changed", "Validation"]),
        ("-OutputJson", True),
    ]
    return args


def _generate(**overrides: object) -> dict:
    args = _valid_args()
    positions = {name: index for index, (name, _) in enumerate(args)}
    for key, value in overrides.items():
        name = f"-{key}"
        if name in positions:
            args[positions[name]] = (name, value)
        else:
            args.append((name, value))
    return _run_script(GENERATOR, args)


def _validate(packet: str) -> dict:
    return _run_script(VALIDATOR, [("-PacketText", packet), ("-OutputJson", True)])


def test_static_contract_declares_complete_v2_metadata():
    text = CONTRACT.read_text(encoding="utf-8")
    assert 'schema = "AIOS_CODEX_PACKET_CONTRACT.v2"' in text
    for manifest in ("exact_first_line", "required_markers", "required_scalar_fields", "list_valued_fields", "protected_action_fields", "unresolved_placeholder_patterns", "required_repository_state_commands"):
        assert manifest in text
    for command in ("pwd", "git status --short --branch", "git branch --show-current", "git remote -v", "git rev-parse HEAD", "git diff --name-only"):
        assert f'"{command}"' in text


def test_static_scripts_share_contract_and_preserve_portability():
    generator = GENERATOR.read_text(encoding="utf-8")
    validator = VALIDATOR.read_text(encoding="utf-8")
    assert "Get-AiOsCodexPacketContract" in generator
    assert "Get-AiOsCodexPacketContract" in validator
    assert 'schema="AIOS_CODEX_PACKET_GENERATOR.v2"' in generator
    assert 'schema="AIOS_CODEX_PACKET_VALIDATOR.v2"' in validator
    # Continuation compatibility keeps current-process discovery rather than a
    # hard-coded pwsh/powershell child host.
    assert "$powerShellHost = (Get-Process -Id $PID).Path" in generator
    assert "& $powerShellHost -NoProfile" in generator
    assert "execution_allowed=$false" in generator
    assert "can_continue_without_anthony=$false" in generator


def test_valid_complete_v2_packet_passes_and_starts_exactly():
    generated = _generate()
    assert generated["schema"] == "AIOS_CODEX_PACKET_GENERATOR.v2"
    assert generated["contract_schema"] == "AIOS_CODEX_PACKET_CONTRACT.v2"
    assert generated["packet_valid"] is True
    packet = generated["generated_packet_text"]
    assert packet.splitlines()[0] == "CODEX-ONLY PROMPT"
    validated = _validate(packet)
    assert validated["schema"] == "AIOS_CODEX_PACKET_VALIDATOR.v2"
    assert validated["packet_valid"] is True


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda p: p.replace("AI_OS BOOTSTRAP REQUIRED", "BOOTSTRAP MISSING"), "AI_OS BOOTSTRAP REQUIRED"),
        (lambda p: "wrong\n" + "\n".join(p.splitlines()[1:]), "CODEX-ONLY PROMPT"),
        (lambda p: p.replace("EPIC ID:\nAIOS-EPIC", "EPIC ID:\n"), "EPIC ID"),
        (lambda p: p.replace("ALLOWED PATHS:\n- tests/orchestration/test_codex_packet_generator.py", "ALLOWED PATHS:\n"), "ALLOWED PATHS"),
        (lambda p: p.replace("FORBIDDEN PATHS:\n- every other path", "FORBIDDEN PATHS:\n"), "FORBIDDEN PATHS"),
        (lambda p: p.replace("COMMIT AUTHORITY:\nAUTHORIZED for one commit.", "COMMIT AUTHORITY:\n"), "COMMIT AUTHORITY"),
    ],
)
def test_validator_rejects_missing_required_content(mutation, expected):
    packet = _generate()["generated_packet_text"]
    result = _validate(mutation(packet))
    assert result["packet_valid"] is False
    assert expected in result["missing_required_fields"]


def test_validator_rejects_placeholder_invalid_mode_and_missing_preflight():
    packet = _generate()["generated_packet_text"]
    malformed = packet.replace("AIOS-PACKET-V2", "{packet-id}", 1).replace("MODE:\nAPPLY", "MODE:\nEXECUTE")
    malformed = malformed.replace("- git remote -v\n", "")
    result = _validate(malformed)
    assert result["packet_valid"] is False
    assert any(item.startswith("unresolved_placeholder:") for item in result["validation_defects"])
    assert "invalid_mode" in result["validation_defects"]
    assert "missing_preflight_command:git remote -v" in result["validation_defects"]


def test_generator_rejects_empty_lists_and_placeholders():
    result = _generate(AllowedPaths=[], PacketName="TBD")
    assert result["packet_valid"] is False
    assert "ALLOWED PATHS" in result["missing_required_fields"]
    assert "unresolved_placeholder:PACKET NAME" in result["validation_defects"]


def test_validator_rejects_malformed_protected_authority():
    packet = _generate()["generated_packet_text"]
    packet = packet.replace("PUSH AUTHORITY:\nNOT AUTHORIZED.", "PUSH AUTHORITY:\nMaybe later.")
    result = _validate(packet)
    assert result["packet_valid"] is False
    assert "malformed_protected_authority:PUSH AUTHORITY" in result["validation_defects"]


def test_dry_run_generator_performs_no_writes():
    before = subprocess.check_output(["git", "status", "--short", "--untracked-files=all"], cwd=REPO_ROOT, text=True)
    _generate(Mode="DRY_RUN")
    after = subprocess.check_output(["git", "status", "--short", "--untracked-files=all"], cwd=REPO_ROOT, text=True)
    assert before == after


def test_terminology_warning_remains_non_blocking():
    packet = _generate()["generated_packet_text"] + "\nLegacy note: task pack\n"
    result = _validate(packet)
    assert result["packet_valid"] is True
    assert result["terminology_warnings"]
