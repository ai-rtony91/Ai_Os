from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "runtime_closure"
    / "aios_p2_enqueue_bridge.py"
)
QUEUE_GATE_PATH = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "work_packets"
    / "aios_queue_mutation_gate.py"
)
HUMAN_GATE_REPORT = REPO_ROOT / "Reports" / "human_gate" / "human_gate_packet_dogfood_report.json"
AUTONOMY_GAP_REPORT = REPO_ROOT / "Reports" / "autonomy_gap" / "autonomy_gap_reassessment_report.json"
COMMAND_QUEUE = REPO_ROOT / "automation" / "orchestration" / "command_queue" / "AIOS_COMMAND_QUEUE.json"
WORKER_INBOX = REPO_ROOT / "automation" / "orchestration" / "workers" / "inbox" / "AIOS_WORKER_INBOX.json"
ACTIVE_PACKETS = REPO_ROOT / "automation" / "orchestration" / "work_packets" / "active"
RUNTIME_TELEMETRY = REPO_ROOT / "telemetry" / "runtime"


def _load():
    spec = importlib.util.spec_from_file_location("aios_p2_enqueue_bridge_for_tests", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_queue_gate():
    spec = importlib.util.spec_from_file_location("aios_queue_mutation_gate_for_p2_tests", QUEUE_GATE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _fingerprint(path: Path):
    if path.is_file():
        return ("file", path.read_bytes())
    if path.is_dir():
        entries = sorted(str(item.relative_to(path)) for item in path.rglob("*"))
        return ("dir", entries)
    return ("missing", None)


def _ready_evidence() -> dict:
    return {
        "human_gate_report": {
            "dogfood_status": "PASS",
            "mutation_check_status": "PASS",
            "mutated_sources": [],
            "queue_validation_summary": {"queue_validation_status": "PASS"},
            "runtime_proof_gate_summary": {"final_verdict": "READY_FOR_HUMAN_GATE"},
            "human_gate_packet_summary": {"packet_status": "READY_FOR_HUMAN_REVIEW"},
            "summary": {
                "runtime_proof_gate_verdict": "READY_FOR_HUMAN_GATE",
                "packet_status": "READY_FOR_HUMAN_REVIEW",
            },
            "approval_granted": False,
            "execution_allowed": False,
            "dispatch_allowed": False,
            "apply_allowed": False,
            "runtime_launch_allowed": False,
            "queue_mutation_allowed": False,
            "telemetry_mutation_allowed": False,
            "scheduler_creation_allowed": False,
            "service_creation_allowed": False,
            "sos_allowed": False,
            "live_trading_allowed": False,
            "credentials_accessed": False,
            "unsafe_autonomy_claim": False,
            "vacation_mode_complete": False,
        },
        "autonomy_gap_report": {
            "reassessment_status": "PASS",
            "p2_enqueue_bridge_readiness": {"status": "READY"},
            "readiness_scorecard": {"p2_enqueue_bridge_ready": {"status": "READY"}},
            "live_execution_readiness": {"status": "BLOCKED"},
            "recommended_next_lanes": [
                {
                    "lane_id": "P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1",
                    "scope": "DRY_RUN_ONLY",
                }
            ],
            "summary": {
                "recommended_next_lane": "P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1",
                "p2_enqueue_bridge_ready": "READY",
            },
            "approval_granted": False,
            "execution_allowed": False,
            "dispatch_allowed": False,
            "apply_allowed": False,
            "runtime_launch_allowed": False,
            "queue_mutation_allowed": False,
            "telemetry_mutation_allowed": False,
            "scheduler_creation_allowed": False,
            "service_creation_allowed": False,
            "sos_allowed": False,
            "live_trading_allowed": False,
            "credentials_accessed": False,
            "unsafe_autonomy_claim": False,
            "vacation_mode_complete": False,
        },
    }


def test_module_imports_cleanly():
    mod = _load()
    assert mod.SCHEMA == "AIOS_P2_ENQUEUE_BRIDGE_PREVIEW.v1"
    assert mod.MODE == "DRY_RUN"
    assert mod.BRIDGE_TYPE == "p2_enqueue_bridge"


def test_current_repo_evidence_builds_blocked_preview(tmp_path):
    mod = _load()
    report = mod.build_p2_enqueue_bridge_report(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "p2_enqueue_bridge",
        now="2026-01-02T03:04:05Z",
    )
    preview = report["proposed_queue_item_preview"]
    assert report["bridge_status"] == "BLOCKED"
    assert report["validation"]["status"] == "PASS"
    assert report["queue_mutation_allowed"] is False
    assert report["runtime_launch_allowed"] is False
    assert report["scheduler_creation_allowed"] is False
    assert report["sos_allowed"] is False
    assert report["live_trading_allowed"] is False
    assert preview["enqueue_allowed"] is False
    assert preview["canonical_queue_write_allowed"] is False
    assert preview["worker_inbox_write_allowed"] is False
    assert preview["active_packet_write_allowed"] is False
    assert preview["runtime_execution_allowed"] is False
    assert preview["allowed_paths"] == ["automation/orchestration/work_packets/"]
    assert "automation/orchestration/work_packets/active/" in preview["forbidden_paths"]


def test_bridge_writes_only_preview_json_and_markdown(tmp_path):
    mod = _load()
    output_dir = tmp_path / "Reports" / "p2_enqueue_bridge"
    report = mod.run_p2_enqueue_bridge(
        repo_root=REPO_ROOT,
        output_dir=output_dir,
        now="2026-01-02T03:04:05Z",
    )
    json_path = output_dir / mod.REPORT_JSON_NAME
    md_path = output_dir / mod.REPORT_MD_NAME
    assert json_path.exists()
    assert md_path.exists()
    assert sorted(path.name for path in output_dir.iterdir()) == [
        mod.REPORT_JSON_NAME,
        mod.REPORT_MD_NAME,
    ]
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["summary"]["bridge_status"] == report["bridge_status"]
    assert "This preview does not approve execution." in md_path.read_text(encoding="utf-8")


def test_ready_evidence_still_produces_preview_only_item(tmp_path):
    mod = _load()
    report = mod.build_p2_enqueue_bridge_report(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "p2_enqueue_bridge",
        now="2026-01-02T03:04:05Z",
        evidence=_ready_evidence(),
    )
    preview = report["proposed_queue_item_preview"]
    assert report["bridge_status"] == "READY_FOR_DRY_RUN_PREVIEW"
    assert report["bridge_blockers"] == []
    assert report["invalid_reasons"] == []
    assert report["validation"]["status"] == "PASS"
    assert preview["preview_state"] == "PREVIEW_READY"
    assert preview["enqueue_allowed"] is False
    assert preview["dispatch_allowed"] is False
    assert preview["runtime_execution_allowed"] is False
    assert preview["allowed_paths"] == ["automation/orchestration/work_packets/"]
    assert "automation/orchestration/workers/inbox/" in preview["forbidden_paths"]


def test_enriched_preview_passes_queue_gate_contract_without_mutation(tmp_path):
    mod = _load()
    queue_gate = _load_queue_gate()
    protected_paths = [COMMAND_QUEUE, WORKER_INBOX, ACTIVE_PACKETS, RUNTIME_TELEMETRY]
    before = {str(path): _fingerprint(path) for path in protected_paths}
    report = mod.build_p2_enqueue_bridge_report(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "p2_enqueue_bridge",
        now="2026-01-02T03:04:05Z",
        evidence=_ready_evidence(),
    )
    json_path = tmp_path / "Reports" / "p2_enqueue_bridge" / mod.REPORT_JSON_NAME
    mod.write_p2_enqueue_bridge_reports(report, output_dir=json_path.parent)

    gate_report = queue_gate.run_queue_mutation_gate(
        repo_root=REPO_ROOT,
        proposed_item_path=json_path,
        output_dir=tmp_path / "Reports" / "queue_mutation_gate",
        now="2026-01-02T03:04:05Z",
    )

    after = {str(path): _fingerprint(path) for path in protected_paths}
    assert before == after
    assert gate_report["gate_status"] == queue_gate.BLOCKED
    assert gate_report["validation"]["invalid_reasons"] == []
    assert gate_report["proposed_queue_item"]["allowed_paths"] == ["automation/orchestration/work_packets/"]
    assert "automation/orchestration/work_packets/active/" in gate_report["proposed_queue_item"]["forbidden_paths"]
    assert gate_report["queue_write_allowed"] is False
    assert gate_report["canonical_queue_mutated"] is False
    assert gate_report["worker_inbox_mutation_allowed"] is False
    assert gate_report["runtime_execution_allowed"] is False


def test_missing_evidence_is_invalid_not_ready(tmp_path):
    mod = _load()
    report = mod.build_p2_enqueue_bridge_report(
        repo_root=tmp_path,
        output_dir=tmp_path / "Reports" / "p2_enqueue_bridge",
        now="2026-01-02T03:04:05Z",
    )
    assert report["bridge_status"] == "INVALID"
    assert report["evidence_missing"]
    assert report["validation"]["status"] == "PASS"
    assert report["proposed_queue_item_preview"]["enqueue_allowed"] is False


def test_validation_blocks_dangerous_tamper(tmp_path):
    mod = _load()
    report = mod.build_p2_enqueue_bridge_report(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "p2_enqueue_bridge",
        now="2026-01-02T03:04:05Z",
    )
    tampered = deepcopy(report)
    tampered["queue_mutation_allowed"] = True
    tampered["proposed_queue_item_preview"]["enqueue_allowed"] = True
    validation = mod.validate_p2_enqueue_bridge_report(tampered)
    assert validation["status"] == "BLOCK"
    assert any("queue_mutation_allowed" in blocker for blocker in validation["blockers"])
    assert any("enqueue_allowed" in blocker for blocker in validation["blockers"])


def test_ready_status_with_blockers_is_blocked_by_validator(tmp_path):
    mod = _load()
    report = mod.build_p2_enqueue_bridge_report(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "p2_enqueue_bridge",
        now="2026-01-02T03:04:05Z",
    )
    report["bridge_status"] = "READY_FOR_DRY_RUN_PREVIEW"
    validation = mod.validate_p2_enqueue_bridge_report(report)
    assert validation["status"] == "BLOCK"
    assert any("bridge_blockers" in blocker for blocker in validation["blockers"])


def test_bridge_does_not_mutate_canonical_queue_or_worker_inbox(tmp_path):
    mod = _load()
    protected_paths = [COMMAND_QUEUE, WORKER_INBOX, ACTIVE_PACKETS, RUNTIME_TELEMETRY]
    before = {str(path): _fingerprint(path) for path in protected_paths}
    report = mod.run_p2_enqueue_bridge(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "p2_enqueue_bridge",
        now="2026-01-02T03:04:05Z",
    )
    after = {str(path): _fingerprint(path) for path in protected_paths}
    assert before == after
    assert report["proposed_queue_item_preview"]["canonical_queue_write_allowed"] is False
    assert report["proposed_queue_item_preview"]["worker_inbox_write_allowed"] is False
    assert report["proposed_queue_item_preview"]["active_packet_write_allowed"] is False


def test_cli_defaults_to_dry_run_and_writes_preview(tmp_path, monkeypatch, capsys):
    mod = _load()
    outdir = tmp_path / "Reports" / "p2_enqueue_bridge"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "aios_p2_enqueue_bridge",
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
    parsed = json.loads(captured.out)
    assert rc == 0
    assert parsed["bridge_status"] == "BLOCKED"
    assert (outdir / mod.REPORT_JSON_NAME).exists()
    assert (outdir / mod.REPORT_MD_NAME).exists()
    assert parsed["enqueue_allowed"] is False


def test_required_evidence_files_exist():
    assert HUMAN_GATE_REPORT.exists()
    assert AUTONOMY_GAP_REPORT.exists()
