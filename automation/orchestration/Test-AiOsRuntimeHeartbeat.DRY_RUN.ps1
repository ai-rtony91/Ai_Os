<#
.SYNOPSIS
Proves the AI_OS runtime heartbeat JSON contract without running the night cycle.

.DESCRIPTION
This DRY_RUN-only harness writes a sample runtime heartbeat to a temp/test path
using a GUID-suffixed temp file and Move-Item -Force. It does not call or
dot-source Invoke-AiOsNightCycle.ps1, does not run child runtime steps, does not
register schedulers, does not arm restart behavior, and does not send alerts.
#>

[CmdletBinding()]
param(
    [string]$OutputPath = "",
    [string]$CycleId = "",
    [string]$PhaseName = "heartbeat-proof",
    [switch]$QuietJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $proofDir = Join-Path ([System.IO.Path]::GetTempPath()) "AIOS_HEARTBEAT_PROOF"
    $OutputPath = Join-Path $proofDir "runtime_heartbeat.proof.json"
}

if ([string]::IsNullOrWhiteSpace($CycleId)) {
    $CycleId = "HEARTBEAT-PROOF-{0}" -f ([guid]::NewGuid().ToString())
}

function Get-AiOsProofUtc {
    return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function Write-AiOsProofJsonAtomic {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Data
    )

    $targetDir = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $targetDir -PathType Container)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }
    $leaf = Split-Path -Leaf $Path
    $tmpPath = Join-Path $targetDir (".{0}.{1}.tmp" -f $leaf, [guid]::NewGuid().ToString("N"))
    try {
        Set-Content -LiteralPath $tmpPath -Value (($Data | ConvertTo-Json -Depth 8) + "`n") -Encoding UTF8
        Move-Item -LiteralPath $tmpPath -Destination $Path -Force
    } catch {
        if (Test-Path -LiteralPath $tmpPath -PathType Leaf) {
            Remove-Item -LiteralPath $tmpPath -Force -ErrorAction SilentlyContinue
        }
        throw
    }
}

$now = Get-AiOsProofUtc
$heartbeat = [ordered]@{
    heartbeatAt = $now
    last_beat = $now
    cycle_id = $CycleId
    phase_name = $PhaseName
    pid = $PID
    mode = "DRY_RUN_PROOF"
    effective_apply = $false
    observe_only = $true
    updated_at_utc = $now
}

Write-AiOsProofJsonAtomic -Path $OutputPath -Data $heartbeat

$normalizedOutputPath = $OutputPath -replace "\\", "/"
$productionTelemetryTouched = (
    $normalizedOutputPath -eq "telemetry/runtime/runtime_heartbeat.json" -or
    $normalizedOutputPath -like "*/telemetry/runtime/runtime_heartbeat.json"
)

$result = [ordered]@{
    status = "PASS"
    mode = "DRY_RUN"
    full_night_cycle_invoked = $false
    scheduler_registered = $false
    restart_supervisor_armed = $false
    live_send_attempted = $false
    production_telemetry_touched = $productionTelemetryTouched
    output_path = $OutputPath
    heartbeat = $heartbeat
    atomic_write = [ordered]@{
        temp_file_pattern = ".<leaf>.<guid>.tmp"
        move_item_force = $true
        collision_safe_guid_suffix = $true
    }
    blocked_capabilities = @(
        "full_night_cycle",
        "scheduler_registration",
        "restart_supervisor_arming",
        "live_send",
        "broker",
        "OANDA",
        "live_trading",
        "webhook",
        "credential"
    )
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AIOS Runtime Heartbeat Proof"
Write-Host "Mode: DRY_RUN"
Write-Host "Output path: $OutputPath"
Write-Host "Full night cycle invoked: NO"
Write-Host "Scheduler registered: NO"
Write-Host "Restart supervisor armed: NO"
Write-Host "Live send attempted: NO"
Write-Host "Production telemetry touched: $($result.production_telemetry_touched)"
Write-Host "Heartbeat JSON:"
$heartbeat | ConvertTo-Json -Depth 8
Write-Host "Atomic write: GUID temp file + Move-Item -Force"
