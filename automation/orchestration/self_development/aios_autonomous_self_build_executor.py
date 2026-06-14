"""Bounded autonomous self-build executor burn-in for AIOS.

This executor proves the AIOS-side self-build loop without recursively
launching Codex, editing arbitrary source, committing, pushing, creating PRs,
or touching protected runtime surfaces.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from datetime import datetime, timezone
from typing import Any

from automation.orchestration.self_development.aios_self_build_candidate_selector import (
    select_self_build_candidate,
)
from automation.orchestration.self_development.aios_self_build_execution_ledger import (
    SelfBuildLedgerPathError,
    build_in_memory_self_build_ledger_reference,
    build_self_build_ledger_record,
    write_self_build_ledger_record,
)
from automation.orchestration.self_development.aios_self_build_execution_packet import (
    build_self_build_execution_packet,
)
from automation.orchestration.self_development.aios_self_build_validator_repair_engine import (
    build_validator_repair_result,
)


SCHEMA = "AIOS_AUTONOMOUS_SELF_BUILD_EXECUTOR_RESULT.v1"
APPLY_APPROVAL = "APPROVED_LOCAL_SELF_BUILD_ONLY"
COMMIT_APPROVAL = "APPROVED_LOCAL_SELF_BUILD_COMMIT"

MODES = {"DRY_RUN", "APPLY"}
SUPERVISOR_MODES = {
    "PLAN_ONLY",
    "SELECT_NEXT_CANDIDATE",
    "BUILD_EXECUTION_PACKET",
    "VALIDATE_AND_REPAIR_STUB",
    "FULL_LOCAL_SELF_BUILD_STUB",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _normalized(value: Any) -> str:
    return _safe_str(value).upper().replace("-", "_").replace(" ", "_") or "UNKNOWN"


def _int_value(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = _safe_str(value).lower()
    if not text:
        return default
    return text in {"true", "1", "yes", "y", "on", "approved", "present"}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item and item not in seen:
            result.append(item)
            seen.add(item)
    return result


def _repo_state(payload: dict[str, Any]) -> dict[str, Any]:
    return _as_dict(payload.get("repo_state")) or {
        "branch": _safe_str(payload.get("branch")),
        "expected_branch": _safe_str(payload.get("expected_branch")),
        "dirty": False,
    }


def _safety(
    *,
    mode: str,
    self_build_allowed: bool,
    ledger_written: bool,
    local_commit_allowed: bool,
    status: str,
) -> dict[str, Any]:
    return {
        "status": status,
        "writes_files": bool(ledger_written),
        "writes_only_approved_run_ledger": bool(mode == "APPLY" and ledger_written),
        "mutates_queue": False,
        "mutates_locks": False,
        "mutates_approval": False,
        "mutates_registry": False,
        "creates_ready_stage": False,
        "starts_runtime": False,
        "launches_workers": False,
        "enables_scheduler": False,
        "starts_daemon": False,
        "touches_secrets_or_env": False,
        "broker_or_live_trading": False,
        "uses_network": False,
        "uses_live_market_data": False,
        "pushes": False,
        "creates_pr": False,
        "merges": False,
        "self_build_allowed": bool(self_build_allowed),
        "local_commit_allowed": bool(local_commit_allowed),
        "arbitrary_source_edit": False,
        "protected_actions_blocked": True,
    }


def _empty_repair(generated_utc: str, reason: str) -> dict[str, Any]:
    return {
        "schema": "AIOS_SELF_BUILD_VALIDATOR_REPAIR_RESULT.v1",
        "generated_utc": generated_utc,
        "status": "NOT_RUN",
        "repair_needed": False,
        "current_attempt": 0,
        "max_repair_attempts": 0,
        "validator_summary": {"results": [], "pass_count": 0, "warn_count": 0, "fail_count": 0},
        "protected_boundary_hits": [],
        "sos_status": "CLEAR",
        "wake_required": False,
        "next_repair_action": "",
        "repair_actions": [],
        "stop_conditions": [reason] if reason else [],
        "next_safe_action": "Select a candidate and build an execution packet before validator repair.",
        "safety": {
            "writes_files": False,
            "arbitrary_code_edits": False,
            "protected_actions_blocked": True,
        },
    }


def _human_wake_policy(repair_result: dict[str, Any], stop_conditions: list[str]) -> dict[str, Any]:
    wake_required = bool(repair_result.get("wake_required")) or any(
        condition in {"SOS_ACTIVE", "PROTECTED_BOUNDARY_HIT", "TIMEBOX_EXCEEDED", "REPO_CORRUPTION"}
        for condition in stop_conditions
    )
    wake_reasons = []
    if wake_required:
        wake_reasons = [
            condition
            for condition in stop_conditions
            if condition in {"SOS_ACTIVE", "PROTECTED_BOUNDARY_HIT", "TIMEBOX_EXCEEDED", "REPO_CORRUPTION"}
        ] or ["VALIDATOR_REPAIR_HARD_STOP"]
    return {
        "wake_required": wake_required,
        "wake_class": "SOS_OR_PROTECTED_BOUNDARY" if wake_required else "NO_WAKE_REQUIRED",
        "wake_reasons": wake_reasons,
        "do_not_wake_for": [
            "routine validator WARN",
            "normal deterministic self-build completion",
            "expected repair exhaustion without protected boundary",
        ],
        "next_safe_action": "Wake Human Owner only for SOS, protected boundary, repo corruption, or timebox breach.",
    }


def _build_ledger(
    payload: dict[str, Any],
    generated_utc: str,
    mode: str,
    candidate: dict[str, Any],
    packet: dict[str, Any],
    repair_result: dict[str, Any],
    status: str,
    stop_reason: str,
    next_safe_action: str,
    write_ledger: bool,
) -> dict[str, Any]:
    run_id = "self_build_{0}_{1}".format(
        _safe_str(candidate.get("candidate_lane") or "candidate").lower(),
        generated_utc.replace(":", "").replace("-", ""),
    )
    record = build_self_build_ledger_record(
        run_id=run_id,
        candidate_id=_safe_str(candidate.get("candidate_id")),
        packet_id=_safe_str(packet.get("packet_id")),
        mode=mode,
        status=status,
        generated_utc=generated_utc,
        validator_summary=_as_dict(repair_result.get("validator_summary")),
        repair_attempts=_int_value(repair_result.get("current_attempt"), 0),
        safety=_safety(
            mode=mode,
            self_build_allowed=(mode == "APPLY"),
            ledger_written=False,
            local_commit_allowed=False,
            status=status,
        ),
        stop_reason=stop_reason,
        next_safe_action=next_safe_action,
    )
    if not write_ledger:
        return build_in_memory_self_build_ledger_reference(
            run_id=run_id,
            candidate_id=_safe_str(candidate.get("candidate_id")),
            packet_id=_safe_str(packet.get("packet_id")),
            mode=mode,
            status=status,
            generated_utc=generated_utc,
            validator_summary=_as_dict(repair_result.get("validator_summary")),
            repair_attempts=_int_value(repair_result.get("current_attempt"), 0),
            stop_reason=stop_reason,
            next_safe_action=next_safe_action,
        )
    return write_self_build_ledger_record(
        payload.get("output_root"),
        record,
        repo_root=payload.get("repo_root"),
    )


def build_autonomous_self_build_executor_result(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    generated_utc = _safe_str(payload.get("generated_utc")) or _now()
    mode = _normalized(payload.get("mode") or "DRY_RUN")
    supervisor_mode = _normalized(payload.get("supervisor_mode") or "PLAN_ONLY")
    approval = _safe_str(payload.get("human_owner_self_build_approval"))
    max_cycles = max(0, _int_value(payload.get("max_supervisor_cycles"), 1))
    max_repair_attempts = max(0, _int_value(payload.get("max_repair_attempts"), 2))
    max_runtime_minutes = _int_value(payload.get("max_runtime_minutes"), 60)
    stop_on_first_failure = _bool(payload.get("stop_on_first_failure"), default=True)
    allow_local_commit = _bool(payload.get("allow_local_commit"), default=False)
    write_ledger = _bool(payload.get("write_ledger"), default=False)
    stop_conditions: list[str] = []
    missing_requirements: list[str] = []

    if mode not in MODES:
        stop_conditions.append("INVALID_MODE")
    if supervisor_mode not in SUPERVISOR_MODES:
        stop_conditions.append("INVALID_SUPERVISOR_MODE")
    if mode == "APPLY" and approval != APPLY_APPROVAL and approval != COMMIT_APPROVAL:
        stop_conditions.append("HUMAN_OWNER_SELF_BUILD_APPROVAL_MISSING")
        missing_requirements.append(APPLY_APPROVAL)
    if max_runtime_minutes < 5 or max_runtime_minutes > 240:
        stop_conditions.append("MAX_RUNTIME_OUT_OF_RANGE")
    if max_cycles < 1 and supervisor_mode != "PLAN_ONLY":
        stop_conditions.append("MAX_SUPERVISOR_CYCLES_OUT_OF_RANGE")

    local_commit_allowed = allow_local_commit and approval == COMMIT_APPROVAL
    if allow_local_commit and not local_commit_allowed:
        stop_conditions.append("LOCAL_COMMIT_APPROVAL_MISSING")
    if local_commit_allowed:
        stop_conditions.append("LOCAL_COMMIT_BLOCKED_IN_BURN_IN")

    blocked = bool(stop_conditions)
    candidate = select_self_build_candidate(
        {
            "generated_utc": generated_utc,
            "eligible_lanes": payload.get("eligible_lanes"),
            "requested_lane": payload.get("requested_lane"),
            "allow_dashboard_ui": False,
        }
    )
    packet = build_self_build_execution_packet(
        candidate,
        {
            "generated_utc": generated_utc,
            "branch": _as_dict(payload.get("repo_state")).get("branch") or payload.get("expected_branch"),
            "max_repair_attempts": max_repair_attempts,
            "timebox_minutes": max_runtime_minutes if 5 <= max_runtime_minutes <= 240 else 60,
        },
    )

    run_repair = supervisor_mode in {
        "VALIDATE_AND_REPAIR_STUB",
        "FULL_LOCAL_SELF_BUILD_STUB",
    }
    if run_repair and not blocked:
        current_attempt = 0
        validator_results = _as_list(payload.get("validator_results")) or [
            {"validator_id": "identity_spine", "status": "PASS"},
            {"validator_id": "orchestration_validator_chain", "status": "PASS"},
            {"validator_id": "approval_sos_hard_gate", "status": "PASS"},
        ]
        repair_result = build_validator_repair_result(
            {
                "generated_utc": generated_utc,
                "validator_results": validator_results,
                "max_repair_attempts": max_repair_attempts,
                "current_attempt": current_attempt,
                "protected_boundary_hits": payload.get("protected_boundary_hits"),
                "sos_status": payload.get("sos_status") or "CLEAR",
            }
        )
        if repair_result["status"] == "REPAIR_ATTEMPT_AVAILABLE" and not stop_on_first_failure:
            repair_result = build_validator_repair_result(
                {
                    "generated_utc": generated_utc,
                    "validator_results": [{"validator_id": "deterministic_repair_stub", "status": "PASS"}],
                    "max_repair_attempts": max_repair_attempts,
                    "current_attempt": min(max_repair_attempts, current_attempt + 1),
                    "protected_boundary_hits": [],
                    "sos_status": "CLEAR",
                }
            )
        elif repair_result["status"] == "REPAIR_ATTEMPT_AVAILABLE" and stop_on_first_failure:
            stop_conditions.append("STOP_ON_FIRST_FAILURE")
        if repair_result["status"] == "HARD_STOP":
            stop_conditions.extend(_safe_str(item) for item in repair_result.get("stop_conditions", []))
    else:
        repair_result = _empty_repair(generated_utc, "VALIDATOR_REPAIR_NOT_REQUESTED")

    blocked = bool(stop_conditions)
    safety_status = "BLOCKED" if blocked else "PASS"
    if stop_conditions:
        stop_reason = ";".join(_dedupe(stop_conditions))
        if "HUMAN_OWNER_SELF_BUILD_APPROVAL_MISSING" in stop_conditions:
            next_safe_action = "Run DRY_RUN or supply APPROVED_LOCAL_SELF_BUILD_ONLY before APPLY self-build burn-in."
        elif "LOCAL_COMMIT_APPROVAL_MISSING" in stop_conditions:
            next_safe_action = "Remove AllowLocalCommit or supply separate explicit commit approval in a future packet."
        elif "LOCAL_COMMIT_BLOCKED_IN_BURN_IN" in stop_conditions:
            next_safe_action = "Do not commit from the executor burn-in; use Codex packet commit gate after validation."
        else:
            next_safe_action = "Correct self-build executor inputs or review validator repair result before continuing."
    else:
        stop_reason = "COMPLETED_BOUNDED_SELF_BUILD_STUB"
        next_safe_action = "Review self-build ledger evidence, then stop before push/PR/merge."

    cycles_requested = max_cycles if supervisor_mode != "PLAN_ONLY" else 1
    cycles_completed = 0 if blocked else min(max_cycles or 1, 1)
    executed_autonomously = mode == "APPLY" and not blocked
    ledger: dict[str, Any]
    try:
        ledger = _build_ledger(
            payload,
            generated_utc,
            mode,
            candidate,
            packet,
            repair_result,
            "PASS" if not blocked else "BLOCKED",
            stop_reason,
            next_safe_action,
            write_ledger=bool(mode == "APPLY" and write_ledger and not blocked),
        )
    except SelfBuildLedgerPathError as exc:
        stop_conditions.append("LEDGER_OUTPUT_ROOT_BLOCKED")
        safety_status = "BLOCKED"
        executed_autonomously = False
        cycles_completed = 0
        stop_reason = ";".join(_dedupe(stop_conditions))
        next_safe_action = f"Use an approved self-build ledger output root. {exc}"
        ledger = {
            "written": False,
            "path": "",
            "output_root": "",
            "error": str(exc),
            "safety": _safety(
                mode=mode,
                self_build_allowed=False,
                ledger_written=False,
                local_commit_allowed=False,
                status="BLOCKED",
            ),
        }

    ledger_written = bool(ledger.get("written"))
    self_build_allowed = mode == "APPLY" and approval in {APPLY_APPROVAL, COMMIT_APPROVAL} and not stop_conditions
    safety = _safety(
        mode=mode,
        self_build_allowed=self_build_allowed,
        ledger_written=ledger_written,
        local_commit_allowed=local_commit_allowed and not stop_conditions,
        status=safety_status,
    )

    return {
        "schema": SCHEMA,
        "mode": mode,
        "generated_utc": generated_utc,
        "repo_state": _repo_state(payload),
        "supervisor_mode": supervisor_mode,
        "approval_state": {
            "human_owner_self_build_approval_required_for_apply": True,
            "required_apply_approval": APPLY_APPROVAL,
            "required_commit_approval": COMMIT_APPROVAL,
            "human_owner_self_build_approval_present": approval in {APPLY_APPROVAL, COMMIT_APPROVAL},
            "local_commit_approval_present": approval == COMMIT_APPROVAL,
            "missing_requirements": _dedupe(missing_requirements),
        },
        "selected_candidate": candidate,
        "execution_packet": packet,
        "validation_repair_result": repair_result,
        "run_ledger": ledger,
        "cycles_requested": cycles_requested,
        "cycles_completed": cycles_completed,
        "executed_autonomously": executed_autonomously,
        "human_wake_policy": _human_wake_policy(repair_result, stop_conditions),
        "safety": safety,
        "stop_reason": stop_reason,
        "stop_conditions": _dedupe(stop_conditions),
        "next_safe_action": next_safe_action,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Run AIOS autonomous self-build executor burn-in.")
    parser.add_argument("--payload-base64", default="")
    args = parser.parse_args()
    if args.payload_base64:
        payload_text = base64.b64decode(args.payload_base64.encode("ascii")).decode("utf-8")
    else:
        payload_text = sys.stdin.read()
    result = build_autonomous_self_build_executor_result(json.loads(payload_text or "{}"))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["safety"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(_main())
