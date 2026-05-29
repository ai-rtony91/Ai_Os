import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = REPO_ROOT / "automation" / "orchestration"
sys.path.insert(0, str(MODULE_DIR))

import supervisor_engine_v2  # noqa: E402
from worker_health_monitor import (  # noqa: E402
    build_worker_health_summary,
    classify_worker_health,
    scan_worker_health,
)


class WorkerHealthMonitorTests(unittest.TestCase):
    def test_no_runtime_tables_returns_safe_result(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            rows = scan_worker_health(temp_dir)
            summary = build_worker_health_summary(rows)

            self.assertEqual(rows, [])
            self.assertEqual(summary["worker_health_status"], "NO_EVIDENCE")
            self.assertEqual(summary["worker_health_evidence_count"], 0)
            self.assertFalse(summary["write_performed"])
            self.assertFalse(summary["dispatch_blocking"])

    def test_stale_classification_works(self) -> None:
        now = datetime(2026, 5, 29, 0, 0, tzinfo=timezone.utc)
        old = (now - timedelta(seconds=120)).isoformat().replace("+00:00", "Z")
        result = classify_worker_health(
            {
                "worker_id": "AIOS-01",
                "current_state": "IDLE",
                "heartbeat_time": old,
                "stale_after_seconds": 30,
            },
            now_utc=now,
        )

        self.assertEqual(result["status"], "STALE")
        self.assertGreater(result["observed_age_seconds"], 30)

    def test_malformed_heartbeat_returns_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "Reports" / "dispatcher" / "runtime" / "workers"
            path.mkdir(parents=True)
            heartbeat = path / "worker_heartbeat_table.json"
            heartbeat.write_text("{bad json", encoding="utf-8")

            rows = scan_worker_health(temp_dir)

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["status"], "UNKNOWN")
            self.assertIn("Malformed", rows[0]["blocked_reason"])

    def test_monitor_does_not_write_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "Reports" / "dispatcher" / "runtime" / "workers"
            path.mkdir(parents=True)
            heartbeat = path / "worker_heartbeat_table.json"
            payload = {
                "heartbeats": [
                    {
                        "worker_id": "AIOS-01",
                        "current_state": "IDLE",
                        "heartbeat_time": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                        "stale_after_seconds": 3600,
                    }
                ]
            }
            heartbeat.write_text(json.dumps(payload), encoding="utf-8")
            before = heartbeat.read_text(encoding="utf-8")

            rows = scan_worker_health(temp_dir)
            summary = build_worker_health_summary(rows)

            self.assertEqual(heartbeat.read_text(encoding="utf-8"), before)
            self.assertEqual(summary["worker_health_evidence_count"], 1)
            self.assertFalse(summary["write_performed"])

    def test_v2_report_includes_worker_health_section(self) -> None:
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

            self.assertIn("worker_health_monitor", report["stage_order"])
            self.assertIn("worker_health", report)
            self.assertIn("worker_health_status", report)
            self.assertIn("worker_health_evidence_count", report)
            self.assertIn("qualification_gate_hint", report)
            self.assertEqual(report["worker_health_status"], "NO_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
