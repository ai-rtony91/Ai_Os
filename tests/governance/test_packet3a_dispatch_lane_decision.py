from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ADR = REPO_ROOT / "docs" / "architecture" / "AIOS_CANONICAL_LOOP_DECISION.md"


def adr_text() -> str:
    return ADR.read_text(encoding="utf-8")


def test_canonical_t2a_lane_is_powershell_python_orchestration() -> None:
    text = adr_text()

    assert "canonical T2A dispatch lane is the PowerShell/Python orchestration lane" in text
    assert "automation/orchestration/dispatcher/assignment_executor.py" in text
    assert "automation/orchestration/dispatcher/control_plane.py" in text


def test_worker_heartbeat_writer_role_is_limited() -> None:
    text = adr_text()

    assert "automation/dispatcher/runtime/workers/Update-AIOSWorkerHeartbeat.ps1" in text
    assert "worker heartbeat/state writer only" in text
    assert "does not assign packets" in text
    assert "does not launch workers" in text


def test_assignment_packet_lane_is_excluded_for_packet3b() -> None:
    text = adr_text()

    assert "automation/dispatcher/runtime/packets/Assign-AIOSPacket.ps1" in text
    assert "excluded from T2A" in text
    assert "Packet 3B" in text


def test_typescript_lane_remains_shelved_and_excluded_from_t2a() -> None:
    text = adr_text()

    assert "services/runtime/" in text
    assert "services/dispatcher/" in text
    assert "shelved/excluded from T2A" in text


def test_no_runtime_launch_or_protected_behavior_is_authorized() -> None:
    text = adr_text()

    assert "No worker launch is authorized" in text
    assert "No scheduler, Night Supervisor, SOS, ADB, broker/live trading, webhook, secrets, or .github/CI behavior is authorized" in text
    assert "Packet 3B, Packet 3C, Packet 3D, and Packet 3E remain separate" in text
