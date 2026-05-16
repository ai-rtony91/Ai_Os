Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$roleName = "AI_OS COMMAND DECK"

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host "========================================" -ForegroundColor Magenta
Write-Host $roleName -ForegroundColor Magenta
Write-Host "Role: Main control window for Git, GitHub CLI, issues, PRs, commits, and merges" -ForegroundColor Cyan
Write-Host "Repo: $repoPath" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "=== COPY START ===" -ForegroundColor Yellow
Write-Host "Paste terminal output between COPY START and COPY END when sending to ChatGPT." -ForegroundColor Gray
Write-Host "=== COPY END ===" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Allowed actions:" -ForegroundColor Green
Write-Host "  git status --short --branch"
Write-Host "  git log --oneline -5"
Write-Host "  gh --version"
Write-Host "  gh issue list --state open"
Write-Host "  gh pr list --state open"
Write-Host "  selective commit/merge only after explicit approval"
Write-Host ""
Write-Host "Blocked actions:" -ForegroundColor Red
Write-Host "  no Codex auto-launch" -ForegroundColor Red
Write-Host "  no extra windows" -ForegroundColor Red
Write-Host "  no startup tasks" -ForegroundColor Red
Write-Host "  no scheduled tasks" -ForegroundColor Red
Write-Host "  no dashboard edits" -ForegroundColor Red
Write-Host "  no broker, OANDA, API keys, webhooks, real orders, or live trading" -ForegroundColor Red
Write-Host ""
