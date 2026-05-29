import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "services" / "python_supervisor" / "worker_route_recommender.py"
REPORT_PATH = Path("automation/orchestration/worker_routing/latest_worker_route_recommendation.json")


def run_recommender(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--repo-root", str(repo_root), *args],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=str(path), capture_output=True, text=True, check=True)


def write_packet(repo_root: Path, relative_path: str, text: str) -> None:
    packet_path = repo_root / relative_path
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(text, encoding="utf-8")


class WorkerRouteRecommenderTests(unittest.TestCase):
    def test_pretty_outputs_readable_json_without_writing_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            init_git_repo(repo_root)
            write_packet(
                repo_root,
                "automation/orchestration/work_packets/sample.md",
                "PACKET ID: TEST-APPLY\nMODE: APPLY\nImplement script tests.",
            )

            result = run_recommender(repo_root, "--pretty")

            self.assertEqual(result.returncode, 0)
            self.assertIn("\n  ", result.stdout)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["schema"], "AIOS_WORKER_ROUTE_RECOMMENDER.v1")
            self.assertFalse((repo_root / REPORT_PATH).exists())

    def test_write_report_writes_only_when_explicitly_requested(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            init_git_repo(repo_root)
            write_packet(
                repo_root,
                "work_packets/review.md",
                "PACKET ID: TEST-REVIEW\nDRY_RUN review architecture risk.",
            )

            no_write = run_recommender(repo_root, "--pretty")
            self.assertEqual(no_write.returncode, 0)
            self.assertFalse((repo_root / REPORT_PATH).exists())

            with_write = run_recommender(repo_root, "--pretty", "--write-report")

            self.assertEqual(with_write.returncode, 0)
            report_path = repo_root / REPORT_PATH
            self.assertTrue(report_path.exists())
            self.assertEqual(
                json.loads(report_path.read_text(encoding="utf-8")),
                json.loads(with_write.stdout),
            )

    def test_output_contains_expected_route_recommendation_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            init_git_repo(repo_root)
            write_packet(
                repo_root,
                "automation/orchestration/work_packets/validate.md",
                "PACKET ID: TEST-VALIDATE\nRun validation parse test check audit.",
            )

            result = run_recommender(repo_root, "--pretty")

            self.assertEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            recommendation = payload["recommendations"][0]
            self.assertEqual(recommendation["packet_id"], "TEST-VALIDATE")
            self.assertEqual(
                recommendation["file_path"],
                "automation/orchestration/work_packets/validate.md",
            )
            self.assertEqual(recommendation["recommended_worker"], "VALIDATOR")
            self.assertTrue(recommendation["reason"])
            self.assertEqual(recommendation["risk_level"], "MEDIUM")
            self.assertEqual(recommendation["blocked_actions"], [])
            self.assertTrue(recommendation["next_safe_action"])
            self.assertIs(recommendation["needs_human_approval"], False)

    def test_missing_repo_root_fails_closed_with_json_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_repo = Path(temp_dir) / "missing"

            result = run_recommender(missing_repo, "--pretty")

            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            recommendation = payload["recommendations"][0]
            self.assertTrue(payload["git_state"]["git_error"])
            self.assertEqual(recommendation["recommended_worker"], "HUMAN_OWNER")
            self.assertEqual(recommendation["risk_level"], "HIGH")
            self.assertIs(recommendation["needs_human_approval"], True)
            self.assertFalse((Path(temp_dir) / REPORT_PATH).exists())


if __name__ == "__main__":
    unittest.main()
