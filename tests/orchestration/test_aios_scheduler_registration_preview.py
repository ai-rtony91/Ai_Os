from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "scheduler"
    / "aios_scheduler_registration_preview.py"
)

QUEUE_GATE_REPORT = (
    REPO_ROOT
    / "Reports"
    / "queue_mutation_gate"
    / "queue_mutation_gate_preview.json"
)
RUNTIME_APPLY_REPORT = (
    REPO_ROOT
    / "Reports"
    / "runtime_apply_lane"
    / "runtime_apply_lane_preview.json"
)
SOS_PREVIEW_REPORT = REPO_ROOT / "Reports" / "sos_preview" / "sos_arming_preview.json"
HUMAN_GATE_REPORT = REPO_ROOT / "Reports" / "human_gate" / "human_gate_packet_dogfood_report.json"
AUTONOMY_REPORT = REPO_ROOT / "Reports" / "autonomy_gap" / "autonomy_gap_reassessment_report.json"

ACTIVE_QUEUE = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "work_packets"
    / "active"
)
WORKER_INBOX = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "workers"
    / "inbox"
    / "AIOS_WORKER_INBOX.json"
)
APPROVAL_INBOX = REPO_ROOT / "automation" / "orchestration" / "approval_inbox"
COMMAND_QUEUE = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "command_queue"
    / "AIOS_COMMAND_QUEUE.json"
)
SERVICES = REPO_ROOT / "services"
TELEMETRY = REPO_ROOT / "telemetry"


def _load():
    spec = importlib.util.spec_from_file_location(
        "aios_scheduler_registration_preview_for_tests", MODULE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha1(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65_536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fingerprint(path: Path):
    if path.is_file():
        return ("file", path.stat().st_size, _sha1(path))
    if path.is_dir():
        entries = sorted(str(item.relative_to(path).as_posix()) for item in path.rglob("*") if item.is_file())
        return ("dir", entries)
    return ("missing", None)


def _ready_evidence():
    return {
        "queue_mutation_gate": {
            "gate_status": "READY_FOR_HUMAN_REVIEW",
            "approval_check": {"explicit_approval": True},
            "validation": {"status": "PASS"},
            "proposed_queue_item": {"packet_id": "AIOS-SCHED-PREVIEW-001"},
        },
        "runtime_apply": {
            "apply_status": "READY_FOR_RUNTIME_PREVIEW",
            "runtime_execution": False,
            "runtime_launch": False,
            "scheduler_registration": False,
            "sos_notification": False,
            "queue_mutation": False,
            "worker_inbox_mutation": False,
            "approval_inbox_mutation": False,
            "runtime_execution_allowed": False,
            "runtime_launch_allowed": False,
            "scheduler_creation_allowed": False,
            "sos_allowed": False,
            "queue_mutation_allowed": False,
            "worker_inbox_mutation_allowed": False,
        },
        "sos_preview": {
            "sos_status": "READY_FOR_SOS_PREVIEW",
            "notification_sent": False,
            "notification_allowed": False,
        },
        "human_gate": {
            "dogfood_status": "PASS",
            "human_gate_packet_summary": {"packet_status": "READY_FOR_HUMAN_REVIEW"},
        },
        "autonomy_gap": {
            "reassessment_status": "PASS",
            "summary": {"scheduler_readiness": "READY"},
        },
    }


def test_module_imports_cleanly():
    mod = _load()
    assert mod.SCHEMA == "AIOS_SCHEDULER_REGISTRATION_PREVIEW.v1"
    assert mod.MODE == "DRY_RUN"


def test_current_repo_evidence_is_blocked_or_ready(tmp_path):
    mod = _load()
    report = mod.build_scheduler_registration_preview(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "scheduler_preview",
        now="2026-06-10T15:20:28Z",
    )
    assert report["scheduler_status"] in {"BLOCKED", "INVALID"}
    assert report["validation"]["status"] == "PASS"
    assert report["would_register_task"] is False
    assert report["would_start_service"] is False
    assert report["scheduler_created"] is False
    assert report["service_created"] is False
    assert report["runtime_launch_allowed"] is False
    assert report["runtime_execution_allowed"] is False
    assert report["notification_send_allowed"] is False


def test_ready_evidence_produces_ready_preview():
    mod = _load()
    report = mod.build_scheduler_registration_preview(
        repo_root=REPO_ROOT,
        now="2026-06-10T15:20:28Z",
        evidence=_ready_evidence(),
    )
    assert report["scheduler_status"] == mod.READY
    assert report["would_schedule"] is True
    assert report["would_register_task"] is False
    assert report["would_start_service"] is False
    assert report["scheduler_registration_allowed"] is False
    assert report["service_created"] is False
    assert report["runtime_launch"] is False
    assert report["runtime_execution"] is False
    assert report["queue_mutation"] is False
    assert report["worker_inbox_mutation"] is False
    assert report["notification_sent"] is False
    assert report["proposed_scheduler"]["status"] == "would_schedule"
    assert report["validation"]["status"] == "PASS"


def test_scheduler_registration_preview_files_written(tmp_path):
    mod = _load()
    output_dir = tmp_path / "Reports" / "scheduler_preview"
    report = mod.run_scheduler_registration_preview(
        repo_root=REPO_ROOT,
        output_dir=output_dir,
        now="2026-06-10T15:20:28Z",
        evidence=_ready_evidence(),
    )
    json_path = output_dir / mod.REPORT_JSON_NAME
    md_path = output_dir / mod.REPORT_MD_NAME
    assert json_path.exists()
    assert md_path.exists()
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["summary"]["scheduler_status"] == report["scheduler_status"]
    assert "This preview does not register scheduler tasks" in md_path.read_text(encoding="utf-8")


def test_protected_paths_are_not_mutated(tmp_path):
    mod = _load()
    paths_to_watch = [ACTIVE_QUEUE, WORKER_INBOX, APPROVAL_INBOX, COMMAND_QUEUE, SERVICES, TELEMETRY]
    before = {str(path): _fingerprint(path) for path in paths_to_watch}
    _ = mod.run_scheduler_registration_preview(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "scheduler_preview",
        now="2026-06-10T15:20:28Z",
        evidence=_ready_evidence(),
    )
    after = {str(path): _fingerprint(path) for path in paths_to_watch}
    assert before == after


def test_validation_blocks_mutation_tamper():
    mod = _load()
    report = mod.build_scheduler_registration_preview(
        repo_root=REPO_ROOT,
        now="2026-06-10T15:20:28Z",
        evidence=_ready_evidence(),
    )
    tampered = dict(report)
    tampered["service_created"] = True
    tampered["scheduler_registration_allowed"] = True
    validation = mod.validate_scheduler_registration_preview(tampered)
    assert validation["status"] == "BLOCK"
    assert any("service_created must be false" in blocker for blocker in validation["blockers"])
    assert any("scheduler_registration_allowed must be false" in blocker for blocker in validation["blockers"])


def test_required_evidence_files_exist():
    assert QUEUE_GATE_REPORT.exists()
    assert RUNTIME_APPLY_REPORT.exists()
    assert SOS_PREVIEW_REPORT.exists()
    assert HUMAN_GATE_REPORT.exists()
    assert AUTONOMY_REPORT.exists()
