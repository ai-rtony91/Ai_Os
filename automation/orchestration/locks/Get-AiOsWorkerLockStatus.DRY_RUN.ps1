param(
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
$locks = @($registry.locks)
$activeLocks = @($locks | Where-Object { $_.status -eq "ACTIVE" })
$releasedLocks = @($locks | Where-Object { $_.status -eq "RELEASED" })
$reviewLocks = @($locks | Where-Object { $_.status -eq "REVIEW_REQUIRED" -or $_.status -eq "EXPIRED" })
$collisionRisks = @()

for ($i = 0; $i -lt $activeLocks.Count; $i++) {
    for ($j = $i + 1; $j -lt $activeLocks.Count; $j++) {
        foreach ($leftPath in @($activeLocks[$i].claimed_paths)) {
            foreach ($rightPath in @($activeLocks[$j].claimed_paths)) {
                if (Test-AiOsPathOverlap -LeftPath $leftPath -RightPath $rightPath) {
                    $collisionRisks += [pscustomobject]@{
                        risk_type = "ACTIVE_LOCK_PATH_OVERLAP"
                        left_lock = $activeLocks[$i].lock_id
                        right_lock = $activeLocks[$j].lock_id
                        left_path = $leftPath
                        right_path = $rightPath
                        recommendation = "Block APPLY until a human resolves ownership."
                    }
                }
            }
        }
    }
}

$recommendedBlocked = @()
$recommendedBlocked += @($registry.global_blocked_paths)
$recommendedBlocked += @($registry.recommended_blocked_files)
foreach ($lock in $activeLocks) {
    $recommendedBlocked += @($lock.claimed_paths)
}
$recommendedBlocked = @($recommendedBlocked | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | Sort-Object -Unique)

$result = [pscustomobject]@{
    task = "Show current AI_OS file locks"
    mode = "DRY_RUN"
    registry_path = $RegistryPath
    lock_count = $locks.Count
    active_lock_count = $activeLocks.Count
    released_lock_count = $releasedLocks.Count
    review_required_count = $reviewLocks.Count
    collision_risk_count = $collisionRisks.Count
    collision_risks = $collisionRisks
    recommended_blocked_paths = $recommendedBlocked
    safety = [pscustomobject]@{
        writes_performed = 0
        commits_performed = 0
        pushes_performed = 0
        broker_or_live_api_work = "NO"
    }
    next_safe_action = "Use Claim-AiOsFileLock.DRY_RUN.ps1 with a proposed path to simulate collision risk before APPLY."
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS File Lock Registry Status"
Write-Host "Mode: DRY_RUN"
Write-Host "Registry: $RegistryPath"
Write-Host ""
Write-Host "Summary:"
Write-Host "  Total locks: $($result.lock_count)"
Write-Host "  Active locks: $($result.active_lock_count)"
Write-Host "  Released locks: $($result.released_lock_count)"
Write-Host "  Review required locks: $($result.review_required_count)"
Write-Host "  Collision risks inside registry: $($result.collision_risk_count)"
Write-Host ""

foreach ($lock in ($locks | Sort-Object lock_id)) {
    Write-Host "Lock: $($lock.lock_id)"
    Write-Host "  Worker: $($lock.worker_id)"
    Write-Host "  Packet: $($lock.packet_id)"
    Write-Host "  Status: $($lock.status)"
    Write-Host "  Claimed paths:"
    foreach ($path in @($lock.claimed_paths)) {
        Write-Host "    - $path"
    }
    Write-Host ""
}

Write-Host "Recommended blocked paths:"
foreach ($path in $recommendedBlocked) {
    Write-Host "  - $path"
}
Write-Host ""
Write-Host "Validator note: no files were changed; this was display-only."
Write-Host "Next safe action: $($result.next_safe_action)"
