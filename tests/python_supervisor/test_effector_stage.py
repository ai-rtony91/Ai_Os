"""Tests for the Night Supervisor effector layer (downstream of Codex V2).

Standard-library unittest only. Run with:
    python3 -m unittest tests/python_supervisor/test_effector_stage.py

These tests feed synthetic Codex routing_contracts (the spine output) and assert
the SAFETY contract: by default every effector is blocked, and execution is only
reachable when all gates pass at once. They do not re-test approval/lock reading,
which is owned by the Codex spine (approval_officer / lock_manager).
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

_PKG = Path(__file__).resolve().parents[2] / "services" / "python_supervisor"
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

import effector_dispatcher  # noqa: E402
import effector_intent  # noqa: E402


def _contract(**overrides):
    base = {
        "packet_id": "PKT-DEMO-1",
        "packet_state": "ASSIGNED",
        "assigned_worker": "EAST_OCC_01",
        "dispatch_status": "DRY_RUN_PREVIEW",
        "approval_status": "APPROVED",
        "lock_status": "FREE",
        "dispatch_mode": "DRY_RUN",
    }
    base.update(overrides)
    return base


class IntentBuilderTests(unittest.TestCase):
    def test_approved_assigned_contract_proposes_assign(self):
        intents = effector_intent.build_effector_intents([_contract()])
        self.assertEqual(len(intents), 1)
        self.assertEqual(intents[0]["effector"], "assign")
        self.assertTrue(intents[0]["blocked_by_default"])
        self.assertEqual(intents[0]["source_contract"]["approval_status"], "APPROVED")

    def test_unassigned_contract_is_noop(self):
        intents = effector_intent.build_effector_intents([_contract(assigned_worker="", recommended_worker="")])
        self.assertEqual(intents[0]["effector"], "noop")
        self.assertEqual(intents[0]["risk_tier"], "read_only")

    def test_complete_contract_proposes_mark_done(self):
        intents = effector_intent.build_effector_intents([_contract(packet_state="COMPLETE")])
        self.assertEqual(intents[0]["effector"], "mark_done")


class DispatcherGateTests(unittest.TestCase):
    def setUp(self):
        os.environ.pop(effector_dispatcher.APPLY_ENV, None)
        os.environ.pop(effector_dispatcher.KILL_SWITCH_ENV, None)

    def test_default_everything_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            intents = effector_intent.build_effector_intents([_contract()])
            report = effector_dispatcher.dispatch(intents, repo_root=d)
            self.assertEqual(report["would_execute_count"], 0)
            self.assertEqual(report["mode"], "DRY_RUN")

    def test_all_gates_satisfied_reaches_would_execute(self):
        with tempfile.TemporaryDirectory() as d:
            os.environ[effector_dispatcher.APPLY_ENV] = "1"
            intents = effector_intent.build_effector_intents([_contract()])
            report = effector_dispatcher.dispatch(
                intents, repo_root=d, enabled_capabilities=["assign"], execution_enabled=True, apply=False,
            )
            self.assertEqual(report["would_execute_count"], 1)

    def test_uncleared_contract_blocks_even_when_armed(self):
        with tempfile.TemporaryDirectory() as d:
            os.environ[effector_dispatcher.APPLY_ENV] = "1"
            # Spine did NOT clear it (lock claimed).
            intents = effector_intent.build_effector_intents([_contract(dispatch_status="BLOCKED_BY_LOCK", lock_status="CLAIMED")])
            report = effector_dispatcher.dispatch(
                intents, repo_root=d, enabled_capabilities=["assign"], execution_enabled=True,
            )
            self.assertEqual(report["would_execute_count"], 0)
            self.assertIn("contract_cleared", report["decisions"][0]["blocking_gates"])

    def test_kill_switch_overrides_everything(self):
        with tempfile.TemporaryDirectory() as d:
            os.environ[effector_dispatcher.APPLY_ENV] = "1"
            os.environ[effector_dispatcher.KILL_SWITCH_ENV] = "1"
            intents = effector_intent.build_effector_intents([_contract()])
            report = effector_dispatcher.dispatch(
                intents, repo_root=d, enabled_capabilities=["assign"], execution_enabled=True,
            )
            self.assertEqual(report["would_execute_count"], 0)
            self.assertTrue(report["kill_switch_engaged"])


if __name__ == "__main__":
    unittest.main()
