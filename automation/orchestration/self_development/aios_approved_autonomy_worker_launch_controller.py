"""Approved local autonomy worker launch controller for AIOS.

This is the first APPLY-capable controller for bounded local simulation and
research tasks. It never launches arbitrary external workers, starts runtime,
starts scheduler/daemon, mutates queues/locks/approvals/registries, touches
secrets/.env, or opens broker/live-trading paths.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from datetime import datetime, timezone
from typing import Any

from automation.orchestration.self_development.aios_autonomy_run_ledger import (
    LedgerPathError,
    build_in_memory_ledger_reference,
    build_ledger_record,
    write_ledger_record,
)
from automation.orchestration.self_development.aios_minimal_sos_wake_policy import (
    build_minimal_sos_wake_policy_result,
)


SCHEMA = "AIOS_APPROVED_AUTONOMY_WORKER_LAUNCH_RESULT.v1"
APPROVAL = "APPROVED_SAFE_LOCAL_SIMULATION_WORKERS_ONLY"

PASS_STATUSES = {"PASS", "CLEAR", "OK", "GREEN"}
WARN_PASS_STATUSES = {"WARN_REVIEWED"}
SOS_ACTIVE_STATUSES = {"SOS_ACTIVE", "SOS", "SOS_HARD_STOP", "EMERGENCY", "CRITICAL"}
READY_PREFLIGHT = "PREFLIGHT_PASS_WORKER_LAUNCH_ELIGIBLE_BUT_NOT_EXECUTED"
READY_GUARDS = {
    "LAUNCH_APPROVED_FOR_FUTURE_PACKET_NOT_EXECUTED",
    "LAUNCH_AWAITING_HUMAN_APPROVAL",
}

POSTURE_CAPS = {
    "READ_ONLY_VALIDATOR_CREW": 2,
    "PACKET_PREVIEW_CREW": 2,
    "SUPERVISED_DAY_CREW_12H": 2,
    "SUPERVISED_DAY_NIGHT_CREW_24H": 3,
    "WEEKEND_LOW_TOUCH_CREW": 1,
    "VACATION_EMERGENCY_ONLY_CREW": 1,
    "FULL_AUTONOMY_SUPERVISED_CREW": 3,
}

ALLOWED_LANES = {
    "validator",
    "self_audit",
    "readiness_review",
    "packet_preview",
    "no_ready_stage_discovery",
    "approval_sos_review",
    "forex_research",
    "forex_backtest",
    "forex_replay",
    "forex_soak",
}

PROTECTED_LANES = {
    "runtime_execution",
    "scheduler",
    "daemon",
    "live_trading",
    "broker",
    "secrets",
    "approval_mutation",
    "queue_mutation",
    "lock_mutation",
    "registry_mutation",
    "reports_write",
    "telemetry_write",
    "relay_write",
    "dashboard_ui",
    "trading_lab_live",
    "forex_live",
    "oanda",
    "webhook",
    "orders",
    ".env",
    "secret",
}

LANE_TASKS = {
    "validator": "VALIDATOR_SUMMARY",
    "self_audit": "SELF_AUDIT_SUMMARY",
    "readiness_review": "VALIDATOR_SUMMARY",
    "packet_preview": "FOREX_RESEARCH_PLAN",
    "no_ready_stage_discovery": "FOREX_RESEARCH_PLAN",
    "approval_sos_review": "APPROVAL_SOS_CHECK",
    "forex_research": "FOREX_RESEARCH_PLAN",
    "forex_backtest": "FOREX_BACKTEST_STUB",
    "forex_replay": "FOREX_REPLAY_STUB",
    "forex_soak": "FOREX_SOAK_STUB",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _normalized(value: Any) -> str:
    return _safe_str(value).upper().replace("-", "_").replace(" ", "_") or "UNKNOWN"


def _lane_key(value: Any) -> str:
    return _safe_str(value).lower().replace("-", "_").replace(" ", "_")


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = _safe_str(value).lower()
    if not text:
        return default
    return text in {"true", "1", "yes", "y", "on", "approved", "present"}


def _int_value(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        key = _safe_str(item)
        if key and key not in seen:
            result.append(key)
            seen.add(key)
    return result


def _requested_lanes(value: Any) -> list[str]:
    result: list[str] = []
    for item in _as_list(value):
        parts = item.split(",") if isinstance(item, str) else [item]
        for part in parts:
            lane = _lane_key(part)
            if lane:
                result.append(lane)
    return _dedupe(result)


def _status_is_pass(value: Any, *, allow_warn_reviewed: bool = False) -> bool:
    normalized = _normalized(value)
    return normalized in PASS_STATUSES or (allow_warn_reviewed and normalized in WARN_PASS_STATUSES)


def _repo_stop_conditions(repo_state: dict[str, Any]) -> list[str]:
    stops: list[str] = []
    if repo_state and not _bool(repo_state.get("branch_matches_expected"), default=True):
        stops.append("BRANCH_MISMATCH")
    if (
        _bool(repo_state.get("dirty"))
        and _bool(repo_state.get("fail_on_dirty_worktree"), default=True)
        and not _bool(repo_state.get("dirty_allowed_for_approved_autonomy_worker_launch_validation"))
    ):
        stops.append("DIRTY_WORKTREE")
    return stops


def _protected_hits(lanes: list[str]) -> list[str]:
    return [lane for lane in lanes if lane in PROTECTED_LANES]


def _unknown_lanes(lanes: list[str]) -> list[str]:
    return [lane for lane in lanes if lane not in ALLOWED_LANES and lane not in PROTECTED_LANES]


def _safety(*, status: str, writes_ledger: bool = False, runs_local_tasks: bool = False) -> dict[str, Any]:
    return {
        "status": status,
        "writes_files": bool(writes_ledger),
        "writes_only_approved_run_ledger": bool(writes_ledger),
        "runs_local_simulation_tasks": bool(runs_local_tasks),
        "starts_runtime": False,
        "launches_workers": False,
        "launches_external_workers": False,
        "enables_scheduler": False,
        "starts_daemon": False,
        "mutates_queue": False,
        "mutates_locks": False,
        "mutates_approval": False,
        "mutates_approvals": False,
        "mutates_registry": False,
        "creates_ready_stage": False,
        "writes_reports": False,
        "writes_telemetry": False,
        "writes_relay": False,
        "touches_secrets_or_env": False,
        "broker_or_live_trading": False,
        "protected_actions_blocked": True,
        "human_owner_required_before_worker_launch": True,
        "worker_launch_executed": False,
        "external_worker_launch_executed": False,
        "valid_for_live_trading": False,
    }


def _task_result(task_type: str, lane: str, research_plan: str) -> dict[str, Any]:
    base = {
        "task_type": task_type,
        "lane": lane,
        "status": "PASS",
        "uses_synthetic_fixture_only": True,
        "valid_for_live_trading": False,
    }
    if task_type == "VALIDATOR_SUMMARY":
        base["summary"] = "Validator evidence accepted for bounded local simulation work."
    elif task_type == "SELF_AUDIT_SUMMARY":
        base["summary"] = "Self-audit confirms protected boundaries remain blocked."
    elif task_type == "FOREX_RESEARCH_PLAN":
        base["summary"] = research_plan or "Create next synthetic Forex research/backtest/replay/soak items."
        base["future_work_items"] = ["synthetic_backtest", "synthetic_replay", "synthetic_soak"]
    elif task_type == "FOREX_BACKTEST_STUB":
        base["summary"] = "Synthetic local backtest stub completed."
        base["trade_count"] = 10
        base["gross_return_sim"] = 2.4
    elif task_type == "FOREX_REPLAY_STUB":
        base["summary"] = "Synthetic local replay stub completed."
        base["events_replayed"] = 30
    elif task_type == "FOREX_SOAK_STUB":
        base["summary"] = "Synthetic local soak stub completed."
        base["cycles_completed"] = 3
    elif task_type == "APPROVAL_SOS_CHECK":
        base["summary"] = "Approval/SOS evidence is clear for local simulation work only."
    else:
        base["status"] = "FAILED"
        base["summary"] = "Unknown task type."
    return base


def _write_task_ledger(
    payload: dict[str, Any],
    generated_utc: str,
    index: int,
    task: dict[str, Any],
    write_ledger: bool,
) -> dict[str, Any]:
    record = build_ledger_record(
        run_id=f"approved_launch_{index}_{task['task_type'].lower()}_{generated_utc.replace(':', '').replace('-', '')}",
        mode=payload.get("mode", "DRY_RUN"),
        task_type=task["task_type"],
        status=task["status"],
        generated_utc=generated_utc,
        safety=_safety(status="PASS", writes_ledger=False, runs_local_tasks=True),
        stop_reason="",
        next_safe_action="Continue bounded local simulation or stop on protected boundary.",
        result_summary=task,
    )
    if not write_ledger:
        return build_in_memory_ledger_reference(
            run_id=record["run_id"],
            mode=record["mode"],
            task_type=record["task_type"],
            status=record["status"],
            generated_utc=generated_utc,
            result_summary=task,
            next_safe_action=record["next_safe_action"],
        )
    return write_ledger_record(payload.get("output_root"), record, repo_root=payload.get("repo_root"))


def _decision(payload: dict[str, Any], lanes: list[str], worker_count: int, max_workers: int, posture_cap: int) -> tuple[str, list[str], list[str], str]:
    repo_stops = _repo_stop_conditions(_as_dict(payload.get("repo_state")))
    if repo_stops:
        return "LAUNCH_REVIEW_REQUIRED", ["clean_repo_and_expected_branch"], repo_stops, "Restore expected clean repo state before local autonomy worker launch."

    approval = _safe_str(payload.get("human_owner_worker_launch_approval"))
    if approval != APPROVAL:
        return "LAUNCH_APPROVAL_MISSING", ["human_owner_worker_launch_approval"], [], "Supply APPROVED_SAFE_LOCAL_SIMULATION_WORKERS_ONLY for APPLY-capable local simulation workers."

    approval_sos = _normalized(payload.get("approval_sos_status") or "UNKNOWN")
    if approval_sos in SOS_ACTIVE_STATUSES:
        return "LAUNCH_BLOCKED_BY_SOS", ["approval_sos_clear"], ["SOS_ACTIVE"], "Wake Human Owner and clear approval/SOS hard gate before continuing."

    if not _status_is_pass(payload.get("identity_spine_status")):
        return "LAUNCH_BLOCKED_BY_VALIDATORS", ["identity_spine_pass"], [], "Run identity spine validator before local autonomy worker launch."
    if not _status_is_pass(payload.get("validator_chain_status"), allow_warn_reviewed=True):
        return "LAUNCH_BLOCKED_BY_VALIDATORS", ["validator_chain_pass_or_warn_reviewed"], [], "Run orchestration validator chain before local autonomy worker launch."
    if approval_sos not in PASS_STATUSES:
        return "LAUNCH_REVIEW_REQUIRED", ["approval_sos_pass_or_clear"], [], "Run approval/SOS hard gate before local autonomy worker launch."
    if _normalized(payload.get("preflight_decision")) != READY_PREFLIGHT:
        return "LAUNCH_BLOCKED_BY_VALIDATORS", ["worker_launch_preflight_pass"], [], "Run worker launch preflight gate until eligible-but-not-executed evidence is present."
    if _normalized(payload.get("launch_guard_decision")) not in READY_GUARDS:
        return "LAUNCH_REVIEW_REQUIRED", ["launch_guard_approved_for_future_packet"], [], "Run launch guard until future-packet approval evidence is present."
    if not lanes:
        return "LAUNCH_REVIEW_REQUIRED", ["allowed_lanes_non_empty"], [], "Provide at least one approved local simulation worker lane."

    protected = _protected_hits(lanes)
    if protected:
        if any(lane in {"broker", "live_trading", "forex_live", "trading_lab_live", "oanda", "webhook", "orders", ".env", "secret", "secrets"} for lane in protected):
            return "LAUNCH_BLOCKED_BY_SECRET_OR_LIVE_TRADING_BOUNDARY", [f"remove_protected_lane:{lane}" for lane in protected], ["PROTECTED_BOUNDARY"], "Stop and wake Human Owner; remove live, broker, OANDA, webhook, order, or secrets lanes."
        return "LAUNCH_BLOCKED_BY_PROTECTED_LANE", [f"remove_protected_lane:{lane}" for lane in protected], [], "Remove protected lanes before local autonomy worker launch."

    unknown = _unknown_lanes(lanes)
    if unknown:
        return "LAUNCH_BLOCKED_BY_PROTECTED_LANE", [f"lane_not_allowed:{lane}" for lane in unknown], [], "Use only approved local simulation/research lanes."

    effective_max = min(max_workers, posture_cap)
    if worker_count < 1 or worker_count > effective_max:
        return "LAUNCH_BLOCKED_BY_WORKER_LIMIT", ["worker_count_within_posture_cap"], [], "Reduce worker count to the posture cap."
    if _int_value(payload.get("timebox_minutes"), 0) < 5 or _int_value(payload.get("timebox_minutes"), 0) > 240:
        return "LAUNCH_BLOCKED_BY_TIMEBOX", ["timebox_between_5_and_240_minutes"], [], "Use a timebox between 5 and 240 minutes."

    mode = _normalized(payload.get("mode") or "DRY_RUN")
    if mode == "APPLY":
        return "LAUNCH_APPLY_EXECUTED", [], [], "Local deterministic simulation tasks executed; review run ledger before any next step."
    return "LAUNCH_APPLY_READY", [], [], "Human Owner may run APPLY with approved local simulation workers only."


def build_approved_autonomy_worker_launch_result(payload: dict[str, Any]) -> dict[str, Any]:
    generated_utc = _safe_str(payload.get("generated_utc") or _now())
    mode = _normalized(payload.get("mode") or "DRY_RUN")
    posture = _normalized(payload.get("worker_posture") or "READ_ONLY_VALIDATOR_CREW")
    operating_profile = _normalized(payload.get("operating_profile") or "24H_SUPERVISED")
    worker_count = max(0, _int_value(payload.get("worker_count"), 1))
    requested_max = max(0, _int_value(payload.get("max_parallel_workers"), 1))
    posture_cap = POSTURE_CAPS.get(posture, 1)
    max_parallel_workers = min(requested_max, posture_cap)
    lanes = _requested_lanes(payload.get("allowed_lanes"))
    research_plan = _safe_str(payload.get("research_plan"))

    decision, missing, stop_conditions, next_safe_action = _decision(payload, lanes, worker_count, requested_max, posture_cap)
    can_execute = decision == "LAUNCH_APPLY_EXECUTED"
    write_ledger = _bool(payload.get("write_ledger"), default=False) and can_execute
    tasks: list[dict[str, Any]] = []
    ledgers: list[dict[str, Any]] = []
    failed_count = 0

    if can_execute:
        task_lanes = lanes[:worker_count]
        for index, lane in enumerate(task_lanes, start=1):
            task = _task_result(LANE_TASKS[lane], lane, research_plan)
            tasks.append(task)
            if task["status"] != "PASS":
                failed_count += 1
                if _bool(payload.get("stop_on_first_failure"), default=True):
                    stop_conditions.append("STOP_ON_FIRST_FAILURE")
                    break
            try:
                ledgers.append(_write_task_ledger(payload, generated_utc, index, task, write_ledger))
            except LedgerPathError as exc:
                stop_conditions.append("LEDGER_OUTPUT_ROOT_BLOCKED")
                failed_count += 1
                decision = "LAUNCH_APPLY_PARTIAL_STOPPED"
                next_safe_action = f"Use an approved run ledger output root. {exc}"
                break
    else:
        tasks = [
            {
                "task_type": LANE_TASKS.get(lane, "UNKNOWN"),
                "lane": lane,
                "status": "NOT_RUN",
                "reason": next_safe_action,
                "valid_for_live_trading": False,
            }
            for lane in lanes[: max(worker_count, 0)]
        ]

    if can_execute and failed_count:
        decision = "LAUNCH_APPLY_PARTIAL_STOPPED"

    wake_events = []
    if decision == "LAUNCH_BLOCKED_BY_SOS":
        wake_events.append("SOS_HARD_STOP")
    if decision in {"LAUNCH_BLOCKED_BY_PROTECTED_LANE", "LAUNCH_BLOCKED_BY_SECRET_OR_LIVE_TRADING_BOUNDARY"}:
        wake_events.append("PROTECTED_ACTION_ATTEMPT")
    if decision == "LAUNCH_BLOCKED_BY_TIMEBOX":
        wake_events.append("WORKER_RUNAWAY_TIMEBOX_BREACH")
    if not wake_events:
        wake_events.append("NORMAL_RESEARCH_COMPLETION" if can_execute else "ROUTINE_VALIDATOR_WARN")

    safety_status = "PASS" if decision in {"LAUNCH_APPLY_READY", "LAUNCH_APPLY_EXECUTED"} else "BLOCKED"
    if decision in {"LAUNCH_REVIEW_REQUIRED", "LAUNCH_APPROVAL_MISSING"}:
        safety_status = "REVIEW_REQUIRED"

    return {
        "schema": SCHEMA,
        "mode": mode,
        "generated_utc": generated_utc,
        "repo_state": _as_dict(payload.get("repo_state")),
        "approval_state": {
            "required": True,
            "required_value": APPROVAL,
            "present": _safe_str(payload.get("human_owner_worker_launch_approval")) == APPROVAL,
            "missing_requirements": _dedupe(missing),
        },
        "input_evidence": {
            "identity_spine_status": _normalized(payload.get("identity_spine_status")),
            "validator_chain_status": _normalized(payload.get("validator_chain_status")),
            "approval_sos_status": _normalized(payload.get("approval_sos_status")),
            "preflight_decision": _normalized(payload.get("preflight_decision")),
            "launch_guard_decision": _normalized(payload.get("launch_guard_decision")),
            "allowed_lanes": lanes,
        },
        "launch_decision": decision,
        "worker_posture": posture,
        "operating_profile": operating_profile,
        "worker_count": worker_count,
        "max_parallel_workers": max_parallel_workers,
        "allowed_lanes": lanes,
        "blocked_lanes": sorted(PROTECTED_LANES),
        "timebox_minutes": _int_value(payload.get("timebox_minutes"), 30),
        "worker_tasks": tasks,
        "run_ledger": {
            "written": any(bool(item.get("written")) for item in ledgers),
            "records": ledgers,
            "output_root": _safe_str(payload.get("output_root")),
        },
        "executed_task_count": len([task for task in tasks if task.get("status") == "PASS" and can_execute]),
        "failed_task_count": failed_count,
        "stop_reason": ";".join(_dedupe(stop_conditions)),
        "human_wake_policy": build_minimal_sos_wake_policy_result({"events": wake_events}),
        "safety": _safety(
            status=safety_status,
            writes_ledger=any(bool(item.get("written")) for item in ledgers),
            runs_local_tasks=can_execute,
        ),
        "no_write_proof": {
            "writes_limited_to_approved_run_ledger": any(bool(item.get("written")) for item in ledgers),
            "global_queue_lock_approval_registry_untouched": True,
        },
        "missing_requirements": _dedupe(missing),
        "next_safe_action": next_safe_action,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Run AIOS approved local autonomy worker launch controller.")
    parser.add_argument("--payload-base64", default="")
    args = parser.parse_args()
    if args.payload_base64:
        payload_text = base64.b64decode(args.payload_base64.encode("ascii")).decode("utf-8")
    else:
        payload_text = sys.stdin.read()
    result = build_approved_autonomy_worker_launch_result(json.loads(payload_text))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["safety"]["status"] in {"PASS", "REVIEW_REQUIRED"} else 1


if __name__ == "__main__":
    raise SystemExit(_main())
