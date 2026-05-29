import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PY_SUPERVISOR_DIR = REPO_ROOT / "services" / "python_supervisor"
sys.path.insert(0, str(PY_SUPERVISOR_DIR))

from worker_route_recommender import build_route_report, recommend_routes_for_packets  # noqa: E402


class WorkerRouteRecommenderActiveOnlyTests(unittest.TestCase):
    def test_active_only_ignores_templates_examples_schemas_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            active = repo_root / "automation" / "orchestration" / "work_packets" / "active"
            templates = repo_root / "automation" / "orchestration" / "work_packets" / "templates"
            active.mkdir(parents=True)
            templates.mkdir(parents=True)
            (active / "packet.json").write_text(json.dumps({"packet_id": "ACTIVE-1", "title": "Validate report"}), encoding="utf-8")
            (templates / "template.md").write_text("PACKET ID: TEMPLATE\nImplement template", encoding="utf-8")
            (templates / "script.ps1").write_text("Write-Host should not be scanned", encoding="utf-8")

            report = build_route_report(repo_root)

            self.assertEqual(report.scanned_packet_folders, ["automation/orchestration/work_packets/active"])
            self.assertEqual(len(report.recommendations), 1)
            self.assertEqual(report.recommendations[0].packet_id, "ACTIVE-1")

    def test_accepts_queue_scanner_packet_list(self) -> None:
        packet = {
            "packet_id": "QUEUE-1",
            "source_path": "automation/orchestration/work_packets/active/queue-1.json",
            "title": "Run validation check",
            "status": "PENDING",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            routes = recommend_routes_for_packets([packet], Path(temp_dir))
            self.assertEqual(routes[0]["packet_id"], "QUEUE-1")
            self.assertEqual(routes[0]["recommended_worker"], "VALIDATOR")


if __name__ == "__main__":
    unittest.main()

