[CmdletBinding()]
param(
    [switch]$Apply,
    [string]$RepoRoot,
    [string]$MarkerPath,
    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path
}

if (-not $PSBoundParameters.ContainsKey('MarkerPath')) {
    $MarkerPath = Join-Path $RepoRoot 'control\cycle\last_marker.json'
}

if (-not $PSBoundParameters.ContainsKey('OutputPath')) {
    $OutputPath = $MarkerPath
}

function Resolve-AiOsPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $Path))
}

function Read-AiOsJsonDocument {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    $raw = Get-Content -LiteralPath $Path -Raw
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return $null
    }

    return $raw | ConvertFrom-Json
}

function Get-AiOsUtc {
    return (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
}

function Copy-AiOsObject {
    param(
        [Parameter(Mandatory = $true)]
        [object]$InputObject
    )

    $copy = [ordered]@{}
    foreach ($property in @($InputObject.PSObject.Properties)) {
        $copy[$property.Name] = $property.Value
    }

    return $copy
}

function Write-AiOsAtomicJson {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DestinationPath,

        [Parameter(Mandatory = $true)]
        [object]$Payload
    )

    $destinationFull = Resolve-AiOsPath -Path $DestinationPath
    $destinationDir = Split-Path -Parent $destinationFull
    if (-not (Test-Path -LiteralPath $destinationDir -PathType Container)) {
        New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
    }

    $tempPath = Join-Path $destinationDir ('.{0}.tmp' -f [System.IO.Path]::GetRandomFileName())
    try {
        $json = $Payload | ConvertTo-Json -Depth 16
        [System.IO.File]::WriteAllText($tempPath, $json, (New-Object System.Text.UTF8Encoding($false)))
        Move-Item -LiteralPath $tempPath -Destination $destinationFull -Force
    }
    catch {
        if (Test-Path -LiteralPath $tempPath) {
            Remove-Item -LiteralPath $tempPath -Force -ErrorAction SilentlyContinue
        }
        throw
    }
}

$markerFullPath = Resolve-AiOsPath -Path $MarkerPath
$defaultMarkerPath = Resolve-AiOsPath -Path (Join-Path $RepoRoot 'control\cycle\last_marker.json')
if ($Apply -and $markerFullPath -ne $defaultMarkerPath) {
    throw 'Apply mode may only write control\cycle\last_marker.json'
}

$markerDocument = Read-AiOsJsonDocument -Path $markerFullPath
if ($null -eq $markerDocument) {
    throw "Cycle marker missing or unreadable: $markerFullPath"
}

$markerPayload = Copy-AiOsObject -InputObject $markerDocument
$existingUpdatedAtUtc = if ($markerPayload.Contains('updated_at_utc')) { [string]$markerPayload['updated_at_utc'] } else { '' }
$newUpdatedAtUtc = Get-AiOsUtc

$markerPayload['updated_at_utc'] = $newUpdatedAtUtc
$markerPayload['marker_refresh_source'] = 'Update-AiOsCycleMarker.DRY_RUN.ps1'
$markerPayload['marker_refresh_mode'] = 'marker_only'
$markerPayload['marker_refresh_reason'] = 'marker_stale_repair'
$markerPayload['marker_refresh_previous_updated_at_utc'] = $existingUpdatedAtUtc
$markerPayload['marker_refresh_applied'] = [bool]$Apply

$report = [ordered]@{
    schema = 'AIOS_CYCLE_MARKER_REFRESH_REPORT.v1'
    system = 'AI_OS'
    mode = if ($Apply) { 'APPLY' } else { 'DRY_RUN' }
    generated_at = (Get-Date).ToUniversalTime().ToString('o')
    repo_root = $RepoRoot
    marker_path = $markerFullPath
    marker_present = $true
    existing_updated_at_utc = $existingUpdatedAtUtc
    proposed_updated_at_utc = $newUpdatedAtUtc
    refresh_mode = 'marker_only'
    refresh_source = 'Update-AiOsCycleMarker.DRY_RUN.ps1'
    write_behavior = 'telemetry_only'
    write_path_enabled = [bool]$Apply
    would_write = @($markerFullPath)
    safe_next_action = 'Regenerate recovery and cockpit telemetry after marker refresh.'
}

if ($Apply) {
    Write-AiOsAtomicJson -DestinationPath $defaultMarkerPath -Payload $markerPayload
}

$report | ConvertTo-Json -Depth 16
