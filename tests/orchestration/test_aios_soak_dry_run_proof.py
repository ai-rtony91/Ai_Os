"""Tests for the AI_OS soak dry-run proof (observe-only)."""

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
LEDGER_PATH = REPO_ROOT / "automation" / "orchestration" / "autonomy_reports" / "aios_operator_dependency_ledger.py"
SELECTOR_PATH = REPO_ROOT / "automation" / "orchestration" / "autonomy_reports" / "aios_reduction_target_selector.py"
SOAK_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_soak_dry_run_proof.py"


def _load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _queue(**state):
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_soak_tests")
    return queue_mod.build_runtime_execution_queue(state or None)


def _processor(**state):
    proc_mod = _load(PROCESSOR_PATH, "aios_relay_runtime_processor_for_soak_tests")
    return proc_mod.build_relay_runtime_processor(existing_state=state or None, queue=_queue(**state), now="2026-01-01T00:05:00Z")


def _review(**state):
    review_mod = _load(REVIEW_PATH, "aios_relay_dry_run_proof_review_for_soak_tests")
    return review_mod.build_relay_dry_run_proof_review(
        existing_state=state or None,
        relay_readout=_processor(**state),
        queue=_queue(**state),
        now="2026-01-01T00:05:00Z",
    )


def _restart_proof(status: str = "PASS"):
    restart_mod = _load(RESTART_PATH, "aios_restart_timeouts_dry_run_proof_for_soak_tests")
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


def _retention_proof(status: str = "PASS"):
    retention_mod = _load(RETENTION_PATH, "aios_retention_rotation_dry_run_proof_for_soak_tests")
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


def _ledger(**state):
    ledger_mod = _load(LEDGER_PATH, "aios_operator_dependency_ledger_for_soak_tests")
    return ledger_mod.build_operator_dependency_ledger(
        state or None,
        queue=_queue(**state),
        relay_readout=_processor(**state),
        relay_review=_review(**state),
        now="2026-01-01T00:05:00Z",
    )


def _selector(**state):
    selector_mod = _load(SELECTOR_PATH, "aios_reduction_target_selector_for_soak_tests")
    return selector_mod.build_reduction_target_selector(state or None, ledger=_ledger(**state), now="2026-01-01T00:05:00Z")


def _soak():
    return _load(SOAK_PATH, "aios_soak_dry_run_proof")


def _healthy_input():
    return {
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
    }


def _short_window_input():
    data = _healthy_input()
    data["window_end_utc"] = "2026-01-01T00:20:00Z"
    return data


def _heartbeat_gap_input():
    data = _healthy_input()
    data["heartbeat_samples_utc"] = [
        "2026-01-01T00:00:00Z",
        "2026-01-01T00:05:00Z",
        "2026-01-01T00:20:30Z",
    ]
    return data


def _checkpoint_gap_input():
    data = _healthy_input()
    data["checkpoint_samples_utc"] = [
        "2026-01-01T00:00:00Z",
        "2026-01-01T00:30:30Z",
    ]
    return data


def _missing_heartbeat_input():
    data = _healthy_input()
    data["heartbeat_samples_utc"] = []
    return data


def _missing_checkpoint_input():
    data = _healthy_input()
    data["checkpoint_samples_utc"] = []
    return data


def _invalid_timestamp_input():
    data = _healthy_input()
    data["heartbeat_samples_utc"] = ["not-a-timestamp"]
    return data


def _future_timestamp_input():
    data = _healthy_input()
    data["heartbeat_samples_utc"] = ["2026-01-01T00:00:00Z", "2026-01-01T02:00:00Z"]
    return data


def test_proof_builds_with_healthy_simulated_soak_input():
    m = _soak()
    proof = m.build_soak_dry_run_proof(
        _healthy_input(),
        restart_timeouts_proof=_restart_proof("PASS"),
        retention_rotation_proof=_retention_proof("PASS"),
        now="2026-01-01T01:00:00Z",
    )
    assert proof["schema"] == "AIOS_SOAK_DRY_RUN_PROOF.v1"
    assert proof["mode"] == "DRY_RUN"
    assert proof["proof_type"] == "soak"
    assert proof["proof_status"] == "PASS"
    assert proof["duration_sufficient"] is True
    assert proof["soak_pass"] is True


def test_healthy_input_returns_pass_and_continuity_true():
    m = _soak()
    proof = m.build_soak_dry_run_proof(
        _healthy_input(),
        restart_timeouts_proof=_restart_proof("PASS"),
        retention_rotation_proof=_retention_proof("PASS"),
        now="2026-01-01T01:00:00Z",
    )
    assert proof["proof_status"] == "PASS"
    assert proof["duration_sufficient"] is True
    assert proof["heartbeat_continuity_ok"] is True
    assert proof["checkpoint_continuity_ok"] is True
    assert proof["soak_pass"] is True
    assert proof["soak_executed"] is False
    assert proof["runtime_launched"] is False


def test_short_window_returns_attention_or_blocked_and_soak_pass_false():
    m = _soak()
    proof = m.build_soak_dry_run_proof(
        _short_window_input(),
        restart_timeouts_proof=_restart_proof("PASS"),
        retention_rotation_proof=_retention_proof("PASS"),
        now="2026-01-01T01:00:00Z",
    )
    assert proof["proof_status"] in {"ATTENTION", "BLOCKED"}
    assert proof["duration_sufficient"] is False
    assert proof["soak_pass"] is False


def test_heartbeat_gap_returns_attention_and_marks_stale_heartbeats():
    m = _soak()
    proof = m.build_soak_dry_run_proof(
        _heartbeat_gap_input(),
        restart_timeouts_proof=_restart_proof("PASS"),
        retention_rotation_proof=_retention_proof("PASS"),
        now="2026-01-01T01:00:00Z",
    )
    assert proof["proof_status"] == "ATTENTION"
    assert proof["heartbeat_continuity_ok"] is False
    assert proof["stale_heartbeats_detected"] is True
    assert proof["soak_pass"] is False


def test_checkpoint_gap_returns_attention_and_marks_checkpoint_gaps():
    m = _soak()
    proof = m.build_soak_dry_run_proof(
        _checkpoint_gap_input(),
        restart_timeouts_proof=_restart_proof("PASS"),
        retention_rotation_proof=_retention_proof("PASS"),
        now="2026-01-01T01:00:00Z",
    )
    assert proof["proof_status"] == "ATTENTION"
    assert proof["checkpoint_continuity_ok"] is False
    assert proof["checkpoint_gaps_detected"] is True
    assert proof["soak_pass"] is False


def test_missing_heartbeat_samples_are_detected():
    m = _soak()
    proof = m.build_soak_dry_run_proof(
        _missing_heartbeat_input(),
        restart_timeouts_proof=_restart_proof("PASS"),
        retention_rotation_proof=_retention_proof("PASS"),
        now="2026-01-01T01:00:00Z",
    )
    assert proof["proof_status"] == "BLOCKED"
    assert proof["missing_heartbeats_detected"] is True


def test_missing_checkpoint_samples_are_detected():
    m = _soak()
    proof = m.build_soak_dry_run_proof(
        _missing_checkpoint_input(),
        restart_timeouts_proof=_restart_proof("PASS"),
        retention_rotation_proof=_retention_proof("PASS"),
        now="2026-01-01T01:00:00Z",
    )
    assert proof["proof_status"] == "BLOCKED"
    assert proof["missing_checkpoints_detected"] is True


def test_blocked_restart_timeouts_proof_blocks_soak_proof():
    m = _soak()
    proof = m.build_soak_dry_run_proof(
        _healthy_input(),
        restart_timeouts_proof=_restart_proof("BLOCKED"),
        retention_rotation_proof=_retention_proof("PASS"),
        now="2026-01-01T01:00:00Z",
    )
    assert proof["proof_status"] == "BLOCKED"
    assert proof["blockers"]
    assert proof["soak_pass"] is False


def test_blocked_retention_rotation_proof_blocks_soak_proof():
    m = _soak()
    proof = m.build_soak_dry_run_proof(
        _healthy_input(),
        restart_timeouts_proof=_restart_proof("PASS"),
        retention_rotation_proof=_retention_proof("BLOCKED"),
        now="2026-01-01T01:00:00Z",
    )
    assert proof["proof_status"] == "BLOCKED"
    assert proof["blockers"]
    assert proof["soak_pass"] is False


def test_invalid_timestamp_returns_blocked():
    m = _soak()
    proof = m.build_soak_dry_run_proof(
        _invalid_timestamp_input(),
        restart_timeouts_proof=_restart_proof("PASS"),
        retention_rotation_proof=_retention_proof("PASS"),
        now="2026-01-01T01:00:00Z",
    )
    assert proof["proof_status"] == "BLOCKED"
    assert proof["invalid_timestamps"]


def test_future_timestamp_returns_blocked():
    m = _soak()
    proof = m.build_soak_dry_run_proof(
        _future_timestamp_input(),
        restart_timeouts_proof=_restart_proof("PASS"),
        retention_rotation_proof=_retention_proof("PASS"),
        now="2026-01-01T01:00:00Z",
    )
    assert proof["proof_status"] == "BLOCKED"
    assert proof["future_timestamps"]


def test_proof_is_dry_run_and_never_returns_complete():
    m = _soak()
    proof = m.build_soak_dry_run_proof(
        _healthy_input(),
        restart_timeouts_proof=_restart_proof("PASS"),
        retention_rotation_proof=_retention_proof("PASS"),
        now="2026-01-01T01:00:00Z",
    )
    assert proof["mode"] == "DRY_RUN"
    assert proof["proof_status"] != "COMPLETE"


def test_proof_keeps_all_mutation_and_live_flags_false():
    m = _soak()
    proof = m.build_soak_dry_run_proof(
        _healthy_input(),
        restart_timeouts_proof=_restart_proof("PASS"),
        retention_rotation_proof=_retention_proof("PASS"),
        now="2026-01-01T01:00:00Z",
    )
    for field in [
        "soak_executed",
        "runtime_launched",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_mutation_allowed",
        "telemetry_mutation_allowed",
        "scheduler_creation_allowed",
        "service_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
        "credentials_accessed",
        "unsafe_autonomy_claim",
        "vacation_mode_complete",
    ]:
        assert proof[field] is False


def test_validation_blocks_if_any_tampered_mutation_or_live_flag_is_true():
    m = _soak()
    proof = m.build_soak_dry_run_proof(
        _healthy_input(),
        restart_timeouts_proof=_restart_proof("PASS"),
        retention_rotation_proof=_retention_proof("PASS"),
        now="2026-01-01T01:00:00Z",
    )
    tampered = dict(proof)
    for field in [
        "soak_executed",
        "runtime_launched",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_mutation_allowed",
        "telemetry_mutation_allowed",
        "scheduler_creation_allowed",
        "service_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
        "credentials_accessed",
        "unsafe_autonomy_claim",
        "vacation_mode_complete",
    ]:
        tampered[field] = True
    validation = m.validate_soak_dry_run_proof(tampered)
    assert validation["status"] == "BLOCK"
    for flag in [
        "soak_executed_true",
        "runtime_launched_true",
        "dispatch_allowed_true",
        "apply_allowed_true",
        "runtime_mutation_allowed_true",
        "telemetry_mutation_allowed_true",
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
    m = _soak()
    proof = m.build_soak_dry_run_proof(
        _healthy_input(),
        restart_timeouts_proof=_restart_proof("PASS"),
        retention_rotation_proof=_retention_proof("PASS"),
        now="2026-01-01T01:00:00Z",
    )
    serialized = json.dumps(proof, sort_keys=True).lower()
    command_patterns = [
        ("git " + "push"),
        ("git " + "commit"),
        ("git " + "merge"),
        ("gh " + "pr " + "create"),
        ("gh " + "pr " + "merge"),
        ("register-" + "scheduledtask"),
        ("new-" + "service"),
        ("start-" + "job"),
        ("start-" + "process"),
        ("start-" + "service"),
        ("sub" + "process"),
        ("shell" + "=" + "true"),
        ("os" + ".system"),
        ("rm" + " -rf"),
        ("remove" + "-" + "item"),
        ("un" + "link"),
        ("re" + "name"),
        ("re" + "place"),
        ("mi" + "kdir"),
        ("open" + "("),
    ]
    for pattern in command_patterns:
        assert pattern not in serialized


def test_proof_does_not_include_obvious_secret_assignment_strings():
    source = SOAK_PATH.read_text(encoding="utf-8").lower()
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
    m = _soak()
    soak_input = _healthy_input()
    restart = _restart_proof("PASS")
    retention = _retention_proof("PASS")
    first = m.build_soak_dry_run_proof(
        soak_input,
        restart_timeouts_proof=restart,
        retention_rotation_proof=retention,
        now="2026-01-01T01:00:00Z",
    )
    second = m.build_soak_dry_run_proof(
        soak_input,
        restart_timeouts_proof=restart,
        retention_rotation_proof=retention,
        now="2026-01-01T01:00:00Z",
    )
    assert first == second


def test_summary_includes_core_proof_fields_and_counts():
    m = _soak()
    proof = m.build_soak_dry_run_proof(
        _heartbeat_gap_input(),
        restart_timeouts_proof=_restart_proof("ATTENTION"),
        retention_rotation_proof=_retention_proof("ATTENTION"),
        now="2026-01-01T01:00:00Z",
    )
    summary = m.summarize_soak_dry_run_proof(proof)
    assert summary["proof_status"] == "ATTENTION"
    assert summary["soak_pass"] is False
    assert summary["attention_count"] >= 1
    assert summary["blocker_count"] >= 0
    assert summary["safe_next_action"]
    assert summary["vacation_mode_complete"] is False


def test_existing_spine_tests_still_pass():
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_soak_regression")
    proc_mod = _load(PROCESSOR_PATH, "aios_relay_runtime_processor_for_soak_regression")
    review_mod = _load(REVIEW_PATH, "aios_relay_dry_run_proof_review_for_soak_regression")
    restart_mod = _load(RESTART_PATH, "aios_restart_timeouts_dry_run_proof_for_soak_regression")
    retention_mod = _load(RETENTION_PATH, "aios_retention_rotation_dry_run_proof_for_soak_regression")
    ledger_mod = _load(LEDGER_PATH, "aios_operator_dependency_ledger_for_soak_regression")
    selector_mod = _load(SELECTOR_PATH, "aios_reduction_target_selector_for_soak_regression")
    queue = queue_mod.build_runtime_execution_queue()
    readout = proc_mod.build_relay_runtime_processor(queue=queue, now="2026-01-01T00:05:00Z")
    review = review_mod.build_relay_dry_run_proof_review(relay_readout=readout, queue=queue, now="2026-01-01T00:05:00Z")
    restart = restart_mod.build_restart_timeouts_dry_run_proof(
        {
            "runtime_label": "aios-runtime",
            "runtime_expected": True,
            "checkpoint_expected": True,
            "last_heartbeat_utc": "2026-01-01T00:04:30Z",
            "last_checkpoint_utc": "2026-01-01T00:01:00Z",
        },
        now="2026-01-01T00:05:00Z",
    )
    retention = retention_mod.build_retention_rotation_dry_run_proof(
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
    ledger = ledger_mod.build_operator_dependency_ledger(queue=queue, relay_readout=readout, relay_review=review, now="2026-01-01T00:05:00Z")
    selector = selector_mod.build_reduction_target_selector(ledger=ledger, now="2026-01-01T00:05:00Z")
    assert queue_mod.validate_runtime_execution_queue(queue)["status"] == "PASS"
    assert proc_mod.validate_relay_runtime_processor(readout)["status"] == "PASS"
    assert review_mod.validate_relay_dry_run_proof_review(review)["status"] == "PASS"
    assert restart_mod.validate_restart_timeouts_dry_run_proof(restart)["status"] == "PASS"
    assert retention_mod.validate_retention_rotation_dry_run_proof(retention)["status"] == "PASS"
    assert ledger_mod.validate_operator_dependency_ledger(ledger)["status"] == "PASS"
    assert selector_mod.validate_reduction_target_selector(selector)["status"] == "PASS"
