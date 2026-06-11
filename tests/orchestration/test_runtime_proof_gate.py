from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_runtime_execution_queue.py"
PROCESSOR_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_relay_runtime_processor.py"
REVIEW_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_relay_dry_run_proof_review.py"
RESTART_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_restart_timeouts_dry_run_proof.py"
RETENTION_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_retention_rotation_dry_run_proof.py"
SOAK_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_soak_dry_run_proof.py"
LEDGER_PATH = REPO_ROOT / "automation" / "orchestration" / "autonomy_reports" / "aios_operator_dependency_ledger.py"
SELECTOR_PATH = REPO_ROOT / "automation" / "orchestration" / "autonomy_reports" / "aios_reduction_target_selector.py"
GATE_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_runtime_proof_gate.py"


def _load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _queue(**state):
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_runtime_proof_gate_tests")
    return queue_mod.build_runtime_execution_queue(state or None)


def _processor(**state):
    proc_mod = _load(PROCESSOR_PATH, "aios_relay_runtime_processor_for_runtime_proof_gate_tests")
    return proc_mod.build_relay_runtime_processor(existing_state=state or None, queue=_queue(**state), now="2026-01-02T03:04:05Z")


def _review(**state):
    review_mod = _load(REVIEW_PATH, "aios_relay_dry_run_proof_review_for_runtime_proof_gate_tests")
    return review_mod.build_relay_dry_run_proof_review(
        existing_state=state or None,
        relay_readout=_processor(**state),
        queue=_queue(**state),
        now="2026-01-02T03:04:05Z",
    )


def _restart(status: str = "PASS"):
    restart_mod = _load(RESTART_PATH, "aios_restart_timeouts_dry_run_proof_for_runtime_proof_gate_tests")
    proof = restart_mod.build_restart_timeouts_dry_run_proof(
        {
            "runtime_label": "aios-runtime",
            "runtime_expected": True,
            "checkpoint_expected": True,
            "last_heartbeat_utc": "2026-01-01T00:04:30Z",
            "last_checkpoint_utc": "2026-01-01T00:01:00Z",
        },
        now="2026-01-01T00:05:00Z",
    )
    proof["proof_status"] = status
    return proof


def _retention(status: str = "PASS"):
    retention_mod = _load(RETENTION_PATH, "aios_retention_rotation_dry_run_proof_for_runtime_proof_gate_tests")
    proof = retention_mod.build_retention_rotation_dry_run_proof(
        [
            {
                "path": "reports/runtime/a.jsonl",
                "kind": "jsonl",
                "created_at_utc": "2026-01-29T00:00:00Z",
                "updated_at_utc": "2026-01-30T00:00:00Z",
                "size_bytes": 2048,
                "line_count": 25,
                "contains_jsonl": True,
                "required": True,
            }
        ],
        now="2026-01-31T00:00:00Z",
    )
    proof["proof_status"] = status
    return proof


def _soak(status: str = "PASS"):
    soak_mod = _load(SOAK_PATH, "aios_soak_dry_run_proof_for_runtime_proof_gate_tests")
    proof = soak_mod.build_soak_dry_run_proof(
        {
            "runtime_label": "aios-runtime",
            "window_start_utc": "2026-01-01T00:00:00Z",
            "window_end_utc": "2026-01-01T01:00:00Z",
            "heartbeat_samples_utc": [
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:05:00Z",
                "2026-01-01T00:10:00Z",
                "2026-01-01T00:15:00Z",
                "2026-01-01T00:20:00Z",
                "2026-01-01T00:25:00Z",
                "2026-01-01T00:30:00Z",
                "2026-01-01T00:35:00Z",
                "2026-01-01T00:40:00Z",
                "2026-01-01T00:45:00Z",
                "2026-01-01T00:50:00Z",
                "2026-01-01T00:55:00Z",
                "2026-01-01T01:00:00Z",
            ],
            "checkpoint_samples_utc": [
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:15:00Z",
                "2026-01-01T00:30:00Z",
                "2026-01-01T00:45:00Z",
                "2026-01-01T01:00:00Z",
            ],
        },
        restart_timeouts_proof=_restart(status),
        retention_rotation_proof=_retention(status),
        now="2026-01-01T01:00:00Z",
    )
    proof["proof_status"] = status
    return proof


def _ledger(**state):
    ledger_mod = _load(LEDGER_PATH, "aios_operator_dependency_ledger_for_runtime_proof_gate_tests")
    return ledger_mod.build_operator_dependency_ledger(
        state or None,
        queue=_queue(**state),
        relay_readout=_processor(**state),
        relay_review=_review(**state),
        now="2026-01-02T03:04:05Z",
    )


def _selector(**state):
    selector_mod = _load(SELECTOR_PATH, "aios_reduction_target_selector_for_runtime_proof_gate_tests")
    return selector_mod.build_reduction_target_selector(state or None, ledger=_ledger(**state), now="2026-01-02T03:04:05Z")


def _ready_inputs():
    state = {
        "approval_card_present": True,
        "completeness_ready": True,
        "path_guard_pass": True,
        "apply_inventory_target_selected": True,
        "runtime_dry_run_pass": True,
        "restart_timeout_proof_pass": True,
        "retention_dry_run_pass": True,
        "soak_pass": True,
        "stop_drill_pass": True,
        "sos_delivered_true": True,
        "scheduler_registered_by_anthony": True,
    }
    queue = _queue(**state)
    processor = _processor(**state)
    review = _review(**state)
    restart = _restart("PASS")
    retention = _retention("PASS")
    soak = _soak("PASS")
    ledger = _ledger(**state)
    selector = _selector(**state)
    return queue, processor, review, restart, retention, soak, ledger, selector


def test_runtime_proof_gate_writes_preview_json_and_markdown(tmp_path):
    mod = _load(GATE_PATH, "aios_runtime_proof_gate_for_write_tests")
    queue, processor, review, restart, retention, soak, ledger, selector = _ready_inputs()
    gate = mod.build_runtime_proof_gate(
        runtime_queue_readout=queue,
        relay_processor_readout=processor,
        relay_proof_review=review,
        restart_timeouts_proof=restart,
        retention_rotation_proof=retention,
        soak_proof=soak,
        operator_dependency_ledger=ledger,
        reduction_target_selector=selector,
        now="2026-01-02T03:04:05Z",
    )
    assert gate["final_verdict"] == "READY_FOR_HUMAN_GATE"

    outdir = tmp_path / "Reports" / "runtime_proof_gate"
    report = mod.write_runtime_proof_gate_reports(gate, repo_root=tmp_path, output_dir=outdir)
    json_path = outdir / mod.REPORT_JSON_NAME
    md_path = outdir / mod.REPORT_MD_NAME

    assert json_path.exists()
    assert md_path.exists()
    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    assert loaded["final_verdict"] == "READY_FOR_HUMAN_GATE"
    assert loaded["report_paths"] == [json_path.as_posix(), md_path.as_posix()]
    assert loaded["blocker_count"] == 0
    assert loaded["attention_count"] == 0
    assert loaded["runtime_execution_allowed"] is False
    assert mod.validate_runtime_proof_gate(loaded)["status"] == "PASS"
    assert "READY_FOR_HUMAN_GATE" in md_path.read_text(encoding="utf-8")
    assert report["report_paths"] == [json_path.as_posix(), md_path.as_posix()]


def test_runtime_proof_gate_blocked_proof_is_valid_and_non_executable():
    mod = _load(GATE_PATH, "aios_runtime_proof_gate_for_blocked_tests")
    queue, processor, _, restart, retention, soak, ledger, selector = _ready_inputs()
    gate = mod.build_runtime_proof_gate(
        runtime_queue_readout=queue,
        relay_processor_readout=processor,
        restart_timeouts_proof=restart,
        retention_rotation_proof=retention,
        soak_proof=soak,
        operator_dependency_ledger=ledger,
        reduction_target_selector=selector,
        now="2026-01-02T03:04:05Z",
    )

    validation = mod.validate_runtime_proof_gate(gate)
    assert gate["final_verdict"] == "BLOCKED"
    assert validation["status"] == "PASS"
    assert gate["human_gate_ready"] is False
    assert gate["execution_allowed"] is False
    assert gate["runtime_launch_allowed"] is False
    assert gate["scheduler_creation_allowed"] is False
    assert gate["sos_allowed"] is False
    assert gate["live_trading_allowed"] is False
