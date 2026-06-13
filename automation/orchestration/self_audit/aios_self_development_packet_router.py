"""Pure AIOS self-development packet router logic.

The PowerShell wrapper gathers read-only evidence. This module only classifies
candidate packet IDs, sanitizes executable fields, ranks safe candidates, and
returns a JSON-ready dictionary. It writes no files and starts no processes.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_SELF_DEVELOPMENT_PACKET_ROUTER_RESULT.v1"
SOURCE_SELF_AUDIT_SCHEMA = "AIOS_SELF_AUDIT_LOOP_RESULT.v1"
MODE = "DRY_RUN_READ_ONLY"

CLASSIFICATIONS = {
    "SAFE_DRY_RUN_REVIEW",
    "SAFE_DESIGN_REVIEW",
    "APPLY_REQUIRES_HUMAN_APPROVAL",
    "BLOCKED_WRITES_PACKET",
    "BLOCKED_READY_STAGE_MUTATION",
    "BLOCKED_REGISTRY_MUTATION",
    "BLOCKED_PROTECTED_ACTION",
    "BLOCKED_RUNTIME_OR_WORKER",
    "BLOCKED_LIVE_TRADING_OR_BROKER",
    "BLOCKED_SECRET_OR_ENV",
    "UNKNOWN_NEEDS_REVIEW",
}

DEFAULT_CANDIDATE_PACKET_IDS = [
    "AIOS-VALIDATOR-EVIDENCE-ROUTER-DRYRUN-V1",
    "AIOS-DAY-NIGHT-SUPERVISOR-READINESS-DRYRUN-V1",
    "AIOS-DASHBOARD-DATA-CONTRACT-REVIEW-DRYRUN-V1",
    "AIOS-DASHBOARD-LAYER-TAXONOMY-DOCS-APPLY-V1",
]

CURRENT_ROUTER_PACKET_TERMS = (
    "SELF-DEVELOPMENT-PACKET-ROUTER",
    "SELF_DEVELOPMENT_PACKET_ROUTER",
)

PACKET_ID_PATTERN = re.compile(r"^(AIOS|PKT)-[A-Z0-9][A-Z0-9_-]*(?:-[A-Z0-9][A-Z0-9_-]*)*$")
UNSAFE_PACKET_CHARS = re.compile(r"[\s/\\:;&|`$<>]")

COMMAND_BLOCK_PATTERNS = [
    r"\bgit\s+add\b",
    r"\bgit\s+commit\b",
    r"\bgit\s+push\b",
    r"\bgit\s+merge\b",
    r"\bgit\s+reset\b",
    r"\bgit\s+clean\b",
    r"\bgh\s+pr\b",
    r"\bapply\b",
    r"\bmode\s+apply\b",
    r"\bnew-aiosrelaymessage\b",
    r"\bnew-aioscodexreportrelayitem\b",
    r"\bnew-aioscodexpacket\b",
    r"\bnew-aioscapabilitypacketdraft\b",
    r"\bget-aioscodexpacketdraftpreview\b",
    r"\bconvert-aioscontinuationplantoproposedpacket\b",
    r"\binvoke-aiosautonomyloop\b",
    r"\binvoke-aiosautonomycontrolplane\b",
    r"\binvoke-aiosruntime\b",
    r"\bscheduler\b",
    r"\bdaemon\b",
    r"\bworker\b",
    r"\bbroker\b",
    r"\boanda\b",
    r"\bwebhook\b",
    r"\border\b",
    r"\blive[-\s]?trading\b",
    r"\bsecret\b",
    r"\btoken\b",
    r"\bapi[-_ ]?key\b",
    r"\.env\b",
    r"code[xX].*prompt",
    r"execution.*token",
]

PACKET_WRITE_TERMS = (
    "PACKET-DRAFT",
    "PACKET-DRAFTER",
    "PROPOSED-PACKET",
    "WORK-PACKET",
    "WRITE-PACKET",
    "WRITES-PACKET",
    "PACKET-WRITER",
)
READY_STAGE_TERMS = (
    "READY-STAGE",
    "CREATE-READY",
    "READY-CREATION",
    "REOPEN-COMPLETE",
    "REOPEN-COMPLETED",
)
REGISTRY_TERMS = (
    "REGISTRY-MUTATION",
    "MUTATE-REGISTRY",
    "CAMPAIGN-STATUS",
    "STATUS-MUTATION",
)
PROTECTED_TERMS = (
    "COMMIT",
    "PUSH",
    "MERGE",
    "PROTECTED-ACTION",
    "GIT-ADD",
    "PR-CREATE",
    "PR-MERGE",
)
RUNTIME_TERMS = (
    "RUNTIME",
    "WORKER-LAUNCH",
    "WORKER",
    "SCHEDULER",
    "DAEMON",
    "WATCHDOG",
    "QUEUE",
    "LOCK",
    "APPROVAL",
)
LIVE_TRADING_TERMS = (
    "BROKER",
    "OANDA",
    "WEBHOOK",
    "ORDER",
    "LIVE-TRADING",
    "LIVETRADING",
    "TRADING-LIVE",
    "FOREX-LIVE",
)
SECRET_TERMS = (
    "SECRET",
    "SECRETS",
    "TOKEN",
    "API-KEY",
    "API_KEY",
    "ENV",
    "DOTENV",
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _upper(value: Any) -> str:
    return _safe_str(value).upper()


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _contains_forbidden_marker(text: str) -> bool:
    lowered = text.lower()
    return bool(re.search(r"code[xX].*prompt", text)) or ("ai_os" in lowered and "execution" in lowered and "token" in lowered)


def _candidate_mode(packet_id: str) -> str:
    upper = packet_id.upper()
    if "DRYRUN" in upper or "DRY-RUN" in upper or "DRY_RUN" in upper:
        return "DRY_RUN"
    if "APPLY" in upper:
        return "APPLY"
    return "UNKNOWN"


def validate_candidate_packet_id(packet_id: Any) -> dict[str, Any]:
    raw = _safe_str(packet_id)
    upper = raw.upper()
    reasons: list[str] = []
    if not raw:
        reasons.append("empty_packet_id")
    if len(raw) > 160:
        reasons.append("packet_id_too_long")
    if raw != upper:
        reasons.append("packet_id_must_be_uppercase")
    if UNSAFE_PACKET_CHARS.search(raw):
        reasons.append("packet_id_contains_unsafe_character")
    if _contains_forbidden_marker(raw):
        reasons.append("packet_id_contains_forbidden_marker")
    if not PACKET_ID_PATTERN.match(raw):
        reasons.append("packet_id_pattern_mismatch")
    if "-V" not in upper:
        reasons.append("packet_id_missing_version")
    return {
        "valid": not reasons,
        "packet_id": raw if not reasons else "[invalid_candidate_id]",
        "raw_upper": upper,
        "reasons": reasons,
    }


def command_is_safe_to_surface(command: Any) -> bool:
    text = _safe_str(command)
    if not text:
        return False
    if "\n" in text or "\r" in text:
        return False
    return not any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in COMMAND_BLOCK_PATTERNS)


def sanitize_command_field(value: Any) -> dict[str, Any]:
    command = _safe_str(value)
    if command_is_safe_to_surface(command):
        return {
            "safe_to_surface": True,
            "display_text": command,
            "blocked_reason": "",
        }
    return {
        "safe_to_surface": False,
        "display_text": "Sanitized: executable recommendation withheld; review packet ID and intent only.",
        "blocked_reason": "command_or_protected_action_not_surfaceable",
    }


def _packet_intent(packet_id: str, classification: str) -> str:
    upper = packet_id.upper()
    if classification.startswith("BLOCKED"):
        return "Blocked candidate; do not route without separate human review."
    if classification == "APPLY_REQUIRES_HUMAN_APPROVAL":
        return "Implementation packet may be reviewed later, but this router cannot recommend applying it."
    if "VALIDATOR" in upper or "EVIDENCE" in upper:
        return "Review validator and evidence routing before broader self-development automation."
    if "SUPERVISOR" in upper:
        return "Review day/night supervisor readiness without enabling runtime autonomy."
    if "DASHBOARD" in upper:
        return "Review dashboard contract or taxonomy only after autonomy routing dependencies are clearer."
    if "DESIGN" in upper or "REVIEW" in upper:
        return "Review the no-write design packet and stop before implementation."
    return "Review candidate packet metadata without writing packet drafts or executing work."


def classify_candidate_packet(packet_id: Any) -> dict[str, Any]:
    validation = validate_candidate_packet_id(packet_id)
    packet = validation["packet_id"]
    upper = validation["raw_upper"]
    mode = _candidate_mode(upper)
    reasons = list(validation["reasons"])

    if reasons:
        classification = "UNKNOWN_NEEDS_REVIEW"
    elif _contains_any(upper, PACKET_WRITE_TERMS):
        classification = "BLOCKED_WRITES_PACKET"
        reasons.append("packet_write_surface")
    elif _contains_any(upper, READY_STAGE_TERMS):
        classification = "BLOCKED_READY_STAGE_MUTATION"
        reasons.append("ready_stage_mutation")
    elif _contains_any(upper, REGISTRY_TERMS):
        classification = "BLOCKED_REGISTRY_MUTATION"
        reasons.append("registry_mutation")
    elif _contains_any(upper, PROTECTED_TERMS):
        classification = "BLOCKED_PROTECTED_ACTION"
        reasons.append("protected_action")
    elif _contains_any(upper, RUNTIME_TERMS):
        classification = "BLOCKED_RUNTIME_OR_WORKER"
        reasons.append("runtime_worker_scheduler_or_state_mutation")
    elif _contains_any(upper, LIVE_TRADING_TERMS):
        classification = "BLOCKED_LIVE_TRADING_OR_BROKER"
        reasons.append("live_trading_or_broker")
    elif _contains_any(upper, SECRET_TERMS):
        classification = "BLOCKED_SECRET_OR_ENV"
        reasons.append("secret_or_env")
    elif mode == "APPLY":
        classification = "APPLY_REQUIRES_HUMAN_APPROVAL"
        reasons.append("apply_requires_human_approval")
    elif mode != "DRY_RUN":
        classification = "UNKNOWN_NEEDS_REVIEW"
        reasons.append("unknown_mode")
    elif "DESIGN" in upper or "REVIEW" in upper:
        classification = "SAFE_DESIGN_REVIEW"
    else:
        classification = "SAFE_DRY_RUN_REVIEW"

    blocked = classification.startswith("BLOCKED") or classification in {
        "APPLY_REQUIRES_HUMAN_APPROVAL",
        "UNKNOWN_NEEDS_REVIEW",
    }
    return {
        "packet_id": packet,
        "classification": classification,
        "mode": mode,
        "blocked": blocked,
        "block_reasons": reasons,
        "rank_score": _rank_score(upper, classification, blocked),
        "intent": _packet_intent(packet, classification),
        "valid_candidate_id": bool(validation["valid"]),
    }


def _rank_score(upper_packet_id: str, classification: str, blocked: bool) -> int:
    if blocked:
        return -1000

    score = 100
    if classification == "SAFE_DESIGN_REVIEW":
        score += 20
    if "VALIDATOR" in upper_packet_id:
        score += 80
    if "EVIDENCE" in upper_packet_id:
        score += 35
    if "ROUTER" in upper_packet_id:
        score += 25
    if "SUPERVISOR" in upper_packet_id:
        score += 45
    if "READINESS" in upper_packet_id:
        score += 15
    if "SELF-DEVELOPMENT" in upper_packet_id or "SELF-AUDIT" in upper_packet_id:
        score += 30
    if "DASHBOARD" in upper_packet_id:
        score -= 30
    if "UI" in upper_packet_id or "VISUAL" in upper_packet_id:
        score -= 25
    if "DOCS" in upper_packet_id:
        score -= 10
    return score


def _candidate_ids_from_self_audit(self_audit: dict[str, Any]) -> list[str]:
    candidates: list[str] = []
    for item in _as_list(self_audit.get("candidate_packets")):
        if isinstance(item, dict):
            packet_id = _safe_str(item.get("packet_id"))
        else:
            packet_id = _safe_str(item)
        if packet_id:
            candidates.append(packet_id)
    recommended = _as_dict(self_audit.get("recommended_next_packet"))
    packet_id = _safe_str(recommended.get("packet_id"))
    if packet_id:
        candidates.append(packet_id)
    return candidates


def _candidate_ids_from_evidence(campaign_no_ready: dict[str, Any], campaign_next_task: dict[str, Any]) -> list[str]:
    candidates: list[str] = []
    next_packet = _safe_str(campaign_next_task.get("next_packet_candidate"))
    if next_packet:
        candidates.append(next_packet)
    for item in _as_list(campaign_no_ready.get("candidate_next_stage_options")):
        if isinstance(item, dict):
            packet_id = _safe_str(item.get("next_packet_candidate") or item.get("packet_id"))
            if packet_id:
                candidates.append(packet_id)
    return candidates


def _dedupe_candidate_ids(candidate_ids: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for packet_id in candidate_ids:
        upper = _upper(packet_id)
        if not upper:
            continue
        if any(term in upper for term in CURRENT_ROUTER_PACKET_TERMS):
            continue
        if upper in seen:
            continue
        seen.add(upper)
        result.append(upper)
    return result


def rank_candidate_packets(candidate_ids: list[str] | None = None, max_candidates: int = 5) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    classified = [classify_candidate_packet(packet_id) for packet_id in (candidate_ids or DEFAULT_CANDIDATE_PACKET_IDS)]
    safe = [item for item in classified if not item["blocked"]]
    blocked = [item for item in classified if item["blocked"]]
    safe.sort(key=lambda item: (-int(item["rank_score"]), str(item["packet_id"])))
    blocked.sort(key=lambda item: (str(item["classification"]), str(item["packet_id"])))
    for index, item in enumerate(safe[: max(0, max_candidates)], start=1):
        item["rank"] = index
    return safe[: max(0, max_candidates)], blocked


def _input_summary(
    self_audit: dict[str, Any],
    campaign_no_ready: dict[str, Any],
    campaign_next_task: dict[str, Any],
    action_recommendation: dict[str, Any],
) -> dict[str, Any]:
    command = sanitize_command_field(action_recommendation.get("recommended_command"))
    recommended = _as_dict(self_audit.get("recommended_next_packet"))
    return {
        "self_audit_status": _safe_str(_as_dict(self_audit.get("safety")).get("status") or "UNKNOWN"),
        "self_audit_recommended_packet_id": _safe_str(recommended.get("packet_id")),
        "campaign_overall_readiness": _safe_str(
            campaign_no_ready.get("overall_readiness") or campaign_next_task.get("overall_readiness") or "UNKNOWN"
        ),
        "no_ready_stage_classification": _safe_str(campaign_no_ready.get("no_ready_stage_classification") or "UNKNOWN"),
        "registry_inconsistency_detected": bool(campaign_no_ready.get("registry_inconsistency_detected", False)),
        "campaign_next_packet_candidate_present": bool(_safe_str(campaign_next_task.get("next_packet_candidate"))),
        "action_packet_status": _safe_str(action_recommendation.get("packet_status") or "UNKNOWN"),
        "action_recommendation_command": command,
    }


def _confidence(
    source_schema_valid: bool,
    no_write_proof: dict[str, Any],
    input_summary: dict[str, Any],
    recommended_packet: dict[str, Any] | None,
) -> float:
    if recommended_packet is None:
        return 0.0
    score = 0.0
    if source_schema_valid:
        score += 0.30
    if not bool(no_write_proof.get("changed", False)):
        score += 0.25
    if _safe_str(input_summary.get("self_audit_status")) == "PASS":
        score += 0.15
    if not bool(input_summary.get("registry_inconsistency_detected", False)):
        score += 0.10
    if recommended_packet and not bool(recommended_packet.get("blocked", True)):
        score += 0.15
    packet_id = _upper(recommended_packet.get("packet_id") if recommended_packet else "")
    if "VALIDATOR" in packet_id or "EVIDENCE" in packet_id:
        score += 0.05
    return round(min(score, 0.95), 2)


def _safety_status(stop_conditions: list[str], no_write_proof: dict[str, Any]) -> str:
    if bool(no_write_proof.get("changed", False)):
        return "BLOCKED_BY_WRITE_SURFACE_RISK"
    if stop_conditions:
        return "BLOCKED"
    return "PASS"


def build_router_result(payload: dict[str, Any]) -> dict[str, Any]:
    self_audit = _as_dict(payload.get("self_audit_result"))
    campaign_no_ready = _as_dict(payload.get("campaign_no_ready"))
    campaign_next_task = _as_dict(payload.get("campaign_next_task"))
    action_recommendation = _as_dict(payload.get("action_recommendation"))
    repo_state = _as_dict(payload.get("repo_state"))
    no_write_proof = _as_dict(payload.get("no_write_proof"))
    max_candidates = int(payload.get("max_candidate_packets") or 5)

    source_schema = _safe_str(self_audit.get("schema"))
    source_schema_valid = source_schema == SOURCE_SELF_AUDIT_SCHEMA
    candidate_ids = _dedupe_candidate_ids(
        DEFAULT_CANDIDATE_PACKET_IDS
        + _candidate_ids_from_self_audit(self_audit)
        + _candidate_ids_from_evidence(campaign_no_ready, campaign_next_task)
    )
    candidate_packets, blocked_candidates = rank_candidate_packets(candidate_ids, max_candidates=max_candidates)
    recommended_packet = candidate_packets[0] if candidate_packets else None
    summary = _input_summary(self_audit, campaign_no_ready, campaign_next_task, action_recommendation)
    confidence = _confidence(source_schema_valid, no_write_proof, summary, recommended_packet)

    stop_conditions: list[str] = []
    if not source_schema_valid:
        stop_conditions.append("SOURCE_SELF_AUDIT_SCHEMA_INVALID")
    if (
        bool(repo_state.get("dirty", False))
        and bool(repo_state.get("fail_on_dirty_worktree", False))
        and not bool(repo_state.get("dirty_allowed_for_router_validation", False))
    ):
        stop_conditions.append("DIRTY_WORKTREE")
    if bool(no_write_proof.get("changed", False)):
        stop_conditions.append("WRITE_SURFACE_RISK")
    if bool(summary.get("registry_inconsistency_detected", False)):
        stop_conditions.append("REGISTRY_INCONSISTENCY")
    if recommended_packet is None:
        stop_conditions.append("NO_SAFE_PACKET_CANDIDATE")
    if confidence < 0.70:
        stop_conditions.append("CONFIDENCE_INSUFFICIENT")

    status = _safety_status(stop_conditions, no_write_proof)
    if status == "PASS":
        next_safe_action = (
            "Review the recommended packet ID and intent in a separate supervised planning packet. "
            "No implementation command or protected action is recommended by this router."
        )
    else:
        next_safe_action = "Stop and review packet-router blockers before selecting a next packet."

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_utc": _safe_str(payload.get("generated_utc") or _now()),
        "source_self_audit_schema": source_schema,
        "repo_state": repo_state,
        "input_summary": summary,
        "candidate_packets": candidate_packets,
        "blocked_candidates": blocked_candidates,
        "ranking_basis": {
            "rules": [
                "hard_block_unsafe_protected_live_secret_runtime_write_candidates",
                "prefer_dry_run_review_and_design_before_implementation",
                "prefer_autonomy_self_development_before_dashboard_visuals",
                "prefer_validator_evidence_routing_before_supervisor_readiness",
                "prefer_dependency_complete_validator_backed_work",
                "withhold_executable_commands_and packet bodies",
            ],
            "max_candidate_packets": max_candidates,
            "confidence_threshold": 0.70,
        },
        "recommended_packet": recommended_packet,
        "confidence": confidence,
        "approval_required_before_apply": True,
        "safety": {
            "status": status,
            "console_only": True,
            "writes_files": False,
            "writes_packet_drafts": False,
            "writes_proposed_packets": False,
            "creates_ready_stage": False,
            "mutates_registry": False,
            "mutates_queue": False,
            "mutates_locks": False,
            "mutates_approvals": False,
            "starts_runtime": False,
            "launches_workers": False,
            "protected_action_recommended": False,
            "broker_or_live_trading": False,
            "secrets_or_env_access": False,
        },
        "stop_conditions": stop_conditions,
        "no_write_proof": no_write_proof,
        "next_safe_action": next_safe_action,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description="Build an AIOS self-development packet router result from JSON evidence.")
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
