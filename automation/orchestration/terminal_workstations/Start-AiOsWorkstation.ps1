Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$roleName = "AI_OS WORKSTATION"

function Write-Section {
    param([Parameter(Mandatory = $true)][string]$Title)

    Write-Host ""
    Write-Host "== $Title =="
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

Write-Host "========================================"
Write-Host "AI_OS TERMINAL WORKSTATION"
Write-Host "Repo: $repoPath"
Write-Host "No Codex auto-launch. No extra windows. No scheduled/startup tasks."
Write-Host "No WScript.Shell, SendKeys, ALT+SPACE automation, Num Lock changes, or Windows Terminal settings edits."
Write-Host "No broker, OANDA, API keys, webhooks, real orders, or live trading."
Write-Host "========================================"
Write-Host "=== COPY START ==="
Write-Host "Paste terminal output between COPY START and COPY END when sending to ChatGPT."
Write-Host "=== COPY END ==="

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
Write-Host "AI_OS COMMAND DECK"
Write-Host "  Use for Git, GitHub CLI, issues, PRs, commits, merges, and operator decisions."
Write-Host "AI_OS BUILD ENGINE"
Write-Host "  Use for Codex work. Codex launch remains manual."
Write-Host "AI_OS VALIDATION DECK"
Write-Host "  Use for PowerShell status checks, validators, queue checks, and repo checks."

Write-Section -Title "Exact Next Safe Action"
Write-Host "Run read-only validation before any commit or push:"
Write-Host "  git diff --check"
Write-Host "  git status --short --branch"
Write-Host ""
