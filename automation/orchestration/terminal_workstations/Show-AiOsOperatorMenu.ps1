Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
$border = "#" * 100
$titleIcon = [char]::ConvertFromUtf32(0x1F451)  # Crown - MAIN CONTROL / COMMAND THRONE

if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoPath = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = "AI_OS OPERATOR MENU"

Write-Host $border -ForegroundColor Cyan
Write-Host ""
Write-Host "  $titleIcon  MAIN CONTROL / COMMAND THRONE" -ForegroundColor Cyan
Write-Host "  LOOK FOR THIS COLOR TO IDENTIFY THIS WINDOW." -ForegroundColor Cyan
Write-Host ""
Write-Host "  AIOS BASE : #05070b  TEXT #e5f6ff  ACTION #38bdf8  GLOW #00a3ff" -ForegroundColor DarkCyan
Write-Host "  OCC LANE  : ALL LANES  |  Persistent command throne for all-day operator control" -ForegroundColor Cyan
Write-Host "  MODE      : [ DRY_RUN ]  Simple read-only commands only" -ForegroundColor DarkCyan
Write-Host "  STATUS    : [ READ-ONLY ]  No destructive actions" -ForegroundColor DarkCyan
Write-Host "  Repo      : $repoPath" -ForegroundColor DarkCyan
Write-Host ""
Write-Host $border -ForegroundColor Cyan
Write-Host ""

Write-Host "  [ LAUNCH ]  Workstation (master launcher):" -ForegroundColor Green
Write-Host "    powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsOneCommandLauncher.ps1"
Write-Host ""
Write-Host "  [ LAUNCH ]  Preview workstation:" -ForegroundColor Green
Write-Host "    powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsOneCommandLauncher.ps1 -Preview"
Write-Host ""
Write-Host "  [ STATUS ]  Repo status:" -ForegroundColor Cyan
Write-Host "    git status --short --branch"
Write-Host ""
Write-Host "  [ STATUS ]  GitHub preflight:" -ForegroundColor Cyan
Write-Host "    powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Show-AiOsLauncherPreflight.ps1"
Write-Host ""
Write-Host "  [ STATUS ]  Supervisor:" -ForegroundColor Cyan
Write-Host "    powershell -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Start-AiOsSupervisor.ps1"
Write-Host ""
Write-Host "  [ STATUS ]  Operator control loop:" -ForegroundColor Cyan
Write-Host "    powershell -ExecutionPolicy Bypass -File automation/orchestration/control/Get-AiOsOperatorControlLoop.DRY_RUN.ps1"
Write-Host ""
Write-Host "  [ MAGENTA ]  MAIN CONTROL / COMMAND THRONE  — Git, GitHub CLI, commits, merges:" -ForegroundColor Magenta
Write-Host "    powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsCommandDeck.ps1"
Write-Host ""
Write-Host "  [ GREEN   ]  BUILD ENGINE / BUILDER FORGE  — temporary OCC worker lane:" -ForegroundColor Green
Write-Host "    powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsBuildEngine.ps1"
Write-Host ""
Write-Host "  [ CYAN    ]  VALIDATION DECK / EVIDENCE SHIELD  — validators, queue checks, repo checks:" -ForegroundColor Cyan
Write-Host "    powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsValidationDeck.ps1"
Write-Host ""
Write-Host "  Next safe action:" -ForegroundColor Yellow
Write-Host "  Run preflight, then work from Command Deck, Build Engine, or Validation Deck."
Write-Host "  Launch Codex manually only inside the Build Engine."
Write-Host ""
Write-Host "  Blocked actions:" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  commit, push, merge, branch creation, PR/issue creation" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  installs, scheduled tasks, startup tasks, Codex auto-launch" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  broker, OANDA, API keys, webhooks, live trading" -ForegroundColor Red
