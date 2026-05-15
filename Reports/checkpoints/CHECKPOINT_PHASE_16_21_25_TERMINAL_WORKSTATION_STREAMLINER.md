# Checkpoint Phase 16.21-25 Terminal Workstation Streamliner

Checkpoint status: APPLY one-launch command deck created

## Files Planned

- `automation/orchestration/terminal_workstations/Start-AiOsWorkstation.ps1`
- `automation/orchestration/terminal_workstations/Start-AiOsCommandDeck.ps1`
- `automation/orchestration/terminal_workstations/Start-AiOsBuildEngine.ps1`
- `automation/orchestration/terminal_workstations/Start-AiOsValidationDeck.ps1`
- `automation/orchestration/terminal_workstations/README_TERMINAL_WORKSTATIONS.md`
- `docs/AI_OS/orchestration/PHASE_16_21_25_TERMINAL_WORKSTATION_STREAMLINER.md`
- `Reports/checkpoints/CHECKPOINT_PHASE_16_21_25_TERMINAL_WORKSTATION_STREAMLINER.md`

## Safety Status

The workstation scripts are current-shell launchers only.

They set the repo path, set a clean title, print banners, show roles, show allowed actions, and show blocked actions.

No WScript.Shell, SendKeys, ALT+SPACE automation, Num Lock changes, Windows Terminal settings edits, Codex auto-launch, extra window launch, startup task, scheduled task, install, dashboard edit, broker action, OANDA action, API key use, webhook call, real order, live trading, commit, or push action was added.

## Validation Commands

```powershell
powershell -NoProfile -Command "Get-ChildItem automation/orchestration/terminal_workstations -Filter *.ps1 | ForEach-Object { [scriptblock]::Create((Get-Content -Raw -Path $_.FullName)) | Out-Null }"
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsWorkstation.ps1
git diff --check
git status --short --branch
```

## Expected Result

- All scripts parse.
- Workstation launcher prints startup banner, repo path, branch, git status, latest commits, open issues, open PRs, lane roles, and next safe action.
- No Codex auto-launch, extra windows, startup task, scheduled task, Windows Terminal settings edit, dashboard edit, broker action, live trading action, commit, or push occurs.

## Next Safe Action

Review validation output and approve a separate selective commit only if Phase 16.21-25 One-Launch Command Deck is accepted.
