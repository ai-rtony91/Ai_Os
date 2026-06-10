"""Tests for the AI_OS relay runtime processor (observe-only)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_runtime_execution_queue.py"
PROCESSOR_PATH = (
    REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_relay_runtime_processor.py"
)


def _load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _queue(**state):
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_relay_tests")
    return queue_mod.build_runtime_execution_queue(state or None)


def _processor():
    return _load(PROCESSOR_PATH, "aios_relay_runtime_processor")


def test_processor_identifies_relay_runtime_processor_as_next_lane_from_queue():
    m = _processor()
    q = _queue()
    readout = m.build_relay_runtime_processor(queue=q, now="2026-01-02T03:04:05Z")
    assert readout["next_lane"]["lane_id"] == "relay_runtime_processor"
    assert readout["source_queue_schema"] == "AIOS_RUNTIME_EXECUTION_QUEUE.v1"
    assert readout["lane_status"] == q["lanes"][0]["current_status"]


def test_processor_returns_dry_run_read_only_proof():
    m = _processor()
    readout = m.build_relay_runtime_processor(queue=_queue(), now="2026-01-02T03:04:05Z")
    assert readout["schema"] == "AIOS_RELAY_RUNTIME_PROCESSOR.v1"
    assert readout["mode"] == "DRY_RUN"
    assert readout["observe_only"] is True
    assert readout["dispatch_allowed"] is False
    assert readout["apply_allowed"] is False
    assert readout["runtime_mutation_allowed"] is False


def test_processor_blocks_dispatch_apply_and_runtime_mutation():
    m = _processor()
    readout = m.build_relay_runtime_processor(queue=_queue(), now="2026-01-02T03:04:05Z")
    tampered = dict(readout)
    tampered["dispatch_allowed"] = True
    tampered["apply_allowed"] = True
    tampered["runtime_mutation_allowed"] = True
    validation = m.validate_relay_runtime_processor(tampered)
    assert validation["status"] == "BLOCK"
    assert "dispatch_allowed_true" in validation["unsafe_flags"]
    assert "apply_allowed_true" in validation["unsafe_flags"]
    assert "runtime_mutation_allowed_true" in validation["unsafe_flags"]


def test_processor_reports_missing_predecessor_proofs_instead_of_advancing():
    m = _processor()
    readout = m.build_relay_runtime_processor(queue=_queue(), now="2026-01-02T03:04:05Z")
    assert readout["proof_status"] == "BLOCKED"
    assert readout["missing_proofs"] == readout["predecessor_requirements"]
    assert "missing predecessor proofs" in readout["safe_next_action"].lower()


def test_processor_preserves_sos_and_scheduler_as_human_only_blocked_gates():
    m = _processor()
    readout = m.build_relay_runtime_processor(queue=_queue(), now="2026-01-02T03:04:05Z")
    assert readout["blocked_human_gates"] == ["human_sos_arming", "human_scheduler_registration"]
    assert readout["human_only_gates"] == ["human_sos_arming", "human_scheduler_registration"]


def test_processor_refuses_vacation_mode_complete_true_without_required_proof_chain():
    m = _processor()
    readout = m.build_relay_runtime_processor(queue=_queue(), now="2026-01-02T03:04:05Z")
    tampered = dict(readout)
    tampered["vacation_mode_complete"] = True
    validation = m.validate_relay_runtime_processor(tampered)
    assert validation["status"] == "BLOCK"
    assert "vacation_mode_complete_true" in validation["unsafe_flags"]


def test_processor_emits_no_command_strings():
    m = _processor()
    readout = m.build_relay_runtime_processor(queue=_queue(), now="2026-01-02T03:04:05Z")
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


def test_processor_does_not_include_obvious_secret_assignment_strings():
    source = PROCESSOR_PATH.read_text(encoding="utf-8").lower()
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


def test_processor_is_deterministic_with_injected_now_and_input():
    m = _processor()
    q = _queue()
    first = m.build_relay_runtime_processor(queue=q, now="2026-01-02T03:04:05Z")
    second = m.build_relay_runtime_processor(queue=q, now="2026-01-02T03:04:05Z")
    assert first == second


def test_existing_runtime_queue_tests_still_pass_with_processor_imports():
    queue_mod = _load(QUEUE_PATH, "aios_runtime_execution_queue_for_relay_test_regression")
    q = queue_mod.build_runtime_execution_queue()
    assert queue_mod.validate_runtime_execution_queue(q)["status"] == "PASS"
    assert queue_mod.summarize_next_actions(q)["primary_lane"]["lane_id"] == "relay_runtime_processor"
