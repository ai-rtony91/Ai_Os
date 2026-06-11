from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "work_packets" / "aios_queue_mutation_gate.py"
REAL_ACTIVE_QUEUE = REPO_ROOT / "automation" / "orchestration" / "work_packets" / "active"
REAL_WORKER_INBOX = REPO_ROOT / "automation" / "orchestration" / "workers" / "inbox" / "AIOS_WORKER_INBOX.json"
REAL_APPROVAL_INBOX = REPO_ROOT / "automation" / "orchestration" / "approval_inbox"
REAL_COMMAND_QUEUE = REPO_ROOT / "automation" / "orchestration" / "command_queue"


def _load_module():
    spec = importlib.util.spec_from_file_location("aios_queue_mutation_gate_test_module", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


gate = _load_module()


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fingerprint(path: Path):
    if path.is_dir():
        return [
            (child.relative_to(path).as_posix(), child.stat().st_size, _sha256(child))
            for child in sorted(path.rglob("*"))
            if child.is_file()
        ]
    if not path.exists():
        return None
    return (path.stat().st_size, _sha256(path))


def _make_repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    (repo_root / "automation" / "orchestration" / "work_packets" / "active").mkdir(parents=True)
    (repo_root / "automation" / "orchestration" / "approval_inbox").mkdir(parents=True)
    return repo_root


def _approved_item(packet_id: str = "AIOS-QUEUE-GATE-TEST-001") -> dict:
    return {
        "packet_id": packet_id,
        "mode": "DRY_RUN",
        "lane": "feature/queue-mutation-gate-dry-run-v1",
        "allowed_paths": ["automation/orchestration/work_packets/"],
        "forbidden_paths": ["automation/orchestration/work_packets/active/"],
        "approval_evidence": {
            "packet_id": packet_id,
            "target_packet_id": packet_id,
            "approval_gate_packet_id": packet_id,
            "approval_gate_packet_mismatch": False,
            "approval_status": "approved_for_apply",
            "approved_by_human": True,
            "approval_authority": "Anthony / Human Owner",
            "approved_by": "Anthony / Human Owner",
            "allowed_paths": ["automation/orchestration/work_packets/"],
            "blocked_paths": ["automation/orchestration/work_packets/active/"],
            "validator_chain_required": True,
            "commit_package_required": True,
            "explicit_approval": True,
            "approval_granted": True,
        },
    }


def test_approved_preview_remains_preview_only(tmp_path):
    repo_root = _make_repo(tmp_path)
    active_queue = repo_root / gate.CANONICAL_QUEUE_OWNER
    before = _fingerprint(active_queue)
    proposal = tmp_path / "proposal.json"
    _write_json(proposal, _approved_item())

    report = gate.run_queue_mutation_gate(
        repo_root=repo_root,
        proposed_item_path=proposal,
        output_dir=tmp_path / "reports",
        now="2026-06-10T15:20:28Z",
    )

    assert report["gate_status"] == gate.READY
    assert report["queue_write_allowed"] is False
    assert report["canonical_queue_mutated"] is False
    assert _fingerprint(active_queue) == before
    assert not list(active_queue.glob("*.json"))
    assert (tmp_path / "reports" / "queue_mutation_gate_preview.json").exists()
    assert (tmp_path / "reports" / "queue_mutation_gate_summary.md").exists()


def test_missing_approval_blocks_preview(tmp_path):
    repo_root = _make_repo(tmp_path)
    proposal = tmp_path / "proposal.json"
    item = _approved_item()
    item.pop("approval_evidence")
    _write_json(proposal, item)

    report = gate.run_queue_mutation_gate(
        repo_root=repo_root,
        proposed_item_path=proposal,
        output_dir=tmp_path / "reports",
        now="2026-06-10T15:20:28Z",
    )

    assert report["gate_status"] == gate.BLOCKED
    assert "approval evidence is missing" in report["validation"]["blockers"]
    assert report["queue_write_allowed"] is False


def test_packet_mismatch_blocks_even_if_approval_evidence_is_approved(tmp_path):
    repo_root = _make_repo(tmp_path)
    proposal = tmp_path / "proposal.json"
    item = _approved_item("P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1")
    item["approval_evidence"]["packet_id"] = "AIOS-HEARTBEAT-ONLY-PROOF-HARNESS-APPLY-V1"
    item["approval_evidence"]["approval_gate_packet_id"] = "AIOS-HEARTBEAT-ONLY-PROOF-HARNESS-APPLY-V1"
    item["approval_evidence"]["approval_gate_packet_mismatch"] = True
    item["approval_evidence"]["target_packet_id"] = "P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1"
    _write_json(proposal, item)

    report = gate.run_queue_mutation_gate(
        repo_root=repo_root,
        proposed_item_path=proposal,
        output_dir=tmp_path / "reports",
        now="2026-06-10T15:20:28Z",
    )

    assert report["gate_status"] == gate.BLOCKED
    assert report["approval_check"]["approval_gate_packet_mismatch"] is True
    assert "approval evidence packet_id does not match proposed queue packet_id" in report["validation"]["blockers"]


def test_duplicate_active_packet_id_is_rejected(tmp_path):
    repo_root = _make_repo(tmp_path)
    active_queue = repo_root / gate.CANONICAL_QUEUE_OWNER
    duplicate_id = "AIOS-DUPLICATE-001"
    _write_json(active_queue / f"{duplicate_id}.json", {"packet_id": duplicate_id})
    proposal = tmp_path / "proposal.json"
    _write_json(proposal, _approved_item(duplicate_id))

    report = gate.run_queue_mutation_gate(
        repo_root=repo_root,
        proposed_item_path=proposal,
        output_dir=tmp_path / "reports",
        now="2026-06-10T15:20:28Z",
    )

    assert report["gate_status"] == gate.BLOCKED
    assert report["duplicate_check"]["duplicate_packet_id"] is True
    assert "duplicate active packet ID would be created" in report["validation"]["blockers"]


def test_protected_path_target_is_rejected(tmp_path):
    repo_root = _make_repo(tmp_path)
    proposal = tmp_path / "proposal.json"
    item = _approved_item()
    item["allowed_paths"] = ["automation/orchestration/workers/inbox/"]
    _write_json(proposal, item)

    report = gate.run_queue_mutation_gate(
        repo_root=repo_root,
        proposed_item_path=proposal,
        output_dir=tmp_path / "reports",
        now="2026-06-10T15:20:28Z",
    )

    assert report["gate_status"] == gate.BLOCKED
    assert report["protected_path_check"]["protected_path_targeted"] is True
    assert "proposed item targets protected paths" in report["validation"]["blockers"]


def test_unsafe_actions_are_rejected(tmp_path):
    repo_root = _make_repo(tmp_path)
    proposal = tmp_path / "proposal.json"
    item = _approved_item()
    item["requested_action"] = "dispatch runtime execution"
    _write_json(proposal, item)

    report = gate.run_queue_mutation_gate(
        repo_root=repo_root,
        proposed_item_path=proposal,
        output_dir=tmp_path / "reports",
        now="2026-06-10T15:20:28Z",
    )

    assert report["gate_status"] == gate.BLOCKED
    assert report["unsafe_action_check"]["unsafe_action_requested"] is True
    assert "dispatch" in report["unsafe_action_check"]["matched_terms"]
    assert "runtime execution" in report["unsafe_action_check"]["matched_terms"]


def test_real_repo_protected_paths_are_not_mutated(tmp_path):
    protected_paths = [REAL_ACTIVE_QUEUE, REAL_WORKER_INBOX, REAL_APPROVAL_INBOX, REAL_COMMAND_QUEUE]
    before = {str(path): _fingerprint(path) for path in protected_paths}
    proposal = tmp_path / "proposal.json"
    _write_json(proposal, _approved_item("AIOS-REAL-REPO-PREVIEW-ONLY-001"))

    report = gate.run_queue_mutation_gate(
        repo_root=REPO_ROOT,
        proposed_item_path=proposal,
        output_dir=tmp_path / "reports",
        now="2026-06-10T15:20:28Z",
    )

    after = {str(path): _fingerprint(path) for path in protected_paths}
    assert after == before
    assert report["gate_status"] == gate.READY
    assert report["queue_write_allowed"] is False
    assert report["worker_inbox_mutation_allowed"] is False
    assert report["approval_inbox_mutation_allowed"] is False
    assert report["command_queue_mutation_allowed"] is False


def test_default_p2_evidence_loads_as_preview_without_real_queue_mutation(tmp_path):
    before = _fingerprint(REAL_ACTIVE_QUEUE)

    report = gate.run_queue_mutation_gate(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "reports",
        now="2026-06-10T15:20:28Z",
    )

    assert report["gate_status"] == gate.READY
    assert report["approval_check"]["approval_evidence_present"] is True
    assert report["approval_check"]["explicit_approval"] is True
    assert report["approval_check"]["approval_gate_packet_mismatch"] is False
    assert report["validation"]["invalid_reasons"] == []
    assert report["validation"]["blockers"] == []
    assert report["proposed_queue_item"]["allowed_paths"] == ["automation/orchestration/work_packets/"]
    assert "automation/orchestration/work_packets/active/" in report["proposed_queue_item"]["forbidden_paths"]
    assert report["queue_write_allowed"] is False
    assert report["canonical_queue_mutated"] is False
    assert report["worker_inbox_mutation_allowed"] is False
    assert report["approval_inbox_mutation_allowed"] is False
    assert report["command_queue_mutation_allowed"] is False
    assert _fingerprint(REAL_ACTIVE_QUEUE) == before
