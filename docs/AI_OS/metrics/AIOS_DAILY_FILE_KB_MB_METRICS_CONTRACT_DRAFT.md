# AI_OS Daily File KB MB Metrics Contract Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.15 - Development Metrics + Completion Dashboard Readiness

## Purpose

Define the daily development metrics contract for tracking AI_OS repository growth without editing dashboard code or running deployment logic.

## Required Metrics

| Field | Meaning | Source |
| --- | --- | --- |
| date | Reporting date | Daily report or collection run |
| files_created | Count of new files created during the workload | Git status or report evidence |
| folders_created | Count of new folders created during the workload | Git status or folder scan evidence |
| bytes_created | Total bytes of new files | File length evidence |
| kb_created | bytes_created divided by 1024 | Calculated |
| mb_created | bytes_created divided by 1048576 | Calculated |
| reports_created | Count of new daily reports | Reports/daily |
| checkpoints_created | Count of new checkpoints | Reports/checkpoints |
| commit_hash | Commit hash associated with the measured work | Git evidence |
| git_status | Git status summary | git status --short --branch |
| notes | Human-readable context | Report evidence |

## Missing Metric Fallback

Missing or unverifiable metrics must be marked UNKNOWN. Missing metrics must not be treated as zero unless file evidence proves zero.

## Safety Boundary

This contract is read-only planning. It does not authorize modifying reports, committing files, editing dashboards, collecting secrets, or connecting external services.

