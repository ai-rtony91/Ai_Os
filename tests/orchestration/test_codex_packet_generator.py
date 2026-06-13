"""Tests for AI_OS Codex packet generator v1."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATOR = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "packet_generator"
    / "New-AiOsCodexPacket.DRY_RUN.ps1"
)
VALIDATOR = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "packet_generator"
    / "Test-AiOsCodexPacket.DRY_RUN.ps1"
)


def _run_ps(script: Path, args: list[str]) -> str:
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
    ]
    cmd.extend(args)
    return subprocess.check_output(cmd, text=True, cwd=str(REPO_ROOT))


def _run_generator(output_json: bool = True, **kwargs: object) -> dict:
    args = ["-Zone", "ORCHESTRATION", "-Lane", "PACKET_GENERATOR", "-Mission", "build packet generator v1", "-Branch", "feature/codex-packet-generator-v1", "-ApprovalAuthority", "Anthony approves this scoped packet."]
    args.extend(["-PacketId", "AIOS-CODEX-PACKET-GENERATOR-APPLY-V1"])
    args.extend(["-Worktree", str(REPO_ROOT)])
    args.extend(["-StartBranch", "main"])
    args.extend(["-AllowedMutationFiles", "automation/orchestration/packet_generator/New-AiOsCodexPacket.DRY_RUN.ps1", "automation/orchestration/packet_generator/Test-AiOsCodexPacket.DRY_RUN.ps1", "tests/orchestration/test_codex_packet_generator.py", "docs/AI_OS/autonomy/AIOS_CODEX_PACKET_GENERATOR_V1.md"])
    args.extend(["-ForbiddenPaths", "broker/OANDA/webhook/order/secrets paths", "runtime state", "scheduler", "daemon"])
    args.extend(["-ReadFirst", "AGENTS.md", "README.md", "RISK_POLICY.md"])
    args.extend(["-Validators", "git diff --check", "python -m pytest tests/forex_engine -q -p no:cacheprovider"])
    if output_json:
        args.append("-OutputJson")
    if kwargs:
        for key, value in kwargs.items():
            switch = f"-{key}"
            if isinstance(value, bool):
                if value:
                    args.append(switch)
            elif isinstance(value, list):
                for item in value:
                    args.extend([switch, str(item)])
            else:
                args.extend([switch, str(value)])
    raw = _run_ps(GENERATOR, args)
    return json.loads(raw.strip())


def _run_validator(packet_text: str) -> dict:
    args = ["-PacketText", packet_text, "-OutputJson"]
    raw = _run_ps(VALIDATOR, args)
    return json.loads(raw.strip())


def test_generator_emits_mandatory_headers():
    result = _run_generator()
    assert result["schema"] == "AIOS_CODEX_PACKET_GENERATOR.v1"
    assert result["packet_valid"] is True
    packet = result["generated_packet_text"]

    for required in (
        "CODEX-ONLY PROMPT",
        "AI_OS EXECUTION TOKEN",
        "AI_OS BOOTSTRAP REQUIRED",
        "IDENTITY MARKER:",
        "SUPERVISOR IDENTITY:",
        "WORKER IDENTITY:",
        "PACKET ID:",
        "MODE:",
        "ZONE:",
        "LANE:",
        "APPROVAL AUTHORITY:",
        "MISSION:",
        "PREFLIGHT",
        "REQUIRED PREFLIGHT STATE:",
        "BRANCH PLAN:",
        "READ FIRST:",
        "ALLOWED MUTATION FILES ONLY:",
        "FORBIDDEN PATHS:",
        "IMPLEMENTATION:",
        "VALIDATOR CHAIN:",
        "COMMIT:",
        "STOP POINT:",
        "COMPLETION REPORT FORMAT:",
    ):
        assert required in packet

    assert "execution_allowed: false" in packet
    assert "can_continue_without_anthony: false" in packet
    assert "writes_files: false" in packet

    assert "automation/orchestration/packet_generator/New-AiOsCodexPacket.DRY_RUN.ps1" in packet
    assert "broker/OANDA/webhook/order/secrets paths" in packet


def test_validator_accepts_complete_packet():
    result = _run_generator()
    validated = _run_validator(result["generated_packet_text"])
    assert validated["schema"] == "AIOS_CODEX_PACKET_VALIDATOR.v1"
    assert validated["packet_valid"] is True
    assert validated["execution_allowed"] is False


def test_validator_detects_missing_bootstrap():
    result = _run_generator()
    malformed = result["generated_packet_text"].replace("AI_OS BOOTSTRAP REQUIRED", "AI OS BOOTSTRAP MISSING")
    validated = _run_validator(malformed)
    assert validated["packet_valid"] is False
    assert "AI_OS BOOTSTRAP REQUIRED" in validated["missing_required_fields"]


def test_validator_detects_missing_identity():
    result = _run_generator()
    malformed = result["generated_packet_text"].replace("IDENTITY MARKER:\r\n", "IDENTITY:\r\n")
    validated = _run_validator(malformed)
    assert validated["packet_valid"] is False
    assert "IDENTITY MARKER" in validated["missing_required_fields"]


def test_validator_detects_missing_stop_point():
    result = _run_generator()
    malformed = result["generated_packet_text"].replace("STOP POINT:", "STOP_POINT:")
    validated = _run_validator(malformed)
    assert validated["packet_valid"] is False
    assert "STOP POINT" in validated["missing_required_fields"]


def test_from_continuation_plan_can_produce_skeleton():
    result = _run_generator(
        PacketId="",
        Zone="",
        Lane="",
        Mission="",
        FromContinuationPlan=True,
        ReadFirst=[],
    )
    packet = result["generated_packet_text"]

    assert result["packet_valid"] is True
    assert "AIOS-FOREX-PAPER-LEARNING-ACTION-ROUTER-APPLY-V1" in packet
    assert "PAPER_LEARNING_ACTION_ROUTER" in packet


def test_dry_run_does_not_write_files():
    pre = subprocess.check_output(
        ["git", "status", "--short", "--untracked-files=all"], text=True, cwd=str(REPO_ROOT)
    )
    _run_generator()
    post = subprocess.check_output(
        ["git", "status", "--short", "--untracked-files=all"], text=True, cwd=str(REPO_ROOT)
    )
    assert pre == post

