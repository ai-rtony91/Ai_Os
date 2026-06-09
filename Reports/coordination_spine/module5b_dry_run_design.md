# Module 5B DRY_RUN Design

## Summary
Module 5B is a deferred helper layer design only. It does not implement a live dispatcher, does not invoke Operation Glue or Auto-Loop, and does not mutate any runtime or authority surface. The design exists to keep future recommendation and evidence flows read-only first.

## Current Position
- The Coordination Spine phase is closed.
- Modules 1, 2, 3, 4, Module 5A, Module 5A closeout, the Spine Orchestrator DRY_RUN design, and the phase closeout are already merged.
- Module 5B remains deferred.
- Orchestrator implementation is not started.
- `main` is the current clean baseline and matches `origin/main`.

## Module 5B Design Scope
Module 5B may design the following helper views and recommendation surfaces:
- self-heal report ingestion
- autonomy bridge state
- goal intake record generation
- Operation Glue / Auto-Loop invocation boundary
- approval inbox helper recommendation flow

## Read-Only First Contract
Each Module 5B item must begin as a read-only helper or view:
- ingest evidence, do not act on it
- summarize state, do not mutate state
- emit recommendations, do not approve or execute
- record prerequisites, do not bypass them
- preserve `telemetry_only` as the default behavior

## Item Classification
- Safe for Module 5B:
  - self-heal report ingestion as a read-only evidence aggregator
  - autonomy bridge state as a read-only status projection
  - goal intake record generation as a draft-only helper artifact
  - approval inbox helper recommendation flow as a recommendation-only view
- Must become separate packets if expanded beyond read-only:
  - any approval inbox mutation
  - any queue mutation
  - any lock mutation
  - any dispatcher mutation
  - any recovery mutation
  - any scheduler wiring
  - any SOS/ADB activation
  - any dashboard wiring
  - any broker access
  - any webhook emission
  - any secrets handling
  - any authority editing
  - any live dispatcher behavior
  - any direct Operation Glue or Auto-Loop invocation

## Operation Glue / Auto-Loop Boundary
- Module 5B may name Operation Glue and Auto-Loop only as boundaries and prerequisites.
- It must not invoke them.
- Any future integration that actually calls them must be a separate approved packet.

## Telemetry / Report Shape
A future Module 5B DRY_RUN helper may emit:
- generated timestamp
- repo root
- source readers
- input evidence list
- draft goal intake record
- autonomy bridge snapshot
- recommendation-only approval helper view
- blockers
- warnings
- deferred item list
- next safe action
- `write_behavior = telemetry_only`
- `write_path_enabled = false`

## Tests Required Before Implementation
- Verify each Module 5B helper can read and summarize inputs without mutating files.
- Verify recommendation outputs are draft-only and never approve or execute anything.
- Verify no queue, lock, dispatcher, recovery, scheduler, SOS/ADB, dashboard, broker, webhook, secret, or authority mutation call exists.
- Verify no direct Operation Glue or Auto-Loop invocation occurs.
- Verify deferred boundaries remain explicit in generated output.
- Verify any future APPLY path is gated behind human approval and module-specific scope.

## Explicit Human Approval Required Before APPLY
Before any APPLY implementation, Anthony must explicitly approve:
- the exact Module 5B sub-item
- the exact allowed write boundary
- the validator chain
- the stop point
- any later commit, push, or merge separately

## Boundary Reminder
Module 5B must not become a live dispatcher. It may design helper views and recommendations only. It must not mutate queue, locks, approval inbox, dispatcher, recovery, scheduler, SOS/ADB, dashboard, broker, webhook, secrets, or authority files.

## Design Status
This is a DRY_RUN design only. It records the deferred helper layer shape and the safe separation between read-only evidence, recommendations, and future implementation packets.

