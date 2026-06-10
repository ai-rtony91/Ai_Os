from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "notifications"
    / "aios_sos_arming_preview.py"
)

QUEUE_GATE_REPORT = REPO_ROOT / "Reports" / "queue_mutation_gate" / "queue_mutation_gate_preview.json"
P2_BRIDGE_REPORT = REPO_ROOT / "Reports" / "p2_enqueue_bridge" / "p2_enqueue_bridge_preview.json"
HUMAN_GATE_REPORT = REPO_ROOT / "Reports" / "human_gate" / "human_gate_packet_dogfood_report.json"
AUTONOMY_GAP_REPORT = REPO_ROOT / "Reports" / "autonomy_gap" / "autonomy_gap_reassessment_report.json"

ACTIVE_QUEUE = REPO_ROOT / "automation" / "orchestration" / "work_packets" / "active"
WORKER_INBOX = REPO_ROOT / "automation" / "orchestration" / "workers" / "inbox" / "AIOS_WORKER_INBOX.json"
APPROVAL_INBOX = REPO_ROOT / "automation" / "orchestration" / "approval_inbox"
COMMAND_QUEUE = REPO_ROOT / "automation" / "orchestration" / "command_queue" / "AIOS_COMMAND_QUEUE.json"
SERVICES = REPO_ROOT / "services"
TELEMETRY = REPO_ROOT / "telemetry"


def _load() -> object:
    spec = importlib.util.spec_from_file_location("aios_sos_arming_preview_for_tests", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def _hash(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65_536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fingerprint(path: Path):
    if path.is_file():
        return ("file", path.stat().st_size, _hash(path))
    if path.is_dir():
        return ("dir", sorted(str(item.relative_to(path).as_posix()) for item in path.rglob("*")))
    return ("missing", None, None)


def _ready_evidence() -> dict:
    return {
        "p2_bridge_report": {
            "bridge_status": "READY_FOR_DRY_RUN_PREVIEW",
            "bridge_blockers": [],
        },
        "queue_mutation_report": {
            "gate_status": "READY_FOR_HUMAN_REVIEW",
            "approval_check": {"explicit_approval": True},
            "proposed_queue_item": {"packet_id": "AIOS-SOS-PREVIEW-READY-001"},
        },
        "human_gate_report": {"dogfood_status": "PASS"},
        "autonomy_gap_report": {
            "reassessment_status": "PASS",
            "summary": {"sos_ready": "READY"},
        },
        "runtime_apply_report": {"status": "READY_FOR_RUNTIME_PREVIEW"},
    }


def test_module_imports_cleanly():
    mod = _load()
    assert mod.SCHEMA == "AIOS_SOS_ARMING_PREVIEW.v1"
    assert mod.MODE == "DRY_RUN"
    assert mod.READY == "READY_FOR_SOS_PREVIEW"
    assert mod.BLOCKED == "BLOCKED"
    assert mod.INVALID == "INVALID"


def test_current_repo_evidence_builds_blocked_preview(tmp_path):
    mod = _load()
    report = mod.build_sos_arming_preview(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "sos_preview",
        now="2026-01-02T03:04:05Z",
    )
    assert report["sos_status"] in {"BLOCKED", "INVALID"}
    assert report["validation"]["status"] == "PASS"
    assert report["notification_allowed"] is False
    assert report["notification_sent"] is False
    assert report["credential_required"] is True
    assert report["scheduler_required"] is False
    assert report["would_apply"] is False
    assert report["would_route"] is False
    assert report["would_execute"] is False
    assert report["runtime_launch"] is False
    assert report["runtime_execution"] is False
    assert report["queue_mutation"] is False
    assert report["worker_inbox_mutation"] is False
    assert report["scheduler_registration"] is False
    assert report["trading_execution"] is False
    assert (
        report["sos_status"] == "BLOCKED"
        and "explicit approval" in report["sos_status_reason"].lower()
    ) or report["sos_status"] == "INVALID"
    assert report["protected_boundaries"]["notification_allowed"] is False


def test_blocked_sos_event_is_simulated_and_non_actionable(tmp_path):
    mod = _load()
    report = mod.build_sos_arming_preview(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "sos_preview",
        now="2026-01-02T03:04:05Z",
        evidence=_ready_evidence(),
    )
    # Without a runtime apply file in the supplied repo root, preview remains blocked,
    # but required safety flags stay false in the SOS simulation.
    assert report["blocked_event"]["would_apply"] is False
    assert report["blocked_event"]["would_route"] is False
    assert report["blocked_event"]["would_execute"] is False
    assert report["blocked_event"]["would_dispatch"] is False
    assert report["blocked_event"]["event_status"] == "BLOCKED"


def test_preview_only_artifacts_are_written(tmp_path):
    mod = _load()
    output_dir = tmp_path / "Reports" / "sos_preview"
    report = mod.run_sos_arming_preview(
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
    assert loaded["sos_status"] == report["sos_status"]
    assert "This preview does not send notifications, mutate state, or arm SOS." in md_path.read_text(encoding="utf-8")


def test_does_not_mutate_real_runtime_or_queue_state(tmp_path):
    mod = _load()
    protected_paths = [ACTIVE_QUEUE, WORKER_INBOX, APPROVAL_INBOX, COMMAND_QUEUE, SERVICES, TELEMETRY]
    before = {str(path): _fingerprint(path) for path in protected_paths}
    _ = mod.run_sos_arming_preview(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "sos_preview",
        now="2026-01-02T03:04:05Z",
    )
    after = {str(path): _fingerprint(path) for path in protected_paths}
    assert before == after


def test_ready_evidence_can_still_be_blocked_when_missing_runtime_apply_preview(tmp_path):
    mod = _load()
    evidence = _ready_evidence()
    evidence.pop("runtime_apply_report", None)
    report = mod.build_sos_arming_preview(
        repo_root=tmp_path,
        output_dir=tmp_path / "Reports" / "sos_preview",
        now="2026-01-02T03:04:05Z",
        evidence=evidence,
    )
    assert report["sos_status"] == "BLOCKED"
    assert report["notification_sent"] is False
    assert report["blocked_event"]["event_status"] == "BLOCKED"
    assert report["evidence_missing"]["runtime_apply_preview"] is True


def test_validation_blocks_dangerous_tamper(tmp_path):
    mod = _load()
    report = mod.build_sos_arming_preview(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "sos_preview",
        now="2026-01-02T03:04:05Z",
    )
    tampered = dict(report)
    tampered["notification_sent"] = True
    validation = mod.validate_sos_arming_report(tampered)
    assert validation["status"] == "PASS"
    assert any("notification_sent" in item for item in validation["blockers"])


def test_required_evidence_sources_exist():
    assert QUEUE_GATE_REPORT.exists()
    assert P2_BRIDGE_REPORT.exists()
    assert HUMAN_GATE_REPORT.exists()
    assert AUTONOMY_GAP_REPORT.exists()
