Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoPath = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot
$roleName = "BUILD ENGINE / BUILDER FORGE"
$border = "#" * 100
$titleIcon = [char]::ConvertFromUtf32(0x2699)

function Write-AiOsActivityCard {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,

        [Parameter(Mandatory = $true)]
        [string]$Text,

        [string]$ForegroundCode = "92",

        [string]$BackgroundCode = "48;5;24"
    )

    $escape = [char]27
    $line = ("  [{0,-8}] {1}" -f $Label, $Text)
    Write-Host "$($escape)[$BackgroundCode;$ForegroundCode`m$line$($escape)[0m"
}

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host $border -ForegroundColor Green
Write-Host ""
Write-Host "  $titleIcon  BUILD ENGINE / BUILDER FORGE" -ForegroundColor Green
Write-Host "  LOOK FOR THIS COLOR TO IDENTIFY THIS WINDOW." -ForegroundColor Green
Write-Host ""
Write-Host "  AIOS BASE : #05070b  TEXT #e5f6ff  OCC/PASS #37ff88  ACTION #38bdf8" -ForegroundColor Cyan
Write-Host "  OCC LANE  : EAST_OCC  |  Temporary packet-scoped worker forge" -ForegroundColor Green
Write-Host "  MODE      : [ MANUAL ]  Manual Codex start only - no auto-launch" -ForegroundColor Cyan
Write-Host "  STATUS    : [ READ-ONLY ]  No Codex auto-launch, no worker launch, no scheduled tasks" -ForegroundColor Cyan
Write-Host "  Repo      : $repoPath" -ForegroundColor Cyan
Write-Host ""
Write-AiOsActivityCard -Label "WORKING" -Text "temporary OCC worker stays visible for the assigned task lifecycle" -ForegroundCode "38;5;208"
Write-AiOsActivityCard -Label "COMPLETE" -Text "close after final APPLY/commit/push/sync report" -ForegroundCode "92"
Write-AiOsActivityCard -Label "BLOCKED" -Text "park visibly for operator review; do not spawn unlimited windows" -ForegroundCode "91"
Write-Host ""
Write-Host $border -ForegroundColor Green
Write-Host $border -ForegroundColor Green
Write-Host $border -ForegroundColor Yellow
Write-Host "  === COPY START ===" -ForegroundColor Yellow
Write-Host "  Paste terminal output between COPY START and COPY END when sending to Claude." -ForegroundColor White
Write-Host "  === COPY END ===" -ForegroundColor Yellow
Write-Host $border -ForegroundColor Yellow
Write-Host ""
Write-Host "  Allowed actions:" -ForegroundColor Green
Write-Host "    [ PASS ]  review assigned prompt" -ForegroundColor Green
Write-Host "    [ PASS ]  inspect files" -ForegroundColor Green
Write-Host "    [ PASS ]  run scoped validators" -ForegroundColor Green
Write-Host "    [ GATE ]  run approved APPLY work after Human Owner approval" -ForegroundColor Yellow
Write-Host "    [ GATE ]  launch Codex manually only when operator chooses" -ForegroundColor Yellow
Write-Host "    [ OCC  ]  temporary workers must show IDLE, COMPLETE, BLOCKED, or CLOSED state" -ForegroundColor Green
Write-Host ""
Write-Host "  Blocked actions:" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  Codex auto-launch, extra windows, startup/scheduled tasks" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  dashboard edits unless explicitly scoped" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  broker, OANDA, API keys, webhooks, real orders, live trading" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  commit or push without explicit Human Owner approval" -ForegroundColor Red
Write-Host ""

$waitScriptPath = Join-Path $PSScriptRoot "Wait-AiOsVisibleTerminal.ps1"
& $waitScriptPath -State "IDLE" -Message "Build Engine remains visible. Temporary OCC workers stay open on COMPLETE or BLOCKED."
