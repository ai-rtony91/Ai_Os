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
    $recommendedCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/approval_processor/Invoke-AiOsApprovalProcessor.DRY_RUN.ps1 -Apply"
    $reason = "Approval exists for waiting packet."
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
