"""AI_OS soak dry-run proof (observe-only).

This module proves, in dry-run mode only, what an endurance/soak window would
evaluate for AI_OS without launching runtime, dispatching workers, mutating
files, mutating telemetry, or calling broker/live operations.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_SOAK_DRY_RUN_PROOF.v1"
PROOF_TYPE = "soak"
DEFAULT_SOAK_POLICY = {
    "required_duration_seconds": 3600,
    "max_heartbeat_gap_seconds": 300,
    "max_checkpoint_gap_seconds": 900,
    "require_restart_timeouts_proof": True,
    "require_retention_rotation_proof": True,
    "runtime_launch_allowed": False,
    "soak_execution_allowed": False,
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
    return int((later - earlier).total_seconds())


def _walk_fragments(obj: Any) -> list[str]:
    values: list[str] = []
    if isinstance(obj, dict):
        for value in obj.values():
            values.extend(_walk_fragments(value))
    elif isinstance(obj, list):
        for item in obj:
            values.extend(_walk_fragments(item))
    elif isinstance(obj, str):
        values.append(obj)
    return values


def _evaluate_samples(samples: list[Any], *, current_time: datetime, max_gap_seconds: int, label: str) -> tuple[list[dict[str, Any]], list[str], list[str], bool, bool, bool, bool, bool]:
    evaluated: list[dict[str, Any]] = []
    missing: list[str] = []
    invalid: list[str] = []
    future: bool = False
    stale: bool = False
    gaps: bool = False
    continuity_ok: bool = True
    seen_valid = 0

    parsed_samples: list[tuple[str, datetime | None]] = []
    if not isinstance(samples, list) or not samples:
        missing.append(f"{label}_samples_missing")
        return evaluated, missing, invalid, future, stale, gaps, False, False

    for index, sample in enumerate(samples):
        if not isinstance(sample, str):
            invalid.append(f"{label}_sample_{index}_invalid")
            evaluated.append({"sample": sample, "index": index, "valid": False, "issue": "invalid timestamp"})
            continue
        parsed = _parse_timestamp(sample)
        if parsed is None:
            invalid.append(f"{label}_sample_{index}_invalid")
            evaluated.append({"sample": sample, "index": index, "valid": False, "issue": "invalid timestamp"})
            continue
        if parsed > current_time:
            future = True
            invalid.append(f"{label}_sample_{index}_future")
            evaluated.append({"sample": sample, "index": index, "valid": False, "issue": "future timestamp"})
            continue
        parsed_samples.append((sample, parsed))

    if not parsed_samples:
        if not invalid:
            missing.append(f"{label}_samples_missing")
        return evaluated, missing, invalid, future, stale, gaps, False, False

    sorted_samples = sorted(parsed_samples, key=lambda item: item[1])
    first = sorted_samples[0][1]
    last = sorted_samples[-1][1]
    window_seconds = _seconds_between(last, first)

    prior = None
    for index, (sample, parsed) in enumerate(sorted_samples):
        issue = None
        if prior is not None:
            gap = _seconds_between(parsed, prior)
            if gap > max_gap_seconds:
                if label == "heartbeat":
                    stale = True
                else:
                    gaps = True
                continuity_ok = False
                issue = "gap"
            else:
                seen_valid += 1
        else:
            seen_valid += 1
        evaluated.append({"sample": sample, "index": index, "valid": True, "issue": issue, "timestamp_utc": sample})
        prior = parsed

    if window_seconds < 0:
        invalid.append(f"{label}_window_invalid")
        return evaluated, missing, invalid, future, stale, gaps, False, False

    continuity_ok = continuity_ok and not stale and not gaps
    return evaluated, missing, invalid, future, stale, gaps, continuity_ok, bool(seen_valid)


def _evaluate_prerequisite(proof: dict[str, Any] | None, *, field: str) -> tuple[str | None, bool]:
    if proof is None:
        return None, True
    status = proof.get("proof_status")
    if not isinstance(status, str):
        return None, True
    if status == "BLOCKED":
        return status, True
    if field == "restart_timeouts_proof" and status not in {"PASS", "ATTENTION"}:
        return status, True
    if field == "retention_rotation_proof" and status not in {"PASS", "ATTENTION"}:
        return status, True
    return status, False


def build_soak_dry_run_proof(
    simulated_soak: dict[str, Any] | None = None,
    *,
    restart_timeouts_proof: dict[str, Any] | None = None,
    retention_rotation_proof: dict[str, Any] | None = None,
    soak_policy: dict[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    simulated_soak = dict(simulated_soak or {})
    soak_policy = {**DEFAULT_SOAK_POLICY, **(soak_policy or {})}
    current_time = _parse_timestamp(now or simulated_soak.get("current_time_utc"))
    if current_time is None:
        current_time = datetime(2026, 1, 1, tzinfo=timezone.utc)

    window_start = _parse_timestamp(simulated_soak.get("window_start_utc"))
    window_end = _parse_timestamp(simulated_soak.get("window_end_utc"))
    heartbeat_samples = simulated_soak.get("heartbeat_samples_utc")
    checkpoint_samples = simulated_soak.get("checkpoint_samples_utc")

    invalid_timestamps: list[dict[str, Any]] = []
    future_timestamps: list[dict[str, Any]] = []
    missing_heartbeats_detected = False
    stale_heartbeats_detected = False
    missing_checkpoints_detected = False
    checkpoint_gaps_detected = False
    attention_reasons: list[str] = []
    blockers: list[str] = []

    restart_status, restart_blocked = _evaluate_prerequisite(restart_timeouts_proof, field="restart_timeouts_proof")
    retention_status, retention_blocked = _evaluate_prerequisite(retention_rotation_proof, field="retention_rotation_proof")

    if window_start is None:
        invalid_timestamps.append({"source": "window_start_utc", "value": simulated_soak.get("window_start_utc")})
    if window_end is None:
        invalid_timestamps.append({"source": "window_end_utc", "value": simulated_soak.get("window_end_utc")})

    if window_start is not None and window_start > current_time:
        future_timestamps.append({"source": "window_start_utc", "value": simulated_soak.get("window_start_utc")})
    if window_end is not None and window_end > current_time:
        future_timestamps.append({"source": "window_end_utc", "value": simulated_soak.get("window_end_utc")})

    if window_start is not None and window_end is not None:
        window_duration_seconds = _seconds_between(window_end, window_start)
    else:
        window_duration_seconds = None

    evaluated_heartbeat_samples, missing_hb, invalid_hb, future_hb, stale_hb, hb_gaps, heartbeat_continuity_ok, hb_seen = _evaluate_samples(
        heartbeat_samples if isinstance(heartbeat_samples, list) else [],
        current_time=current_time,
        max_gap_seconds=soak_policy["max_heartbeat_gap_seconds"],
        label="heartbeat",
    )
    evaluated_checkpoint_samples, missing_cp, invalid_cp, future_cp, stale_cp, cp_gaps, checkpoint_continuity_ok, cp_seen = _evaluate_samples(
        checkpoint_samples if isinstance(checkpoint_samples, list) else [],
        current_time=current_time,
        max_gap_seconds=soak_policy["max_checkpoint_gap_seconds"],
        label="checkpoint",
    )

    if not hb_seen:
        missing_heartbeats_detected = True
    if not cp_seen:
        missing_checkpoints_detected = True
    stale_heartbeats_detected = stale_hb
    checkpoint_gaps_detected = cp_gaps
    invalid_timestamps.extend({"source": item, "value": None} for item in invalid_hb + invalid_cp)
    if future_hb:
        future_timestamps.append({"source": "heartbeat_samples_utc", "value": None})
    if future_cp:
        future_timestamps.append({"source": "checkpoint_samples_utc", "value": None})
    if missing_hb:
        blockers.extend(missing_hb)
    if missing_cp:
        blockers.extend(missing_cp)
    if invalid_hb or invalid_cp:
        blockers.extend(invalid_hb + invalid_cp)
    if future_hb or future_cp:
        if future_hb:
            blockers.append("heartbeat_samples_utc_future")
        if future_cp:
            blockers.append("checkpoint_samples_utc_future")

    duration_sufficient = window_duration_seconds is not None and window_duration_seconds >= soak_policy["required_duration_seconds"]
    if window_duration_seconds is None:
        blockers.append("window timestamps missing or invalid")

    restart_timeouts_proof_status = restart_status
    retention_rotation_proof_status = retention_status
    if restart_blocked or retention_blocked:
        blockers.append("prerequisite proof blocked")

    if not duration_sufficient:
        attention_reasons.append("soak window shorter than required duration")
    if not heartbeat_continuity_ok:
        attention_reasons.append("heartbeat continuity warning")
    if not checkpoint_continuity_ok:
        attention_reasons.append("checkpoint continuity warning")
    if restart_timeouts_proof_status == "ATTENTION":
        attention_reasons.append("restart/timeouts proof attention")
    if retention_rotation_proof_status == "ATTENTION":
        attention_reasons.append("retention/rotation proof attention")

    proof_status = "PASS"
    if blockers:
        proof_status = "BLOCKED"
    elif attention_reasons or not duration_sufficient or not heartbeat_continuity_ok or not checkpoint_continuity_ok:
        proof_status = "ATTENTION"

    if proof_status == "PASS":
        soak_pass = True
    else:
        soak_pass = False

    soak_recommendation = {
        "PASS": {
            "summary": "Dry-run soak proof completed cleanly; no runtime was launched.",
            "reason": "Observation window, heartbeat continuity, checkpoint continuity, and prerequisite proofs were all acceptable.",
            "operator_action": "Use the proof as evidence only; keep runtime launch, scheduler, SOS, and live execution blocked.",
        },
        "ATTENTION": {
            "summary": "Dry-run soak proof detected continuity or retention pressure; no runtime was launched.",
            "reason": "The proof indicates endurance risk or proof-chain attention, but the module only reports it.",
            "operator_action": "Review the simulated soak conditions and keep runtime mutation blocked.",
        },
        "BLOCKED": {
            "summary": "Dry-run soak proof could not complete because the simulated input or prerequisite proofs were invalid or blocked.",
            "reason": "At least one required input or prerequisite proof was not safe to evaluate.",
            "operator_action": "Fix the simulated inputs and prerequisite proofs before rerunning the proof.",
        },
    }[proof_status]

    proof = {
        "schema": SCHEMA,
        "generated_at_utc": _now(now or current_time.isoformat().replace("+00:00", "Z")),
        "mode": "DRY_RUN",
        "proof_type": PROOF_TYPE,
        "proof_status": proof_status,
        "simulated_inputs": {
            "runtime_label": str(simulated_soak.get("runtime_label") or "aios-runtime"),
            "window_start_utc": simulated_soak.get("window_start_utc"),
            "window_end_utc": simulated_soak.get("window_end_utc"),
            "heartbeat_samples_utc": heartbeat_samples if isinstance(heartbeat_samples, list) else [],
            "checkpoint_samples_utc": checkpoint_samples if isinstance(checkpoint_samples, list) else [],
            "current_time_utc": current_time.isoformat().replace("+00:00", "Z"),
        },
        "soak_policy": {
            "required_duration_seconds": soak_policy["required_duration_seconds"],
            "max_heartbeat_gap_seconds": soak_policy["max_heartbeat_gap_seconds"],
            "max_checkpoint_gap_seconds": soak_policy["max_checkpoint_gap_seconds"],
            "require_restart_timeouts_proof": bool(soak_policy.get("require_restart_timeouts_proof", True)),
            "require_retention_rotation_proof": bool(soak_policy.get("require_retention_rotation_proof", True)),
            "runtime_launch_allowed": bool(soak_policy.get("runtime_launch_allowed", False)),
            "soak_execution_allowed": bool(soak_policy.get("soak_execution_allowed", False)),
        },
        "observation_window": {
            "start_utc": simulated_soak.get("window_start_utc"),
            "end_utc": simulated_soak.get("window_end_utc"),
        },
        "evaluated_heartbeat_samples": evaluated_heartbeat_samples,
        "evaluated_checkpoint_samples": evaluated_checkpoint_samples,
        "window_duration_seconds": window_duration_seconds,
        "required_duration_seconds": soak_policy["required_duration_seconds"],
        "duration_sufficient": duration_sufficient,
        "heartbeat_continuity_ok": heartbeat_continuity_ok,
        "checkpoint_continuity_ok": checkpoint_continuity_ok,
        "restart_timeouts_proof_status": restart_timeouts_proof_status,
        "retention_rotation_proof_status": retention_rotation_proof_status,
        "missing_heartbeats_detected": missing_heartbeats_detected,
        "stale_heartbeats_detected": stale_heartbeats_detected,
        "missing_checkpoints_detected": missing_checkpoints_detected,
        "checkpoint_gaps_detected": checkpoint_gaps_detected,
        "invalid_timestamps": invalid_timestamps,
        "future_timestamps": future_timestamps,
        "attention_reasons": attention_reasons,
        "blockers": blockers,
        "soak_recommendation": soak_recommendation,
        "soak_pass": soak_pass,
        "soak_executed": False,
        "runtime_launched": False,
        "dispatch_allowed": False,
        "apply_allowed": False,
        "runtime_mutation_allowed": False,
        "telemetry_mutation_allowed": False,
        "scheduler_creation_allowed": False,
        "service_creation_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
        "credentials_accessed": False,
        "unsafe_autonomy_claim": False,
        "vacation_mode_complete": False,
        "safe_next_action": (
            "Dry-run soak proof only: report the simulated endurance results and keep runtime launch, scheduler, SOS, and live execution blocked."
            if proof_status != "BLOCKED"
            else "Fix the simulated soak inputs or prerequisite proof readouts and rerun the dry-run proof; no runtime action was taken."
        ),
        "proof_notes": [
            "dry-run soak proof only",
            "no real runtime launched",
            "no worker dispatch",
            "no scheduler creation",
            "no SOS sent",
            "no file or telemetry mutation",
            "live operations remain blocked",
        ],
    }

    return proof


def validate_soak_dry_run_proof(proof: dict[str, Any]) -> dict[str, object]:
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
        "soak_policy",
        "observation_window",
        "evaluated_heartbeat_samples",
        "evaluated_checkpoint_samples",
        "window_duration_seconds",
        "required_duration_seconds",
        "duration_sufficient",
        "heartbeat_continuity_ok",
        "checkpoint_continuity_ok",
        "restart_timeouts_proof_status",
        "retention_rotation_proof_status",
        "missing_heartbeats_detected",
        "stale_heartbeats_detected",
        "missing_checkpoints_detected",
        "checkpoint_gaps_detected",
        "invalid_timestamps",
        "future_timestamps",
        "attention_reasons",
        "blockers",
        "soak_recommendation",
        "soak_pass",
        "soak_executed",
        "runtime_launched",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_mutation_allowed",
        "telemetry_mutation_allowed",
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
    if proof.get("soak_executed") is True:
        blockers.append("soak_executed must be false")
        unsafe_flags.append("soak_executed_true")
    if proof.get("runtime_launched") is True:
        blockers.append("runtime_launched must be false")
        unsafe_flags.append("runtime_launched_true")
    if proof.get("dispatch_allowed") is True:
        blockers.append("dispatch_allowed must be false")
        unsafe_flags.append("dispatch_allowed_true")
    if proof.get("apply_allowed") is True:
        blockers.append("apply_allowed must be false")
        unsafe_flags.append("apply_allowed_true")
    if proof.get("runtime_mutation_allowed") is True:
        blockers.append("runtime_mutation_allowed must be false")
        unsafe_flags.append("runtime_mutation_allowed_true")
    if proof.get("telemetry_mutation_allowed") is True:
        blockers.append("telemetry_mutation_allowed must be false")
        unsafe_flags.append("telemetry_mutation_allowed_true")
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
                "un" + "link",
                "re" + "name",
                "re" + "place",
                "mi" + "kdir",
                "open" + "(",
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

    if str(proof.get("proof_status") or "") not in {"PASS", "ATTENTION", "BLOCKED"}:
        blockers.append("proof_status must be PASS, ATTENTION, or BLOCKED")
        unsafe_flags.append("proof_status_invalid")

    status = "PASS" if not blockers else "BLOCK"
    return {
        "status": status,
        "blockers": blockers,
        "checked_fields": checked_fields,
        "unsafe_flags": unsafe_flags,
    }


def summarize_soak_dry_run_proof(proof: dict[str, Any]) -> dict[str, object]:
    return {
        "status": "OK",
        "schema": proof.get("schema") if isinstance(proof, dict) else None,
        "proof_status": proof.get("proof_status") if isinstance(proof, dict) else None,
        "soak_pass": proof.get("soak_pass") if isinstance(proof, dict) else None,
        "soak_executed": proof.get("soak_executed") if isinstance(proof, dict) else None,
        "runtime_launched": proof.get("runtime_launched") if isinstance(proof, dict) else None,
        "duration_sufficient": proof.get("duration_sufficient") if isinstance(proof, dict) else None,
        "heartbeat_continuity_ok": proof.get("heartbeat_continuity_ok") if isinstance(proof, dict) else None,
        "checkpoint_continuity_ok": proof.get("checkpoint_continuity_ok") if isinstance(proof, dict) else None,
        "restart_timeouts_proof_status": proof.get("restart_timeouts_proof_status") if isinstance(proof, dict) else None,
        "retention_rotation_proof_status": proof.get("retention_rotation_proof_status") if isinstance(proof, dict) else None,
        "missing_heartbeats_detected": proof.get("missing_heartbeats_detected") if isinstance(proof, dict) else None,
        "stale_heartbeats_detected": proof.get("stale_heartbeats_detected") if isinstance(proof, dict) else None,
        "missing_checkpoints_detected": proof.get("missing_checkpoints_detected") if isinstance(proof, dict) else None,
        "checkpoint_gaps_detected": proof.get("checkpoint_gaps_detected") if isinstance(proof, dict) else None,
        "attention_count": len(proof.get("attention_reasons", [])) if isinstance(proof, dict) else None,
        "blocker_count": len(proof.get("blockers", [])) if isinstance(proof, dict) else None,
        "safe_next_action": proof.get("safe_next_action") if isinstance(proof, dict) else None,
        "vacation_mode_complete": proof.get("vacation_mode_complete") if isinstance(proof, dict) else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the AI_OS soak dry-run proof (JSON only).")
    parser.add_argument("--soak-json", default=None, help="optional JSON string with simulated soak inputs")
    parser.add_argument("--restart-json", default=None, help="optional JSON string with restart/timeouts proof")
    parser.add_argument("--retention-json", default=None, help="optional JSON string with retention/rotation proof")
    parser.add_argument("--policy-json", default=None, help="optional JSON string with the soak policy")
    parser.add_argument("--now", default=None, help="optional ISO-8601 timestamp for deterministic output")
    args = parser.parse_args()

    soak_inputs = json.loads(args.soak_json) if args.soak_json else None
    restart_proof = json.loads(args.restart_json) if args.restart_json else None
    retention_proof = json.loads(args.retention_json) if args.retention_json else None
    policy = json.loads(args.policy_json) if args.policy_json else None
    proof = build_soak_dry_run_proof(
        soak_inputs,
        restart_timeouts_proof=restart_proof,
        retention_rotation_proof=retention_proof,
        soak_policy=policy,
        now=args.now,
    )
    payload = {
        "proof": proof,
        "validation": validate_soak_dry_run_proof(proof),
        "summary": summarize_soak_dry_run_proof(proof),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["validation"]["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
