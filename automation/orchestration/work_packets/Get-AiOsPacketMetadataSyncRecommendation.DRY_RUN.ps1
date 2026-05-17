[CmdletBinding()]
param(
    [string]$PacketPath = "",
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Get-AiOsNewestActivePacketPath {
    $activePacketRoot = "automation/orchestration/work_packets/active"
    if (-not (Test-Path -LiteralPath $activePacketRoot -PathType Container)) {
        return ""
    }

    $packet = Get-ChildItem -LiteralPath $activePacketRoot -File -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($null -eq $packet) { return "" }
    return $packet.FullName
}

function ConvertTo-AiOsRelativePath {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) { return "" }
    $resolved = Resolve-Path -LiteralPath $Path
    $root = (Get-Location).Path + [IO.Path]::DirectorySeparatorChar
    return ($resolved.Path.Replace($root, "") -replace "\\", "/")
}

function Test-AiOsStaleValue {
    param([string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) { return $true }
    if ($Value -eq "UNKNOWN") { return $true }
    if ($Value -like "*PLACEHOLDER*") { return $true }
    return $false
}

function Get-AiOsPacketWorker {
    param($Packet)

    if ($Packet.PSObject.Properties.Name -contains "worker_id" -and -not (Test-AiOsStaleValue -Value ([string]$Packet.worker_id))) {
        return [string]$Packet.worker_id
    }

    if ($Packet.PSObject.Properties.Name -contains "assigned_worker" -and -not (Test-AiOsStaleValue -Value ([string]$Packet.assigned_worker))) {
        return [string]$Packet.assigned_worker
    }

    return "UNKNOWN"
}

function Get-AiOsLockWorkerWarnings {
    $lockPath = "automation/orchestration/locks/FILE_LOCK_REGISTRY_001.json"
    $warnings = @()

    if (-not (Test-Path -LiteralPath $lockPath -PathType Leaf)) {
        return @("lock registry missing")
    }

    try {
        $lockData = Get-Content -LiteralPath $lockPath -Raw | ConvertFrom-Json
    }
    catch {
        return @("lock registry JSON parse failed")
    }

    $locks = @()
    if ($lockData.PSObject.Properties.Name -contains "locks") {
        $locks = @($lockData.locks)
    }
    else {
        $locks = @($lockData)
    }

    foreach ($lock in $locks) {
        $workerId = if ($lock.PSObject.Properties.Name -contains "worker_id") { [string]$lock.worker_id } else { "" }
        if (Test-AiOsStaleValue -Value $workerId) {
            $warnings += "lock.worker_id"
        }
    }

    return @($warnings | Sort-Object -Unique)
}

if ([string]::IsNullOrWhiteSpace($PacketPath)) {
    $PacketPath = Get-AiOsNewestActivePacketPath
}

$packetId = "UNKNOWN"
$packetPathOut = ""
$currentPacketBranch = "UNKNOWN"
$currentRepoBranch = git branch --show-current
$branchSyncNeeded = $false
$currentWorker = "UNKNOWN"
$workerSyncNeeded = $false
$staleFields = @()
$recommendedAction = "metadata_review_required"
$commandToApplyLater = "No apply command recommended."

if ([string]::IsNullOrWhiteSpace($PacketPath) -or -not (Test-Path -LiteralPath $PacketPath -PathType Leaf)) {
    $staleFields += "packet_path"
    $recommendedAction = "blocked_missing_packet"
}
else {
    $packetPathOut = ConvertTo-AiOsRelativePath -Path $PacketPath

    try {
        $packet = Get-Content -LiteralPath $PacketPath -Raw | ConvertFrom-Json
        $packetId = if ($packet.packet_id) { [string]$packet.packet_id } else { "UNKNOWN" }
        $currentPacketBranch = if ($packet.branch) { [string]$packet.branch } else { "UNKNOWN" }
        $currentWorker = Get-AiOsPacketWorker -Packet $packet

        if ($currentPacketBranch -ne $currentRepoBranch) {
            $branchSyncNeeded = $true
            $staleFields += "branch"
        }

        if (Test-AiOsStaleValue -Value $currentWorker) {
            $workerSyncNeeded = $true
            $staleFields += "worker_id"
        }

        $lockWorkerWarnings = Get-AiOsLockWorkerWarnings
        foreach ($warning in $lockWorkerWarnings) {
            $staleFields += $warning
        }

        $staleFields = @($staleFields | Sort-Object -Unique)

        if ($branchSyncNeeded -or $workerSyncNeeded) {
            $recommendedAction = "metadata_sync_recommended"
        }
        elseif ($staleFields -contains "lock.worker_id") {
            $recommendedAction = "lock_metadata_review_recommended"
        }
        else {
            $recommendedAction = "no_metadata_sync_needed"
        }

        if ($branchSyncNeeded -or $workerSyncNeeded) {
            $commandToApplyLater = "powershell -ExecutionPolicy Bypass -File automation/orchestration/work_packets/Sync-AiOsPacketMetadata.APPLY.ps1 -PacketPath `"$packetPathOut`" -SyncBranch -WorkerId `"$currentWorker`""
        }
    }
    catch {
        $staleFields += "packet_json"
        $recommendedAction = "blocked_packet_parse_review"
    }
}

$result = [ordered]@{
    schema = "aios_packet_metadata_sync_recommendation.v1"
    mode = "DRY_RUN_READ_ONLY"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    packet_id = $packetId
    packet_path = $packetPathOut
    current_packet_branch = $currentPacketBranch
    current_repo_branch = $currentRepoBranch
    branch_sync_needed = $branchSyncNeeded
    current_worker = $currentWorker
    worker_sync_needed = $workerSyncNeeded
    stale_fields = $staleFields
    recommended_action = $recommendedAction
    command_to_apply_later = $commandToApplyLater
    commit_performed = "NO"
    push_performed = "NO"
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AIOS Packet Metadata Sync Recommendation"
Write-Host "Mode: DRY_RUN_READ_ONLY"
Write-Host ""
Write-Host "packet_id: $packetId"
Write-Host "packet_path: $packetPathOut"
Write-Host "current_packet_branch: $currentPacketBranch"
Write-Host "current_repo_branch: $currentRepoBranch"
Write-Host "branch_sync_needed: $branchSyncNeeded"
Write-Host "current_worker: $currentWorker"
Write-Host "worker_sync_needed: $workerSyncNeeded"
Write-Host "stale_fields:"
if ($staleFields.Count -eq 0) { Write-Host "- none" } else { $staleFields | ForEach-Object { Write-Host "- $_" } }
Write-Host "recommended_action: $recommendedAction"
Write-Host "command_to_apply_later:"
Write-Host $commandToApplyLater
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
