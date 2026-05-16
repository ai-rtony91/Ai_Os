Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$roleName = "Ai_Os BUILD ENGINE"
$border = "#" * 100
$titleIcon = [char]::ConvertFromUtf32(0x1F7E2)

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host $border -ForegroundColor Green
Write-Host ""
Write-Host "$titleIcon Ai_Os BUILD ENGINE" -ForegroundColor Green
Write-Host "LOOK FOR THIS COLOR TO IDENTIFY THIS WINDOW." -ForegroundColor Green
Write-Host ""
Write-Host "ROLE: Codex work lane. Manual Codex launch only." -ForegroundColor Green
Write-Host "MODE: Manual Codex start only" -ForegroundColor Cyan
Write-Host "STATUS: No Codex auto-launch, no worker launch, no scheduled tasks" -ForegroundColor Cyan
Write-Host "Repo: $repoPath" -ForegroundColor Cyan
Write-Host ""
Write-Host $border -ForegroundColor Green
Write-Host $border -ForegroundColor Green
Write-Host $border -ForegroundColor Yellow
Write-Host "=== COPY START ===" -ForegroundColor Yellow
Write-Host "Paste terminal output between COPY START and COPY END when sending to ChatGPT." -ForegroundColor White
Write-Host "=== COPY END ===" -ForegroundColor Yellow
Write-Host $border -ForegroundColor Yellow
Write-Host ""
Write-Host "Allowed actions:" -ForegroundColor Green
Write-Host "  review assigned prompt"
Write-Host "  inspect files"
Write-Host "  run approved APPLY work"
Write-Host "  run scoped validators"
Write-Host "  launch Codex manually only when the operator chooses"
Write-Host ""
Write-Host "Blocked actions:" -ForegroundColor Red
Write-Host "  no Codex auto-launch" -ForegroundColor Red
Write-Host "  no extra windows" -ForegroundColor Red
Write-Host "  no startup tasks" -ForegroundColor Red
Write-Host "  no scheduled tasks" -ForegroundColor Red
Write-Host "  no dashboard edits unless explicitly scoped" -ForegroundColor Red
Write-Host "  no broker, OANDA, API keys, webhooks, real orders, or live trading" -ForegroundColor Red
Write-Host "  no commit or push without explicit approval" -ForegroundColor Red
Write-Host ""
