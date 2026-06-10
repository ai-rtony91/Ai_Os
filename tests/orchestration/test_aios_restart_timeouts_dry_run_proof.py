"""Tests for the AI_OS restart/timeouts dry-run proof (observe-only)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_runtime_execution_queue.py"
PROCESSOR_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_relay_runtime_processor.py"
REVIEW_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_relay_dry_run_proof_review.py"
LEDGER_PATH = REPO_ROOT / "automation" / "orchestration" / "autonomy_reports" / "aios_operator_dependency_ledger.py"
SELECTOR_PATH = REPO_ROOT / "automation" / "orchestration" / "autonomy_reports" / "aios_reduction_target_selector.py"
RESTART_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_restart_timeouts_dry_run_proof.py"


def _load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _queue(**state):
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_restart_tests")
    return queue_mod.build_runtime_execution_queue(state or None)


def _processor(**state):
    proc_mod = _load(PROCESSOR_PATH, "aios_relay_runtime_processor_for_restart_tests")
    return proc_mod.build_relay_runtime_processor(existing_state=state or None, queue=_queue(**state), now="2026-01-02T03:04:05Z")


def _review(**state):
    review_mod = _load(REVIEW_PATH, "aios_relay_dry_run_proof_review_for_restart_tests")
    return review_mod.build_relay_dry_run_proof_review(
        existing_state=state or None,
        relay_readout=_processor(**state),
        queue=_queue(**state),
        now="2026-01-02T03:04:05Z",
    )


def _ledger(**state):
    ledger_mod = _load(LEDGER_PATH, "aios_operator_dependency_ledger_for_restart_tests")
    return ledger_mod.build_operator_dependency_ledger(
        state or None,
        queue=_queue(**state),
        relay_readout=_processor(**state),
        relay_review=_review(**state),
        now="2026-01-02T03:04:05Z",
    )


def _selector(**state):
    selector_mod = _load(SELECTOR_PATH, "aios_reduction_target_selector_for_restart_tests")
    return selector_mod.build_reduction_target_selector(state or None, ledger=_ledger(**state), now="2026-01-02T03:04:05Z")


def _restart():
    return _load(RESTART_PATH, "aios_restart_timeouts_dry_run_proof")


def _healthy_inputs():
    return {
        "runtime_label": "aios-runtime",
        "runtime_expected": True,
        "checkpoint_expected": True,
        "last_heartbeat_utc": "2026-01-01T00:04:30Z",
        "last_checkpoint_utc": "2026-01-01T00:01:00Z",
    }


def _stale_inputs():
    return {
        "runtime_label": "aios-runtime",
        "runtime_expected": True,
        "checkpoint_expected": True,
        "last_heartbeat_utc": "2026-01-01T00:00:00Z",
        "last_checkpoint_utc": "2026-01-01T00:01:00Z",
    }


def _missing_checkpoint_inputs():
    return {
        "runtime_label": "aios-runtime",
        "runtime_expected": True,
        "checkpoint_expected": True,
        "last_heartbeat_utc": "2026-01-01T00:04:30Z",
    }


def _invalid_inputs():
    return {
        "runtime_label": "aios-runtime",
        "runtime_expected": True,
        "checkpoint_expected": True,
        "last_heartbeat_utc": "2026-01-01T00:10:30Z",
        "last_checkpoint_utc": "2026-01-01T00:01:00Z",
    }


def test_proof_builds_with_healthy_simulated_input():
    m = _restart()
    proof = m.build_restart_timeouts_dry_run_proof(_healthy_inputs(), now="2026-01-01T00:05:00Z")
    assert proof["schema"] == "AIOS_RESTART_TIMEOUTS_DRY_RUN_PROOF.v1"
    assert proof["mode"] == "DRY_RUN"
    assert proof["proof_type"] == "restart_timeouts"
    assert proof["healthy_state_detected"] is True
    assert proof["restart_required"] is False


def test_healthy_input_returns_pass_and_sets_healthy_state_detected_true():
    m = _restart()
    proof = m.build_restart_timeouts_dry_run_proof(_healthy_inputs(), now="2026-01-01T00:05:00Z")
    assert proof["proof_status"] == "PASS"
    assert proof["healthy_state_detected"] is True


def test_stale_heartbeat_returns_attention_and_marks_restart_required_without_executing_restart():
    m = _restart()
    proof = m.build_restart_timeouts_dry_run_proof(_stale_inputs(), now="2026-01-01T00:10:00Z")
    assert proof["proof_status"] == "ATTENTION"
    assert proof["stale_heartbeat_detected"] is True
    assert proof["restart_required"] is True
    assert proof["restart_executed"] is False


def test_missing_checkpoint_is_detected_and_timeout_is_not_executed():
    m = _restart()
    proof = m.build_restart_timeouts_dry_run_proof(_missing_checkpoint_inputs(), now="2026-01-01T00:10:00Z")
    assert proof["proof_status"] == "ATTENTION"
    assert proof["missing_checkpoint_detected"] is True
    assert proof["timeout_executed"] is False


def test_invalid_timestamp_returns_blocked():
    m = _restart()
    proof = m.build_restart_timeouts_dry_run_proof(_invalid_inputs(), now="2026-01-01T00:05:00Z")
    assert proof["proof_status"] == "BLOCKED"
    assert "safe_next_action" in proof


def test_proof_is_dry_run_and_never_returns_complete():
    m = _restart()
    proof = m.build_restart_timeouts_dry_run_proof(_healthy_inputs(), now="2026-01-01T00:05:00Z")
    assert proof["mode"] == "DRY_RUN"
    assert proof["proof_status"] != "COMPLETE"


def test_proof_keeps_all_mutation_and_live_flags_false():
    m = _restart()
    proof = m.build_restart_timeouts_dry_run_proof(_healthy_inputs(), now="2026-01-01T00:05:00Z")
    for field in [
        "dispatch_allowed",
        "apply_allowed",
        "runtime_mutation_allowed",
        "scheduler_creation_allowed",
        "service_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
        "credentials_accessed",
        "unsafe_autonomy_claim",
        "vacation_mode_complete",
    ]:
        assert proof[field] is False


def test_validation_blocks_if_restart_or_timeout_are_tampered_true():
    m = _restart()
    proof = m.build_restart_timeouts_dry_run_proof(_healthy_inputs(), now="2026-01-01T00:05:00Z")
    tampered = dict(proof)
    tampered["restart_executed"] = True
    tampered["timeout_executed"] = True
    validation = m.validate_restart_timeouts_dry_run_proof(tampered)
    assert validation["status"] == "BLOCK"
    assert "restart_executed_true" in validation["unsafe_flags"]
    assert "timeout_executed_true" in validation["unsafe_flags"]


def test_validation_blocks_if_any_required_safety_flag_is_tampered_true():
    m = _restart()
    proof = m.build_restart_timeouts_dry_run_proof(_healthy_inputs(), now="2026-01-01T00:05:00Z")
    tampered = dict(proof)
    tampered["dispatch_allowed"] = True
    tampered["apply_allowed"] = True
    tampered["runtime_mutation_allowed"] = True
    tampered["scheduler_creation_allowed"] = True
    tampered["service_creation_allowed"] = True
    tampered["sos_allowed"] = True
    tampered["live_trading_allowed"] = True
    tampered["credentials_accessed"] = True
    tampered["unsafe_autonomy_claim"] = True
    tampered["vacation_mode_complete"] = True
    validation = m.validate_restart_timeouts_dry_run_proof(tampered)
    assert validation["status"] == "BLOCK"
    for flag in [
        "dispatch_allowed_true",
        "apply_allowed_true",
        "runtime_mutation_allowed_true",
        "scheduler_creation_allowed_true",
        "service_creation_allowed_true",
        "sos_allowed_true",
        "live_trading_allowed_true",
        "credentials_accessed_true",
        "unsafe_autonomy_claim_true",
        "vacation_mode_complete_true",
    ]:
        assert flag in validation["unsafe_flags"]


def test_proof_does_not_emit_command_strings():
    m = _restart()
    proof = m.build_restart_timeouts_dry_run_proof(_healthy_inputs(), now="2026-01-01T00:05:00Z")
    serialized = json.dumps(proof, sort_keys=True).lower()
    command_patterns = [
        ("git " + "push"),
        ("git " + "commit"),
        ("git " + "merge"),
        ("gh " + "pr " + "merge"),
        ("gh " + "pr " + "create"),
        ("register-" + "scheduledtask"),
        ("new-" + "service"),
        ("start-" + "job"),
        ("start-" + "process"),
        ("start-" + "service"),
        ("sub" + "process"),
        ("shell" + "=" + "true"),
        ("os" + ".system"),
    ]
    for pattern in command_patterns:
        assert pattern not in serialized


def test_proof_does_not_include_obvious_secret_assignment_strings():
    source = RESTART_PATH.read_text(encoding="utf-8").lower()
    patterns = [
        "secret" + "=",
        "token" + "=",
        "pass" + "word" + "=",
        "api" + "_key" + "=",
        "api" + "key" + "=",
        "bear" + "er ",
        "sk" + "-",
    ]
    assert all(pattern not in source for pattern in patterns)


def test_proof_is_deterministic_with_injected_now_and_input():
    m = _restart()
    inputs = _healthy_inputs()
    first = m.build_restart_timeouts_dry_run_proof(inputs, now="2026-01-01T00:05:00Z")
    second = m.build_restart_timeouts_dry_run_proof(inputs, now="2026-01-01T00:05:00Z")
    assert first == second


def test_summary_includes_core_proof_fields():
    m = _restart()
    proof = m.build_restart_timeouts_dry_run_proof(_healthy_inputs(), now="2026-01-01T00:05:00Z")
    summary = m.summarize_restart_timeouts_dry_run_proof(proof)
    assert summary["proof_status"] == "PASS"
    assert summary["healthy_state_detected"] is True
    assert summary["safe_next_action"]
    assert summary["vacation_mode_complete"] is False


def test_relay_runtime_queue_relay_review_ledger_and_selector_regressions_still_pass():
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_restart_regression")
    proc_mod = _load(PROCESSOR_PATH, "aios_relay_runtime_processor_for_restart_regression")
    review_mod = _load(REVIEW_PATH, "aios_relay_dry_run_proof_review_for_restart_regression")
    ledger_mod = _load(LEDGER_PATH, "aios_operator_dependency_ledger_for_restart_regression")
    selector_mod = _load(SELECTOR_PATH, "aios_reduction_target_selector_for_restart_regression")
    q = queue_mod.build_runtime_execution_queue()
    r = proc_mod.build_relay_runtime_processor(queue=q, now="2026-01-02T03:04:05Z")
    v = review_mod.build_relay_dry_run_proof_review(relay_readout=r, queue=q, now="2026-01-02T03:04:05Z")
    l = ledger_mod.build_operator_dependency_ledger(queue=q, relay_readout=r, relay_review=v, now="2026-01-02T03:04:05Z")
    s = selector_mod.build_reduction_target_selector(ledger=l, now="2026-01-02T03:04:05Z")
    assert queue_mod.validate_runtime_execution_queue(q)["status"] == "PASS"
    assert proc_mod.validate_relay_runtime_processor(r)["status"] == "PASS"
    assert review_mod.validate_relay_dry_run_proof_review(v)["status"] == "PASS"
    assert ledger_mod.validate_operator_dependency_ledger(l)["status"] == "PASS"
    assert selector_mod.validate_reduction_target_selector(s)["status"] == "PASS"
