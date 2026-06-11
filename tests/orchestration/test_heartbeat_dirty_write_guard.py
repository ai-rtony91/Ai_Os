from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NIGHT_CYCLE = REPO_ROOT / "automation" / "orchestration" / "Invoke-AiOsNightCycle.ps1"
REPORT = REPO_ROOT / "Reports" / "autonomy_loop_closure" / "heartbeat_dirty_write_guard_after_first_fire.json"


def test_heartbeat_guard_report_json_contract() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))

    assert report["packet_id"] == "AIOS-HEARTBEAT-DIRTY-WRITE-GUARD-APPLY-V1"
    assert report["root_cause"]["owner"] == "automation/orchestration/Invoke-AiOsNightCycle.ps1"
    assert report["root_cause"]["tracked_dirty_file"] == "telemetry/runtime/runtime_heartbeat.json"
    assert report["fix_applied"]["strategy"] == "B"
    assert report["fix_applied"]["active_heartbeat_preserved_for_effective_apply"] is True
    assert report["fix_applied"]["observe_only_heartbeat_evidence_available"] is True
    assert report["fix_applied"]["telemetry_runtime_written_by_this_packet"] is False
    assert report["safety_confirmations"]["no_scheduler_query_by_codex"] is True
    assert report["safety_confirmations"]["no_aios_relay_nightly_run"] is True
    assert report["safety_confirmations"]["no_broker_or_live_trading"] is True


def test_heartbeat_guard_report_passes_python_json_tool() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "json.tool", str(REPORT)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_changed_night_cycle_powershell_parser_passes() -> None:
    parse_command = (
        "$tokens = $null; $errors = $null; "
        f"[System.Management.Automation.Language.Parser]::ParseFile('{NIGHT_CYCLE.as_posix()}', [ref]$tokens, [ref]$errors) | Out-Null; "
        "if ($errors.Count -gt 0) { $errors | ForEach-Object { $_.ToString() }; exit 1 }"
    )
    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", parse_command],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
