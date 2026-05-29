Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
$roleName = "QUEUE CONTROL / SIGNAL ROUTER"
$border = "#" * 100
$titleIcon = [char]::ConvertFromUtf32(0x1F4E1)  # Satellite antenna - signal router

if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoPath = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host $border -ForegroundColor DarkCyan
Write-Host ""
Write-Host "  $titleIcon  QUEUE CONTROL / SIGNAL ROUTER" -ForegroundColor DarkCyan
Write-Host "  LOOK FOR THIS COLOR TO IDENTIFY THIS WINDOW." -ForegroundColor DarkCyan
Write-Host ""
Write-Host "  AIOS BASE : #05070b  TEXT #e5f6ff  ACTION #38bdf8  WARNING #ffd166" -ForegroundColor Cyan
Write-Host "  OCC LANE  : NORTH_OCC  |  Signal router for packet queue and issue/PR tracking" -ForegroundColor DarkCyan
Write-Host "  MODE      : [ DRY_RUN ]  Display and review only" -ForegroundColor Cyan
Write-Host "  STATUS    : [ READ-ONLY ]  No mutation, no launch, no commit" -ForegroundColor Cyan
Write-Host "  Repo      : $repoPath" -ForegroundColor Cyan
Write-Host ""
Write-Host $border -ForegroundColor DarkCyan
Write-Host $border -ForegroundColor DarkCyan
Write-Host $border -ForegroundColor Yellow
Write-Host "  === COPY START ===" -ForegroundColor Yellow
Write-Host "  Paste terminal output between COPY START and COPY END when sending to Claude." -ForegroundColor White
Write-Host "  === COPY END ===" -ForegroundColor Yellow
Write-Host $border -ForegroundColor Yellow
Write-Host ""
Write-Host "  Queue display commands:" -ForegroundColor Green
Write-Host "    powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-packet-queue-ledger.ps1"
Write-Host "    powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-queue-health-supervisor.ps1"
Write-Host ""
Write-Host "  Blocked actions:" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  packet launch, worker launch, startup/scheduled tasks" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  broker, OANDA, API keys, webhooks, real orders, live trading" -ForegroundColor Red
Write-Host ""

$waitScriptPath = Join-Path $PSScriptRoot "Wait-AiOsVisibleTerminal.ps1"
& $waitScriptPath -State "IDLE" -Message "Queue Control remains visible for signal routing review."
