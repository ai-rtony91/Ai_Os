"""Tests for the AI_OS relay dry-run proof review (observe-only)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_runtime_execution_queue.py"
PROCESSOR_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_relay_runtime_processor.py"
REVIEW_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_relay_dry_run_proof_review.py"


def _load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _queue(**state):
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_relay_review_tests")
    return queue_mod.build_runtime_execution_queue(state or None)


def _processor():
    return _load(PROCESSOR_PATH, "aios_relay_runtime_processor_for_review_tests")


def _reviewer():
    return _load(REVIEW_PATH, "aios_relay_dry_run_proof_review")


def _reviewable_state():
    return {
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


def test_reviewer_can_build_from_current_queue_and_relay_processor_state():
    m = _reviewer()
    review = m.build_relay_dry_run_proof_review(existing_state=None, now="2026-01-02T03:04:05Z")
    assert review["schema"] == "AIOS_RELAY_DRY_RUN_PROOF_REVIEW.v1"
    assert review["mode"] == "DRY_RUN"
    assert review["observe_only"] is True
    assert review["source_relay_schema"] == "AIOS_RELAY_RUNTIME_PROCESSOR.v1"
    assert review["review_status"] == "BLOCKED"


def test_reviewer_returns_dry_run_read_only_output():
    m = _reviewer()
    review = m.build_relay_dry_run_proof_review(existing_state=None, now="2026-01-02T03:04:05Z")
    assert review["dispatch_allowed"] is False
    assert review["apply_allowed"] is False
    assert review["runtime_mutation_allowed"] is False
    assert review["vacation_mode_complete"] is False
    assert review["proof_reviewable"] is False


def test_reviewer_reports_blocked_when_predecessor_proofs_are_missing():
    m = _reviewer()
    review = m.build_relay_dry_run_proof_review(existing_state=None, now="2026-01-02T03:04:05Z")
    assert review["review_status"] == "BLOCKED"
    assert review["missing_proofs"]
    assert "missing predecessor proofs" in review["safe_next_action"].lower()


def test_reviewer_returns_invalid_if_dispatch_apply_or_runtime_mutation_flags_are_true():
    m = _reviewer()
    proc = _processor()
    readout = proc.build_relay_runtime_processor(existing_state=_reviewable_state(), now="2026-01-02T03:04:05Z")
    tampered = dict(readout)
    tampered["dispatch_allowed"] = True
    tampered["apply_allowed"] = True
    tampered["runtime_mutation_allowed"] = True
    review = m.build_relay_dry_run_proof_review(relay_readout=tampered, now="2026-01-02T03:04:05Z")
    assert review["review_status"] == "INVALID"
    assert "dispatch_allowed_true" in review["safety_flags"]
    assert "apply_allowed_true" in review["safety_flags"]
    assert "runtime_mutation_allowed_true" in review["safety_flags"]


def test_reviewer_refuses_vacation_mode_complete_true():
    m = _reviewer()
    proc = _processor()
    readout = proc.build_relay_runtime_processor(existing_state=_reviewable_state(), now="2026-01-02T03:04:05Z")
    tampered = dict(readout)
    tampered["vacation_mode_complete"] = True
    review = m.build_relay_dry_run_proof_review(relay_readout=tampered, now="2026-01-02T03:04:05Z")
    assert review["review_status"] == "INVALID"
    assert "vacation_mode_complete_true" in review["safety_flags"]


def test_reviewer_preserves_sos_and_scheduler_as_blocked_human_only_gates():
    m = _reviewer()
    review = m.build_relay_dry_run_proof_review(existing_state=None, now="2026-01-02T03:04:05Z")
    assert review["blocked_human_gates"] == ["human_sos_arming", "human_scheduler_registration"]
    assert review["human_only_gates"] == ["human_sos_arming", "human_scheduler_registration"]


def test_reviewer_does_not_emit_command_strings():
    m = _reviewer()
    review = m.build_relay_dry_run_proof_review(existing_state=None, now="2026-01-02T03:04:05Z")
    serialized = json.dumps(review, sort_keys=True).lower()
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


def test_reviewer_does_not_include_obvious_secret_assignment_strings():
    source = REVIEW_PATH.read_text(encoding="utf-8").lower()
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


def test_reviewer_is_deterministic_with_injected_now_and_readout():
    m = _reviewer()
    proc = _processor()
    readout = proc.build_relay_runtime_processor(existing_state=_reviewable_state(), now="2026-01-02T03:04:05Z")
    first = m.build_relay_dry_run_proof_review(relay_readout=readout, now="2026-01-02T03:04:05Z")
    second = m.build_relay_dry_run_proof_review(relay_readout=readout, now="2026-01-02T03:04:05Z")
    assert first == second


def test_existing_runtime_queue_and_relay_processor_tests_still_pass():
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_relay_review_regression")
    proc_mod = _load(PROCESSOR_PATH, "aios_relay_runtime_processor_for_relay_review_regression")
    q = queue_mod.build_runtime_execution_queue()
    readout = proc_mod.build_relay_runtime_processor(queue=q, now="2026-01-02T03:04:05Z")
    assert queue_mod.validate_runtime_execution_queue(q)["status"] == "PASS"
    assert proc_mod.validate_relay_runtime_processor(readout)["status"] == "PASS"
