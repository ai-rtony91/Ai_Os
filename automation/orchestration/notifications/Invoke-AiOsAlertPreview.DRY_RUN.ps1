[CmdletBinding()]
param(
    [string]$EventType = "BUILD_PROGRESS",
    [ValidateSet("INFO", "REVIEW", "WARNING", "CRITICAL", "SOS")][string]$Severity = "INFO",
    [string]$Message = "AI_OS alert preview: no live sender is active."
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$typesPath = Join-Path $PSScriptRoot "AIOS_ALERT_EVENT_TYPES.json"
$rulesPath = Join-Path $PSScriptRoot "AIOS_ALERT_ROUTING_RULES.example.json"
$types = Get-Content -Raw -LiteralPath $typesPath | ConvertFrom-Json
$rules = Get-Content -Raw -LiteralPath $rulesPath | ConvertFrom-Json

$type = @($types.event_types | Where-Object { $_.event_type -eq $EventType } | Select-Object -First 1)
if ($type.Count -eq 0) {
    Write-Error "Unknown event type: $EventType"
    exit 1
}

$route = @($rules.routing_table | Where-Object { $_.event_type -eq $EventType } | Select-Object -First 1)
if ($route.Count -eq 0) {
    Write-Error "No route for event type: $EventType"
    exit 1
}

$preview = [ordered]@{
    schema = "AIOS_ALERT_ROUTE_PREVIEW.v1"
    mode = "DRY_RUN"
    event_type = $EventType
    schema_event_type = $type[0].schema_event_type
    severity = $Severity
    message = $Message
    planned_channels = @($route[0].channels_planned)
    voice_text_preview = "AI OS alert preview. $Message"
    screen_preview_text = "[$Severity] $EventType - $Message"
    robot_helper_preview_text = "Robot helper would display: $EventType. Hardware action blocked."
    live_send = "BLOCKED"
    tts = "BLOCKED"
    hardware_action = "BLOCKED"
    delivered = $false
}
$preview | ConvertTo-Json -Depth 8
