# AI_OS Strategic Campaign Registry

## Purpose

The AI_OS Strategic Campaign Registry is the planning source for long-running AI_OS campaigns, dependencies, blockers, unlock conditions, progress, and the next safest packet candidate.

It is planning authority only. It does not approve APPLY, run code, create workers, create branches, stage files, commit, push, merge, or replace Human Owner approval.

Canonical machine-readable source:

```text
automation/orchestration/campaign_registry/AIOS_STRATEGIC_CAMPAIGN_REGISTRY.json
```

Schema:

```text
schemas/aios/orchestration/aios-strategic-campaign-registry.schema.json
```

Read-only recommender:

```text
automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1
```

## Campaign Model

The registry uses this hierarchy:

```text
campaign -> phase -> stage -> packet candidate
```

- A `campaign` is a strategic outcome such as governance, orchestration, telemetry, dashboard visibility, paper-only Trading Lab, or supervised autonomy.
- A `phase` groups related work inside a campaign.
- A `stage` is the smallest roadmap unit that can become a DRY_RUN packet candidate.
- A `next_packet_candidate` is a proposed packet ID or work package name. It is not approval.

## Dependency And Unlock Logic

The next-task helper selects one stage only when:

- stage status is `READY`;
- stage blockers are empty;
- campaign blockers are empty;
- every stage in `depends_on` exists and is `COMPLETE`;
- the campaign remains within AI_OS safety boundaries.

The helper ignores stages with these statuses:

- `BLOCKED`
- `DEFERRED`
- `COMPLETE`

If no stage qualifies, the helper returns `NO_READY_STAGE` and recommends registry review.

## Completion Percent Rules

Completion percentages are evidence estimates, not proof of completion.

A campaign should only increase progress when evidence exists:

- authority or roadmap evidence exists;
- schema or contract exists;
- DRY_RUN helper exists;
- validator or parse check exists;
- approved packet or PR evidence exists.

No campaign is complete until the evidence paths and stop conditions support `COMPLETE`.

Timeline values must stay in checkpoint ranges:

- `same session`
- `1-2 work sessions`
- `2-4 work sessions`
- `multi-checkpoint`
- `blocked until decision`

## Safety Boundaries

Trading Lab remains paper-only.

Forex/OANDA remains documentation-boundary only unless a future Human Owner approved policy explicitly changes the boundary.

The registry must not create or imply:

- external account connection;
- credential handling;
- real funds flow;
- live trading;
- external trade routing;
- hidden background automation;
- autonomous protected actions.

## Crew Core Future Integration

Crew Core should read the registry through the DRY_RUN recommender, not directly invent strategic tasks from chat.

Recommended future chain:

```text
AIOS_STRATEGIC_CAMPAIGN_REGISTRY.json
-> Get-AiOsCampaignNextTask.DRY_RUN.ps1
-> New-AiOsCrewTask.DRY_RUN.ps1
-> Get-AiOsCrewIntegrationRecommendation.DRY_RUN.ps1
-> packet proposal preview
-> Human Owner approval gate
```

Crew Core output must remain preview-only until a separate approved APPLY packet wires the bridge.

## Human Owner Authority

Human Owner authority remains final for:

- APPLY;
- protected edits;
- validator exception acceptance;
- worker launch;
- staging;
- commit;
- push;
- PR merge;
- safety policy changes.

The registry recommends direction. It does not approve execution.
