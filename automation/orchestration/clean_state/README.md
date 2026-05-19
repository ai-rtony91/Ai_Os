# AI_OS Clean-State Verifier

This folder contains a DRY_RUN scaffold for checking whether the repository is clean and safe after commits or pushes.

The verifier reports one of three outcomes:

- `CLEAN`: no blocking or review risks were found.
- `REVIEW`: warnings exist and the operator should review them before declaring the repo clean.
- `BLOCKED`: a hard stop exists. Do not declare clean state until corrected.

The verifier is read-only. It does not edit dispatcher runtime, dashboard files, approval inboxes, locks, staged files, commits, pushes, pulls, rebases, or merges.

Checks included:

- current branch
- git status clean or dirty
- ahead/behind state
- untracked files
- staged files
- recent commit exists
- remote sync likely OK from local status
- protected files changed
- worker lanes still dirty
- next safe action

Example beginner command:

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/clean_state/Test-AiOsCleanState.DRY_RUN.ps1 -WorkerLanePath automation/orchestration
```

JSON-only output:

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/clean_state/Test-AiOsCleanState.DRY_RUN.ps1 -Json
```

Next safe action: run this after an approved commit or push to confirm whether the repo can be treated as clean.
