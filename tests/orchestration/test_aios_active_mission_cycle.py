from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE = REPO_ROOT / "automation" / "orchestration" / "aios_active_mission_cycle.py"
SCHEMA = REPO_ROOT / "schemas" / "orchestration" / "aios_active_mission_cycle.schema.json"
FIXED_NOW = "2026-06-14T12:00:00Z"
OUTPUT_DIR = Path("Reports") / "sandbox" / "active_mission_cycle"
OUTPUT_JSON = OUTPUT_DIR / "AIOS_ACTIVE_MISSION_CYCLE_LATEST.json"
OUTPUT_SOS = OUTPUT_DIR / "AIOS_ACTIVE_MISSION_SOS_LATEST.md"


def _load():
    spec = importlib.util.spec_from_file_location("aios_active_mission_cycle", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write(root: Path, relative: Path, payload: dict) -> None:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _paths() -> dict[str, Path]:
    return {
        "closed_loop": Path("Reports/sandbox/closed_autonomy_loop/AIOS_CLOSED_AUTONOMY_LOOP_LATEST.json"),
        "packet_drafter": Path("Reports/sandbox/closed_loop_packet_drafter/AIOS_CLOSED_LOOP_PACKET_DRAFTER_PREVIEW.json"),
        "queue_preview": Path(
            "Reports/sandbox/closed_loop_queue_injection_preview/AIOS_CLOSED_LOOP_QUEUE_INJECTION_PREVIEW.json"
        ),
        "queue_gates": Path("Reports/sandbox/queue_to_dispatch_gates/AIOS_QUEUE_TO_DISPATCH_GATES_PREVIEW.json"),
        "repo_state": Path("Reports/repo_state/AIOS_REPO_STATE_LATEST.json"),
        "governor": Path("Reports/autonomy_decision_governor/AIOS_AUTONOMY_DECISION_GOVERNOR_LATEST.json"),
    }


def _closed_loop(status: str = "ready_for_dry_run", reason: str = "fixture ready") -> dict:
    return {
        "schema_version": "1.0",
        "system": "AI_OS",
        "component": "closed_autonomy_loop",
        "mode": "ONE_CYCLE_RECOMMENDATION_ONLY",
        "generated_at_utc": FIXED_NOW,
        "gate_result": {
            "status": status,
            "reason": reason,
            "safe_to_dispatch": False,
        },
        "dispatch_recommendation": {
            "dispatch_authorized": False,
            "queue_mutation_authorized": False,
            "human_action_required": True,
            "recommended_next_packet_id": "AIOS-FIXTURE-NEXT-PACKET",
            "recommended_worker_lane": "DRY_RUN",
        },
        "proposed_cycle_action": {
            "proposed_action_id": "AIOS-FIXTURE-ACTION",
            "proposed_action_title": "Fixture next safe action.",
            "proposed_packet_id": "AIOS-FIXTURE-NEXT-PACKET",
            "proposed_mode": "DRY_RUN",
            "proposed_lane": "DRY_RUN",
            "allowed_paths": ["Reports/sandbox/example/"],
            "forbidden_paths": ["broker/", "live_trading/", ".env"],
            "required_validators": ["fixture validator"],
            "stop_conditions": ["Stop before queue mutation or dispatch."],
        },
        "safety_boundaries": {
            "continuous_loop": "blocked",
            "worker_dispatch": "recommendation_only",
            "queue_mutation": "blocked",
            "live_trading": "blocked",
            "broker_execution": "blocked",
            "credential_use": "blocked",
        },
    }


def _packet_drafter(blocked: bool = False, reason: str | None = None, approval: bool = False) -> dict:
    return {
        "schema_version": "1.0",
        "system": "AI_OS",
        "component": "closed_loop_packet_drafter",
        "mode": "APPLY_BUILD_WITH_PREVIEW_OUTPUT",
        "generated_at_utc": FIXED_NOW,
        "input_status": {
            "closed_loop_report": "present",
            "governor_decision": "present",
            "recommendation_status": "ready",
        },
        "packet_blueprint": {
            "packet_id": "AIOS-FIXTURE-NEXT-PACKET",
            "mode": "DRY_RUN",
            "zone": "automation / orchestration",
            "lane": "DRY_RUN",
            "risk_level": "medium",
            "allowed_paths": ["Reports/sandbox/example/"],
            "forbidden_paths": ["broker/", "live_trading/", ".env"],
            "validator_chain": ["fixture validator"],
            "stop_point": "Stop after preview.",
        },
        "validation": {
            "agents_required_fields_present": not blocked,
            "missing_fields": [],
            "blocked": blocked,
            "blocked_reason": reason,
        },
        "dispatch": {
            "dispatch_authorized": False,
            "queue_mutation_authorized": False,
            "human_approval_required": approval,
        },
    }


def _queue_preview(blocked: bool = False, reason: str | None = None, approval: bool = False) -> dict:
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
            "queue_item_id": "AIOS-QUEUE-FIXTURE",
            "packet_id": "AIOS-FIXTURE-NEXT-PACKET",
            "mode": "DRY_RUN",
            "lane": "DRY_RUN",
            "risk_level": "medium",
            "approval_required": approval,
            "approval_authority": "Anthony Meza",
            "validators_required": ["fixture validator"],
            "allowed_paths": ["Reports/sandbox/example/"],
            "forbidden_paths": ["broker/", "live_trading/", ".env"],
            "stop_conditions": ["Stop before queue mutation or dispatch."],
            "dispatch_authorized": False,
            "queue_mutation_authorized": False,
            "status": "blocked" if blocked else "preview_only",
            "blocked_reason": reason if blocked else None,
        },
        "validation": {
            "required_fields_present": not blocked,
            "missing_fields": [],
            "blocked": blocked,
            "blocked_reason": reason,
        },
    }


def _queue_gates(status: str = "preview_only", blocked_reason: str | None = None) -> dict:
    blocked = status == "blocked"
    return {
        "schema_version": "1.0",
        "system": "AI_OS",
        "component": "queue_to_dispatch_gates",
        "mode": "APPLY_BUILD_WITH_CONSOLIDATED_GATE_PREVIEW_OUTPUT",
        "generated_at_utc": FIXED_NOW,
        "overall_status": status,
        "validated_queue_item": {
            "queue_item_id": "AIOS-QUEUE-FIXTURE",
            "packet_id": "AIOS-FIXTURE-NEXT-PACKET",
            "mode": "DRY_RUN",
            "lane": "DRY_RUN",
            "risk_level": "medium",
            "approval_required": False,
            "approval_authority": "Anthony Meza",
            "validators_required": ["fixture validator"],
            "allowed_paths": ["Reports/sandbox/example/"],
            "forbidden_paths": ["broker/", "live_trading/", ".env"],
            "stop_conditions": ["Stop before queue mutation or dispatch."],
            "dispatch_authorized": False,
            "queue_mutation_authorized": False,
            "status": status,
        },
        "gates": {
            "queue_admission_preview": {
                "status": status,
                "reason": blocked_reason or "fixture ready",
                "queue_mutation_authorized": False,
                "dispatch_authorized": False,
                "human_approval_required": False,
            }
        },
        "validation": {
            "required_fields_present": not blocked,
            "missing_fields": [],
            "blocked": blocked,
            "blocked_reason": blocked_reason,
        },
        "safety_boundaries": {
            "real_queue_mutation": "blocked",
            "worker_dispatch": "blocked",
            "continuous_loop": "blocked",
            "live_trading": "blocked",
            "broker_execution": "blocked",
            "credential_use": "blocked",
        },
        "next_step": "fixture",
    }


def _repo_state(clean: bool = True) -> dict:
    return {
        "schema_version": "1.0",
        "system": "AI_OS",
        "component": "repo_state_evidence",
        "branch": "main",
        "is_clean": clean,
        "safe_for_apply": clean,
        "blocked_reason": None if clean else "dirty_working_tree",
        "tracked_dirty_files": [] if clean else ["automation/orchestration/Invoke-AiOsNightCycle.ps1"],
        "untracked_files": [],
    }


def _governor(blocked: bool = False) -> dict:
    return {
        "schema_version": "1.0",
        "system": "AI_OS",
        "component": "autonomy_decision_governor",
        "decision_category": "NEXT_SAFE_PACKET",
        "blocked": blocked,
        "blocked_reason": "dirty_working_tree" if blocked else None,
        "allowed_lane": "DRY_RUN",
    }


def _seed_valid_chain(root: Path) -> None:
    paths = _paths()
    _write(root, paths["closed_loop"], _closed_loop())
    _write(root, paths["packet_drafter"], _packet_drafter())
    _write(root, paths["queue_preview"], _queue_preview())
    _write(root, paths["queue_gates"], _queue_gates())
    _write(root, paths["repo_state"], _repo_state())
    _write(root, paths["governor"], _governor())


def _required_fields() -> set[str]:
    return {
        "schema_version",
        "system",
        "component",
        "mode",
        "generated_at_utc",
        "mission_status",
        "current_chain_state",
        "selected_next_action",
        "blocked_reason",
        "human_action_required",
        "approval_required",
        "queue_mutation_authorized",
        "dispatch_authorized",
        "live_trading",
        "broker_execution",
        "sos_message_path",
        "next_step",
        "safety_boundaries",
    }


def _assert_schema_valid(report: dict) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert set(schema["required"]) == _required_fields()
    assert _required_fields().issubset(report)
    assert report["schema_version"] == "1.0"
    assert report["system"] == "AI_OS"
    assert report["component"] == "active_mission_cycle"
    assert report["mode"] == "ONE_CYCLE_SOS_REPORT_ONLY"
    assert report["mission_status"] in schema["properties"]["mission_status"]["enum"]
    assert report["queue_mutation_authorized"] is False
    assert report["dispatch_authorized"] is False


def test_json_report_contains_required_fields(tmp_path: Path) -> None:
    m = _load()
    _seed_valid_chain(tmp_path)

    report = m.build_active_mission_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert _required_fields().issubset(report)
    assert (tmp_path / OUTPUT_JSON).exists()


def test_markdown_sos_file_is_produced(tmp_path: Path) -> None:
    m = _load()
    _seed_valid_chain(tmp_path)

    m.build_active_mission_report(tmp_path, generated_at_utc=FIXED_NOW)
    text = (tmp_path / OUTPUT_SOS).read_text(encoding="utf-8")

    for heading in (
        "AI_OS STATUS",
        "WHAT I CHECKED",
        "WHAT I SELECTED",
        "WHY",
        "BLOCKER",
        "WHAT I NEED FROM ANTHONY",
        "NEXT SAFE ACTION",
        "SAFETY LOCKS",
    ):
        assert heading in text


def test_missing_evidence_produces_blocked_sos_not_failure(tmp_path: Path) -> None:
    m = _load()

    report = m.build_active_mission_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["mission_status"] == "blocked"
    assert "closed_autonomy_loop_missing" in report["blocked_reason"]
    assert (tmp_path / OUTPUT_SOS).exists()


def test_dirty_repo_reports_requires_cleanup(tmp_path: Path) -> None:
    m = _load()
    _seed_valid_chain(tmp_path)
    _write(tmp_path, _paths()["repo_state"], _repo_state(clean=False))

    report = m.build_active_mission_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["mission_status"] == "requires_cleanup"
    assert "dirty_working_tree" in report["blocked_reason"]


def test_blocked_queue_gate_surfaces_blocker(tmp_path: Path) -> None:
    m = _load()
    _seed_valid_chain(tmp_path)
    _write(tmp_path, _paths()["queue_gates"], _queue_gates(status="blocked", blocked_reason="closed_loop_report_missing"))

    report = m.build_active_mission_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["mission_status"] == "blocked"
    assert report["blocked_reason"] == "closed_loop_report_missing"


def test_dispatch_authorized_is_always_false(tmp_path: Path) -> None:
    m = _load()
    _seed_valid_chain(tmp_path)

    report = m.build_active_mission_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["dispatch_authorized"] is False


def test_queue_mutation_authorized_is_always_false(tmp_path: Path) -> None:
    m = _load()
    _seed_valid_chain(tmp_path)

    report = m.build_active_mission_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["queue_mutation_authorized"] is False


def test_live_trading_and_broker_scope_remain_blocked(tmp_path: Path) -> None:
    m = _load()
    _seed_valid_chain(tmp_path)

    report = m.build_active_mission_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["live_trading"] == "blocked"
    assert report["broker_execution"] == "blocked"
    assert report["safety_boundaries"]["credential_use"] == "blocked"


def test_schema_validation_passes(tmp_path: Path) -> None:
    m = _load()
    _seed_valid_chain(tmp_path)

    report = m.build_active_mission_report(tmp_path, generated_at_utc=FIXED_NOW)

    _assert_schema_valid(report)


def test_deterministic_output_except_timestamp(tmp_path: Path) -> None:
    m = _load()
    _seed_valid_chain(tmp_path)

    first = m.build_active_mission_report(tmp_path, generated_at_utc="2026-06-14T12:00:00Z")
    second = m.build_active_mission_report(tmp_path, generated_at_utc="2026-06-14T12:01:00Z")
    first.pop("generated_at_utc")
    second.pop("generated_at_utc")

    assert first == second
