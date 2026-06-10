from __future__ import annotations

import json
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "automation/orchestration/autonomy_control_plane/Invoke-AiOsAutonomyControlPlane.DRY_RUN.ps1"


def test_control_plane_runs_self_build_observe_only_cycle(tmp_path: Path) -> None:
    evidence_path = tmp_path / "control_plane.evidence.json"
    report_path = tmp_path / "control_plane.report.md"
    self_build_root = tmp_path / "self_build_cycle"
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            "-SelfBuildObserveOnly",
            "-SelfBuildCycleOutputRoot",
            str(self_build_root),
            "-OutputEvidencePath",
            str(evidence_path),
            "-OutputReportPath",
            str(report_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["workflow"] == "self_build_observe_only"
    assert payload["latest_decision_label"]
    assert payload["mode"] == "DRY_RUN"
    assert payload["requires_human"] is True
    assert payload["safety_status"] == "SAFE_OBSERVE_ONLY"
    assert Path(payload["self_build_evidence_path"]).exists()
    assert Path(payload["self_build_report_path"]).exists()
    assert payload["emitted_actions"] == []

    blocked_text = json.dumps(payload["blocked_capabilities"]).lower()
    assert "secret" in blocked_text
    action_text = json.dumps(payload["emitted_actions"]).lower()
    for token in ("powershell", "merge", "apply", "broker", "live", "secret", "order"):
        assert token not in action_text
