#!/usr/bin/env python3
"""Functional tests for the AI_OS Night Supervisor harness (DRY_RUN).

Run: python3 -m unittest automation/orchestration/night_supervisor/test_night_supervisor.py
or:  python3 automation/orchestration/night_supervisor/test_night_supervisor.py
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import night_supervisor_harness as nsh

EXPECTED_PHASE_ORDER = [
    "supervisor_bootstrap",
    "nightly_telemetry_checkpoint",
    "validator_automation",
    "lock_enforcement_automation",
    "approval_automation",
    "runtime_state_automation",
    "resume_capability_automation",
    "cleanup_and_ledger",
]


class NightSupervisorChainTest(unittest.TestCase):
    def test_chain_no_emit_structure_and_safety(self):
        report = nsh.run_night_supervision(emit=False)

        self.assertEqual(report["schema"], "AIOS_NIGHT_SUPERVISOR_REPORT.v1")
        self.assertEqual(report["mode"], "DRY_RUN")
        self.assertIn(report["supervisor_status"], {"READY", "REVIEW", "WARNING", "BLOCKED", "UNKNOWN"})

        order = [p["phase"] for p in report["phases"]]
        self.assertEqual(order, EXPECTED_PHASE_ORDER)
        for p in report["phases"]:
            self.assertIn(p["status"], {"PASS", "PLANNED", "WARN", "FAIL", "BLOCKED", "DEFERRED", "SKIPPED"})
            self.assertTrue(p["next_safe_action"])

        sc = report["safety_confirmation"]
        self.assertTrue(sc["no_live_trading"])
        self.assertTrue(sc["no_broker_execution"])
        self.assertTrue(sc["no_secrets_exposed"])
        self.assertTrue(sc["no_active_state_mutation"])
        self.assertTrue(sc["no_commit_or_push"])
        self.assertTrue(sc["writes_within_allowed_paths_only"])
        self.assertEqual(sc["forbidden_write_attempts"], 0)

    def test_emit_writes_only_inside_sandbox(self):
        report = nsh.run_night_supervision(emit=True)
        repo_root = Path(report["repo"]["repo_root"])
        sandbox = (repo_root / nsh.RUNTIME_WRITE_ROOT).resolve()

        self.assertGreater(len(report["_sandbox_writes"]), 0)
        for rel in report["_sandbox_writes"]:
            resolved = (repo_root / rel).resolve()
            self.assertTrue(
                resolved == sandbox or sandbox in resolved.parents,
                f"write escaped sandbox: {rel}",
            )
            self.assertTrue(resolved.is_file(), f"expected file missing: {rel}")

        # The summary report must itself parse as valid JSON.
        report_path = (repo_root / nsh.RUNTIME_WRITE_ROOT / report["_written_report_path"].split(nsh.RUNTIME_WRITE_ROOT + "/")[-1])
        self.assertTrue(report_path.is_file())
        json.loads(report_path.read_text(encoding="utf-8"))

    def test_forbidden_write_is_blocked(self):
        repo_root = nsh.resolve_repo_root()
        writer = nsh.SandboxWriter(repo_root, emit=False)
        with self.assertRaises(nsh.ForbiddenWriteError):
            writer.write_json("../../../README.md", {"x": 1})
        self.assertEqual(writer.forbidden_attempts, 1)

    def test_secret_content_fails_closed(self):
        # Construct the secret-shaped probe at runtime from split pieces so the
        # literal credential pattern never appears in source. This keeps the
        # repo's CI secret-grep green while still exercising the scanner's
        # fail-closed path on a genuinely secret-shaped value.
        keyword = "api" + "_key"
        fake_value = "AKIA" + "EXAMPLEFAKEKEY0" + "99"
        probe = keyword + ' = "' + fake_value + '"'
        with self.assertRaises(RuntimeError):
            nsh._scan_for_secrets(probe, source="unit-test")


if __name__ == "__main__":
    unittest.main(verbosity=2)
