[CmdletBinding()]
param(
    [string[]]$WorkerLanePath = @(),
    [switch]$Json
)

$ErrorActionPreference = "Stop"

function Get-AiOsRepoRoot {
    $root = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($root)) {
        throw "Unable to find git repository root."
    }

    return $root.Trim()
}

function Invoke-AiOsGit {
    param([string[]]$Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = @(& git @Arguments 2>$null)
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    return [pscustomobject]@{
        ExitCode = $exitCode
        Lines = @($output)
    }
}

function Add-AiOsRisk {
    param(
        [System.Collections.Generic.List[object]]$Risks,
        [ValidateSet("INFO", "WARN", "BLOCKED")][string]$Level,
        [string]$CheckId,
        [string]$Message,
        [string[]]$Evidence = @(),
        [string]$NextSafeAction = "Review clean-state output before starting new work."
    )

    $Risks.Add([pscustomobject]@{
        level = $Level
        check_id = $CheckId
        message = $Message
        evidence = @($Evidence)
        next_safe_action = $NextSafeAction
    }) | Out-Null
}

function Convert-AiOsStatusLineToPath {
    param([string]$Line)

    if ([string]::IsNullOrWhiteSpace($Line) -or $Line.Length -lt 4 -or $Line -like "##*") {
        return ""
    }

    $path = $Line.Substring(3).Trim()
    if ($path -match " -> ") {
        $path = ($path -split " -> ")[-1].Trim()
    }

    return ($path -replace "\\", "/")
}

function Test-AiOsPathPrefix {
    param(
        [string]$Path,
        [string]$Prefix
    )

    if ([string]::IsNullOrWhiteSpace($Path) -or [string]::IsNullOrWhiteSpace($Prefix)) {
        return $false
    }

    $normalizedPath = ($Path -replace "\\", "/").Trim("/")
    $normalizedPrefix = ($Prefix -replace "\\", "/").Trim("/")
    return ($normalizedPath -eq $normalizedPrefix -or $normalizedPath.StartsWith($normalizedPrefix + "/"))
}

$repoRoot = Get-AiOsRepoRoot
Set-Location -LiteralPath $repoRoot

$generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$risks = [System.Collections.Generic.List[object]]::new()

$branchResult = Invoke-AiOsGit -Arguments @("branch", "--show-current")
$currentBranch = if ($branchResult.Lines.Count -gt 0) { [string]$branchResult.Lines[0] } else { "" }

if ([string]::IsNullOrWhiteSpace($currentBranch)) {
    Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "current_branch" -Message "Current branch could not be read." -NextSafeAction "Confirm the branch before approving new work."
}
else {
    Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "current_branch" -Message "Current branch detected: $currentBranch" -Evidence @($currentBranch) -NextSafeAction "Confirm this is the intended branch."
}

$statusResult = Invoke-AiOsGit -Arguments @("status", "--short", "--branch")
$statusLines = @($statusResult.Lines)
$branchLine = @($statusLines | Where-Object { $_ -like "##*" } | Select-Object -First 1)
$fileStatusLines = @($statusLines | Where-Object { $_ -notlike "##*" -and -not [string]::IsNullOrWhiteSpace($_) })
$changedFiles = @($fileStatusLines | ForEach-Object { Convert-AiOsStatusLineToPath -Line $_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$untrackedFiles = @($fileStatusLines | Where-Object { $_ -like "??*" } | ForEach-Object { Convert-AiOsStatusLineToPath -Line $_ })

if ($statusResult.ExitCode -ne 0) {
    Add-AiOsRisk -Risks $risks -Level "BLOCKED" -CheckId "git_status" -Message "git status failed." -NextSafeAction "Fix git status access before clean-state approval."
}
elseif ($changedFiles.Count -eq 0) {
    Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "git_status" -Message "Working tree is clean." -NextSafeAction "Continue clean-state review."
}
else {
    Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "git_status" -Message "Working tree has changed or untracked files." -Evidence $changedFiles -NextSafeAction "Review or clear changed files before declaring the repo clean."
}

$aheadBehindText = if ($branchLine.Count -gt 0) { [string]$branchLine[0] } else { "" }
$aheadBehindState = "UNKNOWN"
if ($aheadBehindText -match "ahead\s+(\d+)" -and $aheadBehindText -match "behind\s+(\d+)") {
    $aheadBehindState = "DIVERGED"
    Add-AiOsRisk -Risks $risks -Level "BLOCKED" -CheckId "ahead_behind_state" -Message "Branch appears both ahead and behind its upstream." -Evidence @($aheadBehindText) -NextSafeAction "Stop and request operator review before push, pull, rebase, or merge."
}
elseif ($aheadBehindText -match "ahead\s+(\d+)") {
    $aheadBehindState = "AHEAD"
    Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "ahead_behind_state" -Message "Branch appears ahead of upstream." -Evidence @($aheadBehindText) -NextSafeAction "Confirm commits were intentionally created and whether push is approved."
}
elseif ($aheadBehindText -match "behind\s+(\d+)") {
    $aheadBehindState = "BEHIND"
    Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "ahead_behind_state" -Message "Branch appears behind upstream." -Evidence @($aheadBehindText) -NextSafeAction "Do not pull/rebase/merge without explicit operator approval."
}
elseif (-not [string]::IsNullOrWhiteSpace($aheadBehindText)) {
    $aheadBehindState = "SYNCED_OR_NO_UPSTREAM_SIGNAL"
    Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "ahead_behind_state" -Message "No ahead/behind marker was detected in git status." -Evidence @($aheadBehindText) -NextSafeAction "Treat remote sync as likely OK unless other evidence conflicts."
}
else {
    Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "ahead_behind_state" -Message "Ahead/behind state could not be read." -NextSafeAction "Run git status --short --branch manually before declaring clean state."
}

$stagedResult = Invoke-AiOsGit -Arguments @("diff", "--cached", "--name-only")
$stagedFiles = @($stagedResult.Lines | ForEach-Object { $_ -replace "\\", "/" } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
if ($stagedFiles.Count -gt 0) {
    Add-AiOsRisk -Risks $risks -Level "BLOCKED" -CheckId "staged_files" -Message "Staged files exist." -Evidence $stagedFiles -NextSafeAction "Unstage or review exact staged files before declaring clean state."
}
else {
    Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "staged_files" -Message "No staged files detected." -NextSafeAction "Continue clean-state review."
}

if ($untrackedFiles.Count -gt 0) {
    Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "untracked_files" -Message "Untracked files exist." -Evidence $untrackedFiles -NextSafeAction "Review untracked files before declaring clean state."
}
else {
    Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "untracked_files" -Message "No untracked files detected." -NextSafeAction "Continue clean-state review."
}

$commitResult = Invoke-AiOsGit -Arguments @("log", "-1", "--format=%H|%ci|%s")
$recentCommit = if ($commitResult.Lines.Count -gt 0) { [string]$commitResult.Lines[0] } else { "" }
if ($commitResult.ExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($recentCommit)) {
    Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "recent_commit" -Message "Recent commit could not be read." -NextSafeAction "Confirm at least one recent commit exists before post-push clean-state review."
}
else {
    Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "recent_commit" -Message "Recent commit detected." -Evidence @($recentCommit) -NextSafeAction "Confirm this commit is the intended checkpoint."
}

$remoteSyncLikelyOk = ($aheadBehindState -eq "SYNCED_OR_NO_UPSTREAM_SIGNAL" -and $changedFiles.Count -eq 0 -and $stagedFiles.Count -eq 0)
if ($remoteSyncLikelyOk) {
    Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "remote_sync_likely_ok" -Message "Remote sync looks likely OK from local status." -NextSafeAction "No push or pull is approved by this checker."
}
else {
    Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "remote_sync_likely_ok" -Message "Remote sync is not proven clean from local status." -Evidence @($aheadBehindText) -NextSafeAction "Review ahead/behind and dirty state before declaring remote sync OK."
}

$protectedPatterns = @(
    "^README\.md$",
    "^RISK_POLICY\.md$",
    "^SOURCE_LOG\.md$",
    "^ERROR_LOG\.md$",
    "^HALLUCINATION_LOG\.md$",
    "^AAR\.md$",
    "^DAILY_REPORT\.md$",
    "^ARCHITECTURE\.md$",
    "^DEPLOYMENT\.md$",
    "^WHITEPAPER\.md$",
    "^\.codex_backups/",
    "^apps/dashboard/assets/"
)
$protectedChanged = @($changedFiles | Where-Object {
    $path = $_
    @($protectedPatterns | Where-Object { $path -match $_ }).Count -gt 0
})

if ($protectedChanged.Count -gt 0) {
    Add-AiOsRisk -Risks $risks -Level "BLOCKED" -CheckId "protected_files_changed" -Message "Protected files or paths are changed." -Evidence $protectedChanged -NextSafeAction "Stop and request explicit protected-path review."
}
else {
    Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "protected_files_changed" -Message "No protected file changes detected." -NextSafeAction "Continue clean-state review."
}

if ($WorkerLanePath.Count -eq 0) {
    Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "worker_lanes_dirty" -Message "No worker lane paths were supplied, so lane dirtiness could not be checked." -NextSafeAction "Supply -WorkerLanePath for lane-specific clean-state review."
}
else {
    $dirtyLaneEvidence = New-Object System.Collections.Generic.List[string]
    foreach ($lane in $WorkerLanePath) {
        $laneDirty = @($changedFiles | Where-Object { Test-AiOsPathPrefix -Path $_ -Prefix $lane })
        if ($laneDirty.Count -gt 0) {
            foreach ($item in $laneDirty) {
                $dirtyLaneEvidence.Add("$lane -> $item") | Out-Null
            }
        }
    }

    if ($dirtyLaneEvidence.Count -gt 0) {
        Add-AiOsRisk -Risks $risks -Level "WARN" -CheckId "worker_lanes_dirty" -Message "One or more worker lanes still have changed files." -Evidence @($dirtyLaneEvidence) -NextSafeAction "Review dirty worker lane files before declaring clean state."
    }
    else {
        Add-AiOsRisk -Risks $risks -Level "INFO" -CheckId "worker_lanes_dirty" -Message "No dirty files detected in supplied worker lanes." -Evidence @($WorkerLanePath) -NextSafeAction "Continue clean-state review."
    }
}

$blockedCount = @($risks | Where-Object { $_.level -eq "BLOCKED" }).Count
$warnCount = @($risks | Where-Object { $_.level -eq "WARN" }).Count
$infoCount = @($risks | Where-Object { $_.level -eq "INFO" }).Count

$result = if ($blockedCount -gt 0) {
    "BLOCKED"
}
elseif ($warnCount -gt 0) {
    "REVIEW"
}
else {
    "CLEAN"
}

$nextSafeAction = switch ($result) {
    "CLEAN" { "Repo appears clean from this DRY_RUN check. Record the clean-state report before starting new work." }
    "REVIEW" { "Review warnings before declaring the repo clean or starting new work." }
    default { "Do not declare clean state. Resolve blocked risks before new work, commit, push, pull, or merge." }
}

$report = [pscustomobject]@{
    schema = "AIOS_CLEAN_STATE_REPORT.v1"
    mode = "DRY_RUN"
    generated_at = $generatedAt
    repo_root = $repoRoot
    result = $result
    current_branch = $currentBranch
    branch_status_line = $aheadBehindText
    ahead_behind_state = $aheadBehindState
    remote_sync_likely_ok = $remoteSyncLikelyOk
    changed_files = @($changedFiles)
    staged_files = @($stagedFiles)
    untracked_files = @($untrackedFiles)
    recent_commit = $recentCommit
    worker_lane_paths_checked = @($WorkerLanePath)
    info_count = $infoCount
    warn_count = $warnCount
    blocked_count = $blockedCount
    risks = @($risks)
    files_changed_by_verifier = @()
    commit_performed = $false
    push_performed = $false
    next_safe_action = $nextSafeAction
}

if (-not $Json) {
    Write-Host "AI_OS Clean-State Verifier"
    Write-Host "Mode: DRY_RUN"
    Write-Host "Result: $result"
    Write-Host "Branch: $currentBranch"
    Write-Host "Info: $infoCount  Warnings: $warnCount  Blocked: $blockedCount"
    Write-Host ""
    Write-Host "Risk list:"
    foreach ($risk in $risks) {
        Write-Host ("- {0}: {1} - {2}" -f $risk.level, $risk.check_id, $risk.message)
    }
    Write-Host ""
    Write-Host "Next safe action: $nextSafeAction"
    Write-Host ""
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    Write-Host ""
}

$report | ConvertTo-Json -Depth 12

if ($result -eq "BLOCKED") {
    exit 1
}

exit 0
