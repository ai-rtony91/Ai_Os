"""Tests for the Night Supervisor autonomy chain (brainstem -> dispatch).

Standard-library unittest only (no pytest dependency). Run with:
    python3 -m unittest tests/python_supervisor/test_night_autonomy_chain.py

These tests assert the SAFETY contract: by default every effector is blocked,
and execution is only reachable when all gates are satisfied at once.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

_PKG = Path(__file__).resolve().parents[2] / "services" / "python_supervisor"
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

import action_dispatcher  # noqa: E402
import action_intent  # noqa: E402
import approval_gate  # noqa: E402
import lock_layer  # noqa: E402


READY_FLOW = [
    {
        "packet_id": "PKT-DEMO-1",
        "lane": "demo-lane",
        "worker_identity": "EAST_OCC_01",
        "packet_state": "READY_FOR_REVIEW",
        "approval_required": False,
        "next_safe_action": "Review.",
    }
]


def _write_repo(tmp: Path, *, approval: dict | None = None, lock: dict | None = None) -> Path:
    if approval is not None:
        inbox = tmp / "automation" / "orchestration" / "approval_inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        (inbox / "approval-1.json").write_text(json.dumps(approval), encoding="utf-8")
    if lock is not None:
        locks = tmp / "automation" / "orchestration" / "locks"
        locks.mkdir(parents=True, exist_ok=True)
        (locks / f"{lock['packet_id']}.lock.json").write_text(json.dumps(lock), encoding="utf-8")
    return tmp


class IntentBuilderTests(unittest.TestCase):
    def test_ready_worker_packet_proposes_assign_blocked_by_default(self):
        intents = action_intent.build_action_intents(READY_FLOW)
        self.assertEqual(len(intents), 1)
        self.assertEqual(intents[0]["effector"], "assign")
        self.assertTrue(intents[0]["blocked_by_default"])
        self.assertTrue(intents[0]["requires_approval"])

    def test_blocked_state_is_noop(self):
        flow = [{**READY_FLOW[0], "packet_state": "BLOCKED"}]
        intents = action_intent.build_action_intents(flow)
        self.assertEqual(intents[0]["effector"], "noop")
        self.assertEqual(intents[0]["risk_tier"], "read_only")


class ApprovalGateTests(unittest.TestCase):
    def test_missing_inbox_denies(self):
        with tempfile.TemporaryDirectory() as d:
            intents = action_intent.build_action_intents(READY_FLOW)
            results = approval_gate.evaluate_intents(intents, d)
            self.assertFalse(results[0]["approved"])

    def test_human_approval_grants(self):
        with tempfile.TemporaryDirectory() as d:
            _write_repo(Path(d), approval={
                "approval_id": "A1", "packet_id": "PKT-DEMO-1",
                "requested_action": "assign", "approval_status": "APPROVED",
                "approved_by_human": True, "approval_authority": "Anthony Meza",
            })
            intents = action_intent.build_action_intents(READY_FLOW)
            results = approval_gate.evaluate_intents(intents, d)
            self.assertTrue(results[0]["approved"])

    def test_non_human_record_denied(self):
        with tempfile.TemporaryDirectory() as d:
            _write_repo(Path(d), approval={
                "approval_id": "A1", "packet_id": "PKT-DEMO-1",
                "requested_action": "assign", "approval_status": "APPROVED",
                "approved_by_human": False,
            })
            intents = action_intent.build_action_intents(READY_FLOW)
            self.assertFalse(approval_gate.evaluate_intents(intents, d)[0]["approved"])


class LockLayerTests(unittest.TestCase):
    def test_free_lock_is_clear(self):
        with tempfile.TemporaryDirectory() as d:
            intents = action_intent.build_action_intents(READY_FLOW)
            self.assertTrue(lock_layer.can_act_under_lock(intents[0], d)["lock_clear"])

    def test_lock_held_by_other_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            _write_repo(Path(d), lock={"packet_id": "PKT-DEMO-1", "worker_id": "OTHER", "status": "ACTIVE"})
            intents = action_intent.build_action_intents(READY_FLOW)
            self.assertFalse(lock_layer.can_act_under_lock(intents[0], d)["lock_clear"])


class DispatcherTests(unittest.TestCase):
    def setUp(self):
        os.environ.pop(action_dispatcher.APPLY_ENV, None)
        os.environ.pop(action_dispatcher.KILL_SWITCH_ENV, None)

    def test_default_everything_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            intents = action_intent.build_action_intents(READY_FLOW)
            report = action_dispatcher.dispatch(intents, repo_root=d)
            self.assertEqual(report["would_execute_count"], 0)
            self.assertEqual(report["mode"], "DRY_RUN")

    def test_all_gates_satisfied_reaches_would_execute(self):
        with tempfile.TemporaryDirectory() as d:
            _write_repo(Path(d), approval={
                "approval_id": "A1", "packet_id": "PKT-DEMO-1",
                "requested_action": "assign", "approval_status": "APPROVED",
                "approved_by_human": True,
            })
            os.environ[action_dispatcher.APPLY_ENV] = "1"
            intents = action_intent.build_action_intents(READY_FLOW)
            report = action_dispatcher.dispatch(
                intents, repo_root=d, enabled_capabilities=["assign"], execution_enabled=True, apply=False,
            )
            self.assertEqual(report["would_execute_count"], 1)

    def test_kill_switch_blocks_even_when_armed(self):
        with tempfile.TemporaryDirectory() as d:
            _write_repo(Path(d), approval={
                "approval_id": "A1", "packet_id": "PKT-DEMO-1",
                "requested_action": "assign", "approval_status": "APPROVED",
                "approved_by_human": True,
            })
            os.environ[action_dispatcher.APPLY_ENV] = "1"
            os.environ[action_dispatcher.KILL_SWITCH_ENV] = "1"
            intents = action_intent.build_action_intents(READY_FLOW)
            report = action_dispatcher.dispatch(
                intents, repo_root=d, enabled_capabilities=["assign"], execution_enabled=True,
            )
            self.assertEqual(report["would_execute_count"], 0)
            self.assertTrue(report["kill_switch_engaged"])


if __name__ == "__main__":
    unittest.main()
