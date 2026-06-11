"""Tests for the final autonomy loop status helper."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
STATUS_HELPER = (
    REPO_ROOT / "automation" / "orchestration" / "autonomy_reports"
    / "aios_final_autonomy_loop_status.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("aios_final_autonomy_loop_status", STATUS_HELPER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _full_status(**overrides):
    m = _load()
    base = {
        "evidence_ledger_digest": {"schema": "AIOS_SELF_BUILD_EVIDENCE_LEDGER.v1", "total_cycles": 2},
        "pr_backlog_reconciliation": {"schema": "AIOS_OPEN_PR_BACKLOG_RECONCILIATION.v1"},
        "human_gate_evidence": {"notes": "STOP drill proof chain v2 was consumed"},
        "available_modules": {
            "self_build_evidence_ledger_present": True,
            "decision_packet_drafter_present": True,
            "pr_backlog_reconciliation_present": True,
            "t9_recursion_guard_present": True,
        },
        "validation_results": {
            "validators_present": True,
            "final_status_helper_tests_pass": True,
        },
        "current_repo_state": {"current_main_head": "abc123"},
    }
    base.update(overrides)
    return m.build_final_autonomy_loop_status(**base)


def test_readiness_percent_is_capped_at_85():
    status = _full_status(
        human_gate_evidence={
            "notes": (
                "STOP drill proof chain v2 was consumed. "
                "runtime launch is approved by Anthony. "
                "runtime execution is approved by Anthony. "
                "queue mutation is approved by Anthony."
            )
        }
    )
    assert status["self_build_readiness_percent"] == 85


def test_broker_and_live_trading_always_blocked():
    status = _full_status()
    assert status["broker_action_status"] == "BLOCKED"
    assert status["live_trading_status"] == "BLOCKED"
    assert status["can_execute_live_trading"] is False


def test_runtime_execution_blocked_without_approval():
    status = _full_status(human_gate_evidence={})
    assert status["runtime_launch_status"] == "BLOCKED"
    assert status["runtime_execution_status"] == "BLOCKED"
    assert status["can_mutate_protected_runtime"] is False


def test_queue_mutation_blocked_without_approval():
    status = _full_status(human_gate_evidence={})
    assert status["queue_mutation_status"] == "BLOCKED"
    assert "Queue mutation approval" in status["remaining_blockers"]


def test_sos_remains_blocked_without_delivery_confirmation():
    status = _full_status(human_gate_evidence={"notes": "STOP drill proof chain v2 was consumed"})
    assert status["sos_delivery_status"] == "BLOCKED"
    assert "SOS delivery" in status["remaining_blockers"]


def test_scheduler_remains_blocked_without_manual_confirmation():
    status = _full_status(human_gate_evidence={"notes": "STOP drill proof chain v2 was consumed"})
    assert status["scheduler_registration_status"] == "BLOCKED"
    assert "Scheduler manual registration" in status["remaining_blockers"]


def test_stop_proof_can_be_marked_consumed():
    status = _full_status(human_gate_evidence={"notes": "STOP drill proof chain v2 was consumed"})
    assert status["stop_drill_status"] == "PROOF_CONSUMED"


def test_output_is_json_serializable():
    status = _full_status()
    dumped = json.dumps(status, sort_keys=True)
    assert "AIOS_FINAL_AUTONOMY_LOOP_STATUS.v1" in dumped


def test_out_rejects_paths_outside_reports_autonomy_loop_closure(tmp_path):
    m = _load()
    status = _full_status()
    outside = tmp_path / "outside.json"
    res = m.write_status(status, outside, repo_root=tmp_path)
    assert res["written"] is False
    assert res["status"] == "BLOCKED_OUTSIDE_ALLOWED_REPORT_DIR"
    assert not outside.exists()


def test_out_allows_reports_autonomy_loop_closure(tmp_path):
    m = _load()
    status = _full_status()
    out = tmp_path / "Reports" / "autonomy_loop_closure" / "status.json"
    res = m.write_status(status, out, repo_root=tmp_path)
    assert res["written"] is True
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "AIOS_FINAL_AUTONOMY_LOOP_STATUS.v1"


def test_no_protected_mutation_function_exists():
    m = _load()
    protected_names = [
        "mutate_queue",
        "mutate_approval",
        "launch_runtime",
        "execute_runtime",
        "register_scheduler",
        "send_sos",
        "broker_action",
        "execute_live_trade",
    ]
    for name in protected_names:
        assert not hasattr(m, name)


def test_governed_self_build_ready_is_not_runtime_ready():
    status = _full_status()
    assert status["self_build_readiness"] == "READY_FOR_GOVERNED_CONTINUATION"
    assert status["self_build_readiness_percent"] == 85
    assert status["autonomy_loop_stage"] == "GOVERNED_SELF_BUILD_READY"
    assert status["can_generate_evidence_digest"] is True
    assert status["can_generate_packet_draft"] is True
    assert status["can_propose_next_work"] is True
    assert status["can_validate_next_work"] is True
    assert status["can_mutate_protected_runtime"] is False
    assert status["can_execute_live_trading"] is False
