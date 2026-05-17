[CmdletBinding()]
param(
    [string]$LockRegistryPath = "automation/orchestration/locks/FILE_LOCK_REGISTRY_001.json",
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function ConvertTo-AiOsLockRecord {
    param($Lock)

    $workerId = if ($Lock.worker_id) { [string]$Lock.worker_id } else { "UNKNOWN" }
    $claimedPacket = if ($Lock.claimed_packet) { [string]$Lock.claimed_packet } elseif ($Lock.packet_id) { [string]$Lock.packet_id } else { "UNKNOWN" }
    $claimedPaths = @()
    if ($Lock.claimed_paths) { $claimedPaths = @($Lock.claimed_paths) }
    elseif ($Lock.locked_paths) { $claimedPaths = @($Lock.locked_paths) }

    $lockStatus = if ($Lock.lock_status) { [string]$Lock.lock_status } elseif ($Lock.status) { [string]$Lock.status } else { "UNKNOWN" }
    $staleLockWarning = "NO"

    $expiresRaw = $null
    if ($Lock.expires_at) { $expiresRaw = [string]$Lock.expires_at }
    elseif ($Lock.expires_at_utc) { $expiresRaw = [string]$Lock.expires_at_utc }
    elseif ($Lock.expires_at_placeholder) { $expiresRaw = [string]$Lock.expires_at_placeholder }

    if ([string]::IsNullOrWhiteSpace($workerId) -or $workerId -like "*PLACEHOLDER*") {
        $staleLockWarning = "REVIEW_REQUIRED: missing or placeholder worker_id."
    }
    elseif ($claimedPaths.Count -eq 0) {
        $staleLockWarning = "REVIEW_REQUIRED: no claimed paths."
    }
    elseif ([string]::IsNullOrWhiteSpace($expiresRaw) -or $expiresRaw -like "*PLACEHOLDER*") {
        $staleLockWarning = "REVIEW_REQUIRED: no real expiration timestamp."
    }
    else {
        try {
            $expiresAt = [datetime]::Parse($expiresRaw).ToUniversalTime()
            if ($expiresAt -lt (Get-Date).ToUniversalTime()) {
                $staleLockWarning = "YES: lock is past expiration."
            }
        }
        catch {
            $staleLockWarning = "REVIEW_REQUIRED: expiration timestamp could not be parsed."
        }
    }

    [pscustomobject]@{
        worker_id = $workerId
        claimed_packet = $claimedPacket
        claimed_paths = $claimedPaths
        lock_status = $lockStatus
        stale_lock_warning = $staleLockWarning
    }
}

if (-not (Test-Path -LiteralPath $LockRegistryPath -PathType Leaf)) {
    throw "Lock registry not found: $LockRegistryPath"
}

try {
    $lockData = Get-Content -LiteralPath $LockRegistryPath -Raw | ConvertFrom-Json
}
catch {
    throw "Lock registry JSON could not be parsed: $LockRegistryPath"
}

$locks = @()
if ($lockData.PSObject.Properties.Name -contains "locks") {
    $locks = @($lockData.locks)
}
else {
    $locks = @($lockData)
}

$lockRecords = @($locks | ForEach-Object { ConvertTo-AiOsLockRecord -Lock $_ })

$result = [ordered]@{
    schema = "aios_worker_lock_status.v1"
    mode = "DRY_RUN_READ_ONLY"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    locks = $lockRecords
    commit_performed = "NO"
    push_performed = "NO"
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AIOS Worker Lock Status"
Write-Host "Mode: DRY_RUN_READ_ONLY"
Write-Host ""
if ($lockRecords.Count -eq 0) {
    Write-Host "worker_id: none"
    Write-Host "claimed_packet: none"
    Write-Host "claimed_paths: none"
    Write-Host "lock_status: none"
    Write-Host "stale_lock_warning: none"
}
else {
    foreach ($record in $lockRecords) {
        Write-Host "worker_id: $($record.worker_id)"
        Write-Host "claimed_packet: $($record.claimed_packet)"
        Write-Host "claimed_paths:"
        if (@($record.claimed_paths).Count -eq 0) { Write-Host "- none" } else { @($record.claimed_paths) | ForEach-Object { Write-Host "- $_" } }
        Write-Host "lock_status: $($record.lock_status)"
        Write-Host "stale_lock_warning: $($record.stale_lock_warning)"
        Write-Host ""
    }
}
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
