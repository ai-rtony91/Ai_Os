Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
$roleName = "TELEMETRY DECK / DATA PULSE"
$border = "#" * 100
$titleIcon = [char]::ConvertFromUtf32(0x1F4A0)  # Diamond - data pulse

if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoPath = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host $border -ForegroundColor Cyan
Write-Host ""
Write-Host "  $titleIcon  TELEMETRY DECK / DATA PULSE" -ForegroundColor Cyan
Write-Host "  LOOK FOR THIS COLOR TO IDENTIFY THIS WINDOW." -ForegroundColor Cyan
Write-Host ""
Write-Host "  AIOS BASE : #05070b  TEXT #e5f6ff  BLUE GLOW #00a3ff  PASS #37ff88" -ForegroundColor DarkCyan
Write-Host "  OCC LANE  : NORTH_OCC  |  Progress, logs, metrics, checkpoints" -ForegroundColor Cyan
Write-Host "  MODE      : [ DRY_RUN ]  Local display only" -ForegroundColor DarkCyan
Write-Host "  STATUS    : [ READ-ONLY ]  No secret collection, no mutation" -ForegroundColor DarkCyan
Write-Host "  Repo      : $repoPath" -ForegroundColor DarkCyan
Write-Host ""
Write-Host $border -ForegroundColor Cyan
Write-Host $border -ForegroundColor Cyan
Write-Host $border -ForegroundColor Yellow
Write-Host "  === COPY START ===" -ForegroundColor Yellow
Write-Host "  Paste terminal output between COPY START and COPY END when sending to Claude." -ForegroundColor White
Write-Host "  === COPY END ===" -ForegroundColor Yellow
Write-Host $border -ForegroundColor Yellow
Write-Host ""
Write-Host "  Telemetry display commands:" -ForegroundColor Green
Write-Host "    Get-ChildItem Reports/checkpoints -Filter CHECKPOINT_PHASE_16_*.md"
Write-Host "    powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/control/Get-AiOsOperatorControlLoop.DRY_RUN.ps1"
Write-Host "    powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-orchestration-status.ps1"
Write-Host ""
Write-Host "  Blocked actions:" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  secret collection, startup/scheduled tasks" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  broker, OANDA, API keys, webhooks, real orders, live trading" -ForegroundColor Red
Write-Host ""
