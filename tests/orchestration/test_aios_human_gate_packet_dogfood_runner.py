"""Tests for the AI_OS human gate packet dogfood runner."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_human_gate_packet_dogfood_runner.py"
PACKET_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_human_gate_execution_readiness_packet.py"
PROOF_GATE_PATH = REPO_ROOT / "automation" / "orchestration" / "runtime_closure" / "aios_runtime_proof_gate.py"
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


def _safe_queue_view():
    return {
        "schema": "AIOS_RUNTIME_EXECUTION_QUEUE.v1",
        "generated_at": "2026-01-02T03:04:05Z",
        "observe_only": True,
        "item_count": 2,
        "items": [
            {"id": "queue-1", "state": "QUEUED", "protected_action": False, "source": "relay_inbox"},
            {"id": "queue-2", "state": "DEFERRED", "protected_action": False, "source": "relay_inbox"},
        ],
        "source_map": {"relay_inbox": 2},
        "sources_read": ["relay_inbox"],
        "sources_missing": [],
        "sources_malformed": [],
        "sources_index_only": [],
        "id_collisions": [],
        "state_counts": {"QUEUED": 1, "DEFERRED": 1},
        "protected_item_count": 0,
        "canonical_states": ["BLOCKED", "DEFERRED", "DONE", "ERROR", "QUEUED", "RUNNING"],
        "safe_next_action": "Read-only normalized view.",
    }


def _safe_dogfood_fixtures():
    runtime_queue_mod = _load(QUEUE_CLOSURE_PATH, "aios_runtime_execution_queue_closure_for_dogfood_tests")
    relay_processor_mod = _load(RELAY_PROCESSOR_PATH, "aios_relay_runtime_processor_for_dogfood_tests")
    relay_review_mod = _load(RELAY_REVIEW_PATH, "aios_relay_dry_run_proof_review_for_dogfood_tests")
    restart_mod = _load(RESTART_PATH, "aios_restart_timeouts_dry_run_proof_for_dogfood_tests")
    retention_mod = _load(RETENTION_PATH, "aios_retention_rotation_dry_run_proof_for_dogfood_tests")
    soak_mod = _load(SOAK_PATH, "aios_soak_dry_run_proof_for_dogfood_tests")
    ledger_mod = _load(LEDGER_PATH, "aios_operator_dependency_ledger_for_dogfood_tests")
    selector_mod = _load(SELECTOR_PATH, "aios_reduction_target_selector_for_dogfood_tests")
    gate_mod = _load(PROOF_GATE_PATH, "aios_runtime_proof_gate_for_dogfood_tests")
    packet_mod = _load(PACKET_PATH, "aios_human_gate_packet_for_dogfood_tests")
    queue_validator_mod = _load(QUEUE_VALIDATOR_PATH, "aios_runtime_execution_queue_validator_for_dogfood_tests")

    runtime_queue_readout = runtime_queue_mod.build_runtime_execution_queue()
    relay_processor_readout = relay_processor_mod.build_relay_runtime_processor(
        queue=runtime_queue_readout,
        now="2026-01-02T03:04:05Z",
    )
    relay_proof_review = relay_review_mod.build_relay_dry_run_proof_review(
        relay_readout=relay_processor_readout,
        queue=runtime_queue_readout,
        now="2026-01-02T03:04:05Z",
    )
    restart_timeouts_proof = restart_mod.build_restart_timeouts_dry_run_proof(
        {
            "runtime_label": "aios-runtime",
            "runtime_expected": True,
            "checkpoint_expected": True,
            "last_heartbeat_utc": "2026-01-01T00:04:30Z",
            "last_checkpoint_utc": "2026-01-01T00:01:00Z",
            "current_time_utc": "2026-01-01T00:05:00Z",
        },
        now="2026-01-01T00:05:00Z",
    )
    retention_rotation_proof = retention_mod.build_retention_rotation_dry_run_proof(
        [
            {
                "path": "Reports/runtime_queue/runtime_execution_queue_view.json",
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
    soak_proof = soak_mod.build_soak_dry_run_proof(
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
            "current_time_utc": "2026-01-01T01:00:00Z",
        },
        restart_timeouts_proof=restart_timeouts_proof,
        retention_rotation_proof=retention_rotation_proof,
        now="2026-01-01T01:00:00Z",
    )
    operator_dependency_ledger = ledger_mod.build_operator_dependency_ledger(
        queue=runtime_queue_readout,
        relay_readout=relay_processor_readout,
        relay_review=relay_proof_review,
        now="2026-01-02T03:04:05Z",
    )
    reduction_target_selector = selector_mod.build_reduction_target_selector(
        ledger=operator_dependency_ledger,
        now="2026-01-02T03:04:05Z",
    )
    runtime_proof_gate = gate_mod.build_runtime_proof_gate(
        runtime_queue_readout=runtime_queue_readout,
        relay_processor_readout=relay_processor_readout,
        relay_proof_review=relay_proof_review,
        restart_timeouts_proof=restart_timeouts_proof,
        retention_rotation_proof=retention_rotation_proof,
        soak_proof=soak_proof,
        operator_dependency_ledger=operator_dependency_ledger,
        reduction_target_selector=reduction_target_selector,
        now="2026-01-02T03:04:05Z",
    )
    queue_validation = queue_validator_mod.validate_queue_view(_safe_queue_view())
    human_gate_packet = packet_mod.build_human_gate_execution_readiness_packet(
        runtime_proof_gate=runtime_proof_gate,
        canonical_runtime_queue_view=_safe_queue_view(),
        runtime_queue_validation=queue_validation,
        operator_dependency_ledger=operator_dependency_ledger,
        reduction_target_selector=reduction_target_selector,
        runtime_queue_readout=runtime_queue_readout,
        relay_processor_readout=relay_processor_readout,
        relay_proof_review=relay_proof_review,
        restart_timeouts_proof=restart_timeouts_proof,
        retention_rotation_proof=retention_rotation_proof,
        soak_proof=soak_proof,
        now="2026-01-02T03:04:05Z",
        source_metadata={"fixture": True},
        proof_bundle={
            "runtime_proof_gate": runtime_proof_gate,
            "canonical_runtime_queue_view": _safe_queue_view(),
            "runtime_queue_validation": queue_validation,
            "operator_dependency_ledger": operator_dependency_ledger,
            "reduction_target_selector": reduction_target_selector,
        },
    )

    return {
        "canonical_runtime_queue_view": _safe_queue_view(),
        "runtime_queue_validation": queue_validation,
        "runtime_queue_readout": runtime_queue_readout,
        "relay_processor_readout": relay_processor_readout,
        "relay_proof_review": relay_proof_review,
        "restart_timeouts_proof": restart_timeouts_proof,
        "retention_rotation_proof": retention_rotation_proof,
        "soak_proof": soak_proof,
        "operator_dependency_ledger": operator_dependency_ledger,
        "reduction_target_selector": reduction_target_selector,
        "runtime_proof_gate": runtime_proof_gate,
        "human_gate_packet": human_gate_packet,
    }


def test_prerequisite_modules_exist():
    for path in [
        PACKET_PATH,
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
        RUNNER_PATH,
    ]:
        assert path.exists()


def test_dogfood_report_builds_and_writes_json_and_md_from_safe_fixtures(tmp_path):
    runner = _load(RUNNER_PATH, "aios_human_gate_packet_dogfood_runner_for_build_test")
    fixtures = _safe_dogfood_fixtures()
    observed = [tmp_path / "observed_source.txt"]
    observed[0].write_text("stable", encoding="utf-8")
    output_dir = tmp_path / "Reports" / "human_gate"
    report = runner.run_human_gate_packet_dogfood(
        repo_root=REPO_ROOT,
        output_dir=output_dir,
        now="2026-01-02T03:04:05Z",
        dry_run_proof_fixtures=fixtures,
        observed_source_paths=observed,
    )

    assert report["mode"] == "DOGFOOD_REPORT"
    assert report["dogfood_type"] == "human_gate_packet"
    assert report["report_paths"]
    assert report["report_paths"][0].endswith("human_gate_packet_dogfood_report.json")
    assert report["report_paths"][1].endswith("human_gate_packet_dogfood_summary.md")
    assert Path(report["report_paths"][0]).exists()
    assert Path(report["report_paths"][1]).exists()
    assert report["approval_granted"] is False
    assert report["execution_allowed"] is False
    assert report["dispatch_allowed"] is False
    assert report["apply_allowed"] is False
    assert report["runtime_launch_allowed"] is False
    assert report["queue_mutation_allowed"] is False
    assert report["telemetry_mutation_allowed"] is False
    assert report["scheduler_creation_allowed"] is False
    assert report["service_creation_allowed"] is False
    assert report["sos_allowed"] is False
    assert report["live_trading_allowed"] is False
    assert report["credentials_accessed"] is False
    assert report["unsafe_autonomy_claim"] is False
    assert report["vacation_mode_complete"] is False
    assert report["source_fingerprints"]
    assert report["mutated_sources"] == []
    assert report["mutation_check_status"] == "PASS"
    assert report["packet_validation_summary"]["status"] == "PASS"
    assert report["validation"]["status"] == "PASS"


def test_fingerprint_helpers_detect_mutation(tmp_path):
    runner = _load(RUNNER_PATH, "aios_human_gate_packet_dogfood_runner_for_fingerprint_test")
    observed = tmp_path / "observed_source.txt"
    observed.write_text("stable", encoding="utf-8")
    before = runner.fingerprint_observed_sources(tmp_path, [observed])
    after = runner.fingerprint_observed_sources(tmp_path, [observed])
    merged = runner.compare_source_fingerprints(before, after)
    assert merged[0]["mutated"] is False

    observed.write_text("mutated", encoding="utf-8")
    after_mutated = runner.fingerprint_observed_sources(tmp_path, [observed])
    merged_mutated = runner.compare_source_fingerprints(before, after_mutated)
    assert merged_mutated[0]["mutated"] is True


def test_dogfood_validation_blocks_when_mutated_sources_or_forbidden_status_are_tampered(tmp_path):
    runner = _load(RUNNER_PATH, "aios_human_gate_packet_dogfood_runner_for_validation_test")
    fixtures = _safe_dogfood_fixtures()
    observed = [tmp_path / "observed_source.txt"]
    observed[0].write_text("stable", encoding="utf-8")
    report = runner.run_human_gate_packet_dogfood(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "human_gate",
        now="2026-01-02T03:04:05Z",
        dry_run_proof_fixtures=fixtures,
        observed_source_paths=observed,
    )

    validation = runner.validate_human_gate_packet_dogfood_report(report)
    assert validation["status"] == "PASS"

    tampered = dict(report)
    tampered["mutated_sources"] = ["automation/orchestration/runtime_closure/aios_human_gate_packet_dogfood_runner.py"]
    validation = runner.validate_human_gate_packet_dogfood_report(tampered)
    assert validation["status"] == "BLOCK"

    tampered = dict(report)
    tampered["dogfood_status"] = "EXECUTE"
    validation = runner.validate_human_gate_packet_dogfood_report(tampered)
    assert validation["status"] == "BLOCK"


def test_markdown_summary_contains_safety_statement_and_key_fields(tmp_path):
    runner = _load(RUNNER_PATH, "aios_human_gate_packet_dogfood_runner_for_markdown_test")
    fixtures = _safe_dogfood_fixtures()
    report = runner.run_human_gate_packet_dogfood(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "human_gate",
        now="2026-01-02T03:04:05Z",
        dry_run_proof_fixtures=fixtures,
        observed_source_paths=[tmp_path / "observed_source.txt"],
    )
    markdown = runner.build_dogfood_markdown_summary(report)
    assert "This report does not approve execution." in markdown
    assert "dogfood_status" in markdown
    assert "packet_status" in markdown
    assert "runtime_proof_gate_verdict" in markdown
    assert "queue_validation_status" in markdown
    assert "mutation_check_status" in markdown
    assert "safe_next_action" in markdown
    assert "git " not in markdown.lower()


def test_dogfood_report_is_deterministic_with_same_inputs(tmp_path):
    runner = _load(RUNNER_PATH, "aios_human_gate_packet_dogfood_runner_for_determinism_test")
    fixtures = _safe_dogfood_fixtures()
    observed = [tmp_path / "observed_source.txt"]
    observed[0].write_text("stable", encoding="utf-8")
    output_dir = tmp_path / "Reports" / "human_gate"
    first = runner.run_human_gate_packet_dogfood(
        repo_root=REPO_ROOT,
        output_dir=output_dir,
        now="2026-01-02T03:04:05Z",
        dry_run_proof_fixtures=fixtures,
        observed_source_paths=observed,
    )
    second = runner.run_human_gate_packet_dogfood(
        repo_root=REPO_ROOT,
        output_dir=output_dir,
        now="2026-01-02T03:04:05Z",
        dry_run_proof_fixtures=fixtures,
        observed_source_paths=observed,
    )
    assert first == second
    assert first["summary"]["dogfood_status"] in {"PASS", "ATTENTION"}


def test_json_report_contains_final_validation_and_summary_payload(tmp_path):
    runner = _load(RUNNER_PATH, "aios_human_gate_packet_dogfood_runner_for_json_test")
    fixtures = _safe_dogfood_fixtures()
    report = runner.run_human_gate_packet_dogfood(
        repo_root=REPO_ROOT,
        output_dir=tmp_path / "Reports" / "human_gate",
        now="2026-01-02T03:04:05Z",
        dry_run_proof_fixtures=fixtures,
        observed_source_paths=[tmp_path / "observed_source.txt"],
    )
    report_path = Path(report["report_paths"][0])
    loaded = json.loads(report_path.read_text(encoding="utf-8"))
    assert loaded["validation"]["status"] == "PASS"
    assert loaded["summary"]["dogfood_status"] == report["summary"]["dogfood_status"]
    assert loaded["report_paths"] == report["report_paths"]
    assert loaded["safe_next_action"].startswith("Anthony reviews the dogfood report")
