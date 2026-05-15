Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$roleName = "AI_OS BUILD ENGINE"

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host "========================================"
Write-Host $roleName
Write-Host "Role: Codex work lane. Manual Codex launch only."
Write-Host "Repo: $repoPath"
Write-Host "========================================"
Write-Host "=== COPY START ==="
Write-Host "Paste terminal output between COPY START and COPY END when sending to ChatGPT."
Write-Host "=== COPY END ==="
Write-Host ""
Write-Host "Allowed actions:"
Write-Host "  review assigned prompt"
Write-Host "  inspect files"
Write-Host "  run approved APPLY work"
Write-Host "  run scoped validators"
Write-Host "  launch Codex manually only when the operator chooses"
Write-Host ""
Write-Host "Blocked actions:"
Write-Host "  no Codex auto-launch"
Write-Host "  no extra windows"
Write-Host "  no startup tasks"
Write-Host "  no scheduled tasks"
Write-Host "  no dashboard edits unless explicitly scoped"
Write-Host "  no broker, OANDA, API keys, webhooks, real orders, or live trading"
Write-Host "  no commit or push without explicit approval"
Write-Host ""
