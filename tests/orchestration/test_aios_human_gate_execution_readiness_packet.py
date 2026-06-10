"""Tests for the AI_OS human gate execution readiness packet."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROOF_GATE_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_runtime_proof_gate.py"
PACKET_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_human_gate_execution_readiness_packet.py"
QUEUE_VIEW_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_queue" / "aios_runtime_execution_queue.py"
QUEUE_VALIDATOR_PATH = REPO_ROOT / "automation" / "validators" / "aios_runtime_execution_queue_validator.py"
QUEUE_CLOSURE_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_runtime_execution_queue.py"
RELAY_PROCESSOR_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_relay_runtime_processor.py"
RELAY_REVIEW_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_relay_dry_run_proof_review.py"
RESTART_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_restart_timeouts_dry_run_proof.py"
RETENTION_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_retention_rotation_dry_run_proof.py"
SOAK_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_soak_dry_run_proof.py"
LEDGER_PATH = REPO_ROOT / "automation" / "orchestration" / "autonomy_reports" / "aios_operator_dependency_ledger.py"
SELECTOR_PATH = REPO_ROOT / "automation" / "orchestration" / "autonomy_reports" / "aios_reduction_target_selector.py"


def _load(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _runtime_gate_ready():
    m = _load(PROOF_GATE_PATH, "aios_runtime_proof_gate_for_packet_tests")
    gate = m.build_runtime_proof_gate(now="2026-01-02T03:04:05Z")
    gate.update(
        {
            "final_verdict": "READY_FOR_HUMAN_GATE",
            "final_verdict_reason": "Proof chain is safe enough for human review.",
            "human_gate_required": True,
            "human_gate_ready": True,
            "execution_allowed": False,
            "dispatch_allowed": False,
            "apply_allowed": False,
            "runtime_launch_allowed": False,
            "runtime_mutation_allowed": False,
            "telemetry_mutation_allowed": False,
            "scheduler_creation_allowed": False,
            "service_creation_allowed": False,
            "sos_allowed": False,
            "live_trading_allowed": False,
            "credentials_accessed": False,
            "approval_granted": False,
            "vacation_mode_complete": False,
            "unsafe_autonomy_claim": False,
            "runtime_proof_gate_present": True if "runtime_proof_gate_present" in gate else True,
            "blockers": [],
            "attention_reasons": [],
            "invalid_reasons": [],
            "unsafe_flags_detected": [],
            "forbidden_claims_detected": [],
            "safe_next_action": "Present the connected proof chain for human review only.",
            "stop_condition": "Stop after human review; do not execute.",
            "prerequisite_inputs_missing": [],
            "prerequisite_inputs_present": [
                "runtime_queue_readout",
                "relay_processor_readout",
                "relay_proof_review",
                "restart_timeouts_proof",
                "retention_rotation_proof",
                "soak_proof",
                "operator_dependency_ledger",
                "reduction_target_selector",
            ],
            "accepted_prerequisites": [
                "runtime_queue",
                "relay_processor",
                "relay_proof_review",
                "restart_timeouts_proof",
                "retention_rotation_proof",
                "soak_proof",
                "operator_dependency_ledger",
                "reduction_target_selector",
            ],
            "rejected_prerequisites": [],
            "prerequisite_statuses": {
                "runtime_queue": "PASS",
                "relay_processor": "PASS",
                "relay_proof_review": "REVIEWABLE",
                "restart_timeouts_proof": "PASS",
                "retention_rotation_proof": "PASS",
                "soak_proof": "PASS",
                "operator_dependency_ledger": "PASS",
                "reduction_target_selector": "PASS",
            },
        }
    )
    gate["proof_chain_summary"] = {
        "runtime_queue": {"validation_status": "PASS", "safe_next_action": "Queue is gated."},
        "relay_processor": {"proof_status": "DRY_RUN_PROVEN", "safe_next_action": "Relay preview only."},
        "relay_review": {"review_status": "REVIEWABLE", "safe_next_action": "Human acceptance required."},
        "restart_timeouts": {"proof_status": "PASS", "safe_next_action": "Restart/timeouts proof is acceptable."},
        "retention_rotation": {"proof_status": "PASS", "safe_next_action": "Retention/rotation proof is acceptable."},
        "soak": {"proof_status": "PASS", "soak_pass": True, "safe_next_action": "Soak proof is acceptable."},
    }
    gate["runtime_queue_summary"] = {"validation_status": "PASS", "safe_next_action": "Queue is gated."}
    gate["relay_summary"] = {"review_status": "REVIEWABLE", "safe_next_action": "Relay review only."}
    gate["restart_timeouts_summary"] = {"proof_status": "PASS", "safe_next_action": "Restart/timeouts proof is acceptable."}
    gate["retention_rotation_summary"] = {"proof_status": "PASS", "safe_next_action": "Retention/rotation proof is acceptable."}
    gate["soak_summary"] = {"proof_status": "PASS", "soak_pass": True, "safe_next_action": "Soak proof is acceptable."}
    gate["operator_dependency_summary"] = {
        "autonomy_shift": "PARTIAL",
        "remaining_human_burdens": [{"category": "review"}],
        "reduced_burdens": [{"category": "route"}],
        "next_reduction_target": {"component_id": "relay_proof_acceptance_packet"},
    }
    gate["reduction_target_summary"] = {
        "selected_target": "relay_proof_acceptance_packet",
        "selected_category": "route",
        "selected_reason": "Human acceptance packet is the next reduction target.",
        "safe_next_action_from_selector": "Present the acceptance packet for human review only.",
        "selector_blocks_execution": True,
    }
    return gate


def _canonical_queue_view():
    return {
        "schema": "AIOS_RUNTIME_EXECUTION_QUEUE.v1",
        "generated_at": "2026-01-02T03:04:05Z",
        "observe_only": True,
        "item_count": 3,
        "items": [
            {
                "id": "relay_runtime_processor",
                "synthetic_id": False,
                "source": "relay_inbox",
                "kind": "packet",
                "state": "QUEUED",
                "raw_state": "queued",
                "allowed_paths": [],
                "protected_action": False,
                "created_utc": "2026-01-01T00:00:00Z",
            },
            {
                "id": "restart_supervisor_timeouts",
                "synthetic_id": False,
                "source": "relay_inbox",
                "kind": "packet",
                "state": "RUNNING",
                "raw_state": "running",
                "allowed_paths": [],
                "protected_action": False,
                "created_utc": "2026-01-01T00:05:00Z",
            },
            {
                "id": "soak_endurance_proof",
                "synthetic_id": False,
                "source": "relay_inbox",
                "kind": "packet",
                "state": "DEFERRED",
                "raw_state": "deferred",
                "allowed_paths": [],
                "protected_action": False,
                "created_utc": "2026-01-01T00:10:00Z",
            },
        ],
        "source_map": {"relay_inbox": 3},
        "sources_read": ["relay_inbox"],
        "sources_missing": [],
        "sources_malformed": [],
        "sources_index_only": [],
        "id_collisions": [],
        "state_counts": {"QUEUED": 1, "RUNNING": 1, "DEFERRED": 1},
        "protected_item_count": 0,
        "canonical_states": ["BLOCKED", "DEFERRED", "DONE", "ERROR", "QUEUED", "RUNNING"],
        "safe_next_action": "Read-only normalized view. Nothing enqueued or executed.",
    }


def _queue_validation():
    validator_mod = _load(QUEUE_VALIDATOR_PATH, "aios_runtime_execution_queue_validator_for_packet_tests")
    return validator_mod.validate_queue_view(_canonical_queue_view())


def _operator_dependency_ledger():
    ledger_mod = _load(LEDGER_PATH, "aios_operator_dependency_ledger_for_packet_tests")
    return ledger_mod.build_operator_dependency_ledger(now="2026-01-02T03:04:05Z")


def _reduction_target_selector():
    selector_mod = _load(SELECTOR_PATH, "aios_reduction_target_selector_for_packet_tests")
    selector = selector_mod.build_reduction_target_selector(
        ledger=_operator_dependency_ledger(),
        now="2026-01-02T03:04:05Z",
    )
    selector = dict(selector)
    selector["candidate_targets"] = list(selector.get("candidate_targets") or [])
    if not any(isinstance(item, dict) and item.get("target_id") == "relay_proof_acceptance_packet" for item in selector["candidate_targets"]):
        selector["candidate_targets"].append(
            {
                "target_id": "relay_proof_acceptance_packet",
                "category": "route",
                "reason": "Human acceptance packet is the next reduction target.",
                "supported_by": ["review_status", "proof_status", "safe_next_action", "human_gates"],
                "requires_human": True,
                "scheduler_required": False,
                "sos_required": False,
                "live_required": False,
            }
        )
    selector["selected_target"] = "relay_proof_acceptance_packet"
    selector["selected_category"] = "route"
    selector["selected_reason"] = "Human acceptance packet is the next reduction target."
    selector["safe_next_action"] = "Present the acceptance packet for human review only."
    selector["source_autonomy_shift"] = "PARTIAL"
    return selector


def _safe_packet():
    packet_mod = _load(PACKET_PATH, "aios_human_gate_execution_readiness_packet_for_packet_tests")
    packet = packet_mod.build_human_gate_execution_readiness_packet(
        runtime_proof_gate=_runtime_gate_ready(),
        canonical_runtime_queue_view=_canonical_queue_view(),
        runtime_queue_validation=_queue_validation(),
        operator_dependency_ledger=_operator_dependency_ledger(),
        reduction_target_selector=_reduction_target_selector(),
        now="2026-01-02T03:04:05Z",
    )
    return packet


def test_prerequisite_files_exist_on_current_base():
    for path in [
        PROOF_GATE_PATH,
        QUEUE_VIEW_PATH,
        QUEUE_VALIDATOR_PATH,
        QUEUE_CLOSURE_PATH,
        RELAY_PROCESSOR_PATH,
        RELAY_REVIEW_PATH,
        RESTART_PATH,
        RETENTION_PATH,
        SOAK_PATH,
        LEDGER_PATH,
        SELECTOR_PATH,
    ]:
        assert path.exists()


def test_packet_builds_from_safe_runtime_gate_queue_validation_ledger_and_selector():
    packet = _safe_packet()
    assert packet["schema"] == "AIOS_HUMAN_GATE_EXECUTION_READINESS_PACKET.v1"
    assert packet["mode"] == "HUMAN_GATE_PACKET"
    assert packet["packet_type"] == "execution_readiness"
    assert packet["packet_status"] == "READY_FOR_HUMAN_REVIEW"
    assert packet["human_review_required"] is True
    assert packet["approval_granted"] is False
    assert packet["execution_allowed"] is False
    assert packet["dispatch_allowed"] is False
    assert packet["apply_allowed"] is False
    assert packet["runtime_launch_allowed"] is False
    assert packet["queue_mutation_allowed"] is False


def test_ready_for_human_review_requires_human_review_only_and_no_execution_flags():
    packet = _safe_packet()
    for field in [
        "approval_granted",
        "execution_allowed",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_launch_allowed",
        "queue_mutation_allowed",
        "scheduler_creation_allowed",
        "service_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
    ]:
        assert packet[field] is False
    assert packet["human_review_required"] is True
    assert packet["safe_next_action"]
    assert packet["stop_condition"]


def test_missing_runtime_proof_gate_blocks():
    packet_mod = _load(PACKET_PATH, "aios_human_gate_execution_readiness_packet_missing_gate")
    packet = packet_mod.build_human_gate_execution_readiness_packet(
        canonical_runtime_queue_view=_canonical_queue_view(),
        runtime_queue_validation=_queue_validation(),
        operator_dependency_ledger=_operator_dependency_ledger(),
        reduction_target_selector=_reduction_target_selector(),
        now="2026-01-02T03:04:05Z",
    )
    assert packet["packet_status"] == "BLOCKED"


def test_runtime_proof_gate_blocked_blocks_packet():
    gate = _runtime_gate_ready()
    gate["final_verdict"] = "BLOCKED"
    gate["runtime_proof_gate_human_gate_ready"] = False
    packet_mod = _load(PACKET_PATH, "aios_human_gate_execution_readiness_packet_blocked_gate")
    packet = packet_mod.build_human_gate_execution_readiness_packet(
        runtime_proof_gate=gate,
        canonical_runtime_queue_view=_canonical_queue_view(),
        runtime_queue_validation=_queue_validation(),
        operator_dependency_ledger=_operator_dependency_ledger(),
        reduction_target_selector=_reduction_target_selector(),
        now="2026-01-02T03:04:05Z",
    )
    assert packet["packet_status"] == "BLOCKED"


def test_runtime_proof_gate_invalidates_packet_when_forbidden_claim_present():
    gate = _runtime_gate_ready()
    gate["final_verdict"] = "COMPLETE"
    packet_mod = _load(PACKET_PATH, "aios_human_gate_execution_readiness_packet_invalid_gate")
    packet = packet_mod.build_human_gate_execution_readiness_packet(
        runtime_proof_gate=gate,
        canonical_runtime_queue_view=_canonical_queue_view(),
        runtime_queue_validation=_queue_validation(),
        operator_dependency_ledger=_operator_dependency_ledger(),
        reduction_target_selector=_reduction_target_selector(),
        now="2026-01-02T03:04:05Z",
    )
    assert packet["packet_status"] == "INVALID"


def test_runtime_proof_gate_attention_yields_attention_not_ready():
    gate = _runtime_gate_ready()
    gate["final_verdict"] = "ATTENTION"
    gate["human_gate_ready"] = False
    packet_mod = _load(PACKET_PATH, "aios_human_gate_execution_readiness_packet_attention_gate")
    packet = packet_mod.build_human_gate_execution_readiness_packet(
        runtime_proof_gate=gate,
        canonical_runtime_queue_view=_canonical_queue_view(),
        runtime_queue_validation=_queue_validation(),
        operator_dependency_ledger=_operator_dependency_ledger(),
        reduction_target_selector=_reduction_target_selector(),
        now="2026-01-02T03:04:05Z",
    )
    assert packet["packet_status"] == "ATTENTION"


def test_queue_validation_pass_supports_readiness():
    packet = _safe_packet()
    assert packet["queue_validation_status"] == "PASS"
    assert packet["queue_validation_blockers"] == []
    assert packet["canonical_queue_item_count"] == 3


def test_missing_queue_validation_blocks():
    packet_mod = _load(PACKET_PATH, "aios_human_gate_execution_readiness_packet_missing_queue_validation")
    packet = packet_mod.build_human_gate_execution_readiness_packet(
        runtime_proof_gate=_runtime_gate_ready(),
        canonical_runtime_queue_view=_canonical_queue_view(),
        operator_dependency_ledger=_operator_dependency_ledger(),
        reduction_target_selector=_reduction_target_selector(),
        now="2026-01-02T03:04:05Z",
    )
    assert packet["packet_status"] == "BLOCKED"


def test_queue_validation_block_blocks_packet_and_surfaces_blockers():
    validation = dict(_queue_validation())
    validation["status"] = "BLOCK"
    validation["blocking_findings"] = ["RQV-003-NO-PROTECTED-ITEM"]
    packet = _load(PACKET_PATH, "aios_human_gate_execution_readiness_packet_blocked_queue_validation").build_human_gate_execution_readiness_packet(
        runtime_proof_gate=_runtime_gate_ready(),
        canonical_runtime_queue_view=_canonical_queue_view(),
        runtime_queue_validation=validation,
        operator_dependency_ledger=_operator_dependency_ledger(),
        reduction_target_selector=_reduction_target_selector(),
        now="2026-01-02T03:04:05Z",
    )
    assert packet["packet_status"] == "BLOCKED"
    assert packet["packet_blockers"]


def test_queue_validation_malformed_status_invalidates_packet():
    validation = dict(_queue_validation())
    validation["status"] = "WEIRD"
    packet = _load(PACKET_PATH, "aios_human_gate_execution_readiness_packet_malformed_queue_validation").build_human_gate_execution_readiness_packet(
        runtime_proof_gate=_runtime_gate_ready(),
        canonical_runtime_queue_view=_canonical_queue_view(),
        runtime_queue_validation=validation,
        operator_dependency_ledger=_operator_dependency_ledger(),
        reduction_target_selector=_reduction_target_selector(),
        now="2026-01-02T03:04:05Z",
    )
    assert packet["packet_status"] == "INVALID"


def test_canonical_queue_duplicate_ids_block_when_policy_blocks_duplicates():
    queue_view = _canonical_queue_view()
    queue_view = dict(queue_view)
    queue_view["id_collisions"] = [{"id": "relay_runtime_processor", "sources": ["relay_inbox", "worker_task_queue"]}]
    packet = _load(PACKET_PATH, "aios_human_gate_execution_readiness_packet_duplicate_ids").build_human_gate_execution_readiness_packet(
        runtime_proof_gate=_runtime_gate_ready(),
        canonical_runtime_queue_view=queue_view,
        runtime_queue_validation=_queue_validation(),
        operator_dependency_ledger=_operator_dependency_ledger(),
        reduction_target_selector=_reduction_target_selector(),
        now="2026-01-02T03:04:05Z",
    )
    assert packet["packet_status"] == "BLOCKED"


def test_canonical_queue_protected_items_block_when_present():
    queue_view = _canonical_queue_view()
    queue_view = dict(queue_view)
    queue_view["items"] = list(queue_view["items"])
    queue_view["items"][0] = dict(queue_view["items"][0])
    queue_view["items"][0]["protected_action"] = True
    queue_view["protected_item_count"] = 1
    validation = _queue_validation()
    validation = dict(validation)
    validation["status"] = "BLOCK"
    validation["findings"] = [
        {"check_id": "RQV-003-NO-PROTECTED-ITEM", "passed": False, "message": "No queue item carries a protected/forbidden execution flag.", "evidence": [{"id": "relay_runtime_processor", "kind": "packet"}]}
    ]
    packet = _load(PACKET_PATH, "aios_human_gate_execution_readiness_packet_protected_items").build_human_gate_execution_readiness_packet(
        runtime_proof_gate=_runtime_gate_ready(),
        canonical_runtime_queue_view=queue_view,
        runtime_queue_validation=validation,
        operator_dependency_ledger=_operator_dependency_ledger(),
        reduction_target_selector=_reduction_target_selector(),
        now="2026-01-02T03:04:05Z",
    )
    assert packet["packet_status"] == "BLOCKED"


def test_canonical_queue_unknown_states_block():
    queue_view = _canonical_queue_view()
    queue_view = dict(queue_view)
    queue_view["items"] = list(queue_view["items"])
    queue_view["items"][1] = dict(queue_view["items"][1])
    queue_view["items"][1]["state"] = "WEIRD"
    validation = _queue_validation()
    validation = dict(validation)
    validation["status"] = "BLOCK"
    validation["blocking_findings"] = ["RQV-002-CANONICAL-STATES"]
    packet = _load(PACKET_PATH, "aios_human_gate_execution_readiness_packet_unknown_state").build_human_gate_execution_readiness_packet(
        runtime_proof_gate=_runtime_gate_ready(),
        canonical_runtime_queue_view=queue_view,
        runtime_queue_validation=validation,
        operator_dependency_ledger=_operator_dependency_ledger(),
        reduction_target_selector=_reduction_target_selector(),
        now="2026-01-02T03:04:05Z",
    )
    assert packet["packet_status"] == "BLOCKED"


def test_operator_dependency_ledger_is_summarized_and_can_block_on_unsafe_flags():
    packet = _safe_packet()
    assert packet["operator_dependency_present"] is True
    assert packet["autonomy_shift"] == "PARTIAL"
    assert packet["remaining_human_burdens"]
    assert packet["reduced_burdens"]

    ledger = _operator_dependency_ledger()
    ledger["unsafe_autonomy_claim"] = True
    packet_mod = _load(PACKET_PATH, "aios_human_gate_execution_readiness_packet_unsafe_ledger")
    blocked = packet_mod.build_human_gate_execution_readiness_packet(
        runtime_proof_gate=_runtime_gate_ready(),
        canonical_runtime_queue_view=_canonical_queue_view(),
        runtime_queue_validation=_queue_validation(),
        operator_dependency_ledger=ledger,
        reduction_target_selector=_reduction_target_selector(),
        now="2026-01-02T03:04:05Z",
    )
    assert blocked["packet_status"] in {"BLOCKED", "INVALID"}


def test_reduction_selector_is_summarized_and_attention_or_blocks_on_planning_target():
    packet = _safe_packet()
    assert packet["reduction_selector_present"] is True
    assert packet["selected_target"] == "relay_proof_acceptance_packet"
    assert packet["safe_next_action_from_selector"]

    selector = _reduction_target_selector()
    selector["selected_target"] = "restart_timeouts_proof_planning"
    selector["selected_category"] = "recover"
    selector["selected_reason"] = "Keep planning the next proof instead of moving to human review."
    selector["safe_next_action"] = "Keep the next proof planning step human-reviewed."
    packet_mod = _load(PACKET_PATH, "aios_human_gate_execution_readiness_packet_planning_selector")
    attention = packet_mod.build_human_gate_execution_readiness_packet(
        runtime_proof_gate=_runtime_gate_ready(),
        canonical_runtime_queue_view=_canonical_queue_view(),
        runtime_queue_validation=_queue_validation(),
        operator_dependency_ledger=_operator_dependency_ledger(),
        reduction_target_selector=selector,
        now="2026-01-02T03:04:05Z",
    )
    assert attention["packet_status"] == "ATTENTION"


def test_validation_passes_for_safe_ready_packet_and_blocks_tampering():
    packet_mod = _load(PACKET_PATH, "aios_human_gate_execution_readiness_packet_validation")
    packet = packet_mod.build_human_gate_execution_readiness_packet(
        runtime_proof_gate=_runtime_gate_ready(),
        canonical_runtime_queue_view=_canonical_queue_view(),
        runtime_queue_validation=_queue_validation(),
        operator_dependency_ledger=_operator_dependency_ledger(),
        reduction_target_selector=_reduction_target_selector(),
        now="2026-01-02T03:04:05Z",
    )
    validation = packet_mod.validate_human_gate_execution_readiness_packet(packet)
    assert validation["status"] == "PASS"

    tampered = dict(packet)
    tampered["packet_status"] = "EXECUTE"
    validation = packet_mod.validate_human_gate_execution_readiness_packet(tampered)
    assert validation["status"] == "BLOCK"
    assert "packet_status_invalid" in validation["unsafe_flags"] or "packet_status_forbidden" in validation["unsafe_flags"]


def test_validation_blocks_if_ready_packet_has_blockers_or_unsafe_flags():
    packet_mod = _load(PACKET_PATH, "aios_human_gate_execution_readiness_packet_ready_blocker_validation")
    packet = packet_mod.build_human_gate_execution_readiness_packet(
        runtime_proof_gate=_runtime_gate_ready(),
        canonical_runtime_queue_view=_canonical_queue_view(),
        runtime_queue_validation=_queue_validation(),
        operator_dependency_ledger=_operator_dependency_ledger(),
        reduction_target_selector=_reduction_target_selector(),
        now="2026-01-02T03:04:05Z",
    )
    tampered = dict(packet)
    tampered["packet_blockers"] = ["x"]
    validation = packet_mod.validate_human_gate_execution_readiness_packet(tampered)
    assert validation["status"] == "BLOCK"

    tampered2 = dict(packet)
    tampered2["approval_granted"] = True
    validation = packet_mod.validate_human_gate_execution_readiness_packet(tampered2)
    assert validation["status"] == "BLOCK"


def test_packet_does_not_emit_command_strings_or_obvious_secret_assignments():
    packet = _safe_packet()
    serialized = json.dumps(packet, sort_keys=True).lower()
    for pattern in [
        "".join(["git", " ", "push"]),
        "".join(["git", " ", "commit"]),
        "".join(["git", " ", "merge"]),
        "".join(["gh", " ", "pr", " ", "merge"]),
        "".join(["gh", " ", "pr", " ", "create"]),
        "".join(["register", "-", "scheduledtask"]),
        "".join(["new", "-", "service"]),
        "".join(["start", "-", "job"]),
        "".join(["start", "-", "process"]),
        "".join(["start", "-", "service"]),
        "subprocess",
        "shell=true",
    ]:
        assert pattern not in serialized

    source = PACKET_PATH.read_text(encoding="utf-8").lower()
    for pattern in [
        "".join(["secret", "="]),
        "".join(["token", "="]),
        "".join(["pass", "word", "="]),
        "".join(["api", "_key", "="]),
        "".join(["api", "key", "="]),
        "".join(["bear", "er "]),
        "".join(["sk", "-"]),
    ]:
        assert pattern not in source


def test_packet_is_deterministic_and_summary_counts_are_present():
    packet_mod = _load(PACKET_PATH, "aios_human_gate_execution_readiness_packet_determinism")
    first = packet_mod.build_human_gate_execution_readiness_packet(
        runtime_proof_gate=_runtime_gate_ready(),
        canonical_runtime_queue_view=_canonical_queue_view(),
        runtime_queue_validation=_queue_validation(),
        operator_dependency_ledger=_operator_dependency_ledger(),
        reduction_target_selector=_reduction_target_selector(),
        now="2026-01-02T03:04:05Z",
    )
    second = packet_mod.build_human_gate_execution_readiness_packet(
        runtime_proof_gate=_runtime_gate_ready(),
        canonical_runtime_queue_view=_canonical_queue_view(),
        runtime_queue_validation=_queue_validation(),
        operator_dependency_ledger=_operator_dependency_ledger(),
        reduction_target_selector=_reduction_target_selector(),
        now="2026-01-02T03:04:05Z",
    )
    assert first == second
    summary = packet_mod.summarize_human_gate_execution_readiness_packet(first)
    assert summary["packet_status"] == "READY_FOR_HUMAN_REVIEW"
    assert summary["canonical_queue_item_count"] == 3
    assert summary["human_review_question_count"] >= 1
    assert summary["human_stop_condition_count"] >= 1


def test_existing_runtime_proof_gate_and_runtime_queue_and_validator_and_proof_chain_tests_still_pass():
    runtime_gate_mod = _load(PROOF_GATE_PATH, "aios_runtime_proof_gate_for_packet_regression")
    queue_validator_mod = _load(QUEUE_VALIDATOR_PATH, "aios_runtime_execution_queue_validator_for_packet_regression")
    queue_closure_mod = _load(QUEUE_CLOSURE_PATH, "aios_runtime_execution_queue_closure_for_packet_regression")
    relay_processor_mod = _load(RELAY_PROCESSOR_PATH, "aios_relay_runtime_processor_for_packet_regression")
    relay_review_mod = _load(RELAY_REVIEW_PATH, "aios_relay_dry_run_proof_review_for_packet_regression")
    restart_mod = _load(RESTART_PATH, "aios_restart_timeouts_dry_run_proof_for_packet_regression")
    retention_mod = _load(RETENTION_PATH, "aios_retention_rotation_dry_run_proof_for_packet_regression")
    soak_mod = _load(SOAK_PATH, "aios_soak_dry_run_proof_for_packet_regression")
    ledger_mod = _load(LEDGER_PATH, "aios_operator_dependency_ledger_for_packet_regression")
    selector_mod = _load(SELECTOR_PATH, "aios_reduction_target_selector_for_packet_regression")

    gate = _runtime_gate_ready()
    qv = _canonical_queue_view()
    qval = _queue_validation()
    queue = queue_closure_mod.build_runtime_execution_queue()
    relay = relay_processor_mod.build_relay_runtime_processor(queue=queue, now="2026-01-02T03:04:05Z")
    review = relay_review_mod.build_relay_dry_run_proof_review(relay_readout=relay, queue=queue, now="2026-01-02T03:04:05Z")
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
    soak = soak_mod.build_soak_dry_run_proof(
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
        restart_timeouts_proof=restart,
        retention_rotation_proof=retention,
        now="2026-01-01T01:00:00Z",
    )
    ledger = ledger_mod.build_operator_dependency_ledger(queue=queue, relay_readout=relay, relay_review=review, now="2026-01-02T03:04:05Z")
    selector = selector_mod.build_reduction_target_selector(ledger=ledger, now="2026-01-02T03:04:05Z")
    assert runtime_gate_mod.validate_runtime_proof_gate(gate)["status"] == "PASS"
    assert queue_validator_mod.validate_queue_view(qv)["status"] == "PASS"
    assert queue_validator_mod.validate_queue_view(qv)["approves_protected_action"] is False
    assert queue_closure_mod.validate_runtime_execution_queue(queue)["status"] == "PASS"
    assert relay_processor_mod.validate_relay_runtime_processor(relay)["status"] == "PASS"
    assert relay_review_mod.validate_relay_dry_run_proof_review(review)["status"] == "PASS"
    assert restart_mod.validate_restart_timeouts_dry_run_proof(restart)["status"] == "PASS"
    assert retention_mod.validate_retention_rotation_dry_run_proof(retention)["status"] == "PASS"
    assert soak_mod.validate_soak_dry_run_proof(soak)["status"] == "PASS"
    assert ledger_mod.validate_operator_dependency_ledger(ledger)["status"] == "PASS"
    assert selector_mod.validate_reduction_target_selector(selector)["status"] == "PASS"
