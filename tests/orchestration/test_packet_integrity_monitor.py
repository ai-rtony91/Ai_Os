import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = REPO_ROOT / "automation" / "orchestration"
PY_SUPERVISOR_DIR = REPO_ROOT / "services" / "python_supervisor"
sys.path.insert(0, str(MODULE_DIR))
sys.path.insert(0, str(PY_SUPERVISOR_DIR))

from packet_integrity_monitor import (  # noqa: E402
    build_packet_integrity_summary,
    classify_packet_integrity,
)


class PacketIntegrityMonitorTests(unittest.TestCase):
    def test_healthy_packet_classification(self) -> None:
        packet = {
            "packet_id": "packet-1",
            "packet_path": "automation/orchestration/work_packets/active/packet-1.json",
            "packet_state": "ASSIGNED",
            "assigned_worker": "AIOS-01",
            "lock_status": "FREE",
            "approval_status": "NOT_REQUIRED",
        }
        worker_health = {"worker_health": [{"worker_id": "AIOS-01", "status": "IDLE"}]}

        result = classify_packet_integrity(packet, worker_health, locks=[], approvals=[], duplicate_owner_counts={})

        self.assertEqual(result["packet_integrity_status"], "HEALTHY")

    def test_stale_packet_classification_from_worker_health(self) -> None:
        packet = {
            "packet_id": "packet-1",
            "packet_path": "packet.json",
            "packet_state": "ASSIGNED",
            "assigned_worker": "AIOS-01",
            "lock_status": "FREE",
            "approval_status": "NOT_REQUIRED",
        }
        worker_health = {"worker_health": [{"worker_id": "AIOS-01", "status": "STALE"}]}

        result = classify_packet_integrity(packet, worker_health, locks=[], approvals=[], duplicate_owner_counts={})

        self.assertEqual(result["packet_integrity_status"], "STALE")

    def test_orphan_packet_classification(self) -> None:
        packet = {
            "packet_id": "packet-1",
            "packet_path": "packet.json",
            "packet_state": "ASSIGNED",
            "assigned_worker": "AIOS-99",
            "lock_status": "FREE",
            "approval_status": "NOT_REQUIRED",
        }
        worker_health = {"worker_health": [{"worker_id": "AIOS-01", "status": "IDLE"}]}

        result = classify_packet_integrity(packet, worker_health, locks=[], approvals=[], duplicate_owner_counts={})

        self.assertEqual(result["packet_integrity_status"], "ORPHANED")

    def test_duplicate_owner_classification(self) -> None:
        packet = {
            "packet_id": "packet-1",
            "packet_path": "packet.json",
            "packet_state": "ASSIGNED",
            "assigned_worker": "AIOS-01",
            "lock_status": "FREE",
            "approval_status": "NOT_REQUIRED",
        }
        worker_health = {"worker_health": [{"worker_id": "AIOS-01", "status": "IDLE"}]}

        result = classify_packet_integrity(
            packet,
            worker_health,
            locks=[],
            approvals=[],
            duplicate_owner_counts={"AIOS-01": 2},
        )

        self.assertEqual(result["packet_integrity_status"], "DUPLICATE_OWNER")

    def test_ownership_drift_state_is_summary_supported(self) -> None:
        summary = build_packet_integrity_summary(
            [
                {
                    "packet_integrity_status": "OWNERSHIP_DRIFT",
                    "packet_id": "packet-1",
                }
            ]
        )

        self.assertEqual(summary["counts_by_status"]["OWNERSHIP_DRIFT"], 1)
        self.assertEqual(summary["packet_integrity_status"], "REVIEW_REQUIRED")

    def test_blocked_by_lock_or_approval(self) -> None:
        packet = {
            "packet_id": "packet-1",
            "packet_path": "packet.json",
            "packet_state": "ASSIGNED",
            "assigned_worker": "AIOS-01",
            "lock_status": "CLAIMED",
            "approval_status": "NOT_REQUIRED",
        }
        worker_health = {"worker_health": [{"worker_id": "AIOS-01", "status": "IDLE"}]}

        result = classify_packet_integrity(packet, worker_health, locks=[], approvals=[], duplicate_owner_counts={})

        self.assertEqual(result["packet_integrity_status"], "BLOCKED")

    def test_missing_packet_fields_returns_unknown(self) -> None:
        result = classify_packet_integrity({}, {"worker_health": []}, locks=[], approvals=[], duplicate_owner_counts={})

        self.assertEqual(result["packet_integrity_status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
