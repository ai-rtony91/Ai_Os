from __future__ import annotations

import json
import subprocess

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "automation/validators/aios_soak_evidence_validator.py"
EXAMPLE = REPO_ROOT / "Reports/endurance_soak/soak_evidence_report.example.json"


def _run_validator(report_path: Path) -> dict[str, object]:
    result = subprocess.run(
        [
            "python",
            str(VALIDATOR),
            "--sample-check",
            "--json",
            "--report-path",
            str(report_path),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode in (0, 1), result.stdout + result.stderr
    return json.loads(result.stdout)


def test_evidence_example_exists() -> None:
    assert EXAMPLE.exists()


def test_validator_exists() -> None:
    assert VALIDATOR.exists()


def test_example_evidence_passes_validator() -> None:
    payload = _run_validator(EXAMPLE)
    assert payload["status"] == "PASS"
    assert payload["validator"] == "aios_soak_evidence_validator"


def test_example_evidence_includes_sample_list() -> None:
    evidence = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    assert isinstance(evidence.get("samples"), list)
    assert evidence["samples"], "Example evidence must include at least one sample."


def test_example_evidence_includes_resource_samples() -> None:
    evidence = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    sample = evidence["samples"][0]
    assert sample["disk_samples"]
    assert isinstance(sample["process_rss_mb"], (int, float))


def test_example_evidence_has_status_summary_or_transition() -> None:
    evidence = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    assert evidence.get("status") in {"PASS", "STOPPED", "FAILED", "BLOCKED"}
    assert "status_summary" in evidence
    assert set(evidence["status_summary"].keys()) == {"PASS", "STOPPED", "FAILED", "BLOCKED"}
    assert sum(int(v) for v in evidence["status_summary"].values()) == evidence["sample_count"]


def test_example_evidence_has_reasons_and_forbidden_confirmations() -> None:
    evidence = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    assert isinstance(evidence.get("reasons"), list)
    assert evidence.get("forbidden_actions_confirmed")
    assert isinstance(evidence["forbidden_actions_confirmed"], dict)
    assert "scheduler_registration" in evidence["forbidden_actions_confirmed"]
    assert "worker_launch" in evidence["forbidden_actions_confirmed"]
    assert "outbound_notification" in evidence["forbidden_actions_confirmed"]


def test_validator_rejects_missing_status_summary(tmp_path: Path) -> None:
    evidence = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    evidence.pop("status_summary", None)
    temp = tmp_path / "missing_status_summary.json"
    temp.write_text(json.dumps(evidence), encoding="utf-8")

    payload = _run_validator(temp)
    assert payload["status"] == "FAIL"
    assert any("status_summary" in failure for failure in payload["failures"])


def test_validator_rejects_sample_count_mismatch(tmp_path: Path) -> None:
    evidence = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    evidence["sample_count"] = 0
    temp = tmp_path / "bad_sample_count.json"
    temp.write_text(json.dumps(evidence), encoding="utf-8")

    payload = _run_validator(temp)
    assert payload["status"] == "FAIL"
    assert any("sample_count" in failure for failure in payload["failures"])


def test_validator_rejects_inconsistent_status_summary(tmp_path: Path) -> None:
    evidence = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    evidence["status_summary"]["PASS"] = 0
    evidence["status_summary"]["FAILED"] = 1
    temp = tmp_path / "bad_status_summary.json"
    temp.write_text(json.dumps(evidence), encoding="utf-8")

    payload = _run_validator(temp)
    assert payload["status"] == "FAIL"
    assert any("status_summary" in failure for failure in payload["failures"])
