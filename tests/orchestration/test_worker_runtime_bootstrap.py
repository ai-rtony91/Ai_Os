import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_DIR = REPO_ROOT / "automation" / "orchestration"
sys.path.insert(0, str(MODULE_DIR))

from worker_runtime_bootstrap import initialize_worker_runtime_tables  # noqa: E402


class WorkerRuntimeBootstrapTests(unittest.TestCase):
    def _write_profiles(self, root: Path) -> None:
        path = root / "automation" / "orchestration" / "workers"
        path.mkdir(parents=True)
        (path / "AIOS_WORKER_PROFILES.json").write_text(
            json.dumps(
                {
                    "workers": [
                        {
                            "worker_id": "AIOS-01",
                            "display_title": "AIOS One",
                            "worker_type": "manual_codex",
                            "default_branch": "phase-test",
                        },
                        {
                            "worker_id": "AIOS-02",
                            "display_title": "AIOS Two",
                            "worker_type": "validation",
                            "default_branch": "phase-test",
                        },
                    ]
                }
            ),
            encoding="utf-8",
        )

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_profiles(root)

            result = initialize_worker_runtime_tables(root)

            self.assertEqual(result["mode"], "DRY_RUN")
            self.assertFalse(result["write_performed"])
            self.assertEqual(result["worker_count"], 2)
            self.assertFalse((root / "Reports").exists())

    def test_apply_creates_exactly_four_runtime_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_profiles(root)

            result = initialize_worker_runtime_tables(root, apply=True)

            self.assertTrue(result["write_performed"])
            self.assertEqual(len(result["created_files"]), 4)
            for relative_path in result["created_files"]:
                payload = json.loads((root / relative_path).read_text(encoding="utf-8"))
                self.assertIsInstance(payload, dict)

    def test_existing_files_are_not_overwritten_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_profiles(root)
            runtime = root / "Reports" / "dispatcher" / "runtime" / "workers"
            runtime.mkdir(parents=True)
            existing = runtime / "worker_heartbeat_table.json"
            existing.write_text('{"schema":"existing"}\n', encoding="utf-8")

            result = initialize_worker_runtime_tables(root, apply=True)

            self.assertIn("Reports/dispatcher/runtime/workers/worker_heartbeat_table.json", result["existing_files"])
            self.assertEqual(existing.read_text(encoding="utf-8"), '{"schema":"existing"}\n')

    def test_initialized_workers_are_not_active(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_profiles(root)

            initialize_worker_runtime_tables(root, apply=True)
            active = json.loads(
                (root / "Reports" / "dispatcher" / "runtime" / "workers" / "active_worker_table.json").read_text(
                    encoding="utf-8"
                )
            )
            heartbeat = json.loads(
                (root / "Reports" / "dispatcher" / "runtime" / "workers" / "worker_heartbeat_table.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertTrue(all(row["current_state"] != "ACTIVE" for row in active["workers"]))
            self.assertTrue(all(row["status"] != "ACTIVE" for row in heartbeat["heartbeats"]))

    def test_output_includes_safety_flags_false(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_profiles(root)

            result = initialize_worker_runtime_tables(root, apply=True)

            self.assertFalse(result["worker_launch_enabled"])
            self.assertFalse(result["daemon_enabled"])
            self.assertFalse(result["scheduler_enabled"])
            self.assertFalse(result["effector_enabled"])
            self.assertFalse(result["qualification_ledger_write_enabled"])
            self.assertFalse(result["git_write_enabled"])


if __name__ == "__main__":
    unittest.main()
