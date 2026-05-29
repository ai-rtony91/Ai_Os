import json
import shutil
import sys
import tempfile
import unittest
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


FIXTURE = REPO_ROOT / "tests" / "orchestration" / "fixtures" / "worker_health_drills" / "worker_heartbeat_table.json"


class Gate1ControlledEvidenceDrillTests(unittest.TestCase):
    def _repo_with_fixture(self) -> Path:
        temp_dir = Path(tempfile.mkdtemp())
        runtime = temp_dir / "Reports" / "dispatcher" / "runtime" / "workers"
        runtime.mkdir(parents=True)
        shutil.copyfile(FIXTURE, runtime / "worker_heartbeat_table.json")
        return temp_dir

    def test_all_controlled_state_fixtures_classify_correctly(self) -> None:
        temp_dir = self._repo_with_fixture()
        self.addCleanup(shutil.rmtree, temp_dir)

        rows = scan_worker_health(temp_dir)
        observed = {row["worker_id"]: row["status"] for row in rows}

        expected = {
            "DRILL-ACTIVE": "ACTIVE",
            "DRILL-IDLE": "IDLE",
            "DRILL-STALE": "STALE",
            "DRILL-MISSING": "MISSING",
            "DRILL-CRASHED": "CRASHED",
            "DRILL-UNKNOWN": "UNKNOWN",
            "DRILL-STARTING": "STARTING",
            "DRILL-STOPPING": "STOPPING",
        }
        self.assertEqual(observed, expected)
        for row in rows:
            self.assertEqual(row["heartbeat_source"], "gate1_controlled_fixture")
            self.assertTrue(row["classification_reason"])

    def test_summary_exposes_review_required_evidence_matrix(self) -> None:
        temp_dir = self._repo_with_fixture()
        self.addCleanup(shutil.rmtree, temp_dir)

        summary = build_worker_health_summary(scan_worker_health(temp_dir))

        self.assertEqual(summary["worker_health_evidence_count"], 8)
        self.assertEqual(summary["worker_health_status"], "REVIEW_REQUIRED")
        self.assertEqual(summary["counts_by_status"]["ACTIVE"], 1)
        self.assertEqual(summary["counts_by_status"]["IDLE"], 1)
        self.assertEqual(summary["counts_by_status"]["STALE"], 1)
        self.assertEqual(summary["counts_by_status"]["MISSING"], 1)
        self.assertEqual(summary["counts_by_status"]["CRASHED"], 1)
        self.assertEqual(summary["counts_by_status"]["UNKNOWN"], 1)
        self.assertEqual(summary["counts_by_status"]["STARTING"], 1)
        self.assertEqual(summary["counts_by_status"]["STOPPING"], 1)
        self.assertFalse(summary["write_performed"])
        self.assertFalse(summary["dispatch_blocking"])

    def test_supervisor_v2_reports_fixture_worker_health(self) -> None:
        temp_dir = self._repo_with_fixture()
        self.addCleanup(shutil.rmtree, temp_dir)

        with patch.object(supervisor_engine_v2, "run_queue_stage", return_value=[]):
            report = supervisor_engine_v2.build_supervisor_v2_report(temp_dir)

        self.assertIn("worker_health", report)
        self.assertIn("worker_health_status", report)
        self.assertIn("worker_health_summary", report)
        self.assertIn("worker_health_evidence_count", report)
        self.assertIn("qualification_gate_hint", report)
        self.assertEqual(report["worker_health_status"], "REVIEW_REQUIRED")
        self.assertEqual(report["worker_health_evidence_count"], 8)
        self.assertFalse(report["write_performed"])
        self.assertFalse(report["worker_launch_enabled"])

    def test_false_positive_active_pretending_to_be_current_but_stale(self) -> None:
        result = classify_worker_health(
            {
                "worker_id": "DRILL-FALSE-ACTIVE",
                "status": "ACTIVE",
                "heartbeat_time": "2026-05-28T00:00:00Z",
                "stale_after_seconds": 1,
            }
        )

        self.assertEqual(result["status"], "STALE")

    def test_false_positive_stale_pretending_to_be_active(self) -> None:
        result = classify_worker_health(
            {
                "worker_id": "DRILL-FALSE-STALE",
                "status": "STALE",
                "heartbeat_time": "2026-05-29T00:00:00Z",
                "stale_after_seconds": 315360000,
            }
        )

        self.assertEqual(result["status"], "STALE")

    def test_malformed_timestamp_fails_safely(self) -> None:
        result = classify_worker_health(
            {
                "worker_id": "DRILL-BAD-TIME",
                "status": "ACTIVE",
                "heartbeat_time": "not-a-timestamp",
                "stale_after_seconds": 1800,
            }
        )

        self.assertEqual(result["status"], "UNKNOWN")

    def test_missing_worker_id_fails_safely(self) -> None:
        result = classify_worker_health(
            {
                "status": "ACTIVE",
                "heartbeat_time": "2026-05-29T00:00:00Z",
                "stale_after_seconds": 315360000,
            }
        )

        self.assertEqual(result["status"], "UNKNOWN")

    def test_unknown_state_name_fails_safely(self) -> None:
        result = classify_worker_health(
            {
                "worker_id": "DRILL-BAD-STATE",
                "status": "NOT_A_CANONICAL_STATE",
                "heartbeat_time": "2026-05-29T00:00:00Z",
                "stale_after_seconds": 315360000,
            }
        )

        self.assertEqual(result["status"], "UNKNOWN")

    def test_fixture_json_parses(self) -> None:
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "AIOS_WORKER_HEALTH_DRILL_FIXTURES.v1")
        self.assertEqual(len(payload["heartbeats"]), 8)


if __name__ == "__main__":
    unittest.main()
