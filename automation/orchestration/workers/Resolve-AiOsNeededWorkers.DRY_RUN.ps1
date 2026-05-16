param(
    [string]$Intent = "",
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

function Read-AiOsActivePackets {
    param([Parameter(Mandatory = $true)][string]$RootFullPath)

    $activePath = Join-Path $RootFullPath "active"
    if (-not (Test-Path -LiteralPath $activePath -PathType Container)) {
        return @()
    }

    return @(Get-ChildItem -LiteralPath $activePath -Filter "*.json" -File | Sort-Object Name | ForEach-Object {
        [pscustomobject]@{
            path = $_.FullName
            packet = Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json
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
$workers = @($profiles.workers)
$activePackets = @(Read-AiOsActivePackets -RootFullPath $rootFullPath)

$nextPacket = $null
if (-not [string]::IsNullOrWhiteSpace($PacketId)) {
    $nextPacket = $activePackets | Where-Object { $_.packet.packet_id -eq $PacketId } | Select-Object -First 1
}
if ($null -eq $nextPacket -and $activePackets.Count -gt 0) {
    $nextPacket = $activePackets[0]
}

$workerResolver = Join-Path $PSScriptRoot "Resolve-AiOsWorkerForPacket.DRY_RUN.ps1"
$resolvedPacketWorker = $null
if ($null -ne $nextPacket) {
    $resolvedPacketWorker = (& $workerResolver -PacketPath $nextPacket.path -QuietJson | ConvertFrom-Json)
}

$intentLower = $Intent.ToLowerInvariant()
$suggestedWorkerIds = [System.Collections.Generic.List[string]]::new()
$suggestedWorkerIds.Add("main_control") | Out-Null
$suggestedWorkerIds.Add("save_git") | Out-Null

if ($null -ne $resolvedPacketWorker) {
    $suggestedWorkerIds.Add($resolvedPacketWorker.selected_worker.worker_id) | Out-Null
}
if ($intentLower -match "packet|route|dispatch") {
    $suggestedWorkerIds.Add("route_dispatch") | Out-Null
}
if ($intentLower -match "watch|state|progress") {
    $suggestedWorkerIds.Add("watch_state") | Out-Null
}
if ($intentLower -match "audit|check|validat") {
    $suggestedWorkerIds.Add("check_audit") | Out-Null
}
if ($intentLower -match "rule|operator") {
    $suggestedWorkerIds.Add("rulebook_codex") | Out-Null
}
if ($intentLower -match "brainstem|orchestration|daily start|guard|save") {
    $suggestedWorkerIds.Add("brainstem_codex") | Out-Null
}

$distinctWorkerIds = @($suggestedWorkerIds | Select-Object -Unique)
$neededWorkers = @()
foreach ($workerId in $distinctWorkerIds) {
    $worker = $workers | Where-Object { $_.worker_id -eq $workerId } | Select-Object -First 1
    if ($null -ne $worker) {
        $neededWorkers += $worker
    }
}

$primaryWorker = $null
if ($null -ne $resolvedPacketWorker) {
    $primaryWorker = $resolvedPacketWorker.selected_worker
} else {
    $primaryWorker = $workers | Where-Object { $_.worker_id -eq "brainstem_codex" } | Select-Object -First 1
}

$validator = "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1"
if ($null -ne $resolvedPacketWorker -and -not [string]::IsNullOrWhiteSpace($resolvedPacketWorker.validator)) {
    $validator = $resolvedPacketWorker.validator
}

$guardCommand = "powershell -ExecutionPolicy Bypass -File automation\orchestration\guard\Invoke-AiOsGuard.ps1 -ExpectedPath ""$($primaryWorker.default_path)"" -ExpectedBranch ""$($primaryWorker.default_branch)"" -ExpectedLaneId $($primaryWorker.worker_id) -CommandType validate"
$saveCommand = "powershell -ExecutionPolicy Bypass -File automation\orchestration\git\Submit-AiOsWork.ps1 -Preview -Title ""AI_OS work packet save"" -CommitMessage ""AI_OS work packet save"""
if ($null -ne $resolvedPacketWorker) {
    $saveCommand = $resolvedPacketWorker.save_command
}

$result = [pscustomobject]@{
    mode = "DRY_RUN"
    intent = $Intent
    active_packet_count = $activePackets.Count
    next_packet = if ($null -eq $nextPacket) { $null } else { $nextPacket.packet }
    primary_worker = $primaryWorker
    needed_workers = $neededWorkers
    validator = $validator
    guard_command = $guardCommand
    save_command = $saveCommand
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Needed Workers Resolver" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"
Write-Host "Intent: $Intent"
Write-Host "Active packets: $($activePackets.Count)"
Write-Host ""
Write-Host "Next packet:" -ForegroundColor Yellow
if ($null -eq $nextPacket) {
    Write-Host "  NONE"
} else {
    Write-Host "  packet_id: $($nextPacket.packet.packet_id)"
    Write-Host "  title: $($nextPacket.packet.title)"
    Write-Host "  owner_lane: $($nextPacket.packet.owner_lane)"
    Write-Host "  repo: $($nextPacket.packet.repo)"
    Write-Host "  branch: $($nextPacket.packet.branch)"
}
Write-Host ""
Write-Host "Primary worker:" -ForegroundColor Yellow
Write-Host "  worker_id: $($primaryWorker.worker_id)"
Write-Host "  title: $($primaryWorker.display_title)"
Write-Host "  path: $($primaryWorker.default_path)"
Write-Host "  branch: $($primaryWorker.default_branch)"
Write-Host ""
Write-Host "Needed workers:" -ForegroundColor Yellow
foreach ($worker in @($neededWorkers)) {
    Write-Host "  $($worker.worker_id) - $($worker.display_title) - $($worker.worker_type)"
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
Write-Host "Visible tab/window: $($primaryWorker.display_title)"
Write-Host "Path: $($primaryWorker.default_path)"
Write-Host "Branch: $($primaryWorker.default_branch)"
Write-Host "Run guard first, then work the packet, then run validator."
Write-Host "Launch performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
