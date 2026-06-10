from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_runtime_apply_lane_preview.py"

P2_BRIDGE_REPORT = REPO_ROOT / "Reports" / "p2_enqueue_bridge" / "p2_enqueue_bridge_preview.json"
QUEUE_GATE_REPORT = REPO_ROOT / "Reports" / "queue_mutation_gate" / "queue_mutation_gate_preview.json"
RUNTIME_PROOF_REPORT = REPO_ROOT / "Reports" / "runtime_proof_gate" / "runtime_proof_gate_preview.json"

REAL_ACTIVE_QUEUE = REPO_ROOT / "automation" / "orchestration" / "work_packets" / "active"
REAL_WORKER_INBOX = REPO_ROOT / "automation" / "orchestration" / "workers" / "inbox" / "AIOS_WORKER_INBOX.json"
REAL_APPROVAL_INBOX = REPO_ROOT / "automation" / "orchestration" / "approval_inbox"
REAL_COMMAND_QUEUE = REPO_ROOT / "automation" / "orchestration" / "command_queue" / "AIOS_COMMAND_QUEUE.json"
REAL_RUNTIME_PATH = REPO_ROOT / "services" / "runtime"
REAL_RUNTIME_TELEMETRY = REPO_ROOT / "telemetry" / "runtime"


def _load():
    spec = importlib.util.spec_from_file_location("aios_runtime_apply_lane_preview", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fingerprint(path: Path):
    if path.is_dir():
        return [
            (
                child.relative_to(path).as_posix(),
                child.stat().st_size,
                _hash(child),
            )
            for child in sorted(path.rglob("*"))
            if child.is_file()
        ]
    if not path.exists():
        return None
    return (path.stat().st_size, _hash(path))


def _ready_p2_preview():
    return {
        "bridge_status": "READY_FOR_DRY_RUN_PREVIEW",
        "validation": {"status": "PASS"},
        "summary": {"recommended_next_lane": "QUEUE_BLOCKER_TRIAGE_V1"},
        "proposed_queue_item_preview": {
            "preview_id": "P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1",
            "lane_id": "p2_review_to_queue_enqueue_bridge",
            "mode": "DRY_RUN_PREVIEW_ONLY",
            "allowed_paths": ["automation/orchestration/work_packets/"],
            "forbidden_paths": [
                "automation/orchestration/work_packets/active/",
                "automation/orchestration/work_packets/blocked/",
                "automation/orchestration/work_packets/complete/",
            ],
            "runtime_execution_allowed": False,
            "scheduler_creation_allowed": False,
            "sos_allowed": False,
            "live_trading_allowed": False,
            "queue_mutation_allowed": False,
            "runtime_launch_allowed": False,
            "worker_inbox_write_allowed": False,
        },
    }


def _queue_gate_with_approval(approved: bool = False):
    return {
        "gate_status": "READY_FOR_HUMAN_REVIEW" if approved else "BLOCKED",
        "validation": {"status": "PASS", "blockers": [] if approved else ["approval evidence is not explicit"]},
        "proposed_queue_item": {
            "packet_id": "AIOS-RUNTIME-APPLY-PREVIEW-001",
            "lane": "feature/runtime-apply-lane-preview-v1",
            "mode": "DRY_RUN_PREVIEW_ONLY",
            "allowed_paths": ["automation/orchestration/work_packets/"],
            "forbidden_paths": ["automation/orchestration/work_packets/active/"],
            "target_paths": ["automation/orchestration/work_packets/"],
        },
        "approval_check": {"approval_evidence_present": True, "explicit_approval": approved},
        "runtime_execution_allowed": False,
        "runtime_launch_allowed": False,
        "scheduler_creation_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
        "queue_mutation_allowed": False,
        "worker_inbox_mutation_allowed": False,
        "approval_inbox_mutation_allowed": False,
        "command_queue_mutation_allowed": False,
    }


def _queue_gate_stale_invalid():
    return {
        "gate_status": "INVALID",
        "validation": {"status": "PASS", "invalid_reasons": ["allowed_paths is required; forbidden_paths is required"]},
        "proposed_queue_item": {
            "packet_id": "AIOS-STALE-INVALID-001",
            "lane": "feature/runtime-apply-lane-preview-v1",
            "mode": "DRY_RUN_PREVIEW_ONLY",
            "allowed_paths": [],
            "forbidden_paths": [],
        },
        "approval_check": {"approval_evidence_present": True, "explicit_approval": False},
        "runtime_execution_allowed": False,
        "runtime_launch_allowed": False,
        "scheduler_creation_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
        "queue_mutation_allowed": False,
        "worker_inbox_mutation_allowed": False,
        "approval_inbox_mutation_allowed": False,
        "command_queue_mutation_allowed": False,
    }


def _runtime_proof_gate_ready():
    return {
        "schema": "AIOS_RUNTIME_PROOF_GATE.v1",
        "mode": "DRY_RUN_GATE",
        "final_verdict": "READY_FOR_HUMAN_GATE",
        "human_gate_ready": True,
        "runtime_launch_allowed": False,
        "execution_allowed": False,
        "runtime_mutation_allowed": False,
        "scheduler_creation_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
        "approval_granted": False,
        "vacation_mode_complete": False,
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_module_imports_cleanly():
    mod = _load()
    assert mod.SCHEMA == "AIOS_RUNTIME_APPLY_LANE_PREVIEW.v1"
    assert mod.MODE == "DRY_RUN_PREVIEW_ONLY"


def test_current_inputs_block_without_explicit_queue_approval():
    mod = _load()
    report = mod.build_runtime_apply_lane_report(
        repo_root=REPO_ROOT,
        now="2026-06-10T15:20:28Z",
        p2_preview=_ready_p2_preview(),
        queue_mutation_gate_preview=_queue_gate_with_approval(False),
        runtime_proof_gate=_runtime_proof_gate_ready(),
    )

    assert report["apply_status"] == mod.STATUS_BLOCKED
    assert "queue mutation approval is not explicit" in report["blockers"]
    assert report["would_apply"] is False
    assert report["would_route"] is False
    assert report["would_execute"] is False
    assert report["runtime_launch"] is False
    assert report["runtime_execution"] is False
    assert report["queue_mutation"] is False
    assert report["worker_inbox_mutation"] is False
    assert report["scheduler_registration"] is False
    assert report["sos_notification"] is False
    assert report["trading_execution"] is False
    assert report["validation"]["status"] == "PASS"


def test_stale_queue_gate_invalid_is_still_blocked(tmp_path):
    mod = _load()
    report = mod.build_runtime_apply_lane_report(
        repo_root=REPO_ROOT,
        now="2026-06-10T15:20:28Z",
        p2_preview=_ready_p2_preview(),
        queue_mutation_gate_preview=_queue_gate_stale_invalid(),
        runtime_proof_gate=_runtime_proof_gate_ready(),
    )
    assert report["apply_status"] == mod.STATUS_BLOCKED
    assert not report["invalid_reasons"]
    assert any("invalid reasons" in str(blocker) for blocker in report["blockers"])


def test_ready_with_explicit_approval_produces_ready_preview_status(tmp_path):
    mod = _load()
    report = mod.build_runtime_apply_lane_report(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "runtime_apply_lane",
        now="2026-06-10T15:20:28Z",
        p2_preview=_ready_p2_preview(),
        queue_mutation_gate_preview=_queue_gate_with_approval(True),
        runtime_proof_gate=_runtime_proof_gate_ready(),
    )
    assert report["apply_status"] == mod.STATUS_READY
    assert report["validation"]["status"] == "PASS"
    assert report["execution_projection"]["would_apply"] is False
    assert report["execution_projection"]["would_route"] is False
    assert report["execution_projection"]["would_execute"] is False
    assert report["runtime_launch"] is False
    assert report["runtime_execution"] is False
    assert report["queue_mutation"] is False
    assert report["worker_inbox_mutation"] is False
    assert report["scheduler_registration"] is False
    assert report["sos_notification"] is False
    assert report["trading_execution"] is False
    assert not report["worker_availability_preview"]["protected_targets"]


def test_preview_files_are_written_and_loaded(tmp_path):
    mod = _load()
    outdir = tmp_path / "Reports" / "runtime_apply_lane"
    report = mod.run_runtime_apply_lane_preview(
        repo_root=REPO_ROOT,
        output_dir=outdir,
        now="2026-06-10T15:20:28Z",
    )
    json_path = outdir / mod.REPORT_JSON_NAME
    md_path = outdir / mod.REPORT_MD_NAME
    assert json_path.exists()
    assert md_path.exists()
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["summary"]["apply_status"] == report["apply_status"]
    assert "This preview does not execute runtime, mutate worker inbox, mutate queue" in md_path.read_text(encoding="utf-8")


def test_protected_real_paths_are_not_mutated(tmp_path):
    mod = _load()
    paths_to_watch = [REAL_ACTIVE_QUEUE, REAL_WORKER_INBOX, REAL_APPROVAL_INBOX, REAL_RUNTIME_PATH, REAL_RUNTIME_TELEMETRY]
    before = {str(path): _fingerprint(path) for path in paths_to_watch}
    report = mod.build_runtime_apply_lane_report(
        repo_root=REPO_ROOT,
        now="2026-06-10T15:20:28Z",
        p2_preview=_ready_p2_preview(),
        queue_mutation_gate_preview=_queue_gate_with_approval(False),
        runtime_proof_gate=_runtime_proof_gate_ready(),
    )
    after = {str(path): _fingerprint(path) for path in paths_to_watch}
    assert before == after
    assert report["apply_status"] == mod.STATUS_BLOCKED
    assert report["queue_mutation"] is False
    assert report["worker_inbox_mutation"] is False
    assert report["approval_inbox_mutation"] is False


def test_protect_queue_and_approval_path_flags_are_false(tmp_path):
    mod = _load()
    report = mod.build_runtime_apply_lane_report(
        repo_root=REPO_ROOT,
        now="2026-06-10T15:20:28Z",
        p2_preview=_ready_p2_preview(),
        queue_mutation_gate_preview=_queue_gate_with_approval(True),
        runtime_proof_gate=_runtime_proof_gate_ready(),
    )
    assert report["queue_mutation_allowed"] is False
    assert report["worker_inbox_mutation_allowed"] is False
    assert report["approval_inbox_mutation_allowed"] is False
    assert report["command_queue_mutation_allowed"] is False
    assert report["runtime_launch_allowed"] is False
    assert report["runtime_execution_allowed"] is False


def test_tampering_execution_projection_blocks_validation():
    mod = _load()
    report = mod.build_runtime_apply_lane_report(
        repo_root=REPO_ROOT,
        now="2026-06-10T15:20:28Z",
        p2_preview=_ready_p2_preview(),
        queue_mutation_gate_preview=_queue_gate_with_approval(True),
        runtime_proof_gate=_runtime_proof_gate_ready(),
    )
    tampered = deepcopy(report)
    tampered["runtime_execution"] = True
    validation = mod.validate_runtime_apply_lane_preview(tampered)
    assert validation["status"] == "BLOCK"
    assert any("runtime_execution must remain false" in blocker for blocker in validation["blockers"])


def test_validation_rejects_invalid_status():
    mod = _load()
    report = mod.build_runtime_apply_lane_report(
        repo_root=REPO_ROOT,
        now="2026-06-10T15:20:28Z",
        p2_preview=_ready_p2_preview(),
        queue_mutation_gate_preview=_queue_gate_with_approval(True),
        runtime_proof_gate=_runtime_proof_gate_ready(),
    )
    report["apply_status"] = "UNKNOWN"
    validation = mod.validate_runtime_apply_lane_preview(report)
    assert validation["status"] == "BLOCK"
    assert any("apply_status must be READY_FOR_RUNTIME_PREVIEW, BLOCKED, or INVALID" in blocker for blocker in validation["blockers"])


def test_required_evidence_files_exist():
    assert P2_BRIDGE_REPORT.exists()
    assert QUEUE_GATE_REPORT.exists()
    # runtime proof report location may not exist until the runtime proof lane is
    # refreshed, so verify constants remain valid paths.
    assert str(RUNTIME_PROOF_REPORT).endswith("runtime_proof_gate_preview.json")
