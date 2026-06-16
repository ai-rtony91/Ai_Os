from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

import pytest

try:
    from jsonschema import Draft202012Validator
except ModuleNotFoundError:  # pragma: no cover - fallback keeps this test stdlib-runnable.
    Draft202012Validator = None  # type: ignore[assignment]


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / "schemas" / "aios" / "orchestration" / "AIOS_DASHBOARD_STATE_CONTRACT.v1.schema.json"

AUTHORITY_FALSE_FLAGS = (
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

FAIL_CLOSED_EVIDENCE_STATES = {"MISSING", "STALE", "UNSUPPORTED", "UNKNOWN"}
FAIL_CLOSED_DISPLAY_STATES = {"NEEDS_REVIEW", "REVIEW", "BLOCKED", "UNKNOWN"}


def load_schema() -> dict[str, Any]:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def freshness(evidence_state: str = "CURRENT", is_stale: bool = False) -> dict[str, Any]:
    return {
        "checked_at": "2026-06-16T00:00:00Z",
        "generated_at": "2026-06-16T00:00:00Z",
        "ttl_seconds": 300,
        "is_stale": is_stale,
        "evidence_state": evidence_state,
    }


def section(source_path: str, source_schema: str, display_state: str = "READY") -> dict[str, Any]:
    return {
        "display_state": display_state,
        "authority_state": "EVIDENCE_ONLY",
        "source_path": source_path,
        "source_schema": source_schema,
        "source_type": "canonical_schema",
        "freshness": freshness(),
        "evidence_state": "CURRENT",
        "summary": "Display-only evidence projection.",
        "items": [],
        "blocked_actions": ["APPLY", "git add", "git commit", "git push"],
        "next_safe_action": "Review source evidence before any protected action.",
        "approval_required": False,
        "execution_allowed": False,
        "mutation_allowed": False,
        "safe_for_frontend_display": True,
    }


def minimal_contract() -> dict[str, Any]:
    security = section(
        "schemas/aios/security/AIOS_PREEMPTIVE_SECURITY_STATE.v1.schema.json",
        "AIOS_PREEMPTIVE_SECURITY_STATE.v1",
        display_state="CLEAR",
    )
    security.update(
        {
            "shield_state": "GREEN",
            "vault_lock_state": "LOCKED",
            "radar_events": [],
            "tripwire_events": [],
            "boss_alert": {"active": False, "level": "CLEAR", "reason": ""},
        }
    )

    continuation = section(
        "schemas/aios/orchestration/AIOS_AUTONOMOUS_JOB_CONTINUATION_STATE.v1.schema.json",
        "AIOS_AUTONOMOUS_JOB_CONTINUATION_STATE.v1",
        display_state="CONTINUE",
    )
    continuation.update(
        {
            "current_task": {"task_id": "display-only-fixture", "mode": "DRY_RUN"},
            "repair_count": 0,
            "resume_status": "NO_PREVIOUS_STATE",
            "approval_status": "NOT_REQUIRED",
        }
    )

    watchtower = section(
        "schemas/aios/trading/AIOS_TRADING_WATCHTOWER_RESULT.v1.schema.json",
        "AIOS_TRADING_WATCHTOWER_RESULT.v1",
        display_state="NO_SETUP",
    )
    watchtower.update(
        {
            "market_radar": [],
            "candidate_targets": [],
            "priority_targets": [],
            "market_regime": "UNKNOWN",
            "watchtower_status": "NO_SETUP",
            "next_best_setup": None,
        }
    )

    control_plane = section(
        "automation/orchestration/aios_control_plane_status.py",
        "AIOS_CONTROL_PLANE_STATUS.v1",
        display_state="READY",
    )
    control_plane.update(
        {
            "control_plane_status": "display_only",
            "validator_status": "not_run",
            "governor_status": "display_only",
            "mission_status": "display_only",
        }
    )

    return {
        "schema": "AIOS_DASHBOARD_STATE_CONTRACT.v1",
        "schema_version": "1.0",
        "generated_at_utc": "2026-06-16T00:00:00Z",
        "mode": "DISPLAY_ONLY_READ_MODEL",
        "authority_boundary": {
            "read_only": True,
            "evidence_only": True,
            "dashboard_creates_truth": False,
            "execution_allowed": False,
            "mutation_allowed": False,
            "control_authority": False,
            "button_authority": False,
            "broker_allowed": False,
            "live_trading_allowed": False,
            "approval_mutation_allowed": False,
            "worker_launch_allowed": False,
            "scheduler_allowed": False,
            "daemon_allowed": False,
        },
        "source_index": {
            "primary_sources": [
                {
                    "source_path": "schemas/aios/orchestration/STATE_PROJECTION_RULES.md",
                    "source_schema": "STATE_PROJECTION_RULES",
                    "source_type": "canonical_doc",
                    "authority_state": "CANONICAL_AUTHORITY",
                }
            ],
            "backing_schemas": [
                {
                    "source_path": "schemas/aios/security/AIOS_PREEMPTIVE_SECURITY_STATE.v1.schema.json",
                    "source_schema": "AIOS_PREEMPTIVE_SECURITY_STATE.v1",
                    "source_type": "canonical_schema",
                    "authority_state": "CANONICAL_AUTHORITY",
                },
                {
                    "source_path": "schemas/aios/orchestration/AIOS_AUTONOMOUS_JOB_CONTINUATION_STATE.v1.schema.json",
                    "source_schema": "AIOS_AUTONOMOUS_JOB_CONTINUATION_STATE.v1",
                    "source_type": "canonical_schema",
                    "authority_state": "CANONICAL_AUTHORITY",
                },
                {
                    "source_path": "schemas/aios/trading/AIOS_TRADING_WATCHTOWER_RESULT.v1.schema.json",
                    "source_schema": "AIOS_TRADING_WATCHTOWER_RESULT.v1",
                    "source_type": "canonical_schema",
                    "authority_state": "CANONICAL_AUTHORITY",
                },
            ],
        },
        "freshness": freshness(),
        "system_state": section(
            "schemas/aios/orchestration/RUNTIME_VISIBILITY_SCHEMA.json",
            "RUNTIME_VISIBILITY_SCHEMA",
        ),
        "security_state": security,
        "continuation_state": continuation,
        "governor_state": section(
            "automation/orchestration/aios_autonomy_decision_governor.py",
            "AIOS_AUTONOMY_DECISION_GOVERNOR.v1",
        ),
        "watchtower_state": watchtower,
        "validator_state": section(
            "schemas/aios/orchestration/VALIDATOR_OUTPUT_SCHEMA.json",
            "VALIDATOR_OUTPUT_SCHEMA",
        ),
        "control_plane_state": control_plane,
        "active_mission_state": section(
            "automation/orchestration/aios_active_mission_cycle.py",
            "AIOS_ACTIVE_MISSION_CYCLE.v1",
        ),
        "resume_state": section(
            "automation/orchestration/aios_resume_state.py",
            "AIOS_RESUME_STATE.v1",
        ),
        "worker_state": section(
            "schemas/aios/orchestration/WORKER_REGISTRY_SCHEMA.json",
            "WORKER_REGISTRY_SCHEMA",
        ),
        "system_health": "PASS",
        "system_readiness": "READY",
        "risk_level": "LOW",
        "blocked_actions": ["APPLY", "git add", "git commit", "git push"],
        "next_safe_action": "Review source evidence before any protected action.",
    }


def fallback_validate(instance: dict[str, Any]) -> None:
    schema = load_schema()
    for key in schema["required"]:
        assert key in instance, f"missing top-level field: {key}"
    assert instance["schema"] == "AIOS_DASHBOARD_STATE_CONTRACT.v1"
    assert instance["mode"] == "DISPLAY_ONLY_READ_MODEL"
    assert instance["authority_boundary"]["read_only"] is True
    assert instance["authority_boundary"]["evidence_only"] is True
    for flag in AUTHORITY_FALSE_FLAGS:
        assert instance["authority_boundary"][flag] is False, flag

    for name in STATE_SECTIONS:
        state = instance[name]
        for field in (
            "display_state",
            "authority_state",
            "source_path",
            "source_schema",
            "freshness",
            "summary",
            "items",
            "blocked_actions",
            "next_safe_action",
            "approval_required",
            "execution_allowed",
            "mutation_allowed",
            "safe_for_frontend_display",
        ):
            assert field in state, f"{name}.{field}"
        assert state["source_path"]
        assert state["source_schema"]
        assert state["execution_allowed"] is False
        assert state["mutation_allowed"] is False
        evidence_state = state.get("evidence_state") or state["freshness"].get("evidence_state")
        if evidence_state in FAIL_CLOSED_EVIDENCE_STATES:
            assert state["display_state"] in FAIL_CLOSED_DISPLAY_STATES
            assert state["approval_required"] is True


def validate_contract(instance: dict[str, Any]) -> None:
    schema = load_schema()
    if Draft202012Validator is not None:
        Draft202012Validator(schema).validate(instance)
    else:
        fallback_validate(instance)


def expect_invalid(instance: dict[str, Any]) -> None:
    with pytest.raises(Exception):
        validate_contract(instance)


def test_loads_and_validates_dashboard_schema() -> None:
    schema = load_schema()
    assert schema["$id"].endswith("AIOS_DASHBOARD_STATE_CONTRACT.v1.schema.json")
    assert schema["properties"]["mode"]["const"] == "DISPLAY_ONLY_READ_MODEL"
    if Draft202012Validator is not None:
        Draft202012Validator.check_schema(schema)


def test_validates_minimal_full_contract_fixture() -> None:
    validate_contract(minimal_contract())


def test_authority_flags_are_fail_closed_read_only() -> None:
    fixture = minimal_contract()
    assert fixture["authority_boundary"]["read_only"] is True
    assert fixture["authority_boundary"]["evidence_only"] is True
    for flag in AUTHORITY_FALSE_FLAGS:
        assert fixture["authority_boundary"][flag] is False
    validate_contract(fixture)


@pytest.mark.parametrize("field", ["source_path", "source_schema", "freshness"])
def test_rejects_missing_source_fields_in_state_sections(field: str) -> None:
    fixture = minimal_contract()
    del fixture["system_state"][field]
    expect_invalid(fixture)


def test_rejects_mutation_allowed_true() -> None:
    fixture = minimal_contract()
    fixture["system_state"]["mutation_allowed"] = True
    expect_invalid(fixture)


def test_rejects_execution_allowed_true() -> None:
    fixture = minimal_contract()
    fixture["system_state"]["execution_allowed"] = True
    expect_invalid(fixture)


def test_m1_m2_m3_backed_sections_are_required() -> None:
    schema = load_schema()
    for field in ("security_state", "continuation_state", "watchtower_state"):
        assert field in schema["required"]
        fixture = minimal_contract()
        del fixture[field]
        expect_invalid(fixture)


def test_unknown_missing_evidence_requires_fail_closed_display_state() -> None:
    fixture = minimal_contract()
    fixture["validator_state"]["evidence_state"] = "MISSING"
    fixture["validator_state"]["freshness"] = freshness("MISSING", is_stale=True)
    fixture["validator_state"]["display_state"] = "NEEDS_REVIEW"
    fixture["validator_state"]["approval_required"] = True
    validate_contract(fixture)

    unsafe = deepcopy(fixture)
    unsafe["validator_state"]["display_state"] = "READY"
    expect_invalid(unsafe)


def test_contract_grants_no_control_broker_live_scheduler_daemon_worker_approval_or_button_authority() -> None:
    fixture = minimal_contract()
    boundary = fixture["authority_boundary"]
    for flag in AUTHORITY_FALSE_FLAGS:
        assert boundary[flag] is False

    for name in STATE_SECTIONS:
        assert fixture[name]["execution_allowed"] is False
        assert fixture[name]["mutation_allowed"] is False

    validate_contract(fixture)
