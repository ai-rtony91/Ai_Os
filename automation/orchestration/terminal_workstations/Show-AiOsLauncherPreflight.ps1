Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoPath = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot
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

$titleIcon = [char]::ConvertFromUtf32(0x1F50D)  # Magnifying glass - preflight inspection

Write-Host $border -ForegroundColor Cyan
Write-Host ""
Write-Host "  $titleIcon  AI_OS LAUNCHER PREFLIGHT" -ForegroundColor Cyan
Write-Host "  AIOS BASE : #05070b  TEXT #e5f6ff  ACTION #38bdf8  WARNING #ffd166" -ForegroundColor DarkCyan
Write-Host "  OCC LANE  : ALL LANES  |  Read-only checks before opening AI_OS decks" -ForegroundColor DarkCyan
Write-Host "  MODE      : [ DRY_RUN ]  Read-only — no mutation, no launch" -ForegroundColor DarkCyan
Write-Host ""
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
Write-Host "  [ STEP 1 ]  Review preflight output above." -ForegroundColor Gray
Write-Host "  [ STEP 2 ]  Open Operator Menu or launch the appropriate deck." -ForegroundColor Gray
Write-Host "  [ STEP 3 ]  Codex launch remains manual — Build Engine only." -ForegroundColor Gray
