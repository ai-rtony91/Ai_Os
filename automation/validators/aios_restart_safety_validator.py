from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from automation.orchestration.restart_safety.aios_restart_safety import (
    atomic_write_json,
    classify_marker,
    classify_marker_file,
)


def _marker(**updates):
    payload = {
        "cycle_id": "cycle-001",
        "cycle_in_progress": True,
        "phase_state": "STARTED",
        "phases": [{"name": "hygiene"}, {"name": "clear-stale-approvals"}, {"name": "relay-runner"}],
        "completed_phases": [],
    }
    payload.update(updates)
    return payload


def _source_checks(repo_root: Path) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, evidence: object) -> None:
        checks.append({"name": name, "passed": passed, "evidence": evidence})

    night_cycle_path = repo_root / "automation" / "orchestration" / "Invoke-AiOsNightCycle.ps1"
    runtime_state_path = repo_root / "automation" / "runtime" / "state" / "Write-AiOsRuntimeState.ps1"
    try:
        night_cycle = night_cycle_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        night_cycle = night_cycle_path.read_text(encoding="utf-8-sig")
    try:
        runtime_state = runtime_state_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        runtime_state = runtime_state_path.read_text(encoding="utf-8-sig")

    add("night_cycle_has_restart_resolver", "Resolve-AiOsCrashRecovery" in night_cycle, night_cycle_path.as_posix())
    add("corrupt_marker_fails_closed", "BLOCKED_RESTART_MARKER_CORRUPT" in night_cycle, night_cycle_path.as_posix())
    add("stale_marker_fails_closed", "BLOCKED_RESTART_MARKER_STALE" in night_cycle, night_cycle_path.as_posix())
    add(
        "waiting_approval_fails_closed",
        "BLOCKED_RESTART_WAITING_FOR_APPROVAL" in night_cycle,
        night_cycle_path.as_posix(),
    )
    add("completed_phases_drive_resume", "completed_phases" in night_cycle and "resume_from" in night_cycle, night_cycle_path.as_posix())
    add("runtime_state_uses_temp_write", ".tmp" in runtime_state and "Move-Item" in runtime_state, runtime_state_path.as_posix())
    return checks


def validate(repo_root: Path | None = None) -> dict[str, object]:
    repo_root = repo_root or Path.cwd()
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, evidence: object) -> None:
        checks.append({"name": name, "passed": passed, "evidence": evidence})

    missing = classify_marker(None, marker_exists=False)
    add("missing_marker_dry_run_only", missing.status == "NO_PRIOR_MARKER_SAFE_DRY_RUN_ONLY" and missing.safe_to_start_new_dry_run, missing.to_dict())

    complete = classify_marker(_marker(cycle_in_progress=False, completed_phases=["hygiene"]), marker_exists=True)
    add("completed_marker_no_replay", complete.status == "LAST_CYCLE_COMPLETE_NOTHING_TO_RESUME" and complete.resume_from is None, complete.to_dict())

    apply_done = classify_marker(_marker(completed_phases=["hygiene", "clear-stale-approvals"]), marker_exists=True)
    add(
        "completed_apply_phase_not_replayed",
        apply_done.status == "RESUME_FROM_FIRST_INCOMPLETE_PHASE"
        and apply_done.resume_from == "relay-runner"
        and "clear-stale-approvals" in apply_done.completed_apply_phases,
        apply_done.to_dict(),
    )

    corrupt = classify_marker(None, marker_exists=True, marker_corrupt=True)
    add("corrupt_marker_blocks", corrupt.status == "BLOCKED_RESTART_MARKER_CORRUPT" and not corrupt.safe_to_start_new_dry_run, corrupt.to_dict())

    stale = classify_marker(_marker(completed_phases=["hygiene"]), marker_exists=True, stale=True)
    add("stale_marker_blocks", stale.status == "STALE_RUNNING_MARKER_REQUIRES_OPERATOR", stale.to_dict())

    waiting = classify_marker(_marker(phase_state="WAITING_FOR_APPROVAL"), marker_exists=True)
    add("waiting_approval_blocks", waiting.status == "WAITING_FOR_OPERATOR_APPROVAL", waiting.to_dict())

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / "state.json"
        atomic_write_json(tmp_path, {"ok": True})
        add("atomic_write_json_success", json.loads(tmp_path.read_text(encoding="utf-8")) == {"ok": True}, tmp_path.as_posix())
        corrupt_path = Path(tmp) / "corrupt.json"
        corrupt_path.write_text("{bad", encoding="utf-8")
        file_decision = classify_marker_file(corrupt_path)
        add("malformed_json_file_blocks", file_decision.status == "BLOCKED_RESTART_MARKER_CORRUPT", file_decision.to_dict())

    checks.extend(_source_checks(repo_root))

    status = "PASS" if all(check["passed"] for check in checks) else "FAIL"
    return {
        "validator": "aios_restart_safety_validator",
        "status": status,
        "scheduler_allowed": False,
        "live_sos_allowed": False,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate AI_OS Tier 1 restart-safety rules.")
    parser.add_argument("--sample-check", action="store_true")
    parser.add_argument("--repo-root", default=".", help="Repository root to inspect for restart-safety source wiring.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.sample_check:
        payload = {"status": "BLOCKED", "reason": "--sample-check required"}
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2
    payload = validate(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"{payload['validator']}: {payload['status']}")
        for check in payload["checks"]:
            if not check["passed"]:
                print(f"FAIL: {check['name']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
