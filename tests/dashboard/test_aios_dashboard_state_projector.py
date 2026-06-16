from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import pytest

try:
    from jsonschema import Draft202012Validator
except ModuleNotFoundError:  # pragma: no cover
    Draft202012Validator = None  # type: ignore[assignment]


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "dashboard" / "aios_dashboard_state_projector.py"
SCHEMA_PATH = REPO_ROOT / "schemas" / "aios" / "orchestration" / "AIOS_DASHBOARD_STATE_CONTRACT.v1.schema.json"
FIXED_NOW = "2026-06-16T00:00:00Z"
OLD_NOW = "2026-06-15T23:00:00Z"

STATE_SECTIONS = (
    "system_state",
    "security_state",
    "continuation_state",
    "governor_state",
    "watchtower_state",
    "validator_state",
    "control_plane_state",
    "active_mission_state",
    "resume_state",
    "worker_state",
)

BOUNDARY_FALSE_FLAGS = (
    "dashboard_creates_truth",
    "execution_allowed",
    "mutation_allowed",
    "control_authority",
    "button_authority",
    "broker_allowed",
    "live_trading_allowed",
    "approval_mutation_allowed",
    "worker_launch_allowed",
    "scheduler_allowed",
    "daemon_allowed",
)


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("aios_dashboard_state_projector", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_contract(payload: dict[str, Any]) -> None:
    schema = load_schema()
    if Draft202012Validator is not None:
        Draft202012Validator(schema).validate(payload)
    else:
        for field in schema["required"]:
            assert field in payload
        assert payload["schema"] == "AIOS_DASHBOARD_STATE_CONTRACT.v1"
        assert payload["mode"] == "DISPLAY_ONLY_READ_MODEL"


def evidence_ref(payload: dict[str, Any], section: str, source_schema: str | None = None, **extra: Any) -> dict[str, Any]:
    return {
        "payload": payload,
        "source_path": f"tests/fixtures/dashboard/aios_dashboard_state_projector/{section}.json",
        "source_schema": source_schema or payload.get("schema"),
        "source_type": "fixture",
        **extra,
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


def test_projects_full_payload_against_dashboard_contract_schema() -> None:
    module = load_module()
    projected = module.project_dashboard_state(full_evidence(), now_utc=FIXED_NOW)

    validate_contract(projected)
    assert projected["schema"] == "AIOS_DASHBOARD_STATE_CONTRACT.v1"
    assert projected["schema_version"] == "1.0"
    assert projected["mode"] == "DISPLAY_ONLY_READ_MODEL"


def test_all_required_sections_have_source_freshness_and_authority_fields() -> None:
    module = load_module()
    projected = module.project_dashboard_state(full_evidence(), now_utc=FIXED_NOW)

    for section_name in STATE_SECTIONS:
        section = projected[section_name]
        for field in ("source_path", "source_schema", "freshness", "authority_state"):
            assert section[field]
        assert section["execution_allowed"] is False
        assert section["mutation_allowed"] is False
        assert section["safe_for_frontend_display"] is True


def test_read_only_authority_boundary_is_fail_closed() -> None:
    module = load_module()
    projected = module.project_dashboard_state(full_evidence(), now_utc=FIXED_NOW)

    assert projected["authority_boundary"]["read_only"] is True
    assert projected["authority_boundary"]["evidence_only"] is True
    for flag in BOUNDARY_FALSE_FLAGS:
        assert projected["authority_boundary"][flag] is False


def test_missing_evidence_becomes_needs_review_missing_and_approval_required() -> None:
    module = load_module()
    evidence = full_evidence()
    del evidence["validator_state"]

    projected = module.project_dashboard_state(evidence, now_utc=FIXED_NOW)
    section = projected["validator_state"]

    validate_contract(projected)
    assert section["display_state"] == "NEEDS_REVIEW"
    assert section["freshness"]["evidence_state"] == "MISSING"
    assert section["approval_required"] is True


def test_stale_evidence_becomes_needs_review_stale_and_approval_required() -> None:
    module = load_module()
    evidence = full_evidence()
    evidence["system_state"] = evidence_ref(
        {"schema": "RUNTIME_VISIBILITY_SCHEMA", "generated_at": OLD_NOW, "status": "ready"},
        "system_state",
        ttl_seconds=60,
    )

    projected = module.project_dashboard_state(evidence, now_utc=FIXED_NOW)
    section = projected["system_state"]

    validate_contract(projected)
    assert section["display_state"] == "NEEDS_REVIEW"
    assert section["freshness"]["evidence_state"] == "STALE"
    assert section["approval_required"] is True


def test_unsupported_schema_becomes_needs_review_unsupported_and_approval_required() -> None:
    module = load_module()
    evidence = full_evidence()
    evidence["validator_state"] = evidence_ref(
        {"schema": "UNSUPPORTED_VALIDATOR_SCHEMA.v9", "generated_at_utc": FIXED_NOW, "status": "pass"},
        "validator_state",
    )

    projected = module.project_dashboard_state(evidence, now_utc=FIXED_NOW)
    section = projected["validator_state"]

    validate_contract(projected)
    assert section["display_state"] == "NEEDS_REVIEW"
    assert section["freshness"]["evidence_state"] == "UNSUPPORTED"
    assert section["approval_required"] is True


def test_unsafe_positive_authority_evidence_becomes_blocked() -> None:
    module = load_module()
    evidence = full_evidence()
    payload = dict(evidence["security_state"]["payload"])
    payload["execution_allowed"] = True
    evidence["security_state"] = evidence_ref(payload, "security_state")

    projected = module.project_dashboard_state(evidence, now_utc=FIXED_NOW)
    section = projected["security_state"]

    validate_contract(projected)
    assert section["display_state"] == "BLOCKED"
    assert section["approval_required"] is True
    assert section["execution_allowed"] is False
    assert section["mutation_allowed"] is False
    assert projected["system_health"] == "BLOCKED"


def test_security_continuation_and_watchtower_evidence_map_into_sections() -> None:
    module = load_module()
    projected = module.project_dashboard_state(full_evidence(), now_utc=FIXED_NOW)

    assert projected["security_state"]["display_state"] == "CLEAR"
    assert projected["security_state"]["shield_state"] == "GREEN"
    assert projected["security_state"]["vault_lock_state"] == "LOCKED"
    assert projected["security_state"]["radar_events"][0]["event_id"] == "radar-1"

    assert projected["continuation_state"]["display_state"] == "CONTINUE"
    assert projected["continuation_state"]["current_task"]["task_id"] == "fixture-task"
    assert projected["continuation_state"]["repair_count"] == 0

    assert projected["watchtower_state"]["display_state"] == "CANDIDATE_FOUND"
    assert projected["watchtower_state"]["market_regime"] == "TREND_UP"
    assert projected["watchtower_state"]["next_best_setup"]["symbol"] == "EURUSD"


def test_source_index_includes_supplied_evidence_sources() -> None:
    module = load_module()
    projected = module.project_dashboard_state(full_evidence(), now_utc=FIXED_NOW)

    paths = {item["source_path"] for item in projected["source_index"]["primary_sources"]}
    assert "tests/fixtures/dashboard/aios_dashboard_state_projector/security_state.json" in paths
    assert "tests/fixtures/dashboard/aios_dashboard_state_projector/watchtower_state.json" in paths
    assert "schemas/aios/orchestration/STATE_PROJECTION_RULES.md" in paths


def test_projector_source_has_no_subprocess_or_runtime_write_api() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert "write_text" not in source
    assert "open(" not in source


def test_projector_exports_pure_function_only_for_public_api() -> None:
    module = load_module()
    assert callable(module.project_dashboard_state)
    assert module.__all__ == ["project_dashboard_state"]


@pytest.mark.parametrize("section_name", STATE_SECTIONS)
def test_no_section_grants_execution_or_mutation(section_name: str) -> None:
    module = load_module()
    projected = module.project_dashboard_state(full_evidence(), now_utc=FIXED_NOW)

    section = projected[section_name]
    assert section["execution_allowed"] is False
    assert section["mutation_allowed"] is False
