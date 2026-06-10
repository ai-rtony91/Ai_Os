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
    self_build_path: Path | None = None,
    approval_summary_script_path: Path | None = None,
    approval_inbox_path: Path | None = None,
    report_root: Path,
) -> subprocess.CompletedProcess[str]:
    out_md = report_root / "status_report.md"
    out_json = report_root / "status_report.json"
    command = [
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
        ]
    if self_build_path is not None:
        command.extend(["-SelfBuildEvidencePath", str(self_build_path)])
    if approval_summary_script_path is not None:
        command.extend(["-ApprovalSummaryScriptPath", str(approval_summary_script_path)])
    if approval_inbox_path is not None:
        command.extend(["-ApprovalInboxPath", str(approval_inbox_path)])
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_approval_item(root: Path, name: str, status: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / name).write_text(
        json.dumps(
            {
                "approval_status": status,
                "packet_id": f"packet-{name}",
                "requested_action": "REVIEW_ONLY",
                "risk_level": "low",
            }
        ),
        encoding="utf-8",
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
    self_build = tmp_path / "self_build.evidence.json"
    self_build.write_text(
        json.dumps(
            {
                "schema": "AIOS_SELF_BUILD_CYCLE.v1",
                "cycle_id": "sbc-status-test",
                "generated_at": "2026-06-10T00:00:00Z",
                "mode": "DRY_RUN",
                "executed": False,
                "safety_status": "SAFE",
                "requires_human": False,
                "decision": {"action": "REPORT", "reason": "ready for report"},
                "evidence_bundle": {
                    "runtime": {"runtime_gate": "READY_TO_REPORT"},
                    "completion": {"verdict": "COMPLETION_VERIFIED"},
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    approval_inbox = tmp_path / "approval_inbox"
    approval_inbox.mkdir()

    result = run_status_report(
        discovery_path=discovery,
        control_path=control,
        router_path=router,
        channels_path=channels,
        self_build_path=self_build,
        approval_inbox_path=approval_inbox,
        report_root=report_root,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout.strip())
    assert payload["autonomy_readiness"] == "READY"
    assert payload["control_status"] == "READY_FOR_CODEX"
    assert payload["next_action"] == "RUN_CODEX_WITH_PACKET"
    assert payload["can_autonomously_do_next"]
    assert payload["forex_builder_readiness"]["status"] in {"READY", "PARTIAL"}
    assert payload["self_build_decision"]["normalized_status"] == "REPORT_READY"
    assert payload["self_build_decision"]["operator_route"] == "REPORT_ONLY"
    assert payload["self_build_decision"]["approval_required"] is False
    assert "no action is approved" in payload["self_build_decision"]["safe_next_action"]
    assert payload["self_build_decision_available"] is True
    assert payload["self_build_decision_status"] == "REPORT_READY"
    assert payload["self_build_operator_route"] == "REPORT_ONLY"
    assert payload["self_build_approval_required"] is False
    assert payload["self_build_report_only"] is True
    assert payload["self_build_source_cycle_id"] == "sbc-status-test"
    assert payload["approvals_performed"] == "NO"
    assert payload["approval_inbox_mutated"] == "NO"
    assert payload["apply_gate_mutated"] == "NO"
    assert payload["protected_action_allowed"] == "NO"
    assert payload["approval_summary_available"] is True
    assert payload["approval_pending_count"] == 0
    assert payload["approval_blocked_count"] == 0
    assert payload["approval_completed_count"] == 0
    assert payload["approval_safe_state"] == "PASS"

    md_path = report_root / "status_report.md"
    json_path = report_root / "status_report.json"
    assert md_path.exists()
    assert json_path.exists()

    md = md_path.read_text(encoding="utf-8")
    assert "AIOS Autonomy Status Report" in md
    assert "Self-build decision consumer" in md
    assert "Status: REPORT_READY" in md
    assert "Approval state summary" in md
    assert "Approval safety visibility" in md
    assert "forex-build" in md


def test_autonomy_status_report_surfaces_missing_self_build_evidence(tmp_path: Path) -> None:
    report_root = tmp_path / "reports3"
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
            }
        ),
        encoding="utf-8",
    )
    control = tmp_path / "control.json"
    control.write_text(json.dumps({"status": "READY_FOR_CODEX"}), encoding="utf-8")
    router = tmp_path / "router.json"
    router.write_text(json.dumps({"next_action": "RUN_CODEX_WITH_PACKET"}), encoding="utf-8")
    channels = tmp_path / "channels.json"
    channels.write_text(json.dumps({"channels": [{"name": "Codex CLI local"}]}), encoding="utf-8")

    result = run_status_report(
        discovery_path=discovery,
        control_path=control,
        router_path=router,
        channels_path=channels,
        self_build_path=tmp_path / "missing_self_build.evidence.json",
        report_root=report_root,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout.strip())
    assert payload["self_build_decision_status"] == "WAIT_FOR_EVIDENCE"
    assert payload["self_build_operator_route"] == "REPORT_ONLY"
    assert payload["self_build_approval_required"] is False
    assert payload["self_build_report_only"] is True
    assert payload["protected_action_allowed"] == "NO"


def test_autonomy_status_report_degrades_when_approval_summary_missing(tmp_path: Path) -> None:
    report_root = tmp_path / "reports4"
    report_root.mkdir(parents=True, exist_ok=True)
    discovery = tmp_path / "discovery.json"
    discovery.write_text(json.dumps({"components": {}}), encoding="utf-8")
    control = tmp_path / "control.json"
    control.write_text(json.dumps({"status": "READY_FOR_CODEX"}), encoding="utf-8")
    router = tmp_path / "router.json"
    router.write_text(json.dumps({"next_action": "RUN_CODEX_WITH_PACKET"}), encoding="utf-8")
    channels = tmp_path / "channels.json"
    channels.write_text(json.dumps({"channels": [{"name": "Codex CLI local"}]}), encoding="utf-8")

    result = run_status_report(
        discovery_path=discovery,
        control_path=control,
        router_path=router,
        channels_path=channels,
        approval_summary_script_path=tmp_path / "missing_approval_summary.ps1",
        report_root=report_root,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout.strip())
    assert payload["approval_summary_available"] is False
    assert payload["approval_pending_count"] == 0
    assert payload["approval_blocked_count"] == 0
    assert payload["approval_completed_count"] == 0
    assert payload["approval_safe_state"] == "UNAVAILABLE"
    assert payload["protected_action_allowed"] == "NO"


def test_autonomy_status_report_surfaces_pending_and_blocked_approvals(tmp_path: Path) -> None:
    report_root = tmp_path / "reports5"
    report_root.mkdir(parents=True, exist_ok=True)
    discovery = tmp_path / "discovery.json"
    discovery.write_text(json.dumps({"components": {}}), encoding="utf-8")
    control = tmp_path / "control.json"
    control.write_text(json.dumps({"status": "READY_FOR_CODEX"}), encoding="utf-8")
    router = tmp_path / "router.json"
    router.write_text(json.dumps({"next_action": "RUN_CODEX_WITH_PACKET"}), encoding="utf-8")
    channels = tmp_path / "channels.json"
    channels.write_text(json.dumps({"channels": [{"name": "Codex CLI local"}]}), encoding="utf-8")
    approval_inbox = tmp_path / "approval_inbox"
    write_approval_item(approval_inbox, "pending.json", "pending_review")
    write_approval_item(approval_inbox, "blocked.json", "blocked")

    result = run_status_report(
        discovery_path=discovery,
        control_path=control,
        router_path=router,
        channels_path=channels,
        approval_inbox_path=approval_inbox,
        report_root=report_root,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout.strip())
    assert payload["approval_summary_available"] is True
    assert payload["approval_pending_count"] == 1
    assert payload["approval_blocked_count"] == 1
    assert payload["approval_completed_count"] == 0
    assert payload["approval_safe_state"] == "BLOCKED"
    assert payload["approval_inbox_mutated"] == "NO"
    assert payload["apply_gate_mutated"] == "NO"
    assert payload["protected_action_allowed"] == "NO"


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
