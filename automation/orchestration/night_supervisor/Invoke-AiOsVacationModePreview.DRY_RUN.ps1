[CmdletBinding()]
param(
    [string]$ProfilePath = (Join-Path $PSScriptRoot "AIOS_24H_VACATION_MODE_PROFILE.example.json"),
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

if ($profile.mode -ne "VACATION_24H_PAPER_MODE_PREVIEW") { $errors += "mode must be VACATION_24H_PAPER_MODE_PREVIEW" }
if ([int]$profile.duration_hours -ne 24) { $errors += "duration_hours must equal 24" }
if (-not [bool]$profile.paper_mode_only) { $errors += "paper_mode_only must be true" }
if (-not (Test-PropertyPresent $profile "quiet_hours")) { $errors += "quiet_hours policy is missing" }
if (-not (Test-PropertyPresent $profile "escalation_classes")) { $errors += "escalation_classes are missing" }
if (@($profile.blocks).Count -ne 2) { $errors += "two 12-hour blocks are required" }

$report = [ordered]@{
    schema = "AIOS_24H_VACATION_MODE_PREVIEW.v1"
    mode = "DRY_RUN"
    profile_mode = $profile.mode
    duration_hours = $profile.duration_hours
    blocks = @($profile.blocks)
    quiet_hours = $profile.quiet_hours
    escalation_classes = @($profile.escalation_classes)
    safety_confirmation = [ordered]@{
        paper_mode_only = [bool]$profile.paper_mode_only
        report_only = [bool]$profile.report_only
        no_backtests = [bool]$profile.no_backtesting_execution
        no_data_fetch = [bool]$profile.no_external_data_fetch
        no_scheduler = [bool]$profile.no_scheduler
        writes_performed = $false
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

Write-Host "AI_OS 24H Vacation Mode Preview (DRY_RUN)"
foreach ($block in $profile.blocks) {
    Write-Host ("Block {0}: {1} - {2}" -f $block.block_id, $block.hours, $block.focus)
}
Write-Host ("Quiet hours: {0}-{1}, suppress below {2}" -f $profile.quiet_hours.start_local, $profile.quiet_hours.end_local, $profile.quiet_hours.suppress_below_severity)
Write-Host ("Escalation classes: {0}" -f (($profile.escalation_classes) -join ", "))
Write-Host "Mutation skipped: no files written, no backtests, no data fetch, no scheduler."
