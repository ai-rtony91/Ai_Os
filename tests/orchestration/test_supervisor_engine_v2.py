import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = REPO_ROOT / "automation" / "orchestration"
sys.path.insert(0, str(MODULE_DIR))

import supervisor_engine_v2  # noqa: E402


class SupervisorEngineV2Tests(unittest.TestCase):
    def test_returns_report_and_stage_order_without_default_writes(self) -> None:
        packet = {
            "packet_id": "packet-1",
            "source_path": "automation/orchestration/work_packets/active/packet-1.json",
            "title": "Packet One",
            "status": "PENDING",
            "risk_level": "LOW",
            "approval_required": False,
            "related_files": [],
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(supervisor_engine_v2, "run_queue_stage", return_value=[packet]):
                report = supervisor_engine_v2.build_supervisor_v2_report(Path(temp_dir))

            self.assertEqual(report["stage_order"][0], "queue_scanner")
            self.assertEqual(report["stage_order"][-1], "telemetry_preview")
            self.assertIn("worker_health_monitor", report["stage_order"])
            self.assertIn("packet_integrity_monitor", report["stage_order"])
            self.assertFalse(report["write_performed"])
            self.assertFalse(report["worker_launch_enabled"])
            self.assertFalse(report["packet_integrity_summary"]["write_performed"])
            self.assertEqual(report["routing_contracts"][0]["telemetry_status"], "DRY_RUN_PREVIEW")
            self.assertNotEqual(report["routing_contracts"][0]["dispatch_status"], "DISPATCHED")
            self.assertNotEqual(report["qualification_gate_hint"], "GATE_1_PASSED")
            self.assertNotEqual(report["qualification_gate_2_hint"], "GATE_2_PASSED")

    def test_preserves_blocked_reason(self) -> None:
        contract = {
            "packet_id": "packet-1",
            "packet_path": "packet.json",
            "packet_title": "Packet",
            "packet_state": "PENDING",
            "source": "queue_scanner",
            "risk_level": "LOW",
            "risk_reasons": [],
            "recommended_worker": "dispatcher",
            "assigned_worker": "dispatcher",
            "routing_source": "combined",
            "routing_confidence": "MEDIUM",
            "lock_status": "CLAIMED",
            "lock_owner": "worker",
            "lock_id": "lock-1",
            "approval_required": False,
            "approval_status": "NOT_REQUIRED",
            "approval_id": "",
            "dispatch_status": "NOT_READY",
            "dispatch_mode": "DRY_RUN",
            "dispatch_receipt_id": "",
            "telemetry_status": "NOT_WRITTEN",
            "blocked_reason": "Active lock claims this packet or path.",
            "timestamp": "2026-05-28T00:00:00Z",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            receipts = supervisor_engine_v2.run_dispatch_stage([contract], Path(temp_dir), apply_enabled=False)
            self.assertEqual(receipts[0]["dispatch_status"], "BLOCKED_BY_LOCK")
            self.assertFalse((Path(temp_dir) / "automation" / "orchestration" / "dispatch_receipts").exists())


if __name__ == "__main__":
    unittest.main()
