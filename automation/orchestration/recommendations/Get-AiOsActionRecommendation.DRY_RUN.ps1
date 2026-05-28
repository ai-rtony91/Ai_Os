param(
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$health = powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json
$next = powershell -ExecutionPolicy Bypass -File automation/orchestration/next_step/Resolve-AiOsNextStep.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json
$blocker = powershell -ExecutionPolicy Bypass -File automation/orchestration/blockers/Resolve-AiOsRuntimeBlocker.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json
$approval = powershell -ExecutionPolicy Bypass -File automation/orchestration/approval_detection/Find-AiOsApprovalMatch.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json

$recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/session/Start-AiOsSession.ps1"
$reason = "Default: start AIOS session."

if ($health.health -ne "HEALTHY") {
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1"
    $reason = "Health is not clean."
}
elseif ($approval.matches_found -gt 0) {
    $recommendedCommand = "No command recommended. Use separately approved APPLY helper for approval processing."
    $reason = "Approval exists for waiting packet; DRY_RUN cannot process approval."
}
elseif ($next.status -eq "awaiting_approval") {
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/approval_detection/Find-AiOsApprovalMatch.DRY_RUN.ps1"
    $reason = "Packet is waiting for approval."
}
elseif ($next.status -eq "blocked" -or $next.status -eq "failed") {
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/blockers/Resolve-AiOsRuntimeBlocker.DRY_RUN.ps1"
    $reason = "Packet needs blocker/failure review."
}
else {
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/advancement/Invoke-AiOsPacketAdvancement.DRY_RUN.ps1"
    $reason = "Packet can continue normal advancement."
}

$result = [pscustomobject]@{
    mode = "READ_ONLY"
    recommended_command = $recommendedCommand
    reason = $reason
    health = $health.health
    packet_id = $next.packet_id
    packet_status = $next.status
    approval_matches = $approval.matches_found
    blocker = $blocker.blocker
}

$approvalRequired = ($approval.matches_found -gt 0 -or $next.status -eq "awaiting_approval")
$blockedReason = if ($health.health -ne "HEALTHY") { "Runtime health is not clean." } elseif ($next.status -eq "blocked" -or $next.status -eq "failed") { "Packet is blocked or failed." } else { "none" }
$status = if ($blockedReason -ne "none") { "BLOCKED" } elseif ($approvalRequired) { "REVIEW" } else { "READY" }
$result | Add-Member -NotePropertyName orchestration_result_contract -NotePropertyValue ([pscustomobject]@{
    status = $status
    severity = if ($status -eq "BLOCKED") { "BLOCKED" } elseif ($status -eq "REVIEW") { "REVIEW" } else { "INFO" }
    packet_id = if ($next.packet_id) { [string]$next.packet_id } else { "UNKNOWN" }
    worker_identity = "UNKNOWN"
    validator_results = @()
    approval_required = $approvalRequired
    blocked_reason = $blockedReason
    escalation_reason = if ($approvalRequired) { "Approval evidence requires Human Owner review." } elseif ($blockedReason -ne "none") { $blockedReason } else { "none" }
    commit_candidate = $false
    next_safe_action = $recommendedCommand
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
    }
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
})

if ($QuietJson) {
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
Write-Host ""
Write-Host "RECOMMENDED COMMAND:"
Write-Host $result.recommended_command
Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Get-AiOsActionRecommendation.DRY_RUN.ps1"
