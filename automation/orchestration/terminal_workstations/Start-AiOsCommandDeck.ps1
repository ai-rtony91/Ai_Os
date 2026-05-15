Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$roleName = "AI_OS COMMAND DECK"

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host "========================================"
Write-Host $roleName
Write-Host "Role: Main control window for Git, GitHub CLI, issues, PRs, commits, and merges"
Write-Host "Repo: $repoPath"
Write-Host "========================================"
Write-Host "=== COPY START ==="
Write-Host "Paste terminal output between COPY START and COPY END when sending to ChatGPT."
Write-Host "=== COPY END ==="
Write-Host ""
Write-Host "Allowed actions:"
Write-Host "  git status --short --branch"
Write-Host "  git log --oneline -5"
Write-Host "  gh --version"
Write-Host "  gh issue list --state open"
Write-Host "  gh pr list --state open"
Write-Host "  selective commit/merge only after explicit approval"
Write-Host ""
Write-Host "Blocked actions:"
Write-Host "  no Codex auto-launch"
Write-Host "  no extra windows"
Write-Host "  no startup tasks"
Write-Host "  no scheduled tasks"
Write-Host "  no dashboard edits"
Write-Host "  no broker, OANDA, API keys, webhooks, real orders, or live trading"
Write-Host ""
