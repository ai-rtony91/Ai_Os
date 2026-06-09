from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "automation" / "dispatcher" / "runtime" / "workers" / "Update-AIOSWorkerHeartbeat.ps1"


def script_text() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def write_worker_state(root: Path) -> None:
    root.mkdir(parents=True)
    active_worker = {
        "generated_at": "2026-06-08T00:00:00Z",
        "workers": [
            {
                "worker_id": "AIOS-01",
                "current_state": "IDLE",
                "heartbeat_time": "2026-06-08T00:00:00Z",
                "heartbeat_age_seconds": 0,
                "launch_session_id": "SESSION-1",
                "approval_state": "PENDING",
                "next_safe_action": "Wait.",
            }
        ],
    }
    heartbeat = {
        "generated_at": "2026-06-08T00:00:00Z",
        "heartbeats": [
            {
                "worker_id": "AIOS-01",
                "current_state": "IDLE",
                "heartbeat_time": "2026-06-08T00:00:00Z",
                "heartbeat_age_seconds": 0,
                "stale_status": "CURRENT",
                "launch_session_id": "SESSION-1",
                "next_safe_action": "Wait.",
            }
        ],
    }
    ledger = {"generated_at": "2026-06-08T00:00:00Z", "events": []}
    registrations = {
        "generated_at": "2026-06-08T00:00:00Z",
        "registrations": [
            {
                "worker_id": "AIOS-01",
                "registration_status": "REGISTERED",
                "registration_time": "2026-06-08T00:00:00Z",
                "duplicate_identity_status": "NOT_CHECKED",
                "launch_session_id": "SESSION-1",
                "next_safe_action": "Wait.",
            }
        ],
    }
    (root / "active_worker_table.json").write_text(json.dumps(active_worker), encoding="utf-8")
    (root / "worker_heartbeat_table.json").write_text(json.dumps(heartbeat), encoding="utf-8")
    (root / "worker_session_ledger.json").write_text(json.dumps(ledger), encoding="utf-8")
    (root / "worker_registration_status.json").write_text(json.dumps(registrations), encoding="utf-8")


def run_script(worker_state_root: Path, state: str = "DRY_RUN_STARTED") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-WorkerId",
            "AIOS-01",
            "-CurrentState",
            state,
            "-WorkerStateRoot",
            str(worker_state_root),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_worker_heartbeat_writer_uses_guid_same_directory_atomic_temp() -> None:
    text = script_text()

    assert '[guid]::NewGuid().ToString("N")' in text
    assert '$tmpPath = Join-Path $targetDir' in text
    assert "Move-Item -LiteralPath $tmpPath -Destination $Path -Force" in text


def test_temp_json_is_parsed_before_final_replace() -> None:
    text = script_text()

    parse_index = text.index("Get-Content -LiteralPath $tmpPath -Raw | ConvertFrom-Json")
    move_index = text.index("Move-Item -LiteralPath $tmpPath -Destination $Path -Force")
    assert parse_index < move_index


def test_direct_final_set_content_for_worker_state_writes_is_not_used() -> None:
    text = script_text()

    assert "Set-Content -LiteralPath $Path" not in text
    assert "Set-Content -LiteralPath $tmpPath" in text


def test_successful_update_uses_temp_fixture_and_leaves_no_partial_temp(tmp_path: Path) -> None:
    worker_state_root = tmp_path / "workers"
    write_worker_state(worker_state_root)

    result = run_script(worker_state_root)

    assert result.returncode == 0, result.stdout + result.stderr
    active = json.loads((worker_state_root / "active_worker_table.json").read_text(encoding="utf-8-sig"))
    heartbeat = json.loads((worker_state_root / "worker_heartbeat_table.json").read_text(encoding="utf-8-sig"))
    assert active["workers"][0]["current_state"] == "DRY_RUN_STARTED"
    assert heartbeat["heartbeats"][0]["current_state"] == "DRY_RUN_STARTED"
    assert not list(worker_state_root.glob("*.tmp"))


def test_missing_worker_state_file_fails_closed_without_autocreate(tmp_path: Path) -> None:
    worker_state_root = tmp_path / "workers"
    write_worker_state(worker_state_root)
    missing = worker_state_root / "worker_heartbeat_table.json"
    missing.unlink()

    result = run_script(worker_state_root)

    assert result.returncode != 0
    assert "REVIEW_REQUIRED: Missing required worker-state file" in result.stderr
    assert not missing.exists()


def test_malformed_worker_state_json_fails_closed_without_overwrite(tmp_path: Path) -> None:
    worker_state_root = tmp_path / "workers"
    write_worker_state(worker_state_root)
    malformed = worker_state_root / "active_worker_table.json"
    malformed.write_text("{", encoding="utf-8")

    result = run_script(worker_state_root)

    assert result.returncode != 0
    assert "REVIEW_REQUIRED: Malformed worker-state JSON" in result.stderr
    assert malformed.read_text(encoding="utf-8") == "{"


def test_no_auto_reassignment_or_stale_worker_auto_clear_behavior() -> None:
    text = script_text().lower()

    assert "reassign" not in text
    assert "auto-clear" not in text
    assert "clear-stale" not in text
    assert "stale_status = \"current\"" in text

