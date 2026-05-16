param(
    [Parameter(Mandatory = $true)][string]$Intent,
    [Parameter(Mandatory = $true)][string]$OwnerLane,
    [Parameter(Mandatory = $true)][string]$AssignedWorker,
    [Parameter(Mandatory = $true)][string]$Repo,
    [Parameter(Mandatory = $true)][string]$Branch,
    [Parameter(Mandatory = $true)][string]$Validator,
    [Parameter(Mandatory = $true)][string]$NextAction,
    [string]$Title = "",
    [string]$PacketId = "",
    [string]$Priority = "normal",
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

function ConvertTo-AiOsSlug {
    param([Parameter(Mandatory = $true)][string]$Value)

    $slug = $Value.ToLowerInvariant() -replace "[^a-z0-9]+", "-"
    $slug = $slug.Trim("-")
    if ([string]::IsNullOrWhiteSpace($slug)) {
        return "work-packet"
    }
    return $slug
}

$scriptName = Split-Path -Leaf $PSCommandPath
$utcNow = (Get-Date).ToUniversalTime()
$createdUtc = $utcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
$safePacketId = if ([string]::IsNullOrWhiteSpace($PacketId)) { ConvertTo-AiOsSlug -Value $Intent } else { ConvertTo-AiOsSlug -Value $PacketId }
$safeTitle = if ([string]::IsNullOrWhiteSpace($Title)) { $Intent } else { $Title }
$rootFullPath = Resolve-AiOsPath -Path $RootPath
$activePath = Join-Path $rootFullPath "active"

if (-not (Test-Path -LiteralPath $activePath -PathType Container)) {
    New-Item -ItemType Directory -Path $activePath -Force | Out-Null
}

$fileName = "$($utcNow.ToString('yyyyMMdd-HHmmss'))-$safePacketId.json"
$packetPath = Join-Path $activePath $fileName

$packet = [ordered]@{
    packet_id = $safePacketId
    title = $safeTitle
    intent = $Intent
    owner_lane = $OwnerLane
    assigned_worker = $AssignedWorker
    repo = $Repo
    branch = $Branch
    status = "active"
    priority = $Priority
    created_utc = $createdUtc
    updated_utc = $createdUtc
    validator = $Validator
    next_action = $NextAction
    blocked_by = @()
    related_files = @()
    related_packets = @()
    notes = @()
}

$packet | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $packetPath -Encoding UTF8

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Work Packet Creator" -ForegroundColor Cyan
Write-Host "Mode: APPLY - creates one active packet file"
Write-Host "Packet path: $packetPath"
Write-Host "packet_id: $safePacketId"
Write-Host "owner_lane: $OwnerLane"
Write-Host "assigned_worker: $AssignedWorker"
Write-Host "repo: $Repo"
Write-Host "branch: $Branch"
Write-Host "status: active"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
