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

function ConvertTo-ProcessArgument {
    param([AllowNull()][object]$Value)

    $text = if ($null -eq $Value) { "" } else { [string]$Value }
    if ($text -notmatch '[\s"]') {
        return $text
    }

    return '"' + ($text -replace '"', '\"') + '"'
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

    $resolvedPath = (Resolve-Path -LiteralPath $Path).Path
    $argumentItems = @("-NoProfile", "-File", $resolvedPath) + @($HelperArguments)
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = "powershell"
    $psi.Arguments = (($argumentItems | ForEach-Object { ConvertTo-ProcessArgument -Value $_ }) -join " ")
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $psi

    try {
        $null = $process.Start()
        $stdout = $process.StandardOutput.ReadToEnd()
        $stderr = $process.StandardError.ReadToEnd()
        $process.WaitForExit()

        $jsonText = $stdout.Trim()
        $parsed = if ([string]::IsNullOrWhiteSpace($jsonText)) { $null } else { $jsonText | ConvertFrom-Json }
        $status = if ($process.ExitCode -eq 0 -and [string]::IsNullOrWhiteSpace($stderr)) { "PASS" } else { "FAIL" }
        $errorText = @($stderr.Trim(), $(if ($process.ExitCode -ne 0) { "Exit code: $($process.ExitCode)" } else { "" })) |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) }

        return [pscustomobject]@{
            helper = $Path
            status = $status
            result = $parsed
            error = if ($errorText.Count -gt 0) { $errorText -join "`n" } else { $null }
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
    finally {
        if ($process) {
            $process.Dispose()
        }
    }
}

function Get-AiOsCampaignRegistryDetails {
    param(
        [Parameter(Mandatory = $true)][string]$RegistryPath,
        [Parameter(Mandatory = $false)][AllowNull()][string]$CampaignId
    )

    if ([string]::IsNullOrWhiteSpace($CampaignId)) {
        return $null
    }

    if (-not (Test-Path -LiteralPath $RegistryPath -PathType Leaf)) {
        return $null
    }

    try {
        $registry = Get-Content -Raw -LiteralPath $RegistryPath | ConvertFrom-Json
        return @($registry.campaigns | Where-Object { $_.campaign_id -eq $CampaignId } | Select-Object -First 1)
    }
    catch {
        return $null
    }
}

$crewRoot = "automation/orchestration/crew"
$taskHelper = Join-Path $crewRoot "New-AiOsCrewTask.DRY_RUN.ps1"
$assignmentHelper = Join-Path $crewRoot "Get-AiOsCrewAssignmentRecommendation.DRY_RUN.ps1"
$validatorHelper = Join-Path $crewRoot "Get-AiOsCrewValidatorRecommendation.DRY_RUN.ps1"
$dryRunResultHelper = Join-Path $crewRoot "New-AiOsCrewDryRunResult.DRY_RUN.ps1"
$approvalSummaryHelper = "automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1"
$commitPackageHelper = "automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1"
$campaignHelper = "automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1"
$campaignRegistryPath = "automation/orchestration/campaign_registry/AIOS_STRATEGIC_CAMPAIGN_REGISTRY.json"

$campaignPreview = Invoke-AiOsCrewJsonHelper -Path $campaignHelper -HelperArguments @("-OutputJson")
$campaignResult = $campaignPreview.result
$campaignReady = (
    $campaignPreview.status -eq "PASS" -and
    $null -ne $campaignResult -and
    $campaignResult.overall_readiness -eq "READY_FOR_PACKET_PREVIEW" -and
    -not [string]::IsNullOrWhiteSpace([string]$campaignResult.next_packet_candidate)
)
$campaignId = if ($campaignResult -and $campaignResult.recommended_campaign) {
    [string]$campaignResult.recommended_campaign.campaign_id
}
else {
    ""
}
$campaignDetails = Get-AiOsCampaignRegistryDetails -RegistryPath $campaignRegistryPath -CampaignId $campaignId

$effectiveTaskId = $TaskId
$effectiveTitle = $Title
$effectivePurpose = $Purpose
$effectivePacketId = $PacketId
$effectiveRecommendedWorker = $RecommendedWorker
$effectiveRecommendedLane = $RecommendedLane
$effectiveAllowedPaths = @($AllowedPaths)
$effectiveBlockedPaths = @($BlockedPaths)
$effectiveChangedPaths = @($ChangedPaths)

if ($campaignReady) {
    $effectivePacketId = [string]$campaignResult.next_packet_candidate
    if ($campaignResult.recommended_stage -and -not [string]::IsNullOrWhiteSpace([string]$campaignResult.recommended_stage.stage_id)) {
        $effectiveTaskId = [string]$campaignResult.recommended_stage.stage_id
    }
    if ($campaignResult.recommended_stage -and -not [string]::IsNullOrWhiteSpace([string]$campaignResult.recommended_stage.title)) {
        $effectiveTitle = [string]$campaignResult.recommended_stage.title
    }
    if (-not [string]::IsNullOrWhiteSpace([string]$campaignResult.reason)) {
        $effectivePurpose = [string]$campaignResult.reason
    }
    if (-not [string]::IsNullOrWhiteSpace([string]$campaignResult.recommended_worker)) {
        $effectiveRecommendedWorker = [string]$campaignResult.recommended_worker
    }
    if (-not [string]::IsNullOrWhiteSpace([string]$campaignResult.recommended_lane)) {
        $effectiveRecommendedLane = [string]$campaignResult.recommended_lane
    }
    if ($effectiveAllowedPaths.Count -eq 0 -and $campaignDetails -and $campaignDetails.allowed_paths) {
        $effectiveAllowedPaths = @($campaignDetails.allowed_paths)
    }
    if ($effectiveBlockedPaths.Count -eq 0 -and $campaignDetails -and $campaignDetails.blocked_paths) {
        $effectiveBlockedPaths = @($campaignDetails.blocked_paths)
    }
    if ($effectiveChangedPaths.Count -eq 0) {
        $effectiveChangedPaths = @($effectiveAllowedPaths)
    }
}

$campaignNextTask = if ($campaignReady -or ($campaignPreview.status -eq "PASS" -and $null -ne $campaignResult)) {
    [pscustomobject]@{
        status = if ($campaignReady) { "AVAILABLE" } else { "REVIEW_REQUIRED" }
        recommended_campaign = $campaignResult.recommended_campaign
        recommended_phase = $campaignResult.recommended_phase
        recommended_stage = $campaignResult.recommended_stage
        next_packet_candidate = $campaignResult.next_packet_candidate
        recommended_worker = $campaignResult.recommended_worker
        recommended_lane = $campaignResult.recommended_lane
        reason = $campaignResult.reason
        blockers = @($campaignResult.blockers)
        overall_readiness = $campaignResult.overall_readiness
    }
}
else {
    [pscustomobject]@{
        status = "UNAVAILABLE"
        recommended_campaign = $null
        recommended_phase = $null
        recommended_stage = $null
        next_packet_candidate = $null
        recommended_worker = $null
        recommended_lane = $null
        reason = "Campaign Registry next-task helper unavailable."
        blockers = @($campaignPreview.error)
        overall_readiness = "UNAVAILABLE"
    }
}

$normalizedAllowedPaths = @($effectiveAllowedPaths | ForEach-Object { ConvertTo-AiOsRepoPath -Path $_ } | Where-Object { $_ })
$normalizedBlockedPaths = @($effectiveBlockedPaths | ForEach-Object { ConvertTo-AiOsRepoPath -Path $_ } | Where-Object { $_ })
$normalizedChangedPaths = @($effectiveChangedPaths | ForEach-Object { ConvertTo-AiOsRepoPath -Path $_ } | Where-Object { $_ })
if ($normalizedChangedPaths.Count -eq 0) {
    $normalizedChangedPaths = @($normalizedAllowedPaths)
}

$helperAllowedPaths = @($normalizedAllowedPaths | Select-Object -First 1)
$helperBlockedPaths = @($normalizedBlockedPaths | Select-Object -First 1)
$helperChangedPaths = @($normalizedChangedPaths | Select-Object -First 1)

$taskArgs = @(
    "-TaskId", $effectiveTaskId,
    "-Title", $effectiveTitle,
    "-Purpose", $effectivePurpose,
    "-Owner", $Owner,
    "-StopPoint", $StopPoint
)
if ($helperAllowedPaths.Count -gt 0) {
    $taskArgs += "-AllowedPaths"
    $taskArgs += $helperAllowedPaths
}
if ($helperBlockedPaths.Count -gt 0) {
    $taskArgs += "-BlockedPaths"
    $taskArgs += $helperBlockedPaths
}

$assignmentArgs = @(
    "-WorkerId", $effectiveRecommendedWorker,
    "-PacketId", $effectivePacketId
)
if ($helperAllowedPaths.Count -gt 0) {
    $assignmentArgs += "-AssignedPaths"
    $assignmentArgs += $helperAllowedPaths
}

$validatorArgs = @()
if ($helperChangedPaths.Count -gt 0) {
    $validatorArgs += "-ChangedPaths"
    $validatorArgs += $helperChangedPaths
}

$dryRunArgs = @(
    "-PacketId", $effectivePacketId,
    "-Summary", "Crew integration recommendation preview.",
    "-RiskLevel", "normal",
    "-StopPoint", $StopPoint
)
if ($helperChangedPaths.Count -gt 0) {
    $dryRunArgs += "-FilesToModify"
    $dryRunArgs += $helperChangedPaths
}

$taskPreview = Invoke-AiOsCrewJsonHelper -Path $taskHelper -HelperArguments $taskArgs
$assignmentPreview = Invoke-AiOsCrewJsonHelper -Path $assignmentHelper -HelperArguments $assignmentArgs
$validatorPreview = Invoke-AiOsCrewJsonHelper -Path $validatorHelper -HelperArguments $validatorArgs
$dryRunPreview = Invoke-AiOsCrewJsonHelper -Path $dryRunResultHelper -HelperArguments $dryRunArgs
$approvalPreview = Invoke-AiOsCrewJsonHelper -Path $approvalSummaryHelper -HelperArguments @("-QuietJson")
$commitPreview = Invoke-AiOsCrewJsonHelper -Path $commitPackageHelper -HelperArguments @("-OutputJson")

$helperResults = @($campaignPreview, $taskPreview, $assignmentPreview, $validatorPreview, $dryRunPreview, $approvalPreview, $commitPreview)
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
        status = "AVAILABLE"
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
        status = if ($commitPreview.status -eq "FAIL") { "UNAVAILABLE_CLEAN_WORKTREE" } else { "UNAVAILABLE" }
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
    if ($commitPreview.status -eq "FAIL" -and $failedHelpers.Count -eq 1) {
        "REVIEW_REQUIRED"
    }
    else {
        "BLOCKED"
    }
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
    campaign_next_task = $campaignNextTask
    packet_summary = [pscustomobject]@{
        task_id = $effectiveTaskId
        packet_id = $effectivePacketId
        title = $effectiveTitle
        purpose = $effectivePurpose
        owner = $Owner
        allowed_paths = @($normalizedAllowedPaths)
        blocked_paths = @($normalizedBlockedPaths)
        changed_paths = @($normalizedChangedPaths)
        stop_point = $StopPoint
    }
    next_packet_candidate = $campaignNextTask.next_packet_candidate
    recommended_worker = $effectiveRecommendedWorker
    recommended_lane = $effectiveRecommendedLane
    recommended_validators = @($validatorPreview.result.recommended_validators)
    approval_state_summary = $approvalStateSummary
    commit_package_preview = $commitPackagePreview
    collision_warning = $collisionWarning
    helper_outputs = [pscustomobject]@{
        campaign_next_task = $campaignResult
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
    next_safe_action = if ($campaignReady -and -not [string]::IsNullOrWhiteSpace([string]$campaignResult.next_safe_action)) { $campaignResult.next_safe_action } else { $nextSafeAction }
    overall_readiness = if ($campaignReady) { $campaignResult.overall_readiness } else { $overallReadiness }
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 16
    exit 0
}

Write-Output ($result | ConvertTo-Json -Depth 16)
