<# 
.SYNOPSIS
Run an observe-only DRY_RUN soak sampling harness.

.DESCRIPTION
Collects one or more evidence samples without mutating runtime marker or heartbeat
artifacts. This first version is bounded to a single cycle and supports only
machine-safe DRY_RUN soak sampling.

.PARAMETER MaxCycles
Maximum sample cycles to run. This first version only allows 1.

.PARAMETER IntervalSeconds
Minimum enforced interval between cycles, in seconds.

.PARAMETER RunTimeoutSeconds
Hard timeout for the entire run, in seconds.

.PARAMETER RunMode
Run mode label for emitted evidence.

.PARAMETER EvidenceRoot
Writable evidence root relative to repository root.

.PARAMETER ReportRoot
Writable report root relative to repository root.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [int]$MaxCycles = 1,

    [Parameter(Mandatory = $false)]
    [int]$IntervalSeconds = 30,

    [Parameter(Mandatory = $false)]
    [int]$RunTimeoutSeconds = 600,

    [Parameter(Mandatory = $false)]
    [string]$RunMode = "SOAK_DRY_RUN",

    [Parameter(Mandatory = $false)]
    [string]$EvidenceRoot = "telemetry/soak",

    [Parameter(Mandatory = $false)]
    [string]$ReportRoot = "Reports/endurance_soak"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = [string](Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$GetSampleScript = Join-Path $RepoRoot "automation/orchestration/soak/Get-AiOsSoakSamples.DRY_RUN.ps1"
$ReportScript = Join-Path $RepoRoot "automation/orchestration/soak/New-AiOsSoakEvidenceReport.DRY_RUN.ps1"
$AllowedWritableRoots = @("telemetry/soak", "Reports/endurance_soak")
$StopMarkerPaths = @("control/self_continuation/STOP", "relay/STOP.flag")
$PacketId = "AIOS-SOAK-HARNESS-OBSERVE-ONLY-LOCAL-APPLY-V1"

function Normalize-PathForCompare {
    param([Parameter(Mandatory = $true)][string]$Value)
    $normalized = [string]$Value
    $normalized = $normalized.Replace("\", "/").Trim()
    if ([string]::IsNullOrWhiteSpace($normalized)) {
        return ""
    }
    return $normalized
}

function Assert-WritableRoot {
    param([Parameter(Mandatory = $true)][string]$Path)
    $normalized = Normalize-PathForCompare -Value $Path
    if ($normalized -notmatch "^(?i)(telemetry/soak|Reports/endurance_soak)($|/.*)") {
        throw "SOAK_DRY_RUN_FORBIDDEN_ROOT: only telemetry/soak and Reports/endurance_soak are allowed, got '$Path'."
    }
}

function Write-AiOsJsonAtomic {
    param(
        [Parameter(Mandatory = $true)] $Data,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $directory = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $directory -PathType Container)) {
        New-Item -ItemType Directory -Path $directory -Force | Out-Null
    }

    $leaf = Split-Path -Leaf $Path
    $tmpPath = Join-Path $directory ("{0}.{1}.tmp" -f $leaf, [Guid]::NewGuid().ToString("N"))

    try {
        $json = $Data | ConvertTo-Json -Depth 30
        $encoding = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($tmpPath, $json, $encoding)
        [void](Get-Content -Raw -LiteralPath $tmpPath | ConvertFrom-Json)
        Move-Item -LiteralPath $tmpPath -Destination $Path -Force
    } catch {
        if (Test-Path -LiteralPath $tmpPath) {
            Remove-Item -LiteralPath $tmpPath -Force
        }
        throw "SOAK_DRY_RUN_ATOMIC_WRITE_FAILED: $($_.Exception.Message)"
    }
}

function Get-StopMarkerState {
    param([Parameter(Mandatory = $true)][string]$RepoRootPath)

    $markers = @()
    foreach ($relative in $StopMarkerPaths) {
        $markerPath = Join-Path $RepoRootPath $relative
        if (Test-Path -LiteralPath $markerPath -PathType Leaf) {
            $markers += $relative
        }
    }
    return [ordered]@{
        stop_marker_detected = [bool]($markers.Count -gt 0)
        markers = @($markers)
    }
}

function Get-SoakSample {
    param([Parameter(Mandatory = $true)][string]$RepoRootPath)

    try {
        $sampleRaw = & $GetSampleScript -RepoRoot $RepoRootPath
    } catch {
        throw "SOAK_DRY_RUN_SAMPLE_FAILED: $($_.Exception.Message)"
    }
    try {
        return $sampleRaw | ConvertFrom-Json -ErrorAction Stop
    } catch {
        throw "SOAK_DRY_RUN_SAMPLE_JSON_PARSE_FAILED: $($_.Exception.Message)"
    }
}

function Invoke-AiOsSoakHarnessFinalize {
    param(
        [Parameter(Mandatory = $true)] $Evidence,
        [Parameter(Mandatory = $true)][string]$EvidencePath,
        [Parameter(Mandatory = $true)][string]$ReportPath
    )

    $output = [ordered]@{
        packet_id = $Evidence.packet_id
        run_id = $Evidence.run_id
        run_mode = $Evidence.run_mode
        status = $Evidence.status
        started_utc = $Evidence.started_utc
        completed_utc = $Evidence.completed_utc
        max_cycles = $Evidence.max_cycles
        interval_seconds = $Evidence.interval_seconds
        run_timeout_seconds = $Evidence.run_timeout_seconds
        samples = @($Evidence.samples)
        sample_count = $Evidence.sample_count
        forbidden_actions_confirmed = $Evidence.forbidden_actions_confirmed
        writable_roots = @($Evidence.writable_roots)
        reasons = @($Evidence.reasons)
    }
    Write-AiOsJsonAtomic -Data $output -Path $EvidencePath
    Write-AiOsJsonAtomic -Data $output -Path $EvidenceLatestPath

    $reportRaw = & $ReportScript -InputEvidencePath $EvidencePath -EvidenceRoot $EvidenceRoot -ReportRoot $ReportRoot
    return [ordered]@{
        evidence_path = $EvidencePath
        latest_path = $EvidenceLatestPath
        report_path = $reportRaw
    }
}

$results = [ordered]@{
    packet_id = $PacketId
    status = "PASS"
    run_id = ""
    run_mode = $RunMode
    started_utc = ""
    completed_utc = ""
    max_cycles = $MaxCycles
    interval_seconds = $IntervalSeconds
    run_timeout_seconds = $RunTimeoutSeconds
    samples = @()
    sample_count = 0
    forbidden_actions_confirmed = [ordered]@{
        scheduler_registration = $true
        worker_launch = $true
        outbound_notification = $true
        control_marker_mutation = $true
        runtime_heartbeat_mutation = $true
    }
    writable_roots = @("telemetry/soak", "Reports/endurance_soak")
    reasons = @()
}

$startedUtc = Get-Date
$startedUtc = $startedUtc.ToUniversalTime()
$results.started_utc = $startedUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")
$deadline = $startedUtc.AddSeconds($RunTimeoutSeconds)
$runStamp = $startedUtc.ToString("yyyyMMdd_HHmmssZ")
$runStamp = $runStamp.Replace(":", "")
$runId = "soak_run_$runStamp"
$results.run_id = $runId
$evidenceDir = Join-Path $RepoRoot $EvidenceRoot
$reportDir = Join-Path $RepoRoot $ReportRoot

try {
    Assert-WritableRoot -Path $EvidenceRoot
    Assert-WritableRoot -Path $ReportRoot
    if ($MaxCycles -gt 1) {
        throw "SOAK_DRY_RUN_SCOPE_BLOCKED: MaxCycles greater than 1 is rejected for first packet."
    }
    if ($MaxCycles -lt 1) {
        throw "SOAK_DRY_RUN_SCOPE_BLOCKED: MaxCycles must be at least 1."
    }
    if ($IntervalSeconds -lt 30) {
        throw "SOAK_DRY_RUN_SCOPE_BLOCKED: IntervalSeconds is below minimum 30."
    }
    if ($RunTimeoutSeconds -lt 1) {
        throw "SOAK_DRY_RUN_SCOPE_BLOCKED: RunTimeoutSeconds must be at least 1."
    }

    for ($i = 0; $i -lt $MaxCycles; $i++) {
        if ((Get-Date).ToUniversalTime() -gt $deadline) {
            $results.status = "FAILED"
            $results.reasons += "Run timeout reached before sample collection."
            break
        }

        $stopState = Get-StopMarkerState -RepoRootPath $RepoRoot
        if ($stopState.stop_marker_detected) {
            if ($results.samples.Count -eq 0) {
                $results.reasons += "STOP marker detected before run started."
            } else {
                $results.reasons += "STOP marker detected before sample cycle."
            }
            $results.status = "STOPPED"
            $results.samples += Get-SoakSample -RepoRootPath $RepoRoot
        } else {
            $results.samples += Get-SoakSample -RepoRootPath $RepoRoot
        }

        $results.sample_count = $results.samples.Count
        if (($results.sample_count -eq 0) -and $results.status -eq "PASS") {
            $results.status = "FAILED"
            $results.reasons += "No samples were collected."
        }

        if ($results.samples.Count -gt 0 -and $results.samples[-1].stop_marker_detected) {
            $results.status = "STOPPED"
            if (-not ($results.reasons | Where-Object { $_ -like "*STOP marker detected*" })) {
                $results.reasons += "STOP marker detected in sample payload."
            }
        }

        if ($results.status -in @("STOPPED","FAILED","BLOCKED")) {
            break
        }

        if ($i -lt ($MaxCycles - 1)) {
            $now = (Get-Date).ToUniversalTime()
            $secondsRemaining = [math]::Max(0, ($deadline - $now).TotalSeconds)
            if ($secondsRemaining -le 0) {
                $results.status = "FAILED"
                $results.reasons += "Run timeout reached before interval sleep completed."
                break
            }

            $sleepSeconds = [math]::Min($IntervalSeconds, $secondsRemaining)
            if ($sleepSeconds -gt 0) {
                Start-Sleep -Seconds $sleepSeconds
            } else {
                $results.status = "FAILED"
                $results.reasons += "Run timeout reached while preparing interval wait."
                break
            }
        }
    }

    if ($results.samples.Count -eq 0 -and $results.reasons.Count -eq 0) {
        $results.status = "FAILED"
        $results.reasons += "No evidence samples were produced."
    }
} catch {
    $results.status = "BLOCKED"
    $results.reasons += $_.ToString()
}

$results.completed_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$EvidenceFilePath = Join-Path $evidenceDir ("soak_run_{0}.json" -f $runStamp)
$EvidenceLatestPath = Join-Path $evidenceDir "soak_run_latest.json"

try {
    New-Item -ItemType Directory -Path $evidenceDir -Force | Out-Null
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
    $artifactPaths = Invoke-AiOsSoakHarnessFinalize -Evidence $results -EvidencePath $EvidenceFilePath -ReportPath "unused"
    $results.report_path = $artifactPaths.report_path
    $results.evidence_path = $artifactPaths.evidence_path
    $results.evidence_latest_path = $artifactPaths.latest_path
} catch {
    $results.status = "FAILED"
    $results.reasons += "Evidence/report write failed: $($_.Exception.Message)"
}

$results | ConvertTo-Json -Depth 30
