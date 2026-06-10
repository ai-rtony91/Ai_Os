"""AI_OS self-build cycle composer (observe-only).

Chains the four self-build brain modules into one decision + evidence bundle:
  #515 gap_to_goal_classifier        : inventory  -> goal candidates
  #512 completion_evidence_validator : claim      -> completion verdict (trust gate)
  #514 control_plane_runtime_connector: reports    -> runtime view / gate
  #516 next_action_decider           : the above  -> exactly one safe action

So a caller (e.g. the PowerShell control plane) invokes ONE function instead of
four. It executes nothing, runs no worker, runs no packet, and emits no command.

Safety posture:
  * Observe-only. mode is always DRY_RUN. executed is always False.
  * Fail closed: any malformed input, missing module, or sub-module exception
    yields a BLOCKED decision, never an action.
  * Protected/risky situations propagate requires_human True (the decider owns
    that; the composer never softens it).

Dependency-injected: the four module callables may be passed in (for tests); if
omitted, they are auto-loaded from their on-repo paths, and a missing module
degrades to a fail-closed signal.

Pure standard library. No mutation. No network.
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional


SCHEMA = "AIOS_SELF_BUILD_CYCLE.v1"

_MODULES = [
    ("gap_to_goal_classifier", "#515", "automation/orchestration/autonomy_discovery/aios_gap_to_goal_classifier.py", "classify_gaps_to_goals"),
    ("completion_evidence_validator", "#512", "automation/validators/aios_completion_evidence_validator.py", "evaluate_completion"),
    ("control_plane_runtime_connector", "#514", "automation/orchestration/autonomy_control_plane/aios_control_plane_runtime_connector.py", "build_runtime_view"),
    ("next_action_decider", "#516", "automation/orchestration/autonomy_router/aios_next_action_decider.py", "decide_next_action"),
]


def _toolchain_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_callable(relpath: str, func_name: str) -> Optional[Callable]:
    path = _toolchain_root() / relpath
    if not path.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location("aios_sbc_" + func_name, path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return getattr(module, func_name, None)
    except Exception:
        return None


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def decide_self_build_cycle(
    inventory: Any,
    control_plane_report: Any,
    router_report: Any,
    completion_inputs: Any,
    *,
    classify_gaps: Optional[Callable] = None,
    evaluate_completion: Optional[Callable] = None,
    build_runtime_view: Optional[Callable] = None,
    decide_next_action: Optional[Callable] = None,
    repo_root: Optional[Path] = None,
    now: Optional[str] = None,
    cycle_id: Optional[str] = None,
) -> dict[str, object]:
    now = now or _now()
    repo_root = Path(repo_root) if repo_root else _toolchain_root()

    # Resolve the four callables (injected or auto-loaded).
    classify_gaps = classify_gaps or _load_callable(_MODULES[0][2], _MODULES[0][3])
    evaluate_completion = evaluate_completion or _load_callable(_MODULES[1][2], _MODULES[1][3])
    build_runtime_view = build_runtime_view or _load_callable(_MODULES[2][2], _MODULES[2][3])
    decide_next_action = decide_next_action or _load_callable(_MODULES[3][2], _MODULES[3][3])

    availability = {
        "gap_to_goal_classifier": classify_gaps is not None,
        "completion_evidence_validator": evaluate_completion is not None,
        "control_plane_runtime_connector": build_runtime_view is not None,
        "next_action_decider": decide_next_action is not None,
    }
    source_modules = [
        {"module": name, "ref": ref, "available": availability[name]}
        for name, ref, _, _ in _MODULES
    ]

    if cycle_id is None:
        seed = repr(inventory) + repr(control_plane_report) + repr(router_report) + repr(completion_inputs) + now
        cycle_id = "sbc-" + hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]

    def _blocked(reason: str, decision_action: str = "BLOCKED_MALFORMED_INPUT") -> dict[str, object]:
        return {
            "schema": SCHEMA,
            "cycle_id": cycle_id,
            "generated_at": now,
            "mode": "DRY_RUN",
            "executed": False,
            "decision": {"action": decision_action, "requires_human": True, "mode": "DRY_RUN", "reason": reason},
            "evidence_bundle": evidence_bundle if "evidence_bundle" in locals() else {},
            "source_modules": source_modules,
            "safety_status": "BLOCKED",
            "requires_human": True,
            "blocked_reason": reason,
        }

    # The decider is mandatory; without it we cannot produce a safe action.
    if decide_next_action is None:
        return _blocked("next_action_decider (#516) unavailable", "HOLD_BLOCKED")

    # 1. gaps -> candidates (#515)  [non-fatal: degrade to no candidates]
    try:
        candidates = classify_gaps(inventory) if classify_gaps else {"goals": [], "candidate_count": 0}
    except Exception:
        candidates = {"goals": [], "candidate_count": 0, "error": "classifier_failed"}

    # 2. completion verdict (#512)  [missing inputs -> NOT_EVALUATED]
    completion: dict
    if not completion_inputs or not isinstance(completion_inputs, dict):
        completion = {"verdict": "NOT_EVALUATED", "reasons": []}
    elif evaluate_completion is None:
        completion = {"verdict": "TRUST_GATE_UNAVAILABLE", "reasons": ["completion validator unavailable"]}
    else:
        try:
            completion = evaluate_completion(
                completion_inputs.get("packet_text", ""),
                completion_inputs.get("changed_files", []),
                Path(completion_inputs.get("repo_root", repo_root)),
                completion_inputs.get("evidence_text"),
            )
        except Exception:
            completion = {"verdict": "COMPLETION_CONTRADICTED", "reasons": ["completion check raised"]}

    # 3. runtime view (#514)  [missing -> UNKNOWN gate -> decider fail-safe]
    if build_runtime_view is None:
        runtime = {"runtime_gate": "UNKNOWN", "control_plane": {"status": "UNKNOWN"}}
    else:
        try:
            runtime = build_runtime_view(control_plane_report, router_report, repo_root)
        except Exception:
            runtime = {"runtime_gate": "BLOCKED", "control_plane": {"status": "ERROR"}}

    # Build the evidence bundle (consistent shape).
    evidence_bundle = {
        "gap_candidates": {
            "candidate_count": int((candidates or {}).get("candidate_count", len((candidates or {}).get("goals", []) or []))),
            "goal_ids": [g.get("goal_id") for g in (candidates or {}).get("goals", []) or [] if isinstance(g, dict)],
        },
        "completion": {
            "verdict": completion.get("verdict"),
            "reasons": completion.get("reasons", []),
        },
        "runtime": {
            "runtime_gate": (runtime or {}).get("runtime_gate"),
            "control_plane_status": ((runtime or {}).get("control_plane", {}) or {}).get("status"),
        },
        "decision": None,  # filled below
    }

    # 4. decide one safe action (#516)
    try:
        decision = decide_next_action(completion, runtime, candidates)
    except Exception:
        return _blocked("next_action_decider raised", "BLOCKED_MALFORMED_INPUT")

    if not isinstance(decision, dict) or "action" not in decision:
        return _blocked("decider returned malformed decision", "BLOCKED_MALFORMED_INPUT")

    evidence_bundle["decision"] = decision

    action = decision.get("action")
    requires_human = bool(decision.get("requires_human", True))
    if action in {"HOLD_BLOCKED", "FIX_TRUST_FAILURE", "BLOCKED_MALFORMED_INPUT"}:
        safety_status = "BLOCKED"
        requires_human = True
    elif requires_human:
        safety_status = "HUMAN_REQUIRED"
    else:
        safety_status = "SAFE"

    result: dict[str, object] = {
        "schema": SCHEMA,
        "cycle_id": cycle_id,
        "generated_at": now,
        "mode": "DRY_RUN",
        "executed": False,
        "decision": decision,
        "evidence_bundle": evidence_bundle,
        "source_modules": source_modules,
        "safety_status": safety_status,
        "requires_human": requires_human,
    }
    if decision.get("blocked_reason"):
        result["blocked_reason"] = decision["blocked_reason"]
    return result
