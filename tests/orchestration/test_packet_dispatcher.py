import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = REPO_ROOT / "automation" / "orchestration"
sys.path.insert(0, str(MODULE_DIR))

from packet_dispatcher import (  # noqa: E402
    build_dispatch_preview,
    can_dispatch,
    dispatch_packets,
    write_dispatch_receipt,
    write_worker_inbox_entry,
)


def base_contract() -> dict:
    return {
        "packet_id": "packet-1",
        "packet_path": "automation/orchestration/work_packets/active/packet-1.json",
        "recommended_worker": "dispatcher",
        "assigned_worker": "dispatcher",
        "routing_source": "combined",
        "routing_confidence": "MEDIUM",
        "lock_status": "FREE",
        "approval_required": False,
        "approval_status": "NOT_REQUIRED",
        "approval_id": "",
        "risk_level": "LOW",
        "dispatch_mode": "DRY_RUN",
    }


class PacketDispatcherTests(unittest.TestCase):
    def test_dry_run_returns_preview(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            receipt = build_dispatch_preview(base_contract(), Path(temp_dir))
            self.assertEqual(receipt["dispatch_status"], "DRY_RUN_PREVIEW")
            self.assertFalse(receipt["write_performed"])

    def test_apply_enabled_false_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            receipt = build_dispatch_preview(base_contract(), repo_root)
            written = write_dispatch_receipt(receipt, repo_root, apply_enabled=False)
            inbox = write_worker_inbox_entry(base_contract(), receipt, repo_root, apply_enabled=False)
            self.assertFalse(written["write_performed"])
            self.assertFalse(inbox["write_performed"])
            self.assertFalse((repo_root / "automation" / "orchestration" / "dispatch_receipts").exists())
            self.assertFalse((repo_root / "automation" / "orchestration" / "worker_inboxes").exists())

    def test_blocked_by_lock(self) -> None:
        contract = {**base_contract(), "lock_status": "CLAIMED"}
        allowed, reason = can_dispatch(contract)
        self.assertFalse(allowed)
        self.assertIn("lock", reason.lower())
        self.assertEqual(build_dispatch_preview(contract, Path("."))["dispatch_status"], "BLOCKED_BY_LOCK")

    def test_blocked_by_approval(self) -> None:
        contract = {**base_contract(), "approval_required": True, "approval_status": "PENDING"}
        self.assertEqual(build_dispatch_preview(contract, Path("."))["dispatch_status"], "BLOCKED_BY_APPROVAL")

    def test_blocked_by_risk(self) -> None:
        contract = {**base_contract(), "risk_level": "CRITICAL", "approval_status": "NOT_REQUIRED"}
        self.assertEqual(build_dispatch_preview(contract, Path("."))["dispatch_status"], "BLOCKED_BY_RISK")

    def test_dispatch_receipt_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            receipts = dispatch_packets([base_contract()], Path(temp_dir), apply_enabled=False)
            receipt = receipts[0]
            self.assertIn("dispatch_receipt_id", receipt)
            self.assertIn("route_evidence", receipt)
            self.assertIn("lock_evidence", receipt)
            self.assertIn("approval_evidence", receipt)


if __name__ == "__main__":
    unittest.main()

