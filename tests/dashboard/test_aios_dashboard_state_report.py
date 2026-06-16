from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_MODULE_PATH = (
    REPO_ROOT / "automation" / "orchestration" / "dashboard" / "aios_dashboard_state_report.py"
)
PROJECTOR_MODULE_PATH = (
    REPO_ROOT / "automation" / "orchestration" / "dashboard" / "aios_dashboard_state_projector.py"
)

FIXED_NOW = "2026-06-16T00:00:00Z"


def load_report_module() -> Any:
    spec = importlib.util.spec_from_file_location("aios_dashboard_state_report", REPORT_MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_projector_module() -> Any:
    spec = importlib.util.spec_from_file_location("aios_dashboard_state_projector", PROJECTOR_MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evidence_ref(payload: dict[str, Any], section: str, source_schema: str | None = None) -> dict[str, Any]:
    return {
        "payload": payload,
        "source_path": f"tests/fixtures/dashboard/aios_dashboard_state_projector/{section}.json",
        "source_schema": source_schema or payload.get("schema"),
        "source_type": "fixture",
    }


def full_evidence() -> dict[str, Any]:
    security = {
        "schema": "AIOS_PREEMPTIVE_SECURITY_STATE.v1",
        "generated_utc": FIXED_NOW,
        "overall_state": "CLEAR",
        "security_status": "clear",
        "shield_state": "GREEN",
        "vault_lock_state": "LOCKED",
        "radar_events": [{"event_id": "radar-1", "severity": "CLEAR"}],
        "tripwire_events": [],
        "boss_alert": {"active": False, "level": "CLEAR", "reason": ""},
        "events": [{"event_id": "event-1", "category": "CANARY_TRIP"}],
        "blocked_actions": ["broker execution"],
        "next_safe_action": "Continue display-only security review.",
    }
    continuation = {
        "schema": "AIOS_AUTONOMOUS_JOB_CONTINUATION_STATE.v1",
        "generated_at_utc": FIXED_NOW,
        "state": "CONTINUE",
        "selected_task": {"task_id": "fixture-task", "mode": "DRY_RUN"},
        "repair_count": 0,
        "resume": {"requested": False, "can_resume": False, "reason": "not_requested"},
        "approval_snapshot": {"approval_gate_status": "not_required"},
        "next_safe_action": "Continue to the next safe READ_ONLY/DRY_RUN cycle.",
    }
    watchtower = {
        "schema": "AIOS_TRADING_WATCHTOWER_RESULT.v1",
        "generated_at_utc": FIXED_NOW,
        "watchtower_status": "CANDIDATE_FOUND",
        "market_regime": "TREND_UP",
        "market_radar": [{"symbol": "EURUSD", "direction": "LONG", "status": "CANDIDATE_FOUND"}],
        "candidate_targets": [{"schema": "AIOS_TRADING_WATCHTOWER_CANDIDATE.v1", "symbol": "EURUSD"}],
        "priority_targets": [],
        "next_best_setup": {"symbol": "EURUSD", "direction": "LONG"},
        "next_safe_action": "Review paper-only watchtower candidate.",
    }
    return {
        "system_state": evidence_ref(
            {
                "schema": "RUNTIME_VISIBILITY_SCHEMA",
                "generated_at": FIXED_NOW,
                "status": "ready",
                "summary": "Runtime visibility fixture.",
                "items": [{"name": "runtime", "status": "ready"}],
            },
            "system_state",
        ),
        "security_state": evidence_ref(security, "security_state"),
        "continuation_state": evidence_ref(continuation, "continuation_state"),
        "governor_state": evidence_ref(
            {
                "schema": "AIOS_AUTONOMY_DECISION_GOVERNOR.v1",
                "generated_at_utc": FIXED_NOW,
                "decision_category": "DASHBOARD_SURFACING",
                "next_highest_value_task": "Surface dashboard read model.",
            },
            "governor_state",
        ),
        "watchtower_state": evidence_ref(watchtower, "watchtower_state"),
        "validator_state": evidence_ref(
            {
                "schema": "VALIDATOR_OUTPUT_SCHEMA",
                "generated_at_utc": FIXED_NOW,
                "status": "pass",
                "items": [{"validator": "fixture", "result": "pass"}],
            },
            "validator_state",
        ),
        "control_plane_state": evidence_ref(
            {
                "schema": "AIOS_CONTROL_PLANE_STATUS.v1",
                "generated_at_utc": FIXED_NOW,
                "loop_status": "dashboard_ready",
                "validator_status": "pass",
                "governor_status": "ready",
                "mission_status": "ready_for_next_packet",
                "next_safe_action": "Review control-plane status.",
            },
            "control_plane_state",
        ),
        "active_mission_state": evidence_ref(
            {
                "schema": "AIOS_ACTIVE_MISSION_CYCLE.v1",
                "generated_at_utc": FIXED_NOW,
                "mission_status": "ready_for_next_packet",
                "approval_required": False,
                "input_records": {"governor": {"status": "present"}},
            },
            "active_mission_state",
        ),
        "resume_state": evidence_ref(
            {
                "schema": "AIOS_RESUME_STATE.v1",
                "generated_at_utc": FIXED_NOW,
                "resume_ready": True,
                "next_safe_action": "Resume from fixture evidence.",
            },
            "resume_state",
        ),
        "worker_state": evidence_ref(
            {
                "schema": "WORKER_REGISTRY_SCHEMA",
                "generated_at_utc": FIXED_NOW,
                "status": "ready",
                "workers": [{"worker_id": "EAST_OCC_01", "status": "ready"}],
            },
            "worker_state",
        ),
    }


def projected_state() -> dict[str, Any]:
    projector = load_projector_module()
    return projector.project_dashboard_state(full_evidence(), now_utc=FIXED_NOW)


def test_report_renders_from_projected_state() -> None:
    module = load_report_module()
    report = module.render_dashboard_state_report(projected_state=projected_state())

    assert "# AIOS Dashboard State Report" in report
    assert "schema: `AIOS_DASHBOARD_STATE_CONTRACT.v1`" in report
    assert "mode: `DISPLAY_ONLY_READ_MODEL`" in report


def test_report_renders_from_evidence_through_projector() -> None:
    module = load_report_module()
    report = module.render_dashboard_state_report(evidence=full_evidence(), now_utc=FIXED_NOW)

    assert "generated_at_utc: `2026-06-16T00:00:00Z`" in report
    assert "security_state:" in report
    assert "watchtower_state:" in report
    assert "CANDIDATE_FOUND" in report


def test_report_renders_fail_closed_from_empty_input() -> None:
    module = load_report_module()
    report = module.render_dashboard_state_report(now_utc=FIXED_NOW)

    assert "NEEDS_REVIEW" in report
    assert "MISSING" in report
    assert "UNKNOWN" in report
    assert "Supply schema-backed evidence" in report


def test_report_includes_required_top_level_fields() -> None:
    module = load_report_module()
    report = module.render_dashboard_state_report(evidence=full_evidence(), now_utc=FIXED_NOW)

    for field in (
        "schema",
        "schema_version",
        "generated_at_utc",
        "mode",
        "system_health",
        "system_readiness",
        "risk_level",
        "blocked_actions",
        "next_safe_action",
        "source_count",
    ):
        assert field in report


def test_report_includes_required_operational_summary_sections() -> None:
    module = load_report_module()
    report = module.render_dashboard_state_report(evidence=full_evidence(), now_utc=FIXED_NOW)

    for section_name in (
        "security_state",
        "continuation_state",
        "watchtower_state",
        "control_plane_state",
    ):
        assert section_name in report
    assert "summary=clear" in report
    assert "summary=continuation_state projected from caller-supplied evidence." in report
    assert "summary=watchtower_state projected from caller-supplied evidence." in report
    assert "summary=ready_for_next_packet" in report


def test_report_highlights_fail_closed_states_when_present() -> None:
    module = load_report_module()
    state = projected_state()
    state["security_state"]["display_state"] = "BLOCKED"
    state["security_state"]["evidence_state"] = "UNKNOWN"
    state["security_state"]["freshness"]["evidence_state"] = "UNKNOWN"
    state["continuation_state"]["display_state"] = "STOP"
    state["watchtower_state"]["display_state"] = "SOS"
    state["validator_state"]["display_state"] = "NEEDS_REVIEW"
    state["validator_state"]["evidence_state"] = "STALE"
    state["validator_state"]["freshness"]["evidence_state"] = "STALE"
    state["worker_state"]["display_state"] = "NEEDS_REVIEW"
    state["worker_state"]["evidence_state"] = "UNSUPPORTED"
    state["worker_state"]["freshness"]["evidence_state"] = "UNSUPPORTED"
    state["resume_state"]["display_state"] = "NEEDS_REVIEW"
    state["resume_state"]["evidence_state"] = "MISSING"
    state["resume_state"]["freshness"]["evidence_state"] = "MISSING"
    state["system_health"] = "BLOCKED"
    state["system_readiness"] = "NEEDS_REVIEW"

    report = module.render_dashboard_state_report(projected_state=state)

    for marker in ("NEEDS_REVIEW", "STALE", "UNSUPPORTED", "MISSING", "UNKNOWN", "BLOCKED", "STOP", "SOS"):
        assert f"`{marker}`" in report


def test_blocked_actions_are_not_hidden() -> None:
    module = load_report_module()
    state = projected_state()
    state["blocked_actions"] = ["git add", "live trading", "worker launch"]
    state["security_state"]["blocked_actions"] = ["broker execution", "dashboard control"]

    report = module.render_dashboard_state_report(projected_state=state)

    for action in ("git add", "live trading", "worker launch", "broker execution", "dashboard control"):
        assert action in report


def test_report_output_is_deterministic_for_fixed_timestamp() -> None:
    module = load_report_module()

    first = module.render_dashboard_state_report(evidence=full_evidence(), now_utc=FIXED_NOW)
    second = module.render_dashboard_state_report(evidence=full_evidence(), now_utc=FIXED_NOW)

    assert first == second


def test_report_source_has_no_command_or_file_output_api() -> None:
    source = REPORT_MODULE_PATH.read_text(encoding="utf-8")

    assert "subprocess" not in source
    assert "write_text" not in source
    assert "open(" not in source


def test_report_exports_renderer_only_for_public_api() -> None:
    module = load_report_module()

    assert callable(module.render_dashboard_state_report)
    assert module.__all__ == ["render_dashboard_state_report"]
