Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$roleName = "AI_OS QUEUE CONTROL"

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host "========================================"
Write-Host $roleName
Write-Host "Packet queue and issue/PR tracking"
Write-Host "Repo: $repoPath"
Write-Host "FancyZones target: width 378, height 350"
Write-Host "Safety: display and review only; no packet launch, worker launch, startup tasks, scheduled tasks, broker, OANDA, API keys, webhooks, real orders, or live trading"
Write-Host "========================================"
Write-Host ""
Write-Host "Suggested read-only queue displays:"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-packet-queue-ledger.ps1"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-queue-health-supervisor.ps1"
Write-Host ""
