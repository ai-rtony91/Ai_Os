Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
$roleName = "AI_OS WORKSTATION"
$border = "#" * 100
$commandIcon = [char]::ConvertFromUtf32(0x1F451)
$buildIcon = [char]::ConvertFromUtf32(0x2699)
$validationIcon = [char]::ConvertFromUtf32(0x1F6E1)

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

if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoPath = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host $border -ForegroundColor Cyan
Write-Host ""
Write-Host "  $commandIcon $buildIcon $validationIcon  AI_OS TERMINAL WORKSTATION MASTER" -ForegroundColor Cyan
Write-Host "  LOOK FOR THIS COLOR TO IDENTIFY THIS WINDOW." -ForegroundColor Cyan
Write-Host ""
Write-Host "  AIOS BASE : #05070b  TEXT #e5f6ff  CYAN #38bdf8  BLUE #00a3ff" -ForegroundColor DarkCyan
Write-Host "  OCC LANE  : ALL LANES  |  Master status launcher for all OCC decks" -ForegroundColor Cyan
Write-Host "  ROLE      : Read-only startup summary — launches Command Deck, Build Engine, Validation Deck" -ForegroundColor DarkCyan
Write-Host "  MODE      : [ DRY_RUN ]  Read-only startup summary" -ForegroundColor DarkCyan
Write-Host "  STATUS    : [ READ-ONLY ]  No Codex auto-launch, no extra windows, no scheduled/startup tasks" -ForegroundColor DarkCyan
Write-Host "  Repo      : $repoPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "  No WScript.Shell, SendKeys, ALT+SPACE automation, Num Lock changes, or Windows Terminal settings edits." -ForegroundColor Gray
Write-Host "  [ BLOCKED ]  broker, OANDA, API keys, webhooks, real orders, or live trading" -ForegroundColor Red
Write-Host ""
Write-Host $border -ForegroundColor Cyan
Write-Host $border -ForegroundColor Cyan
Write-Host $border -ForegroundColor Yellow
Write-Host "  === COPY START ===" -ForegroundColor Yellow
Write-Host "  Paste terminal output between COPY START and COPY END when sending to Claude." -ForegroundColor White
Write-Host "  === COPY END ===" -ForegroundColor Yellow
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
Write-Host "  $commandIcon  [ MAGENTA ]  MAIN CONTROL / COMMAND THRONE" -ForegroundColor Magenta
Write-Host "    MAIN_CONTROL  |  Persistent all-day command-deck window"
Write-Host "  $buildIcon  [ GREEN   ]  BUILD ENGINE / BUILDER FORGE" -ForegroundColor Green
Write-Host "    EAST_OCC  |  Temporary packet-scoped worker lane - Codex launch remains manual"
Write-Host "  $validationIcon  [ CYAN    ]  VALIDATION DECK / EVIDENCE SHIELD" -ForegroundColor Cyan
Write-Host "    VALIDATOR_OCC  |  PowerShell status checks, validators, queue checks, repo checks"

Write-Section -Title "Exact Next Safe Action"
Write-Host "  [ STEP 1 ]  Run read-only validation:" -ForegroundColor Gray
Write-Host "    git diff --check"
Write-Host "    git status --short --branch"
Write-Host "  [ STEP 2 ]  Open relevant deck (Command, Build, or Validation)."
Write-Host "  [ STEP 3 ]  Launch Codex manually from Build Engine only when ready."
Write-Host ""
