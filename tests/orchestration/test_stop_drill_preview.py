from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_stop_drill_preview.py"


def _load():
    spec = importlib.util.spec_from_file_location("aios_stop_drill_preview_test", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_stop_drill_preview_is_human_gated_without_execution():
    mod = _load()
    report = mod.build_stop_drill_preview(now="2026-06-11T12:00:00Z")

    assert report["status"] == "HUMAN_GATE_REQUIRED"
    assert report["proof_status"] == "HUMAN_GATE_REQUIRED"
    assert report["stop_drill_pass"] is False
    assert report["stop_drill_human_confirmation_required"] is True
    assert report["manual_step_required"]
    assert report["stop_executed"] is False
    assert report["kill_processes_allowed"] is False
    assert report["runtime_mutation_allowed"] is False
    assert report["runtime_execution_allowed"] is False
    assert report["runtime_launch_allowed"] is False
    assert report["scheduler_creation_allowed"] is False
    assert report["notification_send_allowed"] is False
    assert report["sos_notification_allowed"] is False
    assert report["sos_allowed"] is False
    assert report["protected_mutation_detected"] is False
    assert (
        report["safe_next_action"]
        == "Anthony must confirm STOP drill in a separately approved human-gated packet before runtime readiness can advance."
    )
    assert mod.validate_stop_drill_preview(report)["status"] == "PASS"


def test_stop_drill_preview_can_be_reviewable_with_explicit_human_confirmation():
    mod = _load()
    report = mod.build_stop_drill_preview(
        now="2026-06-11T12:00:00Z",
        explicit_human_confirmation={
            "explicit_human_provided_evidence": True,
            "stop_drill_confirmed": True,
        },
    )

    assert report["status"] == "REVIEWABLE"
    assert report["stop_drill_pass"] is True
    assert report["stop_drill_reviewable"] is True
    assert report["stop_drill_human_confirmation_required"] is False
    assert report["stop_executed"] is False
    assert report["runtime_execution_allowed"] is False
    assert mod.validate_stop_drill_preview(report)["status"] == "PASS"


def test_stop_drill_preview_writes_json_and_markdown(tmp_path):
    mod = _load()
    report = mod.run_stop_drill_preview(
        repo_root=tmp_path,
        output_dir=tmp_path / "Reports" / "stop_drill_preview",
        now="2026-06-11T12:00:00Z",
    )

    json_path = tmp_path / "Reports" / "stop_drill_preview" / "stop_drill_preview.json"
    md_path = tmp_path / "Reports" / "stop_drill_preview" / "stop_drill_preview.md"
    loaded = json.loads(json_path.read_text(encoding="utf-8"))

    assert json_path.exists()
    assert md_path.exists()
    assert loaded["status"] == report["status"]
    assert loaded["validation"]["status"] == "PASS"
    assert "STOP Drill Preview" in md_path.read_text(encoding="utf-8")
