param(
    [string]$ExpectedBranch = "main",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-GitText {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    return [pscustomobject]@{
        Output = @($output | ForEach-Object { [string]$_ })
        ExitCode = $exitCode
    }
}

function Remove-GitWarnings {
    param([string[]]$Lines)

    return @($Lines | Where-Object { $_ -notmatch "^warning:" })
}

function Get-GitWarnings {
    param([string[]]$Lines)

    return @($Lines | Where-Object { $_ -match "^warning:" })
}

function Get-FirstCleanLine {
    param([string[]]$Lines)

    $cleanLines = @(Remove-GitWarnings -Lines $Lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($cleanLines.Count -eq 0) {
        return "UNKNOWN"
    }

    return $cleanLines[0]
}

function Get-ChangedPathFromStatusLine {
    param([Parameter(Mandatory = $true)][string]$Line)

    if ($Line.Length -lt 4) {
        return $Line
    }

    return $Line.Substring(3).Replace("\", "/")
}

$branchResult = Invoke-GitText -Arguments @("branch", "--show-current")
$headHashResult = Invoke-GitText -Arguments @("rev-parse", "--short", "HEAD")
$headFullHashResult = Invoke-GitText -Arguments @("rev-parse", "HEAD")
$messageResult = Invoke-GitText -Arguments @("log", "-1", "--pretty=%s")
$statusResult = Invoke-GitText -Arguments @("status", "--short")
$originMainResult = Invoke-GitText -Arguments @("rev-parse", "--short", "origin/main")
$originMainFullResult = Invoke-GitText -Arguments @("rev-parse", "origin/main")

$gitWarnings = @(
    @(
        Get-GitWarnings -Lines $branchResult.Output
        Get-GitWarnings -Lines $headHashResult.Output
        Get-GitWarnings -Lines $messageResult.Output
        Get-GitWarnings -Lines $statusResult.Output
        Get-GitWarnings -Lines $originMainResult.Output
    ) | Sort-Object -Unique
)

$currentBranch = Get-FirstCleanLine -Lines $branchResult.Output
$latestCommitHash = Get-FirstCleanLine -Lines $headHashResult.Output
$latestCommitFullHash = Get-FirstCleanLine -Lines $headFullHashResult.Output
$latestCommitMessage = Get-FirstCleanLine -Lines $messageResult.Output
$statusLines = @(Remove-GitWarnings -Lines $statusResult.Output | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$dirtyFiles = @($statusLines | Where-Object { -not $_.StartsWith("?? ") } | ForEach-Object { Get-ChangedPathFromStatusLine -Line $_ })
$untrackedFiles = @($statusLines | Where-Object { $_.StartsWith("?? ") } | ForEach-Object { Get-ChangedPathFromStatusLine -Line $_ })
$gitState = if ($statusLines.Count -eq 0) { "clean" } else { "dirty" }

$originMainAvailable = ($originMainResult.ExitCode -eq 0)
$originMainHash = if ($originMainAvailable) { Get-FirstCleanLine -Lines $originMainResult.Output } else { "UNKNOWN" }
$originMainFullHash = if ($originMainFullResult.ExitCode -eq 0) { Get-FirstCleanLine -Lines $originMainFullResult.Output } else { "UNKNOWN" }
$headMatchesOriginMain = ($originMainAvailable -and $latestCommitFullHash -eq $originMainFullHash)
$originMainSyncStatus = if (-not $originMainAvailable) {
    "UNKNOWN"
} elseif ($headMatchesOriginMain) {
    "MATCH"
} else {
    "DIFFERENT"
}

$risks = @()

if ($currentBranch -ne $ExpectedBranch) {
    $risks += [pscustomobject]@{
        risk = "Current branch is '$currentBranch', expected '$ExpectedBranch' for post-push main verification."
        severity = "BLOCKED"
    }
}

if ($gitState -ne "clean") {
    $risks += [pscustomobject]@{
        risk = "Worktree is dirty after supposed push."
        severity = "REVIEW"
    }
}

if (-not $originMainAvailable) {
    $risks += [pscustomobject]@{
        risk = "Local origin/main ref is unavailable; push success cannot be inferred locally."
        severity = "REVIEW"
    }
} elseif (-not $headMatchesOriginMain) {
    $risks += [pscustomobject]@{
        risk = "HEAD does not match local origin/main. Push to main is not verified by local refs."
        severity = "REVIEW"
    }
}

$githubStatusCheckWarning = "UNKNOWN: GitHub checks were not queried by this DRY_RUN scaffold."
$risks += [pscustomobject]@{
    risk = "GitHub status checks may still be running or unavailable."
    severity = "REVIEW"
}

$remotePushLikelySucceeded = "UNKNOWN"
if ($currentBranch -eq $ExpectedBranch -and $headMatchesOriginMain) {
    $remotePushLikelySucceeded = "YES"
} elseif ($currentBranch -ne $ExpectedBranch) {
    $remotePushLikelySucceeded = "NO"
}

$resultStatus = "PASS"
if (@($risks | Where-Object { $_.severity -eq "BLOCKED" }).Count -gt 0) {
    $resultStatus = "BLOCKED"
} elseif ($risks.Count -gt 0 -or $gitState -ne "clean") {
    $resultStatus = "REVIEW"
}

$nextSafeAction = "Post-push state looks locally safe. Confirm GitHub checks before closing the task."
if ($resultStatus -eq "REVIEW") {
    $nextSafeAction = "Review risks, confirm GitHub checks, and verify origin/main before declaring push complete."
} elseif ($resultStatus -eq "BLOCKED") {
    $nextSafeAction = "Stop. Switch to MAIN CONTROL on main or resolve branch mismatch before post-push verification."
}

$result = [pscustomobject]@{
    system = "AI_OS"
    task = "Verify AI_OS post-push state"
    mode = "DRY_RUN"
    result = $resultStatus
    expected_branch = $ExpectedBranch
    current_branch = $currentBranch
    latest_commit_hash = $latestCommitHash
    latest_commit_message = $latestCommitMessage
    origin_main = [pscustomobject]@{
        available = $originMainAvailable
        hash = $originMainHash
        head_matches_origin_main = $headMatchesOriginMain
        sync_status = $originMainSyncStatus
    }
    git_status = [pscustomobject]@{
        state = $gitState
        dirty_count = $dirtyFiles.Count
        untracked_count = $untrackedFiles.Count
        dirty_files = $dirtyFiles
        untracked_files = $untrackedFiles
    }
    remote_push_likely_succeeded = $remotePushLikelySucceeded
    github_status_check_warning = $githubStatusCheckWarning
    risks = $risks
    git_warnings = $gitWarnings
    safety = [pscustomobject]@{
        writes_performed = 0
        commits_performed = 0
        pushes_performed = 0
        dispatcher_edits = "NO"
        runtime_integration = "NO"
        dashboard_edits = "NO"
    }
    validator_friendly = $true
    next_safe_action = $nextSafeAction
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS Post-Push Verification"
Write-Host "Mode: DRY_RUN"
Write-Host "Result: $resultStatus"
Write-Host "Expected branch: $ExpectedBranch"
Write-Host "Current branch: $currentBranch"
Write-Host "Latest commit: $latestCommitHash"
Write-Host "Latest message: $latestCommitMessage"
Write-Host "origin/main sync: $originMainSyncStatus"
Write-Host "Git status: $gitState"
Write-Host "Remote push likely succeeded: $remotePushLikelySucceeded"
Write-Host "GitHub status check warning: $githubStatusCheckWarning"
Write-Host ""

Write-Host "Dirty files:"
if ($dirtyFiles.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($file in $dirtyFiles) {
        Write-Host "  - $file"
    }
}
Write-Host ""

Write-Host "Untracked files:"
if ($untrackedFiles.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($file in $untrackedFiles) {
        Write-Host "  - $file"
    }
}
Write-Host ""

Write-Host "Risks:"
if ($risks.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($risk in $risks) {
        Write-Host "  - [$($risk.severity)] $($risk.risk)"
    }
}
Write-Host ""

Write-Host "Git warnings:"
if ($gitWarnings.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($warning in $gitWarnings) {
        Write-Host "  - $warning"
    }
}
Write-Host ""

Write-Host "Validator note: no files were changed by this DRY_RUN check."
Write-Host "Next safe action: $nextSafeAction"
