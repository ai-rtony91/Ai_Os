# Coordination Spine Orchestrator DRY_RUN Design

## Summary
This design defines a future read-only Coordination Spine Orchestrator that composes Modules 1, 2, 3, 4, and 5A into one operator cockpit view. It does not implement the orchestrator, does not create runtime scripts, and does not authorize any live action.

## What The Orchestrator Reads
- Module 1 queue index telemetry: `telemetry/coordination_spine/UNIFIED_QUEUE_INDEX.json`
- Module 2 lock status telemetry: `telemetry/coordination_spine/UNIFIED_LOCK_STATUS.json`
- Module 3 lead dispatch telemetry: `telemetry/coordination_spine/LEAD_DISPATCH_VIEW.json`
- Module 4 recovery bootstrap telemetry: `telemetry/coordination_spine/RECOVERY_BOOTSTRAP_VIEW.json`
- Module 5A packet factory view telemetry: `telemetry/coordination_spine/PACKET_FACTORY_VIEW.json`
- Module 5A closeout evidence: `Reports/coordination_spine/module5a_scope_closeout.md`
- Optional source context for diagnostics only:
  - `automation/orchestration/work_packets/proposed/AIOS-COORDINATION-SPINE-V1.md`
  - `automation/orchestration/coordination_spine/Get-AiOsPacketFactoryView.DRY_RUN.ps1`

## What It Must Never Mutate
- Queue state, lock state, dispatcher state, recovery state, approval inbox state, scheduler state, dashboard state, broker state, webhook state, secrets, authority files, and runtime bridge state.
- The orchestrator must not mutate any packet file, work queue, lock registry, claim registry, approval inbox, or recovery marker.
- T2B remains a prerequisite only; the orchestrator must never perform assignment-plus-lock write integration.
- Operation Glue and Auto-Loop are read-only context boundaries for this design only; they are not invoked by the orchestrator design.

## Composition Model
- Read each module output as a sealed telemetry input.
- Compose a single top-level spine view with one section per module:
  - queue state
  - lock state
  - dispatch state
  - recovery state
  - packet-factory state
- Use the module outputs as the source of truth rather than rescanning mutable subsystems.
- Preserve each module’s own safety verdict and expose the most restrictive verdict at the top level.
- Preserve `telemetry_only` and `write_path_enabled = false` as top-level orchestrator defaults.

## Blocker Reporting
- Queue blockers should surface when normalized queue states show active `BLOCKED` work or other queue-wide obstruction.
- Lock blockers should surface when the lock view reports collisions, stale locks, or `REVIEW_REQUIRED`.
- Recovery blockers should surface when recovery readiness is `BLOCKED` or the marker is stale.
- Dispatch blockers should surface when the dispatch view is `BLOCKED` or depends on unresolved prerequisites.
- Packet-factory blockers should surface when duplicate intent, missing required fields, or approval requirements are present.
- The top-level orchestrator verdict should be the worst applicable verdict across all module inputs:
  - `SAFE_NO_WORK`
  - `READY_TO_DRAFT`
  - `REVIEW_REQUIRED`
  - `BLOCKED`

## Module 5B Handling
- Module 5B is deferred and remains outside this orchestrator design.
- The orchestrator should carry a visible `module_5b_status = deferred` note, not a runnable integration path.
- If future scope is added, it should arrive as a separately approved packet with its own APPLY gate.

## T2B Prerequisite Handling
- T2B remains a prerequisite for any future assignment-plus-lock write path.
- The orchestrator should display T2B as an external prerequisite only.
- The orchestrator must not simulate, bypass, or partially implement T2B write behavior.

## Creep Prevention
- Do not add runtime bridge behavior.
- Do not invoke Operation Glue or Auto-Loop.
- Do not add approval inbox mutation.
- Do not add queue mutation, lock mutation, dispatcher mutation, recovery mutation, scheduler wiring, SOS/ADB activation, dashboard wiring, broker access, webhook emission, or secret handling.
- Do not infer write permissions from read-only telemetry.
- Do not widen the design into Module 5B or live orchestration.

## Future DRY_RUN Output Shape
A future orchestrator should emit a single report object or markdown report with:
- generated timestamp
- repo root
- module inputs and source paths
- module safety verdicts
- combined blocker list
- combined warnings list
- T2B prerequisite note
- Module 5B deferred note
- recommended next safe action
- `write_behavior = telemetry_only`
- `write_path_enabled = false`

## Required Tests Before Implementation
- Verify the orchestrator reads the five module outputs without mutating any source file.
- Verify the orchestrator reports the worst-case verdict when one or more module inputs are blocked.
- Verify the orchestrator preserves `telemetry_only` and `write_path_enabled = false`.
- Verify Module 5B remains deferred and is not auto-invoked.
- Verify T2B is treated as prerequisite only.
- Verify no runtime bridge, Operation Glue, or Auto-Loop call is present.
- Verify no queue, lock, dispatcher, recovery, approval, scheduler, dashboard, broker, webhook, secret, or authority mutation call is present.

## Human Approval Required Before APPLY
Before any APPLY implementation, Anthony must explicitly approve:
- this packet ID
- the exact module being implemented
- the exact allowed write boundary
- the validator chain for that module
- the stop point

## Design Status
This is DRY_RUN design only. It records the orchestrator shape, guards, and tests without creating the orchestrator.

