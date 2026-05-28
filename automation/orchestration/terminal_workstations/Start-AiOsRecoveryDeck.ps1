Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
$roleName = "RECOVERY DECK / RESTORE BAY"
$border = "#" * 100
$titleIcon = [char]::ConvertFromUtf32(0x1F527)  # Wrench - restore bay

if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoPath = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host $border -ForegroundColor Yellow
Write-Host ""
Write-Host "  $titleIcon  RECOVERY DECK / RESTORE BAY" -ForegroundColor Yellow
Write-Host "  LOOK FOR THIS COLOR TO IDENTIFY THIS WINDOW." -ForegroundColor Yellow
Write-Host ""
Write-Host "  AIOS BASE : #05070b  TEXT #e5f6ff  WARNING #ffd166  ACTION #38bdf8" -ForegroundColor DarkYellow
Write-Host "  OCC LANE  : SOUTH_OCC  |  Recovery and bootstrap verification lane" -ForegroundColor Yellow
Write-Host "  MODE      : [ DRY_RUN ]  Review and verification only" -ForegroundColor DarkYellow
Write-Host "  STATUS    : [ READ-ONLY ]  No restore, no worker launch, no mutation" -ForegroundColor DarkYellow
Write-Host "  Repo      : $repoPath" -ForegroundColor DarkYellow
Write-Host ""
Write-Host $border -ForegroundColor Yellow
Write-Host $border -ForegroundColor Yellow
Write-Host $border -ForegroundColor Yellow
Write-Host "  === COPY START ===" -ForegroundColor Yellow
Write-Host "  Paste terminal output between COPY START and COPY END when sending to Claude." -ForegroundColor White
Write-Host "  === COPY END ===" -ForegroundColor Yellow
Write-Host $border -ForegroundColor Yellow
Write-Host ""
Write-Host "  Recovery display commands:" -ForegroundColor Green
Write-Host "    powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-recovery-bootstrap.ps1"
Write-Host "    powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-recovery-bootstrap-supervisor.ps1"
Write-Host ""
Write-Host "  Blocked actions:" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  restore execution, worker launch, startup/scheduled tasks" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  broker, OANDA, API keys, webhooks, real orders, live trading" -ForegroundColor Red
Write-Host ""
