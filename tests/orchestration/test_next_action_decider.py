"""Tests for the next-action decider (observe-only self-build router logic)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DECIDER = (
    REPO_ROOT / "automation" / "orchestration" / "autonomy_router"
    / "aios_next_action_decider.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("aios_next_action_decider", DECIDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SAFE_GOAL = {"goal_id": "goal-a", "urgency": "MEDIUM", "protected_action_expected": False}
PROT_GOAL = {"goal_id": "goal-sos", "urgency": "HIGH", "protected_action_expected": True}


def _common(res):
    # invariants that must hold for EVERY decision
    m = _load()
    assert res["action"] in m.ALLOWED_ACTIONS
    assert res["mode"] == "DRY_RUN"
    assert res["executed"] is False
    # no command/shell string ever emitted
    blob = " ".join(str(v) for v in res.values()).lower()
    for bad in ("git push", "git merge", "gh pr merge", "--apply", "place_order", "broker"):
        assert bad not in blob


def test_safe_action_proposes_safe_candidate():
    m = _load()
    res = m.decide_next_action("COMPLETION_UNPROVEN", "READY_TO_REPORT", {"goals": [SAFE_GOAL]})
    _common(res)
    assert res["action"] == "PROPOSE_NEXT_GOAL"
    assert res["requires_human"] is False
    assert res["source_signals"]["top_candidate_id"] == "goal-a"


def test_blocked_action_when_runtime_blocked():
    m = _load()
    res = m.decide_next_action("COMPLETION_VERIFIED", "BLOCKED", {"goals": [SAFE_GOAL]})
    _common(res)
    assert res["action"] == "HOLD_BLOCKED"
    assert res["requires_human"] is True
    assert res["blocked_reason"] == "runtime_blocked"


def test_missing_evidence_with_candidate_proposes_goal():
    m = _load()
    res = m.decide_next_action("NOT_EVALUATED", "READY_TO_REPORT", {"goals": [SAFE_GOAL]})
    _common(res)
    assert res["action"] == "PROPOSE_NEXT_GOAL"


def test_multiple_candidates_picks_highest_priority_deterministically():
    m = _load()
    goals = [SAFE_GOAL, PROT_GOAL, {"goal_id": "goal-z", "urgency": "MEDIUM", "protected_action_expected": False}]
    res = m.decide_next_action("COMPLETION_UNPROVEN", "READY_TO_REPORT", {"goals": goals})
    _common(res)
    # HIGH urgency PROT_GOAL wins -> protected -> requires human
    assert res["source_signals"]["top_candidate_id"] == "goal-sos"
    assert res["requires_human"] is True
    assert res["blocked_reason"] == "top_candidate_protected"


def test_no_candidates_yields_no_action():
    m = _load()
    res = m.decide_next_action("COMPLETION_UNPROVEN", "READY_TO_REPORT", {"goals": []})
    _common(res)
    assert res["action"] == "NO_ACTION"
    assert res["requires_human"] is False


def test_failed_completion_verdict_is_trust_failure():
    m = _load()
    res = m.decide_next_action("COMPLETION_CONTRADICTED", "READY_TO_REPORT", {"goals": [SAFE_GOAL]})
    _common(res)
    assert res["action"] == "FIX_TRUST_FAILURE"
    assert res["requires_human"] is True
    assert res["blocked_reason"] == "completion_contradicted"


def test_runtime_human_required_requests_approval():
    m = _load()
    res = m.decide_next_action("COMPLETION_UNPROVEN", "HUMAN_REQUIRED", {"goals": [SAFE_GOAL]})
    _common(res)
    assert res["action"] == "REQUEST_HUMAN_APPROVAL"
    assert res["requires_human"] is True


def test_verified_completion_is_human_merge_review():
    m = _load()
    res = m.decide_next_action("COMPLETION_VERIFIED", "READY_TO_REPORT", {"goals": []})
    _common(res)
    assert res["action"] == "READY_FOR_HUMAN_MERGE_REVIEW"
    assert res["requires_human"] is True  # merge is protected


def test_malformed_input_fails_closed():
    m = _load()
    # candidates is an int (wrong type)
    res = m.decide_next_action("COMPLETION_UNPROVEN", "READY_TO_REPORT", 42)
    _common(res)
    assert res["action"] == "BLOCKED_MALFORMED_INPUT"
    assert res["requires_human"] is True
    assert res["blocked_reason"] == "malformed_input"


def test_accepts_real_connector_and_validator_dicts():
    m = _load()
    completion = {"verdict": "COMPLETION_VERIFIED"}
    runtime = {"runtime_gate": "READY_TO_REPORT"}
    candidates = {"goals": [SAFE_GOAL]}
    res = m.decide_next_action(completion, runtime, candidates)
    _common(res)
    assert res["action"] == "READY_FOR_HUMAN_MERGE_REVIEW"


def test_unrecognized_signals_fail_safe_to_human():
    m = _load()
    res = m.decide_next_action("WHATEVER", "SOMETHING", {"goals": []})
    _common(res)
    assert res["action"] == "REQUEST_HUMAN_APPROVAL"
    assert res["requires_human"] is True
