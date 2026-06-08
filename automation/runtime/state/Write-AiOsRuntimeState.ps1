param(
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$statePath = "automation/runtime/state/AIOS_RUNTIME_STATE.json"

$recommendation = powershell -ExecutionPolicy Bypass -File automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json
$health = powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json

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
}

$stateDir = Split-Path -Parent $statePath
if (-not [string]::IsNullOrWhiteSpace($stateDir) -and -not (Test-Path -LiteralPath $stateDir -PathType Container)) {
    New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
}
$tmpStatePath = "{0}.{1}.tmp" -f $statePath, ([guid]::NewGuid().ToString("N"))
$state | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $tmpStatePath -Encoding UTF8
Move-Item -LiteralPath $tmpStatePath -Destination $statePath -Force

if ($QuietJson) {
    $state | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AIOS Runtime State"
Write-Host "State path: $statePath"
Write-Host "Health: $($state.health)"
Write-Host "Packet: $($state.packet_id)"
Write-Host "Status: $($state.packet_status)"
Write-Host "Recommended command:"
Write-Host $state.recommended_command
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
