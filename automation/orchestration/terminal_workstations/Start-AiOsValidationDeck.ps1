Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$roleName = "Ai_Os VALIDATION DECK"
$border = "#" * 100
$titleIcon = [char]::ConvertFromUtf32(0x1F535)

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host $border -ForegroundColor Cyan
Write-Host ""
Write-Host "$titleIcon Ai_Os VALIDATION DECK" -ForegroundColor Cyan
Write-Host "LOOK FOR THIS COLOR TO IDENTIFY THIS WINDOW." -ForegroundColor Cyan
Write-Host ""
Write-Host "ROLE: PowerShell status checks, validators, queue checks, and repo checks" -ForegroundColor Cyan
Write-Host "MODE: Read-only validation and approved checks" -ForegroundColor White
Write-Host "STATUS: No Codex auto-launch, no scheduled tasks, no startup tasks" -ForegroundColor White
Write-Host "Repo: $repoPath" -ForegroundColor Cyan
Write-Host ""
Write-Host $border -ForegroundColor Cyan
Write-Host $border -ForegroundColor Cyan
Write-Host $border -ForegroundColor Yellow
Write-Host "=== COPY START ===" -ForegroundColor Yellow
Write-Host "Paste terminal output between COPY START and COPY END when sending to ChatGPT." -ForegroundColor White
Write-Host "=== COPY END ===" -ForegroundColor Yellow
Write-Host $border -ForegroundColor Yellow
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
