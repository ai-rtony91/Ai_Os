"""Read-only AI_OS evidence manifest for Morning Brief synthesis.

This module defines approved evidence sources for Python-side orchestration
intelligence. It does not read files, write files, run child processes, call
networks, mutate packets, mutate approvals, schedule work, or control runtime.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from typing import Any


EVIDENCE_CATEGORIES = (
    "validator",
    "approval",
    "commit_package",
    "recommendation",
    "packet",
    "worker",
    "runtime_health",
    "telemetry",
    "backup",
    "github_pr",
    "operator_status",
)


_MANIFEST: tuple[dict[str, Any], ...] = (
    {
        "id": "validator_recommendation",
        "category": "validator",
        "path": "automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1",
        "format": "json_stdout",
        "morning_brief_enabled": True,
        "risk_level": "low",
        "expected_freshness_fields": ["generated_at"],
        "safe_for_unattended_dry_run": True,
        "notes": "Recommends validator routes only; it does not auto-run validators.",
    },
    {
        "id": "validator_chain",
        "category": "validator",
        "path": "automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1",
        "format": "json_stdout",
        "morning_brief_enabled": True,
        "risk_level": "medium",
        "expected_freshness_fields": ["generated_at"],
        "safe_for_unattended_dry_run": True,
        "notes": "Read-only validation evidence; validator output is not approval.",
    },
    {
        "id": "approval_inbox_summary",
        "category": "approval",
        "path": "automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1",
        "format": "json_stdout",
        "morning_brief_enabled": True,
        "risk_level": "medium",
        "expected_freshness_fields": ["generated_utc", "generated_at"],
        "safe_for_unattended_dry_run": True,
        "notes": "Reads approval evidence without creating, updating, or granting approval.",
    },
    {
        "id": "commit_package_recommendation",
        "category": "commit_package",
        "path": "automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1",
        "format": "json_stdout",
        "morning_brief_enabled": True,
        "risk_level": "medium",
        "expected_freshness_fields": ["generated_at"],
        "safe_for_unattended_dry_run": True,
        "notes": "Exact-file package planning only; no staging or repository mutation.",
    },
    {
        "id": "action_recommendation",
        "category": "recommendation",
        "path": "automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1",
        "format": "json_stdout",
        "morning_brief_enabled": True,
        "risk_level": "medium",
        "expected_freshness_fields": ["generated_at"],
        "safe_for_unattended_dry_run": True,
        "notes": "Recommendation only; command suggestions remain human-gated.",
    },
    {
        "id": "next_packet_recommendation",
        "category": "recommendation",
        "path": "automation/orchestration/recommendations/Get-AiOsNextPacketRecommendation.DRY_RUN.ps1",
        "format": "json_stdout",
        "morning_brief_enabled": True,
        "risk_level": "medium",
        "expected_freshness_fields": ["generated_utc"],
        "safe_for_unattended_dry_run": True,
        "notes": "Suggests packet workflow direction without moving packet state.",
    },
    {
        "id": "work_packets",
        "category": "packet",
        "path": "automation/orchestration/work_packets/",
        "format": "json_files",
        "morning_brief_enabled": True,
        "risk_level": "high",
        "expected_freshness_fields": ["updated_utc", "created_utc"],
        "safe_for_unattended_dry_run": True,
        "notes": "Packet records are active state evidence; readers must not move packets.",
    },
    {
        "id": "worker_registry",
        "category": "worker",
        "path": "automation/orchestration/workers/",
        "format": "json_files",
        "morning_brief_enabled": True,
        "risk_level": "medium",
        "expected_freshness_fields": ["updated_utc", "created_utc"],
        "safe_for_unattended_dry_run": True,
        "notes": "Worker registry and inbox evidence; readers must not launch workers.",
    },
    {
        "id": "orchestration_health",
        "category": "runtime_health",
        "path": "automation/orchestration/health_summary/Get-AiOsOrchestrationHealth.DRY_RUN.ps1",
        "format": "json_stdout",
        "morning_brief_enabled": True,
        "risk_level": "high",
        "expected_freshness_fields": ["generated_at", "observation_time"],
        "safe_for_unattended_dry_run": True,
        "notes": "Health summary evidence; runtime control remains out of scope.",
    },
    {
        "id": "work_ledger",
        "category": "telemetry",
        "path": "telemetry/work_ledger.jsonl",
        "format": "jsonl",
        "morning_brief_enabled": True,
        "risk_level": "medium",
        "expected_freshness_fields": ["timestamp_utc"],
        "safe_for_unattended_dry_run": True,
        "notes": "Append-only evidence source; this module does not append events.",
    },
    {
        "id": "t9_snapshot_backup",
        "category": "backup",
        "path": "scripts/backup/Start-AiOsT9SnapshotBackup.ps1",
        "format": "json_stdout",
        "morning_brief_enabled": True,
        "risk_level": "medium",
        "expected_freshness_fields": ["generated_at", "snapshot_name"],
        "safe_for_unattended_dry_run": False,
        "notes": "Backup script is evidence for backup design; do not run backup from Morning Brief.",
    },
    {
        "id": "github_status",
        "category": "github_pr",
        "path": "automation/orchestration/github_status/Get-AiOsGitHubStatusCheck.DRY_RUN.ps1",
        "format": "json_stdout",
        "morning_brief_enabled": True,
        "risk_level": "medium",
        "expected_freshness_fields": ["completedAt", "startedAt", "generated_at"],
        "safe_for_unattended_dry_run": True,
        "notes": "Read-only PR/check evidence; remote actions remain human-gated.",
    },
    {
        "id": "operator_status_line",
        "category": "operator_status",
        "path": "automation/orchestration/control_summary/Get-AiOsOperatorStatusLine.DRY_RUN.ps1",
        "format": "text_stdout",
        "morning_brief_enabled": True,
        "risk_level": "low",
        "expected_freshness_fields": ["observation_time"],
        "safe_for_unattended_dry_run": True,
        "notes": "Compact operator status signal; it does not claim exact Codex output remaining.",
    },
)


def get_evidence_manifest() -> list[dict[str, Any]]:
    return deepcopy(list(_MANIFEST))


def get_enabled_morning_brief_sources() -> list[dict[str, Any]]:
    return [item for item in get_evidence_manifest() if item["morning_brief_enabled"]]


def get_sources_by_category(category: str) -> list[dict[str, Any]]:
    normalized = str(category).strip().lower()
    return [item for item in get_evidence_manifest() if item["category"] == normalized]


def summarize_manifest() -> dict[str, Any]:
    items = get_evidence_manifest()
    categories: dict[str, int] = {category: 0 for category in EVIDENCE_CATEGORIES}
    risk_levels: dict[str, int] = {}
    format_counts: dict[str, int] = {}
    enabled_count = 0
    unattended_count = 0

    for item in items:
        categories[item["category"]] = categories.get(item["category"], 0) + 1
        risk_levels[item["risk_level"]] = risk_levels.get(item["risk_level"], 0) + 1
        format_counts[item["format"]] = format_counts.get(item["format"], 0) + 1
        if item["morning_brief_enabled"]:
            enabled_count += 1
        if item["safe_for_unattended_dry_run"]:
            unattended_count += 1

    return {
        "schema": "AIOS_EVIDENCE_MANIFEST.v1",
        "mode": "DRY_RUN",
        "source_count": len(items),
        "morning_brief_enabled_count": enabled_count,
        "safe_for_unattended_dry_run_count": unattended_count,
        "category_counts": categories,
        "risk_level_counts": risk_levels,
        "format_counts": format_counts,
        "blocked_capabilities": [
            "file_writes",
            "child_process_launch",
            "network_calls",
            "runtime_mutation",
            "scheduler_mutation",
            "packet_movement",
            "approval_mutation",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print the AI_OS read-only evidence manifest summary.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--full", action="store_true", help="Include full manifest items.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = summarize_manifest()
    if args.full:
        output["sources"] = get_evidence_manifest()
    print(json.dumps(output, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
