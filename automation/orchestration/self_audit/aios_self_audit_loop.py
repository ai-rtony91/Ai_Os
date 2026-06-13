"""Pure AI_OS self-audit loop classification logic.

The PowerShell runner gathers repo and orchestration evidence. This module only
classifies that evidence, ranks inert packet IDs, and returns a JSON-ready
dictionary. It writes no files, starts no workers, and emits no executable
packet text.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_SELF_AUDIT_LOOP_RESULT.v1"
MODE = "DRY_RUN_READ_ONLY"

DEFAULT_CANDIDATE_PACKET_IDS = [
    "AIOS-SELF-DEVELOPMENT-PACKET-ROUTER-DRYRUN-V1",
    "AIOS-VALIDATOR-EVIDENCE-ROUTER-DRYRUN-V1",
    "AIOS-DAY-NIGHT-SUPERVISOR-READINESS-DRYRUN-V1",
    "AIOS-DASHBOARD-DATA-CONTRACT-REVIEW-DRYRUN-V1",
    "AIOS-DASHBOARD-LAYER-TAXONOMY-DOCS-APPLY-V1",
]

BLOCKED_COMMAND_PATTERNS = [
    r"\bgit\s+add\b",
    r"\bgit\s+commit\b",
    r"\bgit\s+push\b",
    r"\bgh\s+pr\b",
    r"\bgit\s+merge\b",
    r"\bapply\b",
    r"\bmode\s+apply\b",
    r"\bnew-aiosrelaymessage\b",
    r"\bnew-aioscodexreportrelayitem\b",
    r"\binvoke-aiosautonomyloop\b",
    r"\binvoke-aiosautonomycontrolplane\b",
    r"\binvoke-aiosexactcommitpackage\b",
    r"\bupdate-aiosproductionreadout\b",
    r"\bnew-aiosreport\b",
    r"\bbroker\b",
    r"\boanda\b",
    r"\bwebhook\b",
    r"\border\b",
    r"\blive trading\b",
    r"\bsecret\b",
    r"\.env\b",
]

PROTECTED_PACKET_TERMS = {
    "APPLY",
    "BROKER",
    "OANDA",
    "WEBHOOK",
    "ORDER",
    "LIVE",
    "TRADING",
    "RUNTIME",
    "WORKER-LAUNCH",
    "SCHEDULER",
    "DAEMON",
    "COMMIT",
    "PUSH",
    "MERGE",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def command_is_safe_to_surface(command: str) -> bool:
    text = (command or "").strip().lower()
    if not text:
        return False
    return not any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in BLOCKED_COMMAND_PATTERNS)


def sanitize_recommendation(value: Any) -> dict[str, Any]:
    command = str(value or "").strip()
    if command_is_safe_to_surface(command):
        return {
            "safe_to_surface": True,
            "display_text": command,
            "blocked_reason": "",
        }
    return {
        "safe_to_surface": False,
        "display_text": "Sanitized: command recommendation withheld; review packet ID only.",
        "blocked_reason": "command_or_protected_action_not_surfaceable",
    }


def classify_complete_idle(discovery: dict[str, Any], next_task: dict[str, Any]) -> dict[str, Any]:
    classification = str(discovery.get("no_ready_stage_classification") or "UNKNOWN")
    return {
        "overall_readiness": str(discovery.get("overall_readiness") or next_task.get("overall_readiness") or "UNKNOWN"),
        "no_ready_stage_detected": bool(discovery.get("no_ready_stage_detected", False)),
        "classification": classification,
        "idle_allowed": bool(discovery.get("idle_allowed", False)),
        "next_stage_planning_required": bool(discovery.get("next_stage_planning_required", False)),
        "registry_inconsistency_detected": bool(discovery.get("registry_inconsistency_detected", False)),
        "reason": str(discovery.get("no_ready_stage_classification_reason") or discovery.get("reason") or ""),
    }


def classify_candidate_packet(packet_id: str) -> dict[str, Any]:
    packet = str(packet_id or "").strip()
    upper = packet.upper()
    mode = "DRY_RUN" if "DRYRUN" in upper or "DRY-RUN" in upper else "APPLY" if "APPLY" in upper else "UNKNOWN"
    block_reasons: list[str] = []

    if mode != "DRY_RUN":
        block_reasons.append("not_dry_run")
    for term in sorted(PROTECTED_PACKET_TERMS):
        if term in upper and not (term == "APPLY" and mode == "DRY_RUN"):
            block_reasons.append(f"protected_term_{term.lower().replace('-', '_')}")

    if "SELF-DEVELOPMENT" in upper or "SELF-AUDIT" in upper:
        domain = "SELF_DEVELOPMENT"
        domain_score = 100
    elif "VALIDATOR" in upper:
        domain = "VALIDATOR_EVIDENCE"
        domain_score = 80
    elif "SUPERVISOR" in upper:
        domain = "SUPERVISOR_READINESS"
        domain_score = 60
    elif "DASHBOARD" in upper:
        domain = "DASHBOARD_REVIEW"
        domain_score = 20
    else:
        domain = "UNKNOWN"
        domain_score = 10

    if "ROUTER" in upper:
        domain_score += 12
    if "REVIEW" in upper or "READINESS" in upper:
        domain_score += 8
    if mode == "DRY_RUN":
        domain_score += 20
    if block_reasons:
        domain_score -= 500

    return {
        "packet_id": packet,
        "mode": mode,
        "domain": domain,
        "blocked": bool(block_reasons),
        "block_reasons": block_reasons,
        "rank_score": domain_score,
        "intent": _packet_intent(packet, domain, mode),
    }


def _packet_intent(packet_id: str, domain: str, mode: str) -> str:
    if domain == "SELF_DEVELOPMENT":
        return "Review the next self-development routing surface as a no-write DRY_RUN packet."
    if domain == "VALIDATOR_EVIDENCE":
        return "Review validator evidence routing before broader automation."
    if domain == "SUPERVISOR_READINESS":
        return "Review day/night supervisor readiness without enabling runtime autonomy."
    if domain == "DASHBOARD_REVIEW":
        return "Review dashboard data or taxonomy only after autonomy routing is clearer."
    return f"Review candidate packet metadata in {mode} mode."


def rank_candidate_packets(packet_ids: list[str] | None = None, max_candidates: int = 5) -> list[dict[str, Any]]:
    candidates = [classify_candidate_packet(packet_id) for packet_id in (packet_ids or DEFAULT_CANDIDATE_PACKET_IDS)]
    candidates.sort(key=lambda item: (-int(item["rank_score"]), str(item["packet_id"])))
    for index, item in enumerate(candidates[: max(0, max_candidates)], start=1):
        item["rank"] = index
    return candidates[: max(0, max_candidates)]


def _build_findings(
    repo_state: dict[str, Any],
    complete_idle_state: dict[str, Any],
    recommendation: dict[str, Any],
    no_write_proof: dict[str, Any],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    findings.append(
        {
            "id": "AUTHORITY_CONTEXT",
            "severity": "INFO",
            "classification": "AUTHORITY_CONTEXT_LOADED",
            "summary": "Authority files were checked before self-audit classification.",
        }
    )

    if bool(repo_state.get("dirty")) and not bool(repo_state.get("dirty_allowed_for_self_validation")):
        findings.append(
            {
                "id": "DIRTY_WORKTREE",
                "severity": "BLOCKER",
                "classification": "DIRTY_WORKTREE",
                "summary": "Worktree is dirty; self-audit must stop unless dirty-state review is explicit.",
            }
        )

    if complete_idle_state.get("classification") == "COMPLETE_IDLE":
        findings.append(
            {
                "id": "COMPLETE_IDLE",
                "severity": "INFO",
                "classification": "COMPLETE_IDLE",
                "summary": "No READY stage or active blocker is present; AIOS may idle or request planning review.",
            }
        )
    elif complete_idle_state.get("registry_inconsistency_detected"):
        findings.append(
            {
                "id": "REGISTRY_INCONSISTENCY",
                "severity": "BLOCKER",
                "classification": "REGISTRY_INCONSISTENCY",
                "summary": "Campaign registry inconsistency detected; stop before recommendations.",
            }
        )
    else:
        findings.append(
            {
                "id": "NEXT_STAGE_PLANNING",
                "severity": "REVIEW",
                "classification": "NO_READY_STAGE_PLANNING_GAP",
                "summary": "No READY stage is selectable; planning review may be needed.",
            }
        )

    if str(recommendation.get("packet_status") or "") == "no_active_packet":
        findings.append(
            {
                "id": "NO_ACTIVE_PACKET",
                "severity": "INFO",
                "classification": "NO_ACTIVE_PACKET",
                "summary": "Recommendation surface reports no active packet.",
            }
        )

    sanitized = sanitize_recommendation(recommendation.get("recommended_command"))
    if not sanitized["safe_to_surface"]:
        findings.append(
            {
                "id": "RECOMMENDED_COMMAND_SANITIZED",
                "severity": "INFO",
                "classification": "SURFACE_COMMAND_SANITIZED",
                "summary": "An executable command field was withheld from next-action output.",
            }
        )

    if bool(no_write_proof.get("changed")):
        findings.append(
            {
                "id": "NO_WRITE_PROOF",
                "severity": "BLOCKER",
                "classification": "WRITE_SURFACE_RISK",
                "summary": "Before/after no-write proof detected a forbidden delta.",
            }
        )
    else:
        findings.append(
            {
                "id": "NO_WRITE_PROOF",
                "severity": "INFO",
                "classification": "NO_WRITE_PROOF_PASS",
                "summary": "Before/after no-write proof found no file-state deltas.",
            }
        )
    return findings


def _gap_classifications(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "classification": str(item["classification"]),
            "severity": str(item["severity"]),
            "source_finding": str(item["id"]),
        }
        for item in findings
    ]


def _safety_status(findings: list[dict[str, Any]], no_write_proof: dict[str, Any]) -> str:
    if bool(no_write_proof.get("changed")):
        return "BLOCKED_BY_WRITE_SURFACE_RISK"
    if any(item.get("severity") == "BLOCKER" for item in findings):
        return "BLOCKED"
    return "PASS"


def build_self_audit_result(payload: dict[str, Any]) -> dict[str, Any]:
    repo_state = _as_dict(payload.get("repo_state"))
    authority_context = _as_dict(payload.get("authority_context"))
    evidence = _as_dict(payload.get("evidence"))
    discovery = _as_dict(evidence.get("no_ready_stage_discovery"))
    next_task = _as_dict(evidence.get("campaign_next_task"))
    recommendation = _as_dict(evidence.get("action_recommendation"))
    no_write_proof = _as_dict(payload.get("no_write_proof"))
    max_candidates = int(payload.get("max_candidate_packets") or 5)

    complete_idle_state = classify_complete_idle(discovery, next_task)
    candidate_packets = rank_candidate_packets(
        [str(item) for item in _as_list(payload.get("candidate_packet_ids")) if str(item).strip()],
        max_candidates=max_candidates,
    )
    recommended_next_packet = next((item for item in candidate_packets if not item["blocked"]), None)
    findings = _build_findings(repo_state, complete_idle_state, recommendation, no_write_proof)
    status = _safety_status(findings, no_write_proof)

    stop_conditions = [
        item["classification"]
        for item in findings
        if item.get("severity") == "BLOCKER"
    ]
    if status == "PASS":
        next_safe_action = "Review the recommended DRY_RUN packet ID in a separate supervised planning packet; do not APPLY or execute it from this runner."
    else:
        next_safe_action = "Stop and review blocker evidence before any self-audit continuation."

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_utc": str(payload.get("generated_utc") or _now()),
        "repo_state": repo_state,
        "authority_context": authority_context,
        "complete_idle_state": complete_idle_state,
        "surface_inventory": _as_dict(payload.get("surface_inventory")),
        "blocked_surfaces": _as_list(payload.get("blocked_surfaces")),
        "safe_surfaces_used": _as_list(payload.get("safe_surfaces_used")),
        "findings": findings,
        "gap_classifications": _gap_classifications(findings),
        "candidate_packets": candidate_packets,
        "recommended_next_packet": recommended_next_packet,
        "stop_conditions": stop_conditions,
        "safety": {
            "status": status,
            "console_only": True,
            "writes_files": False,
            "writes_reports": False,
            "writes_telemetry": False,
            "writes_packets": False,
            "mutates_registry": False,
            "mutates_queue": False,
            "mutates_locks": False,
            "mutates_approvals": False,
            "starts_runtime": False,
            "launches_workers": False,
            "protected_git_action": False,
            "broker_or_live_trading": False,
            "no_write_proof": no_write_proof,
        },
        "next_safe_action": next_safe_action,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Build an AIOS self-audit loop result from supplied JSON evidence.")
    parser.add_argument("--payload-base64", default="")
    args = parser.parse_args()
    if args.payload_base64:
        payload_text = base64.b64decode(args.payload_base64.encode("ascii")).decode("utf-8")
    else:
        payload_text = sys.stdin.read()
    result = build_self_audit_result(json.loads(payload_text))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["safety"]["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(_main())
