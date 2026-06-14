from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE = REPO_ROOT / "automation" / "orchestration" / "aios_closed_loop_queue_injection_preview.py"
SCHEMA = REPO_ROOT / "schemas" / "orchestration" / "aios_closed_loop_queue_injection_preview.schema.json"
FIXED_NOW = "2026-06-14T12:00:00Z"
DRAFTER_PATH = (
    Path("Reports")
    / "sandbox"
    / "closed_loop_packet_drafter"
    / "AIOS_CLOSED_LOOP_PACKET_DRAFTER_PREVIEW.json"
)
OUTPUT_PATH = (
    Path("Reports")
    / "sandbox"
    / "closed_loop_queue_injection_preview"
    / "AIOS_CLOSED_LOOP_QUEUE_INJECTION_PREVIEW.json"
)


def _load():
    spec = importlib.util.spec_from_file_location("aios_closed_loop_queue_injection_preview", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _drafter_report(
    *,
    blocked: bool = False,
    human_approval_required: bool = False,
    allowed_paths: list[str] | None = None,
    title: str = "AIOS-RUNTIME-QUEUE-BACKLOG-CONSOLIDATION-DRY-RUN",
) -> dict:
    return {
        "schema_version": "1.0",
        "system": "AI_OS",
        "component": "closed_loop_packet_drafter",
        "mode": "APPLY_BUILD_WITH_PREVIEW_OUTPUT",
        "generated_at_utc": FIXED_NOW,
        "input_status": {
            "closed_loop_report": "present",
            "governor_decision": "present",
            "recommendation_status": "blocked" if blocked else "ready",
        },
        "packet_blueprint": {
            "packet_id": title,
            "mode": "APPLY" if human_approval_required else "DRY_RUN",
            "zone": "automation / orchestration / closed autonomy loop / packet preview",
            "lane": "APPLY_CODE_SAFE" if human_approval_required else "DRY_RUN",
            "risk_level": "medium",
            "allowed_paths": allowed_paths or ["Reports/sandbox/example/"],
            "forbidden_paths": ["AGENTS.md", "automation/orchestration/work_packets/", "broker/", "live_trading/", ".env"],
            "validator_chain": ["packet drafter validator", "git diff --check"],
            "stop_point": "Stop before queue mutation, worker dispatch, commit, push, or merge.",
            "preview_type": "BLOCKED_NEEDS_APPROVAL" if human_approval_required else "DRY_RUN_PACKET_PREVIEW",
        },
        "validation": {
            "agents_required_fields_present": True,
            "missing_fields": [],
            "blocked": blocked,
            "blocked_reason": "fixture_blocked" if blocked else None,
        },
        "dispatch": {
            "dispatch_authorized": False,
            "queue_mutation_authorized": False,
            "human_approval_required": human_approval_required,
        },
        "preview_text_path": "Reports/sandbox/closed_loop_packet_drafter/AIOS_CLOSED_LOOP_PACKET_DRAFTER_PREVIEW.txt",
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


def _write_drafter(root: Path, report: dict) -> None:
    path = root / DRAFTER_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _required_report_fields() -> set[str]:
    return {
        "schema_version",
        "system",
        "component",
        "mode",
        "generated_at_utc",
        "input_status",
        "proposed_queue_item",
        "validation",
        "safety_boundaries",
        "next_step",
    }


def _assert_schema_valid(report: dict) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert set(schema["required"]) == _required_report_fields()
    assert _required_report_fields().issubset(report)
    assert report["schema_version"] == "1.0"
    assert report["system"] == "AI_OS"
    assert report["component"] == "closed_loop_queue_injection_preview"
    assert report["mode"] == "APPLY_BUILD_WITH_QUEUE_PREVIEW_OUTPUT"
    assert report["proposed_queue_item"]["dispatch_authorized"] is False
    assert report["proposed_queue_item"]["queue_mutation_authorized"] is False


def test_preview_produces_json_report_with_required_fields(tmp_path: Path) -> None:
    m = _load()
    _write_drafter(tmp_path, _drafter_report())

    report = m.build_queue_injection_preview_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert _required_report_fields().issubset(report)
    assert (tmp_path / OUTPUT_PATH).exists()
    assert report["input_status"]["packet_drafter_preview"] == "present"


def test_missing_packet_drafter_preview_produces_blocked_queue_preview(tmp_path: Path) -> None:
    m = _load()

    report = m.build_queue_injection_preview_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["input_status"]["packet_drafter_preview"] == "missing"
    assert report["proposed_queue_item"]["status"] == "blocked"
    assert report["proposed_queue_item"]["blocked_reason"] == "missing_packet_drafter_preview"


def test_blocked_packet_drafter_preview_produces_blocked_queue_preview(tmp_path: Path) -> None:
    m = _load()
    _write_drafter(tmp_path, _drafter_report(blocked=True))

    report = m.build_queue_injection_preview_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["input_status"]["packet_drafter_preview"] == "blocked"
    assert report["proposed_queue_item"]["status"] == "blocked"
    assert report["validation"]["blocked"] is True


def test_valid_packet_blueprint_produces_proposed_queue_item(tmp_path: Path) -> None:
    m = _load()
    _write_drafter(tmp_path, _drafter_report())

    report = m.build_queue_injection_preview_report(tmp_path, generated_at_utc=FIXED_NOW)
    item = report["proposed_queue_item"]

    assert item["packet_id"] == "AIOS-RUNTIME-QUEUE-BACKLOG-CONSOLIDATION-DRY-RUN"
    assert item["source_component"] == "closed_loop_packet_drafter"
    assert item["status"] == "preview_only"
    assert item["validators_required"] == ["packet drafter validator", "git diff --check"]


def test_queue_mutation_authorized_is_always_false(tmp_path: Path) -> None:
    m = _load()
    _write_drafter(tmp_path, _drafter_report())

    report = m.build_queue_injection_preview_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["proposed_queue_item"]["queue_mutation_authorized"] is False
    assert report["safety_boundaries"]["real_queue_mutation"] == "blocked"


def test_dispatch_authorized_is_always_false(tmp_path: Path) -> None:
    m = _load()
    _write_drafter(tmp_path, _drafter_report())

    report = m.build_queue_injection_preview_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["proposed_queue_item"]["dispatch_authorized"] is False
    assert report["safety_boundaries"]["worker_dispatch"] == "blocked"


def test_approval_required_true_when_packet_requires_human_approval(tmp_path: Path) -> None:
    m = _load()
    _write_drafter(tmp_path, _drafter_report(human_approval_required=True))

    report = m.build_queue_injection_preview_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["proposed_queue_item"]["approval_required"] is True
    assert report["proposed_queue_item"]["status"] == "requires_approval"
    assert report["proposed_queue_item"]["dispatch_authorized"] is False


def test_live_trading_broker_credential_scope_is_blocked(tmp_path: Path) -> None:
    m = _load()
    _write_drafter(
        tmp_path,
        _drafter_report(allowed_paths=["apps/trading_lab/live_trading/broker_credentials.py"]),
    )

    report = m.build_queue_injection_preview_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["proposed_queue_item"]["status"] == "blocked"
    assert report["proposed_queue_item"]["blocked_reason"] == "unsafe_scope_blocked"
    assert report["safety_boundaries"]["live_trading"] == "blocked"
    assert report["safety_boundaries"]["broker_execution"] == "blocked"
    assert report["safety_boundaries"]["credential_use"] == "blocked"


def test_schema_validation_passes(tmp_path: Path) -> None:
    m = _load()
    _write_drafter(tmp_path, _drafter_report())

    report = m.build_queue_injection_preview_report(tmp_path, generated_at_utc=FIXED_NOW)

    _assert_schema_valid(report)


def test_deterministic_output_except_timestamp_and_generated_queue_item_id(tmp_path: Path) -> None:
    m = _load()
    _write_drafter(tmp_path, _drafter_report())

    first = m.build_queue_injection_preview_report(tmp_path, generated_at_utc="2026-06-14T12:00:00Z")
    second = m.build_queue_injection_preview_report(tmp_path, generated_at_utc="2026-06-14T12:01:00Z")
    first.pop("generated_at_utc")
    second.pop("generated_at_utc")
    first["proposed_queue_item"].pop("queue_item_id")
    second["proposed_queue_item"].pop("queue_item_id")

    assert first == second


def test_no_real_queue_path_is_written(tmp_path: Path) -> None:
    m = _load()
    _write_drafter(tmp_path, _drafter_report())

    m.build_queue_injection_preview_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert not (tmp_path / "automation" / "orchestration" / "work_packets" / "active").exists()
    assert not (tmp_path / "Reports" / "runtime_queue").exists()
    assert (tmp_path / OUTPUT_PATH).exists()
