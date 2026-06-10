[CmdletBinding()]
param(
    [switch]$Apply,
    [string]$RepoRoot = (Get-Location).Path,
    [string]$HeartbeatPath = "",
    [string]$OutputPath = "",
    [string]$Source = "coordination_spine_bounded_heartbeat_refresh"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if ([string]::IsNullOrWhiteSpace($HeartbeatPath)) {
    $HeartbeatPath = Join-Path $RepoRoot "telemetry\runtime\runtime_heartbeat.json"
}

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    $OutputPath = $HeartbeatPath
}

function Resolve-AiOsPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $Path))
}

function Read-AiOsJsonDocument {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    try {
        $raw = Get-Content -LiteralPath $Path -Raw
        if ([string]::IsNullOrWhiteSpace($raw)) {
            return $null
        }
        return $raw | ConvertFrom-Json
    }
    catch {
        return $null
    }
}

function New-AiOsHeartbeatPayload {
    param([object]$ExistingHeartbeat, [string]$Timestamp, [string]$Source)

    $payload = [ordered]@{}
    if ($null -ne $ExistingHeartbeat) {
        foreach ($property in $ExistingHeartbeat.PSObject.Properties) {
            $payload[$property.Name] = $property.Value
        }
    }

    $payload["heartbeatAt"] = $Timestamp
    if (-not $payload.Contains("last_beat")) {
        $payload["last_beat"] = $Timestamp
    }
    $payload["status"] = "OK"
    $payload["supervisor_status"] = "OK"
    $payload["source"] = $Source

    return [pscustomobject]$payload
}

function Write-AiOsAtomicJson {
    param(
        [Parameter(Mandatory = $true)][string]$DestinationPath,
        [Parameter(Mandatory = $true)][object]$Payload
    )

    $resolvedDestination = Resolve-AiOsPath -Path $DestinationPath
    $destinationDir = Split-Path -Parent $resolvedDestination
    if (-not (Test-Path -LiteralPath $destinationDir -PathType Container)) {
        New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
    }

    $tempPath = Join-Path $destinationDir (".{0}.{1}.tmp" -f ([System.IO.Path]::GetFileName($resolvedDestination), [guid]::NewGuid().ToString("N")))
    try {
        [System.IO.File]::WriteAllText($tempPath, ($Payload | ConvertTo-Json -Depth 16), (New-Object System.Text.UTF8Encoding($false)))
        Move-Item -LiteralPath $tempPath -Destination $resolvedDestination -Force
    }
    catch {
        if (Test-Path -LiteralPath $tempPath) {
            Remove-Item -LiteralPath $tempPath -Force -ErrorAction SilentlyContinue
        }
        throw
    }
}

$resolvedHeartbeatPath = Resolve-AiOsPath -Path $HeartbeatPath
$resolvedOutputPath = Resolve-AiOsPath -Path $OutputPath
$existing = Read-AiOsJsonDocument -Path $resolvedHeartbeatPath
$nowUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$nextHeartbeat = New-AiOsHeartbeatPayload -ExistingHeartbeat $existing -Timestamp $nowUtc -Source $Source

$result = [ordered]@{
    mode = "DRY_RUN"
    applied = $Apply.IsPresent
    source = $Source
    heartbeat_path = $resolvedOutputPath
    heartbeat_before_exists = ($null -ne $existing)
    heartbeat_after = $nextHeartbeat
    atomic_write = [ordered]@{
        temp_file_pattern = ".[leaf].[guid].tmp"
        move_item_force = $true
    }
}

if ($Apply) {
    Write-AiOsAtomicJson -DestinationPath $resolvedOutputPath -Payload $nextHeartbeat
}

$result | ConvertTo-Json -Depth 16
