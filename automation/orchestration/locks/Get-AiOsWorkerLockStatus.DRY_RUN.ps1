param(
    [string]$RegistryPath = (Join-Path $PSScriptRoot "FILE_LOCK_REGISTRY.json"),
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

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
$releasedLocks = @($locks | Where-Object { $_.status -eq "RELEASED" })
$reviewLocks = @($locks | Where-Object { $_.status -eq "REVIEW_REQUIRED" -or $_.status -eq "EXPIRED" })
$now = [DateTime]::UtcNow
$staleLocks = @()
$collisionRisks = @()

foreach ($lock in $activeLocks) {
    if ($lock.PSObject.Properties.Name -contains "expires_at_utc" -and -not [string]::IsNullOrWhiteSpace([string]$lock.expires_at_utc)) {
        try {
            if ([DateTime]::Parse([string]$lock.expires_at_utc).ToUniversalTime() -lt $now) {
                $staleLocks += $lock
            }
        }
        catch {
            $staleLocks += $lock
        }
    }
}

for ($i = 0; $i -lt $activeLocks.Count; $i++) {
    for ($j = $i + 1; $j -lt $activeLocks.Count; $j++) {
        foreach ($leftPath in (Get-AiOsLockPaths -Lock $activeLocks[$i])) {
            foreach ($rightPath in (Get-AiOsLockPaths -Lock $activeLocks[$j])) {
                if (Test-AiOsPathOverlap -LeftPath $leftPath -RightPath $rightPath) {
                    $collisionRisks += [pscustomobject]@{
                        risk_type = "ACTIVE_LOCK_PATH_OVERLAP"
                        left_lock = $activeLocks[$i].lock_id
                        right_lock = $activeLocks[$j].lock_id
                        left_path = ConvertTo-AiOsPathKey -Path $leftPath
                        right_path = ConvertTo-AiOsPathKey -Path $rightPath
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
    $recommendedBlocked += @(Get-AiOsLockPaths -Lock $lock)
}
$recommendedBlocked = @($recommendedBlocked | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | ForEach-Object { ConvertTo-AiOsPathKey -Path $_ } | Sort-Object -Unique)

$result = [pscustomobject]@{
    task = "Show current AI_OS file locks"
    mode = "DRY_RUN"
    registry_path = $RegistryPath
    lock_count = $locks.Count
    active_lock_count = $activeLocks.Count
    released_lock_count = $releasedLocks.Count
    review_required_count = $reviewLocks.Count
    stale_lock_review_count = $staleLocks.Count
    collision_risk_count = $collisionRisks.Count
    collision_risks = $collisionRisks
    recommended_blocked_paths = $recommendedBlocked
    safety = [pscustomobject]@{
        writes_performed = 0
        commits_performed = 0
        pushes_performed = 0
        broker_or_live_api_work = "NO"
    }
    next_safe_action = "Use Claim-AiOsFileLock.DRY_RUN.ps1 to preview collision risk before any operator-approved APPLY lock claim."
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 10
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
Write-Host "  Stale lock review count: $($result.stale_lock_review_count)"
Write-Host "  Collision risks inside registry: $($result.collision_risk_count)"
Write-Host ""

foreach ($lock in ($locks | Sort-Object lock_id)) {
    Write-Host "Lock: $($lock.lock_id)"
    Write-Host "  Worker: $($lock.worker_id)"
    Write-Host "  Packet: $($lock.packet_id)"
    Write-Host "  Status: $($lock.status)"
    Write-Host "  Claimed paths:"
    foreach ($path in (Get-AiOsLockPaths -Lock $lock)) {
        Write-Host "    - $(ConvertTo-AiOsPathKey -Path $path)"
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
