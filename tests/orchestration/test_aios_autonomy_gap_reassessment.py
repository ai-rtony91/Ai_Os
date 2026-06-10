from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "autonomy_reports" / "aios_autonomy_gap_reassessment.py"
DOGFOOD_REPORT_PATH = REPO_ROOT / "Reports" / "human_gate" / "human_gate_packet_dogfood_report.json"
QUEUE_VIEW_PATH = REPO_ROOT / "Reports" / "runtime_queue" / "runtime_execution_queue_view.json"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _module():
    return _load(MODULE_PATH, "aios_autonomy_gap_reassessment_for_tests")


def _evidence(now: str = "2026-01-02T03:04:05Z") -> dict:
    mod = _module()
    loaded = mod.load_default_evidence(REPO_ROOT, now)
    return loaded


def test_module_imports_cleanly():
    mod = _module()
    assert mod.SCHEMA == "AIOS_AUTONOMY_GAP_REASSESSMENT.v1"
    assert mod.MODE == "REASSESSMENT_REPORT"
    assert mod.REASSESSMENT_TYPE == "autonomy_gap"


def test_reassessment_report_builds_from_current_repo_evidence(tmp_path):
    mod = _module()
    report = mod.build_autonomy_gap_reassessment_report(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "autonomy_gap",
        now="2026-01-02T03:04:05Z",
    )
    assert report["mode"] == "REASSESSMENT_REPORT"
    assert report["reassessment_type"] == "autonomy_gap"
    assert report["reassessment_status"] == "BLOCKED"
    assert "evidence_loaded" in report
    assert "evidence_missing" in report
    assert "top_blockers" in report
    assert "all_gaps" in report
    assert "blocker_rankings" in report
    assert "readiness_scorecard" in report
    assert "operator_burden_summary" in report
    assert "recommended_next_lanes" in report
    assert "not_ready_lanes" in report
    assert "operator_control_switch_readiness" in report
    assert "p2_enqueue_bridge_readiness" in report
    assert "live_execution_readiness" in report
    assert report["approval_granted"] is False
    assert report["execution_allowed"] is False
    assert report["dispatch_allowed"] is False
    assert report["queue_mutation_allowed"] is False
    assert report["telemetry_mutation_allowed"] is False
    assert report["scheduler_creation_allowed"] is False
    assert report["service_creation_allowed"] is False
    assert report["sos_allowed"] is False
    assert report["live_trading_allowed"] is False
    assert report["unsafe_autonomy_claim"] is False
    assert report["vacation_mode_complete"] is False


def test_reassessment_status_and_scorecard_reflect_current_blocked_evidence(tmp_path):
    mod = _module()
    report = mod.build_autonomy_gap_reassessment_report(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "autonomy_gap",
        now="2026-01-02T03:04:05Z",
    )
    scorecard = report["readiness_scorecard"]
    assert report["queue_validation_summary"]["queue_validation_status"] == "BLOCK"
    assert report["runtime_proof_gate_summary"]["final_verdict"] == "BLOCKED"
    assert report["human_gate_packet_summary"]["packet_status"] == "BLOCKED"
    assert scorecard["queue_validation_ready"]["status"] == "BLOCKED"
    assert scorecard["runtime_proof_gate_ready"]["status"] == "BLOCKED"
    assert scorecard["human_gate_packet_ready"]["status"] == "BLOCKED"
    assert scorecard["live_execution_ready"]["status"] == "BLOCKED"
    assert scorecard["scheduler_ready"]["status"] == "BLOCKED"
    assert scorecard["sos_ready"]["status"] == "BLOCKED"
    assert scorecard["vacation_mode_ready"]["status"] == "BLOCKED"
    assert scorecard["dogfood_runner_ready"]["status"] in {"READY", "ATTENTION"}
    assert scorecard["operator_control_switch_ready"]["status"] in {"ATTENTION", "BLOCKED"}
    assert report["reassessment_status"] == "BLOCKED"


def test_gap_ranking_prioritizes_queue_integrity_over_documentation_ambiguity(tmp_path):
    mod = _module()
    report = mod.build_autonomy_gap_reassessment_report(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "autonomy_gap",
        now="2026-01-02T03:04:05Z",
    )
    impacts = {gap["domain"]: gap["impact_score"] for gap in report["all_gaps"]}
    assert impacts["queue_integrity_gap"] > impacts["documentation_gap"]
    assert impacts["live_execution_gap"] > impacts["queue_integrity_gap"]
    assert report["blocker_rankings"][0]["impact_score"] >= report["blocker_rankings"][-1]["impact_score"]


def test_report_writes_json_and_markdown_and_mentions_safety(tmp_path):
    mod = _module()
    outdir = tmp_path / "Reports" / "autonomy_gap"
    report = mod.run_autonomy_gap_reassessment(
        repo_root=REPO_ROOT,
        output_dir=outdir,
        now="2026-01-02T03:04:05Z",
    )
    json_path = outdir / mod.REPORT_JSON_NAME
    md_path = outdir / mod.REPORT_MD_NAME
    assert json_path.exists()
    assert md_path.exists()
    assert report["report_paths"] == [str(json_path), str(md_path)]
    markdown = md_path.read_text(encoding="utf-8")
    assert "This reassessment does not approve execution." in markdown
    assert "top blocker" in markdown.lower()
    assert "recommended next lanes" in markdown.lower()
    assert "operator burden" in markdown.lower()


def test_validation_passes_for_safe_report_and_blocks_dangerous_tamper(tmp_path):
    mod = _module()
    report = mod.build_autonomy_gap_reassessment_report(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "autonomy_gap",
        now="2026-01-02T03:04:05Z",
    )
    assert mod.validate_autonomy_gap_reassessment_report(report)["status"] == "PASS"

    tampered = deepcopy(report)
    tampered["approval_granted"] = True
    tampered["live_execution_readiness"]["status"] = "READY"
    tampered["p2_enqueue_bridge_readiness"]["status"] = "READY"
    validation = mod.validate_autonomy_gap_reassessment_report(tampered)
    assert validation["status"] == "BLOCK"
    assert any("approval_granted" in blocker for blocker in validation["blockers"])
    assert any("live_execution_readiness" in blocker or "P2" in blocker for blocker in validation["blockers"])


@pytest.mark.parametrize(
    "field,value,needle",
    [
        ("reassessment_status", "COMPLETE", "forbidden"),
        ("safe_next_action", "", "safe_next_action"),
        ("stop_condition", "", "stop_condition"),
    ],
)
def test_validation_blocks_for_forbidden_status_and_empty_fields(tmp_path, field, value, needle):
    mod = _module()
    report = mod.build_autonomy_gap_reassessment_report(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "autonomy_gap",
        now="2026-01-02T03:04:05Z",
    )
    report[field] = value
    validation = mod.validate_autonomy_gap_reassessment_report(report)
    assert validation["status"] == "BLOCK"
    assert any(needle in blocker.lower() for blocker in validation["blockers"])


def test_reassessment_is_deterministic_and_cli_writes_reports(tmp_path, monkeypatch, capsys):
    mod = _module()
    outdir = tmp_path / "Reports" / "autonomy_gap"
    first = mod.build_autonomy_gap_reassessment_report(
        repo_root=REPO_ROOT,
        output_dir=outdir,
        now="2026-01-02T03:04:05Z",
    )
    second = mod.build_autonomy_gap_reassessment_report(
        repo_root=REPO_ROOT,
        output_dir=outdir,
        now="2026-01-02T03:04:05Z",
    )
    assert first["summary"] == second["summary"]
    assert first["readiness_scorecard"] == second["readiness_scorecard"]

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "aios_autonomy_gap_reassessment",
            "--repo-root",
            str(REPO_ROOT),
            "--output-dir",
            str(outdir),
            "--now",
            "2026-01-02T03:04:05Z",
        ],
    )
    rc = mod.main()
    captured = capsys.readouterr()
    assert rc == 0
    parsed = json.loads(captured.out)
    assert parsed["reassessment_status"] == report_status(second)
    assert (outdir / mod.REPORT_JSON_NAME).exists()
    assert (outdir / mod.REPORT_MD_NAME).exists()


def report_status(report: dict[str, Any]) -> str:
    return str(report.get("reassessment_status"))


def test_existing_dogfood_and_queue_evidence_files_are_present():
    assert DOGFOOD_REPORT_PATH.exists()
    assert QUEUE_VIEW_PATH.exists()


def test_summary_includes_core_fields(tmp_path):
    mod = _module()
    report = mod.build_autonomy_gap_reassessment_report(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "autonomy_gap",
        now="2026-01-02T03:04:05Z",
    )
    summary = mod.summarize_autonomy_gap_reassessment_report(report)
    assert summary["top_blocker"]
    assert summary["recommended_next_lane"]
    assert summary["queue_validation_ready"] in {"READY", "ATTENTION", "BLOCKED", "INVALID"}
    assert summary["runtime_proof_gate_ready"] in {"READY", "ATTENTION", "BLOCKED", "INVALID"}
    assert summary["human_gate_packet_ready"] in {"READY", "ATTENTION", "BLOCKED", "INVALID"}
    assert summary["live_execution_ready"] == "BLOCKED"
