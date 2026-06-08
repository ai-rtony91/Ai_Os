param(
    [string]$WorkerId = "AIOS-WORKER-DRY-RUN",
    [string]$PacketId = "PACKET-DRY-RUN",
    [string]$Lane = "UNKNOWN",
    [string[]]$Paths = @("automation/orchestration/locks/FILE_LOCK_REGISTRY.json"),
    [string]$RegistryPath = (Join-Path $PSScriptRoot "FILE_LOCK_REGISTRY.json"),
    [string]$ApprovalPacketId = "",
    [string]$ReleaseCondition = "Release at packet stop point or by explicit operator approval.",
    [int]$TtlMinutes = 240,
    [switch]$Apply,
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsUtcNow {
    return [DateTime]::UtcNow
}

function ConvertTo-AiOsUtcString {
    param([DateTime]$Value)
    return $Value.ToUniversalTime().ToString("o")
}

function Read-AiOsJsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "LOCK_REGISTRY_FAIL_CLOSED: Registry file not found: $Path"
    }

    try {
        return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    }
    catch {
        throw "LOCK_REGISTRY_FAIL_CLOSED: Registry JSON could not be parsed: $($_.Exception.Message)"
    }
}

function Write-AiOsJsonAtomic {
    param(
        [Parameter(Mandatory = $true)]$Data,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $directory = Split-Path -Parent $Path
    if ([string]::IsNullOrWhiteSpace($directory)) {
        $directory = "."
    }
    $leaf = Split-Path -Leaf $Path
    $tempPath = Join-Path $directory (".{0}.{1}.tmp" -f $leaf, [Guid]::NewGuid().ToString("N"))

    try {
        $json = $Data | ConvertTo-Json -Depth 20
        $encoding = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($tempPath, $json, $encoding)
        [void](Get-Content -Raw -LiteralPath $tempPath | ConvertFrom-Json)
        Move-Item -LiteralPath $tempPath -Destination $Path -Force
    }
    catch {
        if (Test-Path -LiteralPath $tempPath) {
            Remove-Item -LiteralPath $tempPath -Force
        }
        throw "LOCK_REGISTRY_ATOMIC_WRITE_FAILED: $($_.Exception.Message)"
    }
}

function ConvertTo-AiOsPathKey {
    param([AllowNull()][string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }

    $key = $Path.Replace("\", "/").Trim()
    while ($key.StartsWith("./")) {
        $key = $key.Substring(2)
    }
    return $key.TrimEnd("/")
}

function Test-AiOsPathOverlap {
    param(
        [string]$LeftPath,
        [string]$RightPath
    )

    $left = ConvertTo-AiOsPathKey -Path $LeftPath
    $right = ConvertTo-AiOsPathKey -Path $RightPath

    if ([string]::IsNullOrWhiteSpace($left) -or [string]::IsNullOrWhiteSpace($right)) {
        return $false
    }

    return ($left -eq $right -or $left.StartsWith("$right/") -or $right.StartsWith("$left/"))
}

function Get-AiOsLockPaths {
    param($Lock)

    if ($Lock.PSObject.Properties.Name -contains "claimed_paths") {
        return @($Lock.claimed_paths)
    }
    if ($Lock.PSObject.Properties.Name -contains "locked_paths") {
        return @($Lock.locked_paths)
    }
    if ($Lock.PSObject.Properties.Name -contains "paths") {
        return @($Lock.paths)
    }
    return @()
}

$registry = Read-AiOsJsonFile -Path $RegistryPath
$locks = @($registry.locks)
$activeLocks = @($locks | Where-Object { $_.status -eq "ACTIVE" })
$collisions = @()
$policyBlocks = @()
$reviewRequired = @()
$now = Get-AiOsUtcNow
$normalizedPaths = @($Paths | ForEach-Object { ConvertTo-AiOsPathKey -Path $_ } | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | Sort-Object -Unique)

if ($normalizedPaths.Count -eq 0) {
    $reviewRequired += [pscustomobject]@{
        risk_type = "EMPTY_CLAIM_PATHS"
        recommendation = "Provide at least one non-empty path before claiming a lock."
    }
}

foreach ($requestedPath in $normalizedPaths) {
    foreach ($blockedPath in @($registry.global_blocked_paths)) {
        if (Test-AiOsPathOverlap -LeftPath $requestedPath -RightPath $blockedPath) {
            $policyBlocks += [pscustomobject]@{
                requested_path = $requestedPath
                blocked_path = ConvertTo-AiOsPathKey -Path $blockedPath
                risk_type = "GLOBAL_BLOCKED_PATH"
                recommendation = "Do not claim this path in an automated worker lock."
            }
        }
    }

    foreach ($lock in $activeLocks) {
        $expired = $false
        if ($lock.PSObject.Properties.Name -contains "expires_at_utc" -and -not [string]::IsNullOrWhiteSpace([string]$lock.expires_at_utc)) {
            try {
                $expired = ([DateTime]::Parse([string]$lock.expires_at_utc).ToUniversalTime() -lt $now)
            }
            catch {
                $reviewRequired += [pscustomobject]@{
                    requested_path = $requestedPath
                    existing_lock_id = $lock.lock_id
                    risk_type = "MALFORMED_EXPIRES_AT_UTC"
                    recommendation = "Fail closed and review the lock timestamp before claiming."
                }
            }
        }

        foreach ($lockedPath in (Get-AiOsLockPaths -Lock $lock)) {
            if (Test-AiOsPathOverlap -LeftPath $requestedPath -RightPath $lockedPath) {
                $riskType = "ACTIVE_LOCK_COLLISION"
                $recommendation = "Block claim. Another worker owns an overlapping path."

                if ($lock.worker_id -eq $WorkerId) {
                    $riskType = "SAME_WORKER_RECLAIM_REVIEW"
                    $recommendation = "Require review before the same worker expands or repeats a claim."
                }
                elseif ($expired) {
                    $riskType = "EXPIRED_LOCK_REVIEW_REQUIRED"
                    $recommendation = "Do not auto-clear stale locks. Require review before claiming this path."
                }

                $collisions += [pscustomobject]@{
                    requested_path = $requestedPath
                    existing_lock_id = $lock.lock_id
                    existing_worker_id = $lock.worker_id
                    existing_packet_id = $lock.packet_id
                    existing_path = ConvertTo-AiOsPathKey -Path $lockedPath
                    risk_type = $riskType
                    recommendation = $recommendation
                }
            }
        }
    }
}

$claimStatus = "READY_TO_CLAIM"
if ($policyBlocks.Count -gt 0) {
    $claimStatus = "BLOCKED"
}
elseif ($collisions.Count -gt 0 -or $reviewRequired.Count -gt 0) {
    $claimStatus = "REVIEW_REQUIRED"
}

$lockId = "AIOS-LOCK-{0}" -f ([Guid]::NewGuid().ToString("N"))
$createdAt = ConvertTo-AiOsUtcString -Value $now
$expiresAt = ConvertTo-AiOsUtcString -Value $now.AddMinutes($TtlMinutes)
$lock = [pscustomobject]@{
    schema = "AIOS_PACKET_LOCK.v1"
    schema_version = "1.0.0"
    lock_id = $lockId
    worker_id = $WorkerId
    packet_id = $PacketId
    lane = $Lane
    status = "ACTIVE"
    claimed_paths = $normalizedPaths
    created_at_utc = $createdAt
    updated_at_utc = $createdAt
    expires_at_utc = $expiresAt
    release_condition = $ReleaseCondition
    approval_packet_id = $ApprovalPacketId
    notes = "Persisted only when -Apply is supplied. No worker launch behavior is included."
}

$writesPerformed = 0
if ($Apply -and $claimStatus -eq "READY_TO_CLAIM") {
    $registry.locks += $lock
    Write-AiOsJsonAtomic -Data $registry -Path $RegistryPath
    $writesPerformed = 1
}

$recommendedBlocked = @()
$recommendedBlocked += @($registry.global_blocked_paths)
$recommendedBlocked += @($registry.recommended_blocked_files)
$recommendedBlocked += @($normalizedPaths)
foreach ($collision in $collisions) {
    $recommendedBlocked += $collision.existing_path
}
$recommendedBlocked = @($recommendedBlocked | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | ForEach-Object { ConvertTo-AiOsPathKey -Path $_ } | Sort-Object -Unique)

$result = [pscustomobject]@{
    task = "AI_OS file lock claim"
    mode = $(if ($Apply) { "APPLY" } else { "DRY_RUN" })
    registry_path = $RegistryPath
    claim_status = $claimStatus
    writes_performed = $writesPerformed
    lock = $lock
    collision_count = $collisions.Count
    policy_block_count = $policyBlocks.Count
    review_required_count = $reviewRequired.Count
    collisions = $collisions
    policy_blocks = $policyBlocks
    review_required = $reviewRequired
    recommended_blocked_paths = $recommendedBlocked
    safety = [pscustomobject]@{
        commits_performed = 0
        pushes_performed = 0
        broker_or_live_api_work = "NO"
    }
    next_safe_action = "Proceed only when claim_status is READY_TO_CLAIM and the operator approved the exact APPLY lock claim."
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AI_OS File Lock Claim"
Write-Host "Mode: $($result.mode)"
Write-Host "Worker: $WorkerId"
Write-Host "Packet: $PacketId"
Write-Host "Result: $claimStatus"
Write-Host "Writes performed: $writesPerformed"
Write-Host ""
Write-Host "Requested paths:"
foreach ($path in $normalizedPaths) {
    Write-Host "  - $path"
}
Write-Host ""
Write-Host "Collision risks: $($collisions.Count)"
foreach ($collision in $collisions) {
    Write-Host "  - $($collision.requested_path) overlaps $($collision.existing_path) owned by $($collision.existing_worker_id)"
}
Write-Host "Policy blocks: $($policyBlocks.Count)"
foreach ($block in $policyBlocks) {
    Write-Host "  - $($block.requested_path) matches blocked path $($block.blocked_path)"
}
Write-Host "Review required: $($reviewRequired.Count)"
Write-Host ""
Write-Host "Next safe action: $($result.next_safe_action)"
