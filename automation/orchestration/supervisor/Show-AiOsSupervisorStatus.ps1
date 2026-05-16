Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$statePath = Join-Path $scriptRoot "aios_supervisor_state.example.json"
$border = "#" * 100

function Read-JsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file was not found: $Path"
    }

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Write-Section {
    param([Parameter(Mandatory = $true)][string]$Title)

    Write-Host ""
    Write-Host "== $Title ==" -ForegroundColor Cyan
}

function Invoke-Capture {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $output = & $Command 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }

    [pscustomobject]@{
        Output = @($output)
        ExitCode = $exitCode
    }
}

function Invoke-GhReadOnly {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Write-Host "gh CLI not found. Supervisor continues local-only." -ForegroundColor Yellow
        return $false
    }

    $result = Invoke-Capture -Command { gh @Arguments }
    if ($result.ExitCode -ne 0) {
        Write-Host "GitHub check unavailable. Supervisor continues local-only." -ForegroundColor Yellow
        if ($result.Output.Count -gt 0) {
            $reason = ($result.Output | Out-String).Trim().Split([Environment]::NewLine)[0]
            Write-Host "Reason: $reason" -ForegroundColor Gray
        }
        return $false
    }

    if ($result.Output.Count -eq 0) {
        Write-Host "None found." -ForegroundColor Gray
    } else {
        $result.Output
    }

    return $true
}

$state = Read-JsonFile -Path $statePath
$repoRoot = $state.repo_root

if (-not (Test-Path -LiteralPath $repoRoot -PathType Container)) {
    throw "AI_OS repo path not found: $repoRoot"
}

Set-Location -LiteralPath $repoRoot
$Host.UI.RawUI.WindowTitle = "AI_OS SUPERVISOR"

Write-Host $border -ForegroundColor Cyan
Write-Host "AI_OS SUPERVISOR CORE" -ForegroundColor Cyan
Write-Host "Read-only workflow watcher. It tells the operator what is happening." -ForegroundColor Gray
Write-Host $border -ForegroundColor Cyan

Write-Section -Title "Repo State"
$branch = (git branch --show-current)
$statusLines = @(git status --short)
$latestCommit = (git log --oneline -1)
$changedFiles = @($statusLines | Where-Object { $_ -match '^\s*M|^\s*A|^\s*D|^\s*R|^\s*C|^MM|^AM|^AD' })
$untrackedFiles = @($statusLines | Where-Object { $_ -match '^\?\?' })
$repoDirty = $statusLines.Count -gt 0

Write-Host "Current branch: $branch" -ForegroundColor Cyan
Write-Host "Repo state: $(if ($repoDirty) { 'DIRTY' } else { 'CLEAN' })" -ForegroundColor $(if ($repoDirty) { 'Yellow' } else { 'Green' })
Write-Host "Changed files: $($changedFiles.Count)" -ForegroundColor Gray
Write-Host "Untracked files: $($untrackedFiles.Count)" -ForegroundColor Gray
Write-Host "Latest commit: $latestCommit" -ForegroundColor Gray

if ($statusLines.Count -gt 0) {
    Write-Host "Files:" -ForegroundColor Yellow
    $statusLines | ForEach-Object { Write-Host "  $_" }
}

Write-Section -Title "GitHub State"
$ghOk = $true
Write-Host "Auth status:" -ForegroundColor Gray
$ghOk = (Invoke-GhReadOnly -Arguments @("auth", "status")) -and $ghOk
Write-Host "Open issues:" -ForegroundColor Gray
$ghOk = (Invoke-GhReadOnly -Arguments @("issue", "list", "--state", "open", "--limit", "10")) -and $ghOk
Write-Host "Open PRs:" -ForegroundColor Gray
$ghOk = (Invoke-GhReadOnly -Arguments @("pr", "list", "--state", "open", "--limit", "10")) -and $ghOk
Write-Host "Current branch PR:" -ForegroundColor Gray
$ghOk = (Invoke-GhReadOnly -Arguments @("pr", "list", "--head", $branch, "--state", "open", "--limit", "5")) -and $ghOk

Write-Section -Title "Worker Lane State"
foreach ($lane in @($state.worker_lanes)) {
    $color = switch ($lane.lane_id) {
        "COMMAND_DECK" { "Magenta" }
        "BUILD_ENGINE" { "Green" }
        "VALIDATION_DECK" { "Cyan" }
        default { "Gray" }
    }
    Write-Host "$($lane.lane_name): $($lane.purpose)" -ForegroundColor $color
    Write-Host "  Use when: $($lane.recommended_when)" -ForegroundColor Gray
}

Write-Section -Title "Queue State"
foreach ($path in @($state.watched_queue_files)) {
    $exists = Test-Path -LiteralPath $path -PathType Leaf
    Write-Host "$path : $(if ($exists) { 'visible' } else { 'missing' })" -ForegroundColor $(if ($exists) { 'Green' } else { 'Yellow' })
}
Write-Host "Approval-needed state: inspect approval inbox files." -ForegroundColor Gray
Write-Host "Validation-needed state: inspect validator flags in queue files." -ForegroundColor Gray
Write-Host "Blocked state: inspect blocked packet examples before any APPLY." -ForegroundColor Red

Write-Section -Title "Validator State"
foreach ($path in @($state.watched_validator_files)) {
    $exists = Test-Path -LiteralPath $path -PathType Leaf
    Write-Host "$path : $(if ($exists) { 'visible' } else { 'missing' })" -ForegroundColor $(if ($exists) { 'Green' } else { 'Yellow' })
}
Write-Host "Needed: git diff --check" -ForegroundColor Yellow
Write-Host "Needed: JSON parse checks for changed JSON files" -ForegroundColor Yellow
Write-Host "Needed: PowerShell parse checks for changed PS1 files" -ForegroundColor Yellow
Write-Host "Needed: repo clean check before commit approval" -ForegroundColor Yellow

Write-Section -Title "Stale State"
if ($repoDirty) {
    Write-Host "Dirty repo after APPLY or validation: review before commit." -ForegroundColor Yellow
}
if ($untrackedFiles.Count -gt 0) {
    Write-Host "Uncommitted files are present after validation." -ForegroundColor Yellow
}
if (-not $ghOk) {
    Write-Host "GitHub status is local-only because gh checks failed or are unavailable." -ForegroundColor Yellow
}
Write-Host "Branch age, issue-without-PR, and PR-without-merge need GitHub/date review before automation." -ForegroundColor Gray

Write-Section -Title "Blocked Actions"
foreach ($action in @($state.blocked_actions)) {
    Write-Host "  no $action" -ForegroundColor Red
}

Write-Section -Title "Next Safe Action"
if ($repoDirty) {
    Write-Host "Use Ai_Os VALIDATION DECK and run: git diff --check" -ForegroundColor Yellow
    Write-Host "Then review changed files before asking for commit approval." -ForegroundColor Gray
} elseif (-not $ghOk) {
    Write-Host "Continue local-only and retry GitHub status from Ai_Os COMMAND DECK later." -ForegroundColor Yellow
} else {
    Write-Host "Use Ai_Os COMMAND DECK to decide the next approved phase or PR action." -ForegroundColor Green
}
