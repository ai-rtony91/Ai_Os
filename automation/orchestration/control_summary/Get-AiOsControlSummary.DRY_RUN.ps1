param(
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

function Test-ToolPresent {
    param([Parameter(Mandatory = $true)][string[]]$Paths)

    foreach ($path in $Paths) {
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            return $true
        }
    }

    return $false
}

function Get-LaneFromBranch {
    param([Parameter(Mandatory = $true)][string]$Branch)

    switch -Regex ($Branch) {
        "^codex/worker-0?1$" { return "CODEX_01" }
        "^codex/worker-0?2$" { return "CODEX_02" }
        "^claude/worker-0?1$" { return "CLAUDE_01" }
        "^(main|master|release/.+)$" { return "MAIN_CONTROL" }
        default { return "UNKNOWN" }
    }
}

function Add-Check {
    param(
        [ref]$Checks,
        [string]$CheckId,
        [string]$Label,
        [string]$Status,
        [string]$Summary
    )

    $Checks.Value += [pscustomobject]@{
        check_id = $CheckId
        label = $Label
        status = $Status
        summary = $Summary
    }
}

$branchResult = Invoke-GitText -Arguments @("branch", "--show-current")
$statusResult = Invoke-GitText -Arguments @("status", "--short")
$gitWarnings = @(
    @(
        Get-GitWarnings -Lines $branchResult.Output
        Get-GitWarnings -Lines $statusResult.Output
    ) | Sort-Object -Unique
)

$currentBranch = Get-FirstCleanLine -Lines $branchResult.Output
$statusLines = @(Remove-GitWarnings -Lines $statusResult.Output | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$dirtyFiles = @($statusLines | Where-Object { -not $_.StartsWith("?? ") })
$untrackedFiles = @($statusLines | Where-Object { $_.StartsWith("?? ") })
$gitStatus = if ($statusLines.Count -eq 0) { "clean" } else { "dirty" }
$lane = Get-LaneFromBranch -Branch $currentBranch

$cleanStateExists = Test-ToolPresent -Paths @("automation/orchestration/clean_state/Test-AiOsCleanState.DRY_RUN.ps1")
$approvalExists = Test-ToolPresent -Paths @("automation/orchestration/approval_runner/Get-AiOsApprovalDecision.DRY_RUN.ps1")
$commitPackageExists = Test-ToolPresent -Paths @("automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1")
$validatorExists = Test-ToolPresent -Paths @("automation/orchestration/validator_chain_runner/Invoke-AiOsValidatorChain.DRY_RUN.ps1")
$postPushExists = Test-ToolPresent -Paths @("automation/orchestration/post_push/Test-AiOsPostPushVerification.DRY_RUN.ps1")
$workerLaneExists = Test-ToolPresent -Paths @("automation/orchestration/worker_lanes/Get-AiOsWorkerLaneStatus.DRY_RUN.ps1")
$complianceExists = Test-ToolPresent -Paths @("automation/orchestration/compliance/Test-AiOsAgentCompliance.DRY_RUN.ps1")
$dailySnapshotExists = Test-ToolPresent -Paths @("automation/orchestration/daily_snapshot/New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1")
$healthSummaryExists = Test-ToolPresent -Paths @("automation/orchestration/health_summary/Get-AiOsOrchestrationHealth.DRY_RUN.ps1")

$checks = @()
$risks = @()

$workerStatus = "READY"
$workerSummary = "Current branch maps to $lane."
if ($lane -eq "UNKNOWN") {
    $workerStatus = "BLOCKED"
    $workerSummary = "Current branch does not map to a known worker lane."
    $risks += "Current branch does not map to a known worker lane."
} elseif ($gitStatus -ne "clean") {
    $workerStatus = "REVIEW"
    $workerSummary = "Current branch maps to $lane and repo has dirty or untracked files."
}
if (-not $workerLaneExists) {
    $workerStatus = "REVIEW"
    $workerSummary = "Worker lane checker is missing; branch mapping was inferred locally."
    $risks += "Worker lane checker is missing."
}
Add-Check -Checks ([ref]$checks) -CheckId "worker_lane_status" -Label "Worker lane status" -Status $workerStatus -Summary $workerSummary

$complianceStatus = if ($complianceExists) { "READY" } else { "REVIEW" }
$complianceSummary = if ($complianceExists) { "Compliance checker exists." } else { "Compliance checker is missing." }
if (-not $complianceExists) {
    $risks += "Compliance checker is missing."
}
Add-Check -Checks ([ref]$checks) -CheckId "compliance_status" -Label "Compliance status" -Status $complianceStatus -Summary $complianceSummary

$validatorStatus = if ($validatorExists) { "READY" } else { "BLOCKED" }
$validatorSummary = if ($validatorExists) { "Validator chain runner exists." } else { "Validator chain runner is missing." }
if (-not $validatorExists) {
    $risks += "Validator chain runner is missing."
}
Add-Check -Checks ([ref]$checks) -CheckId "validator_status" -Label "Validator status" -Status $validatorStatus -Summary $validatorSummary

$healthStatus = if ($healthSummaryExists) { "READY" } else { "REVIEW" }
$healthSummary = if ($healthSummaryExists) { "Health summary exists." } else { "Health summary tool is missing." }
if (-not $healthSummaryExists) {
    $risks += "Health summary tool is missing."
}
Add-Check -Checks ([ref]$checks) -CheckId "health_summary_readiness" -Label "Health summary readiness" -Status $healthStatus -Summary $healthSummary

$dailySnapshotStatus = if ($dailySnapshotExists) { "READY" } else { "REVIEW" }
$dailySnapshotSummary = if ($dailySnapshotExists) { "Daily snapshot tool exists." } else { "Daily snapshot tool is missing." }
if (-not $dailySnapshotExists) {
    $risks += "Daily snapshot tool is missing."
}
Add-Check -Checks ([ref]$checks) -CheckId "daily_snapshot_readiness" -Label "Daily snapshot readiness" -Status $dailySnapshotStatus -Summary $dailySnapshotSummary

$approvalStatus = if ($approvalExists) { "READY" } else { "BLOCKED" }
$approvalSummary = if ($approvalExists) { "Approval processor exists." } else { "Approval processor is missing." }
if (-not $approvalExists) {
    $risks += "Approval processor is missing."
}
Add-Check -Checks ([ref]$checks) -CheckId "approval_readiness" -Label "Approval readiness" -Status $approvalStatus -Summary $approvalSummary

$commitStatus = if ($commitPackageExists) { "READY" } else { "REVIEW" }
$commitSummary = if ($commitPackageExists) { "Commit package recommender exists." } else { "Commit package recommender is missing." }
if (-not $commitPackageExists) {
    $risks += "Commit package recommender is missing."
}
Add-Check -Checks ([ref]$checks) -CheckId "commit_package_readiness" -Label "Commit package readiness" -Status $commitStatus -Summary $commitSummary

$cleanStateStatus = "READY"
$cleanStateSummary = "Clean-state verifier exists and repo is clean."
if (-not $cleanStateExists) {
    $cleanStateStatus = "BLOCKED"
    $cleanStateSummary = "Clean-state verifier is missing."
    $risks += "Clean-state verifier is missing."
} elseif ($gitStatus -ne "clean") {
    $cleanStateStatus = "REVIEW"
    $cleanStateSummary = "Clean-state verifier exists, but repo is dirty."
    $risks += "Repository has dirty or untracked files."
}
Add-Check -Checks ([ref]$checks) -CheckId "clean_state_result" -Label "Clean-state result" -Status $cleanStateStatus -Summary $cleanStateSummary

$postPushStatus = "READY"
$postPushSummary = "Post-push verifier exists and current branch is main."
if (-not $postPushExists) {
    $postPushStatus = "REVIEW"
    $postPushSummary = "Post-push verifier is missing."
    $risks += "Post-push verifier is missing."
} elseif ($currentBranch -ne "main") {
    $postPushStatus = "BLOCKED"
    $postPushSummary = "Post-push verification is blocked because current branch is not main."
    $risks += "Post-push verification is not valid from the current worker branch."
}
Add-Check -Checks ([ref]$checks) -CheckId "post_push_result" -Label "Post-push result" -Status $postPushStatus -Summary $postPushSummary

$resultStatus = "READY"
if (@($checks | Where-Object { $_.status -eq "BLOCKED" }).Count -gt 0) {
    $resultStatus = "BLOCKED"
} elseif (@($checks | Where-Object { $_.status -eq "REVIEW" }).Count -gt 0 -or $gitStatus -ne "clean") {
    $resultStatus = "REVIEW"
}

$nextCommand = "powershell -ExecutionPolicy Bypass -File automation\orchestration\health_summary\Get-AiOsOrchestrationHealth.DRY_RUN.ps1"
if ($resultStatus -eq "READY") {
    $nextCommand = "powershell -ExecutionPolicy Bypass -File automation\orchestration\validator_chain_runner\Invoke-AiOsValidatorChain.DRY_RUN.ps1"
} elseif ($resultStatus -eq "BLOCKED") {
    $nextCommand = "powershell -ExecutionPolicy Bypass -File automation\orchestration\health_summary\Get-AiOsOrchestrationHealth.DRY_RUN.ps1"
}

$result = [pscustomobject]@{
    system = "AI_OS"
    task = "Show AI_OS orchestration control summary"
    mode = "DRY_RUN"
    result = $resultStatus
    repo_state = [pscustomobject]@{
        branch = $currentBranch
        lane = $lane
        git_status = $gitStatus
        dirty_count = $dirtyFiles.Count
        untracked_count = $untrackedFiles.Count
    }
    checks = $checks
    risks = @($risks | Sort-Object -Unique)
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
    next_safe_command = $nextCommand
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS Orchestration Control Summary"
Write-Host "Mode: DRY_RUN"
Write-Host "Result: $resultStatus"
Write-Host "Branch: $currentBranch"
Write-Host "Lane: $lane"
Write-Host "Repo status: $gitStatus"
Write-Host "Dirty tracked files: $($dirtyFiles.Count)"
Write-Host "Untracked files: $($untrackedFiles.Count)"
Write-Host ""

Write-Host "Checks:"
foreach ($check in $checks) {
    Write-Host "  - $($check.label): $($check.status)"
    Write-Host "    $($check.summary)"
}
Write-Host ""

Write-Host "Risks:"
if ($risks.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($risk in ($risks | Sort-Object -Unique)) {
        Write-Host "  - $risk"
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
Write-Host "Next safe command:"
Write-Host "  $nextCommand"
