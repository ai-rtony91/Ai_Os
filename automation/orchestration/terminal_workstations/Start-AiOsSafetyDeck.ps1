Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$roleName = "AI_OS SAFETY DECK"

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

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
