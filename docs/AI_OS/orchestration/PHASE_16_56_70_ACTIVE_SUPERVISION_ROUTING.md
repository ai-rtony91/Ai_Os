# Phase 16.56-70 Active Supervision Routing

## Purpose

This phase upgrades the AI_OS supervisor from passive status display to read-only active supervision and routing.

The supervisor can recommend a risk level, the next lane, validation needs, blocked actions, and the exact next safe action. It does not mutate repo state.

## Created Files

- `automation/orchestration/supervisor/Show-AiOsSupervisorDashboard.ps1`
- `automation/orchestration/supervisor/aios_supervision_rules.example.json`
- `automation/orchestration/supervisor/README_AIOS_ACTIVE_SUPERVISION.md`
- `docs/AI_OS/orchestration/PHASE_16_56_70_ACTIVE_SUPERVISION_ROUTING.md`
- `Reports/checkpoints/CHECKPOINT_PHASE_16_56_70_ACTIVE_SUPERVISION_ROUTING.md`

## Supervision Scope

The dashboard watches:

- dirty repo state
- untracked files
- current branch
- latest commit
- GitHub CLI availability
- open issue visibility
- open PR visibility
- current branch PR visibility
- blocked path visibility
- JSON validation needs
- PowerShell parse needs
- git diff check needs
- repo clean check needs

## Risk States

- `SAFE`: no blocking local condition is visible.
- `WATCH`: GitHub fallback or minor operator review is needed.
- `WARNING`: validation is needed before commit packaging.
- `BLOCKED`: protected, dashboard, broker, OANDA, API, webhook, or live-trading paths are visible.

## Routing Model

- `COMMAND DECK`: approvals, PRs, issues, merge decisions, branch mismatch, blocked state.
- `BUILD ENGINE`: approved APPLY work only.
- `VALIDATION DECK`: dirty repo, JSON changes, PowerShell changes, git diff check, repo clean check.

## Safety Boundaries

The dashboard must not commit, push, merge, create branches, create issues, create PRs, edit dashboards, edit protected root files, create startup tasks, create scheduled tasks, auto-launch Codex, touch broker/OANDA/API/webhook/live trading, or mutate the repo automatically.

## Validation

```powershell
powershell -NoProfile -Command "Get-Content -Raw -Path 'automation/orchestration/supervisor/aios_supervision_rules.example.json' | ConvertFrom-Json | Out-Null"
powershell -NoProfile -Command "Get-ChildItem automation/orchestration/supervisor -Filter *.ps1 | ForEach-Object { [scriptblock]::Create((Get-Content -Raw -Path $_.FullName)) | Out-Null }"
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Show-AiOsSupervisorDashboard.ps1
git diff --check
git status --short --branch
```
