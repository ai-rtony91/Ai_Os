"""Tests for autonomy control plane dry-run orchestration."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "automation/orchestration/autonomy_control_plane/Invoke-AiOsAutonomyControlPlane.DRY_RUN.ps1"


def run_control_plane(
    *,
    goal_text: str | None = None,
    packet_path: Path | None = None,
    validator_script: Path,
    loop_script: Path,
    packet_runner_script: Path,
    report_dir: Path,
) -> subprocess.CompletedProcess[str]:
    args = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(SCRIPT),
        "-AutonomyLoopScriptPath",
        str(loop_script),
        "-PacketRunnerScriptPath",
        str(packet_runner_script),
        "-ValidatorScriptPath",
        str(validator_script),
        "-OutputReportPath",
        str(report_dir / "control_plane.md"),
        "-OutputEvidencePath",
        str(report_dir / "control_plane.evidence.json"),
    ]

    if goal_text is not None:
        args.extend(["-GoalText", goal_text])
    if packet_path is not None:
        args.extend(["-PacketPath", str(packet_path)])

    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def make_fake_validator(script_path: Path, *, status: str = "PASS") -> Path:
    payload = {"status": status, "errors": [] if status == "PASS" else ["invalid"], "warnings": []}
    if status == "PASS":
        exit_code = 0
    else:
        exit_code = 1
    script_path.write_text(
        f"import json,sys\nprint(json.dumps({json.dumps(payload)}))\nsys.exit({exit_code})\n",
        encoding="utf-8",
    )
    return script_path


def make_fake_loop_script(script_path: Path, packet_path: Path) -> Path:
    script_path.write_text(
        "\n".join(
            [
                "param([string]$GoalText,[string]$AutonomyReportDirectory,[switch]$PassThrough,[string]$PacketRunnerOutputPath,[string]$PacketRunnerReportPath)",
                "New-Item -ItemType Directory -Path (Split-Path -Parent $PacketRunnerOutputPath) -Force | Out-Null",
                f"Set-Content -Path '{packet_path}' -Value 'CODEX-ONLY PROMPT`nAI_OS EXECUTION TOKEN: CONTROL_PLANE_FAKE`nAI_OS BOOTSTRAP REQUIRED: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY`n\\nIDENTITY MARKER: CP-TEST`nPACKET PATH TEST`n' -Encoding utf8",
                "Set-Content -Path $PacketRunnerOutputPath -Value 'packet output' -Encoding utf8",
                "Set-Content -Path $PacketRunnerReportPath -Value '{\"status\":\"PASS\"}' -Encoding utf8",
                "$payload = [ordered]@{",
                "    packet_path = '" + str(packet_path) + "'",
                "    packet_output_path = $PacketRunnerOutputPath",
                "    report_output_path = $PacketRunnerReportPath",
                "    validator_status = 'PASS'",
                "    auto_runner_status = 'PASS'",
                "    blocked = $false",
                "}",
                "if ($PassThrough) { Write-Output ($payload | ConvertTo-Json -Depth 20) } else { Write-Output 'Autonomy loop dry-run complete.' }",
            ]
        ),
        encoding="utf-8",
    )
    return script_path


def make_fake_packet_runner(script_path: Path) -> Path:
    script_path.write_text(
        "param([string]$PacketPath,[string]$OutputPath,[string]$ReportPath)\n"
        "Set-Content -Path $OutputPath -Value (Get-Content $PacketPath) -Encoding utf8\n"
        "$obj = [ordered]@{ status = 'PASS'; exit_code = 0; packet_output_path = $OutputPath; report_path = $ReportPath };\n"
        "Write-Output ($obj | ConvertTo-Json -Depth 10)",
        encoding="utf-8",
    )
    return script_path


def test_control_plane_goal_path_goes_through_discovery(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    packet_path = tmp_path / "generated_packet.md"
    loop_script = make_fake_loop_script(tmp_path / "fake_loop.ps1", packet_path=packet_path)
    packet_runner_script = make_fake_packet_runner(tmp_path / "fake_runner.ps1")
    validator_script = make_fake_validator(tmp_path / "fake_validator.py", status="PASS")

    result = run_control_plane(
        goal_text="Build a forex paper-only replay harness.",
        validator_script=validator_script,
        loop_script=loop_script,
        packet_runner_script=packet_runner_script,
        report_dir=report_dir,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout.strip())
    assert payload["status"] in {"READY_FOR_CODEX", "PROTECTED_ACTION_REQUIRED"}
    assert payload["workflow"] == "goal"
    assert payload["packet_path"] == str(packet_path.resolve())
    assert Path(payload["report_path"]).exists()
    assert Path(payload["evidence_path"]).exists()
    assert payload["packet_runner"]["status"] == "PASS"
    assert payload["validator"]["status"] == "PASS"
    assert packet_path.exists()


def test_control_plane_packet_path_and_validation_fail(tmp_path: Path) -> None:
    report_dir = tmp_path / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    packet_path = tmp_path / "bad_packet.md"
    packet_path.write_text(
        "CODEX-ONLY PROMPT\nAI_OS EXECUTION TOKEN: CONTROL_PLANE_BAD\nAI_OS BOOTSTRAP REQUIRED: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY\n",
        encoding="utf-8",
    )
    packet_runner_script = make_fake_packet_runner(tmp_path / "fake_runner_fail.ps1")
    validator_script = make_fake_validator(tmp_path / "fake_validator_fail.py", status="FAIL")
    loop_script = make_fake_loop_script(tmp_path / "fake_loop_unused.ps1", packet_path=tmp_path / "unused.md")

    result = run_control_plane(
        packet_path=packet_path,
        validator_script=validator_script,
        loop_script=loop_script,
        packet_runner_script=packet_runner_script,
        report_dir=report_dir,
    )

    assert result.returncode != 0
    payload = json.loads(result.stderr.strip() if result.stderr else "{}") if result.returncode != 0 and not result.stdout.strip() else json.loads(result.stdout.strip())
    # In current implementation, stdout may still be valid JSON on non-zero status.
    try:
        parsed = json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        parsed = json.loads(result.stderr.strip()) if result.stderr else {}
    assert parsed.get("status") == "VALIDATION_FAILED"
    assert parsed.get("validator", {}).get("status") == "FAILED"
