from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_stop_report_resume.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_stop_report_resume", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_imports_and_summary_schema():
    module = load_module()
    report = module.build_stop_report_resume(
        {
            "run_id": "RUN-1",
            "result": "REVIEW_REQUIRED",
            "completed_steps": ["validate"],
            "failed_steps": [],
            "validators_run": [{"name": "pytest", "passed": True, "returncode": 0}],
        }
    )
    assert report["schema"] == "AIOS_STOP_REPORT_RESUME.v1"
    assert report["run_id"] == "RUN-1"
    assert report["validators_summary"]["passed_count"] == 1
    assert report["resume_ready"] is True
    assert report["files_written"] is False
    assert "Reports/aios_self_build" in report["output_paths_preview"]["stop_report"]


def test_failed_validator_not_resume_ready():
    module = load_module()
    report = module.build_stop_report_resume(
        {
            "run_id": "RUN-2",
            "result": "failed",
            "blocked_reason": "validator_failed",
            "validators_run": [{"name": "pytest", "passed": False, "returncode": 1}],
        }
    )
    assert report["validators_summary"]["failed_count"] == 1
    assert report["resume_ready"] is False
    assert "validator_failed" in report["morning_summary"]


def test_no_file_write_usage():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in [".write_text", "open(", "subprocess", "requests", "socket", "urllib"]:
        assert forbidden not in source
