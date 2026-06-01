[CmdletBinding()]
param(
    [string]$MarkerPath = "control/cycle/last_marker.json",
    [switch]$Apply
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$resolvedMarker = if ([System.IO.Path]::IsPathRooted($MarkerPath)) { $MarkerPath } else { Join-Path $repoRoot $MarkerPath }

if (-not (Test-Path -LiteralPath $resolvedMarker -PathType Leaf)) {
    Write-Host "NO_PRIOR_CYCLE_MARKER"
    exit 0
}

$marker = Get-Content -Raw -LiteralPath $resolvedMarker | ConvertFrom-Json
if (-not [bool]$marker.cycle_in_progress) {
    Write-Host "LAST_CYCLE_COMPLETE_NOTHING_TO_RESUME"
    exit 0
}

$phases = @()
if ($null -ne $marker.phases) {
    $phases = @($marker.phases | ForEach-Object { [string]$_.name })
}
if ($phases.Count -eq 0) {
    $phases = @(
        "hygiene",
        "clear-stale-approvals",
        "pull-backlog",
        "relay-runner",
        "approval-resume",
        "self-continuation",
        "autonomy-bridge",
        "morning-brief",
        "sos-file-notifier",
        "pr-watch"
    )
}

$completed = @()
if ($null -ne $marker.completed_phases) {
    $completed = @($marker.completed_phases | ForEach-Object { [string]$_ })
}

$resumeFrom = $null
foreach ($phase in $phases) {
    if ($completed -notcontains $phase) {
        $resumeFrom = $phase
        break
    }
}
if ([string]::IsNullOrWhiteSpace($resumeFrom)) {
    $resumeFrom = $phases[-1]
}

$cycleId = if ($null -ne $marker.cycle_id) { [string]$marker.cycle_id } else { "UNKNOWN" }
Write-Host ("RESUMING_FROM phase={0} cycle_id={1}" -f $resumeFrom, $cycleId)

if ($Apply) {
    $nightCycle = Join-Path $repoRoot "automation\orchestration\Invoke-AiOsNightCycle.ps1"
    & $nightCycle -ResumeFrom $resumeFrom -Apply
}
