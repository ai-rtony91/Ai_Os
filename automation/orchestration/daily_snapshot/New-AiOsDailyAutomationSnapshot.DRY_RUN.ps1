[CmdletBinding()]
param(
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

$repoRoot = Get-AiOsRepoRoot
Set-Location -LiteralPath $repoRoot

$generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
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

$latestCommitResult = Invoke-AiOsGit -Arguments @("log", "-1", "--format=%H|%ci|%s")
$latestCommit = if ($latestCommitResult.Lines.Count -gt 0) { [string]$latestCommitResult.Lines[0] } else { "UNKNOWN" }

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
        "automation/orchestration/validators/New-CommitPackagePreview.DRY_RUN.ps1",
        "automation/orchestration/show-commit-package.ps1",
        "automation/orchestration/commit_package.example.json"
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

$nextSafeAction = switch ($todayStatus) {
    "CLEAN" { "Record this snapshot, then choose the next approved AI_OS work packet." }
    "REVIEW" { "Review changed files and missing automation before approving APPLY, commit, or push." }
    default { "Stop automation work until blocked snapshot checks are resolved." }
}

$snapshot = [pscustomobject]@{
    schema = "AIOS_DAILY_AUTOMATION_SNAPSHOT.v1"
    mode = "DRY_RUN"
    generated_at = $generatedAt
    today_status = $todayStatus
    repo_root = $repoRoot
    current_branch = $currentBranch
    git_status_lines = @($gitStatusLines)
    changed_files = @($changedFiles)
    latest_commit = $latestCommit
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
    Write-Host "TODAY STATUS: $todayStatus"
    Write-Host "Branch: $currentBranch"
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
