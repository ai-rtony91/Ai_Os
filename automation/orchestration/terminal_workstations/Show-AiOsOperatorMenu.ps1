Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$border = "#" * 100

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = "AI_OS OPERATOR MENU"

Write-Host $border -ForegroundColor Cyan
Write-Host "AI_OS OPERATOR MENU" -ForegroundColor Cyan
Write-Host "Simple commands only. No destructive actions." -ForegroundColor Gray
Write-Host $border -ForegroundColor Cyan
Write-Host ""

Write-Host "Start workstation:" -ForegroundColor Green
Write-Host "  powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsOneCommandLauncher.ps1"
Write-Host ""
Write-Host "Preview workstation launch:" -ForegroundColor Green
Write-Host "  powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsOneCommandLauncher.ps1 -Preview"
Write-Host ""
Write-Host "Show repo status:" -ForegroundColor Green
Write-Host "  git status --short --branch"
Write-Host ""
Write-Host "Show GitHub status:" -ForegroundColor Green
Write-Host "  powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Show-AiOsLauncherPreflight.ps1"
Write-Host ""
Write-Host "Show supervisor:" -ForegroundColor Green
Write-Host "  powershell -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Start-AiOsSupervisor.ps1"
Write-Host ""
Write-Host "Show canonical operator status:" -ForegroundColor Green
Write-Host "  powershell -ExecutionPolicy Bypass -File automation/orchestration/control/Get-AiOsOperatorControlLoop.DRY_RUN.ps1"
Write-Host ""
Write-Host "Launch Command Deck:" -ForegroundColor Magenta
Write-Host "  powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsCommandDeck.ps1"
Write-Host ""
Write-Host "Launch Build Engine:" -ForegroundColor Green
Write-Host "  powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsBuildEngine.ps1"
Write-Host ""
Write-Host "Launch Validation Deck:" -ForegroundColor Cyan
Write-Host "  powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsValidationDeck.ps1"
Write-Host ""
Write-Host "Next safe action:" -ForegroundColor Yellow
Write-Host "  Use the launcher output. If safe, work from Command Deck, Build Engine, and Validation Deck. Launch Codex manually only in the Build Engine."
Write-Host ""
Write-Host "Blocked actions:" -ForegroundColor Red
Write-Host "  no commit, push, merge, branch creation, issue creation, PR creation, installs, scheduled tasks, startup tasks, Codex auto-launch, dashboard edits, broker/OANDA/API/webhook/live trading work" -ForegroundColor Red
