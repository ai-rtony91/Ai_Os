"""Pure AIOS governed self-development soak classification logic.

The PowerShell runner gathers read-only cycle evidence. This module only
classifies that evidence, aggregates no-write proof, and returns a JSON-ready
result. It writes no files, starts no processes, and emits no executable
commands.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_GOVERNED_SELF_DEVELOPMENT_SOAK_RESULT.v1"
MODE = "DRY_RUN_READ_ONLY"
DEFAULT_CYCLES = 3
DEFAULT_MAX_CYCLES = 10
FINAL_VERIFICATION_PACKET = "AIOS-FINAL-VERIFICATION-CLOSURE-READONLY-V1"

GOVERNED_LOOP_SCHEMA = "AIOS_GOVERNED_SELF_DEVELOPMENT_LOOP_RESULT.v1"
APPROVAL_SOS_HARD_GATE_SCHEMA = "AIOS_APPROVAL_SOS_HARD_GATE_RESULT.v1"

UNSAFE_SAFETY_FLAGS = [
    "writes_files",
    "writes_reports",
    "writes_telemetry",
    "writes_packet_drafts",
    "writes_proposed_packets",
    "outputs_packet_body",
    "creates_ready_stage",
    "mutates_registry",
    "mutates_queue",
    "mutates_locks",
    "mutates_approvals",
    "writes_relay",
    "starts_runtime",
    "launches_workers",
    "scheduler_or_daemon",
    "protected_git_action",
    "protected_action_recommended",
    "secrets_or_env_access",
    "broker_or_live_trading",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return _safe_str(value).lower() in {"true", "1", "yes", "y"}


def _status(source: dict[str, Any]) -> str:
    safety = _as_dict(source.get("safety"))
    return _safe_str(safety.get("status") or source.get("status") or "UNKNOWN")


def _schema_ok(source: dict[str, Any], expected: str) -> bool:
    return _safe_str(source.get("schema")) == expected


def _unsafe_flags(source: dict[str, Any]) -> list[str]:
    safety = _as_dict(source.get("safety"))
    return [flag for flag in UNSAFE_SAFETY_FLAGS if _bool(safety.get(flag))]


def _int_value(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        key = _safe_str(item)
        if not key or key in seen:
            continue
        result.append(key)
        seen.add(key)
    return result


def _repo_stop_conditions(repo_state: dict[str, Any]) -> list[str]:
    stops: list[str] = []
    if repo_state and not _bool(repo_state.get("branch_matches_expected", True)):
        stops.append("BRANCH_MISMATCH")
    if (
        _bool(repo_state.get("dirty", False))
        and _bool(repo_state.get("fail_on_dirty_worktree", False))
        and not _bool(repo_state.get("dirty_allowed_for_soak_validation", False))
    ):
        stops.append("DIRTY_WORKTREE")
    return stops


def _no_write_stop_conditions(no_write_proof: dict[str, Any]) -> list[str]:
    if _bool(no_write_proof.get("changed", False)):
        return ["WRITE_SURFACE_RISK"]
    return []


def _cycle_forbidden_deltas(no_write_proof: dict[str, Any], cycle_index: int) -> list[dict[str, Any]]:
    deltas: list[dict[str, Any]] = []
    if _bool(no_write_proof.get("git_state_changed", False)):
        deltas.append({"cycle_index": cycle_index, "surface": "git_state", "delta": "changed"})
    if _bool(no_write_proof.get("forbidden_surface_changed", False)):
        deltas.append({"cycle_index": cycle_index, "surface": "forbidden_roots", "delta": "changed"})
    return deltas


def _cycle_stop_conditions(cycle: dict[str, Any]) -> list[str]:
    cycle_index = _int_value(cycle.get("cycle_index"), 0)
    prefix = f"CYCLE_{cycle_index}" if cycle_index > 0 else "CYCLE_UNKNOWN"
    governed_loop = _as_dict(cycle.get("governed_loop_result"))
    hard_gate = _as_dict(cycle.get("approval_sos_hard_gate_result"))
    no_write_proof = _as_dict(cycle.get("no_write_proof"))
    stops: list[str] = []

    if not _schema_ok(governed_loop, GOVERNED_LOOP_SCHEMA):
        stops.append(f"{prefix}_GOVERNED_LOOP_SCHEMA_INVALID")
    if _status(governed_loop) != "PASS":
        stops.append(f"{prefix}_GOVERNED_LOOP_NOT_PASS")
    for flag in _unsafe_flags(governed_loop):
        stops.append(f"{prefix}_GOVERNED_LOOP_UNSAFE_FLAG_{flag.upper()}")

    if not _schema_ok(hard_gate, APPROVAL_SOS_HARD_GATE_SCHEMA):
        stops.append(f"{prefix}_APPROVAL_SOS_HARD_GATE_SCHEMA_INVALID")
    if _status(hard_gate) != "PASS":
        stops.append(f"{prefix}_APPROVAL_SOS_HARD_GATE_NOT_PASS")
    for flag in _unsafe_flags(hard_gate):
        stops.append(f"{prefix}_APPROVAL_SOS_HARD_GATE_UNSAFE_FLAG_{flag.upper()}")

    for delta in _cycle_forbidden_deltas(no_write_proof, cycle_index):
        stops.append(f"{prefix}_FORBIDDEN_SURFACE_DELTA_{_safe_str(delta.get('surface')).upper()}")

    return stops


def _cycle_result(cycle: dict[str, Any]) -> dict[str, Any]:
    cycle_index = _int_value(cycle.get("cycle_index"), 0)
    governed_loop = _as_dict(cycle.get("governed_loop_result"))
    hard_gate = _as_dict(cycle.get("approval_sos_hard_gate_result"))
    no_write_proof = _as_dict(cycle.get("no_write_proof"))
    stop_conditions = _dedupe(_cycle_stop_conditions(cycle))
    status = "PASS" if not stop_conditions else "BLOCKED"
    if _bool(no_write_proof.get("changed", False)):
        status = "BLOCKED_BY_WRITE_SURFACE_RISK"

    return {
        "cycle_index": cycle_index,
        "status": status,
        "governed_loop_status": _status(governed_loop),
        "approval_sos_hard_gate_status": _status(hard_gate),
        "forbidden_surface_deltas": _cycle_forbidden_deltas(no_write_proof, cycle_index),
        "no_write_proof": no_write_proof,
        "stop_conditions": stop_conditions,
        "safety": {
            "starts_runtime": False,
            "launches_workers": False,
            "scheduler_or_daemon": False,
            "mutates_queue": False,
            "mutates_locks": False,
            "mutates_approvals": False,
            "writes_reports": False,
            "writes_telemetry": False,
            "writes_relay": False,
            "secrets_or_env_access": False,
            "broker_or_live_trading": False,
            "protected_action_recommended": False,
        },
    }


def _approval_required() -> dict[str, Any]:
    return {
        "human_owner_required": True,
        "before_apply": True,
        "before_commit": True,
        "before_push": True,
        "before_pr": True,
        "before_merge": True,
        "before_runtime": True,
        "before_worker_launch": True,
        "before_queue_lock_or_approval_mutation": True,
        "validator_pass_is_not_approval": True,
    }


def build_governed_self_development_soak_result(payload: dict[str, Any]) -> dict[str, Any]:
    cycles_requested = _int_value(payload.get("cycles_requested"), DEFAULT_CYCLES)
    max_cycles = _int_value(payload.get("max_cycles"), DEFAULT_MAX_CYCLES)
    repo_state = _as_dict(payload.get("repo_state"))
    no_write_proof = _as_dict(payload.get("no_write_proof"))
    raw_cycles = [_as_dict(cycle) for cycle in _as_list(payload.get("cycle_results"))]
    cycle_results = [_cycle_result(cycle) for cycle in raw_cycles]

    stop_conditions = _repo_stop_conditions(repo_state) + _no_write_stop_conditions(no_write_proof)
    if cycles_requested < 1:
        stop_conditions.append("CYCLES_REQUESTED_INVALID")
    if max_cycles < 1:
        stop_conditions.append("MAX_CYCLES_INVALID")
    if cycles_requested > max_cycles:
        stop_conditions.append("CYCLES_REQUESTED_EXCEEDS_MAX")
    if cycles_requested <= max_cycles and len(cycle_results) != cycles_requested:
        stop_conditions.append("CYCLES_COMPLETED_MISMATCH")

    forbidden_surface_deltas: list[dict[str, Any]] = []
    for cycle in cycle_results:
        stop_conditions.extend(_as_list(cycle.get("stop_conditions")))
        forbidden_surface_deltas.extend(_as_list(cycle.get("forbidden_surface_deltas")))

    stop_conditions = _dedupe([_safe_str(item) for item in stop_conditions])
    aggregate_status = "PASS" if not stop_conditions else "BLOCKED"
    if _bool(no_write_proof.get("changed", False)) or forbidden_surface_deltas:
        aggregate_status = "BLOCKED_BY_WRITE_SURFACE_RISK"

    recommended_next_packet = None
    if aggregate_status == "PASS":
        recommended_next_packet = {
            "packet_id": FINAL_VERIFICATION_PACKET,
            "mode": "DRY_RUN",
            "intent": "Run final closure verification from console-only evidence and stop before protected actions.",
            "packet_body_included": False,
            "execution_command_included": False,
        }

    next_safe_action = (
        "Review final verification closure evidence; this soak emits no protected-action command."
        if aggregate_status == "PASS"
        else "Stop and inspect soak blockers before continuing read-only validation."
    )

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_utc": _safe_str(payload.get("generated_utc") or _now()),
        "cycles_requested": cycles_requested,
        "cycles_completed": len(cycle_results),
        "cycle_results": cycle_results,
        "aggregate_status": aggregate_status,
        "forbidden_surface_deltas": forbidden_surface_deltas,
        "recommended_next_packet": recommended_next_packet,
        "approval_required": _approval_required(),
        "safety": {
            "status": aggregate_status,
            "console_only": True,
            "writes_files": False,
            "writes_reports": False,
            "writes_telemetry": False,
            "writes_packet_drafts": False,
            "writes_proposed_packets": False,
            "outputs_packet_body": False,
            "creates_ready_stage": False,
            "mutates_registry": False,
            "mutates_queue": False,
            "mutates_locks": False,
            "mutates_approvals": False,
            "writes_relay": False,
            "starts_runtime": False,
            "launches_workers": False,
            "scheduler_or_daemon": False,
            "backup_repo_local_lock": False,
            "protected_action_recommended": False,
            "secrets_or_env_access": False,
            "broker_or_live_trading": False,
            "governed_loop_pass": all(cycle["governed_loop_status"] == "PASS" for cycle in cycle_results),
            "approval_sos_hard_gate_pass": all(
                cycle["approval_sos_hard_gate_status"] == "PASS" for cycle in cycle_results
            ),
        },
        "no_write_proof": no_write_proof,
        "stop_conditions": stop_conditions,
        "next_safe_action": next_safe_action,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Build an AIOS governed self-development soak result from JSON evidence.")
    parser.add_argument("--payload-base64", default="")
    args = parser.parse_args()
    if args.payload_base64:
        payload_text = base64.b64decode(args.payload_base64.encode("ascii")).decode("utf-8")
    else:
        payload_text = sys.stdin.read()
    result = build_governed_self_development_soak_result(json.loads(payload_text))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["aggregate_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(_main())
