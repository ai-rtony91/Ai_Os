"""AI_OS next-action decider (observe-only self-build router logic).

Turns three signals into EXACTLY ONE safe next action:
  * completion validator verdict   (#512 aios_completion_evidence_validator)
  * control-plane runtime status   (#514 control_plane_runtime_connector runtime_gate)
  * gap -> goal candidates         (#515 gap_to_goal_classifier)

Safety posture:
  * Emits ACTION LABELS, never shell commands. No apply/merge/live/broker/secret
    command can leak because none is ever produced.
  * Any protected or risky situation returns requires_human True.
  * mode is always DRY_RUN. It executes nothing, runs no worker, runs no packet.
  * Malformed input fails closed to BLOCKED_MALFORMED_INPUT, not to an action.

Pure standard library. Observe-only. No mutation. No network.
"""

from __future__ import annotations

from typing import Any, Optional


# The only actions this decider may ever return. None of these are commands.
ALLOWED_ACTIONS = {
    "HOLD_BLOCKED",
    "FIX_TRUST_FAILURE",
    "REQUEST_HUMAN_APPROVAL",
    "READY_FOR_HUMAN_MERGE_REVIEW",
    "PROPOSE_NEXT_GOAL",
    "NO_ACTION",
    "BLOCKED_MALFORMED_INPUT",
}

VALID_VERDICTS = {
    "COMPLETION_VERIFIED", "COMPLETION_UNPROVEN", "COMPLETION_CONTRADICTED",
    "NOT_EVALUATED", "TRUST_GATE_UNAVAILABLE",
}
VALID_GATES = {"READY_TO_REPORT", "HUMAN_REQUIRED", "TRUST_FAILED", "BLOCKED", "UNKNOWN"}
_URGENCY_RANK = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def _extract_verdict(completion: Any) -> Optional[str]:
    if completion is None:
        return "NOT_EVALUATED"
    if isinstance(completion, str):
        return completion
    if isinstance(completion, dict):
        v = completion.get("verdict")
        if v is None and isinstance(completion.get("trust_gate_completion"), dict):
            v = completion["trust_gate_completion"].get("verdict")
        return v if isinstance(v, str) else None
    return None  # wrong type -> malformed signal


def _extract_gate(runtime: Any) -> Optional[str]:
    if runtime is None:
        return "UNKNOWN"
    if isinstance(runtime, str):
        return runtime
    if isinstance(runtime, dict):
        g = runtime.get("runtime_gate")
        return g if isinstance(g, str) else None
    return None


def _extract_goals(candidates: Any) -> Optional[list]:
    if candidates is None:
        return []
    if isinstance(candidates, list):
        return candidates
    if isinstance(candidates, dict):
        g = candidates.get("goals")
        return g if isinstance(g, list) else []
    return None  # wrong type -> malformed signal


def _pick_top_goal(goals: list) -> Optional[dict]:
    valid = [g for g in goals if isinstance(g, dict)]
    if not valid:
        return None
    return sorted(
        valid,
        key=lambda g: (_URGENCY_RANK.get(str(g.get("urgency", "LOW")).upper(), 3), str(g.get("goal_id", ""))),
    )[0]


def _result(action: str, reason: str, confidence: float, requires_human: bool,
            signals: dict, blocked_reason: Optional[str] = None) -> dict[str, object]:
    assert action in ALLOWED_ACTIONS, f"illegal action {action}"  # safety invariant
    out: dict[str, object] = {
        "action": action,
        "reason": reason,
        "confidence": round(float(confidence), 2),
        "requires_human": bool(requires_human),
        "mode": "DRY_RUN",
        "source_signals": signals,
        "executed": False,
    }
    if blocked_reason is not None:
        out["blocked_reason"] = blocked_reason
    return out


def decide_next_action(completion: Any, runtime: Any, candidates: Any) -> dict[str, object]:
    verdict = _extract_verdict(completion)
    gate = _extract_gate(runtime)
    goals = _extract_goals(candidates)

    # 0. Malformed input -> fail closed.
    if verdict is None or gate is None or goals is None:
        return _result(
            "BLOCKED_MALFORMED_INPUT",
            "One or more signals were the wrong type and could not be read.",
            0.95, True,
            {"completion_verdict": None, "runtime_gate": None, "candidate_count": None},
            blocked_reason="malformed_input",
        )

    top = _pick_top_goal(goals)
    signals = {
        "completion_verdict": verdict,
        "runtime_gate": gate,
        "candidate_count": len(goals),
        "top_candidate_id": (top or {}).get("goal_id"),
    }

    # 1. Runtime control plane blocked -> hold.
    if gate == "BLOCKED":
        return _result("HOLD_BLOCKED", "Control-plane runtime gate is BLOCKED.", 0.95, True,
                       signals, blocked_reason="runtime_blocked")

    # 2. Trust failure -> fix, never proceed.
    if verdict == "COMPLETION_CONTRADICTED" or gate == "TRUST_FAILED":
        return _result("FIX_TRUST_FAILURE",
                       "Completion evidence contradicts the claim; do not treat as done.",
                       0.95, True, signals, blocked_reason="completion_contradicted")

    # 3. Runtime requires a human (protected/live flagged by the connector).
    if gate == "HUMAN_REQUIRED":
        return _result("REQUEST_HUMAN_APPROVAL", "Runtime gate requires Human Owner approval.",
                       0.9, True, signals, blocked_reason="runtime_requires_human")

    # 4. Verified completion -> surface for human merge review (merge is protected).
    if verdict == "COMPLETION_VERIFIED":
        return _result("READY_FOR_HUMAN_MERGE_REVIEW",
                       "Work is evidence-verified; surface to Human Owner for the merge decision.",
                       0.9, True, signals, blocked_reason="merge_is_protected")

    # 5. Not-yet-proven completion -> propose the next goal candidate (or idle).
    if verdict in {"COMPLETION_UNPROVEN", "NOT_EVALUATED", "TRUST_GATE_UNAVAILABLE"}:
        if top is None:
            return _result("NO_ACTION", "No goal candidates and nothing verified to surface; idle.",
                           0.6, False, signals)
        protected = bool(top.get("protected_action_expected"))
        if protected:
            return _result("PROPOSE_NEXT_GOAL",
                           "Top gap candidate is a protected action; propose it but require human approval.",
                           0.7, True, signals, blocked_reason="top_candidate_protected")
        return _result("PROPOSE_NEXT_GOAL",
                       "Propose the highest-priority safe gap candidate as a DRY_RUN goal.",
                       0.7, False, signals)

    # 6. Unknown but well-typed values -> fail safe to human.
    return _result("REQUEST_HUMAN_APPROVAL",
                   "Signals are unrecognized; defaulting to Human Owner review (fail-safe).",
                   0.4, True, signals, blocked_reason="unrecognized_signals")
