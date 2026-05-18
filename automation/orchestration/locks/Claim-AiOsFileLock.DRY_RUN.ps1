param(
    [string]$WorkerId = "AIOS-WORKER-DRY-RUN",
    [string]$PacketId = "PACKET-DRY-RUN",
    [string[]]$Paths = @("automation/orchestration/locks/FILE_LOCK_REGISTRY.example.json"),
    [string]$RegistryPath = (Join-Path $PSScriptRoot "FILE_LOCK_REGISTRY.example.json"),
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-AiOsJsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Registry file not found: $Path"
    }

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
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

$registry = Read-AiOsJsonFile -Path $RegistryPath
$activeLocks = @($registry.locks | Where-Object { $_.status -eq "ACTIVE" })
$collisions = @()
$policyBlocks = @()
$normalizedPaths = @($Paths | ForEach-Object { ConvertTo-AiOsPathKey -Path $_ } | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })

foreach ($requestedPath in $normalizedPaths) {
    foreach ($blockedPath in @($registry.global_blocked_paths)) {
        if (Test-AiOsPathOverlap -LeftPath $requestedPath -RightPath $blockedPath) {
            $policyBlocks += [pscustomobject]@{
                requested_path = $requestedPath
                blocked_path = $blockedPath
                risk_type = "GLOBAL_BLOCKED_PATH"
                recommendation = "Do not claim this path in an automated worker lock."
            }
        }
    }

    foreach ($lock in $activeLocks) {
        foreach ($lockedPath in @($lock.claimed_paths)) {
            if (Test-AiOsPathOverlap -LeftPath $requestedPath -RightPath $lockedPath) {
                $riskType = "ACTIVE_LOCK_COLLISION"
                $recommendation = "Block claim. Another worker owns an overlapping path."

                if ($lock.worker_id -eq $WorkerId) {
                    $riskType = "SAME_WORKER_RECLAIM_REVIEW"
                    $recommendation = "Require review before the same worker expands or repeats a claim."
                }

                $collisions += [pscustomobject]@{
                    requested_path = $requestedPath
                    existing_lock_id = $lock.lock_id
                    existing_worker_id = $lock.worker_id
                    existing_packet_id = $lock.packet_id
                    existing_path = $lockedPath
                    risk_type = $riskType
                    recommendation = $recommendation
                }
            }
        }
    }
}

$claimStatus = "SIMULATED_ALLOWED"
if ($policyBlocks.Count -gt 0 -or $collisions.Count -gt 0) {
    $claimStatus = "SIMULATED_BLOCKED"
}

$simulatedLock = [pscustomobject]@{
    lock_id = "SIMULATED-$($WorkerId)-$($PacketId)"
    worker_id = $WorkerId
    packet_id = $PacketId
    mode = "DRY_RUN"
    status = $claimStatus
    claimed_paths = $normalizedPaths
    created_at = (Get-Date).ToString("s")
    notes = "Simulation only. No registry file was changed."
}

$recommendedBlocked = @()
$recommendedBlocked += @($registry.global_blocked_paths)
$recommendedBlocked += @($registry.recommended_blocked_files)
$recommendedBlocked += @($normalizedPaths)
foreach ($collision in $collisions) {
    $recommendedBlocked += $collision.existing_path
}
$recommendedBlocked = @($recommendedBlocked | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | Sort-Object -Unique)

$result = [pscustomobject]@{
    task = "Simulate AI_OS file lock claim"
    mode = "DRY_RUN"
    registry_path = $RegistryPath
    claim_status = $claimStatus
    simulated_lock = $simulatedLock
    collision_count = $collisions.Count
    policy_block_count = $policyBlocks.Count
    collisions = $collisions
    policy_blocks = $policyBlocks
    recommended_blocked_paths = $recommendedBlocked
    safety = [pscustomobject]@{
        writes_performed = 0
        commits_performed = 0
        pushes_performed = 0
        broker_or_live_api_work = "NO"
    }
    next_safe_action = "If SIMULATED_BLOCKED appears, do not APPLY. Pick a non-overlapping path or ask the operator to resolve ownership."
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS File Lock Claim Simulation"
Write-Host "Mode: DRY_RUN"
Write-Host "Worker: $WorkerId"
Write-Host "Packet: $PacketId"
Write-Host "Result: $claimStatus"
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
Write-Host ""
Write-Host "Validator note: no files were changed; this was simulation-only."
Write-Host "Next safe action: $($result.next_safe_action)"
