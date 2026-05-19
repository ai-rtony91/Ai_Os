# Phase 16.32-40 One-Command AI_OS Launcher

## Purpose

Phase 16.32-40 designs the practical one-command launcher for the AI_OS terminal workstation.

The operator should be able to run one command, review preflight status, and open the three AI_OS deck windows without rebuilding the setup manually.

## Files Added Or Updated

- `automation/orchestration/terminal_workstations/Start-AiOsOneCommandLauncher.ps1`
- `automation/orchestration/terminal_workstations/Show-AiOsLauncherPreflight.ps1`
- `automation/orchestration/terminal_workstations/Show-AiOsOperatorMenu.ps1`
- `automation/orchestration/terminal_workstations/README_TERMINAL_WORKSTATIONS.md`
- `docs/AI_OS/orchestration/PHASE_16_32_40_ONE_COMMAND_LAUNCHER.md`
- `Reports/checkpoints/CHECKPOINT_PHASE_16_32_40_ONE_COMMAND_LAUNCHER.md`

## Plain Language Model

- Command Deck = main control.
- Build Engine = Codex lane.
- Validation Deck = checks lane.
- One-command launcher = opens the work setup.
- Preflight = checks before work starts.
- Manual Codex launch = prevents wrong auto-start.

## Launcher Behavior

`Start-AiOsOneCommandLauncher.ps1`:

- confirms repo path
- shows current branch
- shows git status
- shows latest commit
- checks GitHub CLI state when available
- opens the Command Deck, Build Engine, and Validation Deck when not in preview mode
- keeps Codex launch manual
- keeps window placement manual
- prints the next safe action

## Safety Boundary

The launcher may print status, open deck windows, read git state, read GitHub CLI state, and show next safe action.

It must not edit files, commit, push, merge, create branches, create issues, create PRs, install anything, create startup tasks, create scheduled tasks, edit Windows Terminal settings JSON, auto-launch Codex, edit dashboard files, touch protected root files, or touch broker/OANDA/API/webhook/live trading files.

## Validation

Run:

```powershell
powershell -NoProfile -Command "Get-ChildItem automation/orchestration/terminal_workstations -Filter *.ps1 | ForEach-Object { [scriptblock]::Create((Get-Content -Raw -Path $_.FullName)) | Out-Null }"
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Show-AiOsLauncherPreflight.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Show-AiOsOperatorMenu.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsOneCommandLauncher.ps1 -Preview
git diff --check
git status --short --branch
```

## Next Safe Action

Run the launcher in preview, review the output, then launch without `-Preview` only when the operator is ready to open the three deck windows.
