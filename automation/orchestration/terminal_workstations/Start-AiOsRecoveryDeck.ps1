Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
$roleName = "AI_OS RECOVERY DECK"

if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoPath = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host "========================================"
Write-Host $roleName
Write-Host "Recovery/bootstrap checks only"
Write-Host "Repo: $repoPath"
Write-Host "FancyZones target: width 378, height 350"
Write-Host "Safety: review only; no restore, worker launch, startup tasks, scheduled tasks, broker, OANDA, API keys, webhooks, real orders, or live trading"
Write-Host "========================================"
Write-Host ""
Write-Host "Suggested read-only recovery displays:"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-recovery-bootstrap.ps1"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-recovery-bootstrap-supervisor.ps1"
Write-Host ""
