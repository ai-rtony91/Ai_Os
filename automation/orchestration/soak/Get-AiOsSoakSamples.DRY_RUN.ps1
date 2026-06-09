<# 
.SYNOPSIS
Collect a read-only soak harness sample for the observe-only DRY_RUN harness.

.DESCRIPTION
This script reads marker and heartbeat artifacts only and returns a JSON-ready
sample object for the soak harness evidence envelope.

.PARAMETER RepoRoot
Repository root to resolve marker, heartbeat, and stop-marker paths.
#>
[CmdletBinding()]
param(
    [string]$RepoRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
}

$RepoRoot = [string]$RepoRoot
$markerPath = Join-Path $RepoRoot "control\cycle\last_marker.json"
$heartbeatPath = Join-Path $RepoRoot "telemetry\runtime\runtime_heartbeat.json"
$stopMarkerPaths = @(
    "control/self_continuation/STOP",
    "relay/STOP.flag"
)

function Parse-TimestampAsUtc {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $null
    }

    $value = $Value.Trim()
    if ([string]::IsNullOrWhiteSpace($value)) {
        return $null
    }

    try {
        $candidate = [datetime]::Parse($value).ToUniversalTime()
        return $candidate
    } catch {
        return $null
    }
}

function Get-JsonSafe {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    try {
        return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json -ErrorAction Stop
    } catch {
        return $null
    }
}

function Get-StopMarkerState {
    $markers = @()
    foreach ($relative in $stopMarkerPaths) {
        $fullPath = Join-Path $RepoRoot $relative
        $exists = [bool](Test-Path -LiteralPath $fullPath -PathType Leaf)
        if ($exists) {
            $markers += [ordered]@{
                path = $relative
                exists = $true
            }
        }
    }
    return $markers
}

$reasons = @()
$now = (Get-Date).ToUniversalTime()
$markerJson = Get-JsonSafe -Path $markerPath
$heartbeatJson = Get-JsonSafe -Path $heartbeatPath

$markerSnapshot = if ($null -ne $markerJson) {
    $markerJson | ConvertTo-Json -Depth 20
} else {
    $null
}

$heartbeatTimestamp = $null
$heartbeatStalenessSeconds = $null
$heartbeatFreshnessStatus = "MISSING"
$heartbeatExists = [bool]($heartbeatJson -ne $null)

if (-not $heartbeatExists) {
    $reasons += "Heartbeat file missing."
} else {
    $timestampValue = $null
    if ($heartbeatJson.PSObject.Properties.Name -contains "heartbeatAt") {
        $timestampValue = [string]$heartbeatJson.heartbeatAt
    } elseif ($heartbeatJson.PSObject.Properties.Name -contains "last_beat") {
        $timestampValue = [string]$heartbeatJson.last_beat
    }

    if ([string]::IsNullOrWhiteSpace($timestampValue)) {
        $heartbeatFreshnessStatus = "MALFORMED"
        $reasons += "Heartbeat missing heartbeatAt/last_beat timestamp."
    } else {
        $heartbeatParsed = Parse-TimestampAsUtc -Value $timestampValue
        if ($null -eq $heartbeatParsed) {
            $heartbeatFreshnessStatus = "MALFORMED"
            $reasons += "Heartbeat timestamp failed to parse."
            $heartbeatTimestamp = $timestampValue
        } else {
            $heartbeatTimestamp = $heartbeatParsed.ToString("yyyy-MM-ddTHH:mm:ssZ")
            $seconds = [math]::Round(($now - $heartbeatParsed).TotalSeconds, 3)
            $heartbeatStalenessSeconds = $seconds
            if ($seconds -lt 0) {
                $heartbeatFreshnessStatus = "FUTURE"
            } elseif ($seconds -le 600) {
                $heartbeatFreshnessStatus = "FRESH"
            } else {
                $heartbeatFreshnessStatus = "STALE"
            }
        }
    }
}

try {
    $proc = Get-Process -Id $PID -ErrorAction Stop
    $rssMb = [math]::Round($proc.WorkingSet64 / 1MB, 2)
} catch {
    $rssMb = $null
    $reasons += "Could not read current process RSS."
}

$diskSamples = @()
$repoDrive = [IO.Path]::GetPathRoot($RepoRoot).TrimEnd(":\")
if ([string]::IsNullOrWhiteSpace($repoDrive)) {
    $diskSamples += [ordered]@{
        drive = "repo"
        status = "UNDETERMINED"
        free_gb = $null
    }
    $reasons += "Could not resolve repository drive."
} else {
    $driveInfo = Get-PSDrive -Name $repoDrive -ErrorAction SilentlyContinue
    if ($null -eq $driveInfo) {
        $diskSamples += [ordered]@{
            drive = $repoDrive
            status = "MISSING"
            free_gb = $null
        }
        $reasons += "Repository drive not visible in this environment."
    } else {
        $freeGb = [math]::Round([decimal]$driveInfo.Free / 1GB, 3)
        $diskSamples += [ordered]@{
            drive = $repoDrive
            status = "OK"
            free_gb = $freeGb
        }
    }
}

$stopMarkers = Get-StopMarkerState
$stopMarkers = @($stopMarkers)
$stopDetected = $stopMarkers.Count -gt 0
if ($stopDetected) {
    $reasons += "Stop marker detected."
}

$sample = [ordered]@{
    sample_utc = $now.ToString("yyyy-MM-ddTHH:mm:ssZ")
    marker_exists = [bool]($markerJson -ne $null)
    marker_snapshot = if ([string]::IsNullOrWhiteSpace($markerSnapshot)) { $null } else { ConvertFrom-Json $markerSnapshot }
    heartbeat_exists = [bool]$heartbeatExists
    heartbeat_timestamp = $heartbeatTimestamp
    heartbeat_staleness_seconds = $heartbeatStalenessSeconds
    heartbeat_freshness_status = $heartbeatFreshnessStatus
    process_rss_mb = $rssMb
    disk_samples = @($diskSamples)
    stop_marker_detected = [bool]$stopDetected
    reasons = @($reasons)
}

if ($null -ne $heartbeatJson) {
    if ($heartbeatJson.PSObject.Properties.Name -contains "cycle_id") {
        $sample.heartbeat_cycle_id = [string]$heartbeatJson.cycle_id
    }
}

$sample | ConvertTo-Json -Depth 20
