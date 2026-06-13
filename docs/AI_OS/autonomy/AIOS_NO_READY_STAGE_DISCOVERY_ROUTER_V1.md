# AIOS No-Ready-Stage Discovery Router V1

## Purpose

`NO_READY_STAGE` is a valid campaign registry state.

It means the campaign selector found no stage with `READY` status, complete dependencies, and no blockers. It does not mean the registry is broken, and it does not authorize AIOS to invent or reopen work.

Before this router, AIOS could stall at `NO_READY_STAGE` because the action recommendation layer had no safe planning path after the selector truthfully reported that no packet candidate was selectable.

`NO_READY_STAGE` can also be healthy. If all currently known selectable work is complete, AIOS should idle cleanly instead of manufacturing new work.

## Discovery Router Behavior

The discovery router is:

- DRY_RUN/read-only
- registry-inspection only
- planning/review oriented
- non-authoritative for registry mutation

The router reads `automation/orchestration/campaign_registry/AIOS_STRATEGIC_CAMPAIGN_REGISTRY.json`, compares it with the existing campaign next-task selector, and reports:

- campaign, phase, and stage inventory
- stage status counts
- last completed high-priority stage when available
- blocked stages and blockers
- in-progress, planned, or review-stage gaps that could become future candidates
- whether supervised autonomy has no next selectable stage

## No-Ready-Stage Classification

The router classifies `NO_READY_STAGE` as one of three states:

- `COMPLETE_IDLE`
- `NEEDS_NEXT_STAGE_PLANNING`
- `BLOCKED_BY_REGISTRY_INCONSISTENCY`

### COMPLETE_IDLE

`COMPLETE_IDLE` means AIOS has no READY stage, no active/high-priority blocker, no high-priority in-progress stage missing a packet candidate, no registry inconsistency, and at least one completed high-priority stage.

In this state:

- `idle_allowed = true`
- `next_stage_planning_required = false`
- AIOS may idle cleanly

The safe next action is:

```text
No READY stage is available and no blocker is detected. Idle cleanly or request a supervised planning review before defining new work.
```

### NEEDS_NEXT_STAGE_PLANNING

`NEEDS_NEXT_STAGE_PLANNING` means no stage is selectable, but active planned or in-progress campaign work could become a future candidate after supervised planning.

In this state:

- `idle_allowed = false`
- `next_stage_planning_required = true`
- AIOS must not invent a READY stage

The safe next action is:

```text
Review campaign registry gaps and create a supervised DRY_RUN packet candidate for the next autonomy stage.
```

### BLOCKED_BY_REGISTRY_INCONSISTENCY

`BLOCKED_BY_REGISTRY_INCONSISTENCY` means the registry contains structural evidence that must be repaired before packet selection is trusted.

Examples include:

- a missing dependency stage id
- a READY stage with blockers
- a COMPLETE stage with a non-null `next_packet_candidate`
- duplicate active `next_packet_candidate` values
- duplicate stage ids

In this state:

- `idle_allowed = false`
- `next_stage_planning_required = false`
- `registry_inconsistency_detected = true`

The safe next action is:

```text
Review and repair campaign registry inconsistencies before requesting a packet.
```

## Why Idle Is Sometimes Correct

False progress is dangerous in a governed automation system. If AIOS creates work just because no READY stage exists, it can drift into duplicate authority, unnecessary stages, or unapproved scope expansion.

`COMPLETE_IDLE` makes clean idling explicit. It tells AIOS that the current known workload is done and that any new work must come from a supervised planning review, not automatic registry promotion.

## Safe Recommendation Boundary

The router may recommend only planning or review, such as:

```text
Review campaign registry gaps and create a supervised DRY_RUN packet candidate for the next autonomy stage.
```

The router must never recommend:

- commit
- push
- PR
- merge
- APPLY
- worker launch
- runtime start
- queue mutation
- approval mutation
- broker, OANDA, webhook, order, or live-trading action
- secret handling
- automatic registry mutation
- creating a READY stage
- reopening a completed stage

## Relationship To Action Recommendation

When `Get-AiOsCampaignNextTask.DRY_RUN.ps1` reports `NO_READY_STAGE` and no relay/SOS continuation applies, `Get-AiOsActionRecommendation.DRY_RUN.ps1` may recommend this read-only command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/campaign_registry/Get-AiOsCampaignNoReadyStageDiscovery.DRY_RUN.ps1 -OutputJson
```

This keeps AIOS moving by producing planning evidence instead of a dead end.

When discovery classifies the state as `COMPLETE_IDLE`, action recommendation should surface idle/review status without implying AIOS is stuck or failed.

When discovery classifies the state as `NEEDS_NEXT_STAGE_PLANNING`, action recommendation may keep routing to the read-only discovery helper for planning evidence.

When discovery classifies the state as `BLOCKED_BY_REGISTRY_INCONSISTENCY`, action recommendation must recommend registry review/repair only.

## Relationship To Relay And SOS

Relay/SOS continuation has priority when an active relay review exists.

Routine relay review may continue through its governed read-only review path when SOS policy allows it. SOS escalation or Anthony-required review still blocks continuation and wakes Anthony.

The no-ready-stage router is for campaign planning gaps only. It does not resolve relay items and does not override SOS policy.

## Anthony Approval Boundary

Anthony remains the approval authority for APPLY, protected actions, registry status promotion, worker launch, runtime changes, commit, push, PR, merge, and live-trading boundaries.

Discovery output is evidence only. It can help draft a future supervised DRY_RUN packet candidate, but it cannot approve or perform registry edits.

## No-Execution / No-Mutation Guarantee

The discovery router does not:

- write files
- mutate the registry
- create a new READY stage
- reopen a completed stage
- launch workers
- start runtime
- mutate queues, locks, approval inbox, telemetry, dashboard, broker, webhook, order, or secret paths
- stage, commit, push, open PRs, or merge

Its safe output is a planning/review recommendation only.
