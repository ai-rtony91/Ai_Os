[CmdletBinding()]
param(
    [switch]$Json
)

$ErrorActionPreference = "Stop"

$backupWorkDeltaScript = Join-Path (Split-Path -Parent $PSScriptRoot) "backups\Get-AiOsBackupWorkDelta.ps1"
. $backupWorkDeltaScript

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
        Lines = @($output | ForEach-Object { [string]$_ })
    }
}

function New-AiOsAutomationItem {
    param(
        [string]$Id,
        [string]$Label,
        [string[]]$CandidatePaths
    )

    $existing = @(
        foreach ($path in $CandidatePaths) {
            if (Test-Path -LiteralPath $path) {
                $path
            }
        }
    )

    return [pscustomobject]@{
        automation_id = $Id
        label = $Label
        status = if ($existing.Count -gt 0) { "PRESENT" } else { "MISSING" }
        paths = @($existing)
        candidate_paths = @($CandidatePaths)
    }
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

function Test-AiOsSecretLikePath {
    param([string]$Path)

    return $Path -match '(?i)(^|[\\/])\.env(\..*)?$|(?i)(^|[\\/])id_rsa$|(?i)(^|[\\/])id_ed25519$|(?i)\.(pem|key|pfx|p12)$|(?i)(secret|secrets|credential|password|token|private[_-]?key)'
}

function Get-AiOsRepoInventory {
    param([string]$RepoRoot)

    $allFiles = @(
        Get-ChildItem -LiteralPath $RepoRoot -Force -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object {
                $relativePath = $_.FullName.Substring($RepoRoot.Length).TrimStart('\', '/')
                $normalized = $relativePath -replace '/', '\'
                -not ($normalized -match '(^|\\)\.git(\\|$)' -or $normalized -match '(^|\\)node_modules(\\|$)' -or (Test-AiOsSecretLikePath -Path $_.FullName))
            }
    )

    $allFolders = @(
        Get-ChildItem -LiteralPath $RepoRoot -Force -Recurse -Directory -ErrorAction SilentlyContinue |
            Where-Object {
                $relativePath = $_.FullName.Substring($RepoRoot.Length).TrimStart('\', '/')
                $normalized = $relativePath -replace '/', '\'
                -not ($normalized -match '(^|\\)\.git(\\|$)' -or $normalized -match '(^|\\)node_modules(\\|$)')
            }
    )

    $totalBytes = [int64](($allFiles | Measure-Object -Property Length -Sum).Sum)

    return [pscustomobject]@{
        Files = @($allFiles)
        Folders = @($allFolders)
        TotalBytes = $totalBytes
        TotalKb = [math]::Round($totalBytes / 1KB, 2)
        TotalMb = [math]::Round($totalBytes / 1MB, 2)
    }
}

function Get-AiOsDailySnapshotText {
    param([object]$Snapshot)

    $changedFiles = @($Snapshot.files_changed_generated_today)
    $changedFilesText = if ($changedFiles.Count -eq 0) {
        'None'
    }
    elseif ($changedFiles.Count -le 20) {
        $changedFiles -join ', '
    }
    else {
        ($changedFiles | Select-Object -First 20) -join ', ' + ', ...'
    }

    $backupSizeText = if ($null -eq $Snapshot.backup_size_bytes -or $Snapshot.backup_ran -ne $true) {
        'N/A'
    }
    else {
        '{0} bytes ({1:N2} KB / {2:N2} MB)' -f $Snapshot.backup_size_bytes, $Snapshot.backup_size_kb, $Snapshot.backup_size_mb
    }

    return @"
## Daily Data Snapshot
- Date/time: $($Snapshot.date_time_local)
- Repo path: $($Snapshot.repo_path)
- Current HEAD: $($Snapshot.current_head)
- Files changed/generated today: $changedFilesText
- Artifact count: $($Snapshot.artifact_count)
- Folder count: $($Snapshot.folder_count)
- Total bytes collected today: $($Snapshot.total_bytes_collected_today) bytes ($($Snapshot.total_kb_collected_today) KB / $($Snapshot.total_mb_collected_today) MB)
- Backup size if backup ran: $backupSizeText
- Skipped secrets count: $($Snapshot.skipped_secrets_count)
- Validation/governance status: $($Snapshot.validation_governance_status)
- Success/failure: $($Snapshot.success_failure)
"@
}

$repoRoot = Get-AiOsRepoRoot
Set-Location -LiteralPath $repoRoot

$generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$generatedAtLocal = Get-Date -Format "yyyy-MM-dd HH:mm:ss K"
$dayStart = (Get-Date).Date
$branchResult = Invoke-AiOsGit -Arguments @("branch", "--show-current")
$currentBranch = if ($branchResult.Lines.Count -gt 0) { [string]$branchResult.Lines[0] } else { "UNKNOWN" }

$statusResult = Invoke-AiOsGit -Arguments @("status", "--short", "--branch")
$gitStatusLines = @($statusResult.Lines)
$changedFiles = @(
    $gitStatusLines |
        Where-Object { $_ -notlike "##*" -and -not [string]::IsNullOrWhiteSpace($_) } |
        ForEach-Object { Convert-AiOsStatusLineToPath -Line $_ } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
)

$currentHeadResult = Invoke-AiOsGit -Arguments @("rev-parse", "HEAD")
$currentHead = if ($currentHeadResult.Lines.Count -gt 0) { [string]$currentHeadResult.Lines[0] } else { "UNKNOWN" }
$backupWorkDelta = Get-AiOsBackupWorkDeltaReport -RepoRoot $repoRoot -BaseCommit "" -CurrentCommit $currentHead -TimeslotLabel "daily_snapshot"
$backupCopiedMetrics = New-AiOsBackupCopiedMetrics -BackupMode "DAILY_SNAPSHOT_NO_BACKUP" `
    -BackupRoot "" `
    -Destination "" `
    -CopiedFilesCount 0 `
    -CopiedBytes 0 `
    -ExcludedPaths @(".git", "node_modules") `
    -ExcludedSecretPatterns @(".env", "*.env", ".env.*", "*.pem", "*.key", "id_rsa", "id_ed25519", "*.pfx", "*.p12", "*secret*", "*secrets*") `
    -FullSnapshotOrIncremental "NO_BACKUP_RAN"

$latestCommitResult = Invoke-AiOsGit -Arguments @("log", "-1", "--format=%H|%ci|%s")
$latestCommit = if ($latestCommitResult.Lines.Count -gt 0) { [string]$latestCommitResult.Lines[0] } else { "UNKNOWN" }

$inventory = Get-AiOsRepoInventory -RepoRoot $repoRoot
$todayFiles = @(
    $inventory.Files |
        Where-Object { $_.LastWriteTime -ge $dayStart } |
        Sort-Object FullName
)
$todayFolders = @(
    $todayFiles |
        ForEach-Object { Split-Path -Parent $_.FullName } |
        Sort-Object -Unique
)
$dailyChangedGeneratedFiles = @(
    $todayFiles |
        ForEach-Object { $_.FullName.Substring($repoRoot.Length).TrimStart('\', '/') -replace '\\', '/' }
)
$skippedSecrets = @(
    Get-ChildItem -LiteralPath $repoRoot -Force -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { Test-AiOsSecretLikePath -Path $_.FullName }
)
$dailyBytesCollected = [int64](($todayFiles | Measure-Object -Property Length -Sum).Sum)
$dailyKbCollected = [math]::Round($dailyBytesCollected / 1KB, 2)
$dailyMbCollected = [math]::Round($dailyBytesCollected / 1MB, 2)
$artifactCount = $dailyChangedGeneratedFiles.Count
$folderCount = $todayFolders.Count
$backupRan = $false
$backupSizeBytes = $null
$backupSizeKb = $null
$backupSizeMb = $null
$validationStatus = if ($statusResult.ExitCode -eq 0 -and $currentHead -ne "UNKNOWN") { "PASS" } else { "WARN" }

$automationItems = @(
    New-AiOsAutomationItem -Id "worker_lane_status_tool" -Label "Worker lane status tool" -CandidatePaths @(
        "automation/orchestration/worker_lanes/Get-AiOsWorkerLaneStatus.DRY_RUN.ps1",
        "automation/orchestration/show-worker-status.ps1",
        "scripts/show-worker-status.ps1"
    )
    New-AiOsAutomationItem -Id "validator_chain_runner" -Label "Validator chain runner" -CandidatePaths @(
        "automation/orchestration/validator_chain_runner/Invoke-AiOsValidatorChain.DRY_RUN.ps1"
    )
    New-AiOsAutomationItem -Id "approval_runner" -Label "Approval runner" -CandidatePaths @(
        "automation/orchestration/approval_runner/Get-AiOsApprovalDecision.DRY_RUN.ps1"
    )
    New-AiOsAutomationItem -Id "commit_package_recommender" -Label "Commit package recommender or preview tool" -CandidatePaths @(
        "automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1",
        "automation/orchestration/commit_packages/COMMIT_PACKAGE_RECOMMENDATION.example.json",
        "automation/orchestration/commit_packages",
        "automation/orchestration/validators/New-CommitPackagePreview.DRY_RUN.ps1",
        "automation/orchestration/show-commit-package.ps1"
    )
    New-AiOsAutomationItem -Id "clean_state_verifier" -Label "Clean-state verifier" -CandidatePaths @(
        "automation/orchestration/clean_state/Test-AiOsCleanState.DRY_RUN.ps1",
        "automation/orchestration/clean_state_gate.ps1"
    )
    New-AiOsAutomationItem -Id "post_push_verifier" -Label "Post-push verifier" -CandidatePaths @(
        "automation/orchestration/post_push/Test-AiOsPostPushVerification.DRY_RUN.ps1",
        "automation/orchestration/post_push_verifier/Test-AiOsPostPush.DRY_RUN.ps1"
    )
    New-AiOsAutomationItem -Id "orchestration_health_summary" -Label "Orchestration health summary if present" -CandidatePaths @(
        "automation/orchestration/health_summary/Get-AiOsOrchestrationHealth.DRY_RUN.ps1",
        "Reports/dispatcher/runtime/queue_health_summary.example.json",
        "automation/orchestration/orchestration_status_snapshot.example.json",
        "automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1"
    )
)

$completedAutomation = @($automationItems | Where-Object { $_.status -eq "PRESENT" })
$missingAutomation = @($automationItems | Where-Object { $_.status -eq "MISSING" })
$governanceStatus = if (@($missingAutomation | Where-Object { $_.automation_id -in @("validator_chain_runner", "approval_runner", "clean_state_verifier") }).Count -gt 0) { "WARN" } else { "PASS" }
$validationGovernanceStatus = "$validationStatus/$governanceStatus"

$blockedReasons = New-Object System.Collections.Generic.List[string]
$reviewReasons = New-Object System.Collections.Generic.List[string]

if ($statusResult.ExitCode -ne 0) {
    $blockedReasons.Add("git status could not be read") | Out-Null
}

if ($changedFiles.Count -gt 0) {
    $reviewReasons.Add("git status has changed or untracked files") | Out-Null
}

if (@($missingAutomation | Where-Object { $_.automation_id -in @("validator_chain_runner", "approval_runner", "clean_state_verifier") }).Count -gt 0) {
    $reviewReasons.Add("one or more core automation runners are missing") | Out-Null
}

if ([string]::IsNullOrWhiteSpace($currentBranch) -or $currentBranch -eq "UNKNOWN") {
    $reviewReasons.Add("current branch is UNKNOWN") | Out-Null
}

if ($latestCommit -eq "UNKNOWN") {
    $reviewReasons.Add("latest commit is UNKNOWN") | Out-Null
}

$todayStatus = if ($blockedReasons.Count -gt 0) {
    "BLOCKED"
}
elseif ($reviewReasons.Count -gt 0) {
    "REVIEW"
}
else {
    "CLEAN"
}

$successFailure = if ($todayStatus -eq "BLOCKED") { "FAILURE" } else { "SUCCESS" }

$nextSafeAction = switch ($todayStatus) {
    "CLEAN" { "Record this snapshot, then choose the next approved AI_OS work packet." }
    "REVIEW" { "Review changed files and missing automation before approving APPLY, commit, or push." }
    default { "Stop automation work until blocked snapshot checks are resolved." }
}

$snapshot = [pscustomobject]@{
    schema = "AIOS_DAILY_AUTOMATION_SNAPSHOT.v1"
    mode = "DRY_RUN"
    generated_at = $generatedAt
    date_time_local = $generatedAtLocal
    repo_path = $repoRoot
    current_head = $currentHead
    current_branch = $currentBranch
    backup_timeslot_label = $backupWorkDelta.backup_timeslot_label
    backup_timeslot_local = $backupWorkDelta.backup_timeslot_local
    backup_window_start = $backupWorkDelta.backup_window_start
    backup_window_end = $backupWorkDelta.backup_window_end
    backup_copied_metrics = $backupCopiedMetrics
    dev_work_delta_metrics = $backupWorkDelta.dev_work_delta_metrics
    daily_work_metrics = $backupWorkDelta.daily_work_metrics
    timeslot_work_metrics = $backupWorkDelta.timeslot_work_metrics
    today_status = $todayStatus
    repo_root = $repoRoot
    git_status_lines = @($gitStatusLines)
    changed_files = @($changedFiles)
    latest_commit = $latestCommit
    files_changed_generated_today = @($dailyChangedGeneratedFiles)
    artifact_count = $artifactCount
    folder_count = $folderCount
    total_bytes_collected_today = $dailyBytesCollected
    total_kb_collected_today = $dailyKbCollected
    total_mb_collected_today = $dailyMbCollected
    repo_total_bytes = $inventory.TotalBytes
    repo_total_kb = $inventory.TotalKb
    repo_total_mb = $inventory.TotalMb
    backup_ran = $backupRan
    backup_size_bytes = $backupSizeBytes
    backup_size_kb = $backupSizeKb
    backup_size_mb = $backupSizeMb
    skipped_secrets_count = @($skippedSecrets).Count
    validation_status = $validationStatus
    governance_status = $governanceStatus
    validation_governance_status = $validationGovernanceStatus
    success_failure = $successFailure
    worked_minutes = $null
    worked_minutes_note = "Placeholder only. Fill manually in a future approved report workflow."
    completed_automation = @($completedAutomation)
    missing_automation = @($missingAutomation)
    review_reasons = @($reviewReasons)
    blocked_reasons = @($blockedReasons)
    files_changed_by_snapshot = @()
    commit_performed = $false
    push_performed = $false
    next_safe_action = $nextSafeAction
}

if (-not $Json) {
    Write-Host "AI_OS Daily Automation Snapshot"
    Write-Host "Mode: DRY_RUN"
    Write-Host "Date/time: $generatedAtLocal"
    Write-Host "Repo path: $repoRoot"
    Write-Host "Current HEAD: $currentHead"
    Write-Host "TODAY STATUS: $todayStatus"
    Write-Host "Branch: $currentBranch"
    Write-Host "Files changed/generated today: $($dailyChangedGeneratedFiles.Count)"
    Write-Host "Artifact count: $artifactCount"
    Write-Host "Folder count: $folderCount"
    Write-Host "Total bytes collected today: $dailyBytesCollected"
    Write-Host "Backup size if backup ran: N/A"
    Write-Host "Skipped secrets count: $(@($skippedSecrets).Count)"
    Write-Host "Validation/governance status: $validationGovernanceStatus"
    Write-Host "Success/failure: $successFailure"
    Write-Host "Changed files: $($changedFiles.Count)"
    Write-Host "Latest commit: $latestCommit"
    Write-Host ""
    Write-Host "Completed automation:"
    foreach ($item in $completedAutomation) {
        Write-Host ("- {0}: {1}" -f $item.automation_id, ($item.paths -join ", "))
    }
    Write-Host ""
    Write-Host "Missing automation:"
    if ($missingAutomation.Count -eq 0) {
        Write-Host "- none"
    }
    else {
        foreach ($item in $missingAutomation) {
            Write-Host ("- {0}" -f $item.automation_id)
        }
    }
    Write-Host ""
    Write-Host "Worked minutes: PLACEHOLDER"
    Write-Host "Next safe action: $nextSafeAction"
    Write-Host ""
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    Write-Host ""
}

$snapshot | ConvertTo-Json -Depth 12

if ($todayStatus -eq "BLOCKED") {
    exit 1
}

exit 0
