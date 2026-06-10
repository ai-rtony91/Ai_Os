"""Tests for the gap-to-goal classifier (self-build detect -> goal arrow, observe-only)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CLASSIFIER = (
    REPO_ROOT / "automation" / "orchestration" / "autonomy_discovery"
    / "aios_gap_to_goal_classifier.py"
)

GOAL_INTAKE_REQUIRED = [
    "goal_id", "created_at", "operator", "objective", "urgency", "target_area",
    "allowed_paths", "blocked_paths", "mode_requested", "worker_preference",
    "approval_required", "protected_action_expected", "notes",
]


def _load():
    spec = importlib.util.spec_from_file_location("aios_gap_to_goal_classifier", CLASSIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


INVENTORY = {
    "missing_components": ["completion evidence validator", "gap to goal feeder"],
    "known_blockers": ["scheduler autostart not registered", "SOS live channel still blocked"],
}


def test_empty_inventory_yields_no_goals():
    m = _load()
    res = m.classify_gaps_to_goals({})
    assert res["candidate_count"] == 0
    assert res["goals"] == []
    assert res["observe_only"] is True


def test_blockers_are_high_missing_are_medium():
    m = _load()
    res = m.classify_gaps_to_goals(INVENTORY)
    urg = {g["source_gap"]: g["urgency"] for g in res["goals"]}
    assert urg["scheduler autostart not registered"] == "HIGH"
    assert urg["SOS live channel still blocked"] == "HIGH"
    assert urg["completion evidence validator"] == "MEDIUM"


def test_every_goal_is_a_safe_candidate():
    m = _load()
    res = m.classify_gaps_to_goals(INVENTORY)
    assert res["summary"]["any_auto_executable"] is False
    for g in res["goals"]:
        assert g["candidate_status"] == "NEEDS_OPERATOR_CONFIRMATION"
        assert g["approval_required"] is True
        assert g["mode_requested"] == "DRY_RUN"
        assert g["auto_executable"] is False
        assert g["allowed_paths"] == []  # never auto-scopes
        # full safety set always attached
        for blocked in ("broker", "secrets", "live_trading", ".env", "git push", "git merge"):
            assert blocked in g["blocked_paths"]


def test_protected_gaps_flagged_protected_action():
    m = _load()
    res = m.classify_gaps_to_goals(INVENTORY)
    prot = {g["source_gap"]: g["protected_action_expected"] for g in res["goals"]}
    assert prot["scheduler autostart not registered"] is True  # scheduler keyword
    assert prot["SOS live channel still blocked"] is True       # sos keyword


def test_goals_match_goal_intake_required_fields():
    m = _load()
    res = m.classify_gaps_to_goals(INVENTORY)
    for g in res["goals"]:
        for field in GOAL_INTAKE_REQUIRED:
            assert field in g, f"missing goal_intake field: {field}"


def test_python_shaped_gap_routes_to_west():
    m = _load()
    res = m.classify_gaps_to_goals({"missing_components": ["completion evidence validator"]})
    assert res["goals"][0]["worker_preference"] == "Claude Code West"


def test_dict_shaped_gap_with_area_and_evidence():
    m = _load()
    inv = {"known_blockers": [{"name": "dispatcher write path open", "area": "dispatch", "evidence": "0 runtime tables"}]}
    res = m.classify_gaps_to_goals(inv)
    g = res["goals"][0]
    assert g["target_area"] == "dispatch"
    assert "0 runtime tables" in g["notes"]
    assert g["protected_action_expected"] is True  # dispatch keyword


def test_duplicate_gaps_deduped():
    m = _load()
    inv = {"known_blockers": ["same gap"], "missing_components": ["same gap"]}
    res = m.classify_gaps_to_goals(inv)
    assert res["candidate_count"] == 1  # blocker wins, missing deduped


def test_deterministic_goal_id_for_same_gap():
    m = _load()
    a = m.classify_gaps_to_goals({"missing_components": ["completion evidence validator"]}, now="2026-01-01T00:00:00Z")
    b = m.classify_gaps_to_goals({"missing_components": ["completion evidence validator"]}, now="2026-01-01T00:00:00Z")
    assert a["goals"][0]["goal_id"] == b["goals"][0]["goal_id"]
