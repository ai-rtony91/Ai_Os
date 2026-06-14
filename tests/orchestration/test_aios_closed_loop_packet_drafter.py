from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE = REPO_ROOT / "automation" / "orchestration" / "aios_closed_loop_packet_drafter.py"
SCHEMA = REPO_ROOT / "schemas" / "orchestration" / "aios_closed_loop_packet_drafter.schema.json"
FIXED_NOW = "2026-06-14T12:00:00Z"


def _load():
    spec = importlib.util.spec_from_file_location("aios_closed_loop_packet_drafter", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _closed_loop_report(
    *,
    gate_status: str = "ready_for_dry_run",
    category: str = "QUEUE_CONSOLIDATION",
    proposed_mode: str = "DRY_RUN",
    title: str = "Consolidate queue evidence before worker routing.",
    allowed_paths: list[str] | None = None,
) -> dict:
    return {
        "schema_version": "1.0",
        "system": "AI_OS",
        "component": "closed_autonomy_loop",
        "mode": "ONE_CYCLE_RECOMMENDATION_ONLY",
        "loop_id": "AIOS-CLOSED-LOOP-fixture",
        "generated_at_utc": FIXED_NOW,
        "loop_phase_status": {
            "observe": "complete",
            "decide": "complete",
            "plan": "complete",
            "validate_gate": "complete",
            "recommend_dispatch": "complete",
            "report": "complete",
            "stop": "complete",
        },
        "inputs": [{"name": "fixture", "path": "fixture.json", "status": "present", "summary": "fixture"}],
        "governor_decision": {
            "selected_candidate_id": "runtime_queue_backlog_consolidation",
            "decision_category": category,
            "blocked": False,
            "blocked_reason": None,
            "allowed_lane": "DRY_RUN" if proposed_mode != "APPLY" else "APPLY_CODE_SAFE",
        },
        "proposed_cycle_action": {
            "proposed_action_id": "runtime_queue_backlog_consolidation",
            "proposed_action_title": title,
            "proposed_packet_id": "AIOS-RUNTIME-QUEUE-BACKLOG-CONSOLIDATION-DRY-RUN",
            "proposed_mode": proposed_mode,
            "proposed_lane": "DRY_RUN" if proposed_mode != "APPLY" else "APPLY_CODE_SAFE",
            "required_validators": ["Runtime execution queue validator", "git diff --check"],
            "required_approval": "anthony" if proposed_mode == "APPLY" else "none",
            "allowed_paths": allowed_paths or ["Reports/runtime_queue/", "tests/orchestration/"],
            "forbidden_paths": ["AGENTS.md", "README.md", "broker/", "live_trading/", ".env"],
            "stop_conditions": ["Stop before queue mutation, worker launch, commit, push, or merge."],
        },
        "gate_result": {
            "status": gate_status,
            "reason": "fixture gate reason",
            "safe_to_dispatch": False,
        },
        "dispatch_recommendation": {
            "dispatch_authorized": False,
            "recommended_next_packet_type": "DRY_RUN_PACKET",
            "recommended_next_packet_id": "AIOS-RUNTIME-QUEUE-BACKLOG-CONSOLIDATION-DRY-RUN",
            "recommended_worker_lane": "DRY_RUN",
            "human_action_required": gate_status != "ready_for_dry_run",
            "reason": "fixture dispatch disabled",
        },
        "safety_boundaries": {
            "continuous_loop": "blocked",
            "worker_dispatch": "recommendation_only",
            "live_trading": "blocked",
            "broker_execution": "blocked",
            "credential_use": "blocked",
            "unapproved_mutation": "blocked",
        },
        "next_loop_requirement": "fixture",
    }


def _write_closed_loop(root: Path, report: dict) -> None:
    path = root / "Reports" / "closed_autonomy_loop" / "AIOS_CLOSED_AUTONOMY_LOOP_LATEST.json"
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
        "packet_blueprint",
        "validation",
        "dispatch",
        "preview_text_path",
        "safety_boundaries",
    }


def _preview_text(root: Path) -> str:
    return (root / "Reports" / "sandbox" / "closed_loop_packet_drafter" / "AIOS_CLOSED_LOOP_PACKET_DRAFTER_PREVIEW.txt").read_text(encoding="utf-8")


def _assert_required_packet_fields(text: str) -> None:
    for marker in [
        "CODEX-ONLY PROMPT",
        "AI_OS EXECUTION TOKEN",
        "AI_OS BOOTSTRAP REQUIRED",
        "IDENTITY",
        "SUPERVISOR IDENTITY",
        "PACKET ID",
        "MODE",
        "ZONE",
        "WORKER IDENTITY",
        "LANE",
        "WORKTREE",
        "BRANCH",
        "PREFLIGHT",
        "ALLOWED PATHS",
        "FORBIDDEN PATHS",
        "APPROVAL AUTHORITY",
        "VALIDATOR CHAIN",
        "STOP POINT",
        "MISSION",
        "FINAL REPORT FORMAT",
    ]:
        assert marker in text


def _assert_schema_valid(report: dict) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    assert set(schema["required"]) == _required_report_fields()
    assert _required_report_fields().issubset(report)
    assert report["schema_version"] == "1.0"
    assert report["system"] == "AI_OS"
    assert report["component"] == "closed_loop_packet_drafter"
    assert report["mode"] == "APPLY_BUILD_WITH_PREVIEW_OUTPUT"
    assert report["dispatch"]["dispatch_authorized"] is False
    assert report["dispatch"]["queue_mutation_authorized"] is False
    for key in (
        "worker_dispatch",
        "queue_mutation",
        "continuous_loop",
        "live_trading",
        "broker_execution",
        "credential_use",
        "unapproved_mutation",
    ):
        assert key in report["safety_boundaries"]


def test_drafter_produces_json_report_with_required_fields(tmp_path: Path) -> None:
    m = _load()
    _write_closed_loop(tmp_path, _closed_loop_report())

    report = m.build_packet_drafter_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert _required_report_fields().issubset(report)
    assert report["input_status"]["closed_loop_report"] == "present"
    assert report["packet_blueprint"]["packet_id"]


def test_drafter_produces_text_preview_with_codex_marker_first(tmp_path: Path) -> None:
    m = _load()
    _write_closed_loop(tmp_path, _closed_loop_report())

    m.build_packet_drafter_report(tmp_path, generated_at_utc=FIXED_NOW)
    text = _preview_text(tmp_path)

    assert text.splitlines()[0] == "CODEX-ONLY PROMPT"


def test_preview_includes_all_agents_required_packet_fields(tmp_path: Path) -> None:
    m = _load()
    _write_closed_loop(tmp_path, _closed_loop_report())

    m.build_packet_drafter_report(tmp_path, generated_at_utc=FIXED_NOW)

    _assert_required_packet_fields(_preview_text(tmp_path))


def test_missing_closed_loop_input_produces_blocked_preview_not_malformed(tmp_path: Path) -> None:
    m = _load()

    report = m.build_packet_drafter_report(tmp_path, generated_at_utc=FIXED_NOW)
    text = _preview_text(tmp_path)

    assert report["input_status"]["closed_loop_report"] in {"missing", "generated_in_memory", "blocked"}
    assert report["validation"]["agents_required_fields_present"] is True
    assert "CODEX-ONLY PROMPT" == text.splitlines()[0]
    assert "PREVIEW_ONLY" in text or "REQUIRES_ANTHONY_APPROVAL" in text


def test_approval_required_apply_marks_human_required_and_dispatch_false(tmp_path: Path) -> None:
    m = _load()
    _write_closed_loop(tmp_path, _closed_loop_report(gate_status="ready_for_apply", proposed_mode="APPLY"))

    report = m.build_packet_drafter_report(tmp_path, generated_at_utc=FIXED_NOW)
    text = _preview_text(tmp_path)

    assert report["packet_blueprint"]["mode"] == "APPLY"
    assert report["dispatch"]["human_approval_required"] is True
    assert report["dispatch"]["dispatch_authorized"] is False
    assert "REQUIRES_ANTHONY_APPROVAL" in text


def test_queue_mutation_remains_false(tmp_path: Path) -> None:
    m = _load()
    _write_closed_loop(tmp_path, _closed_loop_report())

    report = m.build_packet_drafter_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["dispatch"]["queue_mutation_authorized"] is False
    assert report["safety_boundaries"]["queue_mutation"] == "blocked"


def test_worker_dispatch_remains_false(tmp_path: Path) -> None:
    m = _load()
    _write_closed_loop(tmp_path, _closed_loop_report())

    report = m.build_packet_drafter_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["dispatch"]["dispatch_authorized"] is False
    assert report["safety_boundaries"]["worker_dispatch"] == "blocked"


def test_live_trading_broker_credential_scope_is_blocked(tmp_path: Path) -> None:
    m = _load()
    _write_closed_loop(
        tmp_path,
        _closed_loop_report(
            title="Add broker execution with credentials.",
            allowed_paths=["apps/trading_lab/live_trading/broker_credentials.py"],
        ),
    )

    report = m.build_packet_drafter_report(tmp_path, generated_at_utc=FIXED_NOW)

    assert report["packet_blueprint"]["preview_type"] == "BLOCKED_SAFETY_SCOPE"
    assert report["validation"]["blocked"] is True
    assert report["dispatch"]["dispatch_authorized"] is False


def test_schema_validation_passes(tmp_path: Path) -> None:
    m = _load()
    _write_closed_loop(tmp_path, _closed_loop_report())

    report = m.build_packet_drafter_report(tmp_path, generated_at_utc=FIXED_NOW)

    _assert_schema_valid(report)


def test_no_unresolved_placeholders_appear_in_preview_text(tmp_path: Path) -> None:
    m = _load()
    _write_closed_loop(tmp_path, _closed_loop_report())

    m.build_packet_drafter_report(tmp_path, generated_at_utc=FIXED_NOW)
    text = _preview_text(tmp_path)

    for marker in ("TODO", "TBD", "@filename", "path/to/", "[REAL-FILENAME]", "{feature}"):
        assert marker.lower() not in text.lower()


def test_deterministic_output_except_timestamp(tmp_path: Path) -> None:
    m = _load()
    _write_closed_loop(tmp_path, _closed_loop_report())

    first = m.build_packet_drafter_report(tmp_path, generated_at_utc="2026-06-14T12:00:00Z")
    second = m.build_packet_drafter_report(tmp_path, generated_at_utc="2026-06-14T12:01:00Z")
    first.pop("generated_at_utc")
    second.pop("generated_at_utc")

    assert first == second
