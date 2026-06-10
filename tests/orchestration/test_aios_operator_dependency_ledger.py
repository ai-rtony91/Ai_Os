"""Tests for the AI_OS operator dependency ledger (report-only)."""

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


def _load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _queue(**state):
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_dependency_ledger_tests")
    return queue_mod.build_runtime_execution_queue(state or None)


def _processor(**state):
    proc_mod = _load(PROCESSOR_PATH, "aios_relay_runtime_processor_for_dependency_ledger_tests")
    return proc_mod.build_relay_runtime_processor(existing_state=state or None, queue=_queue(**state), now="2026-01-02T03:04:05Z")


def _review(**state):
    review_mod = _load(REVIEW_PATH, "aios_relay_dry_run_proof_review_for_dependency_ledger_tests")
    return review_mod.build_relay_dry_run_proof_review(
        existing_state=state or None,
        relay_readout=_processor(**state),
        queue=_queue(**state),
        now="2026-01-02T03:04:05Z",
    )


def _ledger(**state):
    ledger_mod = _load(LEDGER_PATH, "aios_operator_dependency_ledger")
    return ledger_mod.build_operator_dependency_ledger(
        state or None,
        queue=_queue(**state),
        relay_readout=_processor(**state),
        relay_review=_review(**state),
        now="2026-01-02T03:04:05Z",
    )


def test_ledger_builds_from_current_ai_os_components():
    m = _load(LEDGER_PATH, "aios_operator_dependency_ledger_build_test")
    ledger = m.build_operator_dependency_ledger(now="2026-01-02T03:04:05Z")
    assert ledger["schema"] == "AIOS_OPERATOR_DEPENDENCY_LEDGER.v1"
    assert ledger["mode"] == "REPORT_ONLY"
    assert ledger["scope"] == [
        "runtime_execution_queue",
        "relay_runtime_processor",
        "relay_dry_run_proof_review",
    ]
    assert [component["component_id"] for component in ledger["evaluated_components"]] == [
        "runtime_execution_queue",
        "relay_runtime_processor",
        "relay_dry_run_proof_review",
    ]


def test_ledger_includes_all_five_dependency_categories():
    ledger = _ledger()
    categories = {item["category"] for item in ledger["operator_dependency_items"]}
    assert categories == {"remember", "notice", "decide", "route", "recover"}


def test_ledger_records_ai_os_owned_items_and_human_burdens():
    ledger = _ledger()
    owned = {(item["component_id"], item["item"]) for item in ledger["ai_os_owned_items"]}
    assert ("runtime_execution_queue", "next_strict_serial_order") in owned
    assert ("runtime_execution_queue", "proof_chain") in owned
    assert ("relay_runtime_processor", "missing_proofs") in owned
    assert ("relay_dry_run_proof_review", "review_status") in owned
    assert ("relay_dry_run_proof_review", "safe_next_action") in owned
    assert ledger["remaining_human_burdens"]
    assert ledger["reduced_burdens"]


def test_ledger_keeps_unsafe_autonomy_claim_false_and_vacation_mode_false():
    ledger = _ledger()
    assert ledger["unsafe_autonomy_claim"] is False
    assert ledger["vacation_mode_complete"] is False


def test_ledger_is_deterministic_with_injected_now_and_input():
    m = _load(LEDGER_PATH, "aios_operator_dependency_ledger_determinism_test")
    queue = _queue()
    relay = _processor()
    review = _review()
    first = m.build_operator_dependency_ledger(
        queue=queue,
        relay_readout=relay,
        relay_review=review,
        now="2026-01-02T03:04:05Z",
    )
    second = m.build_operator_dependency_ledger(
        queue=queue,
        relay_readout=relay,
        relay_review=review,
        now="2026-01-02T03:04:05Z",
    )
    assert first == second


def test_ledger_does_not_emit_command_strings():
    ledger = _ledger()
    serialized = json.dumps(ledger, sort_keys=True).lower()
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


def test_ledger_does_not_include_obvious_secret_assignment_strings():
    source = LEDGER_PATH.read_text(encoding="utf-8").lower()
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


def test_ledger_identifies_a_next_reduction_target():
    ledger = _ledger()
    target = ledger["next_reduction_target"]
    assert target["component_id"] in {"relay_dry_run_proof_review", "relay_runtime_processor", "restart_supervisor_timeouts"}
    assert target["safe_next_action"]
    assert ledger["autonomy_scorecard"]["autonomy_shift"] == "PARTIAL"


def test_existing_runtime_queue_relay_and_review_tests_still_pass():
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_dependency_ledger_regression")
    proc_mod = _load(PROCESSOR_PATH, "aios_relay_runtime_processor_for_dependency_ledger_regression")
    review_mod = _load(REVIEW_PATH, "aios_relay_dry_run_proof_review_for_dependency_ledger_regression")
    q = queue_mod.build_runtime_execution_queue()
    r = proc_mod.build_relay_runtime_processor(queue=q, now="2026-01-02T03:04:05Z")
    v = review_mod.build_relay_dry_run_proof_review(relay_readout=r, queue=q, now="2026-01-02T03:04:05Z")
    assert queue_mod.validate_runtime_execution_queue(q)["status"] == "PASS"
    assert proc_mod.validate_relay_runtime_processor(r)["status"] == "PASS"
    assert review_mod.validate_relay_dry_run_proof_review(v)["status"] == "PASS"
