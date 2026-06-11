from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "control_loop"
    / "aios_observe_spine_soak.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("aios_observe_spine_soak_test_module", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _ready_observe_report():
    return {
        "generated_at_utc": "2026-06-10T15:20:28Z",
        "observe_loop_status": "OBSERVE_LOOP_READY",
        "p2_bridge_status": "READY_FOR_DRY_RUN_PREVIEW",
        "queue_gate_status": "READY_FOR_HUMAN_REVIEW",
        "runtime_apply_status": "READY_FOR_RUNTIME_PREVIEW",
        "sos_status": "READY_FOR_SOS_PREVIEW",
        "scheduler_status": "READY_FOR_SCHEDULER_PREVIEW",
        "stale_layers": [],
        "real_blockers": [],
        "governance_blockers": [],
        "code_blockers": [],
        "mutation_projection": {
            "approval_inbox_mutation": False,
            "command_queue_mutation": False,
            "queue_mutation": False,
            "runtime_execution": False,
            "runtime_launch": False,
            "scheduler_registration": False,
            "sos_notification": False,
            "trading_execution": False,
            "worker_inbox_mutation": False,
        },
        "validate_mutation_boundaries": {
            "approval_inbox_mutation": False,
            "command_queue_mutation": False,
            "queue_mutation": False,
            "runtime_execution": False,
            "runtime_launch": False,
            "scheduler_registration": False,
            "sos_notification": False,
            "trading_execution": False,
            "worker_inbox_mutation": False,
        },
        "safe_next_action": "Continue observe-only loop checks with current evidence.",
    }


def _blocked_observe_report():
    report = _ready_observe_report()
    report.update(
        {
            "observe_loop_status": "OBSERVE_LOOP_BLOCKED",
            "p2_bridge_status": "BLOCKED",
            "runtime_apply_status": "BLOCKED",
            "real_blockers": ["runtime_apply_lane"],
            "governance_blockers": ["queue_mutation_gate"],
            "safe_next_action": "Resolve real/gateway blockers and rerun observe-spine runner.",
        }
    )
    return report


def test_7_cycle_soak_writes_only_final_closeout_reports_and_preserves_false_mutation_flags(tmp_path):
    mod = _load()
    calls: list[dict[str, object]] = []

    def fake_runner(**kwargs):
        calls.append(kwargs)
        return _blocked_observe_report()

    output_dir = tmp_path / "Reports" / "final_observe_spine_closure"
    report = mod.run_observe_spine_7_cycle_soak(
        repo_root=REPO_ROOT,
        output_dir=output_dir,
        now="2026-06-10T15:20:28Z",
        observe_runner=fake_runner,
    )

    assert len(calls) == 7
    assert report["cycle_count"] == 7
    assert report["final_status"] == mod.BLOCKED_WITH_REAL_REASON
    assert report["status"] == mod.BLOCKED_WITH_REAL_REASON
    assert report["stable_status"] is True
    assert report["mutation_flags_false_across_all_cycles"] is True
    assert report["stale_layers"] == []
    assert report["real_blockers"] == ["runtime_apply_lane"]
    assert report["governance_blockers"] == ["queue_mutation_gate"]
    assert report["required_human_decision"] == "Resolve: runtime_apply_lane, queue_mutation_gate."
    assert sorted(path.name for path in output_dir.iterdir()) == [
        mod.FINAL_JSON_NAME,
        mod.FINAL_MD_NAME,
        mod.REPORT_JSON_NAME,
        mod.REPORT_MD_NAME,
    ]
    all_files = sorted(
        str(path.relative_to(tmp_path).as_posix())
        for path in tmp_path.rglob("*")
        if path.is_file()
    )
    assert all_files == [
        "Reports/final_observe_spine_closure/final_closeout_status.json",
        "Reports/final_observe_spine_closure/final_closeout_status.md",
        "Reports/final_observe_spine_closure/observe_spine_7_cycle_soak.json",
        "Reports/final_observe_spine_closure/observe_spine_7_cycle_soak.md",
    ]

    final_json = output_dir / mod.FINAL_JSON_NAME
    loaded = json.loads(final_json.read_text(encoding="utf-8"))
    assert loaded["status"] == mod.BLOCKED_WITH_REAL_REASON
    assert loaded["real_blockers"] == ["runtime_apply_lane"]
    assert loaded["mutation_flags_false_across_all_cycles"] is True


def test_7_cycle_soak_can_classify_ready_for_next_phase(tmp_path):
    mod = _load()

    def fake_runner(**kwargs):
        return _ready_observe_report()

    output_dir = tmp_path / "Reports" / "final_observe_spine_closure"
    report = mod.run_observe_spine_7_cycle_soak(
        repo_root=REPO_ROOT,
        output_dir=output_dir,
        now="2026-06-10T15:20:28Z",
        observe_runner=fake_runner,
    )

    assert report["final_status"] == mod.READY_FOR_NEXT_PHASE
    assert report["status"] == mod.READY_FOR_NEXT_PHASE
    assert report["required_human_decision"] == "Anthony may approve the next real phase only after independently reviewing the final closeout evidence."
    assert report["real_blockers"] == []
    assert report["governance_blockers"] == []
    assert report["code_blockers"] == []
    assert report["mutation_flags_false_across_all_cycles"] is True
