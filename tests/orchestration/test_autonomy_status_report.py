"""Tests for autonomy status report generation."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "automation/orchestration/autonomy_reports/New-AiOsAutonomyStatusReport.DRY_RUN.ps1"


def run_status_report(
    *,
    discovery_path: Path,
    control_path: Path,
    router_path: Path,
    channels_path: Path,
    report_root: Path,
) -> subprocess.CompletedProcess[str]:
    out_md = report_root / "status_report.md"
    out_json = report_root / "status_report.json"
    return subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-DiscoveryReportPath",
            str(discovery_path),
            "-ControlPlaneEvidencePath",
            str(control_path),
            "-RouterEvidencePath",
            str(router_path),
            "-WorkerChannelMapPath",
            str(channels_path),
            "-OutputMarkdownPath",
            str(out_md),
            "-OutputJsonPath",
            str(out_json),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_autonomy_status_report_ready_state(tmp_path: Path) -> None:
    report_root = tmp_path / "reports"
    report_root.mkdir(parents=True, exist_ok=True)
    discovery = tmp_path / "discovery.json"
    discovery.write_text(
        json.dumps(
            {
                "schema": "AIOS_AUTONOMY_INVENTORY_V1",
                "components": {
                    "trading": {"automation_exists": True},
                    "packet_runner": {"exists": True},
                    "autonomy_loop": {"exists": True},
                    "coordination_spine": {"exists": True},
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    control = tmp_path / "control.json"
    control.write_text(
        json.dumps(
            {
                "schema_version": "AIOS-AUTONOMY-CONTROL-PLANE-V1",
                "status": "READY_FOR_CODEX",
                "packet_path": "automation/orchestration/work_packets/proposed/dummy.md",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    router = tmp_path / "router.json"
    router.write_text(
        json.dumps(
            {
                "schema_version": "AIOS-AUTONOMY-NEXT-ACTION-V1",
                "next_action": "RUN_CODEX_WITH_PACKET",
                "safe_command": "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/packet_runner/Invoke-AiOsPacketAutoRunner.DRY_RUN.ps1",
                "blocked_by": [],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    channels = tmp_path / "channels.json"
    channels.write_text(
        json.dumps(
            {
                "schema_version": "AIOS-AUTONOMY-WORKER-CHANNEL-MAP-V1",
                "channels": [
                    {"name": "Codex CLI local", "command": "codex --help"},
                    {"name": "ChatGPT desktop/mobile supervisor", "command": "echo manual approval needed"},
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = run_status_report(
        discovery_path=discovery,
        control_path=control,
        router_path=router,
        channels_path=channels,
        report_root=report_root,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout.strip())
    assert payload["autonomy_readiness"] == "READY"
    assert payload["control_status"] == "READY_FOR_CODEX"
    assert payload["next_action"] == "RUN_CODEX_WITH_PACKET"
    assert payload["can_autonomously_do_next"]
    assert payload["forex_builder_readiness"]["status"] in {"READY", "PARTIAL"}

    md_path = report_root / "status_report.md"
    json_path = report_root / "status_report.json"
    assert md_path.exists()
    assert json_path.exists()

    md = md_path.read_text(encoding="utf-8")
    assert "AIOS Autonomy Status Report" in md
    assert "forex-build" in md


def test_autonomy_status_report_reports_blockers(tmp_path: Path) -> None:
    report_root = tmp_path / "reports2"
    report_root.mkdir(parents=True, exist_ok=True)
    control = tmp_path / "control.json"
    control.write_text(
        json.dumps(
            {
                "schema_version": "AIOS-AUTONOMY-CONTROL-PLINE-V1",
                "status": "PROTECTED_ACTION_REQUIRED",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = run_status_report(
        discovery_path=tmp_path / "missing_discovery.json",
        control_path=control,
        router_path=tmp_path / "missing_router.json",
        channels_path=tmp_path / "missing_channels.json",
        report_root=report_root,
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout.strip())
    assert payload["autonomy_readiness"] == "BLOCKED"
    assert payload["control_status"] == "PROTECTED_ACTION_REQUIRED"
    assert payload["requires_anthony_approval"]
    assert payload["blockers_exist"] is True
