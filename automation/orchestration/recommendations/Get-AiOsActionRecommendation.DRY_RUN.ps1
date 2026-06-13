param(
    [switch]$QuietJson,
    [switch]$OutputJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Get-RelayOperatorState {
    param([string]$RepoRoot)

    $relayOperatorStateScript = Join-Path $RepoRoot "automation/orchestration/review_bridge/Get-AiOsRelayOperatorState.DRY_RUN.ps1"
    if (-not (Test-Path -LiteralPath $relayOperatorStateScript -PathType Leaf)) {
        return $null
    }

    try {
        $rawOutput = powershell -NoProfile -ExecutionPolicy Bypass -File $relayOperatorStateScript -OutputJson 2>$null
        $rawText = ($rawOutput | Out-String).Trim()
        if ([string]::IsNullOrWhiteSpace($rawText)) {
            return $null
        }

        return $rawText | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        return $null
    }
}

$health = powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json
$next = powershell -ExecutionPolicy Bypass -File automation/orchestration/next_step/Resolve-AiOsNextStep.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json
$blocker = powershell -ExecutionPolicy Bypass -File automation/orchestration/blockers/Resolve-AiOsRuntimeBlocker.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json
$approval = powershell -ExecutionPolicy Bypass -File automation/orchestration/approval_detection/Find-AiOsApprovalMatch.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json
$gitStatus = @(git status --short)
$repoRoot = (Get-Location).Path
$relayOperatorState = Get-RelayOperatorState -RepoRoot $repoRoot
$relaySosEscalationStatus = "NOT_APPLICABLE"
$relaySosAnthonyRequired = $false
$relaySosRoutineReviewAllowed = $false
$relaySosSafeNextAction = ""
$relaySosApplies = $false

if ($relayOperatorState -and [string]$relayOperatorState.actor_relay_bus_status -eq "NEEDS_HUMAN_REVIEW") {
    $relaySosApplies = $true
    if ($relayOperatorState.PSObject.Properties.Name -contains "sos_escalation_status") {
        $relaySosEscalationStatus = [string]$relayOperatorState.sos_escalation_status
    }
    if ($relayOperatorState.PSObject.Properties.Name -contains "sos_anthony_required") {
        $relaySosAnthonyRequired = [bool]$relayOperatorState.sos_anthony_required
    }
    if ($relayOperatorState.PSObject.Properties.Name -contains "sos_routine_review_allowed") {
        $relaySosRoutineReviewAllowed = [bool]$relayOperatorState.sos_routine_review_allowed
    }
    if ($relayOperatorState.PSObject.Properties.Name -contains "sos_safe_next_action") {
        $relaySosSafeNextAction = [string]$relayOperatorState.sos_safe_next_action
    }
}
$commitPackagePreview = $null
if ($gitStatus.Count -gt 0) {
    try {
        $commitPackagePreview = powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1 -OutputJson | ConvertFrom-Json
    }
    catch {
        $commitPackagePreview = $null
    }
}

$recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/session/Start-AiOsSession.ps1"
$reason = "Default: start AIOS session."
$level5Validators = @(
    "git diff --check",
    "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-WorkerClaimCollision.DRY_RUN.ps1",
    "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-LockRegistryIntegrity.DRY_RUN.ps1",
    "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1",
    "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1"
)

if ($approval.matches_found -gt 0) {
    $recommendedCommand = "No command recommended. Use separately approved APPLY helper for approval processing."
    $reason = "Approval exists for waiting packet; DRY_RUN cannot process approval."
}
elseif ($next.status -eq "awaiting_approval") {
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/approval_detection/Find-AiOsApprovalMatch.DRY_RUN.ps1"
    $reason = "Packet is waiting for approval."
}
elseif ($gitStatus.Count -gt 0 -and $commitPackagePreview) {
    $recommendedCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1 -OutputJson"
    $reason = "Working tree has changes; prepare an exact-file Level 5 commit package preview and stop before staging."
}
elseif ($health.health -ne "HEALTHY") {
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1"
    $reason = "Health is not clean."
}
elseif ($next.status -eq "blocked" -or $next.status -eq "failed") {
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/blockers/Resolve-AiOsRuntimeBlocker.DRY_RUN.ps1"
    $reason = "Packet needs blocker/failure review."
}
elseif ($next.status -eq "campaign_ready") {
    $recommendedCommand = "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1 -OutputJson"
    $reason = "No active packet is present; campaign registry has a READY packet candidate."
}
elseif ($next.status -eq "no_active_packet") {
    $recommendedCommand = "No command recommended. Review campaign registry statuses and approve one next packet candidate."
    $reason = "No active packet and no READY campaign stage are available for automatic advancement."
}
else {
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/advancement/Invoke-AiOsPacketAdvancement.DRY_RUN.ps1"
    $reason = "Packet can continue normal advancement."
}

if ($relaySosApplies -and $relaySosEscalationStatus -eq "ROUTINE_REVIEW") {
    $reason = "Routine relay review may continue through resolver and SOS-governed path."
}
elseif ($relaySosApplies -and $relaySosEscalationStatus -eq "SOS_ESCALATION") {
    $recommendedCommand = "No command recommended. STOP and request Anthony review before any continuation."
    $reason = "Relay SOS escalation requires Anthony; do not continue automatically."
}

$commitPackageChangedFiles = @()
$commitPackageRecommendedFiles = @()
$commitPackageRiskFlags = @()
if ($commitPackagePreview) {
    $commitPackageChangedFiles = @(
        @($commitPackagePreview.changed_files)
        @($commitPackagePreview.new_files)
    ) | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | Sort-Object -Unique
    $commitPackageRecommendedFiles = @($commitPackagePreview.recommended_files | ForEach-Object { [string]$_.path } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique)
    $commitPackageRiskFlags = @($commitPackagePreview.risks | ForEach-Object {
        if ($_.path -and $_.risk) {
            "$($_.path): $($_.risk)"
        } else {
            [string]$_
        }
    } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
}

$result = [pscustomobject]@{
    mode = "READ_ONLY"
    recommended_command = $recommendedCommand
    relay_sos_escalation_status = $relaySosEscalationStatus
    relay_sos_anthony_required = $relaySosAnthonyRequired
    relay_sos_routine_review_allowed = $relaySosRoutineReviewAllowed
    relay_sos_next_safe_action = if ($relaySosSafeNextAction) { $relaySosSafeNextAction } else { "" }
    reason = $reason
    health = $health.health
    packet_id = $next.packet_id
    packet_status = $next.status
    approval_matches = $approval.matches_found
    blocker = $blocker.blocker
    level5_commit_package_preview = [pscustomobject]@{
        available = [bool]($null -ne $commitPackagePreview)
        status = if ($commitPackagePreview -and $commitPackagePreview.orchestration_result_contract.status) { [string]$commitPackagePreview.orchestration_result_contract.status } elseif ($gitStatus.Count -gt 0) { "REVIEW" } else { "NOT_NEEDED" }
        command = "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1 -OutputJson"
        exact_changed_files = @($commitPackageChangedFiles)
        recommended_files = @($commitPackageRecommendedFiles)
        suggested_validators = @($level5Validators)
        risk_flags = @($commitPackageRiskFlags)
        stop_before_staging = "STOP: preview only. Do not run git add, git commit, git push, PR, or merge without separate explicit approval."
    }
}

$approvalRequired = ($approval.matches_found -gt 0 -or $next.status -eq "awaiting_approval" -or $commitPackagePreview)
if ($relaySosApplies -and $relaySosEscalationStatus -eq "SOS_ESCALATION") {
    $approvalRequired = $true
}
$blockedReason = if ($gitStatus.Count -gt 0 -and $commitPackagePreview) { "none" } elseif ($health.health -ne "HEALTHY") { "Runtime health is not clean." } elseif ($next.status -eq "blocked" -or $next.status -eq "failed") { "Packet is blocked or failed." } elseif ($next.status -eq "no_active_packet") { "No active packet or READY campaign stage is available." } else { "none" }
$status = if ($blockedReason -ne "none") { "BLOCKED" } elseif ($approvalRequired) { "REVIEW" } else { "READY" }
$nextSafeAction = $recommendedCommand
if ($relaySosApplies -and $relaySosEscalationStatus -eq "ROUTINE_REVIEW") {
    $nextSafeAction = if ($relaySosSafeNextAction) { $relaySosSafeNextAction } else { "Continue through resolver and SOS-governed routine review flow." }
}
elseif ($relaySosApplies -and $relaySosEscalationStatus -eq "SOS_ESCALATION") {
    $nextSafeAction = "STOP and request Anthony review before continuation."
}
$result | Add-Member -NotePropertyName orchestration_result_contract -NotePropertyValue ([pscustomobject]@{
    status = $status
    severity = if ($status -eq "BLOCKED") { "BLOCKED" } elseif ($status -eq "REVIEW") { "REVIEW" } else { "INFO" }
    packet_id = if ($next.packet_id) { [string]$next.packet_id } else { "UNKNOWN" }
    worker_identity = "UNKNOWN"
    validator_results = @()
    approval_required = $approvalRequired
    blocked_reason = $blockedReason
    escalation_reason = if ($approvalRequired) { "Approval evidence requires Human Owner review." } elseif ($blockedReason -ne "none") { $blockedReason } else { "none" }
    commit_candidate = [bool]($commitPackagePreview)
    next_safe_action = $nextSafeAction
    stop_condition = "REPORT_ONLY_NO_PACKET_ADVANCEMENT"
    runtime_notes = @(
        "READ_ONLY",
        "Recommendation only.",
        "No packet advancement, APPLY, commit, or push was performed."
    )
    evidence = [pscustomobject]@{
        health = $health.health
        packet_status = $next.status
        approval_matches = $approval.matches_found
        blocker = $blocker.blocker
        reason = $reason
        level5_commit_package_preview = $result.level5_commit_package_preview
    }
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
})

if ($QuietJson -or $OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "COPY START - Get-AiOsActionRecommendation.DRY_RUN.ps1"
Write-Host "AI_OS Action Recommendation" -ForegroundColor Cyan
Write-Host "health: $($result.health)"
Write-Host "packet_id: $($result.packet_id)"
Write-Host "packet_status: $($result.packet_status)"
Write-Host "approval_matches: $($result.approval_matches)"
Write-Host "reason: $($result.reason)"
Write-Host "level5_commit_package_preview: available=$($result.level5_commit_package_preview.available); status=$($result.level5_commit_package_preview.status)"
Write-Host "level5_stop: $($result.level5_commit_package_preview.stop_before_staging)"
Write-Host ""
Write-Host "RECOMMENDED COMMAND:"
Write-Host $result.recommended_command
Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Get-AiOsActionRecommendation.DRY_RUN.ps1"
