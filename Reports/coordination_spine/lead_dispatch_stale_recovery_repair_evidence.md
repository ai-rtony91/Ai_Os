# Lead Dispatch Stale Recovery Repair Evidence

## Baseline

- Baseline SHA: `fcbfb324b2a52eac79f0f20ac53cc65fa1650aa0`

## Generator

- `automation/orchestration/coordination_spine/Get-AiOsLeadDispatchView.DRY_RUN.ps1`

## Inputs Read

- `telemetry/coordination_spine/UNIFIED_QUEUE_INDEX.json`
- `telemetry/coordination_spine/UNIFIED_LOCK_STATUS.json`
- `telemetry/coordination_spine/RECOVERY_BOOTSTRAP_VIEW.json`

## Output Regenerated

- `telemetry/coordination_spine/LEAD_DISPATCH_VIEW.json`

## Before State

- `recovery_readiness = BLOCKED`
- recovery blockers included `marker_stale`
- `blocked_reason` included `recovery_blocked`

## After State

- `recovery_readiness = REVIEW_REQUIRED`
- recovery blockers: none
- recovery warnings include `heartbeat_degraded`
- `blocked_reason = queue_blocked, lock_review_required_or_collision`

## Result

- stale `marker_stale` / `recovery_blocked` path is gone
- lead dispatch remains `BLOCKED` for current queue and lock reasons
- `dispatcher_safety_verdict = BLOCKED`
- `write_path_enabled = false`
- `write_behavior = telemetry_only`
- live dispatch remains `BLOCKED`
- `t2b_status` remains `prerequisite_only`
- Module 5B remains `design_only`

## Mutation Check

- No queue files changed
- No lock files changed
- No packet-factory files changed
- No recovery files changed
- No code or test files changed
- No authority, secrets, dashboard, scheduler, SOS/ADB, broker, webhook, Module 5B, live orchestrator, T2B, Operation Glue, or Auto-Loop files changed
- Only `telemetry/coordination_spine/LEAD_DISPATCH_VIEW.json` changed during the repair, plus this evidence report

## Safe Next Action

Commit the evidence report plus regenerated `telemetry/coordination_spine/LEAD_DISPATCH_VIEW.json`, then open a PR.
