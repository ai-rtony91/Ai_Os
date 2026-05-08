# AI_OS Lifetime Development Telemetry Storage Contract Draft

Status: Draft
Mode: Storage contract only
Date: 2026-05-08

## Purpose

Define a safe storage model for lifetime AI_OS development telemetry without enabling real telemetry collectors or inventing unsupported historical values.

## Proposed Storage Paths

Canonical CSV ledger:

`Reports/telemetry/AIOS_LIFETIME_DEVELOPMENT_TELEMETRY_LEDGER.csv`

Canonical summary JSON:

`Reports/telemetry/AIOS_LIFETIME_DEVELOPMENT_TELEMETRY_SUMMARY.json`

Dashboard fixture:

`apps/dashboard/mock-data/lifetime-telemetry-fixture.example.json`

The `Reports/telemetry/` folder was not present during Stage 37-44 DRY_RUN inspection. Creating it should require a separate approved APPLY stage if canonical telemetry storage is later implemented.

## CSV Ledger Purpose

The CSV ledger should be append-only when approved.

Recommended columns:

- `recorded_at`
- `stage`
- `task_id`
- `mode`
- `commit_hash`
- `files_created`
- `files_changed`
- `validators_run`
- `reports_created`
- `checkpoints_created`
- `push_performed`
- `qa_result`
- `blockers`
- `recovery_notes`
- `duration_minutes`
- `duration_evidence_scope`
- `bytes_changed`
- `bytes_evidence_scope`
- `evidence_source`
- `notes`

## JSON Summary Purpose

The JSON summary should provide dashboard-friendly lifetime totals.

Recommended top-level sections:

- `metadata`
- `evidence_scope`
- `git_totals`
- `report_totals`
- `time_spent`
- `size_totals`
- `quality_signals`
- `safety`
- `unknowns`

## Dashboard Fixture Purpose

The dashboard fixture should be local mock data only.

It may show:

- Evidence-backed git totals.
- Evidence-backed report counts.
- Partial duration evidence.
- Unsupported lifetime time as `UNKNOWN`.
- Unsupported lifetime KB/bytes as `UNKNOWN`.
- Safety blocks.

It must not claim production telemetry readiness.

## Required Evidence Source Per Field

Every stored field should include a source.

Examples:

- Git totals source: exact git command.
- Report counts source: folder count command.
- Duration source: `Reports/DAILY_METRICS.csv`.
- QA source: checkpoint report path.
- Validator source: command and output.
- Unknown source: `NO_COMPLETE_EVIDENCE_FOUND`.

## UNKNOWN Handling

Use `UNKNOWN` for:

- Complete lifetime time spent.
- Complete lifetime KB/bytes changed.
- Unverified QA.
- Unverified blockers.
- Unverified recovery notes.
- Any metric not backed by a repo artifact or command output.

Partial evidence must be labeled `PARTIAL`, not promoted to lifetime complete.

## No Real Collectors

This contract does not authorize:

- Background telemetry writers.
- File watchers.
- API calls.
- Account telemetry.
- Secret scanning beyond existing approved validators.
- Deployment telemetry.
- Broker/trading telemetry.
- Live AI telemetry.

## Safety Boundary

Telemetry storage remains documentation and fixture-only until a future explicit APPLY stage creates canonical ledger files and a validator that confirms no unsafe data is stored.
