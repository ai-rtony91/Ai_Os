"""AI_OS human gate packet dogfood runner.

Observe-only dogfood/report lane. It builds the canonical queue view, validates
it, assembles the proof spine, builds the human gate execution readiness packet,
and writes a JSON + Markdown evidence bundle under Reports/human_gate/.

Nothing here grants approval or execution authority.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from automation.orchestration.autonomy_reports.aios_operator_dependency_ledger import (
    build_operator_dependency_ledger,
)
from automation.orchestration.autonomy_reports.aios_reduction_target_selector import (
    build_reduction_target_selector,
)
from automation.orchestration.runtime_closure.aios_human_gate_execution_readiness_packet import (
    build_human_gate_execution_readiness_packet,
    summarize_canonical_queue_section,
    summarize_human_gate_execution_readiness_packet,
    summarize_operator_dependency_section,
    summarize_queue_validation_section,
    summarize_reduction_selector_section,
    summarize_runtime_gate_section,
    validate_human_gate_execution_readiness_packet,
)
from automation.orchestration.runtime_closure.aios_relay_dry_run_proof_review import (
    build_relay_dry_run_proof_review,
)
from automation.orchestration.runtime_closure.aios_relay_runtime_processor import (
    build_relay_runtime_processor,
)
from automation.orchestration.runtime_closure.aios_restart_timeouts_dry_run_proof import (
    build_restart_timeouts_dry_run_proof,
)
from automation.orchestration.runtime_closure.aios_retention_rotation_dry_run_proof import (
    build_retention_rotation_dry_run_proof,
)
from automation.orchestration.runtime_closure.aios_runtime_execution_queue import (
    build_runtime_execution_queue,
)
from automation.orchestration.runtime_closure.aios_runtime_proof_gate import (
    build_runtime_proof_gate,
    summarize_runtime_proof_gate,
    validate_runtime_proof_gate,
)
from automation.orchestration.runtime_closure.aios_soak_dry_run_proof import (
    build_soak_dry_run_proof,
)
from automation.orchestration.runtime_queue.aios_runtime_execution_queue import (
    DEFAULT_SOURCES,
    build_queue_view,
)
from automation.validators.aios_runtime_execution_queue_validator import validate_queue_view


SCHEMA = "AIOS_HUMAN_GATE_PACKET_DOGFOOD_REPORT.v1"
DOGFOOD_TYPE = "human_gate_packet"
MODE = "DOGFOOD_REPORT"
REPORT_JSON_NAME = "human_gate_packet_dogfood_report.json"
REPORT_MD_NAME = "human_gate_packet_dogfood_summary.md"
DEFAULT_REPORT_SUBDIR = Path("Reports") / "human_gate"

FORBIDDEN_STATUSES = {
    "APPROVED",
    "EXECUTE",
    "EXECUTE_NOW",
    "COMPLETE",
    "AUTONOMOUS",
    "VACATION_READY",
    "VACATION_MODE_COMPLETE",
    "SCHEDULER_READY",
    "SOS_READY",
    "LIVE_READY",
    "LIVE_TRADING_READY",
}

UNSAFE_BOOL_KEYS = {
    "approval_granted",
    "execution_allowed",
    "dispatch_allowed",
    "apply_allowed",
    "runtime_launch_allowed",
    "runtime_launched",
    "runtime_mutation_allowed",
    "telemetry_mutation_allowed",
    "queue_mutation_allowed",
    "queue_mutated",
    "scheduler_creation_allowed",
    "service_creation_allowed",
    "sos_allowed",
    "live_trading_allowed",
    "credentials_accessed",
    "unsafe_autonomy_claim",
    "vacation_mode_complete",
    "restart_executed",
    "timeout_executed",
    "rotation_executed",
    "archive_executed",
    "delete_executed",
    "truncate_executed",
    "soak_executed",
}

DEFAULT_DOGFOOD_POLICY = {
    "require_runtime_proof_gate": True,
    "require_canonical_queue_view": True,
    "require_queue_validation": True,
    "require_human_gate_packet": True,
    "require_source_integrity": True,
    "allow_attention": True,
    "allow_missing_sources_attention": True,
    "allow_queue_attention": True,
    "allow_gate_attention": True,
    "allow_packet_attention": True,
    "allow_execution": False,
    "allow_dispatch": False,
    "allow_apply": False,
    "allow_runtime_launch": False,
    "allow_queue_mutation": False,
    "allow_scheduler": False,
    "allow_sos": False,
    "allow_live_trading": False,
    "allow_credentials_access": False,
    "allow_vacation_mode_complete": False,
    "allow_autonomy_claim": False,
}


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _deepcopy(value: Any) -> Any:
    return copy.deepcopy(value)


def _walk(value: Any, *, path: str = "") -> Iterable[tuple[str, Any, str]]:
    if isinstance(value, dict):
        for key, item in value.items():
            next_path = f"{path}.{key}" if path else str(key)
            yield next_path, item, str(key)
            yield from _walk(item, path=next_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            next_path = f"{path}[{index}]"
            yield next_path, item, ""
            yield from _walk(item, path=next_path)


def _normalize_token(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().upper().replace("-", "_").replace(" ", "_")


def _sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _fingerprint(path: Path) -> dict[str, Any]:
    exists = path.exists()
    stat = path.stat() if exists else None
    return {
        "path": str(path),
        "existed": exists,
        "size": stat.st_size if stat else None,
        "sha256": _sha256(path) if exists else None,
    }


def _resolve_path(repo_root: Path, raw_path: str | Path) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else repo_root / path


def _observed_source_paths(repo_root: Path, observed_source_paths: list[str | Path] | None = None) -> list[Path]:
    if observed_source_paths is not None:
        return [_resolve_path(repo_root, path) for path in observed_source_paths]

    module_paths = [
        "automation/orchestration/runtime_queue/aios_runtime_execution_queue.py",
        "automation/validators/aios_runtime_execution_queue_validator.py",
        "automation/orchestration/runtime_closure/aios_runtime_execution_queue.py",
        "automation/orchestration/runtime_closure/aios_relay_runtime_processor.py",
        "automation/orchestration/runtime_closure/aios_relay_dry_run_proof_review.py",
        "automation/orchestration/runtime_closure/aios_restart_timeouts_dry_run_proof.py",
        "automation/orchestration/runtime_closure/aios_retention_rotation_dry_run_proof.py",
        "automation/orchestration/runtime_closure/aios_soak_dry_run_proof.py",
        "automation/orchestration/runtime_closure/aios_runtime_proof_gate.py",
        "automation/orchestration/runtime_closure/aios_human_gate_execution_readiness_packet.py",
        "automation/orchestration/runtime_closure/aios_human_gate_packet_dogfood_runner.py",
        "automation/orchestration/autonomy_reports/aios_operator_dependency_ledger.py",
        "automation/orchestration/autonomy_reports/aios_reduction_target_selector.py",
    ]
    queue_paths = [spec["path"] for spec in DEFAULT_SOURCES if isinstance(spec, dict) and spec.get("path")]
    return [_resolve_path(repo_root, path) for path in [*queue_paths, *module_paths]]


def fingerprint_observed_sources(
    repo_root: Path,
    observed_source_paths: list[str | Path] | None = None,
) -> list[dict[str, Any]]:
    return [_fingerprint(path) for path in _observed_source_paths(repo_root, observed_source_paths)]


def compare_source_fingerprints(
    before: list[dict[str, Any]],
    after: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    before_by_path = {entry["path"]: entry for entry in before if isinstance(entry, dict)}
    after_by_path = {entry["path"]: entry for entry in after if isinstance(entry, dict)}
    merged: list[dict[str, Any]] = []
    for path in sorted(set(before_by_path) | set(after_by_path)):
        before_entry = before_by_path.get(path, {})
        after_entry = after_by_path.get(path, {})
        existed_before = bool(before_entry.get("existed"))
        existed_after = bool(after_entry.get("existed"))
        mutated = (
            existed_before != existed_after
            or before_entry.get("size") != after_entry.get("size")
            or before_entry.get("sha256") != after_entry.get("sha256")
        )
        merged.append(
            {
                "path": path,
                "existed_before": existed_before,
                "existed_after": existed_after,
                "size_before": before_entry.get("size"),
                "size_after": after_entry.get("size"),
                "sha256_before": before_entry.get("sha256"),
                "sha256_after": after_entry.get("sha256"),
                "mutated": mutated,
            }
        )
    return merged


def _collect_status_like_claims(obj: Any, *, input_name: str) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    for path, value, key in _walk(obj):
        if not isinstance(value, str):
            continue
        token = _normalize_token(value)
        if token not in FORBIDDEN_STATUSES:
            continue
        key_token = _normalize_token(key)
        path_token = _normalize_token(path)
        if any(
            fragment in key_token or fragment in path_token
            for fragment in ("STATUS", "VERDICT", "CLAIM", "STATE", "MODE", "RESULT", "DECISION", "FINAL", "TARGET")
        ):
            claims.append({"input": input_name, "path": path, "key": key, "value": value})
    return claims


def _collect_unsafe_flags(obj: Any, *, input_name: str) -> list[dict[str, Any]]:
    flags: list[dict[str, Any]] = []
    for path, value, key in _walk(obj):
        if key.lower() in UNSAFE_BOOL_KEYS and value is True:
            flags.append({"input": input_name, "path": path, "key": key, "value": value})
    return flags


def _safe_restart_inputs() -> dict[str, Any]:
    return {
        "runtime_label": "aios-runtime",
        "runtime_expected": True,
        "checkpoint_expected": True,
        "last_heartbeat_utc": "2026-01-01T00:04:30Z",
        "last_checkpoint_utc": "2026-01-01T00:01:00Z",
        "current_time_utc": "2026-01-01T00:05:00Z",
    }


def _safe_retention_files() -> list[dict[str, Any]]:
    return [
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
    ]


def _safe_soak_inputs() -> dict[str, Any]:
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
        "current_time_utc": "2026-01-01T01:00:00Z",
    }


def _fixture_or_build(fixtures: dict[str, Any], key: str, builder):
    value = fixtures.get(key)
    if isinstance(value, dict):
        return _deepcopy(value)
    return builder()


def _ensure_dict(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def build_human_gate_packet_dogfood_report(
    *,
    repo_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    now: str | None = None,
    packet_policy: dict[str, Any] | None = None,
    dogfood_policy: dict[str, Any] | None = None,
    dry_run_proof_fixtures: dict[str, Any] | None = None,
    observed_source_paths: list[str | Path] | None = None,
) -> dict[str, Any]:
    repo_root_path = Path(repo_root) if repo_root else Path.cwd()
    output_dir_path = Path(output_dir) if output_dir else repo_root_path / DEFAULT_REPORT_SUBDIR
    policy = {**DEFAULT_DOGFOOD_POLICY, **(dogfood_policy or {})}
    generated_at = _now(now)
    fixtures = _deepcopy(dry_run_proof_fixtures) if isinstance(dry_run_proof_fixtures, dict) else {}

    source_paths = _observed_source_paths(repo_root_path, observed_source_paths)
    pre_fingerprints = fingerprint_observed_sources(repo_root_path, observed_source_paths)

    canonical_queue_view = _fixture_or_build(
        fixtures,
        "canonical_runtime_queue_view",
        lambda: build_queue_view(repo_root_path, now=generated_at),
    )
    queue_validation = _fixture_or_build(
        fixtures,
        "runtime_queue_validation",
        lambda: validate_queue_view(canonical_queue_view),
    )
    runtime_queue_readout = _fixture_or_build(
        fixtures,
        "runtime_queue_readout",
        build_runtime_execution_queue,
    )
    relay_processor_readout = _fixture_or_build(
        fixtures,
        "relay_processor_readout",
        lambda: build_relay_runtime_processor(queue=runtime_queue_readout, now=generated_at),
    )
    relay_proof_review = _fixture_or_build(
        fixtures,
        "relay_proof_review",
        lambda: build_relay_dry_run_proof_review(relay_readout=relay_processor_readout, queue=runtime_queue_readout, now=generated_at),
    )
    restart_timeouts_proof = _fixture_or_build(
        fixtures,
        "restart_timeouts_proof",
        lambda: build_restart_timeouts_dry_run_proof(_safe_restart_inputs(), now=generated_at),
    )
    retention_rotation_proof = _fixture_or_build(
        fixtures,
        "retention_rotation_proof",
        lambda: build_retention_rotation_dry_run_proof(_safe_retention_files(), now=generated_at),
    )
    soak_proof = _fixture_or_build(
        fixtures,
        "soak_proof",
        lambda: build_soak_dry_run_proof(
            _safe_soak_inputs(),
            restart_timeouts_proof=restart_timeouts_proof,
            retention_rotation_proof=retention_rotation_proof,
            now=generated_at,
        ),
    )
    operator_dependency_ledger = _fixture_or_build(
        fixtures,
        "operator_dependency_ledger",
        lambda: build_operator_dependency_ledger(
            queue=runtime_queue_readout,
            relay_readout=relay_processor_readout,
            relay_review=relay_proof_review,
            now=generated_at,
        ),
    )
    reduction_target_selector = _fixture_or_build(
        fixtures,
        "reduction_target_selector",
        lambda: build_reduction_target_selector(ledger=operator_dependency_ledger, now=generated_at),
    )
    runtime_proof_gate = _fixture_or_build(
        fixtures,
        "runtime_proof_gate",
        lambda: build_runtime_proof_gate(
            runtime_queue_readout=runtime_queue_readout,
            relay_processor_readout=relay_processor_readout,
            relay_proof_review=relay_proof_review,
            restart_timeouts_proof=restart_timeouts_proof,
            retention_rotation_proof=retention_rotation_proof,
            soak_proof=soak_proof,
            operator_dependency_ledger=operator_dependency_ledger,
            reduction_target_selector=reduction_target_selector,
            now=generated_at,
        ),
    )
    human_gate_packet = _fixture_or_build(
        fixtures,
        "human_gate_packet",
        lambda: build_human_gate_execution_readiness_packet(
            runtime_proof_gate=runtime_proof_gate,
            canonical_runtime_queue_view=canonical_queue_view,
            runtime_queue_validation=queue_validation,
            operator_dependency_ledger=operator_dependency_ledger,
            reduction_target_selector=reduction_target_selector,
            runtime_queue_readout=runtime_queue_readout,
            relay_processor_readout=relay_processor_readout,
            relay_proof_review=relay_proof_review,
            restart_timeouts_proof=restart_timeouts_proof,
            retention_rotation_proof=retention_rotation_proof,
            soak_proof=soak_proof,
            packet_policy=packet_policy,
            now=generated_at,
            source_metadata={
                "repo_root": str(repo_root_path),
                "source_paths": [str(path) for path in source_paths],
            },
            proof_bundle={
                "runtime_proof_gate": runtime_proof_gate,
                "canonical_runtime_queue_view": canonical_queue_view,
                "runtime_queue_validation": queue_validation,
                "operator_dependency_ledger": operator_dependency_ledger,
                "reduction_target_selector": reduction_target_selector,
            },
        ),
    )

    runtime_gate_validation = validate_runtime_proof_gate(runtime_proof_gate)
    packet_validation = validate_human_gate_execution_readiness_packet(human_gate_packet)
    runtime_gate_summary = summarize_runtime_proof_gate(runtime_proof_gate)
    canonical_queue_summary = summarize_canonical_queue_section(canonical_queue_view)
    queue_validation_summary = summarize_queue_validation_section(queue_validation)
    operator_dependency_summary = summarize_operator_dependency_section(operator_dependency_ledger)
    reduction_selector_summary = summarize_reduction_selector_section(reduction_target_selector)
    packet_summary = summarize_human_gate_execution_readiness_packet(human_gate_packet)

    post_fingerprints = fingerprint_observed_sources(repo_root_path, observed_source_paths)
    source_fingerprints = compare_source_fingerprints(pre_fingerprints, post_fingerprints)
    mutated_sources = [entry["path"] for entry in source_fingerprints if entry.get("mutated")]
    missing_sources = [entry["path"] for entry in source_fingerprints if not entry.get("existed_before") and not entry.get("existed_after")]

    unsafe_flags_detected: list[dict[str, Any]] = []
    forbidden_claims_detected: list[dict[str, Any]] = []
    for input_name, obj in {
        "runtime_proof_gate": runtime_proof_gate,
        "canonical_runtime_queue_view": canonical_queue_view,
        "runtime_queue_validation": queue_validation,
        "runtime_queue_readout": runtime_queue_readout,
        "relay_processor_readout": relay_processor_readout,
        "relay_proof_review": relay_proof_review,
        "restart_timeouts_proof": restart_timeouts_proof,
        "retention_rotation_proof": retention_rotation_proof,
        "soak_proof": soak_proof,
        "operator_dependency_ledger": operator_dependency_ledger,
        "reduction_target_selector": reduction_target_selector,
        "human_gate_packet": human_gate_packet,
    }.items():
        if isinstance(obj, dict):
            unsafe_flags_detected.extend(_collect_unsafe_flags(obj, input_name=input_name))
            forbidden_claims_detected.extend(_collect_status_like_claims(obj, input_name=input_name))

    evidence_items = [
        {"component": "canonical_runtime_queue_view", "status": queue_validation.get("status")},
        {"component": "runtime_queue_validation", "status": queue_validation.get("status")},
        {"component": "runtime_proof_gate", "status": runtime_proof_gate.get("final_verdict")},
        {"component": "human_gate_packet", "status": human_gate_packet.get("packet_status")},
    ]

    evidence_missing = []
    if runtime_gate_validation.get("status") != "PASS":
        evidence_missing.append("runtime proof gate validation")
    if queue_validation.get("status") != "PASS":
        evidence_missing.append("queue validation")
    if packet_validation.get("status") != "PASS":
        evidence_missing.append("human gate packet validation")
    if missing_sources:
        evidence_missing.append("expected source files missing")

    evidence_attention = []
    if canonical_queue_summary.get("canonical_queue_fail_soft_errors"):
        evidence_attention.append("canonical queue has fail-soft source warnings")
    if runtime_gate_summary.get("attention_reasons"):
        evidence_attention.extend(runtime_gate_summary.get("attention_reasons") or [])
    if packet_summary.get("attention_count"):
        evidence_attention.extend(human_gate_packet.get("packet_attention_reasons") or [])
    if missing_sources:
        evidence_attention.append("expected source files are missing but no mutation occurred")

    evidence_blockers = []
    if queue_validation.get("status") == "BLOCK":
        evidence_blockers.append("queue validation is BLOCK")
    if runtime_gate_validation.get("status") == "BLOCK":
        evidence_blockers.append("runtime proof gate validation is BLOCK")
    if packet_validation.get("status") == "BLOCK":
        evidence_blockers.append("human gate packet validation is BLOCK")
    if mutated_sources:
        evidence_blockers.append("source mutation detected")

    mutation_check_status = "PASS"
    if mutated_sources:
        mutation_check_status = "BLOCK"
    elif missing_sources:
        mutation_check_status = "ATTENTION"

    dogfood_status = "PASS"
    if mutation_check_status == "BLOCK" or packet_validation.get("status") == "INVALID" or runtime_gate_validation.get("status") == "INVALID":
        dogfood_status = "INVALID"
    elif any(
        status == "BLOCK"
        for status in [queue_validation.get("status"), runtime_gate_validation.get("status"), packet_validation.get("status")]
    ):
        dogfood_status = "BLOCKED"
    elif mutation_check_status == "ATTENTION" or any(
        status == "ATTENTION"
        for status in [runtime_gate_validation.get("status"), packet_validation.get("status")]
    ) or evidence_attention:
        dogfood_status = "ATTENTION"

    approval_granted = False
    execution_allowed = False
    dispatch_allowed = False
    apply_allowed = False
    runtime_launch_allowed = False
    queue_mutation_allowed = False
    telemetry_mutation_allowed = False
    scheduler_creation_allowed = False
    service_creation_allowed = False
    sos_allowed = False
    live_trading_allowed = False
    credentials_accessed = False
    unsafe_autonomy_claim = False
    vacation_mode_complete = False

    report_paths = [
        str(output_dir_path / REPORT_JSON_NAME),
        str(output_dir_path / REPORT_MD_NAME),
    ]

    dogfood_status_reason = (
        "Dogfood evidence is safe and reviewable."
        if dogfood_status == "PASS"
        else "Dogfood evidence is reviewable but carries attention."
        if dogfood_status == "ATTENTION"
        else "Dogfood evidence is blocked by queue/proof/mutation conditions."
        if dogfood_status == "BLOCKED"
        else "Dogfood evidence is invalid and must be repaired."
    )

    report = {
        "schema": SCHEMA,
        "generated_at_utc": generated_at,
        "mode": MODE,
        "dogfood_type": DOGFOOD_TYPE,
        "dogfood_status": dogfood_status,
        "dogfood_status_reason": dogfood_status_reason,
        "repo_root": str(repo_root_path),
        "report_paths": report_paths,
        "prerequisites_confirmed": {
            "human_gate_packet": True,
            "runtime_proof_gate": True,
            "canonical_runtime_queue": True,
            "runtime_queue_validator": True,
            "operator_dependency_ledger": True,
            "reduction_target_selector": True,
            "runtime_queue": True,
            "relay_runtime_processor": True,
            "relay_dry_run_proof_review": True,
            "restart_timeouts_dry_run_proof": True,
            "retention_rotation_dry_run_proof": True,
            "soak_dry_run_proof": True,
        },
        "source_fingerprints": source_fingerprints,
        "mutated_sources": mutated_sources,
        "mutation_check_status": mutation_check_status,
        "canonical_queue_summary": canonical_queue_summary,
        "queue_validation_summary": {
            "queue_validation_status": queue_validation.get("status"),
            "queue_validation_blockers": list(queue_validation.get("blocking_findings") or []),
            "queue_validation_checked_fields": list(queue_validation.get("checked_fields") or []),
            "protected_item_count": queue_validation_summary.get("queue_validation_protected_item_count"),
            "duplicate_id_count": queue_validation_summary.get("queue_validation_duplicate_id_count"),
            "unknown_state_count": queue_validation_summary.get("queue_validation_unknown_state_count"),
            "collision_count": len(canonical_queue_summary.get("canonical_queue_collisions") or []),
        },
        "runtime_proof_gate_summary": runtime_gate_summary,
        "human_gate_packet_summary": packet_summary,
        "packet_validation_summary": packet_validation,
        "evidence_items": evidence_items,
        "evidence_missing": evidence_missing,
        "evidence_attention": list(dict.fromkeys(evidence_attention)),
        "evidence_blockers": list(dict.fromkeys(evidence_blockers)),
        "unsafe_flags_detected": unsafe_flags_detected,
        "forbidden_claims_detected": forbidden_claims_detected,
        "approval_granted": approval_granted,
        "execution_allowed": execution_allowed,
        "dispatch_allowed": dispatch_allowed,
        "apply_allowed": apply_allowed,
        "runtime_launch_allowed": runtime_launch_allowed,
        "queue_mutation_allowed": queue_mutation_allowed,
        "telemetry_mutation_allowed": telemetry_mutation_allowed,
        "scheduler_creation_allowed": scheduler_creation_allowed,
        "service_creation_allowed": service_creation_allowed,
        "sos_allowed": sos_allowed,
        "live_trading_allowed": live_trading_allowed,
        "credentials_accessed": credentials_accessed,
        "unsafe_autonomy_claim": unsafe_autonomy_claim,
        "vacation_mode_complete": vacation_mode_complete,
        "safe_next_action": "Anthony reviews the dogfood report and decides whether the human gate packet should be reviewed.",
        "stop_condition": "Stop after reviewing the dogfood evidence; do not approve or execute.",
        "runtime_queue_summary": _deepcopy(runtime_queue_readout),
        "relay_processor_summary": _deepcopy(relay_processor_readout),
        "relay_review_summary": _deepcopy(relay_proof_review),
        "restart_timeouts_summary": _deepcopy(restart_timeouts_proof),
        "retention_rotation_summary": _deepcopy(retention_rotation_proof),
        "soak_summary": _deepcopy(soak_proof),
        "operator_dependency_summary": operator_dependency_summary,
        "reduction_target_summary": reduction_selector_summary,
        "report_output_summary": {
            "output_dir": str(output_dir_path),
            "json_path": str(output_dir_path / REPORT_JSON_NAME),
            "md_path": str(output_dir_path / REPORT_MD_NAME),
        },
    }
    return report


def write_human_gate_packet_dogfood_reports(
    report: dict[str, Any],
    *,
    output_dir: str | Path,
) -> dict[str, str]:
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    json_path = output_dir_path / REPORT_JSON_NAME
    md_path = output_dir_path / REPORT_MD_NAME
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(build_dogfood_markdown_summary(report), encoding="utf-8")
    return {"json_path": str(json_path), "md_path": str(md_path)}


def build_dogfood_markdown_summary(report: dict[str, Any]) -> str:
    report = report if isinstance(report, dict) else {}
    lines = [
        "# AI_OS Human Gate Packet Dogfood Report",
        "",
        f"- generated_at_utc: `{report.get('generated_at_utc')}`",
        f"- dogfood_status: `{report.get('dogfood_status')}`",
        f"- packet_status: `{(report.get('human_gate_packet_summary') or {}).get('packet_status')}`",
        f"- runtime_proof_gate_verdict: `{(report.get('runtime_proof_gate_summary') or {}).get('runtime_proof_gate_verdict')}`",
        f"- queue_validation_status: `{(report.get('queue_validation_summary') or {}).get('queue_validation_status')}`",
        f"- canonical_queue_item_count: `{(report.get('canonical_queue_summary') or {}).get('canonical_queue_item_count')}`",
        f"- protected_item_count: `{(report.get('canonical_queue_summary') or {}).get('canonical_queue_protected_item_count')}`",
        f"- duplicate_id_count: `{(report.get('canonical_queue_summary') or {}).get('canonical_queue_duplicate_id_count')}`",
        f"- collision_count: `{len((report.get('canonical_queue_summary') or {}).get('canonical_queue_collisions') or [])}`",
        f"- unknown_state_count: `{(report.get('canonical_queue_summary') or {}).get('canonical_queue_unknown_state_count')}`",
        f"- mutation_check_status: `{report.get('mutation_check_status')}`",
        f"- mutated_source_count: `{len(report.get('mutated_sources') or [])}`",
        f"- blocker_count: `{len(report.get('evidence_blockers') or [])}`",
        f"- attention_count: `{len(report.get('evidence_attention') or [])}`",
        f"- unsafe_flag_count: `{len(report.get('unsafe_flags_detected') or [])}`",
        f"- forbidden_claim_count: `{len(report.get('forbidden_claims_detected') or [])}`",
        f"- human_review_questions_count: `{(report.get('human_gate_packet_summary') or {}).get('human_review_question_count')}`",
        f"- human_stop_conditions_count: `{(report.get('human_gate_packet_summary') or {}).get('human_stop_condition_count')}`",
        f"- safe_next_action: {report.get('safe_next_action')}",
        "",
        "## Evidence",
    ]
    for item in report.get("evidence_items") or []:
        if isinstance(item, dict):
            lines.append(f"- `{item.get('component')}`: `{item.get('status')}`")
    lines.extend(
        [
            "",
            "## Safety",
            "- This report does not approve execution.",
            "- No approval granted.",
            "- No runtime launch.",
            "- No queue mutation.",
            "- No scheduler or SOS activation.",
            "- No live trading or credentials access.",
        ]
    )
    return "\n".join(lines) + "\n"


def validate_human_gate_packet_dogfood_report(report: dict[str, Any]) -> dict[str, object]:
    blockers: list[str] = []
    unsafe_flags: list[str] = []
    forbidden_claims: list[dict[str, Any]] = []
    checked_fields: list[str] = []

    if not isinstance(report, dict):
        return {
            "status": "BLOCK",
            "blockers": ["report must be an object"],
            "checked_fields": [],
            "unsafe_flags": ["report_not_object"],
            "forbidden_claims": [],
            "dogfood_status": None,
        }

    required_fields = [
        "schema",
        "generated_at_utc",
        "mode",
        "dogfood_type",
        "dogfood_status",
        "dogfood_status_reason",
        "repo_root",
        "report_paths",
        "prerequisites_confirmed",
        "source_fingerprints",
        "mutated_sources",
        "mutation_check_status",
        "canonical_queue_summary",
        "queue_validation_summary",
        "runtime_proof_gate_summary",
        "human_gate_packet_summary",
        "packet_validation_summary",
        "evidence_items",
        "evidence_missing",
        "evidence_attention",
        "evidence_blockers",
        "unsafe_flags_detected",
        "forbidden_claims_detected",
        "approval_granted",
        "execution_allowed",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_launch_allowed",
        "queue_mutation_allowed",
        "telemetry_mutation_allowed",
        "scheduler_creation_allowed",
        "service_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
        "credentials_accessed",
        "unsafe_autonomy_claim",
        "vacation_mode_complete",
        "safe_next_action",
        "stop_condition",
    ]
    for field in required_fields:
        checked_fields.append(field)
        if field not in report:
            blockers.append(f"missing required field: {field}")

    dogfood_status = str(report.get("dogfood_status") or "")
    if dogfood_status not in {"PASS", "ATTENTION", "BLOCKED", "INVALID"}:
        blockers.append("dogfood_status must be PASS, ATTENTION, BLOCKED, or INVALID")
        unsafe_flags.append("dogfood_status_invalid")
    if dogfood_status in FORBIDDEN_STATUSES:
        blockers.append(f"dogfood_status must never be {dogfood_status}")
        unsafe_flags.append("dogfood_status_forbidden")

    if report.get("mode") != MODE:
        blockers.append("mode must be DOGFOOD_REPORT")
        unsafe_flags.append("mode_invalid")

    if report.get("approval_granted") is True:
        blockers.append("approval_granted must remain false")
        unsafe_flags.append("approval_granted_true")
    if report.get("execution_allowed") is True:
        blockers.append("execution_allowed must remain false")
        unsafe_flags.append("execution_allowed_true")
    if report.get("dispatch_allowed") is True:
        blockers.append("dispatch_allowed must remain false")
        unsafe_flags.append("dispatch_allowed_true")
    if report.get("apply_allowed") is True:
        blockers.append("apply_allowed must remain false")
        unsafe_flags.append("apply_allowed_true")
    if report.get("runtime_launch_allowed") is True:
        blockers.append("runtime_launch_allowed must remain false")
        unsafe_flags.append("runtime_launch_allowed_true")
    if report.get("queue_mutation_allowed") is True:
        blockers.append("queue_mutation_allowed must remain false")
        unsafe_flags.append("queue_mutation_allowed_true")
    if report.get("telemetry_mutation_allowed") is True:
        blockers.append("telemetry_mutation_allowed must remain false")
        unsafe_flags.append("telemetry_mutation_allowed_true")
    if report.get("scheduler_creation_allowed") is True:
        blockers.append("scheduler_creation_allowed must remain false")
        unsafe_flags.append("scheduler_creation_allowed_true")
    if report.get("service_creation_allowed") is True:
        blockers.append("service_creation_allowed must remain false")
        unsafe_flags.append("service_creation_allowed_true")
    if report.get("sos_allowed") is True:
        blockers.append("sos_allowed must remain false")
        unsafe_flags.append("sos_allowed_true")
    if report.get("live_trading_allowed") is True:
        blockers.append("live_trading_allowed must remain false")
        unsafe_flags.append("live_trading_allowed_true")
    if report.get("credentials_accessed") is True:
        blockers.append("credentials_accessed must remain false")
        unsafe_flags.append("credentials_accessed_true")
    if report.get("unsafe_autonomy_claim") is True:
        blockers.append("unsafe_autonomy_claim must remain false")
        unsafe_flags.append("unsafe_autonomy_claim_true")
    if report.get("vacation_mode_complete") is True:
        blockers.append("vacation_mode_complete must remain false")
        unsafe_flags.append("vacation_mode_complete_true")

    report_paths = report.get("report_paths")
    if not isinstance(report_paths, list) or not report_paths:
        blockers.append("report_paths must be non-empty after write")
        unsafe_flags.append("report_paths_missing")

    if not isinstance(report.get("safe_next_action"), str) or not report["safe_next_action"].strip():
        blockers.append("safe_next_action must be a non-empty string")
        unsafe_flags.append("safe_next_action_missing")
    if not isinstance(report.get("stop_condition"), str) or not report["stop_condition"].strip():
        blockers.append("stop_condition must be a non-empty string")
        unsafe_flags.append("stop_condition_missing")

    if not isinstance(report.get("mutated_sources"), list):
        blockers.append("mutated_sources must be a list")
        unsafe_flags.append("mutated_sources_invalid")
    elif report.get("mutated_sources"):
        blockers.append("mutated_sources must remain empty")
        unsafe_flags.append("mutated_sources_present")

    if dogfood_status == "PASS" and report.get("mutation_check_status") != "PASS":
        blockers.append("PASS dogfood requires mutation_check_status PASS")
        unsafe_flags.append("mutation_check_status_not_pass")

    for input_name, obj in report.items():
        forbidden_claims.extend(_collect_status_like_claims(obj, input_name="dogfood_report"))
        unsafe_flags.extend(flag["path"] for flag in _collect_unsafe_flags(obj, input_name="dogfood_report"))

    if forbidden_claims:
        blockers.append("forbidden claims detected in report output")

    if len(report_paths) == 0:
        blockers.append("report_paths must not be empty")

    status = "PASS" if not blockers else "BLOCK"
    return {
        "status": status,
        "blockers": list(dict.fromkeys(blockers)),
        "checked_fields": checked_fields,
        "unsafe_flags": list(dict.fromkeys(unsafe_flags)),
        "forbidden_claims": forbidden_claims,
        "dogfood_status": dogfood_status,
    }


def summarize_human_gate_packet_dogfood_report(report: dict[str, Any]) -> dict[str, object]:
    report = report if isinstance(report, dict) else {}
    canonical = report.get("canonical_queue_summary") if isinstance(report.get("canonical_queue_summary"), dict) else {}
    queue_validation = report.get("queue_validation_summary") if isinstance(report.get("queue_validation_summary"), dict) else {}
    runtime_gate = report.get("runtime_proof_gate_summary") if isinstance(report.get("runtime_proof_gate_summary"), dict) else {}
    packet = report.get("human_gate_packet_summary") if isinstance(report.get("human_gate_packet_summary"), dict) else {}
    packet_validation = report.get("packet_validation_summary") if isinstance(report.get("packet_validation_summary"), dict) else {}
    return {
        "dogfood_status": report.get("dogfood_status"),
        "packet_status": packet.get("packet_status"),
        "runtime_proof_gate_verdict": runtime_gate.get("runtime_proof_gate_verdict"),
        "queue_validation_status": queue_validation.get("queue_validation_status"),
        "canonical_queue_item_count": canonical.get("canonical_queue_item_count"),
        "protected_item_count": canonical.get("canonical_queue_protected_item_count"),
        "duplicate_id_count": canonical.get("canonical_queue_duplicate_id_count"),
        "collision_count": len(canonical.get("canonical_queue_collisions") or []),
        "unknown_state_count": canonical.get("canonical_queue_unknown_state_count"),
        "mutation_check_status": report.get("mutation_check_status"),
        "mutated_source_count": len(report.get("mutated_sources") or []),
        "blocker_count": len(report.get("evidence_blockers") or []),
        "attention_count": len(report.get("evidence_attention") or []),
        "unsafe_flag_count": len(report.get("unsafe_flags_detected") or []),
        "forbidden_claim_count": len(report.get("forbidden_claims_detected") or []),
        "approval_granted": report.get("approval_granted"),
        "execution_allowed": report.get("execution_allowed"),
        "dispatch_allowed": report.get("dispatch_allowed"),
        "runtime_launch_allowed": report.get("runtime_launch_allowed"),
        "queue_mutation_allowed": report.get("queue_mutation_allowed"),
        "scheduler_creation_allowed": report.get("scheduler_creation_allowed"),
        "sos_allowed": report.get("sos_allowed"),
        "live_trading_allowed": report.get("live_trading_allowed"),
        "vacation_mode_complete": report.get("vacation_mode_complete"),
        "report_paths": list(report.get("report_paths") or []),
        "safe_next_action": report.get("safe_next_action"),
        "stop_condition": report.get("stop_condition"),
        "packet_validation_status": packet_validation.get("status"),
    }


def run_human_gate_packet_dogfood(
    *,
    repo_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    now: str | None = None,
    packet_policy: dict[str, Any] | None = None,
    dogfood_policy: dict[str, Any] | None = None,
    dry_run_proof_fixtures: dict[str, Any] | None = None,
    observed_source_paths: list[str | Path] | None = None,
) -> dict[str, Any]:
    report = build_human_gate_packet_dogfood_report(
        repo_root=repo_root,
        output_dir=output_dir,
        now=now,
        packet_policy=packet_policy,
        dogfood_policy=dogfood_policy,
        dry_run_proof_fixtures=dry_run_proof_fixtures,
        observed_source_paths=observed_source_paths,
    )
    output_dir_path = Path(output_dir) if output_dir else Path(repo_root) if repo_root else Path.cwd()
    if output_dir is None:
        output_dir_path = Path(repo_root) if repo_root else Path.cwd()
        output_dir_path = output_dir_path / DEFAULT_REPORT_SUBDIR
    report["report_paths"] = [
        str(output_dir_path / REPORT_JSON_NAME),
        str(output_dir_path / REPORT_MD_NAME),
    ]
    validation = validate_human_gate_packet_dogfood_report(report)
    summary = summarize_human_gate_packet_dogfood_report(report)
    report["validation"] = validation
    report["summary"] = summary
    write_human_gate_packet_dogfood_reports(report, output_dir=output_dir_path)
    return report


def _cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dogfood the AI_OS human gate packet against current repo state.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir")
    parser.add_argument("--now")
    parser.add_argument("--packet-policy-json")
    parser.add_argument("--dogfood-policy-json")
    parser.add_argument("--dry-run-proof-fixtures-json")
    parser.add_argument("--observed-source-paths-json")
    return parser.parse_args()


def _load_json_arg(raw: str | None) -> dict[str, Any] | None:
    if raw is None:
        return None
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError("JSON input must decode to an object")
    return value


def _load_paths_arg(raw: str | None) -> list[str | Path] | None:
    if raw is None:
        return None
    value = json.loads(raw)
    if not isinstance(value, list):
        raise ValueError("Observed source paths JSON must decode to a list")
    return [Path(item) if isinstance(item, str) else item for item in value]


def main() -> int:
    args = _cli_args()
    report = run_human_gate_packet_dogfood(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        now=args.now,
        packet_policy=_load_json_arg(args.packet_policy_json),
        dogfood_policy=_load_json_arg(args.dogfood_policy_json),
        dry_run_proof_fixtures=_load_json_arg(args.dry_run_proof_fixtures_json),
        observed_source_paths=_load_paths_arg(args.observed_source_paths_json),
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    validation = report.get("validation") if isinstance(report.get("validation"), dict) else {"status": "BLOCK"}
    return 0 if validation.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
