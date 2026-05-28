Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoPath = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot
$roleName = "VALIDATION DECK / EVIDENCE SHIELD"
$border = "#" * 100
$titleIcon = [char]::ConvertFromUtf32(0x1F6E1)

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host $border -ForegroundColor Cyan
Write-Host ""
Write-Host "  $titleIcon  VALIDATION DECK / EVIDENCE SHIELD" -ForegroundColor Cyan
Write-Host "  LOOK FOR THIS COLOR TO IDENTIFY THIS WINDOW." -ForegroundColor Cyan
Write-Host ""
Write-Host "  AIOS BASE : #05070b  TEXT #e5f6ff  ACTION #38bdf8  PASS #37ff88" -ForegroundColor DarkCyan
Write-Host "  OCC LANE  : VALIDATOR_OCC  |  Schema chain and correctness validation" -ForegroundColor Cyan
Write-Host "  ROLE      : PowerShell status checks, validators, queue checks, repo checks" -ForegroundColor DarkCyan
Write-Host "  MODE      : [ DRY_RUN ]  Read-only validation and approved checks" -ForegroundColor DarkCyan
Write-Host "  STATUS    : [ READ-ONLY ]  No Codex auto-launch, no scheduled/startup tasks" -ForegroundColor DarkCyan
Write-Host "  Repo      : $repoPath" -ForegroundColor Cyan
Write-Host ""
Write-Host $border -ForegroundColor Cyan
Write-Host $border -ForegroundColor Cyan
Write-Host $border -ForegroundColor Yellow
Write-Host "  === COPY START ===" -ForegroundColor Yellow
Write-Host "  Paste terminal output between COPY START and COPY END when sending to Claude." -ForegroundColor White
Write-Host "  === COPY END ===" -ForegroundColor Yellow
Write-Host $border -ForegroundColor Yellow
Write-Host ""
Write-Host "  Allowed actions:" -ForegroundColor Green
Write-Host "    [ PASS ]  git diff --check" -ForegroundColor Green
Write-Host "    [ PASS ]  git status --short --branch" -ForegroundColor Green
Write-Host "    [ PASS ]  powershell -NoProfile -ExecutionPolicy Bypass -File <approved-validator.ps1>" -ForegroundColor Green
Write-Host "    [ PASS ]  powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-packet-queue-ledger.ps1" -ForegroundColor Green
Write-Host ""
Write-Host "  Blocked actions:" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  Codex auto-launch, extra windows, startup/scheduled tasks" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  dashboard edits, commit or push without explicit approval" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  broker, OANDA, API keys, webhooks, real orders, live trading" -ForegroundColor Red
Write-Host ""
