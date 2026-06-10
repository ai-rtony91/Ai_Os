"""AI_OS restart/timeouts dry-run proof (observe-only).

This module proves, in dry-run mode only, what restart supervision and timeout
handling would check for AI_OS without launching runtime, creating services or
scheduler tasks, dispatching workers, arming SOS, touching credentials, or
calling broker/live operations.

Pure standard library. JSON-only CLI. Deterministic with injected inputs and
timestamp.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_RESTART_TIMEOUTS_DRY_RUN_PROOF.v1"
PROOF_TYPE = "restart_timeouts"
DEFAULT_TIMEOUT_POLICY = {
    "heartbeat_timeout_seconds": 300,
    "checkpoint_timeout_seconds": 900,
    "max_restart_attempts": 0,
    "restart_execution_allowed": False,
    "timeout_execution_allowed": False,
}


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _seconds_between(later: datetime, earlier: datetime) -> int:
    delta = later - earlier
    return int(delta.total_seconds())


def _list_strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if isinstance(item, str)]
    return []


def _evaluate_conditions(simulated_inputs: dict[str, Any], timeout_policy: dict[str, Any], current_time: datetime) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    conditions: list[dict[str, Any]] = []
    stale_heartbeat_detected = False
    missing_checkpoint_detected = False
    healthy_state_detected = False
    restart_required = False
    timeout_triggered = False
    proof_status = "PASS"
    invalid_reason = ""

    runtime_expected = bool(simulated_inputs.get("runtime_expected", True))
    checkpoint_expected = bool(simulated_inputs.get("checkpoint_expected", True))

    last_heartbeat = _parse_timestamp(simulated_inputs.get("last_heartbeat_utc"))
    last_checkpoint = _parse_timestamp(simulated_inputs.get("last_checkpoint_utc"))

    heartbeat_timeout_seconds = timeout_policy.get("heartbeat_timeout_seconds")
    checkpoint_timeout_seconds = timeout_policy.get("checkpoint_timeout_seconds")
    max_restart_attempts = timeout_policy.get("max_restart_attempts")
    restart_execution_allowed = bool(timeout_policy.get("restart_execution_allowed", False))
    timeout_execution_allowed = bool(timeout_policy.get("timeout_execution_allowed", False))

    if not isinstance(heartbeat_timeout_seconds, int) or heartbeat_timeout_seconds <= 0:
        proof_status = "BLOCKED"
        invalid_reason = "heartbeat_timeout_seconds must be a positive integer"
    elif not isinstance(checkpoint_timeout_seconds, int) or checkpoint_timeout_seconds <= 0:
        proof_status = "BLOCKED"
        invalid_reason = "checkpoint_timeout_seconds must be a positive integer"
    elif not isinstance(max_restart_attempts, int) or max_restart_attempts < 0:
        proof_status = "BLOCKED"
        invalid_reason = "max_restart_attempts must be a non-negative integer"
    elif not isinstance(runtime_expected, bool) or not isinstance(checkpoint_expected, bool):
        proof_status = "BLOCKED"
        invalid_reason = "runtime_expected and checkpoint_expected must be boolean"
    elif runtime_expected and last_heartbeat is None:
        proof_status = "BLOCKED"
        invalid_reason = "last_heartbeat_utc is required when runtime_expected is true"
    elif checkpoint_expected and last_checkpoint is None:
        proof_status = "ATTENTION"
        missing_checkpoint_detected = True
        restart_required = True
        timeout_triggered = True
    else:
        heartbeat_age = None
        checkpoint_age = None
        if last_heartbeat is not None:
            if last_heartbeat > current_time:
                proof_status = "BLOCKED"
                invalid_reason = "last_heartbeat_utc cannot be later than current_time_utc"
            else:
                heartbeat_age = _seconds_between(current_time, last_heartbeat)
                stale_heartbeat_detected = runtime_expected and heartbeat_age > heartbeat_timeout_seconds
        if proof_status != "BLOCKED" and last_checkpoint is not None:
            if last_checkpoint > current_time:
                proof_status = "BLOCKED"
                invalid_reason = "last_checkpoint_utc cannot be later than current_time_utc"
            else:
                checkpoint_age = _seconds_between(current_time, last_checkpoint)
                missing_checkpoint_detected = checkpoint_expected and checkpoint_age > checkpoint_timeout_seconds

        if proof_status != "BLOCKED":
            if stale_heartbeat_detected or missing_checkpoint_detected:
                proof_status = "ATTENTION"
                restart_required = True
                timeout_triggered = bool(stale_heartbeat_detected or missing_checkpoint_detected)
            else:
                healthy_state_detected = True
                proof_status = "PASS"

        conditions.append(
            {
                "condition": "heartbeat_age_seconds",
                "passed": heartbeat_age is None or heartbeat_age <= heartbeat_timeout_seconds,
                "evidence": heartbeat_age,
            }
        )
        conditions.append(
            {
                "condition": "checkpoint_age_seconds",
                "passed": checkpoint_age is None or checkpoint_age <= checkpoint_timeout_seconds,
                "evidence": checkpoint_age,
            }
        )

    conditions.insert(0, {"condition": "current_time_utc_valid", "passed": True, "evidence": current_time.isoformat().replace("+00:00", "Z")})
    conditions.insert(1, {"condition": "runtime_expected_boolean", "passed": isinstance(runtime_expected, bool), "evidence": runtime_expected})
    conditions.insert(2, {"condition": "checkpoint_expected_boolean", "passed": isinstance(checkpoint_expected, bool), "evidence": checkpoint_expected})
    conditions.insert(3, {"condition": "restart_execution_allowed_false", "passed": restart_execution_allowed is False, "evidence": restart_execution_allowed})
    conditions.insert(4, {"condition": "timeout_execution_allowed_false", "passed": timeout_execution_allowed is False, "evidence": timeout_execution_allowed})

    if proof_status == "BLOCKED":
        healthy_state_detected = False

    recovery_recommendation = {
        "PASS": {
            "summary": "Dry-run proof completed cleanly; no restart or timeout was executed.",
            "reason": "Heartbeat and checkpoint timing stayed within the conservative windows.",
            "operator_action": "Use the proof as evidence only; keep real restart and timeout execution blocked.",
        },
        "ATTENTION": {
            "summary": "Dry-run proof detected a stale heartbeat or missing checkpoint; no real restart or timeout was executed.",
            "reason": "The proof indicates a recovery concern, but the module only reports it.",
            "operator_action": "Review the simulated condition and keep runtime mutation blocked.",
        },
        "BLOCKED": {
            "summary": "Dry-run proof could not complete because the simulated input was invalid or incomplete.",
            "reason": invalid_reason or "Simulated input validation failed.",
            "operator_action": "Fix the simulated inputs before rerunning the proof.",
        },
    }[proof_status]

    proof = {
        "schema": SCHEMA,
        "generated_at_utc": _now(simulated_inputs.get("current_time_utc") or current_time.isoformat().replace("+00:00", "Z")),
        "mode": "DRY_RUN",
        "proof_type": PROOF_TYPE,
        "proof_status": proof_status,
        "simulated_inputs": {
            "runtime_label": str(simulated_inputs.get("runtime_label") or "aios-runtime"),
            "runtime_expected": runtime_expected,
            "checkpoint_expected": checkpoint_expected,
            "last_heartbeat_utc": simulated_inputs.get("last_heartbeat_utc"),
            "last_checkpoint_utc": simulated_inputs.get("last_checkpoint_utc"),
            "current_time_utc": current_time.isoformat().replace("+00:00", "Z"),
        },
        "timeout_policy": {
            "heartbeat_timeout_seconds": heartbeat_timeout_seconds,
            "checkpoint_timeout_seconds": checkpoint_timeout_seconds,
            "max_restart_attempts": max_restart_attempts,
            "restart_execution_allowed": restart_execution_allowed,
            "timeout_execution_allowed": timeout_execution_allowed,
        },
        "evaluated_conditions": conditions,
        "stale_heartbeat_detected": stale_heartbeat_detected,
        "missing_checkpoint_detected": missing_checkpoint_detected,
        "healthy_state_detected": healthy_state_detected,
        "recovery_recommendation": recovery_recommendation,
        "restart_required": restart_required,
        "restart_executed": False,
        "timeout_triggered": timeout_triggered,
        "timeout_executed": False,
        "dispatch_allowed": False,
        "apply_allowed": False,
        "runtime_mutation_allowed": False,
        "scheduler_creation_allowed": False,
        "service_creation_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
        "credentials_accessed": False,
        "unsafe_autonomy_claim": False,
        "vacation_mode_complete": False,
        "safe_next_action": (
            "Dry-run proof only: report the simulated restart/timeouts result and keep real restart, timeout, scheduler, SOS, and live execution blocked."
            if proof_status != "BLOCKED"
            else "Fix the simulated input and rerun the dry-run proof; no runtime action was taken."
        ),
        "simulated_events_processed": [
            "heartbeat_check",
            "checkpoint_check",
            "timeout_window_evaluation",
            "recovery_recommendation",
        ],
        "restart_window_seconds": heartbeat_timeout_seconds,
        "checkpoint_window_seconds": checkpoint_timeout_seconds,
        "restart_attempts_remaining": max_restart_attempts,
        "proof_notes": [
            "dry-run proof only",
            "no real restart performed",
            "no real timeout executed",
            "scheduler and SOS remain blocked",
            "live operations remain blocked",
        ],
    }

    return proof


def build_restart_timeouts_dry_run_proof(
    simulated_inputs: dict[str, Any] | None = None,
    *,
    timeout_policy: dict[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    simulated_inputs = dict(simulated_inputs or {})
    timeout_policy = {**DEFAULT_TIMEOUT_POLICY, **(timeout_policy or {})}
    current_time = _parse_timestamp(now or simulated_inputs.get("current_time_utc"))
    if current_time is None:
        current_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return _evaluate_conditions(simulated_inputs, timeout_policy, current_time)


def validate_restart_timeouts_dry_run_proof(proof: dict[str, Any]) -> dict[str, object]:
    blockers: list[str] = []
    unsafe_flags: list[str] = []
    checked_fields: list[str] = []

    if not isinstance(proof, dict):
        return {
            "status": "BLOCK",
            "blockers": ["proof must be an object"],
            "checked_fields": [],
            "unsafe_flags": ["proof_not_object"],
        }

    required_fields = [
        "schema",
        "generated_at_utc",
        "mode",
        "proof_type",
        "proof_status",
        "simulated_inputs",
        "timeout_policy",
        "evaluated_conditions",
        "stale_heartbeat_detected",
        "missing_checkpoint_detected",
        "healthy_state_detected",
        "recovery_recommendation",
        "restart_required",
        "restart_executed",
        "timeout_triggered",
        "timeout_executed",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_mutation_allowed",
        "scheduler_creation_allowed",
        "service_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
        "credentials_accessed",
        "unsafe_autonomy_claim",
        "vacation_mode_complete",
        "safe_next_action",
    ]
    checked_fields = list(required_fields)
    missing = [field for field in required_fields if field not in proof]
    if missing:
        blockers.append(f"missing fields: {', '.join(sorted(missing))}")
        unsafe_flags.append("missing_fields")

    if proof.get("mode") != "DRY_RUN":
        blockers.append("mode must be DRY_RUN")
        unsafe_flags.append("mode_not_dry_run")
    if proof.get("proof_status") == "COMPLETE":
        blockers.append("proof_status must never be COMPLETE")
        unsafe_flags.append("proof_status_complete")
    if proof.get("restart_executed") is True:
        blockers.append("restart_executed must be false")
        unsafe_flags.append("restart_executed_true")
    if proof.get("timeout_executed") is True:
        blockers.append("timeout_executed must be false")
        unsafe_flags.append("timeout_executed_true")
    if proof.get("dispatch_allowed") is True:
        blockers.append("dispatch_allowed must be false")
        unsafe_flags.append("dispatch_allowed_true")
    if proof.get("apply_allowed") is True:
        blockers.append("apply_allowed must be false")
        unsafe_flags.append("apply_allowed_true")
    if proof.get("runtime_mutation_allowed") is True:
        blockers.append("runtime_mutation_allowed must be false")
        unsafe_flags.append("runtime_mutation_allowed_true")
    if proof.get("scheduler_creation_allowed") is True:
        blockers.append("scheduler_creation_allowed must be false")
        unsafe_flags.append("scheduler_creation_allowed_true")
    if proof.get("service_creation_allowed") is True:
        blockers.append("service_creation_allowed must be false")
        unsafe_flags.append("service_creation_allowed_true")
    if proof.get("sos_allowed") is True:
        blockers.append("sos_allowed must be false")
        unsafe_flags.append("sos_allowed_true")
    if proof.get("live_trading_allowed") is True:
        blockers.append("live_trading_allowed must be false")
        unsafe_flags.append("live_trading_allowed_true")
    if proof.get("credentials_accessed") is True:
        blockers.append("credentials_accessed must be false")
        unsafe_flags.append("credentials_accessed_true")
    if proof.get("unsafe_autonomy_claim") is True:
        blockers.append("unsafe_autonomy_claim must be false")
        unsafe_flags.append("unsafe_autonomy_claim_true")
    if proof.get("vacation_mode_complete") is True:
        blockers.append("vacation_mode_complete must be false")
        unsafe_flags.append("vacation_mode_complete_true")

    if not isinstance(proof.get("safe_next_action"), str) or not proof["safe_next_action"].strip():
        blockers.append("safe_next_action must be a non-empty string")
        unsafe_flags.append("safe_next_action_missing")

    def _walk(obj: Any) -> list[str]:
        found: list[str] = []
        if isinstance(obj, dict):
            for value in obj.values():
                found.extend(_walk(value))
        elif isinstance(obj, list):
            for item in obj:
                found.extend(_walk(item))
        elif isinstance(obj, str):
            lowered = obj.lower()
            command_fragments = [
                "git " + "push",
                "git " + "commit",
                "git " + "merge",
                "gh " + "pr " + "create",
                "gh " + "pr " + "merge",
                "register-" + "scheduledtask",
                "new-" + "service",
                "start-" + "job",
                "start-" + "process",
                "start-" + "service",
                "sub" + "process",
                "shell" + "=" + "true",
                "os" + ".system",
                "rm" + " -rf",
                "remove" + "-" + "item",
            ]
            secret_fragments = [
                "secret" + "=",
                "token" + "=",
                "pass" + "word" + "=",
                "api" + "_key" + "=",
                "api" + "key" + "=",
                "bear" + "er ",
                "sk" + "-",
            ]
            if any(fragment in lowered for fragment in command_fragments):
                found.append("command_string_detected")
            if any(fragment in lowered for fragment in secret_fragments):
                found.append("secret_assignment_string_detected")
        return found

    suspicious = _walk(proof)
    if "command_string_detected" in suspicious:
        blockers.append("output contains command-like strings")
        unsafe_flags.append("command_string_detected")
    if "secret_assignment_string_detected" in suspicious:
        blockers.append("output contains secret-like assignment strings")
        unsafe_flags.append("secret_assignment_string_detected")

    proof_status = str(proof.get("proof_status") or "")
    if proof_status not in {"PASS", "ATTENTION", "BLOCKED"}:
        blockers.append("proof_status must be PASS, ATTENTION, or BLOCKED")
        unsafe_flags.append("proof_status_invalid")

    status = "PASS" if not blockers else "BLOCK"
    return {
        "status": status,
        "blockers": blockers,
        "checked_fields": checked_fields,
        "unsafe_flags": unsafe_flags,
    }


def summarize_restart_timeouts_dry_run_proof(proof: dict[str, Any]) -> dict[str, object]:
    return {
        "status": "OK",
        "schema": proof.get("schema") if isinstance(proof, dict) else None,
        "proof_status": proof.get("proof_status") if isinstance(proof, dict) else None,
        "stale_heartbeat_detected": proof.get("stale_heartbeat_detected") if isinstance(proof, dict) else None,
        "missing_checkpoint_detected": proof.get("missing_checkpoint_detected") if isinstance(proof, dict) else None,
        "healthy_state_detected": proof.get("healthy_state_detected") if isinstance(proof, dict) else None,
        "restart_required": proof.get("restart_required") if isinstance(proof, dict) else None,
        "restart_executed": proof.get("restart_executed") if isinstance(proof, dict) else None,
        "timeout_triggered": proof.get("timeout_triggered") if isinstance(proof, dict) else None,
        "timeout_executed": proof.get("timeout_executed") if isinstance(proof, dict) else None,
        "safe_next_action": proof.get("safe_next_action") if isinstance(proof, dict) else None,
        "vacation_mode_complete": proof.get("vacation_mode_complete") if isinstance(proof, dict) else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the AI_OS restart/timeouts dry-run proof (JSON only).")
    parser.add_argument("--inputs-json", default=None, help="optional JSON string with simulated runtime inputs")
    parser.add_argument("--policy-json", default=None, help="optional JSON string with the timeout policy")
    parser.add_argument("--now", default=None, help="optional ISO-8601 timestamp for deterministic output")
    args = parser.parse_args()

    inputs = json.loads(args.inputs_json) if args.inputs_json else None
    policy = json.loads(args.policy_json) if args.policy_json else None
    proof = build_restart_timeouts_dry_run_proof(inputs, timeout_policy=policy, now=args.now)
    payload = {
        "proof": proof,
        "validation": validate_restart_timeouts_dry_run_proof(proof),
        "summary": summarize_restart_timeouts_dry_run_proof(proof),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["validation"]["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
