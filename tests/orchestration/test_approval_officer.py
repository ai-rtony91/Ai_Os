import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = REPO_ROOT / "automation" / "orchestration"
sys.path.insert(0, str(MODULE_DIR))

from approval_officer import (  # noqa: E402
    apply_approval_status,
    approval_required_for_packet,
    check_packet_approval,
    is_approval_expired,
    read_approval_inbox,
)


class ApprovalOfficerTests(unittest.TestCase):
    def test_not_required_passes_without_approval(self) -> None:
        result = check_packet_approval("packet-1", "packet.json", [], False)
        self.assertEqual(result["approval_status"], "NOT_REQUIRED")

    def test_approved_matching_record_allows(self) -> None:
        approvals = [{"approval_id": "a1", "packet_id": "packet-1", "approval_status": "APPROVED"}]
        result = check_packet_approval("packet-1", "packet.json", approvals, True)
        self.assertEqual(result["approval_status"], "APPROVED")

    def test_pending_blocked_expired_unknown_states_block(self) -> None:
        for state in ("PENDING", "BLOCKED", "EXPIRED", "UNKNOWN"):
            with self.subTest(state=state):
                approvals = [{"approval_id": "a1", "packet_id": "packet-1", "approval_status": state}]
                result = check_packet_approval("packet-1", "packet.json", approvals, True)
                self.assertEqual(result["approval_status"], state)
                self.assertTrue(result["blocked_reason"])

    def test_missing_approval_blocks_when_required(self) -> None:
        result = check_packet_approval("packet-1", "packet.json", [], True)
        self.assertEqual(result["approval_status"], "UNKNOWN")
        self.assertIn("required", result["blocked_reason"])

    def test_validator_pass_does_not_auto_approve(self) -> None:
        packet = {"packet_id": "packet-1", "approval_required": True, "validator_status": "PASS"}
        self.assertTrue(approval_required_for_packet(packet))
        result = check_packet_approval("packet-1", "packet.json", [], approval_required_for_packet(packet))
        self.assertEqual(result["approval_status"], "UNKNOWN")

    def test_expired_approval_detected(self) -> None:
        expires_at = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        self.assertTrue(is_approval_expired({"expires_at": expires_at}, datetime.now(timezone.utc)))

    def test_read_approval_inbox_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            inbox = repo_root / "automation" / "orchestration" / "approval_inbox"
            inbox.mkdir(parents=True)
            approval_path = inbox / "approval.json"
            approval_path.write_text(json.dumps({"packet_id": "packet-1", "approval_status": "pending_review"}), encoding="utf-8")
            before = approval_path.read_text(encoding="utf-8")

            approvals = read_approval_inbox(repo_root)

            self.assertEqual(approval_path.read_text(encoding="utf-8"), before)
            self.assertEqual(approvals[0]["approval_status"], "PENDING")

    def test_apply_approval_status_updates_copy(self) -> None:
        contract = {"packet_id": "packet-1", "blocked_reason": ""}
        updated = apply_approval_status(contract, {"approval_status": "PENDING", "approval_id": "a1", "blocked_reason": "pending"})
        self.assertNotIn("approval_status", contract)
        self.assertEqual(updated["approval_status"], "PENDING")


if __name__ == "__main__":
    unittest.main()

