[CmdletBinding()]
param(
    [string]$TaskId = "CREW-INTEGRATION-PREVIEW",
    [string]$Title = "Crew integration recommendation preview",
    [string]$Purpose = "Preview Crew Core orchestration integration readiness.",
    [string]$Owner = "Human Owner",
    [string]$PacketId = "PACKET_ID_REQUIRED",
    [string]$RecommendedWorker = "EAST_OCC_01",
    [string]$RecommendedLane = "orchestration-integration",
    [string[]]$AllowedPaths = @(),
    [string[]]$BlockedPaths = @(),
    [string[]]$ChangedPaths = @(),
    [string]$StopPoint = "DRY_RUN_REPORT_ONLY",
    [switch]$OutputJson
)

$ErrorActionPreference = "Stop"

function ConvertTo-AiOsRepoPath {
    param([AllowNull()][string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }

    return $Path.Replace("\", "/").Trim()
}

function Invoke-AiOsCrewJsonHelper {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $false)][object[]]$HelperArguments = @()
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{
            helper = $Path
            status = "MISSING"
            result = $null
            error = "Helper not found."
        }
    }

    try {
        $output = & powershell -NoProfile -File $Path @HelperArguments
        $jsonText = ($output | Out-String).Trim()
        $parsed = if ([string]::IsNullOrWhiteSpace($jsonText)) { $null } else { $jsonText | ConvertFrom-Json }

        return [pscustomobject]@{
            helper = $Path
            status = "PASS"
            result = $parsed
            error = $null
        }
    }
    catch {
        return [pscustomobject]@{
            helper = $Path
            status = "FAIL"
            result = $null
            error = $_.Exception.Message
        }
    }
}

$crewRoot = "automation/orchestration/crew"
$taskHelper = Join-Path $crewRoot "New-AiOsCrewTask.DRY_RUN.ps1"
$assignmentHelper = Join-Path $crewRoot "Get-AiOsCrewAssignmentRecommendation.DRY_RUN.ps1"
$validatorHelper = Join-Path $crewRoot "Get-AiOsCrewValidatorRecommendation.DRY_RUN.ps1"
$dryRunResultHelper = Join-Path $crewRoot "New-AiOsCrewDryRunResult.DRY_RUN.ps1"
$approvalSummaryHelper = "automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1"
$commitPackageHelper = "automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1"

$normalizedAllowedPaths = @($AllowedPaths | ForEach-Object { ConvertTo-AiOsRepoPath -Path $_ } | Where-Object { $_ })
$normalizedBlockedPaths = @($BlockedPaths | ForEach-Object { ConvertTo-AiOsRepoPath -Path $_ } | Where-Object { $_ })
$normalizedChangedPaths = @($ChangedPaths | ForEach-Object { ConvertTo-AiOsRepoPath -Path $_ } | Where-Object { $_ })
if ($normalizedChangedPaths.Count -eq 0) {
    $normalizedChangedPaths = @($normalizedAllowedPaths)
}

$taskArgs = @(
    "-TaskId", $TaskId,
    "-Title", $Title,
    "-Purpose", $Purpose,
    "-Owner", $Owner,
    "-StopPoint", $StopPoint
)
if ($normalizedAllowedPaths.Count -gt 0) {
    $taskArgs += "-AllowedPaths"
    $taskArgs += $normalizedAllowedPaths
}
if ($normalizedBlockedPaths.Count -gt 0) {
    $taskArgs += "-BlockedPaths"
    $taskArgs += $normalizedBlockedPaths
}

$assignmentArgs = @(
    "-WorkerId", $RecommendedWorker,
    "-PacketId", $PacketId
)
if ($normalizedAllowedPaths.Count -gt 0) {
    $assignmentArgs += "-AssignedPaths"
    $assignmentArgs += $normalizedAllowedPaths
}

$validatorArgs = @()
if ($normalizedChangedPaths.Count -gt 0) {
    $validatorArgs += "-ChangedPaths"
    $validatorArgs += $normalizedChangedPaths
}

$dryRunArgs = @(
    "-PacketId", $PacketId,
    "-Summary", "Crew integration recommendation preview.",
    "-RiskLevel", "normal",
    "-StopPoint", $StopPoint
)
if ($normalizedChangedPaths.Count -gt 0) {
    $dryRunArgs += "-FilesToModify"
    $dryRunArgs += $normalizedChangedPaths
}

$taskPreview = Invoke-AiOsCrewJsonHelper -Path $taskHelper -HelperArguments $taskArgs
$assignmentPreview = Invoke-AiOsCrewJsonHelper -Path $assignmentHelper -HelperArguments $assignmentArgs
$validatorPreview = Invoke-AiOsCrewJsonHelper -Path $validatorHelper -HelperArguments $validatorArgs
$dryRunPreview = Invoke-AiOsCrewJsonHelper -Path $dryRunResultHelper -HelperArguments $dryRunArgs
$approvalPreview = Invoke-AiOsCrewJsonHelper -Path $approvalSummaryHelper -HelperArguments @("-QuietJson")
$commitPreview = Invoke-AiOsCrewJsonHelper -Path $commitPackageHelper -HelperArguments @("-OutputJson")

$helperResults = @($taskPreview, $assignmentPreview, $validatorPreview, $dryRunPreview, $approvalPreview, $commitPreview)
$failedHelpers = @($helperResults | Where-Object { $_.status -ne "PASS" })

$blockedMatches = @(
    @($assignmentPreview.result.blocked_path_matches)
    @($validatorPreview.result.blocked_path_matches)
) | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | Select-Object -Unique

$collisionWarning = if ($blockedMatches.Count -gt 0) {
    "BLOCKED: blocked path match detected. Do not assign or route until scope is corrected."
}
elseif ($normalizedAllowedPaths.Count -eq 0) {
    "REVIEW_REQUIRED: allowed paths are empty. Run lock collision validation before APPLY."
}
else {
    "REVIEW_REQUIRED: run Test-WorkerClaimCollision.DRY_RUN.ps1 and lock registry validation before APPLY."
}

$approvalStateSummary = if ($approvalPreview.result) {
    [pscustomobject]@{
        pending_approvals = @($approvalPreview.result.pending_approvals).Count
        approved_actions = @($approvalPreview.result.approved_actions).Count
        blocked_actions = @($approvalPreview.result.blocked_actions).Count
        next_safe_command = $approvalPreview.result.next_safe_command
    }
}
else {
    [pscustomobject]@{
        pending_approvals = 0
        approved_actions = 0
        blocked_actions = 0
        next_safe_command = "Approval summary unavailable."
    }
}

$commitPackagePreview = if ($commitPreview.result) {
    [pscustomobject]@{
        current_branch = $commitPreview.result.current_branch
        git_status = $commitPreview.result.git_status
        recommended_file_count = $commitPreview.result.summary.recommended_file_count
        excluded_file_count = $commitPreview.result.summary.excluded_file_count
        risk_count = $commitPreview.result.summary.risk_count
        commit_message_suggestion = $commitPreview.result.commit_message_suggestion
        next_safe_action = $commitPreview.result.next_safe_action
    }
}
else {
    [pscustomobject]@{
        current_branch = "UNKNOWN"
        git_status = "UNKNOWN"
        recommended_file_count = 0
        excluded_file_count = 0
        risk_count = 0
        commit_message_suggestion = "Commit package unavailable"
        next_safe_action = "Commit package preview unavailable."
    }
}

$overallReadiness = if ($blockedMatches.Count -gt 0 -or $failedHelpers.Count -gt 0) {
    "BLOCKED"
}
else {
    "REVIEW_REQUIRED"
}

$nextSafeAction = if ($overallReadiness -eq "BLOCKED") {
    "Stop. Resolve blocked paths or failed helper outputs before preparing any APPLY packet."
}
else {
    "Review this recommendation, run lock collision validation and recommended validators, then request Human Owner approval before APPLY."
}

$result = [pscustomobject]@{
    schema = "AIOS_CREW_INTEGRATION_RECOMMENDATION.v1"
    mode = "DRY_RUN_READ_ONLY"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    packet_summary = [pscustomobject]@{
        task_id = $TaskId
        packet_id = $PacketId
        title = $Title
        purpose = $Purpose
        owner = $Owner
        allowed_paths = @($normalizedAllowedPaths)
        blocked_paths = @($normalizedBlockedPaths)
        changed_paths = @($normalizedChangedPaths)
        stop_point = $StopPoint
    }
    recommended_worker = $RecommendedWorker
    recommended_lane = $RecommendedLane
    recommended_validators = @($validatorPreview.result.recommended_validators)
    approval_state_summary = $approvalStateSummary
    commit_package_preview = $commitPackagePreview
    collision_warning = $collisionWarning
    helper_outputs = [pscustomobject]@{
        task_intake = $taskPreview.result
        worker_assignment = $assignmentPreview.result
        validator_recommendation = $validatorPreview.result
        dry_run_result = $dryRunPreview.result
    }
    helper_status = @($helperResults | ForEach-Object {
        [pscustomobject]@{
            helper = $_.helper
            status = $_.status
            error = $_.error
        }
    })
    safety = [pscustomobject]@{
        dry_run_only = $true
        validator_output_is_evidence_only = $true
        creates_approval = $false
        claims_locks = $false
        runs_apply = $false
        modifies_files = $false
        commits = $false
        pushes = $false
        merges = $false
    }
    modifies_files = $false
    commits = $false
    pushes = $false
    next_safe_action = $nextSafeAction
    overall_readiness = $overallReadiness
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 16
    exit 0
}

Write-Output ($result | ConvertTo-Json -Depth 16)
