"""Tests for the AI_OS reduction target selector (report-only)."""

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


def _load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _queue(**state):
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_selector_tests")
    return queue_mod.build_runtime_execution_queue(state or None)


def _processor(**state):
    proc_mod = _load(PROCESSOR_PATH, "aios_relay_runtime_processor_for_selector_tests")
    return proc_mod.build_relay_runtime_processor(existing_state=state or None, queue=_queue(**state), now="2026-01-02T03:04:05Z")


def _review(**state):
    review_mod = _load(REVIEW_PATH, "aios_relay_dry_run_proof_review_for_selector_tests")
    return review_mod.build_relay_dry_run_proof_review(
        existing_state=state or None,
        relay_readout=_processor(**state),
        queue=_queue(**state),
        now="2026-01-02T03:04:05Z",
    )


def _ledger(**state):
    ledger_mod = _load(LEDGER_PATH, "aios_operator_dependency_ledger_for_selector_tests")
    return ledger_mod.build_operator_dependency_ledger(
        state or None,
        queue=_queue(**state),
        relay_readout=_processor(**state),
        relay_review=_review(**state),
        now="2026-01-02T03:04:05Z",
    )


def _selector(**state):
    selector_mod = _load(SELECTOR_PATH, "aios_reduction_target_selector")
    return selector_mod.build_reduction_target_selector(state or None, ledger=_ledger(**state), now="2026-01-02T03:04:05Z")


def test_selector_can_build_from_current_operator_dependency_ledger():
    m = _load(SELECTOR_PATH, "aios_reduction_target_selector_build_test")
    readout = m.build_reduction_target_selector(now="2026-01-02T03:04:05Z")
    assert readout["schema"] == "AIOS_REDUCTION_TARGET_SELECTOR.v1"
    assert readout["mode"] == "REPORT_ONLY"
    assert readout["source_ledger_schema"] == "AIOS_OPERATOR_DEPENDENCY_LEDGER.v1"
    assert readout["source_autonomy_shift"] == "PARTIAL"


def test_selector_includes_all_dependency_categories():
    readout = _selector()
    assert set(readout["evaluated_dependency_categories"]) == {"remember", "notice", "decide", "route", "recover"}


def test_selector_records_source_ledger_schema_and_autonomy_shift():
    readout = _selector()
    assert readout["source_ledger_schema"] == "AIOS_OPERATOR_DEPENDENCY_LEDGER.v1"
    assert readout["source_autonomy_shift"] == "PARTIAL"


def test_selector_produces_candidate_targets_and_selects_non_empty_target():
    readout = _selector()
    assert readout["candidate_targets"]
    assert readout["selected_target"]
    assert readout["selected_reason"]


def test_selector_keeps_unsafe_autonomy_claim_and_vacation_mode_false():
    readout = _selector()
    assert readout["unsafe_autonomy_claim"] is False
    assert readout["vacation_mode_complete"] is False


def test_selector_blocks_dispatch_apply_runtime_scheduler_sos_and_live_flags():
    m = _load(SELECTOR_PATH, "aios_reduction_target_selector_flags_test")
    readout = m.build_reduction_target_selector(ledger=_ledger(), now="2026-01-02T03:04:05Z")
    for field in [
        "dispatch_allowed",
        "apply_allowed",
        "runtime_mutation_allowed",
        "scheduler_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
    ]:
        assert readout[field] is False


def test_selector_safe_next_action_is_non_empty():
    readout = _selector()
    assert readout["safe_next_action"]


def test_selector_uses_repo_held_inputs_from_ledger():
    readout = _selector()
    basis = readout["dependency_reduction_basis"]
    assert basis["source_blockers"]
    assert basis["source_human_gates"]
    assert basis["source_safe_next_action"]
    assert readout["ai_os_owned_inputs_used"]
    assert readout["remaining_human_burdens"]


def test_selector_does_not_emit_command_strings():
    readout = _selector()
    serialized = json.dumps(readout, sort_keys=True).lower()
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


def test_selector_does_not_include_obvious_secret_assignment_strings():
    source = SELECTOR_PATH.read_text(encoding="utf-8").lower()
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


def test_selector_is_deterministic_with_injected_now_and_input_ledger():
    m = _load(SELECTOR_PATH, "aios_reduction_target_selector_determinism_test")
    ledger = _ledger()
    first = m.build_reduction_target_selector(ledger=ledger, now="2026-01-02T03:04:05Z")
    second = m.build_reduction_target_selector(ledger=ledger, now="2026-01-02T03:04:05Z")
    assert first == second


def test_selector_validation_blocks_tampered_safety_flags():
    m = _load(SELECTOR_PATH, "aios_reduction_target_selector_validation_test")
    readout = m.build_reduction_target_selector(ledger=_ledger(), now="2026-01-02T03:04:05Z")
    tampered = dict(readout)
    tampered["dispatch_allowed"] = True
    validation = m.validate_reduction_target_selector(tampered)
    assert validation["status"] == "BLOCK"
    assert "dispatch_allowed_true" in validation["unsafe_flags"]


def test_selector_validation_blocks_when_dependency_category_missing():
    m = _load(SELECTOR_PATH, "aios_reduction_target_selector_dependency_test")
    readout = m.build_reduction_target_selector(ledger=_ledger(), now="2026-01-02T03:04:05Z")
    tampered = dict(readout)
    tampered["evaluated_dependency_categories"] = ["remember", "notice", "decide", "route"]
    validation = m.validate_reduction_target_selector(tampered)
    assert validation["status"] == "BLOCK"
    assert "dependency_categories_missing" in validation["unsafe_flags"]


def test_existing_runtime_and_relay_and_ledger_tests_still_pass():
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_selector_regression")
    proc_mod = _load(PROCESSOR_PATH, "aios_relay_runtime_processor_for_selector_regression")
    review_mod = _load(REVIEW_PATH, "aios_relay_dry_run_proof_review_for_selector_regression")
    ledger_mod = _load(LEDGER_PATH, "aios_operator_dependency_ledger_for_selector_regression")
    q = queue_mod.build_runtime_execution_queue()
    r = proc_mod.build_relay_runtime_processor(queue=q, now="2026-01-02T03:04:05Z")
    v = review_mod.build_relay_dry_run_proof_review(relay_readout=r, queue=q, now="2026-01-02T03:04:05Z")
    l = ledger_mod.build_operator_dependency_ledger(queue=q, relay_readout=r, relay_review=v, now="2026-01-02T03:04:05Z")
    assert queue_mod.validate_runtime_execution_queue(q)["status"] == "PASS"
    assert proc_mod.validate_relay_runtime_processor(r)["status"] == "PASS"
    assert review_mod.validate_relay_dry_run_proof_review(v)["status"] == "PASS"
    assert ledger_mod.validate_operator_dependency_ledger(l)["status"] == "PASS"
