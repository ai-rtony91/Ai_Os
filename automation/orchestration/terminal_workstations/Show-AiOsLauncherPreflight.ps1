Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$border = "#" * 100

function Write-Section {
    param([Parameter(Mandatory = $true)][string]$Title)

    Write-Host ""
    Write-Host "== $Title ==" -ForegroundColor Cyan
}

function Invoke-ReadOnlyCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$UnavailableMessage,

        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    try {
        & $Command
    } catch {
        Write-Host "$UnavailableMessage $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

function Invoke-GhReadOnly {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Write-Host "gh CLI not found. Continuing local-only." -ForegroundColor Yellow
        return
    }

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & gh @Arguments 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    if ($exitCode -ne 0) {
        Write-Host "GitHub CLI check unavailable. Continuing local-only." -ForegroundColor Yellow
        if ($output) {
            $reason = ($output | Out-String).Trim().Split([Environment]::NewLine)[0]
            Write-Host "Reason: $reason" -ForegroundColor Gray
        }
        return
    }

    if ($output) {
        $output
    } else {
        Write-Host "None found." -ForegroundColor Gray
    }
}

Write-Host $border -ForegroundColor Cyan
Write-Host "AI_OS LAUNCHER PREFLIGHT" -ForegroundColor Cyan
Write-Host "Read-only checks before opening the AI_OS decks." -ForegroundColor Gray
Write-Host $border -ForegroundColor Cyan

Write-Section -Title "Repo Path"
if (Test-Path -LiteralPath $repoPath -PathType Container) {
    Write-Host "Repo path exists: $repoPath" -ForegroundColor Cyan
    Set-Location -LiteralPath $repoPath
} else {
    Write-Host "Repo path missing: $repoPath" -ForegroundColor Red
    exit 1
}

Write-Section -Title "Current Branch"
Invoke-ReadOnlyCommand -UnavailableMessage "Branch check unavailable:" -Command {
    git branch --show-current
}

Write-Section -Title "Git Status"
Invoke-ReadOnlyCommand -UnavailableMessage "Git status unavailable:" -Command {
    git status --short --branch
}

Write-Section -Title "Latest Commit"
Invoke-ReadOnlyCommand -UnavailableMessage "Latest commit unavailable:" -Command {
    git log --oneline -1
}

Write-Section -Title "GitHub CLI"
if (Get-Command gh -ErrorAction SilentlyContinue) {
    gh --version | Select-Object -First 1
    Invoke-GhReadOnly -Arguments @("auth", "status")
} else {
    Write-Host "gh CLI not found. GitHub checks will run local-only." -ForegroundColor Yellow
}

Write-Section -Title "Open GitHub Issues"
Invoke-GhReadOnly -Arguments @("issue", "list", "--state", "open", "--limit", "100", "--json", "number", "--jq", "length")

Write-Section -Title "Open GitHub PRs"
Invoke-GhReadOnly -Arguments @("pr", "list", "--state", "open", "--limit", "100", "--json", "number", "--jq", "length")

Write-Section -Title "Next Safe Action"
Write-Host "Run the one-command launcher in preview first, then launch decks only when the preflight looks safe." -ForegroundColor Gray
