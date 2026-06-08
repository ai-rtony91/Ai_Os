from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from automation.bridge.aios_status_model import read_json_if_exists


QUEUE_TERMS = ("queue", "inbox", "worker", "packet")
LOCK_TERMS = ("lock", "claim")
APPROVAL_TERMS = ("approval", "approve")
SOS_TERMS = ("sos", "notification", "alert")


@dataclass
class BridgeQueueInventory:
    worker_queue_files: list[str] = field(default_factory=list)
    lock_files: list[str] = field(default_factory=list)
    approval_files: list[str] = field(default_factory=list)
    sos_files: list[str] = field(default_factory=list)
    canonical_queue_present: bool = False
    canonical_approval_present: bool = False
    canonical_lock_present: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _matches(path: str, terms: tuple[str, ...]) -> bool:
    lower = path.lower()
    return any(term in lower for term in terms)


def inventory_queue_systems(repo_root: Path, tracked_files: list[str]) -> BridgeQueueInventory:
    worker_queue_files = [p for p in tracked_files if _matches(p, QUEUE_TERMS)][:200]
    lock_files = [p for p in tracked_files if _matches(p, LOCK_TERMS)][:200]
    approval_files = [p for p in tracked_files if _matches(p, APPROVAL_TERMS)][:200]
    sos_files = [p for p in tracked_files if _matches(p, SOS_TERMS)][:200]
    canonical_queue = repo_root / "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"
    canonical_approval = repo_root / "automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json"
    canonical_lock = repo_root / "automation/orchestration/assignment_locks.example.json"
    return BridgeQueueInventory(
        worker_queue_files=worker_queue_files,
        lock_files=lock_files,
        approval_files=approval_files,
        sos_files=sos_files,
        canonical_queue_present=canonical_queue.exists(),
        canonical_approval_present=canonical_approval.exists(),
        canonical_lock_present=canonical_lock.exists(),
    )


def load_known_state(repo_root: Path) -> dict[str, object]:
    return {
        "worker_inbox": read_json_if_exists(repo_root / "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"),
        "approval_inbox": read_json_if_exists(repo_root / "automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json"),
        "apply_approval_gate": read_json_if_exists(repo_root / "automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json"),
        "command_queue": read_json_if_exists(repo_root / "automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json"),
    }

