from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_runtime_queue_blocker_stack.py"
GATE_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_runtime_proof_gate.py"
GATE_TEST_HELPERS_PATH = REPO_ROOT / "tests" / "orchestration" / "test_aios_runtime_proof_gate.py"


def _load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _runtime_proof_payload() -> dict:
    return {
        "schema": "AIOS_RUNTIME_PROOF_GATE.v1",
        "relay_review_status": "REVIEWABLE",
        "restart_timeouts_status": "PASS",
        "retention_rotation_status": "PASS",
        "soak_status": "PASS",
        "restart_timeouts_summary": {"proof_status": "PASS"},
        "retention_rotation_summary": {"proof_status": "PASS"},
        "soak_summary": {"proof_status": "PASS", "soak_pass": True},
        "cross_proof_consistency": {
            "relay_review_status": "REVIEWABLE",
            "restart_timeouts_status": "PASS",
            "retention_rotation_status": "PASS",
            "soak_status": "PASS",
        },
        "runtime_execution_allowed": False,
        "runtime_launch_allowed": False,
        "scheduler_creation_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
        "vacation_mode_complete": False,
    }


def test_stack_normalizes_aliases_and_preserves_human_gates(tmp_path):
    mod = _load(MODULE_PATH, "aios_runtime_queue_blocker_stack_test")
    _write_json(
        tmp_path / "Reports" / "runtime_proof_gate" / "runtime_proof_gate_preview.json",
        _runtime_proof_payload(),
    )
    _write_json(
        tmp_path / "Reports" / "relay_proof_review" / "relay_proof_review.json",
        {"schema": "AIOS_RELAY_PROOF_REVIEW.v1", "review_status": "REVIEWABLE"},
    )

    report = mod.run_runtime_queue_blocker_stack(
        repo_root=tmp_path,
        output_dir=tmp_path / "Reports" / "runtime_queue_blocker_stack",
        now="2026-06-11T12:00:00Z",
    )

    assert report["status"] == "HUMAN_GATE_REQUIRED"
    assert report["proofs"]["relay_runtime_proof"]["status"] == "REVIEWABLE"
    assert report["proofs"]["restart_timeouts_proof"]["status"] == "PASS"
    assert report["proofs"]["retention_rotation_proof"]["status"] == "PASS"
    assert report["proofs"]["soak_proof"]["status"] == "PASS"
    assert report["proofs"]["stop_drill_proof"]["status"] == "HUMAN_GATE_REQUIRED"
    assert report["proofs"]["sos_delivery_proof"]["status"] == "HUMAN_GATE_REQUIRED"
    assert report["proofs"]["scheduler_manual_registration_proof"]["status"] == "HUMAN_GATE_REQUIRED"
    assert report["protected_mutation_detected"] is False
    assert report["queue_mutation_allowed"] is False
    assert report["runtime_execution_allowed"] is False
    assert report["normalized_runtime_queue_readout"]["validation_status"] == "HUMAN_GATE_REQUIRED"
    assert "restart/timeouts proof missing" in report["stale_blockers_resolved"]
    assert report["validation"]["status"] == "PASS"


def test_human_gate_requests_do_not_claim_delivery_or_scheduler_registration(tmp_path):
    mod = _load(MODULE_PATH, "aios_runtime_queue_blocker_stack_request_test")
    report = mod.run_runtime_queue_blocker_stack(repo_root=tmp_path, now="2026-06-11T12:00:00Z")

    stop_path = tmp_path / "Reports" / "human_gate" / "stop_drill_confirmation_request.json"
    sos_path = tmp_path / "Reports" / "human_gate" / "sos_delivery_request.json"
    scheduler_path = tmp_path / "Reports" / "human_gate" / "scheduler_manual_registration_request.json"
    handoff_path = tmp_path / "Reports" / "human_gate" / "final_human_gate_handoff.json"
    stop = json.loads(stop_path.read_text(encoding="utf-8"))
    sos = json.loads(sos_path.read_text(encoding="utf-8"))
    scheduler = json.loads(scheduler_path.read_text(encoding="utf-8"))
    handoff = json.loads(handoff_path.read_text(encoding="utf-8"))

    assert report["source_loaded"]["stop_drill_confirmation_request"] is True
    assert report["source_loaded"]["final_human_gate_handoff"] is True
    assert report["proofs"]["sos_delivery_proof"]["status"] == "HUMAN_GATE_REQUIRED"
    assert stop["schema"] == "AIOS_STOP_DRILL_CONFIRMATION_REQUEST.v1"
    assert stop["stop_drill_pass"] is False
    assert stop["stop_drill_human_confirmation"] is False
    assert stop["runtime_execution_allowed"] is False
    assert stop["runtime_launch_allowed"] is False
    assert stop["scheduler_registration_allowed"] is False
    assert stop["sos_notification_allowed"] is False
    assert (
        stop["exact_human_confirmation_phrase"]
        == "ANTHONY_CONFIRMS_STOP_DRILL_PASSED_FOR_DRY_RUN_RECOVERY_PROOF_ONLY"
    )
    assert sos["schema"] == "AIOS_SOS_DELIVERY_CONFIRMATION_REQUEST.v1"
    assert sos["real_channel_armed"] is False
    assert sos["notification_send_allowed"] is False
    assert sos["delivered_true"] is False
    assert sos["sos_delivery_human_confirmation"] is False
    assert sos["scheduler_registration_allowed"] is False
    assert (
        sos["exact_human_confirmation_phrase"]
        == "ANTHONY_CONFIRMS_SOS_DELIVERED_TRUE_FOR_SINGLE_TEST_ONLY_NO_SECRET_IN_REPO"
    )
    assert scheduler["schema"] == "AIOS_SCHEDULER_MANUAL_REGISTRATION_CONFIRMATION_REQUEST.v1"
    assert scheduler["scheduler_registered_by_anthony"] is False
    assert scheduler["real_scheduler_registered"] is False
    assert scheduler["scheduler_creation_allowed"] is False
    assert scheduler["manual_registration_confirmed"] is False
    assert scheduler["sos_notification_allowed"] is False
    assert (
        scheduler["exact_human_confirmation_phrase"]
        == "ANTHONY_CONFIRMS_SCHEDULER_MANUALLY_REGISTERED_AFTER_STOP_AND_SOS_PROOF"
    )
    assert handoff["status"] == "HUMAN_GATE_REQUIRED"
    assert handoff["stop_drill_pass"] is False
    assert handoff["sos_delivered_true"] is False
    assert handoff["scheduler_registered_by_anthony"] is False
    assert handoff["vacation_mode_complete"] is False
    assert handoff["runtime_execution_allowed"] is False
    assert handoff["queue_write_allowed"] is False
    assert handoff["scheduler_creation_allowed"] is False
    assert handoff["sos_allowed"] is False
    assert len(handoff["next_strict_human_order"]) == 7


def test_runtime_proof_gate_consumes_normalized_stack_without_stale_alias_blockers(tmp_path):
    stack_mod = _load(MODULE_PATH, "aios_runtime_queue_blocker_stack_gate_test")
    gate_mod = _load(GATE_PATH, "aios_runtime_proof_gate_normalized_stack_test")
    helpers = _load(GATE_TEST_HELPERS_PATH, "aios_runtime_proof_gate_helpers_for_stack_test")
    proven_dry_run_state = {
        "approval_card_present": True,
        "completeness_ready": True,
        "path_guard_pass": True,
        "apply_inventory_target_selected": True,
        "runtime_dry_run_pass": True,
        "restart_timeout_proof_pass": True,
        "retention_dry_run_pass": True,
        "soak_pass": True,
    }
    _write_json(
        tmp_path / "Reports" / "runtime_proof_gate" / "runtime_proof_gate_preview.json",
        _runtime_proof_payload(),
    )
    _write_json(
        tmp_path / "Reports" / "relay_proof_review" / "relay_proof_review.json",
        {
            "runtime_queue_readout": helpers._queue(**proven_dry_run_state),
            "relay_processor_readout": helpers._processor(**proven_dry_run_state),
            "relay_proof_review": helpers._review(**proven_dry_run_state),
            "operator_dependency_ledger": helpers._ledger(**proven_dry_run_state),
            "reduction_target_selector": helpers._selector(**proven_dry_run_state),
            "review_status": "REVIEWABLE",
        },
    )
    stack_mod.run_runtime_queue_blocker_stack(repo_root=tmp_path, now="2026-06-11T12:00:00Z")

    gate = gate_mod.run_runtime_proof_gate(
        repo_root=tmp_path,
        output_dir=tmp_path / "Reports" / "runtime_proof_gate",
        now="2026-06-11T12:01:00Z",
    )

    assert gate["final_verdict"] == "BLOCKED"
    assert gate["runtime_queue_status"] == "HUMAN_GATE_REQUIRED"
    assert gate["restart_timeouts_status"] == "PASS"
    assert gate["retention_rotation_status"] == "PASS"
    assert gate["soak_status"] == "PASS"
    assert gate["relay_review_status"] == "REVIEWABLE"
    assert "runtime queue still lists remaining blockers" not in gate["blockers"]
    assert "restart_timeouts_proof" not in gate["blockers"]
    assert "retention_rotation_proof" not in gate["blockers"]
    assert "soak_proof" not in gate["blockers"]
    assert all(str(item).startswith("human gate required:") for item in gate["blockers"])
    assert gate["runtime_execution_allowed"] is False
    assert gate["runtime_launch_allowed"] is False

def test_stop_drill_human_confirmation_reduces_only_stop_drill_blocker():
    import json
    from pathlib import Path

    report = json.loads(Path("Reports/runtime_queue_blocker_stack/runtime_queue_blocker_stack.json").read_text(encoding="utf-8"))
    proofs = report.get("proofs", {})

    assert proofs.get("stop_drill_proof", {}).get("status") == "PASS"
    assert proofs.get("stop_drill_proof", {}).get("human_gate") is None
    assert proofs.get("sos_delivery_proof", {}).get("status") == "HUMAN_GATE_REQUIRED"
    assert proofs.get("scheduler_manual_registration_proof", {}).get("status") == "HUMAN_GATE_REQUIRED"

    assert report.get("runtime_execution_allowed") is False
    assert report.get("runtime_launch_allowed") is False
    assert report.get("scheduler_registration_allowed") is False
    assert report.get("sos_allowed") is False
    assert report.get("live_trading_allowed") is False
    assert report.get("vacation_mode_complete") is False
