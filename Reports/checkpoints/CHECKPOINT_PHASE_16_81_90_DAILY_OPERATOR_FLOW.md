# Checkpoint: Phase 16.81-90 Daily Operator Flow

## Task

Improve the daily operator launcher so one command runs preflight, supervisor, operator menu, and the three AI_OS deck launches.

## Files Changed

- `automation/orchestration/terminal_workstations/Start-AiOsOneCommandLauncher.ps1`
- `automation/orchestration/terminal_workstations/Show-AiOsLauncherPreflight.ps1`
- `automation/orchestration/terminal_workstations/Show-AiOsOperatorMenu.ps1`
- `automation/orchestration/supervisor/Start-AiOsSupervisor.ps1`
- `automation/orchestration/terminal_workstations/README_TERMINAL_WORKSTATIONS.md`
- `docs/AI_OS/orchestration/PHASE_16_81_90_DAILY_OPERATOR_FLOW.md`
- `Reports/checkpoints/CHECKPOINT_PHASE_16_81_90_DAILY_OPERATOR_FLOW.md`

## Safety Rules

- No Codex auto-launch.
- No startup tasks.
- No scheduled tasks.
- No Windows Terminal JSON edits.
- No WScript.Shell.
- No SendKeys.
- No ALT+SPACE.
- No automatic resize.
- No commit.
- No push.
- No merge.
- No issue creation.
- No PR creation.
- No dashboard edits.
- No broker, OANDA, API, webhook, or live trading work.

## Validation Plan

```powershell
powershell -NoProfile -Command "Get-ChildItem automation/orchestration/terminal_workstations -Filter *.ps1 | ForEach-Object { [scriptblock]::Create((Get-Content -Raw -Path $_.FullName)) | Out-Null }"
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsOneCommandLauncher.ps1 -Preview
git diff --check
git status --short --branch
```

## Next Safe Action

Run the launcher in preview mode first. If the output looks safe, run the launcher without `-Preview` to open Command Deck, Build Engine, and Validation Deck.
