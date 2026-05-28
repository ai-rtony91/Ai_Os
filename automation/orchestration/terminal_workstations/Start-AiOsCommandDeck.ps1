Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoPath = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot
$roleName = "MAIN CONTROL / COMMAND THRONE"
$border = "#" * 100
$titleIcon = [char]::ConvertFromUtf32(0x1F451)

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host $border -ForegroundColor Magenta
Write-Host ""
Write-Host "  $titleIcon  MAIN CONTROL / COMMAND THRONE" -ForegroundColor Magenta
Write-Host "  LOOK FOR THIS COLOR TO IDENTIFY THIS WINDOW." -ForegroundColor Magenta
Write-Host ""
Write-Host "  AIOS BASE : #05070b  TEXT #e5f6ff  VIOLET #a855f7  ACTION #38bdf8" -ForegroundColor Cyan
Write-Host "  OCC LANE  : MAIN_CONTROL  |  Persistent all-day command deck" -ForegroundColor Magenta
Write-Host "  MODE      : [ MANUAL ]  Operator control only - no auto-launch" -ForegroundColor Cyan
Write-Host "  STATUS    : [ READ-ONLY ]  No Codex auto-launch, no scheduled/startup tasks" -ForegroundColor Cyan
Write-Host "  Repo      : $repoPath" -ForegroundColor Cyan
Write-Host ""
Write-Host $border -ForegroundColor Magenta
Write-Host $border -ForegroundColor Magenta
Write-Host $border -ForegroundColor Yellow
Write-Host "  === COPY START ===" -ForegroundColor Yellow
Write-Host "  Paste terminal output between COPY START and COPY END when sending to Claude." -ForegroundColor White
Write-Host "  === COPY END ===" -ForegroundColor Yellow
Write-Host $border -ForegroundColor Yellow
Write-Host ""
Write-Host "  Allowed actions:" -ForegroundColor Green
Write-Host "    [ PASS ]  git status --short --branch" -ForegroundColor Green
Write-Host "    [ PASS ]  git log --oneline -5" -ForegroundColor Green
Write-Host "    [ PASS ]  gh --version" -ForegroundColor Green
Write-Host "    [ PASS ]  gh issue list --state open" -ForegroundColor Green
Write-Host "    [ PASS ]  gh pr list --state open" -ForegroundColor Green
Write-Host "    [ GATE ]  selective commit/merge only after explicit Human Owner approval" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Blocked actions:" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  Codex auto-launch, extra windows, startup/scheduled tasks" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  dashboard edits" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  broker, OANDA, API keys, webhooks, real orders, live trading" -ForegroundColor Red
Write-Host ""
