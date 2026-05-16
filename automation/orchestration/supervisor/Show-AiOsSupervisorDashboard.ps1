Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$rulesPath = Join-Path $scriptRoot "aios_supervision_rules.example.json"
$border = "=" * 100

function Read-JsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file was not found: $Path"
    }

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Write-Section {
    param(
        [Parameter(Mandatory = $true)][string]$Title,
        [string]$Color = "Cyan"
    )

    Write-Host ""
    Write-Host "== $Title ==" -ForegroundColor $Color
}

function Invoke-Capture {
    param([Parameter(Mandatory = $true)][scriptblock]$Command)

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
        return [pscustomobject]@{
            Available = $false
            ExitCode = 127
            Output = @("gh CLI not found")
        }
    }

    $result = Invoke-Capture -Command { gh @Arguments }
    [pscustomobject]@{
        Available = ($result.ExitCode -eq 0)
        ExitCode = $result.ExitCode
        Output = @($result.Output)
    }
}

function Test-BlockedPath {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object[]]$Patterns
    )

    $normalized = $Path -replace "\\", "/"
    foreach ($pattern in $Patterns) {
        $patternText = [string]$pattern
        if ($normalized -ieq $patternText -or $normalized -like "*$patternText*") {
            return $true
        }
    }
    return $false
}

function Write-List {
    param(
        [Parameter(Mandatory = $true)][object[]]$Lines,
        [string]$Color = "Gray",
        [string]$EmptyText = "None visible."
    )

    if ($Lines.Count -eq 0) {
        Write-Host $EmptyText -ForegroundColor Gray
        return
    }

    foreach ($line in $Lines) {
        Write-Host "  $line" -ForegroundColor $Color
    }
}

$rules = Read-JsonFile -Path $rulesPath
$repoRoot = $rules.repo_root

if (-not (Test-Path -LiteralPath $repoRoot -PathType Container)) {
    throw "AI_OS repo path not found: $repoRoot"
}

Set-Location -LiteralPath $repoRoot
$Host.UI.RawUI.WindowTitle = "AI_OS ACTIVE SUPERVISION"

Write-Host $border -ForegroundColor Cyan
Write-Host "AI_OS ACTIVE SUPERVISION + ROUTING ENGINE" -ForegroundColor Cyan
Write-Host "Read-only operator routing. No commits, pushes, merges, workers, or repo mutation." -ForegroundColor Gray
Write-Host $border -ForegroundColor Cyan

$branch = (git branch --show-current)
$statusLines = @(git status --short)
$latestCommit = (git log --oneline -1)
$repoDirty = $statusLines.Count -gt 0
$untrackedFiles = @($statusLines | Where-Object { $_ -match '^\?\?' })
$changedFiles = @(
    $statusLines |
        ForEach-Object { if ($_.Length -gt 3) { $_.Substring(3).Trim() } } |
        Where-Object { $_ }
)
$blockedFiles = @($changedFiles | Where-Object { Test-BlockedPath -Path $_ -Patterns @($rules.blocked_path_patterns) })
$jsonFiles = @($changedFiles | Where-Object { [System.IO.Path]::GetExtension($_) -ieq ".json" })
$ps1Files = @($changedFiles | Where-Object { [System.IO.Path]::GetExtension($_) -ieq ".ps1" })
$validationNeeded = $repoDirty -or $jsonFiles.Count -gt 0 -or $ps1Files.Count -gt 0

$ghAuth = Invoke-GhReadOnly -Arguments @("auth", "status")
$ghIssues = Invoke-GhReadOnly -Arguments @("issue", "list", "--state", "open", "--limit", "20")
$ghPrs = Invoke-GhReadOnly -Arguments @("pr", "list", "--state", "open", "--limit", "20")
$ghBranchPr = Invoke-GhReadOnly -Arguments @("pr", "list", "--head", $branch, "--state", "open", "--limit", "5")
$ghAvailable = $ghAuth.Available -and $ghIssues.Available -and $ghPrs.Available -and $ghBranchPr.Available
$openIssueCount = if ($ghIssues.Available) { @($ghIssues.Output | Where-Object { "$_".Trim() }).Count } else { 0 }
$openPrCount = if ($ghPrs.Available) { @($ghPrs.Output | Where-Object { "$_".Trim() }).Count } else { 0 }
$branchPrCount = if ($ghBranchPr.Available) { @($ghBranchPr.Output | Where-Object { "$_".Trim() }).Count } else { 0 }

$risk = "SAFE"
$riskColor = "Green"
$riskReasons = New-Object System.Collections.Generic.List[string]

if ($blockedFiles.Count -gt 0) {
    $risk = "BLOCKED"
    $riskColor = "Red"
    $riskReasons.Add("Blocked or protected path changed.")
} elseif ($validationNeeded) {
    $risk = "WARNING"
    $riskColor = "Yellow"
    $riskReasons.Add("Validation is needed before commit packaging.")
} elseif (-not $ghAvailable) {
    $risk = "WATCH"
    $riskColor = "Yellow"
    $riskReasons.Add("GitHub checks are unavailable. Local-only mode is active.")
}

if ($untrackedFiles.Count -gt 0 -and $risk -eq "SAFE") {
    $risk = "WATCH"
    $riskColor = "Yellow"
    $riskReasons.Add("Untracked files need review.")
}

if ($openPrCount -gt 0 -and $risk -eq "SAFE") {
    $risk = "WATCH"
    $riskColor = "Yellow"
    $riskReasons.Add("Open PRs are visible and may need operator review.")
}

if ($riskReasons.Count -eq 0) {
    $riskReasons.Add("No blocking local condition is visible.")
}

$recommendedLane = "COMMAND DECK"
$laneColor = "Magenta"
$nextSafeAction = "Use Ai_Os COMMAND DECK to choose the next approved phase or PR action."

if ($risk -eq "BLOCKED") {
    $recommendedLane = "COMMAND DECK"
    $laneColor = "Magenta"
    $nextSafeAction = "Use Ai_Os COMMAND DECK and stop for operator review before any commit, push, merge, or edit."
} elseif ($validationNeeded) {
    $recommendedLane = "VALIDATION DECK"
    $laneColor = "Cyan"
    $nextSafeAction = "Use Ai_Os VALIDATION DECK and run git diff --check plus file-specific parse checks."
} elseif (-not $ghAvailable -or $openIssueCount -gt 0 -or $openPrCount -gt 0 -or $branchPrCount -gt 0) {
    $recommendedLane = "COMMAND DECK"
    $laneColor = "Magenta"
    $nextSafeAction = "Use Ai_Os COMMAND DECK to review GitHub issue, PR, approval, or merge state."
} else {
    $recommendedLane = "BUILD ENGINE"
    $laneColor = "Green"
    $nextSafeAction = "Use Ai_Os BUILD ENGINE only after the next APPLY task is explicitly approved."
}

Write-Section -Title "Risk Level" -Color $riskColor
Write-Host "Risk: $risk" -ForegroundColor $riskColor
Write-Host "Reasons:" -ForegroundColor Gray
Write-List -Lines @($riskReasons) -Color Gray

Write-Section -Title "Recommended Lane" -Color $laneColor
Write-Host $recommendedLane -ForegroundColor $laneColor
Write-Host "Next safe action: $nextSafeAction" -ForegroundColor Yellow

Write-Section -Title "Repo State"
Write-Host "Repo path: $repoRoot" -ForegroundColor Gray
Write-Host "Current branch: $branch" -ForegroundColor Cyan
Write-Host "Repo state: $(if ($repoDirty) { 'DIRTY' } else { 'CLEAN' })" -ForegroundColor $(if ($repoDirty) { "Yellow" } else { "Green" })
Write-Host "Changed files: $($changedFiles.Count)" -ForegroundColor Gray
Write-Host "Untracked files: $($untrackedFiles.Count)" -ForegroundColor Gray
Write-Host "Latest commit: $latestCommit" -ForegroundColor Gray
if ($statusLines.Count -eq 0) {
    Write-Host "No changed or untracked files." -ForegroundColor Gray
} else {
    Write-List -Lines @($statusLines) -Color Gray
}

Write-Section -Title "GitHub State"
if ($ghAvailable) {
    Write-Host "GitHub CLI state: AVAILABLE" -ForegroundColor Green
    Write-Host "Open issues visible: $openIssueCount" -ForegroundColor Gray
    Write-Host "Open PRs visible: $openPrCount" -ForegroundColor Gray
    Write-Host "Current branch open PRs: $branchPrCount" -ForegroundColor Gray
} else {
    Write-Host "GitHub CLI state: LOCAL-ONLY FALLBACK" -ForegroundColor Yellow
    foreach ($check in @($ghAuth, $ghIssues, $ghPrs, $ghBranchPr)) {
        if (-not $check.Available -and $check.Output.Count -gt 0) {
            $reason = ($check.Output | Select-Object -First 1)
            Write-Host "  $reason" -ForegroundColor Gray
        }
    }
}

Write-Section -Title "Validation Routing"
Write-Host "git diff --check needed: $(if ($repoDirty) { 'YES' } else { 'NO' })" -ForegroundColor $(if ($repoDirty) { "Yellow" } else { "Green" })
Write-Host "JSON validation needed: $(if ($jsonFiles.Count -gt 0) { 'YES' } else { 'NO' })" -ForegroundColor $(if ($jsonFiles.Count -gt 0) { "Yellow" } else { "Green" })
Write-Host "PowerShell parse needed: $(if ($ps1Files.Count -gt 0) { 'YES' } else { 'NO' })" -ForegroundColor $(if ($ps1Files.Count -gt 0) { "Yellow" } else { "Green" })
Write-Host "Repo clean check needed: YES" -ForegroundColor Yellow

Write-Section -Title "Stale And Approval Routing"
Write-Host "Stale branch: review branch age from Ai_Os COMMAND DECK before merge decisions." -ForegroundColor Gray
Write-Host "Issue without PR: route to Ai_Os COMMAND DECK if issue work is complete but no PR exists." -ForegroundColor Gray
Write-Host "PR without merge: route to Ai_Os COMMAND DECK for operator approval." -ForegroundColor Gray
Write-Host "Approval-needed state: route to Ai_Os COMMAND DECK." -ForegroundColor Gray
Write-Host "Validation-needed state: route to Ai_Os VALIDATION DECK." -ForegroundColor Gray

Write-Section -Title "Blocked Actions" -Color Red
foreach ($action in @($rules.blocked_actions)) {
    Write-Host "  no $action" -ForegroundColor Red
}

if ($blockedFiles.Count -gt 0) {
    Write-Section -Title "Blocked Files Visible" -Color Red
    Write-List -Lines @($blockedFiles) -Color Red
}

Write-Section -Title "Exact Next Safe Action" -Color Yellow
Write-Host $nextSafeAction -ForegroundColor Yellow
