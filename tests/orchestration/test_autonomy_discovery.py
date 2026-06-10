"""Tests for autonomy inventory discovery dry-run script."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "automation/orchestration/autonomy_discovery/Get-AiOsAutonomyInventory.DRY_RUN.ps1"


def run_inventory(repo_root: Path, *, output_path: Path | None = None) -> subprocess.CompletedProcess[str]:
    args = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(SCRIPT),
        "-RepoRoot",
        str(repo_root),
    ]
    if output_path is not None:
        args.extend(["-OutputPath", str(output_path)])

    return subprocess.run(
        args,
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )


def test_inventory_detects_expected_components_on_repo_fixture(tmp_path: Path) -> None:
    # Build a minimal fixture repo to validate structure detection, independent of
    # current local state.
    repo = tmp_path / "repo"
    packet_runner = repo / "automation/orchestration/packet_runner"
    autonomy_loop = repo / "automation/orchestration/autonomy_loop"
    coordination_spine = repo / "automation/orchestration/coordination_spine"
    validators = repo / "automation/validators"
    work_packets = repo / "automation/orchestration/work_packets/proposed"
    trading = repo / "automation/trading"
    dispatcher = repo / "automation/dispatcher"
    locks = repo / "automation/orchestration/locks"
    approval = repo / "automation/orchestration/approval_inbox"

    for folder in [packet_runner, autonomy_loop, coordination_spine, validators, work_packets, trading, dispatcher, locks, approval]:
        folder.mkdir(parents=True, exist_ok=True)

    (packet_runner / "Invoke-AiOsPacketAutoRunner.DRY_RUN.ps1").write_text("test", encoding="utf-8")
    (autonomy_loop / "Invoke-AiOsAutonomyLoop.DRY_RUN.ps1").write_text("test", encoding="utf-8")
    (coordination_spine / "Invoke-AiOsCoordinationSpine.DRY_RUN.ps1").write_text("test", encoding="utf-8")
    (validators / "aios_governance_validator.py").write_text("test", encoding="utf-8")
    (trading / "paper_completion_sweep.py").write_text("test", encoding="utf-8")
    (dispatcher / "control_plane.py").write_text("test", encoding="utf-8")
    (locks / "unified_lock_status.ps1").write_text("test", encoding="utf-8")
    (approval / "README.md").write_text("test", encoding="utf-8")

    # Optional packet folders that are not mandatory should still be detected as absent.
    (repo / "automation/orchestration/work_packets/active").mkdir(parents=True, exist_ok=True)

    output_path = tmp_path / "inventory.json"
    result = run_inventory(repo, output_path=output_path)

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.strip())

    assert payload["schema"] == "AIOS_AUTONOMY_INVENTORY_V1"
    assert payload["repo_root"] == str(repo.resolve())
    assert payload["components"]["packet_runner"]["exists"] is True
    assert payload["components"]["packet_runner"]["detection_count"] >= 1
    assert payload["components"]["autonomy_loop"]["exists"] is True
    assert payload["components"]["validators"]["exists"] is True
    assert payload["components"]["work_packets"]["folders"]["proposed"]["exists"] is True
    assert payload["components"]["dispatch"]["exists"] is True
    assert payload["components"]["approval"]["exists"] is True
    assert output_path.exists()
    saved_payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved_payload["schema"] == payload["schema"]
