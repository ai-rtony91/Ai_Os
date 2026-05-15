Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$roleName = "AI_OS RECOVERY DECK"

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host "========================================"
Write-Host $roleName
Write-Host "Recovery/bootstrap checks only"
Write-Host "Repo: $repoPath"
Write-Host "FancyZones target: width 378, height 350"
Write-Host "Safety: review only; no restore, worker launch, startup tasks, scheduled tasks, broker, OANDA, API keys, webhooks, real orders, or live trading"
Write-Host "========================================"
Write-Host ""
Write-Host "Suggested read-only recovery displays:"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-recovery-bootstrap.ps1"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-recovery-bootstrap-supervisor.ps1"
Write-Host ""
