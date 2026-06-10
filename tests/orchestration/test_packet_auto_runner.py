from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "automation" / "orchestration" / "packet_runner" / "Invoke-AiOsPacketAutoRunner.DRY_RUN.ps1"


def make_valid_packet(path: Path) -> str:
    path.write_text(
        """CODEX-ONLY PROMPT
AI_OS EXECUTION TOKEN: TEST_PACKET_AUTO_RUN
AI_OS BOOTSTRAP REQUIRED: OPERATOR_REVIEW_REQUIRED_BEFORE_APPLY
IDENTITY MARKER: AIOS-AUTO-RUNNER-TEST
SUPERVISOR IDENTITY: Codex East
PACKET ID: AIOS-AUTO-RUNNER-TEST
MODE: DRY_RUN
ZONE: packet_runner
WORKER IDENTITY: Codex East
LANE: AIOS_PACKET_AUTO_RUNNER
WORKTREE: C:\\Dev\\Ai.Os
BRANCH: main
ALLOWED PATHS:
- automation/orchestration/packet_runner/
AUTHORITY FILES:
Read first. Do not modify.
- AGENTS.md
FORBIDDEN PATHS:
- secrets/
- credentials/
- broker/
- live_trading/
APPROVAL AUTHORITY:
Anthony is approval authority.
MISSION: Validate packet auto-runner behavior.
PREFLIGHT:
- pwd
VALIDATOR CHAIN:
- python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-AUTO-RUNNER-TEST.md
STOP POINT:
Stop after packet creation and validation.
FINAL REPORT FORMAT:
SUMMARY:
FILE CREATED:
VALIDATION:
NEXT SAFE COMMAND:
STATUS:
""",
        encoding="utf-8",
    )
    return path.read_text(encoding="utf-8")


def run_auto_runner(packet_path: Path, output_path: Path, report_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-PacketPath",
            str(packet_path),
            "-OutputPath",
            str(output_path),
            "-ReportPath",
            str(report_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_auto_runner_generates_codable_output_and_report(tmp_path: Path) -> None:
    packet_path = tmp_path / "AIOS-AUTO-RUNNER-TEST.md"
    packet_text = make_valid_packet(packet_path)

    output_path = tmp_path / "AIOS-AUTO-RUNNER-TEST.full_packet.md"
    report_path = tmp_path / "AIOS-AUTO-RUNNER-TEST.report.json"
    result = run_auto_runner(packet_path, output_path, report_path)

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout.strip())

    assert payload["codex_ready_generated"] is True
    assert Path(payload["packet_output_path"]).resolve() == output_path.resolve()
    assert Path(payload["report_path"]).resolve() == report_path.resolve()

    assert output_path.read_text(encoding="utf-8") == packet_text
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["packet_path"] == str(packet_path.resolve())
    assert report["validator_status"] in {"PASS", "WARN", "FAIL"}


def test_auto_runner_requires_existing_packet_path(tmp_path: Path) -> None:
    output_path = tmp_path / "output.md"
    report_path = tmp_path / "report.json"
    result = run_auto_runner(tmp_path / "missing.md", output_path, report_path)

    assert result.returncode != 0
    assert "REVIEW_REQUIRED" in result.stderr
