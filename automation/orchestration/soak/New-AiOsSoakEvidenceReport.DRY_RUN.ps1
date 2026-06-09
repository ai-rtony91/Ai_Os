<# 
.SYNOPSIS
Convert AI_OS soak evidence JSON into a Markdown report for DRY_RUN review.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$InputEvidencePath,

    [string]$EvidenceRoot = "telemetry/soak",
    [string]$ReportRoot = "Reports/endurance_soak"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = [string](Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$AllowedWritableRoots = @("telemetry/soak", "Reports/endurance_soak")

function Normalize-PathForCompare {
    param([Parameter(Mandatory = $true)][string]$Value)
    $normalized = [string]$Value
    $normalized = $normalized.Replace("\", "/").Trim()
    return $normalized
}

function Assert-WritableRoot {
    param([Parameter(Mandatory = $true)][string]$Path)
    $normalized = Normalize-PathForCompare -Value $Path
    if ($normalized -notmatch "^(?i)(telemetry/soak|Reports/endurance_soak)($|/.*)") {
        throw "SOAK_REPORT_ROOT_GUARD_BLOCKED: only telemetry/soak and Reports/endurance_soak are allowed, got '$Path'."
    }
}

function Write-TextAtomic {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Text
    )

    $directory = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $directory -PathType Container)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }

    $leaf = Split-Path -Leaf $Path
    $tmpPath = Join-Path $directory ("{0}.{1}.tmp" -f $leaf, [Guid]::NewGuid().ToString("N"))
    try {
        $encoding = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($tmpPath, $Text, $encoding)
        Move-Item -LiteralPath $tmpPath -Destination $Path -Force
    } catch {
        if (Test-Path -LiteralPath $tmpPath) {
            Remove-Item -LiteralPath $tmpPath -Force
        }
        throw "SOAK_REPORT_ATOMIC_WRITE_FAILED: $($_.Exception.Message)"
    }
}

function Read-Evidence {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "SOAK_EVIDENCE_MISSING: $Path"
    }
    try {
        $raw = Get-Content -Raw -LiteralPath $Path
        return $raw | ConvertFrom-Json -ErrorAction Stop
    } catch {
        throw "SOAK_EVIDENCE_JSON_PARSE_FAILED: $($_.Exception.Message)"
    }
}

function Aggregate-DiskSummary {
    param($Samples)

    if (-not $Samples) {
        return "No disk sample data."
    }

    $latest = $Samples[-1]
    $summaries = @()
    foreach ($sample in $Samples) {
        if (-not ($sample.disk_samples)) {
            continue
        }
        foreach ($disk in $sample.disk_samples) {
            $summaries += [string]$disk.drive
        }
    }

    if ($summaries.Count -eq 0) {
        return "No disk samples collected."
    }

    $uniq = $summaries | Select-Object -Unique
    return "Latest drives: $($uniq -join ', ')"
}

Assert-WritableRoot -Path $EvidenceRoot
Assert-WritableRoot -Path $ReportRoot

$evidence = Read-Evidence -Path $InputEvidencePath
$samples = @($evidence.samples)
$runId = if ($evidence.run_id) { [string]$evidence.run_id } else { "soak_unknown" }

$reportDir = Join-Path $RepoRoot $ReportRoot
$reportPath = Join-Path $reportDir ("soak_run_{0}.md" -f ($runId.Replace(":", "").Replace("/", "_")))

$sampleCount = $samples.Count
$latest = if ($sampleCount -gt 0) { $samples[-1] } else { $null }
$markerSummary = if ($latest -and $latest.PSObject.Properties.Name -contains "marker_exists") {
    if ($latest.marker_exists) { "Marker present." } else { "Marker not present." }
} else {
    "Marker not sampled."
}
$heartbeatSummary = if ($latest -and $latest.PSObject.Properties.Name -contains "heartbeat_freshness_status") {
    if ($latest.heartbeat_exists) {
        "Freshness={0}, staleness={1}s, timestamp={2}" -f $latest.heartbeat_freshness_status, $latest.heartbeat_staleness_seconds, $latest.heartbeat_timestamp
    } else {
        "Heartbeat missing."
    }
} else {
    "Heartbeat not sampled."
}
$memorySummary = if ($latest -and $latest.PSObject.Properties.Name -contains "process_rss_mb") {
    "Latest process RSS={0} MB." -f $latest.process_rss_mb
} else {
    "Memory sample missing."
}
$diskSummary = Aggregate-DiskSummary -Samples $samples
$stopSummary = if (($samples | Where-Object { $_.stop_marker_detected }) -or $evidence.status -eq "STOPPED") { "STOP detected." } else { "No STOP marker detected." }
$forbidden = if ($evidence.forbidden_actions_confirmed) { $evidence.forbidden_actions_confirmed } else { @{} }
$forbiddenLines = @()
foreach ($kvp in $forbidden.PSObject.Properties) {
    $forbiddenLines += "- {0}: {1}" -f $kvp.Name, $kvp.Value
}
if ($forbiddenLines.Count -eq 0) {
    $forbiddenLines += "- (no forbidden action confirmations were recorded)"
}

$reasons = if ($evidence.reasons) { $evidence.reasons } else { @("No reasons recorded.") }

$reportLines = @()
$reportLines += "# Soak Harness DRY_RUN Report"
$reportLines += ""
$reportLines += "## Run Overview"
$reportLines += "- Run ID: $($evidence.run_id)"
$reportLines += "- Mode: $($evidence.run_mode)"
$reportLines += "- Status: $($evidence.status)"
$reportLines += "- Packet ID: $($evidence.packet_id)"
$reportLines += "- Started: $($evidence.started_utc)"
$reportLines += "- Completed: $($evidence.completed_utc)"
$reportLines += "- Sample Count: $sampleCount"
$reportLines += ""
$reportLines += "## Marker Summary"
$reportLines += "- $markerSummary"
$reportLines += ""
$reportLines += "## Heartbeat Summary"
$reportLines += "- $heartbeatSummary"
$reportLines += ""
$reportLines += "## Memory Summary"
$reportLines += "- $memorySummary"
$reportLines += ""
$reportLines += "## Disk Summary"
$reportLines += "- $diskSummary"
$reportLines += ""
$reportLines += "## STOP Status"
$reportLines += "- $stopSummary"
$reportLines += ""
$reportLines += "## Forbidden Action Confirmation"
$reportLines += $forbiddenLines
$reportLines += ""
$reportLines += "## Failure Reasons"
foreach ($reason in $reasons) {
    $reportLines += "- $reason"
}
$reportLines += ""
$reportLines += "## Writable Evidence Roots"
$reportLines += "- telemetry/soak"
$reportLines += "- Reports/endurance_soak"
$reportLines += ""
$reportLines += "## Human Review Notes"
$reportLines += "- This report is DRY_RUN-only and does not approve runtime action."

Write-TextAtomic -Path $reportPath -Text ($reportLines -join "`r`n")
Write-Output $reportPath
