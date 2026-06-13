"""Tests for draft capability packet generation."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "packet_generator"
    / "New-AiOsCapabilityPacketDraft.DRY_RUN.ps1"
)
VALIDATOR = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "packet_generator"
    / "Test-AiOsCodexPacket.DRY_RUN.ps1"
)


def _run_capability_draft(**kwargs: str | list[str] | bool) -> dict:
    args = ["-OutputJson"]
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

    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(SCRIPT),
    ] + args
    raw = subprocess.check_output(cmd, text=True, cwd=str(REPO_ROOT))
    return json.loads(raw.strip())


def _run_validator(packet_text: str) -> dict:
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(VALIDATOR),
        "-PacketText",
        packet_text,
        "-OutputJson",
    ]
    raw = subprocess.check_output(cmd, text=True, cwd=str(REPO_ROOT))
    return json.loads(raw.strip())


def _packet_headers(packet: str) -> None:
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
        "execution_allowed: false",
        "can_continue_without_anthony: false",
    ):
        assert required in packet


def test_claude_code_intent_becomes_research_scaffold() -> None:
    result = _run_capability_draft(
        CapabilityName="Claude Code",
        CapabilityIntent="connect Claude Code as optional code review actor",
    )

    assert result["schema"] == "AIOS_CAPABILITY_PACKET_DRAFT.v1"
    assert result["capability_type"] in {"cli_tool", "unknown"}
    assert result["safety_tier"] == "DRY_RUN_ONLY"
    assert result["suggested_actor"] == "claude_code"
    assert result["execution_allowed"] is False
    assert result["requires_human_review"] is True
    assert "RESEARCH" in result["exact_next_action"].upper()
    _packet_headers(result["generated_packet_text"])


def test_ue5_build_logs_maps_to_game_engine_style() -> None:
    result = _run_capability_draft(
        CapabilityName="UE5 Logs",
        CapabilityIntent="inspect Unreal Engine 5 build logs and generate fix packet",
    )

    assert result["capability_type"] == "game_engine"
    assert result["suggested_actor"] == "unreal_engine_5"
    assert result["safety_tier"] == "DRY_RUN_ONLY"
    assert result["execution_allowed"] is False
    assert result["generated_packet_id"].startswith("AIOS-CAPABILITY-GAME_ENGINE")


def test_broker_api_is_blocked_high_risk_intent() -> None:
    result = _run_capability_draft(
        CapabilityName="Broker API",
        CapabilityIntent="connect broker API for future sandbox trading",
    )

    assert result["capability_type"] == "broker_sandbox"
    assert result["safety_tier"] in {"REQUIRES_SECRET_REVIEW", "BLOCKED_HIGH_RISK"}
    assert result["execution_allowed"] is False
    assert "No live integration" in result["stop_point"]
    assert "live_integration" in result["exact_next_action"].lower() or "risk review" in result["exact_next_action"].lower()


def test_unknown_intent_uses_dry_run_scaffold() -> None:
    result = _run_capability_draft(
        CapabilityName="Quantum Weather Sensor",
        CapabilityIntent="connect a brand new unsupported capability",
    )

    assert result["capability_type"] == "unknown"
    assert result["safety_tier"] == "DRY_RUN_ONLY"
    assert result["suggested_actor"] == "unknown_actor"
    assert result["execution_allowed"] is False
    assert "broker/OANDA/webhook/order/secrets paths" in result["forbidden_paths"]


def test_generated_packet_passes_validator() -> None:
    result = _run_capability_draft(
        CapabilityName="Research Connector",
        CapabilityIntent="draft a study capability",
    )

    validated = _run_validator(result["generated_packet_text"])
    assert validated["schema"] == "AIOS_CODEX_PACKET_VALIDATOR.v1"
    assert validated["packet_valid"] is True
    assert validated["execution_allowed"] is False


def test_dry_run_does_not_write_files() -> None:
    pre = subprocess.check_output(["git", "status", "--short"], text=True, cwd=str(REPO_ROOT))
    _run_capability_draft(
        CapabilityName="No File Write",
        CapabilityIntent="run in dry run mode only",
    )
    post = subprocess.check_output(["git", "status", "--short"], text=True, cwd=str(REPO_ROOT))
    assert pre == post
