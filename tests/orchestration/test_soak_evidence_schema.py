from __future__ import annotations

import json
import subprocess

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "automation/validators/aios_soak_evidence_validator.py"
EXAMPLE = REPO_ROOT / "Reports/endurance_soak/soak_evidence_report.example.json"


def test_evidence_example_exists() -> None:
    assert EXAMPLE.exists()


def test_validator_exists() -> None:
    assert VALIDATOR.exists()


def test_example_evidence_passes_validator() -> None:
    result = subprocess.run(
        [
            "python",
            str(VALIDATOR),
            "--sample-check",
            "--json",
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
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
    assert "status_summary" in evidence or "status" in evidence


def test_example_evidence_has_reasons_and_forbidden_confirmations() -> None:
    evidence = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    assert isinstance(evidence.get("reasons"), list)
    assert evidence.get("forbidden_actions_confirmed")
    assert isinstance(evidence["forbidden_actions_confirmed"], dict)
    assert "scheduler_registration" in evidence["forbidden_actions_confirmed"]
    assert "worker_launch" in evidence["forbidden_actions_confirmed"]
    assert "outbound_notification" in evidence["forbidden_actions_confirmed"]
