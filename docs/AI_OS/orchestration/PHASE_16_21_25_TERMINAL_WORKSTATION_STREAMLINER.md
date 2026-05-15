# Phase 16.21-25 Terminal Workstation Streamliner

## Purpose

Phase 16.21-25 provides a practical AI_OS terminal automation layer with one master launcher and three operator lanes.

The master launcher is `Start-AiOsWorkstation.ps1`. It prints repo status, branch, recent commits, open GitHub issues, open PRs, lane guidance, and the next safe action.

## Files Added

- `automation/orchestration/terminal_workstations/Start-AiOsWorkstation.ps1`
- `automation/orchestration/terminal_workstations/Start-AiOsCommandDeck.ps1`
- `automation/orchestration/terminal_workstations/Start-AiOsBuildEngine.ps1`
- `automation/orchestration/terminal_workstations/Start-AiOsValidationDeck.ps1`
- `automation/orchestration/terminal_workstations/README_TERMINAL_WORKSTATIONS.md`
- `docs/AI_OS/orchestration/PHASE_16_21_25_TERMINAL_WORKSTATION_STREAMLINER.md`
- `Reports/checkpoints/CHECKPOINT_PHASE_16_21_25_TERMINAL_WORKSTATION_STREAMLINER.md`

## Lane Map

- AI_OS COMMAND DECK: Git, GitHub CLI, issues, PRs, commits, merges.
- AI_OS BUILD ENGINE: Codex work lane. Codex launch is manual only.
- AI_OS VALIDATION DECK: PowerShell status checks, validators, queue checks, repo checks.

## Safety Boundary

This phase does not:

- use WScript.Shell
- use SendKeys
- press ALT+SPACE
- change Num Lock
- edit Windows Terminal settings JSON
- auto-launch Codex
- open extra windows
- install anything
- create startup tasks
- create scheduled tasks
- edit dashboard files
- connect to broker or OANDA
- use API keys
- call webhooks
- place real orders
- enable live trading
- commit
- push

## Validation

Run:

```powershell
powershell -NoProfile -Command "Get-ChildItem automation/orchestration/terminal_workstations -Filter *.ps1 | ForEach-Object { [scriptblock]::Create((Get-Content -Raw -Path $_.FullName)) | Out-Null }"
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsWorkstation.ps1
git diff --check
git status --short --branch
```

Expected result:

- All PowerShell scripts parse.
- Workstation launcher prints repo path, branch, git status, latest commits, GitHub issues, GitHub PRs, lane map, and next safe action.
- No Codex launch, extra windows, startup task, scheduled task, Windows Terminal settings edit, dashboard edit, broker action, or live trading action occurs.

## Next Safe Action

Review the workstation launcher output and checkpoint, then decide whether to approve a separate selective commit prompt.
