from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE = REPO_ROOT / "automation" / "security" / "aios_preemptive_security_layer.py"


def _load():
    spec = importlib.util.spec_from_file_location("aios_preemptive_security_layer", MODULE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _event_categories(state: dict) -> set[str]:
    return {event["category"] for event in state["events"]}


def test_clear_state_has_green_hud_and_allows_apply() -> None:
    m = _load()

    state = m.build_security_state(repo_root=REPO_ROOT, dirty_tree={"files": []}, generated_utc="2026-06-16T00:00:00Z")

    assert state["schema"] == "AIOS_PREEMPTIVE_SECURITY_STATE.v1"
    assert state["overall_state"] == "CLEAR"
    assert state["shield_state"] == "GREEN"
    assert state["vault_lock_state"] == "LOCKED"
    assert state["safe_for_dry_run"] is True
    assert state["safe_for_apply"] is True
    assert state["sos_required"] is False
    assert state["events"] == []
    assert state["safety"]["read_only"] is True
    assert state["safety"]["writes_reports_by_default"] is False


def test_secret_assignment_becomes_sos_without_value_echo() -> None:
    m = _load()
    key_name = "API" + "_" + "KEY"
    value = "do-not-echo-value"

    state = m.build_security_state(
        repo_root=REPO_ROOT,
        evidence_items=[{"path": "scratch/example.txt", "content": f"{key_name}={value}"}],
        generated_utc="2026-06-16T00:00:00Z",
    )
    dumped = json.dumps(state, sort_keys=True)

    assert state["overall_state"] == "SOS"
    assert state["sos_required"] is True
    assert "SECRET_EXPOSURE_RISK" in _event_categories(state)
    assert value not in dumped
    for event in state["events"]:
        assert event["matched_values_printed"] is False
        assert event["values_redacted"] is True


def test_generated_report_broker_safety_mentions_are_watch_not_sos() -> None:
    m = _load()
    dirty_tree = {
        "files": [
            {
                "path": "Reports/aios_resume/safety_report.json",
                "classification": "SECURITY_SOS_DIRTY",
                "reason": "Generated report mentions broker and live trading risk as blocked safety context.",
                "security_indicators": ["broker_oanda_live_trading"],
                "status": "??",
            }
        ]
    }

    state = m.build_security_state(repo_root=REPO_ROOT, dirty_tree=dirty_tree, generated_utc="2026-06-16T00:00:00Z")

    assert state["overall_state"] == "WATCH"
    assert state["safe_for_dry_run"] is True
    assert state["safe_for_apply"] is False
    assert state["sos_required"] is False
    assert state["stop_required"] is False
    assert all(event["severity"] == "WATCH" for event in state["events"])


def test_broker_enablement_text_is_sos() -> None:
    m = _load()

    state = m.build_security_state(
        repo_root=REPO_ROOT,
        evidence_items=[{"path": "automation/runtime/example.txt", "content": "enable broker execution"}],
        generated_utc="2026-06-16T00:00:00Z",
    )

    assert state["overall_state"] == "SOS"
    assert state["safe_for_dry_run"] is False
    assert state["safe_for_apply"] is False
    assert "BROKER_AUTHORITY_RISK" in _event_categories(state)


def test_protected_action_categories_stop_or_sos() -> None:
    m = _load()
    cases = [
        ("external webhook send", "WEBHOOK_RISK", "STOP"),
        ("deploy production now", "PRODUCTION_DEPLOY_RISK", "STOP"),
        ("dashboard mutation write", "DASHBOARD_MUTATION_RISK", "STOP"),
        ("start scheduler daemon", "SCHEDULER_DAEMON_RISK", "STOP"),
        ("launch worker", "WORKER_LAUNCH_RISK", "STOP"),
        ("place real order", "REAL_ORDER_RISK", "SOS"),
    ]

    for content, category, expected_state in cases:
        state = m.build_security_state(
            repo_root=REPO_ROOT,
            evidence_items=[{"path": "automation/runtime/example.txt", "content": content}],
            generated_utc="2026-06-16T00:00:00Z",
        )
        assert category in _event_categories(state)
        assert state["overall_state"] == expected_state
        assert "APPLY" in state["blocked_actions"]


def test_canary_trip_creates_boss_alert() -> None:
    m = _load()

    state = m.build_security_state(
        repo_root=REPO_ROOT,
        evidence_items=[{"path": "scratch/example.txt", "content": "AIOS_CANARY touched"}],
        generated_utc="2026-06-16T00:00:00Z",
    )

    assert state["overall_state"] == "SOS"
    assert state["boss_alert"]["active"] is True
    assert state["tripwire_events"]
    assert "CANARY_TRIP" in _event_categories(state)


def test_dirty_tree_unknown_requires_review() -> None:
    m = _load()
    dirty_tree = {
        "files": [
            {
                "path": "scratch/unknown.tmp",
                "classification": "UNKNOWN_DIRTY",
                "reason": "unclassified file",
                "status": "??",
            }
        ]
    }

    state = m.build_security_state(repo_root=REPO_ROOT, dirty_tree=dirty_tree, generated_utc="2026-06-16T00:00:00Z")

    assert state["overall_state"] == "REVIEW_REQUIRED"
    assert state["review_required"] is True
    assert state["safe_for_dry_run"] is False
    assert state["safe_for_apply"] is False
    assert "UNKNOWN_SECURITY_RISK" in _event_categories(state)


def test_dirty_tree_native_dirty_files_field_is_consumed() -> None:
    m = _load()
    dirty_tree = {
        "dirty_files": [
            {
                "path": "scratch/native.tmp",
                "classification": "UNKNOWN_DIRTY",
                "reason": "native classifier payload",
                "git_code": "??",
            }
        ]
    }

    state = m.build_security_state(repo_root=REPO_ROOT, dirty_tree=dirty_tree, generated_utc="2026-06-16T00:00:00Z")

    assert state["overall_state"] == "REVIEW_REQUIRED"
    assert state["event_count"] == 1
    assert state["events"][0]["source_path"] == "scratch/native.tmp"


def test_hud_contract_fields_present() -> None:
    m = _load()

    state = m.build_security_state(repo_root=REPO_ROOT, dirty_tree={"files": []}, generated_utc="2026-06-16T00:00:00Z")

    for field in (
        "shield_state",
        "vault_lock_state",
        "radar_events",
        "tripwire_events",
        "boss_alert",
        "blocked_actions",
        "next_safe_action",
    ):
        assert field in state
    assert state["safety"]["broker_access"] is False
    assert state["safety"]["live_trading"] is False
    assert state["safety"]["production_mutation"] is False
    assert state["safety"]["dashboard_mutation"] is False
    assert state["safety"]["worker_launch"] is False
