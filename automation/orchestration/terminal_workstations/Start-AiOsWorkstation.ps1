Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$roleName = "AI_OS WORKSTATION"
$border = "#" * 100
$commandIcon = [char]::ConvertFromUtf32(0x1F7E3)
$buildIcon = [char]::ConvertFromUtf32(0x1F7E2)
$validationIcon = [char]::ConvertFromUtf32(0x1F535)

function Write-Section {
    param([Parameter(Mandatory = $true)][string]$Title)

    Write-Host ""
    Write-Host "== $Title ==" -ForegroundColor Cyan
}

function Invoke-ReadOnlyCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,

        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    Write-Section -Title $Label
    try {
        & $Command
    } catch {
        Write-Host "Unavailable: $($_.Exception.Message)"
    }
}

function Invoke-GhReadOnly {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Write-Host "gh CLI not found on PATH."
        return
    }

    $output = & gh @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "GitHub CLI request unavailable in this environment."
        if ($output) {
            Write-Host "Reason: $($output | Select-Object -First 1)"
        }
        return
    }

    if ($output) {
        $output
    } else {
        Write-Host "None found."
    }
}

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host $border -ForegroundColor Cyan
Write-Host ""
Write-Host "AI_OS TERMINAL WORKSTATION MASTER" -ForegroundColor Cyan
Write-Host "LOOK FOR THIS COLOR TO IDENTIFY THIS WINDOW." -ForegroundColor Yellow
Write-Host ""
Write-Host "Repo: $repoPath" -ForegroundColor Cyan
Write-Host "ROLE: Master status launcher for Command Deck, Build Engine, and Validation Deck" -ForegroundColor Cyan
Write-Host "MODE: Read-only startup summary" -ForegroundColor Gray
Write-Host "STATUS: No Codex auto-launch, no extra windows, no scheduled/startup tasks" -ForegroundColor Gray
Write-Host ""
Write-Host "No Codex auto-launch. No extra windows. No scheduled/startup tasks." -ForegroundColor Gray
Write-Host "No WScript.Shell, SendKeys, ALT+SPACE automation, Num Lock changes, or Windows Terminal settings edits." -ForegroundColor Gray
Write-Host "No broker, OANDA, API keys, webhooks, real orders, or live trading." -ForegroundColor Red
Write-Host ""
Write-Host $border -ForegroundColor Cyan
Write-Host $border -ForegroundColor Cyan
Write-Host $border -ForegroundColor Yellow
Write-Host "=== COPY START ===" -ForegroundColor Yellow
Write-Host "Paste terminal output between COPY START and COPY END when sending to ChatGPT." -ForegroundColor White
Write-Host "=== COPY END ===" -ForegroundColor Yellow
Write-Host $border -ForegroundColor Yellow

Invoke-ReadOnlyCommand -Label "Current Git Branch" -Command {
    git branch --show-current
}

Invoke-ReadOnlyCommand -Label "Git Status" -Command {
    git status --short --branch
}

Invoke-ReadOnlyCommand -Label "Latest 5 Commits" -Command {
    git log --oneline -5
}

Invoke-ReadOnlyCommand -Label "Open GitHub Issues" -Command {
    Invoke-GhReadOnly -Arguments @("issue", "list", "--state", "open", "--limit", "10")
}

Invoke-ReadOnlyCommand -Label "Open GitHub PRs" -Command {
    Invoke-GhReadOnly -Arguments @("pr", "list", "--state", "open", "--limit", "10")
}

Write-Section -Title "Operator Lanes"
Write-Host "$commandIcon Ai_Os COMMAND DECK" -ForegroundColor Magenta
Write-Host "  Use for Git, GitHub CLI, issues, PRs, commits, merges, and operator decisions."
Write-Host "$buildIcon Ai_Os BUILD ENGINE" -ForegroundColor Green
Write-Host "  Use for Codex work. Codex launch remains manual."
Write-Host "$validationIcon Ai_Os VALIDATION DECK" -ForegroundColor Cyan
Write-Host "  Use for PowerShell status checks, validators, queue checks, and repo checks."

Write-Section -Title "Exact Next Safe Action"
Write-Host "Run read-only validation before any commit or push:" -ForegroundColor Gray
Write-Host "  git diff --check"
Write-Host "  git status --short --branch"
Write-Host ""
