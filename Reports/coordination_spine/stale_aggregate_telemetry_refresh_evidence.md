# Stale Aggregate Telemetry Refresh Evidence

## Baseline

- Baseline SHA: `91c5d7d4578da35c0bd8ef4c8fa5bf942106a30d`

## Generators Used

- `automation/orchestration/coordination_spine/Get-AiOsPacketFactoryView.DRY_RUN.ps1`
- `automation/orchestration/coordination_spine/Invoke-AiOsCoordinationSpine.DRY_RUN.ps1`

## Files Regenerated

- `telemetry/coordination_spine/PACKET_FACTORY_VIEW.json`
- `telemetry/coordination_spine/COORDINATION_SPINE_VIEW.json`

## Before State

- `COORDINATION_SPINE_VIEW.json` carried stale `recovery_blocked`
- `PACKET_FACTORY_VIEW.json` carried stale `recovery_readiness = BLOCKED`
- `PACKET_FACTORY_VIEW.json` carried stale `marker_stale`
- `PACKET_FACTORY_VIEW.json` carried stale `recovery_blocked`

## After State

- `COORDINATION_SPINE_VIEW.json` now carries `blocked_reason = queue_blocked, lock_review_required_or_collision`
- `PACKET_FACTORY_VIEW.json` now carries `recovery_readiness = REVIEW_REQUIRED`
- `PACKET_FACTORY_VIEW.json` recovery blockers are empty
- `PACKET_FACTORY_VIEW.json` lead-dispatch `blocked_reason = queue_blocked, lock_review_required_or_collision`

## Remaining Real Blockers

- `queue_blocked`
- `lock_review_required_or_collision`
- `heartbeat_degraded`
- `packet_factory_blocked`
- `packet_factory_missing_required_fields`

## Expected Design Gates

- `packet_factory_approval_required`
- `live_dispatch_blocked_by_design`
- `module5b_design_only`
- `t2b_prerequisite_only`

## Validation Summary

- parser checks passed
- JSON parse passed
- packet factory tests passed
- coordination spine scaffold tests passed
- governance validator passed
- `git diff --check` passed

## Mutation Check

- Only the two target telemetry files changed during refresh, plus this evidence report
- No queue mutation
- No lock mutation
- No runtime heartbeat mutation
- No work packet mutation
- No code mutation
- No test mutation
- No approval mutation
- No authority mutation
- No scheduler mutation
- No SOS/ADB mutation
- No dashboard mutation
- No broker mutation
- No webhook mutation
- No secrets mutation
- No Module 5B mutation
- No T2B mutation
- No Operation Glue mutation
- No Auto-Loop mutation

## Safe Next Action

Commit this evidence report plus the refreshed `PACKET_FACTORY_VIEW.json` and `COORDINATION_SPINE_VIEW.json`, then open a PR.
