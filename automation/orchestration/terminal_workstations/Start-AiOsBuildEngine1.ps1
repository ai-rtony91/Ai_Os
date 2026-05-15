Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$roleName = "AI_OS BUILD ENGINE 1"

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host "========================================"
Write-Host $roleName
Write-Host "Primary Codex build lane"
Write-Host "Repo: $repoPath"
Write-Host "FancyZones target: width 378, height 350"
Write-Host "Manual only: start Codex only after explicit operator action"
Write-Host "Safety: no worker auto-launch, startup tasks, scheduled tasks, broker, OANDA, API keys, webhooks, real orders, or live trading"
Write-Host "========================================"
Write-Host ""
Write-Host "Suggested first check:"
Write-Host "  git status --short --branch"
Write-Host ""
