# Phase 16.81-90 Daily Operator Flow

## Purpose

This phase improves the real daily AI_OS startup flow.

The operator can run one command to perform preflight checks, run the supervisor, print the operator menu, and open the three AI_OS deck windows.

## One Command

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsOneCommandLauncher.ps1
```

## Daily Flow

The launcher runs:

1. launcher preflight
2. supervisor simple mode
3. operator menu
4. Command Deck
5. Build Engine
6. Validation Deck
7. exact next safe action display
8. manual Codex reminder

Preview mode runs the checks and menu without opening deck windows:

```powershell
powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsOneCommandLauncher.ps1 -Preview
```

## Safety

This flow does not launch Codex automatically, create startup tasks, create scheduled tasks, edit Windows Terminal JSON, use WScript.Shell, use SendKeys, press ALT+SPACE, resize windows automatically, commit, push, merge, create issues, create PRs, touch dashboard files, or touch broker/OANDA/API/webhook/live trading.

## Validation

```powershell
powershell -NoProfile -Command "Get-ChildItem automation/orchestration/terminal_workstations -Filter *.ps1 | ForEach-Object { [scriptblock]::Create((Get-Content -Raw -Path $_.FullName)) | Out-Null }"
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsOneCommandLauncher.ps1 -Preview
git diff --check
git status --short --branch
```
