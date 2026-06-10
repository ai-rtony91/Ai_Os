"""AI_OS retention/rotation dry-run proof (observe-only).

This module proves, in dry-run mode only, what JSONL/log retention and
rotation would check for AI_OS without deleting, moving, truncating, archiving,
or otherwise mutating files or telemetry.

Pure standard library. JSON-only CLI. Deterministic with injected inputs and
timestamp.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_RETENTION_ROTATION_DRY_RUN_PROOF.v1"
PROOF_TYPE = "retention_rotation"
DEFAULT_RETENTION_POLICY = {
    "max_age_days": 30,
    "max_size_bytes": 5_242_880,
    "archive_after_days": 14,
    "rotate_after_size_bytes": 1_048_576,
    "delete_execution_allowed": False,
    "archive_execution_allowed": False,
    "rotation_execution_allowed": False,
    "truncate_execution_allowed": False,
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


def _days_between(later: datetime, earlier: datetime) -> float:
    return (later - earlier).total_seconds() / 86_400


def _file_path(file_meta: dict[str, Any], index: int) -> str:
    path = file_meta.get("path")
    if isinstance(path, str) and path.strip():
        return path
    return f"<simulated-file-{index}>"


def _evaluate_file(file_meta: dict[str, Any], policy: dict[str, Any], current_time: datetime, index: int) -> dict[str, Any]:
    if not isinstance(file_meta, dict):
        return {
            "path": f"<simulated-file-{index}>",
            "kind": "jsonl",
            "required": False,
            "classification": "review",
            "issues": ["file_metadata_not_object"],
            "age_days": None,
            "size_bytes": None,
            "line_count": None,
            "contains_jsonl": None,
            "rotation_required": False,
            "archive_required": False,
            "delete_required": False,
            "truncate_required": False,
        }

    path = _file_path(file_meta, index)
    kind = str(file_meta.get("kind") or "jsonl")
    contains_jsonl = file_meta.get("contains_jsonl")
    required = bool(file_meta.get("required", False))
    size_bytes = file_meta.get("size_bytes")
    line_count = file_meta.get("line_count")
    created_at = _parse_timestamp(file_meta.get("created_at_utc"))
    updated_at = _parse_timestamp(file_meta.get("updated_at_utc"))

    issues: list[str] = []
    if not isinstance(file_meta, dict):
        issues.append("file_metadata_not_object")
        return {
            "path": path,
            "kind": kind,
            "required": required,
            "classification": "review",
            "issues": issues,
            "age_days": None,
            "size_bytes": size_bytes,
            "line_count": line_count,
            "contains_jsonl": contains_jsonl,
            "rotation_required": False,
            "archive_required": False,
            "delete_required": False,
            "truncate_required": False,
        }

    if not isinstance(path, str) or not path.strip():
        issues.append("missing path")
    if not isinstance(size_bytes, int) or size_bytes < 0:
        issues.append("missing size_bytes")
    if contains_jsonl not in {True, False}:
        issues.append("missing contains_jsonl")
    if created_at is None and file_meta.get("created_at_utc") is not None:
        issues.append("invalid created_at_utc")
    if updated_at is None:
        issues.append("missing updated_at_utc")

    if issues:
        return {
            "path": path,
            "kind": kind,
            "required": required,
            "classification": "review",
            "issues": issues,
            "age_days": None,
            "size_bytes": size_bytes,
            "line_count": line_count,
            "contains_jsonl": contains_jsonl,
            "rotation_required": False,
            "archive_required": False,
            "delete_required": False,
            "truncate_required": False,
        }

    if updated_at > current_time or (created_at is not None and created_at > current_time):
        return {
            "path": path,
            "kind": kind,
            "required": required,
            "classification": "review",
            "issues": ["future timestamp"],
            "age_days": None,
            "size_bytes": size_bytes,
            "line_count": line_count,
            "contains_jsonl": contains_jsonl,
            "rotation_required": False,
            "archive_required": False,
            "delete_required": False,
            "truncate_required": False,
        }

    age_days = _days_between(current_time, updated_at)
    max_age_days = policy["max_age_days"]
    archive_after_days = policy["archive_after_days"]
    rotate_after_size_bytes = policy["rotate_after_size_bytes"]
    max_size_bytes = policy["max_size_bytes"]

    if contains_jsonl is False:
        classification = "review"
        issues.append("not jsonl")
    elif age_days >= max_age_days:
        classification = "review"
        issues.append("age exceeds max_age_days")
    elif age_days >= archive_after_days:
        classification = "archive"
    elif size_bytes >= rotate_after_size_bytes or size_bytes >= max_size_bytes:
        classification = "rotate"
    else:
        classification = "keep"

    return {
        "path": path,
        "kind": kind,
        "required": required,
        "classification": classification,
        "issues": issues,
        "age_days": round(age_days, 3),
        "size_bytes": size_bytes,
        "line_count": line_count,
        "contains_jsonl": contains_jsonl,
        "rotation_required": classification == "rotate",
        "archive_required": classification == "archive",
        "delete_required": age_days >= max_age_days,
        "truncate_required": classification == "rotate" and size_bytes >= max_size_bytes,
    }


def build_retention_rotation_dry_run_proof(
    simulated_files: list[dict[str, Any]] | None = None,
    *,
    retention_policy: dict[str, Any] | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    simulated_files = list(simulated_files or [])
    retention_policy = {**DEFAULT_RETENTION_POLICY, **(retention_policy or {})}
    current_time = _parse_timestamp(now)
    if current_time is None:
        current_time = datetime(2026, 1, 31, tzinfo=timezone.utc)

    evaluated_files = [
        _evaluate_file(file_meta, retention_policy, current_time, index)
        for index, file_meta in enumerate(simulated_files)
    ]

    malformed_inputs = [item for item in evaluated_files if "file_metadata_not_object" in item["issues"]]
    missing_metadata = [item for item in evaluated_files if any(issue.startswith("missing ") for issue in item["issues"])]
    future_timestamp_files = [item for item in evaluated_files if "future timestamp" in item["issues"]]
    oversized_files = [item for item in evaluated_files if item["classification"] == "rotate"]
    expired_files = [item for item in evaluated_files if item["classification"] == "review" and "age exceeds max_age_days" in item["issues"]]

    keep_candidates = [item for item in evaluated_files if item["classification"] == "keep"]
    rotate_candidates = [item for item in evaluated_files if item["classification"] == "rotate"]
    archive_candidates = [item for item in evaluated_files if item["classification"] == "archive"]
    review_candidates = [item for item in evaluated_files if item["classification"] == "review"]

    invalid_inputs = bool(malformed_inputs or missing_metadata or future_timestamp_files)
    attention_conditions = bool(rotate_candidates or archive_candidates or (expired_files and not invalid_inputs))

    proof_status = "PASS"
    if invalid_inputs:
        proof_status = "BLOCKED"
    elif attention_conditions:
        proof_status = "ATTENTION"

    rotation_required = bool(rotate_candidates)
    archive_required = bool(archive_candidates)
    delete_required = any(item["delete_required"] for item in expired_files)
    truncate_required = any(item["truncate_required"] for item in evaluated_files)

    retention_recommendation = {
        "PASS": {
            "summary": "Dry-run retention proof completed cleanly; no file mutation occurred.",
            "reason": "All simulated files stayed within the conservative age and size windows.",
            "operator_action": "Use the proof as evidence only; keep retention, rotation, archive, delete, and truncate execution blocked.",
        },
        "ATTENTION": {
            "summary": "Dry-run retention proof found files that would need rotate, archive, or review handling; no file mutation occurred.",
            "reason": "The proof identified retention pressure, but the module only reports it.",
            "operator_action": "Review the simulated file set and keep file mutation blocked.",
        },
        "BLOCKED": {
            "summary": "Dry-run retention proof could not complete because simulated file metadata was invalid, missing, or future-dated.",
            "reason": "At least one simulated file could not be evaluated safely.",
            "operator_action": "Fix the simulated metadata before rerunning the proof.",
        },
    }[proof_status]

    proof = {
        "schema": SCHEMA,
        "generated_at_utc": _now(now or current_time.isoformat().replace("+00:00", "Z")),
        "mode": "DRY_RUN",
        "proof_type": PROOF_TYPE,
        "proof_status": proof_status,
        "simulated_inputs": {
            "file_count": len(simulated_files),
            "current_time_utc": current_time.isoformat().replace("+00:00", "Z"),
        },
        "retention_policy": {
            "max_age_days": retention_policy["max_age_days"],
            "max_size_bytes": retention_policy["max_size_bytes"],
            "archive_after_days": retention_policy["archive_after_days"],
            "rotate_after_size_bytes": retention_policy["rotate_after_size_bytes"],
            "delete_execution_allowed": bool(retention_policy.get("delete_execution_allowed", False)),
            "archive_execution_allowed": bool(retention_policy.get("archive_execution_allowed", False)),
            "rotation_execution_allowed": bool(retention_policy.get("rotation_execution_allowed", False)),
            "truncate_execution_allowed": bool(retention_policy.get("truncate_execution_allowed", False)),
        },
        "evaluated_files": evaluated_files,
        "keep_candidates": keep_candidates,
        "rotate_candidates": rotate_candidates,
        "archive_candidates": archive_candidates,
        "review_candidates": review_candidates,
        "malformed_inputs": malformed_inputs,
        "missing_metadata": missing_metadata,
        "future_timestamp_files": future_timestamp_files,
        "oversized_files": oversized_files,
        "expired_files": expired_files,
        "retention_recommendation": retention_recommendation,
        "rotation_required": rotation_required,
        "rotation_executed": False,
        "archive_required": archive_required,
        "archive_executed": False,
        "delete_required": delete_required,
        "delete_executed": False,
        "truncate_required": truncate_required,
        "truncate_executed": False,
        "file_mutation_allowed": False,
        "telemetry_mutation_allowed": False,
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
            "Dry-run proof only: report the retention, rotation, archive, and review results and keep file mutation, telemetry mutation, scheduler, SOS, and live execution blocked."
            if proof_status != "BLOCKED"
            else "Fix the simulated file metadata and rerun the dry-run proof; no file action was taken."
        ),
        "proof_notes": [
            "dry-run proof only",
            "no file deletion performed",
            "no file move performed",
            "no file archive performed",
            "no file truncation performed",
            "telemetry remains unchanged",
            "scheduler and SOS remain blocked",
            "live operations remain blocked",
        ],
    }

    return proof


def validate_retention_rotation_dry_run_proof(proof: dict[str, Any]) -> dict[str, object]:
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
        "retention_policy",
        "evaluated_files",
        "keep_candidates",
        "rotate_candidates",
        "archive_candidates",
        "review_candidates",
        "malformed_inputs",
        "missing_metadata",
        "future_timestamp_files",
        "oversized_files",
        "expired_files",
        "retention_recommendation",
        "rotation_required",
        "rotation_executed",
        "archive_required",
        "archive_executed",
        "delete_required",
        "delete_executed",
        "truncate_required",
        "truncate_executed",
        "file_mutation_allowed",
        "telemetry_mutation_allowed",
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
    if proof.get("rotation_executed") is True:
        blockers.append("rotation_executed must be false")
        unsafe_flags.append("rotation_executed_true")
    if proof.get("archive_executed") is True:
        blockers.append("archive_executed must be false")
        unsafe_flags.append("archive_executed_true")
    if proof.get("delete_executed") is True:
        blockers.append("delete_executed must be false")
        unsafe_flags.append("delete_executed_true")
    if proof.get("truncate_executed") is True:
        blockers.append("truncate_executed must be false")
        unsafe_flags.append("truncate_executed_true")
    if proof.get("file_mutation_allowed") is True:
        blockers.append("file_mutation_allowed must be false")
        unsafe_flags.append("file_mutation_allowed_true")
    if proof.get("telemetry_mutation_allowed") is True:
        blockers.append("telemetry_mutation_allowed must be false")
        unsafe_flags.append("telemetry_mutation_allowed_true")
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


def summarize_retention_rotation_dry_run_proof(proof: dict[str, Any]) -> dict[str, object]:
    return {
        "status": "OK",
        "schema": proof.get("schema") if isinstance(proof, dict) else None,
        "proof_status": proof.get("proof_status") if isinstance(proof, dict) else None,
        "keep_count": len(proof.get("keep_candidates", [])) if isinstance(proof, dict) else None,
        "rotate_count": len(proof.get("rotate_candidates", [])) if isinstance(proof, dict) else None,
        "archive_count": len(proof.get("archive_candidates", [])) if isinstance(proof, dict) else None,
        "review_count": len(proof.get("review_candidates", [])) if isinstance(proof, dict) else None,
        "malformed_count": len(proof.get("malformed_inputs", [])) if isinstance(proof, dict) else None,
        "missing_metadata_count": len(proof.get("missing_metadata", [])) if isinstance(proof, dict) else None,
        "future_timestamp_count": len(proof.get("future_timestamp_files", [])) if isinstance(proof, dict) else None,
        "oversized_count": len(proof.get("oversized_files", [])) if isinstance(proof, dict) else None,
        "expired_count": len(proof.get("expired_files", [])) if isinstance(proof, dict) else None,
        "rotation_required": proof.get("rotation_required") if isinstance(proof, dict) else None,
        "rotation_executed": proof.get("rotation_executed") if isinstance(proof, dict) else None,
        "archive_required": proof.get("archive_required") if isinstance(proof, dict) else None,
        "archive_executed": proof.get("archive_executed") if isinstance(proof, dict) else None,
        "delete_required": proof.get("delete_required") if isinstance(proof, dict) else None,
        "delete_executed": proof.get("delete_executed") if isinstance(proof, dict) else None,
        "truncate_required": proof.get("truncate_required") if isinstance(proof, dict) else None,
        "truncate_executed": proof.get("truncate_executed") if isinstance(proof, dict) else None,
        "safe_next_action": proof.get("safe_next_action") if isinstance(proof, dict) else None,
        "vacation_mode_complete": proof.get("vacation_mode_complete") if isinstance(proof, dict) else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the AI_OS retention/rotation dry-run proof (JSON only).")
    parser.add_argument("--files-json", default=None, help="optional JSON string with simulated file metadata")
    parser.add_argument("--policy-json", default=None, help="optional JSON string with the retention policy")
    parser.add_argument("--now", default=None, help="optional ISO-8601 timestamp for deterministic output")
    args = parser.parse_args()

    files = json.loads(args.files_json) if args.files_json else None
    policy = json.loads(args.policy_json) if args.policy_json else None
    proof = build_retention_rotation_dry_run_proof(files, retention_policy=policy, now=args.now)
    payload = {
        "proof": proof,
        "validation": validate_retention_rotation_dry_run_proof(proof),
        "summary": summarize_retention_rotation_dry_run_proof(proof),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["validation"]["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
