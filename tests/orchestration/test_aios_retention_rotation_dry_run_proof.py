"""Tests for the AI_OS retention/rotation dry-run proof (observe-only)."""

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
LEDGER_PATH = REPO_ROOT / "automation" / "orchestration" / "autonomy_reports" / "aios_operator_dependency_ledger.py"
SELECTOR_PATH = REPO_ROOT / "automation" / "orchestration" / "autonomy_reports" / "aios_reduction_target_selector.py"
RETENTION_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_retention_rotation_dry_run_proof.py"


def _load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _queue(**state):
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_retention_tests")
    return queue_mod.build_runtime_execution_queue(state or None)


def _processor(**state):
    proc_mod = _load(PROCESSOR_PATH, "aios_relay_runtime_processor_for_retention_tests")
    return proc_mod.build_relay_runtime_processor(existing_state=state or None, queue=_queue(**state), now="2026-01-31T00:00:00Z")


def _review(**state):
    review_mod = _load(REVIEW_PATH, "aios_relay_dry_run_proof_review_for_retention_tests")
    return review_mod.build_relay_dry_run_proof_review(
        existing_state=state or None,
        relay_readout=_processor(**state),
        queue=_queue(**state),
        now="2026-01-31T00:00:00Z",
    )


def _restart_proof():
    restart_mod = _load(RESTART_PATH, "aios_restart_timeouts_dry_run_proof_for_retention_tests")
    return restart_mod.build_restart_timeouts_dry_run_proof(
        {
            "runtime_label": "aios-runtime",
            "runtime_expected": True,
            "checkpoint_expected": True,
            "last_heartbeat_utc": "2026-01-01T00:04:30Z",
            "last_checkpoint_utc": "2026-01-01T00:01:00Z",
        },
        now="2026-01-01T00:05:00Z",
    )


def _ledger(**state):
    ledger_mod = _load(LEDGER_PATH, "aios_operator_dependency_ledger_for_retention_tests")
    return ledger_mod.build_operator_dependency_ledger(
        state or None,
        queue=_queue(**state),
        relay_readout=_processor(**state),
        relay_review=_review(**state),
        now="2026-01-31T00:00:00Z",
    )


def _selector(**state):
    selector_mod = _load(SELECTOR_PATH, "aios_reduction_target_selector_for_retention_tests")
    return selector_mod.build_reduction_target_selector(state or None, ledger=_ledger(**state), now="2026-01-31T00:00:00Z")


def _retention():
    return _load(RETENTION_PATH, "aios_retention_rotation_dry_run_proof")


def _healthy_files():
    return [
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
    ]


def _oversized_files():
    return [
        {
            "path": "reports/runtime/b.jsonl",
            "kind": "jsonl",
            "created_at_utc": "2026-01-30T00:00:00Z",
            "updated_at_utc": "2026-01-30T00:00:00Z",
            "size_bytes": 2_000_000,
            "line_count": 9000,
            "contains_jsonl": True,
            "required": False,
        }
    ]


def _archive_files():
    return [
        {
            "path": "reports/runtime/c.jsonl",
            "kind": "jsonl",
            "created_at_utc": "2026-01-10T00:00:00Z",
            "updated_at_utc": "2026-01-10T00:00:00Z",
            "size_bytes": 4096,
            "line_count": 100,
            "contains_jsonl": True,
            "required": False,
        }
    ]


def _expired_files():
    return [
        {
            "path": "reports/runtime/d.jsonl",
            "kind": "jsonl",
            "created_at_utc": "2025-12-01T00:00:00Z",
            "updated_at_utc": "2025-12-20T00:00:00Z",
            "size_bytes": 4096,
            "line_count": 100,
            "contains_jsonl": True,
            "required": False,
        }
    ]


def _missing_metadata_files():
    return [
        {
            "path": "reports/runtime/e.jsonl",
            "kind": "jsonl",
            "created_at_utc": "2026-01-29T00:00:00Z",
            "contains_jsonl": True,
            "required": True,
        }
    ]


def _future_timestamp_files():
    return [
        {
            "path": "reports/runtime/f.jsonl",
            "kind": "jsonl",
            "created_at_utc": "2026-02-01T00:00:00Z",
            "updated_at_utc": "2026-02-01T00:00:00Z",
            "size_bytes": 2048,
            "line_count": 25,
            "contains_jsonl": True,
            "required": True,
        }
    ]


def _malformed_files():
    return ["not-a-metadata-object"]


def test_proof_builds_with_healthy_simulated_jsonl_metadata():
    m = _retention()
    proof = m.build_retention_rotation_dry_run_proof(_healthy_files(), now="2026-01-31T00:00:00Z")
    assert proof["schema"] == "AIOS_RETENTION_ROTATION_DRY_RUN_PROOF.v1"
    assert proof["mode"] == "DRY_RUN"
    assert proof["proof_type"] == "retention_rotation"
    assert proof["proof_status"] == "PASS"
    assert proof["keep_candidates"]


def test_healthy_input_includes_keep_candidate_and_passes_validation():
    m = _retention()
    proof = m.build_retention_rotation_dry_run_proof(_healthy_files(), now="2026-01-31T00:00:00Z")
    assert proof["keep_candidates"][0]["path"] == "reports/runtime/a.jsonl"
    assert proof["rotation_required"] is False
    assert m.validate_retention_rotation_dry_run_proof(proof)["status"] == "PASS"


def test_oversized_input_returns_attention_and_sets_rotation_required_without_executing_rotation():
    m = _retention()
    proof = m.build_retention_rotation_dry_run_proof(_oversized_files(), now="2026-01-31T00:00:00Z")
    assert proof["proof_status"] == "ATTENTION"
    assert proof["rotate_candidates"]
    assert proof["rotation_required"] is True
    assert proof["rotation_executed"] is False


def test_expired_input_returns_attention_and_sets_archive_required_true():
    m = _retention()
    proof = m.build_retention_rotation_dry_run_proof(_archive_files(), now="2026-01-31T00:00:00Z")
    assert proof["proof_status"] == "ATTENTION"
    assert proof["archive_candidates"]
    assert proof["archive_required"] is True
    assert proof["archive_executed"] is False
    assert proof["delete_executed"] is False


def test_expired_input_sets_delete_required_true_when_age_breaches_max_age():
    m = _retention()
    proof = m.build_retention_rotation_dry_run_proof(_expired_files(), now="2026-01-31T00:00:00Z")
    assert proof["proof_status"] == "ATTENTION"
    assert proof["expired_files"]
    assert proof["delete_required"] is True
    assert proof["delete_executed"] is False


def test_missing_metadata_returns_blocked_and_lists_missing_metadata():
    m = _retention()
    proof = m.build_retention_rotation_dry_run_proof(_missing_metadata_files(), now="2026-01-31T00:00:00Z")
    assert proof["proof_status"] == "BLOCKED"
    assert proof["missing_metadata"]


def test_future_timestamp_returns_blocked_and_lists_future_timestamp_files():
    m = _retention()
    proof = m.build_retention_rotation_dry_run_proof(_future_timestamp_files(), now="2026-01-31T00:00:00Z")
    assert proof["proof_status"] == "BLOCKED"
    assert proof["future_timestamp_files"]


def test_malformed_metadata_returns_blocked():
    m = _retention()
    proof = m.build_retention_rotation_dry_run_proof(_malformed_files(), now="2026-01-31T00:00:00Z")
    assert proof["proof_status"] == "BLOCKED"
    assert proof["malformed_inputs"]


def test_proof_is_dry_run_and_never_returns_complete():
    m = _retention()
    proof = m.build_retention_rotation_dry_run_proof(_healthy_files(), now="2026-01-31T00:00:00Z")
    assert proof["mode"] == "DRY_RUN"
    assert proof["proof_status"] != "COMPLETE"


def test_proof_keeps_mutation_and_live_flags_false():
    m = _retention()
    proof = m.build_retention_rotation_dry_run_proof(_healthy_files(), now="2026-01-31T00:00:00Z")
    for field in [
        "rotation_executed",
        "archive_executed",
        "delete_executed",
        "truncate_executed",
        "file_mutation_allowed",
        "telemetry_mutation_allowed",
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


def test_validation_blocks_if_any_tampered_mutation_or_live_flag_is_true():
    m = _retention()
    proof = m.build_retention_rotation_dry_run_proof(_healthy_files(), now="2026-01-31T00:00:00Z")
    tampered = dict(proof)
    for field in [
        "rotation_executed",
        "archive_executed",
        "delete_executed",
        "truncate_executed",
        "file_mutation_allowed",
        "telemetry_mutation_allowed",
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
        tampered[field] = True
    validation = m.validate_retention_rotation_dry_run_proof(tampered)
    assert validation["status"] == "BLOCK"
    for flag in [
        "rotation_executed_true",
        "archive_executed_true",
        "delete_executed_true",
        "truncate_executed_true",
        "file_mutation_allowed_true",
        "telemetry_mutation_allowed_true",
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
    m = _retention()
    proof = m.build_retention_rotation_dry_run_proof(_healthy_files(), now="2026-01-31T00:00:00Z")
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
    source = RETENTION_PATH.read_text(encoding="utf-8").lower()
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
    m = _retention()
    files = _healthy_files() + _oversized_files() + _archive_files()
    first = m.build_retention_rotation_dry_run_proof(files, now="2026-01-31T00:00:00Z")
    second = m.build_retention_rotation_dry_run_proof(files, now="2026-01-31T00:00:00Z")
    assert first == second


def test_summary_includes_core_proof_fields_and_counts():
    m = _retention()
    proof = m.build_retention_rotation_dry_run_proof(
        _healthy_files() + _oversized_files() + _archive_files() + _expired_files(),
        now="2026-01-31T00:00:00Z",
    )
    summary = m.summarize_retention_rotation_dry_run_proof(proof)
    assert summary["proof_status"] == "ATTENTION"
    assert summary["keep_count"] == 1
    assert summary["rotate_count"] == 1
    assert summary["archive_count"] == 1
    assert summary["review_count"] == 1
    assert summary["rotation_required"] is True
    assert summary["safe_next_action"]
    assert summary["vacation_mode_complete"] is False


def test_existing_spine_tests_still_pass():
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_retention_regression")
    proc_mod = _load(PROCESSOR_PATH, "aios_relay_runtime_processor_for_retention_regression")
    review_mod = _load(REVIEW_PATH, "aios_relay_dry_run_proof_review_for_retention_regression")
    restart_mod = _load(RESTART_PATH, "aios_restart_timeouts_dry_run_proof_for_retention_regression")
    ledger_mod = _load(LEDGER_PATH, "aios_operator_dependency_ledger_for_retention_regression")
    selector_mod = _load(SELECTOR_PATH, "aios_reduction_target_selector_for_retention_regression")
    queue = queue_mod.build_runtime_execution_queue()
    readout = proc_mod.build_relay_runtime_processor(queue=queue, now="2026-01-31T00:00:00Z")
    review = review_mod.build_relay_dry_run_proof_review(relay_readout=readout, queue=queue, now="2026-01-31T00:00:00Z")
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
    ledger = ledger_mod.build_operator_dependency_ledger(queue=queue, relay_readout=readout, relay_review=review, now="2026-01-31T00:00:00Z")
    selector = selector_mod.build_reduction_target_selector(ledger=ledger, now="2026-01-31T00:00:00Z")
    assert queue_mod.validate_runtime_execution_queue(queue)["status"] == "PASS"
    assert proc_mod.validate_relay_runtime_processor(readout)["status"] == "PASS"
    assert review_mod.validate_relay_dry_run_proof_review(review)["status"] == "PASS"
    assert restart_mod.validate_restart_timeouts_dry_run_proof(restart)["status"] == "PASS"
    assert ledger_mod.validate_operator_dependency_ledger(ledger)["status"] == "PASS"
    assert selector_mod.validate_reduction_target_selector(selector)["status"] == "PASS"
