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

function Invoke-HelperScout {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $false)][string[]]$Arguments = @(),
        [Parameter(Mandatory = $false)][switch]$ParseJson
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{
            path = $Path
            status = "UNAVAILABLE"
            exit_code = $null
            summary = "Helper is missing."
            data = $null
            raw_output = @()
        }
    }

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & powershell -NoProfile -ExecutionPolicy Bypass -File $Path @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference
    $rawLines = @($output | ForEach-Object { [string]$_ })

    $data = $null
    $summary = if ($exitCode -eq 0) { "Helper completed." } else { "Helper returned exit code $exitCode." }
    $status = if ($exitCode -eq 0) { "READY" } else { "REVIEW" }

    if ($ParseJson -and $rawLines.Count -gt 0) {
        $jsonStart = -1
        for ($i = 0; $i -lt $rawLines.Count; $i++) {
            if ($rawLines[$i].Trim().StartsWith("{")) {
                $jsonStart = $i
                break
            }
        }

        if ($jsonStart -ge 0) {
            try {
                $jsonText = ($rawLines[$jsonStart..($rawLines.Count - 1)] -join [Environment]::NewLine)
                $data = $jsonText | ConvertFrom-Json
            }
            catch {
                $status = "REVIEW"
                $summary = "Helper completed, but JSON output could not be parsed."
            }
        }
        elseif ($exitCode -eq 0) {
            $status = "REVIEW"
            $summary = "Helper completed, but JSON output was not found."
        }
    }

    return [pscustomobject]@{
        path = $Path
        status = $status
        exit_code = $exitCode
        summary = $summary
        data = $data
        raw_output = $rawLines
    }
}

function Get-PropertyValue {
    param(
        [Parameter(Mandatory = $false)]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $false)][string]$Default = "UNKNOWN"
    )

    if ($null -eq $Object) {
        return $Default
    }

    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property -or $null -eq $property.Value -or [string]::IsNullOrWhiteSpace([string]$property.Value)) {
        return $Default
    }

    return [string]$property.Value
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
$stagedResult = Invoke-GitText -Arguments @("diff", "--cached", "--name-only")
$gitWarnings = @(
    @(
        Get-GitWarnings -Lines $branchResult.Output
        Get-GitWarnings -Lines $statusResult.Output
        Get-GitWarnings -Lines $stagedResult.Output
    ) | Sort-Object -Unique
)

$currentBranch = Get-FirstCleanLine -Lines $branchResult.Output
$statusLines = @(Remove-GitWarnings -Lines $statusResult.Output | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
$stagedFiles = @(Remove-GitWarnings -Lines $stagedResult.Output | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
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
$prLaneScoutPath = "automation/orchestration/pr_gates/Invoke-AiOsPrLaneRunner.DRY_RUN.ps1"
$commitPushScoutPath = "automation/orchestration/commit_packages/Test-AiOsCommitPushGate.DRY_RUN.ps1"
$knownStateScoutPath = "automation/orchestration/control_summary/Get-AiOsKnownStateFilter.DRY_RUN.ps1"
$prHandoffScoutPath = "automation/orchestration/Export-AIOSPrHandoff.ps1"
$approvalScoutPath = "automation/orchestration/approval_runner/Get-AiOsApprovalDecision.DRY_RUN.ps1"
$prLaneScoutExists = Test-ToolPresent -Paths @($prLaneScoutPath)
$commitPushScoutExists = Test-ToolPresent -Paths @($commitPushScoutPath)
$knownStateScoutExists = Test-ToolPresent -Paths @($knownStateScoutPath)
$prHandoffScoutExists = Test-ToolPresent -Paths @($prHandoffScoutPath)
$approvalScoutExists = Test-ToolPresent -Paths @($approvalScoutPath)

$prLaneScout = Invoke-HelperScout -Path $prLaneScoutPath -Arguments @("-Mode", "DRY_RUN", "-Json") -ParseJson
$commitPushScout = Invoke-HelperScout -Path $commitPushScoutPath -Arguments @("-Mode", "DRY_RUN", "-Json") -ParseJson
$knownStateScout = Invoke-HelperScout -Path $knownStateScoutPath -Arguments @("-Mode", "DRY_RUN", "-Json") -ParseJson
$approvalScout = Invoke-HelperScout -Path $approvalScoutPath -Arguments @("-CommandText", "git status --short --branch", "-LaneType", "daily-workflow-summary", "-Mode", "DRY_RUN", "-Json") -ParseJson

$prNumber = $null
if ($null -ne $prLaneScout.data) {
    $prInfoProperty = $prLaneScout.data.PSObject.Properties["pr_info"]
    if ($null -ne $prInfoProperty -and $null -ne $prInfoProperty.Value) {
        $detectedProperty = $prInfoProperty.Value.PSObject.Properties["detected"]
        $prProperty = $prInfoProperty.Value.PSObject.Properties["pr"]
        if ($null -ne $detectedProperty -and $detectedProperty.Value -and $null -ne $prProperty -and $null -ne $prProperty.Value) {
            $numberProperty = $prProperty.Value.PSObject.Properties["number"]
            if ($null -ne $numberProperty -and $null -ne $numberProperty.Value) {
                $prNumber = [int]$numberProperty.Value
            }
        }
    }
}

$prHandoffScout = if ($null -ne $prNumber) {
    Invoke-HelperScout -Path $prHandoffScoutPath -Arguments @("-PrNumber", [string]$prNumber, "-Format", "JSON", "-Mode", "DRY_RUN") -ParseJson
}
else {
    [pscustomobject]@{
        path = $prHandoffScoutPath
        status = if ($prHandoffScoutExists) { "SKIPPED" } else { "UNAVAILABLE" }
        exit_code = $null
        summary = if ($prHandoffScoutExists) { "No PR detected for handoff export." } else { "Helper is missing." }
        data = $null
        raw_output = @()
    }
}

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

$scoutChecks = @(
    [pscustomobject]@{ check_id = "pr_lane_runner_scout"; label = "PR lane runner scout"; helper = $prLaneScout },
    [pscustomobject]@{ check_id = "commit_push_gate_scout"; label = "Commit/push gate scout"; helper = $commitPushScout },
    [pscustomobject]@{ check_id = "known_state_filter_scout"; label = "Known-state filter scout"; helper = $knownStateScout },
    [pscustomobject]@{ check_id = "pr_handoff_scout"; label = "PR handoff scout"; helper = $prHandoffScout },
    [pscustomobject]@{ check_id = "approval_decision_scout"; label = "Approval decision scout"; helper = $approvalScout }
)

foreach ($scout in $scoutChecks) {
    $status = switch ($scout.helper.status) {
        "READY" { "READY" }
        "SKIPPED" { "REVIEW" }
        "UNAVAILABLE" { "REVIEW" }
        default { "REVIEW" }
    }
    if ($scout.helper.status -eq "UNAVAILABLE") {
        $risks += "$($scout.label) is unavailable."
    }
    elseif ($scout.helper.status -eq "REVIEW") {
        $risks += "$($scout.label) returned review status."
    }
    Add-Check -Checks ([ref]$checks) -CheckId $scout.check_id -Label $scout.label -Status $status -Summary $scout.helper.summary
}

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

$branchSyncState = Get-PropertyValue -Object $knownStateScout.data -Name "branch_sync_state"
$knownBacklog = Get-PropertyValue -Object $knownStateScout.data -Name "untracked_backlog" -Default $(if ($untrackedFiles.Count -gt 0) { "exists; known local backlog" } else { "none" })
$prLaneState = Get-PropertyValue -Object $prLaneScout.data -Name "lane_state"
$prApprovalClass = Get-PropertyValue -Object $prLaneScout.data -Name "approval_class"
$prRecommendedCommand = Get-PropertyValue -Object $prLaneScout.data -Name "recommended_next_command"
$ciValidate = Get-PropertyValue -Object $prLaneScout.data -Name "ci_validate"
$commitGateState = Get-PropertyValue -Object $commitPushScout.data -Name "gate_state"
$commitApprovalClass = Get-PropertyValue -Object $commitPushScout.data -Name "approval_class"
$approvalRecommendation = Get-PropertyValue -Object $approvalScout.data -Name "recommended_option" -Default "UNKNOWN"

$commitSafe = switch ($commitGateState) {
    "SAFE_TO_COMMIT" { "yes" }
    "BLOCKED" { "no" }
    "HUMAN_APPROVAL_REQUIRED" { "approval_required" }
    default { "unknown" }
}
$pushSafe = switch ($commitGateState) {
    "SAFE_TO_PUSH" { "yes" }
    "BLOCKED" { "no" }
    "HUMAN_APPROVAL_REQUIRED" { "approval_required" }
    default { "unknown" }
}
$prLaneReady = switch ($prLaneState) {
    "BLOCKED" { "blocked" }
    "UNKNOWN" { "unknown" }
    default {
        if ($prLaneState -eq "UNKNOWN") { "unknown" } else { $prLaneState }
    }
}

$mainSynced = if ($currentBranch -ne "main") {
    "unknown; not on main"
}
elseif ($branchSyncState -eq "synced_or_no_ahead_behind_marker") {
    "yes"
}
elseif ($branchSyncState -eq "ahead" -or $branchSyncState -eq "behind" -or $branchSyncState -eq "diverged") {
    "no; $branchSyncState"
}
else {
    "unknown"
}

$dailyNextAction = if ($commitGateState -eq "BLOCKED" -or $prLaneState -eq "BLOCKED") {
    "Stop and resolve BLOCKED findings before APPLY, commit, push, merge, or cleanup."
}
elseif ($prRecommendedCommand -ne "UNKNOWN" -and $prApprovalClass -eq "AUTO_PROCEED_READ_ONLY") {
    $prRecommendedCommand
}
elseif ($resultStatus -eq "READY") {
    $nextCommand
}
else {
    "Review the control summary and request the next scoped AI_OS lane."
}

$dailyWorkflowSummary = [pscustomobject]@{
    current_branch = $currentBranch
    branch_sync = $branchSyncState
    main_synced = $mainSynced
    known_backlog = $knownBacklog
    staged_files = $stagedFiles.Count
    unstaged_tracked = $dirtyFiles.Count
    pr_lane_ready = $prLaneReady
    commit_safe = $commitSafe
    push_safe = $pushSafe
    ci_validate = $ciValidate
    approval_state = if ($prApprovalClass -ne "UNKNOWN") { $prApprovalClass } elseif ($commitApprovalClass -ne "UNKNOWN") { $commitApprovalClass } else { $approvalRecommendation }
    next_safe_action = $dailyNextAction
    blockers = @($risks | Sort-Object -Unique)
    mutation_status = "none"
    commit_status = "not committed"
    push_status = "not pushed"
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
        branch_sync = $branchSyncState
        dirty_count = $dirtyFiles.Count
        staged_count = $stagedFiles.Count
        untracked_count = $untrackedFiles.Count
        known_backlog = $knownBacklog
    }
    daily_workflow_summary = $dailyWorkflowSummary
    checks = $checks
    risks = @($risks | Sort-Object -Unique)
    git_warnings = $gitWarnings
    helper_scouts = [pscustomobject]@{
        pr_lane_runner = [pscustomobject]@{ path = $prLaneScoutPath; status = $prLaneScout.status; summary = $prLaneScout.summary }
        commit_push_gate = [pscustomobject]@{ path = $commitPushScoutPath; status = $commitPushScout.status; summary = $commitPushScout.summary }
        known_state_filter = [pscustomobject]@{ path = $knownStateScoutPath; status = $knownStateScout.status; summary = $knownStateScout.summary }
        pr_handoff = [pscustomobject]@{ path = $prHandoffScoutPath; status = $prHandoffScout.status; summary = $prHandoffScout.summary }
        approval_decision = [pscustomobject]@{ path = $approvalScoutPath; status = $approvalScout.status; summary = $approvalScout.summary }
    }
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
Write-Host "Staged files: $($stagedFiles.Count)"
Write-Host "Untracked files: $($untrackedFiles.Count)"
Write-Host ""

Write-Host "Daily Workflow Summary:"
Write-Host "  Branch state:"
Write-Host "    Current: $($dailyWorkflowSummary.current_branch)"
Write-Host "    Sync: $($dailyWorkflowSummary.branch_sync)"
Write-Host "    Main synced: $($dailyWorkflowSummary.main_synced)"
Write-Host "  Repo state:"
Write-Host "    Known backlog: $($dailyWorkflowSummary.known_backlog)"
Write-Host "    Staged files: $($dailyWorkflowSummary.staged_files)"
Write-Host "    Unstaged tracked: $($dailyWorkflowSummary.unstaged_tracked)"
Write-Host "  Readiness gates:"
Write-Host "    PR lane ready: $($dailyWorkflowSummary.pr_lane_ready)"
Write-Host "    Commit safe: $($dailyWorkflowSummary.commit_safe)"
Write-Host "    Push safe: $($dailyWorkflowSummary.push_safe)"
Write-Host "    CI/validate: $($dailyWorkflowSummary.ci_validate)"
Write-Host "    Approval state: $($dailyWorkflowSummary.approval_state)"
Write-Host "  Mutation status: $($dailyWorkflowSummary.mutation_status)"
Write-Host "  Commit status: $($dailyWorkflowSummary.commit_status)"
Write-Host "  Push status: $($dailyWorkflowSummary.push_status)"
Write-Host "  Next safe action: $($dailyWorkflowSummary.next_safe_action)"
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
