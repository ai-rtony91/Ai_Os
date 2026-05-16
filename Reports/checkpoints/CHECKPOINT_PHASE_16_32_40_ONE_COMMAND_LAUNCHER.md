# Checkpoint Phase 16.32-40 One-Command AI_OS Launcher

Checkpoint status: APPLY one-command launcher created

## Files Planned

- `automation/orchestration/terminal_workstations/Start-AiOsOneCommandLauncher.ps1`
- `automation/orchestration/terminal_workstations/Show-AiOsLauncherPreflight.ps1`
- `automation/orchestration/terminal_workstations/Show-AiOsOperatorMenu.ps1`
- `automation/orchestration/terminal_workstations/README_TERMINAL_WORKSTATIONS.md`
- `docs/AI_OS/orchestration/PHASE_16_32_40_ONE_COMMAND_LAUNCHER.md`
- `Reports/checkpoints/CHECKPOINT_PHASE_16_32_40_ONE_COMMAND_LAUNCHER.md`

## Safety Status

The one-command launcher is safe by default.

It can print status, read git state, read GitHub CLI state, and open deck windows.

It does not auto-launch Codex, edit files, commit, push, merge, create branches, create issues, create PRs, install anything, create startup tasks, create scheduled tasks, edit Windows Terminal settings JSON, edit dashboard files, touch protected root files, or touch broker/OANDA/API/webhook/live trading files.

## Validation Commands

```powershell
powershell -NoProfile -Command "Get-ChildItem automation/orchestration/terminal_workstations -Filter *.ps1 | ForEach-Object { [scriptblock]::Create((Get-Content -Raw -Path $_.FullName)) | Out-Null }"
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Show-AiOsLauncherPreflight.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Show-AiOsOperatorMenu.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsOneCommandLauncher.ps1 -Preview
git diff --check
git status --short --branch
```

## Expected Result

- All scripts parse.
- Preflight prints repo, branch, git, and GitHub status.
- Operator menu prints simple commands.
- Launcher preview shows the three deck windows it would open.
- No Codex auto-launch, file mutation, commit, push, merge, branch creation, issue creation, PR creation, install, scheduled task, startup task, dashboard edit, or live trading work occurs.

## Next Safe Action

Review validation output and approve a separate selective commit only if Phase 16.32-40 One-Command AI_OS Launcher is accepted.
