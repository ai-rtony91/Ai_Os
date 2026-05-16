Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$roleName = "AI_OS VALIDATION DECK"

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host "========================================" -ForegroundColor Cyan
Write-Host $roleName -ForegroundColor Cyan
Write-Host "Role: PowerShell status checks, validators, queue checks, and repo checks" -ForegroundColor Cyan
Write-Host "Repo: $repoPath" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "=== COPY START ===" -ForegroundColor Yellow
Write-Host "Paste terminal output between COPY START and COPY END when sending to ChatGPT." -ForegroundColor Gray
Write-Host "=== COPY END ===" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Allowed actions:" -ForegroundColor Green
Write-Host "  git diff --check"
Write-Host "  git status --short --branch"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File <approved-validator.ps1>"
Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-packet-queue-ledger.ps1"
Write-Host ""
Write-Host "Blocked actions:" -ForegroundColor Red
Write-Host "  no Codex auto-launch" -ForegroundColor Red
Write-Host "  no extra windows" -ForegroundColor Red
Write-Host "  no startup tasks" -ForegroundColor Red
Write-Host "  no scheduled tasks" -ForegroundColor Red
Write-Host "  no dashboard edits" -ForegroundColor Red
Write-Host "  no broker, OANDA, API keys, webhooks, real orders, or live trading" -ForegroundColor Red
Write-Host "  no commit or push without explicit approval" -ForegroundColor Red
Write-Host ""
