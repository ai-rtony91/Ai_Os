from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE = REPO_ROOT / "automation" / "orchestration" / "aios_executive_control_readiness.py"
SCHEMA = REPO_ROOT / "schemas" / "orchestration" / "aios_executive_control_readiness.schema.json"
FIXED_NOW = "2026-06-14T12:00:00Z"


def _load():
    spec = importlib.util.spec_from_file_location("aios_executive_control_readiness", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(root: Path, rel_path: str | Path, payload: dict) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _governor(blocked: bool = False) -> dict:
    return {
        "schema_version": "1.0",
        "system": "AI_OS",
        "component": "autonomy_decision_governor",
        "mode": "APPLY_SAFE_DECISION_OUTPUT",
        "generated_at_utc": FIXED_NOW,
        "blocked": blocked,
        "blocked_reason": "dirty_working_tree" if blocked else None,
        "allowed_lane": "DRY_RUN",
        "safety_boundaries": {
            "live_trading": "blocked",
            "broker_execution": "blocked",
            "credential_use": "blocked",
            "unapproved_mutation": "blocked",
        },
    }


def _closed_loop(status: str = "ready_for_dry_run") -> dict:
    return {
        "schema_version": "1.0",
        "system": "AI_OS",
        "component": "closed_autonomy_loop",
        "mode": "ONE_CYCLE_RECOMMENDATION_ONLY",
        "generated_at_utc": FIXED_NOW,
        "loop_phase_status": {"stop": "complete"},
        "gate_result": {"status": status, "reason": "fixture", "safe_to_dispatch": False},
        "dispatch_recommendation": {
            "dispatch_authorized": False,
            "queue_mutation_authorized": False,
        },
        "safety_boundaries": {
            "continuous_loop": "blocked",
            "worker_dispatch": "recommendation_only",
            "queue_mutation": "blocked",
            "live_trading": "blocked",
            "broker_execution": "blocked",
            "credential_use": "blocked",
            "unapproved_mutation": "blocked",
        },
    }


def _packet_drafter(blocked: bool = False) -> dict:
    return {
        "schema_version": "1.0",
        "system": "AI_OS",
        "component": "closed_loop_packet_drafter",
        "mode": "APPLY_BUILD_WITH_PREVIEW_OUTPUT",
        "generated_at_utc": FIXED_NOW,
        "validation": {
            "agents_required_fields_present": True,
            "missing_fields": [],
            "blocked": blocked,
            "blocked_reason": "fixture_blocked" if blocked else None,
        },
        "dispatch": {
            "dispatch_authorized": False,
            "queue_mutation_authorized": False,
            "human_approval_required": True,
        },
        "safety_boundaries": {
            "worker_dispatch": "blocked",
            "queue_mutation": "blocked",
            "continuous_loop": "blocked",
            "live_trading": "blocked",
            "broker_execution": "blocked",
            "credential_use": "blocked",
            "unapproved_mutation": "blocked",
        },
    }


def _queue_preview(blocked: bool = False) -> dict:
    return {
        "schema_version": "1.0",
        "system": "AI_OS",
        "component": "closed_loop_queue_injection_preview",
        "mode": "APPLY_BUILD_WITH_QUEUE_PREVIEW_OUTPUT",
        "generated_at_utc": FIXED_NOW,
        "proposed_queue_item": {
            "status": "blocked" if blocked else "requires_approval",
            "blocked_reason": "fixture_blocked" if blocked else None,
            "dispatch_authorized": False,
            "queue_mutation_authorized": False,
        },
        "validation": {
            "required_fields_present": True,
            "missing_fields": [],
            "blocked": blocked,
            "blocked_reason": "fixture_blocked" if blocked else None,
        },
        "safety_boundaries": {
            "real_queue_mutation": "blocked",
            "worker_dispatch": "blocked",
            "continuous_loop": "blocked",
            "live_trading": "blocked",
            "broker_execution": "blocked",
            "credential_use": "blocked",
            "unapproved_mutation": "blocked",
        },
    }


def _queue_dispatch_gates(blocked: bool = False) -> dict:
    gate_status = "blocked" if blocked else "requires_approval"
    return {
        "schema_version": "1.0",
        "system": "AI_OS",
        "component": "queue_to_dispatch_gates",
        "mode": "APPLY_BUILD_WITH_CONSOLIDATED_GATE_PREVIEW_OUTPUT",
        "generated_at_utc": FIXED_NOW,
        "overall_status": "blocked" if blocked else "requires_approval",
        "gates": {
            name: {
                "status": gate_status,
                "reason": "fixture",
                "dispatch_authorized": False,
                "queue_mutation_authorized": False,
                "human_approval_required": True,
            }
            for name in (
                "queue_admission_preview",
                "worker_dispatch_preview",
                "human_approval_preview",
                "real_queue_injection_gate_preview",
            )
        },
        "validation": {
            "required_fields_present": True,
            "missing_fields": [],
            "blocked": blocked,
            "blocked_reason": "fixture_blocked" if blocked else None,
        },
        "safety_boundaries": {
            "real_queue_mutation": "blocked",
            "worker_dispatch": "blocked",
            "continuous_loop": "blocked",
            "live_trading": "blocked",
            "broker_execution": "blocked",
            "credential_use": "blocked",
            "webhook_execution": "blocked",
            "scheduler_creation": "blocked",
            "unapproved_mutation": "blocked",
        },
    }


def _seed_valid(root: Path) -> None:
    _write_json(root, "Reports/autonomy_decision_governor/AIOS_AUTONOMY_DECISION_GOVERNOR_LATEST.json", _governor())
    _write_json(root, "Reports/sandbox/closed_autonomy_loop/AIOS_CLOSED_AUTONOMY_LOOP_LATEST.json", _closed_loop())
    _write_json(
        root,
        "Reports/sandbox/closed_loop_packet_drafter/AIOS_CLOSED_LOOP_PACKET_DRAFTER_PREVIEW.json",
        _packet_drafter(),
    )
    _write_json(
        root,
        "Reports/sandbox/closed_loop_queue_injection_preview/AIOS_CLOSED_LOOP_QUEUE_INJECTION_PREVIEW.json",
        _queue_preview(),
    )
    _write_json(
        root,
        "Reports/sandbox/queue_to_dispatch_gates/AIOS_QUEUE_TO_DISPATCH_GATES_PREVIEW.json",
        _queue_dispatch_gates(),
    )


def _assert_schema_valid(report: dict) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert set(schema["required"]).issubset(report.keys())
    assert report["schema_version"] == "1.0"
    assert report["system"] == "AI_OS"
    assert report["component"] == "executive_control_readiness"
    assert report["readiness_status"] in schema["properties"]["readiness_status"]["enum"]


def test_missing_evidence_blocks(tmp_path: Path) -> None:
    m = _load()

    report = m.build_executive_control_readiness_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["readiness_status"] == "blocked"
    assert report["governor_ready"] is False
    assert report["closed_loop_ready"] is False
    assert report["blockers"]


def test_blocked_upstream_blocks(tmp_path: Path) -> None:
    m = _load()
    _seed_valid(tmp_path)
    _write_json(
        tmp_path,
        "Reports/sandbox/queue_to_dispatch_gates/AIOS_QUEUE_TO_DISPATCH_GATES_PREVIEW.json",
        _queue_dispatch_gates(blocked=True),
    )

    report = m.build_executive_control_readiness_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["readiness_status"] == "blocked"
    assert report["queue_dispatch_gates_ready"] is False
    assert any("queue_dispatch_gates" in blocker for blocker in report["blockers"])


def test_valid_upstream_reports_produce_ready_for_control_plane_design(tmp_path: Path) -> None:
    m = _load()
    _seed_valid(tmp_path)

    report = m.build_executive_control_readiness_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["readiness_status"] == "ready_for_control_plane_design"
    assert report["governor_ready"] is True
    assert report["closed_loop_ready"] is True
    assert report["packet_drafter_ready"] is True
    assert report["queue_preview_ready"] is True
    assert report["queue_dispatch_gates_ready"] is True
    assert report["blockers"] == []


def test_safety_locks_must_remain_false_and_blocked(tmp_path: Path) -> None:
    m = _load()
    _seed_valid(tmp_path)
    unsafe = _packet_drafter()
    unsafe["dispatch"]["dispatch_authorized"] = True
    _write_json(
        tmp_path,
        "Reports/sandbox/closed_loop_packet_drafter/AIOS_CLOSED_LOOP_PACKET_DRAFTER_PREVIEW.json",
        unsafe,
    )

    report = m.build_executive_control_readiness_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["readiness_status"] == "blocked"
    assert report["packet_drafter_ready"] is False
    assert any("dispatch_authorized" in blocker for blocker in report["blockers"])
    assert report["safety_boundaries"]["real_queue_mutation"] == "blocked"
    assert report["safety_boundaries"]["worker_dispatch"] == "blocked"
    assert report["safety_boundaries"]["continuous_loop"] == "blocked"


def test_schema_validates(tmp_path: Path) -> None:
    m = _load()
    _seed_valid(tmp_path)

    report = m.build_executive_control_readiness_report(tmp_path, generated_at_utc=FIXED_NOW)

    _assert_schema_valid(report)


def test_output_is_deterministic_except_timestamp(tmp_path: Path) -> None:
    m = _load()
    _seed_valid(tmp_path)

    first = m.build_executive_control_readiness_report(tmp_path, generated_at_utc="2026-06-14T12:00:00Z")
    second = m.build_executive_control_readiness_report(tmp_path, generated_at_utc="2026-06-14T12:01:00Z")
    first.pop("generated_at_utc")
    second.pop("generated_at_utc")

    assert first == second
