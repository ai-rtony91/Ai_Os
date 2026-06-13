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


def _ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _ps_array(values: list[str]) -> str:
    if not values:
        return "@()"
    return "@(" + ", ".join(_ps_quote(str(item)) for item in values) + ")"


def _run_ps_command(command: str) -> str:
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        command,
    ]
    return subprocess.check_output(cmd, text=True, cwd=str(REPO_ROOT))


def _run_generator_command(script: Path, args: list[tuple[str, object]]) -> str:
    command_parts = [f"& {_ps_quote(str(script))}"]
    for switch, value in args:
        if isinstance(value, bool):
            if value:
                command_parts.append(switch)
        elif isinstance(value, list):
            command_parts.append(switch)
            command_parts.append(_ps_array(value))
        else:
            command_parts.append(switch)
            command_parts.append(_ps_quote(str(value)))

    command = " ".join(command_parts)
    return _run_ps_command(command)


def _get_field(packet_text: str, field_name: str) -> str:
    lines = packet_text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == f"{field_name}:" and index + 1 < len(lines):
            return lines[index + 1].strip()
    raise AssertionError(f"Missing field '{field_name}' in generated packet.")


def _apply_kwarg_overrides(args: list[tuple[str, object]], kwargs: dict[str, object]) -> list[tuple[str, object]]:
    args_map = {key: index for index, (key, _) in enumerate(args)}
    for key, value in kwargs.items():
        switch = f"-{key}"
        if switch in args_map:
            args[args_map[switch]] = (switch, value)
        else:
            args.append((switch, value))
    return args


def _run_generator(output_json: bool = True, **kwargs: object) -> dict:
    args: list[tuple[str, object]] = [
        ("-Zone", "ORCHESTRATION"),
        ("-Lane", "PACKET_GENERATOR"),
        ("-Mission", "build packet generator v1"),
        ("-Branch", "feature/codex-packet-generator-v1"),
        ("-ApprovalAuthority", "Anthony approves this scoped packet."),
        ("-PacketId", "AIOS-CODEX-PACKET-GENERATOR-APPLY-V1"),
        ("-Worktree", str(REPO_ROOT)),
        ("-StartBranch", "main"),
        ("-AllowedMutationFiles", [
            "automation/orchestration/packet_generator/New-AiOsCodexPacket.DRY_RUN.ps1",
            "automation/orchestration/packet_generator/Test-AiOsCodexPacket.DRY_RUN.ps1",
            "tests/orchestration/test_codex_packet_generator.py",
            "docs/AI_OS/autonomy/AIOS_CODEX_PACKET_GENERATOR_V1.md",
        ]),
        ("-ForbiddenPaths", [
            "broker/OANDA/webhook/order/secrets paths",
            "runtime state",
            "scheduler",
            "daemon",
        ]),
        ("-ReadFirst", ["AGENTS.md", "README.md", "RISK_POLICY.md"]),
        ("-Validators", [
            "git diff --check",
            "python -m pytest tests/forex_engine -q -p no:cacheprovider",
        ]),
    ]
    if output_json:
        args.append(("-OutputJson", True))
    if kwargs:
        args = _apply_kwarg_overrides(args, kwargs)
    raw = _run_generator_command(GENERATOR, args)
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


def test_array_binding_uses_scalar_identity_fields():
    result = _run_generator(
        Lane="RELAY_OPERATOR_ACTION_ROUTER",
        Mode="APPLY",
        AllowedMutationFiles=[
            "automation/orchestration/packet_generator/New-AiOsCodexPacket.DRY_RUN.ps1",
            "automation/orchestration/packet_generator/Test-AiOsCodexPacket.DRY_RUN.ps1",
            "tests/orchestration/test_relay_operator_mode.py",
            "docs/AI_OS/autonomy/AIOS_RELAY_OPERATOR_MODE_V1.md",
        ],
        ForbiddenPaths=[
            "broker/OANDA/webhook/order/secrets paths",
            "runtime state",
            "scheduler",
        ],
        Validators=[
            "git diff --check",
            "python -m pytest tests/orchestration/test_codex_packet_generator.py -q -p no:cacheprovider",
            "python -m pytest tests/orchestration/test_capability_packet_draft.py -q -p no:cacheprovider",
        ],
    )

    assert result["packet_valid"] is True
    packet = result["generated_packet_text"]

    assert _get_field(packet, "SUPERVISOR IDENTITY") == "ChatGPT Planning Supervisor under Anthony Human Owner"
    assert _get_field(packet, "WORKER IDENTITY") == "Codex CLI local executor inside C:\\Dev\\Ai.Os"
    assert _get_field(packet, "WORKTREE") == str(REPO_ROOT)
    assert _get_field(packet, "START_BRANCH") == "main"
    assert _get_field(packet, "MODE") == "APPLY"
    assert _get_field(packet, "ZONE") == "ORCHESTRATION"
    assert _get_field(packet, "LANE") == "RELAY_OPERATOR_ACTION_ROUTER"

    validated = _run_validator(packet)
    assert validated["packet_valid"] is True


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
    malformed = result["generated_packet_text"].replace("IDENTITY MARKER:", "IDENTITY:")
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
