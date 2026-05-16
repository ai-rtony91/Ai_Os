param(
    [string]$RootPath = "automation/orchestration/work_packets",
    [string]$ProfilesPath = "automation/orchestration/workers/AIOS_WORKER_PROFILES.json"
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Resolve-AiOsPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return Join-Path (Get-Location).Path $Path
}

function Read-PacketFolder {
    param(
        [Parameter(Mandatory = $true)][string]$RootFullPath,
        [Parameter(Mandatory = $true)][string]$State
    )

    $statePath = Join-Path $RootFullPath $State
    if (-not (Test-Path -LiteralPath $statePath -PathType Container)) {
        return @()
    }

    return @(Get-ChildItem -LiteralPath $statePath -Filter "*.json" -File | ForEach-Object {
        $packet = Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json
        [pscustomobject]@{
            file = $_.FullName
            folder_state = $State
            packet = $packet
        }
    })
}

$scriptName = Split-Path -Leaf $PSCommandPath
$rootFullPath = Resolve-AiOsPath -Path $RootPath
$profilesFullPath = Resolve-AiOsPath -Path $ProfilesPath
if (-not (Test-Path -LiteralPath $profilesFullPath -PathType Leaf)) {
    throw "Worker profiles file not found: $profilesFullPath"
}

$profiles = Get-Content -LiteralPath $profilesFullPath -Raw | ConvertFrom-Json
$profileIds = @($profiles.workers | ForEach-Object { $_.worker_id })
$activePackets = @(Read-PacketFolder -RootFullPath $rootFullPath -State "active")
$blockedPackets = @(Read-PacketFolder -RootFullPath $rootFullPath -State "blocked")
$allPackets = @($activePackets + $blockedPackets)

$unassignedPackets = @($activePackets | Where-Object { [string]::IsNullOrWhiteSpace($_.packet.assigned_worker) })
$unknownOwnerPackets = @($allPackets | Where-Object { -not [string]::IsNullOrWhiteSpace($_.packet.owner_lane) -and $profileIds -notcontains $_.packet.owner_lane })
$unknownWorkerPackets = @($allPackets | Where-Object { -not [string]::IsNullOrWhiteSpace($_.packet.assigned_worker) -and $profileIds -notcontains $_.packet.assigned_worker })
$duplicateOwners = @($activePackets | Where-Object { -not [string]::IsNullOrWhiteSpace($_.packet.owner_lane) } | Group-Object { $_.packet.owner_lane } | Where-Object { $_.Count -gt 1 })

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Work Packet Router Preview" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"
Write-Host "Root: $rootFullPath"
Write-Host "Routing lane: route_dispatch"
Write-Host "State observer lane: watch_state"
Write-Host "CONTROL remains root lane."
Write-Host "Worker profiles: $profilesFullPath"
Write-Host "No files changed. No automation loops. No background processes."

Write-Host ""
Write-Host "Active packets inspected: $($activePackets.Count)" -ForegroundColor Yellow
foreach ($entry in $activePackets) {
    $packet = $entry.packet
    Write-Host "  $($packet.packet_id) - owner: $($packet.owner_lane) - worker: $($packet.assigned_worker) - repo: $($packet.repo) - branch: $($packet.branch)"
}

Write-Host ""
Write-Host "Suggested routing:" -ForegroundColor Yellow
foreach ($entry in $activePackets) {
    $packet = $entry.packet
    if ([string]::IsNullOrWhiteSpace($packet.assigned_worker)) {
        Write-Host "  $($packet.packet_id): assign worker before APPLY."
    } elseif ([string]::IsNullOrWhiteSpace($packet.owner_lane)) {
        Write-Host "  $($packet.packet_id): assign owner_lane before APPLY."
    } else {
        Write-Host "  $($packet.packet_id): route to $($packet.owner_lane) for $($packet.assigned_worker)."
    }
}

Write-Host ""
Write-Host "Unassigned packets:" -ForegroundColor Yellow
if ($unassignedPackets.Count -eq 0) {
    Write-Host "  NONE"
} else {
    $unassignedPackets | ForEach-Object { Write-Host "  $($_.packet.packet_id)" }
}

Write-Host ""
Write-Host "Unknown owner/profile references:" -ForegroundColor Yellow
if ($unknownOwnerPackets.Count -eq 0 -and $unknownWorkerPackets.Count -eq 0) {
    Write-Host "  NONE"
} else {
    $unknownOwnerPackets | ForEach-Object { Write-Host "  owner_lane unknown: $($_.packet.packet_id) -> $($_.packet.owner_lane)" }
    $unknownWorkerPackets | ForEach-Object { Write-Host "  assigned_worker unknown: $($_.packet.packet_id) -> $($_.packet.assigned_worker)" }
}

Write-Host ""
Write-Host "Blocked packets:" -ForegroundColor Yellow
if ($blockedPackets.Count -eq 0) {
    Write-Host "  NONE"
} else {
    $blockedPackets | ForEach-Object {
        Write-Host "  $($_.packet.packet_id) - blocked_by: $($_.packet.blocked_by -join '; ')"
    }
}

Write-Host ""
Write-Host "Duplicate active owners:" -ForegroundColor Yellow
if ($duplicateOwners.Count -eq 0) {
    Write-Host "  NONE"
} else {
    $duplicateOwners | ForEach-Object {
        Write-Host "  $($_.Name): $($_.Count) active packets"
    }
}

Write-Host ""
Write-Host "Next safe action:" -ForegroundColor Yellow
Write-Host "  Review routing preview, resolve unknown worker/profile references, then update one packet at a time with explicit APPLY approval."
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
