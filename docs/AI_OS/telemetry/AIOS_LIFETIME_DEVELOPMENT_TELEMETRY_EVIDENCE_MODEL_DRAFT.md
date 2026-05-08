# AI_OS Lifetime Development Telemetry Evidence Model Draft

Status: Draft
Mode: Evidence model only
Date: 2026-05-08

## Purpose

Define how AI_OS lifetime development telemetry may be represented without inventing history, inferring unsupported time, or enabling real telemetry collection.

## Evidence-Backed Fields

Evidence-backed fields must come from repository files, git output, committed reports, committed fixtures, or explicit operator-provided QA results.

Allowed evidence examples:

- Git commit count from `git rev-list --count HEAD`.
- Tracked file count from `git ls-files`.
- Git numstat insertions, deletions, and changed-file rows.
- Count of checkpoint files in `Reports/checkpoints/`.
- Count of daily report files in `Reports/daily/`.
- Count of progress files in `Reports/progress/`.
- Count of dashboard mock-data files in `apps/dashboard/mock-data/`.
- Validator command results from committed or rerun DRY_RUN validators.
- QA results recorded in checkpoint reports.
- Push history recorded by pushed commits and checkpoint reports.

## UNKNOWN Rules

Use `UNKNOWN` when evidence is absent, partial, stale, or not directly verified.

Required UNKNOWN cases:

- Complete lifetime time spent when only partial session rows exist.
- Complete lifetime KB/bytes changed when no canonical lifetime byte ledger exists.
- Cross-browser QA status unless a browser QA checkpoint explicitly records it.
- Human effort estimates that are inferred from commit timestamps.
- Any unstored historical activity that cannot be reconstructed from repo evidence.

## Git-Derived Totals

Git-derived totals are allowed when the exact git command is recorded.

Evidence observed during Stage 37 DRY_RUN/APPLY preparation:

- Commit count: `187`
- Tracked file count: `993`
- Git numstat file-change rows: `2530`
- Git numstat insertions: `143842`
- Git numstat deletions: `87507`

These values are evidence-backed at the time observed. Future changes require regeneration.

## Report-Derived Totals

Report-derived totals are allowed when the source folder is listed.

Evidence observed during Stage 37 DRY_RUN preparation:

- `Reports/checkpoints/`: `47` files.
- `Reports/daily/`: `53` files.
- `Reports/progress/`: `10` files.
- `apps/dashboard/mock-data/`: `23` files.

## Time-Spent Boundary

Time spent must not be inferred from commit timestamps.

Partial evidence exists in:

`Reports/DAILY_METRICS.csv`

Observed partial value:

- `duration_minutes` sum: `139.65`
- Evidence scope: `PARTIAL`
- Row count with duration evidence: `3`

Complete lifetime time spent:

`UNKNOWN`

## KB/Bytes Boundary

KB/bytes created or changed may be recorded only when backed by explicit metrics rows or a validator-generated calculation.

Current complete lifetime KB/bytes changed:

`UNKNOWN`

Git line insertions/deletions are not byte counts and must not be represented as KB/bytes.

## No Invented History

Lifetime telemetry must never invent:

- Missing time.
- Missing byte totals.
- Missing QA results.
- Missing validator runs.
- Missing push events.
- Missing blocker history.

When in doubt, store `UNKNOWN` with an evidence note.

## Safety Boundary

This model does not authorize:

- Real telemetry collectors.
- APIs.
- Secrets.
- Deployment.
- Broker/trading execution.
- Live AI execution.
- Background services.
