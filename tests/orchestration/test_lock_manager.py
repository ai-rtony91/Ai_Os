import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = REPO_ROOT / "automation" / "orchestration"
sys.path.insert(0, str(MODULE_DIR))

from lock_manager import apply_lock_status, check_packet_lock, is_lock_expired, scan_locks  # noqa: E402


class LockManagerTests(unittest.TestCase):
    def test_free_when_no_matching_lock(self) -> None:
        result = check_packet_lock("packet-1", "automation/x.json", [])
        self.assertEqual(result["lock_status"], "FREE")

    def test_claimed_matching_lock_blocks(self) -> None:
        result = check_packet_lock(
            "packet-1",
            "automation/x.json",
            [{"lock_id": "lock-1", "packet_id": "packet-1", "status": "ACTIVE", "owner": "worker"}],
        )
        self.assertEqual(result["lock_status"], "CLAIMED")
        self.assertIn("Active lock", result["blocked_reason"])

    def test_conflict_when_multiple_active_locks_match(self) -> None:
        locks = [
            {"lock_id": "lock-1", "packet_id": "packet-1", "status": "ACTIVE", "owner": "a"},
            {"lock_id": "lock-2", "packet_id": "packet-1", "status": "ACTIVE", "owner": "b"},
        ]
        result = check_packet_lock("packet-1", "automation/x.json", locks)
        self.assertEqual(result["lock_status"], "CONFLICT")

    def test_expired_lock_is_not_free(self) -> None:
        expired = (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
        lock = {"lock_id": "lock-1", "packet_id": "packet-1", "status": "ACTIVE", "expires_at": expired}
        self.assertTrue(is_lock_expired(lock, datetime.now(timezone.utc)))
        result = check_packet_lock("packet-1", "automation/x.json", [lock])
        self.assertEqual(result["lock_status"], "EXPIRED")

    def test_unknown_matching_lock_blocks_as_unknown(self) -> None:
        result = check_packet_lock("packet-1", "automation/x.json", [{"lock_id": "lock-1", "packet_id": "packet-1"}])
        self.assertEqual(result["lock_status"], "UNKNOWN")

    def test_malformed_lock_file_safe_handling_and_no_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            lock_dir = repo_root / "automation" / "orchestration" / "locks"
            lock_dir.mkdir(parents=True)
            lock_path = lock_dir / "bad.lock.json"
            lock_path.write_text("{bad json", encoding="utf-8")
            before = lock_path.read_text(encoding="utf-8")

            locks = scan_locks(repo_root)

            self.assertEqual(lock_path.read_text(encoding="utf-8"), before)
            self.assertEqual(locks[0]["status"], "UNKNOWN")

    def test_apply_lock_status_updates_contract_only(self) -> None:
        contract = {"packet_id": "packet-1", "blocked_reason": ""}
        updated = apply_lock_status(contract, {"lock_status": "CLAIMED", "lock_owner": "worker", "lock_id": "lock-1", "blocked_reason": "blocked"})
        self.assertEqual(contract.get("lock_status"), None)
        self.assertEqual(updated["lock_status"], "CLAIMED")


if __name__ == "__main__":
    unittest.main()

