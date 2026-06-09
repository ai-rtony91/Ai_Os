# AI_OS Daily Automation Snapshot

This folder contains a DRY_RUN scaffold for producing one daily automation summary.

The snapshot is read-only. It does not edit dispatcher runtime, dashboard files, health summary folders, staged files, commits, pushes, pulls, rebases, or merges.

This script is the canonical source for the `DAILY DATA SNAPSHOT` section used by AI_OS reports, telemetry snapshots, and backup summaries.

Checks included:

- current branch
- git status
- latest commit
- worker lane status tool exists
- validator chain runner exists
- approval runner exists
- commit package recommender exists
- clean-state verifier exists
- post-push verifier exists
- orchestration health summary exists if present
- worked-minutes placeholder

The snapshot reports:

- `TODAY STATUS: CLEAN`
- `TODAY STATUS: REVIEW`
- `TODAY STATUS: BLOCKED`
- `DAILY DATA SNAPSHOT`
- `date/time`
- `repo path`
- `current HEAD`
- `files changed/generated today`
- `artifact count`
- `folder count`
- `total bytes/KB/MB collected today`
- `backup size if backup ran`
- `skipped secrets count`
- `validation/governance status`
- `success/failure`

Example beginner command:

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/daily_snapshot/New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1
```

JSON-only output:

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/daily_snapshot/New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1 -Json
```

Next safe action: run this once at the end of a work session before deciding whether the repo is ready for commit, push, or a new packet.
