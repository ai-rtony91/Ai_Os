"""Pure AIOS validator/evidence router logic.

The PowerShell wrapper gathers read-only repo state. This module classifies
validator and evidence surfaces, sanitizes command-like fields, recommends
validation chains, and returns a JSON-ready dictionary. It writes no files and
starts no processes.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_VALIDATOR_EVIDENCE_ROUTER_RESULT.v1"
MODE = "DRY_RUN_READ_ONLY"
SOURCE_PACKET_ROUTER_SCHEMA = "AIOS_SELF_DEVELOPMENT_PACKET_ROUTER_RESULT.v1"
NEXT_SAFE_PACKET = "AIOS-DAY-NIGHT-SUPERVISOR-READINESS-DRYRUN-V1"

CLASSIFICATIONS = {
    "SAFE_READ_ONLY_VALIDATOR",
    "SAFE_READ_ONLY_EVIDENCE",
    "SAFE_WITH_SANITIZATION",
    "PROTECTED_ACTION_PREVIEW_ONLY",
    "WRITE_OR_MUTATION_SURFACE_BLOCKED",
    "SECRET_OR_ENV_BLOCKED",
    "RUNTIME_OR_WORKER_BLOCKED",
    "BROKER_OR_LIVE_TRADING_BLOCKED",
    "UNKNOWN_NEEDS_REVIEW",
}

COMMAND_BLOCK_PATTERNS = [
    r"\bgit\s+add\b",
    r"\bgit\s+commit\b",
    r"\bgit\s+push\b",
    r"\bgit\s+merge\b",
    r"\bgit\s+reset\b",
    r"\bgit\s+clean\b",
    r"\bgh\s+pr\b",
    r"\b-Mode\s+APPLY\b",
    r"\bmode\s*[:=]\s*APPLY\b",
    r"\bInvoke-AiOsExactCommitPackage\b",
    r"\bNew-AiOsRelayMessage\b",
    r"\bNew-AiOsPacketApprovalRequest\b",
    r"\bInvoke-AiOsApprovalChain\b",
    r"\bClaim-AiOsFileLock\b",
    r"\bRelease-AiOsFileLock\b",
    r"\bStart-AiOsPersistentRuntimeSupervisor\b",
    r"\bStart-AiOsWorkerDaemon\b",
    r"\bStart-AiOsWorkerLoop\b",
    r"\bOpen-AiOsWorkerWindow\b",
    r"\bworker\s+launch\b",
    r"\bscheduler\b",
    r"\bdaemon\b",
    r"\bbroker\b",
    r"\boanda\b",
    r"\bwebhook\b",
    r"\border\b",
    r"\blive[-_\s]?trading\b",
    r"\bsecret\b",
    r"\btoken\b",
    r"\bapi[-_ ]?key\b",
    r"\.env\b",
    r"code[xX].*prompt",
    r"execution.*token",
]

SAFE_VALIDATOR_SURFACES = [
    {
        "surface_id": "validator_chain",
        "path": "automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1",
        "family": "validator",
        "classification": "SAFE_READ_ONLY_VALIDATOR",
        "chain_roles": ["apply_packet", "pre_commit"],
    },
    {
        "surface_id": "apply_approval_gate",
        "path": "automation/orchestration/validators/Test-ApplyApprovalGate.DRY_RUN.ps1",
        "family": "validator",
        "classification": "SAFE_READ_ONLY_VALIDATOR",
        "chain_roles": ["apply_packet"],
    },
    {
        "surface_id": "approval_inbox_integrity",
        "path": "automation/orchestration/validators/Test-ApprovalInboxIntegrity.DRY_RUN.ps1",
        "family": "validator",
        "classification": "SAFE_READ_ONLY_VALIDATOR",
        "chain_roles": ["planning_review", "apply_packet"],
    },
    {
        "surface_id": "lock_registry_integrity",
        "path": "automation/orchestration/validators/Test-LockRegistryIntegrity.DRY_RUN.ps1",
        "family": "validator",
        "classification": "SAFE_READ_ONLY_VALIDATOR",
        "chain_roles": ["apply_packet", "pre_commit"],
    },
    {
        "surface_id": "worker_claim_collision",
        "path": "automation/orchestration/validators/Test-WorkerClaimCollision.DRY_RUN.ps1",
        "family": "validator",
        "classification": "SAFE_READ_ONLY_VALIDATOR",
        "chain_roles": ["apply_packet", "pre_commit"],
    },
    {
        "surface_id": "identity_spine",
        "path": "automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1",
        "family": "validator",
        "classification": "SAFE_READ_ONLY_VALIDATOR",
        "chain_roles": ["planning_review", "apply_packet"],
    },
    {
        "surface_id": "schema_contracts",
        "path": "automation/orchestration/validators/Test-AiOsOrchestrationSchemaContracts.DRY_RUN.ps1",
        "family": "validator",
        "classification": "SAFE_READ_ONLY_VALIDATOR",
        "chain_roles": ["pre_commit", "post_commit"],
    },
    {
        "surface_id": "commit_manifest",
        "path": "automation/orchestration/validators/Test-CommitPackageManifest.DRY_RUN.ps1",
        "family": "validator",
        "classification": "SAFE_READ_ONLY_VALIDATOR",
        "chain_roles": ["pre_commit"],
    },
    {
        "surface_id": "authority_duplication_guard",
        "path": "automation/orchestration/validators/Invoke-AiOsAuthorityDuplicationGuard.ps1",
        "family": "validator",
        "classification": "SAFE_READ_ONLY_VALIDATOR",
        "chain_roles": ["planning_review", "pre_commit"],
    },
]

EVIDENCE_SURFACES = [
    {
        "surface_id": "self_development_packet_router",
        "path": "automation/orchestration/self_audit/Get-AiOsSelfDevelopmentPacketRouter.DRY_RUN.ps1",
        "family": "packet_router",
        "classification": "SAFE_READ_ONLY_EVIDENCE",
        "chain_roles": ["planning_review"],
    },
    {
        "surface_id": "self_audit_loop",
        "path": "automation/orchestration/self_audit/Invoke-AiOsSelfAuditLoop.DRY_RUN.ps1",
        "family": "self_audit",
        "classification": "SAFE_READ_ONLY_EVIDENCE",
        "chain_roles": ["planning_review"],
    },
    {
        "surface_id": "action_recommendation",
        "path": "automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1",
        "family": "recommendation",
        "classification": "SAFE_WITH_SANITIZATION",
        "chain_roles": ["planning_review"],
    },
    {
        "surface_id": "campaign_no_ready",
        "path": "automation/orchestration/campaign_registry/Get-AiOsCampaignNoReadyStageDiscovery.DRY_RUN.ps1",
        "family": "campaign_registry",
        "classification": "SAFE_READ_ONLY_EVIDENCE",
        "chain_roles": ["planning_review"],
    },
    {
        "surface_id": "campaign_next_task",
        "path": "automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1",
        "family": "campaign_registry",
        "classification": "SAFE_READ_ONLY_EVIDENCE",
        "chain_roles": ["planning_review"],
    },
    {
        "surface_id": "approval_inbox_summary",
        "path": "automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1",
        "family": "approval",
        "classification": "SAFE_READ_ONLY_EVIDENCE",
        "chain_roles": ["planning_review", "apply_packet"],
    },
    {
        "surface_id": "lock_status",
        "path": "automation/orchestration/locks/Get-AiOsWorkerLockStatus.DRY_RUN.ps1",
        "family": "locks",
        "classification": "SAFE_READ_ONLY_EVIDENCE",
        "chain_roles": ["apply_packet"],
    },
    {
        "surface_id": "worker_registry",
        "path": "automation/orchestration/workers/Get-AiOsWorkerRegistry.DRY_RUN.ps1",
        "family": "workers",
        "classification": "SAFE_READ_ONLY_EVIDENCE",
        "chain_roles": ["planning_review"],
    },
    {
        "surface_id": "worker_inbox",
        "path": "automation/orchestration/workers/inbox/Get-AiOsWorkerInbox.DRY_RUN.ps1",
        "family": "workers",
        "classification": "SAFE_READ_ONLY_EVIDENCE",
        "chain_roles": ["planning_review"],
    },
    {
        "surface_id": "relay_bus_state",
        "path": "automation/orchestration/relay_bus/Get-AiOsRelayBusState.DRY_RUN.ps1",
        "family": "relay",
        "classification": "SAFE_READ_ONLY_EVIDENCE",
        "chain_roles": ["planning_review", "post_commit"],
    },
    {
        "surface_id": "relay_human_review",
        "path": "automation/orchestration/relay_bus/Resolve-AiOsRelayHumanReview.DRY_RUN.ps1",
        "family": "relay",
        "classification": "SAFE_READ_ONLY_EVIDENCE",
        "chain_roles": ["planning_review"],
    },
    {
        "surface_id": "runtime_state_bundle",
        "path": "automation/orchestration/runtime/Get-AiOsRuntimeStateBundle.DRY_RUN.ps1",
        "family": "runtime",
        "classification": "SAFE_READ_ONLY_EVIDENCE",
        "chain_roles": ["post_commit"],
    },
]

PROTECTED_PREVIEW_SURFACES = [
    {
        "surface_id": "commit_package_preview_validator",
        "path": "automation/orchestration/validators/New-CommitPackagePreview.DRY_RUN.ps1",
        "family": "commit_package",
        "classification": "PROTECTED_ACTION_PREVIEW_ONLY",
        "chain_roles": ["pre_commit"],
    },
    {
        "surface_id": "commit_package_recommendation",
        "path": "automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1",
        "family": "commit_package",
        "classification": "PROTECTED_ACTION_PREVIEW_ONLY",
        "chain_roles": ["pre_commit"],
    },
    {
        "surface_id": "commit_push_gate",
        "path": "automation/orchestration/commit_packages/Test-AiOsCommitPushGate.DRY_RUN.ps1",
        "family": "commit_package",
        "classification": "PROTECTED_ACTION_PREVIEW_ONLY",
        "chain_roles": ["pre_commit"],
    },
]

BLOCKED_SURFACES = [
    ("exact_commit_helper", "automation/orchestration/commit_packages/Invoke-AiOsExactCommitPackage.ps1"),
    ("approval_request_writer", "automation/orchestration/approval_inbox/New-AiOsPacketApprovalRequest.DRY_RUN.ps1"),
    ("approval_chain", "automation/orchestration/approval_inbox/Invoke-AiOsApprovalChain.DRY_RUN.ps1"),
    ("approval_processor", "automation/orchestration/approval_processor/Invoke-AiOsApprovalProcessor.DRY_RUN.ps1"),
    ("approved_action_resume", "automation/orchestration/approval_runner/Invoke-AiOsApprovedActionResume.ps1"),
    ("lock_claim", "automation/orchestration/locks/Claim-AiOsFileLock.DRY_RUN.ps1"),
    ("lock_release", "automation/orchestration/locks/Release-AiOsFileLock.DRY_RUN.ps1"),
    ("relay_writer", "automation/orchestration/relay_bus/New-AiOsRelayMessage.DRY_RUN.ps1"),
    ("worker_ready_packet_writer", "automation/orchestration/workers/inbox/New-AiOsWorkerReadyPacket.DRY_RUN.ps1"),
    ("worker_inbox_add", "automation/orchestration/workers/inbox/Add-AiOsWorkerInboxItem.DRY_RUN.ps1"),
    ("worker_state_setter", "automation/orchestration/workers/state/Set-AiOsWorkerTaskState.DRY_RUN.ps1"),
    ("worker_launcher", "automation/orchestration/workers/launcher/Open-AiOsWorkerWindow.DRY_RUN.ps1"),
    ("worker_daemon", "automation/orchestration/workers/daemon/Start-AiOsWorkerDaemon.DRY_RUN.ps1"),
    ("worker_loop", "automation/orchestration/workers/loop/Start-AiOsWorkerLoop.DRY_RUN.ps1"),
    ("worker_cycle", "automation/orchestration/workers/cycle/Start-AiOsAutonomousWorkerCycle.DRY_RUN.ps1"),
    ("worker_safe_execute", "automation/orchestration/workers/execution/Invoke-AiOsWorkerSafeExecute.DRY_RUN.ps1"),
    ("runtime_cycle", "automation/orchestration/runtime/Start-AiOsRuntimeCycle.DRY_RUN.ps1"),
    ("runtime_supervisor", "automation/orchestration/runtime/Start-AiOsPersistentRuntimeSupervisor.ps1"),
    ("runtime_self_route", "automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1"),
    ("runtime_packet_advancement", "automation/orchestration/runtime/Invoke-AiOsRuntimePacketAdvancement.ps1"),
    ("env_file", ".env"),
    ("env_glob", ".env*"),
    ("secret_store", "secrets/"),
    ("broker_path", "automation/trading/broker/"),
    ("oanda_path", "automation/trading/oanda/"),
    ("live_order_path", "automation/trading/live_orders/"),
    ("webhook_path", "automation/trading/webhooks/"),
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


def _norm_path(path: Any) -> str:
    return _safe_str(path).replace("\\", "/").strip()


def _lower_path(path: Any) -> str:
    return _norm_path(path).lower()


def command_is_safe_to_surface(command: Any) -> bool:
    text = _safe_str(command)
    if not text:
        return False
    if "\n" in text or "\r" in text:
        return False
    return not any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in COMMAND_BLOCK_PATTERNS)


def sanitize_command_field(command: Any) -> dict[str, Any]:
    text = _safe_str(command)
    if command_is_safe_to_surface(text):
        return {"safe_to_surface": True, "display_text": text, "blocked_reason": ""}
    return {
        "safe_to_surface": False,
        "display_text": "Sanitized: executable recommendation withheld; review surface classification and intent only.",
        "blocked_reason": "command_or_protected_action_not_surfaceable",
    }


def classify_surface(path: Any) -> dict[str, Any]:
    normalized = _norm_path(path)
    lowered = _lower_path(path)
    reason = "unknown_surface"
    classification = "UNKNOWN_NEEDS_REVIEW"
    family = "unknown"

    if lowered in {".env", ".env*"} or lowered.startswith(".env") or "/.env" in lowered or "secret" in lowered or "api_key" in lowered:
        classification = "SECRET_OR_ENV_BLOCKED"
        family = "secret_env"
        reason = "secret_or_env_surface"
    elif any(term in lowered for term in ("broker", "oanda", "webhook", "live_order", "live-orders", "live_trading", "live-trading")):
        classification = "BROKER_OR_LIVE_TRADING_BLOCKED"
        family = "broker_live_trading"
        reason = "broker_or_live_trading_surface"
    elif "invoke-aiosexactcommitpackage.ps1" in lowered:
        classification = "WRITE_OR_MUTATION_SURFACE_BLOCKED"
        family = "commit_package"
        reason = "exact_commit_helper_is_protected_write_surface"
    elif "new-commitpackagepreview.dry_run.ps1" in lowered or "new-aioscommitpackagerecommendation.dry_run.ps1" in lowered or "test-aioscommitpushgate.dry_run.ps1" in lowered:
        classification = "PROTECTED_ACTION_PREVIEW_ONLY"
        family = "commit_package"
        reason = "commit_or_push_related_preview_only"
    elif "new-aiosrelaymessage.dry_run.ps1" in lowered:
        classification = "WRITE_OR_MUTATION_SURFACE_BLOCKED"
        family = "relay"
        reason = "relay_writer_can_persist_when_apply_mode_is_used"
    elif any(term in lowered for term in ("claim-aiosfilelock", "release-aiosfilelock")):
        classification = "WRITE_OR_MUTATION_SURFACE_BLOCKED"
        family = "locks"
        reason = "lock_claim_release_mutates_lock_state"
    elif any(term in lowered for term in ("new-aiospacketapprovalrequest", "invoke-aiosapprovalchain", "invoke-aiosapprovalprocessor", "invoke-aiosapprovedactionresume")):
        classification = "WRITE_OR_MUTATION_SURFACE_BLOCKED"
        family = "approval"
        reason = "approval_mutation_or_execution_helper"
    elif any(
        term in lowered
        for term in (
            "start-aiospersistentruntimesupervisor",
            "start-aiosruntimecycle",
            "invoke-aiosruntimeselfroute",
            "invoke-aiosruntimepacketadvancement",
            "start-aiosworkerdaemon",
            "start-aiosworkerloop",
            "start-aiosautonomousworkercycle",
            "open-aiosworkerwindow",
            "invoke-aiosworkersafeexecute",
            "set-aiosworkertaskstate",
            "add-aiosworkerinboxitem",
            "new-aiosworkerreadypacket",
        )
    ):
        classification = "RUNTIME_OR_WORKER_BLOCKED"
        family = "runtime_worker"
        reason = "runtime_worker_scheduler_daemon_or_state_mutation_surface"
    elif lowered.startswith("automation/orchestration/validators/") and lowered.endswith(".ps1"):
        classification = "SAFE_READ_ONLY_VALIDATOR"
        family = "validator"
        reason = "validator_surface_read_only_or_guard"
    elif lowered.startswith("automation/orchestration/recommendations/"):
        classification = "SAFE_WITH_SANITIZATION"
        family = "recommendation"
        reason = "recommendation_surface_can_expose_command_text"
    elif any(
        lowered.startswith(prefix)
        for prefix in (
            "automation/orchestration/campaign_registry/get-",
            "automation/orchestration/approval_inbox/get-",
            "automation/orchestration/locks/get-",
            "automation/orchestration/workers/get-",
            "automation/orchestration/workers/inbox/get-",
            "automation/orchestration/relay_bus/get-",
            "automation/orchestration/relay_bus/resolve-",
            "automation/orchestration/runtime/get-",
            "automation/orchestration/self_audit/get-",
        )
    ):
        classification = "SAFE_READ_ONLY_EVIDENCE"
        family = "evidence"
        reason = "read_only_evidence_surface"

    return {
        "path": normalized,
        "classification": classification,
        "family": family,
        "reason": reason,
        "blocked": classification.endswith("_BLOCKED") or classification == "UNKNOWN_NEEDS_REVIEW",
    }


def _surface_entry(item: dict[str, Any], exists_map: dict[str, bool]) -> dict[str, Any]:
    path = _norm_path(item["path"])
    classified = classify_surface(path)
    classification = item.get("classification") or classified["classification"]
    command = "powershell -NoProfile -ExecutionPolicy Bypass -File " + path + " -OutputJson"
    if classification in {"WRITE_OR_MUTATION_SURFACE_BLOCKED", "RUNTIME_OR_WORKER_BLOCKED"}:
        command += " -Mode APPLY"
    return {
        "surface_id": item["surface_id"],
        "path": path,
        "family": item.get("family") or classified["family"],
        "classification": classification,
        "exists": bool(exists_map.get(path, False)),
        "blocked": classification.endswith("_BLOCKED") or classification == "UNKNOWN_NEEDS_REVIEW",
        "chain_roles": list(item.get("chain_roles", [])),
        "safe_to_execute_by_router": False,
        "safe_to_use_as_evidence": classification in {
            "SAFE_READ_ONLY_VALIDATOR",
            "SAFE_READ_ONLY_EVIDENCE",
            "SAFE_WITH_SANITIZATION",
            "PROTECTED_ACTION_PREVIEW_ONLY",
        },
        "command": sanitize_command_field(command),
        "reason": item.get("reason") or classified["reason"],
    }


def _blocked_entry(surface_id: str, path: str, exists_map: dict[str, bool]) -> dict[str, Any]:
    classified = classify_surface(path)
    return _surface_entry(
        {
            "surface_id": surface_id,
            "path": path,
            "family": classified["family"],
            "classification": classified["classification"],
            "reason": classified["reason"],
            "chain_roles": [],
        },
        exists_map,
    )


def _existence_map(payload: dict[str, Any]) -> dict[str, bool]:
    mapping: dict[str, bool] = {}
    for item in _as_list(payload.get("surface_inventory")):
        if isinstance(item, dict):
            mapping[_norm_path(item.get("path"))] = bool(item.get("exists", False))
    return mapping


def _chain(chain_id: str, name: str, purpose: str, entries: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "chain_id": chain_id,
        "name": name,
        "purpose": purpose,
        "surfaces": [entry["surface_id"] for entry in entries],
        "classifications_allowed": sorted({entry["classification"] for entry in entries}),
        "requires_human_approval_before_protected_action": chain_id in {"apply_packet_chain", "pre_commit_chain"},
        "protected_action_recommended": False,
        "stop_condition": "Report evidence and stop; do not mutate repo, queue, locks, approvals, relay, runtime, or workers.",
    }


def build_recommended_chains(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_role: dict[str, list[dict[str, Any]]] = {
        "planning_review": [],
        "apply_packet": [],
        "pre_commit": [],
        "post_commit": [],
    }
    for entry in entries:
        if entry["blocked"]:
            continue
        for role in entry.get("chain_roles", []):
            if role in by_role:
                by_role[role].append(entry)

    return [
        _chain("planning_review_chain", "Planning/review chain", "Trust only read-only validators, evidence readers, and sanitized recommendations before selecting the next packet.", by_role["planning_review"]),
        _chain("apply_packet_chain", "APPLY packet chain", "Validate identity, approval, lock, worker-collision, and validator-chain evidence before APPLY work.", by_role["apply_packet"]),
        _chain("pre_commit_chain", "Pre-commit chain", "Use validator evidence and protected-action previews only; do not stage or commit from router output.", by_role["pre_commit"]),
        _chain("post_commit_chain", "Post-commit chain", "Refresh read-only schema, relay, and runtime-state evidence after a separately approved commit.", by_role["post_commit"]),
    ]


def _stop_conditions(payload: dict[str, Any], no_write_proof: dict[str, Any]) -> list[str]:
    repo_state = _as_dict(payload.get("repo_state"))
    authority_context = _as_dict(payload.get("authority_context"))
    stop_conditions: list[str] = []
    if bool(repo_state.get("dirty", False)) and bool(repo_state.get("fail_on_dirty_worktree", False)) and not bool(
        repo_state.get("dirty_allowed_for_validator_evidence_router_validation", False)
    ):
        stop_conditions.append("DIRTY_WORKTREE")
    if bool(no_write_proof.get("changed", False)):
        stop_conditions.append("WRITE_SURFACE_RISK")
    if authority_context and not bool(authority_context.get("all_required_loaded", True)):
        stop_conditions.append("AUTHORITY_CONTEXT_MISSING")
    if repo_state and not bool(repo_state.get("branch_matches_expected", True)):
        stop_conditions.append("BRANCH_MISMATCH")
    return stop_conditions


def _status(stop_conditions: list[str], no_write_proof: dict[str, Any]) -> str:
    if bool(no_write_proof.get("changed", False)):
        return "BLOCKED_BY_WRITE_SURFACE_RISK"
    if stop_conditions:
        return "BLOCKED"
    return "PASS"


def build_router_result(payload: dict[str, Any]) -> dict[str, Any]:
    exists_map = _existence_map(payload)
    validators = [_surface_entry(item, exists_map) for item in SAFE_VALIDATOR_SURFACES + PROTECTED_PREVIEW_SURFACES]
    evidence = [_surface_entry(item, exists_map) for item in EVIDENCE_SURFACES]
    excluded = [_blocked_entry(surface_id, path, exists_map) for surface_id, path in BLOCKED_SURFACES]
    no_write_proof = _as_dict(payload.get("no_write_proof"))
    source_router = _as_dict(payload.get("source_packet_router_result"))
    source_schema = _safe_str(payload.get("source_packet_router_schema") or source_router.get("schema") or SOURCE_PACKET_ROUTER_SCHEMA)
    action_recommendation = _as_dict(payload.get("action_recommendation"))
    stop_conditions = _stop_conditions(payload, no_write_proof)
    status = _status(stop_conditions, no_write_proof)

    safe_entries = validators + evidence
    chains = build_recommended_chains(safe_entries)
    next_safe_action = (
        f"Review {NEXT_SAFE_PACKET} in a separate DRY_RUN packet after this router passes validation. "
        "No APPLY execution command or protected git action is recommended by this router."
        if status == "PASS"
        else "Stop and review validator/evidence router blockers before selecting the next packet."
    )

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_utc": _safe_str(payload.get("generated_utc") or _now()),
        "repo_state": _as_dict(payload.get("repo_state")),
        "source_packet_router_schema": source_schema,
        "validator_catalog": validators,
        "evidence_sources": evidence,
        "excluded_surfaces": excluded,
        "recommended_chains": chains,
        "required_before_next_packet": [
            "Run the planning/review chain and confirm only safe read-only evidence or sanitized recommendations are trusted.",
            f"Next candidate packet may be reviewed as {NEXT_SAFE_PACKET}; this router must not generate the packet body.",
        ],
        "required_before_apply": [
            "Require a complete tokenized APPLY packet, exact allowed paths, forbidden paths, validator chain, approval authority, and stop point.",
            "Use APPLY packet chain evidence; validator PASS remains evidence only and does not approve mutation.",
        ],
        "required_before_commit": [
            "Require current Human Owner commit approval, exact changed file list, reviewed diff, cached diff review, and pre-commit chain evidence.",
            "Use protected-action previews only; router output must not recommend staging or committing commands.",
        ],
        "required_after_commit": [
            "Run post-commit read-only checks and report commit hash, files committed, validation evidence, and push status.",
            "Stop after local commit unless a separate push packet and approval exist.",
        ],
        "safety": {
            "status": status,
            "console_only": True,
            "writes_files": False,
            "writes_reports": False,
            "writes_telemetry": False,
            "writes_packet_drafts": False,
            "outputs_packet_body": False,
            "mutates_registry": False,
            "mutates_queue": False,
            "mutates_locks": False,
            "mutates_approvals": False,
            "writes_relay": False,
            "starts_runtime": False,
            "launches_workers": False,
            "protected_action_recommended": False,
            "commands_sanitized": True,
            "secrets_or_env_access": False,
            "broker_or_live_trading": False,
            "next_safe_packet": NEXT_SAFE_PACKET,
            "action_recommendation_command": sanitize_command_field(action_recommendation.get("recommended_command")),
        },
        "no_write_proof": no_write_proof,
        "stop_conditions": stop_conditions,
        "next_safe_action": next_safe_action,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Build an AIOS validator/evidence router result from JSON evidence.")
    parser.add_argument("--payload-base64", default="")
    args = parser.parse_args()
    if args.payload_base64:
        payload_text = base64.b64decode(args.payload_base64.encode("ascii")).decode("utf-8")
    else:
        payload_text = sys.stdin.read()
    result = build_router_result(json.loads(payload_text))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["safety"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(_main())
