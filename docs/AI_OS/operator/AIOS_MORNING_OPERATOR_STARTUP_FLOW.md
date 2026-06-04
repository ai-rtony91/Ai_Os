> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

# AI_OS Morning Operator Startup Flow

## Purpose

The morning startup flow prepares AI_OS for the workday using local-only validation and work intelligence.

It generates a daily snapshot and a beginner-readable operator voice briefing, then prints repo status and the next safe action.

## Command

Run from the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File automation/operator/Start-AiOsMorningOperations.ps1
```

## What It Runs

The script runs:

```powershell
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Invoke-AiOsWorkIntelligenceScan.ps1 -SaveSnapshot -GenerateBriefing
git status --short --branch
```

It then prints:

- repo status
- latest snapshot path
- latest briefing path
- next safe action

## Optional Worker Launch

Workers do not launch by default.

To launch the parallel DRY_RUN crew after the morning check:

```powershell
powershell -ExecutionPolicy Bypass -File automation/operator/Start-AiOsMorningOperations.ps1 -LaunchWorkers
```

## Safety Defaults

- No commit.
- No push.
- No git add.
- No APPLY.
- No automatic worker launch.
- Local-only.

The startup script is an operator preparation tool. It does not approve changes or perform code edits.
