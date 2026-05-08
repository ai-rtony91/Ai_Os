# AI_OS Dashboard Reports + Telemetry Grouping Draft

## Purpose

Define why Reports and Telemetry should share one dashboard nav group while keeping their responsibilities separate.

## Decision

Reports and Telemetry belong under one top-level dashboard tab because both are operational evidence surfaces.

## Reports Scope

- Daily reports
- Checkpoints
- Audit outputs
- Operator evidence
- Apply / DRY_RUN summaries

## Telemetry Scope

- Health snapshots
- Validator summaries
- Dashboard status signals
- Runtime-style state fixtures
- Progress/status telemetry placeholders

## UI Rule

The main nav label may be `Reports + Telemetry`, but internal cards must be clearly labeled as either Reports or Telemetry.

## Safety Boundary

Telemetry is fixture/read-only planning unless a later approved stage defines a local telemetry writer. No live telemetry service is connected here.
