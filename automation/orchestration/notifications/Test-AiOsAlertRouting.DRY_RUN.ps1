[CmdletBinding()]
param([switch]$QuietJson)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$errors = @()

function Add-Error {
    param([string]$Message)
    $script:errors += $Message
}

function Read-Json {
    param([string]$Path)
    return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Test-ParsePowerShell {
    param([string]$Path)
    $lexemes = $null
    $parseErrors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$lexemes, [ref]$parseErrors) | Out-Null
    if ($parseErrors.Count -gt 0) { Add-Error "PowerShell parse failed: $Path" }
}

$typesPath = Join-Path $PSScriptRoot "AIOS_ALERT_EVENT_TYPES.json"
$rulesPath = Join-Path $PSScriptRoot "AIOS_ALERT_ROUTING_RULES.example.json"
$previewPath = Join-Path $PSScriptRoot "Invoke-AiOsAlertPreview.DRY_RUN.ps1"
$types = Read-Json $typesPath
$rules = Read-Json $rulesPath
Test-ParsePowerShell $previewPath

$required = @(
    "AIOS_BLOCKED",
    "APPROVAL_NEEDED",
    "VALIDATION_FAILED",
    "STOP_MARKER_ACTIVE",
    "REPO_DIRTY_UNEXPECTED",
    "SUPERVISOR_STALE",
    "OMEN_UNREACHABLE",
    "PI_HELPER_UNREACHABLE",
    "ALERT_CHANNEL_FAILED",
    "SECRET_RISK_DETECTED",
    "FORBIDDEN_ACTION_REQUESTED",
    "BUILD_PROGRESS",
    "HEARTBEAT",
    "COMPLETE"
)
$actual = @($types.event_types | ForEach-Object { $_.event_type })
foreach ($eventType in $required) {
    if ($actual -notcontains $eventType) { Add-Error "missing event type: $eventType" }
}
foreach ($eventType in $required) {
    if (@($rules.routing_table | Where-Object { $_.event_type -eq $eventType }).Count -eq 0) { Add-Error "missing route: $eventType" }
}

if (-not [bool]$rules.no_real_senders) { Add-Error "no_real_senders must be true" }
if ([bool]$rules.telegram_live_send_enabled) { Add-Error "telegram_live_send_enabled must be false" }
if ([bool]$rules.webhook_live_send_enabled) { Add-Error "webhook_live_send_enabled must be false" }
if ([bool]$rules.hardware_enabled) { Add-Error "hardware_enabled must be false" }
if ([bool]$rules.tts_enabled) { Add-Error "tts_enabled must be false" }

$result = [ordered]@{
    schema = "AIOS_ALERT_ROUTING_TEST.v1"
    mode = "DRY_RUN"
    status = if ($errors.Count -eq 0) { "PASS" } else { "FAIL" }
    errors = $errors
    mutation = "NONE"
}
$result | ConvertTo-Json -Depth 8
if ($errors.Count -gt 0) { exit 1 }
exit 0
