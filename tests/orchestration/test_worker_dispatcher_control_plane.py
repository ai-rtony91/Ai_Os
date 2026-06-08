from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from automation.orchestration.dispatcher.control_plane import (
    build_dispatch_preview,
    sample_assignments,
    sample_registry,
    sample_task,
    validate_control_plane,
)


def test_valid_registry_passes() -> None:
    result = validate_control_plane(sample_registry(), sample_assignments(), REPO_ROOT)
    assert result["status"] == "PASS", result


def test_duplicate_worker_id_fails() -> None:
    registry = sample_registry()
    registry["workers"].append(dict(registry["workers"][0]))
    result = validate_control_plane(registry, sample_assignments(), REPO_ROOT)
    assert result["status"] == "FAIL"
    assert any(finding["code"] == "AIOS-DISPATCHER-DUPLICATE-WORKER" for finding in result["findings"])


def test_worker_authority_claim_blocks() -> None:
    registry = sample_registry()
    registry["workers"][1]["authority_level"] = "approval_authority"
    result = validate_control_plane(registry, sample_assignments(), REPO_ROOT)
    assert result["status"] == "BLOCKED"
    assert any(finding["code"] == "AIOS-DISPATCHER-AUTHORITY-CLAIM" for finding in result["findings"])


def test_two_workers_claim_same_lane_fails() -> None:
    assignments = sample_assignments()
    second = dict(assignments["assignments"][0])
    second["assigned_worker_id"] = "github_pr_checks_layer"
    assignments["assignments"].append(second)
    result = validate_control_plane(sample_registry(), assignments, REPO_ROOT)
    assert result["status"] == "FAIL"
    assert any(finding["code"] == "AIOS-DISPATCHER-LANE-COLLISION" for finding in result["findings"])


def test_stale_worker_apply_assignment_blocks() -> None:
    registry = sample_registry()
    registry["workers"][1]["default_status"] = "stale"
    result = validate_control_plane(registry, sample_assignments(), REPO_ROOT)
    assert result["status"] == "BLOCKED"
    assert any(finding["code"] == "AIOS-DISPATCHER-STALE-APPLY" for finding in result["findings"])


def test_unknown_worker_apply_assignment_blocks() -> None:
    registry = sample_registry()
    registry["workers"][1]["default_status"] = "unknown"
    result = validate_control_plane(registry, sample_assignments(), REPO_ROOT)
    assert result["status"] == "BLOCKED"
    assert any(finding["code"] == "AIOS-DISPATCHER-UNKNOWN-APPLY" for finding in result["findings"])


def test_scheduler_and_live_trading_lanes_are_blocked() -> None:
    assignments = sample_assignments()
    assignments["assignments"][0]["lane_id"] = "scheduler-live-trading-lane"
    assignments["assignments"][0]["lane_name"] = "scheduler live trading lane"
    result = validate_control_plane(sample_registry(), assignments, REPO_ROOT)
    assert result["status"] == "BLOCKED"
    assert any(finding["code"] == "AIOS-DISPATCHER-GATED-LANE-UNBLOCKED" for finding in result["findings"])


def test_protected_path_collision_fails() -> None:
    assignments = sample_assignments()
    second = dict(assignments["assignments"][0])
    second["lane_id"] = "worker-dispatcher-docs-collision"
    second["assigned_worker_id"] = "github_pr_checks_layer"
    second["protected_paths"] = ["docs/AI_OS/worker_dispatcher/overview.md"]
    assignments["assignments"].append(second)
    result = validate_control_plane(sample_registry(), assignments, REPO_ROOT)
    assert result["status"] == "FAIL"
    assert any(finding["code"] == "AIOS-DISPATCHER-PATH-COLLISION" for finding in result["findings"])


def test_dispatch_preview_non_executable_and_read_only() -> None:
    preview = build_dispatch_preview(sample_registry(), sample_assignments(), sample_task())
    assert preview["decision"] == "can_assign"
    assert preview["dispatch_packet"]["format"] == "DRAFT_ONLY_NON_EXECUTABLE"
    assert preview["dispatch_packet"]["contains_execution_token"] is False
    assert preview["dispatch_packet"]["apply_execution_approved"] is False


def test_dispatcher_validator_cli_sample_check() -> None:
    result = subprocess.run(
        [
            "python",
            "automation/validators/aios_worker_dispatcher_validator.py",
            "--sample-check",
            "--repo-root",
            ".",
            "--json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert '"status": "PASS"' in result.stdout
