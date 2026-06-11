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
    / "approval_inbox"
    / "aios_queue_specific_approval_request.py"
)

APPROVAL_GATE_PATH = REPO_ROOT / "automation" / "orchestration" / "approval_inbox" / "APPLY_APPROVAL_GATE_001.json"
QUEUE_SPECIFIC_APPROVAL_GATE_PATH = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "approval_inbox"
    / "APPLY_APPROVAL_GATE_P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1.json"
)
APPROVAL_INBOX_PATH = REPO_ROOT / "automation" / "orchestration" / "approval_inbox" / "APPROVAL_INBOX_001.json"
P2_REPORT_PATH = REPO_ROOT / "Reports" / "p2_enqueue_bridge" / "p2_enqueue_bridge_preview.json"
QUEUE_GATE_REPORT_PATH = REPO_ROOT / "Reports" / "queue_mutation_gate" / "queue_mutation_gate_preview.json"


def _load():
    spec = importlib.util.spec_from_file_location("aios_queue_specific_approval_request_test_module", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fingerprint(path: Path):
    if path.is_file():
        return (path.stat().st_size, _sha256(path))
    if path.is_dir():
        return [
            (child.relative_to(path).as_posix(), child.stat().st_size, _sha256(child))
            for child in sorted(path.rglob("*"))
            if child.is_file()
        ]
    return None


def _approval_paths():
    return [APPROVAL_GATE_PATH, APPROVAL_INBOX_PATH, P2_REPORT_PATH, QUEUE_GATE_REPORT_PATH]


def test_default_request_is_pending_review_and_non_authorizing(tmp_path):
    mod = _load()
    before = {str(path): _fingerprint(path) for path in _approval_paths()}

    report = mod.build_queue_specific_approval_request(repo_root=REPO_ROOT, now="2026-06-10T15:20:28Z")
    output_dir = tmp_path / "Reports" / "approval_state_transition"
    written = mod.write_queue_specific_approval_request(report, output_dir)

    after = {str(path): _fingerprint(path) for path in _approval_paths()}
    assert before == after
    assert report["schema"] == mod.SCHEMA
    assert report["mode"] == mod.MODE
    assert report["target_packet_id"] == mod.TARGET_PACKET_ID
    assert report["approval_status"] == "pending_review"
    assert report["approved_by_human"] is False
    assert report["queue_write_allowed"] is False
    assert report["canonical_queue_mutation_allowed"] is False
    assert report["worker_inbox_mutation_allowed"] is False
    assert report["runtime_execution_allowed"] is False
    assert report["scheduler_registration_allowed"] is False
    assert report["sos_notification_allowed"] is False
    assert report["live_trading_allowed"] is False
    assert report["approval_gate_output_path"].endswith(
        "APPLY_APPROVAL_GATE_P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1.json"
    )
    assert report["approval_gate_output_path"] != "automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json"
    assert report["approval_evidence"]["status"] == "PENDING_HUMAN_APPROVAL"
    assert report["approval_evidence"]["approval_status"] == "pending_review"
    assert report["approval_evidence"]["approved_by_human"] is False
    assert report["approval_evidence"]["approval_granted"] is False
    assert report["approval_evidence"]["explicit_approval"] is False
    assert report["approval_evidence"]["approval_gate_packet_mismatch"] is True
    assert report["approval_evidence"]["approval_gate_packet_id"] == "AIOS-HEARTBEAT-ONLY-PROOF-HARNESS-APPLY-V1"
    assert "queue-specific approval required" in report["approval_evidence"]["non_authorizing_reason"]
    assert (output_dir / mod.DEFAULT_REQUEST_JSON_NAME).exists()
    assert (output_dir / mod.DEFAULT_REQUEST_MD_NAME).exists()
    assert written["json_path"].endswith(mod.DEFAULT_REQUEST_JSON_NAME)
    assert written["md_path"].endswith(mod.DEFAULT_REQUEST_MD_NAME)


def test_default_request_targets_p2_and_carries_paths():
    mod = _load()
    report = mod.build_queue_specific_approval_request(repo_root=REPO_ROOT, now="2026-06-10T15:20:28Z")

    assert report["allowed_paths"] == ["automation/orchestration/work_packets/"]
    assert "automation/orchestration/work_packets/active/" in report["blocked_paths"]
    assert report["queue_gate_status"]
    assert report["queue_gate_blockers"] is not None
    assert report["approval_evidence"]["source_files"]
    assert any(
        path.endswith("APPLY_APPROVAL_GATE_001.json") for path in report["approval_evidence"]["source_files"]
    )
    assert any(
        path.endswith("APPROVAL_INBOX_001.json") for path in report["approval_evidence"]["source_files"]
    )


def test_approved_flag_without_exact_phrase_is_rejected():
    mod = _load()
    report = mod.build_queue_specific_approval_request(
        repo_root=REPO_ROOT,
        approved=True,
        approved_by="Anthony / Human Owner",
        approval_authority="Anthony / Human Owner",
        now="2026-06-10T15:20:28Z",
    )

    assert report["approval_status"] == "pending_review"
    assert report["approved_by_human"] is False
    assert report["approval_attempt_rejected"] is True
    assert report["approval_evidence"]["explicit_approval"] is False
    assert report["approval_gate_write_allowed"] is False


def test_exact_phrase_builds_approved_in_memory_request_but_does_not_write_approval_inbox(tmp_path):
    mod = _load()
    before = _fingerprint(QUEUE_SPECIFIC_APPROVAL_GATE_PATH)
    report = mod.build_queue_specific_approval_request(
        repo_root=REPO_ROOT,
        approved=True,
        approved_by="Anthony / Human Owner",
        approval_authority="Anthony / Human Owner",
        human_approval_phrase=mod.EXACT_HUMAN_APPROVAL_PHRASE,
        now="2026-06-10T15:20:28Z",
    )
    outdir = tmp_path / "Reports" / "approval_state_transition"
    mod.write_queue_specific_approval_request(report, outdir)
    after = _fingerprint(QUEUE_SPECIFIC_APPROVAL_GATE_PATH)

    assert report["approval_status"] == "approved_for_apply"
    assert report["approved_by_human"] is True
    assert report["approval_evidence"]["explicit_approval"] is True
    assert report["approval_gate_write_allowed"] is False
    assert before == after


def test_packet_mismatch_validation_blocks_tampered_request():
    mod = _load()
    report = mod.build_queue_specific_approval_request(repo_root=REPO_ROOT, now="2026-06-10T15:20:28Z")
    tampered = json.loads(json.dumps(report))
    tampered["approval_evidence"]["target_packet_id"] = "AIOS-OTHER-TARGET"

    validation = mod.validate_queue_specific_approval_request(tampered)

    assert validation["status"] == "BLOCK"
    assert any("approval_evidence.target_packet_id" in blocker for blocker in validation["blockers"])


def test_markdown_contains_checkpoint_and_warnings(tmp_path):
    mod = _load()
    report = mod.build_queue_specific_approval_request(
        repo_root=REPO_ROOT,
        approved=True,
        approved_by="Anthony / Human Owner",
        approval_authority="Anthony / Human Owner",
        human_approval_phrase=mod.EXACT_HUMAN_APPROVAL_PHRASE,
        now="2026-06-10T15:20:28Z",
    )
    outdir = tmp_path / "Reports" / "approval_state_transition"
    mod.write_queue_specific_approval_request(report, outdir)
    md_text = (outdir / mod.DEFAULT_REQUEST_MD_NAME).read_text(encoding="utf-8")

    assert "Human Approval Checkpoint" in md_text
    assert mod.EXACT_HUMAN_APPROVAL_PHRASE in md_text
    assert "This draft does not mutate approval inbox state." in md_text
    assert "A mismatched heartbeat gate must not be repurposed." in md_text


def test_cli_no_write_skips_report_creation(tmp_path, monkeypatch, capsys):
    mod = _load()
    outdir = tmp_path / "Reports" / "approval_state_transition"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "aios_queue_specific_approval_request",
            "--repo-root",
            str(REPO_ROOT),
            "--output-dir",
            str(outdir),
            "--no-write",
        ],
    )

    rc = mod.main()
    captured = capsys.readouterr()

    assert rc == 0
    assert not (outdir / mod.DEFAULT_REQUEST_JSON_NAME).exists()
    assert not (outdir / mod.DEFAULT_REQUEST_MD_NAME).exists()
    assert "target_packet_id" in captured.out
