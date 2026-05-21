Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
$roleName = "AI_OS QUEUE CONTROL"

if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoPath = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot

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
