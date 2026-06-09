from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "automation/orchestration/coordination_spine/Get-AiOsUnifiedQueueIndex.DRY_RUN.ps1"


def run_index(packet_root: Path) -> dict[str, object]:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-PacketRoot",
            str(packet_root),
            "-OutputJson",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def write_packet(root: Path, folder: str, filename: str, *, packet_id: str, status: str) -> None:
    folder_path = root / folder
    folder_path.mkdir(parents=True, exist_ok=True)
    payload = {
        "packet_id": packet_id,
        "title": f"{packet_id} title",
        "owner_lane": "lane",
        "assigned_worker": "",
        "repo": "Ai.Os",
        "branch": "main",
        "status": status,
    }
    (folder_path / filename).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_known_states_map_to_expected_buckets(tmp_path: Path) -> None:
    packet_root = tmp_path / "work_packets"
    cases = [
        ("active", "pending.json", "pending-packet", "PENDING", "QUEUED"),
        ("active", "assigned.json", "assigned-packet", "ASSIGNED", "RUNNING"),
        ("active", "validating.json", "validating-packet", "VALIDATING", "RUNNING"),
        ("blocked", "blocked.json", "blocked-packet", "BLOCKED", "BLOCKED"),
        ("active", "waiting_approval.json", "waiting-approval-packet", "WAITING_APPROVAL", "WAITING_APPROVAL"),
        ("complete", "complete.json", "complete-packet", "COMPLETE", "COMPLETE"),
        ("blocked", "failed.json", "failed-packet", "FAILED", "FAILED"),
        ("complete", "archived.json", "archived-packet", "ARCHIVED", "ARCHIVED"),
        ("active", "unknown.json", "unknown-packet", "mystery_state", None),
    ]

    for folder, filename, packet_id, status, _ in cases:
        write_packet(packet_root, folder, filename, packet_id=packet_id, status=status)

    payload = run_index(packet_root)

    assert payload["schema"] == "AIOS_UNIFIED_QUEUE_INDEX.v1"
    assert payload["mode"] == "DRY_RUN"
    assert payload["packet_count"] == len(cases)
    assert payload["normalized_state_counts"] == {
        "QUEUED": 1,
        "RUNNING": 2,
        "BLOCKED": 1,
        "WAITING_APPROVAL": 1,
        "COMPLETE": 1,
        "FAILED": 1,
        "ARCHIVED": 1,
    }

    records = {record["packet_id"]: record for record in payload["records"]}
    for _, _, packet_id, _, expected in cases:
        record = records[packet_id]
        assert record["normalized_state"] == expected

    assert "MYSTERY_STATE" in payload["unmapped_states"]
    assert records["unknown-packet"]["normalized_state"] is None


def test_script_uses_atomic_write_helpers() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "WriteAllText" in text
    assert "Move-Item -LiteralPath $tempPath -Destination $destinationFull -Force" in text
    assert "New-Item -ItemType Directory -Path $destinationDir -Force" in text
