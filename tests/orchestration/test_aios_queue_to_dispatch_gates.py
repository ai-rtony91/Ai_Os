from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE = REPO_ROOT / "automation" / "orchestration" / "aios_queue_to_dispatch_gates.py"
SCHEMA = REPO_ROOT / "schemas" / "orchestration" / "aios_queue_to_dispatch_gates.schema.json"
FIXED_NOW = "2026-06-14T12:00:00Z"
INPUT_PATH = (
    Path("Reports")
    / "sandbox"
    / "closed_loop_queue_injection_preview"
    / "AIOS_CLOSED_LOOP_QUEUE_INJECTION_PREVIEW.json"
)
OUTPUT_PATH = Path("Reports") / "sandbox" / "queue_to_dispatch_gates" / "AIOS_QUEUE_TO_DISPATCH_GATES_PREVIEW.json"


def _load():
    spec = importlib.util.spec_from_file_location("aios_queue_to_dispatch_gates", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _queue_preview(
    *,
    item_status: str = "preview_only",
    mode: str = "DRY_RUN",
    approval_required: bool = False,
    queue_mutation_authorized: bool = False,
    dispatch_authorized: bool = False,
    allowed_paths: list[str] | None = None,
) -> dict:
    return {
        "schema_version": "1.0",
        "system": "AI_OS",
        "component": "closed_loop_queue_injection_preview",
        "mode": "APPLY_BUILD_WITH_QUEUE_PREVIEW_OUTPUT",
        "generated_at_utc": FIXED_NOW,
        "input_status": {
            "packet_drafter_preview": "present",
            "packet_blueprint": "present",
        },
        "proposed_queue_item": {
            "queue_item_id": "AIOS-QUEUE-PREVIEW-FIXTURE",
            "source_component": "closed_loop_packet_drafter",
            "source_preview_path": "Reports/sandbox/closed_loop_packet_drafter/AIOS_CLOSED_LOOP_PACKET_DRAFTER_PREVIEW.json",
            "packet_id": "AIOS-FIXTURE-PACKET",
            "mode": mode,
            "lane": "APPLY_CODE_SAFE" if mode == "APPLY" else "DRY_RUN",
            "risk_level": "medium",
            "approval_required": approval_required,
            "approval_authority": "Anthony Meza",
            "validators_required": ["fixture validator", "git diff --check"],
            "allowed_paths": allowed_paths or ["Reports/sandbox/example/"],
            "forbidden_paths": ["automation/orchestration/work_packets/", "broker/", "live_trading/", ".env"],
            "stop_conditions": ["Stop before queue mutation, worker dispatch, commit, push, or merge."],
            "dispatch_authorized": dispatch_authorized,
            "queue_mutation_authorized": queue_mutation_authorized,
            "status": item_status,
            "blocked_reason": "fixture_blocked" if item_status == "blocked" else None,
        },
        "validation": {
            "required_fields_present": item_status != "blocked",
            "missing_fields": [],
            "blocked": item_status == "blocked",
            "blocked_reason": "fixture_blocked" if item_status == "blocked" else None,
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
        "next_step": "fixture",
    }


def _write_preview(root: Path, preview: dict) -> None:
    path = root / INPUT_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(preview, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _required_fields() -> set[str]:
    return {
        "schema_version",
        "system",
        "component",
        "mode",
        "generated_at_utc",
        "input_status",
        "overall_status",
        "validated_queue_item",
        "gates",
        "validation",
        "safety_boundaries",
        "next_step",
    }


def _assert_schema_valid(report: dict) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert set(schema["required"]) == _required_fields()
    assert _required_fields().issubset(report)
    assert report["schema_version"] == "1.0"
    assert report["system"] == "AI_OS"
    assert report["component"] == "queue_to_dispatch_gates"
    assert report["mode"] == "APPLY_BUILD_WITH_CONSOLIDATED_GATE_PREVIEW_OUTPUT"
    for gate in report["gates"].values():
        assert gate["queue_mutation_authorized"] is False
        assert gate["dispatch_authorized"] is False


def test_missing_input_blocks(tmp_path: Path) -> None:
    m = _load()

    report = m.build_queue_to_dispatch_gates_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["overall_status"] == "blocked"
    assert report["input_status"]["queue_injection_preview"] == "missing"
    assert report["validation"]["blocked"] is True


def test_valid_preview_passes_preview_only(tmp_path: Path) -> None:
    m = _load()
    _write_preview(tmp_path, _queue_preview())

    report = m.build_queue_to_dispatch_gates_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["overall_status"] == "preview_only"
    assert report["gates"]["queue_admission_preview"]["status"] == "preview_only"
    assert report["gates"]["worker_dispatch_preview"]["dispatch_authorized"] is False
    assert (tmp_path / OUTPUT_PATH).exists()


def test_queue_mutation_blocks(tmp_path: Path) -> None:
    m = _load()
    _write_preview(tmp_path, _queue_preview(queue_mutation_authorized=True))

    report = m.build_queue_to_dispatch_gates_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["overall_status"] == "blocked"
    assert "queue_mutation_authorized_false" in report["validation"]["missing_fields"]


def test_dispatch_blocks(tmp_path: Path) -> None:
    m = _load()
    _write_preview(tmp_path, _queue_preview(dispatch_authorized=True))

    report = m.build_queue_to_dispatch_gates_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["overall_status"] == "blocked"
    assert "dispatch_authorized_false" in report["validation"]["missing_fields"]


def test_apply_requires_approval(tmp_path: Path) -> None:
    m = _load()
    _write_preview(tmp_path, _queue_preview(mode="APPLY", approval_required=True))

    report = m.build_queue_to_dispatch_gates_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["overall_status"] == "requires_approval"
    assert report["gates"]["human_approval_preview"]["status"] == "requires_approval"
    assert report["gates"]["human_approval_preview"]["human_approval_required"] is True


def test_apply_without_approval_blocks(tmp_path: Path) -> None:
    m = _load()
    _write_preview(tmp_path, _queue_preview(mode="APPLY", approval_required=False))

    report = m.build_queue_to_dispatch_gates_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["overall_status"] == "blocked"
    assert "apply_requires_anthony_approval" in report["validation"]["missing_fields"]


def test_unsafe_trading_scope_blocks(tmp_path: Path) -> None:
    m = _load()
    _write_preview(
        tmp_path,
        _queue_preview(allowed_paths=["apps/trading_lab/live_trading/broker_credentials.py"]),
    )

    report = m.build_queue_to_dispatch_gates_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["overall_status"] == "blocked"
    assert "unsafe_scope_blocked" in report["validation"]["missing_fields"]
    assert report["safety_boundaries"]["live_trading"] == "blocked"
    assert report["safety_boundaries"]["broker_execution"] == "blocked"
    assert report["safety_boundaries"]["credential_use"] == "blocked"


def test_schema_validates(tmp_path: Path) -> None:
    m = _load()
    _write_preview(tmp_path, _queue_preview())

    report = m.build_queue_to_dispatch_gates_report(tmp_path, generated_at_utc=FIXED_NOW)

    _assert_schema_valid(report)


def test_deterministic_output_except_timestamp(tmp_path: Path) -> None:
    m = _load()
    _write_preview(tmp_path, _queue_preview())

    first = m.build_queue_to_dispatch_gates_report(tmp_path, generated_at_utc="2026-06-14T12:00:00Z")
    second = m.build_queue_to_dispatch_gates_report(tmp_path, generated_at_utc="2026-06-14T12:01:00Z")
    first.pop("generated_at_utc")
    second.pop("generated_at_utc")

    assert first == second
