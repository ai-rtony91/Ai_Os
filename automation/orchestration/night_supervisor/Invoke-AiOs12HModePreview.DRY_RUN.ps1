[CmdletBinding()]
param(
    [string]$ProfilePath = (Join-Path $PSScriptRoot "AIOS_12H_MODE_PROFILE.example.json"),
    [switch]$QuietJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-PropertyPresent {
    param([object]$InputObject, [string]$Name)
    return $null -ne $InputObject.PSObject.Properties[$Name]
}

$profile = Get-Content -Raw -LiteralPath $ProfilePath | ConvertFrom-Json
$errors = @()

if ($profile.mode -ne "REPORT_ONLY_BUILD_PREP") { $errors += "mode must be REPORT_ONLY_BUILD_PREP" }
if ([int]$profile.duration_hours -ne 12) { $errors += "duration_hours must equal 12" }
if (-not (Test-PropertyPresent $profile "stop_marker_required")) { $errors += "stop_marker_required is missing" }
if (-not (Test-PropertyPresent $profile "blocked_actions") -or @($profile.blocked_actions).Count -eq 0) { $errors += "blocked_actions are missing" }
if (@($profile.hourly_focus).Count -ne 12) { $errors += "hourly_focus must contain 12 entries" }

$report = [ordered]@{
    schema = "AIOS_12H_MODE_PREVIEW.v1"
    mode = "DRY_RUN"
    profile_mode = $profile.mode
    duration_hours = $profile.duration_hours
    max_cycles = $profile.max_cycles
    planned_sequence = @($profile.hourly_focus)
    safety_confirmation = [ordered]@{
        paper_mode_only = [bool]$profile.paper_mode_only
        no_executor = [bool]$profile.no_executor
        no_scheduler = [bool]$profile.no_scheduler
        no_hardware = [bool]$profile.no_hardware
        no_real_senders = [bool]$profile.no_real_senders
        no_commit_push_merge = [bool]$profile.no_commit_push_merge
        writes_performed = $false
        workers_launched = $false
    }
    errors = $errors
}

if ($errors.Count -gt 0) {
    $report | ConvertTo-Json -Depth 8
    exit 1
}

if ($QuietJson) {
    $report | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS 12H Mode Preview (DRY_RUN)"
foreach ($item in $profile.hourly_focus) {
    Write-Host ("Hour {0}: {1}" -f $item.hour, $item.focus)
}
Write-Host "Safety: paper-only, no executor, no scheduler, no hardware, no real senders."
Write-Host "Mutation skipped: no files written and no workers launched."
