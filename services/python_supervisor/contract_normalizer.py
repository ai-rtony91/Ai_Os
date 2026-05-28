"""DRY_RUN-only orchestration result contract normalizer.

This module reads existing JSON report objects and emits one normalized
orchestration_result_contract-compatible summary. It never writes files, runs
subprocesses, mutates packets, mutates approvals, launches workers, or touches
Git state.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


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

STATUS_RANK = {
    "BLOCKED": 4,
    "REVIEW": 3,
    "UNKNOWN": 2,
    "NOT_RUN": 1,
    "PASS": 0,
}

SEVERITY_RANK = {
    "BLOCKED": 3,
    "REVIEW": 2,
    "UNKNOWN": 1,
    "INFO": 0,
}


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


def choose_ranked(values: list[str], ranks: dict[str, int], default: str) -> str:
    if not values:
        return default

    return sorted(values, key=lambda item: ranks.get(item, -1), reverse=True)[0]


def read_json_report(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
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
        "error": "JSON root must be an object for orchestration normalization.",
    }


def contract_from_report(report: dict[str, Any]) -> dict[str, Any]:
    embedded = report.get("orchestration_result_contract")
    if isinstance(embedded, dict):
        return embedded

    return report


def collect_validator_results(contract: dict[str, Any]) -> list[dict[str, Any]]:
    raw_results = contract.get("validator_results")
    if not isinstance(raw_results, list):
        raw_results = contract.get("results")

    if not isinstance(raw_results, list):
        return []

    normalized = []
    for index, item in enumerate(raw_results):
        if not isinstance(item, dict):
            continue

        validator_id = (
            item.get("validator_id")
            or item.get("validator_name")
            or item.get("check")
            or f"validator_{index + 1}"
        )
        status = normalize_status(item.get("status") or item.get("result"))
        severity = normalize_severity(item.get("severity") or status)
        evidence = item.get("evidence") or item.get("notes") or item.get("reason") or ""

        normalized.append(
            {
                "validator_id": str(validator_id),
                "status": status,
                "severity": severity,
                "evidence": str(evidence),
                "next_safe_action": str(
                    item.get("next_safe_action")
                    or "Review validator result before protected action."
                ),
            }
        )

    return normalized


def bool_from_report(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().upper() in {"TRUE", "YES", "Y", "1"}

    return bool(value)


def normalize_reports(reports: list[dict[str, Any]]) -> dict[str, Any]:
    statuses: list[str] = []
    severities: list[str] = []
    validator_results: list[dict[str, Any]] = []
    runtime_notes: list[str] = [
        "DRY_RUN",
        "Report-only normalization.",
        "No files were written.",
        "No subprocesses were started.",
        "No packet, approval, worker, Git, or runtime state was mutated.",
    ]
    evidence_sources: list[dict[str, Any]] = []
    approval_required = False
    commit_candidate = False
    blocked_reasons: list[str] = []
    escalation_reasons: list[str] = []
    next_safe_actions: list[str] = []

    for report in reports:
        contract = contract_from_report(report)
        status = normalize_status(
            contract.get("status")
            or contract.get("overall_result")
            or contract.get("result")
            or contract.get("decision")
        )
        severity = normalize_severity(contract.get("severity") or status)
        statuses.append(status)
        severities.append(severity)
        validator_results.extend(collect_validator_results(contract))

        approval_required = approval_required or bool_from_report(
            contract.get("approval_required")
            or contract.get("requiresApproval")
            or contract.get("requires_approval")
        )
        commit_candidate = commit_candidate or bool_from_report(
            contract.get("commit_candidate")
            or contract.get("auto_git_eligible")
            or contract.get("commit_performed") == "YES"
        )

        blocked_reason = str(contract.get("blocked_reason") or "").strip()
        if blocked_reason and blocked_reason.lower() != "none":
            blocked_reasons.append(blocked_reason)

        escalation_reason = str(contract.get("escalation_reason") or "").strip()
        if escalation_reason and escalation_reason.lower() != "none":
            escalation_reasons.append(escalation_reason)

        next_action = (
            contract.get("next_safe_action")
            or contract.get("recommended_next_action")
            or contract.get("next_safe_command")
        )
        if next_action:
            next_safe_actions.append(str(next_action))

        evidence_sources.append(
            {
                "source_path": str(report.get("source_path", "INLINE")),
                "raw_status": str(
                    contract.get("status")
                    or contract.get("overall_result")
                    or contract.get("result")
                    or contract.get("decision")
                    or "UNKNOWN"
                ),
                "normalized_status": status,
                "normalized_severity": severity,
            }
        )

    if validator_results:
        statuses.extend(item["status"] for item in validator_results)
        severities.extend(item["severity"] for item in validator_results)

    status = choose_ranked(statuses, STATUS_RANK, "UNKNOWN")
    severity = choose_ranked(severities, SEVERITY_RANK, "UNKNOWN")

    if status == "BLOCKED":
        approval_required = True
    elif status == "REVIEW":
        approval_required = True

    blocked_reason = "; ".join(blocked_reasons) if blocked_reasons else "none"
    escalation_reason = (
        "; ".join(escalation_reasons)
        if escalation_reasons
        else ("Human review required" if approval_required else "none")
    )
    next_safe_action = (
        next_safe_actions[0]
        if next_safe_actions
        else ("Human review required" if approval_required else "Continue with the next approved DRY_RUN step.")
    )

    return {
        "status": status,
        "severity": severity,
        "packet_id": "PYTHON_CONTRACT_NORMALIZER",
        "worker_identity": "EAST_OCC_01",
        "validator_results": validator_results,
        "approval_required": approval_required,
        "blocked_reason": blocked_reason,
        "escalation_reason": escalation_reason,
        "commit_candidate": commit_candidate,
        "next_safe_action": next_safe_action,
        "stop_condition": "REPORT_ONLY_NO_MUTATION",
        "runtime_notes": runtime_notes,
        "evidence": {
            "source_count": len(reports),
            "sources": evidence_sources,
            "normalization_maps": {
                "status": sorted(STATUS_ALIASES.keys()),
                "severity": sorted(SEVERITY_ALIASES.keys()),
            },
        },
        "generated_at": utc_now(),
    }


def build_empty_report() -> dict[str, Any]:
    return normalize_reports(
        [
            {
                "source_path": "NO_INPUT",
                "status": "UNKNOWN",
                "severity": "UNKNOWN",
                "next_safe_action": "Provide one or more JSON report paths for normalization.",
            }
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize AI_OS orchestration DRY_RUN/report JSON into one canonical contract object."
    )
    parser.add_argument(
        "json_report",
        nargs="*",
        type=Path,
        help="Existing JSON report file(s) to normalize. Files are read only.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reports = [read_json_report(path) for path in args.json_report]
    output = normalize_reports(reports) if reports else build_empty_report()
    indent = 2 if args.pretty else None
    print(json.dumps(output, indent=indent, sort_keys=False))


if __name__ == "__main__":
    main()
