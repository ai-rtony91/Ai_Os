from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOAK_DIR = REPO_ROOT / "automation" / "orchestration" / "soak"
INVOKE_SCRIPT = SOAK_DIR / "Invoke-AiOsSoakHarness.DRY_RUN.ps1"
GET_SAMPLE_SCRIPT = SOAK_DIR / "Get-AiOsSoakSamples.DRY_RUN.ps1"
NEW_REPORT_SCRIPT = SOAK_DIR / "New-AiOsSoakEvidenceReport.DRY_RUN.ps1"


def _read(script: Path) -> str:
    return script.read_text(encoding="utf-8").lower()


def test_harness_scripts_exist() -> None:
    assert INVOKE_SCRIPT.exists()
    assert GET_SAMPLE_SCRIPT.exists()
    assert NEW_REPORT_SCRIPT.exists()


def test_harness_scripts_use_dry_run_suffix() -> None:
    assert INVOKE_SCRIPT.name.endswith(".DRY_RUN.ps1")
    assert GET_SAMPLE_SCRIPT.name.endswith(".DRY_RUN.ps1")
    assert NEW_REPORT_SCRIPT.name.endswith(".DRY_RUN.ps1")


def test_harness_enforces_maxcycles_guard() -> None:
    text = _read(INVOKE_SCRIPT)
    assert "maxcycles -gt 1" in text
    assert "soak_dry_run_scope_blocked" in text


def test_harness_enforces_min_interval_guard() -> None:
    text = _read(INVOKE_SCRIPT)
    assert "intervalseconds -lt 30" in text


def test_harness_enforces_run_timeout_guard() -> None:
    text = _read(INVOKE_SCRIPT)
    assert "runtimeoutseconds -lt 1" in text


def test_harness_checks_stop_markers() -> None:
    text = _read(INVOKE_SCRIPT)
    assert "control/self_continuation/stop" in text
    assert "relay/stop.flag" in text


def test_harness_does_not_register_scheduler() -> None:
    text = _read(INVOKE_SCRIPT)
    assert "scheduler" not in text or all(token not in text for token in ["start-aischeduler", "invoke-aischeduler", "register-scheduler", "scheduler registration"])


def test_harness_does_not_launch_workers() -> None:
    text = _read(INVOKE_SCRIPT)
    assert "start-aiosworker" not in text
    assert "worker loop" not in text
    assert "launch" not in text or "run_launcher" not in text


def test_harness_does_not_send_outbound_notifications() -> None:
    text = _read(INVOKE_SCRIPT)
    assert "sendmail" not in text
    assert "telegram" not in text
    assert "invoke-webrequest" not in text
    assert "restmethod" not in text


def test_harness_does_not_mutate_marker_or_runtime_files() -> None:
    text = _read(INVOKE_SCRIPT)
    assert "control/cycle/last_marker.json" not in text
    assert "telemetry/runtime/runtime_heartbeat.json" not in text


def test_harness_writes_only_to_soak_report_roots() -> None:
    text = _read(INVOKE_SCRIPT)
    assert "telemetry/soak" in text
    assert "reports/endurance_soak" in text
    assert "telemetry/runtime" not in text
    assert "control/cycle/last_marker.json" not in text
    assert re.search(r"join-path .*soak_run_.*\.json", text) is not None
