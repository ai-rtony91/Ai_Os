"""DRY_RUN-only Morning Brief synthesis for AI_OS orchestration evidence.

This module reads existing JSON or JSONL evidence and prints one compact
Morning Brief object. It does not write files, launch child processes, mutate
packets, mutate approvals, start workers, schedule work, or control runtime
state.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_MORNING_BRIEF_SYNTHESIS.v1"
MODE = "DRY_RUN"

STATUS_ALIASES = {
    "PASS": "PASS",
    "READY": "PASS",
    "SAFE_TO_COMMIT": "PASS",
    "SAFE_TO_PUSH": "PASS",
    "INFO": "PASS",
    "RECOMMENDED": "REVIEW",
    "REVIEW": "REVIEW",
    "WARN": "REVIEW",
    "WARNING": "REVIEW",
    "REVIEW_REQUIRED": "REVIEW",
    "HUMAN_APPROVAL_REQUIRED": "REVIEW",
    "PENDING": "REVIEW",
    "PENDING_REVIEW": "REVIEW",
    "WAITING_APPROVAL": "REVIEW",
    "AWAITING_APPROVAL": "REVIEW",
    "FAIL": "BLOCKED",
    "FAILED": "BLOCKED",
    "BLOCKER": "BLOCKED",
    "BLOCKED": "BLOCKED",
    "STOP": "BLOCKED",
    "STOPPED": "BLOCKED",
    "ERROR": "BLOCKED",
    "MISSING": "UNKNOWN",
    "UNKNOWN": "UNKNOWN",
    "NO_ACTION": "UNKNOWN",
    "NOT_RUN": "NOT_RUN",
}

SEVERITY_ALIASES = {
    "PASS": "INFO",
    "READY": "INFO",
    "INFO": "INFO",
    "RECOMMENDED": "REVIEW",
    "REVIEW": "REVIEW",
    "WARN": "REVIEW",
    "WARNING": "REVIEW",
    "REVIEW_REQUIRED": "REVIEW",
    "HUMAN_APPROVAL_REQUIRED": "REVIEW",
    "PENDING": "REVIEW",
    "PENDING_REVIEW": "REVIEW",
    "FAIL": "BLOCKED",
    "FAILED": "BLOCKED",
    "BLOCKER": "BLOCKED",
    "BLOCKED": "BLOCKED",
    "STOP": "BLOCKED",
    "STOPPED": "BLOCKED",
    "ERROR": "BLOCKED",
    "MISSING": "UNKNOWN",
    "UNKNOWN": "UNKNOWN",
    "NO_ACTION": "UNKNOWN",
    "NOT_RUN": "UNKNOWN",
}

SEVERITY_RANK = {
    "BLOCKED": 0,
    "REVIEW": 1,
    "INFO": 2,
    "UNKNOWN": 3,
}

PROTECTED_TERMS = (
    "commit",
    "push",
    "merge",
    "approval",
    "governance",
    "protected",
    "runtime",
    "packet movement",
    "worker launch",
    "scheduler",
    "trading",
    "broker",
    "oanda",
    "secret",
    "credential",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_token(value: Any, aliases: dict[str, str], default: str) -> str:
    if value is None:
        return default
    token = str(value).strip().upper().replace("-", "_").replace(" ", "_")
    if not token:
        return default
    return aliases.get(token, default)


def normalize_status(value: Any) -> str:
    return normalize_token(value, STATUS_ALIASES, "UNKNOWN")


def normalize_severity(value: Any) -> str:
    return normalize_token(value, SEVERITY_ALIASES, "UNKNOWN")


def boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().upper() in {"TRUE", "YES", "Y", "1", "REQUIRED"}
    return bool(value)


def rank_key(item: dict[str, Any]) -> tuple[int, str]:
    severity = normalize_severity(item.get("severity") or item.get("status"))
    return (SEVERITY_RANK.get(severity, 3), str(item.get("source_path", "")))


def read_json_object(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig", errors="replace"))
    except OSError as exc:
        return {
            "source_path": str(path),
            "status": "MISSING",
            "severity": "UNKNOWN",
            "error": str(exc),
        }
    except json.JSONDecodeError as exc:
        return {
            "source_path": str(path),
            "status": "ERROR",
            "severity": "BLOCKED",
            "error": str(exc),
        }

    if isinstance(payload, dict):
        payload.setdefault("source_path", str(path))
        return payload

    return {
        "source_path": str(path),
        "status": "ERROR",
        "severity": "BLOCKED",
        "error": "JSON root must be an object.",
    }


def read_jsonl_summary(path: Path) -> dict[str, Any]:
    try:
        lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    except OSError as exc:
        return {
            "source_path": str(path),
            "status": "MISSING",
            "severity": "UNKNOWN",
            "error": str(exc),
            "event_count": 0,
            "invalid_line_count": 0,
        }

    events: list[dict[str, Any]] = []
    invalid_line_count = 0
    for line in lines:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            invalid_line_count += 1
            continue
        if isinstance(event, dict):
            events.append(event)

    blocked_events = [
        event
        for event in events
        if normalize_status(event.get("result") or event.get("status") or event.get("validation_status")) == "BLOCKED"
    ]
    review_events = [
        event
        for event in events
        if normalize_severity(event.get("risk_level") or event.get("severity")) == "REVIEW"
    ]
    last_event = events[-1] if events else {}

    return {
        "source_path": str(path),
        "status": "BLOCKED" if blocked_events else ("REVIEW" if invalid_line_count else "PASS"),
        "severity": "BLOCKED" if blocked_events else ("REVIEW" if review_events or invalid_line_count else "INFO"),
        "event_count": len(events),
        "invalid_line_count": invalid_line_count,
        "last_event_at": last_event.get("timestamp_utc") or last_event.get("ts"),
        "last_event_type": last_event.get("event_type") or last_event.get("eventType"),
        "next_safe_action": last_event.get("next_safe_action") or "Review telemetry freshness before relying on overnight state.",
    }


def contract_from_evidence(item: dict[str, Any]) -> dict[str, Any]:
    embedded = item.get("orchestration_result_contract")
    if isinstance(embedded, dict):
        embedded = dict(embedded)
        embedded.setdefault("source_path", item.get("source_path", "INLINE"))
        return embedded
    return item


def collect_values(value: Any) -> list[str]:
    if isinstance(value, dict):
        output: list[str] = []
        for nested in value.values():
            output.extend(collect_values(nested))
        return output
    if isinstance(value, list):
        output = []
        for nested in value:
            output.extend(collect_values(nested))
        return output
    if isinstance(value, str):
        return [value]
    return []


def summarize_source(item: dict[str, Any]) -> dict[str, Any]:
    contract = contract_from_evidence(item)
    status = normalize_status(
        contract.get("status")
        or contract.get("supervisor_status")
        or contract.get("result")
        or contract.get("decision")
        or contract.get("validation_status")
    )
    severity = normalize_severity(
        contract.get("severity")
        or contract.get("risk_level")
        or contract.get("repo_health", {}).get("risk_level")
        or status
    )
    source_path = str(contract.get("source_path") or item.get("source_path") or "INLINE")
    next_safe_action = str(
        contract.get("next_safe_action")
        or contract.get("recommended_first_action")
        or contract.get("recommended_command")
        or contract.get("morning_brief", {}).get("recommended_first_action")
        or "Review source evidence before protected action."
    )
    return {
        "source_path": source_path,
        "status": status,
        "severity": severity,
        "approval_required": boolish(contract.get("approval_required")),
        "commit_candidate": boolish(contract.get("commit_candidate")),
        "next_safe_action": next_safe_action,
        "raw": contract,
    }


def synthesize_validator_alerts(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    alerts: list[dict[str, Any]] = []
    for source in sources:
        raw = source["raw"]
        candidates = raw.get("validator_results") or raw.get("validator_recommendations") or []
        if not isinstance(candidates, list):
            continue
        for index, item in enumerate(candidates):
            if not isinstance(item, dict):
                continue
            status = normalize_status(item.get("status") or item.get("state") or item.get("result"))
            severity = normalize_severity(item.get("severity") or item.get("priority") or status)
            if severity == "INFO" and status == "PASS":
                continue
            alerts.append(
                {
                    "validator_id": str(item.get("validator_id") or item.get("check") or f"validator_{index + 1}"),
                    "status": status,
                    "severity": severity,
                    "source_path": source["source_path"],
                    "evidence": str(item.get("evidence") or item.get("reason") or ""),
                    "next_safe_action": str(item.get("next_safe_action") or source["next_safe_action"]),
                }
            )
    return sorted(alerts, key=rank_key)


def synthesize_approval_needed(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    approvals: list[dict[str, Any]] = []
    for source in sources:
        raw = source["raw"]
        approval_items = raw.get("approval_required")
        if isinstance(approval_items, list):
            for item in approval_items:
                if not isinstance(item, dict):
                    continue
                approvals.append(
                    {
                        "approval_type": "mutation_required",
                        "packet_id": str(item.get("packet_id") or "UNKNOWN"),
                        "severity": "REVIEW",
                        "reason": str(item.get("reason") or "Human approval required."),
                        "source_path": source["source_path"],
                        "next_safe_action": str(item.get("next_safe_action") or source["next_safe_action"]),
                    }
                )
        elif source["approval_required"]:
            approval_type = "blocked_until_fixed" if source["severity"] == "BLOCKED" else "review_only"
            approvals.append(
                {
                    "approval_type": approval_type,
                    "packet_id": str(raw.get("packet_id") or "UNKNOWN"),
                    "severity": source["severity"],
                    "reason": str(raw.get("escalation_reason") or "Human review required."),
                    "source_path": source["source_path"],
                    "next_safe_action": source["next_safe_action"],
                }
            )
    return sorted(approvals, key=rank_key)


def synthesize_stale_packets(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stale: list[dict[str, Any]] = []
    for source in sources:
        raw = source["raw"]
        for item in raw.get("stale_packets") or []:
            if not isinstance(item, dict):
                continue
            stale.append(
                {
                    "packet_id": str(item.get("packet_id") or "UNKNOWN"),
                    "state": str(item.get("state") or item.get("status") or "UNKNOWN"),
                    "severity": "REVIEW",
                    "reason": str(item.get("reason") or "Stale packet evidence was reported."),
                    "source_path": source["source_path"],
                    "next_safe_action": str(item.get("next_safe_action") or source["next_safe_action"]),
                }
            )
        if raw.get("last_event_at") is None and raw.get("event_count") == 0:
            stale.append(
                {
                    "packet_id": "TELEMETRY",
                    "state": "UNKNOWN",
                    "severity": "UNKNOWN",
                    "reason": "Telemetry ledger has no parsed events.",
                    "source_path": source["source_path"],
                    "next_safe_action": source["next_safe_action"],
                }
            )
    return sorted(stale, key=rank_key)


def synthesize_commit_candidates(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for source in sources:
        raw = source["raw"]
        raw_candidates = raw.get("commit_package_candidates")
        if isinstance(raw_candidates, list):
            for item in raw_candidates:
                if not isinstance(item, dict):
                    continue
                candidates.append(
                    {
                        "packet_id": str(item.get("packet_id") or raw.get("packet_id") or "UNKNOWN"),
                        "lane": str(item.get("lane") or "UNKNOWN"),
                        "severity": normalize_severity(item.get("status") or "REVIEW"),
                        "candidate_files": item.get("candidate_files") or item.get("recommended_files") or [],
                        "source_path": source["source_path"],
                        "next_safe_action": str(item.get("next_safe_action") or source["next_safe_action"]),
                    }
                )
        elif source["commit_candidate"]:
            candidates.append(
                {
                    "packet_id": str(raw.get("packet_id") or "UNKNOWN"),
                    "lane": str(raw.get("lane") or raw.get("worker_identity") or "UNKNOWN"),
                    "severity": source["severity"],
                    "candidate_files": raw.get("candidate_files") or [],
                    "source_path": source["source_path"],
                    "next_safe_action": source["next_safe_action"],
                }
            )
    return sorted(candidates, key=rank_key)


def synthesize_health(sources: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = [source["status"] for source in sources]
    severities = [source["severity"] for source in sources]
    status = "BLOCKED" if "BLOCKED" in statuses else ("REVIEW" if "REVIEW" in statuses else ("UNKNOWN" if "UNKNOWN" in statuses else "PASS"))
    severity = sorted(severities, key=lambda item: SEVERITY_RANK.get(item, 3))[0] if severities else "UNKNOWN"
    return {
        "status": status,
        "severity": severity,
        "source_count": len(sources),
        "blocked_source_count": sum(1 for source in sources if source["status"] == "BLOCKED"),
        "review_source_count": sum(1 for source in sources if source["status"] == "REVIEW"),
        "unknown_source_count": sum(1 for source in sources if source["status"] == "UNKNOWN"),
    }


def synthesize_next_actions(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    ranked: list[dict[str, Any]] = []
    for source in sorted(sources, key=rank_key):
        action = source["next_safe_action"]
        if action in seen:
            continue
        seen.add(action)
        ranked.append(
            {
                "rank": len(ranked) + 1,
                "severity": source["severity"],
                "action": action,
                "requires_human_approval": source["approval_required"] or source["severity"] in {"BLOCKED", "REVIEW"},
                "source_path": source["source_path"],
            }
        )
    if not ranked:
        ranked.append(
            {
                "rank": 1,
                "severity": "UNKNOWN",
                "action": "Provide DRY_RUN evidence JSON or review the existing orchestration reports.",
                "requires_human_approval": False,
                "source_path": "NO_INPUT",
            }
        )
    return ranked


def synthesize_protected_warnings(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    for source in sources:
        text = " ".join(collect_values(source["raw"])).lower()
        matched = sorted({term for term in PROTECTED_TERMS if term in text})
        if matched:
            warnings.append(
                {
                    "severity": "REVIEW",
                    "source_path": source["source_path"],
                    "matched_terms": matched,
                    "warning": "Protected action language detected; treat as planning evidence only.",
                    "next_safe_action": "Require Human Owner approval before any protected action.",
                }
            )
    return warnings


def build_summary(sources: list[dict[str, Any]]) -> dict[str, Any]:
    health = synthesize_health(sources)
    validator_alerts = synthesize_validator_alerts(sources)
    approval_needed = synthesize_approval_needed(sources)
    stale_packets = synthesize_stale_packets(sources)
    commit_candidates = synthesize_commit_candidates(sources)
    next_actions = synthesize_next_actions(sources)
    protected_warnings = synthesize_protected_warnings(sources)

    status = health["status"]
    severity = health["severity"]
    if approval_needed and status == "PASS":
        status = "REVIEW"
        severity = "REVIEW"
    if protected_warnings and severity == "INFO":
        severity = "REVIEW"

    return {
        "schema": SCHEMA,
        "mode": MODE,
        "generated_at": utc_now(),
        "status": status,
        "severity": severity,
        "overnight_summary": {
            "source_count": len(sources),
            "validator_alert_count": len(validator_alerts),
            "approval_needed_count": len(approval_needed),
            "stale_packet_count": len(stale_packets),
            "commit_package_candidate_count": len(commit_candidates),
            "protected_warning_count": len(protected_warnings),
        },
        "validator_alerts": validator_alerts,
        "approval_needed": approval_needed,
        "stale_packets": stale_packets,
        "commit_package_candidates": commit_candidates,
        "orchestration_health": health,
        "recommended_next_actions": next_actions,
        "protected_action_warnings": protected_warnings,
        "evidence_sources": [
            {
                "source_path": source["source_path"],
                "status": source["status"],
                "severity": source["severity"],
            }
            for source in sources
        ],
        "authority_boundary": {
            "read_only": True,
            "stdout_only": True,
            "blocked_capabilities": [
                "file_writes",
                "child_process_launch",
                "network_calls",
                "packet_mutation",
                "approval_mutation",
                "worker_launch",
                "scheduler_loop",
                "runtime_control",
                "stage_commit_push",
                "pr_automation",
            ],
        },
    }


def load_sources(paths: list[Path], include_default_telemetry: bool) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for path in paths:
        if path.suffix.lower() == ".jsonl":
            evidence.append(read_jsonl_summary(path))
        else:
            evidence.append(read_json_object(path))

    telemetry_path = Path("telemetry/work_ledger.jsonl")
    if include_default_telemetry and not paths and telemetry_path.exists():
        evidence.append(read_jsonl_summary(telemetry_path))

    if not evidence:
        evidence.append(
            {
                "source_path": "NO_INPUT",
                "status": "UNKNOWN",
                "severity": "UNKNOWN",
                "next_safe_action": "Provide JSON or JSONL evidence paths, or run from a repo with telemetry/work_ledger.jsonl.",
            }
        )

    return [summarize_source(item) for item in evidence]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synthesize a DRY_RUN AI_OS Morning Brief from existing orchestration evidence."
    )
    parser.add_argument(
        "evidence_path",
        nargs="*",
        type=Path,
        help="Existing JSON or JSONL evidence files to read. Files are not modified.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    parser.add_argument(
        "--no-default-telemetry",
        action="store_true",
        help="Do not read telemetry/work_ledger.jsonl when no evidence paths are provided.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sources = load_sources(
        paths=args.evidence_path,
        include_default_telemetry=not args.no_default_telemetry,
    )
    output = build_summary(sources)
    indent = 2 if args.pretty else None
    print(json.dumps(output, indent=indent, sort_keys=False))


if __name__ == "__main__":
    main()
