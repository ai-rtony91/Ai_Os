param(
    [string]$LockRegistryPath = "automation/orchestration/locks/FILE_LOCK_REGISTRY.example.json",
    [string[]]$ProposedPaths = @(),
    [string]$WorkerId = "CURRENT_WORKER",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-AiOsPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return (Join-Path (Get-Location).Path $Path)
}

function Read-AiOsJsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Lock registry not found: $Path"
    }

    try {
        return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    } catch {
        throw "Lock registry JSON parse failed: $($_.Exception.Message)"
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
        [Parameter(Mandatory = $true)][string]$LeftPath,
        [Parameter(Mandatory = $true)][string]$RightPath
    )

    $left = ConvertTo-AiOsPathKey -Path $LeftPath
    $right = ConvertTo-AiOsPathKey -Path $RightPath

    if ([string]::IsNullOrWhiteSpace($left) -or [string]::IsNullOrWhiteSpace($right)) {
        return $false
    }

    return ($left -eq $right -or $left.StartsWith("$right/") -or $right.StartsWith("$left/"))
}

function Invoke-AiOsGit {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    return [pscustomobject]@{
        Output = @($output | ForEach-Object { [string]$_ })
        ExitCode = $exitCode
    }
}

function Get-AiOsStatusPaths {
    $status = Invoke-AiOsGit -Arguments @("status", "--short")
    $paths = @()

    foreach ($line in @($status.Output | Where-Object { $_ -notmatch "^warning:" -and -not [string]::IsNullOrWhiteSpace($_) })) {
        if ($line.Length -ge 4) {
            $paths += ConvertTo-AiOsPathKey -Path $line.Substring(3)
        }
    }

    return [pscustomobject]@{
        paths = @($paths | Sort-Object -Unique)
        warnings = @($status.Output | Where-Object { $_ -match "^warning:" })
        exit_code = $status.ExitCode
    }
}

$resolvedLockRegistryPath = Resolve-AiOsPath -Path $LockRegistryPath
$lockRegistry = Read-AiOsJsonFile -Path $resolvedLockRegistryPath
$statusPaths = Get-AiOsStatusPaths
$candidatePaths = @()
$candidatePaths += @($ProposedPaths | ForEach-Object { ConvertTo-AiOsPathKey -Path $_ })
$candidatePaths += @($statusPaths.paths)
$candidatePaths = @($candidatePaths | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique)

$activeLocks = @($lockRegistry.locks | Where-Object { "$($_.status)" -eq "ACTIVE" })
$globalBlocked = @($lockRegistry.global_blocked_paths)
$blockedFiles = @($lockRegistry.recommended_blocked_files)
$warnings = @()
$collisions = @()

foreach ($candidate in $candidatePaths) {
    foreach ($blockedPath in @($globalBlocked + $blockedFiles)) {
        if (Test-AiOsPathOverlap -LeftPath $candidate -RightPath "$blockedPath") {
            $collisions += [pscustomobject]@{
                risk_type = "PROTECTED_PATH_OVERLAP"
                candidate_path = $candidate
                owner = "AI_OS_PROTECTION_RULE"
                overlapping_path = "$blockedPath"
                recommendation = "Block APPLY unless the user explicitly approves this protected scope."
            }
        }
    }

    foreach ($lock in $activeLocks) {
        foreach ($lockedPath in @($lock.claimed_paths)) {
            if (Test-AiOsPathOverlap -LeftPath $candidate -RightPath "$lockedPath") {
                $sameWorker = ("$($lock.worker_id)" -eq $WorkerId)
                $collisions += [pscustomobject]@{
                    risk_type = if ($sameWorker) { "SAME_WORKER_RECLAIM_REVIEW" } else { "ACTIVE_LOCK_PATH_OVERLAP" }
                    candidate_path = $candidate
                    owner = "$($lock.worker_id)"
                    lock_id = "$($lock.lock_id)"
                    overlapping_path = "$lockedPath"
                    recommendation = "Block APPLY until lane ownership is reviewed."
                }
            }
        }
    }
}

if ($candidatePaths.Count -eq 0) {
    $warnings += "No proposed paths and no current dirty files were found. Isolation can only report registry state."
}

if ($activeLocks.Count -eq 0) {
    $warnings += "No active locks found in the selected lock registry."
}

$overallStatus = "PASS"
if ($collisions.Count -gt 0) {
    $overallStatus = "BLOCKED"
} elseif ($warnings.Count -gt 0) {
    $overallStatus = "WARN"
}

$result = [pscustomobject]@{
    task = "AI_OS worker isolation and file-scope overlap check"
    mode = "READ_ONLY"
    overall_status = $overallStatus
    worker_id = $WorkerId
    lock_registry_path = $resolvedLockRegistryPath
    candidate_paths = $candidatePaths
    active_lock_count = $activeLocks.Count
    collision_count = $collisions.Count
    collisions = $collisions
    warnings = $warnings
    git_warnings = $statusPaths.warnings
    safety = [pscustomobject]@{
        writes_performed = 0
        commits_performed = 0
        pushes_performed = 0
        runtime_edits = "NO"
        dashboard_edits = "NO"
        policy_edits = "NO"
        telemetry_edits = "NO"
    }
    next_safe_action = if ($overallStatus -eq "BLOCKED") { "Stop. Resolve path ownership before APPLY." } elseif ($overallStatus -eq "WARN") { "Review warnings and rerun with -ProposedPaths before APPLY." } else { "Isolation check passed for the selected paths." }
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS Worker Isolation Check"
Write-Host "Mode: READ_ONLY"
Write-Host "Status: $overallStatus"
Write-Host "Worker: $WorkerId"
Write-Host "Candidate paths: $($candidatePaths.Count)"
Write-Host "Active locks: $($activeLocks.Count)"
Write-Host "Collisions: $($collisions.Count)"
Write-Host ""

Write-Host "Candidate paths:"
if ($candidatePaths.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($path in $candidatePaths) {
        Write-Host "  - $path"
    }
}
Write-Host ""

Write-Host "Collision warnings:"
if ($collisions.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($collision in $collisions) {
        Write-Host "  - $($collision.risk_type): $($collision.candidate_path) overlaps $($collision.overlapping_path)"
        Write-Host "    Owner: $($collision.owner)"
        Write-Host "    Recommendation: $($collision.recommendation)"
    }
}
Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "Next safe action: $($result.next_safe_action)"
