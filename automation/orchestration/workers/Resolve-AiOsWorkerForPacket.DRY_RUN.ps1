param(
    [string]$PacketPath = "",
    [string]$PacketId = "",
    [switch]$QuietJson,
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

function Read-AiOsPacket {
    param(
        [string]$PacketPath,
        [string]$PacketId,
        [string]$RootFullPath
    )

    if (-not [string]::IsNullOrWhiteSpace($PacketPath)) {
        $fullPath = Resolve-AiOsPath -Path $PacketPath
        if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
            throw "Packet file not found: $fullPath"
        }
        return [pscustomobject]@{
            path = $fullPath
            packet = Get-Content -LiteralPath $fullPath -Raw | ConvertFrom-Json
        }
    }

    $packetFiles = @(Get-ChildItem -LiteralPath $RootFullPath -Recurse -Filter "*.json" -File)
    if ([string]::IsNullOrWhiteSpace($PacketId)) {
        $activePath = Join-Path $RootFullPath "active"
        $packetFiles = @(Get-ChildItem -LiteralPath $activePath -Filter "*.json" -File | Sort-Object Name)
        if ($packetFiles.Count -lt 1) {
            throw "No active packets found."
        }
        $selectedFile = $packetFiles[0]
        return [pscustomobject]@{
            path = $selectedFile.FullName
            packet = Get-Content -LiteralPath $selectedFile.FullName -Raw | ConvertFrom-Json
        }
    }

    foreach ($file in $packetFiles) {
        $packet = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
        if ($packet.packet_id -eq $PacketId) {
            return [pscustomobject]@{
                path = $file.FullName
                packet = $packet
            }
        }
    }

    throw "PacketId not found: $PacketId"
}

function Test-PathOwnedByWorker {
    param(
        [Parameter(Mandatory = $true)]$Worker,
        [Parameter(Mandatory = $true)][string]$RelativePath
    )

    foreach ($ownedPath in @($Worker.owns_paths)) {
        if ($RelativePath.StartsWith($ownedPath, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }

    return $false
}

$scriptName = Split-Path -Leaf $PSCommandPath
$rootFullPath = Resolve-AiOsPath -Path $RootPath
$profilesFullPath = Resolve-AiOsPath -Path $ProfilesPath
if (-not (Test-Path -LiteralPath $profilesFullPath -PathType Leaf)) {
    throw "Worker profiles file not found: $profilesFullPath"
}

$profiles = Get-Content -LiteralPath $profilesFullPath -Raw | ConvertFrom-Json
$workers = @($profiles.workers)
$packetEntry = Read-AiOsPacket -PacketPath $PacketPath -PacketId $PacketId -RootFullPath $rootFullPath
$packet = $packetEntry.packet

$selectedWorker = $null
$reason = "No worker selected."

if (-not [string]::IsNullOrWhiteSpace($packet.owner_lane)) {
    $selectedWorker = $workers | Where-Object { $_.worker_id -eq $packet.owner_lane } | Select-Object -First 1
    if ($null -ne $selectedWorker) {
        $reason = "Matched packet owner_lane."
    }
}

if ($null -eq $selectedWorker -and -not [string]::IsNullOrWhiteSpace($packet.assigned_worker)) {
    $selectedWorker = $workers | Where-Object { $_.worker_id -eq $packet.assigned_worker } | Select-Object -First 1
    if ($null -ne $selectedWorker) {
        $reason = "Matched packet assigned_worker."
    }
}

if ($null -eq $selectedWorker) {
    foreach ($relatedFile in @($packet.related_files)) {
        foreach ($worker in $workers) {
            if (Test-PathOwnedByWorker -Worker $worker -RelativePath $relatedFile) {
                $selectedWorker = $worker
                $reason = "Matched related_files path: $relatedFile"
                break
            }
        }
        if ($null -ne $selectedWorker) { break }
    }
}

if ($null -eq $selectedWorker) {
    $selectedWorker = $workers | Where-Object { $_.worker_id -eq "brainstem_codex" } | Select-Object -First 1
    $reason = "Fallback to brainstem_codex for unresolved AI_OS packet."
}

$conflicts = @()
foreach ($workerId in @($selectedWorker.cannot_overlap_with)) {
    $conflicts += $workerId
}

$validator = $packet.validator
if ([string]::IsNullOrWhiteSpace($validator)) {
    $validator = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1"
}

$guardCommand = "powershell -ExecutionPolicy Bypass -File automation\orchestration\guard\Invoke-AiOsGuard.ps1 -ExpectedPath ""$($selectedWorker.default_path)"" -ExpectedBranch ""$($selectedWorker.default_branch)"" -ExpectedLaneId $($selectedWorker.worker_id) -CommandType validate"
$saveCommand = "powershell -ExecutionPolicy Bypass -File automation\orchestration\git\Submit-AiOsWork.ps1 -Preview -Title ""$($packet.title)"" -CommitMessage ""$($packet.title)"""

$result = [pscustomobject]@{
    mode = "DRY_RUN"
    packet_id = $packet.packet_id
    packet_path = $packetEntry.path
    selected_worker = $selectedWorker
    reason = $reason
    conflicts = $conflicts
    validator = $validator
    guard_command = $guardCommand
    save_command = $saveCommand
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Worker For Packet Resolver" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"
Write-Host "Packet: $($packet.packet_id)"
Write-Host "Packet path: $($packetEntry.path)"
Write-Host ""
Write-Host "Selected worker:" -ForegroundColor Yellow
Write-Host "  worker_id: $($selectedWorker.worker_id)"
Write-Host "  title: $($selectedWorker.display_title)"
Write-Host "  type: $($selectedWorker.worker_type)"
Write-Host "  path: $($selectedWorker.default_path)"
Write-Host "  branch: $($selectedWorker.default_branch)"
Write-Host "  why: $reason"
Write-Host ""
Write-Host "Conflicts:" -ForegroundColor Yellow
if ($conflicts.Count -eq 0) {
    Write-Host "  NONE"
} else {
    $conflicts | ForEach-Object { Write-Host "  $_" }
}
Write-Host ""
Write-Host "Validator:" -ForegroundColor Yellow
Write-Host "  $validator"
Write-Host "Guard check:" -ForegroundColor Yellow
Write-Host "  $guardCommand"
Write-Host "Later save/PR command:" -ForegroundColor Yellow
Write-Host "  $saveCommand"
Write-Host ""
Write-Host "WHERE TO RUN NEXT" -ForegroundColor Yellow
Write-Host "Visible tab/window: $($selectedWorker.display_title)"
Write-Host "Path: $($selectedWorker.default_path)"
Write-Host "Branch: $($selectedWorker.default_branch)"
Write-Host "Run guard before work, then run validator after work."
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
