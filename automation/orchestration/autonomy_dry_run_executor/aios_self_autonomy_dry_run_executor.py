from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_SELF_AUTONOMY_DRY_RUN_EXECUTION.v1"
PLAN_SCHEMA = "AIOS_SELF_AUTONOMY_PLAN.v1"
COMPONENT = "self_autonomy_dry_run_executor"
MODE = "READ_ONLY_DRY_RUN_SIMULATOR"
READY_PLAN_VERDICT = "PLAN_READY_DRY_RUN_PREVIEW"
SIMULATED_STEPS = (
    "inspect_allowed_paths",
    "verify_forbidden_paths_absent",
    "verify_non_executable_preview",
    "verify_validator_chain_present",
    "simulate_validator_plan",
    "produce_dry_run_summary",
    "stop_before_mutation",
)
UNSAFE_TERMS = (
    "secret",
    "secrets",
    "credential",
    "credentials",
    "broker",
    "oanda",
    "live trading",
    "live-trading",
    "live order",
    "real order",
    "webhook execution",
    "production",
    "scheduler",
    "daemon",
    "worker launch",
    "dashboard mutation",
    "git add",
    "git commit",
    "git push",
    "commit",
    "push",
    "merge",
    "deployment",
    ".env",
)
TOKEN_TERMS = ("codex-only prompt", "ai_os execution token")
HARD_FALSE_FIELDS = (
    "apply_allowed",
    "worker_launch_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "broker_allowed",
    "live_trading_allowed",
    "production_allowed",
    "dashboard_mutation_allowed",
    "commit_allowed",
    "push_allowed",
    "merge_allowed",
)


def build_self_autonomy_dry_run_execution(
    plan: Mapping[str, Any] | None,
    now_utc: str | None = None,
) -> dict[str, Any]:
    generated_at = now_utc or _utc_now()
    if not isinstance(plan, Mapping):
        return _result(
            generated_at_utc=generated_at,
            execution_id=_execution_id(plan),
            inherited_plan_id="",
            inherited_plan_verdict="MISSING",
            inherited_plan_state="MISSING",
            verdict="BLOCKED_PLAN_MISSING",
            execution_state="BLOCKED",
            blockers=["plan_missing_or_non_object"],
            evidence_inputs=_evidence_inputs(plan, None),
            next_safe_action="Provide an object-shaped M12 plan before dry-run simulation.",
        )

    inherited_plan_id = str(plan.get("plan_id") or "")
    inherited_plan_verdict = str(plan.get("verdict") or "UNKNOWN")
    inherited_plan_state = str(plan.get("plan_state") or "UNKNOWN")
    preview = plan.get("non_executable_packet_preview")
    execution_id = _execution_id(plan)

    if not _plan_shape_ok(plan) or _stale_looking(plan):
        return _result(
            generated_at_utc=generated_at,
            execution_id=execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_plan_verdict=inherited_plan_verdict,
            inherited_plan_state=inherited_plan_state,
            verdict="BLOCKED_PLAN_MISSING",
            execution_state="BLOCKED",
            blockers=["plan_missing_malformed_or_stale"],
            evidence_inputs=_evidence_inputs(plan, preview),
            next_safe_action="Provide a fresh valid M12 plan payload.",
        )

    if inherited_plan_verdict != READY_PLAN_VERDICT:
        return _result(
            generated_at_utc=generated_at,
            execution_id=execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_plan_verdict=inherited_plan_verdict,
            inherited_plan_state=inherited_plan_state,
            verdict="BLOCKED_PLAN_NOT_READY",
            execution_state="BLOCKED",
            blockers=_string_list(plan.get("blockers")) or ["plan_not_ready"],
            evidence_inputs=_evidence_inputs(plan, preview),
            next_safe_action="Resolve inherited M12 plan blockers before dry-run simulation.",
        )

    if not isinstance(preview, Mapping):
        return _result(
            generated_at_utc=generated_at,
            execution_id=execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_plan_verdict=inherited_plan_verdict,
            inherited_plan_state=inherited_plan_state,
            verdict="BLOCKED_PREVIEW_MISSING",
            execution_state="BLOCKED",
            blockers=["preview_missing_or_malformed"],
            evidence_inputs=_evidence_inputs(plan, preview),
            next_safe_action="Provide a non-executable preview before simulation.",
        )

    if not _preview_base_shape_ok(preview):
        return _result(
            generated_at_utc=generated_at,
            execution_id=execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_plan_verdict=inherited_plan_verdict,
            inherited_plan_state=inherited_plan_state,
            verdict="BLOCKED_PREVIEW_MISSING",
            execution_state="BLOCKED",
            blockers=["preview_missing_or_malformed"],
            evidence_inputs=_evidence_inputs(plan, preview),
            next_safe_action="Provide a complete non-executable preview before simulation.",
        )

    preview_executable = preview.get("executable") is True
    token_flag = preview.get("execution_token_present") is True
    prompt_flag = preview.get("codex_prompt_present") is True
    approval_flag = preview.get("human_approval_required_before_execution") is True
    if preview_executable or token_flag or prompt_flag or not approval_flag:
        return _result(
            generated_at_utc=generated_at,
            execution_id=execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_plan_verdict=inherited_plan_verdict,
            inherited_plan_state=inherited_plan_state,
            verdict="BLOCKED_EXECUTABLE_PREVIEW",
            execution_state="BLOCKED",
            preview_executable=preview_executable,
            blockers=["preview_executable_or_token_bearing"],
            evidence_inputs=_evidence_inputs(plan, preview),
            next_safe_action="Replace the preview with a non-executable, approval-gated dry-run preview.",
        )

    if _preview_mode(preview) != "DRY_RUN" or _preview_lane(preview) != "DRY_RUN":
        return _result(
            generated_at_utc=generated_at,
            execution_id=execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_plan_verdict=inherited_plan_verdict,
            inherited_plan_state=inherited_plan_state,
            verdict="BLOCKED_NOT_DRY_RUN",
            execution_state="BLOCKED",
            blockers=["preview_not_dry_run"],
            evidence_inputs=_evidence_inputs(plan, preview),
            next_safe_action="Provide a preview with mode and lane set to DRY_RUN.",
        )

    unsafe_found = _unsafe_terms_present(plan)
    if unsafe_found:
        return _result(
            generated_at_utc=generated_at,
            execution_id=execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_plan_verdict=inherited_plan_verdict,
            inherited_plan_state=inherited_plan_state,
            verdict="BLOCKED_UNSAFE_SCOPE",
            execution_state="BLOCKED",
            blockers=["unsafe_scope_detected"],
            evidence_inputs=_evidence_inputs(plan, preview),
            next_safe_action="Remove unsafe scope before dry-run simulation.",
        )

    allowed_paths = _string_list(preview.get("allowed_paths"))
    forbidden_paths = _string_list(preview.get("forbidden_paths"))
    if not allowed_paths or not forbidden_paths:
        return _result(
            generated_at_utc=generated_at,
            execution_id=execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_plan_verdict=inherited_plan_verdict,
            inherited_plan_state=inherited_plan_state,
            verdict="BLOCKED_SCOPE_UNKNOWN",
            execution_state="BLOCKED",
            blockers=["allowed_or_forbidden_paths_missing"],
            evidence_inputs=_evidence_inputs(plan, preview),
            next_safe_action="Provide allowed and forbidden paths before dry-run simulation.",
        )

    validator_chain = _string_list(preview.get("validator_chain"))
    if not validator_chain:
        return _result(
            generated_at_utc=generated_at,
            execution_id=execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_plan_verdict=inherited_plan_verdict,
            inherited_plan_state=inherited_plan_state,
            verdict="BLOCKED_VALIDATORS_UNKNOWN",
            execution_state="BLOCKED",
            allowed_paths=allowed_paths,
            forbidden_paths=forbidden_paths,
            blockers=["validator_chain_missing"],
            evidence_inputs=_evidence_inputs(plan, preview),
            next_safe_action="Provide validator chain before dry-run simulation.",
        )

    return _result(
        generated_at_utc=generated_at,
        execution_id=execution_id,
        inherited_plan_id=inherited_plan_id,
        inherited_plan_verdict=inherited_plan_verdict,
        inherited_plan_state=inherited_plan_state,
        verdict="DRY_RUN_SIMULATION_COMPLETE",
        execution_state="SIMULATED",
        preview_valid=True,
        allowed_paths=allowed_paths,
        forbidden_paths=forbidden_paths,
        validator_chain=validator_chain,
        simulated_steps=list(SIMULATED_STEPS),
        simulated_findings={
            "would_inspect_files": allowed_paths,
            "would_avoid_files": forbidden_paths,
            "validators_required": validator_chain,
            "mutation_intent": False,
            "protected_action_intent": False,
            "human_approval_required_before_execution": True,
        },
        blockers=[],
        evidence_inputs=_evidence_inputs(plan, preview),
        next_safe_action="Stop before mutation; human review is required before executable work.",
    )


def _result(
    *,
    generated_at_utc: str,
    execution_id: str,
    inherited_plan_id: str,
    inherited_plan_verdict: str,
    inherited_plan_state: str,
    verdict: str,
    execution_state: str,
    blockers: list[str],
    evidence_inputs: list[dict[str, Any]],
    next_safe_action: str,
    preview_valid: bool = False,
    preview_executable: bool = False,
    allowed_paths: list[str] | None = None,
    forbidden_paths: list[str] | None = None,
    validator_chain: list[str] | None = None,
    simulated_steps: list[str] | None = None,
    simulated_findings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": generated_at_utc,
        "component": COMPONENT,
        "mode": MODE,
        "execution_id": execution_id,
        "inherited_plan_id": inherited_plan_id,
        "inherited_plan_verdict": inherited_plan_verdict,
        "inherited_plan_state": inherited_plan_state,
        "verdict": verdict,
        "execution_state": execution_state,
        "simulated": verdict == "DRY_RUN_SIMULATION_COMPLETE",
        "commands_executed": False,
        "files_written": False,
        "mutations_performed": False,
        "executable_packet_emitted": False,
        "execution_token_emitted": False,
        "codex_prompt_emitted": False,
        "apply_allowed": False,
        "worker_launch_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_allowed": False,
        "live_trading_allowed": False,
        "production_allowed": False,
        "dashboard_mutation_allowed": False,
        "commit_allowed": False,
        "push_allowed": False,
        "merge_allowed": False,
        "preview_valid": preview_valid,
        "preview_executable": preview_executable,
        "allowed_paths": allowed_paths or [],
        "forbidden_paths": forbidden_paths or [],
        "validator_chain": validator_chain or [],
        "simulated_steps": simulated_steps or [],
        "simulated_findings": simulated_findings or {},
        "blockers": blockers,
        "evidence_inputs": evidence_inputs,
        "next_safe_action": next_safe_action,
        "safety": {
            "read_only": True,
            "side_effect_free": True,
            "simulation_only": True,
            "commands_executed": False,
            "files_written": False,
            "reports_written": False,
            "network_access": False,
            "secrets_accessed": False,
            "runtime_mutation": False,
            "approval_mutation": False,
            "queue_mutation": False,
        },
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _plan_shape_ok(plan: Mapping[str, Any]) -> bool:
    return (
        plan.get("schema") == PLAN_SCHEMA
        and isinstance(plan.get("plan_id"), str)
        and isinstance(plan.get("verdict"), str)
        and isinstance(plan.get("plan_state"), str)
    )


def _stale_looking(plan: Mapping[str, Any]) -> bool:
    if plan.get("stale") is True or plan.get("is_stale") is True:
        return True
    for key in ("freshness", "freshness_state", "status"):
        if str(plan.get(key) or "").strip().upper() == "STALE":
            return True
    return False


def _preview_mode(preview: Mapping[str, Any]) -> str:
    return str(preview.get("mode") or "").strip().upper()


def _preview_lane(preview: Mapping[str, Any]) -> str:
    return str(preview.get("lane") or "").strip().upper()


def _preview_base_shape_ok(preview: Mapping[str, Any]) -> bool:
    required = (
        "executable",
        "execution_token_present",
        "codex_prompt_present",
        "human_approval_required_before_execution",
        "mode",
        "lane",
    )
    return all(key in preview for key in required)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _execution_id(plan: Any) -> str:
    seed = _safe_scan_payload(plan)
    digest = hashlib.sha256(json.dumps(seed, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:16]
    return f"dryrun-{digest}"


def _unsafe_terms_present(plan: Mapping[str, Any]) -> bool:
    values = _scan_strings(plan)
    return any(_string_has_unsafe_term(value) for value in values)


def _string_has_unsafe_term(value: str) -> bool:
    lowered = value.lower()
    return any(term in lowered for term in UNSAFE_TERMS) or any(term in lowered for term in TOKEN_TERMS)


def _scan_strings(value: Any, parent_key: str = "") -> list[str]:
    ignored_keys = {
        "blockers",
        "forbidden_paths",
        "protected_actions",
        "next_safe_action",
        "rollback_note",
        "safety",
        "stop_point",
    }
    if parent_key in ignored_keys:
        return []
    if isinstance(value, Mapping):
        strings: list[str] = []
        for key, item in value.items():
            strings.extend(_scan_strings(item, str(key)))
        return strings
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        strings = []
        for item in value:
            strings.extend(_scan_strings(item, parent_key))
        return strings
    if isinstance(value, str):
        return [value]
    return []


def _safe_scan_payload(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            "schema": value.get("schema"),
            "plan_id": value.get("plan_id"),
            "verdict": value.get("verdict"),
            "plan_state": value.get("plan_state"),
            "preview": _safe_scan_payload(value.get("non_executable_packet_preview")),
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_safe_scan_payload(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _evidence_inputs(plan: Any, preview: Any) -> list[dict[str, Any]]:
    return [
        {
            "name": "plan",
            "status": "present" if isinstance(plan, Mapping) else "missing_or_non_object",
            "schema": plan.get("schema") if isinstance(plan, Mapping) else None,
        },
        {
            "name": "non_executable_packet_preview",
            "status": "present" if isinstance(preview, Mapping) else "missing_or_malformed",
            "schema": None,
        },
    ]


__all__ = ["build_self_autonomy_dry_run_execution"]
