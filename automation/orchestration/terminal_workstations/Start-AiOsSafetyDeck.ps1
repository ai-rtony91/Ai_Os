Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
$roleName = "AI_OS SAFETY DECK"

if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoPath = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host "========================================"
Write-Host $roleName
Write-Host "Blocked live trading / broker / secret checks"
Write-Host "Repo: $repoPath"
Write-Host "FancyZones target: width 378, height 350"
Write-Host "Safety: no broker, OANDA, API keys, webhooks, real orders, live trading, startup tasks, scheduled tasks, commits, or pushes"
Write-Host "========================================"
Write-Host ""
Write-Host "Manual safety review targets:"
Write-Host "  blocked paths: broker/, oanda/, webhooks/, live_trading/, secrets/, .env"
Write-Host "  protected paths: apps/dashboard/, .git/, .codex_backups/"
Write-Host ""
