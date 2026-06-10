"""Tests for the packet completeness / promotion review (observe-only)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REVIEW = (
    REPO_ROOT / "automation" / "orchestration" / "autonomy_review"
    / "aios_packet_completeness_review.py"
)
DRAFTER = (
    REPO_ROOT / "automation" / "orchestration" / "autonomy_router"
    / "aios_decision_to_packet_drafter.py"
)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _review():
    return _load("aios_packet_completeness_review", REVIEW)


def _real_scoped_draft():
    drf = _load("aios_decision_to_packet_drafter", DRAFTER)
    goal = {"objective": "Close autonomy gap: build the schema reconciliation validator",
            "target_area": "automation/validators", "urgency": "MEDIUM"}
    return drf.build_packet_draft(goal, allowed_paths=["automation/validators/", "tests/orchestration/"])


def test_real_scoped_draft_is_ready_for_human_review():
    m = _review()
    draft = _real_scoped_draft()
    res = m.review_packet_completeness(draft["draft_text"], path_status=draft["path_status"])
    assert res["verdict"] == "READY_FOR_HUMAN_REVIEW"
    assert res["promotion_ready"] is True
    assert res["requires_human"] is True
    assert res["approves_protected_action"] is False


def test_unscoped_draft_is_incomplete():
    m = _review()
    drf = _load("aios_decision_to_packet_drafter", DRAFTER)
    draft = drf.build_packet_draft({"objective": "Close gap: x", "target_area": "automation/x"})
    res = m.review_packet_completeness(draft["draft_text"], path_status=draft["path_status"])
    assert res["verdict"] == "INCOMPLETE"
    assert "PCR-005-PATHS-SCOPED" in res["failed_checks"]


def test_missing_sections_is_incomplete():
    m = _review()
    res = m.review_packet_completeness("CODEX-ONLY PROMPT\nMISSION:\njust a stub\n")
    assert res["verdict"] == "INCOMPLETE"
    assert "PCR-004-READINESS-MARKERS" in res["failed_checks"]


def test_hazard_block_is_promotion_blocked():
    m = _review()
    # inject a real governance BLOCK hazard (live trading) into an otherwise-shaped draft
    draft = _real_scoped_draft()["draft_text"] + "\nEXTRA: enable live trading now\n"
    res = m.review_packet_completeness(draft)
    assert res["verdict"] == "PROMOTION_BLOCKED"
    assert res["promotion_ready"] is False


def test_injected_validator_is_used():
    m = _review()
    calls = {}

    def fake_validate(text, path):
        calls["used"] = True
        return {"status": "PASS", "errors": [], "warnings": []}

    draft = _real_scoped_draft()
    res = m.review_packet_completeness(draft["draft_text"], path_status="SCOPED", validate=fake_validate)
    assert calls.get("used") is True
    assert res["verdict"] == "READY_FOR_HUMAN_REVIEW"


def test_never_approves_protected_action():
    m = _review()
    draft = _real_scoped_draft()
    res = m.review_packet_completeness(draft["draft_text"], path_status="SCOPED")
    assert res["approves_protected_action"] is False
    assert res["requires_human"] is True
