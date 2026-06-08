from __future__ import annotations

import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NIGHT_CYCLE = REPO_ROOT / "automation" / "orchestration" / "Invoke-AiOsNightCycle.ps1"
WATCHDOG = REPO_ROOT / "automation" / "orchestration" / "watchdog" / "aios_deadman_watchdog.py"
RUNTIME_STATE = REPO_ROOT / "automation" / "runtime" / "state" / "Write-AiOsRuntimeState.ps1"
HEARTBEAT_PROOF = REPO_ROOT / "automation" / "orchestration" / "Test-AiOsRuntimeHeartbeat.DRY_RUN.ps1"


def night_cycle_text() -> str:
    return NIGHT_CYCLE.read_text(encoding="utf-8")


def load_watchdog_module():
    spec = importlib.util.spec_from_file_location("aios_deadman_watchdog", WATCHDOG)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_night_cycle_emits_runtime_heartbeat_schema() -> None:
    text = night_cycle_text()

    assert "telemetry\\runtime\\runtime_heartbeat.json" in text
    assert "function Write-AiOsRuntimeHeartbeat" in text
    assert 'Write-AiOsRuntimeHeartbeat -Phase "cycle" -State "STARTED"' in text
    assert '$heartbeatPhase = if ([string]::IsNullOrWhiteSpace($Phase) -and $State -eq "CYCLE_COMPLETE") { "cycle" } else { $Phase }' in text
    for field in (
        "heartbeatAt",
        "last_beat",
        "cycle_id",
        "phase_name",
        "pid",
        "mode",
        "effective_apply",
        "observe_only",
        "updated_at_utc",
    ):
        assert field in text


def test_night_cycle_uses_collision_safe_atomic_temp_writes() -> None:
    text = night_cycle_text()

    assert "function Write-AiOsJsonAtomic" in text
    assert '[guid]::NewGuid().ToString("N")' in text
    assert "Move-Item -LiteralPath $tmpPath -Destination $Path -Force" in text
    assert '$cycleMarkerPath + ".tmp"' not in text


def test_runtime_state_writer_uses_collision_safe_temp_path() -> None:
    text = RUNTIME_STATE.read_text(encoding="utf-8")

    assert '[guid]::NewGuid().ToString("N")' in text
    assert "$tmpStatePath = Join-Path $stateDir" in text
    assert '$statePath + ".tmp"' not in text


def test_heartbeat_only_proof_harness_is_dry_run_and_isolated() -> None:
    text = HEARTBEAT_PROOF.read_text(encoding="utf-8")

    assert "runtime_heartbeat.proof.json" in text
    assert "DRY_RUN_PROOF" in text
    assert "full_night_cycle_invoked = $false" in text
    assert "scheduler_registered = $false" in text
    assert "restart_supervisor_armed = $false" in text
    assert "live_send_attempted = $false" in text
    assert "Write-AiOsProofJsonAtomic" in text
    assert '[guid]::NewGuid().ToString("N")' in text
    assert "Move-Item -LiteralPath $tmpPath -Destination $Path -Force" in text
    assert "& $PSScriptRoot" not in text
    assert "automation/orchestration/Invoke-AiOsNightCycle.ps1" not in text


def test_restart_marker_corruption_approval_wait_and_stale_state_block() -> None:
    text = night_cycle_text()

    assert "Read-CycleMarker -FailClosed" in text
    assert "cycle_marker_unreadable_or_malformed" in text
    assert "approval_wait_state_detected" in text
    assert "WAITING_FOR_APPROVAL|WAITING_APPROVAL|awaiting_approval|pending_approval" in text
    assert "RestartMarkerMaxAgeSeconds" in text
    assert "cycle_marker_stale" in text
    assert "approval_sensitive_resume_phase" in text


def test_safe_crash_recovery_preserves_cycle_id() -> None:
    text = night_cycle_text()

    assert "$script:AiOsCycleId = [string]$recoverMarker.cycle_id" in text
    assert "CRASH_RECOVERY resume_from={0} cycle_id={1}" in text


def test_watchdog_blocks_missing_and_stale_heartbeat(tmp_path: Path) -> None:
    watchdog = load_watchdog_module()
    now = datetime(2026, 6, 8, 12, 0, 0, tzinfo=timezone.utc)
    missing = watchdog.evaluate(tmp_path / "missing.json", threshold_seconds=600, now=now)

    assert missing["status"] == "BLOCKED"
    assert missing["reason"] == "heartbeat_file_missing"

    heartbeat = tmp_path / "runtime_heartbeat.json"
    heartbeat.write_text(
        '{"heartbeatAt":"2026-06-08T11:00:00Z","last_beat":"2026-06-08T11:00:00Z"}\n',
        encoding="utf-8",
    )
    stale = watchdog.evaluate(heartbeat, threshold_seconds=600, now=now)

    assert stale["status"] == "BLOCKED"
    assert stale["reason"] == "heartbeat_stale"


def test_watchdog_accepts_fresh_heartbeat(tmp_path: Path) -> None:
    watchdog = load_watchdog_module()
    now = datetime(2026, 6, 8, 12, 0, 0, tzinfo=timezone.utc)
    fresh_time = (now - timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    heartbeat = tmp_path / "runtime_heartbeat.json"
    heartbeat.write_text(
        f'{{"heartbeatAt":"{fresh_time}","last_beat":"{fresh_time}"}}\n',
        encoding="utf-8",
    )

    result = watchdog.evaluate(heartbeat, threshold_seconds=600, now=now)

    assert result["status"] == "OK"
    assert result["reason"] == "heartbeat_fresh"
