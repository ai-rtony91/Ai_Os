# AIOS No-Ready-Stage Discovery Router V1

## Purpose

`NO_READY_STAGE` is a valid campaign registry state.

It means the campaign selector found no stage with `READY` status, complete dependencies, and no blockers. It does not mean the registry is broken, and it does not authorize AIOS to invent or reopen work.

Before this router, AIOS could stall at `NO_READY_STAGE` because the action recommendation layer had no safe planning path after the selector truthfully reported that no packet candidate was selectable.

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
