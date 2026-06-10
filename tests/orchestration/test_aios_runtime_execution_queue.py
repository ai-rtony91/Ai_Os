"""Tests for the AI_OS runtime execution queue (observe-only manifest)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
QUEUE = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "runtime_closure"
    / "aios_runtime_execution_queue.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("aios_runtime_execution_queue", QUEUE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _queue(**state):
    m = _load()
    return m.build_runtime_execution_queue(state or None)


def _lane(queue: dict, lane_id: str) -> dict:
    return next(lane for lane in queue["lanes"] if lane["lane_id"] == lane_id)


def test_default_queue_has_all_seven_lanes():
    q = _queue()
    assert len(q["lanes"]) == 7
    assert [lane["lane_id"] for lane in q["lanes"]] == [
        "relay_runtime_processor",
        "restart_supervisor_timeouts",
        "jsonl_rotation_retention",
        "soak_endurance_proof",
        "stop_drill_recovery_proof",
        "human_sos_arming",
        "human_scheduler_registration",
    ]


def test_strict_serial_order_exact():
    m = _load()
    q = m.build_runtime_execution_queue()
    assert q["next_strict_serial_order"] == [
        "relay_runtime_processor",
        "restart_supervisor_timeouts",
        "jsonl_rotation_retention",
        "soak_endurance_proof",
        "stop_drill_recovery_proof",
        "human_sos_arming",
        "human_scheduler_registration",
    ]


def test_every_lane_has_producer_and_consumer_fields():
    q = _queue()
    for lane in q["lanes"]:
        assert lane["producer"]
        assert lane["consumer"]
        assert lane["consumes_from"]
        assert lane["consumed_by"]


def test_every_lane_has_hard_gates_and_forbidden_actions():
    q = _queue()
    for lane in q["lanes"]:
        assert lane["hard_gates"]
        assert lane["forbidden_actions"]
        assert lane["vacation_mode_blocker"] is True


def test_vacation_mode_complete_is_false_by_default():
    q = _queue()
    assert q["vacation_mode_complete"] is False


def test_cloud_buildable_lane_complete_tracks_ledger_state():
    m = _load()
    default_q = m.build_runtime_execution_queue()
    false_q = m.build_runtime_execution_queue({"ledger_on_main": False})
    assert default_q["cloud_buildable_lane_complete"] is True
    assert false_q["cloud_buildable_lane_complete"] is False


def test_relay_lane_requires_approval_card_completeness_path_guard_and_inventory_target():
    q = _queue()
    relay = _lane(q, "relay_runtime_processor")
    for required in [
        "approval_card_present",
        "completeness_ready",
        "path_guard_pass",
        "apply_inventory_target_selected",
    ]:
        assert required in relay["required_inputs"]
    assert "runtime_dry_run_pass" in relay["proof_required"]


def test_scheduler_lane_is_human_required_and_automation_allowed_false():
    q = _queue()
    scheduler = _lane(q, "human_scheduler_registration")
    assert scheduler["human_required"] is True
    assert scheduler["automation_allowed"] is False
    assert scheduler["owner_type"] == "anthony_human"
    assert scheduler["human_only"] is True


def test_sos_lane_is_human_required_and_contains_no_secret_value():
    q = _queue()
    sos = _lane(q, "human_sos_arming")
    assert sos["human_required"] is True
    assert sos["owner_type"] == "anthony_human"
    serialized = json.dumps(sos, sort_keys=True)
    for pattern in ["secret=", "token=", "password=", "api_key=", "bearer ", "sk-"]:
        assert pattern not in serialized.lower()


def test_queue_blocks_if_vacation_mode_true_but_proofs_missing():
    m = _load()
    q = m.build_runtime_execution_queue({"vacation_mode_complete": True})
    res = m.validate_runtime_execution_queue(q)
    assert res["status"] == "BLOCK"
    assert "vacation_mode_complete cannot be true while proof blockers remain" in res["blockers"]


def test_queue_blocks_if_auto_apply_true():
    m = _load()
    q = m.build_runtime_execution_queue()
    q["lanes"][0]["auto_apply"] = True
    res = m.validate_runtime_execution_queue(q)
    assert res["status"] == "BLOCK"
    assert "auto_apply_true" in res["unsafe_flags"]


def test_queue_blocks_if_auto_merge_true():
    m = _load()
    q = m.build_runtime_execution_queue()
    q["lanes"][0]["auto_merge"] = True
    res = m.validate_runtime_execution_queue(q)
    assert res["status"] == "BLOCK"
    assert "auto_merge_true" in res["unsafe_flags"]


def test_queue_blocks_if_auto_scheduler_true():
    m = _load()
    q = m.build_runtime_execution_queue()
    q["lanes"][0]["auto_scheduler"] = True
    res = m.validate_runtime_execution_queue(q)
    assert res["status"] == "BLOCK"
    assert "auto_scheduler_true" in res["unsafe_flags"]


def test_queue_blocks_if_scheduler_lane_not_human_required():
    m = _load()
    q = m.build_runtime_execution_queue()
    _lane(q, "human_scheduler_registration")["human_required"] = False
    res = m.validate_runtime_execution_queue(q)
    assert res["status"] == "BLOCK"
    assert "scheduler_not_human_required" in res["unsafe_flags"]


def test_queue_blocks_if_relay_lacks_path_guard_pass():
    m = _load()
    q = m.build_runtime_execution_queue()
    relay = _lane(q, "relay_runtime_processor")
    relay["required_inputs"] = [item for item in relay["required_inputs"] if item != "path_guard_pass"]
    res = m.validate_runtime_execution_queue(q)
    assert res["status"] == "BLOCK"
    assert "relay_prerequisites_missing" in res["unsafe_flags"]


def test_summarize_next_actions_returns_relay_first():
    m = _load()
    q = m.build_runtime_execution_queue()
    summary = m.summarize_next_actions(q)
    assert summary["next_actions"][0]["lane_id"] == "relay_runtime_processor"
    assert summary["primary_lane"]["lane_id"] == "relay_runtime_processor"


def test_assert_no_hard_gate_bypass_passes_and_blocks():
    m = _load()
    good = m.build_runtime_execution_queue()
    good_result = m.assert_no_hard_gate_bypass(good)
    assert good_result["status"] == "PASS"

    bad = m.build_runtime_execution_queue()
    bad["lanes"][0]["auto_apply"] = True
    bad_result = m.assert_no_hard_gate_bypass(bad)
    assert bad_result["status"] == "BLOCK"
    assert bad_result["blockers"]


def test_no_lane_writes_to_work_packets_active():
    q = _queue()
    assert all(
        "work_packets/active" in " ".join(lane["forbidden_actions"])
        for lane in q["lanes"]
    )


def test_no_lane_claims_live_broker_trading_enabled():
    q = _queue()
    assert all(lane["live_broker_trading_enabled"] is False for lane in q["lanes"])

