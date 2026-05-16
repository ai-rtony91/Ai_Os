# Phase 16.41-55 AI_OS Supervisor Core

## Purpose

Phase 16.41-55 creates the first AI_OS Supervisor Core.

The supervisor watches the workflow and tells the operator what is happening. It does not automate dangerous actions.

## Files Added

- `automation/orchestration/supervisor/Start-AiOsSupervisor.ps1`
- `automation/orchestration/supervisor/Show-AiOsSupervisorStatus.ps1`
- `automation/orchestration/supervisor/aios_supervisor_state.example.json`
- `automation/orchestration/supervisor/README_AIOS_SUPERVISOR.md`
- `docs/AI_OS/orchestration/PHASE_16_41_55_AIOS_SUPERVISOR_CORE.md`
- `Reports/checkpoints/CHECKPOINT_PHASE_16_41_55_AIOS_SUPERVISOR_CORE.md`

## Watched State

The supervisor watches:

- repo branch, cleanliness, changed files, untracked files, latest commit
- GitHub CLI availability, auth, issues, PRs, current branch PR status
- Command Deck, Build Engine, and Validation Deck lane guidance
- queue file visibility and blocked/approval/validation state reminders
- validator file visibility and required validation reminders
- stale state such as dirty repo after APPLY and uncommitted files after validation
- exact next safe action

## Safety Boundary

The supervisor is read-only.

It does not commit, push, merge, create branches, create issues, create PRs, edit dashboard files, edit protected root files, create startup tasks, create scheduled tasks, auto-launch Codex, or touch broker/OANDA/API/webhook/live trading work.

## Validation

Run:

```powershell
powershell -NoProfile -Command "Get-Content -Raw -Path 'automation/orchestration/supervisor/aios_supervisor_state.example.json' | ConvertFrom-Json | Out-Null"
powershell -NoProfile -Command "Get-ChildItem automation/orchestration/supervisor -Filter *.ps1 | ForEach-Object { [scriptblock]::Create((Get-Content -Raw -Path $_.FullName)) | Out-Null }"
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Show-AiOsSupervisorStatus.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Start-AiOsSupervisor.ps1
git diff --check
git status --short --branch
```

## Next Safe Action

Run the supervisor, review the next safe action it prints, and only request commit or PR work in a separate explicit approval prompt.
