from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "automation" / "orchestration" / "coordination_spine" / "Update-AiOsRuntimeHeartbeat.DRY_RUN.ps1"


def test_dry_run_does_not_write_when_apply_missing() -> None:
    target = REPO_ROOT / "telemetry" / "runtime" / "runtime_heartbeat.json"
    original = target.read_text(encoding="utf-8")
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT), "-HeartbeatPath", str(target)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert target.read_text(encoding="utf-8") == original


def test_apply_updates_heartbeat_status_and_supervisor_status(tmp_path: Path) -> None:
    heartbeat = tmp_path / "runtime_heartbeat.json"
    heartbeat.write_text(
        json.dumps(
            {
                "heartbeatAt": "2026-06-01T15:50:46Z",
                "last_beat": "2026-06-01T15:50:46Z",
                "status": "degraded",
                "supervisor_status": "WARNING",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-Apply",
            "-HeartbeatPath",
            str(heartbeat),
            "-OutputPath",
            str(heartbeat),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    updated = json.loads(heartbeat.read_text(encoding="utf-8"))
    assert updated["status"] == "OK"
    assert updated["supervisor_status"] == "OK"

    parsed = datetime.strptime(updated["heartbeatAt"], "%Y-%m-%dT%H:%M:%SZ")
    assert parsed.tzinfo is None

    assert "atomic_write" in result.stdout
