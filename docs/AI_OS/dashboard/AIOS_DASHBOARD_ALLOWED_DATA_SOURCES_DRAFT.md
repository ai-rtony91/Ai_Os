# AI_OS Dashboard Allowed Data Sources Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.14 - Dashboard Status Implementation Readiness

## Purpose

List local AI_OS data sources that a future read-only dashboard adapter may inspect.

## Allowed Sources

| Source | Purpose | Access Mode |
| --- | --- | --- |
| Reports/progress | Progress ledger status | Read-only |
| Reports/checkpoints | Latest checkpoint and next action | Read-only |
| Reports/health | Validator health summaries | Read-only |
| Reports/daily | Daily workload reports | Read-only |
| docs/AI_OS/dashboard | Dashboard planning contracts | Read-only |
| docs/AI_OS/governance | Safety status planning references | Read-only |

## Rules

- Prefer the latest approved artifact by date and file evidence.
- Do not infer state when source files are missing.
- Do not read files outside approved local AI_OS data paths without explicit approval.

