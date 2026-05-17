param(
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$statePath = "automation/runtime/state/AIOS_RUNTIME_STATE.json"

$recommendation = powershell -ExecutionPolicy Bypass -File automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json
$health = powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json
$nextCommand = powershell -ExecutionPolicy Bypass -File automation/runtime/recommendation/Get-AiOsNextCommand.ps1 -QuietJson | ConvertFrom-Json

$state = [ordered]@{
    mode = "READ_ONLY"
    updated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    health = $health.health
    packet_id = $recommendation.packet_id
    packet_status = $recommendation.packet_status
    recommended_command = $recommendation.recommended_command
    reason = $recommendation.reason
    blocker = $recommendation.blocker
    approval_matches = $recommendation.approval_matches
    safety = "repo_scoped_only_no_live_trading_no_secrets_no_broker"
    operator_summary = "Health: $($health.health). Packet: $($recommendation.packet_id) [$($recommendation.packet_status)]. Next: $($nextCommand.next_best_step)"
    next_best_step = $nextCommand.next_best_step
    fatigue_reduction_target = "Reduce repeated manual checks across git status, packet state, runtime state, and validators."
    automation_candidate = $(if ($nextCommand.why) { $nextCommand.why } else { "Generate repo status and next-command guidance from runtime state." })
    manual_work_removed = $(if ($nextCommand.manual_work_removed) { $nextCommand.manual_work_removed } else { "Manual runtime triage." })
}

$state | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $statePath -Encoding UTF8

if ($QuietJson) {
    $state | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AIOS Runtime State"
Write-Host "State path: $statePath"
Write-Host "Health: $($state.health)"
Write-Host "Packet: $($state.packet_id)"
Write-Host "Status: $($state.packet_status)"
Write-Host "Operator summary: $($state.operator_summary)"
Write-Host "Next best step: $($state.next_best_step)"
Write-Host "Recommended command:"
Write-Host $state.recommended_command
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
