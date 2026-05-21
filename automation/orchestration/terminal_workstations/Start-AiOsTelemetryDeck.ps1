Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
$roleName = "AI_OS TELEMETRY DECK"

if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoPath = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot

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
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/control/Get-AiOsOperatorControlLoop.DRY_RUN.ps1"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-orchestration-status.ps1"
Write-Host ""
