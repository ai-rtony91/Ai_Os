"""Tests for the AI_OS runtime proof gate (observe-only)."""

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
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_gate_tests")
    return queue_mod.build_runtime_execution_queue(state or None)


def _processor(**state):
    proc_mod = _load(PROCESSOR_PATH, "aios_relay_runtime_processor_for_gate_tests")
    return proc_mod.build_relay_runtime_processor(existing_state=state or None, queue=_queue(**state), now="2026-01-02T03:04:05Z")


def _review(**state):
    review_mod = _load(REVIEW_PATH, "aios_relay_dry_run_proof_review_for_gate_tests")
    return review_mod.build_relay_dry_run_proof_review(
        existing_state=state or None,
        relay_readout=_processor(**state),
        queue=_queue(**state),
        now="2026-01-02T03:04:05Z",
    )


def _restart(status: str = "PASS"):
    restart_mod = _load(RESTART_PATH, "aios_restart_timeouts_dry_run_proof_for_gate_tests")
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
    retention_mod = _load(RETENTION_PATH, "aios_retention_rotation_dry_run_proof_for_gate_tests")
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
    soak_mod = _load(SOAK_PATH, "aios_soak_dry_run_proof_for_gate_tests")
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
        restart_timeouts_proof=_restart("PASS"),
        retention_rotation_proof=_retention("PASS"),
        now="2026-01-01T01:00:00Z",
    )
    proof["proof_status"] = status
    return proof


def _ledger(**state):
    ledger_mod = _load(LEDGER_PATH, "aios_operator_dependency_ledger_for_gate_tests")
    return ledger_mod.build_operator_dependency_ledger(
        state or None,
        queue=_queue(**state),
        relay_readout=_processor(**state),
        relay_review=_review(**state),
        now="2026-01-02T03:04:05Z",
    )


def _selector(**state):
    selector_mod = _load(SELECTOR_PATH, "aios_reduction_target_selector_for_gate_tests")
    return selector_mod.build_reduction_target_selector(state or None, ledger=_ledger(**state), now="2026-01-02T03:04:05Z")


def _gate(**kwargs):
    gate_mod = _load(GATE_PATH, "aios_runtime_proof_gate")
    return gate_mod.build_runtime_proof_gate(now="2026-01-02T03:04:05Z", **kwargs)


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


def test_prerequisite_modules_exist_on_current_base():
    for path in [
        QUEUE_PATH,
        PROCESSOR_PATH,
        REVIEW_PATH,
        RESTART_PATH,
        RETENTION_PATH,
        SOAK_PATH,
        LEDGER_PATH,
        SELECTOR_PATH,
    ]:
        assert path.exists()


def test_gate_builds_from_all_safe_pass_reviewable_inputs():
    gate_mod = _load(GATE_PATH, "aios_runtime_proof_gate_build_test")
    queue, processor, review, restart, retention, soak, ledger, selector = _ready_inputs()
    gate = gate_mod.build_runtime_proof_gate(
        runtime_queue_readout=queue,
        relay_processor_readout=processor,
        relay_proof_review=review,
        restart_timeouts_proof=restart,
        retention_rotation_proof=retention,
        soak_proof=soak,
        operator_dependency_ledger=ledger,
        reduction_target_selector=selector,
        gate_policy={
            "require_runtime_queue": True,
            "require_relay_processor": True,
            "require_relay_proof_review": True,
            "require_restart_timeouts_proof": True,
            "require_retention_rotation_proof": True,
            "require_soak_proof": True,
            "require_operator_dependency_ledger": True,
            "require_reduction_target_selector": True,
            "require_soak_pass": True,
            "allow_restart_attention": False,
            "allow_retention_attention": False,
            "allow_soak_attention": False,
            "require_all_execution_flags_false": True,
            "require_human_gate": True,
            "allow_scheduler": False,
            "allow_sos": False,
            "allow_live_trading": False,
            "allow_credentials_access": False,
            "allow_vacation_mode_complete": False,
            "allow_autonomy_claim": False,
        },
    )
    assert gate["schema"] == "AIOS_RUNTIME_PROOF_GATE.v1"
    assert gate["mode"] == "DRY_RUN_GATE"
    assert gate["gate_type"] == "runtime_proof_gate"
    assert gate["final_verdict"] == "READY_FOR_HUMAN_GATE"
    assert gate["human_gate_required"] is True
    assert gate["human_gate_ready"] is True
    assert gate["execution_allowed"] is False
    assert gate["approval_granted"] is False


def test_ready_for_human_gate_keeps_execution_and_approval_blocked():
    queue, processor, review, restart, retention, soak, ledger, selector = _ready_inputs()
    gate = _gate(
        runtime_queue_readout=queue,
        relay_processor_readout=processor,
        relay_proof_review=review,
        restart_timeouts_proof=restart,
        retention_rotation_proof=retention,
        soak_proof=soak,
        operator_dependency_ledger=ledger,
        reduction_target_selector=selector,
    )
    assert gate["final_verdict"] == "READY_FOR_HUMAN_GATE"
    for field in [
        "execution_allowed",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_launch_allowed",
        "runtime_mutation_allowed",
        "telemetry_mutation_allowed",
        "scheduler_creation_allowed",
        "service_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
        "credentials_accessed",
        "approval_granted",
        "vacation_mode_complete",
        "unsafe_autonomy_claim",
    ]:
        assert gate[field] is False


def test_missing_runtime_queue_blocks_gate():
    gate_mod = _load(GATE_PATH, "aios_runtime_proof_gate_missing_queue_test")
    gate = gate_mod.build_runtime_proof_gate(
        relay_processor_readout=_processor(),
        relay_proof_review=_review(),
        restart_timeouts_proof=_restart(),
        retention_rotation_proof=_retention(),
        soak_proof=_soak(),
        operator_dependency_ledger=_ledger(),
        reduction_target_selector=_selector(),
        now="2026-01-02T03:04:05Z",
    )
    assert gate["final_verdict"] == "BLOCKED"


def test_missing_relay_review_blocks_gate():
    gate = _gate(
        runtime_queue_readout=_queue(),
        relay_processor_readout=_processor(),
        restart_timeouts_proof=_restart(),
        retention_rotation_proof=_retention(),
        soak_proof=_soak(),
        operator_dependency_ledger=_ledger(),
        reduction_target_selector=_selector(),
    )
    assert gate["final_verdict"] == "BLOCKED"


def test_blocked_or_invalid_prerequisites_block_or_invalidate_gate():
    queue, processor, review, restart, retention, soak, ledger, selector = _ready_inputs()
    blocked_restart = dict(restart)
    blocked_restart["proof_status"] = "BLOCKED"
    gate = _gate(
        runtime_queue_readout=queue,
        relay_processor_readout=processor,
        relay_proof_review=review,
        restart_timeouts_proof=blocked_restart,
        retention_rotation_proof=retention,
        soak_proof=soak,
        operator_dependency_ledger=ledger,
        reduction_target_selector=selector,
    )
    assert gate["final_verdict"] == "INVALID"

    invalid_review = dict(review)
    invalid_review["review_status"] = "INVALID"
    gate = _gate(
        runtime_queue_readout=queue,
        relay_processor_readout=processor,
        relay_proof_review=invalid_review,
        restart_timeouts_proof=restart,
        retention_rotation_proof=retention,
        soak_proof=soak,
        operator_dependency_ledger=ledger,
        reduction_target_selector=selector,
    )
    assert gate["final_verdict"] == "INVALID"


def test_attention_propagates_from_prerequisite_proofs_and_selector():
    queue, processor, review, restart, retention, soak, ledger, selector = _ready_inputs()
    attention_restart = dict(restart)
    attention_restart["proof_status"] = "ATTENTION"
    gate = _gate(
        runtime_queue_readout=queue,
        relay_processor_readout=processor,
        relay_proof_review=review,
        restart_timeouts_proof=attention_restart,
        retention_rotation_proof=retention,
        soak_proof=soak,
        operator_dependency_ledger=ledger,
        reduction_target_selector=selector,
    )
    assert gate["final_verdict"] == "BLOCKED"

    planning_selector = dict(selector)
    planning_selector["selected_target"] = "restart_timeouts_proof_planning"
    gate = _gate(
        runtime_queue_readout=queue,
        relay_processor_readout=processor,
        relay_proof_review=review,
        restart_timeouts_proof=restart,
        retention_rotation_proof=retention,
        soak_proof=soak,
        operator_dependency_ledger=ledger,
        reduction_target_selector=planning_selector,
    )
    assert gate["final_verdict"] == "ATTENTION"


def test_unsafe_flags_anywhere_block_or_invalidate_gate():
    queue, processor, review, restart, retention, soak, ledger, selector = _ready_inputs()
    tampered_soak = dict(soak)
    tampered_soak["runtime_launched"] = True
    gate = _gate(
        runtime_queue_readout=queue,
        relay_processor_readout=processor,
        relay_proof_review=review,
        restart_timeouts_proof=restart,
        retention_rotation_proof=retention,
        soak_proof=tampered_soak,
        operator_dependency_ledger=ledger,
        reduction_target_selector=selector,
    )
    assert gate["final_verdict"] in {"BLOCKED", "INVALID"}
    assert gate["unsafe_flags_detected"]


def test_forbidden_claims_are_detected_and_invalidate_gate():
    queue, processor, review, restart, retention, soak, ledger, selector = _ready_inputs()
    tampered_selector = dict(selector)
    tampered_selector["final_verdict"] = "COMPLETE"
    gate = _gate(
        runtime_queue_readout=queue,
        relay_processor_readout=processor,
        relay_proof_review=review,
        restart_timeouts_proof=restart,
        retention_rotation_proof=retention,
        soak_proof=soak,
        operator_dependency_ledger=ledger,
        reduction_target_selector=tampered_selector,
    )
    assert gate["final_verdict"] == "INVALID"
    assert gate["forbidden_claims_detected"]


def test_cross_proof_consistency_blocks_soak_pass_with_blocked_prerequisites():
    queue, processor, review, restart, retention, soak, ledger, selector = _ready_inputs()
    blocked_retention = dict(retention)
    blocked_retention["proof_status"] = "BLOCKED"
    gate = _gate(
        runtime_queue_readout=queue,
        relay_processor_readout=processor,
        relay_proof_review=review,
        restart_timeouts_proof=restart,
        retention_rotation_proof=blocked_retention,
        soak_proof=soak,
        operator_dependency_ledger=ledger,
        reduction_target_selector=selector,
    )
    assert gate["final_verdict"] == "INVALID"
    assert gate["cross_proof_consistency"]["retention_rotation_status"] == "BLOCKED"


def test_validation_passes_for_safe_ready_gate_and_blocks_tampering():
    gate_mod = _load(GATE_PATH, "aios_runtime_proof_gate_validation_test")
    queue, processor, review, restart, retention, soak, ledger, selector = _ready_inputs()
    gate = gate_mod.build_runtime_proof_gate(
        runtime_queue_readout=queue,
        relay_processor_readout=processor,
        relay_proof_review=review,
        restart_timeouts_proof=restart,
        retention_rotation_proof=retention,
        soak_proof=soak,
        operator_dependency_ledger=ledger,
        reduction_target_selector=selector,
    )
    validation = gate_mod.validate_runtime_proof_gate(gate)
    assert validation["status"] == "PASS"

    tampered = dict(gate)
    tampered["dispatch_allowed"] = True
    validation = gate_mod.validate_runtime_proof_gate(tampered)
    assert validation["status"] == "BLOCK"
    assert "dispatch_allowed_true" in validation["unsafe_flags"]


def test_validation_blocks_forbidden_final_verdicts_and_ready_inconsistencies():
    gate_mod = _load(GATE_PATH, "aios_runtime_proof_gate_forbidden_validation_test")
    queue, processor, review, restart, retention, soak, ledger, selector = _ready_inputs()
    gate = gate_mod.build_runtime_proof_gate(
        runtime_queue_readout=queue,
        relay_processor_readout=processor,
        relay_proof_review=review,
        restart_timeouts_proof=restart,
        retention_rotation_proof=retention,
        soak_proof=soak,
        operator_dependency_ledger=ledger,
        reduction_target_selector=selector,
    )
    tampered = dict(gate)
    tampered["final_verdict"] = "COMPLETE"
    validation = gate_mod.validate_runtime_proof_gate(tampered)
    assert validation["status"] == "BLOCK"
    assert "final_verdict_forbidden" in validation["unsafe_flags"]

    ready_but_blocked = dict(gate)
    ready_but_blocked["final_verdict"] = "READY_FOR_HUMAN_GATE"
    ready_but_blocked["blockers"] = ["x"]
    validation = gate_mod.validate_runtime_proof_gate(ready_but_blocked)
    assert validation["status"] == "BLOCK"


def test_gate_output_is_deterministic_and_hygienic():
    queue, processor, review, restart, retention, soak, ledger, selector = _ready_inputs()
    gate1 = _gate(
        runtime_queue_readout=queue,
        relay_processor_readout=processor,
        relay_proof_review=review,
        restart_timeouts_proof=restart,
        retention_rotation_proof=retention,
        soak_proof=soak,
        operator_dependency_ledger=ledger,
        reduction_target_selector=selector,
    )
    gate2 = _gate(
        runtime_queue_readout=queue,
        relay_processor_readout=processor,
        relay_proof_review=review,
        restart_timeouts_proof=restart,
        retention_rotation_proof=retention,
        soak_proof=soak,
        operator_dependency_ledger=ledger,
        reduction_target_selector=selector,
    )
    assert gate1 == gate2
    serialized = json.dumps(gate1, sort_keys=True).lower()
    for pattern in [
        "git push",
        "git commit",
        "git merge",
        "gh pr merge",
        "gh pr create",
        "register-scheduledtask",
        "new-service",
        "start-job",
        "start-process",
        "start-service",
        "subprocess",
        "shell=true",
    ]:
        assert pattern not in serialized

    source = GATE_PATH.read_text(encoding="utf-8").lower()
    for pattern in [
        "secret" + "=",
        "token" + "=",
        "pass" + "word" + "=",
        "api" + "_key" + "=",
        "api" + "key" + "=",
        "bear" + "er ",
        "sk" + "-",
    ]:
        assert pattern not in source


def test_existing_runtime_and_proof_chain_tests_still_pass():
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_gate_regression")
    proc_mod = _load(PROCESSOR_PATH, "aios_relay_runtime_processor_for_gate_regression")
    review_mod = _load(REVIEW_PATH, "aios_relay_dry_run_proof_review_for_gate_regression")
    restart_mod = _load(RESTART_PATH, "aios_restart_timeouts_dry_run_proof_for_gate_regression")
    retention_mod = _load(RETENTION_PATH, "aios_retention_rotation_dry_run_proof_for_gate_regression")
    soak_mod = _load(SOAK_PATH, "aios_soak_dry_run_proof_for_gate_regression")
    ledger_mod = _load(LEDGER_PATH, "aios_operator_dependency_ledger_for_gate_regression")
    selector_mod = _load(SELECTOR_PATH, "aios_reduction_target_selector_for_gate_regression")
    q = queue_mod.build_runtime_execution_queue()
    r = proc_mod.build_relay_runtime_processor(queue=q, now="2026-01-02T03:04:05Z")
    v = review_mod.build_relay_dry_run_proof_review(relay_readout=r, queue=q, now="2026-01-02T03:04:05Z")
    rt = restart_mod.build_restart_timeouts_dry_run_proof(
        {
            "runtime_label": "aios-runtime",
            "runtime_expected": True,
            "checkpoint_expected": True,
            "last_heartbeat_utc": "2026-01-01T00:04:30Z",
            "last_checkpoint_utc": "2026-01-01T00:01:00Z",
        },
        now="2026-01-01T00:05:00Z",
    )
    rr = retention_mod.build_retention_rotation_dry_run_proof(
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
    s = soak_mod.build_soak_dry_run_proof(
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
        restart_timeouts_proof=rt,
        retention_rotation_proof=rr,
        now="2026-01-01T01:00:00Z",
    )
    l = ledger_mod.build_operator_dependency_ledger(queue=q, relay_readout=r, relay_review=v, now="2026-01-02T03:04:05Z")
    sel = selector_mod.build_reduction_target_selector(ledger=l, now="2026-01-02T03:04:05Z")
    assert queue_mod.validate_runtime_execution_queue(q)["status"] == "PASS"
    assert proc_mod.validate_relay_runtime_processor(r)["status"] == "PASS"
    assert review_mod.validate_relay_dry_run_proof_review(v)["status"] == "PASS"
    assert restart_mod.validate_restart_timeouts_dry_run_proof(rt)["status"] == "PASS"
    assert retention_mod.validate_retention_rotation_dry_run_proof(rr)["status"] == "PASS"
    assert soak_mod.validate_soak_dry_run_proof(s)["status"] == "PASS"
    assert ledger_mod.validate_operator_dependency_ledger(l)["status"] == "PASS"
    assert selector_mod.validate_reduction_target_selector(sel)["status"] == "PASS"
