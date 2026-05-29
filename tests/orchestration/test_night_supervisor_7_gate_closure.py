import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = REPO_ROOT / "automation" / "orchestration"
PY_SUPERVISOR_DIR = REPO_ROOT / "services" / "python_supervisor"
sys.path.insert(0, str(MODULE_DIR))
sys.path.insert(0, str(PY_SUPERVISOR_DIR))

import supervisor_engine_v2  # noqa: E402
from morning_handoff_report import build_morning_handoff_preview  # noqa: E402
from multi_night_evidence_model import evaluate_multi_night_evidence  # noqa: E402
from night_supervisor_overnight_simulator import build_overnight_simulation  # noqa: E402
from packet_integrity_monitor import classify_packet_integrity  # noqa: E402
from qualification_ledger import build_promotion_package, build_qualification_entry  # noqa: E402
from recovery_awareness_monitor import classify_recovery_awareness  # noqa: E402


class NightSupervisorSevenGateClosureTests(unittest.TestCase):
    def test_gate2_packet_integrity_all_required_states(self) -> None:
        worker_health = {
            "worker_health": [
                {"worker_id": "AIOS-01", "status": "IDLE"},
                {"worker_id": "AIOS-02", "status": "STALE"},
                {"worker_id": "AIOS-03", "status": "CRASHED"},
            ]
        }
        cases = [
            (
                "HEALTHY",
                {
                    "packet_id": "p1",
                    "packet_path": "p1.json",
                    "packet_state": "ASSIGNED",
                    "assigned_worker": "AIOS-01",
                    "lock_status": "FREE",
                    "approval_status": "NOT_REQUIRED",
                },
                {},
            ),
            (
                "STALE",
                {
                    "packet_id": "p2",
                    "packet_path": "p2.json",
                    "packet_state": "ASSIGNED",
                    "assigned_worker": "AIOS-02",
                    "lock_status": "FREE",
                    "approval_status": "NOT_REQUIRED",
                },
                {},
            ),
            (
                "ABANDONED",
                {
                    "packet_id": "p3",
                    "packet_path": "p3.json",
                    "packet_state": "ASSIGNED",
                    "assigned_worker": "AIOS-03",
                    "lock_status": "FREE",
                    "approval_status": "NOT_REQUIRED",
                },
                {},
            ),
            (
                "ORPHANED",
                {
                    "packet_id": "p4",
                    "packet_path": "p4.json",
                    "packet_state": "ASSIGNED",
                    "assigned_worker": "AIOS-99",
                    "lock_status": "FREE",
                    "approval_status": "NOT_REQUIRED",
                },
                {},
            ),
            (
                "DUPLICATE_OWNER",
                {
                    "packet_id": "p5",
                    "packet_path": "p5.json",
                    "packet_state": "ASSIGNED",
                    "assigned_worker": "AIOS-01",
                    "lock_status": "FREE",
                    "approval_status": "NOT_REQUIRED",
                },
                {"AIOS-01": 2},
            ),
            (
                "OWNERSHIP_DRIFT",
                {
                    "packet_id": "p6",
                    "packet_path": "p6.json",
                    "packet_state": "ASSIGNED",
                    "assigned_worker": "AIOS-01",
                    "history": [{"assigned_worker": "AIOS-02"}],
                    "lock_status": "FREE",
                    "approval_status": "NOT_REQUIRED",
                },
                {},
            ),
            (
                "BLOCKED",
                {
                    "packet_id": "p7",
                    "packet_path": "p7.json",
                    "packet_state": "ASSIGNED",
                    "assigned_worker": "AIOS-01",
                    "lock_status": "CONFLICT",
                    "approval_status": "NOT_REQUIRED",
                },
                {},
            ),
            ("UNKNOWN", {"packet_path": "", "packet_state": "BAD"}, {}),
        ]
        for expected, packet, dupes in cases:
            with self.subTest(expected=expected):
                result = classify_packet_integrity(packet, worker_health, locks=[], approvals=[], duplicate_owner_counts=dupes)
                self.assertEqual(result["packet_integrity_status"], expected)

    def test_gate3_recovery_awareness_states(self) -> None:
        cases = [
            ("RECOVERABLE", {"case_id": "clean", "status": "STOPPING", "lock_status": "FREE", "runtime_table_status": "PRESENT"}),
            ("PARTIAL_RECOVERY", {"case_id": "lock", "worker_status": "STALE", "lock_status": "CLAIMED", "runtime_table_status": "PRESENT"}),
            ("FAILED_RECOVERY", {"case_id": "crash", "worker_status": "CRASHED", "progress_status": "UNCHANGED", "runtime_table_status": "PRESENT"}),
            ("UNKNOWN_RECOVERY", {"case_id": "unknown", "runtime_table_status": "MALFORMED"}),
        ]
        for expected, case in cases:
            with self.subTest(expected=expected):
                self.assertEqual(classify_recovery_awareness(case)["recovery_status"], expected)

    def test_gate4_overnight_simulation_is_evidence_only(self) -> None:
        result = build_overnight_simulation()

        self.assertEqual(result["cycle_count"], 6)
        self.assertEqual(result["unsafe_actions"], 0)
        self.assertFalse(result["effectors_enabled"])
        self.assertFalse(result["scheduler_enabled"])
        self.assertFalse(result["daemon_enabled"])
        self.assertIn(result["simulation_result"], {"PASS", "WARN"})

    def test_gate5_multi_night_model_rejects_fake_qualification(self) -> None:
        result = evaluate_multi_night_evidence([{"status": "PASS"} for _ in range(5)])

        self.assertEqual(result["classification"], "MODEL_READY_NOT_PASSED_REAL_WORLD")
        self.assertFalse(result["explicit_real_windows"])

    def test_gate5_multi_night_model_accepts_explicit_real_windows(self) -> None:
        result = evaluate_multi_night_evidence(
            [{"status": "PASS", "real_world_window": True} for _ in range(4)]
            + [{"status": "WARN", "real_world_window": True}]
        )

        self.assertEqual(result["classification"], "PASSED_REAL_WORLD")

    def test_gate6_morning_handoff_preview_is_fail_closed(self) -> None:
        result = build_morning_handoff_preview()

        self.assertEqual(result["actions_taken"], "NONE")
        self.assertFalse(result["effectors_enabled"])
        self.assertFalse(result["scheduler_enabled"])
        self.assertEqual(result["night_supervisor_status"], "PROVISIONAL")

    def test_gate7_promotion_package_does_not_forge_approval(self) -> None:
        entries = [
            build_qualification_entry("GATE_1", "PASS", metrics={"score": 7}),
            build_qualification_entry("GATE_2", "PASS", metrics={"score": 7}),
        ]
        package = build_promotion_package(entries, requested_status="TESTED_PENDING_REVIEW")

        self.assertEqual(package["final_qualification_status"], "TESTED_PENDING_REVIEW")
        self.assertIsNone(package["approved_by"])
        self.assertEqual(package["approval_status"], "PENDING_HUMAN_OWNER")
        self.assertTrue(package["human_owner_decision_required"])
        self.assertFalse(package["write_performed"])

    def test_gate7_forbidden_qualification_status_blocks(self) -> None:
        entry = build_qualification_entry("GATE_1", "PASS", metrics={"score": 10})
        package = build_promotion_package([entry], requested_status="QUALIFIED")

        self.assertEqual(package["final_qualification_status"], "BLOCKED")

    def test_supervisor_v2_consolidates_gate_previews_without_authority(self) -> None:
        report = supervisor_engine_v2.build_supervisor_v2_report(REPO_ROOT)

        self.assertIn("recovery_awareness_monitor", report["stage_order"])
        self.assertIn("overnight_simulation_preview", report["stage_order"])
        self.assertIn("morning_handoff_preview", report["stage_order"])
        self.assertIn("qualification_summary_preview", report["stage_order"])
        self.assertIn("recovery_awareness_summary", report)
        self.assertIn("overnight_simulation", report)
        self.assertIn("morning_handoff_preview", report)
        self.assertIn("qualification_summary", report)
        self.assertFalse(report["worker_launch_enabled"])
        self.assertFalse(report["write_performed"])
        self.assertEqual(report["qualification_summary"]["approval_status"], "PENDING_HUMAN_OWNER")


if __name__ == "__main__":
    unittest.main()
