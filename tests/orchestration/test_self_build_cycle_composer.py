"""Tests for the self-build cycle composer (observe-only, dependency-injected)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPOSER = (
    REPO_ROOT / "automation" / "orchestration" / "autonomy_control_plane"
    / "aios_self_build_cycle_composer.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("aios_self_build_cycle_composer", COMPOSER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# ---- stub dependencies (canned, deterministic) ----
def stub_classify(goals):
    return lambda inventory: {"goals": goals, "candidate_count": len(goals)}


def stub_completion(verdict):
    return lambda *a, **k: {"verdict": verdict, "reasons": [] if verdict == "COMPLETION_VERIFIED" else ["x"]}


def stub_runtime(gate, status="PASS"):
    return lambda *a, **k: {"runtime_gate": gate, "control_plane": {"status": status}}


def stub_decider():
    # a faithful mini-decider that mirrors #516 priority for the tests
    def _d(completion, runtime, candidates):
        v = completion.get("verdict") if isinstance(completion, dict) else completion
        g = runtime.get("runtime_gate") if isinstance(runtime, dict) else runtime
        goals = (candidates or {}).get("goals", []) if isinstance(candidates, dict) else (candidates or [])
        if g == "BLOCKED":
            return {"action": "HOLD_BLOCKED", "requires_human": True, "mode": "DRY_RUN", "blocked_reason": "runtime_blocked"}
        if v == "COMPLETION_CONTRADICTED":
            return {"action": "FIX_TRUST_FAILURE", "requires_human": True, "mode": "DRY_RUN", "blocked_reason": "completion_contradicted"}
        if v == "COMPLETION_VERIFIED":
            return {"action": "READY_FOR_HUMAN_MERGE_REVIEW", "requires_human": True, "mode": "DRY_RUN"}
        if goals:
            prot = bool(goals[0].get("protected_action_expected"))
            return {"action": "PROPOSE_NEXT_GOAL", "requires_human": prot, "mode": "DRY_RUN"}
        return {"action": "NO_ACTION", "requires_human": False, "mode": "DRY_RUN"}
    return _d


SAFE_GOAL = {"goal_id": "g1", "urgency": "MEDIUM", "protected_action_expected": False}
PROT_GOAL = {"goal_id": "sos", "urgency": "HIGH", "protected_action_expected": True}


def _run(m, *, goals, verdict, gate, completion_inputs={"evidence_text": "passed"}):
    return m.decide_self_build_cycle(
        {"missing_components": ["x"]}, {"status": "PASS"}, {"next_action": "OPEN_PR"}, completion_inputs,
        classify_gaps=stub_classify(goals),
        evaluate_completion=stub_completion(verdict),
        build_runtime_view=stub_runtime(gate),
        decide_next_action=stub_decider(),
        now="2026-01-01T00:00:00Z",
    )


def _invariants(res):
    assert res["mode"] == "DRY_RUN"
    assert res["executed"] is False
    assert res["cycle_id"].startswith("sbc-")
    blob = " ".join(str(v) for v in res["decision"].values()).lower()
    for bad in ("git push", "git merge", "--apply", "place_order", "broker", "live_order"):
        assert bad not in blob


def test_happy_path_verified_completion():
    m = _load()
    res = _run(m, goals=[SAFE_GOAL], verdict="COMPLETION_VERIFIED", gate="READY_TO_REPORT")
    _invariants(res)
    assert res["decision"]["action"] == "READY_FOR_HUMAN_MERGE_REVIEW"
    assert res["safety_status"] == "HUMAN_REQUIRED"  # merge is protected
    assert res["requires_human"] is True


def test_no_gaps_and_unproven_is_no_action():
    m = _load()
    res = _run(m, goals=[], verdict="NOT_EVALUATED", gate="READY_TO_REPORT")
    _invariants(res)
    assert res["decision"]["action"] == "NO_ACTION"
    assert res["safety_status"] == "SAFE"
    assert res["requires_human"] is False


def test_unsafe_gap_requires_human():
    m = _load()
    res = _run(m, goals=[PROT_GOAL], verdict="NOT_EVALUATED", gate="READY_TO_REPORT")
    _invariants(res)
    assert res["decision"]["action"] == "PROPOSE_NEXT_GOAL"
    assert res["safety_status"] == "HUMAN_REQUIRED"
    assert res["requires_human"] is True


def test_missing_completion_proof_degrades_to_not_evaluated():
    m = _load()
    res = m.decide_self_build_cycle(
        {"missing_components": ["x"]}, {"status": "PASS"}, {"next_action": "OPEN_PR"},
        None,  # no completion inputs
        classify_gaps=stub_classify([SAFE_GOAL]),
        evaluate_completion=stub_completion("COMPLETION_VERIFIED"),  # should NOT be called
        build_runtime_view=stub_runtime("READY_TO_REPORT"),
        decide_next_action=stub_decider(),
        now="2026-01-01T00:00:00Z",
    )
    _invariants(res)
    assert res["evidence_bundle"]["completion"]["verdict"] == "NOT_EVALUATED"
    assert res["decision"]["action"] == "PROPOSE_NEXT_GOAL"


def test_failed_completion_proof_is_blocked_trust_failure():
    m = _load()
    res = _run(m, goals=[SAFE_GOAL], verdict="COMPLETION_CONTRADICTED", gate="READY_TO_REPORT")
    _invariants(res)
    assert res["decision"]["action"] == "FIX_TRUST_FAILURE"
    assert res["safety_status"] == "BLOCKED"
    assert res["blocked_reason"] == "completion_contradicted"


def test_runtime_blocked_holds():
    m = _load()
    res = _run(m, goals=[SAFE_GOAL], verdict="COMPLETION_VERIFIED", gate="BLOCKED")
    _invariants(res)
    assert res["decision"]["action"] == "HOLD_BLOCKED"
    assert res["safety_status"] == "BLOCKED"


def test_malformed_input_fails_closed():
    m = _load()
    # decider returns a malformed decision (no "action") -> composer must fail closed
    res = m.decide_self_build_cycle(
        {}, {}, {}, {},
        classify_gaps=stub_classify([]),
        evaluate_completion=stub_completion("NOT_EVALUATED"),
        build_runtime_view=stub_runtime("READY_TO_REPORT"),
        decide_next_action=lambda *a, **k: {"not_an_action": True},
        now="2026-01-01T00:00:00Z",
    )
    assert res["safety_status"] == "BLOCKED"
    assert res["requires_human"] is True
    assert res["decision"]["action"] == "BLOCKED_MALFORMED_INPUT"


def test_contradictory_input_blocked_wins_over_verified():
    m = _load()
    # completion says VERIFIED but runtime says BLOCKED -> BLOCKED must win
    res = _run(m, goals=[SAFE_GOAL], verdict="COMPLETION_VERIFIED", gate="BLOCKED")
    _invariants(res)
    assert res["decision"]["action"] == "HOLD_BLOCKED"
    assert res["safety_status"] == "BLOCKED"


def test_sub_module_exception_fails_closed():
    m = _load()
    def boom(*a, **k):
        raise RuntimeError("kaboom")
    res = m.decide_self_build_cycle(
        {"missing_components": ["x"]}, {"status": "PASS"}, {"next_action": "OPEN_PR"}, {"evidence_text": "p"},
        classify_gaps=stub_classify([SAFE_GOAL]),
        evaluate_completion=stub_completion("COMPLETION_VERIFIED"),
        build_runtime_view=stub_runtime("READY_TO_REPORT"),
        decide_next_action=boom,  # decider raises
        now="2026-01-01T00:00:00Z",
    )
    assert res["safety_status"] == "BLOCKED"
    assert res["requires_human"] is True


def test_evidence_bundle_shape():
    m = _load()
    res = _run(m, goals=[SAFE_GOAL], verdict="COMPLETION_VERIFIED", gate="READY_TO_REPORT")
    eb = res["evidence_bundle"]
    assert set(eb.keys()) == {"gap_candidates", "completion", "runtime", "decision"}
    assert eb["gap_candidates"]["candidate_count"] == 1
    assert eb["gap_candidates"]["goal_ids"] == ["g1"]
    assert eb["completion"]["verdict"] == "COMPLETION_VERIFIED"
    assert eb["runtime"]["runtime_gate"] == "READY_TO_REPORT"
    assert eb["decision"]["action"] == "READY_FOR_HUMAN_MERGE_REVIEW"
    # source modules listed with availability flags
    mods = {s["module"]: s["available"] for s in res["source_modules"]}
    assert set(mods.keys()) == {
        "gap_to_goal_classifier", "completion_evidence_validator",
        "control_plane_runtime_connector", "next_action_decider",
    }


def test_deterministic_cycle_id_for_same_inputs():
    m = _load()
    a = _run(m, goals=[SAFE_GOAL], verdict="COMPLETION_VERIFIED", gate="READY_TO_REPORT")
    b = _run(m, goals=[SAFE_GOAL], verdict="COMPLETION_VERIFIED", gate="READY_TO_REPORT")
    assert a["cycle_id"] == b["cycle_id"]
