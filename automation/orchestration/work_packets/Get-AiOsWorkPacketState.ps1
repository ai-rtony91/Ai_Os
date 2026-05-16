param(
    [string]$RootPath = "automation/orchestration/work_packets"
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

function Read-PacketFiles {
    param([Parameter(Mandatory = $true)][string]$RootFullPath)

    $states = @("active", "blocked", "complete")
    $packets = @()
    foreach ($state in $states) {
        $statePath = Join-Path $RootFullPath $state
        if (-not (Test-Path -LiteralPath $statePath -PathType Container)) {
            continue
        }

        Get-ChildItem -LiteralPath $statePath -Filter "*.json" -File | ForEach-Object {
            $packet = Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json
            $packets += [pscustomobject]@{
                file = $_.FullName
                folder_state = $state
                packet = $packet
            }
        }
    }
    return $packets
}

function Get-PacketStatusWarnings {
    param([Parameter(Mandatory = $true)][array]$Packets)

    return @($Packets | Where-Object {
        -not [string]::IsNullOrWhiteSpace($_.packet.status) -and
        $_.packet.status -ne $_.folder_state
    })
}

$scriptName = Split-Path -Leaf $PSCommandPath
$rootFullPath = Resolve-AiOsPath -Path $RootPath
$packets = @(Read-PacketFiles -RootFullPath $rootFullPath)

$activePackets = @($packets | Where-Object { $_.folder_state -eq "active" })
$blockedPackets = @($packets | Where-Object { $_.folder_state -eq "blocked" })
$completePackets = @($packets | Where-Object { $_.folder_state -eq "complete" })
$statusWarnings = @(Get-PacketStatusWarnings -Packets $packets)
$orphanPackets = @($packets | Where-Object {
    [string]::IsNullOrWhiteSpace($_.packet.owner_lane) -or
    [string]::IsNullOrWhiteSpace($_.packet.repo) -or
    [string]::IsNullOrWhiteSpace($_.packet.branch)
})

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Work Packet State" -ForegroundColor Cyan
Write-Host "Mode: READ_ONLY"
Write-Host "Root: $rootFullPath"

Write-Host ""
Write-Host "Counts by state:" -ForegroundColor Yellow
Write-Host "  active: $($activePackets.Count)"
Write-Host "  blocked: $($blockedPackets.Count)"
Write-Host "  complete: $($completePackets.Count)"
Write-Host "  total: $($packets.Count)"

Write-Host ""
Write-Host "Folder/status warnings:" -ForegroundColor Yellow
if ($statusWarnings.Count -eq 0) {
    Write-Host "  NONE"
} else {
    $statusWarnings | ForEach-Object {
        Write-Host "  WARN $($_.packet.packet_id) - folder: $($_.folder_state) - packet.status: $($_.packet.status) - using folder state"
    }
}

Write-Host ""
Write-Host "Owners:" -ForegroundColor Yellow
@($packets | Where-Object { -not [string]::IsNullOrWhiteSpace($_.packet.owner_lane) } | Group-Object { $_.packet.owner_lane }) | ForEach-Object {
    Write-Host "  $($_.Name): $($_.Count)"
}

Write-Host ""
Write-Host "Blocked packets:" -ForegroundColor Yellow
if ($blockedPackets.Count -eq 0) {
    Write-Host "  NONE"
} else {
    $blockedPackets | ForEach-Object {
        Write-Host "  $($_.packet.packet_id) - $($_.packet.title)"
    }
}

Write-Host ""
Write-Host "Active packets:" -ForegroundColor Yellow
if ($activePackets.Count -eq 0) {
    Write-Host "  NONE"
} else {
    $activePackets | ForEach-Object {
        Write-Host "  $($_.packet.packet_id) - owner: $($_.packet.owner_lane) - worker: $($_.packet.assigned_worker)"
    }
}

Write-Host ""
Write-Host "Orphan packets:" -ForegroundColor Yellow
if ($orphanPackets.Count -eq 0) {
    Write-Host "  NONE"
} else {
    $orphanPackets | ForEach-Object {
        Write-Host "  $($_.packet.packet_id) - missing owner/repo/branch"
    }
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
