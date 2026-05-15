Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$roleName = "AI_OS TELEMETRY DECK"

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host "========================================"
Write-Host $roleName
Write-Host "Progress, logs, metrics, checkpoints"
Write-Host "Repo: $repoPath"
Write-Host "FancyZones target: width 378, height 350"
Write-Host "Safety: local display only; no secret collection, startup tasks, scheduled tasks, broker, OANDA, API keys, webhooks, real orders, or live trading"
Write-Host "========================================"
Write-Host ""
Write-Host "Suggested read-only telemetry displays:"
Write-Host "  Get-ChildItem Reports/checkpoints -Filter CHECKPOINT_PHASE_16_*.md"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-orchestration-status.ps1"
Write-Host ""
