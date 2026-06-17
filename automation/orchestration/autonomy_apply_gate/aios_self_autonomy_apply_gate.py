from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_SELF_AUTONOMY_APPLY_GATE.v1"
DRY_RUN_SCHEMA = "AIOS_SELF_AUTONOMY_DRY_RUN_EXECUTION.v1"
COMPONENT = "self_autonomy_apply_gate"
MODE = "READ_ONLY_APPLY_REVIEW_ELIGIBILITY_GATE"
READY_DRY_RUN_VERDICT = "DRY_RUN_SIMULATION_COMPLETE"
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
PROTECTED_ALLOWED_PATH_TERMS = (
    "agents.md",
    "readme.md",
    "whitepaper.md",
    "risk_policy.md",
    "security.md",
    "docs/governance/",
    "docs/security/",
    "docs/workflows/",
    "docs/architecture/",
    "docs/audits/",
    "aios.ps1",
    ".github/",
    "services/",
    "apps/",
    "telemetry/",
    "reports/",
    "automation/orchestration/approval_inbox/",
    "automation/orchestration/work_packets/",
    "automation/orchestration/workers/",
    "automation/orchestration/command_queue/",
    "automation/orchestration/continuation/",
    "automation/security/",
    "apps/trading_lab/",
    "aios/modules/trader/",
    ".env",
    "secret",
    "credential",
    "broker",
    "oanda",
    "webhook",
    "live-trading",
    "production",
    "scheduler",
    "daemon",
    "commit",
    "push",
    "merge",
    "deployment",
)
SIDE_EFFECT_FIELDS = (
    "commands_executed",
    "files_written",
    "mutations_performed",
    "executable_packet_emitted",
    "execution_token_emitted",
    "codex_prompt_emitted",
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


def build_self_autonomy_apply_gate(
    dry_run_execution: Mapping[str, Any] | None,
    approval: Mapping[str, Any] | None = None,
    now_utc: str | None = None,
) -> dict[str, Any]:
    generated_at = now_utc or _utc_now()
    if not isinstance(dry_run_execution, Mapping):
        return _result(
            generated_at_utc=generated_at,
            gate_id=_gate_id(dry_run_execution, approval),
            inherited_execution_id="",
            inherited_plan_id="",
            inherited_execution_verdict="MISSING",
            verdict="BLOCKED_DRY_RUN_MISSING",
            gate_state="BLOCKED",
            blockers=["dry_run_execution_missing_or_non_object"],
            evidence_inputs=_evidence_inputs(dry_run_execution, approval),
            next_safe_action="Provide object-shaped M13 dry-run execution evidence.",
        )

    inherited_execution_id = str(dry_run_execution.get("execution_id") or "")
    inherited_plan_id = str(dry_run_execution.get("inherited_plan_id") or "")
    inherited_execution_verdict = str(dry_run_execution.get("verdict") or "UNKNOWN")
    gate_id = _gate_id(dry_run_execution, approval)
    allowed_paths = _string_list(dry_run_execution.get("allowed_paths"))
    forbidden_paths = _string_list(dry_run_execution.get("forbidden_paths"))
    validator_chain = _string_list(dry_run_execution.get("validator_chain"))
    rollback_note = _rollback_note(dry_run_execution)

    if not _dry_run_shape_ok(dry_run_execution) or _stale_looking(dry_run_execution):
        return _result(
            generated_at_utc=generated_at,
            gate_id=gate_id,
            inherited_execution_id=inherited_execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_execution_verdict=inherited_execution_verdict,
            verdict="BLOCKED_DRY_RUN_MISSING",
            gate_state="BLOCKED",
            allowed_paths=allowed_paths,
            forbidden_paths=forbidden_paths,
            validator_chain=validator_chain,
            rollback_note=rollback_note,
            blockers=["dry_run_execution_missing_malformed_or_stale"],
            evidence_inputs=_evidence_inputs(dry_run_execution, approval),
            next_safe_action="Provide fresh valid M13 dry-run execution evidence.",
        )

    if inherited_execution_verdict != READY_DRY_RUN_VERDICT:
        return _result(
            generated_at_utc=generated_at,
            gate_id=gate_id,
            inherited_execution_id=inherited_execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_execution_verdict=inherited_execution_verdict,
            verdict="BLOCKED_DRY_RUN_NOT_READY",
            gate_state="BLOCKED",
            allowed_paths=allowed_paths,
            forbidden_paths=forbidden_paths,
            validator_chain=validator_chain,
            rollback_note=rollback_note,
            blockers=_string_list(dry_run_execution.get("blockers")) or ["dry_run_not_ready"],
            evidence_inputs=_evidence_inputs(dry_run_execution, approval),
            next_safe_action="Resolve inherited M13 blockers before APPLY review eligibility.",
        )

    if _side_effect_present(dry_run_execution):
        return _result(
            generated_at_utc=generated_at,
            gate_id=gate_id,
            inherited_execution_id=inherited_execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_execution_verdict=inherited_execution_verdict,
            verdict="BLOCKED_EXECUTION_SIDE_EFFECT",
            gate_state="BLOCKED",
            allowed_paths=allowed_paths,
            forbidden_paths=forbidden_paths,
            validator_chain=validator_chain,
            rollback_note=rollback_note,
            blockers=["dry_run_side_effect_or_authority_flag"],
            evidence_inputs=_evidence_inputs(dry_run_execution, approval),
            next_safe_action="Provide dry-run evidence proving no commands, writes, mutations, tokens, prompts, or protected authority.",
        )

    if _unsafe_terms_present(dry_run_execution, approval):
        return _result(
            generated_at_utc=generated_at,
            gate_id=gate_id,
            inherited_execution_id=inherited_execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_execution_verdict=inherited_execution_verdict,
            verdict="BLOCKED_UNSAFE_SCOPE",
            gate_state="BLOCKED",
            allowed_paths=allowed_paths,
            forbidden_paths=forbidden_paths,
            validator_chain=validator_chain,
            rollback_note=rollback_note,
            blockers=["unsafe_scope_detected"],
            evidence_inputs=_evidence_inputs(dry_run_execution, approval),
            next_safe_action="Remove unsafe scope before APPLY review eligibility.",
        )

    if not allowed_paths or not forbidden_paths:
        return _result(
            generated_at_utc=generated_at,
            gate_id=gate_id,
            inherited_execution_id=inherited_execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_execution_verdict=inherited_execution_verdict,
            verdict="BLOCKED_SCOPE_UNKNOWN",
            gate_state="BLOCKED",
            allowed_paths=allowed_paths,
            forbidden_paths=forbidden_paths,
            validator_chain=validator_chain,
            rollback_note=rollback_note,
            dry_run_valid=True,
            blockers=["allowed_or_forbidden_paths_missing"],
            evidence_inputs=_evidence_inputs(dry_run_execution, approval),
            next_safe_action="Provide non-empty allowed and forbidden paths.",
        )

    scope_valid, scope_blocker = _scope_valid(allowed_paths, forbidden_paths)
    if not scope_valid:
        return _result(
            generated_at_utc=generated_at,
            gate_id=gate_id,
            inherited_execution_id=inherited_execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_execution_verdict=inherited_execution_verdict,
            verdict="BLOCKED_SCOPE_UNSAFE",
            gate_state="BLOCKED",
            allowed_paths=allowed_paths,
            forbidden_paths=forbidden_paths,
            validator_chain=validator_chain,
            rollback_note=rollback_note,
            dry_run_valid=True,
            blockers=[scope_blocker],
            evidence_inputs=_evidence_inputs(dry_run_execution, approval),
            next_safe_action="Constrain allowed paths to safe non-overlapping review scope.",
        )

    if not validator_chain:
        return _result(
            generated_at_utc=generated_at,
            gate_id=gate_id,
            inherited_execution_id=inherited_execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_execution_verdict=inherited_execution_verdict,
            verdict="BLOCKED_VALIDATORS_UNKNOWN",
            gate_state="BLOCKED",
            allowed_paths=allowed_paths,
            forbidden_paths=forbidden_paths,
            validator_chain=validator_chain,
            rollback_note=rollback_note,
            dry_run_valid=True,
            scope_valid=True,
            blockers=["validator_chain_missing"],
            evidence_inputs=_evidence_inputs(dry_run_execution, approval),
            next_safe_action="Provide validator chain before APPLY review eligibility.",
        )

    rollback_path_known = bool(rollback_note)
    if not rollback_path_known:
        return _result(
            generated_at_utc=generated_at,
            gate_id=gate_id,
            inherited_execution_id=inherited_execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_execution_verdict=inherited_execution_verdict,
            verdict="BLOCKED_ROLLBACK_MISSING",
            gate_state="BLOCKED",
            allowed_paths=allowed_paths,
            forbidden_paths=forbidden_paths,
            validator_chain=validator_chain,
            dry_run_valid=True,
            scope_valid=True,
            validators_known=True,
            blockers=["rollback_note_or_path_missing"],
            evidence_inputs=_evidence_inputs(dry_run_execution, approval),
            next_safe_action="Add rollback note or rollback path before APPLY review eligibility.",
        )

    explicit_approval = _explicit_approval_present(approval)
    if not explicit_approval:
        return _result(
            generated_at_utc=generated_at,
            gate_id=gate_id,
            inherited_execution_id=inherited_execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_execution_verdict=inherited_execution_verdict,
            verdict="HUMAN_APPROVAL_REQUIRED",
            gate_state="WAITING_FOR_HUMAN_APPROVAL",
            allowed_paths=allowed_paths,
            forbidden_paths=forbidden_paths,
            validator_chain=validator_chain,
            rollback_note=rollback_note,
            dry_run_valid=True,
            scope_valid=True,
            validators_known=True,
            rollback_path_known=True,
            human_approval_required=True,
            blockers=["explicit_human_approval_missing"],
            evidence_inputs=_evidence_inputs(dry_run_execution, approval),
            next_safe_action="Collect explicit human approval with matching scope before APPLY review.",
        )

    approval_scope_matches = _approval_scope_matches(approval, allowed_paths, validator_chain)
    if not approval_scope_matches:
        return _result(
            generated_at_utc=generated_at,
            gate_id=gate_id,
            inherited_execution_id=inherited_execution_id,
            inherited_plan_id=inherited_plan_id,
            inherited_execution_verdict=inherited_execution_verdict,
            verdict="BLOCKED_APPROVAL_SCOPE_MISMATCH",
            gate_state="BLOCKED",
            allowed_paths=allowed_paths,
            forbidden_paths=forbidden_paths,
            validator_chain=validator_chain,
            rollback_note=rollback_note,
            dry_run_valid=True,
            scope_valid=True,
            validators_known=True,
            rollback_path_known=True,
            human_approval_required=True,
            explicit_human_approval_present=True,
            blockers=["approval_scope_mismatch"],
            evidence_inputs=_evidence_inputs(dry_run_execution, approval),
            next_safe_action="Provide explicit approval that names matching allowed paths and validators.",
        )

    return _result(
        generated_at_utc=generated_at,
        gate_id=gate_id,
        inherited_execution_id=inherited_execution_id,
        inherited_plan_id=inherited_plan_id,
        inherited_execution_verdict=inherited_execution_verdict,
        verdict="APPLY_REVIEW_READY",
        gate_state="READY_FOR_HUMAN_APPLY_REVIEW",
        allowed_paths=allowed_paths,
        forbidden_paths=forbidden_paths,
        validator_chain=validator_chain,
        rollback_note=rollback_note,
        dry_run_valid=True,
        scope_valid=True,
        validators_known=True,
        rollback_path_known=True,
        human_approval_required=True,
        explicit_human_approval_present=True,
        approval_scope_matches=True,
        apply_review_ready=True,
        blockers=[],
        evidence_inputs=_evidence_inputs(dry_run_execution, approval),
        next_safe_action="Prepare a separate human-approved APPLY packet; this gate does not authorize execution.",
    )


def _result(
    *,
    generated_at_utc: str,
    gate_id: str,
    inherited_execution_id: str,
    inherited_plan_id: str,
    inherited_execution_verdict: str,
    verdict: str,
    gate_state: str,
    blockers: list[str],
    evidence_inputs: list[dict[str, Any]],
    next_safe_action: str,
    dry_run_valid: bool = False,
    scope_valid: bool = False,
    validators_known: bool = False,
    rollback_path_known: bool = False,
    human_approval_required: bool = True,
    explicit_human_approval_present: bool = False,
    approval_scope_matches: bool = False,
    apply_review_ready: bool = False,
    allowed_paths: list[str] | None = None,
    forbidden_paths: list[str] | None = None,
    validator_chain: list[str] | None = None,
    rollback_note: str = "",
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": generated_at_utc,
        "component": COMPONENT,
        "mode": MODE,
        "gate_id": gate_id,
        "inherited_execution_id": inherited_execution_id,
        "inherited_plan_id": inherited_plan_id,
        "inherited_execution_verdict": inherited_execution_verdict,
        "verdict": verdict,
        "gate_state": gate_state,
        "dry_run_valid": dry_run_valid,
        "scope_valid": scope_valid,
        "validators_known": validators_known,
        "rollback_path_known": rollback_path_known,
        "human_approval_required": human_approval_required,
        "explicit_human_approval_present": explicit_human_approval_present,
        "approval_scope_matches": approval_scope_matches,
        "apply_review_ready": apply_review_ready,
        "apply_allowed": False,
        "apply_performed": False,
        "commands_executed": False,
        "files_written": False,
        "mutations_performed": False,
        "executable_packet_emitted": False,
        "execution_token_emitted": False,
        "codex_prompt_emitted": False,
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
        "allowed_paths": allowed_paths or [],
        "forbidden_paths": forbidden_paths or [],
        "validator_chain": validator_chain or [],
        "rollback_note": rollback_note,
        "blockers": blockers,
        "evidence_inputs": evidence_inputs,
        "next_safe_action": next_safe_action,
        "safety": {
            "read_only": True,
            "side_effect_free": True,
            "eligibility_only": True,
            "commands_executed": False,
            "files_written": False,
            "reports_written": False,
            "runtime_mutation": False,
            "approval_mutation": False,
            "queue_mutation": False,
            "apply_performed": False,
        },
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _dry_run_shape_ok(value: Mapping[str, Any]) -> bool:
    return (
        value.get("schema") == DRY_RUN_SCHEMA
        and isinstance(value.get("execution_id"), str)
        and isinstance(value.get("inherited_plan_id"), str)
        and isinstance(value.get("verdict"), str)
    )


def _stale_looking(value: Mapping[str, Any]) -> bool:
    if value.get("stale") is True or value.get("is_stale") is True:
        return True
    for key in ("freshness", "freshness_state", "status"):
        if str(value.get(key) or "").strip().upper() == "STALE":
            return True
    return False


def _side_effect_present(value: Mapping[str, Any]) -> bool:
    if value.get("simulated") is not True:
        return True
    for field in SIDE_EFFECT_FIELDS:
        if value.get(field) is True:
            return True
    safety = value.get("safety")
    if isinstance(safety, Mapping):
        for field in ("commands_executed", "files_written", "runtime_mutation", "approval_mutation", "queue_mutation"):
            if safety.get(field) is True:
                return True
    return False


def _scope_valid(allowed_paths: list[str], forbidden_paths: list[str]) -> tuple[bool, str]:
    allowed = {_norm_path(path) for path in allowed_paths}
    forbidden = {_norm_path(path) for path in forbidden_paths}
    if allowed & forbidden:
        return False, "allowed_forbidden_path_overlap"
    for path in allowed:
        if _allowed_path_is_unsafe(path):
            return False, "allowed_path_unsafe_or_protected"
    return True, ""


def _allowed_path_is_unsafe(path: str) -> bool:
    return any(term in path for term in PROTECTED_ALLOWED_PATH_TERMS)


def _rollback_note(value: Mapping[str, Any]) -> str:
    direct = str(value.get("rollback_note") or value.get("rollback_path") or "").strip()
    if direct:
        return direct
    findings = value.get("simulated_findings")
    if isinstance(findings, Mapping):
        return str(findings.get("rollback_note") or findings.get("rollback_path") or "").strip()
    return ""


def _explicit_approval_present(approval: Mapping[str, Any] | None) -> bool:
    if not isinstance(approval, Mapping):
        return False
    if approval.get("explicit_human_approval_present") is True or approval.get("anthony_approved") is True:
        return True
    return str(approval.get("approval_status") or approval.get("status") or "").strip().lower() == "approved"


def _approval_scope_matches(approval: Mapping[str, Any] | None, allowed_paths: list[str], validator_chain: list[str]) -> bool:
    if not isinstance(approval, Mapping):
        return False
    approval_allowed = _string_list(approval.get("allowed_paths"))
    approval_validators = _string_list(approval.get("validator_chain"))
    if not approval_allowed or not approval_validators:
        return False
    return {_norm_path(path) for path in approval_allowed} == {_norm_path(path) for path in allowed_paths} and set(
        approval_validators
    ) == set(validator_chain)


def _unsafe_terms_present(dry_run_execution: Mapping[str, Any], approval: Mapping[str, Any] | None) -> bool:
    values = _scan_strings(dry_run_execution) + _scan_strings(approval)
    return any(_string_has_unsafe_term(value) for value in values)


def _string_has_unsafe_term(value: str) -> bool:
    lowered = value.lower()
    return any(term in lowered for term in UNSAFE_TERMS) or any(term in lowered for term in TOKEN_TERMS)


def _scan_strings(value: Any, parent_key: str = "") -> list[str]:
    if isinstance(value, Mapping):
        strings: list[str] = []
        for key, item in value.items():
            strings.extend(_scan_strings(item, str(key)))
        return strings
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        strings: list[str] = []
        for item in value:
            strings.extend(_scan_strings(item, parent_key))
        return strings
    if isinstance(value, str):
        return [value]
    return []


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _norm_path(path: str) -> str:
    text = str(path or "").strip().replace("\\", "/").lower()
    while text.startswith("./"):
        text = text[2:]
    return text


def _gate_id(dry_run_execution: Any, approval: Any) -> str:
    seed = {
        "dry_run": _safe_identity(dry_run_execution),
        "approval": _safe_identity(approval),
    }
    digest = hashlib.sha256(json.dumps(seed, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:16]
    return f"applygate-{digest}"


def _safe_identity(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            "schema": value.get("schema"),
            "execution_id": value.get("execution_id"),
            "inherited_plan_id": value.get("inherited_plan_id"),
            "verdict": value.get("verdict"),
            "allowed_paths": value.get("allowed_paths"),
            "validator_chain": value.get("validator_chain"),
            "approval_status": value.get("approval_status"),
            "status": value.get("status"),
            "explicit_human_approval_present": value.get("explicit_human_approval_present"),
            "anthony_approved": value.get("anthony_approved"),
        }
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _evidence_inputs(dry_run_execution: Any, approval: Any) -> list[dict[str, Any]]:
    return [
        {
            "name": "dry_run_execution",
            "status": "present" if isinstance(dry_run_execution, Mapping) else "missing_or_non_object",
            "schema": dry_run_execution.get("schema") if isinstance(dry_run_execution, Mapping) else None,
        },
        {
            "name": "approval",
            "status": "present" if isinstance(approval, Mapping) else "missing",
            "schema": approval.get("schema") if isinstance(approval, Mapping) else None,
        },
    ]


__all__ = ["build_self_autonomy_apply_gate"]
